from unittest.mock import Mock

import numpy as np
import pytest
from app.config import settings
from app.schemas.chat import ChatMode
from app.services.chatbot_service import ChatbotService
from app.services.retriever_service import SearchResult
from app.services.verifier_service import VerificationResult, VerifierService


@pytest.fixture
def sources():
    return [SearchResult(1, "projects", "Python Projekt", "Luca nutzt Python seit 2020.",
                         "python", "projects", "python", 0.85, {"technologies": ["Python"]}),
            SearchResult(2, "work_experiences", "React Arbeit", "Luca nutzt React.",
                         "react", "experience", "react", 0.8, {})]


@pytest.fixture
def verifier():
    service = VerifierService.__new__(VerifierService)
    service.verification_threshold = 0.6
    service.embedding_service = Mock()
    service.embedding_service.generate_embedding.return_value = np.array([1.0, 0.0])
    service.embedding_service.calculate_similarity.return_value = 1.0
    service.embedding_service.generate_embeddings.side_effect = lambda texts: [np.array([1.0, 0.0]) for _ in texts]
    return service


def test_verifier_batches_each_text_once(verifier, sources):
    result = verifier.verify_response("Luca nutzt Python [1]. Luca nutzt React [2].", sources)
    assert result.is_verified
    verifier.embedding_service.generate_embedding.assert_not_called()
    texts = verifier.embedding_service.generate_embeddings.call_args.args[0]
    assert len(texts) == len(set(texts))
    assert verifier.embedding_service.generate_embeddings.call_count == 1


@pytest.mark.parametrize("answer", [
    "Luca nutzt Python.", "Luca nutzt Python [9].", "Luca nutzt Python [0].",
    "Luca nutzt Python seit 2035 [1].", "Luca nutzt Python nicht [1].",
    "Luca arbeitet bei Google [1].", "[1]", "", "Luca ist Arzt [1].",
    "Luca nutzt Python [1]. Er ist reich.",
])
def test_unsupported_claims_fail_even_with_high_similarity(verifier, sources, answer):
    assert not verifier.verify_response(answer, sources).is_verified


def test_only_cited_evidence_is_compared(verifier, sources):
    def embed(texts):
        return [np.array([0.0, 1.0]) if "React" in t else np.array([1.0, 0.0]) for t in texts]
    verifier.embedding_service.generate_embeddings.side_effect = embed
    assert not verifier.verify_response("Luca nutzt Python [2].", sources).is_verified


@pytest.fixture
def chatbot(sources):
    service = ChatbotService.__new__(ChatbotService)
    service.retriever = Mock()
    service.generator = Mock()
    service.verifier = Mock()
    service._retrieve_documents = Mock(return_value=sources)
    service.generator.generate_response.return_value = {
        "answer": "Luca arbeitet bei Google [1].", "sources": [],
        "confidence": 0.9, "model": "test", "tokens_used": 20,
        "finish_reason": "stop",
    }
    service.verifier.verify_response.return_value = VerificationResult(False, 0.1, [])
    return service


def test_failed_verification_replaces_generated_answer(chatbot):
    result = chatbot.process_message("Welche Projekte?")
    assert "Google" not in result.answer
    assert "Python" in result.answer
    assert result.outcome == "source_fallback"
    assert not result.verification or not result.verification.is_verified


def test_skip_verification_returns_excerpts_without_generation(chatbot, monkeypatch):
    monkeypatch.setenv("SKIP_VERIFICATION", "true")
    monkeypatch.setattr(settings, "SKIP_VERIFICATION", True)
    result = chatbot.process_message("Welche Projekte?")
    assert "Google" not in result.answer
    assert result.outcome == "source_fallback"
    chatbot.generator.generate_response.assert_not_called()


@pytest.mark.parametrize("failure", ["truncated", "empty", "exception", "verifier_exception"])
def test_incomplete_or_failed_generation_falls_back(chatbot, failure):
    if failure == "truncated":
        chatbot.generator.generate_response.return_value["finish_reason"] = "length"
    elif failure == "empty":
        chatbot.generator.generate_response.return_value["answer"] = ""
    elif failure == "exception":
        chatbot.generator.generate_response.side_effect = TimeoutError()
    else:
        chatbot.verifier.verify_response.side_effect = RuntimeError()
    result = chatbot.process_message("Welche Projekte?")
    assert "Google" not in result.answer
    assert result.outcome == "source_fallback"


def test_no_results_has_honest_outcome_and_timings(chatbot):
    chatbot._retrieve_documents.return_value = []
    result = chatbot.process_message("Hat Luca Erfahrung mit COBOL?")
    assert result.outcome == "no_information"
    assert not result.sources
    assert "timings_ms" in result.metadata
    chatbot.generator.generate_response.assert_not_called()


def test_no_arbitrary_recent_records_on_empty_search(sources):
    service = ChatbotService.__new__(ChatbotService)
    service.retriever = Mock()
    service.retriever.search.return_value = []
    service.retriever.get_fallback_results.return_value = sources
    assert service._retrieve_documents("Unbekannt", ChatMode.NATURAL) == []
    service.retriever.get_fallback_results.assert_not_called()


def test_success_preserves_only_cited_source_indices(chatbot):
    chatbot.generator.generate_response.return_value["answer"] = "Luca nutzt React [2]."
    chatbot.verifier.verify_response.return_value = VerificationResult(True, 0.8, [])
    result = chatbot.process_message("Welche Technologien?")
    assert result.outcome == "answered"
    assert [s.index for s in result.sources] == [2]
    assert result.verification.is_verified
