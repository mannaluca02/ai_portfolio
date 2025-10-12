'use client'

import { useEffect, useState } from 'react'
import FadeInSection from '../ui/FadeInSection'

interface ContactInfo {
  full_name: string
  title: string
  email: string
  phone?: string
  city?: string
  country?: string
  availability?: string
}

export default function Contact() {
  const [contactInfo, setContactInfo] = useState<ContactInfo | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle')

  useEffect(() => {
    // Fetch contact info
    fetch('/api/contact-info')
      .then(res => res.json())
      .then(data => {
        console.log('Contact Info loaded:', data)
        setContactInfo(data)
      })
      .catch(err => console.error('Error fetching contact info:', err))
  }, [])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setSubmitStatus('idle')

    try {
      // Simulate form submission (replace with actual API call)
      await new Promise(resolve => setTimeout(resolve, 1500))

      // Reset form on success
      setFormData({ name: '', email: '', subject: '', message: '' })
      setSubmitStatus('success')

      // Clear success message after 5 seconds
      setTimeout(() => setSubmitStatus('idle'), 5000)
    } catch (error) {
      console.error('Error submitting form:', error)
      setSubmitStatus('error')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section id="contact" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
      <div className="max-w-5xl mx-auto space-y-16">
        {/* Section Label */}
        <FadeInSection>
          <span className="inline-block text-xs uppercase tracking-[0.2em] text-text-secondary-light dark:text-text-secondary-dark font-medium">
            07 — Kontakt
          </span>
        </FadeInSection>

        {/* Section Title */}
        <FadeInSection delay={100}>
          <h2 className="text-5xl md:text-6xl font-semibold tracking-tight text-text-light dark:text-text-dark">
            Kontakt aufnehmen
          </h2>
        </FadeInSection>

        {/* Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
          {/* Left Column - Contact Info */}
          <FadeInSection delay={200}>
            <div className="space-y-8">
              <div>
                <h3 className="text-xl font-semibold text-text-light dark:text-text-dark mb-6">
                  Kontaktinformationen
                </h3>

                {!contactInfo ? (
                  <p className="text-text-secondary-light dark:text-text-secondary-dark">
                    Lädt Kontaktinformationen...
                  </p>
                ) : (
                  <div className="space-y-6 text-text-secondary-light dark:text-text-secondary-dark">
                    {contactInfo.email && (
                      <div>
                        <p className="text-sm uppercase tracking-wider mb-1">Email</p>
                        <a
                          href={`mailto:${contactInfo.email}`}
                          className="text-lg text-text-light dark:text-text-dark hover:text-tekhelet transition-colors"
                        >
                          {contactInfo.email}
                        </a>
                      </div>
                    )}

                    {contactInfo.phone && (
                      <div>
                        <p className="text-sm uppercase tracking-wider mb-1">Telefon</p>
                        <a
                          href={`tel:${contactInfo.phone}`}
                          className="text-lg text-text-light dark:text-text-dark hover:text-tekhelet transition-colors"
                        >
                          {contactInfo.phone}
                        </a>
                      </div>
                    )}

                    {(contactInfo.city || contactInfo.country) && (
                      <div>
                        <p className="text-sm uppercase tracking-wider mb-1">Standort</p>
                        <p className="text-lg text-text-light dark:text-text-dark">
                          {[contactInfo.city, contactInfo.country].filter(Boolean).join(', ')}
                        </p>
                      </div>
                    )}

                    {contactInfo.availability && (
                      <div>
                        <p className="text-sm uppercase tracking-wider mb-1">Verfügbarkeit</p>
                        <p className="text-lg text-text-light dark:text-text-dark">
                          {contactInfo.availability}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </FadeInSection>

          {/* Right Column - Contact Form */}
          <FadeInSection delay={300}>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="name" className="block text-sm uppercase tracking-wider text-text-secondary-light dark:text-text-secondary-dark mb-2">
                  Name *
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full px-0 py-3 bg-transparent border-b border-gray-300 dark:border-gray-700 text-text-light dark:text-text-dark placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:border-tekhelet transition-colors"
                  placeholder="Ihr Name"
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm uppercase tracking-wider text-text-secondary-light dark:text-text-secondary-dark mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-0 py-3 bg-transparent border-b border-gray-300 dark:border-gray-700 text-text-light dark:text-text-dark placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:border-tekhelet transition-colors"
                  placeholder="ihre.email@beispiel.com"
                />
              </div>

              <div>
                <label htmlFor="subject" className="block text-sm uppercase tracking-wider text-text-secondary-light dark:text-text-secondary-dark mb-2">
                  Betreff *
                </label>
                <input
                  type="text"
                  id="subject"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  required
                  className="w-full px-0 py-3 bg-transparent border-b border-gray-300 dark:border-gray-700 text-text-light dark:text-text-dark placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:border-tekhelet transition-colors"
                  placeholder="Worum geht es?"
                />
              </div>

              <div>
                <label htmlFor="message" className="block text-sm uppercase tracking-wider text-text-secondary-light dark:text-text-secondary-dark mb-2">
                  Nachricht *
                </label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows={6}
                  className="w-full px-0 py-3 bg-transparent border-b border-gray-300 dark:border-gray-700 text-text-light dark:text-text-dark placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:border-tekhelet transition-colors resize-none"
                  placeholder="Ihre Nachricht..."
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full px-8 py-4 bg-tekhelet text-cream rounded-xl hover:opacity-90 transition-all duration-300 font-medium text-base disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Wird gesendet...' : 'Nachricht senden'}
              </button>

              {submitStatus === 'success' && (
                <div className="pt-4 text-sm text-green-600 dark:text-green-400">
                  Vielen Dank für Ihre Nachricht! Ich werde mich so schnell wie möglich bei Ihnen melden.
                </div>
              )}

              {submitStatus === 'error' && (
                <div className="pt-4 text-sm text-red-600 dark:text-red-400">
                  Es gab einen Fehler beim Senden Ihrer Nachricht. Bitte versuchen Sie es später erneut.
                </div>
              )}
            </form>
          </FadeInSection>
        </div>
      </div>
    </section>
  )
}
