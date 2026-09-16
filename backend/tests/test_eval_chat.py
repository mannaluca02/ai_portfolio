"""Offline acceptance tests for the budgeted chat evaluator."""
import json
from unittest.mock import Mock

import httpx
import pytest
from scripts import eval_chat


def question(**changes):
    return eval_chat.Question.model_validate({
        "id": "python", "question": "Kann Luca Python?", "reviewed": True,
        "expected_outcome": "answered",
        "expected_sources": [{"table": "skills", "slug": "python"}],
        **changes,
    })


def answer(**changes):
    return {"answer": "Luca nutzt Python [1].", "outcome": "answered",
            "sources": [{"index": 1, "table": "skills", "slug": "python"}],
            "verification": {"is_verified": True}, **changes}


def test_metrics_do_not_confuse_citations_with_retrieval():
    measured = eval_chat.score_response(question(), answer(), latency_ms=100)
    assert measured["recall_at_k"] is None
    assert measured["wrong_source_rate"] == 0
    assert measured["passed"] is True
    assert measured["ttft_ms"] is None


def test_recall_uses_retrieved_order_and_deduplicates_sources():
    payload = answer(metadata={"retrieved_sources": [
        {"table": "projects", "slug": "other"},
        {"table": "skills", "slug": "python"},
        {"table": "skills", "slug": "python"},
    ]})
    assert eval_chat.score_response(question(), payload, latency_ms=1, k=1)["recall_at_k"] == 0
    assert eval_chat.score_response(question(), payload, latency_ms=1, k=5)["recall_at_k"] == 1


def test_wrong_sources_and_forbidden_claims_fail():
    q = question(forbidden_answer_fragments=["Google"])
    measured = eval_chat.score_response(q, answer(answer="Luca arbeitet bei Google [1].",
        sources=[{"index": 1, "table": "work_experiences", "slug": "google"}]), latency_ms=1)
    assert measured["wrong_source_rate"] == 1
    assert measured["passed"] is False
    assert measured["forbidden_fragments_found"] == ["Google"]


@pytest.mark.parametrize("payload", [
    answer(verification={"is_verified": False}),
    answer(answer="Luca nutzt Python."),
    answer(answer="Luca nutzt Python [9]."),
    answer(sources=[]),
    {"answer": "anything"},
    answer(outcome=["answered"]),
])
def test_malformed_or_unverified_answers_cannot_pass(payload):
    measured = eval_chat.score_response(question(), payload, latency_ms=1)
    assert measured["passed"] is False
    assert measured["contract_ok"] is False


def test_legitimate_abstention_is_distinct_from_an_error():
    q = question(expected_outcome="no_information", expected_sources=[])
    measured = eval_chat.score_response(q, answer(answer="Keine Information.",
        outcome="no_information", sources=[], verification=None), latency_ms=20)
    assert measured["passed"] is True
    assert measured["recall_at_k"] is None
    assert measured["wrong_source_rate"] is None


def test_summary_keeps_errors_in_denominator_and_missing_metrics_null():
    valid = eval_chat.score_response(question(), answer(), latency_ms=100)
    failed = {"id": "error", "error": "HTTP 503", "passed": False}
    report = eval_chat.summarize([valid, failed], planned=3)
    assert report["attempted"] == 2
    assert report["planned"] == 3
    assert report["answer_rate"] == 0.5
    assert report["pass_rate"] == 0.5
    assert report["latency_ms"] == {"p50": 100, "p95": 100, "samples": 1}
    assert report["ttft_ms"] == {"p50": None, "p95": None, "samples": 0}
    assert report["recall_at_k"] is None


def test_empty_summary_does_not_claim_success():
    report = eval_chat.summarize([], planned=40)
    assert report["pass_rate"] is None
    assert report["answer_rate"] is None
    assert report["complete"] is False


def test_percentiles_use_documented_linear_interpolation():
    assert eval_chat.percentile([100, 200, 300, 400], 0.5) == 250
    assert eval_chat.percentile([100, 200, 300, 400], 0.95) == 385


