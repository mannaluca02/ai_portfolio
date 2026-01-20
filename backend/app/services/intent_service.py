"""
Intent Detection Service - Query Analysis and Table Routing
Determines which database tables should be searched based on user query
"""
from typing import List, Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)


class QueryIntent:
    """Represents the detected intent of a user query"""

    def __init__(
        self,
        tables: List[str],
        priority: str = "balanced",
        boost_factors: Optional[Dict[str, float]] = None,
        description: str = ""
    ):
        """
        Args:
            tables: List of table names to search
            priority: Search priority ("strict", "focused", "balanced")
            boost_factors: Optional dict of table -> boost multiplier
            description: Human-readable intent description
        """
        self.tables = tables
        self.priority = priority
        self.boost_factors = boost_factors or {}
        self.description = description

    def __repr__(self):
        return f"QueryIntent(tables={self.tables}, priority={self.priority}, description='{self.description}')"


class IntentService:
    """Service for detecting user intent and routing queries to appropriate tables"""

    # Contact-related keywords
    CONTACT_KEYWORDS = [
        "kontakt", "kontaktieren", "erreichen", "erreichbar",
        "email", "e-mail", "mail",
        "github", "linkedin", "twitter", "social", "socials",
        "profil", "link", "links"
    ]

    # Technical experience keywords
    TECH_EXPERIENCE_KEYWORDS = [
        "erfahrung mit", "erfahrung in",
        "kann", "kennt", "kenntnisse",
        "beherrscht", "beherrschung",
        "verwendet", "nutzt", "arbeitet mit",
        "skills", "fähigkeiten", "technologien"
    ]

    # Work/Company keywords
    WORK_KEYWORDS = [
        "firma", "firmen", "unternehmen",
        "arbeitgeber", "employer",
        "position", "rolle", "job", "stelle",
        "arbeitet bei", "gearbeitet bei",
        "angestellt", "beschäftigt"
    ]

    # Project keywords
    PROJECT_KEYWORDS = [
        "projekt", "projekte", "project", "projects",
        "entwickelt", "gebaut", "erstellt",
        "portfolio", "arbeit", "arbeiten"
    ]

    # Education keywords
    EDUCATION_KEYWORDS = [
        "studium", "studiert", "student",
        "universität", "hochschule", "uni",
        "abschluss", "degree", "bachelor", "master",
        "ausbildung", "bildung"
    ]

    # Certificate keywords
    CERTIFICATE_KEYWORDS = [
        "zertifikat", "zertifikate", "certificate",
        "zertifizierung", "zertifiziert",
        "qualifikation", "nachweis"
    ]

    def detect_intent(self, query: str) -> QueryIntent:
        """
        Detect the intent of a user query and determine which tables to search

        Args:
            query: User's query text

        Returns:
            QueryIntent: Detected intent with table routing information
        """
        query_lower = query.lower()

        logger.info(f"Detecting intent for query: {query[:50]}...")

        # 1. CONTACT INTENT (exclusive - high priority)
        if self._contains_keywords(query_lower, self.CONTACT_KEYWORDS):
            logger.info("Detected: CONTACT intent")
            return QueryIntent(
                tables=["contact_info", "social_links"],
                priority="strict",
                description="Contact information request"
            )

        # 2. TECHNICAL EXPERIENCE INTENT (projects + work, then skills)
        if self._contains_keywords(query_lower, self.TECH_EXPERIENCE_KEYWORDS):
            logger.info("Detected: TECHNICAL EXPERIENCE intent")
            return QueryIntent(
                tables=["projects", "work_experiences", "skills"],
                priority="focused",
                boost_factors={"projects": 1.5, "work_experiences": 1.3},
                description="Technical skills/experience question"
            )

        # 3. WORK/COMPANY INTENT
        if self._contains_keywords(query_lower, self.WORK_KEYWORDS):
            logger.info("Detected: WORK/COMPANY intent")
            return QueryIntent(
                tables=["work_experiences", "projects"],
                priority="focused",
                boost_factors={"work_experiences": 1.5},
                description="Work history question"
            )

        # 4. PROJECT INTENT
        if self._contains_keywords(query_lower, self.PROJECT_KEYWORDS):
            logger.info("Detected: PROJECT intent")
            return QueryIntent(
                tables=["projects", "work_experiences"],
                priority="focused",
                boost_factors={"projects": 1.5},
                description="Project portfolio question"
            )

        # 5. EDUCATION INTENT
        if self._contains_keywords(query_lower, self.EDUCATION_KEYWORDS):
            logger.info("Detected: EDUCATION intent")
            return QueryIntent(
                tables=["education", "certificates"],
                priority="focused",
                boost_factors={"education": 1.3},
                description="Education/academic question"
            )

        # 6. CERTIFICATE INTENT
        if self._contains_keywords(query_lower, self.CERTIFICATE_KEYWORDS):
            logger.info("Detected: CERTIFICATE intent")
            return QueryIntent(
                tables=["certificates", "education"],
                priority="focused",
                boost_factors={"certificates": 1.3},
                description="Certification question"
            )

        # 7. DEFAULT INTENT (exclude contact, prioritize meaningful content)
        logger.info("Detected: DEFAULT intent (general question)")
        return QueryIntent(
            tables=["projects", "work_experiences", "education", "certificates", "skills"],
            priority="balanced",
            description="General portfolio question"
        )

    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """
        Check if text contains any of the specified keywords

        Args:
            text: Text to search in (should be lowercase)
            keywords: List of keywords to search for

        Returns:
            bool: True if any keyword is found
        """
        for keyword in keywords:
            # Use word boundaries for exact matches
            if keyword in text:
                return True
        return False

    def should_exclude_table(self, table: str, intent: QueryIntent) -> bool:
        """
        Determine if a table should be excluded based on intent

        Args:
            table: Table name
            intent: Detected query intent

        Returns:
            bool: True if table should be excluded
        """
        return table not in intent.tables


# Global instance
_intent_service = None


def get_intent_service() -> IntentService:
    """Get the global intent service instance"""
    global _intent_service
    if _intent_service is None:
        _intent_service = IntentService()
    return _intent_service
