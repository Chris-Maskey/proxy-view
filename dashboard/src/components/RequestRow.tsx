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

export default function RequestRow({ request, selected, onSelect }: Props) {
	const loading = !request.is_completed && !request.is_error;
	const isError = request.is_error;

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
		</div>
	);
}
