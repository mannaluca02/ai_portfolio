// @vitest-environment node
import {describe, expect, it, vi} from 'vitest'
import {GET as projects} from '../app/api/projects/route'
import {GET as contact} from '../app/api/contact-info/route'
import {GET as education} from '../app/api/education/route'
import {GET as work} from '../app/api/work-experiences/route'
import {GET as skills} from '../app/api/skills/route'
import {GET as certificates} from '../app/api/certificates/route'

describe.each([
  ['projects', projects], ['contact-info', contact], ['education', education],
  ['work-experiences', work], ['skills', skills], ['certificates', certificates],
] as const)('%s language proxy', (path, get) => {
  it('forwards the English locale', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('[]')))
    const result = await get(new Request(`http://localhost/api/${path}?lang=en`))
    expect(result.status).toBe(200)
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining(`/api/${path}?lang=en`), expect.any(Object))
  })
  it('rejects unsupported locales before contacting the backend', async () => {
    vi.stubGlobal('fetch', vi.fn())
    const result = await get(new Request(`http://localhost/api/${path}?lang=fr`))
    expect(result.status).toBe(400)
    expect(fetch).not.toHaveBeenCalled()
  })
})
