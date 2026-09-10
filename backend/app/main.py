import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from app.api import (
    certificate,
    chat,
    contact,
    education,
    health,
    project,
    skill,
    social,
    work,
)
from app.config import settings
from app.middleware.rate_limiter import DailyMonthlyRateLimiter
from app.services.embedding_service import get_embedding_service
from app.services.generator_service import get_generator_service
from app.services.verifier_service import get_verifier_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
    openapi_url="/openapi.json",
)
app.state.chat_ready = False

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware (daily/monthly limits per mode)
app.add_middleware(
    DailyMonthlyRateLimiter,
    mode_limits={
        "natural": {
            "daily": settings.RATE_LIMIT_NATURAL_DAILY,
            "monthly": settings.RATE_LIMIT_NATURAL_MONTHLY,
        },
        "listen": {
            "daily": settings.RATE_LIMIT_LISTEN_DAILY,
            "monthly": settings.RATE_LIMIT_LISTEN_MONTHLY,
        },
    },
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
    app.state.chat_ready = False

    def warm_up():
        get_embedding_service().generate_embedding("Portfolio")
        get_generator_service()
        get_verifier_service()

    await run_in_threadpool(warm_up)
    app.state.chat_ready = True
    logger.info("Chat model loaded and warmed; ready for requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down Portfolio RAG Chatbot API...")


if __name__ == "__main__":

    @app.get("/health")
    def health():
        return {"status": "ok"}

    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
