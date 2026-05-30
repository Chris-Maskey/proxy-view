import { describe, it, expect, vi, beforeAll } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "./App";

// Mock the WebSocket hook to avoid real connections
vi.mock("./hooks/useWebSocket", () => ({
	useWebSocket: vi.fn(() => ({ connected: false, error: null })),
}));

// Mock URL query params
beforeAll(() => {
	Object.defineProperty(window, "location", {
		value: { search: "?port=9090&target=http://localhost:3000" },
		writable: true,
	});
});

describe("App", () => {
	it("renders welcome screen when no requests", () => {
		render(<App />);
		expect(screen.getByText(/proxy-view/i)).toBeInTheDocument();
		expect(screen.getByText(/waiting/i)).toBeInTheDocument();
	});

	it("renders status bar", () => {
		render(<App />);
		expect(screen.getByText(/Disconnected/i)).toBeInTheDocument();
	});
});
