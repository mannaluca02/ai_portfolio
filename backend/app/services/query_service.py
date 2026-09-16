"""Query normalisation for a single-subject portfolio corpus.

Every row describes the same person, so the owner's name carries no
discriminating signal. It does, however, match the rows that are literally his
name (contact_info.full_name, the LinkedIn slug, the GitHub handle), which drags
them above the row that actually answers the question. Measured locally: the
correct source reached the top three for 7 of 11 questions as asked, and 10 of 11
once the name was removed.

Only the embedded search query is normalised. The generator, the verifier and
every user-facing string keep the question exactly as it was asked.
"""
import logging
import re
from collections.abc import Iterable

from sqlalchemy import text

from app.services.document_service import DOCUMENT_FIELDS, document_from_record

logger = logging.getLogger(__name__)

# A query that keeps only these after name removal has no topic left to search
# for, so it is left untouched instead ("Wer ist Luca Manna?").
_STOPWORD_TEXT = """
was wer wie wo wann warum weshalb welche welcher welches wieviel viele
ist sind war waren hat hatte habe haben kann kannst koennen könnt darf wurde
heisst heißt heissen heißen nennt nennen
der die das den dem des ein eine einen einem eines kein keine
er sie es du ich wir ihr ihm ihn sein seine seiner ihre ihrer
mit bei von vom zu zum zur in im an am auf fuer für und oder aber auch
what who how where when why which whose is are was were has have had can could
the a an of to for with at on and or do does did his her their he she it you
"""
STOPWORDS = frozenset(_STOPWORD_TEXT.split())

# Fields that name real things. Deliberately narrower than DOCUMENT_FIELDS:
# descriptions are prose and would flood this with ordinary German.
ENTITY_FIELDS = {
    "work_experiences": ("company", "location", "technologies"),
    "projects": ("name", "technologies", "client_company"),
    "skills": ("name",),
    "certificates": ("name", "issuing_organization"),
    "education": ("institution", "location"),
    "hobbies": ("name",),
    "languages": ("name",),
    "contact_info": ("full_name", "city", "country"),
    "social_links": ("platform", "username"),
}

WORD = re.compile(r"[^\W\d_]+", re.UNICODE)
MIN_NAME_LENGTH = 3

_subject_names: frozenset[str] | None = None
_corpus_vocabulary: frozenset[str] | None = None
_corpus_blob: str = ""
_corpus_entities: frozenset[str] | None = None


def name_tokens(full_name: str) -> frozenset[str]:
    """Name tokens plus the German genitive form, e.g. Luca -> {luca, lucas}."""
    tokens = {token.casefold() for token in WORD.findall(full_name or "")
              if len(token) >= MIN_NAME_LENGTH}
    return frozenset(tokens | {token + "s" for token in tokens})


def subject_names(db) -> frozenset[str]:
    """Read the portfolio owner's name from the corpus, never hardcoded.

    Cached after the first success. A failure is reported and not cached, so a
    transient database problem degrades ranking instead of persisting.
    """
    global _subject_names
    if _subject_names is not None:
        return _subject_names
    if db is None:
        return frozenset()
    try:
        rows = db.execute(text("SELECT full_name FROM contact_info")).fetchall()
        names: set[str] = set()
        for row in rows:
            names |= name_tokens(row.full_name)
    except Exception:
        logger.warning("Subject names unavailable; query normalisation is off", exc_info=True)
        return frozenset()
    _subject_names = frozenset(names)
    return _subject_names


def cached_subject_names() -> frozenset[str]:
    """Names already loaded, without triggering a database read."""
    return _subject_names or frozenset()


def corpus_vocabulary(db) -> frozenset[str]:
    """Every word the portfolio itself uses, for telling entities apart.

    A capitalised word absent from this vocabulary was introduced by the model
    ("Google"); a capitalised word present in it is ordinary German ("Projekt",
    "Sprache") and must not be treated as an invented entity. Cached after the
    first success, failures are reported and not cached.
    """
    global _corpus_vocabulary, _corpus_blob
    if _corpus_vocabulary is not None:
        return _corpus_vocabulary
    if db is None:
        return frozenset()
    try:
        tokens: set[str] = set()
        for table, fields in DOCUMENT_FIELDS.items():
            columns = ", ".join(fields)
            for row in db.execute(text(f"SELECT {columns} FROM {table}")).fetchall():
                tokens |= {word.casefold()
                           for word in WORD.findall(document_from_record(table, row))}
    except Exception:
        logger.warning("Corpus vocabulary unavailable; entity checks stay strict", exc_info=True)
        return frozenset()
    _corpus_vocabulary = frozenset(tokens)
    _corpus_blob = " ".join(sorted(tokens))
    return _corpus_vocabulary


def cached_corpus_terms() -> tuple[frozenset[str], str]:
    """Vocabulary and a joined blob for compound matching, without a DB read."""
    return _corpus_vocabulary or frozenset(), _corpus_blob


def corpus_entities(db) -> frozenset[str]:
    """Words from the fields that actually name things: employers, schools,
    technologies, platforms, places, product names.

    This is the set worth policing. A claim citing one row must not introduce an
    entity that belongs to a different row ("Microsoft" is a technology of the
    room booker, not of the PostFinance project). Ordinary German nouns are
    deliberately not in here, so they are never mistaken for invented entities.
    """
    global _corpus_entities
    if _corpus_entities is not None:
        return _corpus_entities
    if db is None:
        return frozenset()
    try:
        tokens: set[str] = set()
        for table, fields in ENTITY_FIELDS.items():
            columns = ", ".join(fields)
            for row in db.execute(text(f"SELECT {columns} FROM {table}")).fetchall():
                for field in fields:
                    value = getattr(row, field, None)
                    values = value if isinstance(value, (list, tuple)) else [value]
                    for item in values:
                        if item:
                            tokens |= {word.casefold() for word in WORD.findall(str(item))}
    except Exception:
        logger.warning("Corpus entities unavailable; cross-row checks are off", exc_info=True)
        return frozenset()
    _corpus_entities = frozenset(tokens)
    return _corpus_entities


def cached_corpus_entities() -> frozenset[str]:
    """Entities already loaded, without triggering a database read."""
    return _corpus_entities or frozenset()


def reset_subject_names() -> None:
    """Drop the caches; used by tests and by any future corpus reload."""
    global _subject_names, _corpus_vocabulary, _corpus_blob, _corpus_entities
    _subject_names = None
    _corpus_vocabulary = None
    _corpus_blob = ""
    _corpus_entities = None


def normalize_query(query: str, names: Iterable[str]) -> str:
    names = {name.casefold() for name in names if name}
    if not names:
        return query
    remaining = [word.casefold() for word in WORD.findall(query)
                 if word.casefold() not in names]
    if not any(word not in STOPWORDS for word in remaining):
        return query
    pattern = "|".join(re.escape(name) for name in sorted(names, key=len, reverse=True))
    stripped = re.sub(rf"(?<!\w)(?:{pattern})(?!\w)", " ", query, flags=re.IGNORECASE)
    stripped = re.sub(r"\s{2,}", " ", stripped).strip()
    return stripped or query
