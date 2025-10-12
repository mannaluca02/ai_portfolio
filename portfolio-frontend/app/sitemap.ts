import { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://lucamanna.ch'

  // Statische Seiten
  const routes = [''].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 1,
  }))

  // Sections auf der Homepage (für Deep Links)
  const sections = [
    '#home',
    '#about',
    '#experience',
    '#projects',
    '#education',
    '#skills',
    '#certificates',
    '#contact'
  ].map((section) => ({
    url: `${baseUrl}${section}`,
    lastModified: new Date(),
    changeFrequency: 'monthly' as const,
    priority: 0.8,
  }))

  return [...routes, ...sections]
}
