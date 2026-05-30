import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useWebSocket } from './useWebSocket'

describe('useWebSocket', () => {
  let mockWs: any

  beforeEach(() => {
    mockWs = {
      send: vi.fn(),
      close: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      readyState: WebSocket.OPEN,
    }
    vi.stubGlobal('WebSocket', vi.fn(() => mockWs))
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  it('creates a WebSocket connection', () => {
    const onEvent = vi.fn()
    renderHook(() => useWebSocket('ws://localhost:9090/ws', onEvent))
    expect(WebSocket).toHaveBeenCalledWith('ws://localhost:9090/ws')
  })

  it('calls onEvent when message received', () => {
    const onEvent = vi.fn()
    renderHook(() => useWebSocket('ws://localhost:9090/ws', onEvent))

    const msgHandler = mockWs.addEventListener.mock.calls.find(
      (c: any[]) => c[0] === 'message'
    )
    expect(msgHandler).toBeDefined()
    msgHandler[1]({ data: JSON.stringify({ type: 'connected' }) })
    expect(onEvent).toHaveBeenCalledWith({ type: 'connected' })
  })

  it('returns connected state', () => {
    const onEvent = vi.fn()
    const { result } = renderHook(() => useWebSocket('ws://localhost:9090/ws', onEvent))

    const openHandler = mockWs.addEventListener.mock.calls.find(
      (c: any[]) => c[0] === 'open'
    )
    expect(openHandler).toBeDefined()
    act(() => {
      openHandler[1](new Event('open'))
    })
    expect(result.current.connected).toBe(true)
  })

  it('closes connection on unmount', () => {
    const onEvent = vi.fn()
    const { unmount } = renderHook(() => useWebSocket('ws://localhost:9090/ws', onEvent))
    unmount()
    expect(mockWs.close).toHaveBeenCalled()
  })
})
