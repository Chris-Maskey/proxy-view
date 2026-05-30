import type { RequestEntry } from "../types";
import RequestRow from "./RequestRow";
import "./RequestList.css";

interface Props {
	requests: RequestEntry[];
	selectedId: string | null;
	onSelect: (id: string) => void;
}

export default function RequestList({ requests, selectedId, onSelect }: Props) {
	if (requests.length === 0) return null;

	return (
		<div className="request-list" role="listbox" aria-label="Request list">
			<div className="request-list-header">
				<span style={{ width: 60 }} className="request-list-header-label">
					Method
				</span>
				<span style={{ flex: 1 }} className="request-list-header-label">
					Path
				</span>
				<span
					style={{ width: 40, textAlign: "right" }}
					className="request-list-header-label"
				>
					Status
				</span>
				<span
					style={{ width: 70, textAlign: "right" }}
					className="request-list-header-label"
				>
					Latency
				</span>
			</div>
			{requests.map((req) => (
				<RequestRow
					key={req.request_id}
					request={req}
					selected={req.request_id === selectedId}
					onSelect={onSelect}
				/>
			))}
		</div>
	);
}
