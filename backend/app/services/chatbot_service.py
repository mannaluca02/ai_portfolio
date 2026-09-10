"""Retrieve evidence, generate a short answer, and fail closed before publishing."""
import logging
import re
from time import perf_counter

from sqlalchemy.orm import Session

from app.config import settings
from app.schemas.chat import ChatMode, ChatResponse, SourceReference, VerificationResult
from app.services.generator_service import get_generator_service
from app.services.retriever_service import RetrieverService
from app.services.verifier_service import get_verifier_service

logger = logging.getLogger(__name__)
NO_INFORMATION = "Dazu finde ich keine Information in meinen Portfolio-Daten."


class ChatbotService:
    def __init__(self, db: Session):
        self.retriever = RetrieverService(db)
        self.generator = get_generator_service()
        self.verifier = get_verifier_service()

    def process_message(self, message: str, mode: ChatMode = ChatMode.NATURAL) -> ChatResponse:
        start = perf_counter()
        timings = {"retrieval": 0, "generation": 0, "verification": 0}
        results = self._retrieve_documents(message, mode)
        timings["retrieval"] = round((perf_counter() - start) * 1000)
        if not results:
            response = self._no_information(mode)
        elif mode == ChatMode.LISTEN or settings.SKIP_VERIFICATION:
            # The legacy performance setting now selects safe excerpts.
            response = self._source_fallback(results, mode)
        else:
            response = self._natural_response(message, results, timings)
        response.metadata = {**(response.metadata or {}), "timings_ms": timings,
                             "processing_time_ms": round((perf_counter() - start) * 1000)}
        logger.info("Chat outcome=%s timings_ms=%s", response.outcome, timings)
        return response

    def _retrieve_documents(self, message, mode):
        # Preserve recall but never fill an empty search with unrelated recent rows.
        words = len(message.split())
        base = 0.3 if mode == ChatMode.LISTEN else 0.35
        threshold = 0.15 if words <= 3 else max(0.2, base - 0.1) if words <= 6 else base
        results = self.retriever.search(query=message, limit=8 if mode == ChatMode.NATURAL else 5,
                                        similarity_threshold=threshold, use_mmr=True)
        if not results:
            return []
        top = max(result.similarity for result in results)
        return [result for result in results if top - result.similarity <= 0.25]

    def _natural_response(self, message, results, timings):
        started = perf_counter()
        try:
            generated = self.generator.generate_response(message, results)
        except Exception:
            logger.warning("Generation unavailable; using source excerpts", exc_info=True)
            return self._source_fallback(results, ChatMode.NATURAL)
        finally:
            timings["generation"] = round((perf_counter() - started) * 1000)

        answer = generated.get("answer", "").strip()
        if not answer or generated.get("finish_reason") != "stop":
            return self._source_fallback(results, ChatMode.NATURAL)
        if answer == NO_INFORMATION:
            return self._no_information(ChatMode.NATURAL)

        started = perf_counter()
        try:
            checked = self.verifier.verify_response(answer, results)
        except Exception:
            logger.warning("Verification unavailable; using source excerpts", exc_info=True)
            return self._source_fallback(results, ChatMode.NATURAL)
        finally:
            timings["verification"] = round((perf_counter() - started) * 1000)
        if not checked.is_verified:
            return self._source_fallback(results, ChatMode.NATURAL)

        cited = {int(n) for n in re.findall(r"\[(\d+)\]", answer)}
        return ChatResponse(answer=answer, outcome="answered", mode=ChatMode.NATURAL,
                            sources=[s for s in self._sources(results) if s.index in cited],
                            confidence=checked.confidence,
                            verification=VerificationResult(is_verified=True, confidence=checked.confidence,
                                                            threshold=settings.VERIFICATION_THRESHOLD),
                            metadata={"model": generated.get("model"), "tokens_used": generated.get("tokens_used"),
                                      "results_count": len(results)})

    def _source_fallback(self, results, mode):
        # Related entries are never presented as confirmation of the question's premise.
        relevant = [r for r in results if r.similarity >= 0.45][:3]
        if not relevant:
            return self._no_information(mode)
        excerpts = [f"• {r.title}: {r.content} [{i}]" for i, r in enumerate(relevant, 1)]
        return ChatResponse(answer="Hier sind passende Einträge aus meinem Portfolio:\n" + "\n".join(excerpts),
                            outcome="source_fallback", sources=self._sources(relevant), mode=mode,
                            confidence=0.0, verification=None, metadata={"results_count": len(results)})

    @staticmethod
    def _no_information(mode):
        return ChatResponse(answer=NO_INFORMATION, outcome="no_information", sources=[], mode=mode,
                            confidence=0.0, verification=None, metadata={"results_count": 0})

    @staticmethod
    def _sources(results):
        return [SourceReference(index=i, title=r.title, table=r.table, slug=r.slug,
                                section=r.section, anchor=r.anchor, similarity=r.similarity)
                for i, r in enumerate(results, 1)]


def get_chatbot_service(db):
    return ChatbotService(db)
