# proxy-view

**A CLI-first API debugging proxy** — intercept, inspect, replay, and debug HTTP traffic
in real-time from your terminal or browser dashboard.

```bash
pip install proxy-view
proxy-view --target http://localhost:3000 --port 9090
```

---

## Quick Start

```bash
# Start the proxy
proxy-view --target https://jsonplaceholder.typicode.com --port 9090

# In another terminal, make requests through the proxy
curl http://localhost:9090/posts
curl http://localhost:9090/posts/1
curl http://localhost:9090/posts/1/comments

# Press Ctrl+C to stop
```

The terminal shows a live-updating table with colored method/status/latency for every request.

### Open the Dashboard

Add `-d` to open the React dashboard in your browser:

```bash
proxy-view --target http://localhost:3000 --port 9090 -d
```

### Replay a Request

```bash
# Replay from the command line
proxy-view replay <request-id> --port 9090

# With diff mode (compare original vs replayed response)
proxy-view replay <request-id> --port 9090 --diff

# Or click the ↻ replay button in the dashboard
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Reverse proxy** | Forwards HTTP requests to any target URL — no system proxy config needed |
| **Real-time streaming** | Live CLI table + WebSocket event stream to the dashboard |
| **Request history** | All requests stored in SQLite with WAL mode (auto-purged after 7 days) |
| **Replay engine** | Re-send any captured request through the proxy, with --diff support |
| **Browser dashboard** | Full DevTools-style UI: request list, detail panel with Headers/Body/Timing tabs |
| **No config required** | Works out of the box — no config files, no SSL certs |

---

## CLI Reference

```bash
# Global options (passed before any command)
proxy-view --target URL --port PORT [--db PATH] [--dashboard]

# Commands
proxy-view replay REQUEST_ID --port PORT [--diff]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--target` | `-t` | `http://localhost:3000` | Target URL to forward requests to |
| `--port` | `-p` | `9090` | Port to run the proxy on |
| `--db` | | `~/.proxy-view/db.sqlite` | Path to SQLite database |
| `--dashboard` | `-d` | `false` | Open the React dashboard in browser |

### Replay Command

| Argument | Description |
|----------|-------------|
| `REQUEST_ID` | The ID of a previously captured request (required) |
| `--port` | Port of the running proxy server (default: 9090) |
| `--diff` | Show a diff between the original and replayed response |

---

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Your App   │ ──► │  proxy-view      │ ──► │  Target API  │
│  (client)   │     │  :9090           │     │  (server)    │
└─────────────┘     └──────────────────┘     └──────────────┘
                         │        ▲
                         │        │
                    ┌────▼────────┴────┐
                    │  WebSocket Hub   │
                    │  /ws             │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌────────────┐
        │  CLI     │  │Dashboard │  │  SQLite    │
        │  Viewer  │  │ (React)  │  │  Storage   │
        └──────────┘  └──────────┘  └────────────┘
```

### Layers

1. **Proxy Core** (httpx) — Forwards requests, handles 502/504 errors, connection pooling
2. **Event Hub** (WebSocket) — `ConnectionManager` broadcasts `request.started`, `request.completed`, `request.error` events
3. **Storage** (SQLite/aiosqlite) — WAL mode, CRUD with pagination, 7-day session auto-cleanup
4. **CLI** (Typer + Rich) — Live-updating table with colored method/status/latency, stats bar
5. **Dashboard** (React + Vite) — DevTools-style UI with WebSocket auto-reconnect, 3-tab detail panel, replay button

---

## Requirements

- Python 3.11+
- Works on macOS, Linux, Windows

## License

MIT
