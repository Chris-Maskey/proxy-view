"""Configuration models for proxy-view."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProxyConfig:
    """Configuration for the HTTP proxy."""

    target_url: str
    timeout_ms: int = 30_000  # 30 seconds default timeout
