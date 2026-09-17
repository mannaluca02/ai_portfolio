'use client'

import {useTranslations, useLocale} from 'next-intl'

import { useState, useEffect } from 'react'
import {usePathname} from 'next/navigation'

export default function Navbar() {
  const t = useTranslations('Navbar')
  const locale = useLocale()
  const navigationLinks = [
    { href: '#home', label: 'Home' },
    { href: '#about', label: t('about') },
    { href: '#experience', label: t('experience') },
    { href: '#projects', label: t('projects') },
    { href: '#education', label: t('education') },
    { href: '#skills', label: 'Skills' },
    { href: '#certificates', label: t('certificates') },
    { href: '#contact', label: t('contact') },
  ]

  const pathname = usePathname()
  const otherLocale = locale === 'de' ? 'en' : 'de'
  const targetPath = pathname.replace(/^\/(de|en)(?=\/|$)/, '/' + otherLocale)
  const switchLanguage = (event: React.MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault()
    document.cookie = 'NEXT_LOCALE=' + otherLocale + '; Path=/; Max-Age=31536000; SameSite=Lax'
    window.location.assign(targetPath + window.location.search + window.location.hash)
  }
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }

    return () => {
      document.body.style.overflow = ''
    }
  }, [isMobileMenuOpen])

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false)
  }

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    if (!document.getElementById(href.replace('#', ''))) return
    e.preventDefault()
    window.history.replaceState(null, '', href)
    closeMobileMenu()

    // Get the target section
    const targetId = href.replace('#', '')
    const targetSection = document.getElementById(targetId)

    if (targetSection) {
      targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  return (
    <>
      {/* Fixed Header */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled
            ? 'bg-cream/95 dark:bg-dark-bg/95 backdrop-blur-md shadow-sm'
            : 'bg-transparent'
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div className="flex items-center justify-between gap-4 h-16 md:h-20">
            {/* Logo */}
            <a
              href={`/${locale}#home`}
              className="text-xl font-bold text-text-light dark:text-text-dark hover:text-tekhelet transition-colors relative z-50"
              onClick={(e) => handleNavClick(e, '#home')}
            >
              LM
            </a>

            {/* Desktop Navigation */}
            <nav className="hidden xl:flex items-center gap-8">
              {navigationLinks.map((link) => (
                <a
                  key={link.href}
                  href={`/${locale}${link.href}`}
                  onClick={(e) => handleNavClick(e, link.href)}
                  className="text-sm font-medium text-text-secondary-light dark:text-text-secondary-dark hover:text-text-light dark:hover:text-text-dark transition-colors"
                >
                  {link.label}
                </a>
              ))}
            </nav>

            <a href={targetPath} hrefLang={otherLocale} lang={otherLocale}
              onClick={switchLanguage} aria-label={otherLocale === 'en' ? 'Switch to English' : 'Auf Deutsch wechseln'}
              className="relative z-50 whitespace-nowrap shrink-0 text-sm font-medium px-3 py-2 border rounded-lg">
              {locale.toUpperCase()} / {otherLocale.toUpperCase()}
            </a>
            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="xl:hidden relative z-50 w-10 h-10 flex items-center justify-center"
              aria-label={t('toggleMenu')}
            >
              <div className="w-6 h-5 flex flex-col justify-between">
                <span
                  className={`block h-0.5 w-full bg-text-light dark:bg-text-dark transition-all duration-300 ${
                    isMobileMenuOpen ? 'rotate-45 translate-y-2' : ''
                  }`}
                />
                <span
                  className={`block h-0.5 w-full bg-text-light dark:bg-text-dark transition-all duration-300 ${
                    isMobileMenuOpen ? 'opacity-0' : ''
                  }`}
                />
                <span
                  className={`block h-0.5 w-full bg-text-light dark:bg-text-dark transition-all duration-300 ${
                    isMobileMenuOpen ? '-rotate-45 -translate-y-2' : ''
                  }`}
                />
              </div>
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-text-light/20 dark:bg-text-dark/20 backdrop-blur-sm z-40 xl:hidden"
            onClick={closeMobileMenu}
          />

          {/* Menu Panel */}
          <div
            className={`fixed top-0 right-0 bottom-0 w-full sm:w-80 bg-cream dark:bg-dark-bg z-40 xl:hidden transition-transform duration-300 ${
              isMobileMenuOpen ? 'translate-x-0' : 'translate-x-full'
            }`}
          >
            <nav className="flex flex-col items-center justify-start h-full gap-6 px-8 pt-24 pb-8 overflow-y-auto" data-lenis-prevent>
              {navigationLinks.map((link, index) => (
                <a
                  key={link.href}
                  href={`/${locale}${link.href}`}
                  onClick={(e) => handleNavClick(e, link.href)}
                  className="text-2xl sm:text-3xl font-medium text-text-light dark:text-text-dark hover:text-tekhelet transition-colors"
                  style={{
                    animation: `fadeInUp 0.3s ease-out forwards ${index * 0.1}s`,
                    opacity: 0,
                  }}
                >
                  {link.label}
                </a>
              ))}
            </nav>
          </div>
        </>
      )}

      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </>
  )
}
