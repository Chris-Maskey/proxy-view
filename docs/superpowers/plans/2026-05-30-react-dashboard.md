# React Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a DevTools-style React dashboard that connects to the Proxai WebSocket, displays live requests in a table, and provides a slide-in detail panel with Headers/Body/Timing tabs.

**Architecture:** Vite + React + TypeScript SPA in a `dashboard/` directory. WebSocket hook provides real-time events to a React context. Request list is the primary view; clicking a row slides in a detail panel. No routing library — state-driven layout with CSS transitions. DevTools dark theme via CSS custom properties.

**Tech Stack:** Vite 6, React 19, TypeScript 5, Vitest + Testing Library

**WS Event Schema:**
- `connected` — initial handshake
- `request.started` — { request_id, method, url, path, query, headers, body, timestamp }
- `request.completed` — { request_id, method, url, status, status_text, response_headers, response_body, latency_ms, timestamp }
- `request.error` — { request_id, method, url, error, timestamp }

---

### Task 1: Scaffold Vite + React project

**Files:**
- Create: `dashboard/package.json`
- Create: `dashboard/vite.config.ts`
- Create: `dashboard/tsconfig.json`
- Create: `dashboard/tsconfig.app.json`
- Create: `dashboard/tsconfig.node.json`
- Create: `dashboard/index.html`
- Create: `dashboard/src/main.tsx`
- Create: `dashboard/src/vite-env.d.ts`
- Create: `dashboard/.gitignore`

- [ ] **Step 1: Create package.json with React + Vite + Vitest deps**

```json
{
  "name": "proxai-dashboard",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.0",
    "@testing-library/react": "^16.1.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.3.0",
    "jsdom": "^25.0.0",
    "typescript": "~5.6.0",
    "vite": "^6.0.0",
    "vitest": "^2.1.0"
  }
}
```

- [ ] **Step 2: Create vite.config.ts**

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
  },
  build: {
    outDir: 'dist',
  },
})
```

- [ ] **Step 3: Create tsconfig.json**

```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}
```

- [ ] **Step 4: Create tsconfig.app.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  },
  "include": ["src"]
}
```

- [ ] **Step 5: Create tsconfig.node.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2023"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 6: Create index.html**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Proxai — API Debug Proxy</title>
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 7: Create main.tsx (minimal bootstrap)**

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- [ ] **Step 8: Create vite-env.d.ts**

```ts
/// <reference types="vite/client" />
```

- [ ] **Step 9: Create .gitignore**

```
node_modules
dist
```

- [ ] **Step 10: Install deps and verify Vite starts**

```bash
cd dashboard && npm install && npx vite --version
```

Expected: Vite version printed, no errors.

- [ ] **Step 11: Commit**

```bash
git add dashboard/
git commit -m "feat(dashboard): scaffold Vite + React + TypeScript project"
```

---

### Task 2: Design tokens + global styles (DevTools dark theme)

**Files:**
- Create: `dashboard/src/index.css`
- Create: `dashboard/src/vitest.setup.ts`

- [ ] **Step 1: Write failing test for CSS custom properties**

```ts
// dashboard/tests/setup.ts
import '@testing-library/jest-dom'
```

```bash
# Tests will use vitest --config - verify vitest works first
echo "vitest.config merged with vite.config"
```

- [ ] **Step 2: Create index.css with design tokens**

```css
/* Proxai Design Tokens — DevTools Dark Theme */
:root {
  /* Background hierarchy */
  --bg-primary: #1e1e1e;
  --bg-secondary: #252526;
  --bg-tertiary: #2d2d2d;
  --bg-hover: #2a2d2e;
  --bg-active: #37373d;
  --bg-selected: #094771;

  /* Text */
  --text-primary: #cccccc;
  --text-secondary: #969696;
  --text-dim: #6e6e6e;
  --text-inverse: #1e1e1e;

  /* Method colors */
  --method-get: #4ec9b0;
  --method-post: #569cd6;
  --method-put: #dcdcaa;
  --method-patch: #c586c0;
  --method-delete: #f44747;

  /* Status colors */
  --status-2xx: #4ec9b0;
  --status-3xx: #dcdcaa;
  --status-4xx: #ce9178;
  --status-5xx: #f44747;

  /* Latency colors (heatmap) */
  --latency-fast: #4ec9b0;
  --latency-medium: #dcdcaa;
  --latency-slow: #f44747;

  /* Borders */
  --border-primary: #3c3c3c;
  --border-secondary: #454545;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 12px;
  --spacing-lg: 16px;
  --spacing-xl: 24px;

  /* Fonts */
  --font-mono: 'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
  --font-ui: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

  /* Sizing */
  --header-height: 48px;
  --status-bar-height: 28px;
  --request-list-min-width: 400px;
  --detail-panel-width: 50%;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;

  /* Scrollbar */
  --scrollbar-thumb: #424242;
  --scrollbar-track: transparent;
}

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body, #root {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

body {
  font-family: var(--font-ui);
  font-size: 13px;
  line-height: 1.4;
  color: var(--text-primary);
  background: var(--bg-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}
::-webkit-scrollbar-track {
  background: var(--scrollbar-track);
}
::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb);
  border-radius: 5px;
}
::-webkit-scrollbar-thumb:hover {
  background: #555;
}
```

- [ ] **Step 3: Create vitest setup file at `src/vitest.setup.ts`**

```ts
import '@testing-library/jest-dom'
```

- [ ] **Step 4: Add vitest config to vite.config.ts**

```ts
/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { port: 3000, open: true },
  build: { outDir: 'dist' },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/vitest.setup.ts',
    css: true,
  },
})
```

- [ ] **Step 5: Verify vitest runs**

```bash
cd dashboard && npx vitest run
```

Expected: No tests found, exit code 0.

- [ ] **Step 6: Commit**

```bash
git add dashboard/src/index.css dashboard/src/vitest.setup.ts dashboard/vite.config.ts
git commit -m "feat(dashboard): add design tokens and DevTools dark theme"
```

---

### Task 3: TypeScript type definitions

**Files:**
- Create: `dashboard/src/types.ts`

- [ ] **Step 1: Write the types matching Pydantic event models**

