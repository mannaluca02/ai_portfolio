# AGENTS.md

This file provides guidance to coding agents working in this repository.

It is a copy of CLAUDE.md and must stay in sync with it: the two files differ in
this header and nowhere else. If you change one, change the other in the same
commit. A stale copy here is worse than no copy, because an agent will follow it
as if it were current.

## Project Overview

A digital portfolio website with an integrated RAG (Retrieval-Augmented Generation) chatbot. The chatbot can answer questions about portfolio content using semantic search and LLM-powered responses.

**Goal:** Create a portfolio that showcases work experience, projects, skills, and certificates, with an intelligent chatbot that can answer visitor questions about the portfolio owner's background.

## Architecture

This is a full-stack application with:

- **Frontend**: Next.js 14+ (App Router) with TypeScript and Tailwind CSS
- **Backend**: FastAPI (Python 3.13+) with RAG-based chatbot
- **Database**: PostgreSQL with pgvector extension (hosted on Supabase)
- **ML Models**: bge-m3 (1024-dim embeddings), OpenAI gpt-4o-mini

### Key Components

**Backend** (`backend/`):

- **API Layer** (`app/api/`): REST endpoints for chatbot and health checks
- **Services** (`app/services/`):
  - `embedding_service.py`: Generates embeddings using bge-m3 model
  - `retriever_service.py`: Semantic search via pgvector
  - `generator_service.py`: LLM response generation with strict source citation
  - `verifier_service.py`: Anti-hallucination verification
  - `chatbot_service.py`: Orchestrates the RAG pipeline
  - `document_service.py`: Canonical row text for embeddings, evidence and excerpts
  - `query_service.py`: Strips the owner's name from the search text; corpus vocabulary
  - `intent_service.py`: Ranking hints only, never an evidence allowlist
  - `sentence_service.py`: German sentence boundaries, shared by verifier and excerpts
- **Models** (`app/models/`): SQLAlchemy ORM models for all portfolio data
- **Middleware** (`app/middleware/`): Rate limiting and CORS
- **Database** (`app/database/`): Connection management and session handling

**Database Structure**:
All tables include:

- `embedding VECTOR(1024)`: For semantic search
- `slug`, `section`, `anchor`: For deterministic deep-linking
- Standard timestamps

Main tables: `work_experiences`, `projects`, `skills`, `certificates`, `education`, `hobbies`, `languages`, `contact_info`, `social_links`

`languages` holds spoken languages only; programming languages are `skills`. It has no public API endpoint and no section of its own on the page: it exists so the chatbot can answer language questions, and its source links scroll to the skills section.

### RAG Workflow

The chatbot supports two modes:

1. **Listen Mode** (fast, free):
  - Query → Embedding → pgvector search → Return matched sources
  - No LLM involved, ~0.3-0.4s response time
2. **Natural Mode** (intelligent, uses OpenAI):
  - Query → Embedding → pgvector search → LLM generation with source citations → Semantic verification → Response with clickable links
  - ~2.8-3.2s response time
  - LLM MUST cite sources with [1], [2], [3]
  - Responses are verified against source material to prevent hallucinations

## Database

**Critical**: Always reference `backend/database/supabase-script.sql` to understand the database schema. This is the single source of truth for:

- Table structures
- ENUMs (employment_type, project_type, skill_level, etc.)
- Vector indices
- Triggers for automatic timestamp updates

The database uses PostgreSQL with pgvector extension for efficient similarity search.

## Development Commands

### Backend Setup and Development

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download ML model (bge-m3, ~2.2GB)
python scripts/download_model.py

# Generate embeddings for existing database content
python scripts/generate_embeddings.py

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Test individual components (from backend/)
python scripts/test_connection.py          # Database connection
python scripts/test_embedding_service.py   # Embedding generation
python scripts/test_retriever_service.py   # Semantic search
python scripts/test_generator_service.py   # LLM generation
python scripts/test_verifier_service.py    # Hallucination detection
python scripts/test_api.py                 # Full API integration

# Check embedding status
python scripts/check_embeddings.py
```

### Database Operations

```bash
# Execute the complete database setup (in PostgreSQL)
psql -f backend/database/supabase-script.sql

