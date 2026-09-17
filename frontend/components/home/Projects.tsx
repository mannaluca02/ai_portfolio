'use client'

import {useTranslations, useLocale} from 'next-intl'

import { useEffect, useState } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import FadeInSection from '@/components/ui/FadeInSection'

interface Project {
  id: number
  name: string
  description: string
  project_type: string
  featured: boolean
  start_date?: string
  end_date?: string
  project_url?: string
  github_url?: string
  demo_url?: string
  technologies?: string[] | null
  your_role?: string
  team_size?: number
  client_company?: string
  image_urls?: string[]
  slug: string
  section: string
  anchor: string
}

type TabType = 'featured' | 'all'


export default function Projects() {
  const t = useTranslations('Projects')
  const locale = useLocale()

  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>('featured')
  const [pendingLink, setPendingLink] = useState<string | null>(null)
  const reduceMotion = useReducedMotion()

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch(`/api/projects?lang=${locale}`)
        if (response.ok) {
          const data = await response.json()
          setProjects(data)
        }
      } catch (error) {
        console.error('Error fetching projects:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProjects()
  }, [locale])

  // Handle accordion opening from chatbot links
  useEffect(() => {
    const handleOpenAccordion = (event: CustomEvent) => {
      const link = event.detail?.link
      if (typeof link !== 'string') return

      // Check if this link is for the projects section
      if (link.includes('project')) {
        // Find the project by matching the slug
        const project = projects.find(proj => {
          const fullSlug = `${proj.section}-${proj.slug}`
          return link === fullSlug || link === proj.slug || link.endsWith(proj.slug)
        })

        if (project) {
          // If the project is featured, switch to featured tab
          // Otherwise switch to all tab
          if (project.featured) {
            setActiveTab('featured')
          } else {
            setActiveTab('all')
          }

          setExpandedId(project.id)

          setPendingLink(`${project.section}-${project.slug}`)
        }
      }
    }

    window.addEventListener('openAccordion', handleOpenAccordion as EventListener)
    return () => window.removeEventListener('openAccordion', handleOpenAccordion as EventListener)
  }, [projects])

  useEffect(() => {
    if (!pendingLink) return
    const frame = requestAnimationFrame(() => {
      document.getElementById(pendingLink)?.scrollIntoView({
        behavior: reduceMotion ? 'auto' : 'smooth', block: 'start',
      })
      setPendingLink(null)
    })
    return () => cancelAnimationFrame(frame)
  }, [pendingLink, activeTab, expandedId, reduceMotion])

  const formatDate = (dateString?: string) => {
    if (!dateString) return null
    const date = new Date(dateString)
    return date.toLocaleDateString(locale === 'de' ? 'de-CH' : 'en-GB', { month: 'short', year: 'numeric' })
  }

  const getProjectTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'Personal': 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
      'Professional': 'bg-green-500/10 text-green-600 dark:text-green-400',
      'Academic': 'bg-green-500/10 text-green-600 dark:text-green-400',
      'Open Source': 'bg-tekhelet/10 text-tekhelet',
      'Startup': 'bg-red-500/10 text-red-600 dark:text-red-400',
      'Client Work': 'bg-orange-500/10 text-orange-600 dark:text-orange-400',
      'Hackathon': 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
    }
    return colors[type] || 'bg-gray-500/10 text-gray-600 dark:text-gray-400'
  }

  // Get projects for each tab
  const featuredProjects = projects.filter(p => p.featured)
  const allProjects = projects

  const featuredCount = featuredProjects.length
  const allCount = allProjects.length

  const visibleProjects = activeTab === 'featured' ? featuredProjects : allProjects

  // Render project function to avoid duplication
  const renderProject = (project: Project) => {
    const isExpanded = expandedId === project.id

    return (
      <div
        key={project.id}
        id={`${project.section}-${project.slug}`}
        data-project-id={project.id}
        data-expanded={isExpanded}
        style={{ scrollMarginTop: '6rem' }}
        onClick={() => setExpandedId(isExpanded ? null : project.id)}
        className="group cursor-pointer border-b border-gray-200 dark:border-gray-800 pb-6 hover:border-tekhelet dark:hover:border-tekhelet transition-colors duration-300"
      >
        {/* Compact View */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-2xl font-semibold text-text-light dark:text-text-dark group-hover:text-tekhelet transition-colors">
                {project.name}
              </h3>
              <span className={`px-2 py-1 text-xs font-medium rounded ${getProjectTypeColor(project.project_type)}`}>
                {project.project_type}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-text-secondary-light dark:text-text-secondary-dark">
              <p className="text-sm line-clamp-1">{project.description}</p>
              {project.start_date && (
                <span className="text-xs">
                  {formatDate(project.start_date)} {project.end_date ? `- ${formatDate(project.end_date)}` : t('untilPresent')}
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
            {/* Full Description */}
            <p className="text-lg text-text-secondary-light dark:text-text-secondary-dark leading-relaxed">
              {project.description}
            </p>

            {/* Project Meta */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              {project.your_role && (
                <div>
                  <span className="font-semibold text-text-light dark:text-text-dark">{t('role')} </span>
                  <span className="text-text-secondary-light dark:text-text-secondary-dark">{project.your_role}</span>
                </div>
              )}
              {project.team_size && (
                <div>
                  <span className="font-semibold text-text-light dark:text-text-dark">{t('teamSize')} </span>
                  <span className="text-text-secondary-light dark:text-text-secondary-dark">{t('people', {count: project.team_size})}</span>
                </div>
              )}
              {project.client_company && (
                <div>
                  <span className="font-semibold text-text-light dark:text-text-dark">{t('client')} </span>
                  <span className="text-text-secondary-light dark:text-text-secondary-dark">{project.client_company}</span>
                </div>
              )}
            </div>

            {/* Technologies */}
            {project.technologies && project.technologies.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-text-light dark:text-text-dark mb-3 uppercase tracking-wider">
                  {t('technologies')}
                </h4>
                <div className="flex flex-wrap gap-2">
                  {project.technologies.map((tech, idx) => (
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

            {/* Links */}
            {(project.project_url || project.github_url || project.demo_url) && (
              <div>
                <h4 className="text-sm font-semibold text-text-light dark:text-text-dark mb-3 uppercase tracking-wider">
                  Links
                </h4>
                <div className="flex flex-wrap gap-3">
                  {project.project_url && (
                    <a
                      href={project.project_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-tekhelet border border-tekhelet rounded-lg hover:bg-tekhelet hover:text-white transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                      Website
                    </a>
                  )}
                  {project.github_url && (
                    <a
                      href={project.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-tekhelet border border-tekhelet rounded-lg hover:bg-tekhelet hover:text-white transition-colors"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                      </svg>
                      GitHub
                    </a>
                  )}
                  {project.demo_url && (
                    <a
                      href={project.demo_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-tekhelet border border-tekhelet rounded-lg hover:bg-tekhelet hover:text-white transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Demo
                    </a>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <section id="projects" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
        <div className="max-w-5xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
            <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section id="projects" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
      <div className="max-w-5xl mx-auto space-y-16">
        {/* Section Label */}
        <FadeInSection>
          <span className="inline-block text-xs uppercase tracking-[0.2em] text-text-secondary-light dark:text-text-secondary-dark font-medium">
            {t('section')}
          </span>
        </FadeInSection>

        {/* Section Title */}
        <FadeInSection delay={100}>
          <h2 className="text-5xl md:text-6xl font-semibold tracking-tight text-text-light dark:text-text-dark">
            {t('title')}
          </h2>
        </FadeInSection>

        {/* Tab Navigation */}
        <FadeInSection delay={150}>
          <div className="flex items-center gap-2 border-b border-gray-200 dark:border-gray-800">
            <button
              onClick={() => {
                setActiveTab('featured')
                setExpandedId(null)
              }}
              className={`px-6 py-3 text-sm font-medium uppercase tracking-wider transition-all duration-300 relative ${
                activeTab === 'featured'
                  ? 'text-tekhelet'
                  : 'text-text-secondary-light dark:text-text-secondary-dark hover:text-text-light dark:hover:text-text-dark'
              }`}
            >
              Featured
              {featuredCount > 0 && (
                <span className="ml-2 text-xs opacity-60">({featuredCount})</span>
              )}
              {activeTab === 'featured' && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-tekhelet"></span>
              )}
            </button>
            <button
              onClick={() => {
                setActiveTab('all')
                setExpandedId(null)
              }}
              className={`px-6 py-3 text-sm font-medium uppercase tracking-wider transition-all duration-300 relative ${
                activeTab === 'all'
                  ? 'text-tekhelet'
                  : 'text-text-secondary-light dark:text-text-secondary-dark hover:text-text-light dark:hover:text-text-dark'
              }`}
            >
              {t('all')}
              {allCount > 0 && (
                <span className="ml-2 text-xs opacity-60">({allCount})</span>
              )}
              {activeTab === 'all' && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-tekhelet"></span>
              )}
            </button>
          </div>
        </FadeInSection>

        {/* Only the active panel participates in layout or keyboard navigation. */}
        <motion.div
          key={activeTab}
          className="space-y-4"
          initial={reduceMotion ? false : { opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: reduceMotion ? 0 : 0.15 }}
        >
          {visibleProjects.map(renderProject)}
          {visibleProjects.length === 0 && (
            <div className="text-center py-16">
              <p className="text-xl text-text-secondary-light dark:text-text-secondary-dark">
                {activeTab === 'featured' ? t('emptyFeatured') : t('empty')}
              </p>
            </div>
          )}
        </motion.div>
      </div>
    </section>
  )
}
