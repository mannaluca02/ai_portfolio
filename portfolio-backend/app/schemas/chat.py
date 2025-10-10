"""
Chat API Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ChatMode(str, Enum):
    """Chat mode enum"""
    LISTEN = "listen"
    NATURAL = "natural"


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., min_length=1, max_length=1000, description="User's question")
    mode: ChatMode = Field(default=ChatMode.NATURAL, description="Chat mode (listen or natural)")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation tracking")

    class Config:
        json_schema_extra = {
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
        json_schema_extra = {
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
        json_schema_extra = {
            "example": {
                "is_verified": True,
                "confidence": 0.72,
                "threshold": 0.60
            }
        }


class ChatResponse(BaseModel):
    """Chat response schema"""
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceReference] = Field(default=[], description="List of source references")
    mode: ChatMode = Field(..., description="Chat mode used")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    verification: Optional[VerificationResult] = Field(None, description="Verification result (only in natural mode)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
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
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
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
    services: Dict[str, str] = Field(..., description="Service statuses")

    class Config:
        json_schema_extra = {
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
