"""
Project Schemas
Pydantic models for project API responses
"""
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime, date


class ProjectResponse(BaseModel):
    """Project Response Schema"""
    id: int
    name: str
    description: str
    project_type: str
    featured: bool
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_url: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    technologies: List[str]
    your_role: Optional[str] = None
    team_size: Optional[int] = None
    client_company: Optional[str] = None
    image_urls: Optional[List[str]] = None
    slug: str
    section: str
    anchor: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
