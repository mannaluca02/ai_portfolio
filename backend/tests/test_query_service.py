from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from app.services import query_service
from app.services.query_service import (
    name_tokens,
    normalize_query,
    reset_subject_names,
    subject_names,
)

NAMES = name_tokens("Ada Muster")


@pytest.fixture(autouse=True)
def clear_cache():
    reset_subject_names()
    yield
    reset_subject_names()


@pytest.mark.parametrize("query,expected", [
    ("Was hat ada studiert?", "Was hat studiert?"),
    ("Wo hat Ada gearbeitet?", "Wo hat gearbeitet?"),
    ("Hat Ada Muster mit PyTorch gearbeitet?", "Hat mit PyTorch gearbeitet?"),
    ("Was sind Adas Projekte?", "Was sind Projekte?"),
])
def test_owner_name_is_removed_from_the_search_query(query, expected):
    assert normalize_query(query, NAMES) == expected


@pytest.mark.parametrize("query", [
    "Wer ist Ada Muster?", "Ada", "Ada Muster", "Wie heisst Ada?",
])
def test_queries_that_are_only_the_name_are_left_untouched(query):
    """Removing the name would leave nothing topical to search for."""
    assert normalize_query(query, NAMES) == query


@pytest.mark.parametrize("query", [
    "Kann er Docker?", "Wie alt ist er?", "Was ist PostFinance Horizons",
])
def test_queries_without_the_name_are_unchanged(query):
    assert normalize_query(query, NAMES) == query


def test_unrelated_words_containing_the_name_survive():
    assert normalize_query("Was ist Adaptivität?", NAMES) == "Was ist Adaptivität?"


def test_without_known_names_the_query_is_returned_unchanged():
    assert normalize_query("Was hat Ada studiert?", []) == "Was hat Ada studiert?"


def test_name_tokens_cover_genitive_and_ignore_initials():
    assert name_tokens("Ada B. Muster") == frozenset({"ada", "adas", "muster", "musters"})
    assert name_tokens("") == frozenset()


def test_subject_names_are_read_from_the_corpus_and_cached():
    db = Mock()
    db.execute.return_value.fetchall.return_value = [SimpleNamespace(full_name="Ada Muster")]
    assert subject_names(db) == NAMES
    assert subject_names(db) == NAMES
    assert db.execute.call_count == 1


def test_database_failure_degrades_ranking_without_caching_the_failure(caplog):
    db = Mock()
    db.execute.side_effect = RuntimeError("connection lost")
    assert subject_names(db) == frozenset()
    assert "Subject names unavailable" in caplog.text
    assert query_service._subject_names is None


def test_missing_session_never_raises():
    assert subject_names(None) == frozenset()
