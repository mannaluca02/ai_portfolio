"""
Certificate API Routes
Endpoints for retrieving certificates
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["certificates"])


@router.get(
    "/certificates",
    response_model=List[CertificateResponse],
    status_code=status.HTTP_200_OK,
    summary="Get certificates",
    description="Retrieve all certificates ordered by issue date (newest first)"
)
async def get_certificates(db: Session = Depends(get_db)) -> List[CertificateResponse]:
    """
    Get certificates

    **Returns:**
    - List of certificates ordered by issue_date DESC

    **Example Response:**
    ```json
    [
        {
            "id": 1,
            "name": "AWS Certified Solutions Architect",
            "issuing_organization": "Amazon Web Services",
            "issue_date": "2023-06-15",
            "expiration_date": "2026-06-15",
            "credential_id": "AWS-CSA-123456",
            "description": "Professional-level certification for AWS solutions architects",
            "certificate_url": "https://example.com/cert.pdf",
            "slug": "certificate-aws-solutions-architect",
            "section": "certificates",
            "anchor": "aws-solutions-architect",
            "created_at": "2024-10-10T20:00:00",
            "updated_at": "2024-10-10T20:00:00"
        }
    ]
    ```
    """
    try:
        # Get all certificates ordered by issue date (newest first)
        certificates = db.query(Certificate).order_by(Certificate.issue_date.desc()).all()

        if not certificates:
            logger.info("No certificates found in database")
            return []

        return certificates

    except Exception as e:
        logger.error(f"Error retrieving certificates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve certificates"
        )
