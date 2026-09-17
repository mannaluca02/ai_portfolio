import re
from unittest.mock import Mock

import numpy as np
import pytest

from app.config import settings
from app.schemas.chat import ChatMode
from app.services import verifier_service
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
    # Claims are encoded per request, evidence comes from the cached path.
    service.embedding_service.generate_embeddings.side_effect = lambda texts: [np.array([1.0, 0.0]) for _ in texts]
    service.embedding_service.embed_documents.side_effect = lambda texts: [np.array([1.0, 0.0]) for _ in texts]
    return service


def test_verifier_batches_each_text_once(verifier, sources):
    result = verifier.verify_response("Luca nutzt Python [1]. Luca nutzt React [2].", sources)
    assert result.is_verified
    verifier.embedding_service.generate_embedding.assert_not_called()
    claims = verifier.embedding_service.generate_embeddings.call_args.args[0]
    evidence = verifier.embedding_service.embed_documents.call_args.args[0]
    assert len(claims) == len(set(claims))
    assert len(evidence) == len(set(evidence))
    assert verifier.embedding_service.generate_embeddings.call_count == 1
    assert verifier.embedding_service.embed_documents.call_count == 1


def test_evidence_is_never_re_encoded_per_request(verifier, sources):
    """Row text does not change, so only the answer's own sentences are encoded."""
    verifier.verify_response("Luca nutzt Python [1]. Luca nutzt React [2].", sources)
    encoded = verifier.embedding_service.generate_embeddings.call_args.args[0]
    assert not any(source.evidence_text() in encoded for source in sources)
    assert all("Luca nutzt" in claim for claim in encoded)


@pytest.mark.parametrize("answer", [
    "Luca nutzt Python.", "Luca nutzt Python [9].", "Luca nutzt Python [0].",
    "Luca nutzt Python seit 2035 [1].", "Luca nutzt Python nicht [1].",
    "Luca arbeitet bei Google [1].", "[1]", "", "Luca ist Arzt [1].",
    "Luca nutzt Python [1]. Er ist reich.",
])
def test_unsupported_claims_fail_even_with_high_similarity(verifier, sources, answer):
    assert not verifier.verify_response(answer, sources).is_verified


@pytest.mark.parametrize("text,expected", [
    # A German ordinal is not a sentence end. Splitting here left "…den 9."
    # uncited and threw away a correct answer.
    ("Luca erreichte den 9. Platz [1].", 1),
    ("Am 9. September 2024 begann das Studium [1].", 1),
    ("Er nutzt z.B. Python [1].", 1),
    # A year and a decimal grade do end a sentence.
    ("Luca studiert seit 2024. Er hat einen Abschluss [1].", 2),
    ("Abschluss mit Note 5.5. Zudem Top 5 Prozent [1].", 2),
    ("Luca nutzt Python [1]. Luca nutzt React [2].", 2),
])
def test_german_punctuation_does_not_split_a_sentence(text, expected):
    assert len(VerifierService._split_into_sentences(text)) == expected


def test_an_ordinal_keeps_its_citation_and_verifies(verifier, sources):
    """This is the shape that production rejected: the split dropped the
    citation off the first half of a single, correctly cited sentence."""
    source = sources[0]
    source.document = "name: Ranking\ndescription: Rang 9 von 97 im Leistungsranking."
    answer = "Im Leistungsranking erreichte er den 9. Rang [1]."
    assert verifier.verify_response(answer, [source]).is_verified


def test_citation_does_not_have_to_be_the_final_token(verifier, sources):
    """Correct answers were rejected over punctuation placement alone."""
    assert verifier.verify_response("Luca nutzt [1] Python seit 2020.", sources).is_verified


def test_german_declension_no_longer_rejects_a_supported_claim(verifier, sources):
    """Evidence says "Projekt"; a claim saying "Projekten" means the same."""
    assert verifier.verify_response("Luca nutzt Python in Projekten [1].", sources).is_verified


