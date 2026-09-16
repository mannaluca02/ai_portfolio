from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from app.services.document_service import DOCUMENT_FIELDS
from app.services.intent_service import PORTFOLIO_TABLES, IntentService, QueryIntent
from app.services.query_service import ENTITY_FIELDS, reset_subject_names
from app.services.retriever_service import RetrieverService, SearchResult

# Derived, never listed by hand: a new table must not need this file edited to
# stay covered, and a hardcoded copy silently went stale when languages arrived.
TABLES = set(PORTFOLIO_TABLES)


@pytest.mark.parametrize("query", ["Wo hat Luca gearbeitet?", "Kann Luca Docker?",
                                  "PyTorch", "Was studiert Luca?", "GitHub Projekte", "Wer ist Luca?"])
def test_detected_intent_never_excludes_a_portfolio_table(query):
    service = IntentService()
    intent = service.detect_intent(query)
    assert set(intent.tables) == TABLES
    assert all(not service.should_exclude_table(table, intent) for table in TABLES)


@pytest.mark.parametrize("text,keywords", [
    ("gearbeitet", ["arbeit"]), ("kommunikation", ["uni"]), ("profiling", ["profil"]),
])
def test_keywords_do_not_match_inside_other_words(text, keywords):
    assert not IntentService()._contains_keywords(text, keywords)


def test_work_and_multi_topic_queries_receive_only_soft_boosts():
    service = IntentService()
    assert service.detect_intent("Wo hat Luca gearbeitet?").boost_factors.get("work_experiences", 1) > 1
    intent = service.detect_intent("GitHub Links zu Projekten und Studium")
    assert intent.boost_factors.get("social_links", 1) > 1
    assert intent.boost_factors.get("education", 1) > 1


@pytest.fixture
def retriever():
    service = RetrieverService.__new__(RetrieverService)
    service.embedding_service = Mock()
    service.embedding_service.generate_embedding.return_value = np.array([1.0, 0.0])
    service.intent_service = IntentService()
    service._search_table = Mock(return_value=[])
    service.db = Mock()
    service.db.execute.return_value.fetchall.return_value = [SimpleNamespace(full_name="Ada Muster")]
    reset_subject_names()
    return service


def test_profile_rows_are_damped_when_the_question_is_not_about_contact():
    """They describe the owner, so they otherwise match every question."""
    boosts = IntentService().detect_intent("Wo wurde gearbeitet?").boost_factors
    assert boosts["contact_info"] < 1 and boosts["social_links"] < 1


def test_profile_rows_are_boosted_when_contact_is_asked_for():
    boosts = IntentService().detect_intent("Wie ist die Email-Adresse?").boost_factors
    assert boosts["contact_info"] > 1 and boosts["social_links"] > 1


def test_search_embeds_the_query_without_the_owner_name(retriever):
    retriever.search("Wo hat Ada gearbeitet?", use_mmr=False)
    assert retriever.embedding_service.generate_embedding.call_args.args[0] == "Wo hat gearbeitet?"


def test_retriever_ignores_legacy_intent_exclusions(retriever):
    retriever.search("Python?", intent=QueryIntent(tables=["projects"]), use_mmr=False)
    assert {call.args[0] for call in retriever._search_table.call_args_list} == TABLES


def test_explicit_table_filter_is_still_respected(retriever):
    retriever.search("Python?", tables=["skills"], use_mmr=False)
    assert [call.args[0] for call in retriever._search_table.call_args_list] == ["skills"]


def test_ranking_boost_never_changes_raw_similarity(retriever):
    source = SearchResult(1, "work_experiences", "Job", "Documented job", "job", "experience", "job", 0.4, {})
    retriever._search_table.side_effect = lambda table, *args: [source] if table == "work_experiences" else []
    results = retriever.search("Wo hat Luca gearbeitet?", use_mmr=False)
    assert results == [source]
    assert source.similarity == 0.4
    assert source.ranking_score > source.similarity


def test_hobby_rows_are_damped_unless_the_question_asks_about_free_time():
    """"Heim Netzwerk" outranked the answer for Docker and for work history."""
    service = IntentService()
    assert service.detect_intent("Kann er Docker?").boost_factors["hobbies"] < 1.0
    assert service.detect_intent("Wo hat luca gearbeitet?").boost_factors["hobbies"] < 1.0


@pytest.mark.parametrize("question", [
    "Was macht er in der Freizeit?", "Welche Hobbys hat er?", "Treibt er Sport?",
    "Was macht er neben dem Studium?",
])
def test_a_real_free_time_question_lifts_the_hobby_rows_back(question):
    assert IntentService().detect_intent(question).boost_factors["hobbies"] > 1.0


def test_damping_never_removes_a_table_from_the_search():
    """Intent ranks; it must not decide what evidence exists."""
    intent = IntentService().detect_intent("Kann er Docker?")
    assert set(intent.tables) == set(PORTFOLIO_TABLES)
    assert all(not IntentService.should_exclude_table(table, intent) for table in PORTFOLIO_TABLES)


def test_every_searchable_table_is_wired_through_the_whole_pipeline():
    """A table added to some maps but not others is silently unsearchable.

    That is exactly what happened when `languages` was added: retrieval logged
    "Unknown table" and the question returned no information, with nothing
    failing anywhere. These four maps must agree.
    """
    retriever = RetrieverService.__new__(RetrieverService)
    tables = set(PORTFOLIO_TABLES)
    assert tables <= set(retriever._formatters()), "missing a row formatter"
    assert tables <= set(DOCUMENT_FIELDS), "missing evidence fields"
    assert tables <= set(ENTITY_FIELDS), "missing entity fields"


def test_search_and_fallback_use_the_same_formatters():
    """They were separate copies, which is how the gap above went unnoticed."""
    retriever = RetrieverService.__new__(RetrieverService)
    assert retriever._formatters() == retriever._formatters()


@pytest.mark.parametrize("question", [
    "Welche Sprachen spricht Luca?", "Sprichst du Englisch?",
    "Was ist seine Muttersprache?", "Welche Sprachen kann er?",
])
def test_a_spoken_language_question_routes_to_the_languages_table(question):
    assert IntentService().detect_intent(question).boost_factors["languages"] > 1.0


@pytest.mark.parametrize("question", [
    "Welche Programmiersprachen kann er?", "Kann er Docker?",
    "Welche Technologien nutzt das Portfolio?",
])
def test_a_programming_question_is_not_mistaken_for_a_spoken_language(question):
    """Word boundaries: "Programmiersprache" must not match "Sprache"."""
    assert IntentService().detect_intent(question).boost_factors.get("languages", 1.0) <= 1.0
