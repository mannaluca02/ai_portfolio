"""
Skill API Routes
Endpoints for retrieving skills
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.skill import Skill
from app.schemas.skill import SkillResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["skills"])


@router.get(
    "/skills",
    response_model=List[SkillResponse],
    status_code=status.HTTP_200_OK,
    summary="Get skills",
    description="Retrieve all skills grouped by category and ordered by skill level"
)
async def get_skills(db: Session = Depends(get_db)) -> List[SkillResponse]:
    """
    Get skills

    **Returns:**
    - List of skills ordered by category and skill_level DESC

    **Example Response:**
    ```json
    [
        {
            "id": 1,
            "name": "Python",
            "skill_level": "Expert",
            "category": "Backend",
            "years_of_experience": 8.0,
            "description": "Hauptprogrammiersprache für Backend-Entwicklung",
            "slug": "skill-python",
            "section": "skills",
            "anchor": "python",
            "created_at": "2024-10-10T20:00:00",
            "updated_at": "2024-10-10T20:00:00"
        }
    ]
    ```
    """
    try:
        # Define skill level order for sorting
        skill_level_order = {
            'Expert': 4,
            'Advanced': 3,
            'Intermediate': 2,
            'Beginner': 1
        }

        # Get all skills
        skills = db.query(Skill).all()

        if not skills:
            logger.info("No skills found in database")
            return []

        # Sort by category, then by skill level (Expert first)
        sorted_skills = sorted(
            skills,
            key=lambda s: (s.category, -skill_level_order.get(s.skill_level, 0))
        )

        return sorted_skills

    except Exception as e:
        logger.error(f"Error retrieving skills: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve skills"
        )
