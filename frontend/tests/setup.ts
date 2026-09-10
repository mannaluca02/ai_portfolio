import { afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'

afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.restoreAllMocks() })
if (typeof HTMLElement !== 'undefined') Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', { value: vi.fn(), configurable: true })
if (typeof window !== 'undefined') Object.defineProperty(window, 'matchMedia', { writable: true, value: vi.fn().mockImplementation(() => ({
  matches: false, addListener: vi.fn(), removeListener: vi.fn(),
  addEventListener: vi.fn(), removeEventListener: vi.fn(),
})) })
