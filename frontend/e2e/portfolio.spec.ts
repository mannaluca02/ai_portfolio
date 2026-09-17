import { test, expect } from '@playwright/test'

const projects = Array.from({ length: 18 }, (_, i) => ({
  id: i + 1, name: `Fixture project ${i + 1}`, description: 'A documented project. '.repeat(30),
  featured: i < 2, project_type: 'Personal', section: 'projects', slug: `fixture-${i + 1}`,
  your_role: 'Developer', technologies: ['Python'],
}))

test.beforeEach(async ({ page }) => {
  // Only synthetic portfolio content; no production database or LLM calls.
  await page.route('**/api/**', route => route.fulfill({ json:
    new URL(route.request().url()).pathname === '/api/projects' ? projects : [] }))
})

test('featured height is independent of the hidden all-projects list', async ({ page }) => {
  await page.goto('/de')
  const section = page.locator('#projects')
  await expect(section.locator('[data-project-id]')).toHaveCount(2)
  const initialHeight = (await section.boundingBox())!.height
  await section.getByRole('button', { name: /Alle Projekte/ }).click()
  await expect(section.locator('[data-project-id]')).toHaveCount(18)
  expect((await section.boundingBox())!.height).toBeGreaterThan(initialHeight + 500)
  await section.getByRole('button', { name: /Featured/ }).click()
  await expect(section.locator('[data-project-id]')).toHaveCount(2)
  expect(Math.abs((await section.boundingBox())!.height - initialHeight)).toBeLessThan(2)
  await expect.poll(async () => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
})

test('accordions and citation links still work after tab changes', async ({ page }) => {
  await page.goto('/de')
  const section = page.locator('#projects')
  await expect(section.locator('[data-project-id]')).toHaveCount(2)
  await section.getByRole('heading', { name: 'Fixture project 1', exact: true }).click()
  await expect(section.locator('[data-project-id="1"]')).toHaveAttribute('data-expanded', 'true')
  const expandedHeight = (await section.boundingBox())!.height
  await section.getByRole('button', { name: /Alle Projekte/ }).click()
  await section.getByRole('button', { name: /Featured/ }).click()
  await expect(section.locator('[data-project-id="1"]')).toHaveAttribute('data-expanded', 'false')
  expect((await section.boundingBox())!.height).toBeLessThanOrEqual(expandedHeight)
  await page.evaluate(() => window.dispatchEvent(new CustomEvent('openAccordion', { detail: { link: 'projects-fixture-18' } })))
  const target = page.locator('#projects-fixture-18')
  await expect(target).toHaveAttribute('data-expanded', 'true')
  await expect(target).toBeInViewport()
})

test('empty featured panel and reduced motion have no hidden project footprint', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.route('**/api/projects?*', route => route.fulfill({ json: projects.map(project => ({ ...project, featured: false })) }))
  await page.goto('/de')
  const section = page.locator('#projects')
  await expect(section.getByText('Keine Featured Projekte vorhanden.')).toBeVisible()
  await expect(section.locator('[data-project-id]')).toHaveCount(0)
  await section.getByRole('button', { name: /Alle Projekte/ }).click()
  await expect(section.locator('[data-project-id]')).toHaveCount(18)
})
