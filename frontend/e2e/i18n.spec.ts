import {test, expect} from '@playwright/test'

test('switching locale preserves query and anchor and persists the choice', async ({page, context}) => {
  await page.route('**/api/**', route => route.fulfill({json: []}))
  await page.goto('/de?ref=test#projects')
  await page.getByRole('link', {name: 'Switch to English'}).click()
  await expect(page).toHaveURL('/en?ref=test#projects')
  await expect(page.locator('html')).toHaveAttribute('lang', 'en')
  await expect(page.getByRole('heading', {name: 'Selected projects'})).toBeVisible()
  expect((await context.cookies()).find(cookie => cookie.name === 'NEXT_LOCALE')?.value).toBe('en')
  await page.goto('/')
  await expect(page).toHaveURL('/en')
})

test('root negotiates language and API cron bypasses locale middleware', async ({request}) => {
  const root = await request.get('/', {headers: {'Accept-Language': 'en-GB,en;q=0.9'}, maxRedirects: 0})
  expect(root.status()).toBe(307)
  expect(root.headers().location).toMatch(/\/en$/)
  const cron = await request.get('/api/keep-alive', {maxRedirects: 0})
  // A disconnected local backend can return 503; it must never redirect.
  expect(cron.status()).not.toBe(307)
  expect(cron.headers().location).toBeUndefined()
})

test('locale homepages have canonical and hreflang; legal pages do not', async ({request}) => {
  for (const locale of ['de', 'en']) {
    const response = await request.get('/' + locale)
    expect(response.status()).toBe(200)
    const html = await response.text()
    expect(html).toContain(`lang="${locale}"`)
    expect(html).toContain(`rel="canonical" href="https://lucamanna.ch/${locale}"`)
    expect(html).toMatch(/hrefLang="de" href="https:\/\/lucamanna.ch\/de"/i)
    expect(html).toMatch(/hrefLang="en" href="https:\/\/lucamanna.ch\/en"/i)
  }
  const legal = await request.get('/de/impressum')
  expect(await legal.text()).not.toMatch(/rel="alternate"[^>]*hrefLang/i)
})
