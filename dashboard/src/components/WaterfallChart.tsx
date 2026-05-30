import type { RequestEntry } from '../types'
import { latencyColor } from '../utils/formatters'
import './WaterfallChart.css'

interface Props {
  request: RequestEntry
}

export default function WaterfallChart({ request }: Props) {
  const latMs = request.latency_ms ?? 0
  const pct = Math.min(latMs / 2000 * 100, 100)

  return (
    <div className="waterfall">
      <div className="waterfall-item">
        <span className="waterfall-label">Total</span>
        <div className="waterfall-track">
          <div
            className="waterfall-bar"
            style={{
              width: `${pct}%`,
              background: latencyColor(latMs),
            }}
          />
          <span className="waterfall-ms">{latMs.toFixed(0)}ms</span>
        </div>
      </div>
    </div>
  )
}
