import { expect, it } from 'vitest'
import { parseChatResponse } from '@/lib/chat-response'

const source = { index: 2, title: 'Python', section: 'projects', slug: 'python' }
const answer = { answer: 'Luca nutzt Python [2].', outcome: 'answered',
  verification: { is_verified: true }, sources: [source] }

it('preserves valid citations without renumbering them', () => {
  expect(parseChatResponse(answer)).toEqual({ content: answer.answer, outcome: 'answered',
    sources: [{ title: 'Python', index: 2, link: 'projects-python' }] })
})

it('accepts source excerpts without claiming verification', () => {
  expect(parseChatResponse({ ...answer, outcome: 'source_fallback', verification: null }).outcome).toBe('source_fallback')
})

it('suppresses sources on no-information responses', () => {
  expect(parseChatResponse({ ...answer, outcome: 'no_information' }).sources).toEqual([])
})

it.each([null, {}, { ...answer, answer: '' }, { ...answer, outcome: undefined },
  { ...answer, verification: null }, { ...answer, sources: null },
  { ...answer, sources: [null] }, { ...answer, sources: [{ ...source, index: 0 }] },
  { ...answer, answer: 'Missing citation' }, { ...answer, answer: 'Wrong citation [3].' },
])('fails closed for malformed or unsupported responses: %j', data => {
  const parsed = parseChatResponse(data)
  expect(parsed.outcome).toBe('no_information')
  expect(parsed.sources).toEqual([])
  expect(parsed.content).not.toContain('Luca nutzt Python')
})
