import { defineConfig } from 'vitest/config'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  resolve: { alias: { '@': fileURLToPath(new URL('.', import.meta.url)) } },
  esbuild: { jsx: 'automatic' },
  test: {
    environment: 'jsdom',
    include: ['tests/**/*.test.{ts,tsx}'],
    setupFiles: ['./tests/setup.ts'],
    coverage: { provider: 'v8', include: ['app/api/chat/route.ts', 'lib/chat-response.ts', 'components/home/Projects.tsx'] },
  },
})
