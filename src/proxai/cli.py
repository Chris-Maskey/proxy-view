"""CLI entrypoint for Proxai — Typer + Rich Live display."""

from __future__ import annotations

import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text

app = typer.Typer(
    name="proxai",
    help="A CLI-first API debugging proxy with real-time WebSocket streaming.",
)
console = Console()

PROXAI_DIR = Path.home() / ".proxai"


def _get_proxai_dir() -> Path:
    """Ensure .proxai directory exists in user's home."""
    PROXAI_DIR.mkdir(parents=True, exist_ok=True)
    return PROXAI_DIR


def _create_table() -> Table:
    """Create a Rich table for the live traffic display."""
    table = Table(
        show_header=True,
        header_style="bold",
        box=None,
        padding=(0, 1),
        show_edge=False,
        expand=True,
    )
    table.add_column("Method", width=8, no_wrap=True)
    table.add_column("Path", width=60, no_wrap=True)
    table.add_column("Status", justify="right", width=6)
    table.add_column("Latency", justify="right", width=10)
    table.add_column("Time", width=12)
    return table


def _method_style(method: str) -> str:
    """Return the Rich style for an HTTP method."""
    styles = {
        "GET": "green",
        "POST": "blue",
        "PUT": "orange1",
        "PATCH": "magenta",
        "DELETE": "red",
        "HEAD": "grey70",
        "OPTIONS": "grey70",
    }
    return styles.get(method.upper(), "white")


def _status_style(status: int) -> str:
    """Return the Rich style for an HTTP status code."""
    if status < 200:
        return "grey70"
    elif status < 300:
        return "green"
    elif status < 400:
        return "yellow"
    elif status < 500:
        return "orange1"
    else:
        return "red"


def _latency_style(latency_ms: float) -> str:
    """Return the Rich style for a latency value."""
    if latency_ms < 100:
        return "green"
    elif latency_ms < 500:
        return "yellow"
    else:
        return "red"


@app.command()
def start(
    target: str = typer.Option(
        "http://localhost:3000",
        "--target",
        "-t",
        help="Target URL to forward requests to.",
    ),
    port: int = typer.Option(
        9090,
        "--port",
        "-p",
        help="Port to run the proxy on.",
    ),
    db_path: Optional[str] = typer.Option(
        None,
        "--db",
        help="Path to SQLite database (default: ~/.proxai/db.sqlite).",
    ),
    dashboard: bool = typer.Option(
        False,
        "--dashboard",
        "-d",
        help="Open the React dashboard in a browser.",
    ),
) -> None:
    """Start the Proxai proxy server and live CLI viewer."""
    _get_proxai_dir()
    run = os.environ.get("PROXAI_RUN")  # internal flag for testing
    if run != "server":
        _run_cli(target=target, port=port, db_path=db_path, dashboard=dashboard)


def _run_cli(
    target: str,
    port: int,
    db_path: Optional[str] = None,
    dashboard: bool = False,
) -> None:
    """Run the CLI: start server subprocess, health check, connect WS, show live display."""
    resolved_db = db_path or str(PROXAI_DIR / "db.sqlite")

    # Launch the Uvicorn server as a subprocess
    server_env = os.environ.copy()
    server_env["PROXAI_TARGET"] = target
    if db_path:
        server_env["PROXAI_DB_PATH"] = db_path
    server_args = [
        sys.executable,
        "-m",
        "uvicorn",
        "proxai.server:create_app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--log-level",
        "error",
        "--factory",
    ]

    console.print(f"[dim]Starting Proxai on port {port} → {target}...[/dim]")

    server_proc = subprocess.Popen(
        server_args,
        env=server_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    try:
        # Health-check loop
        _wait_for_health(port)

        # Open dashboard in browser if requested
        if dashboard:
            import webbrowser
            dashboard_url = f"http://127.0.0.1:{port}/dashboard/?port={port}&target={target}"
            console.print(f"[blue]Opening dashboard: {dashboard_url}[/blue]")
            webbrowser.open(dashboard_url)

        # Connect WebSocket and show live display
        asyncio.run(_run_live_display(port, target))
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
    finally:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()


def _wait_for_health(port: int, timeout: float = 10.0) -> None:
    """Poll the /health endpoint until the server is ready."""
    import http.client

    start = time.monotonic()
    while time.monotonic() - start < timeout:
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
            conn.request("GET", "/health")
            resp = conn.getresponse()
            if resp.status == 200:
                console.print("[green]✓ Proxy is ready[/green]")
                return
            conn.close()
        except (ConnectionRefusedError, OSError, http.client.HTTPException):
            pass
        time.sleep(0.3)

    console.print("[red]✗ Proxy failed to start. Check the port is available.[/red]")
    sys.exit(1)


async def _run_live_display(port: int, target: str) -> None:
    """Connect WebSocket and display live traffic."""
    import json
    from datetime import datetime

    from websockets.asyncio.client import connect as ws_connect

    ws_url = f"ws://127.0.0.1:{port}/ws"

    console.print(f"[green]✓ WebSocket connected to {ws_url}[/green]")
    console.print(f"[dim]Target: {target} | Press Ctrl+C to stop[/dim]\n")

    # Stats tracking
    stats = {"total": 0, "errors": 0, "latencies": []}
    recent_requests: list[dict] = []

    table = _create_table()

    try:
        async with ws_connect(ws_url) as ws:
            # Read the connected message
            connected = await ws.recv()

            with Live(table, refresh_per_second=10, console=console) as live:
                async for message in ws:
                    try:
                        data = json.loads(message)
                        event_type = data.get("type")

                        if event_type == "request.started":
                            pass  # We'll show on completed
                        elif event_type == "request.completed":
                            method = data.get("method", "?")
                            path = data.get("url", "/")
                            status = data.get("status", 0)
                            latency = data.get("latency_ms", 0)

                            stats["total"] += 1
                            stats["latencies"].append(latency)

                            # Add to recent requests
                            req = {
                                "method": method,
                                "path": path,
                                "status": status,
                                "latency": latency,
                                "time": datetime.now().strftime("%H:%M:%S"),
                            }
                            recent_requests.insert(0, req)
                            if len(recent_requests) > 100:
                                recent_requests.pop()

                            # Rebuild table
                            table = _create_table()
                            for r in recent_requests:
                                method_text = Text(
                                    r["method"],
                                    style=_method_style(r["method"]),
                                )
                                path_text = Text(r["path"])
                                status_text = Text(
                                    str(r["status"]),
                                    style=_status_style(r["status"]),
                                )
                                latency_text = Text(
                                    f"{r['latency']:.0f}ms",
                                    style=_latency_style(r["latency"]),
                                )
                                time_text = Text(r["time"], style="dim")
                                table.add_row(
                                    method_text,
                                    path_text,
                                    status_text,
                                    latency_text,
                                    time_text,
                                )

                            # Add stats summary row
                            avg_latency = (
                                sum(stats["latencies"]) / len(stats["latencies"])
                                if stats["latencies"]
                                else 0
                            )
                            summary = Text(
                                f"Total: {stats['total']} requests | "
                                f"Avg latency: {avg_latency:.0f}ms | "
                                f"Target: {target}",
                                style="dim",
                            )
                            live.update(table)

                        elif event_type == "request.error":
                            stats["total"] += 1
                            stats["errors"] += 1

                    except json.JSONDecodeError:
                        pass

    except Exception as e:
        console.print(f"[red]Connection error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    app()
