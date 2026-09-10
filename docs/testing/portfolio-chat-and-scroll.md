# Chat latency, grounding, and project scrolling

Status: implementation tested locally on 2026-09-10; not committed, pushed, or deployed.
User journeys were derived from the request to speed up chat without inventing facts
about Luca Manna, and remove the extra mobile scrolling in Featured projects.

## Project overview and findings

The frontend is Next.js 14 / React 18 with Tailwind, Framer Motion, and Lenis.
It fetches portfolio sections through Next API routes. The chatbot proxies requests
to FastAPI, which searches PostgreSQL/pgvector with local BGE-M3 embeddings,
generates with OpenAI, then checks the answer against the retrieved evidence.
The database schema remains `backend/database/supabase-script.sql`; no migration
or portfolio content change is included.

The prior implementation ran the synchronous chat pipeline on the async request
thread, re-encoded sources repeatedly during verification, allowed long generated
answers, and could return text after failed verification. The frontend could also
override a failed check using source similarity. These were code findings, not a
production latency profile. Featured and All Projects were both mounted in one
horizontal flex row, so the taller list determined the section height.

## Implementation

- Warm the embedding model before the API accepts traffic; run chat in a bounded
  worker pool with database sessions confined to their worker thread.
- Batch and deduplicate verification embeddings. Default generated output is now
  300 tokens; the OpenAI client has a 15-second timeout and no automatic retries.
  The Next proxy aborts at 30 seconds and the widget at 35 seconds.
- Keep relevance ranking boosts separate from raw similarity. Empty retrieval
  no longer invokes the unrelated-recent-records fallback.
- Require valid citations and per-statement checks; reject mismatched numbers,
  negation, and unsupported capitalized terms. Generation/verification errors,
  incomplete output, and failed checks return source excerpts or no information.
- Preserve backend outcome and citation numbering in the UI; do not label
  similarity scores as proof of correctness. Preserve 429/503/504 error handling.
- Mount only the active project list. Citation events mount the relevant tab,
  expand its project, and scroll to the card after React commits it.

The model remains `gpt-3.5-turbo`; no claim is made that changing models was tested.
`SKIP_VERIFICATION=true` now selects source excerpts, never unchecked generation.

## Evidence

| Behavior | Automated evidence | Result |
| --- | --- | --- |
| Unsupported statements, dates, negation, missing/invalid citations, failed checks, and truncated output fail safely | `backend/tests/test_chat_safety.py` | Pass |
| Slow synchronous pipeline does not block the event loop; excess requests return 503 | `backend/tests/test_chat_runtime.py` | Pass |
| Model warms before readiness; failed startup stays unready | `backend/tests/test_chat_runtime.py` | Pass |
| Real middleware returns 429, preserves the request body, and lets validation reject invalid modes | `backend/tests/test_chat_runtime.py` | Pass |
| Generator uses bounded output, timeout, and shared evidence text | `backend/tests/test_generator.py` | Pass |
| Hidden projects are unmounted; empty Featured and cross-tab citation work | `frontend/tests/projects.test.tsx` | Pass |
| Rejected answers stay hidden despite high similarity | `frontend/tests/chat-widget.test.tsx`, `chat-response.test.ts` | Pass |
| Proxy preserves rate-limit headers, aborts stalled requests, and forwards cancellation | `frontend/tests/chat-proxy.test.ts` | Pass |

Initial RED evidence recorded during implementation: chat safety 20 failed / 1
passed, runtime 3 failed, startup 2 failed, and exhausted middleware returned 500
instead of 429. Those targets passed after their fixes. The widget reproducer also
failed before removal of the similarity override. No checkpoint commits were made,
per the user's instruction not to commit without permission.

Final commands run from the repository, with Python inside `.venv`:

```sh
source .venv/bin/activate
python -m pytest backend/tests -q --cov=app.api.chat --cov=app.services.chatbot_service --cov=app.services.generator_service --cov=app.services.verifier_service --cov-report=term
```

Result: **29 passed**, targeted line coverage **90%**. Models, DB, and OpenAI are
mocked; tests do not read `.env` files. Coverage requires `pytest-cov` (7.1.0 used).
Existing Pydantic class-config and FastAPI startup-hook deprecations remain.

From `frontend`:

```sh
npm run test:coverage
node_modules/.bin/tsc --noEmit
node_modules/.bin/eslint --no-cache app components lib tests vitest.config.ts playwright.config.ts e2e
```

Result: **23 passed**, **99.43% lines / 87.06% branches / 82.35% functions** for
the selected Projects, response-parser, and proxy files, not the whole application.
TypeScript passed. ESLint passed with four pre-existing warnings in About,
Certificates, and useScrollAnimation. Ruff passed for the nine touched Python
application files plus `backend/tests`; no lint rules were weakened.
`git diff --check` passed.

