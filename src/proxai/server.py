"""FastAPI application factory with WebSocket and proxy endpoints."""

from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response

from proxai.config import ProxyConfig
from proxai.models import RequestCompleted, RequestError, RequestStarted
from proxai.proxy import ProxyHandler
from proxai.ws import get_manager

logger = logging.getLogger(__name__)


def create_app(config: Optional[ProxyConfig] = None) -> FastAPI:
    """Create the FastAPI application with proxy forwarding.

    Args:
        config: Proxy configuration. If None, defaults to localhost:3000.
    """
    if config is None:
        config = ProxyConfig(target_url="http://localhost:3000")

    app = FastAPI(title="Proxai", version="0.1.0")
    manager = get_manager()
    handler = ProxyHandler(config)

    @app.get("/health")
    async def health():
        return JSONResponse({"status": "ok"})

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        await manager.connect(websocket)
        try:
            await websocket.send_json({"type": "connected"})
            while True:
                try:
                    data = await websocket.receive_text()
                except WebSocketDisconnect:
                    break
        finally:
            await manager.disconnect(websocket)

    # Catch-all route — must be registered AFTER /ws and /health
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
    async def proxy(request: Request, path: str):
        # Read and cache the request body
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8", errors="replace") if body_bytes else None

        # Build headers dict
        headers = dict(request.headers.items())

        # Generate a unique request ID
        import uuid
        request_id = uuid.uuid4().hex

        # Emit request.started
        started = RequestStarted(
            request_id=request_id,
            method=request.method,
            url=f"/{path}",
            path=f"/{path}",
            query=str(request.url.query) if request.url.query else None,
            headers=headers,
            body=body_str,
        )
        await manager.broadcast(started)

        # Forward the request
        result = await handler.forward(
            method=request.method,
            path=path,
            headers=headers,
            body=body_str,
        )

        if result["error"]:
            # Emit request.error
            error_event = RequestError(
                request_id=started.request_id,
                method=request.method,
                url=f"/{path}",
                error=result["error"],
            )
            await manager.broadcast(error_event)

            # Get the response body from the error result
            error_body = result.get("response_body", json.dumps({"error": result["error"]}))
            return Response(
                content=error_body,
                status_code=result["status"],
                media_type="application/json",
            )
        else:
            # Emit request.completed
            completed = RequestCompleted(
                request_id=started.request_id,
                method=request.method,
                url=f"/{path}",
                status=result["status"],
                status_text=result["status_text"],
                response_headers=result.get("response_headers"),
                response_body=result.get("response_body"),
                latency_ms=result["latency_ms"],
            )
            await manager.broadcast(completed)

            # Return the response
            return Response(
                content=result.get("response_body", ""),
                status_code=result["status"],
                headers=result.get("response_headers", {}),
                media_type="application/json",
            )

    return app
