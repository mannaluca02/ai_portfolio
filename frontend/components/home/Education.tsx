'use client'

import { useEffect, useState } from 'react'
import FadeInSection from '@/components/ui/FadeInSection'

interface EducationRecord {
  id: number
  institution: string
  degree: string
  degree_type: string
  field_of_study?: string
  location?: string
  start_date: string
  end_date?: string
  grade?: string
  description?: string
  achievements?: string[]
  institution_logo_url?: string
  slug: string
  section: string
  anchor: string
}

export default function Education() {
  const [education, setEducation] = useState<EducationRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<number | null>(null)

  useEffect(() => {
    const fetchEducation = async () => {
      try {
        const response = await fetch('/api/education')
        if (response.ok) {
          const data = await response.json()
          if (Array.isArray(data)) {
            setEducation(data)
          }
        }
      } catch (error) {
        console.error('Error fetching education:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchEducation()
  }, [])

  // Handle accordion opening from chatbot links
  useEffect(() => {
    const handleOpenAccordion = (event: CustomEvent) => {
      const link = event.detail.link

      // Check if this link is for the education section
      if (link.includes('education')) {
        // Find the education record by matching the slug
        const educationRecord = education.find(edu => {
          const fullSlug = `${edu.section}-${edu.slug}`
          return link === fullSlug || link === edu.slug || link.endsWith(edu.slug)
        })

        if (educationRecord) {
          setExpandedId(educationRecord.id)

          // Scroll to the section after a short delay
          setTimeout(() => {
            const element = document.getElementById('education')
            if (element) {
              element.scrollIntoView({ behavior: 'smooth', block: 'start' })
            }
          }, 100)
        }
      }
    }

    window.addEventListener('openAccordion', handleOpenAccordion as EventListener)
    return () => window.removeEventListener('openAccordion', handleOpenAccordion as EventListener)
  }, [education])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('de-DE', { month: 'short', year: 'numeric' })
  }

  const calculateDuration = (start: string, end?: string) => {
    const startDate = new Date(start)
    const endDate = end ? new Date(end) : new Date()
    const months = (endDate.getFullYear() - startDate.getFullYear()) * 12 +
                   (endDate.getMonth() - startDate.getMonth())
    const years = Math.floor(months / 12)
    const remainingMonths = months % 12

    if (years > 0 && remainingMonths > 0) {
      return `${years} Jahr${years > 1 ? 'e' : ''}, ${remainingMonths} Monat${remainingMonths > 1 ? 'e' : ''}`
    } else if (years > 0) {
      return `${years} Jahr${years > 1 ? 'e' : ''}`
    } else {
      return `${remainingMonths} Monat${remainingMonths > 1 ? 'e' : ''}`
    }
  }

  if (loading) {
    return (
      <section id="education" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
        <div className="max-w-5xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
            <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="space-y-4">
              {[1, 2].map(i => (
                <div key={i} className="h-48 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </section>
    )
  }

  if (education.length === 0) {
    return null
  }

  return (
    <section id="education" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
      <div className="max-w-5xl mx-auto space-y-16">
        {/* Section Label */}
        <FadeInSection>
          <span className="inline-block text-xs uppercase tracking-[0.2em] text-text-secondary-light dark:text-text-secondary-dark font-medium">
            04 — Ausbildung
          </span>
        </FadeInSection>

        {/* Section Title */}
        <FadeInSection delay={100}>
          <h2 className="text-5xl md:text-6xl font-semibold tracking-tight text-text-light dark:text-text-dark">
            Akademischer Werdegang
          </h2>
        </FadeInSection>

        {/* Education List */}
        <div className="space-y-4">
          {education.map((edu, index) => {
            const isExpanded = expandedId === edu.id

            return (
              <FadeInSection key={edu.id} delay={200 + index * 50}>
                <div
                  onClick={() => setExpandedId(isExpanded ? null : edu.id)}
                  className="group cursor-pointer border-b border-gray-200 dark:border-gray-800 pb-6 hover:border-tekhelet dark:hover:border-tekhelet transition-colors duration-300"
                >
                  {/* Compact View */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-2xl font-semibold text-text-light dark:text-text-dark group-hover:text-tekhelet transition-colors mb-2">
                        {edu.degree}
                      </h3>
                      <div className="flex flex-wrap items-center gap-3 text-text-secondary-light dark:text-text-secondary-dark">
                        <span className="font-medium">{edu.institution}</span>
                        <span className="text-sm">
                          {formatDate(edu.start_date)} - {edu.end_date ? formatDate(edu.end_date) : 'Laufend'}
                        </span>
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
                      {/* Meta Information */}
                      <div className="flex flex-wrap gap-4 text-sm text-text-secondary-light dark:text-text-secondary-dark">
                        {edu.location && (
                          <span className="flex items-center gap-1.5">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            {edu.location}
                          </span>
                        )}
                        <span className="flex items-center gap-1.5">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                          </svg>
                          {edu.degree_type}
                        </span>
                        {edu.grade && (
                          <span className="flex items-center gap-1.5">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                            </svg>
                            Note {edu.grade}
                          </span>
                        )}
                        <span className="flex items-center gap-1.5">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {calculateDuration(edu.start_date, edu.end_date)}
                        </span>
                      </div>

                      {/* Field of Study */}
                      {edu.field_of_study && (
                        <div>
                          <h4 className="text-sm font-semibold text-text-light dark:text-text-dark mb-3 uppercase tracking-wider">
                            Studienrichtung
                          </h4>
                          <p className="text-lg text-text-secondary-light dark:text-text-secondary-dark leading-relaxed">
                            {edu.field_of_study}
                          </p>
                        </div>
                      )}

                      {/* Description */}
                      {edu.description && (
                        <p className="text-lg text-text-secondary-light dark:text-text-secondary-dark leading-relaxed">
                          {edu.description}
                        </p>
                      )}

                      {/* Achievements */}
                      {edu.achievements && edu.achievements.length > 0 && (
                        <div>
                          <h4 className="text-sm font-semibold text-text-light dark:text-text-dark mb-3 uppercase tracking-wider">
                            Besondere Leistungen
                          </h4>
                          <ul className="space-y-2">
                            {edu.achievements.map((achievement, idx) => (
                              <li key={idx} className="flex items-start gap-2 text-text-secondary-light dark:text-text-secondary-dark">
                                <svg className="w-5 h-5 text-tekhelet flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span>{achievement}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
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
