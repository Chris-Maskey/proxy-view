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
