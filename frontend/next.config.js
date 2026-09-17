/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
}

const withNextIntl = require('next-intl/plugin')('./i18n/request.ts')
module.exports = withNextIntl(nextConfig)
