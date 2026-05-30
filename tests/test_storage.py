"""Tests for SQLite storage layer."""

import os
import tempfile

import pytest
import pytest_asyncio

from proxai.models import RequestCompleted, RequestError, RequestStarted
from proxai.storage import Storage


@pytest_asyncio.fixture
async def db_path() -> str:
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest_asyncio.fixture
async def storage(db_path: str) -> Storage:
    """Create a Storage instance with the temp database."""
    store = Storage(db_path=db_path)
    await store.initialize()
    yield store
    await store.close()


class TestStorageInitialization:
    @pytest.mark.asyncio
    async def test_initialize_creates_tables(self, db_path: str):
        """initialize() creates the requests table."""
        store = Storage(db_path=db_path)
        await store.initialize()
        await store.close()
        assert os.path.exists(db_path)

    @pytest.mark.asyncio
    async def test_initialize_is_idempotent(self, db_path: str):
        """initialize() can be called multiple times safely."""
        store = Storage(db_path=db_path)
        await store.initialize()
        await store.initialize()  # second call should not raise
        await store.close()


class TestStorageWrite:
    @pytest.mark.asyncio
    async def test_store_event_saves_request(self, storage: Storage):
        """store_event() persists a request to the database."""
        event = RequestStarted(
            request_id="test-1",
            method="GET",
            url="/api/users",
            path="/api/users",
        )
        await storage.store_event(event)

        # Verify by reading back
        stored = await storage.get_request("test-1")
        assert stored is not None
        assert stored["request_id"] == "test-1"
        assert stored["method"] == "GET"
        assert stored["path"] == "/api/users"
        assert stored["error"] is None

    @pytest.mark.asyncio
    async def test_store_completed_event(self, storage: Storage):
        """store_event() persists a completed request with status."""
        # First store the started event
        started = RequestStarted(
            request_id="test-2",
            method="POST",
            url="/api/data",
            path="/api/data",
        )
        await storage.store_event(started)

        # Then store the completed event
        completed = RequestCompleted(
            request_id="test-2",
            method="POST",
            url="/api/data",
            status=201,
            status_text="Created",
            latency_ms=150,
        )
        await storage.store_event(completed)

        # Verify merged state
        stored = await storage.get_request("test-2")
        assert stored is not None
        assert stored["request_id"] == "test-2"
        assert stored["status"] == 201
        assert stored["latency_ms"] == 150.0

    @pytest.mark.asyncio
    async def test_store_error_event(self, storage: Storage):
        """store_event() persists an error event."""
        error = RequestError(
            request_id="test-3",
            method="GET",
            url="/api/nonexistent",
            error="Connection refused",
        )
        await storage.store_event(error)

        stored = await storage.get_request("test-3")
        assert stored is not None
        assert stored["error"] == "Connection refused"


class TestStorageRead:
    @pytest.mark.asyncio
    async def test_get_request_returns_none_for_missing(self, storage: Storage):
        """get_request() returns None for unknown request_id."""
        result = await storage.get_request("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_requests_returns_all(self, storage: Storage):
        """list_requests() returns all stored requests."""
        # Store multiple requests
        for i in range(3):
            event = RequestStarted(
                request_id=f"list-{i}",
                method="GET",
                url=f"/api/{i}",
                path=f"/api/{i}",
            )
            await storage.store_event(event)

        results = await storage.list_requests()
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_list_requests_pagination(self, storage: Storage):
        """list_requests() supports limit and offset."""
        for i in range(5):
            event = RequestStarted(
                request_id=f"page-{i}",
                method="GET",
                url=f"/api/{i}",
                path=f"/api/{i}",
            )
            await storage.store_event(event)

        page1 = await storage.list_requests(limit=2, offset=0)
        assert len(page1) == 2

        page2 = await storage.list_requests(limit=2, offset=2)
        assert len(page2) == 2
        assert page2[0]["request_id"] != page1[0]["request_id"]


class TestStorageCleanup:
    @pytest.mark.asyncio
    async def test_clear_session(self, storage: Storage):
        """clear_session() removes all requests."""
        event = RequestStarted(
            request_id="clean-1",
            method="GET",
            url="/api/1",
            path="/api/1",
        )
        await storage.store_event(event)
        await storage.clear_session()

        results = await storage.list_requests()
        assert len(results) == 0
