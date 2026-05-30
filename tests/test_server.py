"""Tests for FastAPI server and WebSocket endpoint."""

import asyncio

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from proxai.server import create_app


@pytest_asyncio.fixture
async def app() -> FastAPI:
    return create_app()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client: AsyncClient):
        """GET /health returns 200 with status ok."""
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


class TestWebSocketEndpoint:
    @pytest.mark.asyncio
    async def test_ws_accepts_connection(self, app: FastAPI):
        """WebSocket at /ws accepts connections and confirms."""
        from fastapi.testclient import TestClient

        with TestClient(app) as test_client:
            with test_client.websocket_connect("/ws") as ws:
                # Server should send a confirmation message on connect
                msg = ws.receive_json()
                assert msg["type"] == "connected"

    @pytest.mark.asyncio
    async def test_ws_receives_proxy_events(self, app: FastAPI):
        """WebSocket receives broadcast events after connecting."""
        from fastapi.testclient import TestClient

        with TestClient(app) as test_client:
            with test_client.websocket_connect("/ws") as ws:
                # Read the connected message
                ws.receive_json()

                # Simulate a broadcast
                from proxai.models import RequestStarted
                from proxai.ws import get_manager

                mgr = get_manager()
                event = RequestStarted(
                    request_id="ws-test-1",
                    method="GET",
                    url="/api/test",
                    path="/api/test",
                )
                await mgr.broadcast(event)

                # The WS client should receive the event
                msg = ws.receive_json()
                assert msg["type"] == "request.started"
                assert msg["request_id"] == "ws-test-1"
