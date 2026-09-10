// @vitest-environment node
import { afterEach, expect, it, vi } from 'vitest'
import { POST } from '@/app/api/chat/route'

afterEach(() => { vi.unstubAllGlobals(); vi.useRealTimers() })
const request = () => new Request('http://localhost/api/chat', { method: 'POST', body: JSON.stringify({ message: 'Python?' }) })

it('preserves rate limits and retry headers', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 'Rate limit' }), {
    status: 429, headers: { 'Retry-After': '60', 'X-RateLimit-Daily-Remaining': '0' },
  })))
  const result = await POST(request())
  expect(result.status).toBe(429)
  expect(result.headers.get('retry-after')).toBe('60')
  expect(result.headers.get('x-ratelimit-daily-remaining')).toBe('0')
})

it('bounds the upstream wait and maps timeouts to 504', async () => {
  const fetchMock = vi.fn().mockRejectedValue(new DOMException('Timed out', 'TimeoutError'))
  vi.stubGlobal('fetch', fetchMock)
  const result = await POST(request())
  expect(result.status).toBe(504)
  expect(fetchMock.mock.calls[0][1].signal).toBeDefined()
})

it('rejects malformed client JSON with 400', async () => {
  const result = await POST(new Request('http://localhost/api/chat', { method: 'POST', body: '{' }))
  expect(result.status).toBe(400)
})

it('passes safe response fields unchanged', async () => {
  const body = { answer: 'Portfolio excerpt', outcome: 'source_fallback', sources: [], verification: null }
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json(body)))
  expect(await (await POST(request())).json()).toEqual(body)
})

it('actually aborts a stalled upstream request after 30 seconds', async () => {
  vi.useFakeTimers()
  vi.stubGlobal('fetch', vi.fn((_url, options) => new Promise((_resolve, reject) => {
    options.signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')))
  })))
  const pending = POST(request())
  await vi.advanceTimersByTimeAsync(30_000)
  expect((await pending).status).toBe(504)
})

it('forwards caller cancellation to the upstream request', async () => {
  const caller = new AbortController()
  const upstream = vi.fn((_url, options) => new Promise((_resolve, reject) => {
    options.signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')))
    caller.abort()
  }))
  vi.stubGlobal('fetch', upstream)
  const result = await POST(new Request('http://localhost/api/chat', {
    method: 'POST', body: '{}', signal: caller.signal,
  }))
  expect(result.status).toBe(504)
  expect(upstream.mock.calls[0][1].signal.aborted).toBe(true)
})
