'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Navigation from './Navigation'

export default function Header() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 100)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled
          ? 'bg-cream/98 dark:bg-dark-bg/98 backdrop-blur-xl border-b border-text-light/10 dark:border-text-dark/10'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 md:px-12 lg:px-20">
        <div className={`flex items-center justify-between transition-all duration-500 ${
          scrolled ? 'py-4' : 'py-6'
        }`}>
          {/* Logo */}
          <Link
            href="/"
            className="text-lg font-semibold tracking-tight text-text-light dark:text-text-dark hover:text-tekhelet transition-colors z-[60]"
          >
            LM
          </Link>

          {/* Navigation */}
          <Navigation scrolled={scrolled} />
        </div>
      </div>
    </header>
  )
}
