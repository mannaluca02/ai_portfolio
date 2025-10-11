import Link from 'next/link'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-smoky-black text-seasalt py-12">
      <div className="max-w-7xl mx-auto px-6 md:px-12 lg:px-24">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* About */}
          <div>
            <h3 className="text-xl font-bold mb-4 text-scarlet">Luca Manna</h3>
            <p className="text-taupe-gray">
              Full-Stack Developer mit Fokus auf moderne Web-Technologien und KI-Integration.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-xl font-bold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link href="#about" className="text-taupe-gray hover:text-seasalt transition-colors">
                  Über mich
                </Link>
              </li>
              <li>
                <Link href="#projects" className="text-taupe-gray hover:text-seasalt transition-colors">
                  Projekte
                </Link>
              </li>
              <li>
                <Link href="#contact" className="text-taupe-gray hover:text-seasalt transition-colors">
                  Kontakt
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-xl font-bold mb-4">Kontakt</h3>
            <ul className="space-y-2 text-taupe-gray">
              <li>Email: luca@example.com</li>
              <li>GitHub: github.com/lucamanna</li>
              <li>LinkedIn: linkedin.com/in/lucamanna</li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-taupe-gray/30 pt-8 text-center text-taupe-gray">
          <p>&copy; {currentYear} Luca Manna. Alle Rechte vorbehalten.</p>
        </div>
      </div>
    </footer>
  )
}
