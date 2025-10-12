"""
Contact Info API Routes
Endpoints for retrieving contact information
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.contact_info import ContactInfo
from app.schemas.contact import ContactInfoResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["contact"])


@router.get(
    "/contact-info",
    response_model=ContactInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Get contact information",
    description="Retrieve the primary contact information from the database"
)
async def get_contact_info(db: Session = Depends(get_db)) -> ContactInfoResponse:
    """
    Get contact information

    **Returns:**
    - Contact information including name, title, email, location, availability, and bio

    **Example Response:**
    ```json
    {
        "id": 1,
        "full_name": "Max Mustermann",
        "title": "Senior Full-Stack Developer",
        "email": "max.mustermann@example.com",
        "phone": "+41 76 123 45 67",
        "city": "Basel",
        "country": "Schweiz",
        "availability": "Verfügbar für neue Projekte ab März 2025",
        "bio": "Leidenschaftlicher Full-Stack Developer...",
        "profile_image_url": null,
        "resume_pdf_url": null,
        "slug": "contact",
        "section": "contact",
        "anchor": "contact",
        "created_at": "2024-10-10T20:00:00",
        "updated_at": "2024-10-10T20:00:00"
    }
    ```
    """
    try:
        # Get the first (and should be only) contact info record
        contact_info = db.query(ContactInfo).first()

        if not contact_info:
            logger.warning("No contact info found in database")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact information not found"
            )

        return contact_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving contact info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contact information"
        )
