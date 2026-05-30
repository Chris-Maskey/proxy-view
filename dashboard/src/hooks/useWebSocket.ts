import { useEffect, useRef, useState, useCallback } from "react";

type EventHandler = (event: any) => void;

export function useWebSocket(url: string, onEvent: EventHandler) {
	const [connected, setConnected] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const wsRef = useRef<WebSocket | null>(null);
	const reconnectTimer = useRef<ReturnType<typeof setTimeout> | undefined>(
		undefined,
	);

	const connect = useCallback(() => {
		try {
			const ws = new WebSocket(url);
			wsRef.current = ws;

			ws.addEventListener("open", () => {
				setConnected(true);
				setError(null);
			});

			ws.addEventListener("message", (event) => {
				try {
					const data = JSON.parse(event.data);
					onEvent(data);
				} catch {
					// ignore malformed messages
				}
			});

			ws.addEventListener("error", () => {
				setError("WebSocket connection error");
				setConnected(false);
			});

			ws.addEventListener("close", () => {
				setConnected(false);
				reconnectTimer.current = setTimeout(() => {
					connect();
				}, 2000);
			});
		} catch (e) {
			setError(`Failed to connect: ${e}`);
			setConnected(false);
			reconnectTimer.current = setTimeout(() => connect(), 2000);
		}
	}, [url, onEvent]);

	useEffect(() => {
		connect();
		return () => {
			clearTimeout(reconnectTimer.current);
			wsRef.current?.close();
		};
	}, [connect]);

	return { connected, error };
}
