"""
Education Schemas
Pydantic models for education API responses
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class EducationResponse(BaseModel):
    """Education Response Schema"""
    id: int
    institution: str
    degree: str
    degree_type: str
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    achievements: Optional[List[str]] = None
    institution_logo_url: Optional[str] = None
    slug: str
    section: str
    anchor: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
