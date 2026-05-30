import { describe, it, expect, vi } from 'vitest'
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
