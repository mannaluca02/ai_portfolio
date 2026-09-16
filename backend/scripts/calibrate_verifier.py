"""Measure the verification threshold against the live corpus.

Read-only. Prints the similarity of supported and unsupported German claims
against a pinned source row, so the threshold in app/config.py is a measurement
rather than a guess. Sources are pinned by slug: retrieval quality is a separate
question and must not silently change the calibration.

    python backend/scripts/calibrate_verifier.py
"""
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import get_db_session
from app.services.document_service import document_from_record
from app.services.query_service import corpus_entities, corpus_vocabulary, subject_names
from app.services.retriever_service import RetrieverService
from app.services.verifier_service import get_verifier_service
from sqlalchemy import text

# (table, slug, claim, is_supported_by_that_row)
CASES = [
    ("skills", "skill-java", "Java ist eine sekundäre Backend-Sprache [1].", True),
    ("skills", "skill-agile", "Zu den Methoden gehören Scrum und Kanban [1].", True),
    ("skills", "skill-docker", "Docker wird für Containerisierung eingesetzt [1].", True),
    ("projects", "project-postfinance-horizons", "Das Projekt entstand an einem Hackathon [1].", True),
    ("projects", "project-fundyour-club", "Fundyour.club ermöglicht Vereinen das Sammeln von Spenden [1].", True),
    ("projects", "project-fundyour-club", "Die Plattform nutzt ein MVC-Backend in PHP [1].", True),
    ("education", "edu-bsc-data-science-fhnw", "Das Bachelorstudium umfasst Machine Learning und Statistik [1].", True),
    ("work_experiences", "work-novartis-ag-2020", "Bei Novartis gab es einen Einsatz im Second Level Support [1].", True),
    ("work_experiences", "work-novartis-ag-2020", "Es gab eine Anstellung bei Google [1].", False),
    ("education", "edu-bsc-data-science-fhnw", "Das Studium fand an der ETH Zürich statt [1].", False),
    ("skills", "skill-docker", "Docker wurde zwanzig Jahre lang eingesetzt [1].", False),
    ("skills", "skill-docker", "Docker wird nicht eingesetzt [1].", False),
    ("skills", "skill-java", "Es gibt einen Doktortitel in Medizin [1].", False),
    ("projects", "project-postfinance-horizons", "Das Projekt wurde für Microsoft entwickelt [1].", False),
    ("skills", "skill-agile", "Zu den Methoden gehört Waterfall [1].", False),
]
THRESHOLDS = (0.40, 0.45, 0.50, 0.55, 0.60, 0.65)


def main() -> int:
    logging.disable(logging.INFO)
    verifier = get_verifier_service()
    scored = []
    db = get_db_session()
    try:
        corpus_vocabulary(db)
        corpus_entities(db)
        subject_names(db)
        retriever = RetrieverService(db)
        formatters = {
            "skills": retriever._format_skill, "projects": retriever._format_project,
            "education": retriever._format_education,
            "work_experiences": retriever._format_work_experience,
        }
        for table, slug, claim, supported in CASES:
            row = db.execute(text(f"SELECT *, 1.0 as similarity FROM {table} WHERE slug = :slug"),
                             {"slug": slug}).fetchone()
            if row is None:
                print(f"SKIP missing row {table}/{slug}", file=sys.stderr)
                continue
            source = formatters[table](row, table)
            source.document = document_from_record(table, row)
            detail = verifier.verify_response(claim, [source], threshold=0.0).details[0]
            # A structural rejection scores zero; that is a decision, not a score.
            scored.append((supported, 0.0 if "error" in detail else detail["similarity"], claim))
    finally:
        db.close()

    for supported, score, claim in sorted(scored, key=lambda row: -row[1]):
        print(f"{'SUPPORTED  ' if supported else 'UNSUPPORTED'} {score:6.3f}  {claim}")
    true_scores = [s for supported, s, _ in scored if supported]
    false_scores = [s for supported, s, _ in scored if not supported]
    print()
    for threshold in THRESHOLDS:
        accepted_true = sum(score >= threshold for score in true_scores)
        accepted_false = sum(score >= threshold for score in false_scores)
        print(f"threshold {threshold:.2f}: accepts {accepted_true}/{len(true_scores)} supported, "
              f"{accepted_false}/{len(false_scores)} unsupported")
    return 0


if __name__ == "__main__":
    sys.exit(main())
