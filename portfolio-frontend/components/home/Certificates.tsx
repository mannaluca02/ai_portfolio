'use client'

import { useEffect, useState } from 'react'
import FadeInSection from '@/components/ui/FadeInSection'

interface Certificate {
  id: number
  name: string
  issuing_organization: string
  issue_date: string
  expiration_date?: string
  credential_id?: string
  description?: string
  certificate_url?: string
}

export default function Certificates() {
  const [certificates, setCertificates] = useState<Certificate[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<number | null>(null)

  useEffect(() => {
    const fetchCertificates = async () => {
      try {
        const response = await fetch('/api/certificates')
        if (response.ok) {
          const data = await response.json()
          if (Array.isArray(data)) {
            setCertificates(data)
          }
        }
      } catch (error) {
        console.error('Error fetching certificates:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchCertificates()
  }, [])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('de-DE', { month: 'short', year: 'numeric' })
  }

  const isExpired = (expirationDate?: string) => {
    if (!expirationDate) return false
    return new Date(expirationDate) < new Date()
  }

  if (loading) {
    return (
      <section id="certificates" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
        <div className="max-w-5xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
            <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-48 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </section>
    )
  }

  if (certificates.length === 0) {
    return null
  }

  return (
    <section id="certificates" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
      <div className="max-w-5xl mx-auto space-y-16">
        {/* Section Label */}
        <FadeInSection>
          <span className="inline-block text-xs uppercase tracking-[0.2em] text-text-secondary-light dark:text-text-secondary-dark font-medium">
            06 — Zertifikate
          </span>
        </FadeInSection>

        {/* Section Title */}
        <FadeInSection delay={100}>
          <h2 className="text-5xl md:text-6xl font-semibold tracking-tight text-text-light dark:text-text-dark">
            Zertifizierungen
          </h2>
        </FadeInSection>

        {/* Certificates List */}
        <div className="space-y-4">
          {certificates.map((cert, index) => {
            const isExpanded = expandedId === cert.id
            const expired = isExpired(cert.expiration_date)

            return (
              <FadeInSection key={cert.id} delay={200 + index * 50}>
                <div
                  onClick={() => setExpandedId(isExpanded ? null : cert.id)}
                  className="group cursor-pointer border-b border-gray-200 dark:border-gray-800 pb-6 hover:border-tekhelet dark:hover:border-tekhelet transition-colors duration-300"
                >
                  {/* Compact View */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-2xl font-semibold text-text-light dark:text-text-dark group-hover:text-tekhelet transition-colors mb-2">
                        {cert.name}
                      </h3>
                      <div className="flex flex-wrap items-center gap-3 text-text-secondary-light dark:text-text-secondary-dark">
                        <span className="font-medium">{cert.issuing_organization}</span>
                        <span className="text-sm">
                          {formatDate(cert.issue_date)}
                          {cert.expiration_date && ` - ${formatDate(cert.expiration_date)}`}
                        </span>
                        {cert.expiration_date && (
                          <span className={`text-xs px-2 py-0.5 rounded ${
                            expired
                              ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                              : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                          }`}>
                            {expired ? 'Abgelaufen' : 'Gültig'}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Expand/Collapse Icon */}
                    <div className="flex-shrink-0">
                      <svg
                        className={`w-6 h-6 text-text-secondary-light dark:text-text-secondary-dark group-hover:text-tekhelet transition-all duration-300 ${
                          isExpanded ? 'rotate-180' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  <div
                    className={`overflow-hidden transition-all duration-300 ease-in-out ${
                      isExpanded ? 'max-h-[2000px] opacity-100 mt-6' : 'max-h-0 opacity-0'
                    }`}
                  >
                    <div className="space-y-6 pt-6 border-t border-gray-100 dark:border-gray-800">
                      {/* Description */}
                      {cert.description && (
                        <p className="text-lg text-text-secondary-light dark:text-text-secondary-dark leading-relaxed">
                          {cert.description}
                        </p>
                      )}

                      {/* Meta Information */}
                      <div className="flex flex-wrap gap-4 text-sm text-text-secondary-light dark:text-text-secondary-dark">
                        {cert.credential_id && (
                          <span className="flex items-center gap-1.5">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                            </svg>
                            Credential ID: {cert.credential_id}
                          </span>
                        )}
                      </div>

                      {/* Certificate Link */}
                      {cert.certificate_url && (
                        <a
                          href={cert.certificate_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="inline-flex items-center gap-2 text-tekhelet hover:text-tekhelet/80 transition-colors font-medium"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                          Zertifikat anzeigen
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </FadeInSection>
            )
          })}
        </div>
      </div>
    </section>
  )
}
