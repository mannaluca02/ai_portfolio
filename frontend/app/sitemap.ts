import {MetadataRoute} from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const base = 'https://lucamanna.ch'
  return ['de', 'en'].map(locale => ({
    url: base + '/' + locale,
    changeFrequency: 'weekly',
    priority: 1,
    alternates: {languages: {de: base + '/de', en: base + '/en', 'x-default': base + '/'}},
  }))
}
