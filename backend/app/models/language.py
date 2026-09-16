from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import TIMESTAMP, Column, Integer, String, Text

from app.database import Base


class Language(Base):
    """Spoken language. Programming languages are skills, not languages."""
    __tablename__ = "languages"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    name = Column(String(100), nullable=False, unique=True)  # e.g., "Deutsch"
    level = Column(String(120), nullable=False)  # e.g., "Muttersprache", "B2 (Cambridge English: First)"
    description = Column(Text)

    # For pgvector & Links
    embedding = Column(Vector(1024))
    slug = Column(String(255), unique=True, nullable=False)
    # The skills section is what a source link scrolls to; there is no separate
    # languages section on the page.
    section = Column(String(100), default='skills')
    anchor = Column(String(255), nullable=False)

    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Language(id={self.id}, name='{self.name}', level='{self.level}')>"
