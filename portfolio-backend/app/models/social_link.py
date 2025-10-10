from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from pgvector.sqlalchemy import Vector
from app.database import Base
from datetime import datetime


class SocialLink(Base):
    """Social Link Model"""
    __tablename__ = "social_links"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    platform = Column(String(100), nullable=False, index=True)  # e.g., "GitHub", "LinkedIn"
    url = Column(Text, nullable=False)
    username = Column(String(255))
    
    # Display
    icon_name = Column(String(100))  # e.g., "github", "linkedin" for icon lookup
    display_order = Column(Integer, default=0)
    
    # For pgvector & Links (optional for social)
    embedding = Column(Vector(1024))
    slug = Column(String(255), unique=True, nullable=False, index=True)
    section = Column(String(100), default='social')
    anchor = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SocialLink(id={self.id}, platform='{self.platform}')>"
