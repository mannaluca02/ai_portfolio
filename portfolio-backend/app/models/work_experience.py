from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import ENUM
from pgvector.sqlalchemy import Vector
from app.database import Base
from datetime import datetime


# Employment Type Enum
employment_type_enum = ENUM(
    'Vollzeit',
    'Teilzeit',
    'Freelance',
    'Praktikum',
    'Werkstudent',
    name='employment_type',
    create_type=False  # Type already exists in DB
)


class WorkExperience(Base):
    """Work Experience Model"""
    __tablename__ = "work_experiences"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    location = Column(String(255))
    employment_type = Column(employment_type_enum, default='Vollzeit')
    
    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  # NULL = current position
    
    # Content
    description = Column(Text, nullable=False)
    responsibilities = Column(ARRAY(Text))  # Array of responsibilities
    technologies = Column(ARRAY(Text))  # Array of technologies
    
    # Media
    company_logo_url = Column(Text)
    
    # For pgvector & Links
    embedding = Column(Vector(1024))  # bge-m3 produces 1024 dimensions
    slug = Column(String(255), unique=True, nullable=False, index=True)
    section = Column(String(100), default='experience')
    anchor = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<WorkExperience(id={self.id}, company='{self.company}', position='{self.position}')>"
