'use client'

import { useEffect, useState } from 'react'
import FadeInSection from '@/components/ui/FadeInSection'

interface WorkExperience {
  id: number
  company: string
  position: string
  location?: string
  employment_type: string
  start_date: string
  end_date?: string
  description: string
  responsibilities: string[]
  technologies: string[]
  company_logo_url?: string
}

export default function Experience() {
  const [experiences, setExperiences] = useState<WorkExperience[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<number | null>(null)

  useEffect(() => {
    const fetchExperiences = async () => {
      try {
        const response = await fetch('/api/work-experiences')
        if (response.ok) {
          const data = await response.json()
          setExperiences(data)
        }
      } catch (error) {
        console.error('Error fetching work experiences:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchExperiences()
  }, [])

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
      <section id="experience" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
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

  return (
    <section id="experience" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
      <div className="max-w-5xl mx-auto space-y-16">
        {/* Section Label */}
        <FadeInSection>
          <span className="inline-block text-xs uppercase tracking-[0.2em] text-text-secondary-light dark:text-text-secondary-dark font-medium">
            02 — Erfahrung
          </span>
        </FadeInSection>

        {/* Section Title */}
        <FadeInSection delay={100}>
          <h2 className="text-5xl md:text-6xl font-semibold tracking-tight text-text-light dark:text-text-dark">
            Berufserfahrung
          </h2>
        </FadeInSection>

        {/* Experience List */}
        <div className="space-y-4">
          {experiences.map((exp, index) => {
            const isExpanded = expandedId === exp.id

            return (
              <FadeInSection key={exp.id} delay={200 + index * 50}>
                <div
                  onClick={() => setExpandedId(isExpanded ? null : exp.id)}
                  className="group cursor-pointer border-b border-gray-200 dark:border-gray-800 pb-6 hover:border-tekhelet dark:hover:border-tekhelet transition-colors duration-300"
                >
                  {/* Compact View */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-2xl font-semibold text-text-light dark:text-text-dark group-hover:text-tekhelet transition-colors mb-2">
                        {exp.position}
                      </h3>
                      <div className="flex flex-wrap items-center gap-3 text-text-secondary-light dark:text-text-secondary-dark">
                        <span className="font-medium">{exp.company}</span>
                        <span className="text-sm">
                          {formatDate(exp.start_date)} - {exp.end_date ? formatDate(exp.end_date) : 'Heute'}
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
                        {exp.location && (
                          <span className="flex items-center gap-1.5">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            {exp.location}
                          </span>
                        )}
                        <span className="flex items-center gap-1.5">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                          {exp.employment_type}
                        </span>
                        <span className="flex items-center gap-1.5">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {calculateDuration(exp.start_date, exp.end_date)}
                        </span>
                      </div>

                      {/* Description */}
                      <p className="text-lg text-text-secondary-light dark:text-text-secondary-dark leading-relaxed">
                        {exp.description}
                      </p>

                      {/* Responsibilities */}
                      {exp.responsibilities && exp.responsibilities.length > 0 && (
                        <div>
                          <h4 className="text-sm font-semibold text-text-light dark:text-text-dark mb-3 uppercase tracking-wider">
                            Aufgaben & Verantwortlichkeiten
                          </h4>
                          <ul className="space-y-2">
                            {exp.responsibilities.map((resp, idx) => (
                              <li key={idx} className="flex items-start gap-2 text-text-secondary-light dark:text-text-secondary-dark">
                                <svg className="w-5 h-5 text-tekhelet flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span>{resp}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Technologies */}
                      {exp.technologies && exp.technologies.length > 0 && (
                        <div>
                          <h4 className="text-sm font-semibold text-text-light dark:text-text-dark mb-3 uppercase tracking-wider">
                            Technologien
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {exp.technologies.map((tech, idx) => (
                              <span
                                key={idx}
                                className="px-3 py-1 text-sm font-medium bg-tekhelet/10 text-tekhelet rounded-lg"
                              >
                                {tech}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </FadeInSection>
            )
          })}
        </div>

        {/* Empty State */}
        {experiences.length === 0 && !loading && (
          <FadeInSection delay={200}>
            <div className="text-center py-16">
              <p className="text-xl text-text-secondary-light dark:text-text-secondary-dark">
                Keine Berufserfahrung gefunden.
              </p>
            </div>
          </FadeInSection>
        )}
      </div>
    </section>
  )
}
