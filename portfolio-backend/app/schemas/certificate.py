"""
Certificate Schemas
Pydantic models for certificate API responses
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class CertificateResponse(BaseModel):
    """Certificate Response Schema"""
    id: int
    name: str
    issuing_organization: str
    issue_date: date
    expiration_date: Optional[date] = None
    credential_id: Optional[str] = None
    description: Optional[str] = None
    certificate_url: Optional[str] = None
    slug: str
    section: str
    anchor: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
