// Shared types matching Proxai's Pydantic event models

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
