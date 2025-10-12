import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import SmoothScroll from '@/components/SmoothScroll'
import StructuredData from '@/components/StructuredData'
import { Providers } from './providers'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
})

export const metadata: Metadata = {
  metadataBase: new URL('https://lucamanna.ch'),
  title: {
    default: 'Luca Manna - Data Scientist & Full-Stack Developer | Basel',
    template: '%s | Luca Manna'
  },
  description: 'Luca Manna - Data Science Student (BSc) & Full-Stack Developer aus Basel. Spezialisiert auf Machine Learning, Python, React und innovative Weblösungen. Portfolio mit KI-Chatbot.',
  keywords: [
    'Luca Manna',
    'Data Scientist Basel',
    'Machine Learning',
    'Full-Stack Developer Schweiz',
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
    title: 'Luca Manna - Data Scientist & Full-Stack Developer',
    description: 'Data Science Student (BSc) & Full-Stack Developer aus Basel. Spezialisiert auf Machine Learning, Python, React und innovative Weblösungen.',
    siteName: 'Luca Manna Portfolio',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Luca Manna - Data Scientist & Full-Stack Developer',
    description: 'Data Science Student (BSc) & Full-Stack Developer aus Basel. Spezialisiert auf Machine Learning, Python und React.',
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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="de" suppressHydrationWarning>
      <head>
        <StructuredData />
      </head>
      <body className={inter.className}>
        <Providers>
          <SmoothScroll />
          <Navbar />
          <main>{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  )
}
