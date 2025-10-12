from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import ENUM
from pgvector.sqlalchemy import Vector
from app.database import Base
from datetime import datetime


# Project Type Enum
project_type_enum = ENUM(
    'Personal',
    'Professional',
    'Open Source',
    'Client Work',
    name='project_type',
    create_type=False  # Type already exists in DB
)


class Project(Base):
    """Project Model"""
    __tablename__ = "projects"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    project_type = Column(project_type_enum, default='Personal')
    featured = Column(Boolean, default=False, nullable=False)

    # Dates
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Links
    project_url = Column(Text)
    github_url = Column(Text)
    demo_url = Column(Text)
    
    # Details
    technologies = Column(ARRAY(Text))  # Array of technologies
    your_role = Column(String(255))
    team_size = Column(Integer)
    client_company = Column(String(255))  # if client work
    
    # Media
    image_urls = Column(ARRAY(Text))  # Array of image URLs
    
    # For pgvector & Links
    embedding = Column(Vector(1024))
    slug = Column(String(255), unique=True, nullable=False, index=True)
    section = Column(String(100), default='projects')
    anchor = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', type='{self.project_type}')>"
