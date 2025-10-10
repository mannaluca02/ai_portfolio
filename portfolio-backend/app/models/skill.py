from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, DECIMAL
from sqlalchemy.dialects.postgresql import ENUM
from pgvector.sqlalchemy import Vector
from app.database import Base
from datetime import datetime


# Skill Level Enum
skill_level_enum = ENUM(
    'Beginner',
    'Intermediate',
    'Advanced',
    'Expert',
    name='skill_level',
    create_type=False  # Type already exists in DB
)

# Skill Category Enum
skill_category_enum = ENUM(
    'Backend',
    'Frontend',
    'DevOps',
    'Database',
    'Cloud',
    'Mobile',
    'Design',
    'Testing',
    'Tools',
    'Soft Skills',
    name='skill_category',
    create_type=False  # Type already exists in DB
)


class Skill(Base):
    """Skill Model"""
    __tablename__ = "skills"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False, unique=True)
    skill_level = Column(skill_level_enum, default='Intermediate')
    category = Column(skill_category_enum, nullable=False, index=True)
    
    # Experience
    years_of_experience = Column(DECIMAL(3, 1))  # e.g., 5.5 years
    
    # Content
    description = Column(Text)
    
    # For pgvector & Links
    embedding = Column(Vector(1024))
    slug = Column(String(255), unique=True, nullable=False, index=True)
    section = Column(String(100), default='skills')
    anchor = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Skill(id={self.id}, name='{self.name}', level='{self.skill_level}')>"
