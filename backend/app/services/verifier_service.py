"""Conservative citation and similarity checks, not a proof of factual truth."""
import re
from typing import Any

import numpy as np

from app.config import settings
from app.services.embedding_service import get_embedding_service
from app.services.query_service import (
    cached_corpus_entities,
    cached_corpus_terms,
    cached_subject_names,
)
from app.services.retriever_service import SearchResult
from app.services.sentence_service import continues_sentence, split_sentences

CITATION = re.compile(r"\[(\d+)\]")
# Shared prefix length that tolerates German declension without letting an
# unrelated entity through: "vereinen"/"vereine" match, "google" matches nothing.
STEM_LENGTH = 6
# Capitalised words that carry no entity claim, including sentence-initial ones.
_FUNCTION_WORD_TEXT = """
der die das den dem des ein eine einen einem eines kein keine keinen
er sie es ihm ihn sein seine seiner seinem ihre ihrer dessen
dies diese dieser dieses diesem als auch bei beim dabei damit dazu dort
für fuer mit nach von vom vor zu zum zur in im an am auf aus über ueber
und oder aber sowie zudem ausserdem außerdem heute aktuell derzeit
zuvor danach davor später frueher früher seit während waehrend laut gemäss
gemaess weiterhin ebenso ebenfalls dadurch daher deshalb darum somit insgesamt
zusätzlich zusaetzlich anschliessend anschließend schliesslich schließlich
hier hierbei hierfür hierfuer dafür dafuer dagegen neben nur noch bereits
the a an of to for with at on and or in his her their he she it they this that
"""
FUNCTION_WORDS = frozenset(_FUNCTION_WORD_TEXT.split())

# Ordinary German a CV answer uses. These are nouns, not entities: a 44-row
# corpus is not a dictionary, so without this list correct sentences were
# rejected over words like "Jahre" or "Verantwortlichkeiten". Allowing them
# asserts nothing; the similarity threshold still has to support the sentence.
_COMMON_WORD_TEXT = """
jahr jahre jahren monat monate monaten woche wochen tag tage zeit zeitraum
erfahrung erfahrungen kenntnis kenntnisse wissen faehigkeit fähigkeit
faehigkeiten fähigkeiten schwerpunkt schwerpunkte fokus ziel ziele zweck
aufgabe aufgaben verantwortlichkeit verantwortlichkeiten taetigkeit tätigkeit
taetigkeiten tätigkeiten rolle rollen funktion einsatz einsaetze einsätze
bereich bereiche abteilung abteilungen team teams mitglied mitglieder
projekt projekte projekten arbeit arbeiten praxis theorie methode methoden
ansatz vorgehen umsetzung entwicklung entwicklungen aufbau einfuehrung
einführung migration integration analyse auswertung ergebnis ergebnisse
sprache sprachen technologie technologien werkzeug werkzeuge system systeme
plattform plattformen anwendung anwendungen loesung lösung loesungen lösungen
modell modelle daten datensatz software hardware schnittstelle schnittstellen
studium ausbildung lehre praktikum abschluss abschluesse abschlüsse note noten
schule hochschule universitaet universität semester modul module kurs kurse
unternehmen firma firmen arbeitgeber kunde kunden branche level niveau stufe
beispiel beispiele thema themen inhalt inhalte grundlage grundlagen teil teile
anzahl menge groesse größe dauer beginn ende stand bereits fachbereich
anstellung anstellungen handle profil account konto benutzername nutzername
adresse standort ort orte titel position positionen stelle stellen link links
seite webseite website eintrag eintraege einträge angabe angaben liste
"""
COMMON_WORDS = frozenset(_COMMON_WORD_TEXT.split())
# Matched by stem as well, so German inflection does not need to be enumerated:
# "Benutzernamen" and "Anstellungen" resolve through "benutzername"/"anstellung".
COMMON_STEMS = frozenset(word[:STEM_LENGTH] for word in COMMON_WORDS
                         if len(word) >= STEM_LENGTH)

# Month names per ISO month, German and English. Added to the evidence only for
# the months a row actually contains (see _facts_match).
ISO_DATE = re.compile(r"\d{4}-(\d{2})-\d{2}")
_MONTHS = (
    ("januar", "january"), ("februar", "february"), ("maerz", "märz", "march"),
    ("april",), ("mai", "may"), ("juni", "june"), ("juli", "july"),
    ("august",), ("september",), ("oktober", "october"),
    ("november",), ("dezember", "december"),
)
MONTH_NAMES = {f"{index:02d}": frozenset(names) for index, names in enumerate(_MONTHS, 1)}

