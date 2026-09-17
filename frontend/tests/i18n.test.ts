// @vitest-environment node
import {describe, expect, it} from 'vitest'
import {NextRequest} from 'next/server'
import middleware, {config} from '../middleware'

describe('locale routing', () => {
  it.each([
    [{}, '/de'],
    [{'accept-language': 'en-GB,en;q=0.9,de;q=0.5'}, '/en'],
    [{'cookie': 'NEXT_LOCALE=de', 'accept-language': 'en'}, '/de'],
    [{'cookie': 'NEXT_LOCALE=xx', 'accept-language': 'en'}, '/en'],
  ])('negotiates a temporary redirect: %j', (headers, path) => {
    const response = middleware(new NextRequest('https://lucamanna.ch/', {headers}))
    expect(response.status).toBe(307)
    expect(response.headers.get('location')).toBe(`https://lucamanna.ch${path}`)
  })
  it.each(['/api/keep-alive', '/api/chat', '/_next/static/a.js', '/icon.png', '/sitemap.xml', '/robots.txt'])('excludes %s', path => {
    expect(new RegExp(`^${config.matcher}$`).test(path)).toBe(false)
  })
  it.each(['/de', '/en'])('keeps explicit locale %s', path => {
    const response = middleware(new NextRequest(`https://lucamanna.ch${path}`, {headers: {'accept-language': 'fr'}}))
    expect(response.status).toBe(200)
    expect(response.headers.get('location')).toBeNull()
  })
})
