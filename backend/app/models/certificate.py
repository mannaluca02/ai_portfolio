from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP
from pgvector.sqlalchemy import Vector
from app.database import Base
from datetime import datetime


class Certificate(Base):
    """Certificate Model"""
    __tablename__ = "certificates"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    issuing_organization = Column(String(255), nullable=False)
    
    # Dates
    issue_date = Column(Date, nullable=False, index=True)
    expiration_date = Column(Date)  # NULL = no expiration
    
    # Verification
    credential_id = Column(String(255))
    
    # Content
    description = Column(Text)
    
    # Media
    certificate_url = Column(Text)  # URL to certificate image/PDF
    
    # For pgvector & Links
    embedding = Column(Vector(1024))
    slug = Column(String(255), unique=True, nullable=False, index=True)
    section = Column(String(100), default='certificates')
    anchor = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Certificate(id={self.id}, name='{self.name}', issuer='{self.issuing_organization}')>"
