-- Migration 5: spoken languages
--
-- "Welche Sprachen spricht er?" had no data to answer from. Languages are kept
-- in their own table rather than in `skills`, because `skill_category` is an
-- ENUM with no language value (and Postgres cannot drop an ENUM value once
-- added), and `skill_level` is Beginner/Intermediate/Expert, which cannot state
-- "Muttersprache" or a CEFR level without misrepresenting it on the public
-- skills section.
--
-- `section` is 'skills' on purpose: it is what the chatbot's source link scrolls
-- to, and the skills section is where a visitor would look for this.
--
-- Run in the Supabase SQL editor, then re-run backend/scripts/generate_embeddings.py
-- so the new rows become searchable.

CREATE TABLE IF NOT EXISTS languages (
    id SERIAL PRIMARY KEY,

    -- Basic Information
    name VARCHAR(100) NOT NULL UNIQUE,   -- e.g., 'Deutsch'
    level VARCHAR(120) NOT NULL,         -- e.g., 'Muttersprache', 'B2 (Cambridge English: First)'
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

CREATE INDEX IF NOT EXISTS idx_languages_embedding ON languages
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_languages_slug ON languages(slug);

DROP TRIGGER IF EXISTS update_languages_updated_at ON languages;
CREATE TRIGGER update_languages_updated_at
    BEFORE UPDATE ON languages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

INSERT INTO languages (name, level, description, slug, section, anchor) VALUES
('Deutsch', 'Muttersprache',
 'Deutsch ist die Muttersprache von Luca Manna.',
 'lang-deutsch', 'skills', 'deutsch'),
('Englisch', 'B2 (Cambridge English: First)',
 'Englisch auf Niveau B2 des Gemeinsamen Europaeischen Referenzrahmens, belegt durch das Zertifikat Cambridge English: First (FCE).',
 'lang-englisch', 'skills', 'englisch')
ON CONFLICT (slug) DO NOTHING;

-- Verify: expects the two rows, embeddings still empty until the script runs.
SELECT name, level, slug, (embedding IS NOT NULL) AS has_embedding FROM languages ORDER BY id;
