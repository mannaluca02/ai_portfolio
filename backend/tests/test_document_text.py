from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.services import document_service
from app.services.document_service import document_from_record, document_text
from app.services.retriever_service import SearchResult


def test_project_technologies_and_role_are_embedded_not_only_description():
    row = {"name": "CNN", "description": "Image classification", "technologies": ["Python", "PyTorch"],
           "your_role": "Data Scientist", "start_date": date(2026, 3, 17)}
    text = document_text("projects", row)
    assert "PyTorch" in text
    assert "Data Scientist" in text
    assert "2026-03-17" in text
    assert text == document_from_record("projects", SimpleNamespace(**row))


def test_numbers_zero_values_and_education_achievements_are_preserved():
    text = document_text("education", {"institution": "FHNW", "grade": Decimal("5.5"),
                                      "achievements": ["Rang 9 von 97"], "end_date": None})
    assert "5.5" in text
    assert "Rang 9 von 97" in text
    assert "None" not in text
    assert "0" in document_text("skills", {"name": "Python", "years_of_experience": 0})


def test_phone_field_and_its_formatted_copy_in_bio_are_removed():
    text = document_text("contact_info", {"full_name": "Synthetic Person", "phone": "+41 79 123 45 67",
        "bio": "Kontakt unter +41 (79) 123-45-67.", "email": "test@example.com", "city": "Basel"})
    assert "123" not in text
    assert "phone" not in text
    assert "test@example.com" in text
    assert "Basel" in text


def test_phone_denylist_applies_to_other_tables_too():
    text = document_text("projects", {"name": "Test", "description": "Call +41 79 123 45 67"},
                         phone_numbers=["+41791234567"])
    assert "123" not in text


def test_unknown_fields_vectors_and_credentials_never_enter_documents():
    text = document_text("projects", {"name": "Test", "embedding": [0.7], "secret": "do-not-copy",
                                     "api_key": "private", "phone": "+41791234567"})
    assert text == "name: Test"


@pytest.mark.parametrize("table,row,expected", [
    ("work_experiences", {"responsibilities": ["Database indexing"]}, "Database indexing"),
    ("skills", {"skill_level": "Expert"}, "Expert"),
    ("certificates", {"issuing_organization": "Example University"}, "Example University"),
    ("hobbies", {"since_year": 2015}, "2015"),
    ("social_links", {"platform": "GitHub", "url": "https://github.com/example"}, "https://github.com/example"),
    ("contact_info", {"availability": "Available"}, "Available"),
])
def test_table_specific_fields_are_covered(table, row, expected):
    assert expected in document_text(table, row)


def test_unknown_table_fails_explicitly():
    with pytest.raises(ValueError):
        document_text("not_a_table", {"name": "Test"})


def test_search_result_uses_canonical_text_and_removes_phone():
    source = SearchResult(1, "contact_info", "Test", "Synthetic bio", "contact", "contact", "contact", 0.8,
                          {"phone": "+41791234567", "city": "Basel"})
    assert source.evidence_text() == document_text("contact_info", {
        "full_name": "Test", "bio": "Synthetic bio", "phone": "+41791234567", "city": "Basel"})


def retrieved_project():
    from unittest.mock import Mock

    from app.services.retriever_service import RetrieverService

    row = SimpleNamespace(name="CNN", description="Images", technologies=["PyTorch"])
    service = RetrieverService.__new__(RetrieverService)
    service.db = Mock()
    service.db.execute.return_value.fetchall.return_value = [row]
    formatter = Mock(return_value=SearchResult(1, "projects", "CNN", "Images", "cnn", "projects", "cnn", 0.8, {}))
    return service._search_table("projects", "[1,0]", 5, 0.2, formatter, None)[0], row


def test_retrieved_document_carries_the_full_evidence_for_verification():
    result, row = retrieved_project()
    assert result.evidence_text() == document_from_record("projects", row)
    assert "PyTorch" in result.evidence_text()


def test_retrieval_never_overwrites_the_visitor_facing_content():
    """Excerpts are shown verbatim, so `content` must not become a field dump."""
    result, _ = retrieved_project()
    assert result.content == "Images"
    assert "description:" not in result.content


def test_age_is_computed_from_the_birth_date_and_never_shows_it():
    """The visitor asked "wie alt", not for a date of birth: only the derived
    number of years reaches the model, so it cannot repeat the exact date."""
    text = document_service.document_text(
        "contact_info", {"full_name": "Luca Manna", "birth_date": date(2002, 11, 7)},
        today=date(2026, 9, 12))
    assert "age: 23 Jahre alt" in text
    assert "2002" not in text and "birth_date" not in text


@pytest.mark.parametrize("today,expected", [
    (date(2026, 11, 6), 23),   # the day before
    (date(2026, 11, 7), 24),   # the birthday itself
    (date(2026, 11, 8), 24),
])
def test_the_age_turns_over_on_the_birthday(today, expected):
    assert document_service.age_in_years(date(2002, 11, 7), today=today) == expected


@pytest.mark.parametrize("value", [None, "", "not-a-date", 0])
def test_a_missing_or_unusable_birth_date_adds_no_age_claim(value):
    assert document_service.age_in_years(value) is None
    text = document_service.document_text("contact_info", {"full_name": "Luca Manna", "birth_date": value})
    assert "age:" not in text


def test_an_iso_string_from_a_raw_row_is_accepted():
    assert document_service.age_in_years("2002-11-07", today=date(2026, 9, 12)) == 23


def test_a_record_without_the_column_still_produces_a_document():
    """A backend deployed before the migration must not break on contact_info."""
    class Row:
        full_name = "Luca Manna"
        bio = "Data Science Student"
    text = document_service.document_from_record("contact_info", Row())
    assert "full_name: Luca Manna" in text
    assert "age:" not in text


def test_a_spoken_language_carries_its_level_as_evidence():
    text = document_text("languages", {"name": "Englisch", "level": "B2 (Cambridge English: First)",
                                        "description": "Englisch auf Niveau B2 des GER."})
    assert "name: Englisch" in text
    assert "level: B2 (Cambridge English: First)" in text
    assert "Niveau B2" in text
