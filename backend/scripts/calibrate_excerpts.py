"""Measure the excerpt gate against the live corpus.

Read-only. When verification rejects an answer, the visitor is shown portfolio
excerpts instead. Which rows are worth showing is a presentation decision, and
it was a hardcoded 0.45 with no measurement behind it, which is how "Fitness"
and "Heim Netzwerk" ended up next to "Novartis" for "wo arbeitest du?".

For every reviewed question this prints the retrieved rows with their similarity
and whether the row is one of the labelled expected sources, then scores each
candidate (floor, gap) pair on the only two things that matter: does the right
row still get shown, and does anything unrelated come with it.

    python backend/scripts/calibrate_excerpts.py

    --dataset  question file (default backend/tests/data/golden_questions.json)
    --ids      only these question ids
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import get_db_session
from app.schemas.chat import ChatMode
from app.services.chatbot_service import EXCERPT_LIMIT, ChatbotService
from app.services.query_service import corpus_entities, corpus_vocabulary, subject_names

DEFAULT_DATASET = Path(__file__).resolve().parents[1] / "tests/data/golden_questions.json"
FLOORS = (0.40, 0.42, 0.45, 0.48)
GAPS = (0.03, 0.07, 0.15)


def selected(rows, floor: float, gap: float, limit: int = EXCERPT_LIMIT,
             same_table: bool = False):
    """The gate under test, kept identical in shape to ChatbotService.

    `same_table` is the candidate rule for the reported noise: a hobby row
    0.006 behind a work row is not a second answer to "wo hat luca gearbeitet",
    it is the export feeling the owner complained about.
    """
    ranked = sorted((row for row in rows if not row["off_topic"]),
                    key=lambda row: row["similarity"], reverse=True)
    if not ranked:
        return []
    best = ranked[0]
    return [row for row in ranked
            if row["similarity"] >= floor
            and best["similarity"] - row["similarity"] <= gap
            and (not same_table or row["table"] == best["table"])][:limit]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--ids", nargs="*", default=None)
    args = parser.parse_args(argv)

    logging.disable(logging.INFO)
    dataset = json.loads(args.dataset.read_text())
    questions = [q for q in dataset["questions"] if q.get("reviewed")
                 and (args.ids is None or q["id"] in args.ids)]
    if not questions:
        print("No reviewed questions selected", file=sys.stderr)
        return 2

    measured = []
    db = get_db_session()
    try:
        corpus_vocabulary(db)
        corpus_entities(db)
        subject_names(db)
        service = ChatbotService(db)
        for question in questions:
            expected = {(source["table"], source["slug"])
                        for source in question.get("expected_sources", [])}
            results = service._retrieve_documents(question["question"], ChatMode.NATURAL)
            rows = [{"table": result.table, "slug": result.slug, "similarity": result.similarity,
                     "title": result.title, "off_topic": result.off_topic,
                     "expected": (result.table, result.slug) in expected}
                    for result in results]
            measured.append({"id": question["id"], "question": question["question"],
                             "expected": expected, "rows": rows})
            print(f"\n{question['id']}  {question['question']}")
            for row in sorted(rows, key=lambda row: -row["similarity"]):
                mark = "*" if row["expected"] else "-" if row["off_topic"] else " "
                print(f"  {mark} {row['similarity']:.3f}  {row['table']:<18} {row['title'][:46]}")
            if not rows:
                print("    (nothing retrieved)")
    finally:
        db.close()

    labelled = [entry for entry in measured if entry["expected"]]
    total = len(labelled)
    variants = (("limit 2", 2, False), ("limit 2, same table", 2, True), ("limit 1", 1, False))
    print(f"\nOver {total} labelled questions. right = an expected row is shown, "
          "clean = nothing but expected rows, wrong = excerpts with no expected row.")
    for name, limit, same_table in variants:
        print(f"\n{name}")
        print("floor  gap    right  clean  wrong  silent")
        for floor in FLOORS:
            for gap in GAPS:
                hit = only = shown = 0
                for entry in labelled:
                    chosen = selected(entry["rows"], floor, gap, limit, same_table)
                    shown += bool(chosen)
                    if chosen and any(row["expected"] for row in chosen):
                        hit += 1
                        only += all(row["expected"] for row in chosen)
                print(f"{floor:.2f}   {gap:.2f}  {hit:>5}  {only:>5}  {shown - hit:>5}  {total - shown:>6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
