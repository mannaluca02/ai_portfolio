"""German sentence boundaries, shared by verification and excerpt presentation.

The verifier splits a generated answer to require a citation in every sentence.
The excerpt fallback splits a stored row to show one sentence instead of the
whole field. Both need the same German rules, so they live in one place: an
ordinal ("den 9. Platz") and an abbreviation ("z.B.") are not sentence ends,
while a year ("seit 2024.") and a decimal grade ("Note 5.5.") are.
"""
import re

# German abbreviations whose period is not a sentence end.
ABBREVIATIONS = frozenset({
    "z.b.", "d.h.", "u.a.", "u.ä.", "o.ä.", "z.t.", "i.d.r.", "u.v.m.",
    "bzw.", "usw.", "etc.", "ca.", "ggf.", "inkl.", "exkl.", "evtl.", "bspw.",
    "max.", "min.", "nr.", "mio.", "mrd.", "tsd.", "vs.", "bzgl.", "jhd.",
    "dr.", "prof.", "dipl.", "str.", "abs.", "vgl.", "s.", "ff.", "sog.",
})


ENGLISH_ABBREVIATIONS = frozenset({'e.g.', 'i.e.', 'etc.', 'inc.', 'ltd.', 'corp.', 'dr.', 'mr.', 'mrs.', 'ms.', 'prof.', 'vs.', 'no.'})


def continues_sentence(part: str, language: str = 'de') -> bool:
    """True when a trailing period is German punctuation, not a sentence end.

    "erreichte er den 9. Platz [1]." is one sentence. Splitting it left the
    first half uncited and rejected a correct answer. A year ("seit 2024.")
    and a decimal ("Note 5.5.") do end a sentence, so only a one or two digit
    ordinal counts, and a short list of abbreviations.
    """
    stripped = part.rstrip()
    if not stripped.endswith("."):
        return False
    if language == "de" and re.search(r"(?<![\d.])\d{1,2}\.$", stripped):
        return True
    return stripped.rsplit(maxsplit=1)[-1].casefold() in (ENGLISH_ABBREVIATIONS if language == "en" else ABBREVIATIONS)


def split_sentences(text: str, language: str = "de") -> list[str]:
    """Sentences in order, bullet markers removed, citations kept."""
    # Accept both "sentence [1]." and "sentence. [1]". Never discard a short
    # factual statement such as "Luca ist Arzt" as if it were a greeting.
    text = re.sub(r"([.!?])\s*((?:\[\d+\]\s*)+)", r" \2\1 ", text)
    sentences: list[str] = []
    for raw in re.split(r"(?<=[.!?])\s+|\n+", text):
        part = raw.strip().lstrip("•*- ")
        if not part:
            continue
        if sentences and continues_sentence(sentences[-1], language):
            sentences[-1] = f"{sentences[-1]} {part}"
        else:
            sentences.append(part)
    return sentences


def first_sentence(text: str, *, max_chars: int = 180) -> str:
    """The opening sentence of a stored field, shortened at a word boundary.

    Portfolio rows contain whole paragraphs. Pasting one into a chat answer is
    what made the fallback read like a database export, so only the first
    statement is shown, and a single long sentence is cut rather than sent in
    full. The ellipsis marks that the entry continues.
    """
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    sentences = split_sentences(text or "")
    if not sentences:
        return ""
    sentence = re.sub(r"\s+", " ", sentences[0]).strip()
    if len(sentence) <= max_chars:
        return sentence
    head = sentence[:max_chars].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return f"{head or sentence[:max_chars].rstrip()}…"
