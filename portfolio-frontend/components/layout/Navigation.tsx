'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

const navItems = [
  { href: '#home', label: 'Home' },
  { href: '#about', label: 'Über mich' },
  { href: '#experience', label: 'Erfahrung' },
  { href: '#projects', label: 'Projekte' },
  { href: '#skills', label: 'Skills' },
  { href: '#contact', label: 'Kontakt' },
]

interface NavigationProps {
  scrolled?: boolean
}

export default function Navigation({ scrolled = false }: NavigationProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [mobileMenuOpen])

  const handleLinkClick = () => {
    setMobileMenuOpen(false)
  }

  return (
    <>
      {/* Desktop Navigation */}
      <nav className="hidden md:flex items-center gap-8">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="text-sm text-text-secondary-light dark:text-text-secondary-dark hover:text-text-light dark:hover:text-text-dark transition-colors font-medium"
          >
            {item.label}
          </Link>
        ))}
      </nav>

      {/* Mobile Menu Button */}
      <button
        className="md:hidden flex flex-col gap-1.5 w-8 h-8 justify-center items-center relative z-[60]"
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        aria-label="Toggle menu"
      >
        <span
          className={`block h-0.5 w-full bg-text-light dark:bg-text-dark transition-all duration-300 ${
            mobileMenuOpen ? 'rotate-45 translate-y-2' : ''
          }`}
        />
        <span
          className={`block h-0.5 w-full bg-text-light dark:bg-text-dark transition-all duration-300 ${
            mobileMenuOpen ? 'opacity-0' : ''
          }`}
        />
        <span
          className={`block h-0.5 w-full bg-text-light dark:bg-text-dark transition-all duration-300 ${
            mobileMenuOpen ? '-rotate-45 -translate-y-2' : ''
          }`}
        />
      </button>

      {/* Mobile Menu Overlay */}
      <div
        className={`fixed inset-0 bg-cream dark:bg-dark-bg md:hidden z-50 transition-transform duration-500 ease-in-out ${
          mobileMenuOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <nav className="flex flex-col items-center justify-start min-h-screen gap-6 px-6 pt-24 pb-8 overflow-y-auto">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={handleLinkClick}
              className="text-3xl text-text-light dark:text-text-dark hover:text-tekhelet transition-colors font-medium"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </>
  )
}
