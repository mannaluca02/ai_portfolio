"""
Verifier Service - Hallucination Detection
Verifies LLM responses against source documents using semantic similarity
"""
from app.services.embedding_service import get_embedding_service
from app.services.retriever_service import SearchResult
from typing import List, Dict, Any
import logging
import numpy as np

logger = logging.getLogger(__name__)


class VerificationResult:
    """Result of verification check"""
    def __init__(self, is_verified: bool, confidence: float, details: List[Dict[str, Any]]):
        self.is_verified = is_verified
        self.confidence = confidence
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "is_verified": self.is_verified,
            "confidence": self.confidence,
            "details": self.details
        }


class VerifierService:
    """Service for verifying LLM responses against source documents"""

    def __init__(self):
        """Initialize verifier service"""
        self.embedding_service = get_embedding_service()
        self.verification_threshold = 0.60  # Minimum similarity for verification

    def verify_response(self, response: str, sources: List[SearchResult]) -> VerificationResult:
        """
        Verify that the LLM response is grounded in source documents

        Args:
            response: Generated LLM response text
            sources: Original source documents used for generation

        Returns:
            VerificationResult: Verification result with confidence score
        """
        try:
            if not response or not response.strip():
                logger.warning("Empty response provided for verification")
                return VerificationResult(
                    is_verified=False,
                    confidence=0.0,
                    details=[{"error": "Empty response"}]
                )

            if not sources:
                logger.warning("No sources provided for verification")
                return VerificationResult(
                    is_verified=False,
                    confidence=0.0,
                    details=[{"error": "No sources provided"}]
                )

            logger.info(f"Verifying response against {len(sources)} sources...")

            # Split response into sentences for granular verification
            sentences = self._split_into_sentences(response)
            logger.info(f"Split response into {len(sentences)} sentences")

            # Verify each sentence
            sentence_results = []
            for sentence in sentences:
                if self._is_citation_or_greeting(sentence):
                    # Skip citations like "[1]" and greetings
                    continue

                result = self._verify_sentence(sentence, sources)
                sentence_results.append(result)

            if not sentence_results:
                # All sentences were citations/greetings
                return VerificationResult(
                    is_verified=True,
                    confidence=1.0,
                    details=[{"info": "Only citations and greetings"}]
                )

            # Calculate overall verification
            verified_count = sum(1 for r in sentence_results if r["is_verified"])
            total_count = len(sentence_results)
            overall_confidence = sum(r["similarity"] for r in sentence_results) / total_count

            is_verified = overall_confidence >= self.verification_threshold

            logger.info(f"Verification: {verified_count}/{total_count} sentences verified")
            logger.info(f"Overall confidence: {overall_confidence:.2%}")

            return VerificationResult(
                is_verified=is_verified,
                confidence=overall_confidence,
                details=sentence_results
            )

        except Exception as e:
            logger.error(f"Verification failed: {e}")
            raise

    def _verify_sentence(self, sentence: str, sources: List[SearchResult]) -> Dict[str, Any]:
        """
        Verify a single sentence against source documents

        Args:
            sentence: Sentence to verify
            sources: Source documents

        Returns:
            Dict with verification result for this sentence
        """
        try:
            # Generate embedding for sentence
            sentence_embedding = self.embedding_service.generate_embedding(sentence)

            # Compare with each source
            max_similarity = 0.0
            best_source = None

            for source in sources:
                # Generate embedding for source content
                source_embedding = self.embedding_service.generate_embedding(source.content)

                # Calculate similarity
                similarity = self.embedding_service.calculate_similarity(
                    sentence_embedding,
                    source_embedding
                )

                if similarity > max_similarity:
                    max_similarity = similarity
                    best_source = source

            is_verified = max_similarity >= self.verification_threshold

            return {
                "sentence": sentence,
                "is_verified": is_verified,
                "similarity": max_similarity,
                "best_match": {
                    "title": best_source.title if best_source else None,
                    "table": best_source.table if best_source else None,
                    "content": best_source.content[:100] + "..." if best_source else None
                }
            }

        except Exception as e:
            logger.error(f"Failed to verify sentence: {e}")
            return {
                "sentence": sentence,
                "is_verified": False,
                "similarity": 0.0,
                "error": str(e)
            }

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Simple sentence splitting (handles German punctuation)
        import re

        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text).strip()

        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Filter out empty sentences and very short ones
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

        return sentences

    def _is_citation_or_greeting(self, sentence: str) -> bool:
        """
        Check if sentence is just a citation or greeting

        Args:
            sentence: Sentence to check

        Returns:
            True if sentence is citation/greeting, False otherwise
        """
        # Check for citations like "[1]", "[1][2]"
        import re
        if re.match(r'^\[[\d,\s\[\]]+\]\.?$', sentence):
            return True

        # Check for very short sentences (likely greetings)
        if len(sentence.split()) <= 3:
            return True

        return False

    def verify_with_threshold(self, response: str, sources: List[SearchResult],
                             threshold: float) -> VerificationResult:
        """
        Verify response with custom threshold

        Args:
            response: Generated response
            sources: Source documents
            threshold: Custom verification threshold

        Returns:
            VerificationResult
        """
        original_threshold = self.verification_threshold
        self.verification_threshold = threshold

        try:
            result = self.verify_response(response, sources)
            return result
        finally:
            self.verification_threshold = original_threshold


# Global instance
_verifier_service = None


def get_verifier_service() -> VerifierService:
    """Get the global verifier service instance"""
    global _verifier_service
    if _verifier_service is None:
        _verifier_service = VerifierService()
    return _verifier_service
