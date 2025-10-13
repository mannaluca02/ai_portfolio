# Portfolio Backend - RAG Chatbot API

FastAPI backend for a portfolio website with an integrated RAG (Retrieval-Augmented Generation) chatbot.

## Features

- **Semantic Search**: pgvector-based similarity search across portfolio data
- **Embedding Generation**: bge-m3 multilingual embeddings (1024 dimensions)
- **Natural Language Generation**: OpenAI GPT-3.5 powered responses
- **Hallucination Detection**: Verifier service to ensure response accuracy
- **Dual Mode Operation**:
  - Listen Mode (fast, no LLM)
  - Natural Mode (with LLM generation)

## Tech Stack

- **Framework**: FastAPI 0.118.2
- **Database**: PostgreSQL with pgvector extension (via Supabase)
- **ML Models**:
  - bge-m3 (BAAI) for embeddings
  - OpenAI GPT-3.5 Turbo for generation
- **ORM**: SQLAlchemy 2.0
- **Python**: 3.13+

## Project Structure

```
portfolio-backend/
├── app/
│   ├── api/              # API endpoints
│   ├── database/         # Database connection & session
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   │   ├── embedding_service.py
│   │   ├── retriever_service.py
│   │   ├── generator_service.py
│   │   └── verifier_service.py
│   ├── middleware/       # Custom middleware
│   ├── utils/            # Helper functions
│   ├── config.py         # Settings management
│   └── main.py           # FastAPI app
├── scripts/              # Utility scripts
├── tests/                # Tests
├── database/             # SQL scripts
├── requirements.txt      # Python dependencies
└── .env.example          # Environment template
```

## Setup

### 1. Prerequisites

- Python 3.13+
- PostgreSQL with pgvector extension (or Supabase account)
- OpenAI API key

### 2. Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: Your OpenAI API key
- `CORS_ORIGINS`: Allowed frontend origins

### 4. Download ML Model

```bash
python scripts/download_model.py
```

This downloads the bge-m3 model (~2.2GB) to `app/ml_models/`.

### 5. Database Setup

Ensure your PostgreSQL database has the pgvector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 6. Generate Embeddings

```bash
python scripts/generate_embeddings.py
```

## Backend Starten - Schnellanleitung

### Methode 1: Mit Start-Skript (Empfohlen)

Das ist die einfachste Methode:

```bash
cd portfolio-backend
./start.sh
```

Das Skript erledigt automatisch:
- ✓ Überprüfung des Virtual Environments
- ✓ Aktivierung des Virtual Environments
- ✓ Überprüfung der .env Datei
- ✓ Port-Verfügbarkeit prüfen
- ✓ Server starten

### Methode 2: Manuell

#### Voraussetzung
Das Virtual Environment und alle Dependencies müssen installiert sein (siehe Setup oben).

#### Schritt 1: Terminal öffnen
Navigiere zum Backend-Verzeichnis:
```bash
cd portfolio-backend
```

#### Schritt 2: Virtual Environment aktivieren
```bash
source venv/bin/activate
```

**Wichtig**: Du erkennst, dass das Virtual Environment aktiv ist, wenn `(venv)` vor deinem Terminal-Prompt erscheint.

#### Schritt 3: Server starten
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Fertig!
Das Backend ist jetzt verfügbar unter:
- API: `http://localhost:8000`
- Dokumentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### Server stoppen
Drücke `CTRL+C` im Terminal, um den Server zu stoppen.

---

## Running the Application (Detailed)

### Development Mode
```bash
# Mit aktiviertem venv
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
# Mit aktiviertem venv
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Alternative: Ohne Virtual Environment zu aktivieren
```bash
# Startet direkt mit dem venv Python
./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`

## Testing

```bash
# Test database connection
python scripts/test_connection.py

# Test embedding service
python scripts/test_embedding_service.py

# Test retriever service
python scripts/test_retriever_service.py

# Test generator service
python scripts/test_generator_service.py

# Test verifier service
python scripts/test_verifier_service.py
```

## API Endpoints

- `GET /`: API status
- `POST /api/chat`: Chatbot endpoint
- `GET /api/health`: Health check

## Services Architecture

### 1. Embedding Service
- Generates 1024-dimensional embeddings using bge-m3
- Singleton pattern to avoid model reloading
- Supports batch processing

### 2. Retriever Service
- Performs semantic search using pgvector
- Cosine similarity matching
- Searches across 8 portfolio tables

### 3. Generator Service
- Generates natural language responses using GPT-3.5
- Includes source citations [1], [2], [3]
- German language responses

### 4. Verifier Service
- Anti-hallucination verification
- Sentence-by-sentence similarity check
- 60% confidence threshold

## Database Models

- `work_experiences`
- `projects`
- `skills`
- `certificates`
- `education`
- `hobbies`
- `contact_info`
- `social_links`

Each model includes:
- Vector embedding (1024 dimensions)
- Slug, section, anchor for frontend linking
- Timestamps (created_at, updated_at)

## Development Notes

- ML models are NOT tracked in git (too large)
- `.env` file is NOT tracked (contains secrets)
- Use `.env.example` as template
- Virtual environment should be in `venv/`

## License

Private project - FHNW

## Author

Luca Manna
