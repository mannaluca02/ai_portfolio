from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import ENUM
from pgvector.sqlalchemy import Vector
from app.database import Base
from datetime import datetime


# Degree Type Enum
degree_type_enum = ENUM(
    'Bachelor',
    'Master',
    'Diplom',
    'PhD',
    'Ausbildung',
    'Zertifikat',
    'Sonstige',
    name='degree_type',
    create_type=False  # Type already exists in DB
)


class Education(Base):
    """Education Model"""
    __tablename__ = "education"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    degree_type = Column(degree_type_enum, nullable=False)
    field_of_study = Column(String(255))
    location = Column(String(255))
    
    # Dates
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date)  # NULL = ongoing
    
    # Details
    grade = Column(String(50))  # e.g., "1.5" or "Sehr gut"
    description = Column(Text)
    achievements = Column(ARRAY(Text))  # Array of achievements
    
    # Media
    institution_logo_url = Column(Text)
    
    # For pgvector & Links
    embedding = Column(Vector(1024))
    slug = Column(String(255), unique=True, nullable=False, index=True)
    section = Column(String(100), default='education')
    anchor = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Education(id={self.id}, degree='{self.degree}', institution='{self.institution}')>"
