#!/usr/bin/env python3
"""Read-only coverage reconciliation; optional audit-only publication after assembly.

Default: compute and print a summary without writes. --write requires the exact
coordinator-supplied base bank SHA and closed substantive coverage. --check-binding
accepts a later bank embedding this audit only when the declared payload digest
is unchanged. No question, source, app, build output, or canonical bank is edited.
"""
import argparse
import collections
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import canonical_json, question_hash
from review_gate import apply_review_gate
from assemble_bank import assignment_reuse_errors

FIELDS = ('sources', 'slides', 'concepts', 'questions', 'reviews', 'assignmentReuse')
AUDIT = ROOT / 'audits/coverage_challenge.json'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def object_hash(value):
    return hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()


def coverage_input_digest(bank):
    """Object keys sorted, list order retained, UTF-8 canonical JSON, no newline."""
    return object_hash({key: bank.get(key) for key in FIELDS})


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def atomic_write(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == raw:
        return
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_bytes(raw)
    temporary.replace(path)


def binding_check(bank, audit, current_bank_sha):
    binding = audit.get('coverageInputBinding', {})
    errors = []
    if (audit.get('schema_version') != '2.0.0'
            or audit.get('audit_id') != 'robotics-final-source-coverage-reconciliation'
            or audit.get('status') != 'substantive_coverage_closed_release_pending'
            or audit.get('substantiveCoverage', {}).get('allRecordedSubstantiveCoverageClosed') is not True
            or audit.get('issues') != [] or audit.get('unresolvedFindings') != []):
        errors.append('Audit is not a complete, closed substantive-coverage reconciliation record.')
    if not isinstance(audit.get('bankSnapshotSha256'), str) or len(audit['bankSnapshotSha256']) != 64:
        errors.append('Reviewed base bank file SHA is missing or malformed.')
    if current_bank_sha != audit.get('bankSnapshotSha256') and bank.get('coverageChallenge') != audit:
        errors.append('Derived bank does not embed the exact coverage audit being checked.')
    if binding.get('fields') != list(FIELDS):
        errors.append('Coverage digest scope differs from the declared contract.')
    if binding.get('sha256') != coverage_input_digest(bank):
        errors.append('Coverage-relevant payload changed after reviewed base assembly.')
    artifacts = audit.get('evidenceArtifacts', [])
    required_paths = {
        'audits/legacy-concept-closure/L30-durable-coverage-crosslinks.json',
        'audits/legacy-concept-closure/L02-summary-quote-disposition.json',
        'audits/legacy-concept-closure/summary-row-crosslinks.json',
        'audits/legacy-concept-closure/independent-sidecar-binding-receipt-v1.json',
        'audits/legacy-concept-closure/L60-stale-pending-metadata-receipt-v1.json',
        'audits/assignment-coverage/full120-independent-completeness-closure.json',
    }
    if not required_paths <= {x.get('path') for x in artifacts if isinstance(x, dict)}:
        errors.append('Required independent coverage evidence artifacts are missing.')
    for item in artifacts:
        path = ROOT / item['path']
        if not path.is_file() or file_hash(path) != item['sha256']:
            errors.append('Missing or changed audit evidence: ' + item['path'])
    receipt = audit.get('detailedReceipt', {})
    if receipt.get('path') and receipt.get('sha256'):
        path = ROOT / receipt['path']
        if not path.is_file() or file_hash(path) != receipt['sha256']:
            errors.append('Missing or changed detailed coverage receipt.')
        else:
            detail = read(path)
            if (detail.get('coverageInputSha256') != binding.get('sha256')
                    or detail.get('reviewedBaseBankSha256') != audit.get('bankSnapshotSha256')
                    or detail.get('counts') != audit.get('counts')
                    or detail.get('findings') != []
                    or detail.get('generatorSha256') != file_hash(__file__)):
                errors.append('Detailed receipt bindings, findings, counts or generator are inconsistent.')
    else:
        errors.append('Detailed hash-bound coverage receipt is required.')
    # A digest proves equality, not completeness. Reproduce the fail-closed
    # coverage checks instead of trusting a caller-supplied closed status label.
    # The only bank-version normalization permitted is the explicitly identified
    # reviewed base version. All coverage payload fields remain the current ones.
    normalized = dict(bank, bankVersion=audit.get('bankVersion'))
    rechecked, _, regenerated_receipt_raw = reconcile(normalized, audit.get('bankSnapshotSha256', 'missing'))
    if rechecked['issues']:
        errors.append('Current payload has unresolved coverage reconciliation findings.')
    if audit.get('counts') != rechecked['counts']:
        errors.append('Audit counts do not reproduce from the current bound payload.')
    if audit.get('evidenceArtifacts') != rechecked['evidenceArtifacts']:
        errors.append('Audit evidence list does not reproduce from the current reconciliation.')
    # Do not let prose/provenance or detail rows silently overstate this purely
    # deterministic audit. History is the sole non-derived audit field; its
    # archival hash is checked separately. In particular, no browser certification,
    # fresh all-page inspection or erased source qualification can be injected.
    if {k: v for k, v in audit.items() if k != 'history'} != {k: v for k, v in rechecked.items() if k != 'history'}:
        errors.append('Audit semantic, provenance, release or receipt fields differ from exact regeneration.')
    if receipt.get('path'):
        path = ROOT / receipt['path']
        if not path.is_file() or path.read_bytes() != regenerated_receipt_raw:
            errors.append('Detailed accountability receipt differs from exact regeneration.')
    history = audit.get('history', {})
    if history.get('supersedes'):
        path = ROOT / history['supersedes']
        if not path.is_file() or file_hash(path) != history.get('sha256'):
            errors.append('Historical coverage audit archive is missing or changed.')
    return errors


def reconcile(bank, bank_sha):
    evidence = {}
    problems = []

    def record(path):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        evidence[path.relative_to(ROOT).as_posix()] = file_hash(path)
        return read(path)

    def require(condition, code, target):
        if not condition:
            problems.append({'code': code, 'target': target})
        return bool(condition)

    def sidecar_link(container, field, path):
        value = container.get(field, {})
        relative = path.relative_to(ROOT).as_posix()
        return require(value.get('path') == relative and value.get('sha256') == file_hash(path),
                       'stale_or_missing_sidecar_link', container['id'])

    qmap = {x['id']: x for x in bank['questions']}
    cmap = {x['id']: x for x in bank['concepts']}
    smap = {x['id']: x for x in bank['slides']}
    rmap = {x['id']: x for x in bank['reviews']}
    source_map = {x['id']: x for x in bank['sources']}
    for key in ('questions', 'concepts', 'slides', 'reviews', 'sources'):
        require(len(bank[key]) == len({x['id'] for x in bank[key]}), 'duplicate_ids', key)
    gated = copy.deepcopy(bank['questions'])
    quarantine = apply_review_gate(gated, bank['reviews'], bank['slides'], bank['sources'])
    gate_changes = [q['id'] for q in gated if q != qmap[q['id']]]
    require(not gate_changes, 'assembled_gate_projection_mismatch', gate_changes)
    verified = {q['id'] for q in gated if q['status'] == 'verified'}
    qhash = {qid: question_hash(q) for qid, q in qmap.items()}

    def question_binding(binding, page=None):
        qid = binding['id']
        q = qmap.get(qid)
        valid = require(qid in verified, 'crosslink_not_currently_verified', qid)
        if not q:
            return False
        valid &= require(qhash[qid] == binding['questionSha256'] and q['version'] == binding['version'],
                         'crosslink_question_hash_mismatch', qid)
        valid &= require(object_hash(q) == binding['wholeObjectSha256'], 'crosslink_whole_object_changed', qid)
        pages = [c['physicalPage'] for c in q['citations']]
        valid &= require(pages == binding['actualCitedPhysicalPages'], 'crosslink_actual_pages_changed', qid)
        if page is not None:
            valid &= require(binding['directlyCitesContextPage'] == (page in pages), 'false_direct_citation_claim', qid)
        for review in binding['reviewBindings']:
            valid &= require(review['id'] in rmap and object_hash(rmap[review['id']]) == review['sha256']
                             and review['id'] in q['reviewIds'], 'crosslink_review_hash_mismatch', review['id'])
        return bool(valid)

    aliases = record(HERE / 'L30-durable-coverage-crosslinks.json')
    quote = record(HERE / 'L02-summary-quote-disposition.json')
    summaries = record(HERE / 'summary-row-crosslinks.json')
    adjudication = record('audits/lecture-ledger-challenge/L02-L05-independent-adjudication.json')
    require(len(aliases['items']) == 8, 'alias_count_mismatch', 'L30')
    alias_ids = set()
    for item in aliases['items']:
        cid = item['legacyConceptId']
        c = cmap.get(cid, {})
        require(bool(c), 'missing_alias_concept', cid)
        if not c:
            continue
        alias_ids.add(cid)
        sidecar_link(c, 'coverageResolution', HERE / 'L30-durable-coverage-crosslinks.json')
        original = item['originalConcept']
        require(object_hash(original) == item['legacyConceptWholeObjectSha256'], 'original_alias_hash_changed', cid)
        for field in ('id', 'title', 'description', 'slideIds', 'questionIds'):
            require(c.get(field) == original.get(field), 'alias_source_or_question_mutation', cid + ':' + field)
        require(c.get('coverageDisposition') == item['disposition'], 'alias_disposition_not_integrated', cid)
        for link in item['verifiedQuestionCrosslinks']:
            question_binding(link, item['originalPhysicalPages'][0])
    terminal = next(a for a in aliases['items'] if a['legacyConceptId'] == 'learning-observed-P0905-C03')
    require(bool(terminal['residualSourceQualification']), 'terminal_omission_not_retained', terminal['legacyConceptId'])
    terminal_link = next(q for q in terminal['verifiedQuestionCrosslinks'] if q['id'] == 'W06-L30-Q056')
    require(terminal_link['actualCitedPhysicalPages'] == [914] and not terminal_link['directlyCitesContextPage'],
            'p905_terminal_false_citation', 'W06-L30-Q056')

    quote_id = quote['conceptId']
    qc = cmap.get(quote_id, {})
    require(qc.get('coverageDisposition') == 'excluded_commentary_only' and not qc.get('questionIds'),
            'quote_exclusion_not_narrowly_integrated', quote_id)
    if qc:
        sidecar_link(qc, 'coverageResolution', HERE / 'L02-summary-quote-disposition.json')
    require(len(quote['substantiveRowsPreserved']) == 7 and quote['pageRemainsExaminable'] is True,
            'substantive_p93_rows_not_preserved', quote_id)
    require(smap['lectures-p0093']['disposition'] == 'examinable', 'p93_page_incorrectly_excluded', 'lectures-p0093')
    require(any(d['conceptId'] == quote_id and d['decision'] == 'commentary_exclusion' for d in adjudication['decisions']),
            'quote_independent_adjudication_missing', quote_id)
    for row in quote['substantiveRowsPreserved']:
        for link in row['semanticQuestionCrosslinks']:
            question_binding(link, 93)

    for summary in summaries['summaryPages']:
        pp = summary['physicalPage']
        slide = smap[f'lectures-p{pp:04}']
        require(slide['disposition'] == 'repeated' and slide.get('incrementalChangesChecked') is True
                and slide.get('repeatsSlideIds') == summary['proposedRepeatsSlideIds'],
                'summary_repeat_not_integrated', slide['id'])
        sidecar_link(slide, 'coverageCrosslinks', HERE / 'summary-row-crosslinks.json')
        require(file_hash(ROOT / summary['previewPath']) == summary['previewSha256'], 'summary_preview_changed', slide['id'])
        for row in summary['rows']:
            for link in row['semanticQuestionCrosslinks']:
                question_binding(link, pp)

    frozen = {}
    for version in (1, 2, 3):
        draft = record(HERE / f'qualified-drafts-v{version}.json')
        record(HERE / f'freeze-manifest-v{version}.json')
        record(HERE / ('independent-review-v1.json' if version == 1 else f'independent-supplemental-review-v{version}.json'))
        for q in draft['questions']:
            frozen[q['id']] = q
    six = []
    for qid, author_q in sorted(frozen.items()):
        q = qmap.get(qid, {})
        require(qid in verified and qhash.get(qid) == question_hash(author_q), 'qualified_question_not_integrated', qid)
        if not q:
            continue
        restored = copy.deepcopy(q)
        restored['status'] = author_q['status']
        restored['reviewIds'] = author_q['reviewIds']
        require(restored == author_q, 'frozen_qualified_object_mutated', qid)
        six.append({'questionId': qid, 'version': q['version'], 'questionSha256': qhash[qid],
                    'wholeAssembledObjectSha256': object_hash(q), 'reviewIds': q['reviewIds'],
                    'sourceQualification': q['conflictResolution']['qualification'],
                    'primaryEvidenceScope': q['primaryEvidence']['scope']})

    by_slide_q = collections.defaultdict(list)
    by_slide_c = collections.defaultdict(list)
    by_concept_q = collections.defaultdict(set)
    for q in bank['questions']:
        for c in q['citations']:
            if q['id'] in verified:
                by_slide_q[c['slideId']].append(q['id'])
        for cid in q['conceptIds']:
            by_concept_q[cid].add(q['id'])
    for c in bank['concepts']:
        for sid in c['slideIds']:
            by_slide_c[sid].append(c['id'])

    reuse_errors = assignment_reuse_errors(bank, ROOT, check_files=True)
    require(not reuse_errors, 'assignment_reuse_gate_failed', reuse_errors)
    reuse = bank.get('assignmentReuse', {})
    require(not reuse.get('diagnostics'), 'assignment_reuse_diagnostics', reuse.get('diagnostics'))
    reuse_concepts = set(reuse.get('byConcept', {}))
    concept_rows = []
    for c in bank['concepts']:
        cid = c['id']
        source_ids = sorted({smap[s]['sourceId'] for s in c['slideIds']})
        direct = sorted(set(c['questionIds']) & verified)
        require(set(c['questionIds']) == by_concept_q[cid], 'asymmetric_concept_question_links', cid)
        if direct:
            kind = 'direct_declared_concept_question_coverage'
        elif cid in alias_ids:
            kind = 'reviewed_semantic_alias_with_original_source_qualification' if cid == terminal['legacyConceptId'] else 'reviewed_semantic_alias'
        elif cid == quote_id:
            kind = 'excluded_commentary_only'
        elif cid in reuse_concepts:
            kind = 'independently_reviewed_assignment_reuse'
        else:
            kind = 'unresolved'
            require(False, 'concept_without_accepted_coverage_or_disposition', cid)
        concept_rows.append({'conceptId': cid, 'sourceIds': source_ids, 'coverageKind': kind,
                             'directVerifiedQuestionIds': direct, 'semanticResolution': c.get('coverageResolution'),
                             'assignmentReuseMappingIds': reuse.get('byConcept', {}).get(cid, [])})

    page_rows = []
    for source in bank['sources']:
        actual = sorted(s['physicalPage'] for s in bank['slides'] if s['sourceId'] == source['id'])
        require(actual == list(range(1, source['pageCount'] + 1)), 'source_pagination_gap_or_duplicate', source['id'])
        require(file_hash(ROOT / source['localPath']) == source['sha256'], 'source_pdf_hash_changed', source['id'])
    for s in bank['slides']:
        sid = s['id']
        require(s.get('sourceSha256') == source_map[s['sourceId']]['sha256'], 'slide_source_hash_mismatch', sid)
        require(s.get('visualInspection', {}).get('status') == 'complete', 'visual_inspection_incomplete', sid)
        require(bool(s.get('visualInspection', {}).get('inspectorId')), 'visual_inspector_missing', sid)
        require((ROOT / s['previewPath']).is_file(), 'rendered_preview_missing', sid)
        require(s.get('disposition') in ('examinable', 'repeated', 'excluded'), 'unaccounted_page_disposition', sid)
        require(not s.get('conceptLedgerPending'), 'stale_concept_pending_flag', sid)
        if s['disposition'] == 'excluded':
            require(bool(s.get('exclusionReason')), 'page_exclusion_reason_missing', sid)
            kind = 'justified_source_page_exclusion'
        elif s['disposition'] == 'repeated':
            targets = s.get('repeatsSlideIds', [])
            require(bool(targets) and s.get('incrementalChangesChecked') is True, 'repeat_evidence_incomplete', sid)
            require(all(t in smap and t != sid for t in targets), 'repeat_target_missing_or_self', sid)
            require(any(by_slide_q[t] for t in targets), 'repeat_targets_without_direct_verified_support', sid)
            kind = 'repeated_content_with_explicit_source_targets'
        else:
            require(bool(by_slide_c[sid]), 'examinable_page_without_concepts', sid)
            require(bool(by_slide_q[sid]), 'examinable_page_without_direct_verified_citation', sid)
            kind = 'examinable_direct_citation_and_concept_coverage'
        page_rows.append({'slideId': sid, 'sourceId': s['sourceId'], 'physicalPage': s['physicalPage'],
                          'disposition': s['disposition'], 'accountabilityKind': kind,
                          'visualInspection': s['visualInspection'], 'conceptIds': by_slide_c[sid],
                          'directVerifiedQuestionIds': sorted(set(by_slide_q[sid])),
                          'repeatTargets': s.get('repeatsSlideIds', []), 'exclusionReason': s.get('exclusionReason')})

    ledger = record('audits/assignment-coverage/coverage-ledger.json')
    challenge = record('audits/assignment-coverage/full120-independent-completeness-challenge-v2.json')
    closure = record('audits/assignment-coverage/full120-independent-completeness-closure.json')
    require(challenge['ledgerSha256'] == file_hash(ROOT / challenge['ledgerPath']),
            'assignment_completeness_ledger_changed', challenge['ledgerPath'])
    require(challenge['sourceSha256'] == ledger['sourceSha256'] == source_map['assignments']['sha256'],
            'assignment_completeness_source_changed', 'assignments')
    require(closure['challengeSha256'] == file_hash(ROOT / closure['challengePath']), 'assignment_closure_challenge_changed', closure['challengePath'])
    closure_summary = closure.get('summary', {})
    require(closure_summary.get('boundedAssignmentSubpartChallengeClosed') is True
            and closure_summary.get('openBoundedSubpartGaps') == 0
            and closure_summary.get('missingOriginalItems') == 0
            and closure_summary.get('originalItemDenominator') == 120
            and closure_summary.get('originalItemsRepresented') == 120,
            'assignment_completeness_closure_incomplete', closure['id'])
    expected_discharge = set(challenge['summary']['newBoundedGapItems']) | set(challenge['summary']['knownDuplicateReuseItems'])
    discharged = [x['sourceItemId'] for x in closure['closedFindings']]
    require(set(discharged) == expected_discharge and len(discharged) == len(expected_discharge),
            'assignment_completeness_findings_not_exactly_discharged', sorted(expected_discharge))
    mapping_evidence = closure['mappingEvidence']
    require(file_hash(ROOT / mapping_evidence['path']) == mapping_evidence['sha256']
            and file_hash(ROOT / mapping_evidence['independentReviewPath']) == mapping_evidence['independentReviewSha256']
            and mapping_evidence['additionalUniqueQuestions'] == 0,
            'assignment_completeness_mapping_evidence_stale', mapping_evidence['path'])
    record(mapping_evidence['path'])
    record(mapping_evidence['independentReviewPath'])
    require(len(ledger['items']) == 120 and len(challenge['items']) == 120, 'assignment_source_denominator_mismatch', '120')
    assignment_rows = []
    current_assignment = collections.defaultdict(list)
    for q in bank['questions']:
        if q.get('assignmentSourceItemId'):
            current_assignment[q['assignmentSourceItemId']].append(q['id'])
    challenge_map = {i['originalSourceItemId']: i for i in challenge['items']}
    for original in ledger['items']:
        oid = original['id']
        item = challenge_map[oid]
        require(file_hash(ROOT / item['originalRecordPath']) == item['originalRecordSha256'], 'assignment_original_changed', oid)
        require(qhash.get(item['questionId']) == item['questionSha256'], 'assignment_completeness_question_changed', item['questionId'])
        direct = sorted(qid for qid in current_assignment[oid] if qid in verified)
        mappings = reuse.get('bySourceItem', {}).get(oid, [])
        require(bool(direct or mappings), 'assignment_source_item_uncovered', oid)
        assignment_rows.append({'sourceItemId': oid, 'sourcePages': original['physicalPages'],
                                'originalSourceKeyDisposition': original['independentSourceKeyAuditStatus'],
                                'directVerifiedAdaptationQuestionIds': direct, 'reviewedReuseMappingIds': mappings,
                                'coverageKind': 'reviewed_semantic_reuse' if mappings else 'verified_direct_adaptation',
                                'originalRecordPath': item['originalRecordPath'], 'originalRecordSha256': item['originalRecordSha256']})
    for finding in closure['closedFindings']:
        if finding.get('questionId'):
            require(finding['questionId'] in verified and qhash.get(finding['questionId']) == finding['questionSha256'],
                    'assignment_subpart_closure_not_accepted', finding['questionId'])
            record(finding['reviewPath'])
            require(file_hash(ROOT / finding['reviewPath']) == finding['reviewSha256'],
                    'assignment_subpart_closure_review_stale', finding['reviewPath'])
        elif finding.get('mappingId'):
            require(finding['mappingId'] in {x['id'] for x in reuse.get('links', [])}, 'assignment_reuse_closure_missing', finding['mappingId'])
    duplicate_ids = {x['duplicateQuestionId'] for x in reuse.get('links', [])}
    require(duplicate_ids == {'ASSIGN-W04-Q007', 'ASSIGN-W04-Q009'}, 'expected_two_audit_duplicates_not_dispositioned', sorted(duplicate_ids))
    unaccepted = sorted(set(qmap) - verified)
    unexpected_unaccepted = sorted(set(unaccepted) - duplicate_ids)
    require(not unexpected_unaccepted, 'unexpected_unaccepted_questions', unexpected_unaccepted)
    exclusions = [{'questionId': qid, 'status': qmap[qid]['status'], 'questionSha256': qhash[qid],
                   'sourceItemId': qmap[qid].get('assignmentSourceItemId'),
                   'reason': 'Duplicate adaptation excluded from the normal pool; original item covered through separately approved unchanged-question reuse.',
                   'mappingIds': [x['id'] for x in reuse.get('links', []) if x['duplicateQuestionId'] == qid]}
                  for qid in sorted(duplicate_ids)]

    # Historical observations are evidence of who viewed what, not new inspections.
    old_observations = record('audits/lecture-ledger-challenge/source-observations.json')
    author_observations = record(HERE / 'author-visual-observations.json')
    crosslink_observations = record(HERE / 'coverage-visual-observations.json')
    record('audits/lecture-ledger-challenge/distributed-review-index.json')
    record('audits/lecture-ledger-challenge/L30-legacy-aliases.json')
    record('audits/lecture-ledger-challenge/L60-course-review-crosslinks.json')
    sidecar_review = record(HERE / 'independent-sidecar-binding-receipt-v1.json')
    require(not sidecar_review['blockingFindings'], 'independent_sidecar_review_unresolved', sidecar_review['receiptId'])
    for binding in sidecar_review['sidecarBindings']:
        require(file_hash(ROOT / binding['path']) == binding['sha256'], 'independent_sidecar_review_stale', binding['path'])
    extra = sidecar_review['documentationNote']['supplementalBinding']
    extra_q = qmap.get(extra['questionId'], {})
    require(extra['questionId'] in verified and qhash.get(extra['questionId']) == extra['questionSha256']
            and object_hash(extra_q) == extra['assembledWholeObjectSha256'],
            'supplemental_Q078_qualification_binding_stale', extra['questionId'])
    for binding in extra['reviewBindings']:
        require(binding['id'] in rmap and object_hash(rmap[binding['id']]) == binding['sha256'],
                'supplemental_Q078_review_binding_stale', binding['id'])
    stale_metadata_receipt = record(HERE / 'L60-stale-pending-metadata-receipt-v1.json')
    for page in stale_metadata_receipt['pages']:
        require(smap[page['slideId']].get('conceptLedgerPending') is False,
                'L60_stale_pending_receipt_not_integrated', page['slideId'])
        for q in page['directVerifiedQuestionBindings']:
            require(q['id'] in verified and qhash.get(q['id']) == q['questionSha256'],
                    'L60_pending_closure_question_binding_stale', q['id'])
    closure_pages = sorted({x['physicalPage'] for x in author_observations['pages']} |
                           {x['physicalPage'] for x in crosslink_observations['observations']})
    for observations in (old_observations, author_observations['pages'], crosslink_observations['observations'], sidecar_review['visualEvidence']):
        for observation in observations:
            require(file_hash(ROOT / observation['previewPath']) == observation['previewSha256'],
                    'historical_observation_preview_changed', observation['physicalPage'])

    lecture_concepts = [c for c in concept_rows if 'lectures' in c['sourceIds']]
    lecture_pages = [p for p in page_rows if p['sourceId'] == 'lectures']
    lecture_ids = {p['slideId'] for p in lecture_pages} | {c['conceptId'] for c in lecture_concepts}
    lecture_qids = {q['id'] for q in bank['questions'] if any(c['sourceId'] == 'lectures' for c in q['citations'])}
    lecture_related_codes = ('crosslink_', 'alias_', 'original_alias_', 'quote_', 'summary_', 'frozen_', 'qualified_', 'terminal_', 'p905_', 'p93_', 'substantive_')
    lecture_problems = [p for p in problems if str(p['target']) in lecture_ids | lecture_qids
                        or p['code'].startswith(lecture_related_codes)]
    closed = not problems
    digest = coverage_input_digest(bank)
    counts = {
        'lecturePages': len(lecture_pages), 'assignmentPages': len(page_rows) - len(lecture_pages),
        'allSourcePages': len(page_rows), 'distributedVisualInspectionRecords': sum(s['visualInspection']['status'] == 'complete' for s in bank['slides']),
        'lectureConceptRecords': len(lecture_concepts), 'allConceptRecords': len(concept_rows),
        'lectureConceptCoverageKinds': dict(collections.Counter(c['coverageKind'] for c in lecture_concepts)),
        'allConceptCoverageKinds': dict(collections.Counter(c['coverageKind'] for c in concept_rows)),
        'lecturePageAccountabilityKinds': dict(collections.Counter(p['accountabilityKind'] for p in lecture_pages)),
        'allPageDispositions': dict(collections.Counter(s['disposition'] for s in bank['slides'])),
        'questionsTotal': len(qmap), 'questionsVerified': len(verified),
        'questionStatuses': dict(collections.Counter(q['status'] for q in bank['questions'])),
        'substantiveCoverageOpenQuestions': len(unexpected_unaccepted), 'sourceDuplicateAuditExclusions': len(exclusions),
        'legacyAliasesResolved': len(alias_ids), 'commentaryOnlyConceptExclusions': 1,
        'p93SubstantiveRowsPreserved': 7, 'newSummaryRowsCrosslinked': sum(len(x['rows']) for x in summaries['summaryPages']),
        'qualifiedQuestionsVerified': len(six), 'assignmentSourceItemDenominator': 120,
        'assignmentItemsWithDirectVerifiedAdaptations': sum(bool(x['directVerifiedAdaptationQuestionIds']) for x in assignment_rows),
        'assignmentItemsWithReviewedReuse': sum(bool(x['reviewedReuseMappingIds']) for x in assignment_rows),
        'assignmentOriginalSourceKeyDispositions': dict(collections.Counter(x['originalSourceKeyDisposition'] for x in assignment_rows)),
        'additionalUniqueQuestionsFromReuse': 0, 'reviewGateProjectionMismatches': len(gate_changes),
        'unresolvedReconciliationFindings': len(problems)}
    receipt = {'schemaVersion': '1.0.0', 'reviewedBaseBankVersion': bank['bankVersion'], 'reviewedBaseBankSha256': bank_sha,
               'coverageInputSha256': digest, 'counts': counts, 'findings': problems,
               'lectureFindings': lecture_problems, 'pageAccountability': page_rows, 'conceptAccountability': concept_rows,
               'assignmentSourceItems': assignment_rows, 'qualifiedQuestions': six, 'sourceDuplicateAuditExclusions': exclusions,
               'reviewGateQuarantine': quarantine, 'generatorPath': Path(__file__).relative_to(ROOT).as_posix(),
               'generatorSha256': file_hash(__file__)}
    receipt_path = HERE / ('final-coverage-receipt-' + digest + '.json')
    receipt_raw = encoded(receipt)
    status = 'substantive_coverage_closed_release_pending' if closed else 'coverage_reconciliation_findings_pending'
    audit = {
        'schema_version': '2.0.0', 'audit_id': 'robotics-final-source-coverage-reconciliation', 'status': status,
        'reviewerId': 'robotics-legacy-closure-coverage-compiler',
        'reviewerRoleBoundary': 'Compiler authored the six narrow qualified additions; their approvals are separate exact-hash independent reviews. This reconciliation carries prior independent source/coverage decisions and does not independently approve its own questions.',
        'scope': 'All 1953 lecture pages and 59 assignment pages structurally reconciled, with distributed prior visual inspections, prior independent source-item challenges and exact current question/review bindings.',
        'claim': ('Recorded substantive lecture and assignment coverage is closed; two duplicate adaptations remain audit-only exclusions, not missing source coverage. ' if closed else 'Current reconciliation has the listed findings; no full content-closure claim is made. ') + 'This is not a browser, hardware, runtime, or finished-release certificate, nor a fresh single-reviewer inspection of every page.',
        'bankVersion': bank['bankVersion'], 'bankSnapshotSha256': bank_sha,
        'coverageInputBinding': {'fields': list(FIELDS), 'sha256': digest,
            'algorithm': 'SHA256 of UTF-8 scripts.validate.canonical_json({field: bank.get(field) for field in fields}); sorted object keys, preserved array order, no trailing newline.',
            'excludes': ['bankVersion', 'coverageChallenge', 'all other top-level bank fields'],
            'interpretation': 'bankSnapshotSha256 identifies the exact reviewed base bank file. A later bank embedding this audit may have a different whole-file SHA; equivalence is asserted only for this exact coverage-input digest.',
            'validator': 'python audits/legacy-concept-closure/refresh_coverage_challenge.py --check-binding'},
        'counts': counts,
        'source_versions': [{'source': s['id'], 'sha256': s['sha256'], 'pageCount': s['pageCount']} for s in bank['sources']],
        'substantiveCoverage': {'lectures': 'closed' if closed else 'reconciliation_findings_pending_no_partial_certification',
                                'assignments': 'closed' if closed else 'see_receipt',
                                'allRecordedSubstantiveCoverageClosed': closed,
                                'coverageMeaning': 'Every identified concept and source item is accounted for by current reviewed direct questions, exact reviewed semantic reuse, or narrow justified disposition. This bounded challenge is not a mathematical proof that no future reviewer could discover an omitted angle.'},
        'inspection_provenance': {
            'distributedManifest': 'Exact bound bank slides[].visualInspection; 2012 source pages, not a new single-person sweep.',
            'priorTargetedLectureChallengePages': len(old_observations), 'closureStreamPersonallyViewedPages': closure_pages,
            'closureStreamPersonallyViewedPageCount': len(closure_pages), 'newPagesPersonallyViewedByThisRefresh': 0,
            'priorAssignmentChallengePersonallyViewedPages': challenge['summary']['personallyInspectedPages'],
            'sourceExtractionCountedAsVisualInspection': False,
            'limitation': 'Prior observations retain their original authors and dates; historical question-review approvals are not recast as fresh page inspections.'},
        'coverageDistinctions': {
            'direct': 'Declared concept/question links and actual cited source pages are enumerated in the receipt.',
            'semanticAliases': 'Eight L30 original concept IDs remain with empty questionIds and exact sidecar links. These links do not rewrite accepted question conceptIds or source citations.',
            'terminalOmission': aliases['terminalBoundary'],
            'quoteOnlyExclusion': quote['exclusionScope'], 'p93SubstantiveRowsPreserved': 7,
            'repeatedSummaries': 'Pages 984/1085/1195 retain row-level semantic links and explicit earlier-page targets; these are not direct citations from the unchanged questions.',
            'sourceDuplicateAuditExclusions': exclusions,
            'sourceKeyConflicts': 'The 12 conflicting original assignment keys and 26 qualified source cases remain preserved. Qualified accepted adaptations do not validate or silently replace those original keys.'},
        'primaryEvidenceAccessBoundary': 'ROS historical release and OccupancyGrid support remains official indexed evidence, not full page reads. Existing Anubis denials, other ROS documentation denials and all denied execution routes remain stopped.',
        'issues': problems, 'unresolvedFindings': [p['code'] + ':' + str(p['target']) for p in problems],
        'release_gates': {'source_inventory_reconciled': 'passed' if closed else 'see_receipt',
            'all_pages_visually_inspected': 'distributed_prior_manifest_not_single_reviewer_fresh_inspection',
            'substantive_lecture_coverage': 'closed' if closed else 'reconciliation_findings_pending_no_partial_certification',
            'substantive_assignment_coverage': 'closed' if closed else 'findings_pending',
            'source_duplicate_audit_exclusions': 'retained_separate_from_substantive_coverage',
            'independent_answer_reviews': 'exact_current_fail_closed_gate_reproduced',
            'offline_browser_qa': 'pending_permitted_environment_not_executed_by_this_stream',
            'downloaded_release_offline_qa': 'pending_exact_downloaded_HTML_real_browser_verification',
            'complete_bank_performance': 'not_certified_by_coverage_audit',
            'github_checkpoint_verified': 'tracked_by_coordinator_not_certified_here',
            'final_release_certified': False},
        'remainingReleaseRequirements': ['Run the exact downloaded final HTML in a permitted environment with existing Node/Playwright/Chromium, normal local process sockets and file:// access; complete real interactions, screenshots, source-PDF and print checks.',
                                          'Keep passing deterministic logic tests distinct from actual browser verification; do not retry denied browser or dependency routes.',
                                          'Coordinator verifies final package, final payload digest, release performance and remote checkpoint separately.'],
        'detailedReceipt': {'path': receipt_path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(receipt_raw).hexdigest()},
        'evidenceArtifacts': [{'path': p, 'sha256': h} for p, h in sorted(evidence.items())],
        'history': {'supersededAuditPolicy': 'Previous top-level audit bytes are archived by SHA before replacement; their original pending findings remain history rather than current claims.'}}
    return audit, receipt_path, receipt_raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bank', type=Path, default=ROOT / 'data/bank.json')
    parser.add_argument('--expected-bank-sha')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check-binding', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    bank_raw = args.bank.read_bytes()
    bank_sha = hashlib.sha256(bank_raw).hexdigest()
    bank = json.loads(bank_raw)
    if args.expected_bank_sha and args.expected_bank_sha != bank_sha:
        raise SystemExit('STOP: expected assembled bank SHA does not match current bytes.')
    if args.self_test:
        base = coverage_input_digest(bank)
        changed = copy.deepcopy(bank)
        changed['bankVersion'] = 'test-version-only'
        changed['coverageChallenge'] = {'test': 'embedding-only'}
        assert coverage_input_digest(changed) == base
        changed['questions'][0]['stem'] += ' test substantive mutation'
        assert coverage_input_digest(changed) != base
        print(json.dumps({'digestSelfTest': 'passed', 'bankSha256': bank_sha, 'coverageInputSha256': base}))
        return
    if args.check_binding:
        audit = read(AUDIT)
        errors = binding_check(bank, audit, bank_sha)
        if file_hash(args.bank) != bank_sha:
            errors.append('Bank changed during binding validation.')
        print(json.dumps({'bindingValid': not errors, 'errors': errors, 'currentBankSha256': bank_sha,
                          'reviewedBaseBankSha256': audit.get('bankSnapshotSha256'),
                          'coverageInputSha256': coverage_input_digest(bank)}, indent=2))
        raise SystemExit(bool(errors))
    audit, receipt_path, receipt_raw = reconcile(bank, bank_sha)
    summary = {k: audit[k] for k in ('status', 'bankVersion', 'bankSnapshotSha256', 'counts', 'issues')}
    summary['coverageInputSha256'] = audit['coverageInputBinding']['sha256']
    summary['writesPerformed'] = False
    if args.write:
        if not args.expected_bank_sha:
            raise SystemExit('STOP: --write requires --expected-bank-sha from integration owner.')
        if audit['issues']:
            print(json.dumps(summary, indent=2))
            raise SystemExit('STOP: unresolved substantive/metadata findings; no audit replaced.')
        if file_hash(args.bank) != bank_sha:
            raise SystemExit('STOP: bank changed during reconciliation; no audit replaced.')
        if AUDIT.is_file():
            old_raw = AUDIT.read_bytes()
            old = json.loads(old_raw)
            if old.get('audit_id') == audit['audit_id'] and old.get('bankSnapshotSha256') == bank_sha:
                audit['history'] = old['history']
            else:
                old_sha = hashlib.sha256(old_raw).hexdigest()
                archive = HERE / ('history/coverage_challenge-' + old_sha + '.json')
                atomic_write(archive, old_raw)
                audit['history'].update(supersedes=archive.relative_to(ROOT).as_posix(), sha256=old_sha)
        atomic_write(receipt_path, receipt_raw)
        atomic_write(AUDIT, encoded(audit))
        summary['writesPerformed'] = True
        summary['auditSha256'] = file_hash(AUDIT)
        summary['detailedReceipt'] = audit['detailedReceipt']
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
