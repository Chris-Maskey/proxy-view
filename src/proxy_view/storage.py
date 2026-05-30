"""SQLite storage for proxied requests."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Optional

import aiosqlite

from proxy_view.models import RequestCompleted, RequestError, RequestStarted

logger = logging.getLogger(__name__)

Schema = """
CREATE TABLE IF NOT EXISTS requests (
    request_id TEXT PRIMARY KEY,
    method TEXT NOT NULL,
    url TEXT NOT NULL,
    path TEXT NOT NULL,
    query TEXT,
    request_headers TEXT,
    request_body TEXT,
    status INTEGER,
    status_text TEXT,
    response_headers TEXT,
    response_body TEXT,
    latency_ms REAL,
    error TEXT,
    session_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_requests_method ON requests(method);
CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status);
CREATE INDEX IF NOT EXISTS idx_requests_path ON requests(path);
CREATE INDEX IF NOT EXISTS idx_requests_session ON requests(session_id);
"""


class Storage:
    """SQLite storage for proxied requests.

    Writes are non-blocking relative to the proxy — this class is called
    from a background subscriber, not the request path.
    """

    def __init__(self, db_path: str, session_id: str | None = None) -> None:
        self.db_path = db_path
        self.session_id = session_id or datetime.now().strftime("%Y%m%d-%H%M%S")
        self._conn: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        """Open the database and create schema."""
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.executescript(Schema)
        await self._conn.commit()

    async def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def store_event(self, event: RequestStarted | RequestCompleted | RequestError) -> None:
        """Persist an event to the database.

        For started events, inserts a new row.
        For completed/error events, updates the existing row.
        """
        conn = self._conn
        if conn is None:
            raise RuntimeError("Storage not initialized")

        if isinstance(event, RequestStarted):
            await self._do_insert_started(conn, event)
        elif isinstance(event, RequestCompleted):
            await self._do_update_completed(conn, event)
        elif isinstance(event, RequestError):
            await self._do_update_error(conn, event)

    async def _do_insert_started(
        self, conn: aiosqlite.Connection, event: RequestStarted
    ) -> None:
        """Insert a new request row."""
        await conn.execute(
            """INSERT OR IGNORE INTO requests
               (request_id, method, url, path, query,
                request_headers, request_body, session_id, started_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event.request_id,
                event.method,
                event.url,
                event.path,
                event.query,
                json.dumps(event.headers) if event.headers else None,
                event.body,
                self.session_id,
                event.timestamp.isoformat(),
            ),
        )
        await conn.commit()

    async def _do_update_completed(
        self, conn: aiosqlite.Connection, event: RequestCompleted
    ) -> None:
        """Update a request row with completion data."""
        await conn.execute(
            """UPDATE requests SET
               status = ?, status_text = ?,
               response_headers = ?, response_body = ?,
               latency_ms = ?, completed_at = ?
               WHERE request_id = ?""",
            (
                event.status,
                event.status_text,
                json.dumps(event.response_headers) if event.response_headers else None,
                event.response_body,
                event.latency_ms,
                event.timestamp.isoformat(),
                event.request_id,
            ),
        )
        await conn.commit()

    async def _do_update_error(
        self, conn: aiosqlite.Connection, event: RequestError
    ) -> None:
        """Update a request row with an error, or insert if not yet tracked."""
        cursor = await conn.execute(
            "UPDATE requests SET error = ?, completed_at = ? WHERE request_id = ?",
            (event.error, event.timestamp.isoformat(), event.request_id),
        )
        if cursor.rowcount == 0:
            # No existing row — insert as a standalone error event
            await conn.execute(
                """INSERT OR IGNORE INTO requests
                   (request_id, method, url, path, query,
                    request_headers, request_body, error,
                    session_id, started_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.request_id,
                    event.method,
                    event.url,
                    event.url,
                    None,
                    None,
                    None,
                    event.error,
                    self.session_id,
                    event.timestamp.isoformat(),
                    event.timestamp.isoformat(),
                ),
            )
        await conn.commit()

    async def get_request(self, request_id: str) -> dict[str, Any] | None:
        """Retrieve a single request by ID."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Storage not initialized")

        cursor = await conn.execute(
            "SELECT * FROM requests WHERE request_id = ?",
            (request_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    async def list_requests(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List stored requests with pagination."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Storage not initialized")

        cursor = await conn.execute(
            "SELECT * FROM requests ORDER BY started_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def clear_session(self) -> None:
        """Delete all requests for the current session."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Storage not initialized")

        await conn.execute("DELETE FROM requests WHERE session_id = ?", (self.session_id,))
        await conn.commit()
