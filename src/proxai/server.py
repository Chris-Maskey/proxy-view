"""FastAPI application factory with WebSocket and proxy endpoints."""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response

from proxai.config import ProxyConfig
from proxai.models import RequestCompleted, RequestError, RequestStarted
from proxai.proxy import ProxyHandler
from proxai.storage import Storage
from proxai.ws import get_manager

logger = logging.getLogger(__name__)


def create_app(config: Optional[ProxyConfig] = None, db_path: Optional[str] = None) -> FastAPI:
    """Create the FastAPI application with proxy forwarding.

    Args:
        config: Proxy configuration. If None, defaults to localhost:3000.
        db_path: Optional path to SQLite database. If None, logging is skipped.
    """
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response

from proxai.config import ProxyConfig
from proxai.models import RequestCompleted, RequestError, RequestStarted
from proxai.proxy import ProxyHandler
from proxai.storage import Storage
from proxai.ws import get_manager

logger = logging.getLogger(__name__)


def create_app(config: Optional[ProxyConfig] = None, db_path: Optional[str] = None) -> FastAPI:
    """Create the FastAPI application with proxy forwarding.

    Args:
        config: Proxy configuration. If None, reads from PROXAI_TARGET env var
                 or defaults to localhost:3000.
        db_path: Optional path to SQLite database. If None, reads from
                 PROXAI_DB_PATH env var or None.
    """
    if config is None:
        target = os.environ.get("PROXAI_TARGET", "http://localhost:3000")
        config = ProxyConfig(target_url=target)
    if db_path is None:
        db_path = os.environ.get("PROXAI_DB_PATH")

    handler = ProxyHandler(config)
    storage: Storage | None = None
    if db_path:
        storage = Storage(db_path=db_path)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if storage:
            await storage.initialize()
        yield
        if storage:
            await storage.close()
        await handler.close()

    app = FastAPI(title="Proxai", version="0.1.0", lifespan=lifespan)
    manager = get_manager()

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
        if storage:
            await storage.store_event(started)

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
            if storage:
                await storage.store_event(error_event)

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
            if storage:
                await storage.store_event(completed)

            # Return the response
            return Response(
                content=result.get("response_body", ""),
                status_code=result["status"],
                headers=result.get("response_headers", {}),
                media_type="application/json",
            )

    return app
