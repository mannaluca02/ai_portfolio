"""
Chat API Schemas
Pydantic models for request/response validation
"""
from enum import Enum
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, Field


class ChatMode(str, Enum):
    """Chat mode enum"""
    LISTEN = "listen"
    NATURAL = "natural"


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., min_length=1, max_length=1000, description="User's question")
    mode: ChatMode = Field(default=ChatMode.NATURAL, description="Chat mode (listen or natural)")
    session_id: str | None = Field(None, description="Optional session ID for conversation tracking")

    class Config:
        json_schema_extra: ClassVar[dict[str, Any]] = {
            "example": {
                "message": "Welche Python Erfahrung hat Luca?",
                "mode": "natural",
                "session_id": "abc-123"
            }
        }


class SourceReference(BaseModel):
    """Source reference schema"""
    index: int = Field(..., description="Citation index [1], [2], etc.")
    title: str = Field(..., description="Source title")
    table: str = Field(..., description="Database table name")
    slug: str = Field(..., description="Frontend route slug")
    section: str = Field(..., description="Page section")
    anchor: str = Field(..., description="HTML anchor ID")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score (0-1)")

    class Config:
        json_schema_extra: ClassVar[dict[str, Any]] = {
            "example": {
                "index": 1,
                "title": "Python",
                "table": "skills",
                "slug": "skills",
                "section": "skills",
                "anchor": "skill-python",
                "similarity": 0.85
            }
        }


class VerificationResult(BaseModel):
    """Verification result schema"""
    is_verified: bool = Field(..., description="Whether response passed verification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    threshold: float = Field(..., ge=0.0, le=1.0, description="Verification threshold used")

    class Config:
        json_schema_extra: ClassVar[dict[str, Any]] = {
            "example": {
                "is_verified": True,
                "confidence": 0.72,
                "threshold": 0.60
            }
        }


class ChatResponse(BaseModel):
    """Chat response schema"""
    answer: str = Field(..., description="Generated answer")
    outcome: Literal["answered", "source_fallback", "no_information"] = "answered"
    sources: list[SourceReference] = Field(default_factory=list, description="List of source references")
    mode: ChatMode = Field(..., description="Chat mode used")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    verification: VerificationResult | None = Field(None, description="Verification result (only in natural mode)")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra: ClassVar[dict[str, Any]] = {
            "example": {
                "answer": "Luca hat 8 Jahre Erfahrung mit Python [1] und nutzt es für Backend-Entwicklung [2].",
                "sources": [
                    {
                        "index": 1,
                        "title": "Python",
                        "table": "skills",
                        "slug": "skills",
                        "section": "skills",
                        "anchor": "skill-python",
                        "similarity": 0.85
                    }
                ],
                "mode": "natural",
                "confidence": 0.75,
                "verification": {
                    "is_verified": True,
                    "confidence": 0.72,
                    "threshold": 0.60
                },
                "metadata": {
                    "model": "gpt-3.5-turbo",
                    "tokens_used": 150,
                    "processing_time_ms": 1250
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")

    class Config:
        json_schema_extra: ClassVar[dict[str, Any]] = {
            "example": {
                "error": "RateLimitExceeded",
                "message": "Rate limit exceeded. Please try again later.",
                "details": {
                    "retry_after": 60
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    services: dict[str, str] = Field(..., description="Service statuses")

    class Config:
        json_schema_extra: ClassVar[dict[str, Any]] = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "services": {
                    "database": "connected",
                    "embedding_service": "loaded",
                    "openai": "available"
                }
            }
        }
