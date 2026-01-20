"""
Generate embeddings for all existing data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_db_session
from app.models import WorkExperience, Project, Skill, Certificate, Education, Hobby, ContactInfo, SocialLink
from app.services.embedding_service import get_embedding_service
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_embeddings():
    """Generate embeddings for all portfolio data"""
    db = get_db_session()
    embedding_service = get_embedding_service()
    
    try:
        logger.info("Generating embeddings for portfolio data...\n")
        
        # Work Experiences
        logger.info("Processing work_experiences...")
        work_exps = db.query(WorkExperience).all()
        for exp in work_exps:
            text = f"{exp.position} at {exp.company}. {exp.description}"
            embedding = embedding_service.generate_embedding(text)
            exp.embedding = embedding.tolist()
        db.commit()
        logger.info(f"✅ Generated {len(work_exps)} work experience embeddings")
        
        # Projects
        logger.info("\nProcessing projects...")
        projects = db.query(Project).all()
        for proj in projects:
            text = f"{proj.name}. {proj.description}"
            embedding = embedding_service.generate_embedding(text)
            proj.embedding = embedding.tolist()
        db.commit()
        logger.info(f"✅ Generated {len(projects)} project embeddings")
        
        # Skills
        logger.info("\nProcessing skills...")
        skills = db.query(Skill).all()
        for skill in skills:
            text = f"{skill.name} - {skill.skill_level}. {skill.description or ''}"
            embedding = embedding_service.generate_embedding(text)
            skill.embedding = embedding.tolist()
        db.commit()
        logger.info(f"✅ Generated {len(skills)} skill embeddings")
        
        # Certificates
        logger.info("\nProcessing certificates...")
        certs = db.query(Certificate).all()
        for cert in certs:
            text = f"{cert.name} from {cert.issuing_organization}. {cert.description or ''}"
            embedding = embedding_service.generate_embedding(text)
            cert.embedding = embedding.tolist()
        db.commit()
        logger.info(f"✅ Generated {len(certs)} certificate embeddings")
        
        # Education
        logger.info("\nProcessing education...")
        edu_list = db.query(Education).all()
        for edu in edu_list:
            text = f"{edu.degree} in {edu.field_of_study or ''} at {edu.institution}. {edu.description or ''}"
            embedding = embedding_service.generate_embedding(text)
            edu.embedding = embedding.tolist()
        db.commit()
        logger.info(f"✅ Generated {len(edu_list)} education embeddings")
        
        # Hobbies
        logger.info("\nProcessing hobbies...")
        hobbies = db.query(Hobby).all()
        for hobby in hobbies:
            text = f"{hobby.name}. {hobby.description}"
            embedding = embedding_service.generate_embedding(text)
            hobby.embedding = embedding.tolist()
        db.commit()
        logger.info(f"✅ Generated {len(hobbies)} hobby embeddings")
        
        # Contact Info
        logger.info("\nProcessing contact_info...")
        contacts = db.query(ContactInfo).all()
        for contact in contacts:
            text = f"{contact.full_name}, {contact.title}. {contact.bio or ''}"
            embedding = embedding_service.generate_embedding(text)
            contact.embedding = embedding.tolist()
        db.commit()
        logger.info(f"✅ Generated {len(contacts)} contact embeddings")
        
        # Social Links
        logger.info("\nProcessing social_links...")
        socials = db.query(SocialLink).all()
        for social in socials:
            text = f"{social.platform}: {social.url}"
            embedding = embedding_service.generate_embedding(text)
            social.embedding = embedding.tolist()
        db.commit()
        logger.info(f"✅ Generated {len(socials)} social link embeddings")
        
        logger.info("\n✅ All embeddings generated successfully!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Failed to generate embeddings: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = generate_embeddings()
    sys.exit(0 if success else 1)
