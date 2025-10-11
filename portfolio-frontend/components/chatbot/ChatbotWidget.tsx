'use client'

import { useState, useEffect, forwardRef, useImperativeHandle, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export interface ChatbotWidgetRef {
  open: () => void
}

type ChatMode = 'listen' | 'natural'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{
    title: string
    link: string
    relevance: number
  }>
  responseTime?: number
  verified?: boolean
}

const ChatbotWidget = forwardRef<ChatbotWidgetRef>((props, ref) => {
  const [isOpen, setIsOpen] = useState(false)
  const [showFloatingButton, setShowFloatingButton] = useState(false)
  const [mode, setMode] = useState<ChatMode>('listen')
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 200) {
        setShowFloatingButton(true)
      } else {
        setShowFloatingButton(false)
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useImperativeHandle(ref, () => ({
    open: () => {
      setIsOpen(true)
    }
  }))

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // TODO: Replace with actual API call
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: mode === 'listen'
          ? '📌 3 relevante Informationen gefunden:'
          : 'Ja, ich habe umfangreiche React-Erfahrung! [1] Von 2021 bis 2023 habe ich als Frontend Developer bei Firma X gearbeitet.',
        sources: [
          { title: 'Frontend Developer mit React', link: '#experience-firma-x', relevance: 95 },
          { title: 'React + Next.js E-Commerce Projekt', link: '#projects-ecommerce', relevance: 87 },
          { title: 'React Professional Certificate', link: '#certificates-react', relevance: 81 },
        ],
        responseTime: mode === 'listen' ? 0.3 : 2.9,
        verified: mode === 'natural' ? true : undefined
      }
      setMessages(prev => [...prev, botMessage])
      setIsLoading(false)
    }, mode === 'listen' ? 300 : 2900)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <>
      {/* Backdrop when chat is open */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-text-light/20 dark:bg-dark-bg/50 backdrop-blur-sm z-[60]"
            onClick={() => setIsOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Floating Button */}
      <AnimatePresence>
        {showFloatingButton && !isOpen && (
          <motion.button
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 100, opacity: 0 }}
            transition={{ duration: 0.3, type: 'spring' }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 bg-tekhelet text-cream p-4 rounded-full shadow-2xl hover:opacity-90 transition-all transform hover:scale-110 z-50"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Expanded Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ duration: 0.3, type: 'spring' }}
            className="fixed bottom-4 right-4 w-[95vw] sm:w-96 h-[85vh] sm:h-[600px] bg-cream dark:bg-dark-bg-secondary rounded-2xl shadow-2xl overflow-hidden z-[70] border border-cream-dark dark:border-dark-bg flex flex-col"
          >
            {/* Header */}
            <div className="bg-tekhelet text-cream p-4 flex-shrink-0">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                  <h3 className="font-medium text-cream">Portfolio Chatbot</h3>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="hover:opacity-80 p-2 rounded-lg transition-opacity"
                >
                  <svg className="w-5 h-5 text-cream" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Mode Selection */}
              <div className="flex gap-2">
                <button
                  onClick={() => setMode('listen')}
                  className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    mode === 'listen'
                      ? 'bg-cream text-tekhelet'
                      : 'bg-tekhelet/30 text-cream/70 hover:bg-tekhelet/40'
                  }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Listen
                  </div>
                </button>
                <button
                  onClick={() => setMode('natural')}
                  className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    mode === 'natural'
                      ? 'bg-cream text-tekhelet'
                      : 'bg-tekhelet/30 text-cream/70 hover:bg-tekhelet/40'
                  }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    Natural
                  </div>
                </button>
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-cream dark:bg-dark-bg-secondary">
              {/* Welcome Message */}
              {messages.length === 0 && (
                <div className="bg-text-light/5 dark:bg-text-dark/5 rounded-lg p-4">
                  <p className="text-sm text-text-light dark:text-text-dark mb-2">
                    👋 Hallo! Ich bin dein Portfolio-Assistent.
                  </p>
                  <p className="text-xs text-text-secondary-light dark:text-text-secondary-dark">
                    <strong>Listen-Modus:</strong> Schnelle Suche (40 Anfragen/Tag)<br />
                    <strong>Natural-Modus:</strong> KI-Antworten (10 Anfragen/Tag)
                  </p>
                </div>
              )}

              {/* Messages */}
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-tekhelet text-cream'
                        : 'bg-text-light/5 dark:bg-text-dark/5 text-text-light dark:text-text-dark'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                    {/* Sources */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-text-light/10 dark:border-text-dark/10 space-y-2">
                        <p className="text-xs font-medium opacity-75">📚 Quellen:</p>
                        {message.sources.map((source, index) => (
                          <a
                            key={index}
                            href={source.link}
                            className="block text-xs p-2 rounded bg-text-light/5 dark:bg-text-dark/5 hover:bg-text-light/10 dark:hover:bg-text-dark/10 transition-colors"
                            onClick={() => setIsOpen(false)}
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-medium">[{index + 1}] {source.title}</span>
                              <span className="text-tekhelet dark:text-tekhelet opacity-75">{source.relevance}%</span>
                            </div>
                            <div className="flex items-center gap-1 mt-1 text-text-secondary-light dark:text-text-secondary-dark">
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                              </svg>
                              Details ansehen
                            </div>
                          </a>
                        ))}
                      </div>
                    )}

                    {/* Response Time & Verification */}
                    {message.role === 'assistant' && (message.responseTime || message.verified !== undefined) && (
                      <div className="mt-2 pt-2 border-t border-text-light/10 dark:border-text-dark/10 flex items-center gap-3 text-xs opacity-60">
                        {message.verified !== undefined && (
                          <span className="flex items-center gap-1">
                            {message.verified ? '✓' : '✗'} {message.verified ? 'Verifiziert' : 'Nicht verifiziert'}
                          </span>
                        )}
                        {message.responseTime && (
                          <span>⏱️ {message.responseTime}s</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Loading Indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-text-light/5 dark:bg-text-dark/5 rounded-lg p-3">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-tekhelet rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-tekhelet rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-tekhelet rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="flex-shrink-0 p-4 bg-cream dark:bg-dark-bg-secondary border-t border-cream-dark dark:border-dark-bg">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Stell mir eine Frage..."
                  disabled={isLoading}
                  className="flex-1 px-4 py-2 border border-cream-dark dark:border-dark-bg rounded-lg focus:outline-none focus:border-tekhelet bg-cream dark:bg-dark-bg text-text-light dark:text-text-dark disabled:opacity-50"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={isLoading || !inputValue.trim()}
                  className="bg-tekhelet text-cream px-4 py-2 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
})

ChatbotWidget.displayName = 'ChatbotWidget'

export default ChatbotWidget
