import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import RequestList from "./RequestList";

const mockRequests = [
	{
		request_id: "1",
		method: "GET",
		url: "/api/users",
		path: "/api/users",
		status: 200,
		status_text: "OK",
		latency_ms: 42,
		started_at: new Date().toISOString(),
		is_completed: true,
		is_error: false,
	},
	{
		request_id: "2",
		method: "POST",
		url: "/api/login",
		path: "/api/login",
		status: 401,
		status_text: "Unauthorized",
		latency_ms: 15,
		started_at: new Date().toISOString(),
		is_completed: true,
		is_error: false,
	},
];

describe("RequestList", () => {
	it("renders request rows", () => {
		render(
			<RequestList
				requests={mockRequests}
				selectedId={null}
				onSelect={() => {}}
			/>,
		);
		expect(screen.getByText("/api/users")).toBeInTheDocument();
		expect(screen.getByText("/api/login")).toBeInTheDocument();
	});

	it("calls onSelect when a row is clicked", () => {
		const onSelect = vi.fn();
		render(
			<RequestList
				requests={mockRequests}
				selectedId={null}
				onSelect={onSelect}
			/>,
		);
		fireEvent.click(screen.getByText("/api/users"));
		expect(onSelect).toHaveBeenCalledWith("1");
	});
});
