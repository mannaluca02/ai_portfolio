"""
Work Experience Schemas
Pydantic models for work experience API responses
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class WorkExperienceResponse(BaseModel):
    """Work Experience Response Schema"""
    id: int
    company: str
    position: str
    location: Optional[str] = None
    employment_type: str
    start_date: date
    end_date: Optional[date] = None
    description: str
    responsibilities: List[str]
    technologies: List[str]
    company_logo_url: Optional[str] = None
    slug: str
    section: str
    anchor: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