def test_unrelated_negation_inside_a_long_row_no_longer_blocks_claims(verifier, sources):
    source = sources[0]
    source.document = "name: Assistent\ndescription: Das Sprachmodell rechnet nie."
    assert verifier.verify_response("Das Sprachmodell rechnet [1].", [source]).is_verified


def test_a_negated_claim_still_needs_negated_evidence(verifier, sources):
    assert not verifier.verify_response("Luca nutzt Python nicht [1].", sources).is_verified


def test_invented_entity_is_rejected_even_with_a_loaded_corpus(verifier, sources, monkeypatch):
    """The corpus vocabulary must not become a hole in the entity check."""
    monkeypatch.setattr(verifier_service, "cached_corpus_terms",
                        lambda: (frozenset({"python", "projekt"}), "python projekt"))
    assert not verifier.verify_response("Luca arbeitet bei Google [1].", sources).is_verified


@pytest.fixture
def loaded_corpus(monkeypatch):
    """A corpus that names Microsoft somewhere other than the cited row."""
    monkeypatch.setattr(verifier_service, "cached_corpus_terms",
                        lambda: (frozenset({"python", "microsoft"}), "python microsoft"))
    monkeypatch.setattr(verifier_service, "cached_corpus_entities",
                        lambda: frozenset({"python", "microsoft"}))


def test_an_entity_belonging_to_another_row_is_rejected(verifier, sources, loaded_corpus):
    assert not verifier.verify_response("Das Projekt nutzt Microsoft [1].", sources).is_verified


def test_ordinary_german_absent_from_a_small_corpus_is_not_an_entity(verifier, sources, loaded_corpus):
    """A 44-row portfolio is not a dictionary; "Jahre" asserts nothing."""
    assert verifier.verify_response("Luca nutzt Python seit Jahren [1].", sources).is_verified


def test_an_unknown_capitalised_word_is_still_rejected(verifier, sources, loaded_corpus):
    assert not verifier.verify_response("Luca studierte an der ETH [1].", sources).is_verified


def test_only_cited_evidence_is_compared(verifier, sources):
    def embed(texts):
        return [np.array([0.0, 1.0]) if "React" in t else np.array([1.0, 0.0]) for t in texts]
    verifier.embedding_service.generate_embeddings.side_effect = embed
    verifier.embedding_service.embed_documents.side_effect = embed
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


def test_excerpts_stay_readable_and_never_expose_field_labels(chatbot, sources):
    """Visitors see this text verbatim, so it must not become a raw row dump."""
    for source in sources:
        source.document = source.evidence_text()
    answer = chatbot._source_fallback(sources, ChatMode.NATURAL).answer
    assert "Luca nutzt Python seit 2020." in answer
    assert not any(label in answer for label in ("description:", "technologies:", "name:"))


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


@pytest.fixture
def noisy_results():
    """The shape behind the owner's complaint about "wo arbeitest du?": one
    plausible row, and two weaker ones from unrelated sections."""
    return [
        SearchResult(1, "work_experiences", "Applikationsentwickler bei Novartis",
                     "Entwicklung interner Web-Applikationen im Bereich Clinical Data. "
                     "Zusätzlich Betreuung der Datenpipelines und Abstimmung mit den Fachbereichen.",
                     "work", "experience", "work", 0.482, {}),
        SearchResult(2, "hobbies", "Fitness", "Krafttraining viermal pro Woche.",
                     "fitness", "hobbies", "fitness", 0.401, {}),
        SearchResult(3, "projects", "Heim Netzwerk", "Aufbau eines Heimnetzwerks mit VLANs.",
                     "heim", "projects", "heim", 0.372, {}),
    ]


def test_excerpts_say_they_are_unverified_and_quote_one_sentence(chatbot, noisy_results):
    """This is the "1 zu 1 Supabase Export" the owner reported: whole rows, no
    statement that nothing was verified, unrelated sections alongside."""
    answer = chatbot._source_fallback(noisy_results, ChatMode.NATURAL).answer
    assert "keine geprüfte Antwort" in answer
    assert "Novartis" in answer
    # One sentence of the row, not the paragraph.
    assert "Clinical Data." in answer
    assert "Datenpipelines" not in answer
    # Weaker rows from other sections are not presented as related answers.
    assert "Fitness" not in answer and "Heim Netzwerk" not in answer


