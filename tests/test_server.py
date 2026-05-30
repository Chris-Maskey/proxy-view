"""Tests for FastAPI server and WebSocket endpoint."""

import asyncio

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from proxy_view.server import create_app


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
                from proxy_view.models import RequestStarted
                from proxy_view.ws import get_manager

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


class TestDashboardEndpoint:
    @pytest.mark.asyncio
    async def test_dashboard_static_files_served(self, client: AsyncClient):
        """Dashboard static files are served at /dashboard/."""
        import os

        dashboard_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "dashboard", "dist",
        )
        if not os.path.isdir(dashboard_dir):
            pytest.skip("Dashboard not built")

        resp = await client.get("/dashboard/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_dashboard_does_not_interfere_with_health(self, client: AsyncClient):
        """Health endpoint still works with dashboard mounted."""
        import os

        dashboard_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "dashboard", "dist",
        )
        if not os.path.isdir(dashboard_dir):
            pytest.skip("Dashboard not built")

        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_replay_stored_request():
    """POST /replay/{id} replays a stored request and returns the result."""
    import socket
    import threading
    import time
    import os
    import tempfile
    import uvicorn
    import sqlite3
    from fastapi import FastAPI as TargetApp
    from httpx import AsyncClient
    from proxy_view.config import ProxyConfig
    from proxy_view.server import create_app
    from proxy_view.ws import get_manager

    # Reset WS state
    get_manager().active_connections = []

    # Start echo target
    target = TargetApp()

    @target.get("/ping")
    async def ping():
        return {"pong": True, "source": "target"}

    @target.post("/ping")
    async def ping_post():
        return {"pong": True, "echoed": True}

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    target_port = sock.getsockname()[1]
    sock.close()

    # Temp DB for storage
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = db_file.name
    db_file.close()

    config = ProxyConfig(target_url=f"http://127.0.0.1:{target_port}")
    proxy_app = create_app(config=config, db_path=db_path)
    proxy_port = target_port + 1

    # Start servers
    threading.Thread(
        target=uvicorn.run, args=(target,),
        kwargs={"host": "127.0.0.1", "port": target_port, "log_level": "error"},
        daemon=True,
    ).start()
    threading.Thread(
        target=uvicorn.run, args=(proxy_app,),
        kwargs={"host": "127.0.0.1", "port": proxy_port, "log_level": "error"},
        daemon=True,
    ).start()
    time.sleep(2)

    # Make a request through the proxy (gets stored)
    async with AsyncClient() as c:
        resp = await c.get(f"http://127.0.0.1:{proxy_port}/ping")
        assert resp.status_code == 200
        assert resp.json()["source"] == "target"

    # Query storage for the request_id
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT request_id FROM requests ORDER BY started_at DESC LIMIT 1"
    ).fetchone()
    request_id = row[0]
    conn.close()

    # Replay the request
    async with AsyncClient() as c:
        resp = await c.post(f"http://127.0.0.1:{proxy_port}/replay/{request_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["original_request_id"] == request_id
        assert data["status"] == 200
        assert data["method"] == "GET"
        assert "/ping" in data["path"]
        assert data["latency_ms"] >= 0

    # Cleanup
    os.unlink(db_path)
