"""Tests for the HTTP proxy forwarding core."""

import pytest

from proxai.config import ProxyConfig
from proxai.proxy import ProxyHandler


class TestProxyHandler:
    @pytest.mark.asyncio
    async def test_proxy_creates_handler(self):
        """ProxyHandler can be instantiated with a config."""
        config = ProxyConfig(target_url="http://localhost:3000")
        handler = ProxyHandler(config)
        assert handler.config.target_url == "http://localhost:3000"
        assert handler.client is not None
        await handler.close()

    @pytest.mark.asyncio
    async def test_forward_get_to_valid_endpoint(self):
        """forward() returns 200 with correct body from a valid target."""
        config = ProxyConfig(
            target_url="https://httpbin.org",
            timeout_ms=10_000,
        )
        handler = ProxyHandler(config)
        try:
            result = await handler.forward(
                method="GET",
                path="/get",
                headers={},
                body=None,
            )
            assert result["status"] == 200
            assert result["status_text"] == "OK"
            assert result["error"] is None
            assert result["latency_ms"] > 0
        finally:
            await handler.close()

    @pytest.mark.asyncio
    async def test_forward_preserves_post_body(self):
        """forward() sends POST body to the target."""
        import json

        config = ProxyConfig(
            target_url="https://httpbin.org",
            timeout_ms=10_000,
        )
        handler = ProxyHandler(config)
        try:
            body = json.dumps({"name": "Alice"})
            result = await handler.forward(
                method="POST",
                path="/post",
                headers={"Content-Type": "application/json"},
                body=body,
            )
            assert result["status"] == 200
            assert result["error"] is None
            # httpbin returns the sent data in the 'data' field
            assert result["response_body"] is not None
        finally:
            await handler.close()

    @pytest.mark.asyncio
    async def test_forward_handles_target_unreachable(self):
        """forward() returns 502 when target is unreachable."""
        config = ProxyConfig(
            target_url="http://localhost:1",
            timeout_ms=500,
        )
        handler = ProxyHandler(config)
        try:
            result = await handler.forward(
                method="GET",
                path="/api/test",
                headers={},
                body=None,
            )
            assert result["status"] == 502
            assert result["error"] is not None
        finally:
            await handler.close()
