"""
Social Links API Routes
Endpoints for retrieving social media links
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.social_link import SocialLink
from app.schemas.social import SocialLinkResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["social"])


@router.get(
    "/social-links",
    response_model=List[SocialLinkResponse],
    status_code=status.HTTP_200_OK,
    summary="Get social media links",
    description="Retrieve all social media links ordered by display order"
)
async def get_social_links(db: Session = Depends(get_db)) -> List[SocialLinkResponse]:
    """
    Get social media links

    **Returns:**
    - List of social media links ordered by display_order

    **Example Response:**
    ```json
    [
        {
            "id": 1,
            "platform": "GitHub",
            "url": "https://github.com/maxmustermann",
            "username": "maxmustermann",
            "icon_name": "github",
            "display_order": 1,
            "created_at": "2024-10-10T20:00:00",
            "updated_at": "2024-10-10T20:00:00"
        },
        {
            "id": 2,
            "platform": "LinkedIn",
            "url": "https://linkedin.com/in/maxmustermann",
            "username": "maxmustermann",
            "icon_name": "linkedin",
            "display_order": 2,
            "created_at": "2024-10-10T20:00:00",
            "updated_at": "2024-10-10T20:00:00"
        }
    ]
    ```
    """
    try:
        # Get all social links ordered by display_order
        social_links = db.query(SocialLink).order_by(SocialLink.display_order).all()

        if not social_links:
            logger.info("No social links found in database")
            return []

        return social_links

    except Exception as e:
        logger.error(f"Error retrieving social links: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve social links"
        )
