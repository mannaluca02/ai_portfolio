import {NextIntlClientProvider} from 'next-intl'
import messages from '../messages/de.json'
import type {ReactElement} from 'react'
import { act, fireEvent, render as baseRender, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import type { ReactNode } from 'react'
import Projects from '@/components/home/Projects'

vi.mock('@/components/ui/FadeInSection', () => ({ default: ({ children }: { children: ReactNode }) => children }))

const projects = [
  { id: 1, name: 'Featured fixture', description: 'Python project', featured: true, project_type: 'Personal',
    slug: 'featured', section: 'projects', your_role: 'Developer', start_date: '2024-01-01', end_date: '2024-03-01',
    team_size: 2, client_company: 'Fixture company', technologies: ['Python'],
    project_url: 'https://example.com', github_url: 'https://example.com/code', demo_url: 'https://example.com/demo' },
  { id: 2, name: 'Other fixture', description: 'React project', featured: false, project_type: 'Academic',
    slug: 'other', section: 'projects', your_role: 'Researcher' },
]

describe('project tabs', () => {
  it('only mounts the active list, so hidden projects cannot extend its height', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => projects }))
    render(<Projects />)
    await screen.findByText('Featured fixture')
    expect(screen.queryByText('Other fixture')).toBeNull()
    expect(screen.getAllByText('Featured fixture')).toHaveLength(1)
    fireEvent.click(screen.getByText('Featured fixture'))
    expect(screen.getByText('Fixture company')).toBeDefined()
    expect(screen.getByText('Featured fixture').closest('[data-project-id]')?.getAttribute('data-expanded')).toBe('true')
    fireEvent.click(screen.getByText('Featured fixture'))
    expect(screen.getByText('Featured fixture').closest('[data-project-id]')?.getAttribute('data-expanded')).toBe('false')
    fireEvent.click(screen.getByRole('button', { name: /Alle Projekte/ }))
    await screen.findByText('Other fixture')
    fireEvent.click(screen.getByRole('button', { name: /Featured/ }))
    await waitFor(() => expect(screen.queryByText('Other fixture')).toBeNull())
  })

  it('opens a non-featured project from a citation after mounting its tab', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => projects }))
    render(<Projects />)
    await screen.findByText('Featured fixture')
    act(() => window.dispatchEvent(new CustomEvent('openAccordion', { detail: { link: 'projects-other' } })))
    const heading = await screen.findByText('Other fixture')
    await waitFor(() => expect(heading.closest('[data-project-id]')?.getAttribute('data-expanded')).toBe('true'))
    await waitFor(() => expect(document.getElementById('projects-other')).not.toBeNull())
  })

  it('shows the featured empty state without reserving the all-projects list', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [projects[1]] }))
    render(<Projects />)
    await screen.findByText('Keine Featured Projekte vorhanden.')
    expect(screen.queryByText('Other fixture')).toBeNull()
  })
})

function render(element: ReactElement) { return baseRender(<NextIntlClientProvider locale="de" messages={messages}>{element}</NextIntlClientProvider>) }
