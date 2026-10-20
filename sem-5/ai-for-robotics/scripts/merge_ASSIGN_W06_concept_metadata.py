"""One-shot concept-only integration repair; never rewrite accepted questions."""
import copy
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
BASE = 'data/question-batches/ASSIGN-W06.json'
SUP = 'data/question-batches/ASSIGN-W06-tree-boundaries.json'
REPORT = 'audits/assignment-coverage/ASSIGN-W06-concept-integration-repair.json'
HISTORY = ROOT / 'data/history/ASSIGN-W06/concept-integration'
CID = 'ASSIGN-W06-C008'

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def whole_hash(value):
    return digest(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())

def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()

assert not (ROOT / REPORT).exists(), 'Frozen repair already exists; do not rerun.'
assert not HISTORY.exists(), 'Prior snapshot exists; inspect uncertain outcome before retry.'
raw = {p: (ROOT / p).read_bytes() for p in (BASE, SUP)}
before = {p: json.loads(v) for p, v in raw.items()}
after = copy.deepcopy(before)
base_concept = next(c for c in after[BASE]['concepts'] if c['id'] == CID)
sup_concept = next(c for c in after[SUP]['concepts'] if c['id'] == CID)
assert len(after[SUP]['concepts']) == 1
for field in ('questionIds', 'examinationAngles'):
    base_concept[field] = sorted(set(base_concept.get(field, [])) | set(sup_concept.get(field, [])))
base_concept['coverageNotes'] = ('The independently accepted additional boundary/branch item closes root equality, '
    'root-true short-circuiting, reached-second equality and rightmost-leaf averaging. '
    'The existing interior-path question and all accepted question objects are unchanged. '
    'Acceptance is recorded in audits/assignment-coverage/ASSIGN-W06-tree-boundaries-independent-review-summary.json.')
after[SUP]['concepts'] = []

# No question, source, packet, review, or bank changes are authorized here.
questions_before = {q['id']: whole_hash(q) for p in before for q in before[p]['questions']}
questions_after = {q['id']: whole_hash(q) for p in after for q in after[p]['questions']}
assert len(questions_before) == 11 and questions_before == questions_after
for p in before:
    assert before[p]['questions'] == after[p]['questions']
    assert {k: v for k, v in before[p].items() if k != 'concepts'} == {k: v for k, v in after[p].items() if k != 'concepts'}
for old, new in zip(before[BASE]['concepts'], after[BASE]['concepts']):
    if old['id'] != CID:
        assert old == new
    else:
        assert {k: v for k, v in old.items() if k not in ('questionIds', 'examinationAngles', 'coverageNotes')} == {k: v for k, v in new.items() if k not in ('questionIds', 'examinationAngles', 'coverageNotes')}
questions = {q['id']: q for p in after for q in after[p]['questions']}
concepts = [c for p in after for c in after[p]['concepts']]
assert len(concepts) == len({c['id'] for c in concepts}) == 10
concept_map = {c['id']: c for c in concepts}
for q in questions.values():
    for cid in q['conceptIds']:
        assert q['id'] in concept_map[cid]['questionIds']
for c in concepts:
    for qid in c['questionIds']:
        assert c['id'] in questions[qid]['conceptIds']
assert base_concept['questionIds'] == ['ASSIGN-W06-Q008', 'ASSIGN-W06-Q011']
source_paths = {q['originalRecordPath'] for q in questions.values()}
protected = source_paths | {
    'data/bank.json',
    'audits/blind-ASSIGN-W06-tree-boundaries.json',
    'audits/blind-binding-ASSIGN-W06-tree-boundaries.json',
    'data/reviews/ASSIGN-W06-tree-boundaries-independent-recovery.json',
    'audits/assignment-coverage/ASSIGN-W06-tree-boundaries-independent-review-summary.json',
}
protected_hashes = {p: digest((ROOT / p).read_bytes()) for p in sorted(protected)}
for q in questions.values():
    assert protected_hashes[q['originalRecordPath']] == q['originalRecordSha256']
HISTORY.mkdir(parents=True)
for p in raw:
    (HISTORY / Path(p).name).write_bytes(raw[p])
# Verify the inspected inputs still match before the two small atomic replacements.
for p in raw:
    assert (ROOT / p).read_bytes() == raw[p], 'Concurrent batch edit; stop.'
for p in after:
    dest = ROOT / p
    staging = dest.with_name(dest.name + '.concept-merge-staging')
    assert not staging.exists()
    staging.write_bytes(encode(after[p]))
    os.replace(staging, dest)
for p, h in protected_hashes.items():
    assert digest((ROOT / p).read_bytes()) == h, p
for p in after:
    assert json.loads((ROOT / p).read_text()) == after[p]
report = {
    'checkedAt': datetime.now(timezone.utc).isoformat(),
    'role': 'Concept-only author integration repair, not a new content review or bank assembly',
    'conceptId': CID,
    'singleDeclarationPath': BASE,
    'removedDuplicateDeclarationPath': SUP,
    'mergedFields': ['questionIds', 'examinationAngles', 'coverageNotes'],
    'originalConceptStatusPreserved': base_concept['status'] == next(c for c in before[BASE]['concepts'] if c['id'] == CID)['status'],
    'uniqueConceptCount': len(concepts),
    'questionCount': len(questions),
    'wholeQuestionObjectHashesBeforeAndAfter': questions_after,
    'wholeQuestionObjectsUnchanged': True,
    'bidirectionalConceptLinksValid': True,
    'originalSourceRecordsAndReviewProvenanceUnchanged': True,
    'protectedFileHashes': protected_hashes,
    'batchSha256Before': {p: digest(v) for p, v in raw.items()},
    'batchSha256After': {p: digest((ROOT / p).read_bytes()) for p in after},
    'historyDirectory': str(HISTORY.relative_to(ROOT)),
    'canonicalBankWritten': False,
    'globalValidationClaimed': False,
}
(ROOT / REPORT).write_bytes(encode(report))
print(json.dumps({k: report[k] for k in ['conceptId', 'uniqueConceptCount', 'questionCount', 'wholeQuestionObjectsUnchanged', 'bidirectionalConceptLinksValid', 'originalSourceRecordsAndReviewProvenanceUnchanged', 'canonicalBankWritten']}))
print(REPORT)
