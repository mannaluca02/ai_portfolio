"""
Retriever Service - pgvector Similarity Search
Performs semantic search across portfolio data using embeddings
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import WorkExperience, Project, Skill, Certificate, Education, Hobby, ContactInfo, SocialLink
from app.services.embedding_service import get_embedding_service
from typing import List, Dict, Any, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)


class SearchResult:
    """Search result with similarity score"""
    def __init__(self, id: int, table: str, title: str, content: str, 
                 slug: str, section: str, anchor: str, similarity: float, data: Dict[Any, Any]):
        self.id = id
        self.table = table
        self.title = title
        self.content = content
        self.slug = slug
        self.section = section
        self.anchor = anchor
        self.similarity = similarity
        self.data = data
    
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
    
    def search(self, query: str, limit: int = 5, similarity_threshold: float = 0.6,
               tables: Optional[List[str]] = None) -> List[SearchResult]:
        """
        Perform semantic search across all tables
        
        Args:
            query: Search query text
            limit: Maximum number of results per table
            similarity_threshold: Minimum similarity score (0-1)
            tables: Optional list of table names to search (default: all)
            
        Returns:
            List[SearchResult]: Sorted list of search results
        """
        try:
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
            
            search_tables = tables if tables else list(all_tables.keys())
            
            # Search across all specified tables
            all_results = []
            for table_name in search_tables:
                if table_name not in all_tables:
                    logger.warning(f"Unknown table: {table_name}")
                    continue
                
                results = self._search_table(
                    table_name, 
                    embedding_str, 
                    limit, 
                    similarity_threshold,
                    all_tables[table_name]
                )
                all_results.extend(results)
            
            # Sort by similarity (highest first)
            all_results.sort(key=lambda x: x.similarity, reverse=True)
            
            logger.info(f"Found {len(all_results)} results above threshold {similarity_threshold}")
            return all_results[:limit * 2]  # Return top results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def _search_table(self, table_name: str, embedding_str: str, limit: int,
                      threshold: float, formatter) -> List[SearchResult]:
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
    
    def _format_work_experience(self, row, table_name: str) -> SearchResult:
        """Format work experience result"""
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
            }
        )
    
    def _format_project(self, row, table_name: str) -> SearchResult:
        """Format project result"""
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
            }
        )
    
    def _format_skill(self, row, table_name: str) -> SearchResult:
        """Format skill result"""
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
            }
        )
    
    def _format_certificate(self, row, table_name: str) -> SearchResult:
        """Format certificate result"""
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
            }
        )
    
    def _format_education(self, row, table_name: str) -> SearchResult:
        """Format education result"""
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
            }
        )
    
    def _format_hobby(self, row, table_name: str) -> SearchResult:
        """Format hobby result"""
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
            }
        )
    
    def _format_contact_info(self, row, table_name: str) -> SearchResult:
        """Format contact info result"""
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
            }
        )
    
    def _format_social_link(self, row, table_name: str) -> SearchResult:
        """Format social link result"""
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
            }
        )
