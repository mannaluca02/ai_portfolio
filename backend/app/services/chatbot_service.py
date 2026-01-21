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
import os


logger = logging.getLogger(__name__)


class ChatbotService:
    """Service for handling chatbot requests"""

    def __init__(self, db: Session):
        """Initialize chatbot service with database session"""
        self.db = db
        self.retriever = RetrieverService(db)
        self.generator = get_generator_service()
        self.verifier = get_verifier_service()

    def process_message(
        self, message: str, mode: ChatMode = ChatMode.NATURAL
    ) -> ChatResponse:
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
        Retrieve relevant documents from database with intent-based routing

        Args:
            message: User's question
            mode: Chat mode

        Returns:
            List of search results
        """
        # ADAPTIVE THRESHOLD: Adjust based on query length
        # Short queries need lower thresholds to find results
        base_threshold = 0.3 if mode == ChatMode.LISTEN else 0.35
        threshold = self._get_adaptive_threshold(message, base_threshold)

        # Limit results to avoid overwhelming LLM with too many sources
        # Natural mode: 8 high-quality sources for accurate citations
        # Listen mode: 5 sources for quick response
        limit = 8 if mode == ChatMode.NATURAL else 5

        logger.info(
            f"Retrieving documents (adaptive_threshold={threshold}, limit={limit})..."
        )

        # Retriever automatically detects intent and applies:
        # - Table filtering based on query intent
        # - Boost factors for relevant tables
        # - MMR diversification to reduce redundancy
        search_results = self.retriever.search(
            query=message,
            limit=limit,
            similarity_threshold=threshold,
            use_mmr=True,  # Enable MMR for diverse, non-redundant results
        )

        # Apply quality filter to remove outliers with poor scores
        if search_results and mode == ChatMode.NATURAL:
            search_results = self._filter_by_quality(search_results)

        logger.info(
            f"Retrieved {len(search_results)} documents after quality filtering"
        )

        # FALLBACK: If no results found, try without embedding filter
        if not search_results:
            logger.warning(
                f"No results found with threshold {threshold}. Attempting fallback retrieval..."
            )
            search_results = self._fallback_retrieval(message, mode, limit)

        return search_results

    def _filter_by_quality(self, results: List, max_gap: float = 0.25) -> List:
        """
        Filter results to remove low-quality outliers

        Removes results that are:
        1. More than max_gap (25%) below the top result
        2. Creating a large quality gap from previous result

        Args:
            results: Sorted list of search results (best first)
            max_gap: Maximum allowed similarity gap from top result

        Returns:
            Filtered list of high-quality results
        """
        if not results or len(results) <= 1:
            return results

        top_score = results[0].similarity
        filtered = [results[0]]  # Always keep the top result

        for i, result in enumerate(results[1:], 1):
            # Calculate gap from top result
            gap_from_top = top_score - result.similarity

            # Reject if too far below top result
            if gap_from_top > max_gap:
                logger.info(
                    f"Filtering out result {i+1}/{len(results)}: {result.title} "
                    f"(similarity: {result.similarity:.2%}, gap from top: {gap_from_top:.2%})"
                )
                continue

            filtered.append(result)

        logger.info(f"Quality filter: kept {len(filtered)}/{len(results)} results")
        return filtered

    def _get_adaptive_threshold(self, query: str, base_threshold: float) -> float:
        """
        Calculate adaptive similarity threshold based on query length

        Short/generic queries get lower thresholds to ensure results are found.
        Longer/specific queries maintain higher thresholds for precision.

        Args:
            query: User's question
            base_threshold: Base threshold for this mode

        Returns:
            float: Adjusted threshold (0.15 - base_threshold)
        """
        word_count = len(query.split())

        if word_count <= 3:
            # Very short queries: "Welche Projekte", "Wer ist Luca"
            adjusted = 0.15
            logger.info(
                f"Short query ({word_count} words): lowering threshold to {adjusted}"
            )
            return adjusted
        elif word_count <= 6:
            # Medium queries: lower threshold moderately
            adjusted = max(0.20, base_threshold - 0.10)
            logger.info(
                f"Medium query ({word_count} words): adjusting threshold to {adjusted}"
            )
            return adjusted
        else:
            # Long queries: use base threshold
            logger.info(
                f"Long query ({word_count} words): using base threshold {base_threshold}"
            )
            return base_threshold

    def _fallback_retrieval(self, message: str, mode: ChatMode, limit: int) -> List:
        """
        Fallback retrieval strategy when semantic search returns no results.
        Fetches top N entries from each relevant table without embedding filter.

        Args:
            message: User's question
            mode: Chat mode
            limit: Number of results per table

        Returns:
            List of search results from database
        """
        logger.info("Executing fallback retrieval without embedding filter...")

        # Detect intent to know which tables to query
        from app.services.intent_service import get_intent_service

        intent_service = get_intent_service()
        intent = intent_service.detect_intent(message)

        fallback_results = []

        # Fetch recent/top entries from each intent table
        for table_name in intent.tables[:3]:  # Limit to top 3 most relevant tables
            try:
                results = self.retriever.get_fallback_results(
                    table_name=table_name, limit=min(3, limit)  # Max 3 per table
                )
                fallback_results.extend(results)
                logger.info(
                    f"Fallback: Retrieved {len(results)} results from {table_name}"
                )
            except Exception as e:
                logger.warning(f"Fallback failed for table {table_name}: {e}")
                continue

        if fallback_results:
            logger.info(
                f"✅ Fallback retrieval found {len(fallback_results)} total results"
            )
        else:
            logger.warning("❌ Fallback retrieval found no results")

        return fallback_results

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
                "top_similarity": top_result.similarity,
            },
        )

    def _create_natural_response(
        self, message: str, search_results: List
    ) -> ChatResponse:
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

        # Verify response (skip if disabled for performance)
        if os.getenv("SKIP_VERIFICATION", "false").lower() == "true":
            logger.info("Verification skipped (SKIP_VERIFICATION=true)")
            verification_result = type(
                "obj",
                (object,),
                {"is_verified": True, "confidence": 0.8, "details": []},
            )()
        else:
            logger.info("Verifying response...")
            verification_result = self.verifier.verify_response(
                generation_result["answer"], search_results
            )

        # Check if LLM indicated no relevant information found
        # If so, don't show sources (they are irrelevant/low quality)
        answer = generation_result["answer"]
        no_info_indicators = [
            "keine information",
            "keine relevanten informationen",
            "nichts gefunden",
            "dazu finde ich keine",
            "kann ich keine information",
        ]

        has_no_info = any(
            indicator in answer.lower() for indicator in no_info_indicators
        )

        # Convert sources only if relevant information was found
        sources = (
            []
            if has_no_info
            else self._convert_sources_from_dict(generation_result["sources"])
        )

        # Create verification result
        # If no info was found, set verification to None and confidence to 0
        if has_no_info:
            verification = None
            confidence = 0.0
            logger.info(
                "No relevant information found - suppressing sources and verification"
            )
        else:
            verification = VerificationResult(
                is_verified=verification_result.is_verified,
                confidence=verification_result.confidence,
                threshold=0.30,
            )
            confidence = generation_result["confidence"]

        # Build metadata
        metadata = {
            "model": generation_result.get("model"),
            "tokens_used": generation_result.get("tokens_used"),
            "results_count": len(search_results),
            "verification_sentences": (
                len(verification_result.details) if verification_result.details else 0
            ),
            "no_info_detected": has_no_info,
        }

        return ChatResponse(
            answer=generation_result["answer"],
            sources=sources,
            mode=ChatMode.NATURAL,
            confidence=confidence,
            verification=verification,
            metadata=metadata,
        )

    def _create_no_results_response(self, mode: ChatMode) -> ChatResponse:
        """
        Create response when no documents are found

        Args:
            mode: Chat mode

        Returns:
            ChatResponse with no results message
        """
        answer = (
            "Ich habe leider keine relevanten Informationen zu deiner Frage gefunden."
        )

        return ChatResponse(
            answer=answer,
            sources=[],
            mode=mode,
            confidence=0.0,
            verification=None,
            metadata={"results_count": 0},
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
            sources.append(
                SourceReference(
                    index=i,
                    title=result.title,
                    table=result.table,
                    slug=result.slug,
                    section=result.section,
                    anchor=result.anchor,
                    similarity=result.similarity,
                )
            )
        return sources

    def _convert_sources_from_dict(
        self, source_dicts: List[Dict[str, Any]]
    ) -> List[SourceReference]:
        """
        Convert source dictionaries to SourceReference objects

        Args:
            source_dicts: List of source dictionaries from generator

        Returns:
            List of SourceReference objects
        """
        sources = []
        for source_dict in source_dicts:
            sources.append(
                SourceReference(
                    index=source_dict["index"],
                    title=source_dict["title"],
                    table=source_dict["table"],
                    slug=source_dict["slug"],
                    section=source_dict["section"],
                    anchor=source_dict["anchor"],
                    similarity=source_dict["similarity"],
                )
            )
        return sources


def get_chatbot_service(db: Session) -> ChatbotService:
    """Get chatbot service instance"""
    return ChatbotService(db)
