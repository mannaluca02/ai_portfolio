"""
Social Links Schemas
Pydantic models for social links API responses
"""
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class SocialLinkResponse(BaseModel):
    """Social Link Response Schema"""
    id: int
    platform: str
    url: str
    username: Optional[str] = None
    icon_name: Optional[str] = None
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
