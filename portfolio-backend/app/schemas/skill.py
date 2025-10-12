"""
Skill Schemas
Pydantic models for skill API responses
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class SkillResponse(BaseModel):
    """Skill Response Schema"""
    id: int
    name: str
    skill_level: str
    category: str
    years_of_experience: Optional[Decimal] = None
    description: Optional[str] = None
    slug: str
    section: str
    anchor: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
