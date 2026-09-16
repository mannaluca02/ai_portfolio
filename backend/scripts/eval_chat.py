"""Budgeted JSON/SSE chat evaluation. No app settings, .env, or DB imports.

The backend currently serves JSON only, so `--protocol sse` has no endpoint to
talk to. The SSE client is kept because it is tested and the contract it expects
is the one a future streaming endpoint would have to meet.

Default: print a dry-run plan. Execution requires reviewed labels, an explicit
endpoint and a sufficient request budget. Metrics assess supplied labels, not
semantic truth; a human must still review claims against the source corpus.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path
from time import perf_counter
from typing import Any, Literal
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field, model_validator

OUTCOMES = {"answered", "source_fallback", "no_information"}
DEFAULT_DATASET = Path(__file__).resolve().parents[1] / "tests/data/golden_questions.json"
MAX_RESPONSE_BYTES = 1_000_000


class SourceKey(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    table: str = Field(min_length=1)
    slug: str = Field(min_length=1)


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(min_length=1)
    question: str = Field(min_length=1, max_length=1000)
    reviewed: bool = False
    expected_outcome: Literal["answered", "source_fallback", "no_information"] | None = None
    expected_sources: list[SourceKey] = Field(default_factory=list)
    required_answer_fragments: list[str] = Field(default_factory=list)
    forbidden_answer_fragments: list[str] = Field(default_factory=list)
    notes: str = ""

    @model_validator(mode="after")
    def validate_review(self) -> Question:
        if self.reviewed:
            if self.expected_outcome is None:
                raise ValueError("Reviewed questions require an expected outcome")
            if self.expected_outcome != "no_information" and not self.expected_sources:
                raise ValueError("Reviewed answers require expected source table/slug labels")
            if self.expected_outcome == "no_information" and self.expected_sources:
                raise ValueError("No-information questions must not require sources")
        if len(set(self.expected_sources)) != len(self.expected_sources):
            raise ValueError("Duplicate expected sources")
        return self


class Dataset(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1]
    corpus_version: str = Field(min_length=1)
    notes: str = ""
    questions: list[Question] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_ids(self) -> Dataset:
        if len({q.id for q in self.questions}) != len(self.questions):
            raise ValueError("Duplicate question IDs")
        return self


def source_keys(values: Any) -> list[SourceKey]:
    if not isinstance(values, list):
        raise TypeError("Sources must be a list")
    return [SourceKey(table=value["table"], slug=value["slug"]) for value in values]


def score_response(q: Question, payload: Any, *, latency_ms: float,
                   ttft_ms: float | None = None, k: int = 5) -> dict[str, Any]:
    """Score final citations separately from explicit pre-generation retrieval."""
    if k < 1:
        raise ValueError("k must be positive")
    payload = payload if isinstance(payload, dict) else {}
    text = payload.get("answer", "")
    outcome = payload.get("outcome")
    contract_ok = (isinstance(text, str) and bool(text.strip())
                   and isinstance(outcome, str) and outcome in OUTCOMES)
    if not isinstance(text, str):
        text = ""
    try:
        sources = source_keys(payload.get("sources"))
        indices = [source["index"] for source in payload["sources"]]
        contract_ok &= all(type(index) is int and index > 0 for index in indices)
        contract_ok &= len(set(indices)) == len(indices)
        if outcome == "no_information":
            contract_ok &= not sources
        else:
            cited = [int(index) for index in re.findall(r"\[(\d+)\]", text)]
            contract_ok &= bool(cited) and set(cited) <= set(indices)
        if outcome == "answered":
            verification = payload.get("verification")
            contract_ok &= isinstance(verification, dict) and verification.get("is_verified") is True
    except (KeyError, TypeError, ValueError):
        sources, contract_ok = [], False

    expected = set(q.expected_sources)
    actual = set(sources)
    wrong_source_rate = len(actual - expected) / len(actual) if actual else None
    metadata = payload.get("metadata")
    recall = None
    if expected and isinstance(metadata, dict) and "retrieved_sources" in metadata:
        try:
            retrieved = source_keys(metadata["retrieved_sources"])
            # Deduplicate before applying k so repeated rows do not consume slots.
            top_k = set(list(dict.fromkeys(retrieved))[:k])
            recall = len(expected & top_k) / len(expected)
        except (KeyError, TypeError, ValueError):
            recall = None  # Malformed instrumentation is not zero recall.
    forbidden = [fragment for fragment in q.forbidden_answer_fragments if fragment.casefold() in text.casefold()]
    missing = [fragment for fragment in q.required_answer_fragments if fragment.casefold() not in text.casefold()]
    matches = outcome == q.expected_outcome
    passed = q.reviewed and contract_ok and matches and not forbidden and not missing and not (actual - expected)
    return {
        "id": q.id, "question": q.question, "answer": text,
        "outcome": outcome, "expected_outcome": q.expected_outcome,
        "contract_ok": bool(contract_ok), "outcome_matches": matches,
        "passed": bool(passed), "error": None,
        "sources": [source.model_dump() for source in sources],
        "recall_at_k": recall, "k": k, "wrong_source_rate": wrong_source_rate,
        "required_fragments_missing": missing, "forbidden_fragments_found": forbidden,
        "latency_ms": latency_ms, "ttft_ms": ttft_ms,
    }


def percentile(values: list[float], quantile: float) -> float | None:
    """Linear interpolation at (n - 1) * quantile, including single samples."""
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    return round(ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower), 3)


def summarize(results: list[dict[str, Any]], *, planned: int) -> dict[str, Any]:
    """Rates use all attempted requests, including errors. Means omit unknowns."""
    total = len(results)

    def mean_known(key: str) -> float | None:
        values = [r[key] for r in results if r.get(key) is not None]
        return sum(values) / len(values) if values else None

    def timings(key: str) -> dict[str, Any]:
        values = [r[key] for r in results if not r.get("error") and r.get(key) is not None]
        return {"p50": percentile(values, 0.5), "p95": percentile(values, 0.95), "samples": len(values)}

    return {
        "planned": planned, "attempted": total, "complete": total == planned,
        "answer_rate": sum(r.get("outcome") == "answered" and r.get("contract_ok", False) for r in results) / total if total else None,
        "pass_rate": sum(r["passed"] for r in results) / total if total else None,
        "error_rate": sum(bool(r.get("error")) for r in results) / total if total else None,
        "source_fallback_count": sum(r.get("outcome") == "source_fallback" for r in results),
        "no_information_count": sum(r.get("outcome") == "no_information" for r in results),
        "recall_at_k": mean_known("recall_at_k"),
        "recall_samples": sum(r.get("recall_at_k") is not None for r in results),
        "wrong_source_rate": mean_known("wrong_source_rate"),
        "wrong_source_samples": sum(r.get("wrong_source_rate") is not None for r in results),
        "latency_ms": timings("latency_ms"), "ttft_ms": timings("ttft_ms"),
    }


def sse_events(lines: Iterable[str]) -> Iterator[tuple[str, Any]]:
    """Parse SSE framing, including comments, CRLF (via httpx), and multiline data."""
    event, data, size = "message", [], 0
    for line in lines:
        size += len(line.encode("utf-8"))
        if size > MAX_RESPONSE_BYTES:
            raise ValueError("Response exceeds size limit")
        if not line:
            if data:
                yield event, json.loads("\n".join(data))
            event, data = "message", []
        elif not line.startswith(":"):
            field, _, value = line.partition(":")
            value = value.removeprefix(" ")
            if field == "event":
                event = value
            elif field == "data":
                data.append(value)


def measure(client: httpx.Client, endpoint: str, q: Question, *, protocol: str,
            k: int = 5) -> dict[str, Any]:
    started = perf_counter()
    first_token = None
    result = {"id": q.id, "question": q.question, "passed": False}
    try:
        with client.stream("POST", endpoint, json={"message": q.question, "mode": "natural"}) as response:
            result["status_code"] = response.status_code
            if response.status_code != 200:
                return {**result, "error": f"HTTP {response.status_code}",
                        "retry_after": response.headers.get("retry-after")}
            if protocol == "sse":
                if "text/event-stream" not in response.headers.get("content-type", ""):
                    raise ValueError("Expected SSE content type")
                payload = None
                for event, data in sse_events(response.iter_lines()):
                    if event == "token" and isinstance(data, dict) and data.get("text") and first_token is None:
                        first_token = (perf_counter() - started) * 1000
                    elif event == "error":
                        raise ValueError("SSE error event")
                    elif event == "done":
                        payload = data
                        break
                if payload is None:
                    raise ValueError("Stream ended without done event")
            else:
                chunks, size = [], 0
                for chunk in response.iter_bytes():
                    size += len(chunk)
                    if size > MAX_RESPONSE_BYTES:
                        raise ValueError("Response exceeds size limit")
                    chunks.append(chunk)
                payload = json.loads(b"".join(chunks))
        return {**result, **score_response(q, payload, latency_ms=(perf_counter() - started) * 1000,
                                          ttft_ms=first_token, k=k)}
    except (httpx.HTTPError, ValueError) as exc:
        # Exception class only: URLs and upstream error bodies can contain secrets.
        return {**result, "error": type(exc).__name__}


def run_questions(client: httpx.Client, endpoint: str, questions: list[Question], *,
                  max_requests: int, protocol: str, repeats: int = 1, k: int = 5) -> list[dict[str, Any]]:
    if repeats < 1 or k < 1 or not questions:
        raise ValueError("Positive repeats/k and at least one question are required")
    if len(questions) * repeats > max_requests:
        raise ValueError("Request budget is smaller than the planned run")
    if any(not q.reviewed for q in questions):
        raise ValueError("Every selected question needs reviewed expected sources/outcomes")
    results = []
    for repeat in range(repeats):
        for q in questions:
            result = measure(client, endpoint, q, protocol=protocol, k=k)
            result["repeat"] = repeat + 1
            results.append(result)
            if result.get("status_code") == 429:
                return results  # Never retry or consume the rest of a daily budget.
    return results


def endpoint_url(base_url: str, protocol: str) -> str:
    parsed = urlsplit(base_url)
    if (parsed.scheme not in {"http", "https"} or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment):
        raise ValueError("Use an HTTP(S) base URL without credentials, query, or fragment")
    return base_url.rstrip("/") + ("/api/chat/stream" if protocol == "sse" else "/api/chat")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--base-url")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--execute", action="store_true")
    action.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-requests", type=int, default=0)
    parser.add_argument("--question-id", action="append", default=[])
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=35)
    parser.add_argument("--protocol", choices=["json", "sse"], default="json")
    parser.add_argument("--label", default="unlabelled")
    args = parser.parse_args(argv)
    try:
        raw = args.dataset.read_bytes()
        dataset = Dataset.model_validate_json(raw)
        questions = [q for q in dataset.questions if not args.question_id or q.id in args.question_id]
        unknown = set(args.question_id) - {q.id for q in dataset.questions}
        if unknown or args.repeats < 1 or args.k < 1 or not math.isfinite(args.timeout) or args.timeout <= 0:
            raise ValueError("Unknown question ID or invalid repeats/k/timeout")
        plan = {"dry_run": not args.execute, "label": args.label,
                "dataset_sha256": hashlib.sha256(raw).hexdigest(), "corpus_version": dataset.corpus_version,
                "protocol": args.protocol, "k": args.k, "planned_requests": len(questions) * args.repeats,
                "questions": [{"id": q.id, "question": q.question} for q in questions],
                "unreviewed_ids": [q.id for q in questions if not q.reviewed]}
        if not args.execute:
            print(json.dumps(plan, ensure_ascii=False, indent=2))
            return 0
        if plan["unreviewed_ids"]:
            raise ValueError("Selected questions need source/outcome review before execution")
        if not args.base_url:
            raise ValueError("Execution requires --base-url")
        endpoint = endpoint_url(args.base_url, args.protocol)
        if plan["planned_requests"] > args.max_requests:
            raise ValueError("Execution requires a sufficient --max-requests budget")
        with httpx.Client(timeout=args.timeout, follow_redirects=False, trust_env=False) as client:
            results = run_questions(client, endpoint, questions, repeats=args.repeats,
                                    max_requests=args.max_requests, protocol=args.protocol, k=args.k)
        report = {**plan, "endpoint": endpoint, "results": results,
                  "summary": summarize(results, planned=plan["planned_requests"])}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["summary"]["complete"] and all(r["passed"] for r in results) else 1
    except (OSError, ValueError) as exc:
        # Do not echo dataset contents or credentials from validation exceptions.
        message = str(exc) if type(exc) is ValueError else type(exc).__name__
        print(f"Evaluation refused: {message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
