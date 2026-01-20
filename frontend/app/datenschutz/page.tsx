import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Datenschutzerklärung',
  description: 'Datenschutzerklärung und Informationen zur Datenverarbeitung auf lucamanna.ch',
  robots: {
    index: true,
    follow: true,
  },
}

export default function DatenschutzPage() {
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
            Datenschutzerklärung
          </h1>
          <p className="text-text-secondary-light dark:text-text-secondary-dark">
            Letzte Aktualisierung: {new Date().toLocaleDateString('de-CH')}
          </p>
        </div>

        {/* Content */}
        <div className="prose prose-lg dark:prose-invert max-w-none space-y-8">

          {/* Grundsätze */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-4">
              1. Grundsätze
            </h2>
            <p className="text-text-secondary-light dark:text-text-secondary-dark">
              Der Schutz Ihrer persönlichen Daten ist mir ein wichtiges Anliegen. Diese
              Datenschutzerklärung informiert Sie darüber, welche Daten bei der Nutzung
              dieser Website erhoben werden und wie diese verwendet werden. Die Datenverarbeitung
              erfolgt im Einklang mit dem Schweizer Datenschutzgesetz (DSG) und der
              EU-Datenschutz-Grundverordnung (DSGVO).
            </p>
          </div>

          {/* Verantwortlicher */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-4">
              2. Verantwortlicher
            </h2>
            <div className="text-text-secondary-light dark:text-text-secondary-dark space-y-2">
              <p className="font-medium text-text-light dark:text-text-dark">Luca Manna</p>
              <p>Basel, Schweiz</p>
              <p>
                E-Mail:{' '}
                <a
                  href="mailto:mannaluca02@gmail.com"
                  className="text-tekhelet hover:text-tekhelet/80 dark:text-tekhelet dark:hover:text-tekhelet/80 transition-colors"
                >
                  mannaluca02@gmail.com
                </a>
              </p>
            </div>
          </div>

          {/* Hosting */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-4">
              3. Hosting und Server
            </h2>
            <div className="space-y-4 text-text-secondary-light dark:text-text-secondary-dark">
              <div>
                <p className="font-medium text-text-light dark:text-text-dark mb-2">
                  Frontend-Hosting (Vercel)
                </p>
                <p>
                  Diese Website wird auf Servern von Vercel Inc. (USA) gehostet. Vercel erhebt
                  automatisch technische Daten wie IP-Adresse, Browser-Typ und Zugriffszeiten
                  zu Sicherheits- und Optimierungszwecken.
                </p>
                <p className="mt-2">
                  Weitere Informationen:{' '}
                  <a
                    href="https://vercel.com/legal/privacy-policy"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-tekhelet hover:text-tekhelet/80 dark:text-tekhelet dark:hover:text-tekhelet/80 transition-colors"
                  >
                    Vercel Privacy Policy
                  </a>
                </p>
              </div>

              <div className="pt-4">
                <p className="font-medium text-text-light dark:text-text-dark mb-2">
                  Datenbank (Supabase)
                </p>
                <p>
                  Portfolio-Daten werden auf Servern von Supabase Inc. in der EU (Region: Frankfurt/Irland)
                  gespeichert. Es werden keine personenbezogenen Daten von Website-Besuchern
                  in der Datenbank gespeichert.
                </p>
                <p className="mt-2">
                  Weitere Informationen:{' '}
                  <a
                    href="https://supabase.com/privacy"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-tekhelet hover:text-tekhelet/80 dark:text-tekhelet dark:hover:text-tekhelet/80 transition-colors"
                  >
                    Supabase Privacy Policy
                  </a>
                </p>
              </div>
            </div>
          </div>

          {/* KI-Chatbot */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-4">
              4. KI-Chatbot (OpenAI Integration)
            </h2>
            <div className="space-y-4 text-text-secondary-light dark:text-text-secondary-dark">
              <div>
                <p className="font-medium text-text-light dark:text-text-dark mb-2">
                  Funktionsweise
                </p>
                <p>
                  Der Chatbot auf dieser Website nutzt die OpenAI API (GPT-3.5 Turbo) zur
                  Beantwortung von Fragen über mein Portfolio. Ihre Anfragen werden an
                  OpenAI übermittelt und verarbeitet.
                </p>
              </div>

              <div>
                <p className="font-medium text-text-light dark:text-text-dark mb-2">
                  Verarbeitete Daten
                </p>
                <ul className="list-disc pl-5 space-y-1">
                  <li>Ihre Chat-Nachrichten (Fragen an den Chatbot)</li>
                  <li>IP-Adresse (zu Rate-Limiting-Zwecken, siehe Abschnitt 5)</li>
                  <li>Zeitpunkt der Anfrage</li>
                </ul>
              </div>

              <div>
                <p className="font-medium text-text-light dark:text-text-dark mb-2">
                  Zweck der Verarbeitung
                </p>
                <p>
                  Die Verarbeitung erfolgt zur Bereitstellung der Chatbot-Funktionalität und
                  zur Beantwortung Ihrer Fragen. OpenAI speichert die Daten für maximal 30 Tage
                  zur Missbrauchsprävention und löscht sie anschliessend.
                </p>
              </div>

              <div>
                <p className="font-medium text-text-light dark:text-text-dark mb-2">
                  Rechtsgrundlage
                </p>
                <p>
                  Die Verarbeitung erfolgt auf Basis Ihrer Einwilligung durch aktive Nutzung
                  des Chatbots (Art. 6 Abs. 1 lit. a DSGVO).
                </p>
              </div>

              <div>
                <p className="font-medium text-text-light dark:text-text-dark mb-2">
                  Datenweitergabe
                </p>
                <p>
                  Ihre Anfragen werden an OpenAI LLC (USA) übermittelt. OpenAI ist nach dem
                  EU-US Data Privacy Framework zertifiziert.
                </p>
                <p className="mt-2">
                  Weitere Informationen:{' '}
                  <a
                    href="https://openai.com/policies/privacy-policy"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-tekhelet hover:text-tekhelet/80 dark:text-tekhelet dark:hover:text-tekhelet/80 transition-colors"
                  >
                    OpenAI Privacy Policy
                  </a>
                </p>
              </div>
            </div>
          </div>

          {/* Rate Limiting */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-4">
              5. Rate Limiting (IP-Speicherung)
            </h2>
            <div className="space-y-4 text-text-secondary-light dark:text-text-secondary-dark">
              <div>
                <p className="font-medium text-text-light dark:text-text-dark mb-2">
                  Zweck
                </p>
                <p>
                  Zum Schutz vor Missbrauch und zur Gewährleistung der Verfügbarkeit des
                  Chatbots wird Ihre IP-Adresse temporär gespeichert, um die Anzahl der
                  Anfragen zu limitieren.
                </p>
              </div>

              <div>
                <p className="font-medium text-text-light dark:text-text-dark mb-2">
                  Limits
                </p>
                <ul className="list-disc pl-5 space-y-1">
                  <li>Natural Mode (KI-Antworten): 20 Anfragen pro Tag, 100 pro Monat</li>
                  <li>Listen Mode (Suchfunktion): 40 Anfragen pro Tag, 200 pro Monat</li>
                </ul>
              </div>

              <div>
                <p className="font-medium text-text-light dark:text-text-dark mb-2">
                  Speicherdauer
                </p>
                <p>
                  Die IP-Adressen werden ausschliesslich im Arbeitsspeicher des Servers gehalten
                  und automatisch nach Ablauf der Zählperiode (täglich/monatlich) gelöscht.
                  Es erfolgt keine permanente Speicherung.
                </p>
              </div>

              <div>
                <p className="font-medium text-text-light dark:text-text-dark mb-2">
                  Rechtsgrundlage
                </p>
                <p>
                  Die Verarbeitung erfolgt zur Wahrung berechtigter Interessen (Art. 6 Abs. 1 lit. f DSGVO)
                  zum Schutz vor Missbrauch und zur Kostenkontrolle der API-Nutzung.
                </p>
              </div>
            </div>
          </div>

          {/* Kontaktformular */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-4">
              6. Kontaktformular
            </h2>
            <div className="space-y-4 text-text-secondary-light dark:text-text-secondary-dark">
              <p>
                Wenn Sie das Kontaktformular nutzen, werden folgende Daten erhoben:
              </p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Name</li>
                <li>E-Mail-Adresse</li>
                <li>Nachricht</li>
              </ul>
              <p className="mt-4">
                Diese Daten werden ausschliesslich zur Bearbeitung Ihrer Anfrage verwendet und
                per E-Mail über den Dienst Resend (resend.com) an mich weitergeleitet. Die Daten
                werden nicht dauerhaft gespeichert oder an Dritte weitergegeben.
              </p>
              <p className="mt-4">
                <span className="font-medium text-text-light dark:text-text-dark">Rechtsgrundlage:</span>{' '}
                Art. 6 Abs. 1 lit. b DSGVO (Vertragsanbahnung) und Art. 6 Abs. 1 lit. f DSGVO
                (berechtigtes Interesse an der Beantwortung Ihrer Anfrage).
              </p>
            </div>
          </div>

          {/* Analytics */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-4">
              7. Web Analytics
            </h2>
            <div className="space-y-4 text-text-secondary-light dark:text-text-secondary-dark">
              <div>
                <p className="font-medium text-text-light dark:text-text-dark mb-2">
                  Vercel Analytics (optional)
                </p>
                <p>
                  Diese Website kann Vercel Analytics zur Analyse des Nutzerverhaltens verwenden.
                  Vercel Analytics erhebt anonymisierte Daten ohne Verwendung von Cookies:
                </p>
                <ul className="list-disc pl-5 space-y-1 mt-2">
                  <li>Seitenaufrufe</li>
                  <li>Anonymisierte IP-Adressen</li>
                  <li>Referrer-Informationen</li>
                  <li>Browser und Geräteinformationen</li>
                </ul>
                <p className="mt-4">
                  Es werden keine personenbezogenen Daten gespeichert und keine Cookies gesetzt.
                  Die Daten sind nicht mit Ihrer Person verknüpfbar.
                </p>
              </div>
            </div>
          </div>

          {/* Cookies */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-4">
              8. Cookies
            </h2>
            <div className="space-y-4 text-text-secondary-light dark:text-text-secondary-dark">
              <p>
                Diese Website verwendet <span className="font-medium text-text-light dark:text-text-dark">
                keine Tracking-Cookies</span>. Es werden ausschliesslich technisch notwendige
                Cookies eingesetzt, um die Funktionalität der Website zu gewährleisten:
              </p>
              <ul className="list-disc pl-5 space-y-1 mt-4">
                <li>Theme-Präferenz (Hell-/Dunkelmodus)</li>
                <li>Session-Verwaltung</li>
              </ul>
              <p className="mt-4">
                Diese Cookies enthalten keine personenbezogenen Daten und dienen ausschliesslich
                der Benutzerfreundlichkeit. Sie können in Ihren Browser-Einstellungen jederzeit
                gelöscht werden.
              </p>
              <p className="mt-4">
                <span className="font-medium text-text-light dark:text-text-dark">
                  Cookie-Consent-Banner:
                </span>{' '}
                Da ausschliesslich technisch notwendige Cookies verwendet werden, ist kein
                Cookie-Consent-Banner erforderlich.
              </p>
            </div>
          </div>

          {/* Ihre Rechte */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-4">
              9. Ihre Rechte
            </h2>
            <div className="space-y-4 text-text-secondary-light dark:text-text-secondary-dark">
              <p>
                Sie haben jederzeit das Recht auf:
              </p>
              <ul className="list-disc pl-5 space-y-2">
                <li>
                  <span className="font-medium text-text-light dark:text-text-dark">Auskunft</span>{' '}
                  über Ihre gespeicherten personenbezogenen Daten (Art. 15 DSGVO)
                </li>
                <li>
                  <span className="font-medium text-text-light dark:text-text-dark">Berichtigung</span>{' '}
                  unrichtiger Daten (Art. 16 DSGVO)
                </li>
                <li>
                  <span className="font-medium text-text-light dark:text-text-dark">Löschung</span>{' '}
                  Ihrer Daten (Art. 17 DSGVO)
                </li>
                <li>
                  <span className="font-medium text-text-light dark:text-text-dark">Einschränkung</span>{' '}
                  der Verarbeitung (Art. 18 DSGVO)
                </li>
                <li>
                  <span className="font-medium text-text-light dark:text-text-dark">Datenübertragbarkeit</span>{' '}
                  (Art. 20 DSGVO)
                </li>
                <li>
                  <span className="font-medium text-text-light dark:text-text-dark">Widerspruch</span>{' '}
                  gegen die Verarbeitung (Art. 21 DSGVO)
                </li>
                <li>
                  <span className="font-medium text-text-light dark:text-text-dark">Beschwerde</span>{' '}
                  bei einer Aufsichtsbehörde (Art. 77 DSGVO)
                </li>
              </ul>
              <p className="mt-6">
                Zur Ausübung dieser Rechte kontaktieren Sie mich bitte unter:{' '}
                <a
                  href="mailto:mannaluca02@gmail.com"
                  className="text-tekhelet hover:text-tekhelet/80 dark:text-tekhelet dark:hover:text-tekhelet/80 transition-colors font-medium"
                >
                  mannaluca02@gmail.com
                </a>
              </p>
            </div>
          </div>

          {/* Datensicherheit */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-4">
              10. Datensicherheit
            </h2>
            <div className="text-text-secondary-light dark:text-text-secondary-dark">
              <p>
                Alle Datenübertragungen erfolgen verschlüsselt über HTTPS (SSL/TLS).
                Es werden technische und organisatorische Sicherheitsmassnahmen getroffen,
                um Ihre Daten gegen zufällige oder vorsätzliche Manipulation, Verlust oder
                unbefugten Zugriff zu schützen.
              </p>
            </div>
          </div>

          {/* Änderungen */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-text-light dark:text-text-dark mb-4">
              11. Änderungen der Datenschutzerklärung
            </h2>
            <div className="text-text-secondary-light dark:text-text-secondary-dark">
              <p>
                Diese Datenschutzerklärung kann bei Bedarf angepasst werden, um rechtlichen
                Anforderungen oder Änderungen an den Diensten zu entsprechen. Die aktuelle
                Version ist stets auf dieser Seite verfügbar. Ich empfehle Ihnen, diese Seite
                regelmässig zu besuchen, um über eventuelle Änderungen informiert zu bleiben.
              </p>
            </div>
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
              href="/impressum"
              className="text-tekhelet hover:text-tekhelet/80 dark:text-tekhelet dark:hover:text-tekhelet/80 transition-colors"
            >
              Impressum
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
