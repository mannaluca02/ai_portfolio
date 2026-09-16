# Fast chat implementation checkpoint

Date: 2026-09-11. Local implementation only; no deployment, production settings
change, database mutation, re-embedding, commit, or push performed.

## Implemented

- A standalone, budget-limited evaluation CLI, defaulting to dry-run. It does not
  import application settings or read credential files. JSON and SSE transports,
  contract checks, citation checks, fragment checks, latency, TTFT, and retrieval
  recall reporting have offline tests. These checks do not prove semantic truth.
- Forty candidate German questions, twelve reviewed against selected public API
  records. These are not the user's missing twelve-question log. Unreviewed
  questions are refused by the execution gate.
- All-table retrieval with word-boundary intent boosts. Intent no longer excludes
  relevant tables. Explicit caller table filters still work. Boosts are not yet
  calibrated on the full corpus; this change alone is not a latency improvement.
- Shared allowlisted document text for embedding generation, retrieved excerpts,
  generator context, and verification. Technologies, achievements, and dates are
  included. Phone fields and known supplied phone numbers are removed. A future
  corpus loader must supply the complete phone denylist to cover cross-row copies.
- A separate, tested OpenAI embedding adapter, not yet connected to the runtime
  factory. It requests `text-embedding-3-small` with 1024 dimensions, disables
  automatic retries, sets a five-second SDK timeout, validates returned model,
  indices, shape and finite/nonzero vectors, and maintains a bounded LRU cache.
  Batch ordering and duplicates are preserved; callers get independent arrays.

The dimensions parameter is supported by third-generation embedding models in
the [official API reference](https://developers.openai.com/api/reference/python/resources/embeddings/methods/create).
The installed Python SDK was also inspected. Account access and actual returned
vectors have not been tested with the user's key.

## Production baseline

Three successful HTTP 200 calls to `https://www.lucamanna.ch/api/chat`, natural
mode, one attempt per question. An earlier sandbox attempt returned connection
errors and is not included in these measurements. No further baseline calls were
made. Each successful response was `no_information`, with no sources and text:
“Dazu finde ich keine Information in meinen Portfolio-Daten.”

| ID | Question | Expected | Measured client latency |
| --- | --- | --- | --- |
| q11 | Welche Rolle hatte Luca bei Novartis? | answered | 10489.241 ms |
| q13 | Kann Luca Docker? | answered | 10078.890 ms |
| q14 | Hat Luca Erfahrung mit PyTorch? | answered | 11867.045 ms |

Answer rate and pass rate: 0/3. HTTP/contract errors: 0/3. Median: 10489.241 ms.
Interpolated sample p95: 11729.265 ms, not a representative production percentile
with only three observations. Retrieval recall, wrong-source rate, and TTFT were
unavailable, not zero. Existing production responses do not expose ranked
retrieval candidates; cited sources cannot substitute for retrieval recall.

Dataset SHA256 at baseline:
`5049d63f7530cddc8f8b7210c015a0c2dee3be74f27ac9dd83254ecf91371071`.
Corpus review version: `public-api-source-review-2026-09-11`.

Safe command (does not send requests):

```sh
source .venv/bin/activate
python backend/scripts/eval_chat.py --base-url https://www.lucamanna.ch --question-id q11 --question-id q13 --question-id q14 --max-requests 3
```

Adding `--execute` sends up to three rate-limited requests. Do not repeat merely
to regenerate this report. The recorded baseline used label
`production-baseline-2026-09-11`.

## Verification and remaining gates

Offline backend suite: 118 passed, 18 existing deprecation warnings. Selected
modules (evaluation, document text, intent, OpenAI adapter) have 97% combined line
coverage; adapter 100%. This is not whole-application coverage or live model
quality evidence. Test-first failures included the absent adapter module, then
all 21 provider contract tests passed after implementation.

```sh
source .venv/bin/activate
python -m pytest backend/tests -q --cov=scripts.eval_chat --cov=app.services.document_service --cov=app.services.intent_service --cov=app.services.openai_embedding_service --cov-report=term-missing
```

Next implementation steps:

1. Versioned vector storage and an in-memory corpus index with a complete phone
   denylist. Equal vector lengths do not make BGE and OpenAI embeddings compatible.
   Never query existing BGE vectors using OpenAI query vectors. Keep old storage
   and runtime available until the new corpus passes a measured recall gate.
2. Complete source labels and obtain the missing user log. Capture actual ranked
   retrieval candidates for a valid baseline, then calibrate retrieval thresholds.
3. Implement birth-date support without inventing a value, lexical matching,
   profile context, explicit pipeline configuration and degraded-error reporting.
4. Rewrite verification, implement backend/frontend SSE, and settle the visible
   pre-verification token policy before integration. Current frontend is unchanged
   by this checkpoint; no new browser verification was needed for this adapter.
5. Verify live API/model access, prepare and approve data migration, run full
   quality/latency evaluation, then obtain deployment authorization.

Do not remove BGE dependencies, flip production pipeline flags, or promise the
sub-second latency target based on these offline tests.

Original modified implementation files were backed up under
`/private/tmp/portfolio-eval-backup.8UPvHZ/`. The concurrent `CLAUDE.md` change is
user-owned and untouched; its trailing blank line currently fails global
`git diff --check` independently of these changes.

## Checkpoint self-review

Accuracy 4/5: offline contracts pass, but model access and quality remain untested.
Completeness 2/5: migration, index, verifier, SSE and deployment remain unfinished.
Clarity 4/5: implemented and pending work are separated; the source labels are
still only a partial corpus review. Actionability 4/5: reproducible tests and a
dry-run CLI exist, but runtime activation requires versioned storage. Conciseness
4/5: this detailed handoff is longer than the user-facing status. Overall 3.6/5.
This is a partial checkpoint, not task completion. Highest-impact improvement is
safe runtime integration, followed by measured retrieval quality and streaming.
The user should reasonably expect those remaining phases before calling it done.
