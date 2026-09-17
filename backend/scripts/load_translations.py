"""Validate a reviewed translation manifest, or apply it in one transaction.

Dry run is the default and needs no database. Execution uses DATABASE_URL from
process environment only; this script never loads .env files. Set manifest
status to 'approved' only after the owner has reviewed its contents.
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.translation_service import ARRAY_FIELDS, TRANSLATABLE_FIELDS


def validate_manifest(manifest):
    entries = manifest['entries']
    if not isinstance(entries, list) or not entries:
        raise ValueError('Manifest needs nonempty entries')
    seen = set()
    for entry in entries:
        table, field = entry['source_table'], entry['field']
        if table not in TRANSLATABLE_FIELDS or field not in TRANSLATABLE_FIELDS[table]:
            raise ValueError('Unsupported table or field')
        if entry['locale'] != 'en' or not isinstance(entry['slug'], str) or not entry['slug']:
            raise ValueError('Invalid locale or slug')
        value = entry['value']
        valid = (isinstance(value, list) and all(isinstance(item, str) for item in value)
                 if field in ARRAY_FIELDS else isinstance(value, str) and bool(value.strip()))
        if not valid or 'source_value' not in entry:
            raise ValueError('Invalid translation type or missing source snapshot')
        key = (table, entry['slug'], entry['locale'], field)
        if key in seen:
            raise ValueError('Duplicate translation key')
        seen.add(key)
    return entries


def apply_entries(connection, entries):
    from sqlalchemy import text
    for entry in entries:
        table, field = entry['source_table'], entry['field']
        # SQL identifiers come exclusively from the validated allowlist.
        source = connection.execute(text(f'SELECT id, "{field}" FROM "{table}" '
                                         'WHERE slug = :slug FOR SHARE'),
                                    {'slug': entry['slug']}).mappings().one()
        if source[field] != entry['source_value']:
            raise ValueError(f'Source changed: {table}/{entry["slug"]}/{field}')
        connection.execute(text('INSERT INTO content_translations '
            '(source_table, source_id, locale, field, value) '
            'VALUES (:table, :id, :locale, :field, CAST(:value AS jsonb)) '
            'ON CONFLICT (source_table, source_id, locale, field) '
            'DO UPDATE SET value = EXCLUDED.value'),
            {'table': table, 'id': source['id'], 'locale': entry['locale'],
             'field': field, 'value': json.dumps(entry['value'], ensure_ascii=False)})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--dry-run', action='store_true')
    action.add_argument('--execute', action='store_true')
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text())
        entries = validate_manifest(manifest)
        if not args.execute:
            print(json.dumps({'dry_run': True, 'status': manifest.get('status'),
                              'fields': len(entries),
                              'tables': sorted({e['source_table'] for e in entries}),
                              'source_checks': 'Execution rejects missing or changed source rows.'}))
            return 0
        if manifest.get('status') != 'approved':
            raise ValueError('Owner approval is required: manifest status is not approved')
        if not os.environ.get('DATABASE_URL'):
            raise ValueError('DATABASE_URL must be supplied through process environment')
        from sqlalchemy import create_engine
        engine = create_engine(os.environ['DATABASE_URL'])
        try:
            with engine.begin() as connection:
                apply_entries(connection, entries)
        finally:
            engine.dispose()
        print(f'Applied {len(entries)} approved translation fields.')
        return 0
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1
    except Exception as error:
        # Connection errors can contain credentials; report the class only.
        print(f'Translation import failed: {type(error).__name__}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
