# Projektstruktur - AI Portfolio mit RAG Chatbot

## Übersicht
```
ai_portfolio/
├── .idea/                          # Projektdokumentation
│   ├── TechnologieStac.md         # Technologie-Stack Dokumentation
│   └── diagram.mmd                # Architektur-Diagramm
├── frontend/            # Next.js 14+ Frontend
│   ├── src/
│   │   ├── app/                   # App Router (Next.js 14+)
│   │   │   ├── layout.tsx        # Root Layout
│   │   │   ├── page.tsx          # Homepage
│   │   │   ├── cv/               # CV/Portfolio Seite
│   │   │   │   └── page.tsx
│   │   │   ├── projects/         # Projekte Detailseiten
│   │   │   │   ├── page.tsx
│   │   │   │   └── [slug]/
│   │   │   │       └── page.tsx
│   │   │   ├── experience/       # Berufserfahrung Detailseiten
│   │   │   │   └── [slug]/
│   │   │   │       └── page.tsx
│   │   │   ├── skills/           # Skills Seite
│   │   │   │   └── page.tsx
│   │   │   └── contact/          # Kontakt Seite
│   │   │       └── page.tsx
│   │   ├── components/           # React Komponenten
│   │   │   ├── chatbot/          # Chatbot Komponenten
│   │   │   │   ├── ChatbotWidget.tsx      # Hauptkomponente
│   │   │   │   ├── ChatbotUI.tsx          # UI Container
│   │   │   │   ├── ChatMessage.tsx        # Einzelne Nachricht
│   │   │   │   ├── SourceList.tsx         # Quellen-Liste
│   │   │   │   ├── SourceItem.tsx         # Einzelne Quelle
│   │   │   │   ├── ModeToggle.tsx         # Listen/Natural Toggle
│   │   │   │   ├── ChatInput.tsx          # Input Field
│   │   │   │   └── TypingIndicator.tsx    # Loading Animation
│   │   │   ├── portfolio/        # Portfolio Komponenten
│   │   │   │   ├── Hero.tsx              # Hero Section
│   │   │   │   ├── About.tsx             # About Section
│   │   │   │   ├── ExperienceCard.tsx    # Berufserfahrung Card
│   │   │   │   ├── ProjectCard.tsx       # Projekt Card
│   │   │   │   ├── SkillCard.tsx         # Skill Badge/Card
│   │   │   │   ├── CertificateCard.tsx   # Zertifikat Card
│   │   │   │   ├── EducationCard.tsx     # Bildung Card
│   │   │   │   ├── HobbyCard.tsx         # Hobby Card
│   │   │   │   ├── Timeline.tsx          # Timeline für Experience
│   │   │   │   └── ContactInfo.tsx       # Kontakt Informationen
│   │   │   ├── ui/               # Wiederverwendbare UI Komponenten
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Badge.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   └── Toast.tsx
│   │   │   └── layout/           # Layout Komponenten
│   │   │       ├── Header.tsx
│   │   │       ├── Footer.tsx
│   │   │       ├── Navigation.tsx
│   │   │       └── Sidebar.tsx
│   │   ├── lib/                  # Utilities & API Clients
│   │   │   ├── api/              # API Client
│   │   │   │   ├── client.ts            # Axios/Fetch Wrapper
│   │   │   │   ├── chatbot.ts           # Chatbot API
│   │   │   │   └── portfolio.ts         # Portfolio Daten API
│   │   │   ├── hooks/            # Custom React Hooks
│   │   │   │   ├── useChatbot.ts        # Chatbot State Management
│   │   │   │   ├── usePortfolio.ts      # Portfolio Daten Hook
│   │   │   │   ├── useScrollTo.ts       # Smooth Scroll Hook
│   │   │   │   └── useMediaQuery.ts     # Responsive Hook
│   │   │   ├── utils/            # Helper Functions
│   │   │   │   ├── formatting.ts        # Date, Text Formatting
│   │   │   │   ├── validators.ts        # Input Validation
│   │   │   │   └── slugify.ts           # Slug Generation
│   │   │   └── types/            # TypeScript Types
│   │   │       ├── chatbot.ts
│   │   │       ├── portfolio.ts
│   │   │       └── api.ts
│   │   ├── styles/               # Global Styles
│   │   │   ├── globals.css
│   │   │   └── chatbot.css
│   │   └── config/               # Configuration
│   │       ├── api.config.ts     # API URLs
│   │       └── site.config.ts    # Site Metadata
│   ├── public/                   # Static Assets
│   │   ├── images/
│   │   ├── icons/
│   │   └── fonts/
│   ├── .env.local                # Environment Variables
│   ├── .env.example              # Example Environment Variables
│   ├── next.config.js            # Next.js Configuration
│   ├── tailwind.config.ts        # Tailwind CSS Configuration
│   ├── tsconfig.json             # TypeScript Configuration
│   ├── package.json
│   └── README.md
│
├── backend/            # FastAPI Backend
│   ├── app/
│   │   ├── main.py              # FastAPI Entry Point
│   │   ├── config.py            # Configuration & Settings
│   │   ├── api/                 # API Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── chatbot.py              # Chatbot Endpoints
│   │   │   ├── portfolio.py            # Portfolio CRUD Endpoints
│   │   │   ├── embeddings.py           # Embedding Generation Webhook
│   │   │   └── health.py               # Health Check
│   │   ├── services/            # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── embedding_service.py    # bge-m3 Embedding Generation
│   │   │   ├── retriever_service.py    # pgvector Similarity Search
│   │   │   ├── generator_service.py    # LLM Response Generation
│   │   │   ├── verifier_service.py     # Semantic Verification
│   │   │   ├── link_service.py         # Link Generation
│   │   │   └── rate_limiter_service.py # Rate Limiting Logic
│   │   ├── models/              # Database Models (SQLAlchemy)
│   │   │   ├── __init__.py
│   │   │   ├── work_experience.py
│   │   │   ├── project.py
│   │   │   ├── skill.py
│   │   │   ├── certificate.py
│   │   │   ├── education.py
│   │   │   ├── hobby.py
│   │   │   ├── contact_info.py
│   │   │   └── social_link.py
│   │   ├── schemas/             # Pydantic Schemas (Request/Response)
│   │   │   ├── __init__.py
│   │   │   ├── chatbot_schema.py       # Chat Request/Response
│   │   │   ├── portfolio_schema.py     # Portfolio Data Schemas
│   │   │   └── embedding_schema.py     # Embedding Webhook Schema
│   │   ├── database/            # Database Setup
│   │   │   ├── __init__.py
│   │   │   ├── connection.py           # Database Connection Pool
│   │   │   ├── session.py              # Session Management
│   │   │   └── supabase-script.sql     # Database Schema (für Referenz)
│   │   ├── middleware/          # FastAPI Middleware
│   │   │   ├── __init__.py
│   │   │   ├── rate_limiter.py         # Rate Limiting Middleware
│   │   │   ├── cors.py                 # CORS Configuration
│   │   │   └── error_handler.py        # Global Error Handler
│   │   ├── utils/               # Utility Functions
│   │   │   ├── __init__.py
│   │   │   ├── logger.py               # Logging Setup
│   │   │   ├── validators.py           # Input Validation
│   │   │   └── blockwords.py           # Blockwords Filter
│   │   └── ml_models/           # ML Models Cache
│   │       └── bge-m3/                 # Downloaded bge-m3 Model
│   ├── tests/                   # Tests
│   │   ├── __init__.py
│   │   ├── test_chatbot.py
│   │   ├── test_embeddings.py
│   │   ├── test_retriever.py
│   │   └── test_api.py
│   ├── scripts/                 # Utility Scripts
│   │   ├── download_model.py           # Download bge-m3 Model
│   │   ├── generate_embeddings.py      # Batch Embedding Generation
│   │   └── seed_database.py            # Database Seeding
│   ├── .env                     # Environment Variables
│   ├── .env.example             # Example Environment Variables
│   ├── requirements.txt         # Python Dependencies
│   ├── pyproject.toml           # Poetry Configuration (optional)
│   ├── Dockerfile               # Docker Container
│   ├── docker-compose.yml       # Docker Compose für Local Development
│   └── README.md
│
├── database/                     # Database Scripts & Migrations
│   ├── migrations/              # Migration Scripts (Alembic)
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── seeds/                   # Seed Data
│   │   └── sample_data.sql
│   └── supabase-script.sql      # Complete Database Setup
│
├── docs/                        # Dokumentation
│   ├── API.md                   # API Dokumentation
│   ├── ARCHITECTURE.md          # Architektur-Übersicht
│   ├── DEPLOYMENT.md            # Deployment Guide
│   ├── LOCAL_SETUP.md           # Local Development Setup
│   └── CHATBOT_USAGE.md         # Chatbot User Guide
│
├── .github/                     # GitHub Workflows
│   └── workflows/
│       ├── frontend-ci.yml      # Frontend CI/CD
│       ├── backend-ci.yml       # Backend CI/CD
│       └── deploy.yml           # Deployment Workflow
│
├── .gitignore                   # Git Ignore
├── CLAUDE.md                    # Claude Instruktionen
├── README.md                    # Projekt README
└── PROJECT_STRUCTURE.md         # Diese Datei
```

