import json
from pathlib import Path
import pytest
from scripts.load_translations import main, validate_manifest

DRAFT = Path(__file__).resolve().parents[1] / 'translations/en.draft.json'


def test_complete_draft_is_valid_and_remains_unapproved():
    manifest = json.loads(DRAFT.read_text())
    assert manifest['status'] == 'draft'
    assert len(validate_manifest(manifest)) == 59
    assert main([str(DRAFT), '--dry-run']) == 0
    assert main([str(DRAFT), '--execute']) == 1


def test_loader_rejects_changes_to_language_independent_fields():
    entry = {'source_table': 'projects', 'slug': 'project', 'locale': 'en',
             'field': 'slug', 'source_value': 'project', 'value': 'changed'}
    with pytest.raises(ValueError, match='Unsupported table or field'):
        validate_manifest({'entries': [entry]})


def test_loader_rejects_duplicate_fields():
    entry = {'source_table': 'projects', 'slug': 'project', 'locale': 'en',
             'field': 'description', 'source_value': 'Deutsch', 'value': 'English'}
    with pytest.raises(ValueError, match='Duplicate'):
        validate_manifest({'entries': [entry, entry]})