```ts
// dashboard/src/types.ts — Shared types matching Proxai's Pydantic models

export interface RequestStarted {
  type: 'request.started'
  request_id: string
  method: string
  url: string
  path: string
  query?: string
  headers?: Record<string, string>
  body?: string
  timestamp: string
}

export interface RequestCompleted {
  type: 'request.completed'
  request_id: string
  method: string
  url: string
  status: number
  status_text: string
  response_headers?: Record<string, string>
  response_body?: string
  latency_ms: number
  timestamp: string
}

export interface RequestError {
  type: 'request.error'
  request_id: string
  method: string
  url: string
  error: string
  timestamp: string
}

export type RequestEvent = RequestStarted | RequestCompleted | RequestError

/** Aggregated request with both start and completed data */
export interface RequestEntry {
  request_id: string
  method: string
  url: string
  path: string
  query?: string
  request_headers?: Record<string, string>
  request_body?: string
  status?: number
  status_text?: string
  response_headers?: Record<string, string>
  response_body?: string
  latency_ms?: number
  error?: string
  started_at: string
  completed_at?: string
  is_completed: boolean
  is_error: boolean
}
```

- [ ] **Step 2: Commit**

```bash
git add dashboard/src/types.ts
git commit -m "feat(dashboard): add TypeScript types matching Pydantic event models"
```

---

### Task 4: WebSocket hook + request state hook

**Files:**
- Create: `dashboard/src/hooks/useWebSocket.ts`
- Create: `dashboard/src/hooks/useRequests.ts`
- Create: `dashboard/src/hooks/useRequests.test.ts`

- [ ] **Step 1: Write failing test for request state management**

```ts
// dashboard/src/hooks/useRequests.test.ts
import { describe, it, expect } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useRequests } from './useRequests'

const sampleCompleted = {
  type: 'request.completed' as const,
  request_id: 'abc123',
  method: 'GET',
  url: '/api/users',
  path: '/api/users',
  status: 200,
  status_text: 'OK',
  latency_ms: 42,
  timestamp: new Date().toISOString(),
}

const sampleStarted = {
  type: 'request.started' as const,
  request_id: 'abc123',
  method: 'GET',
  url: '/api/users',
  path: '/api/users',
  timestamp: new Date().toISOString(),
}

const sampleError = {
  type: 'request.error' as const,
  request_id: 'err456',
  method: 'GET',
  url: '/api/bad',
  error: 'Connection refused',
  timestamp: new Date().toISOString(),
}

describe('useRequests', () => {
  it('starts with empty list', () => {
    const { result } = renderHook(() => useRequests())
    expect(result.current.requests).toHaveLength(0)
  })

  it('adds a completed request', () => {
    const { result } = renderHook(() => useRequests())
    act(() => result.current.addEvent(sampleCompleted))
    expect(result.current.requests).toHaveLength(1)
    expect(result.current.requests[0].method).toBe('GET')
    expect(result.current.requests[0].status).toBe(200)
    expect(result.current.requests[0].is_completed).toBe(true)
  })

  it('associates started event with completed event by request_id', () => {
    const { result } = renderHook(() => useRequests())
    act(() => result.current.addEvent(sampleStarted))
    act(() => result.current.addEvent(sampleCompleted))
    expect(result.current.requests).toHaveLength(1)
    expect(result.current.requests[0].status).toBe(200)
    expect(result.current.requests[0].request_body).toBeUndefined()
  })

  it('handles errors', () => {
    const { result } = renderHook(() => useRequests())
    act(() => result.current.addEvent(sampleError))
    expect(result.current.requests).toHaveLength(1)
    expect(result.current.requests[0].is_error).toBe(true)
    expect(result.current.requests[0].error).toBe('Connection refused')
  })

  it('selects a request', () => {
    const { result } = renderHook(() => useRequests())
    act(() => result.current.addEvent(sampleCompleted))
    act(() => result.current.selectRequest('abc123'))
    expect(result.current.selectedId).toBe('abc123')
  })

  it('clears selection', () => {
    const { result } = renderHook(() => useRequests())
    act(() => result.current.addEvent(sampleCompleted))
    act(() => result.current.selectRequest('abc123'))
    act(() => result.current.clearSelection())
    expect(result.current.selectedId).toBeNull()
  })

  it('limits requests to 500', () => {
    const { result } = renderHook(() => useRequests())
    for (let i = 0; i < 510; i++) {
      act(() => result.current.addEvent({
        ...sampleCompleted,
        request_id: `req-${i}`,
        url: `/api/${i}`,
      }))
    }
    expect(result.current.requests.length).toBeLessThanOrEqual(500)
    expect(result.current.requests[0].request_id).toBe('req-509')
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd dashboard && npx vitest run src/hooks/useRequests.test.ts
```

Expected: FAIL — module not found

- [ ] **Step 3: Implement useRequests hook**

```ts
// dashboard/src/hooks/useRequests.ts
import { useState, useCallback, useRef } from 'react'
import type { RequestEvent, RequestEntry } from '../types'

const MAX_REQUESTS = 500

interface RequestsState {
  requests: RequestEntry[]
  selectedId: string | null
  stats: { total: number; errors: number; avgLatency: number }
}

function buildEntry(event: RequestEvent): RequestEntry {
  const base = {
    request_id: event.request_id,
    method: event.method,
    url: event.url,
    started_at: event.timestamp,
  }
  if (event.type === 'request.started') {
    return {
      ...base,
      path: event.path,
      query: event.query,
      request_headers: event.headers,
      request_body: event.body,
      is_completed: false,
      is_error: false,
    }
  }
  if (event.type === 'request.completed') {
    return {
      ...base,
      path: event.url,
      status: event.status,
      status_text: event.status_text,
      response_headers: event.response_headers,
      response_body: event.response_body,
      latency_ms: event.latency_ms,
      completed_at: event.timestamp,
      is_completed: true,
      is_error: false,
    }
  }
  return {
    ...base,
    path: event.url,
    error: event.error,
    is_completed: false,
    is_error: true,
  }
}

export function useRequests() {
  const [state, setState] = useState<RequestsState>({
    requests: [],
    selectedId: null,
    stats: { total: 0, errors: 0, avgLatency: 0 },
  })
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const requestsRef = useRef<RequestEntry[]>([])

  const addEvent = useCallback((event: RequestEvent) => {
    if (event.type === 'request.completed' || event.type === 'request.error') {
      // Try to merge with an existing started entry
      requestsRef.current = requestsRef.current.map(r => {
        if (r.request_id === event.request_id && !r.is_completed && !r.is_error) {
          const update = buildEntry(event)
          return { ...r, ...update }
        }
        return r
      })

      // If no started entry existed, add as new
      const exists = requestsRef.current.some(r => r.request_id === event.request_id)
      if (!exists) {
        requestsRef.current = [buildEntry(event), ...requestsRef.current]
      }
    } else {
      // started event — add new or update existing
      const exists = requestsRef.current.some(r => r.request_id === event.request_id)
      if (!exists) {
        requestsRef.current = [buildEntry(event), ...requestsRef.current]
      }
    }

    // Enforce max
    if (requestsRef.current.length > MAX_REQUESTS) {
      requestsRef.current = requestsRef.current.slice(0, MAX_REQUESTS)
    }

    // Recalculate stats
    const completed = requestsRef.current.filter(r => r.is_completed)
    const total = requestsRef.current.length
    const errors = requestsRef.current.filter(r => r.is_error).length
    const avgLatency = completed.length > 0
      ? completed.reduce((sum, r) => sum + (r.latency_ms ?? 0), 0) / completed.length
      : 0

    setState({
      requests: [...requestsRef.current],
      selectedId: null,
      stats: { total, errors, avgLatency },
    })
  }, [])

  const selectRequest = useCallback((id: string) => {
    setSelectedId(id)
  }, [])

  const clearSelection = useCallback(() => {
    setSelectedId(null)
  }, [])

  return {
    requests: state.requests,
    selectedId,
    stats: state.stats,
    addEvent,
    selectRequest,
    clearSelection,
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd dashboard && npx vitest run src/hooks/useRequests.test.ts
```

