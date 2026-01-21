import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Impressum',
  description: 'Impressum und Kontaktinformationen von Luca Manna',
  robots: {
    index: true,
    follow: true,
  },
}

export default function ImpressumPage() {
  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark py-20">
      <div className="max-w-4xl mx-auto px-6 md:px-12">
        {/* Header */}
        <div className="mb-12">
          <Link
            href="/"
            className="inline-flex items-center text-tekhelet hover:text-tekhelet/80 transition-colors mb-6"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Zurück zur Startseite
          </Link>
          <h1 className="text-4xl md:text-5xl font-bold text-text-light dark:text-text-dark mb-4">
            Impressum
          </h1>
          <p className="text-text-secondary-light dark:text-text-secondary-dark">
            Angaben gemäss Schweizer Recht
          </p>
        </div>

        {/* Content */}
        <div className="prose prose-lg dark:prose-invert max-w-none">
          <div className="bg-white dark:bg-[#0A0A0A] rounded-lg shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-6">
              Kontaktadresse
            </h2>

            <div className="space-y-4 text-text-secondary-light dark:text-text-secondary-dark">
              <div>
                <p className="font-medium text-text-light dark:text-text-dark">Name:</p>
                <p>Luca Manna</p>
              </div>

              <div>
                <p className="font-medium text-text-light dark:text-text-dark">Ort:</p>
                <p>Basel, Schweiz</p>
              </div>

              <div>
                <p className="font-medium text-text-light dark:text-text-dark">E-Mail:</p>
                <a
                  href="mailto:mannaluca02@gmail.com"
                  className="text-tekhelet hover:text-tekhelet/80 dark:text-tekhelet dark:hover:text-tekhelet/80 transition-colors"
                >
                  mannaluca02@gmail.com
                </a>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-[#0A0A0A] rounded-lg shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-6">
              Zweck der Website
            </h2>
            <p className="text-text-secondary-light dark:text-text-secondary-dark">
              Diese Website dient als persönliches Portfolio zur Präsentation meiner Arbeit,
              Projekte und Fähigkeiten im Bereich Data Science und Softwareentwicklung.
              Die Website wird nicht-kommerziell und ausschliesslich zu Informationszwecken betrieben.
            </p>
          </div>

          <div className="bg-white dark:bg-[#0A0A0A] rounded-lg shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-6">
              Haftungsausschluss
            </h2>

            <h3 className="text-xl font-medium text-text-light dark:text-text-dark mt-6 mb-3">
              Haftung für Inhalte
            </h3>
            <p className="text-text-secondary-light dark:text-text-secondary-dark mb-4">
              Die Inhalte dieser Website wurden mit grösstmöglicher Sorgfalt erstellt.
              Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte kann jedoch
              keine Gewähr übernommen werden. Als Diensteanbieter bin ich gemäss Schweizer
              Recht für eigene Inhalte auf diesen Seiten verantwortlich.
            </p>

            <h3 className="text-xl font-medium text-text-light dark:text-text-dark mt-6 mb-3">
              Haftung für Links
            </h3>
            <p className="text-text-secondary-light dark:text-text-secondary-dark mb-4">
              Diese Website enthält Links zu externen Websites Dritter, auf deren Inhalte
              ich keinen Einfluss habe. Deshalb kann für diese fremden Inhalte auch keine
              Gewähr übernommen werden. Für die Inhalte der verlinkten Seiten ist stets
              der jeweilige Anbieter oder Betreiber der Seiten verantwortlich.
            </p>

            <h3 className="text-xl font-medium text-text-light dark:text-text-dark mt-6 mb-3">
              Urheberrecht
            </h3>
            <p className="text-text-secondary-light dark:text-text-secondary-dark">
              Die durch den Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten
              unterliegen dem schweizerischen Urheberrecht. Die Vervielfältigung, Bearbeitung,
              Verbreitung und jede Art der Verwertung ausserhalb der Grenzen des Urheberrechts
              bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.
            </p>
          </div>

          <div className="bg-white dark:bg-[#0A0A0A] rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-6">
              KI-Chatbot
            </h2>
            <p className="text-text-secondary-light dark:text-text-secondary-dark mb-4">
              Diese Website verwendet einen KI-gestützten Chatbot zur Beantwortung von Fragen
              über mein Portfolio. Der Chatbot nutzt die OpenAI API und basiert auf den Inhalten
              dieser Website.
            </p>
            <p className="text-text-secondary-light dark:text-text-secondary-dark">
              Weitere Informationen zur Datenverarbeitung finden Sie in der{' '}
              <Link
                href="/datenschutz"
                className="text-tekhelet hover:text-tekhelet/80 dark:text-tekhelet dark:hover:text-tekhelet/80 transition-colors font-medium"
              >
                Datenschutzerklärung
              </Link>.
            </p>
          </div>
        </div>

        {/* Footer Navigation */}
        <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-wrap gap-4 justify-center text-sm">
            <Link
              href="/"
              className="text-tekhelet hover:text-tekhelet/80 dark:text-tekhelet dark:hover:text-tekhelet/80 transition-colors"
            >
              Startseite
            </Link>
            <span className="text-gray-400">•</span>
            <Link
              href="/datenschutz"
              className="text-tekhelet hover:text-tekhelet/80 dark:text-tekhelet dark:hover:text-tekhelet/80 transition-colors"
            >
              Datenschutzerklärung
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
