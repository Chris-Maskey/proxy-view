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
