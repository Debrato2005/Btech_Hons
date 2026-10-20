"""Fail-closed, independently reviewed question-input visual sidecars.

Question content and its answer-review hash never change here. A visual review
is separate evidence, not a substitute for the question's existing answer gate.
Only exact lossless PNG bytes are packaged; original PDFs remain separate assets.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct
import zlib

_SPEC = importlib.util.spec_from_file_location('visual_canonical_validator', Path(__file__).with_name('validate.py'))
_VALIDATOR = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_VALIDATOR)
canonical_json, question_hash = _VALIDATOR.canonical_json, _VALIDATOR.question_hash
VISUAL_CHECKS = ('inventoryCompleteness', 'requiredInputFidelity', 'legibility', 'noAnswerLeak', 'sourceLinkage')


def digest(value):
    return hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def unique_strings(values, *, empty=False):
    return isinstance(values, list) and (empty or bool(values)) and all(nonblank(v) for v in values) and len(values) == len(set(values))


def valid_sha(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def local_path(root, relative):
    if not nonblank(relative) or Path(relative).is_absolute() or '..' in Path(relative).parts or ':' in relative:
        return None
    result = (Path(root) / relative).resolve()
    return result if result.is_relative_to(Path(root).resolve()) else None


def load_visual_inputs(root):
    root = Path(root)
    path = root / 'data/question-visuals/manifest.json'
    manifest = _VALIDATOR.load_json(path) if path.is_file() else {}
    reviews = []
    for path in sorted((root / 'data/question-visuals/reviews').glob('*.json')):
        value = _VALIDATOR.load_json(path)
        reviews.extend(value if isinstance(value, list) else value.get('reviews', [value]))
    return {'manifest': {k: copy.deepcopy(v) for k, v in manifest.items() if k not in ('records', 'assets')},
            'records': manifest.get('records', []), 'assets': manifest.get('assets', []), 'reviews': reviews}


def source_ref_valid(ref, sources, slides):
    if not isinstance(ref, dict):
        return False
    source, slide = sources.get(ref.get('sourceId'), {}), slides.get(ref.get('slideId'), {})
    page, sha = ref.get('physicalPage'), ref.get('sourceSha256')
    return (valid_sha(sha) and source.get('retrievalStatus') == 'ready' and source.get('sha256') == sha
            and slide.get('sourceId') == ref.get('sourceId') and slide.get('sourceSha256') == sha
            and type(page) is int and type(source.get('pageCount')) is int and 1 <= page <= source['pageCount']
            and type(slide.get('physicalPage')) is int and slide['physicalPage'] == page
            and slide.get('visualInspection', {}).get('status') == 'complete'
            and slide.get('disposition') in ('examinable', 'repeated', 'excluded'))


def source_key(ref):
    return tuple(ref.get(k) for k in ('sourceId', 'sourceSha256', 'slideId', 'physicalPage'))


def authors(record):
    return {a.strip() for a in [record.get('authorId'), *record.get('revisionAuthors', [])] if nonblank(a)}


def current_question(question, reviews, sources, slides):
    if (question.get('status') != 'verified' or question.get('synthetic') or question.get('origin') == 'synthetic'
            or not nonblank(question.get('authorId')) or type(question.get('version')) is not int or question['version'] < 1):
        return False
    refs, options, answers = question.get('citations'), question.get('options'), question.get('correctOptionIds')
    if not isinstance(refs, list) or not refs or any(not source_ref_valid(r, sources, slides) for r in refs):
        return False
    if any(r.get('role') == 'conflict' for r in refs) and not question.get('conflictResolution'):
        return False
    if not isinstance(options, list) or len(options) < 2 or any(not isinstance(o, dict) for o in options):
        return False
    ids = [o.get('id') for o in options]
    if not unique_strings(ids) or not unique_strings(answers) or not set(answers) <= set(ids):
        return False
    if question.get('selectionMode') not in ('single', 'multi') or (question['selectionMode'] == 'single' and len(answers) != 1):
        return False
    sha, own = question_hash(question), authors(question)
    current = [r for r in reviews if r.get('questionVersion') == question.get('version') and r.get('questionSha256') == sha
               and all(r.get('sourceVersions', {}).get(c['sourceId']) == c['sourceSha256'] for c in refs)
               and all(sources.get(sid, {}).get('sha256') == h for sid, h in r.get('sourceVersions', {}).items())]
    if any(r.get('decision') in ('flagged', 'rejected') for r in current):
        return False
    return any(r.get('id') in question.get('reviewIds', []) and r.get('decision') == 'verified'
               and nonblank(r.get('reviewerId')) and r['reviewerId'].strip() not in own
               and unique_strings(r.get('independentAnswerOptionIds')) and set(r['independentAnswerOptionIds']) == set(answers)
               and all(r.get('checks', {}).get(k) is True for k in _VALIDATOR.CHECK_KEYS)
               and {c['slideId'] for c in refs} <= set(r.get('reviewedSlideIds', [])) for r in current)


def png_dimensions(data):
    """Check PNG framing/CRC without recompressing or otherwise editing pixels."""
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Required visual is not a PNG.')
    offset, dimensions, image_data, ended = 8, None, False, False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError('Truncated PNG chunk.')
        size = struct.unpack('>I', data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        end = offset + 12 + size
        if end > len(data):
            raise ValueError('Truncated PNG payload.')
        payload = data[offset + 8:offset + 8 + size]
        expected_crc = struct.unpack('>I', data[offset + 8 + size:end])[0]
        if zlib.crc32(kind + payload) & 0xffffffff != expected_crc:
            raise ValueError('PNG chunk CRC mismatch.')
        if dimensions is None:
            if kind != b'IHDR' or size != 13:
                raise ValueError('PNG lacks an initial IHDR.')
            dimensions = struct.unpack('>II', payload[:8])
            if not all(dimensions):
                raise ValueError('PNG has empty dimensions.')
        elif kind == b'IHDR':
            raise ValueError('Duplicate PNG IHDR.')
        if kind == b'IDAT':
            image_data = True
        if kind == b'IEND':
            if size != 0 or end != len(data):
                raise ValueError('Invalid PNG end marker.')
            ended = True
            break
        offset = end
    if not ended or not image_data:
        raise ValueError('PNG lacks complete image data/end marker.')
    return dimensions


def asset_reasons(asset, root, sources, slides, *, check_files):
    reasons = []
    if not nonblank(asset.get('id')) or not valid_sha(asset.get('sha256')) or asset.get('mimeType') != 'image/png':
        reasons.append('Visual asset must have an ID and a lossless PNG SHA-256 binding.')
    path = local_path(root, asset.get('path'))
    if path is None or not path.is_relative_to((Path(root) / 'assets/question-visuals').resolve()):
        reasons.append('Visual asset path is outside assets/question-visuals.')
    if not source_ref_valid(asset, sources, slides):
        reasons.append('Visual asset source/page/inspection binding is not current.')
    rect, dpi = asset.get('cropRectangle'), asset.get('renderDpi')
    dimensions = (asset.get('width'), asset.get('height'))
    if any(type(x) is not int or x <= 0 for x in dimensions):
        reasons.append('Visual asset dimensions must be positive integers.')
    numeric = lambda n: type(n) in (int, float) and math.isfinite(n)
    if not isinstance(rect, list) or len(rect) != 4 or not all(numeric(n) for n in rect) or not (0 <= rect[0] < rect[2] and 0 <= rect[1] < rect[3]):
        reasons.append('Visual asset crop rectangle is invalid.')
    if not numeric(dpi) or dpi <= 0:
        reasons.append('Visual asset render DPI is invalid.')
    if not nonblank(asset.get('alt')):
        reasons.append('Visual asset lacks descriptive alternative text.')
    if check_files and path is not None:
        if not path.is_file():
            reasons.append('Required visual PNG is missing.')
        else:
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != asset.get('sha256'):
                reasons.append('Required visual PNG bytes have changed.')
            try:
                if png_dimensions(data) != dimensions:
                    reasons.append('Required visual PNG dimensions differ from its metadata.')
            except ValueError as error:
                reasons.append(str(error))
    return reasons


def prepare_question_visuals(bank, root, inputs=None, *, check_files=True):
    """Produce immutable-input projections; independently quarantine missing inputs."""
    inputs = copy.deepcopy(load_visual_inputs(root) if inputs is None else inputs)
    result = {'formatVersion': 1, **inputs, 'reviewBindings': {}, 'assetBindings': {}, 'bindings': {}, 'diagnostics': []}
    sources, slides = ({x['id']: x for x in bank[k]} for k in ('sources', 'slides'))
    qmap = {q['id']: q for q in bank['questions']}
    records, assets, reviews, manifest = (inputs[k] for k in ('records', 'assets', 'reviews', 'manifest'))
    global_reasons = []
    if not isinstance(manifest, dict) or not nonblank(manifest.get('authorId')):
        global_reasons.append('Visual inventory manifest has no author identity.')
    for name, values in [('records', records), ('assets', assets), ('reviews', reviews)]:
        if not isinstance(values, list) or any(not isinstance(v, dict) for v in values):
            raise ValueError('Malformed question-visual ' + name)
        ids = [v.get('id') for v in values]
        if not unique_strings(ids, empty=True):
            global_reasons.append('Visual ' + name + ' IDs are missing or duplicated.')
    amap = {a['id']: a for a in assets if nonblank(a.get('id'))}
    by_question, by_visual, answer_reviews = {}, {}, {}
    for record in records:
        by_question.setdefault(record.get('questionId'), []).append(record)
    for review in reviews:
        by_visual.setdefault(review.get('visualId'), []).append(review)
        if nonblank(review.get('id')):
            result['reviewBindings'][review['id']] = {'id': review['id'], 'reviewSha256': digest(review), 'rawJSON': canonical_json(review)}
    for review in bank['reviews']:
        answer_reviews.setdefault(review.get('questionId'), []).append(review)
    asset_errors, seen_hashes = {}, {}
    for aid, asset in amap.items():
        asset_errors[aid] = asset_reasons(asset, root, sources, slides, check_files=check_files)
        result['assetBindings'][aid] = {'id': aid, 'assetSha256': asset.get('sha256'), 'assetMetadataSha256': digest(asset), 'rawJSON': canonical_json(asset)}
        seen_hashes.setdefault(asset.get('sha256'), []).append(aid)
    for ids in seen_hashes.values():
        if len(ids) > 1:
            for aid in ids:
                asset_errors[aid].append('Identical visual bytes must share one asset ID.')
    for qid, question in qmap.items():
        # Flagged duplicate adaptations are not part of the active denominator.
        if question.get('status') != 'verified':
            continue
        reasons = list(global_reasons)
        candidates = by_question.get(qid, [])
        if len(candidates) != 1:
            result['diagnostics'].append({'questionId': qid, 'reasons': sorted(set(reasons + ['Missing or duplicate current visual-dependency inventory record.']))})
            continue
        record = candidates[0]
        rid, sha = record.get('id'), digest(record)
        if not current_question(question, answer_reviews.get(qid, []), sources, slides):
            reasons.append('Answer-review eligibility is missing or revoked, independently of visuals.')
        if record.get('questionVersion') != question.get('version') or record.get('questionSha256') != question_hash(question):
            reasons.append('Visual record is stale for the current question content/version.')
        if not nonblank(record.get('authorId')) or type(record.get('version')) is not int or record['version'] < 1 or not nonblank(record.get('reason')):
            reasons.append('Visual record lacks valid authorship, version or dependency reasoning.')
        aids, required, refs = record.get('assetIds'), record.get('requiredInputs'), record.get('sourceRefs')
        if not unique_strings(aids, empty=True) or not unique_strings(required, empty=True):
            reasons.append('Visual asset IDs or required inputs are malformed.'); aids, required = [], []
        if record.get('dependencyStatus') == 'required':
            if not aids or not required:
                reasons.append('Required question inputs have no bound visual assets or input descriptions.')
        elif record.get('dependencyStatus') == 'self_contained':
            if aids or required:
                reasons.append('Self-contained questions must not claim required visual inputs.')
        else:
            reasons.append('Visual dependency status is missing or unsupported.')
        if not isinstance(refs, list) or not refs or any(not source_ref_valid(ref, sources, slides) for ref in refs):
            reasons.append('Visual record source references are missing or stale.'); refs = []
        elif len({source_key(ref) for ref in refs}) != len(refs) or not {(ref['sourceId'], ref['sourceSha256']) for ref in refs} <= {(c['sourceId'], c['sourceSha256']) for c in question['citations']}:
            reasons.append('Visual record references a source/version outside the current question evidence.')
        if any(manifest.get('sourceVersions', {}).get(ref['sourceId']) != ref['sourceSha256'] for ref in refs):
            reasons.append('Visual manifest does not bind all record source versions.')
        for aid in aids:
            if aid not in amap:
                reasons.append('Required visual asset is missing: ' + aid)
                continue
            reasons.extend(aid + ': ' + r for r in asset_errors[aid])
            if source_key(amap[aid]) not in {source_key(ref) for ref in refs}:
                reasons.append('Required asset is outside the record source references: ' + aid)
        own = authors(manifest) | authors(record)
        current = [r for r in by_visual.get(rid, []) if r.get('visualVersion') == record.get('version') and r.get('visualSha256') == sha]
        if any(r.get('decision') in ('flagged', 'rejected') for r in current):
            reasons.append('Current independent visual review is flagged or rejected.')
        accepted = []
        for review in current:
            if (review.get('decision') != 'verified' or not nonblank(review.get('reviewerId')) or review['reviewerId'].strip() in own
                    or any(review.get('checks', {}).get(k) is not True for k in VISUAL_CHECKS)
                    or review.get('questionId') != qid or review.get('questionVersion') != question.get('version')
                    or review.get('questionSha256') != question_hash(question)
                    or review.get('displayRole') != 'question_input' or not _VALIDATOR.valid_timestamp(review.get('reviewedAt'))
                    or not unique_strings(review.get('reviewedAssetIds'), empty=True) or set(review['reviewedAssetIds']) != set(aids)
                    or review.get('assetHashes') != {aid: amap.get(aid, {}).get('sha256') for aid in aids}
                    or review.get('assetMetadataHashes') != {aid: digest(amap[aid]) for aid in aids if aid in amap}
                    or any(review.get('sourceVersions', {}).get(ref['sourceId']) != ref['sourceSha256'] for ref in refs)
                    or any(sources.get(sid, {}).get('sha256') != h for sid, h in review.get('sourceVersions', {}).items())):
                continue
            accepted.append({'id': review['id'], 'reviewSha256': digest(review)})
        if not accepted:
            reasons.append('No current independent visual-dependency approval; answer review is not visual approval.')
        if reasons:
            result['diagnostics'].append({'questionId': qid, 'reasons': sorted(set(reasons))})
            continue
        result['bindings'][qid] = {'recordId': rid, 'recordVersion': record['version'], 'recordSha256': sha,
                                  'recordRawJSON': canonical_json(record), 'questionVersion': question['version'],
                                  'questionSha256': question_hash(question), 'dependencyStatus': record['dependencyStatus'],
                                  'assetIds': aids, 'requiredInputs': required, 'reviewBindings': accepted}
    return result


def projected_visual_assets(sidecar):
    return [{**copy.deepcopy(a), 'kind': 'diagram'} for a in sidecar.get('assets', [])]


def question_visual_errors(bank, root, *, check_files=True):
    value = bank.get('questionVisuals')
    if value is None:
        return [] if bank.get('synthetic') or not bank.get('questions') else ['Question visuals: missing independent dependency inventory; answer reviews alone cannot enable exam/print inputs.']
    if not isinstance(value, dict) or value.get('formatVersion') != 1:
        return ['Question visuals: malformed sidecar.']
    try:
        inputs = {k: value[k] for k in ('manifest', 'records', 'assets', 'reviews')}
        expected = prepare_question_visuals(bank, root, inputs, check_files=check_files)
        errors = []
        if value != expected:
            errors.append('Question visuals: stale or altered record/review/asset bindings.')
        if check_files and inputs != load_visual_inputs(root):
            errors.append('Question visuals: embedded inventory/reviews differ from current source files.')
        by_asset = {a['id']: a for a in bank['assets']}
        for asset in projected_visual_assets(value):
            if by_asset.get(asset['id']) != asset:
                errors.append('Question visuals: required asset projection is missing or altered: ' + asset['id'])
        for item in expected['diagnostics']:
            errors.append('Question visuals: ' + item['questionId'] + ': ' + '; '.join(item['reasons']))
        return errors
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        return ['Question visuals: malformed sidecar: ' + str(error)]
