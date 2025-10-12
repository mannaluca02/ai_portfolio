"""
Work Experience API Routes
Endpoints for retrieving work experiences
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.work_experience import WorkExperience
from app.schemas.work import WorkExperienceResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["work"])


@router.get(
    "/work-experiences",
    response_model=List[WorkExperienceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get work experiences",
    description="Retrieve all work experiences ordered by start date (newest first)"
)
async def get_work_experiences(db: Session = Depends(get_db)) -> List[WorkExperienceResponse]:
    """
    Get work experiences

    **Returns:**
    - List of work experiences ordered by start_date DESC (newest first)

    **Example Response:**
    ```json
    [
        {
            "id": 1,
            "company": "TechVision AG",
            "position": "Senior Full-Stack Developer",
            "location": "Basel, Schweiz",
            "employment_type": "Vollzeit",
            "start_date": "2021-03-01",
            "end_date": null,
            "description": "Entwicklung und Wartung von Enterprise-Web-Anwendungen...",
            "responsibilities": [
                "Design und Implementierung von RESTful APIs mit FastAPI",
                "Entwicklung von React-basierten Single-Page-Applications"
            ],
            "technologies": ["Python", "FastAPI", "React", "TypeScript"],
            "company_logo_url": null,
            "slug": "work-techvision-ag-2021",
            "section": "experience",
            "anchor": "techvision-ag-2021",
            "created_at": "2024-10-10T20:00:00",
            "updated_at": "2024-10-10T20:00:00"
        }
    ]
    ```
    """
    try:
        # Get all work experiences ordered by start_date DESC (newest first)
        work_experiences = db.query(WorkExperience).order_by(
            WorkExperience.start_date.desc()
        ).all()

        if not work_experiences:
            logger.info("No work experiences found in database")
            return []

        return work_experiences

    except Exception as e:
        logger.error(f"Error retrieving work experiences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve work experiences"
        )
