'use client'

interface HeroProps {
  onChatClick: () => void
}

export default function Hero({ onChatClick }: HeroProps) {
  return (
    <section
      id="home"
      className="relative min-h-screen flex items-center justify-center overflow-hidden px-6 py-32"
    >
      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto w-full space-y-16">
        {/* Label */}
        <div className="animate-fade-in-up">
          <span className="inline-block text-xs uppercase tracking-[0.2em] text-text-secondary-light dark:text-text-secondary-dark font-medium">
            Portfolio 2025
          </span>
        </div>

        {/* Main Heading */}
        <div className="space-y-6 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-semibold tracking-tight">
            <span className="block text-text-light dark:text-text-dark">Hi, ich bin</span>
            <span className="block text-tekhelet mt-2">Luca Manna</span>
          </h1>
          <p className="text-xl md:text-2xl text-text-secondary-light dark:text-text-secondary-dark max-w-2xl leading-relaxed">
            Full-Stack Developer & KI-Enthusiast
          </p>
        </div>

        {/* Main CTA - Chatbot */}
        <div className="space-y-4 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          <button
            onClick={onChatClick}
            className="group inline-flex items-center gap-3 px-8 py-4 bg-tekhelet text-cream rounded-xl hover:opacity-90 transition-all duration-300 font-medium text-base"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
            Chat mit meinem Portfolio-Bot
          </button>
          <p className="text-sm text-text-secondary-light dark:text-text-secondary-dark">
            Frag mich alles über meine Erfahrung & Projekte
          </p>
        </div>

        {/* Secondary Links */}
        <div className="flex flex-wrap gap-6 text-sm animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
          <a
            href="#about"
            className="text-text-secondary-light dark:text-text-secondary-dark hover:text-text-light dark:hover:text-text-dark transition-colors underline underline-offset-4 decoration-1"
          >
            Mehr erfahren
          </a>
          <a
            href="#contact"
            className="text-text-secondary-light dark:text-text-secondary-dark hover:text-text-light dark:hover:text-text-dark transition-colors underline underline-offset-4 decoration-1"
          >
            Kontakt
          </a>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-12 left-1/2 transform -translate-x-1/2 animate-bounce">
        <svg
          className="w-5 h-5 text-text-secondary-light dark:text-text-secondary-dark"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
        </svg>
      </div>
    </section>
  )
}
