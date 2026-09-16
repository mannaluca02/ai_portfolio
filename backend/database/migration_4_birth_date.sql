-- Migration 4: birth date for the chatbot's age answer
--
-- "Wie alt ist er?" was unanswerable because no birth date existed anywhere in
-- the corpus. The chatbot computes the age on every request from this column
-- and only ever emits the computed number of years, never the date itself
-- (see backend/app/services/document_service.py: DERIVED_FIELDS).
--
-- Run in the Supabase SQL editor, then re-run backend/scripts/generate_embeddings.py
-- so the contact_info embedding contains the "age: N Jahre alt" line.

ALTER TABLE contact_info ADD COLUMN IF NOT EXISTS birth_date DATE;

UPDATE contact_info
SET birth_date = DATE '2002-11-07'
WHERE birth_date IS NULL;

-- Verify: expects one row with the date and the current age.
SELECT full_name,
       birth_date,
       date_part('year', age(birth_date))::int AS age_years
FROM contact_info;