# Or via Supabase SQL Editor:
# Copy contents of supabase-script.sql and execute
```

## Important Constraints and Behaviors

1. **Never access .env files**: Credentials and API keys should never be read or displayed
2. **Always check supabase-script.sql** when working with database models or queries
3. **Use .idea/ documentation**: Reference files in `.idea/` directory to understand project architecture and technology stack
4. **Think rationally and logically**: Behave like an experienced software developer
5. **Ask for clarification**: When something is unclear, always ask before proceeding

## Rate Limiting

**Centralized Configuration** - All rate limits are configured in `app/config.py` and can be adjusted via environment variables.

**Natural Mode** (LLM-powered responses):

- 50 requests per day per IP
- 400 requests per month per IP
- ~2.8-3.2s response time
- Token Limit: Max 300 tokens per LLM response

**Listen Mode** (search-only, currently disabled in frontend):

- 40 requests per day per IP
- 200 requests per month per IP
- ~0.3-0.4s response time

**Implementation**:

- Dual-period rate limiting (daily + monthly) in `app/middleware/rate_limiter.py`
- Uses `DailyMonthlyRateLimiter` class with automatic counter resets
- Rate limit headers included in API responses: `X-RateLimit-Daily-Remaining`, `X-RateLimit-Monthly-Remaining`
- Tracks usage per IP address and per chat mode independently

## Key Technologies

- **Embeddings**: BAAI/bge-m3 (multilingual, 1024 dimensions)
- **Vector Search**: pgvector with HNSW indices
- **LLM**: OpenAI gpt-4o-mini with strict source citation requirements
- **ORM**: SQLAlchemy 2.0
- **API Framework**: FastAPI 0.118.2
- **Deployment**: Backend on Railway (paid Hobby plan, 5 CHF per month), database on
  Supabase (free tier), frontend on Vercel (Hobby plan).

**The Railway service never sleeps.** The plan is paid, so there is no idle
shutdown and no cold start to design around. Do not add keep-alive pings,
warm-up jobs or sleep workarounds for the backend.

The Supabase project is a different matter: on the free tier it pauses after
7 days without activity. That is what the daily Vercel cron exists for.

## Keeping Supabase awake

Supabase pauses a free-tier project after 7 days without activity. The site
itself only touches the database when a visitor loads it, so a quiet week would
put the project to sleep.

`frontend/vercel.json` runs a daily Vercel cron against
`frontend/app/api/keep-alive/route.ts`, which calls the backend's `/api/health`.
That endpoint executes `SELECT 1`, so the ping reaches the database rather than
just the backend, and it is excluded from rate limiting. The route returns 503
when the backend answers but reports the database as disconnected, because a
reachable backend with a dead database is the failure worth seeing.

Notes:

- Vercel Hobby allows a daily cron at most, and the exact hour is not
  guaranteed. That is sufficient against a 7-day pause.
- Crons only run on production deployments.
- Set `CRON_SECRET` in the Vercel project to stop anyone from triggering the
  route; the handler enforces it whenever the variable exists.
- This is only about Supabase. The Railway backend is on a paid plan and does
  not sleep, so it needs no ping of its own.
- The lightweight `/health` route in `app/main.py` sits inside
  `if __name__ == "__main__":` and therefore never registers under uvicorn;
  `/api/health` is the endpoint that exists in production.

## Configuration

Backend configuration is managed via `app/config.py` using Pydantic settings. Key environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key
- `BGE_MODEL_PATH`: Path to bge-m3 model (default: `./app/ml_models/bge-m3`)
- `RATE_LIMIT_NATURAL_DAILY`: Daily limit for natural mode (default: 50)
- `RATE_LIMIT_NATURAL_MONTHLY`: Monthly limit for natural mode (default: 400)
- `RATE_LIMIT_LISTEN_DAILY`: Daily limit for listen mode (default: 40)
- `RATE_LIMIT_LISTEN_MONTHLY`: Monthly limit for listen mode (default: 200)
- `CORS_ORIGINS`: Comma-separated allowed origins

**Note**: Rate limits are enforced per IP address and tracked separately for each chat mode. Both daily and monthly limits must be satisfied for a request to succeed.

## Anti-Hallucination Strategy

1. **Source Citation Requirement**: LLM must cite every fact with [1], [2], [3]
2. **Semantic Verification**: Compare LLM response embeddings against source embeddings
3. **Confidence Threshold**: 55% similarity, per sentence, and the weakest
  sentence decides. Calibrated with `backend/scripts/calibrate_verifier.py`;
  0.60 rejected half of the true claims.
4. **Fallback**: On verification failure, show at most two portfolio excerpts,
  each shortened to its first sentence and introduced as unverified. The gate
  is calibrated with `backend/scripts/calibrate_excerpts.py`.
5. **Derived values are computed, never stored**: the age comes from
  `contact_info.birth_date` at request time, and the date itself is kept out of
  the evidence the model sees (`document_service.DERIVED_FIELDS`).

Thresholds are measurements against the live corpus with the current embedding
model. Changing the embedding model invalidates both and requires re-running
the two calibration scripts.

## Common Patterns

- **Singleton Pattern**: Embedding service loads model once and reuses it
- **Dependency Injection**: Database sessions injected via FastAPI dependencies
- **Async/Await**: All API endpoints are async for better performance
- **Error Handling**: Comprehensive logging at INFO level by default

## File Locations

- Database schema: `backend/database/supabase-script.sql`
- Technology documentation: `.idea/TechnologieStac.md`
- Architecture diagram: `.idea/diagram.mmd`
- Project structure: `PROJECT_STRUCTURE.md`
- Backend README: `backend/README.md`

