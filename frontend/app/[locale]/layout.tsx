import {NextIntlClientProvider, hasLocale} from 'next-intl'
import {getMessages, setRequestLocale} from 'next-intl/server'
import {notFound} from 'next/navigation'
import {routing} from '@/i18n/routing'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '../globals.css'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import SmoothScroll from '@/components/SmoothScroll'
import StructuredData from '@/components/StructuredData'
import { Providers } from '../providers'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
})

const baseMetadata: Metadata = {
  metadataBase: new URL('https://lucamanna.ch'),
  title: {
    default: 'Luca Manna - Data Scientist & ML Engineer | Basel',
    template: '%s | Luca Manna'
  },
  description: 'Luca Manna - Data Science Student (BSc) & ML Engineer aus Basel. Spezialisiert auf Machine Learning, Python, React und innovative Weblösungen. Portfolio mit KI-Chatbot.',
  keywords: [
    'Luca Manna',
    'Data Scientist Basel',
    'Machine Learning',
    'ML Engineer Schweiz',
    'Machine Learning Engineer',
    'Python Developer',
    'FHNW Student',
    'Data Science Student',
    'React Developer',
    'Basel',
    'Schweiz',
    'Portfolio',
    'Web Development',
    'Künstliche Intelligenz',
    'Deep Learning',
    'Software Engineer'
  ],
  authors: [{ name: 'Luca Manna', url: 'https://lucamanna.ch' }],
  creator: 'Luca Manna',
  publisher: 'Luca Manna',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: 'website',
    locale: 'de_CH',
    url: 'https://lucamanna.ch',
    title: 'Luca Manna - Data Scientist & ML Engineer',
    description: 'Data Science Student (BSc) & ML Engineer aus Basel. Spezialisiert auf Machine Learning, Python, React und innovative Weblösungen.',
    siteName: 'Luca Manna Portfolio',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Luca Manna - Data Scientist & ML Engineer',
    description: 'Data Science Student (BSc) & ML Engineer aus Basel. Spezialisiert auf Machine Learning, Python und React.',
    creator: '@lucamanna',
  },
  robots: {
    index: true,
    follow: true,
    nocache: false,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: 'https://lucamanna.ch',
  },
  verification: {
    // Google Search Console verification code (später hinzufügen)
    // google: 'your-verification-code',
  },
  manifest: '/manifest.webmanifest',
  icons: {
    icon: [
      { url: '/icon.png', sizes: 'any' },
    ],
    apple: [
      { url: '/apple-icon.png', sizes: '180x180', type: 'image/png' },
    ],
    shortcut: '/icon.png',
  },
}

export function generateStaticParams() { return routing.locales.map(locale => ({locale})) }

export function generateMetadata({params: {locale}}: {params: {locale: string}}): Metadata {
  const description = locale === 'en'
    ? 'Luca Manna - Data Science student (BSc) & ML Engineer based in Basel. Specialising in Machine Learning, Python, React and web development.'
    : baseMetadata.description!
  return {...baseMetadata, description,
    keywords: locale === 'en' ? ['Luca Manna', 'Data Scientist Basel', 'Machine Learning', 'Python', 'Switzerland', 'Portfolio'] : baseMetadata.keywords,
    alternates: {canonical: '/' + locale},
    openGraph: {...baseMetadata.openGraph, description, url: '/' + locale, locale: locale === 'en' ? 'en_GB' : 'de_CH', alternateLocale: locale === 'en' ? ['de_CH'] : ['en_GB']},
    twitter: {...baseMetadata.twitter, description},
  }
}

export default async function RootLayout({children, params: {locale}}: {
  children: React.ReactNode; params: {locale: string}
}) {
  if (!hasLocale(routing.locales, locale)) notFound()
  setRequestLocale(locale)
  const messages = await getMessages()
  return (
    <html lang={locale} suppressHydrationWarning>
      <head>
        <StructuredData />
      </head>
      <body className={inter.className}>
        <NextIntlClientProvider locale={locale} messages={messages}>
        <Providers>
          <SmoothScroll />
          <Navbar />
          <main>{children}</main>
          <Footer />
        </Providers>
        </NextIntlClientProvider>
      </body>
    </html>
  )
}
