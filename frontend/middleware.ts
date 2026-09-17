import createMiddleware from 'next-intl/middleware'
import {NextRequest, NextResponse} from 'next/server'
import {routing} from './i18n/routing'

const handleLocale = createMiddleware(routing)

export default function middleware(request: NextRequest) {
  // Legal content is available only in German, including legacy inbound URLs.
  const legal = request.nextUrl.pathname.match(/^\/(?:en\/)?(impressum|datenschutz)\/?$/)
  if (legal) return NextResponse.redirect(new URL(`/de/${legal[1]}${request.nextUrl.search}`, request.url), 307)
  return handleLocale(request)
}

export const config = {matcher: '/((?!api|_next|_vercel|.*\\..*).*)'}
