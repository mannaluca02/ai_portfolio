// Local-only preview for Orca browser checks. Never forwards API calls.
import http from 'node:http'
import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import { resolve } from 'node:path'

const app = process.env.PORTFOLIO_TEST_APP
if (!app || !existsSync(resolve(app, '.next/BUILD_ID'))) {
  throw new Error('PORTFOLIO_TEST_APP must point to an isolated production build without .env files')
}
const projects = Array.from({ length: 18 }, (_, index) => ({
  id: index + 1, name: `Fixture project ${index + 1}`,
  description: 'A documented project. '.repeat(30), featured: index < 2,
  project_type: 'Personal', section: 'projects', slug: `fixture-${index + 1}`,
  anchor: `projects-fixture-${index + 1}`, your_role: 'Developer', technologies: ['Python'],
}))
const next = spawn(process.execPath, [resolve(app, 'node_modules/next/dist/bin/next'),
  'start', '--hostname', '127.0.0.1', '--port', '3101'], {
  cwd: app, stdio: 'inherit', env: { ...process.env, NEXT_TELEMETRY_DISABLED: '1',
    RESEND_API_KEY: 're_offline_test_placeholder' },
})
const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://127.0.0.1:3100')
  if (url.pathname.startsWith('/api/')) {
    res.setHeader('Content-Type', 'application/json')
    res.setHeader('Cache-Control', 'no-store')
    const empty = req.headers.cookie?.includes('empty-featured=1')
    const data = url.pathname === '/api/projects'
      ? projects.map(project => ({ ...project, featured: empty ? false : project.featured }))
      : url.pathname === '/api/chat'
        ? { answer: 'Synthetic unsupported claim.', outcome: 'answered', sources: [],
          confidence: 0.99, verification: { verified: false } }
        : url.pathname === '/api/contact-info' ? {} : []
    res.end(JSON.stringify(data))
    return
  }
  const proxy = http.request({ hostname: '127.0.0.1', port: 3101,
    path: req.url, method: req.method, headers: req.headers }, upstream => {
    res.writeHead(upstream.statusCode, upstream.headers)
    upstream.pipe(res)
  })
  proxy.on('error', () => { res.writeHead(502); res.end('Preview is starting') })
  req.pipe(proxy)
})
server.listen(3100, '127.0.0.1', () => console.log('Orca fixture preview: http://127.0.0.1:3100'))
const stop = () => { server.close(); next.kill('SIGTERM') }
process.on('SIGINT', stop)
process.on('SIGTERM', stop)
next.on('exit', () => server.close())
