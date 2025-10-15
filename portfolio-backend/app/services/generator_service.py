"""
Generator Service - OpenAI GPT-3.5 Response Generation
Generates natural language responses with source citations
"""
from openai import OpenAI
from app.config import settings
from app.services.retriever_service import SearchResult
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GeneratorService:
    """Service for generating natural language responses using OpenAI"""

    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-3.5-turbo"

    def generate_response(self, query: str, search_results: List[SearchResult],
                         max_context_sources: int = 8) -> Dict[str, Any]:
        """
        Generate a natural language response based on search results

        Args:
            query: User's question
            search_results: List of relevant documents from retriever
            max_context_sources: Maximum number of sources to include in LLM context (default: 8)

        Returns:
            Dict containing response, sources, and metadata
        """
        try:
            # Check if we have any search results
            if not search_results:
                return {
                    "answer": "Ich habe leider keine relevanten Informationen zu deiner Frage gefunden.",
                    "sources": [],
                    "mode": "natural",
                    "confidence": 0.0
                }

            # Limit context to top N most relevant sources
            # Too many sources confuse the LLM and cause incorrect citation numbers
            context_sources = search_results[:max_context_sources]

            logger.info(f"Using top {len(context_sources)} of {len(search_results)} sources for LLM context")

            # Build context from limited search results
            context = self._build_context(context_sources)

            # Build system prompt
            system_prompt = self._build_system_prompt()

            # Build user prompt
            user_prompt = self._build_user_prompt(query, context)

            logger.info(f"Generating response for query: {query[:50]}...")

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower for factual, precise responses
                max_tokens=700,   # More room for detailed answers
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            # Extract answer
            answer = response.choices[0].message.content.strip()

            # Extract sources with metadata (only from context sources used)
            sources = self._extract_sources(context_sources)

            # Calculate confidence (average similarity score of context sources)
            confidence = sum(r.similarity for r in context_sources) / len(context_sources)

            logger.info(f"✅ Response generated (confidence: {confidence:.2f})")

            return {
                "answer": answer,
                "sources": sources,
                "mode": "natural",
                "confidence": confidence,
                "model": self.model,
                "tokens_used": response.usage.total_tokens
            }

        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the LLM"""
        return """Du bist ein präziser Assistent für ein Portfolio-Profil.

KRITISCHE REGELN FÜR QUELLENZITATE:
1. JEDE Aussage MUSS mit einer Quellenangabe enden: [1], [2], [3] etc.
2. Verwende NUR Quellennummern die im KONTEXT-DOKUMENTE Bereich aufgelistet sind
3. Zitiere in der EXAKTEN Reihenfolge wie die Quellen nummeriert sind
4. Format: "Hat Erfahrung mit Python [1] und arbeitete mit React [2]."
5. Mehrere Quellen für einen Fakt: [1][2] wenn beide denselben Punkt bestätigen

INFORMATIONSQUELLE:
- Nutze AUSSCHLIESSLICH die bereitgestellten Kontext-Dokumente
- Wenn keine passende Quelle existiert: "Dazu finde ich keine Information in meinen Daten."
- NIEMALS eigenes Wissen oder Vermutungen hinzufügen
- NIEMALS Quellennummern erfinden die nicht im Kontext existieren

ANTWORTFORMAT:
- Beginne direkt mit der Antwort (keine Floskeln wie "Basierend auf...")
- Kurze, präzise Sätze - jeder Satz endet mit [N]
- Bei mehreren Punkten: Bulletpoints verwenden:
  • Erster Punkt mit Quelle [1]
  • Zweiter Punkt mit Quelle [2]
- Professioneller aber freundlicher Ton auf Deutsch

VERBOTEN:
- Aussagen ohne Quellenangabe [N]
- Vage Formulierungen ohne Beleg
- Wiederholungen derselben Information
- Quellennummern die nicht im Kontext-Bereich stehen"""

    def _build_context(self, search_results: List[SearchResult]) -> str:
        """Build context string from search results"""
        context_parts = []

        for i, result in enumerate(search_results, 1):
            context_parts.append(f"[{i}] {result.title}")
            context_parts.append(f"    Typ: {result.table}")
            context_parts.append(f"    Inhalt: {result.content}")

            # Add relevant data fields
            if result.table == "work_experiences":
                context_parts.append(f"    Firma: {result.data.get('company')}")
                context_parts.append(f"    Position: {result.data.get('position')}")
                context_parts.append(f"    Technologien: {result.data.get('technologies')}")
            elif result.table == "projects":
                context_parts.append(f"    Typ: {result.data.get('project_type')}")
                context_parts.append(f"    Technologien: {result.data.get('technologies')}")
                context_parts.append(f"    Rolle: {result.data.get('your_role')}")
            elif result.table == "skills":
                context_parts.append(f"    Level: {result.data.get('skill_level')}")
                context_parts.append(f"    Kategorie: {result.data.get('category')}")
                years = result.data.get('years_of_experience')
                if years:
                    context_parts.append(f"    Erfahrung: {years} Jahre")

            context_parts.append("")  # Empty line between sources

        return "\n".join(context_parts)

    def _build_user_prompt(self, query: str, context: str) -> str:
        """Build the user prompt with query and context"""
        return f"""KONTEXT-DOKUMENTE:
{context}

FRAGE: {query}

Beantworte die Frage basierend auf den obigen Kontext-Dokumenten. Verwende Quellenzitate [1], [2], etc."""

    def _extract_sources(self, search_results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Extract source metadata for citations"""
        sources = []

        for i, result in enumerate(search_results, 1):
            sources.append({
                "index": i,
                "title": result.title,
                "table": result.table,
                "slug": result.slug,
                "section": result.section,
                "anchor": result.anchor,
                "similarity": result.similarity
            })

        return sources


# Global instance
_generator_service = None


def get_generator_service() -> GeneratorService:
    """Get the global generator service instance"""
    global _generator_service
    if _generator_service is None:
        _generator_service = GeneratorService()
    return _generator_service
