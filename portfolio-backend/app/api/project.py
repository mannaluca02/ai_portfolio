"""
Project API Routes
Endpoints for retrieving projects
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["projects"])


@router.get(
    "/projects",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Get projects",
    description="Retrieve all projects ordered by start date (newest first)"
)
async def get_projects(db: Session = Depends(get_db)) -> List[ProjectResponse]:
    """
    Get projects

    **Returns:**
    - List of projects ordered by start_date DESC (newest first)

    **Example Response:**
    ```json
    [
        {
            "id": 1,
            "name": "E-Commerce Platform Redesign",
            "description": "Komplettes Redesign und technische Modernisierung...",
            "project_type": "Professional",
            "start_date": "2022-06-01",
            "end_date": "2023-03-31",
            "project_url": "https://shop-example.com",
            "github_url": null,
            "demo_url": null,
            "technologies": ["React", "Next.js", "Node.js", "PostgreSQL"],
            "your_role": "Lead Developer",
            "team_size": 4,
            "client_company": null,
            "image_urls": [],
            "slug": "project-ecommerce-redesign",
            "section": "projects",
            "anchor": "ecommerce-redesign",
            "created_at": "2024-10-10T20:00:00",
            "updated_at": "2024-10-10T20:00:00"
        }
    ]
    ```
    """
    try:
        # Get all projects ordered by start_date DESC (newest first), with nulls last
        projects = db.query(Project).order_by(
            Project.start_date.desc().nullslast()
        ).all()

        if not projects:
            logger.info("No projects found in database")
            return []

        return projects

    except Exception as e:
        logger.error(f"Error retrieving projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )
