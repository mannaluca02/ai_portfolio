"""Retrieve evidence, generate a short answer, and fail closed before publishing."""
import logging
import re
from time import perf_counter

from sqlalchemy.orm import Session

from app.config import settings
from app.schemas.chat import ChatMode, ChatResponse, SourceReference, VerificationResult
from app.services.generator_service import get_generator_service
from app.services.retriever_service import RetrieverService
from app.services.sentence_service import first_sentence
from app.services.verifier_service import get_verifier_service

logger = logging.getLogger(__name__)
NO_INFORMATION = "Dazu finde ich keine Information in meinen Portfolio-Daten."
# Said before every excerpt list, so an unverified answer is never mistaken for
# a confirmed one. The excerpts are quoted portfolio rows, not a claim that they
# answer the question.
UNVERIFIED_INTRO = ("Dafür habe ich keine geprüfte Antwort. Das kommt deiner Frage "
                    "am nächsten:")
# Presentation gate for those excerpts, measured over the 24 labelled questions
# with scripts/calibrate_excerpts.py. "Right" counts questions whose excerpt
# list contains a row labelled as answering it, "clean" those whose list
# contains nothing else. Re-measured on 2026-09-13 after the corpus was
# re-embedded from the richer row text, which moved every score:
#   floor 0.45, gap 0.07  -> right 15, clean 13, unrelated 3, nothing shown 6
#   floor 0.42, gap 0.03  -> right 18, clean 17, unrelated 3, nothing shown 3
#   floor 0.40, gap 0.03  -> right 19, clean 17, unrelated 4, nothing shown 1
# Re-checked on 2026-09-13 after the languages table was added (27 labelled
# questions): 0.40/0.03 gives right 21, clean 19, unrelated 5, nothing shown 1,
# still the best of the grid, so the values stand.
# 0.40/0.03 recovers the most questions for one more imperfect list. Keeping the
# candidates in the best row's own section is worth +2 clean lists at no cost on
# these vectors (15 -> 17); it was measured as costing recall on the previous
# ones, so it is re-checked whenever the corpus is re-embedded.
EXCERPT_FLOOR = 0.40
EXCERPT_GAP = 0.03
EXCERPT_LIMIT = 2
EXCERPT_CHARS = 170


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
        relevant = self._excerpt_candidates(results)
        if not relevant:
            return self._no_information(mode)
        excerpts = []
        for index, result in enumerate(relevant, 1):
            summary = first_sentence(result.content or "", max_chars=EXCERPT_CHARS)
            excerpts.append(f"• {result.title}: {summary} [{index}]" if summary
                            else f"• {result.title} [{index}]")
        return ChatResponse(answer=f"{UNVERIFIED_INTRO}\n" + "\n".join(excerpts),
                            outcome="source_fallback", sources=self._sources(relevant), mode=mode,
                            confidence=0.0, verification=None, metadata={"results_count": len(results)})

    @staticmethod
    def _excerpt_candidates(results):
        """The few rows worth quoting: strong enough, close to the best one, and
        from the same section, so a job is never listed beside a hobby.

        Rows from a section the question did not ask about are dropped first. A
        damped row can still outscore everything else ("Heim Netzwerk" scores
        0.519 for "Kann er Docker?"), and quoting it answers with the wrong part
        of the portfolio. It remains available to the model as evidence.
        """
        ranked = sorted((result for result in results if not result.off_topic),
                        key=lambda result: result.similarity, reverse=True)
        if not ranked:
            return []
        best = ranked[0]
        return [result for result in ranked
                if result.similarity >= EXCERPT_FLOOR
                and best.similarity - result.similarity <= EXCERPT_GAP
                and result.table == best.table][:EXCERPT_LIMIT]

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
