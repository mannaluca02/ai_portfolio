'use client'

import { useEffect, useState, useRef } from 'react'
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
  slug: string
  section: string
  anchor: string
}

export default function Certificates() {
  const [certificates, setCertificates] = useState<Certificate[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [viewingCertificate, setViewingCertificate] = useState<Certificate | null>(null)
  const mobileModalRef = useRef<HTMLDivElement>(null)
  const [touchStart, setTouchStart] = useState<number>(0)
  const [touchEnd, setTouchEnd] = useState<number>(0)

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

  // ESC key handler to close modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && viewingCertificate) {
        setViewingCertificate(null)
      }
    }

    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [viewingCertificate])

  // Handle swipe down to close mobile panel
  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchStart(e.touches[0].clientY)
  }

  const handleTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.touches[0].clientY)
  }

  const handleTouchEnd = () => {
    // Swipe down detected (at least 100px)
    if (touchStart - touchEnd < -100) {
      setViewingCertificate(null)
    }
  }

  // Handle accordion opening from chatbot links
  useEffect(() => {
    const handleOpenAccordion = (event: CustomEvent) => {
      const link = event.detail.link

      // Check if this link is for the certificates section
      if (link.includes('certificate')) {
        // Find the certificate by matching the slug
        const certificate = certificates.find(cert => {
          const fullSlug = `${cert.section}-${cert.slug}`
          return link === fullSlug || link === cert.slug || link.endsWith(cert.slug)
        })

        if (certificate) {
          setExpandedId(certificate.id)

          // Scroll to the section after a short delay
          setTimeout(() => {
            const element = document.getElementById('certificates')
            if (element) {
              element.scrollIntoView({ behavior: 'smooth', block: 'start' })
            }
          }, 100)
        }
      }
    }

    window.addEventListener('openAccordion', handleOpenAccordion as EventListener)
    return () => window.removeEventListener('openAccordion', handleOpenAccordion as EventListener)
  }, [certificates])

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

                      {/* Certificate View Button */}
                      {cert.certificate_url && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setViewingCertificate(cert)
                          }}
                          className="inline-flex items-center gap-2 text-tekhelet hover:text-tekhelet/80 transition-colors font-medium"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                          Zertifikat anzeigen
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </FadeInSection>
            )
          })}
        </div>
      </div>

      {/* Certificate Viewer - Desktop Modal & Mobile Slide-Up */}
      {viewingCertificate && (
        <>
          {/* Backdrop */}
          <div
            onClick={() => setViewingCertificate(null)}
            className="fixed inset-0 bg-text-light/20 dark:bg-dark-bg/50 backdrop-blur-sm z-50 transition-opacity duration-300"
          />

          {/* Desktop Modal */}
          <div className="hidden md:flex fixed inset-0 z-50 items-center justify-center p-4 pointer-events-none">
            <div
              onClick={(e) => e.stopPropagation()}
              className="relative bg-cream dark:bg-dark-bg rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden pointer-events-auto animate-in fade-in zoom-in duration-300"
            >
              {/* Close Button */}
              <button
                onClick={() => setViewingCertificate(null)}
                className="absolute top-4 right-4 z-10 p-2 rounded-full bg-cream dark:bg-dark-bg hover:bg-cream-dark dark:hover:bg-dark-bg-secondary transition-colors shadow-lg"
                aria-label="Schließen"
              >
                <svg className="w-6 h-6 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              {/* Modal Content */}
              <div className="flex flex-col h-full">
                {/* Header */}
                <div className="px-8 py-6 border-b border-gray-200 dark:border-gray-800">
                  <h3 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-2">
                    {viewingCertificate.name}
                  </h3>
                  <div className="flex flex-wrap gap-3 text-sm text-text-secondary-light dark:text-text-secondary-dark">
                    <span className="font-medium">{viewingCertificate.issuing_organization}</span>
                    <span>•</span>
                    <span>{formatDate(viewingCertificate.issue_date)}</span>
                    {viewingCertificate.credential_id && (
                      <>
                        <span>•</span>
                        <span>ID: {viewingCertificate.credential_id}</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Certificate Image */}
                <div className="flex-1 overflow-auto p-8">
                  <div className="flex items-center justify-center h-full">
                    {viewingCertificate.certificate_url?.toLowerCase().endsWith('.pdf') ? (
                      // PDF Viewer - embedded without toolbar
                      <iframe
                        src={`${viewingCertificate.certificate_url}#toolbar=0&navpanes=0&scrollbar=0&view=FitH`}
                        className="w-full h-full min-h-[600px] rounded-lg shadow-lg border-0"
                        title={`Zertifikat: ${viewingCertificate.name}`}
                        style={{ border: 'none' }}
                      />
                    ) : (
                      // Image Viewer
                      <img
                        src={viewingCertificate.certificate_url}
                        alt={`Zertifikat: ${viewingCertificate.name}`}
                        className="max-w-full max-h-full object-contain rounded-lg shadow-lg"
                        onError={(e) => {
                          console.error('Failed to load certificate image:', viewingCertificate.certificate_url)
                          // Fallback: Show error message
                          e.currentTarget.style.display = 'none'
                          const errorDiv = document.createElement('div')
                          errorDiv.className = 'text-center text-text-secondary-light dark:text-text-secondary-dark'
                          errorDiv.innerHTML = `
                            <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            <p class="text-lg font-medium mb-2">Bild konnte nicht geladen werden</p>
                            <p class="text-sm">Bitte verwenden Sie "In neuem Tab öffnen"</p>
                          `
                          e.currentTarget.parentElement?.appendChild(errorDiv)
                        }}
                      />
                    )}
                  </div>
                </div>

                {/* Footer */}
                <div className="px-8 py-4 border-t border-gray-200 dark:border-gray-800">
                  <div className="flex justify-end items-center">
                    <a
                      href={viewingCertificate.certificate_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-tekhelet hover:text-tekhelet/80 transition-colors flex items-center gap-1"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                      In neuem Tab öffnen
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Mobile Slide-Up Panel */}
          <div className="md:hidden fixed inset-x-0 bottom-0 z-50 pointer-events-none">
            <div
              ref={mobileModalRef}
              onClick={(e) => e.stopPropagation()}
              onTouchStart={handleTouchStart}
              onTouchMove={handleTouchMove}
              onTouchEnd={handleTouchEnd}
              className="bg-cream dark:bg-dark-bg rounded-t-3xl shadow-2xl max-h-[85vh] overflow-hidden pointer-events-auto animate-in slide-in-from-bottom duration-300"
            >
              {/* Handle Bar - Draggable */}
              <div className="flex justify-center pt-3 pb-2 cursor-grab active:cursor-grabbing">
                <div className="w-12 h-1 bg-gray-300 dark:bg-gray-700 rounded-full" />
              </div>

              {/* Close Button */}
              <button
                onClick={() => setViewingCertificate(null)}
                className="absolute top-4 right-4 z-10 p-2 rounded-full bg-cream dark:bg-dark-bg hover:bg-cream-dark dark:hover:bg-dark-bg-secondary transition-colors shadow-lg"
                aria-label="Schließen"
              >
                <svg className="w-5 h-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              {/* Panel Content */}
              <div className="flex flex-col max-h-[calc(85vh-2rem)]">
                {/* Header */}
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800">
                  <h3 className="text-lg font-semibold text-text-light dark:text-text-dark mb-2 pr-8">
                    {viewingCertificate.name}
                  </h3>
                  <div className="text-sm text-text-secondary-light dark:text-text-secondary-dark space-y-1">
                    <div>{viewingCertificate.issuing_organization}</div>
                    <div>{formatDate(viewingCertificate.issue_date)}</div>
                    {viewingCertificate.credential_id && (
                      <div className="text-xs">ID: {viewingCertificate.credential_id}</div>
                    )}
                  </div>
                </div>

                {/* Certificate Image */}
                <div className="flex-1 overflow-auto p-4" data-lenis-prevent>
                  {viewingCertificate.certificate_url?.toLowerCase().endsWith('.pdf') ? (
                    // PDF Viewer - embedded without toolbar
                    <iframe
                      src={`${viewingCertificate.certificate_url}#toolbar=0&navpanes=0&scrollbar=0&view=FitH`}
                      className="w-full h-full min-h-[400px] rounded-lg shadow-lg border-0"
                      title={`Zertifikat: ${viewingCertificate.name}`}
                      style={{ border: 'none' }}
                    />
                  ) : (
                    // Image Viewer
                    <img
                      src={viewingCertificate.certificate_url}
                      alt={`Zertifikat: ${viewingCertificate.name}`}
                      className="w-full rounded-lg shadow-lg"
                      onError={(e) => {
                        console.error('Failed to load certificate image:', viewingCertificate.certificate_url)
                        e.currentTarget.style.display = 'none'
                        const errorDiv = document.createElement('div')
                        errorDiv.className = 'text-center text-text-secondary-light dark:text-text-secondary-dark p-8'
                        errorDiv.innerHTML = `
                          <svg class="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                          <p class="font-medium mb-1">Bild konnte nicht geladen werden</p>
                          <p class="text-sm">Bitte "In neuem Tab öffnen" verwenden</p>
                        `
                        e.currentTarget.parentElement?.appendChild(errorDiv)
                      }}
                    />
                  )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-800">
                  <a
                    href={viewingCertificate.certificate_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full text-center py-3 bg-tekhelet text-white rounded-lg hover:bg-tekhelet/90 transition-colors font-medium"
                  >
                    In neuem Tab öffnen
                  </a>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </section>
  )
}
