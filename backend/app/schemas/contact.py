"""
Contact Info Schemas
Pydantic models for contact info API responses
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ContactInfoResponse(BaseModel):
    """Contact Info Response Schema"""
    id: int
    full_name: str
    title: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    availability: Optional[str] = None
    profile_image_url: Optional[str] = None
    resume_pdf_url: Optional[str] = None
    bio: Optional[str] = None
    slug: str
    section: str
    anchor: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
