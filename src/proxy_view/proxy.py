"""HTTP proxy forwarding handler with httpx."""

from __future__ import annotations

import json
import logging

import httpx

from proxy_view.config import ProxyConfig

logger = logging.getLogger(__name__)


class ProxyHandler:
    """Forwards HTTP requests to a target URL via httpx."""

    def __init__(self, config: ProxyConfig) -> None:
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(config.timeout_ms / 1000.0),
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
            ),
        )

    async def close(self) -> None:
        """Close the httpx client (call on server shutdown)."""
        await self.client.aclose()

    async def forward(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        body: str | None,
    ) -> dict:
        """Forward a request to the target and return the response details.

        Returns a dict with:
          - status: int
          - status_text: str
          - response_headers: dict[str, str]
          - response_body: str
          - latency_ms: float
          - error: str | None (None on success)
        """
        url = f"{self.config.target_url.rstrip('/')}/{path.lstrip('/')}"
        request_headers = {
            k: v for k, v in headers.items()
            if k.lower() not in ("host", "content-length")
        }
        content = body.encode() if body else None

        import time
        t0 = time.monotonic()

        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=request_headers,
                content=content,
            )
            latency_ms = (time.monotonic() - t0) * 1000

            # httpx auto-decompresses gzip/deflate. The headers still reflect
            # the original encoding — strip them so the downstream client
            # doesn't try to decompress an already-decompressed body.
            response_body = response.text
            response_headers = {
                k: v for k, v in response.headers.items()
                if k.lower() not in (
                    "content-encoding",
                    "transfer-encoding",
                    "content-length",
                )
            }

            return {
                "status": response.status_code,
                "status_text": response.reason_phrase or "",
                "response_headers": response_headers,
                "response_body": response_body,
                "latency_ms": round(latency_ms, 2),
                "error": None,
            }

        except httpx.ConnectError as e:
            return {
                "status": 502,
                "status_text": "Bad Gateway",
                "response_headers": {},
                "response_body": json.dumps({"error": "upstream_unreachable"}),
                "latency_ms": 0,
                "error": f"Connection refused: {e}",
            }

        except httpx.TimeoutException as e:
            return {
                "status": 504,
                "status_text": "Gateway Timeout",
                "response_headers": {},
                "response_body": json.dumps({"error": "upstream_timeout"}),
                "latency_ms": self.config.timeout_ms,
                "error": f"Target timeout: {e}",
            }

        except Exception as e:
            logger.exception("Unexpected proxy error")
            return {
                "status": 502,
                "status_text": "Bad Gateway",
                "response_headers": {},
                "response_body": json.dumps({"error": "proxy_error"}),
                "latency_ms": 0,
                "error": str(e),
            }
