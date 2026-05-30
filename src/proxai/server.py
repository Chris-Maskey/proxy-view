"""FastAPI application factory with WebSocket and proxy endpoints."""

from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

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

    # Serve dashboard static files if built
    _dashboard_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'dashboard', 'dist')
    _dashboard_dir = os.path.abspath(_dashboard_dir)
    if os.path.isdir(_dashboard_dir):
        _sf = StaticFiles(directory=_dashboard_dir, html=True)

        # Wrap with no-cache headers
        from starlette.types import ASGIApp, Scope, Receive, Send
        class _NoCacheASGI:
            def __init__(self, app: ASGIApp):
                self.app = app
            async def __call__(self, scope: Scope, receive: Receive, send: Send):
                async def _send(msg):
                    if msg["type"] == "http.response.start":
                        headers = list(msg.get("headers", []))
                        headers.append((b"cache-control", b"no-cache, no-store, must-revalidate"))
                        msg["headers"] = headers
                    await send(msg)
                await self.app(scope, receive, _send)

        app.mount("/dashboard", _NoCacheASGI(_sf), name="dashboard")

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

    # --- API endpoints (must come before catch-all) ---

    @app.post("/replay/{request_id}")
    async def replay_request(request_id: str):
        """Replay a previously captured request by ID."""
        if storage is None:
            return JSONResponse(
                {"error": "Storage not enabled — replay requires a database"},
                status_code=400,
            )

        original = await storage.get_request(request_id)
        if original is None:
            return JSONResponse(
                {"error": f"Request {request_id} not found"},
                status_code=404,
            )

        if not original.get("method") or not original.get("path"):
            return JSONResponse(
                {"error": "Incomplete request data — missing method or path"},
                status_code=400,
            )

        import uuid
        new_id = uuid.uuid4().hex

        orig_headers = {}
        if original.get("request_headers"):
            try:
                orig_headers = json.loads(original["request_headers"])
            except (json.JSONDecodeError, TypeError):
                orig_headers = {}

        # Emit request.started for the replay
        started = RequestStarted(
            request_id=new_id,
            method=original["method"],
            url=original["url"] or original["path"],
            path=original["path"],
            query=original.get("query"),
            headers=orig_headers,
            body=original.get("request_body"),
        )
        await manager.broadcast(started)
        if storage:
            await storage.store_event(started)

        # Forward the replayed request
        result = await handler.forward(
            method=original["method"],
            path=original["path"].lstrip("/"),
            headers=orig_headers,
            body=original.get("request_body"),
        )

        if result["error"]:
            error_event = RequestError(
                request_id=new_id,
                method=original["method"],
                url=original["url"] or original["path"],
                error=result["error"],
            )
            await manager.broadcast(error_event)
            if storage:
                await storage.store_event(error_event)
        else:
            completed = RequestCompleted(
                request_id=new_id,
                method=original["method"],
                url=original["url"] or original["path"],
                status=result["status"],
                status_text=result["status_text"],
                response_headers=result.get("response_headers"),
                response_body=result.get("response_body"),
                latency_ms=result["latency_ms"],
            )
            await manager.broadcast(completed)
            if storage:
                await storage.store_event(completed)

        return JSONResponse({
            "original_request_id": request_id,
            "replay_request_id": new_id,
            "method": original["method"],
            "path": original["url"] or original["path"],
            "status": result["status"],
            "status_text": result["status_text"],
            "response_body": result.get("response_body"),
            "latency_ms": result["latency_ms"],
            "error": result["error"],
        })

    @app.get("/logs")
    async def list_logs(limit: int = 50, offset: int = 0):
        """List stored request logs."""
        if storage is None:
            return JSONResponse([], status_code=200)
        logs = await storage.list_requests(limit=limit, offset=offset)
        return JSONResponse([
            {
                "request_id": r["request_id"],
                "method": r["method"],
                "url": r["url"],
                "status": r["status"],
                "latency_ms": r["latency_ms"],
                "started_at": r["started_at"],
            }
            for r in logs
        ])

    @app.get("/logs/{request_id}")
    async def get_log_detail(request_id: str):
        """Get full details for a single stored request (for diff)."""
        if storage is None:
            return JSONResponse({"error": "Storage not enabled"}, status_code=400)
        record = await storage.get_request(request_id)
        if record is None:
            return JSONResponse({"error": "Not found"}, status_code=404)

        # Parse JSON fields back to dicts for the response
        req_headers = {}
        if record.get("request_headers"):
            try:
                req_headers = json.loads(record["request_headers"])
            except (json.JSONDecodeError, TypeError):
                req_headers = {}

        resp_headers = {}
        if record.get("response_headers"):
            try:
                resp_headers = json.loads(record["response_headers"])
            except (json.JSONDecodeError, TypeError):
                resp_headers = {}

        return JSONResponse({
            "request_id": record["request_id"],
            "method": record["method"],
            "url": record["url"],
            "path": record["path"],
            "query": record.get("query"),
            "request_headers": req_headers,
            "request_body": record.get("request_body"),
            "status": record.get("status"),
            "status_text": record.get("status_text"),
            "response_headers": resp_headers,
            "response_body": record.get("response_body"),
            "latency_ms": record.get("latency_ms"),
            "error": record.get("error"),
            "started_at": record["started_at"],
            "completed_at": record.get("completed_at"),
        })

    # Catch-all route — must be registered AFTER specific routes
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
