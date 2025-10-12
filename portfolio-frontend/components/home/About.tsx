'use client'

import { useEffect, useState } from 'react'
import FadeInSection from '@/components/ui/FadeInSection'

interface ContactInfo {
  full_name: string
  title: string
  email: string
  phone?: string
  city?: string
  country?: string
  availability?: string
  bio: string
  profile_image_url?: string
}

export default function About() {
  const [contactInfo, setContactInfo] = useState<ContactInfo | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchContactInfo = async () => {
      try {
        const response = await fetch('/api/contact-info')
        if (response.ok) {
          const data = await response.json()
          setContactInfo(data)
        }
      } catch (error) {
        console.error('Error fetching contact info:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchContactInfo()
  }, [])

  if (loading) {
    return (
      <section id="about" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
        <div className="max-w-5xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
            <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section id="about" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
      <div className="max-w-5xl mx-auto space-y-16">
        {/* Section Label */}
        <FadeInSection>
          <span className="inline-block text-xs uppercase tracking-[0.2em] text-text-secondary-light dark:text-text-secondary-dark font-medium">
            01 — Über mich
          </span>
        </FadeInSection>

        {/* Content */}
        <div className="grid md:grid-cols-5 gap-12 items-start">
          {/* Text Content */}
          <div className="md:col-span-3 space-y-8">
            <FadeInSection delay={100}>
              <h2 className="text-5xl md:text-6xl font-semibold tracking-tight text-text-light dark:text-text-dark">
                Wer ich bin
              </h2>
            </FadeInSection>

            <FadeInSection delay={200}>
              <div className="space-y-6">
                {contactInfo?.bio ? (
                  <p className="text-xl md:text-2xl text-text-secondary-light dark:text-text-secondary-dark leading-relaxed">
                    {contactInfo.bio}
                  </p>
                ) : (
                  <p className="text-xl md:text-2xl text-text-secondary-light dark:text-text-secondary-dark leading-relaxed">
                    Willkommen auf meinem Portfolio! Hier erfahren Sie mehr über meine Erfahrungen und Projekte.
                  </p>
                )}
              </div>
            </FadeInSection>

            {/* Quick Facts */}
            {contactInfo && (
              <FadeInSection delay={300}>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-8">
                  {contactInfo.city && contactInfo.country && (
                    <div className="space-y-2">
                      <div className="text-sm uppercase tracking-wider text-text-secondary-light dark:text-text-secondary-dark">
                        Standort
                      </div>
                      <div className="text-lg text-text-light dark:text-text-dark">
                        {contactInfo.city}, {contactInfo.country}
                      </div>
                    </div>
                  )}

                  {contactInfo.title && (
                    <div className="space-y-2">
                      <div className="text-sm uppercase tracking-wider text-text-secondary-light dark:text-text-secondary-dark">
                        Rolle
                      </div>
                      <div className="text-lg text-text-light dark:text-text-dark">
                        {contactInfo.title}
                      </div>
                    </div>
                  )}

                  {contactInfo.availability && (
                    <div className="space-y-2 sm:col-span-2">
                      <div className="text-sm uppercase tracking-wider text-text-secondary-light dark:text-text-secondary-dark">
                        Verfügbarkeit
                      </div>
                      <div className="text-lg text-text-light dark:text-text-dark">
                        {contactInfo.availability}
                      </div>
                    </div>
                  )}
                </div>
              </FadeInSection>
            )}
          </div>

          {/* Profile Image */}
          {contactInfo?.profile_image_url && (
            <FadeInSection delay={400} className="md:col-span-2">
              <div className="relative w-full aspect-square max-w-sm mx-auto">
                <div className="absolute inset-0 bg-gradient-to-br from-tekhelet/20 to-transparent rounded-2xl"></div>
                <img
                  src={contactInfo.profile_image_url}
                  alt={contactInfo.full_name}
                  className="relative w-full h-full object-cover rounded-2xl shadow-lg"
                />
              </div>
            </FadeInSection>
          )}
        </div>
      </div>
    </section>
  )
}
