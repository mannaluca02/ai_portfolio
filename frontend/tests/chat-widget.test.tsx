import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { createRef } from 'react'
import { expect, it, vi } from 'vitest'
import ChatbotWidget, { ChatbotWidgetRef } from '@/components/chatbot/ChatbotWidget'

it('does not display a rejected answer even when work-source similarity is high', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({
    answer: 'Luca arbeitet bei Google [1].', outcome: 'answered', confidence: 0.99,
    verification: { is_verified: false, confidence: 0.99 },
    sources: [{ index: 1, title: 'Work', table: 'work_experiences', similarity: 0.99, section: 'experience', slug: 'work' }],
  }) }))
  const ref = createRef<ChatbotWidgetRef>()
  render(<ChatbotWidget ref={ref} />)
  act(() => ref.current?.open())
  const input = await screen.findByRole('textbox')
  fireEvent.change(input, { target: { value: 'Welche Firma?' } })
  fireEvent.keyDown(input, { key: 'Enter' })
  // Existing widget uses keyPress; exercise both handlers during migration.
  fireEvent.keyPress(input, { key: 'Enter', charCode: 13 })
  await waitFor(() => expect(fetch).toHaveBeenCalled())
  await waitFor(() => expect((input as HTMLInputElement).disabled).toBe(false))
  expect(screen.queryByText(/Luca arbeitet bei Google/)).toBeNull()
  expect(screen.queryByText(/^Verifiziert$/)).toBeNull()
})
