export function formatBytes(bytes?: number | null): string {
	if (bytes == null) return "\u2014";
	if (bytes === 0) return "0 B";
	const units = ["B", "KB", "MB", "GB"];
	const i = Math.floor(Math.log(bytes) / Math.log(1024));
	return `${(bytes / 1024 ** i).toFixed(1)} ${units[i]}`;
}

export function latencyColor(ms: number | undefined | null): string {
	if (ms == null || ms < 0) return "var(--text-dim)";
	if (ms < 100) return "var(--latency-fast)";
	if (ms < 500) return "var(--latency-medium)";
	return "var(--latency-slow)";
}

export function statusColor(status?: number): string {
	if (!status) return "var(--text-dim)";
	if (status < 200) return "var(--text-dim)";
	if (status < 300) return "var(--status-2xx)";
	if (status < 400) return "var(--status-3xx)";
	if (status < 500) return "var(--status-4xx)";
	return "var(--status-5xx)";
}

const METHOD_COLORS: Record<string, string> = {
	GET: "var(--method-get)",
	POST: "var(--method-post)",
	PUT: "var(--method-put)",
	PATCH: "var(--method-patch)",
	DELETE: "var(--method-delete)",
};

export function methodColor(method: string | undefined | null): string {
	if (!method) return "var(--text-secondary)";
	return METHOD_COLORS[method.toUpperCase()] ?? "var(--text-secondary)";
}

export function formatLatency(ms?: number): string {
	if (ms == null) return "\u2014";
	if (ms < 1000) return `${ms.toFixed(0)}ms`;
	return `${(ms / 1000).toFixed(2)}s`;
}
