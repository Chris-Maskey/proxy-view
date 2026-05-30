import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import WelcomeScreen from './WelcomeScreen'

describe('WelcomeScreen', () => {
  it('renders the logo and welcome message', () => {
    render(<WelcomeScreen proxyPort={9090} targetUrl="http://localhost:3000" />)
    expect(screen.getByText(/Proxai/i)).toBeInTheDocument()
    expect(screen.getAllByText(/9090/i).length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText(/localhost:3000/i)).toBeInTheDocument()
  })

  it('renders usage instructions', () => {
    render(<WelcomeScreen proxyPort={9090} targetUrl="http://localhost:3000" />)
    expect(screen.getByText(/waiting/i)).toBeInTheDocument()
  })
})
