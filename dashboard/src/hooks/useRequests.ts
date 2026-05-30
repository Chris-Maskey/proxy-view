import { useState, useCallback, useRef } from "react";
import type { RequestEvent, RequestEntry } from "../types";

const MAX_REQUESTS = 500;

function buildEntry(event: RequestEvent): RequestEntry {
	const base = {
		request_id: event.request_id,
		method: event.method,
		url: event.url,
		started_at: event.timestamp,
	};
	if (event.type === "request.started") {
		return {
			...base,
			path: event.path,
			query: event.query,
			request_headers: event.headers,
			request_body: event.body,
			is_completed: false,
			is_error: false,
		};
	}
	if (event.type === "request.completed") {
		return {
			...base,
			path: event.url,
			status: event.status,
			status_text: event.status_text,
			response_headers: event.response_headers,
			response_body: event.response_body,
			latency_ms: event.latency_ms,
			completed_at: event.timestamp,
			is_completed: true,
			is_error: false,
		};
	}
	return {
		...base,
		path: event.url,
		error: event.error,
		is_completed: false,
		is_error: true,
	};
}

export function useRequests() {
	const [requests, setRequests] = useState<RequestEntry[]>([]);
	const [selectedId, setSelectedId] = useState<string | null>(null);
	const [stats, setStats] = useState({ total: 0, errors: 0, avgLatency: 0 });
	const requestsRef = useRef<RequestEntry[]>([]);

	const addEvent = useCallback((event: RequestEvent) => {
		// Ignore non-request events (e.g. { type: "connected" })
		if (
			event.type !== "request.started" &&
			event.type !== "request.completed" &&
			event.type !== "request.error"
		) {
			return;
		}

		if (event.type === "request.completed" || event.type === "request.error") {
			requestsRef.current = requestsRef.current.map((r) => {
				if (
					r.request_id === event.request_id &&
					!r.is_completed &&
					!r.is_error
				) {
					const update = buildEntry(event);
					return { ...r, ...update };
				}
				return r;
			});
			const exists = requestsRef.current.some(
				(r) => r.request_id === event.request_id,
			);
			if (!exists) {
				requestsRef.current = [buildEntry(event), ...requestsRef.current];
			}
		} else {
			const exists = requestsRef.current.some(
				(r) => r.request_id === event.request_id,
			);
			if (!exists) {
				requestsRef.current = [buildEntry(event), ...requestsRef.current];
			}
		}

		if (requestsRef.current.length > MAX_REQUESTS) {
			requestsRef.current = requestsRef.current.slice(0, MAX_REQUESTS);
		}

		const completed = requestsRef.current.filter((r) => r.is_completed);
		const total = requestsRef.current.length;
		const errors = requestsRef.current.filter((r) => r.is_error).length;
		const avgLatency =
			completed.length > 0
				? completed.reduce((sum, r) => sum + (r.latency_ms ?? 0), 0) /
					completed.length
				: 0;

		setRequests([...requestsRef.current]);
		setStats({ total, errors, avgLatency });
	}, []);

	const selectRequest = useCallback((id: string) => setSelectedId(id), []);
	const clearSelection = useCallback(() => setSelectedId(null), []);

	return {
		requests,
		selectedId,
		stats,
		addEvent,
		selectRequest,
		clearSelection,
	};
}
