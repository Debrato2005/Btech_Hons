#!/usr/bin/env python3
"""Build a validated, offline, single-file study app without network dependencies.

The default checkpoint includes complete source PDFs and all diagrams. Exact page
images are optional when the same evidence is available in an embedded PDF, to
avoid duplicating the entire 2,012-page corpus. No remote resource is loaded by the
resulting HTML. Native PDF viewers receive local Blob URLs, not network URLs.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import load_json, validate_bank  # noqa: E402


def script_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def confined_path(path):
    resolved = (ROOT / path).resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError(f'Asset path escapes project: {path}')
    return resolved


def selected_assets(bank, include_page_previews=False):
    pdf_sources = {source['id'] for source in bank['sources'] if source.get('assetId') and any(asset['id'] == source['assetId'] for asset in bank['assets'])}
    directly_required = {aid for q in bank['questions'] for aid in q.get('assetIds', [])}
    directly_required.update(aid for binding in bank.get('questionVisuals', {}).get('bindings', {}).values() for aid in binding['assetIds'])
    for records in bank['learningTools'].values():
        for record in records:
            directly_required.update(record.get('assetIds', []))
    chosen = []
    for asset in bank['assets']:
        if asset['kind'] == 'source_page' and not include_page_previews and asset.get('sourceId') in pdf_sources and asset['id'] not in directly_required:
            continue
        chosen.append(asset)
    return chosen


def stream_assets(handle, assets):
    handle.write('{')
    for index, asset in enumerate(assets):
        if index:
            handle.write(',')
        handle.write(script_json(asset['id']) + ':')
        metadata = {key: value for key, value in asset.items() if key != 'data'}
        handle.write(script_json(metadata)[:-1] + ',"data":"')
        # 3-divisible chunks preserve a single uninterrupted base64 stream.
        encoded_hash = hashlib.sha256()
        with confined_path(asset['path']).open('rb') as source:
            for chunk in iter(lambda: source.read(3 * 16384), b''):
                encoded_hash.update(chunk)
                handle.write(base64.b64encode(chunk).decode('ascii'))
        if encoded_hash.hexdigest() != asset['sha256']:
            raise ValueError('Embedded asset changed during build: ' + asset['id'])
        handle.write('"}')
    handle.write('}')


def build(args):
    started = time.perf_counter()
    bank = load_json(args.bank)
    if args.test_fixture:
        if args.release:
            raise ValueError('Synthetic test fixtures can never be release builds.')
        if args.output == ROOT / 'dist' / 'ai-for-robotics-mcq.html':
            raise ValueError('Choose --output outside the course deliverable filename for synthetic test fixtures.')
        bank = dict(bank)
        bank['complete'] = False
        bank['title'] = 'SYNTHETIC SOFTWARE TEST FIXTURE · NOT COURSE CONTENT'
        bank['bankVersion'] = 'SYNTHETIC-TEST-' + bank['bankVersion']
    report = validate_bank(bank, ROOT, release=args.release, allow_synthetic=args.test_fixture, check_files=True)
    if not report['valid']:
        for error in report['errors']:
            print('ERROR:', error, file=sys.stderr)
        raise ValueError('Build refused: bank integrity validation failed.')
    chosen = selected_assets(bank, args.include_page_previews)
    required_visuals = {aid for binding in bank.get('questionVisuals', {}).get('bindings', {}).values() for aid in binding['assetIds']}
    if not required_visuals <= {a['id'] for a in chosen}:
        raise ValueError('Build refused: reviewed required question visuals were not selected for offline embedding.')
    assets_by_id = {asset['id']: asset for asset in chosen}
    sources = {source['id']: source for source in bank['sources']}
    slides = {slide['id']: slide for slide in bank['slides']}
    missing_evidence = []
    for question in bank['questions']:
        if question['status'] != 'verified':
            continue
        for citation in question['citations']:
            slide = slides[citation['slideId']]
            source = sources[citation['sourceId']]
            if slide.get('assetId') not in assets_by_id and source.get('assetId') not in assets_by_id:
                missing_evidence.append(f'{question["id"]}: {citation["slideId"]}')
    # Verified course evidence is always inspectable, even in partial checkpoints.
    if missing_evidence:
        raise ValueError('Verified questions lack embedded source evidence: ' + ', '.join(missing_evidence))
    estimated_bytes = sum(confined_path(a['path']).stat().st_size * 4 // 3 + 8 for a in chosen)
    if estimated_bytes > 90 * 1024 * 1024:
        print(f'WARNING: assets alone will occupy {estimated_bytes/1024/1024:.1f} MiB; use a release asset rather than a Git object if total exceeds hosting limits.', file=sys.stderr)
    assets_stats = [{'id': a['id'], 'kind': a['kind'], 'bytes': confined_path(a['path']).stat().st_size, 'sha256': a['sha256']} for a in chosen]
    template = (ROOT / 'app' / 'index.html').read_text(encoding='utf-8')
    replacements = {
        'STYLES': (ROOT / 'app' / 'styles.css').read_text(encoding='utf-8'),
        'CORE': (ROOT / 'app' / 'core.js').read_text(encoding='utf-8'),
        'LEARNING_RESOURCES': (ROOT / 'app' / 'learning-resources.js').read_text(encoding='utf-8'),
        'LEARNING_RESOURCE_UI': (ROOT / 'app' / 'learning-resource-ui.js').read_text(encoding='utf-8'),
        'APP': (ROOT / 'app' / 'app.js').read_text(encoding='utf-8'),
        'COURSE_NUMERICAL': (ROOT / 'app' / 'course-numerical.js').read_text(encoding='utf-8'),
        'LEARNING_TOOLS': (ROOT / 'app' / 'learning-tools.js').read_text(encoding='utf-8') if (ROOT / 'app' / 'learning-tools.js').exists() else '/* No learning-tools engine packaged. */',
        'BANK': script_json(bank),
    }
    for key in ('CORE', 'APP', 'LEARNING_TOOLS', 'LEARNING_RESOURCES', 'LEARNING_RESOURCE_UI', 'COURSE_NUMERICAL'):
        if re.search(r'</script', replacements[key], flags=re.I):
            raise ValueError(f'Unescaped closing script tag in {key}.')
    if re.search(r'(?:src|href)\s*=\s*["\']https?://', template, flags=re.I):
        raise ValueError('External runtime resource in HTML template.')
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + '.tmp')
    try:
        with temporary.open('w', encoding='utf-8', newline='\n') as handle:
            cursor = 0
            for match in re.finditer(r'/\*__([A-Z_]+)__\*/', template):
                handle.write(template[cursor:match.start()])
                token = match.group(1)
                if token == 'ASSETS':
                    stream_assets(handle, chosen)
                elif token in replacements:
                    handle.write(replacements[token])
                else:
                    raise ValueError(f'Unknown build token {token}')
                cursor = match.end()
            handle.write(template[cursor:])
        size = temporary.stat().st_size
        if args.max_size_mib and size > args.max_size_mib * 1024 * 1024:
            raise ValueError(f'Build is {size/1024/1024:.2f} MiB, above --max-size-mib={args.max_size_mib}. No source evidence was silently omitted. Choose a durable large-file delivery route.')
        # Recheck current local supplemental bytes after serialization, before publication.
        for name, artifact in bank.get('questionVisuals', {}).get('supplementalArtifacts', {}).items():
            if hashlib.sha256(confined_path(name).read_bytes()).hexdigest() != artifact['sha256']:
                raise ValueError('Build refused: supplemental source changed during build: ' + name)
        os.replace(temporary, output)
    finally:
        if temporary.exists():
            temporary.unlink()
    digest = hashlib.sha256()
    with output.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    result = {
        'schemaVersion': '1.0.0', 'bankVersion': bank['bankVersion'], 'complete': bank['complete'],
        'syntheticTestFixture': args.test_fixture, 'output': str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output),
        'bytes': size, 'mebibytes': round(size / 1024 / 1024, 3), 'sha256': digest.hexdigest(),
        'buildSeconds': round(time.perf_counter() - started, 3), 'embeddedAssets': assets_stats,
        'omittedDuplicatePagePreviews': len(bank['assets']) - len(chosen), 'offlineEvidence': 'Complete embedded PDF or exact source-page asset for every verified citation',
        'runtimeNetworkDependencies': [], 'validation': report,
        'questionVisuals': {'reviewedDispositions': len(bank.get('questionVisuals', {}).get('bindings', {})), 'requiredAssetIds': sorted(required_visuals), 'requiredAssetBytes': sum(confined_path(a['path']).stat().st_size for a in chosen if a['id'] in required_visuals), 'supplementalInputIds': sorted(bank.get('questionVisuals', {}).get('supplementalBindings', {})), 'supplementalArtifacts': {name: {'sha256': artifact['sha256'], 'utf8Bytes': len(artifact['rawText'].encode('utf-8'))} for name, artifact in bank.get('questionVisuals', {}).get('supplementalArtifacts', {}).items()}, 'packaging': 'Exact lossless PNG bytes, one shared asset ID per pixel hash; separate verbatim notebook/code text and local-file SHA-256 bindings; complete original PDFs retained.'},
        'performanceNote': 'Build time is not browser load time. Browser performance and offline PDF display require separate runtime QA.'
    }
    output.with_suffix('.build-report.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('output', 'bytes', 'mebibytes', 'sha256', 'buildSeconds', 'complete')}, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bank', type=Path, default=ROOT / 'data' / 'bank.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist' / 'ai-for-robotics-mcq.html')
    parser.add_argument('--release', action='store_true', help='Require complete coverage and independent coverage-challenge gates')
    parser.add_argument('--include-page-previews', action='store_true', help='Embed exact page images in addition to full source PDFs')
    parser.add_argument('--max-size-mib', type=float, default=0, help='Fail rather than silently reduce evidence if output exceeds this limit')
    parser.add_argument('--test-fixture', action='store_true', help='Explicitly permit synthetic bank ONLY in a separately named software-test artifact')
    args = parser.parse_args()
    try:
        build(args)
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
