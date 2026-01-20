"""
Education API Routes
Endpoints for retrieving education records
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.education import Education
from app.schemas.education import EducationResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["education"])


@router.get(
    "/education",
    response_model=List[EducationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get education records",
    description="Retrieve all education records ordered by start date (newest first)"
)
async def get_education(db: Session = Depends(get_db)) -> List[EducationResponse]:
    """
    Get education records

    **Returns:**
    - List of education records ordered by start_date DESC

    **Example Response:**
    ```json
    [
        {
            "id": 1,
            "institution": "ETH Zürich",
            "degree": "Master of Science in Computer Science",
            "degree_type": "Master",
            "field_of_study": "Computer Science",
            "location": "Zürich, Schweiz",
            "start_date": "2018-09-01",
            "end_date": "2020-08-31",
            "grade": "1.5",
            "description": "Focus on Machine Learning and Distributed Systems",
            "achievements": [
                "Thesis on Deep Learning for NLP",
                "Dean's List 2019"
            ],
            "institution_logo_url": "https://example.com/eth-logo.png",
            "slug": "education-eth-master",
            "section": "education",
            "anchor": "eth-master",
            "created_at": "2024-10-10T20:00:00",
            "updated_at": "2024-10-10T20:00:00"
        }
    ]
    ```
    """
    try:
        # Get all education records ordered by start date (newest first)
        education_records = db.query(Education).order_by(Education.start_date.desc()).all()

        if not education_records:
            logger.info("No education records found in database")
            return []

        return education_records

    except Exception as e:
        logger.error(f"Error retrieving education records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve education records"
        )
