#!/usr/bin/env python3
"""Validate the source-bound bank using only the Python standard library.

Structural validity is not evidence of independent subject-matter review. The
release gate is deliberately stricter than partial checkpoint validation.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / 'data' / 'schema.bank.json'
ENTITY_KEYS = ('sources', 'slides', 'concepts', 'questions', 'reviews', 'assets')
CHECK_KEYS = ('sourceSupport', 'assumptions', 'answerSet', 'distractors',
              'calculations', 'figureFidelity', 'explanation', 'difficulty', 'duplication')
_LEARNING_RESOURCES = None


def learning_resources_module():
    """Load the sibling gate under CLI, package and file-spec entry points."""
    global _LEARNING_RESOURCES
    if _LEARNING_RESOURCES is None:
        spec = importlib.util.spec_from_file_location(
            'robotics_learning_resources', Path(__file__).with_name('learning_resources.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _LEARNING_RESOURCES = module
    return _LEARNING_RESOURCES


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def question_hash(question: dict) -> str:
    content = {k: v for k, v in question.items() if k not in ('status', 'reviewIds')}
    return hashlib.sha256(canonical_json(content).encode('utf-8')).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    def reject_constant(value):
        raise ValueError(f'Non-finite JSON number {value}')
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'Duplicate JSON object key: {key}')
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), parse_constant=reject_constant, object_pairs_hook=unique_keys)


def schema_errors(value: Any, schema: dict, path: str = '$', root: dict | None = None) -> list[str]:
    """Evaluate the documented JSON-Schema subset used by schema.bank.json.

    No silent optional dependency: the same structural checks run on a clean
    Python installation. Standard validators can also consume the published schema.
    """
    root = schema if root is None else root
    errors = []
    if '$ref' in schema:
        ref = schema['$ref']
        if not ref.startswith('#/'):
            return [f'{path}: unsupported nonlocal schema reference {ref}']
        target = root
        for component in ref[2:].split('/'):
            target = target[component.replace('~1', '/').replace('~0', '~')]
        errors.extend(schema_errors(value, target, path, root))
    if 'anyOf' in schema and all(schema_errors(value, child, path, root) for child in schema['anyOf']):
        errors.append(f'{path}: does not match any allowed schema')
    if 'const' in schema and (value != schema['const'] or type(value) is not type(schema['const'])):
        errors.append(f'{path}: must equal {schema["const"]!r}')
    if 'enum' in schema and not any(value == candidate and type(value) is type(candidate) for candidate in schema['enum']):
        errors.append(f'{path}: unsupported value {value!r}; expected one of {schema["enum"]!r}')
    types = schema.get('type')
    if types is not None:
        types = [types] if isinstance(types, str) else types
        matches = {'null': value is None, 'boolean': isinstance(value, bool),
                   'string': isinstance(value, str), 'integer': isinstance(value, int) and not isinstance(value, bool),
                   'number': isinstance(value, (int, float)) and not isinstance(value, bool),
                   'object': isinstance(value, dict), 'array': isinstance(value, list)}
        if not any(matches.get(t, False) for t in types):
            return errors + [f'{path}: expected {" or ".join(types)}, got {type(value).__name__}']
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                errors.append(f'{path}: missing required field {key}')
        properties = schema.get('properties', {})
        for key, child in value.items():
            if key in properties:
                errors.extend(schema_errors(child, properties[key], f'{path}.{key}', root))
            elif isinstance(schema.get('additionalProperties'), dict):
                errors.extend(schema_errors(child, schema['additionalProperties'], f'{path}.{key}', root))
            elif schema.get('additionalProperties') is False:
                errors.append(f'{path}: unknown property {key}')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            errors.append(f'{path}: requires at least {schema["minItems"]} items')
        if schema.get('uniqueItems') and len({canonical_json(v) for v in value}) != len(value):
            errors.append(f'{path}: contains duplicate items')
        if 'items' in schema:
            for index, child in enumerate(value):
                errors.extend(schema_errors(child, schema['items'], f'{path}[{index}]', root))
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0) or (schema.get('minLength', 0) and not value.strip()):
            errors.append(f'{path}: must contain nonblank text')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            errors.append(f'{path}: does not match pattern {schema["pattern"]}')
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if 'minimum' in schema and value < schema['minimum']:
            errors.append(f'{path}: below minimum {schema["minimum"]}')
        if 'maximum' in schema and value > schema['maximum']:
            errors.append(f'{path}: above maximum {schema["maximum"]}')
        if 'exclusiveMinimum' in schema and value <= schema['exclusiveMinimum']:
            errors.append(f'{path}: must exceed {schema["exclusiveMinimum"]}')
    return errors


def normalized_text(value: str) -> str:
    # Preserve mathematical signs, decimals, punctuation, and variable order.
    # Removing punctuation would dangerously equate -1 with 1 or 1.5 with 15.
    return ' '.join(unicodedata.normalize('NFC', value).split())


def valid_timestamp(value: str | None) -> bool:
    if not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed.tzinfo is not None
    except (ValueError, TypeError):
        return False


def validate_bank(bank: dict, root: Path | str = PROJECT_ROOT, *, release: bool = False,
                  allow_synthetic: bool = False, check_files: bool = True) -> dict:
    root = Path(root).resolve()
    schema = load_json(SCHEMA_PATH)
    errors = schema_errors(bank, schema)
    warnings = []
    report = {'valid': False, 'release': release, 'errors': errors, 'warnings': warnings, 'counts': {}}
    if errors:
        return report  # Do not run semantic code on structurally malformed values.
    if bank.get('synthetic') and not allow_synthetic:
        errors.append('Course bank must not contain synthetic test content (synthetic:true).')
    strict = release or bank['complete']
    if release and not bank['complete']:
        errors.append('Release requires complete:true; a partial checkpoint is not a final deliverable.')
    indexes = {}
    for kind in ENTITY_KEYS:
        indexes[kind] = {}
        for item in bank[kind]:
            if item['id'] in indexes[kind]:
                errors.append(f'{kind}: duplicate ID {item["id"]}')
            indexes[kind][item['id']] = item
    sources, slides, concepts, questions, reviews, assets = (indexes[k] for k in ENTITY_KEYS)
    hash_cache = {}

    def local_file(path_string: str, owner: str, expected_hash: str | None = None):
        path = Path(path_string)
        if path.is_absolute() or '..' in path.parts or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', path_string):
            errors.append(f'{owner}: asset/source path must be project-relative, not a URL or traversal: {path_string}')
            return None
        path = (root / path).resolve()
        if not path.is_relative_to(root):
            errors.append(f'{owner}: resolved path escapes project root')
            return None
        if check_files:
            if not path.is_file():
                errors.append(f'{owner}: missing file {path_string}')
            elif expected_hash:
                if path not in hash_cache:
                    hash_cache[path] = file_hash(path)
                if hash_cache[path] != expected_hash:
                    errors.append(f'{owner}: file SHA-256 mismatch for {path_string}')
        return path

    def refs(ids, index, owner, label):
        for value in ids:
            if value not in index:
                errors.append(f'{owner}: broken {label} reference {value}')

    for source in sources.values():
        sid = source['id']
        if source['retrievalStatus'] == 'ready':
            if source['sha256'] is None or source['pageCount'] is None or not source['localPath']:
                errors.append(f'{sid}: ready source needs measured SHA-256, pageCount and localPath')
            if source['localPath']:
                local_file(source['localPath'], sid, source['sha256'])
        elif strict:
            errors.append(f'{sid}: source is not ready ({source["retrievalStatus"]})')
        if source['assetId'] is not None:
            refs([source['assetId']], assets, sid, 'asset')
            asset = assets.get(source['assetId'])
            if asset and (asset['kind'] != 'source_pdf' or asset['sha256'] != source['sha256']):
                errors.append(f'{sid}: source asset must be its exact hashed source_pdf')
        if strict and not source['assetId']:
            errors.append(f'{sid}: release needs an offline source PDF asset')
    for asset in assets.values():
        local_file(asset['path'], asset['id'], asset['sha256'])
        if 'sourceId' in asset:
            refs([asset['sourceId']], sources, asset['id'], 'source')
        if 'physicalPage' in asset:
            source = sources.get(asset.get('sourceId'))
            if not source or not source['pageCount'] or asset['physicalPage'] > source['pageCount']:
                errors.append(f'{asset["id"]}: invalid asset physical page mapping')
    physical_pages = defaultdict(set)
    for slide in slides.values():
        sid = slide['id']
        source = sources.get(slide['sourceId'])
        if not source:
            errors.append(f'{sid}: broken source reference {slide["sourceId"]}')
            continue
        if source['sha256'] != slide['sourceSha256']:
            errors.append(f'{sid}: source hash is stale')
        page = slide['physicalPage']
        if page in physical_pages[source['id']]:
            errors.append(f'{sid}: duplicate physical page {page} for source {source["id"]}')
        physical_pages[source['id']].add(page)
        if not source['pageCount'] or page > source['pageCount']:
            errors.append(f'{sid}: physical page {page} exceeds measured source page count')
        expected_combined = page if source['role'] == 'lectures' else None
        if slide['combinedLecturePage'] != expected_combined:
            errors.append(f'{sid}: combinedLecturePage must be {expected_combined!r}, not assignment pagination')
        printed = slide['printedSlideNumberStatus']
        if (printed == 'present') != bool(slide['printedSlideNumber']):
            errors.append(f'{sid}: printed slide number and its presence status disagree')
        inspection = slide['visualInspection']
        if inspection['status'] == 'complete':
            if not inspection['inspectorId'] or not valid_timestamp(inspection['inspectedAt']) or not inspection['method']:
                errors.append(f'{sid}: complete visual inspection needs inspector, timezone-aware timestamp and method')
            if source['retrievalStatus'] != 'ready':
                errors.append(f'{sid}: cannot visually inspect an unavailable source')
            if not inspection['notes'].strip():
                errors.append(f'{sid}: complete visual inspection needs observed details in notes')
        if strict and inspection['status'] != 'complete':
            errors.append(f'{sid}: visual inspection is not complete')
        if slide['disposition'] == 'excluded' and not slide['exclusionReason']:
            errors.append(f'{sid}: excluded slide lacks a specific reason')
        if slide['disposition'] == 'repeated' and (not slide['repeatsSlideIds'] or not slide['incrementalChangesChecked']):
            errors.append(f'{sid}: repeated slide needs mapped originals and incremental-change check')
        if strict and slide['disposition'] in ('unreviewed', 'unresolved'):
            errors.append(f'{sid}: unresolved page disposition {slide["disposition"]}')
        if slide['disposition'] == 'examinable' and not slide['conceptIds']:
            errors.append(f'{sid}: examinable slide lacks concepts')
        refs(slide['conceptIds'], concepts, sid, 'concept')
        refs(slide['repeatsSlideIds'], slides, sid, 'repeated slide')
        if sid in slide['repeatsSlideIds']:
            errors.append(f'{sid}: a slide cannot repeat itself')
        for concept_id in slide['conceptIds']:
            if concept_id in concepts and sid not in concepts[concept_id]['slideIds']:
                errors.append(f'{sid}: concept {concept_id} lacks reciprocal slide link')
        if slide['assetId']:
            refs([slide['assetId']], assets, sid, 'asset')
            asset = assets.get(slide['assetId'])
            if asset and (asset['kind'] != 'source_page' or asset.get('sourceId') != source['id'] or asset.get('physicalPage') != page):
                errors.append(f'{sid}: preview asset must identify this exact source page')
    for source in sources.values():
        if source['pageCount']:
            missing = set(range(1, source['pageCount'] + 1)) - physical_pages[source['id']]
            if missing:
                message = f'{source["id"]}: {len(missing)} source pages missing from ledger; first: {sorted(missing)[:12]}'
                (errors if strict else warnings).append(message)

    current_verified = set()
    stale_review_ids = set()
    for review in reviews.values():
        rid = review['id']
        question = questions.get(review['questionId'])
        if not question:
            errors.append(f'{rid}: broken question reference {review["questionId"]}')
            continue
        refs(review['reviewedSlideIds'], slides, rid, 'reviewed slide')
        if not valid_timestamp(review['reviewedAt']):
            errors.append(f'{rid}: reviewedAt requires an ISO timestamp with timezone')
        option_ids = {o['id'] for o in question['options']}
        if not set(review['independentAnswerOptionIds']) <= option_ids:
            errors.append(f'{rid}: independent answer refers to a missing option ID')
        conditional_ids = review.get('conditionalIntendedOptionIds', [])
        if conditional_ids:
            if not set(conditional_ids) <= option_ids:
                errors.append(f'{rid}: conditional intended answer refers to a missing option ID')
            if not str(review.get('conditionalAnswerAssumption', '')).strip():
                errors.append(f'{rid}: conditional intended answers require a separately labeled repair assumption')
        if review['decision'] == 'verified' and not review['independentAnswerOptionIds']:
            errors.append(f'{rid}: verified review requires a nonempty literal independent answer set')
        if review['questionVersion'] != question['version'] or review['questionSha256'] != question_hash(question):
            stale_review_ids.add(rid)
        for source_id, sha in review['sourceVersions'].items():
            if source_id not in sources or sources[source_id]['sha256'] != sha:
                stale_review_ids.add(rid)
        # Historic review records are retained, not silently overwritten.
        if rid in stale_review_ids:
            warnings.append(f'{rid}: stale historical review; cannot verify the current question/source versions')

    normalized = defaultdict(list)
    tokens = defaultdict(list)
    for question in questions.values():
        qid = question['id']
        question_error_start = len(errors)
        option_ids = [o['id'] for o in question['options']]
        if len(option_ids) != len(set(option_ids)):
            errors.append(f'{qid}: duplicate option IDs')
        option_texts = [normalized_text(o['text']) for o in question['options']]
        if len(option_texts) != len(set(option_texts)):
            errors.append(f'{qid}: duplicate/equivalent option text')
        answers = set(question['correctOptionIds'])
        if not answers <= set(option_ids):
            errors.append(f'{qid}: correct answer references missing option IDs')
        if question['selectionMode'] == 'single' and len(answers) != 1:
            errors.append(f'{qid}: single-select question requires exactly one correct option')
        if len(option_ids) < 4 and not question.get('optionCountRationale', '').strip():
            errors.append(f'{qid}: fewer than four options needs optionCountRationale')
        explanations = question['solution']['optionExplanations']
        if set(explanations) != set(option_ids):
            errors.append(f'{qid}: optionExplanations must cover exactly every option ID')
        if question['cognitiveSkill'] in ('numerical', 'algorithm') and not question['solution']['steps']:
            errors.append(f'{qid}: numerical/algorithm solution needs explicit steps')
        refs(question['conceptIds'], concepts, qid, 'concept')
        refs(question['solution']['prerequisiteConceptIds'], concepts, qid, 'solution prerequisite')
        refs(question['reviewIds'], reviews, qid, 'review')
        refs(question.get('assetIds', []), assets, qid, 'asset')
        refs(question.get('relatedQuestionIds', []), questions, qid, 'related question')
        for concept_id in question['conceptIds']:
            if concept_id in concepts and qid not in concepts[concept_id]['questionIds']:
                errors.append(f'{qid}: concept {concept_id} lacks reciprocal question link')
        required_sources = {}
        required_slides = set()
        for citation in question['citations']:
            slide = slides.get(citation['slideId'])
            source = sources.get(citation['sourceId'])
            required_slides.add(citation['slideId'])
            required_sources[citation['sourceId']] = citation['sourceSha256']
            if not slide or not source:
                errors.append(f'{qid}: broken citation source/slide reference')
                continue
            if (slide['sourceId'] != source['id'] or slide['physicalPage'] != citation['physicalPage'] or
                slide['sourceSha256'] != citation['sourceSha256'] or source['sha256'] != citation['sourceSha256']):
                errors.append(f'{qid}: citation page/source/hash does not match source ledger')
            region = citation['region']
            if region and (region['x'] + region['width'] > 1.000000001 or region['y'] + region['height'] > 1.000000001):
                errors.append(f'{qid}: citation region extends outside page')
            if question['status'] == 'verified':
                if source['retrievalStatus'] != 'ready' or slide['visualInspection']['status'] != 'complete':
                    errors.append(f'{qid}: verified question cites a source page not actually visually inspected')
                if slide['disposition'] in ('unreviewed', 'unresolved'):
                    errors.append(f'{qid}: verified question cites unresolved source material')
                if citation['role'] == 'conflict' and not question.get('conflictResolution'):
                    errors.append(f'{qid}: conflicting source evidence needs explicit conflictResolution')
        accepted = []
        # Every correctness-changing contributor is an author for independence.
        # revisionAuthors is schema-checked as a unique array of nonblank IDs.
        authors = {question['authorId'], *question.get('revisionAuthors', [])}
        for rid in question['reviewIds']:
            review = reviews.get(rid)
            if not review:
                continue
            if review['questionId'] != qid:
                errors.append(f'{qid}: review {rid} is for another question')
                continue
            if review['decision'] != 'verified':
                continue
            reasons = []
            if rid in stale_review_ids:
                reasons.append('stale content/source binding')
            if review['reviewerId'] in authors:
                reasons.append('reviewer is the author or a revision author')
            if not all(review['checks'][key] for key in CHECK_KEYS):
                reasons.append('failed review checks')
            if set(review['independentAnswerOptionIds']) != answers:
                reasons.append('reviewer answer set differs')
            if not required_slides <= set(review['reviewedSlideIds']):
                reasons.append('not all cited slides reviewed')
            if any(review['sourceVersions'].get(key) != value for key, value in required_sources.items()):
                reasons.append('not all cited source versions bound')
            if reasons:
                if question['status'] == 'verified':
                    errors.append(f'{qid}: acceptance review {rid} invalid: {", ".join(reasons)}')
            else:
                accepted.append(rid)
        if question['status'] == 'verified':
            unresolved_reviews = [r['id'] for r in reviews.values() if r['questionId'] == qid and r['id'] not in stale_review_ids and r['decision'] in ('flagged', 'rejected')]
            if unresolved_reviews:
                errors.append(f'{qid}: current independent review dispute is unresolved: {unresolved_reviews}')
            if not accepted:
                errors.append(f'{qid}: verified status lacks a current independent acceptance review')
            else:
                if len(errors) == question_error_start:
                    current_verified.add(qid)
                if all(not reviews[rid]['solvedBeforeAnswerSeen'] for rid in accepted):
                    warnings.append(f'{qid}: accepted independent review was not blind to the proposed answer')
        normalized[normalized_text(question['stem'])].append(qid)
        # Lexical fingerprints report rewordings with identical word sets cheaply.
        tokens[' '.join(sorted(set(normalized_text(question['stem']).split())))].append(qid)
        if any(re.search(r'\b(all|none) of the (above|below)\b', o['text'], re.I) for o in question['options']):
            warnings.append(f'{qid}: position-dependent option wording is unsafe for shuffling')

    for concept in concepts.values():
        cid = concept['id']
        refs(concept['slideIds'], slides, cid, 'slide')
        refs(concept['questionIds'], questions, cid, 'question')
        refs(concept['prerequisiteConceptIds'], concepts, cid, 'prerequisite')
        if cid in concept['prerequisiteConceptIds']:
            errors.append(f'{cid}: concept cannot be its own prerequisite')
        for sid in concept['slideIds']:
            if sid in slides and cid not in slides[sid]['conceptIds']:
                errors.append(f'{cid}: slide {sid} lacks reciprocal concept link')
        for qid in concept['questionIds']:
            if qid in questions and cid not in questions[qid]['conceptIds']:
                errors.append(f'{cid}: question {qid} lacks reciprocal concept link')
        if concept['status'] == 'verified' and not current_verified.intersection(concept['questionIds']):
            errors.append(f'{cid}: verified concept lacks currently independently verified questions')
        if strict and concept['status'] != 'verified':
            errors.append(f'{cid}: concept has not reached verified coverage')
    for group in normalized.values():
        if len(group) > 1:
            message = f'Duplicate question stems: {", ".join(group)}'
            (errors if len(current_verified.intersection(group)) > 1 else warnings).append(message)
    for group in tokens.values():
        if len(group) > 1 and len({normalized_text(questions[q]['stem']) for q in group}) > 1:
            warnings.append(f'Suspicious paraphrase cluster (same token set): {", ".join(group)}')
    tool_indexes = {}
    for category, records in bank['learningTools'].items():
        if not isinstance(records, list):
            continue
        ids = [r['id'] for r in records if isinstance(r, dict) and 'id' in r]
        if len(ids) != len(set(ids)):
            errors.append(f'learningTools.{category}: duplicate IDs')
        tool_indexes[category] = set(ids)
        for record in records:
            if not isinstance(record, dict):
                continue
            for field, index in [('questionIds', questions), ('conceptIds', concepts), ('slideIds', slides), ('assetIds', assets)]:
                refs(record.get(field, []), index, f'learningTools.{category}.{record.get("id")}', field)
    for question in questions.values():
        if question.get('variant') and question['variant']['familyId'] not in tool_indexes['numericalFamilies']:
            errors.append(f'{question["id"]}: variant familyId is missing from learningTools.numericalFamilies')
    errors.extend(learning_resources_module().integrity_errors(bank, root))
    if strict:
        if not bank.get('learningResourceIntegrity', {}).get('policyEligible'):
            errors.append('Complete release requires an independently approved learning-resource extraction policy.')
        if not sources or not slides or not concepts or not current_verified:
            errors.append('Complete bank requires sources, source pages, concepts, and independently verified questions.')
        if stale_review_ids & {rid for q in questions.values() if q['status'] == 'verified' for rid in q['reviewIds']}:
            errors.append('Release contains stale linked reviews on verified questions.')
        challenge_path = root / 'audits' / 'coverage_challenge.json'
        if not challenge_path.is_file():
            errors.append('Release requires audits/coverage_challenge.json with an independent completed coverage challenge.')
        else:
            challenge = load_json(challenge_path)
            if challenge.get('status') not in ('complete', 'passed') or not challenge.get('reviewerId'):
                errors.append('Independent coverage challenge is not marked complete/passed with an identified reviewer.')
            if challenge.get('bankVersion') != bank['bankVersion']:
                errors.append('Independent coverage challenge does not bind the current bankVersion.')
            if challenge.get('unresolvedFindings') not in ([], 0):
                errors.append('Independent coverage challenge has unresolved or unaccounted findings.')
    question_statuses = Counter(q['status'] for q in questions.values())
    report['counts'] = {
        'sources': len(sources), 'sourcesReady': sum(s['retrievalStatus'] == 'ready' for s in sources.values()),
        'pagesExpected': sum(s['pageCount'] or 0 for s in sources.values()), 'pagesInventoried': len(slides),
        'pagesVisuallyInspected': sum(s['visualInspection']['status'] == 'complete' for s in slides.values()),
        'pagesExcluded': sum(s['disposition'] == 'excluded' for s in slides.values()),
        'pagesRepeated': sum(s['disposition'] == 'repeated' for s in slides.values()),
        'concepts': len(concepts),
        'conceptsWithDraftQuestions': sum(bool(c['questionIds']) for c in concepts.values()),
        'conceptsWithVerifiedQuestions': sum(bool(current_verified.intersection(c['questionIds'])) for c in concepts.values()),
        'questions': len(questions), 'questionsByStatus': dict(question_statuses),
        'currentlyVerifiedQuestions': len(current_verified), 'staleReviews': len(stale_review_ids),
        'numericalFamilies': len(bank['learningTools']['numericalFamilies']),
        'verifiedByWeek': dict(Counter(str(questions[q]['week']) if questions[q]['week'] is not None else 'unmapped' for q in current_verified)),
        'verifiedByDifficulty': dict(Counter(questions[q]['difficulty'] for q in current_verified)),
        'verifiedByType': dict(Counter(questions[q]['type'] for q in current_verified)),
    }
    report['valid'] = not errors
    return report


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == 'question-hash':
        parser = argparse.ArgumentParser(description='Print canonical question SHA-256')
        parser.add_argument('command')
        parser.add_argument('question', type=Path)
        args = parser.parse_args(argv)
        print(question_hash(load_json(args.question)))
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bank', nargs='?', type=Path, default=PROJECT_ROOT / 'data' / 'bank.json')
    parser.add_argument('--root', type=Path, default=PROJECT_ROOT)
    parser.add_argument('--release', action='store_true')
    parser.add_argument('--allow-synthetic', action='store_true', help='Test fixtures only; never use for course builds')
    parser.add_argument('--skip-files', action='store_true', help='Only schema/reference checks; NOT release validation')
    parser.add_argument('--json', action='store_true', help='Write machine-readable report to stdout')
    parser.add_argument('--report', type=Path, help='Persist machine-readable report')
    args = parser.parse_args(argv)
    if args.release and args.skip_files:
        parser.error('--release cannot be combined with --skip-files')
    try:
        bank = load_json(args.bank)
        result = validate_bank(bank, args.root, release=args.release, allow_synthetic=args.allow_synthetic, check_files=not args.skip_files)
    except (OSError, ValueError, KeyError) as exc:
        result = {'valid': False, 'release': args.release, 'errors': [str(exc)], 'warnings': [], 'counts': {}}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(('PASS' if result['valid'] else 'FAIL') + (' release' if args.release else ' checkpoint') + ' integrity validation')
        for key, value in result['counts'].items():
            print(f'  {key}: {value}')
        for kind in ('errors', 'warnings'):
            for message in result[kind]:
                print(f'{kind[:-1].upper()}: {message}')
        print('Source-based independent review, full visual coverage, and offline browser tests remain separate requirements.')
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
