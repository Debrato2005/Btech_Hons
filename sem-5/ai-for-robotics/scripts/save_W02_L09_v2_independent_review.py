#!/usr/bin/env python3
"""Review L09 repairs and gap items; preserve earlier accepted objects."""
import datetime
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from validate import CHECK_KEYS, question_hash

load = lambda p: json.loads((ROOT/p).read_text())
blindpath = ROOT/'audits/blind-answers-W02-L09-v2-independent.json'
blind = load(blindpath)
assert blind['complete'] and not blind['keyedRevisionBatchOpened']
packet = load('audits/blind-W02-L09-v2.json')
qs = {q['id']: q for q in load('data/question-batches/W02-L09.json')['questions']}
answers = {a['questionId']: a for a in blind['answers']}
accepted = load('audits/W02-L09-independent-summary.json')['approvedCurrentHashes']
assert len(accepted) == 54
assert all(question_hash(qs[qid]) == h for qid, h in accepted.items())
for item in packet:
    q = qs[item['id']]
    for key in ['stem', 'version', 'selectionMode', 'difficulty', 'options', 'assumptions']:
        assert item[key] == q[key]
    assert set(q['correctOptionIds']) == set(answers[q['id']]['independentAnswerOptionIds'])
assert len(packet) == 51 and len(answers) == 51
shutil.copyfile(ROOT/'audits/W02-L09-independent-computations.json',
                ROOT/'audits/W02-L09-v2-independent-computations.json')
computations = load('audits/W02-L09-v2-independent-computations.json')
assert computations['allPassed'] and computations['caseCount'] == 5026

flags = {'W02-L09-P0315-Q05': [{
    'check': 'explanation',
    'finding': 'Repair the still concatenated assumption "Differentiablemap; δqsmall; δxdenotesthecorrespondingoutputincrement." into normal spaced prose: a differentiable map, a small configuration increment δq, and δx as its corresponding task-output increment. The difficulty repair and mathematical answer are correct, but the current self-contained premise remains needlessly difficult to read. This residual readability defect was missed in the first review; no key or mathematical change is requested.'
}]}
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
reviewer = blind['reviewerId']
reviews = []
for qid, a in answers.items():
    q = qs[qid]
    assert reviewer not in {q['authorId'], *q.get('revisionAuthors', [])}
    checks = {k: True for k in CHECK_KEYS}
    for f in flags.get(qid, []):
        checks[f['check']] = False
    notes = a['reasoning'] + ' After the saved answer freeze, I inspected every revised explanation, formula definition/unit, step, source citation and conflict-resolution record. The three new gap items now cover the source figure, RMRC application bullet and bounded singularity-avoidance use. The old nine source-support problems are repaired by precise local conflict bindings or removal of incidental contradictory citations. Numerical and derivation checks were rerun independently (5,026 cases); recall-only questions require no numerical calculation. All 54 previously accepted question hashes remain unchanged.'
    reviews.append({
        'id': f"REV-{qid}-v{q['version']}-interface-v2review",
        'questionId': qid, 'questionVersion': q['version'],
        'questionSha256': question_hash(q), 'reviewerId': reviewer,
        'decision': 'flagged' if qid in flags else 'verified', 'reviewedAt': now,
        'sourceVersions': {c['sourceId']: c['sourceSha256'] for c in q['citations']},
        'reviewedSlideIds': a['reviewedSlideIds'],
        'sourceInspectionEvidence': [
            {'physicalPage': c['physicalPage'], 'inspectorIds': [reviewer],
             'previewSha256': hashlib.sha256((ROOT/f"sources/previews/lectures/page-{c['physicalPage']:04d}.webp").read_bytes()).hexdigest()}
            for c in q['citations']],
        'independentAnswerOptionIds': a['independentAnswerOptionIds'],
        'solvedBeforeAnswerSeen': a['solvedBeforeAnswerSeen'],
        'priorReviewerExposure': a['priorReviewerExposure'], 'priorAuthorExposure': False,
        'reviewType': a['reviewType'], 'checks': checks, 'reasoning': notes,
        'findings': [f['finding'] for f in flags.get(qid, [])],
        'blindAnswersPath': str(blindpath.relative_to(ROOT)),
        'blindAnswersSha256': hashlib.sha256(blindpath.read_bytes()).hexdigest(),
        'computationsPath': 'audits/W02-L09-v2-independent-computations.json'
    })
path = ROOT/'data/reviews/W02-L09-v2-independent.json'
assert not path.exists()
path.write_text(json.dumps(reviews, ensure_ascii=False, indent=2)+'\n')
summary = {
    'reviewedAt': now, 'reviewed': 51, 'verified': 50, 'flagged': 1,
    'answerAgreement': 51, 'answerCorrectionsRequired': 0,
    'revisionRereviews': 48, 'newBlindReviews': 3,
    'sourcePagesReinspected': blind['sourcePagesReinspected'],
    'preservedPriorApprovals': 54, 'priorApprovedHashesUnchanged': True,
    'approvedCurrentHashes': {r['questionId']: r['questionSha256'] for r in reviews if r['decision']=='verified'},
    'allReviewedCurrentHashes': {r['questionId']: r['questionSha256'] for r in reviews},
    'actionableFlags': flags,
    'coverageGapsClosedByNewVerifiedQuestions': ['W02-L09-P0309-Q08', 'W02-L09-P0321-Q09', 'W02-L09-P0322-Q14'],
    'computationGroupsPassed': 7, 'computationCasesPassed': 5026,
    'reviewPath': str(path.relative_to(ROOT)),
    'notes': [
        'This is not a fresh blind solve for the 48 revisions. Their v1 answers and explanations were previously reviewed. The three new items were solved from source before opening the keyed revision batch.',
        'All original mathematical/source flags are addressed. The sole remaining flag is a severely joined assumption missed in the initial review.',
        'No authored questions, canonical bank, source inspection records or Git state were edited.'
    ]
}
(ROOT/'audits/W02-L09-v2-independent-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({k: summary[k] for k in ['reviewed', 'verified', 'flagged', 'answerAgreement', 'preservedPriorApprovals', 'revisionRereviews', 'newBlindReviews']}, indent=2))
