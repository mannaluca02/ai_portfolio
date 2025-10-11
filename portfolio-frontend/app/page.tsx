'use client'

import { useRef } from 'react'
import Hero from '@/components/home/Hero'
import ChatbotWidget, { ChatbotWidgetRef } from '@/components/chatbot/ChatbotWidget'

export default function Home() {
  const chatbotRef = useRef<ChatbotWidgetRef>(null)

  const handleChatClick = () => {
    chatbotRef.current?.open()
  }

  return (
    <>
      <Hero onChatClick={handleChatClick} />
      <ChatbotWidget ref={chatbotRef} />

      {/* Additional sections will be added here */}
      <section id="about" className="min-h-screen py-32 px-6 md:px-12 lg:px-20">
        <div className="max-w-5xl mx-auto space-y-16">
          {/* Section Label */}
          <div>
            <span className="inline-block text-xs uppercase tracking-[0.2em] text-text-secondary-light dark:text-text-secondary-dark font-medium">
              01 — Über mich
            </span>
          </div>

          {/* Content */}
          <div className="space-y-8">
            <h2 className="text-5xl md:text-6xl font-semibold tracking-tight text-text-light dark:text-text-dark">
              Wer ich bin
            </h2>
            <p className="text-xl md:text-2xl text-text-secondary-light dark:text-text-secondary-dark max-w-3xl leading-relaxed">
              Content coming soon...
            </p>
          </div>
        </div>
      </section>
    </>
  )
}
