'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

interface ContactInfo {
  full_name: string
  title: string
  email: string
  bio: string
}

interface SocialLink {
  platform: string
  url: string
  username?: string
}

// Social Media Icons
const LinkedInIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
  </svg>
)

const GitHubIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd"/>
  </svg>
)

const EmailIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
  </svg>
)

export default function Footer() {
  const currentYear = new Date().getFullYear()
  const [contactInfo, setContactInfo] = useState<ContactInfo | null>(null)
  const [socialLinks, setSocialLinks] = useState<SocialLink[]>([])

  useEffect(() => {
    // Fetch contact info
    fetch('/api/contact-info')
      .then(res => res.json())
      .then(data => setContactInfo(data))
      .catch(err => console.error('Error fetching contact info:', err))

    // Fetch social links
    fetch('/api/social-links')
      .then(res => res.json())
      .then(data => {
        // Ensure data is an array before setting
        if (Array.isArray(data)) {
          setSocialLinks(data)
        } else {
          console.error('Invalid social links data format:', data)
        }
      })
      .catch(err => console.error('Error fetching social links:', err))
  }, [])

  const getSocialIcon = (platform: string) => {
    const platformLower = platform.toLowerCase()
    if (platformLower.includes('linkedin')) return <LinkedInIcon />
    if (platformLower.includes('github')) return <GitHubIcon />
    return null
  }

  return (
    <footer className="bg-background-light dark:bg-background-dark border-t border-gray-200 dark:border-gray-800 py-12">
      <div className="max-w-7xl mx-auto px-6 md:px-12 lg:px-24">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {/* About */}
          <div className="lg:col-span-1">
            <h3 className="text-xl font-bold mb-4 text-tekhelet">
              {contactInfo?.full_name || 'Loading...'}
            </h3>
            <p className="text-text-secondary-light dark:text-text-secondary-dark text-sm leading-relaxed">
              {contactInfo?.title || 'Data Scientist & Full-Stack Developer'}
            </p>
          </div>

          {/* Quick Links - Split into 2 columns */}
          <div className="lg:col-span-2">
            <h3 className="text-lg font-semibold mb-4 text-text-light dark:text-text-dark">
              Navigation
            </h3>
            <div className="grid grid-cols-2 gap-x-8 gap-y-2">
              <Link
                href="#about"
                className="text-sm text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
              >
                Über mich
              </Link>
              <Link
                href="#projects"
                className="text-sm text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
              >
                Projekte
              </Link>
              <Link
                href="#experience"
                className="text-sm text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
              >
                Erfahrung
              </Link>
              <Link
                href="#skills"
                className="text-sm text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
              >
                Skills
              </Link>
              <Link
                href="#education"
                className="text-sm text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
              >
                Ausbildung
              </Link>
              <Link
                href="#certificates"
                className="text-sm text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
              >
                Zertifikate
              </Link>
              <Link
                href="#contact"
                className="text-sm text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
              >
                Kontakt
              </Link>
            </div>
          </div>

          {/* Contact & Social */}
          <div className="lg:col-span-1">
            <h3 className="text-lg font-semibold mb-4 text-text-light dark:text-text-dark">
              Connect
            </h3>
            <div className="space-y-3">
              {/* Email */}
              {contactInfo?.email && (
                <a
                  href={`mailto:${contactInfo.email}`}
                  className="flex items-center gap-2 text-sm text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors group"
                >
                  <span className="group-hover:scale-110 transition-transform">
                    <EmailIcon />
                  </span>
                  <span className="truncate">{contactInfo.email}</span>
                </a>
              )}

              {/* Social Icons */}
              <div className="flex items-center gap-4 pt-2">
                {socialLinks.map((link) => {
                  const icon = getSocialIcon(link.platform)
                  if (!icon) return null

                  return (
                    <a
                      key={link.platform}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-all hover:scale-110"
                      aria-label={link.platform}
                      title={link.platform}
                    >
                      {icon}
                    </a>
                  )
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-text-secondary-light dark:text-text-secondary-dark">
            {/* Copyright */}
            <div className="text-center md:text-left">
              <p>&copy; {currentYear} {contactInfo?.full_name || 'Portfolio'}. Alle Rechte vorbehalten.</p>
            </div>

            {/* Legal Links */}
            <div className="flex items-center gap-4">
              <Link
                href="/impressum"
                className="hover:text-tekhelet transition-colors"
              >
                Impressum
              </Link>
              <span className="text-gray-400">•</span>
              <Link
                href="/datenschutz"
                className="hover:text-tekhelet transition-colors"
              >
                Datenschutz
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
