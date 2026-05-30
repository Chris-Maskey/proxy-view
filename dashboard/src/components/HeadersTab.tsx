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
