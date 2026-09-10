import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function POST(request: Request) {
  let body: unknown
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 })
  }

  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 30_000)
  const abort = () => controller.abort()
  request.signal.addEventListener('abort', abort, { once: true })
  if (request.signal.aborted) controller.abort()
  try {
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
      cache: 'no-store',
    })
    const headers = new Headers()
    for (const name of ['Retry-After', 'X-RateLimit-Daily-Limit', 'X-RateLimit-Daily-Remaining',
      'X-RateLimit-Monthly-Limit', 'X-RateLimit-Monthly-Remaining']) {
      const value = response.headers.get(name)
      if (value !== null) headers.set(name, value)
    }
    if (!response.ok) {
      return NextResponse.json({ error: 'Chat request could not be completed' },
        { status: response.status, headers })
    }
    return NextResponse.json(await response.json(), { headers })
  } catch (error) {
    const timedOut = controller.signal.aborted || (error instanceof Error && error.name === 'TimeoutError')
    return NextResponse.json({ error: timedOut ? 'Chat request timed out' : 'Chat service unavailable' },
      { status: timedOut ? 504 : 502 })
  } finally {
    clearTimeout(timeout)
    request.signal.removeEventListener('abort', abort)
  }
}
