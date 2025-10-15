"""
Retriever Service - pgvector Similarity Search
Performs semantic search across portfolio data using embeddings
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import WorkExperience, Project, Skill, Certificate, Education, Hobby, ContactInfo, SocialLink
from app.services.embedding_service import get_embedding_service
from app.services.intent_service import get_intent_service, QueryIntent
from typing import List, Dict, Any, Optional
import logging
import numpy as np
import json

logger = logging.getLogger(__name__)


class SearchResult:
    """Search result with similarity score"""
    def __init__(self, id: int, table: str, title: str, content: str,
                 slug: str, section: str, anchor: str, similarity: float, data: Dict[Any, Any],
                 embedding: Optional[np.ndarray] = None):
        self.id = id
        self.table = table
        self.title = title
        self.content = content
        self.slug = slug
        self.section = section
        self.anchor = anchor
        self.similarity = similarity
        self.data = data
        self.embedding = embedding  # Store for MMR diversification
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "table": self.table,
            "title": self.title,
            "content": self.content,
            "slug": self.slug,
            "section": self.section,
            "anchor": self.anchor,
            "similarity": self.similarity,
            "data": self.data
        }


class RetrieverService:
    """Service for semantic search using pgvector"""
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = get_embedding_service()
        self.intent_service = get_intent_service()
    
    def search(self, query: str, limit: int = 5, similarity_threshold: float = 0.6,
               tables: Optional[List[str]] = None, use_mmr: bool = True,
               intent: Optional[QueryIntent] = None) -> List[SearchResult]:
        """
        Perform semantic search across all tables with intent-based routing

        Args:
            query: Search query text
            limit: Maximum number of final results
            similarity_threshold: Minimum similarity score (0-1)
            tables: Optional list of table names to search (overrides intent)
            use_mmr: Apply MMR diversification (default: True)
            intent: Optional pre-detected query intent

        Returns:
            List[SearchResult]: Sorted list of search results
        """
        try:
            # Detect intent if not provided
            if intent is None:
                intent = self.intent_service.detect_intent(query)
                logger.info(f"Detected intent: {intent.description}")

            # Use intent tables if no explicit tables provided
            search_tables = tables if tables else intent.tables

            # Generate query embedding
            logger.info(f"Generating embedding for query: {query[:50]}...")
            query_embedding = self.embedding_service.generate_embedding(query)

            # Convert to list for SQL
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

            # Define tables to search
            all_tables = {
                'work_experiences': self._format_work_experience,
                'projects': self._format_project,
                'skills': self._format_skill,
                'certificates': self._format_certificate,
                'education': self._format_education,
                'hobbies': self._format_hobby,
                'contact_info': self._format_contact_info,
                'social_links': self._format_social_link
            }

            # Search across specified tables
            all_results = []
            for table_name in search_tables:
                if table_name not in all_tables:
                    logger.warning(f"Unknown table: {table_name}")
                    continue

                # Get boost factor from intent
                boost_factor = intent.boost_factors.get(table_name, 1.0)

                results = self._search_table(
                    table_name,
                    embedding_str,
                    limit * 3,  # Get more candidates for MMR
                    similarity_threshold,
                    all_tables[table_name],
                    query_embedding
                )

                # Apply boost factor to similarity scores
                if boost_factor != 1.0:
                    for result in results:
                        result.similarity *= boost_factor
                        # Clamp to max 1.0
                        result.similarity = min(result.similarity, 1.0)

                all_results.extend(results)

            # Sort by similarity (highest first)
            all_results.sort(key=lambda x: x.similarity, reverse=True)

            # Apply MMR diversification if enabled
            if use_mmr and len(all_results) > limit:
                logger.info(f"Applying MMR diversification to {len(all_results)} candidates...")
                all_results = self._apply_mmr(query_embedding, all_results, limit * 2, lambda_param=0.5)

            # Return only the requested number of results (not limit * 2)
            # This prevents overwhelming the LLM with too many sources
            final_results = all_results[:limit]
            logger.info(f"Returning {len(final_results)} results (threshold={similarity_threshold})")

            return final_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def _search_table(self, table_name: str, embedding_str: str, limit: int,
                      threshold: float, formatter, query_embedding: np.ndarray) -> List[SearchResult]:
        """Search a single table using pgvector"""
        try:
            # pgvector similarity search using cosine distance (<=>)
            # Similarity = 1 - cosine_distance
            # Use cast() to convert string to vector type
            query = text(f"""
                SELECT
                    *,
                    1 - (embedding <=> cast(:embedding as vector)) as similarity
                FROM {table_name}
                WHERE embedding IS NOT NULL
                    AND 1 - (embedding <=> cast(:embedding as vector)) >= :threshold
                ORDER BY embedding <=> cast(:embedding as vector)
                LIMIT :limit
            """)

            result = self.db.execute(
                query,
                {
                    "embedding": embedding_str,
                    "threshold": threshold,
                    "limit": limit
                }
            )

            rows = result.fetchall()
            results = []

            for row in rows:
                search_result = formatter(row, table_name)
                results.append(search_result)

            logger.info(f"Found {len(results)} results in {table_name}")
            return results

        except Exception as e:
            logger.error(f"Failed to search {table_name}: {e}")
            return []

    def _apply_mmr(self, query_embedding: np.ndarray, candidates: List[SearchResult],
                   k: int, lambda_param: float = 0.5) -> List[SearchResult]:
        """
        Apply Maximal Marginal Relevance to diversify results

        Args:
            query_embedding: Query embedding vector
            candidates: List of candidate search results
            k: Number of results to select
            lambda_param: Balance between relevance and diversity (0-1)
                         1.0 = only relevance, 0.0 = only diversity, 0.5 = balanced

        Returns:
            List[SearchResult]: Diversified results
        """
        if len(candidates) <= k:
            return candidates

        selected = []
        remaining = candidates.copy()

        while len(selected) < k and remaining:
            if not selected:
                # First document: highest relevance
                best = remaining[0]  # Already sorted by similarity
                selected.append(best)
                remaining.remove(best)
            else:
                # Calculate MMR score for each remaining candidate
                best_score = float('-inf')
                best_doc = None

                for candidate in remaining:
                    # Relevance score (already normalized 0-1)
                    relevance = candidate.similarity

                    # Calculate max similarity to already selected documents
                    max_sim_to_selected = 0.0
                    if candidate.embedding is not None:
                        for selected_doc in selected:
                            if selected_doc.embedding is not None:
                                sim = self._cosine_similarity(
                                    candidate.embedding,
                                    selected_doc.embedding
                                )
                                max_sim_to_selected = max(max_sim_to_selected, sim)

                    # MMR score: balance relevance and diversity
                    mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim_to_selected

                    if mmr_score > best_score:
                        best_score = mmr_score
                        best_doc = candidate

                if best_doc:
                    selected.append(best_doc)
                    remaining.remove(best_doc)
                else:
                    break

        logger.info(f"MMR selected {len(selected)} diverse results from {len(candidates)} candidates")
        return selected

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)
    
    def _format_work_experience(self, row, table_name: str) -> SearchResult:
        """Format work experience result"""
        # Parse embedding from database (stored as string)
        embedding = self._parse_embedding(row.embedding) if hasattr(row, 'embedding') and row.embedding else None

        return SearchResult(
            id=row.id,
            table=table_name,
            title=f"{row.position} at {row.company}",
            content=row.description,
            slug=row.slug,
            section=row.section,
            anchor=row.anchor,
            similarity=float(row.similarity),
            data={
                "company": row.company,
                "position": row.position,
                "location": row.location,
                "employment_type": row.employment_type,
                "start_date": str(row.start_date) if row.start_date else None,
                "end_date": str(row.end_date) if row.end_date else None,
                "technologies": row.technologies
            },
            embedding=embedding
        )
    
    def _format_project(self, row, table_name: str) -> SearchResult:
        """Format project result"""
        embedding = self._parse_embedding(row.embedding) if hasattr(row, 'embedding') and row.embedding else None

        return SearchResult(
            id=row.id,
            table=table_name,
            title=row.name,
            content=row.description,
            slug=row.slug,
            section=row.section,
            anchor=row.anchor,
            similarity=float(row.similarity),
            data={
                "name": row.name,
                "project_type": row.project_type,
                "technologies": row.technologies,
                "your_role": row.your_role,
                "project_url": row.project_url,
                "github_url": row.github_url
            },
            embedding=embedding
        )
    
    def _format_skill(self, row, table_name: str) -> SearchResult:
        """Format skill result"""
        embedding = self._parse_embedding(row.embedding) if hasattr(row, 'embedding') and row.embedding else None

        return SearchResult(
            id=row.id,
            table=table_name,
            title=row.name,
            content=row.description or f"{row.name} - {row.skill_level}",
            slug=row.slug,
            section=row.section,
            anchor=row.anchor,
            similarity=float(row.similarity),
            data={
                "name": row.name,
                "skill_level": row.skill_level,
                "category": row.category,
                "years_of_experience": float(row.years_of_experience) if row.years_of_experience else None
            },
            embedding=embedding
        )
    
    def _format_certificate(self, row, table_name: str) -> SearchResult:
        """Format certificate result"""
        embedding = self._parse_embedding(row.embedding) if hasattr(row, 'embedding') and row.embedding else None

        return SearchResult(
            id=row.id,
            table=table_name,
            title=row.name,
            content=row.description or f"{row.name} from {row.issuing_organization}",
            slug=row.slug,
            section=row.section,
            anchor=row.anchor,
            similarity=float(row.similarity),
            data={
                "name": row.name,
                "issuing_organization": row.issuing_organization,
                "issue_date": str(row.issue_date) if row.issue_date else None,
                "credential_id": row.credential_id
            },
            embedding=embedding
        )
    
    def _format_education(self, row, table_name: str) -> SearchResult:
        """Format education result"""
        embedding = self._parse_embedding(row.embedding) if hasattr(row, 'embedding') and row.embedding else None

        return SearchResult(
            id=row.id,
            table=table_name,
            title=f"{row.degree} at {row.institution}",
            content=row.description or f"{row.degree} in {row.field_of_study}",
            slug=row.slug,
            section=row.section,
            anchor=row.anchor,
            similarity=float(row.similarity),
            data={
                "institution": row.institution,
                "degree": row.degree,
                "degree_type": row.degree_type,
                "field_of_study": row.field_of_study,
                "grade": row.grade
            },
            embedding=embedding
        )
    
    def _format_hobby(self, row, table_name: str) -> SearchResult:
        """Format hobby result"""
        embedding = self._parse_embedding(row.embedding) if hasattr(row, 'embedding') and row.embedding else None

        return SearchResult(
            id=row.id,
            table=table_name,
            title=row.name,
            content=row.description,
            slug=row.slug,
            section=row.section,
            anchor=row.anchor,
            similarity=float(row.similarity),
            data={
                "name": row.name,
                "since_year": row.since_year
            },
            embedding=embedding
        )
    
    def _format_contact_info(self, row, table_name: str) -> SearchResult:
        """Format contact info result"""
        embedding = self._parse_embedding(row.embedding) if hasattr(row, 'embedding') and row.embedding else None

        return SearchResult(
            id=row.id,
            table=table_name,
            title=row.full_name,
            content=row.bio or f"{row.title}",
            slug=row.slug,
            section=row.section,
            anchor=row.anchor,
            similarity=float(row.similarity),
            data={
                "full_name": row.full_name,
                "title": row.title,
                "email": row.email,
                "city": row.city,
                "country": row.country
            },
            embedding=embedding
        )
    
    def _format_social_link(self, row, table_name: str) -> SearchResult:
        """Format social link result"""
        embedding = self._parse_embedding(row.embedding) if hasattr(row, 'embedding') and row.embedding else None

        return SearchResult(
            id=row.id,
            table=table_name,
            title=f"{row.platform}",
            content=row.url,
            slug=row.slug,
            section=row.section,
            anchor=row.anchor,
            similarity=float(row.similarity),
            data={
                "platform": row.platform,
                "url": row.url,
                "username": row.username
            },
            embedding=embedding
        )

    def _parse_embedding(self, embedding_str: str) -> Optional[np.ndarray]:
        """
        Parse embedding from database string format to numpy array

        Args:
            embedding_str: Embedding as string (e.g., "[0.1, 0.2, ...]")

        Returns:
            np.ndarray or None if parsing fails
        """
        try:
            if not embedding_str:
                return None

            # pgvector returns embeddings as strings like "[0.1,0.2,...]"
            if isinstance(embedding_str, str):
                # Remove brackets and split by comma
                embedding_str = embedding_str.strip('[]')
                values = [float(x.strip()) for x in embedding_str.split(',')]
                return np.array(values, dtype=np.float32)
            elif isinstance(embedding_str, (list, np.ndarray)):
                return np.array(embedding_str, dtype=np.float32)
            else:
                return None

        except Exception as e:
            logger.warning(f"Failed to parse embedding: {e}")
            return None
