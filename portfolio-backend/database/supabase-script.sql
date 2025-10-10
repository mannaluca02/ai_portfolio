-- =====================================================
-- Portfolio Database Setup - Complete SQL Script
-- PostgreSQL mit pgvector Extension
-- =====================================================

-- =====================================================
-- 1. EXTENSIONS
-- =====================================================

-- pgvector Extension für Vector Similarity Search
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- 2. ENUMS & TYPES
-- =====================================================

-- Employment Type für Work Experiences
CREATE TYPE employment_type AS ENUM (
    'Vollzeit',
    'Teilzeit',
    'Freelance',
    'Praktikum',
    'Werkstudent'
);

-- Project Type
CREATE TYPE project_type AS ENUM (
    'Personal',
    'Professional',
    'Open Source',
    'Client Work'
);

-- Skill Level
CREATE TYPE skill_level AS ENUM (
    'Beginner',
    'Intermediate',
    'Advanced',
    'Expert'
);

-- Skill Category
CREATE TYPE skill_category AS ENUM (
    'Backend',
    'Frontend',
    'DevOps',
    'Database',
    'Cloud',
    'Mobile',
    'Design',
    'Testing',
    'Tools',
    'Soft Skills'
);

-- Education Degree Type
CREATE TYPE degree_type AS ENUM (
    'Bachelor',
    'Master',
    'Diplom',
    'PhD',
    'Ausbildung',
    'Zertifikat',
    'Sonstige'
);

-- =====================================================
-- 3. MAIN TABLES
-- =====================================================

