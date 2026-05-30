"""WebSocket broadcast hub — ConnectionManager."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import WebSocket

from proxy_view.models import RequestCompleted, RequestError, RequestStarted

logger = logging.getLogger(__name__)

Event = RequestStarted | RequestCompleted | RequestError


_manager: ConnectionManager | None = None


def get_manager() -> ConnectionManager:
    """Return the singleton ConnectionManager instance."""
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager


class ConnectionManager:
    """Manages WebSocket connections and broadcasts events to all clients.

    Each connected client gets events pushed as text JSON messages.
    If a client disconnects or errors mid-broadcast, it is removed from
    the active set silently.
    """

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Register a new WebSocket client."""
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        """Unregister a WebSocket client. Safe to call for unknown clients."""
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def broadcast(self, event: Event) -> None:
        """Send an event to all connected WebSocket clients.

        Clients that fail to receive are removed from the active set.
        """
        payload = event.model_dump_json()
        dead: list[WebSocket] = []
        for ws in self.active_connections:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active_connections.remove(ws)
