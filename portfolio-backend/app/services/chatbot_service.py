"""
Chatbot Service - Orchestrates all RAG services
Coordinates retrieval, generation, and verification
"""
from sqlalchemy.orm import Session
from app.services.retriever_service import RetrieverService
from app.services.generator_service import get_generator_service
from app.services.verifier_service import get_verifier_service
from app.schemas.chat import ChatMode, ChatResponse, SourceReference, VerificationResult
from typing import List, Dict, Any
import logging
import time

logger = logging.getLogger(__name__)


class ChatbotService:
    """Service for handling chatbot requests"""

    def __init__(self, db: Session):
        """Initialize chatbot service with database session"""
        self.db = db
        self.retriever = RetrieverService(db)
        self.generator = get_generator_service()
        self.verifier = get_verifier_service()

    def process_message(self, message: str, mode: ChatMode = ChatMode.NATURAL) -> ChatResponse:
        """
        Process a user message and generate a response

        Args:
            message: User's question
            mode: Chat mode (listen or natural)

        Returns:
            ChatResponse: Complete chat response with answer, sources, and metadata
        """
        start_time = time.time()

        try:
            logger.info(f"Processing message in {mode} mode: {message[:50]}...")

            # Step 1: Retrieve relevant documents
            search_results = self._retrieve_documents(message, mode)

            if not search_results:
                return self._create_no_results_response(mode)

            # Step 2: Generate response based on mode
            if mode == ChatMode.LISTEN:
                # Listen mode: Return top result directly
                response = self._create_listen_response(search_results)
            else:
                # Natural mode: Generate with LLM
                response = self._create_natural_response(message, search_results)

            # Add processing time to metadata
            processing_time = int((time.time() - start_time) * 1000)
            if response.metadata:
                response.metadata["processing_time_ms"] = processing_time
            else:
                response.metadata = {"processing_time_ms": processing_time}

            logger.info(f"✅ Response generated in {processing_time}ms")
            return response

        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            raise

    def _retrieve_documents(self, message: str, mode: ChatMode) -> List:
        """
        Retrieve relevant documents from database

        Args:
            message: User's question
            mode: Chat mode

        Returns:
            List of search results
        """
        # Use lower threshold in listen mode for more results
        threshold = 0.3 if mode == ChatMode.LISTEN else 0.3
        limit = 10 if mode == ChatMode.NATURAL else 5

        logger.info(f"Retrieving documents (threshold={threshold}, limit={limit})...")

        search_results = self.retriever.search(
            query=message,
            limit=limit,
            similarity_threshold=threshold
        )

        logger.info(f"Retrieved {len(search_results)} documents")
        return search_results

    def _create_listen_response(self, search_results: List) -> ChatResponse:
        """
        Create response in listen mode (fast, no LLM)

        Args:
            search_results: Retrieved documents

        Returns:
            ChatResponse in listen mode
        """
        # Get top result
        top_result = search_results[0]

        # Format answer from top result
        answer = f"{top_result.title}: {top_result.content}"

        # Convert sources
        sources = self._convert_sources(search_results[:3])  # Top 3 sources

        return ChatResponse(
            answer=answer,
            sources=sources,
            mode=ChatMode.LISTEN,
            confidence=top_result.similarity,
            verification=None,
            metadata={
                "results_count": len(search_results),
                "top_similarity": top_result.similarity
            }
        )

    def _create_natural_response(self, message: str, search_results: List) -> ChatResponse:
        """
        Create response in natural mode (with LLM generation and verification)

        Args:
            message: User's question
            search_results: Retrieved documents

        Returns:
            ChatResponse in natural mode
        """
        # Generate response with LLM
        logger.info("Generating response with LLM...")
        generation_result = self.generator.generate_response(message, search_results)

        # Verify response
        logger.info("Verifying response...")
        verification_result = self.verifier.verify_response(
            generation_result["answer"],
            search_results
        )

        # Convert sources
        sources = self._convert_sources_from_dict(generation_result["sources"])

        # Create verification result
        verification = VerificationResult(
            is_verified=verification_result.is_verified,
            confidence=verification_result.confidence,
            threshold=0.60
        )

        # Build metadata
        metadata = {
            "model": generation_result.get("model"),
            "tokens_used": generation_result.get("tokens_used"),
            "results_count": len(search_results),
            "verification_sentences": len(verification_result.details) if verification_result.details else 0
        }

        return ChatResponse(
            answer=generation_result["answer"],
            sources=sources,
            mode=ChatMode.NATURAL,
            confidence=generation_result["confidence"],
            verification=verification,
            metadata=metadata
        )

    def _create_no_results_response(self, mode: ChatMode) -> ChatResponse:
        """
        Create response when no documents are found

        Args:
            mode: Chat mode

        Returns:
            ChatResponse with no results message
        """
        answer = "Ich habe leider keine relevanten Informationen zu deiner Frage gefunden."

        return ChatResponse(
            answer=answer,
            sources=[],
            mode=mode,
            confidence=0.0,
            verification=None,
            metadata={"results_count": 0}
        )

    def _convert_sources(self, search_results: List) -> List[SourceReference]:
        """
        Convert search results to source references

        Args:
            search_results: List of SearchResult objects

        Returns:
            List of SourceReference objects
        """
        sources = []
        for i, result in enumerate(search_results, 1):
            sources.append(SourceReference(
                index=i,
                title=result.title,
                table=result.table,
                slug=result.slug,
                section=result.section,
                anchor=result.anchor,
                similarity=result.similarity
            ))
        return sources

    def _convert_sources_from_dict(self, source_dicts: List[Dict[str, Any]]) -> List[SourceReference]:
        """
        Convert source dictionaries to SourceReference objects

        Args:
            source_dicts: List of source dictionaries from generator

        Returns:
            List of SourceReference objects
        """
        sources = []
        for source_dict in source_dicts:
            sources.append(SourceReference(
                index=source_dict["index"],
                title=source_dict["title"],
                table=source_dict["table"],
                slug=source_dict["slug"],
                section=source_dict["section"],
                anchor=source_dict["anchor"],
                similarity=source_dict["similarity"]
            ))
        return sources


def get_chatbot_service(db: Session) -> ChatbotService:
    """Get chatbot service instance"""
    return ChatbotService(db)
