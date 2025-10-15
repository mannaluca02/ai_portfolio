-- =====================================================
-- Migration: Consolidate Skill Levels from 4 to 3
-- Old: Beginner, Intermediate, Advanced, Expert
-- New: Beginner, Intermediate, Expert
-- =====================================================

-- Step 1: Update all 'Advanced' skills to 'Expert'
-- Rationale: 'Advanced' skills (2.5-7 years) should be considered 'Expert'
UPDATE skills
SET skill_level = 'Expert'
WHERE skill_level = 'Advanced';

-- Step 2: Drop the old ENUM type and create new one
-- Note: This requires PostgreSQL 12+ or manual steps
-- First, alter the column to use TEXT temporarily
ALTER TABLE skills
ALTER COLUMN skill_level TYPE TEXT;

-- Drop the old ENUM
DROP TYPE IF EXISTS skill_level;

-- Create new ENUM with only 3 levels
CREATE TYPE skill_level AS ENUM (
    'Beginner',
    'Intermediate',
    'Expert'
);

-- Convert column back to ENUM type
ALTER TABLE skills
ALTER COLUMN skill_level TYPE skill_level
USING skill_level::skill_level;

-- Verify migration
SELECT
    skill_level,
    COUNT(*) as count,
    STRING_AGG(name, ', ' ORDER BY name) as skills
FROM skills
GROUP BY skill_level
ORDER BY
    CASE skill_level
        WHEN 'Expert' THEN 1
        WHEN 'Intermediate' THEN 2
        WHEN 'Beginner' THEN 3
    END;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration completed: Skill levels consolidated to 3 levels';
    RAISE NOTICE '   - Expert (blau)';
    RAISE NOTICE '   - Intermediate (grün)';
    RAISE NOTICE '   - Beginner (grau)';
END $$;
