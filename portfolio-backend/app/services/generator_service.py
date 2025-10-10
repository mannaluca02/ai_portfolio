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

    def generate_response(self, query: str, search_results: List[SearchResult]) -> Dict[str, Any]:
        """
        Generate a natural language response based on search results

        Args:
            query: User's question
            search_results: List of relevant documents from retriever

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

            # Build context from search results
            context = self._build_context(search_results)

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
                temperature=0.7,
                max_tokens=500,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            # Extract answer
            answer = response.choices[0].message.content.strip()

            # Extract sources with metadata
            sources = self._extract_sources(search_results)

            # Calculate confidence (average similarity score)
            confidence = sum(r.similarity for r in search_results) / len(search_results)

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
        return """Du bist ein hilfreicher Assistent, der Fragen über Luca Manna's Portfolio beantwortet.

WICHTIGE REGELN:
1. Beantworte Fragen basierend NUR auf den bereitgestellten Kontext-Dokumenten
2. Verwende IMMER Quellenzitate im Format [1], [2], [3] etc.
3. Wenn die Information nicht im Kontext ist, sage das ehrlich
4. Antworte auf Deutsch in einem professionellen aber freundlichen Ton
5. Sei präzise und konkret - keine vagen Aussagen
6. Vermeide Wiederholungen

QUELLENZITATE:
- Jede Aussage MUSS mit einer Quelle belegt werden
- Format: "Luca hat Erfahrung mit Python [1] und React [2]."
- Mehrere Quellen: [1][2] wenn beide dieselbe Info bestätigen

ANTWORTSTRUKTUR:
- Beginne direkt mit der Antwort (keine Floskeln wie "Basierend auf...")
- Strukturiere längere Antworten mit Absätzen
- Verwende Aufzählungen für Listen von Skills/Projekten"""

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