A production Next build passed in an isolated copy without `.env` files:
`/private/tmp/ai-portfolio-verify.ZoKh6h/frontend`, using a dummy Resend build key.
No mail, database update, or real LLM request was sent. API fetches to the absent
local backend logged connection errors in this isolated environment.

## Orca browser checks

Used Orca 1.4.198's embedded browser and native `viewport` command. The fixture
server `frontend/tests/browser-fixtures.mjs` serves 18 synthetic projects, including
two featured projects, and intercepts browser API calls on localhost:3100.
It starts the isolated production Next build on localhost:3101.

| Check | Observed result |
| --- | --- |
| Mobile viewport 390 × 844, Featured | 2 mounted cards; section height 844 px; no horizontal overflow |
| Switch to All Projects | 18 mounted cards; height 2521.25 px |
| Switch back to Featured | 2 cards; height restored to exactly 844 px |
| Expand mobile featured card | Expanded state true; section height increased to 1610.57 px |
| Citation event for project 18 | All tab mounted, target expanded; after smooth scrolling settled, heading top 95.76 px |
| Screenshot | Inspected project 18 below fixed navigation, with no horizontal clipping |
| Desktop 1440 × 900 | 2 featured cards; section height 900 px; no horizontal overflow |
| Empty Featured after reload | Empty message and zero mounted cards verified; reload reset Orca sizing, so this was not a mobile-height assertion |

Orca resets viewport sizing on reload in this session: always reapply it and
measure `innerWidth`/`innerHeight`. The final chat submission was **not verified in
the browser** because the local tab disappeared before inspection completed.
The automated widget rejection test passed. The additional Playwright specs are
retained for future CI but were **not run**; no standalone browser was installed.
Reduced-motion handling is implemented but not visually verified on a real device.

To repeat the Orca preview, first create an isolated build excluding all `.env*`,
node_modules, and build artifacts, build with appropriate dummy configuration,
then launch:

```sh
PORTFOLIO_TEST_APP=/absolute/path/to/isolated/frontend node frontend/tests/browser-fixtures.mjs
```

Open localhost:3100 through Orca. Reapply viewport sizing after each reload.
Set the local cookie `empty-featured=1` to test the empty state, and clear it
afterward. Fixture content is intentionally synthetic and must never be deployed.

## Release gates and limitations

1. Deploy to staging first, backend before frontend. The new frontend rejects
   legacy responses without an explicit outcome. Keep `SKIP_VERIFICATION=false`
   for generated answers; true intentionally uses excerpts only.
2. Allow time for model download/warmup and persist its cache. A missing/broken
   model now fails startup rather than making the first visitor wait for loading.
3. Use a fixed set of questions with human-reviewed answers from the actual
   portfolio: supported skills/projects, missing facts, false premises, changed
   dates, negated facts, contradictory sources, and prompt-injection attempts.
   Review every accepted assertion and its citation; inspect fallback usefulness.
4. Compare baseline and candidate on the same host/data/model. Record cold start
   separately, then repeated warm requests with p50/p95 end-to-end latency and
   `metadata.timings_ms` (retrieval, generation, verification). Also test concurrent
   requests and proxy error paths. **No live latency reduction is claimed yet.**
5. Embedding similarity plus lexical checks is not logical entailment. It can
   reject valid paraphrases and still miss incorrect relationships. It is not a
   zero-hallucination guarantee. If that guarantee is mandatory, use the excerpt
   path and human-reviewed source content rather than generated prose.

Existing in-memory rate limits are per process and reset on restart. Trusted
proxy/IP configuration and multi-worker/global rate limiting were not redesigned.
DB query deadlines are not added: client/proxy timeouts do not necessarily cancel
work already running on the backend. Tune concurrency after measuring real load.

Backups: `/private/tmp/ai-portfolio-backup.TGNTJ1/source.tar`, plus the original
rate limiter and pre-lint tests in that directory. The user's `AGENTS.md` was not
modified. No commit, push, or deployment was performed.

## Self-evaluation

Overall 3.8/5. Accuracy 4: measurements are separated from unmeasured model
quality; staging evidence would strengthen this. Completeness 3: both requested
changes are implemented, but real-model latency/quality validation remains.
Clarity 4: this report indexes evidence; a staging result summary would shorten
the remaining caveats. Actionability 4: code and repeatable tests exist; staging
configuration still needs the owner. Conciseness 4: detailed evidence is kept here
rather than in the handoff; the browser command history could be automated later.

Highest-impact improvement: run the same human-reviewed question set against
baseline and candidate staging backends, then set release thresholds from those
measurements. This requires real service configuration, not more mocked tests.
Self-check: would the user agree? Likely only once the real speed improvement is
measured; this is a locally verified implementation, not a verified live upgrade.
