# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A digital portfolio website with an integrated RAG (Retrieval-Augmented Generation) chatbot. The chatbot can answer questions about portfolio content using semantic search and LLM-powered responses.

**Goal:** Create a portfolio that showcases work experience, projects, skills, and certificates, with an intelligent chatbot that can answer visitor questions about the portfolio owner's background.

## Architecture

This is a full-stack application with:

- **Frontend**: Next.js 14+ (App Router) with TypeScript and Tailwind CSS
- **Backend**: FastAPI (Python 3.13+) with RAG-based chatbot
- **Database**: PostgreSQL with pgvector extension (hosted on Supabase)
- **ML Models**: bge-m3 (1024-dim embeddings), OpenAI GPT-3.5 Turbo

### Key Components

**Backend** (`portfolio-backend/`):
- **API Layer** (`app/api/`): REST endpoints for chatbot and health checks
- **Services** (`app/services/`):
  - `embedding_service.py`: Generates embeddings using bge-m3 model
  - `retriever_service.py`: Semantic search via pgvector
  - `generator_service.py`: LLM response generation with strict source citation
  - `verifier_service.py`: Anti-hallucination verification
  - `chatbot_service.py`: Orchestrates the RAG pipeline
- **Models** (`app/models/`): SQLAlchemy ORM models for all portfolio data
- **Middleware** (`app/middleware/`): Rate limiting and CORS
- **Database** (`app/database/`): Connection management and session handling

**Database Structure**:
All tables include:
- `embedding VECTOR(1024)`: For semantic search
- `slug`, `section`, `anchor`: For deterministic deep-linking
- Standard timestamps

Main tables: `work_experiences`, `projects`, `skills`, `certificates`, `education`, `hobbies`, `contact_info`, `social_links`

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

**Critical**: Always reference `portfolio-backend/database/supabase-script.sql` to understand the database schema. This is the single source of truth for:
- Table structures
- ENUMs (employment_type, project_type, skill_level, etc.)
- Vector indices
- Triggers for automatic timestamp updates

The database uses PostgreSQL with pgvector extension for efficient similarity search.

## Development Commands

### Backend Setup and Development

```bash
# Navigate to backend directory
cd portfolio-backend

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
# Test individual components (from portfolio-backend/)
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
psql -f portfolio-backend/database/supabase-script.sql

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

- **Natural Mode**: 10 requests per day per IP
- **Listen Mode**: 40 requests per day per IP
- **Token Limit**: Max 300 tokens per LLM response
- Implementation: Path-based rate limiting in `app/middleware/rate_limiter.py`

## Key Technologies

- **Embeddings**: BAAI/bge-m3 (multilingual, 1024 dimensions)
- **Vector Search**: pgvector with HNSW indices
- **LLM**: OpenAI GPT-3.5 Turbo with strict source citation requirements
- **ORM**: SQLAlchemy 2.0
- **API Framework**: FastAPI 0.118.2
- **Deployment**: Backend on Railway/Render, Database on Supabase, Frontend planned for Vercel

## Configuration

Backend configuration is managed via `app/config.py` using Pydantic settings. Key environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key
- `BGE_MODEL_PATH`: Path to bge-m3 model (default: `./app/ml_models/bge-m3`)
- `RATE_LIMIT_NATURAL_MODE`: Rate limit for natural mode (default: 10)
- `RATE_LIMIT_LISTEN_MODE`: Rate limit for listen mode (default: 40)
- `CORS_ORIGINS`: Comma-separated allowed origins

## Anti-Hallucination Strategy

1. **Source Citation Requirement**: LLM must cite every fact with [1], [2], [3]
2. **Semantic Verification**: Compare LLM response embeddings against source embeddings
3. **Confidence Threshold**: 60% similarity required to accept response
4. **Fallback**: On verification failure, return raw sources (Listen Mode)

## Common Patterns

- **Singleton Pattern**: Embedding service loads model once and reuses it
- **Dependency Injection**: Database sessions injected via FastAPI dependencies
- **Async/Await**: All API endpoints are async for better performance
- **Error Handling**: Comprehensive logging at INFO level by default

## File Locations

- Database schema: `portfolio-backend/database/supabase-script.sql`
- Technology documentation: `.idea/TechnologieStac.md`
- Architecture diagram: `.idea/diagram.mmd`
- Project structure: `PROJECT_STRUCTURE.md`
- Backend README: `portfolio-backend/README.md`
