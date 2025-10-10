from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from pgvector.sqlalchemy import Vector
from app.database import Base
from datetime import datetime


class Hobby(Base):
    """Hobby Model"""
    __tablename__ = "hobbies"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    since_year = Column(Integer)  # e.g., 2015
    
    # Media
    icon_url = Column(Text)
    image_url = Column(Text)
    
    # For pgvector & Links
    embedding = Column(Vector(1024))
    slug = Column(String(255), unique=True, nullable=False, index=True)
    section = Column(String(100), default='hobbies')
    anchor = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Hobby(id={self.id}, name='{self.name}')>"
