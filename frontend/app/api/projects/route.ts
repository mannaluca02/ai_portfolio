import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function GET(request: Request) {
  const language = new URL(request.url).searchParams.get('lang') || 'de'
  if (!['de', 'en'].includes(language)) return NextResponse.json({error: 'Unsupported language'}, {status: 400})
  try {
    const response = await fetch(`${BACKEND_URL}/api/projects?lang=${language}`, {
      cache: 'no-store',
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching projects:', error)
    return NextResponse.json(
      { error: 'Failed to fetch projects' },
      { status: 500 }
    )
  }
}
