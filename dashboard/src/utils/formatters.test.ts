import { describe, it, expect } from 'vitest'
import { formatBytes, latencyColor, statusColor, methodColor } from './formatters'

describe('formatBytes', () => {
  it('returns "\u2014" for undefined', () => {
    expect(formatBytes(undefined)).toBe('\u2014')
  })
  it('formats bytes', () => {
    expect(formatBytes(0)).toBe('0 B')
    expect(formatBytes(1024)).toBe('1.0 KB')
    expect(formatBytes(1536)).toBe('1.5 KB')
    expect(formatBytes(1048576)).toBe('1.0 MB')
  })
})

describe('latencyColor', () => {
  it('returns fast color for <100ms', () => {
    expect(latencyColor(50)).toBe('var(--latency-fast)')
  })
  it('returns medium color for <500ms', () => {
    expect(latencyColor(250)).toBe('var(--latency-medium)')
  })
  it('returns slow color for >=500ms', () => {
    expect(latencyColor(500)).toBe('var(--latency-slow)')
  })
})

describe('statusColor', () => {
  it('returns 2xx color', () => {
    expect(statusColor(200)).toBe('var(--status-2xx)')
  })
  it('returns 5xx color', () => {
    expect(statusColor(500)).toBe('var(--status-5xx)')
  })
  it('returns default for no status', () => {
    expect(statusColor(undefined)).toBe('var(--text-dim)')
  })
})

describe('methodColor', () => {
  it('returns correct color per method', () => {
    expect(methodColor('GET')).toBe('var(--method-get)')
    expect(methodColor('POST')).toBe('var(--method-post)')
    expect(methodColor('PUT')).toBe('var(--method-put)')
    expect(methodColor('DELETE')).toBe('var(--method-delete)')
  })
  it('returns default for unknown', () => {
    expect(methodColor('OPTIONS')).toBe('var(--text-secondary)')
  })
})
