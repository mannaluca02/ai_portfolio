"""
Chat API Routes
Endpoints for chatbot interactions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ErrorResponse, ChatMode
from app.services.chatbot_service import get_chatbot_service, ChatbotService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the chatbot",
    description="Process a user message and get an AI-generated response with sources",
    responses={
        200: {
            "description": "Successful response",
            "model": ChatResponse
        },
        400: {
            "description": "Bad request",
            "model": ErrorResponse
        },
        429: {
            "description": "Rate limit exceeded",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Process a chat message and return a response

    **Modes:**
    - `listen`: Fast mode, returns top search result directly (no LLM)
    - `natural`: Full RAG mode with LLM generation and verification

    **Example Request:**
    ```json
    {
        "message": "Welche Python Erfahrung hat Luca?",
        "mode": "natural",
        "session_id": "abc-123"
    }
    ```

    **Example Response:**
    ```json
    {
        "answer": "Luca hat 8 Jahre Erfahrung mit Python [1]...",
        "sources": [...],
        "mode": "natural",
        "confidence": 0.75,
        "verification": {...},
        "metadata": {...}
    }
    ```
    """
    try:
        # Validate message
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )

        # Get chatbot service
        chatbot = get_chatbot_service(db)

        # Process message
        response = chatbot.process_message(
            message=request.message.strip(),
            mode=request.mode
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get(
    "/modes",
    summary="Get available chat modes",
    description="Returns information about available chat modes"
)
async def get_chat_modes():
    """
    Get available chat modes

    **Returns:**
    - Information about listen and natural modes
    """
    return {
        "modes": [
            {
                "name": "listen",
                "description": "Fast mode - returns top search result directly without LLM generation",
                "features": [
                    "Quick response time",
                    "No API costs",
                    "Direct document retrieval"
                ],
                "use_cases": [
                    "Quick information lookup",
                    "Testing semantic search",
                    "Preview of relevant content"
                ]
            },
            {
                "name": "natural",
                "description": "Full RAG mode - uses LLM for natural language generation with verification",
                "features": [
                    "Natural language responses",
                    "Multi-document synthesis",
                    "Source citations [1], [2], [3]",
                    "Hallucination detection",
                    "Verification score"
                ],
                "use_cases": [
                    "Conversational interactions",
                    "Complex questions",
                    "Production chatbot"
                ]
            }
        ]
    }
