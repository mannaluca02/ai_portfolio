import {defineRouting} from 'next-intl/routing'

export const routing = defineRouting({
  locales: ['de', 'en'],
  defaultLocale: 'de',
  localePrefix: 'always',
  localeCookie: {name: 'NEXT_LOCALE', maxAge: 60 * 60 * 24 * 365},
  // Only the homepages have translations. Metadata emits their alternates.
  alternateLinks: false,
})
