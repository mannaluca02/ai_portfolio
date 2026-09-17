import {getLocale} from 'next-intl/server'

export default async function StructuredData() {
  const locale = await getLocale()
  const personSchema = {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name: 'Luca Manna',
    jobTitle: 'Data Scientist & ML Engineer',
    description: locale === 'en' ? 'Data Science student (BSc) at FHNW. Specialising in Machine Learning, Python, React and web development.' : 'Data Science Student (BSc) an der FHNW. Spezialisiert auf Machine Learning, Python, React und innovative Weblösungen.',
    url: `https://lucamanna.ch/${locale}`,
    email: 'mannaluca02@gmail.com',
    telephone: '+41762047441',
    address: {
      '@type': 'PostalAddress',
      addressLocality: 'Basel',
      addressCountry: 'CH'
    },
    alumniOf: {
      '@type': 'EducationalOrganization',
      name: 'Fachhochschule Nordwestschweiz FHNW',
      url: 'https://www.fhnw.ch'
    },
    knowsAbout: [
      'Machine Learning',
      'Data Science',
      'Python',
      'React',
      'Full-Stack Development',
      'Deep Learning',
      'Web Development',
      'Artificial Intelligence'
    ],
    sameAs: [
      'https://www.linkedin.com/in/luca-manna-1543b4241',
      'https://github.com/mannaluca02'
    ]
  }

  const websiteSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'Luca Manna Portfolio',
    url: `https://lucamanna.ch/${locale}`,
    description: locale === 'en' ? 'Portfolio of Luca Manna - Data Scientist & ML Engineer based in Basel' : 'Portfolio von Luca Manna - Data Scientist & ML Engineer aus Basel',
    author: {
      '@type': 'Person',
      name: 'Luca Manna'
    },
    inLanguage: locale === 'en' ? 'en-GB' : 'de-CH'
  }

  const profilePageSchema = {
    '@context': 'https://schema.org',
    '@type': 'ProfilePage',
    mainEntity: {
      '@type': 'Person',
      name: 'Luca Manna'
    }
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(personSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(profilePageSchema) }}
      />
    </>
  )
}
