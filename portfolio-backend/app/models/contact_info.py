from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from pgvector.sqlalchemy import Vector
from app.database import Base
from datetime import datetime


class ContactInfo(Base):
    """Contact Info Model"""
    __tablename__ = "contact_info"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Personal
    full_name = Column(String(255), nullable=False)
    title = Column(String(255))  # e.g., "Senior Full-Stack Developer"
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    
    # Location
    city = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Professional
    availability = Column(String(100))  # e.g., "Verfügbar ab Januar 2025"
    
    # Media
    profile_image_url = Column(Text)
    resume_pdf_url = Column(Text)
    
    # Bio
    bio = Column(Text)  # Short bio for about section
    
    # For pgvector & Links (optional for contact)
    embedding = Column(Vector(1024))
    slug = Column(String(255), unique=True, default='contact')
    section = Column(String(100), default='contact')
    anchor = Column(String(255), default='contact')
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ContactInfo(id={self.id}, name='{self.full_name}')>"
