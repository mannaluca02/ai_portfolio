"""Conservative citation and similarity checks, not a proof of factual truth."""
import re
from typing import Any

import numpy as np

from app.config import settings
from app.services.embedding_service import get_embedding_service
from app.services.retriever_service import SearchResult

CITATION = re.compile(r"\[(\d+)\]")
NEGATION = re.compile(r"\b(?:nicht|nie|niemals|kein\w*|ohne|not|never|no|without)\b", re.IGNORECASE)
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
WORD = re.compile(r"[^\W\d_]+(?:[+#]+)?", re.UNICODE)


class VerificationResult:
    def __init__(self, is_verified: bool, confidence: float, details: list[dict[str, Any]]):
        self.is_verified = is_verified
        self.confidence = confidence
        self.details = details

    def to_dict(self):
        return vars(self)


class VerifierService:
    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.verification_threshold = settings.VERIFICATION_THRESHOLD

    def verify_response(self, response: str, sources: list[SearchResult], *, threshold=None):
        threshold = self.verification_threshold if threshold is None else threshold
        if not response or not sources:
            return VerificationResult(False, 0.0, [{"error": "Missing answer or sources"}])
        sentences = self._split_into_sentences(response)
        if not sentences:
            return VerificationResult(False, 0.0, [{"error": "No factual statements"}])
        evidence = [source.evidence_text() for source in sources]
        claims = []
        for sentence in sentences:
            indices = [int(n) for n in CITATION.findall(sentence)]
            claim = CITATION.sub("", sentence).strip(" .!?•*-\t")
            if (not indices or not claim or any(i < 1 or i > len(sources) for i in indices)
                    or "[" in claim or "]" in claim
                    or not re.search(r"\[\d+\][.!?]*$", sentence)):
                return VerificationResult(False, 0.0, [{"error": "Invalid or missing citation"}])
            claims.append((claim, indices))

        # One batch, deduplicated by exact text. Retrieval vectors encode different
        # text and must not be substituted for verification embeddings.
        texts = list(dict.fromkeys([c for c, _ in claims] + evidence))
        vectors = self.embedding_service.generate_embeddings(texts)
        if len(vectors) != len(texts):
            return VerificationResult(False, 0.0, [{"error": "Incomplete embeddings"}])
        lookup = dict(zip(texts, vectors))
        details = []
        for claim, indices in claims:
            scores = []
            for index in indices:
                source_text = evidence[index - 1]
                if not self._facts_match(claim, source_text):
                    continue
                a, b = lookup[claim], lookup[source_text]
                denominator = np.linalg.norm(a) * np.linalg.norm(b)
                score = float(np.dot(a, b) / denominator) if denominator else 0.0
                if np.isfinite(score):
                    scores.append(max(0.0, min(1.0, score)))
            similarity = max(scores, default=0.0)
            details.append({"sentence": claim, "similarity": similarity,
                            "is_verified": similarity >= threshold})
        # A high average cannot hide even one unsupported statement.
        return VerificationResult(all(d["is_verified"] for d in details),
                                  min(d["similarity"] for d in details), details)

    @staticmethod
    def _facts_match(claim: str, evidence: str) -> bool:
        if not set(NUMBER.findall(claim)) <= set(NUMBER.findall(evidence)):
            return False
        if bool(NEGATION.search(claim)) != bool(NEGATION.search(evidence)):
            return False
        # Conservative entity check. German capitalised nouns can cause a safe
        # fallback. This heuristic does not establish logical entailment.
        evidence_words = {word.casefold() for word in WORD.findall(evidence)}
        for word in WORD.findall(claim):
            if (word[0].isupper() and word not in {"Luca", "Er", "Seine", "Sein", "Die", "Der", "Das"}
                    and word.casefold() not in evidence_words):
                return False
        return True

    @staticmethod
    def _split_into_sentences(text: str) -> list[str]:
        # Accept both "sentence [1]." and "sentence. [1]". Never discard a short
        # factual statement such as "Luca ist Arzt" as if it were a greeting.
        text = re.sub(r"([.!?])\s*((?:\[\d+\]\s*)+)", r" \2\1 ", text)
        return [part.strip().lstrip("•*- ") for part in re.split(r"(?<=[.!?])\s+|\n+", text)
                if part.strip().lstrip("•*- ")]

    def verify_with_threshold(self, response, sources, threshold):
        return self.verify_response(response, sources, threshold=threshold)


_verifier_service = None


def get_verifier_service():
    global _verifier_service
    if _verifier_service is None:
        _verifier_service = VerifierService()
    return _verifier_service
