"""Word-boundary intent hints for ranking, never for excluding evidence."""
import re
from collections.abc import Sequence

PORTFOLIO_TABLES = (
    "work_experiences", "projects", "skills", "certificates", "education",
    "hobbies", "contact_info", "social_links", "languages",
)
# Rows about the person rather than about a topic. They match almost any
# question about him and then outrank the row that answers it, so each is damped
# unless the question actually asks for that side of the portfolio. Damping
# lowers rank only: the evidence stays available to the model either way.
PROFILE_TABLES = ("contact_info", "social_links")
PROFILE_DAMPING = 0.75
DAMPED_UNLESS_ASKED = {
    "contact_info": ("contact", "personal"),
    "social_links": ("contact", "personal"),
    # Measured on the live corpus: "Heim Netzwerk" scored 0.519 for "Kann er
    # Docker?" and 0.434 for "Wo hat luca gearbeitet?", above the rows that
    # answer either question.
    "hobbies": ("hobbies",),
}


class QueryIntent:
    """Compatibility container; tables are hints, not a retrieval allowlist."""

    def __init__(self, tables: list[str], priority: str = "balanced",
                 boost_factors: dict[str, float] | None = None, description: str = ""):
        self.tables = tables
        self.priority = priority
        self.boost_factors = boost_factors or {}
        self.description = description

    def __repr__(self):
        return f"QueryIntent(tables={self.tables}, priority={self.priority}, description={self.description!r})"


class IntentService:
    CONTACT_KEYWORDS = (
        "kontakt", "kontaktieren", "erreichen", "erreichbar", "email", "e-mail",
        "mail", "github", "linkedin", "twitter", "social", "socials", "profil", "link", "links",
    )
    TECH_EXPERIENCE_KEYWORDS = (
        "erfahrung mit", "erfahrung in", "kann", "kennt", "kenntnisse", "beherrscht",
        "beherrschung", "verwendet", "nutzt", "arbeitet mit", "skills", "fähigkeiten", "technologien",
    )
    WORK_KEYWORDS = (
        "firma", "firmen", "unternehmen", "arbeitgeber", "employer", "position",
        "rolle", "job", "stelle", "arbeitet bei", "gearbeitet", "angestellt", "beschäftigt",
    )
    PROJECT_KEYWORDS = (
        "projekt", "projekte", "projekten", "project", "projects", "entwickelt",
        "gebaut", "erstellt", "portfolio", "arbeit", "arbeiten",
    )
    EDUCATION_KEYWORDS = (
        "studium", "studiert", "student", "universität", "hochschule", "uni",
        "abschluss", "degree", "bachelor", "master", "ausbildung", "bildung",
    )
    # Questions about the person rather than a topic. Without these, "Wie alt
    # ist er?" was damped away from contact_info, which is the only row that
    # can answer it.
    PERSONAL_KEYWORDS = (
        "alt", "alter", "geboren", "geburtstag", "geburtsdatum", "jahrgang",
        "age", "born", "wohnt", "wohnort", "lebt", "wer ist", "wer bist",
        "ueber dich", "über dich", "vorstellen",
    )
    # Spoken languages only. Word boundaries keep "Programmiersprache" out, so a
    # question about programming languages still routes to skills and projects.
    LANGUAGE_KEYWORDS = (
        "sprache", "sprachen", "spricht", "sprichst", "sprechen", "muttersprache",
        "deutsch", "englisch", "französisch", "franzoesisch", "italienisch",
        "language", "languages", "speak", "speaks", "fluent", "niveau", "cefr", "ger",
    )
    HOBBY_KEYWORDS = (
        "hobby", "hobbys", "hobbies", "freizeit", "freizeitaktivität", "privat",
        "privatleben", "sport", "sportlich", "interessen", "interesse",
        "ausgleich", "nebenbei", "neben der arbeit", "neben dem studium",
    )
    CERTIFICATE_KEYWORDS = (
        "zertifikat", "zertifikate", "certificate", "zertifizierung", "zertifiziert",
        "qualifikation", "nachweis",
    )

    def detect_intent(self, query: str) -> QueryIntent:
        # Combine hints rather than allowing a contact/project match to hide
        # skills, education, hobbies, or profile evidence.
        rules = (
            (self.CONTACT_KEYWORDS, {"contact_info": 1.3, "social_links": 1.3}, "contact"),
            (self.TECH_EXPERIENCE_KEYWORDS, {"projects": 1.5, "work_experiences": 1.3}, "technical"),
            (self.WORK_KEYWORDS, {"work_experiences": 1.5}, "work"),
            (self.PROJECT_KEYWORDS, {"projects": 1.5}, "projects"),
            (self.EDUCATION_KEYWORDS, {"education": 1.3}, "education"),
            (self.CERTIFICATE_KEYWORDS, {"certificates": 1.3}, "certificates"),
            (self.PERSONAL_KEYWORDS, {"contact_info": 1.4}, "personal"),
            (self.HOBBY_KEYWORDS, {"hobbies": 1.4}, "hobbies"),
            (self.LANGUAGE_KEYWORDS, {"languages": 1.4}, "languages"),
        )
        boosts: dict[str, float] = {}
        matched = []
        for keywords, weights, name in rules:
            if self._contains_keywords(query, keywords):
                matched.append(name)
                for table, weight in weights.items():
                    boosts[table] = max(boosts.get(table, 1.0), weight)
        asked = set(matched)
        for table, intents in DAMPED_UNLESS_ASKED.items():
            # Damp instead of exclude: a genuine question about that side of the
            # portfolio must still be answerable, and the keyword rules above
            # lift the table back up when one is asked.
            if not asked & set(intents):
                boosts.setdefault(table, PROFILE_DAMPING)
        return QueryIntent(tables=list(PORTFOLIO_TABLES), boost_factors=boosts,
                           description=", ".join(matched) or "general")

    @staticmethod
    def _contains_keywords(text: str, keywords: Sequence[str]) -> bool:
        text = text.casefold()
        return any(re.search(r"(?<!\w)" + re.escape(keyword.casefold()).replace(r"\ ", r"\s+")
                             + r"(?!\w)", text) is not None for keyword in keywords)

    @staticmethod
    def should_exclude_table(table: str, intent: QueryIntent) -> bool:
        """Retained for callers: only unknown tables are excluded, never by intent."""
        return table not in PORTFOLIO_TABLES


_intent_service = None


def get_intent_service() -> IntentService:
    global _intent_service
    if _intent_service is None:
        _intent_service = IntentService()
    return _intent_service
