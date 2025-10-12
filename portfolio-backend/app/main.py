from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import chat, health, contact, social, work, project, skill, certificate, education
from app.middleware.rate_limiter import PathBasedRateLimiter
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Portfolio RAG Chatbot API",
    description="Backend API für Portfolio mit RAG-basiertem Chatbot",
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware (path-specific)
app.add_middleware(
    PathBasedRateLimiter,
    limits={
        "/api/chat": (settings.RATE_LIMIT_NATURAL_MODE, 5),  # Natural mode: 10 req/min, burst 5
    }
)

# Include routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(contact.router)
app.include_router(social.router)
app.include_router(work.router)
app.include_router(project.router)
app.include_router(skill.router)
app.include_router(certificate.router)
app.include_router(education.router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting Portfolio RAG Chatbot API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down Portfolio RAG Chatbot API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
