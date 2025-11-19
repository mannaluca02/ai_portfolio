'use client'

import { useEffect, useState } from 'react'
import FadeInSection from '@/components/ui/FadeInSection'

interface Skill {
  id: number
  name: string
  skill_level: string
  category: string
  years_of_experience?: number
  description?: string
}

interface SkillsByCategory {
  [category: string]: Skill[]
}

export default function Skills() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const response = await fetch('/api/skills')
        if (response.ok) {
          const data = await response.json()
          setSkills(data)
        }
      } catch (error) {
        console.error('Error fetching skills:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchSkills()
  }, [])

  // Group skills by category
  const skillsByCategory: SkillsByCategory = skills.reduce((acc, skill) => {
    if (!acc[skill.category]) {
      acc[skill.category] = []
    }
    acc[skill.category].push(skill)
    return acc
  }, {} as SkillsByCategory)

  const getSkillLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      'Expert': 'bg-green-500',
      'Intermediate': 'bg-yellow-500',
      'Beginner': 'bg-gray-400',
    }
    return colors[level] || 'bg-gray-400'
  }

  const getSkillLevelWidth = (level: string) => {
    const widths: Record<string, string> = {
      'Expert': 'w-full',
      'Intermediate': 'w-3/5',
      'Beginner': 'w-2/5',
    }
    return widths[level] || 'w-2/5'
  }

  if (loading) {
    return (
      <section id="skills" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
        <div className="max-w-5xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
            <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-48 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section id="skills" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
      <div className="max-w-5xl mx-auto space-y-16">
        {/* Section Label */}
        <FadeInSection>
          <span className="inline-block text-xs uppercase tracking-[0.2em] text-text-secondary-light dark:text-text-secondary-dark font-medium">
            05 — Skills
          </span>
        </FadeInSection>

        {/* Section Title */}
        <FadeInSection delay={100}>
          <h2 className="text-5xl md:text-6xl font-semibold tracking-tight text-text-light dark:text-text-dark">
            Fähigkeiten & Expertise
          </h2>
        </FadeInSection>

        {/* Skills Grid by Category */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {Object.entries(skillsByCategory).map(([category, categorySkills], categoryIndex) => (
            <FadeInSection key={category} delay={200 + categoryIndex * 100}>
              <div className="space-y-6">
                {/* Category Header */}
                <div className="border-b border-gray-200 dark:border-gray-800 pb-3">
                  <h3 className="text-xl font-semibold text-text-light dark:text-text-dark">
                    {category}
                  </h3>
                </div>

                {/* Skills in Category */}
                <div className="space-y-4">
                  {categorySkills.map((skill) => (
                    <div key={skill.id} className="group">
                      {/* Skill Name & Level */}
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-text-light dark:text-text-dark group-hover:text-tekhelet transition-colors">
                          {skill.name}
                        </span>
                        <div className="flex items-center gap-2">
                          {skill.years_of_experience && (
                            <span className="text-xs text-text-secondary-light dark:text-text-secondary-dark">
                              {skill.years_of_experience} {skill.years_of_experience === 1 ? 'Jahr' : 'Jahre'}
                            </span>
                          )}
                          <span className="text-xs font-medium text-text-secondary-light dark:text-text-secondary-dark">
                            {skill.skill_level}
                          </span>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${getSkillLevelColor(skill.skill_level)} ${getSkillLevelWidth(skill.skill_level)} transition-all duration-500 ease-out group-hover:opacity-80`}
                        ></div>
                      </div>

                      {/* Optional Description */}
                      {skill.description && (
                        <p className="text-sm text-text-secondary-light dark:text-text-secondary-dark mt-1">
                          {skill.description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </FadeInSection>
          ))}
        </div>

        {/* Empty State */}
        {skills.length === 0 && !loading && (
          <FadeInSection delay={200}>
            <div className="text-center py-16">
              <p className="text-xl text-text-secondary-light dark:text-text-secondary-dark">
                Keine Skills gefunden.
              </p>
            </div>
          </FadeInSection>
        )}

        {/* Legend */}
        {skills.length > 0 && (
          <FadeInSection delay={400}>
            <div className="pt-8 border-t border-gray-200 dark:border-gray-800">
              <div className="flex flex-wrap items-center gap-6 justify-center text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-500 rounded"></div>
                  <span className="text-text-secondary-light dark:text-text-secondary-dark">Expert</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-yellow-500 rounded"></div>
                  <span className="text-text-secondary-light dark:text-text-secondary-dark">Intermediate</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-gray-400 rounded"></div>
                  <span className="text-text-secondary-light dark:text-text-secondary-dark">Beginner</span>
                </div>
              </div>
            </div>
          </FadeInSection>
        )}
      </div>
    </section>
  )
}
