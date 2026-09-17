-- Apply before deploying the bilingual API. No base content or embeddings change.
BEGIN;
CREATE TABLE IF NOT EXISTS content_translations (
    source_table TEXT NOT NULL CHECK (source_table IN
        ('work_experiences', 'projects', 'skills', 'certificates', 'education',
         'contact_info', 'hobbies', 'languages')),
    source_id INTEGER NOT NULL CHECK (source_id > 0),
    locale TEXT NOT NULL CHECK (locale IN ('de', 'en')),
    field TEXT NOT NULL,
    value JSONB NOT NULL CHECK (jsonb_typeof(value) IN ('string', 'array')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (source_table, source_id, locale, field)
);
ALTER TABLE content_translations ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON content_translations FROM anon, authenticated;
-- Like the base tables, only the backend database role reads these rows.
CREATE TRIGGER update_content_translations_updated_at
    BEFORE UPDATE ON content_translations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
COMMIT;