def test_excerpts_stay_within_two_entries(chatbot):
    """Three equally close education rows answer "was hat er studiert"; a chat
    answer still shows two of them, not the whole table."""
    degrees = [SearchResult(index, "education", f"Abschluss {index}", f"Studium {index}.",
                            f"edu-{index}", "education", f"edu-{index}", 0.48 - index / 100, {})
               for index in (1, 2, 3)]
    response = chatbot._source_fallback(degrees, ChatMode.NATURAL)
    assert response.answer.count("•") == 2
    assert len(response.sources) == 2
    # Citation numbers still address the sources that are shown.
    assert {int(n) for n in re.findall(r"\[(\d+)\]", response.answer)} == {s.index for s in response.sources}


def test_a_close_row_from_another_section_is_not_listed_as_a_second_answer(chatbot):
    """The reported case: a hobby row 0.006 behind the job row. Measured on the
    live corpus for "Wo hat luca gearbeitet?" (Novartis 0.440, Heim Netzwerk
    0.434), and the reason the answer read like a database export."""
    job = SearchResult(1, "work_experiences", "IT-Supporter bei Novartis",
                       "Second Level Support für interne Systeme.", "work", "experience", "work", 0.440, {})
    hobby = SearchResult(2, "hobbies", "Heim Netzwerk", "Aufbau eines Heimnetzwerks mit VLANs.",
                         "heim", "hobbies", "heim", 0.434, {})
    hobby.off_topic = True  # A work question damps the hobby table.
    response = chatbot._source_fallback([job, hobby], ChatMode.NATURAL)
    assert "Novartis" in response.answer
    assert "Heim Netzwerk" not in response.answer
    assert [source.table for source in response.sources] == ["work_experiences"]


def test_a_row_from_a_section_nobody_asked_about_is_never_quoted(chatbot):
    """Measured: "Heim Netzwerk" scores 0.519 for "Kann er Docker?", above every
    project row. Intent damps the hobby table, and a damped row is evidence for
    the model but never an answer on its own."""
    hobby = SearchResult(1, "hobbies", "Heim Netzwerk", "Aufbau eines Heimnetzwerks mit VLANs.",
                         "heim", "hobbies", "heim", 0.519, {})
    hobby.off_topic = True
    project = SearchResult(2, "projects", "PostFinance Horizons", "Hackathon-Projekt mit Docker.",
                           "pfh", "projects", "pfh", 0.421, {})
    response = chatbot._source_fallback([hobby, project], ChatMode.NATURAL)
    assert "Heim Netzwerk" not in response.answer
    assert "PostFinance Horizons" in response.answer


def test_excerpts_below_the_floor_are_not_offered_at_all(chatbot, noisy_results):
    for result in noisy_results:
        result.similarity = 0.3
    response = chatbot._source_fallback(noisy_results, ChatMode.NATURAL)
    assert response.outcome == "no_information"
    assert not response.sources


@pytest.mark.parametrize('pronoun', ['I', "I'm", 'He', 'Luca'])
def test_english_age_claims_pass_fact_checks_but_wrong_ages_do_not(verifier, pronoun):
    source = SearchResult(1, 'contact_info', 'Luca', '', 'contact', 'contact', 'contact', 0.8, {})
    source.document = 'full_name: Luca\nage: 23 Jahre alt'
    verb = '' if pronoun == "I'm" else ' am' if pronoun == 'I' else ' is'
    assert verifier.verify_response(f'{pronoun}{verb} 23 years old [1].', [source], language='en').is_verified
    assert not verifier.verify_response(f'{pronoun}{verb} 24 years old [1].', [source], language='en').is_verified