def test_json_transport_never_invents_ttft():
    with httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, json=answer()))) as client:
        result = eval_chat.measure(client, "http://test/api/chat", question(), protocol="json")
    assert result["passed"] is True
    assert result["ttft_ms"] is None
    assert result["latency_ms"] >= 0


def test_sse_handles_comments_multiple_data_lines_and_final_response():
    stream = ': heartbeat\r\n\r\nevent: token\r\ndata: {"text":\r\ndata: "Luca"}\r\n\r\n'
    stream += 'event: done\ndata: ' + json.dumps(answer()) + '\n\n'
    with httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200,
        headers={"content-type": "text/event-stream"}, text=stream))) as client:
        result = eval_chat.measure(client, "http://test/api/chat/stream", question(), protocol="sse")
    assert result["passed"] is True
    assert 0 <= result["ttft_ms"] <= result["latency_ms"]


@pytest.mark.parametrize("stream", [
    'event: token\ndata: {"text":"hello"}\n\n',
    'event: done\ndata: invalid json\n\n',
    'event: error\ndata: {"message":"private details"}\n\n',
])
def test_incomplete_or_invalid_sse_is_an_error(stream):
    with httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200,
        headers={"content-type": "text/event-stream"}, text=stream))) as client:
        result = eval_chat.measure(client, "http://test/api/chat/stream", question(), protocol="sse")
    assert result["passed"] is False
    assert result["error"]
    assert "private details" not in json.dumps(result)


def test_rate_limit_stops_the_run_without_retries():
    handler = Mock(return_value=httpx.Response(429, headers={"retry-after": "60"}))
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        results = eval_chat.run_questions(client, "http://test/api/chat", [question()], repeats=3,
                                         max_requests=3, protocol="json")
    assert handler.call_count == 1
    assert results[0]["status_code"] == 429
    assert results[0]["retry_after"] == "60"


def test_request_budget_is_checked_before_any_network_call():
    client = Mock()
    with pytest.raises(ValueError, match="budget"):
        eval_chat.run_questions(client, "http://test/api/chat", [question()], repeats=2,
                                max_requests=1, protocol="json")
    client.stream.assert_not_called()


def test_unreviewed_questions_cannot_be_executed():
    client = Mock()
    with pytest.raises(ValueError, match="review"):
        eval_chat.run_questions(client, "http://test/api/chat", [question(reviewed=False)],
                                max_requests=1, protocol="json")
    client.stream.assert_not_called()


def test_cli_defaults_to_dry_run_without_constructing_client(monkeypatch, capsys):
    client = Mock(side_effect=AssertionError("No network allowed"))
    monkeypatch.setattr(eval_chat.httpx, "Client", client)
    assert eval_chat.main([]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["dry_run"] is True
    expected = eval_chat.Dataset.model_validate_json(eval_chat.DEFAULT_DATASET.read_bytes())
    assert report["planned_requests"] == len(expected.questions)
    assert report["unreviewed_ids"]
    client.assert_not_called()


def test_cli_rejects_unreviewed_baseline_before_constructing_client(monkeypatch, capsys):
    client = Mock(side_effect=AssertionError("No network allowed"))
    monkeypatch.setattr(eval_chat.httpx, "Client", client)
    assert eval_chat.main(["--execute", "--base-url", "https://example.com", "--max-requests", "40"]) == 2
    assert "review" in capsys.readouterr().err
    client.assert_not_called()


@pytest.mark.parametrize("url", ["https://user:secret@example.com", "https://example.com?key=secret", "file:///tmp/x"])
def test_endpoint_rejects_credentials_queries_and_non_http_urls(url):
    with pytest.raises(ValueError):
        eval_chat.endpoint_url(url, "json")


@pytest.mark.parametrize("changes", [
    {"expected_outcome": None},
    {"expected_sources": []},
    {"expected_outcome": "no_information"},
    {"expected_sources": [{"table": "skills", "slug": "python"}] * 2},
])
def test_review_requires_consistent_complete_labels(changes):
    with pytest.raises(ValueError):
        question(**changes)


def test_required_fragments_are_checked_without_case_sensitivity():
    q = question(required_answer_fragments=["PYTHON", "Docker"])
    result = eval_chat.score_response(q, answer(), latency_ms=1)
    assert result["required_fragments_missing"] == ["Docker"]
    assert result["passed"] is False


def test_malformed_retrieval_instrumentation_is_not_zero_recall():
    result = eval_chat.score_response(question(), answer(metadata={"retrieved_sources": "wrong type"}), latency_ms=1)
    assert result["recall_at_k"] is None


@pytest.mark.parametrize("protocol", ["json", "sse"])
def test_response_size_limit_is_enforced(protocol, monkeypatch):
    monkeypatch.setattr(eval_chat, "MAX_RESPONSE_BYTES", 10)
    body = json.dumps(answer()) if protocol == "json" else 'event: done\ndata: ' + json.dumps(answer()) + '\n\n'
    with httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200,
        text=body, headers={"content-type": "text/event-stream"}))) as client:
        result = eval_chat.measure(client, "http://test/api/chat", question(), protocol=protocol)
    assert result["error"] == "ValueError"