-- -----------------------------------------------------
-- 3.1 WORK EXPERIENCES
-- -----------------------------------------------------
CREATE TABLE work_experiences (
    id SERIAL PRIMARY KEY,
    
    -- Basic Information
    company VARCHAR(255) NOT NULL,
    position VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    employment_type employment_type DEFAULT 'Vollzeit',
    
    -- Dates
    start_date DATE NOT NULL,
    end_date DATE, -- NULL = current position
    
    -- Content
    description TEXT NOT NULL,
    responsibilities TEXT[], -- Array of responsibilities
    technologies TEXT[], -- Array of technologies used
    
    -- Media
    company_logo_url TEXT,
    
    -- For pgvector & Links
    embedding VECTOR(1024), -- bge-m3 produces 1024 dimensions
    slug VARCHAR(255) UNIQUE NOT NULL,
    section VARCHAR(100) DEFAULT 'experience',
    anchor VARCHAR(255) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- -----------------------------------------------------
-- 3.2 PROJECTS
-- -----------------------------------------------------
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    project_type project_type DEFAULT 'Personal',
    
    -- Dates
    start_date DATE,
    end_date DATE,
    
    -- Links
    project_url TEXT,
    github_url TEXT,
    demo_url TEXT,
    
    -- Details
    technologies TEXT[], -- Array of technologies
    your_role VARCHAR(255),
    team_size INTEGER,
    client_company VARCHAR(255), -- if client work
    
    -- Media
    image_urls TEXT[], -- Array of image URLs
    
    -- For pgvector & Links
    embedding VECTOR(1024),
    slug VARCHAR(255) UNIQUE NOT NULL,
    section VARCHAR(100) DEFAULT 'projects',
    anchor VARCHAR(255) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- -----------------------------------------------------
-- 3.3 SKILLS
-- -----------------------------------------------------
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    
    -- Basic Information
    name VARCHAR(255) NOT NULL UNIQUE,
    skill_level skill_level DEFAULT 'Intermediate',
    category skill_category NOT NULL,
    
    -- Experience
    years_of_experience DECIMAL(3,1), -- e.g., 5.5 years
    
    -- Content
    description TEXT,
    
    -- For pgvector & Links
    embedding VECTOR(1024),
    slug VARCHAR(255) UNIQUE NOT NULL,
    section VARCHAR(100) DEFAULT 'skills',
    anchor VARCHAR(255) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- -----------------------------------------------------
-- 3.4 CERTIFICATES
-- -----------------------------------------------------
CREATE TABLE certificates (
    id SERIAL PRIMARY KEY,
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255) NOT NULL,
    
    -- Dates
    issue_date DATE NOT NULL,
    expiration_date DATE, -- NULL = no expiration
    
    -- Verification
    credential_id VARCHAR(255),
    
    -- Content
    description TEXT,
    
    -- Media
    certificate_url TEXT, -- URL to certificate image/PDF
    
    -- For pgvector & Links
    embedding VECTOR(1024),
    slug VARCHAR(255) UNIQUE NOT NULL,
    section VARCHAR(100) DEFAULT 'certificates',
    anchor VARCHAR(255) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- -----------------------------------------------------
-- 3.5 HOBBIES
-- -----------------------------------------------------
CREATE TABLE hobbies (
    id SERIAL PRIMARY KEY,
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    since_year INTEGER, -- e.g., 2015
    
    -- Media
    icon_url TEXT,
    image_url TEXT,
    
    -- For pgvector & Links
    embedding VECTOR(1024),
    slug VARCHAR(255) UNIQUE NOT NULL,
    section VARCHAR(100) DEFAULT 'hobbies',
    anchor VARCHAR(255) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- -----------------------------------------------------
-- 3.6 EDUCATION
-- -----------------------------------------------------
CREATE TABLE education (
    id SERIAL PRIMARY KEY,
    
    -- Basic Information
    institution VARCHAR(255) NOT NULL,
    degree VARCHAR(255) NOT NULL,
    degree_type degree_type NOT NULL,
    field_of_study VARCHAR(255),
    location VARCHAR(255),
    
    -- Dates
    start_date DATE NOT NULL,
    end_date DATE, -- NULL = ongoing
    
    -- Details
    grade VARCHAR(50), -- e.g., "1.5" or "Sehr gut"
    description TEXT,
    achievements TEXT[], -- Array of achievements
    
    -- Media
    institution_logo_url TEXT,
    
    -- For pgvector & Links
    embedding VECTOR(1024),
    slug VARCHAR(255) UNIQUE NOT NULL,
    section VARCHAR(100) DEFAULT 'education',
    anchor VARCHAR(255) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- -----------------------------------------------------
-- 3.7 CONTACT INFO
-- -----------------------------------------------------
CREATE TABLE contact_info (
    id SERIAL PRIMARY KEY,
    
    -- Personal
    full_name VARCHAR(255) NOT NULL,
    title VARCHAR(255), -- e.g., "Senior Full-Stack Developer"
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    
    -- Location
    city VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    
    -- Professional
    availability VARCHAR(100), -- e.g., "Verfügbar ab Januar 2025"
    
    -- Media
    profile_image_url TEXT,
    resume_pdf_url TEXT,
    
    -- Bio
    bio TEXT, -- Short bio for about section
    
    -- For pgvector & Links (optional for contact)
    embedding VECTOR(1024),
    slug VARCHAR(255) UNIQUE DEFAULT 'contact',
    section VARCHAR(100) DEFAULT 'contact',
    anchor VARCHAR(255) DEFAULT 'contact',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- -----------------------------------------------------
-- 3.8 SOCIAL LINKS
-- -----------------------------------------------------
CREATE TABLE social_links (
    id SERIAL PRIMARY KEY,
    
    -- Basic Information
    platform VARCHAR(100) NOT NULL, -- e.g., "GitHub", "LinkedIn", "Twitter"
    url TEXT NOT NULL,
    username VARCHAR(255),
    
    -- Display
    icon_name VARCHAR(100), -- e.g., "github", "linkedin" for icon lookup
    display_order INTEGER DEFAULT 0,
    
    -- For pgvector & Links (optional for social)
    embedding VECTOR(1024),
    slug VARCHAR(255) UNIQUE NOT NULL,
    section VARCHAR(100) DEFAULT 'social',
    anchor VARCHAR(255) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(platform, url)
);

-- =====================================================
-- 4. INDICES FOR PERFORMANCE
-- =====================================================

-- pgvector Indices (HNSW for better performance)
CREATE INDEX idx_work_experiences_embedding ON work_experiences 
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_projects_embedding ON projects 
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_skills_embedding ON skills 
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_certificates_embedding ON certificates 
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_hobbies_embedding ON hobbies 
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_education_embedding ON education 
USING hnsw (embedding vector_cosine_ops);

-- Regular Indices
CREATE INDEX idx_work_experiences_dates ON work_experiences(start_date, end_date);
CREATE INDEX idx_work_experiences_slug ON work_experiences(slug);

CREATE INDEX idx_projects_dates ON projects(start_date, end_date);
CREATE INDEX idx_projects_slug ON projects(slug);

CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_slug ON skills(slug);

CREATE INDEX idx_certificates_dates ON certificates(issue_date, expiration_date);
CREATE INDEX idx_certificates_slug ON certificates(slug);

CREATE INDEX idx_education_dates ON education(start_date, end_date);
CREATE INDEX idx_education_slug ON education(slug);

CREATE INDEX idx_social_links_platform ON social_links(platform);

-- =====================================================
-- 5. TRIGGER FUNCTIONS (für auto-update timestamps)
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach triggers to all tables
CREATE TRIGGER update_work_experiences_updated_at
    BEFORE UPDATE ON work_experiences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skills_updated_at
    BEFORE UPDATE ON skills
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_certificates_updated_at
    BEFORE UPDATE ON certificates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hobbies_updated_at
    BEFORE UPDATE ON hobbies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_education_updated_at
    BEFORE UPDATE ON education
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contact_info_updated_at
    BEFORE UPDATE ON contact_info
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_social_links_updated_at
    BEFORE UPDATE ON social_links
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 6. SAMPLE DATA
-- =====================================================

-- -----------------------------------------------------
-- 6.1 CONTACT INFO
-- -----------------------------------------------------
INSERT INTO contact_info (
    full_name, title, email, phone, city, country,
    availability, bio, slug, anchor
) VALUES (
    'Max Mustermann',
    'Senior Full-Stack Developer',
    'max.mustermann@example.com',
    '+41 76 123 45 67',
    'Basel',
    'Schweiz',
    'Verfügbar für neue Projekte ab März 2025',
    'Leidenschaftlicher Full-Stack Developer mit 8+ Jahren Erfahrung in der Entwicklung skalierbarer Web-Anwendungen. Spezialisiert auf Python, React und Cloud-Infrastruktur.',
    'contact',
    'contact'
);

-- -----------------------------------------------------
-- 6.2 WORK EXPERIENCES
-- -----------------------------------------------------
INSERT INTO work_experiences (
    company, position, location, employment_type,
    start_date, end_date, description, responsibilities, technologies,
    slug, anchor
) VALUES 
(
    'TechVision AG',
    'Senior Full-Stack Developer',
    'Basel, Schweiz',
    'Vollzeit',
    '2021-03-01',
    NULL, -- current position
    'Entwicklung und Wartung von Enterprise-Web-Anwendungen für Kunden aus dem Finanzsektor. Verantwortlich für die gesamte Projektarchitektur und technische Leitung eines 5-köpfigen Teams.',
    ARRAY[
        'Design und Implementierung von RESTful APIs mit FastAPI',
        'Entwicklung von React-basierten Single-Page-Applications',
        'Aufbau und Wartung von CI/CD Pipelines mit GitLab',
        'Code Reviews und Mentoring von Junior Developern',
        'Direkte Kommunikation mit Stakeholdern und Requirements Engineering'
    ],
    ARRAY['Python', 'FastAPI', 'React', 'TypeScript', 'PostgreSQL', 'Docker', 'AWS', 'GitLab CI'],
    'work-techvision-ag-2021',
    'techvision-ag-2021'
),
(
    'StartupHub GmbH',
    'Full-Stack Developer',
    'Zürich, Schweiz',
    'Vollzeit',
    '2019-01-15',
    '2021-02-28',
    'Entwicklung innovativer Web-Plattformen für verschiedene Startup-Projekte. Enge Zusammenarbeit mit Product Owners und UX-Designern in agilen Teams.',
    ARRAY[
        'Entwicklung von MVP-Features für neue Produkte',
        'Integration von Dritt-APIs (Stripe, SendGrid, AWS S3)',
        'Performance-Optimierung und Skalierung bestehender Systeme',
        'Teilnahme an Sprint Planning und Daily Standups'
    ],
    ARRAY['Python', 'Django', 'Vue.js', 'JavaScript', 'MySQL', 'Redis', 'Heroku'],
    'work-startuphub-gmbh-2019',
    'startuphub-gmbh-2019'
),
(
    'WebSolutions Ltd',
    'Junior Frontend Developer',
    'Remote',
    'Vollzeit',
    '2017-08-01',
    '2018-12-31',
    'Einstiegsposition als Frontend Developer mit Fokus auf responsive Webdesign und JavaScript-Frameworks.',
    ARRAY[
        'Umsetzung von Design-Mockups in funktionale Websites',
        'Bugfixing und Feature-Erweiterungen in bestehenden Projekten',
        'Schreiben von Unit Tests mit Jest',
        'Teilnahme an wöchentlichen Tech-Talks'
    ],
    ARRAY['HTML', 'CSS', 'JavaScript', 'React', 'SASS', 'Git', 'Webpack'],
    'work-websolutions-ltd-2017',
    'websolutions-ltd-2017'
);

-- -----------------------------------------------------
-- 6.3 PROJECTS
-- -----------------------------------------------------
INSERT INTO projects (
    name, description, project_type, start_date, end_date,
    project_url, github_url, technologies, your_role, team_size,
    slug, anchor
) VALUES
(
    'E-Commerce Platform Redesign',
    'Komplettes Redesign und technische Modernisierung einer E-Commerce-Plattform mit 50.000+ monatlichen Besuchern. Migration von Legacy-System zu moderner Microservices-Architektur.',
    'Professional',
    '2022-06-01',
    '2023-03-31',
    'https://shop-example.com',
    NULL,
    ARRAY['React', 'Next.js', 'Node.js', 'PostgreSQL', 'Redis', 'Kubernetes', 'Stripe API'],
    'Lead Developer',
    4,
    'project-ecommerce-redesign',
    'ecommerce-redesign'
),
(
    'Portfolio RAG Chatbot',
    'Intelligenter Chatbot für Portfolio-Website mit RAG (Retrieval-Augmented Generation) Pattern. Nutzt pgvector für Semantic Search und GPT-3.5 für natürliche Antworten.',
    'Personal',
    '2024-10-01',
    NULL,
    NULL,
    'https://github.com/maxmustermann/portfolio-chatbot',
    ARRAY['Python', 'FastAPI', 'Next.js', 'PostgreSQL', 'pgvector', 'OpenAI API', 'bge-m3'],
    'Solo Developer',
    1,
    'project-portfolio-chatbot',
    'portfolio-chatbot'
),
(
    'Open Source Contribution: Django REST Framework',
    'Aktive Contributions zu Django REST Framework. Implementierung neuer Features und Bugfixes.',
    'Open Source',
    '2020-05-01',
    '2021-12-31',
    'https://www.django-rest-framework.org',
    'https://github.com/encode/django-rest-framework',
    ARRAY['Python', 'Django', 'REST APIs'],
    'Contributor',
    NULL,
    'project-django-rest-contrib',
    'django-rest-contrib'
);

-- -----------------------------------------------------
-- 6.4 SKILLS
-- -----------------------------------------------------
INSERT INTO skills (name, skill_level, category, years_of_experience, description, slug, anchor) VALUES
-- Backend
('Python', 'Expert', 'Backend', 8.0, 'Hauptprogrammiersprache für Backend-Entwicklung', 'skill-python', 'python'),
('FastAPI', 'Advanced', 'Backend', 3.5, 'Moderne API-Entwicklung mit FastAPI', 'skill-fastapi', 'fastapi'),
('Django', 'Advanced', 'Backend', 5.0, 'Full-Stack Web Framework', 'skill-django', 'django'),
('Node.js', 'Intermediate', 'Backend', 3.0, 'JavaScript Backend-Entwicklung', 'skill-nodejs', 'nodejs'),

-- Frontend
('React', 'Advanced', 'Frontend', 6.0, 'Component-based UI Development', 'skill-react', 'react'),
('Next.js', 'Advanced', 'Frontend', 3.0, 'React Framework mit SSR', 'skill-nextjs', 'nextjs'),
('TypeScript', 'Advanced', 'Frontend', 4.0, 'Type-safe JavaScript', 'skill-typescript', 'typescript'),
('Tailwind CSS', 'Advanced', 'Frontend', 2.5, 'Utility-first CSS Framework', 'skill-tailwind', 'tailwind'),

-- Database
('PostgreSQL', 'Advanced', 'Database', 7.0, 'Relationale Datenbanken und pgvector', 'skill-postgresql', 'postgresql'),
('Redis', 'Intermediate', 'Database', 4.0, 'Caching und Session Management', 'skill-redis', 'redis'),
('MongoDB', 'Intermediate', 'Database', 2.0, 'NoSQL Datenbanken', 'skill-mongodb', 'mongodb'),

-- DevOps
('Docker', 'Advanced', 'DevOps', 5.0, 'Containerization und Orchestrierung', 'skill-docker', 'docker'),
('Kubernetes', 'Intermediate', 'DevOps', 2.0, 'Container Orchestrierung', 'skill-kubernetes', 'kubernetes'),
('GitLab CI', 'Advanced', 'DevOps', 4.0, 'CI/CD Pipelines', 'skill-gitlab-ci', 'gitlab-ci'),

-- Cloud
('AWS', 'Intermediate', 'Cloud', 3.5, 'EC2, S3, Lambda, RDS', 'skill-aws', 'aws'),

-- Tools
('Git', 'Expert', 'Tools', 8.0, 'Version Control', 'skill-git', 'git'),

-- Soft Skills
('Agile Development', 'Advanced', 'Soft Skills', 6.0, 'Scrum und Kanban', 'skill-agile', 'agile'),
('Team Leadership', 'Intermediate', 'Soft Skills', 2.0, 'Führung von Entwicklerteams', 'skill-leadership', 'leadership');

-- -----------------------------------------------------
-- 6.5 CERTIFICATES
-- -----------------------------------------------------
INSERT INTO certificates (
    name, issuing_organization, issue_date, expiration_date,
    credential_id, description, certificate_url,
    slug, anchor
) VALUES
(
    'AWS Certified Solutions Architect - Associate',
    'Amazon Web Services',
    '2023-06-15',
    '2026-06-15',
    'AWS-ASA-12345',
    'Zertifizierung für das Design und die Implementierung verteilter Systeme auf AWS',
    'https://example.com/certificates/aws-cert.pdf',
    'cert-aws-solutions-architect',
    'aws-solutions-architect'
),
(
    'Professional Scrum Master I (PSM I)',
    'Scrum.org',
    '2022-03-20',
    NULL,
    'PSM-67890',
    'Zertifizierung für agile Projektmethodik nach Scrum',
    'https://example.com/certificates/psm1.pdf',
    'cert-scrum-master',
    'scrum-master'
),
(
    'Machine Learning Specialization',
    'Stanford University / Coursera',
    '2024-01-10',
    NULL,
    'COURSERA-ML-2024',
    'Spezialisierung in Machine Learning und neuronalen Netzen',
    'https://example.com/certificates/ml-spec.pdf',
    'cert-ml-specialization',
    'ml-specialization'
);

-- -----------------------------------------------------
-- 6.6 EDUCATION
-- -----------------------------------------------------
INSERT INTO education (
    institution, degree, degree_type, field_of_study, location,
    start_date, end_date, grade, description, achievements,
    slug, anchor
) VALUES
(
    'ETH Zürich',
    'Master of Science',
    'Master',
    'Computer Science',
    'Zürich, Schweiz',
    '2015-09-01',
    '2017-07-31',
    '5.3',
    'Schwerpunkt auf Software Engineering und Distributed Systems. Master-Thesis über Scalable Web Architectures.',
    ARRAY[
        'Master-Thesis mit Note 5.8 bewertet',
        'Teaching Assistant für Kurs "Web Engineering"',
        'Teilnahme am ETH Entrepreneur Club'
    ],
    'edu-eth-master',
    'eth-master'
),
(
    'Universität Basel',
    'Bachelor of Science',
    'Bachelor',
    'Informatik',
    'Basel, Schweiz',
    '2012-09-01',
    '2015-07-31',
    '5.1',
    'Grundstudium in Informatik mit Nebenfach Mathematik.',
    ARRAY[
        'Bachelor-Arbeit über Web Security',
        'Stipendium für herausragende Leistungen im 3. Semester'
    ],
    'edu-unibas-bachelor',
    'unibas-bachelor'
);

-- -----------------------------------------------------
-- 6.7 HOBBIES
-- -----------------------------------------------------
INSERT INTO hobbies (name, description, since_year, icon_url, slug, anchor) VALUES
(
    'Open Source Contributions',
    'Aktive Beteiligung an Open Source Projekten. Besonders interessiert an Python- und JavaScript-Libraries.',
    2018,
    'https://example.com/icons/opensource.svg',
    'hobby-opensource',
    'opensource'
),
(
    'Mountainbiken',
    'Regelmäßige Bike-Touren in den Schweizer Alpen. Lieblingsroute: Davos-Lenzerheide Trail.',
    2015,
    'https://example.com/icons/bike.svg',
    'hobby-mountainbiking',
    'mountainbiking'
),
(
    'Tech Blogging',
    'Schreibe regelmäßig Artikel über Web-Entwicklung und Best Practices auf Medium.',
    2020,
    'https://example.com/icons/blog.svg',
    'hobby-blogging',
    'blogging'
);

-- -----------------------------------------------------
-- 6.8 SOCIAL LINKS
-- -----------------------------------------------------
INSERT INTO social_links (platform, url, username, icon_name, display_order, slug, anchor) VALUES
('GitHub', 'https://github.com/maxmustermann', 'maxmustermann', 'github', 1, 'social-github', 'github'),
('LinkedIn', 'https://linkedin.com/in/maxmustermann', 'maxmustermann', 'linkedin', 2, 'social-linkedin', 'linkedin'),
('Twitter', 'https://twitter.com/maxmustermann', '@maxmustermann', 'twitter', 3, 'social-twitter', 'twitter'),
('Medium', 'https://medium.com/@maxmustermann', '@maxmustermann', 'medium', 4, 'social-medium', 'medium'),
('Stack Overflow', 'https://stackoverflow.com/users/123456/maxmustermann', 'maxmustermann', 'stackoverflow', 5, 'social-stackoverflow', 'stackoverflow');

-- =====================================================
-- 7. UTILITY VIEWS (Optional, für einfache Abfragen)
-- =====================================================

-- View für aktuelle Positions (end_date IS NULL)
CREATE VIEW current_positions AS
SELECT * FROM work_experiences
WHERE end_date IS NULL
ORDER BY start_date DESC;

-- View für alle Skills gruppiert nach Kategorie
CREATE VIEW skills_by_category AS
SELECT 
    category,
    ARRAY_AGG(name ORDER BY skill_level DESC, years_of_experience DESC) as skills
FROM skills
GROUP BY category
ORDER BY category;

-- View für gültige Zertifikate (nicht abgelaufen)
CREATE VIEW valid_certificates AS
SELECT * FROM certificates
WHERE expiration_date IS NULL OR expiration_date > CURRENT_DATE
ORDER BY issue_date DESC;

-- =====================================================
-- 8. HELPFUL QUERIES (als Kommentare für Referenz)
-- =====================================================

/*
-- Alle Einträge ohne Embedding finden (für manuelle Generierung):
SELECT 'work_experiences' as table_name, id, company, position 
FROM work_experiences WHERE embedding IS NULL
UNION ALL
SELECT 'projects', id, name, NULL 
FROM projects WHERE embedding IS NULL
UNION ALL
SELECT 'skills', id, name, NULL 
FROM skills WHERE embedding IS NULL;

-- Anzahl Einträge pro Tabelle:
SELECT 'work_experiences' as table_name, COUNT(*) FROM work_experiences
UNION ALL SELECT 'projects', COUNT(*) FROM projects
UNION ALL SELECT 'skills', COUNT(*) FROM skills
UNION ALL SELECT 'certificates', COUNT(*) FROM certificates
UNION ALL SELECT 'education', COUNT(*) FROM education
UNION ALL SELECT 'hobbies', COUNT(*) FROM hobbies;

-- Similarity Search Beispiel (nachdem Embeddings generiert wurden):
SELECT 
    company, 
    position,
    1 - (embedding <=> '[embedding_vector_here]'::vector) as similarity
FROM work_experiences
WHERE embedding IS NOT NULL
ORDER BY similarity DESC
LIMIT 5;
*/

-- =====================================================
-- 9. SUCCESS MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Database setup completed successfully!';
    RAISE NOTICE '📊 Created 8 main tables with pgvector support';
    RAISE NOTICE '🔍 Created indices for fast similarity search';
    RAISE NOTICE '📝 Inserted sample data for testing';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Next steps:';
    RAISE NOTICE '1. Generate embeddings with your FastAPI backend';
    RAISE NOTICE '2. Test similarity search with sample queries';
    RAISE NOTICE '3. Add your own data!';
END $$;