"""
Test database models
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_db_session
from app.models import WorkExperience, Project, Skill, Certificate, Education, Hobby, ContactInfo, SocialLink
from sqlalchemy import text
from datetime import date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_models():
    """Test all database models"""
    db = get_db_session()
    
    try:
        logger.info("Testing database models...\n")
        
        # Test 1: Check if tables exist
        logger.info("Test 1: Checking if tables exist...")
        tables = ['work_experiences', 'projects', 'skills', 'certificates', 'education', 'hobbies', 'contact_info', 'social_links']
        
        for table in tables:
            result = db.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                );
            """))
            exists = result.scalar()
            if exists:
                logger.info(f"  ✅ Table '{table}' exists")
            else:
                logger.error(f"  ❌ Table '{table}' NOT found!")
                return False
        
        # Test 2: Query existing data
        logger.info("\nTest 2: Querying existing data...")
        
        # Work Experiences
        work_exp_count = db.query(WorkExperience).count()
        logger.info(f"  ✅ WorkExperience: {work_exp_count} entries")
        
        # Projects
        project_count = db.query(Project).count()
        logger.info(f"  ✅ Project: {project_count} entries")
        
        # Skills
        skill_count = db.query(Skill).count()
        logger.info(f"  ✅ Skill: {skill_count} entries")
        
        # Certificates
        cert_count = db.query(Certificate).count()
        logger.info(f"  ✅ Certificate: {cert_count} entries")
        
        # Education
        edu_count = db.query(Education).count()
        logger.info(f"  ✅ Education: {edu_count} entries")

        # Hobbies
        hobby_count = db.query(Hobby).count()
        logger.info(f"  ✅ Hobby: {hobby_count} entries")

        # Contact Info
        contact_count = db.query(ContactInfo).count()
        logger.info(f"  ✅ ContactInfo: {contact_count} entries")

        # Social Links
        social_count = db.query(SocialLink).count()
        logger.info(f"  ✅ SocialLink: {social_count} entries")
        
        # Test 3: Fetch sample data
        logger.info("\nTest 3: Fetching sample data...")
        
        # Get first work experience
        work_exp = db.query(WorkExperience).first()
        if work_exp:
            logger.info(f"  ✅ Sample WorkExperience: {work_exp.company} - {work_exp.position}")
        
        # Get first project
        project = db.query(Project).first()
        if project:
            logger.info(f"  ✅ Sample Project: {project.name}")
        
        # Get first skill
        skill = db.query(Skill).first()
        if skill:
            logger.info(f"  ✅ Sample Skill: {skill.name} ({skill.skill_level})")

        # Get first hobby
        hobby = db.query(Hobby).first()
        if hobby:
            logger.info(f"  ✅ Sample Hobby: {hobby.name}")

        # Get first contact info
        contact = db.query(ContactInfo).first()
        if contact:
            logger.info(f"  ✅ Sample ContactInfo: {contact.full_name}")

        # Get first social link
        social = db.query(SocialLink).first()
        if social:
            logger.info(f"  ✅ Sample SocialLink: {social.platform} - {social.url}")
        
        # Test 4: Test model attributes
        logger.info("\nTest 4: Testing model attributes...")
        
        if work_exp:
            # Check if embedding column exists (even if NULL)
            has_embedding = hasattr(work_exp, 'embedding')
            logger.info(f"  ✅ WorkExperience has embedding attribute: {has_embedding}")
            
            # Check slug, section, anchor
            logger.info(f"  ✅ WorkExperience slug: {work_exp.slug}")
            logger.info(f"  ✅ WorkExperience section: {work_exp.section}")
            logger.info(f"  ✅ WorkExperience anchor: {work_exp.anchor}")
        
        logger.info("\n✅ All model tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = test_models()
    sys.exit(0 if success else 1)
