#!/usr/bin/env python3
"""Package the unchanged single HTML losslessly, with exact-byte delivery receipts.

This neither builds the HTML nor grants release/browser/source approval. It refuses
an unbound build report, malformed embedded bytes, and synthetic course artifacts.
No upload, Git operation, network request or dependency installation is performed.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import mmap
import os
from pathlib import Path
from datetime import datetime, timezone
import zipfile
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from embedded_payloads import assets as embedded_assets, decoded_chunks

ROOT = Path(__file__).resolve().parents[1]


def digest_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def verify_embedded_assets(html, expected_assets):
    """Validate decoded embedded bytes without loading PDFs/HTML wholesale."""
    results = []
    with Path(html).open('rb') as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as data:
        if b'"payloadId":' in data[:min(len(data), 32 * 1024 * 1024)]:
            expected = {a['id']: a for a in expected_assets}
            seen = set()
            for metadata, start, end in embedded_assets(data):
                aid = metadata['id']
                if aid in seen or aid not in expected:
                    raise ValueError('Unexpected or duplicate embedded asset: ' + aid)
                seen.add(aid)
                asset = expected[aid]
                digest, size, prefix = hashlib.sha256(), 0, b''
                for block in decoded_chunks(data, start, end):
                    if not prefix:
                        prefix = block[:8]
                    digest.update(block)
                    size += len(block)
                if metadata.get('sha256') != asset['sha256'] or digest.hexdigest() != asset['sha256'] or size != asset['bytes']:
                    raise ValueError('Embedded bytes differ from original source/asset: ' + aid)
                if asset['kind'] == 'source_pdf' and not prefix.startswith(b'%PDF-'):
                    raise ValueError('Source PDF bytes lack PDF header: ' + aid)
                results.append({**asset, 'embeddedByteIdentity': 'verified'})
            if seen != set(expected) or len(seen) != len(expected_assets):
                raise ValueError('Embedded asset inventory differs from build report.')
            return results
        marker = b'<script type="application/json" id="asset-data">'
        start = data.find(marker)
        if start < 0:
            raise ValueError('HTML lacks the builder\'s embedded asset-data block.')
        start += len(marker)
        end = data.find(b'</script>', start)
        if end < 0:
            raise ValueError('Unterminated embedded asset-data block.')
        ids = set()
        for asset in expected_assets:
            if asset['id'] in ids:
                raise ValueError('Duplicate asset ID in build report.')
            ids.add(asset['id'])
            key = json.dumps(asset['id'], ensure_ascii=False, separators=(',', ':')).encode() + b':'
            key_at = data.find(key, start, end)
            if key_at < 0:
                raise ValueError(f'Missing embedded asset: {asset["id"]}')
            header_at = key_at + len(key)
            encoded_at = data.find(b'"data":"', header_at, end)
            if encoded_at < 0:
                raise ValueError(f'Missing base64 payload: {asset["id"]}')
            encoded_at += len(b'"data":"')
            metadata = json.loads(data[header_at:encoded_at] + b'"}')
            if metadata.get('id') != asset['id'] or metadata.get('sha256') != asset['sha256']:
                raise ValueError(f'Embedded metadata differs from receipt: {asset["id"]}')
            encoded_end = data.find(b'"', encoded_at, end)
            if encoded_end < 0:
                raise ValueError(f'Unterminated base64 payload: {asset["id"]}')
            digest, size, prefix = hashlib.sha256(), 0, b''
            for offset in range(encoded_at, encoded_end, 4 * 16384):
                block = base64.b64decode(data[offset:min(offset + 4 * 16384, encoded_end)], validate=True)
                if not prefix:
                    prefix = block[:8]
                digest.update(block)
                size += len(block)
            if digest.hexdigest() != asset['sha256'] or size != asset['bytes']:
                raise ValueError(f'Embedded bytes differ from original source/asset: {asset["id"]}')
            if asset['kind'] == 'source_pdf' and not prefix.startswith(b'%PDF-'):
                raise ValueError(f'Source PDF bytes lack PDF header: {asset["id"]}')
            results.append({**asset, 'embeddedByteIdentity': 'verified'})
    return results


def package(html, build_report, output, *, allow_partial=False, project_root=ROOT):
    html, build_report, output = map(lambda p: Path(p).resolve(), (html, build_report, output))
    if html == output or build_report == output:
        raise ValueError('ZIP output must not overwrite the HTML or build report.')
    report_bytes = build_report.read_bytes()
    report = json.loads(report_bytes)
    if report.get('syntheticTestFixture'):
        raise ValueError('Synthetic test artifacts cannot be packaged as course delivery.')
    if not report.get('validation', {}).get('valid'):
        raise ValueError('The build report did not pass its integrity gate.')
    release_validated = bool(report.get('complete') and report.get('validation', {}).get('release'))
    if not release_validated and not allow_partial:
        raise ValueError('This is an incomplete checkpoint or lacks release validation; use --allow-partial only for an explicitly labeled checkpoint.')
    sha, size = digest_file(html), html.stat().st_size
    if report.get('sha256') != sha or report.get('bytes') != size:
        raise ValueError('HTML bytes do not match the supplied build report. Rebuild or choose the correct report.')
    with html.open('rb') as handle:
        if not handle.read(256).lstrip().lower().startswith(b'<!doctype html'):
            raise ValueError('The deliverable is not real HTML (possible pointer/error document).')
    assets = verify_embedded_assets(html, report['embeddedAssets'])
    if not any(a['kind'] == 'source_pdf' for a in assets):
        raise ValueError('No complete source PDF is embedded; this delivery must retain original source evidence.')
    created = datetime.now(timezone.utc).isoformat()
    practice = report.get('applicationScope') == 'practice-only'
    manifest = {
        'schemaVersion': '1.0.0', 'createdAt': created,
        'classification': 'practice-only-verified-bank' if practice else 'release-validated-content-build' if release_validated else 'partial-course-checkpoint',
        'applicationScope': report.get('applicationScope', 'historical-multi-mode'),
        'bankVersion': report['bankVersion'], 'complete': report['complete'],
        'html': {'filename': 'ai-for-robotics-mcq.html', 'bytes': size, 'sha256': sha},
        'buildReportSha256': hashlib.sha256(report_bytes).hexdigest(), 'releaseValidated': release_validated, 'embeddedAssets': assets,
        'sourceEvidence': 'Original source PDFs remain embedded, byte-identical to their recorded hashes. No downsampling or evidence omission.',
        'browserValidation': {'status': 'pending', 'requirement': 'Test the exact independently downloaded HTML in a permitted offline file:// browser, then inspect source pixels, screenshots and print PDFs.'},
        'compression': 'Standard lossless ZIP DEFLATE; extracted HTML must match the recorded SHA-256 exactly.',
        'warning': 'A successful package is not final course, browser or visual acceptance. See the build/coverage audits and separate exact-artifact QA report.'
    }
    required = ['tests/browser_practice.js', 'docs/CURRENT_SCOPE.md'] if practice else ['tests/browser_final_artifact.js', 'tests/browser_learning_resources_artifact.js', 'docs/FINAL_OFFLINE_QA.md', 'docs/OPEN_AND_STUDY.md']
    for relative in required:
        if not (project_root / relative).is_file():
            raise ValueError(f'Missing transferable QA support file: {relative}')
    storage_note = 'Answers and bookmarks save automatically. Keep the same file path and browser to resume.' if practice else 'Keep progress backups because browser file-origin storage differs between browsers/computers.'
    qa_note = 'See docs/CURRENT_SCOPE.md and the separately hash-bound Practice browser report.' if practice else 'See docs/FINAL_OFFLINE_QA.md.'
    readme = f'''AI for Robotics offline study file

Status: {manifest['classification']}
Bank version: {report['bankVersion']}
HTML SHA-256: {sha}

Extract this ZIP, then open ai-for-robotics-mcq.html directly in your browser.
The HTML is the single-file application. No server, account or installation is
required. Both original source PDFs are embedded; Save source opens them in an
offline reader if your browser cannot display PDF objects.
{storage_note}

The ZIP is only a lossless transport container. Its extra files are optional QA
instructions/runner and receipts; the application does not load them at runtime.
The packager does not certify browser behavior. {qa_note}
Testing uses an already installed, permitted Node/Playwright/Chromium environment.
Never rerun a denied browser route unchanged.
'''
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + '.tmp')
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as archive:
            archive.write(html, 'ai-for-robotics-mcq.html')
            archive.writestr('ai-for-robotics-mcq.build-report.json', report_bytes)
            archive.writestr('package-content.json', json.dumps(manifest, indent=2) + '\n')
            archive.writestr('README-delivery.txt', readme)
            for relative in required:
                archive.write(project_root / relative, relative)
            # A generated delivery report is optional for isolated packaging tests.
            report_note = project_root / ('docs/PRACTICE_RELEASE.md' if practice else 'docs/DELIVERY_REPORT.md')
            if report_note.is_file():
                archive.write(report_note, 'docs/' + report_note.name)
        # Stream-decompress the actual ZIP member, not the original file, and rehash it.
        with zipfile.ZipFile(temporary) as archive, archive.open('ai-for-robotics-mcq.html') as member:
            extracted_hash, extracted_size = hashlib.sha256(), 0
            for block in iter(lambda: member.read(1024 * 1024), b''):
                extracted_hash.update(block)
                extracted_size += len(block)
            if extracted_hash.hexdigest() != sha or extracted_size != size:
                raise ValueError('ZIP round trip changed or truncated the HTML.')
        os.replace(temporary, output)
    finally:
        if temporary.exists():
            temporary.unlink()
    receipt = {**manifest, 'archive': {'filename': output.name, 'bytes': output.stat().st_size, 'sha256': digest_file(output)},
               'verifiedZipRoundTrip': {'sha256': sha, 'bytes': size, 'status': 'passed'},
               'htmlCompressionRatio': round(output.stat().st_size / size, 6)}
    receipt_path = output.with_suffix('.delivery-receipt.json')
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    return receipt, receipt_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', type=Path, required=True)
    parser.add_argument('--build-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--allow-partial', action='store_true')
    args = parser.parse_args()
    try:
        receipt, receipt_path = package(args.html, args.build_report, args.output, allow_partial=args.allow_partial)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, f'Delivery packaging refused: {error}\n')
    print(json.dumps({'classification': receipt['classification'], 'html': receipt['html'], 'archive': receipt['archive'], 'receipt': str(receipt_path), 'browserValidation': 'pending'}, indent=2))


if __name__ == '__main__':
    main()
