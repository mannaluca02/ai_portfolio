"""Read-only presentation overlays; never change rows used for RAG evidence."""
from typing import Literal

from sqlalchemy import bindparam, text

Language = Literal['de', 'en']

TRANSLATABLE_FIELDS = {
    'work_experiences': {'position', 'location', 'description', 'responsibilities'},
    'projects': {'name', 'description', 'your_role', 'client_company'},
    'skills': {'description'},
    'certificates': {'name', 'description'},
    'education': {'degree', 'field_of_study', 'location', 'description', 'achievements'},
    'contact_info': {'title', 'city', 'country', 'availability', 'bio'},
    'hobbies': {'name', 'description'},
    'languages': {'name', 'level', 'description'},
}
ARRAY_FIELDS = {'responsibilities', 'achievements'}


def overlay_translations(db, table: str, rows: list, language: Language) -> list:
    if language == 'de' or not rows or table not in TRANSLATABLE_FIELDS:
        return rows
    # Copy mapped column values only, without SQLAlchemy state or lazy relationships.
    copies = [dict(row) if isinstance(row, dict) else {
        column.key: getattr(row, column.key) for column in row.__table__.columns
    } for row in rows]
    by_id = {row['id']: row for row in copies}
    query = text('SELECT source_id, field, value FROM content_translations '
                 'WHERE source_table = :table AND locale = :locale '
                 'AND source_id IN :ids').bindparams(bindparam('ids', expanding=True))
    translations = db.execute(query, {'table': table, 'locale': language,
                                      'ids': list(by_id)}).mappings().all()
    for translation in translations:
        field, value = translation['field'], translation['value']
        valid = (isinstance(value, list) and all(isinstance(item, str) for item in value)
                 if field in ARRAY_FIELDS else isinstance(value, str))
        if (translation['source_id'] in by_id and field in TRANSLATABLE_FIELDS[table]
                and valid):
            by_id[translation['source_id']][field] = value
    return copies
