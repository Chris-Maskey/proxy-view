import type { RequestEntry } from "../types";
import WaterfallChart from "./WaterfallChart";
import "./TimingTab.css";

interface Props {
	request: RequestEntry;
}

export default function TimingTab({ request }: Props) {
	return (
		<div className="timing-tab">
			<h3 className="timing-section-title">Response Time</h3>
			<WaterfallChart request={request} />

			<div className="timing-details">
				<div className="timing-row">
					<span className="timing-label">Status</span>
					<span className="timing-value">
						{request.status} {request.status_text}
					</span>
				</div>
				<div className="timing-row">
					<span className="timing-label">Latency</span>
					<span className="timing-value">
						{request.latency_ms?.toFixed(0)}ms
					</span>
				</div>
				<div className="timing-row">
					<span className="timing-label">Completed</span>
					<span className="timing-value">
						{request.completed_at || "\u2014"}
					</span>
				</div>
			</div>
		</div>
	);
}