@pytest.fixture
def reviewed_dataset(monkeypatch):
    data = {"schema_version": 1, "corpus_version": "synthetic-fixture-v1",
            "questions": [question().model_dump()]}
    monkeypatch.setattr(eval_chat.Path, "read_bytes", lambda _: json.dumps(data).encode())


def test_cli_executes_with_budget_and_reports_results(reviewed_dataset, monkeypatch, capsys):
    client = httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, json=answer())))
    monkeypatch.setattr(eval_chat.httpx, "Client", lambda **kwargs: client)
    assert eval_chat.main(["--execute", "--base-url", "http://test", "--max-requests", "1"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["summary"]["pass_rate"] == 1
    assert report["endpoint"] == "http://test/api/chat"
    assert report["corpus_version"] == "synthetic-fixture-v1"


@pytest.mark.parametrize("args", [
    ["--execute"],
    ["--execute", "--base-url", "http://test"],
    ["--question-id", "missing"],
    ["--timeout", "nan"],
    ["--repeats", "0"],
])
def test_cli_invalid_arguments_make_no_requests(args, reviewed_dataset, monkeypatch, capsys):
    client = Mock(side_effect=AssertionError("No network allowed"))
    monkeypatch.setattr(eval_chat.httpx, "Client", client)
    assert eval_chat.main(args) == 2
    assert "Evaluation refused" in capsys.readouterr().err
    client.assert_not_called()


def test_public_source_labels_resolve_to_reviewed_records():
    root = eval_chat.DEFAULT_DATASET.parent
    dataset = eval_chat.Dataset.model_validate_json(eval_chat.DEFAULT_DATASET.read_bytes())
    records = json.loads((root / "source_review.json").read_text())["records"]
    keys = {(row["table"], row["slug"]) for row in records}
    reviewed = [q for q in dataset.questions if q.reviewed]
    assert len(reviewed) >= 12
    assert all((source.table, source.slug) in keys for q in reviewed for source in q.expected_sources)
    assert all("phone" not in row for row in records)


def test_production_log_questions_are_present_verbatim_and_reviewed():
    """The owner's real 2026-09-10 log is the primary regression target."""
    dataset = eval_chat.Dataset.model_validate_json(eval_chat.DEFAULT_DATASET.read_bytes())
    log = {q.question: q for q in dataset.questions if q.id.startswith("log")}
    assert len(log) == 12
    assert all(q.reviewed for q in log.values())
    # Pronoun, second-person and typo phrasing must survive verbatim: it is part
    # of what production failed on, and normalising it would hide the defect.
    assert {"Wie alt ist er?", "Kann er Docker?", "Kannst du java?",
            "Ist er in Agile Development ein exoierte¨"} <= set(log)
    # Answerable since birth_date exists; the label tracks the target corpus,
    # which needs migration_4_birth_date.sql and a re-run of the embeddings.
    assert log["Wie alt ist er?"].expected_outcome == "answered"
