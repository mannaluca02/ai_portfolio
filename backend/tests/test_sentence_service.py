"""The German rules the verifier and the excerpt fallback both depend on."""
import pytest

from app.services.sentence_service import first_sentence, split_sentences


@pytest.mark.parametrize("text,expected", [
    # A whole paragraph from a portfolio row shrinks to its first statement.
    ("Entwicklung interner Web-Applikationen. Zusätzlich Betreuung der Pipelines.",
     "Entwicklung interner Web-Applikationen."),
    # An ordinal is not a sentence end, so the number keeps its sentence.
    ("Er erreichte den 9. Platz im Ranking. Danach folgte mehr.",
     "Er erreichte den 9. Platz im Ranking."),
    ("Er nutzt z.B. Python und Go. Zweiter Satz.", "Er nutzt z.B. Python und Go."),
    # A year does end a sentence.
    ("Tätig seit 2024. Zweiter Satz.", "Tätig seit 2024."),
    ("Mehrere\nZeilen als Eintrag.", "Mehrere"),
    ("", ""),
])
def test_only_the_first_statement_of_a_row_is_quoted(text, expected):
    assert first_sentence(text) == expected


def test_a_single_long_sentence_is_cut_at_a_word_boundary():
    text = "Aufbau " + "sehr langer Beschreibungstext " * 12
    quoted = first_sentence(text, max_chars=60)
    assert len(quoted) <= 61  # the ellipsis is one character
    assert quoted.endswith("…")
    assert not quoted.removesuffix("…").endswith(" ")
    assert text.startswith(quoted.removesuffix("…"))


def test_whitespace_inside_a_stored_field_is_normalised():
    assert first_sentence("Aufbau   eines\t Netzwerks.") == "Aufbau eines Netzwerks."


def test_an_unusable_limit_is_rejected_rather_than_silently_ignored():
    with pytest.raises(ValueError):
        first_sentence("Text.", max_chars=0)


def test_citations_survive_the_split_used_for_verification():
    assert split_sentences("Luca nutzt Python [1]. Luca nutzt React [2].") == [
        "Luca nutzt Python [1].", "Luca nutzt React [2]."]
