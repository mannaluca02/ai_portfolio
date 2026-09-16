import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

// Muss bei jedem Aufruf laufen, sonst liefert Vercel eine gecachte Antwort
// zurueck und die Datenbank sieht nichts.
export const dynamic = 'force-dynamic'
export const maxDuration = 60

/**
 * Haelt die Supabase-Datenbank wach.
 *
 * Supabase pausiert Projekte im Free-Tier nach 7 Tagen ohne Aktivitaet. Besucht
 * niemand die Seite, gibt es keine Abfrage und das Projekt schlaeft ein. Der
 * Cron-Job in vercel.json ruft diese Route einmal taeglich auf.
 *
 * Wichtig ist, dass der Ping die Datenbank erreicht und nicht nur das Backend:
 * /api/health fuehrt ein SELECT 1 aus, genau deshalb wird dieser Endpunkt
 * verwendet. Er ist ausserdem vom Rate-Limit ausgenommen.
 */
export async function GET(request: Request) {
  // Vercel sendet CRON_SECRET als Bearer-Token, sofern die Variable gesetzt
  // ist. Ohne die Pruefung koennte jeder die Route oeffentlich ausloesen.
  const secret = process.env.CRON_SECRET
  if (secret && request.headers.get('authorization') !== `Bearer ${secret}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const started = Date.now()
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`, {
      cache: 'no-store',
      signal: AbortSignal.timeout(50_000),
    })
    const body = await response.json().catch(() => null)
    const database = body?.services?.database ?? 'unknown'

    // Das Backend antwortet auch dann mit 200, wenn die Datenbank weg ist.
    // Genau dieser Fall ist hier der interessante, also wird er zum Fehler.
    const ok = response.ok && database === 'connected'
    return NextResponse.json(
      { ok, database, backendStatus: response.status, durationMs: Date.now() - started },
      { status: ok ? 200 : 503 },
    )
  } catch (error) {
    return NextResponse.json(
      {
        ok: false,
        database: 'unreachable',
        error: error instanceof Error ? error.name : 'unknown',
        durationMs: Date.now() - started,
      },
      { status: 503 },
    )
  }
}
