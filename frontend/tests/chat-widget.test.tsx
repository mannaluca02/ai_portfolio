import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { createRef } from 'react'
import { expect, it, vi } from 'vitest'
import ChatbotWidget, { ChatbotWidgetRef } from '@/components/chatbot/ChatbotWidget'

const answer = (payload: unknown) =>
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(payload), {
    status: 200, headers: { 'Content-Type': 'application/json' },
  })))

async function ask(question = 'Welche Projekte?') {
  const ref = createRef<ChatbotWidgetRef>()
  render(<ChatbotWidget ref={ref} />)
  act(() => ref.current?.open())
  const input = await screen.findByRole('textbox')
  fireEvent.change(input, { target: { value: question } })
  fireEvent.keyDown(input, { key: 'Enter' })
  await waitFor(() => expect(fetch).toHaveBeenCalled())
  await waitFor(() => expect((input as HTMLInputElement).disabled).toBe(false))
  return input as HTMLInputElement
}

it('does not display a rejected answer even when work-source similarity is high', async () => {
  answer({
    answer: 'Luca arbeitet bei Google [1].', outcome: 'answered', confidence: 0.99,
    verification: { is_verified: false, confidence: 0.99 },
    sources: [{ index: 1, title: 'Work', table: 'work_experiences', similarity: 0.99, section: 'experience', slug: 'work' }],
  })
  await ask('Welche Firma?')
  expect(screen.queryByText(/Luca arbeitet bei Google/)).toBeNull()
  expect(screen.queryByText(/^Verifiziert$/)).toBeNull()
})

it('shows a verified answer with its sources', async () => {
  answer({
    answer: 'Luca studiert Data Science [1].', outcome: 'answered', confidence: 0.8,
    verification: { is_verified: true, confidence: 0.8 },
    sources: [{ index: 1, title: 'BSc Data Science', table: 'education', section: 'education', slug: 'bsc', similarity: 0.7 }],
  })
  await ask('Was hat er studiert?')
  expect(screen.getByText(/Luca studiert Data Science \[1\]\./)).toBeTruthy()
  expect(screen.getByText(/BSc Data Science/)).toBeTruthy()
})

it('shows the unverified excerpt fallback as excerpts, not as an answer', async () => {
  answer({
    answer: 'Dafür habe ich keine geprüfte Antwort. Das kommt deiner Frage am nächsten:\n• IT-Supporter bei Novartis: Lehrstelle als Betriebsinformatiker EFZ. [1]',
    outcome: 'source_fallback', verification: null, confidence: 0,
    sources: [{ index: 1, title: 'IT-Supporter bei Novartis', table: 'work_experiences', section: 'experience', slug: 'novartis', similarity: 0.48 }],
  })
  await ask('Wo arbeitest du?')
  expect(screen.getByText(/keine geprüfte Antwort/)).toBeTruthy()
  expect(screen.getByText(/Portfolio-Auszüge/)).toBeTruthy()
})

it('reports a refused request without leaving a half-written message behind', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('{}', { status: 429 })))
  await ask()
  expect(screen.getByText(/Chat-Limit/)).toBeTruthy()
})
