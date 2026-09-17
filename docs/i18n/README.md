# German / English rollout

This document records implementation verification and the remaining production rollout steps. The database migration and translation import have not been executed against production.

## Behaviour

- `/de` and `/en` are the homepages. `/` negotiates a 307 redirect using `NEXT_LOCALE`, then `Accept-Language`, then German.
- next-intl is pinned to 4.14.5; its npm peer range includes the installed Next.js 14.2.33 and React 18. The setup uses Next 14's `middleware.ts` and `setRequestLocale`, not Next 16's root-params API. See [next-intl routing setup](https://next-intl.dev/docs/routing/setup).
- API routes, Next assets and static files bypass locale middleware. The daily keep-alive route remains unchanged.
- The switcher retains the query and fragment. Homepages have separate canonicals and reciprocal hreflang links. The sitemap lists both homepages, without fragment URLs.
- Legal content exists in German. Legacy and English legal URLs redirect to `/de/impressum` or `/de/datenschutz`. Legal pages have no language alternates.
- UI messages live in `frontend/messages`. Dates and duration plurals follow the active locale.
- Content requests carry `?lang=de|en`; unsupported values are rejected. Translation overlays copy response fields and never mutate German ORM rows or embeddings. Missing fields retain their German source text.
- Chat requests carry `language: de|en`. Generation and fallback messages follow it; German evidence and quoted excerpts remain German. The English excerpt introduction discloses this.

## Content review and database order

1. Review `backend/translations/en.draft.json`: 59 English fields alongside their original German values, identified by table and slug. The vocational baccalaureate title says Business and Services while its field says Technology, Architecture and Life Sciences; confirm the correct track before approval.
2. Apply `backend/database/migration_7_content_translations.sql` before deploying the bilingual backend. It creates an RLS-protected translation table and revokes public role privileges. German requests do not query this table; English requests require it to exist.
3. After owner approval, save an approved copy with `status: "approved"`. Run the loader's dry run before execution. It validates the field allowlist, locale, types and duplicate keys. Execution resolves IDs from slugs and rejects changed German source values. All writes occur in one transaction.

From the repository root, inside the existing virtual environment:

```sh
source .venv/bin/activate
python backend/scripts/load_translations.py backend/translations/en.draft.json --dry-run
# After owner review, use the approved copy:
python backend/scripts/load_translations.py /path/to/en.approved.json --dry-run
python backend/scripts/load_translations.py /path/to/en.approved.json --execute
```

The loader reads `DATABASE_URL` only from process environment and does not read `.env`. Never put credentials in command-line arguments. Translation rows must be maintained when a source row is deleted; this polymorphic table has no foreign key to the individual content tables.

## Verification completed

- Production build, TypeScript and Next lint passed. Existing image/hook warnings remain.
- Frontend: 53 tests passed, covering routing, API exclusion, language forwarding, message parity, message formatting and existing chat/project behaviour.
- Backend: 224 tests passed, including language validation, English abbreviations, fallback text, overlay behaviour and draft-loader validation.
- Existing frontend coverage scope: 91.23% lines, 85.62% branches, 69.23% functions. This scope covers chat proxy, chat response, chat widget and Projects; it is not whole-project coverage.
- Isolated PostgreSQL 14: migration applied, public-role SELECT denied, a synthetic translation imported, and the actual FastAPI contact endpoint returned German and English content correctly, retained an untranslated field, and rejected an unsupported locale. The unused embedding column was TEXT in this test fixture; vector search was not tested by this check.
- Orca browser: `/de?ref=verification#projects` switched to `/en?ref=verification#projects`, set `NEXT_LOCALE=en`, showed English draft content, and exposed the correct canonical/hreflang. Root navigation honoured the cookie. Both locale pages and keep-alive returned 200; legal HTML had no hreflang. The preview used public-content snapshots plus in-memory draft translations, not production writes; its health response was a fixture.
- The temporary preview on port 3100 uses a content fixture on port 8109. That fixture has no `/api/chat` endpoint: chat returns 404 in both languages. End-to-end chat requires the real FastAPI backend; the fixture preview does not verify it.
- Playwright specs were added, but a full Playwright run did not pass because browser binaries were absent. Browser verification switched to Orca at the owner's request; do not report `npm run test:e2e` as passed.
- `git diff --check` passed.

## Chat measurement and remaining release gate

`verifier-snapshot-20260917.json` records a real local bge-m3 measurement using public API snapshots from six tables retrieved on 2026-09-16. It is not the full live corpus and includes neither retrieval nor LLM generation.

| Threshold 0.55 | Supported accepted | Unsupported accepted |
| --- | ---: | ---: |
| German | 8/8 | 0/7 |
| English | 7/8 | 0/7 |

At 0.50, English admits one unsupported claim. Keep 0.55 pending the full measurement. English excerpt floor/gap remain provisional at 0.40/0.03. Configuration exposes `VERIFICATION_THRESHOLD_EN`, `EXCERPT_FLOOR_EN` and `EXCERPT_GAP_EN`; no English embedding corpus has been introduced.

The English dataset contains translations of all 27 reviewed questions, with the same expected source labels. The evaluation dry run validated 27 planned requests and no unreviewed entries. Before release, run against a configured staging backend with the current full corpus and model:

```sh
python backend/scripts/calibrate_verifier.py --language en
python backend/scripts/calibrate_excerpts.py --dataset backend/tests/data/golden_questions.en.json
python backend/scripts/eval_chat.py --dataset backend/tests/data/golden_questions.en.json --language en --dry-run
python backend/scripts/eval_chat.py --dataset backend/tests/data/golden_questions.en.json --language en --base-url http://localhost:8000 --execute --max-requests 27
```

Compare with the same 27 German IDs and corpus. The calibration scripts use the application's normal settings, so run them in the appropriately configured backend environment. Full live retrieval hit rate, generated-answer pass rate and English excerpt calibration remain unmeasured. Do not represent snapshot verifier results as those metrics.

Deploy database migration and approved translations first, backend second, frontend last. Verify production locale routes and authenticated keep-alive, then resubmit the sitemap in Search Console. A code rollback may leave the additive translation table in place; the old backend ignores it.

## Review assessment

Accuracy 4/5: build, tests, Orca and PostgreSQL support the implemented behaviour; live English retrieval remains unmeasured. Completeness 3/5: content approval/import and full calibration remain release gates. Clarity 4/5: this document distinguishes fixture, snapshot and live evidence, though the change spans both stacks. Actionability 4/5: draft, loader, migration and calibration commands are supplied; approval and a configured staging run are still needed. Conciseness 4/5: the implementation retains existing component structures, with some repeated proxy validation. Overall 3.8/5. The user should consider this implementation ready for review, not a completed production rollout.

Backups before edits: `/private/tmp/ai-portfolio-i18n-backup-20260916`.
