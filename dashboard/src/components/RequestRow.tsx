import { useState, useCallback } from "react";
import type { RequestEntry } from "../types";
import {
	methodColor,
	statusColor,
	latencyColor,
	formatLatency,
} from "../utils/formatters";
import "./RequestRow.css";

interface Props {
	request: RequestEntry;
	selected: boolean;
	onSelect: (id: string) => void;
}

function getReplayUrl(requestId: string): string {
	const port =
		new URLSearchParams(window.location.search).get("port") || "9090";
	return `http://127.0.0.1:${port}/replay/${requestId}`;
}

export default function RequestRow({ request, selected, onSelect }: Props) {
	const [replayState, setReplayState] = useState<
		"idle" | "replaying" | "done"
	>("idle");
	const loading = !request.is_completed && !request.is_error;
	const isError = request.is_error;

	const handleReplay = useCallback(
		async (e: React.MouseEvent) => {
			e.stopPropagation();
			if (replayState !== "idle") return;
			setReplayState("replaying");
			try {
				const resp = await fetch(getReplayUrl(request.request_id), {
					method: "POST",
				});
				if (resp.ok) {
					setReplayState("done");
					setTimeout(() => setReplayState("idle"), 2000);
				} else {
					setReplayState("idle");
				}
			} catch {
				setReplayState("idle");
			}
		},
		[request.request_id, replayState],
	);

	return (
		<div
			className={`request-row${selected ? " request-row--selected" : ""}`}
			data-selected={selected || undefined}
			onClick={() => onSelect(request.request_id)}
			role="button"
			tabIndex={0}
			onKeyDown={(e) => e.key === "Enter" && onSelect(request.request_id)}
			aria-selected={selected}
		>
			<span
				className="request-method"
				style={{ color: methodColor(request.method) }}
			>
				{request.method}
			</span>
			<span className="request-path">{request.path}</span>
			<span
				className="request-status"
				style={{ color: statusColor(request.status) }}
			>
				{loading ? "\u2026" : isError ? "ERR" : request.status}
			</span>
			<span
				className="request-latency"
				style={{ color: latencyColor(request.latency_ms ?? 0) }}
			>
				{formatLatency(request.latency_ms)}
			</span>
			<button
				className={`request-replay-btn${
					replayState !== "idle" ? " request-replay-btn--active" : ""
				}`}
				onClick={handleReplay}
				title="Replay this request"
				aria-label="Replay request"
			>
				{replayState === "idle"
					? "\u21bb"
					: replayState === "replaying"
						? "\u2026"
						: "\u2713"}
			</button>
		</div>
	);
}