Expected: 6 tests passing

- [ ] **Step 5: Write failing test for WebSocket hook**

```ts
// dashboard/src/hooks/useWebSocket.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useWebSocket } from './useWebSocket'

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('connects and returns connected status', () => {
    const onEvent = vi.fn()
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:9090/ws', onEvent)
    )
    expect(result.current.connected).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('updates connection on ws message', () => {
    // mock WebSocket
    const mockWs = {
      send: vi.fn(),
      close: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      readyState: WebSocket.OPEN,
    }
    vi.stubGlobal('WebSocket', vi.fn(() => mockWs))
    
    const onEvent = vi.fn()
    renderHook(() => useWebSocket('ws://localhost:9090/ws', onEvent))
    
    // Simulate open
    const openHandler = mockWs.addEventListener.mock.calls.find(
      c => c[0] === 'open'
    )
    act(() => openHandler?.[1]())
    
    // After this, result.current.connected should still be false since
    // we need a re-render. Let's test through the message handler instead.
    const msgHandler = mockWs.addEventListener.mock.calls.find(
      c => c[0] === 'message'
    )
    act(() => msgHandler?.[1]({ data: JSON.stringify({ type: 'connected' }) }))
    expect(onEvent).toHaveBeenCalledWith({ type: 'connected' })
  })
})
```

- [ ] **Step 6: Implement useWebSocket hook**

```ts
// dashboard/src/hooks/useWebSocket.ts
import { useEffect, useRef, useState, useCallback } from 'react'

type EventHandler = (event: any) => void

export function useWebSocket(url: string, onEvent: EventHandler) {
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>()

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        setConnected(true)
        setError(null)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onEvent(data)
        } catch {
          // ignore malformed messages
        }
      }

      ws.onerror = () => {
        setError('WebSocket connection error')
        setConnected(false)
      }

      ws.onclose = () => {
        setConnected(false)
        // Auto-reconnect after 2 seconds
        reconnectTimer.current = setTimeout(() => {
          connect()
        }, 2000)
      }
    } catch (e) {
      setError(`Failed to connect: ${e}`)
      setConnected(false)
      // Retry
      reconnectTimer.current = setTimeout(() => {
        connect()
      }, 2000)
    }
  }, [url, onEvent])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])

  return { connected, error }
}
```

- [ ] **Step 7: Commit**

```bash
git add dashboard/src/hooks/
git commit -m "feat(dashboard): add useRequests and useWebSocket hooks"
```

---

### Task 5: Welcome screen (empty state)

**Files:**
- Create: `dashboard/src/components/WelcomeScreen.tsx`
- Create: `dashboard/src/components/WelcomeScreen.test.tsx`
- Create: `dashboard/src/components/WelcomeScreen.css`

- [ ] **Step 1: Write failing test for WelcomeScreen**

```tsx
// dashboard/src/components/WelcomeScreen.test.tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import WelcomeScreen from './WelcomeScreen'

describe('WelcomeScreen', () => {
  it('renders the logo and welcome message', () => {
    render(<WelcomeScreen proxyPort={9090} targetUrl="http://localhost:3000" />)
    expect(screen.getByText(/Proxai/i)).toBeInTheDocument()
    expect(screen.getByText(/9090/i)).toBeInTheDocument()
    expect(screen.getByText(/localhost:3000/i)).toBeInTheDocument()
  })

  it('renders usage instructions', () => {
    render(<WelcomeScreen proxyPort={9090} targetUrl="http://localhost:3000" />)
    expect(screen.getByText(/waiting/i)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Implement WelcomeScreen**

```tsx
// dashboard/src/components/WelcomeScreen.tsx
import './WelcomeScreen.css'

interface Props {
  proxyPort: number
  targetUrl: string
}

