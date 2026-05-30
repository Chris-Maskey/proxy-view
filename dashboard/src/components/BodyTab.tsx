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
