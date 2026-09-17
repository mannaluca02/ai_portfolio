'use client'

import { useRef } from 'react'
import Hero from '@/components/home/Hero'
import About from '@/components/home/About'
import Experience from '@/components/home/Experience'
import Education from '@/components/home/Education'
import Projects from '@/components/home/Projects'
import Skills from '@/components/home/Skills'
import Certificates from '@/components/home/Certificates'
import Contact from '@/components/home/Contact'
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

      <About />
      <Experience />
      <Projects />
      <Education />
      <Skills />
      <Certificates />
      <Contact />
    </>
  )
}
