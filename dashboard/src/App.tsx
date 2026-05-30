import { useWebSocket } from "./hooks/useWebSocket";
import { useRequests } from "./hooks/useRequests";
import WelcomeScreen from "./components/WelcomeScreen";
import RequestList from "./components/RequestList";
import DetailPanel from "./components/DetailPanel";
import StatusBar from "./components/StatusBar";
import "./App.css";

function getProxyConfig() {
	const params = new URLSearchParams(window.location.search);
	return {
		port: parseInt(params.get("port") || "9090", 10),
		targetUrl: params.get("target") || "unknown",
	};
}

export default function App() {
	const { port, targetUrl } = getProxyConfig();
	// Use same hostname as the page to avoid cross-origin WS issues
	const wsUrl = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.hostname}:${port}/ws`;
	const {
		requests,
		selectedId,
		stats,
		addEvent,
		selectRequest,
		clearSelection,
	} = useRequests();
	const { connected } = useWebSocket(wsUrl, addEvent as (e: unknown) => void);

	const selectedRequest = selectedId
		? (requests.find((r) => r.request_id === selectedId) ?? null)
		: null;

	const hasRequests = requests.length > 0;

	return (
		<div className="app">
			<div className="app-main">
				<div className="app-list">
					{hasRequests ? (
						<RequestList
							requests={requests}
							selectedId={selectedId}
							onSelect={selectRequest}
						/>
					) : (
						<WelcomeScreen proxyPort={port} targetUrl={targetUrl} />
					)}
				</div>
				{selectedRequest && (
					<div className="app-detail">
						<DetailPanel request={selectedRequest} onClose={clearSelection} />
					</div>
				)}
			</div>
			<StatusBar stats={stats} connected={connected} targetUrl={targetUrl} />
		</div>
	);
}
