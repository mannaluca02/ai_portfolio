# AI Portfolio - Digitales Portfolio mit RAG-Chatbot

Ein modernes Portfolio-Website mit integriertem KI-gestützten Chatbot, der Fragen zu Berufserfahrung, Projekten, Ausbildung und Skills des Portfolio-Inhabers beantworten kann.

## Inhaltsverzeichnis

- [Projektübersicht](#projektübersicht)
- [Repository-Struktur](#repository-struktur)
- [Technologie-Stack](#technologie-stack)
- [Setup & Installation](#setup--installation)
- [Konfiguration](#konfiguration)
- [Architektur](#architektur)
- [API-Dokumentation](#api-dokumentation)
- [Testing](#testing)
- [Deployment](#deployment)

---

## Projektübersicht

Dieses Projekt besteht aus zwei Hauptkomponenten:

1. **Frontend**: Next.js 14+ Portfolio-Website mit modernem UI
2. **Backend**: FastAPI-basierter RAG (Retrieval-Augmented Generation) Chatbot

Der Chatbot nutzt Semantic Search und LLM-gestützte Antwortgenerierung, um präzise und quellenbasierte Antworten zu Portfolio-Inhalten zu liefern.

### Hauptfunktionen

- **Portfolio-Anzeige**: Berufserfahrung, Projekte, Skills, Zertifikate, Ausbildung
- **RAG-Chatbot**: Intelligente Antworten mit Quellenangaben
- **Anti-Halluzination**: Semantische Verifikation der LLM-Antworten
- **Deep-Linking**: Klickbare Quellen führen direkt zu Portfolio-Sektionen
- **Rate-Limiting**: Schutz vor Missbrauch mit täglichen/monatlichen Limits
- **Responsive Design**: Optimiert für Desktop und Mobile
- **Dark Mode**: Automatische Erkennung der System-Einstellungen

---

## Repository-Struktur

```
ai_portfolio/
├── frontend/          # Next.js Frontend
│   ├── app/                     # App Router (Next.js 14+)
│   │   ├── api/                 # API Routes (Proxy zum Backend)
│   │   │   ├── contact-info/
│   │   │   ├── work-experiences/
│   │   │   ├── projects/
│   │   │   ├── skills/
│   │   │   ├── certificates/
│   │   │   ├── education/
│   │   │   ├── social-links/
│   │   │   └── send-email/
│   │   ├── impressum/
│   │   ├── datenschutz/
│   │   ├── layout.tsx           # Root Layout mit SEO
│   │   ├── page.tsx             # Hauptseite
│   │   ├── providers.tsx
│   │   ├── robots.ts
│   │   └── sitemap.ts
│   ├── components/
│   │   ├── home/                # Portfolio-Sektionen
│   │   │   ├── Hero.tsx
│   │   │   ├── About.tsx
│   │   │   ├── Experience.tsx
│   │   │   ├── Education.tsx
│   │   │   ├── Projects.tsx
│   │   │   ├── Skills.tsx
│   │   │   ├── Certificates.tsx
│   │   │   └── Contact.tsx
│   │   ├── chatbot/
│   │   │   └── ChatbotWidget.tsx   # Chatbot-Komponente
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Navigation.tsx
│   │   │   └── ClientLayout.tsx
│   │   ├── ui/
│   │   │   └── FadeInSection.tsx
│   │   ├── SmoothScroll.tsx
│   │   └── StructuredData.tsx
│   ├── lib/
│   │   └── hooks/
│   │       └── useScrollAnimation.ts
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── next.config.js
│
├── backend/           # FastAPI Backend
│   ├── app/
│   │   ├── api/                 # API Endpoints
│   │   │   ├── chat.py          # Chatbot-Endpunkt
│   │   │   ├── health.py        # Health-Check
│   │   │   ├── contact.py
│   │   │   ├── social.py
│   │   │   ├── work.py
│   │   │   ├── project.py
│   │   │   ├── skill.py
│   │   │   ├── certificate.py
│   │   │   └── education.py
│   │   ├── services/            # Business Logic
│   │   │   ├── chatbot_service.py    # RAG Orchestrierung
│   │   │   ├── embedding_service.py  # bge-m3 Embeddings
│   │   │   ├── retriever_service.py  # pgvector Suche
│   │   │   ├── generator_service.py  # LLM Antwortgenerierung
│   │   │   ├── verifier_service.py   # Anti-Halluzination
│   │   │   └── intent_service.py     # Intent-Erkennung
│   │   ├── models/              # SQLAlchemy ORM Models
│   │   │   ├── work_experience.py
│   │   │   ├── project.py
│   │   │   ├── skill.py
│   │   │   ├── certificate.py
│   │   │   ├── education.py
│   │   │   ├── hobby.py
│   │   │   ├── contact_info.py
│   │   │   └── social_link.py
│   │   ├── schemas/             # Pydantic Schemas
│   │   │   ├── chat.py
│   │   │   ├── work.py
│   │   │   ├── project.py
│   │   │   ├── skill.py
│   │   │   ├── certificate.py
│   │   │   ├── education.py
│   │   │   ├── contact.py
│   │   │   └── social.py
│   │   ├── database/            # Datenbankverbindung
│   │   │   ├── connection.py
│   │   │   └── session.py
│   │   ├── middleware/          # Middleware
│   │   │   └── rate_limiter.py  # Rate-Limiting
│   │   ├── config.py            # Konfiguration
│   │   └── main.py              # FastAPI App
│   ├── database/
│   │   └── supabase-script.sql  # Datenbank-Schema
│   ├── scripts/                 # Utility Scripts
│   │   ├── download_model.py    # ML-Modell Download
│   │   ├── generate_embeddings.py
│   │   ├── check_embeddings.py
│   │   ├── test_connection.py
│   │   ├── test_embedding_service.py
│   │   ├── test_retriever_service.py
│   │   ├── test_generator_service.py
│   │   ├── test_verifier_service.py
│   │   └── test_api.py
│   ├── start_local.sh           # Start-Script für lokale Entwicklung
│   └── requirements.txt
│
├── .idea/
│   ├── TechnologieStac.md       # Detaillierte Architektur-Doku
│   └── diagram.mmd              # Mermaid Diagramm
│
├── CLAUDE.md                    # Claude Code Instruktionen
└── README.md                    # Diese Datei
```

---

## Technologie-Stack

### Frontend
| Technologie | Version | Zweck |
|-------------|---------|-------|
| **Next.js** | 14.2+ | React Framework mit App Router |
| **React** | 18.3 | UI Library |
| **TypeScript** | 5.x | Type Safety |
| **Tailwind CSS** | 3.4 | Styling |
| **Framer Motion** | 11.x | Animationen |
| **Lenis** | 1.3 | Smooth Scrolling |
| **Resend** | 6.x | E-Mail-Versand |

### Backend
| Technologie | Version | Zweck |
|-------------|---------|-------|
| **FastAPI** | 0.118.2 | Web Framework |
| **Python** | 3.13+ | Programmiersprache |
| **SQLAlchemy** | 2.0 | ORM |
| **Pydantic** | 2.10 | Validierung |
| **pgvector** | 0.3.6 | Vector Search Extension |
| **sentence-transformers** | 3.3 | Embedding-Modell |
| **OpenAI** | 2.3 | LLM API |
| **slowapi** | 0.1.9 | Rate Limiting |

### Datenbank
| Technologie | Zweck |
|-------------|-------|
| **PostgreSQL** | Relationale Datenbank |
| **pgvector** | Vector Similarity Search |
| **Supabase** | Hosting (Free Tier) |

### ML/AI
| Komponente | Modell | Zweck |
|------------|--------|-------|
| **Embeddings** | BAAI/bge-m3 | 1024-dim Vektoren, multilingual (DE/EN) |
| **LLM** | GPT-3.5 Turbo | Antwortgenerierung |

---

## Setup & Installation

### Voraussetzungen

- **Node.js** >= 18.x
- **Python** >= 3.13
- **PostgreSQL** mit pgvector Extension (z.B. Supabase)
- **OpenAI API Key**

### 1. Repository klonen

```bash
git clone <repository-url>
cd ai_portfolio
```

### 2. Backend Setup

```bash
# In das Backend-Verzeichnis wechseln
cd backend

# Virtual Environment erstellen und aktivieren
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# ML-Modell herunterladen (~2.2GB)
python scripts/download_model.py

# Environment-Variablen erstellen
cp .env.example .env
# .env mit eigenen Werten ausfüllen (siehe Konfiguration)
```

### 3. Datenbank Setup

```bash
# SQL-Script in PostgreSQL ausführen
# Option A: Mit psql
psql -f database/supabase-script.sql

# Option B: Über Supabase SQL Editor
# Inhalt von database/supabase-script.sql kopieren und ausführen
```

### 4. Embeddings generieren

```bash
# Im Backend-Verzeichnis mit aktiviertem venv
python scripts/generate_embeddings.py
```

### 5. Backend starten

```bash
# Empfohlen: Start-Script verwenden (prüft Abhängigkeiten automatisch)
./start_local.sh

# Alternativ: Manuell starten
# Development Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production Server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Das `start_local.sh` Script:
- Prüft ob das Virtual Environment existiert
- Aktiviert das Virtual Environment automatisch
- Prüft ob die `.env` Datei vorhanden ist
- Prüft ob Port 8000 bereits belegt ist (mit Option zum Beenden)
- Startet den Development Server

### 6. Frontend Setup

```bash
# In das Frontend-Verzeichnis wechseln
cd ../frontend

# Dependencies installieren
npm install

# Development Server
npm run dev

# Production Build
npm run build
npm start
```

### 7. Anwendung aufrufen

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Konfiguration

### Backend Environment Variables (.env)

```env
# Datenbank (Pflicht)
DATABASE_URL=postgresql://user:password@host:port/database

# OpenAI API (Pflicht)
OPENAI_API_KEY=sk-...

# ML-Modell (Optional, Default-Werte)
BGE_MODEL_PATH=./app/ml_models/bge-m3
BGE_MODEL_NAME=BAAI/bge-m3

# Rate Limiting (Optional)
RATE_LIMIT_NATURAL_DAILY=20      # Anfragen/Tag für Natural Mode
RATE_LIMIT_NATURAL_MONTHLY=100   # Anfragen/Monat für Natural Mode
RATE_LIMIT_LISTEN_DAILY=40       # Anfragen/Tag für Listen Mode
RATE_LIMIT_LISTEN_MONTHLY=200    # Anfragen/Monat für Listen Mode

# CORS (Optional)
CORS_ORIGINS=http://localhost:3000,https://deine-domain.com

# Anwendung (Optional)
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### Frontend Environment Variables (.env.local)

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# E-Mail (Resend)
RESEND_API_KEY=re_...
```

---

## Architektur

### RAG (Retrieval-Augmented Generation) Workflow

```
User Frage
    │
    ▼
┌─────────────────────────────────────────────┐
│            RATE LIMITING                     │
│  - Prüft IP-basierte Limits (täglich/monatl.)│
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│          EMBEDDING SERVICE (bge-m3)          │
│  - Konvertiert Frage zu 1024-dim Vektor     │
│  - Multilingual (DE + EN)                    │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│         RETRIEVER SERVICE (pgvector)         │
│  - Similarity Search in PostgreSQL          │
│  - Intent-basiertes Table-Routing           │
│  - MMR für Diversität                        │
│  - Adaptive Schwellenwerte                   │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│        GENERATOR SERVICE (GPT-3.5)           │
│  - Erstellt natürliche Antwort              │
│  - Pflicht: Quellenreferenzen [1], [2], [3] │
│  - Max 300 Tokens                            │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│          VERIFIER SERVICE                    │
│  - Semantische Prüfung gegen Quellen        │
│  - 60% Confidence-Schwellenwert             │
│  - Fallback bei Verification-Fehler         │
└─────────────────────────────────────────────┘
    │
    ▼
Response mit Antwort + klickbaren Quellen
```

### Chatbot-Modi

| Modus | Beschreibung | Antwortzeit | Kosten | Status |
|-------|--------------|-------------|--------|--------|
| **Natural** | LLM-generierte Antworten mit Quellenangaben | ~2.8-3.2s | OpenAI API | Aktiv |
| **Listen** | Nur Semantic Search, zeigt relevante Quellen | ~0.3-0.4s | Kostenlos | Backend implementiert, im Frontend deaktiviert |

> **Hinweis:** Der Listen-Modus ist im Backend vollständig implementiert und funktionsfähig, wird jedoch im Frontend aktuell nicht angezeigt. Das Frontend verwendet standardmässig den Natural-Modus.

### Datenbank-Schema

Alle Content-Tabellen enthalten:
- `embedding VECTOR(1024)` - pgvector für Similarity Search
- `slug VARCHAR(255)` - Eindeutige URL-ID
- `section VARCHAR(100)` - Portfolio-Sektion
- `anchor VARCHAR(255)` - Deep-Link Anker

Tabellen:
- `work_experiences` - Berufserfahrung
- `projects` - Projekte
- `skills` - Fähigkeiten
- `certificates` - Zertifikate
- `education` - Ausbildung
- `hobbies` - Hobbys
- `contact_info` - Kontaktinformationen
- `social_links` - Social Media Links

---

## API-Dokumentation

### Chat-Endpunkt

```http
POST /api/chat
Content-Type: application/json

{
  "message": "Welche Projekte hast du gemacht?",
  "mode": "natural"  // oder "listen"
}
```

**Response:**
```json
{
  "answer": "Ich habe mehrere Projekte entwickelt...",
  "sources": [
    {
      "index": 1,
      "title": "E-Commerce Platform",
      "table": "projects",
      "slug": "project-ecommerce",
      "section": "projects",
      "anchor": "ecommerce",
      "similarity": 0.89
    }
  ],
  "mode": "natural",
  "confidence": 0.85,
  "verification": {
    "is_verified": true,
    "confidence": 0.87,
    "threshold": 0.60
  },
  "metadata": {
    "processing_time_ms": 2850,
    "model": "gpt-3.5-turbo",
    "tokens_used": 245
  }
}
```

### Health-Check

```http
GET /api/health
```

### Weitere Endpunkte

- `GET /api/work` - Berufserfahrung
- `GET /api/projects` - Projekte
- `GET /api/skills` - Skills
- `GET /api/certificates` - Zertifikate
- `GET /api/education` - Ausbildung
- `GET /api/contact` - Kontaktinfo
- `GET /api/social` - Social Links

Vollständige API-Dokumentation: http://localhost:8000/docs

---

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Datenbankverbindung testen
python scripts/test_connection.py

# Embedding Service testen
python scripts/test_embedding_service.py

# Retriever testen
python scripts/test_retriever_service.py

# Generator testen
python scripts/test_generator_service.py

# Verifier testen
python scripts/test_verifier_service.py

# API Integration Test
python scripts/test_api.py

# Embedding-Status prüfen
python scripts/check_embeddings.py
```

### Frontend Tests

```bash
cd frontend

# Linting
npm run lint

# Build (prüft TypeScript Fehler)
npm run build
```

---

## Deployment

### Backend (Railway/Render)

1. Repository mit Railway/Render verbinden
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables setzen (siehe Konfiguration)
5. ML-Modell wird beim Start automatisch geladen

### Frontend (Vercel)

1. Repository mit Vercel verbinden
2. Framework: Next.js
3. Root Directory: `frontend`
4. Environment Variables setzen
5. Deploy

### Datenbank (Supabase)

1. Neues Projekt auf Supabase erstellen
2. pgvector Extension aktivieren: `CREATE EXTENSION vector;`
3. SQL-Script ausführen (`database/supabase-script.sql`)
4. Connection String in Backend-Umgebungsvariablen eintragen

---

## Rate Limiting

| Modus | Täglich | Monatlich | Status |
|-------|---------|-----------|--------|
| **Natural** (LLM) | 20 Anfragen | 100 Anfragen | Aktiv |
| **Listen** (Search) | 40 Anfragen | 200 Anfragen | Backend-only (Frontend deaktiviert) |

Bei Überschreitung wird HTTP 429 zurückgegeben.

Response Header enthalten:
- `X-RateLimit-Daily-Remaining`
- `X-RateLimit-Monthly-Remaining`

---

## Anti-Halluzination

Der Chatbot implementiert mehrere Strategien zur Vermeidung von Halluzinationen:

1. **Strikte Quellenreferenzierung**: LLM muss jede Aussage mit [1], [2], [3] belegen
2. **Semantische Verifikation**: Antwort wird gegen Quellen-Embeddings geprüft
3. **Confidence-Schwellenwert**: 60% Similarity erforderlich
4. **Fallback**: Bei Verifikationsfehler werden nur Originalquellen angezeigt
5. **"Keine Info"-Erkennung**: Wenn LLM keine Infos findet, werden keine Quellen gezeigt
