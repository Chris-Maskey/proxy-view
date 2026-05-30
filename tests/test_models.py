"""Tests for Pydantic event models."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from proxy_view.models import (
    RequestError,
    RequestStarted,
    RequestCompleted,
)


class TestRequestStarted:
    def test_create_minimal(self):
        """Create a RequestStarted with required fields."""
        event = RequestStarted(
            request_id="abc123",
            method="GET",
            url="/api/users",
            path="/api/users",
        )
        assert event.request_id == "abc123"
        assert event.method == "GET"
        assert event.url == "/api/users"
        assert event.path == "/api/users"
        assert event.query is None
        assert event.headers is None
        assert event.body is None
        assert isinstance(event.timestamp, datetime)

    def test_create_with_all_fields(self):
        """Create a RequestStarted with all optional fields."""
        ts = datetime.now(timezone.utc)
        event = RequestStarted(
            request_id="def456",
            method="POST",
            url="/api/users",
            path="/api/users",
            query="page=1",
            headers={"Content-Type": "application/json"},
            body='{"name": "Alice"}',
            timestamp=ts,
        )
        assert event.query == "page=1"
        assert event.headers == {"Content-Type": "application/json"}
        assert event.body == '{"name": "Alice"}'
        assert event.timestamp == ts

    def test_serializes_to_json(self):
        """RequestStarted serializes to JSON via model_dump."""
        event = RequestStarted(
            request_id="abc123",
            method="GET",
            url="/api/users",
            path="/api/users",
        )
        data = event.model_dump(mode="json")
        assert data["request_id"] == "abc123"
        assert data["method"] == "GET"
        assert data["type"] == "request.started"
        assert isinstance(data["timestamp"], str)

    def test_empty_request_id_rejected(self):
        """Empty request_id should raise validation error."""
        with pytest.raises(ValidationError):
            RequestStarted(
                request_id="",
                method="GET",
                url="/api/users",
                path="/api/users",
            )


class TestRequestCompleted:
    def test_create_minimal(self):
        """Create a RequestCompleted with required fields."""
        event = RequestCompleted(
            request_id="abc123",
            method="GET",
            url="/api/users",
            status=200,
            status_text="OK",
            latency_ms=42,
        )
        assert event.status == 200
        assert event.latency_ms == 42.0

    def test_preserves_method_and_url(self):
        """Completed event carries method/url from the original request."""
        event = RequestCompleted(
            request_id="abc123",
            method="POST",
            url="/api/users",
            status=201,
            status_text="Created",
            latency_ms=150,
        )
        assert event.method == "POST"
        assert event.type == "request.completed"

    def test_latency_can_be_zero(self):
        """Zero latency is valid (sub-millisecond responses)."""
        event = RequestCompleted(
            request_id="abc123",
            method="GET",
            url="/api/health",
            status=200,
            status_text="OK",
            latency_ms=0,
        )
        assert event.latency_ms == 0.0

    def test_negative_latency_rejected(self):
        """Negative latency should raise validation error."""
        with pytest.raises(ValidationError):
            RequestCompleted(
                request_id="abc123",
                method="GET",
                url="/api/users",
                status=200,
                status_text="OK",
                latency_ms=-1,
            )


class TestRequestError:
    def test_create(self):
        """Create a RequestError event."""
        event = RequestError(
            request_id="abc123",
            method="GET",
            url="/api/users",
            error="Connection refused: target unreachable",
        )
        assert event.error == "Connection refused: target unreachable"
        assert event.type == "request.error"

    def test_serialization(self):
        """RequestError serializes to JSON."""
        event = RequestError(
            request_id="abc123",
            method="GET",
            url="/api/users",
            error="timeout",
        )
        data = event.model_dump(mode="json")
        assert data["type"] == "request.error"
        assert data["error"] == "timeout"
