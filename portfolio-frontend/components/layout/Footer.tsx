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

  return (
    <footer className="bg-background-light dark:bg-background-dark border-t border-gray-200 dark:border-gray-800 py-12">
      <div className="max-w-7xl mx-auto px-6 md:px-12 lg:px-24">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* About */}
          <div>
            <h3 className="text-xl font-bold mb-4 text-tekhelet">
              {contactInfo?.full_name || 'Loading...'}
            </h3>
            <p className="text-text-secondary-light dark:text-text-secondary-dark">
              {contactInfo?.title || 'Full-Stack Developer & KI-Enthusiast'}
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-xl font-bold mb-4 text-text-light dark:text-text-dark">
              Quick Links
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="#about"
                  className="text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
                >
                  Über mich
                </Link>
              </li>
              <li>
                <Link
                  href="#experience"
                  className="text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
                >
                  Erfahrung
                </Link>
              </li>
              <li>
                <Link
                  href="#education"
                  className="text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
                >
                  Ausbildung
                </Link>
              </li>
              <li>
                <Link
                  href="#projects"
                  className="text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
                >
                  Projekte
                </Link>
              </li>
              <li>
                <Link
                  href="#skills"
                  className="text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
                >
                  Skills
                </Link>
              </li>
              <li>
                <Link
                  href="#certificates"
                  className="text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
                >
                  Zertifikate
                </Link>
              </li>
              <li>
                <Link
                  href="#contact"
                  className="text-text-secondary-light dark:text-text-secondary-dark hover:text-tekhelet transition-colors"
                >
                  Kontakt
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact & Social */}
          <div>
            <h3 className="text-xl font-bold mb-4 text-text-light dark:text-text-dark">
              Kontakt & Social
            </h3>
            <ul className="space-y-2 text-text-secondary-light dark:text-text-secondary-dark">
              {contactInfo?.email && (
                <li>
                  <a
                    href={`mailto:${contactInfo.email}`}
                    className="hover:text-tekhelet transition-colors"
                  >
                    {contactInfo.email}
                  </a>
                </li>
              )}
              {socialLinks.map((link) => (
                <li key={link.platform}>
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-tekhelet transition-colors"
                  >
                    {link.platform}: {link.username || link.url.split('/').pop()}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-200 dark:border-gray-800 pt-8 text-center text-text-secondary-light dark:text-text-secondary-dark">
          <p>&copy; {currentYear} {contactInfo?.full_name || 'Portfolio'}. Alle Rechte vorbehalten.</p>
        </div>
      </div>
    </footer>
  )
}
