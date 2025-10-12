export default function StructuredData() {
  const personSchema = {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name: 'Luca Manna',
    jobTitle: 'Data Science Student & Full-Stack Developer',
    description: 'Data Science Student (BSc) an der FHNW. Spezialisiert auf Machine Learning, Python, React und innovative Weblösungen.',
    url: 'https://lucamanna.ch',
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
    url: 'https://lucamanna.ch',
    description: 'Portfolio von Luca Manna - Data Science Student & Full-Stack Developer aus Basel',
    author: {
      '@type': 'Person',
      name: 'Luca Manna'
    },
    inLanguage: 'de-CH'
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
