import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  workers: 1,
  retries: 0,
  outputDir: process.env.PORTFOLIO_TEST_OUTPUT || '/private/tmp/ai-portfolio-browser-results',
  use: { baseURL: 'http://127.0.0.1:3100', screenshot: 'only-on-failure', trace: 'retain-on-failure' },
  projects: [
    { name: 'desktop-chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile-chromium', use: { ...devices['Pixel 7'] } },
    { name: 'mobile-webkit', use: { ...devices['iPhone 13'] } },
  ],
  webServer: {
    command: 'npm run start -- --hostname 127.0.0.1 --port 3100',
    cwd: process.env.PORTFOLIO_TEST_APP || process.cwd(),
    env: { RESEND_API_KEY: 're_offline_test_placeholder', NEXT_TELEMETRY_DISABLED: '1' },
    url: 'http://127.0.0.1:3100',
    reuseExistingServer: false,
  },
})
