"""Tests for the integrated proxy server (catch-all route + events)."""

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

from proxy_view.config import ProxyConfig
from proxy_view.server import create_app
from proxy_view.ws import get_manager


@pytest.mark.asyncio
async def test_proxy_catch_all_forwards_request():
    """A GET through the catch-all route is forwarded to the target."""
    # Start an echo target
    from fastapi import FastAPI as TargetApp, Request
    from fastapi.responses import JSONResponse

    target = TargetApp()

    @target.get("/api/hello")
    async def hello():
        return {"message": "hello", "source": "target"}

    @target.post("/api/echo")
    async def echo(request: Request):
        body = await request.body()
        return JSONResponse({"method": "POST", "body": body.decode()})

    import uvicorn
    import threading

    # Start the target server on a random port
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    target_port = sock.getsockname()[1]
    sock.close()

    from proxy_view.ws import get_manager
    mgr = get_manager()

    # Reset the manager for clean state
    mgr.active_connections = []

    config = ProxyConfig(target_url=f"http://127.0.0.1:{target_port}")
    proxy_app = create_app(config=config)

    # Start the proxy server
    proxy_port = target_port + 1
    proxy_thread = threading.Thread(
        target=uvicorn.run,
        args=(proxy_app,),
        kwargs={"host": "127.0.0.1", "port": proxy_port, "log_level": "error"},
        daemon=True,
    )
    proxy_thread.start()

    # Start the target server
    target_thread = threading.Thread(
        target=uvicorn.run,
        args=(target,),
        kwargs={"host": "127.0.0.1", "port": target_port, "log_level": "error"},
        daemon=True,
    )
    target_thread.start()

    import time
    time.sleep(2)

    # Send a request through the proxy
    async with AsyncClient() as client:
        resp = await client.get(f"http://127.0.0.1:{proxy_port}/api/hello")
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "hello"
        assert data["source"] == "target"

    # Cleanup - stop servers
    import signal
    # The daemon threads will die when the test process exits


@pytest.mark.asyncio
async def test_proxy_events_emitted_via_websocket():
    """Requests through the proxy emit WebSocket events."""
    import time
    import asyncio
    import socket
    import threading
    import uvicorn
    from fastapi import FastAPI as TargetApp, Request
    from fastapi.responses import JSONResponse

    # Echo target
    target = TargetApp()

    @target.get("/api/hello")
    async def hello():
        return {"message": "world"}

    # Find a free port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    target_port = sock.getsockname()[1]
    sock.close()

    # Reset state
    from proxy_view.ws import get_manager
    mgr = get_manager()
    mgr.active_connections = []

    config = ProxyConfig(target_url=f"http://127.0.0.1:{target_port}")
    proxy_app = create_app(config=config)
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

    # Connect WebSocket client before making the request
    from websockets.sync.client import connect as ws_connect
    with ws_connect(f"ws://127.0.0.1:{proxy_port}/ws") as ws:
        # Read connected message
        msg = ws.recv(timeout=5)

        # Make a request through the proxy
        async with AsyncClient() as client:
            resp = await client.get(f"http://127.0.0.1:{proxy_port}/api/hello")
            assert resp.status_code == 200

        # Now check for request.started and request.completed events
        # We might need to wait a moment for events to flow
        import time as _time
        _time.sleep(0.5)

        events_received = []
        try:
            while True:
                msg = ws.recv(timeout=2)
                events_received.append(msg)
        except TimeoutError:
            pass

        # Check for event types
        event_types = []
        for msg in events_received:
            import json
            try:
                data = json.loads(msg)
                event_types.append(data.get("type"))
            except json.JSONDecodeError:
                pass

        assert "request.started" in event_types, (
            f"Expected request.started event, got: {event_types}"
        )
        assert "request.completed" in event_types, (
            f"Expected request.completed event, got: {event_types}"
        )
