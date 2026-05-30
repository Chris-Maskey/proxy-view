"""FastAPI application factory with WebSocket and health endpoints."""

from __future__ import annotations

import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from proxai.ws import get_manager

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    app = FastAPI(title="Proxai", version="0.1.0")

    manager = get_manager()

    @app.get("/health")
    async def health():
        return JSONResponse({"status": "ok"})

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        await manager.connect(websocket)
        try:
            # Send a confirmation message
            await websocket.send_json({"type": "connected"})

            # Keep the connection alive receiving messages (not used currently)
            while True:
                try:
                    data = await websocket.receive_text()
                except WebSocketDisconnect:
                    break
        finally:
            await manager.disconnect(websocket)

    return app