NEGATION = re.compile(r"\b(?:nicht|nie|niemals|kein\w*|ohne|not|never|no|without)\b", re.IGNORECASE)
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
WORD = re.compile(r"[^\W\d_]+(?:[+#]+)?", re.UNICODE)


def _numeric_values(text: str) -> set[str]:
    """Numbers in a canonical form, so "3" and "3.0" compare equal.

    A German decimal comma is read as a decimal point. Anything that is not a
    plain number is kept verbatim and therefore still has to match exactly.
    """
    values = set()
    for token in NUMBER.findall(text):
        canonical = token.replace(",", ".")
        try:
            values.add(str(float(canonical)))
        except ValueError:
            values.add(canonical)
    return values


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
            # A citation anywhere in the sentence counts. Requiring it in final
            # position rejected correct answers over punctuation alone.
            if (not indices or not claim or any(i < 1 or i > len(sources) for i in indices)
                    or "[" in claim or "]" in claim):
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
        # Compare values, not spelling: the row stores "3.0" while a natural
        # answer says "3 Jahre". A year or a grade the row does not contain is
        # still rejected.
        if not _numeric_values(claim) <= _numeric_values(evidence):
            return False
        # Only the claim's own negation is decisive. Evidence is a whole row, and
        # a single unrelated "nie" in a long description (PostFinance: "das
        # Sprachmodell rechnet nie") otherwise rejected every plain statement
        # about that row. A claim that negates what the row asserts still has to
        # clear the similarity threshold.
        if NEGATION.search(claim) and not NEGATION.search(evidence):
            return False
        # Entity check: an invented name such as "Google" is still rejected, but
        # German declension is not. "Vereinen" and "Vereine" share a stem, so the
        # claim is no longer discarded for grammar alone. This heuristic does not
        # establish logical entailment.
        evidence_words = {word.casefold() for word in WORD.findall(evidence)}
        # Rows store dates as 2020-08-10, so no month name appears anywhere in
        # the corpus, and a natural "am 10. August 2020" looked invented. Only
        # the months the row actually contains are added, so a wrong month is
        # still caught.
        for month in ISO_DATE.findall(evidence):
            evidence_words |= MONTH_NAMES.get(month, frozenset())
        evidence_stems = {word[:STEM_LENGTH] for word in evidence_words
                          if len(word) >= STEM_LENGTH}
        vocabulary, blob = cached_corpus_terms()
        entities = cached_corpus_entities()
        allowed = FUNCTION_WORDS | COMMON_WORDS | cached_subject_names()
        for word in WORD.findall(claim):
            lowered = word.casefold()
            if (not word[0].isupper() or lowered in allowed or lowered in evidence_words
                    or (len(lowered) >= STEM_LENGTH
                        and (lowered[:STEM_LENGTH] in evidence_stems
                             or lowered[:STEM_LENGTH] in COMMON_STEMS))):
                continue
            # Named in the portfolio but belonging to a different row: this is a
            # cross-row mixup, such as citing the room booker's "Microsoft" as a
            # technology of the PostFinance project.
            if lowered in entities:
                return False
            # Ordinary German the portfolio itself uses ("Projekt", "Sprache",
            # also inside a compound) asserts no entity; the similarity score
            # still has to support the sentence.
            if lowered in vocabulary or (len(lowered) >= STEM_LENGTH and lowered in blob):
                continue
            # Neither ordinary German nor anything the portfolio mentions: the
            # model introduced it ("Google", "ETH").
            return False
        return True

    # German sentence rules are shared with the excerpt fallback; see
    # sentence_service. Kept as methods because callers and tests use them.
    _continues_sentence = staticmethod(continues_sentence)
    _split_into_sentences = staticmethod(split_sentences)

    def verify_with_threshold(self, response, sources, threshold):
        return self.verify_response(response, sources, threshold=threshold)


_verifier_service = None


def get_verifier_service():
    global _verifier_service
    if _verifier_service is None:
        _verifier_service = VerifierService()
    return _verifier_service
