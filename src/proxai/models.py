"""Pydantic event models for Proxai events."""

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RequestStarted(BaseModel):
    """Emitted when a proxied request begins."""

    type: str = "request.started"
    request_id: str = Field(..., min_length=1)
    method: str
    url: str
    path: str
    query: Optional[str] = None
    headers: Optional[dict[str, str]] = None
    body: Optional[str] = None
    timestamp: datetime = Field(default_factory=_now)


class RequestCompleted(BaseModel):
    """Emitted when a proxied request completes successfully."""

    type: str = "request.completed"
    request_id: str = Field(..., min_length=1)
    method: str
    url: str
    status: int
    status_text: str
    response_headers: Optional[dict[str, str]] = None
    response_body: Optional[str] = None
    latency_ms: float = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=_now)

    @field_validator("latency_ms")
    @classmethod
    def latency_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("latency_ms must be >= 0")
        return v


class RequestError(BaseModel):
    """Emitted when a proxied request fails."""

    type: str = "request.error"
    request_id: str = Field(..., min_length=1)
    method: str
    url: str
    error: str
    timestamp: datetime = Field(default_factory=_now)
