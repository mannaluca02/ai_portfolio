'use client'

import { ReactNode, useEffect } from 'react'
import Header from './Header'
import Footer from './Footer'

export default function ClientLayout({ children }: { children: ReactNode }) {
  useEffect(() => {
    // Check system preference on mount
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)')

    if (darkModeQuery.matches) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }

    // Listen for changes
    const handler = (e: MediaQueryListEvent) => {
      if (e.matches) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }

    darkModeQuery.addEventListener('change', handler)
    return () => darkModeQuery.removeEventListener('change', handler)
  }, [])

  return (
    <>
      <Header />
      <main>
        {children}
      </main>
      <Footer />
    </>
  )
}