## Technologie-Details

### Frontend (frontend/)
- **Framework:** Next.js 14+ (App Router)
- **UI:** React 18, TypeScript, Tailwind CSS
- **State Management:** React Hooks, Context API
- **API Client:** Axios / Fetch
- **Deployment:** Vercel

### Backend (backend/)
- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL mit pgvector Extension
- **ML:** bge-m3 Embedding Model (lokaler Betrieb)
- **LLM:** OpenAI GPT-3.5 Turbo API
- **Rate Limiting:** slowapi
- **Deployment:** Railway / Render

### Database
- **PostgreSQL** mit **pgvector Extension**
- Tabellen: work_experiences, projects, skills, certificates, education, hobbies, contact_info, social_links
- Alle Tabellen haben embedding-Spalten für Semantic Search

## Workflow-Übersicht

### User Query (Natural-Modus)
1. Frontend → Backend API (`POST /api/chatbot/query`)
2. Rate Limiting Check
3. Query Validation & Blockwords Filter
4. Embedding Generation (bge-m3)
5. Similarity Search in PostgreSQL (pgvector)
6. Context Building mit Metadaten
7. LLM Response Generation (GPT-3.5 mit Quellenpflicht)
8. Semantic Verification (Anti-Hallucination)
9. Link Generation (deterministische URLs)
10. Response mit klickbaren Quellen
11. Frontend Display mit Smooth-Scroll zu Sections

