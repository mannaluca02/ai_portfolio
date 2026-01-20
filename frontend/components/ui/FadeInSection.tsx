'use client'

import { ReactNode } from 'react'
import useScrollAnimation from '@/lib/hooks/useScrollAnimation'

interface FadeInSectionProps {
  children: ReactNode
  className?: string
  delay?: number
}

export default function FadeInSection({ children, className = '', delay = 0 }: FadeInSectionProps) {
  const { elementRef, isVisible } = useScrollAnimation({ threshold: 0.1 })

  return (
    <div
      ref={elementRef}
      className={`transition-all duration-1000 ${
        isVisible
          ? 'opacity-100 translate-y-0'
          : 'opacity-0 translate-y-10'
      } ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  )
}
