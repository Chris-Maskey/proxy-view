"""Tests for WebSocket broadcast hub (ConnectionManager)."""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from proxy_view.models import RequestStarted
from proxy_view.ws import ConnectionManager


class TestConnectionManager:
    """Tests for ConnectionManager — WebSocket broadcast hub."""

    @pytest.mark.asyncio
    async def test_connect_adds_client(self):
        """connect() registers a WebSocket client."""
        mgr = ConnectionManager()
        ws = AsyncMock()
        await mgr.connect(ws)
        assert len(mgr.active_connections) == 1
        assert mgr.active_connections[0] is ws

    @pytest.mark.asyncio
    async def test_disconnect_removes_client(self):
        """disconnect() unregisters a WebSocket client."""
        mgr = ConnectionManager()
        ws = AsyncMock()
        await mgr.connect(ws)
        await mgr.disconnect(ws)
        assert len(mgr.active_connections) == 0

    @pytest.mark.asyncio
    async def test_disconnect_unregistered_client_is_safe(self):
        """disconnect() on a client that wasn't connected does nothing."""
        mgr = ConnectionManager()
        ws = AsyncMock()
        await mgr.disconnect(ws)  # should not raise
        assert len(mgr.active_connections) == 0

    @pytest.mark.asyncio
    async def test_broadcast_sends_to_all_clients(self):
        """broadcast() sends the event to every connected client."""
        mgr = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await mgr.connect(ws1)
        await mgr.connect(ws2)

        event = RequestStarted(
            request_id="abc", method="GET", url="/test", path="/test"
        )
        await mgr.broadcast(event)

        expected = event.model_dump_json()
        ws1.send_text.assert_awaited_once_with(expected)
        ws2.send_text.assert_awaited_once_with(expected)

    @pytest.mark.asyncio
    async def test_broadcast_skips_disconnected_client(self):
        """broadcast() removes and skips clients that disconnect mid-broadcast."""
        mgr = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        ws1.send_text = AsyncMock(side_effect=Exception("disconnected"))
        await mgr.connect(ws1)
        await mgr.connect(ws2)

        event = RequestStarted(
            request_id="abc", method="GET", url="/test", path="/test"
        )
        await mgr.broadcast(event)

        # ws1 should be removed, ws2 should still get the event
        assert ws1 not in mgr.active_connections
        assert ws2 in mgr.active_connections
        expected = event.model_dump_json()
        ws2.send_text.assert_awaited_once_with(expected)

    @pytest.mark.asyncio
    async def test_broadcast_to_empty_set_is_safe(self):
        """broadcast() with no connected clients does nothing."""
        mgr = ConnectionManager()
        event = RequestStarted(
            request_id="abc", method="GET", url="/test", path="/test"
        )
        await mgr.broadcast(event)  # should not raise

    @pytest.mark.asyncio
    async def test_multiple_connect_disconnect(self):
        """Multiple connect/disconnect cycles maintain correct state."""
        mgr = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        ws3 = AsyncMock()

        await mgr.connect(ws1)
        await mgr.connect(ws2)
        assert len(mgr.active_connections) == 2

        await mgr.disconnect(ws1)
        assert len(mgr.active_connections) == 1
        assert mgr.active_connections[0] is ws2

        await mgr.connect(ws3)
        assert len(mgr.active_connections) == 2
        assert ws3 in mgr.active_connections