export default function WelcomeScreen({ proxyPort, targetUrl }: Props) {
  return (
    <div className="welcome">
      <div className="welcome-logo">
        <span className="welcome-logo-icon">⬡</span>
        <h1 className="welcome-logo-text">Proxai</h1>
      </div>
      <p className="welcome-subtitle">API Debug Proxy</p>

      <div className="welcome-info">
        <div className="welcome-info-row">
          <span className="welcome-label">Proxy</span>
          <code className="welcome-value">http://localhost:{proxyPort}</code>
        </div>
        <div className="welcome-info-row">
          <span className="welcome-label">Target</span>
          <code className="welcome-value">{targetUrl}</code>
        </div>
      </div>

      <div className="welcome-instructions">
        <p>Waiting for requests...</p>
        <p className="welcome-hint">
          Make requests to <code>http://localhost:{proxyPort}</code> to see them here.
        </p>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Create WelcomeScreen.css**

```css
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
  user-select: none;
}

.welcome-logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.welcome-logo-icon {
  font-size: 48px;
  color: var(--method-get);
}

.welcome-logo-text {
  font-size: 32px;
  font-weight: 300;
  letter-spacing: -1px;
  color: var(--text-primary);
}

.welcome-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-lg);
}

.welcome-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  padding: var(--spacing-lg);
  min-width: 400px;
}

.welcome-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-label {
  color: var(--text-secondary);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.welcome-value {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--method-post);
}

.welcome-instructions {
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
  animation: pulse 2s ease-in-out infinite;
}

.welcome-hint {
  margin-top: var(--spacing-sm);
  font-size: 12px;
  color: var(--text-dim);
  animation: none;
}

.welcome-hint code {
  font-family: var(--font-mono);
  color: var(--method-post);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

- [ ] **Step 4: Run tests**

```bash
cd dashboard && npx vitest run src/components/WelcomeScreen.test.tsx
```

Expected: 2 tests passing

- [ ] **Step 5: Commit**

```bash
git add dashboard/src/components/WelcomeScreen*
git commit -m "feat(dashboard): add WelcomeScreen component"
```

---

### Task 6: Request list component (DevTools-style table)

**Files:**
- Create: `dashboard/src/components/RequestList.tsx`
- Create: `dashboard/src/components/RequestList.test.tsx`
- Create: `dashboard/src/components/RequestList.css`
- Create: `dashboard/src/components/RequestRow.tsx`
- Create: `dashboard/src/components/RequestRow.css`
- Create: `dashboard/src/utils/formatters.ts`
- Create: `dashboard/src/utils/formatters.test.ts`

- [ ] **Step 1: Write failing test for formatters**

```ts
// dashboard/src/utils/formatters.test.ts
import { describe, it, expect } from 'vitest'
import { formatBytes, latencyColor, statusColor, methodColor } from './formatters'

describe('formatBytes', () => {
  it('returns "—" for undefined', () => {
    expect(formatBytes(undefined)).toBe('—')
  })
  it('formats bytes', () => {
    expect(formatBytes(0)).toBe('0 B')
    expect(formatBytes(1024)).toBe('1.0 KB')
    expect(formatBytes(1536)).toBe('1.5 KB')
    expect(formatBytes(1048576)).toBe('1.0 MB')
  })
})

describe('latencyColor', () => {
  it('returns fast color for <100ms', () => {
    expect(latencyColor(50)).toBe('var(--latency-fast)')
  })
  it('returns medium color for <500ms', () => {
    expect(latencyColor(250)).toBe('var(--latency-medium)')
  })
  it('returns slow color for >=500ms', () => {
    expect(latencyColor(500)).toBe('var(--latency-slow)')
  })
})

describe('statusColor', () => {
  it('returns 2xx color', () => {
    expect(statusColor(200)).toBe('var(--status-2xx)')
  })
  it('returns 5xx color', () => {
    expect(statusColor(500)).toBe('var(--status-5xx)')
  })
  it('returns default for no status', () => {
    expect(statusColor(undefined)).toBe('var(--text-dim)')
  })
})

describe('methodColor', () => {
  it('returns correct color per method', () => {
    expect(methodColor('GET')).toBe('var(--method-get)')
    expect(methodColor('POST')).toBe('var(--method-post)')
    expect(methodColor('PUT')).toBe('var(--method-put)')
    expect(methodColor('DELETE')).toBe('var(--method-delete)')
  })
  it('returns default for unknown', () => {
    expect(methodColor('OPTIONS')).toBe('var(--text-secondary)')
  })
})
```

- [ ] **Step 2: Implement formatters**

```ts
// dashboard/src/utils/formatters.ts
export function formatBytes(bytes?: number | null): string {
  if (bytes == null) return '—'
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`
}

export function latencyColor(ms: number): string {
  if (ms < 100) return 'var(--latency-fast)'
  if (ms < 500) return 'var(--latency-medium)'
  return 'var(--latency-slow)'
}

export function statusColor(status?: number): string {
  if (!status) return 'var(--text-dim)'
  if (status < 200) return 'var(--text-dim)'
  if (status < 300) return 'var(--status-2xx)'
  if (status < 400) return 'var(--status-3xx)'
  if (status < 500) return 'var(--status-4xx)'
  return 'var(--status-5xx)'
}

const METHOD_COLORS: Record<string, string> = {
  GET: 'var(--method-get)',
  POST: 'var(--method-post)',
  PUT: 'var(--method-put)',
  PATCH: 'var(--method-patch)',
  DELETE: 'var(--method-delete)',
}

export function methodColor(method: string): string {
  return METHOD_COLORS[method.toUpperCase()] ?? 'var(--text-secondary)'
}

export function formatLatency(ms?: number): string {
  if (ms == null) return '—'
  if (ms < 1000) return `${ms.toFixed(0)}ms`
  return `${(ms / 1000).toFixed(2)}s`
}
```

- [ ] **Step 3: Write failing tests for RequestList and RequestRow**

```tsx
// dashboard/src/components/RequestList.test.tsx
import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import RequestList from './RequestList'

const mockRequests = [
  {
    request_id: '1',
    method: 'GET',
    url: '/api/users',
    path: '/api/users',
    status: 200,
    status_text: 'OK',
    latency_ms: 42,
    started_at: new Date().toISOString(),
    is_completed: true,
    is_error: false,
  },
  {
    request_id: '2',
    method: 'POST',
    url: '/api/login',
    path: '/api/login',
    status: 401,
    status_text: 'Unauthorized',
    latency_ms: 15,
    started_at: new Date().toISOString(),
    is_completed: true,
    is_error: false,
  },
  {
    request_id: '3',
    method: 'GET',
    url: '/api/slow',
    path: '/api/slow',
    latency_ms: 1200,
    started_at: new Date().toISOString(),
    is_completed: false,
    is_error: false,
  },
]

describe('RequestList', () => {
  it('renders request rows', () => {
    render(<RequestList requests={mockRequests} selectedId={null} onSelect={() => {}} />)
    expect(screen.getByText('/api/users')).toBeInTheDocument()
    expect(screen.getByText('/api/login')).toBeInTheDocument()
  })

  it('calls onSelect when a row is clicked', () => {
    const onSelect = vi.fn()
    render(<RequestList requests={mockRequests} selectedId={null} onSelect={onSelect} />)
    fireEvent.click(screen.getByText('/api/users'))
    expect(onSelect).toHaveBeenCalledWith('1')
  })

  it('highlights selected row', () => {
    const { container } = render(
      <RequestList requests={mockRequests} selectedId="1" onSelect={() => {}} />
    )
    const selected = container.querySelector('[data-selected="true"]')
    expect(selected).toBeInTheDocument()
  })
})
```

- [ ] **Step 4: Implement RequestRow component**

```tsx
// dashboard/src/components/RequestRow.tsx
import type { RequestEntry } from '../types'
import { methodColor, statusColor, latencyColor, formatLatency } from '../utils/formatters'
import './RequestRow.css'

interface Props {
  request: RequestEntry
  selected: boolean
  onSelect: (id: string) => void
}

export default function RequestRow({ request, selected, onSelect }: Props) {
  const loading = !request.is_completed && !request.is_error
  const isError = request.is_error

  return (
    <div
      className={`request-row${selected ? ' request-row--selected' : ''}`}
      data-selected={selected || undefined}
      onClick={() => onSelect(request.request_id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onSelect(request.request_id)}
    >
      <span className="request-method" style={{ color: methodColor(request.method) }}>
        {request.method}
      </span>
      <span className="request-path">{request.path}</span>
      <span className="request-status" style={{ color: statusColor(request.status) }}>
        {loading ? '…' : isError ? 'ERR' : request.status}
      </span>
      <span
        className="request-latency"
        style={{ color: latencyColor(request.latency_ms ?? 0) }}
      >
        {formatLatency(request.latency_ms)}
      </span>
    </div>
  )
}
```

- [ ] **Step 5: Create RequestRow.css**

```css
.request-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-md);
  cursor: pointer;
  border-bottom: 1px solid var(--border-primary);
  transition: background var(--transition-fast);
  min-height: 28px;
}
.request-row:hover {
  background: var(--bg-hover);
}
.request-row--selected {
  background: var(--bg-selected);
}

.request-method {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  width: 60px;
  flex-shrink: 0;
}

.request-path {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-primary);
}

.request-status {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  width: 40px;
  text-align: right;
  flex-shrink: 0;
}

.request-latency {
  font-family: var(--font-mono);
  font-size: 12px;
  width: 70px;
  text-align: right;
  flex-shrink: 0;
}
```

- [ ] **Step 6: Implement RequestList component**

```tsx
// dashboard/src/components/RequestList.tsx
import type { RequestEntry } from '../types'
import RequestRow from './RequestRow'
import './RequestList.css'

interface Props {
  requests: RequestEntry[]
  selectedId: string | null
  onSelect: (id: string) => void
}

export default function RequestList({ requests, selectedId, onSelect }: Props) {
  if (requests.length === 0) return null

  return (
    <div className="request-list" role="listbox" aria-label="Request list">
      <div className="request-list-header">
        <span className="request-list-header-label" style={{ width: 60 }}>Method</span>
        <span className="request-list-header-label" style={{ flex: 1 }}>Path</span>
        <span className="request-list-header-label" style={{ width: 40, textAlign: 'right' }}>Status</span>
        <span className="request-list-header-label" style={{ width: 70, textAlign: 'right' }}>Latency</span>
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
  )
}
```

- [ ] **Step 7: Create RequestList.css**

```css
.request-list {
  height: 100%;
  overflow-y: auto;
  background: var(--bg-primary);
}

.request-list-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-md);
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
  position: sticky;
  top: 0;
  z-index: 1;
  min-height: 28px;
}

.request-list-header-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
}
```

- [ ] **Step 8: Run tests**

```bash
cd dashboard && npx vitest run src/components/RequestList.test.tsx src/utils/formatters.test.ts
```

Expected: All tests passing

- [ ] **Step 9: Commit**

```bash
git add dashboard/src/components/RequestList* dashboard/src/components/RequestRow* dashboard/src/utils/
git commit -m "feat(dashboard): add RequestList and RequestRow components"
```

---

### Task 7: Detail panel with tabs (Headers, Body, Timing)

**Files:**
- Create: `dashboard/src/components/DetailPanel.tsx`
- Create: `dashboard/src/components/DetailPanel.test.tsx`
- Create: `dashboard/src/components/DetailPanel.css`
- Create: `dashboard/src/components/HeadersTab.tsx`
- Create: `dashboard/src/components/HeadersTab.css`
- Create: `dashboard/src/components/BodyTab.tsx`
- Create: `dashboard/src/components/BodyTab.css`
- Create: `dashboard/src/components/TimingTab.tsx`
- Create: `dashboard/src/components/TimingTab.css`
- Create: `dashboard/src/components/WaterfallChart.tsx`
- Create: `dashboard/src/components/WaterfallChart.css`

- [ ] **Step 1: Write failing test for DetailPanel**

```tsx
// dashboard/src/components/DetailPanel.test.tsx
import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import DetailPanel from './DetailPanel'

const mockRequest = {
  request_id: 'abc123',
  method: 'GET',
  url: '/api/users',
  path: '/api/users',
  status: 200,
  status_text: 'OK',
  latency_ms: 42,
  request_headers: { 'content-type': 'application/json' },
  response_headers: { 'content-type': 'application/json', 'x-request-id': 'abc123' },
  response_body: '{"users":[]}',
  started_at: '2026-01-01T00:00:00Z',
  is_completed: true,
  is_error: false,
}

describe('DetailPanel', () => {
  it('renders request method and path', () => {
    render(<DetailPanel request={mockRequest} onClose={() => {}} />)
    expect(screen.getByText(/GET/)).toBeInTheDocument()
    expect(screen.getByText(/api\/users/)).toBeInTheDocument()
  })

  it('shows tab headers', () => {
    render(<DetailPanel request={mockRequest} onClose={() => {}} />)
    expect(screen.getByText('Headers')).toBeInTheDocument()
    expect(screen.getByText('Body')).toBeInTheDocument()
    expect(screen.getByText('Timing')).toBeInTheDocument()
  })

  it('switches tabs on click', () => {
    render(<DetailPanel request={mockRequest} onClose={() => {}} />)
    fireEvent.click(screen.getByText('Body'))
    expect(screen.getByText(/Response Body/)).toBeInTheDocument()
  })

  it('calls onClose when close button clicked', () => {
    const onClose = vi.fn()
    render(<DetailPanel request={mockRequest} onClose={onClose} />)
    fireEvent.click(screen.getByRole('button', { name: /close/i }))
    expect(onClose).toHaveBeenCalled()
  })
})
```

- [ ] **Step 2: Implement HeadersTab**

```tsx
// dashboard/src/components/HeadersTab.tsx
import type { RequestEntry } from '../types'
import './HeadersTab.css'

interface Props {
  request: RequestEntry
}

export default function HeadersTab({ request }: Props) {
  const reqHeaders = request.request_headers
  const resHeaders = request.response_headers

  return (
    <div className="headers-tab">
      {reqHeaders && Object.keys(reqHeaders).length > 0 && (
        <section>
          <h3 className="headers-section-title">Request Headers</h3>
          <div className="headers-list">
            {Object.entries(reqHeaders).map(([key, value]) => (
              <div key={key} className="header-row">
                <span className="header-key">{key}</span>
                <span className="header-value">{value}</span>
              </div>
            ))}
          </div>
        </section>
      )}
      {resHeaders && Object.keys(resHeaders).length > 0 && (
        <section>
          <h3 className="headers-section-title">Response Headers</h3>
          <div className="headers-list">
            {Object.entries(resHeaders).map(([key, value]) => (
              <div key={key} className="header-row">
                <span className="header-key">{key}</span>
                <span className="header-value">{value}</span>
              </div>
            ))}
          </div>
        </section>
      )}
      {(!reqHeaders || Object.keys(reqHeaders).length === 0) &&
        (!resHeaders || Object.keys(resHeaders).length === 0) && (
        <p className="headers-empty">No headers captured.</p>
      )}
    </div>
  )
}
```

```css
/* HeadersTab.css */
.headers-tab {
  padding: var(--spacing-md);
  overflow-y: auto;
  height: 100%;
}

.headers-section-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-sm);
  margin-top: var(--spacing-md);
}
.headers-section-title:first-child {
  margin-top: 0;
}

.headers-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.header-row {
  display: flex;
  gap: var(--spacing-sm);
  padding: 2px 0;
  font-family: var(--font-mono);
  font-size: 12px;
  border-bottom: 1px solid var(--border-primary);
}

.header-key {
  color: var(--method-post);
  flex-shrink: 0;
  min-width: 200px;
}

.header-value {
  color: var(--text-primary);
  word-break: break-all;
}

.headers-empty {
  color: var(--text-dim);
  font-style: italic;
  padding: var(--spacing-lg);
  text-align: center;
}
```

- [ ] **Step 3: Implement BodyTab**

```tsx
// dashboard/src/components/BodyTab.tsx
import type { RequestEntry } from '../types'
import { formatBytes } from '../utils/formatters'
import './BodyTab.css'

interface Props {
  request: RequestEntry
}

function tryFormatJson(text: string): string {
  try {
    return JSON.stringify(JSON.parse(text), null, 2)
  } catch {
    return text
  }
}

export default function BodyTab({ request }: Props) {
  const reqBody = request.request_body
  const resBody = request.response_body

  return (
    <div className="body-tab">
      {reqBody && (
        <section>
          <h3 className="body-section-title">
            Request Body <span className="body-size">({formatBytes(reqBody.length)})</span>
          </h3>
          <pre className="body-content">{tryFormatJson(reqBody)}</pre>
        </section>
      )}
      {resBody && (
        <section>
          <h3 className="body-section-title">
            Response Body <span className="body-size">({formatBytes(resBody.length)})</span>
          </h3>
          <pre className="body-content">{tryFormatJson(resBody)}</pre>
        </section>
      )}
      {!reqBody && !resBody && (
        <p className="body-empty">No body data captured.</p>
      )}
    </div>
  )
}
```

```css
/* BodyTab.css */
.body-tab {
  padding: var(--spacing-md);
  overflow-y: auto;
  height: 100%;
}

.body-section-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-sm);
  margin-top: var(--spacing-md);
}
.body-section-title:first-child {
  margin-top: 0;
}

.body-size {
  font-weight: 400;
  color: var(--text-dim);
}

.body-content {
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-primary);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 4px;
  padding: var(--spacing-md);
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 400px;
  overflow-y: auto;
}

.body-empty {
  color: var(--text-dim);
  font-style: italic;
  padding: var(--spacing-lg);
  text-align: center;
}
```

- [ ] **Step 4: Implement WaterfallChart**

```tsx
// dashboard/src/components/WaterfallChart.tsx
import type { RequestEntry } from '../types'
import { latencyColor } from '../utils/formatters'
import './WaterfallChart.css'

interface Props {
  request: RequestEntry
}

export default function WaterfallChart({ request }: Props) {
  const latMs = request.latency_ms ?? 0
  const barWidth = Math.min(latMs, 2000) / 2000 * 100 // scale to %, cap at 2s

  return (
    <div className="waterfall">
      <div className="waterfall-item">
        <span className="waterfall-label">Total</span>
        <div className="waterfall-track">
          <div
            className="waterfall-bar"
            style={{
              width: `${barWidth}%`,
              background: latencyColor(latMs),
            }}
          />
          <span className="waterfall-ms">{latMs.toFixed(0)}ms</span>
        </div>
      </div>
    </div>
  )
}
```

```css
/* WaterfallChart.css */
.waterfall {
  padding: var(--spacing-md);
}

.waterfall-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) 0;
}

.waterfall-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  width: 60px;
  flex-shrink: 0;
}

.waterfall-track {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.waterfall-bar {
  height: 16px;
  border-radius: 3px;
  min-width: 4px;
  transition: width var(--transition-normal);
}

.waterfall-ms {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-primary);
  flex-shrink: 0;
}
```

- [ ] **Step 5: Implement TimingTab**

```tsx
// dashboard/src/components/TimingTab.tsx
import type { RequestEntry } from '../types'
import WaterfallChart from './WaterfallChart'
import './TimingTab.css'

interface Props {
  request: RequestEntry
}

export default function TimingTab({ request }: Props) {
  return (
    <div className="timing-tab">
      <h3 className="timing-section-title">Response Time</h3>
      <WaterfallChart request={request} />
      
      <div className="timing-details">
        <div className="timing-row">
          <span className="timing-label">Status</span>
          <span className="timing-value">{request.status} {request.status_text}</span>
        </div>
        <div className="timing-row">
          <span className="timing-label">Latency</span>
          <span className="timing-value">{request.latency_ms?.toFixed(0)}ms</span>
        </div>
        <div className="timing-row">
          <span className="timing-label">Completed</span>
          <span className="timing-value">{request.completed_at || '—'}</span>
        </div>
      </div>
    </div>
  )
}
```

```css
/* TimingTab.css */
.timing-tab {
  padding: var(--spacing-md);
}

.timing-section-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-md);
}

.timing-details {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-lg);
}

.timing-row {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-xs) 0;
  border-bottom: 1px solid var(--border-primary);
  font-family: var(--font-mono);
  font-size: 12px;
}

.timing-label {
  color: var(--text-secondary);
}

.timing-value {
  color: var(--text-primary);
}
```

- [ ] **Step 6: Implement DetailPanel (container with tabs)**

```tsx
// dashboard/src/components/DetailPanel.tsx
import { useState } from 'react'
import type { RequestEntry } from '../types'
import { methodColor, statusColor, latencyColor, formatLatency } from '../utils/formatters'
import HeadersTab from './HeadersTab'
import BodyTab from './BodyTab'
import TimingTab from './TimingTab'
import './DetailPanel.css'

interface Props {
  request: RequestEntry
  onClose: () => void
}

const TABS = ['Headers', 'Body', 'Timing'] as const
type Tab = (typeof TABS)[number]

export default function DetailPanel({ request, onClose }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('Headers')

  return (
    <aside className="detail-panel" role="dialog" aria-label="Request detail">
      {/* Header */}
      <div className="detail-header">
        <div className="detail-header-info">
          <span
            className="detail-method"
            style={{ color: methodColor(request.method) }}
          >
            {request.method}
          </span>
          <span className="detail-path">{request.path}</span>
        </div>
        <button className="detail-close" onClick={onClose} aria-label="Close detail panel">
          ✕
        </button>
      </div>

      {/* Summary */}
      <div className="detail-summary">
        <div className="detail-summary-item">
          <span className="detail-summary-label">Status</span>
          {request.is_completed ? (
            <span className="detail-summary-value" style={{ color: statusColor(request.status) }}>
              {request.status} {request.status_text}
            </span>
          ) : request.is_error ? (
            <span className="detail-summary-value" style={{ color: 'var(--status-5xx)' }}>
              Error
            </span>
          ) : (
            <span className="detail-summary-value">Pending…</span>
          )}
        </div>
        <div className="detail-summary-item">
          <span className="detail-summary-label">Latency</span>
          <span className="detail-summary-value" style={{ color: latencyColor(request.latency_ms ?? 0) }}>
            {formatLatency(request.latency_ms)}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="detail-tabs" role="tablist">
        {TABS.map((tab) => (
          <button
            key={tab}
            className={`detail-tab${activeTab === tab ? ' detail-tab--active' : ''}`}
            onClick={() => setActiveTab(tab)}
            role="tab"
            aria-selected={activeTab === tab}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="detail-tab-content" role="tabpanel">
        {activeTab === 'Headers' && <HeadersTab request={request} />}
        {activeTab === 'Body' && <BodyTab request={request} />}
        {activeTab === 'Timing' && <TimingTab request={request} />}
      </div>
    </aside>
  )
}
```

- [ ] **Step 7: Create DetailPanel.css**

```css
.detail-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  border-left: 1px solid var(--border-primary);
  min-width: 400px;
  animation: slideIn 200ms ease;
}

@keyframes slideIn {
  from { transform: translateX(20px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
  min-height: 36px;
}

.detail-header-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  overflow: hidden;
}

.detail-method {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.detail-path {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 16px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background var(--transition-fast);
}
.detail-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.detail-summary {
  display: flex;
  gap: var(--spacing-xl);
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-tertiary);
}

.detail-summary-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.detail-summary-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
}

.detail-summary-value {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 600;
}

/* Tabs */
.detail-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
}

.detail-tab {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-bottom: 2px solid transparent;
  transition: all var(--transition-fast);
}

.detail-tab:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.detail-tab--active {
  color: var(--text-primary);
  border-bottom-color: var(--method-post);
}

.detail-tab-content {
  flex: 1;
  overflow: hidden;
}
```

- [ ] **Step 8: Run tests**

```bash
cd dashboard && npx vitest run src/components/DetailPanel.test.tsx
```

Expected: 4 tests passing

- [ ] **Step 9: Commit**

```bash
git add dashboard/src/components/DetailPanel* dashboard/src/components/HeadersTab* dashboard/src/components/BodyTab* dashboard/src/components/TimingTab* dashboard/src/components/WaterfallChart*
git commit -m "feat(dashboard): add DetailPanel with Headers, Body, Timing tabs"
```

---

### Task 8: Status bar component

**Files:**
- Create: `dashboard/src/components/StatusBar.tsx`
- Create: `dashboard/src/components/StatusBar.css`

- [ ] **Step 1: Implement StatusBar**

```tsx
// dashboard/src/components/StatusBar.tsx
import type { RequestStats } from '../hooks/useRequests'
import './StatusBar.css'

interface Props {
  stats: { total: number; errors: number; avgLatency: number }
  connected: boolean
  targetUrl?: string
}

export default function StatusBar({ stats, connected, targetUrl }: Props) {
  return (
    <div className="status-bar">
      <span className="status-bar-section">
        <span className={`status-bar-dot ${connected ? 'connected' : 'disconnected'}`} />
        {connected ? 'Connected' : 'Disconnected'}
      </span>
      <span className="status-bar-divider" />
      <span className="status-bar-section">
        Requests: <strong>{stats.total}</strong>
      </span>
      {stats.errors > 0 && (
        <>
          <span className="status-bar-divider" />
          <span className="status-bar-section status-bar-errors">
            Errors: <strong>{stats.errors}</strong>
          </span>
        </>
      )}
      <span className="status-bar-divider" />
      <span className="status-bar-section">
        Avg latency: <strong>{stats.avgLatency.toFixed(0)}ms</strong>
      </span>
      {targetUrl && (
        <>
          <span className="status-bar-divider" />
          <span className="status-bar-section status-bar-target">
            Target: {targetUrl}
          </span>
        </>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Create StatusBar.css**

```css
.status-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  height: var(--status-bar-height);
  padding: 0 var(--spacing-md);
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-primary);
  font-size: 12px;
  color: var(--text-primary);
  flex-shrink: 0;
}

.status-bar-section {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-bar-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-bar-dot.connected {
  background: var(--status-2xx);
  box-shadow: 0 0 4px var(--status-2xx);
}

.status-bar-dot.disconnected {
  background: var(--status-5xx);
}

.status-bar-divider {
  width: 1px;
  height: 16px;
  background: var(--border-secondary);
}

.status-bar-errors strong {
  color: var(--status-5xx);
}

.status-bar-target {
  color: var(--text-dim);
  margin-left: auto;
}
```

- [ ] **Step 3: Commit**

```bash
git add dashboard/src/components/StatusBar*
git commit -m "feat(dashboard): add StatusBar component"
```

---

### Task 9: App shell — wire everything together

**Files:**
- Create: `dashboard/src/App.tsx`
- Create: `dashboard/src/App.css`
- Modify: `dashboard/src/main.tsx` (already created)

- [ ] **Step 1: Write failing App test**

```tsx
// dashboard/src/App.test.tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders welcome screen initially', () => {
    render(<App />)
    expect(screen.getByText(/Proxai/i)).toBeInTheDocument()
    expect(screen.getByText(/Waiting for requests/i)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Implement App component**

```tsx
// dashboard/src/App.tsx
import { useState, useCallback } from 'react'
import { useWebSocket } from './hooks/useWebSocket'
import { useRequests } from './hooks/useRequests'
import type { RequestEvent } from './types'
import WelcomeScreen from './components/WelcomeScreen'
import RequestList from './components/RequestList'
import DetailPanel from './components/DetailPanel'
import StatusBar from './components/StatusBar'
import './App.css'

// Parse proxy info from URL query params (set by the CLI when spawning the dashboard)
function getProxyConfig() {
  const params = new URLSearchParams(window.location.search)
  return {
    port: parseInt(params.get('port') || '9090', 10),
    targetUrl: params.get('target') || 'unknown',
  }
}

export default function App() {
  const { port, targetUrl } = getProxyConfig()
  const wsUrl = `ws://localhost:${port}/ws`
  const { requests, selectedId, stats, addEvent, selectRequest, clearSelection } = useRequests()
  const { connected } = useWebSocket(wsUrl, addEvent as (e: unknown) => void)

  const selectedRequest = selectedId
    ? requests.find((r) => r.request_id === selectedId) ?? null
    : null

  const hasRequests = requests.length > 0

  return (
    <div className="app">
      {/* Main content */}
      <div className="app-main">
        {/* Left panel: request list */}
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

        {/* Right panel: detail view */}
        {selectedRequest && (
          <div className="app-detail">
            <DetailPanel request={selectedRequest} onClose={clearSelection} />
          </div>
        )}
      </div>

      {/* Bottom status bar */}
      <StatusBar stats={stats} connected={connected} targetUrl={targetUrl} />
    </div>
  )
}
```

- [ ] **Step 3: Create App.css**

```css
.app {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.app-list {
  flex: 1;
  overflow: hidden;
  min-width: var(--request-list-min-width);
}

.app-detail {
  width: var(--detail-panel-width);
  min-width: 400px;
  max-width: 700px;
  overflow: hidden;
  flex-shrink: 0;
}
```

- [ ] **Step 4: Update main.tsx to use App.css**

Already done — `./index.css` is imported for design tokens. `App.css` handles layout.

- [ ] **Step 5: Run tests**

```bash
cd dashboard && npx vitest run
```

Expected: All ~15+ tests passing

- [ ] **Step 6: Verify Vite dev server starts**

```bash
cd dashboard && npx vite build 2>&1
```

Expected: Build succeeds with no errors

- [ ] **Step 7: Commit**

```bash
git add dashboard/src/App.tsx dashboard/src/App.css
git commit -m "feat(dashboard): wire App shell with request list and detail panel"
```

---

### Task 10: Spawn dashboard from the CLI

**Files:**
- Modify: `src/proxai/cli.py` (add dashboard launch logic in the `start` command)

- [ ] **Step 1: Implement dashboard subprocess launching in cli.py**

After the proxy health check succeeds and the live CLI display starts, add an option to also launch the dashboard. Update `start` command to accept `--with-dashboard` / `-d` flag.

The dashboard flag should:
1. Resolve the dashboard directory relative to the package
2. Spawn `npx vite --port <dashboard_port> -- --port <proxy_port> --target <target_url>`
3. Or better: build the dashboard first with the config embedded

Actually the cleanest approach: serve the built dashboard as a static file from the FastAPI server. Let's add middleware to the FastAPI server that serves `dashboard/dist/` at the root URL.

Update `server.py` to:
1. Check if `dashboard/dist/index.html` exists
2. If so, mount a StaticFiles for the dashboard
3. The dashboard JS reads proxy port from query params: `?port=9090&target=...`

- [ ] **Step 2: Build the dashboard**

```bash
cd dashboard && npm run build
```

Expected: `dashboard/dist/` directory created with index.html + JS bundle

- [ ] **Step 3: Modify server.py to serve dashboard static files**

```python
# In server.py, after create_app function
import os
from fastapi.staticfiles import StaticFiles

# After creating the FastAPI app, add:
dashboard_dir = os.path.join(os.path.dirname(__file__), "..", "..", "dashboard", "dist")
dashboard_dir = os.path.abspath(dashboard_dir)
if os.path.isdir(dashboard_dir):
    @app.get("/dashboard")
    async def dashboard_redirect():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/dashboard/index.html")
    
    app.mount("/dashboard", StaticFiles(directory=dashboard_dir), name="dashboard")
```

- [ ] **Step 4: Auto-open dashboard URL in browser**

```python
# In cli.py start command, after proxy health check:
import webbrowser
if dashboard:
    webbrowser.open(f"http://localhost:{port}/dashboard?port={port}&target={target}")
```

- [ ] **Step 5: Run full integration test**

```bash
# Start proxy
PROXAI_TARGET=https://httpbin.org .venv/bin/uvicorn proxai.server:create_app --factory --port 19110

# In another terminal, open http://localhost:19110/dashboard?port=19110&target=httpbin.org
# Make some requests: curl http://localhost:19110/get
```

- [ ] **Step 6: Commit**

```bash
git add dashboard/dist/ src/proxai/server.py src/proxai/cli.py
git commit -m "feat(dashboard): serve built dashboard from FastAPI static files"
```

---

### Task 11: Final integration test

**Files:**
- Modify: `tests/test_server.py` (add dashboard static file serving test)

- [ ] **Step 1: Write test for dashboard static serving**

```python
# tests/test_server.py — add:
def test_dashboard_static_served(self):
    """Dashboard static files are served at /dashboard/..."""
    response = client.get("/dashboard/index.html")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
```

- [ ] **Step 2: Run all tests**

```bash
cd /Users/chrismaskey/Repos/Proxai && .venv/bin/pytest -v --timeout=10
```

Expected: All existing 36 tests + new tests pass

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat(dashboard): final integration tests and polish"
```
