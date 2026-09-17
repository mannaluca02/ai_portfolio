export type ChatOutcome = 'answered' | 'source_fallback' | 'no_information'

export interface ChatSource {
  title: string
  link: string
  index: number
}

export interface DisplayAnswer {
  content: string
  outcome: ChatOutcome
  sources: ChatSource[]
}

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

/** Backend outcomes are authoritative; similarity never overrides failed checks. */
export function parseChatResponse(data: unknown, unavailableMessage = 'Die Antwort konnte nicht geprüft werden. Bitte versuche es erneut.'): DisplayAnswer {
  const unavailable = (): DisplayAnswer => ({content: unavailableMessage, outcome: 'no_information', sources: []})
  if (!record(data) || typeof data.answer !== 'string' || !data.answer.trim()) return unavailable()
  if (data.outcome === 'no_information') return { content: data.answer, outcome: 'no_information', sources: [] }
  if (data.outcome !== 'answered' && data.outcome !== 'source_fallback') return unavailable()
  if (data.outcome === 'answered' && (!record(data.verification) || data.verification.is_verified !== true)) return unavailable()
  if (!Array.isArray(data.sources)) return unavailable()

  const sources: ChatSource[] = []
  for (const source of data.sources) {
    if (!record(source) || typeof source.title !== 'string' || typeof source.section !== 'string'
      || typeof source.slug !== 'string' || typeof source.index !== 'number'
      || !Number.isSafeInteger(source.index) || source.index < 1) return unavailable()
    sources.push({ title: source.title, link: `${source.section}-${source.slug}`, index: source.index })
  }
  const cited = [...data.answer.matchAll(/\[(\d+)\]/g)].map(match => Number(match[1]))
  if (!cited.length || cited.some(index => !sources.some(source => source.index === index))) return unavailable()
  return { content: data.answer, outcome: data.outcome, sources: sources.filter(source => cited.includes(source.index)) }
}
