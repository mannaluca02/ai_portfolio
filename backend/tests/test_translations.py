from types import SimpleNamespace
from unittest.mock import Mock

from app.services.translation_service import overlay_translations


def test_overlay_is_partial_and_does_not_mutate_source():
    row = {'id': 1, 'description': 'Deutsch', 'name': 'Original', 'slug': 'stable', 'responsibilities': ['Alt']}
    db = Mock()
    db.execute.return_value.mappings.return_value.all.return_value = [
        {'source_id': 1, 'field': 'description', 'value': 'English'},
        {'source_id': 1, 'field': 'responsibilities', 'value': ['New']},
        {'source_id': 1, 'field': 'slug', 'value': 'unsafe-change'},
    ]
    result = overlay_translations(db, 'work_experiences', [row], 'en')
    assert result[0]['description'] == 'English'
    assert result[0]['responsibilities'] == ['New']
    assert result[0]['name'] == 'Original'
    assert result[0]['slug'] == 'stable'
    assert row['description'] == 'Deutsch'


def test_german_never_queries_translation_table():
    db = Mock()
    rows = [{'id': 1, 'description': 'Deutsch'}]
    assert overlay_translations(db, 'projects', rows, 'de') == rows
    db.execute.assert_not_called()


def test_missing_or_wrong_type_translation_falls_back():
    db = Mock()
    db.execute.return_value.mappings.return_value.all.return_value = [
        {'source_id': 1, 'field': 'description', 'value': ['Wrong type']},
        {'source_id': 1, 'field': 'responsibilities', 'value': 'Wrong type'},
    ]
    rows = [{'id': 1, 'description': 'Deutsch', 'responsibilities': ['Original']}]
    assert overlay_translations(db, 'work_experiences', rows, 'en') == rows
