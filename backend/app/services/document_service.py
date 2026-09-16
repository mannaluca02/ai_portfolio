"""Canonical, allowlisted portfolio evidence for embeddings and answers."""
import re
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from enum import Enum
from typing import Any

# These are public evidence fields, not an invitation to serialize entire rows.
# Keep private fields and vector/version columns out even if schemas expand.
DOCUMENT_FIELDS = {
    "work_experiences": ("company", "position", "location", "employment_type", "start_date", "end_date",
                         "description", "responsibilities", "technologies"),
    "projects": ("name", "description", "project_type", "start_date", "end_date", "technologies",
                 "your_role", "team_size", "client_company", "project_url", "github_url", "demo_url"),
    "skills": ("name", "skill_level", "category", "years_of_experience", "description"),
    "certificates": ("name", "issuing_organization", "issue_date", "expiration_date", "description"),
    "education": ("institution", "degree", "degree_type", "field_of_study", "location", "start_date",
                  "end_date", "grade", "description", "achievements"),
    "hobbies": ("name", "description", "since_year"),
    "languages": ("name", "level", "description"),
    "contact_info": ("full_name", "title", "bio", "city", "country", "email", "availability"),
    "social_links": ("platform", "url", "username"),
}

# Read to derive a value, never emitted verbatim. The age is a public fact the
# chatbot is asked for; the exact date of birth is personal data the model has
# no reason to repeat, so it is kept out of the evidence text entirely.
DERIVED_FIELDS = {"contact_info": ("birth_date",)}

TITLE_FIELDS = {"work_experiences": "position", "education": "degree",
                "contact_info": "full_name", "social_links": "platform"}


def _value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, Enum):
        return _value(value.value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return "; ".join(part for item in value if (part := _value(item)))
    return str(value).strip()


def redact_phones(text: str, numbers: Sequence[str]) -> str:
    """Remove known numbers even if punctuation/spacing differs in free text.

    A corpus loader should supply all denied numbers, not just the current row's.
    Do not guess phone numbers from arbitrary numeric facts such as dates/grades.
    """
    for number in numbers:
        digits = re.sub(r"\D", "", str(number))
        if len(digits) >= 7:
            pattern = r"(?<!\d)\+?" + r"[\s()./-]*".join(digits) + r"(?!\d)"
            text = re.sub(pattern, "[entfernt]", text)
    return text


def _as_date(value: Any) -> date | None:
    """Accept a date column, a datetime, or an ISO string from a mapping."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except (TypeError, ValueError):
        return None


def age_in_years(birth_date: Any, *, today: date | None = None) -> int | None:
    """Completed years, or None when the date is missing or not yet reached."""
    birth = _as_date(birth_date)
    if birth is None:
        return None
    # Local date on purpose: the age a Swiss visitor expects, not a UTC one.
    today = today or datetime.now().astimezone().date()
    years = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return years if years >= 0 else None


def document_text(table: str, row: Mapping[str, Any], *, phone_numbers: Sequence[str] = (),
                  today: date | None = None) -> str:
    if table not in DOCUMENT_FIELDS:
        raise ValueError(f"Unsupported portfolio table: {table}")
    lines = []
    for field in DOCUMENT_FIELDS[table]:
        value = _value(row.get(field))
        if value:
            lines.append(f"{field}: {value}")
    # Computed on every request, never stored: an age written into the database
    # is silently wrong from the next birthday onwards, and a language model
    # cannot be trusted to subtract a year from a date.
    if table == "contact_info":
        age = age_in_years(row.get("birth_date"), today=today)
        if age is not None:
            lines.append(f"age: {age} Jahre alt")
    denied = [*phone_numbers]
    if row.get("phone"):
        denied.append(str(row["phone"]))
    return redact_phones("\n".join(lines), denied)


def document_from_record(table: str, record: Any, *, phone_numbers: Sequence[str] = (),
                         today: date | None = None) -> str:
    """Accept ORM/SQL rows or mappings without serializing internal attributes."""
    if table not in DOCUMENT_FIELDS:
        raise ValueError(f"Unsupported portfolio table: {table}")
    if isinstance(record, Mapping):
        row = record
    else:
        fields = (*DOCUMENT_FIELDS[table], *DERIVED_FIELDS.get(table, ()), "phone")
        row = {field: getattr(record, field, None) for field in fields}
    return document_text(table, row, phone_numbers=phone_numbers, today=today)
