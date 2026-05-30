import { describe, it, expect, vi } from 'vitest'
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
