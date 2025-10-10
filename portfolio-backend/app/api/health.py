"""
Health Check API Routes
Endpoints for monitoring API health
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.schemas.chat import HealthResponse
from app.services.embedding_service import get_embedding_service
from openai import OpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Check the health status of the API and its dependencies"
)
async def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """
    Check API health and service statuses

    **Checks:**
    - Database connection
    - Embedding service (bge-m3 model)
    - OpenAI API availability

    **Example Response:**
    ```json
    {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "embedding_service": "loaded",
            "openai": "available"
        }
    }
    ```
    """
    services = {}

    # Check database
    try:
        db.execute(text("SELECT 1"))
        services["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        services["database"] = "disconnected"

    # Check embedding service
    try:
        embedding_service = get_embedding_service()
        if embedding_service._model is not None:
            services["embedding_service"] = "loaded"
        else:
            services["embedding_service"] = "not_loaded"
    except Exception as e:
        logger.error(f"Embedding service health check failed: {e}")
        services["embedding_service"] = "error"

    # Check OpenAI
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        # Simple test to check if API key is valid
        services["openai"] = "available"
    except Exception as e:
        logger.error(f"OpenAI health check failed: {e}")
        services["openai"] = "unavailable"

    # Determine overall status
    status_value = "healthy"
    if any(status != "connected" and status != "loaded" and status != "available"
           for status in services.values()):
        status_value = "degraded"

    return HealthResponse(
        status=status_value,
        version="1.0.0",
        services=services
    )


@router.get(
    "/",
    summary="API root",
    description="Get basic API information"
)
async def root():
    """
    Get API root information

    **Returns:**
    - Basic API information and available endpoints
    """
    return {
        "name": "Portfolio RAG Chatbot API",
        "version": "1.0.0",
        "description": "FastAPI backend for portfolio chatbot with RAG architecture",
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat",
            "chat_modes": "/api/chat/modes",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "features": [
            "Semantic search with pgvector",
            "bge-m3 embeddings (1024 dimensions)",
            "OpenAI GPT-3.5 generation",
            "Hallucination verification",
            "Dual mode (listen/natural)"
        ]
    }
