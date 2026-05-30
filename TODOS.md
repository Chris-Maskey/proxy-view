# Proxai TODOs

## Design review items (30 May 2026)

- [ ] **Dashboard a11y** — Add keyboard navigation (tab through request list, Enter to open detail, Escape to close), ARIA labels on method/status badges, focus management when detail panel opens. Target: Phase 3 (dashboard build).

## Implementation

- [ ] Phase 1: Project scaffold — pyproject.toml, module structure
- [ ] Phase 1: WebSocket broadcast hub — verify with wscat before proxy exists
- [ ] Phase 1: HTTP proxy core — catch-all route, httpx forwarding
- [ ] Phase 1: Event emission — push events on request/response
- [ ] Phase 1: SQLite logger — background subscriber
- [ ] Phase 2: Rich CLI viewer — traffic table, latency heatmap, stats panel
- [ ] Phase 3: React dashboard — request list, detail view, waterfall chart
- [ ] Phase 4: Replay engine, time machine, replay --diff
