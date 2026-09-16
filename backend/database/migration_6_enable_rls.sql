-- Migration 6: close the public API off from the portfolio tables
--
-- WHY
-- Supabase grants `anon` and `authenticated` full privileges on everything in
-- the public schema by default, and relies on Row-Level Security to restrain
-- them. This schema never enabled RLS, so anyone holding the project URL and
-- the anon key (which is public by design, it ships in browser apps) could read,
-- modify or delete every row. Verified on 2026-09-16 against the live database:
-- as `anon`, SELECT count(*) FROM projects returned 12.
--
-- WHY THIS IS SAFE FOR THE APPLICATION
-- The FastAPI backend connects over a direct Postgres connection as `postgres`,
-- which has BYPASSRLS, and the website reads everything through that backend.
-- Nothing in this project uses the Supabase REST API, the Supabase client, or
-- the anon key. Tested in a rolled-back transaction: after these statements
-- `anon` is denied on every table and view, while `postgres` still reads them.
--
-- NO POLICIES ARE CREATED, ON PURPOSE
-- RLS with no policy denies every row to every non-bypassing role. That is
-- exactly what is wanted: the public API should expose nothing at all. If you
-- ever want to read the portfolio directly from the browser with the Supabase
-- client, add a read-only policy per table at that point, for example:
--   CREATE POLICY public_read ON projects FOR SELECT TO anon USING (true);
-- and re-grant SELECT only. Never re-grant write privileges.
--
-- Run in the Supabase SQL editor.

BEGIN;

ALTER TABLE work_experiences ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects         ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills           ENABLE ROW LEVEL SECURITY;
ALTER TABLE certificates     ENABLE ROW LEVEL SECURITY;
ALTER TABLE education        ENABLE ROW LEVEL SECURITY;
ALTER TABLE hobbies          ENABLE ROW LEVEL SECURITY;
ALTER TABLE languages        ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_info     ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_links     ENABLE ROW LEVEL SECURITY;

-- A view runs with its owner's privileges unless told otherwise, and the owner
-- here (postgres) bypasses RLS. Without this the three views stay fully
-- readable through the API and the RLS above buys nothing.
ALTER VIEW current_positions  SET (security_invoker = on);
ALTER VIEW skills_by_category SET (security_invoker = on);
ALTER VIEW valid_certificates SET (security_invoker = on);

-- Not redundant with RLS. Per the PostgreSQL documentation, row-level security
-- governs SELECT, INSERT, UPDATE and DELETE; TRUNCATE is controlled only by the
-- TRUNCATE privilege, which anon currently holds. Removing the grants also
-- means a table added later is not exposed by an inherited grant.
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated;

COMMIT;

-- Verify: expects rls_enabled = true and policies = 0 for all nine tables,
-- and no remaining anon/authenticated privileges in the public schema.
SELECT c.relname AS table_name,
       c.relrowsecurity AS rls_enabled,
       (SELECT count(*) FROM pg_policies p
         WHERE p.schemaname = 'public' AND p.tablename = c.relname) AS policies
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public' AND c.relkind = 'r'
ORDER BY c.relname;

SELECT grantee, count(*) AS tables_still_granted
FROM information_schema.role_table_grants
WHERE table_schema = 'public' AND grantee IN ('anon', 'authenticated')
GROUP BY grantee;