### Database Update Flow
1. PostgreSQL INSERT/UPDATE
2. Database Trigger ausgelöst
3. FastAPI Webhook (`POST /api/embeddings/generate`)
4. bge-m3 generiert Embedding
5. Embedding wird in pgvector-Column gespeichert
6. Transaktional committed
7. Sofort verfügbar im Chatbot

## Entwicklungsumgebung Setup

### Voraussetzungen
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+ mit pgvector Extension
- Git

### Setup Steps
1. **Repository klonen**
2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   npm run dev
   ```
3. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   python scripts/download_model.py  # Download bge-m3
   uvicorn app.main:app --reload
   ```
4. **Database Setup:**
   - Supabase Account erstellen oder lokale PostgreSQL Installation
   - pgvector Extension aktivieren
   - `database/supabase-script.sql` ausführen

## Deployment

### Frontend (Vercel)
1. GitHub Repository mit Vercel verbinden
2. Root Directory: `frontend`
3. Environment Variables konfigurieren
4. Auto-Deploy bei Push zu main

### Backend (Railway)
1. GitHub Repository mit Railway verbinden
2. Root Directory: `backend`
3. Environment Variables konfigurieren
4. Auto-Deploy bei Push zu main

### Database (Supabase)
1. Supabase Projekt erstellen
2. pgvector Extension aktivieren
3. SQL Editor: `database/supabase-script.sql` ausführen
4. Connection String kopieren

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:5432/database
OPENAI_API_KEY=sk-...
BGE_MODEL_PATH=./app/ml_models/bge-m3
RATE_LIMIT_NATURAL_MODE=10
RATE_LIMIT_LISTEN_MODE=40
CORS_ORIGINS=http://localhost:3000,https://portfolio.com
```

## Nächste Schritte
1. Frontend-Grundstruktur erstellen
2. Backend API Endpoints implementieren
3. Database Setup durchführen
4. Embedding Service implementieren
5. Chatbot Logic implementieren
6. Tests schreiben
7. Deployment konfigurieren
