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
      <div className="detail-header">
        <div className="detail-header-info">
          <span className="detail-method" style={{ color: methodColor(request.method) }}>
            {request.method}
          </span>
          <span className="detail-path">{request.path}</span>
        </div>
        <button className="detail-close" onClick={onClose} aria-label="Close detail panel">
          {'\u2715'}
        </button>
      </div>

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
            <span className="detail-summary-value">Pending\u2026</span>
          )}
        </div>
        <div className="detail-summary-item">
          <span className="detail-summary-label">Latency</span>
          <span className="detail-summary-value" style={{ color: latencyColor(request.latency_ms ?? 0) }}>
            {formatLatency(request.latency_ms)}
          </span>
        </div>
      </div>

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

      <div className="detail-tab-content" role="tabpanel">
        {activeTab === 'Headers' && <HeadersTab request={request} />}
        {activeTab === 'Body' && <BodyTab request={request} />}
        {activeTab === 'Timing' && <TimingTab request={request} />}
      </div>
    </aside>
  )
}
