"""Freeze the L29 repair review; never rerun over changed author objects."""
from pathlib import Path
import copy, datetime, hashlib, json, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import question_hash, schema_errors, validate_bank

def read(path): return json.loads((ROOT / path).read_text())
def sha(path): return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
def write(path, value): (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
ap = 'audits/blind-answers-W06-L29-v2-contracts-reviewer.json'
e = read(ap)
assert sha(ap) == '0357a8786fb8f1a716e5ec6ccaa4ca9edeaddf0a0d7174ba7f0858ce46da7e56'
m = read('audits/W06-L29-v2-repair-manifest.json')
r = read('audits/W06-L29-v2-contracts-keyed-reveal.json')
b = read(r['snapshotPath'])
qs = {q['id']: q for q in b['questions']}
hm = {q['questionId']: q for q in m['questions']}
assert e['frozenAt'] < r['revealedAt']
assert sha(ap) == r['answersSha256']
assert sha(e['blindPacketPath']) == e['blindPacketSha256'] == m['blindPacketSha256']
assert e['blindPacketSha256'] == 'c1d7dd4ff907aa950dcc7b13ac8f0c1c81efdafc7689f909a2d7aa51dc1a7670'
assert sha(r['snapshotPath']) == sha('data/question-batches/W06-L29.json') == r['snapshotSha256']
assert e['priorVersionExposure'] and len(hm) == 25 and len(m['preservedQuestionHashes']) == 51
assert all(question_hash(qs[qid]) == value for qid, value in m['preservedQuestionHashes'].items())
c = read(e['independentCheckPath'])
assert sha(e['independentCheckPath']) == e['independentCheckSha256']
assert c['assertionCount'] == 16 and c['randomWeightedCases'] == 500
obs = {o['physicalPage']: o for o in e['sourceObservations']}
assert len(obs) == 18
for o in obs.values(): assert sha(o['previewPath']) == o['previewSha256']
flags = {'W06-L29-Q059': [('sourceSupport', 'The repaired question now explicitly tests per-tree bootstrap sampling with replacement, but cites only page 882, which discusses feature count and remaining randomness. Add page 876, where the training-row sampling procedure and replacement are actually shown. The current key and rationale are correct; the required row-sampling premise lacks its exact source locator.') ]}
closures = {
11: 'The depicted unequal leaf depths are correctly distinguished from full binary branching and perfect balance.',
17: 'The concrete depth-limit scenario now tests why a mixed-label leaf can remain. Alternatives distinguish overriding a hard limit, rewriting targets, and miscounting added depth; the rationale corrects each.',
20: 'Deployment choices no longer use obviously unrelated outputs; interpretability and offline evidence remain distinct from validated operational safety.',
27: 'Direct timing recall is labeled easy and pre-pruning is distinguished from post-pruning without silently correcting the source API claim.',
28: 'The dated, explicit official API qualification supports ccp_alpha. Reduced-error pruning is not conflated with minimal cost-complexity pruning.',
31: 'Direct stratification identification is labeled easy; the explanation does not claim equal split sizes or fitting on held-out rows.',
32: 'The depth-bound lookup is labeled easy. Independent execution produces depth 2 under max_depth=3, confirming upper bound rather than equality.',
41: 'Alternatives now compare actual data perturbations and model stability rather than nonexistent estimator capabilities.',
42: 'Ensemble diversity and variance are distinguished from copying one fitted tree or chaining trees as a different algorithm.',
47: 'Feature selection timing is correctly labeled easy and is per node rather than once for the whole forest or once per tree.',
55: 'Page 871 now supports the X_tr/y_tr comparison with page 880. Undefined names, aliases, training targets and held-out arrays are correctly distinguished.',
56: 'Both the earlier three-class example and the later binary panels are cited; visual similarity is not represented as proof of dataset identity.',
58: 'Additional trees are distinguished from additional depth, changed sample count or guaranteed monotonic test-score improvement.',
59: 'The distractor repair correctly separates row bootstrapping from feature selection, fixed-seed reproducibility and tie-breaking. Exact page support remains incomplete.',
61: 'The official parameter semantics are explicitly supplied and independently checked. sqrt(9)=3 and the floating fraction 1.0 gives 9 nominal features, with the valid-split search caveat retained.',
63: 'Scaling invariance does not excuse inconsistent columns, unsupported categorical encoding or wrong input dimensions; option explanations preserve these distinctions.',
64: 'Resource comparisons are scoped to actual fitted model sizes and requirements rather than a universal ordering.',
66: 'The options now distinguish supplied synthetic results, lists of applications, and evidence for a universal benchmark claim. The source overstatement remains visibly qualified.',
67: 'Operational constraints and evaluation evidence, not model names alone, guide the explicitly stated model-choice scenario.',
71: 'The replacement closes the fall-distribution/block-boundary trace: zero-based rows 150 and 300 start labels 1 and 2; means [4,150] and [4,-150], scales [2,30]. Seeded draws are not their means.',
72: 'Replacing one terminal node by two changes the count from 4 to 5. The leaf cap can block a split even if the depth cap permits it; the competing counts are explained.',
73: 'The source nonincrease rule accepts 3-to-3 and rejects 3-to-4, with the candidates evaluated separately. It is not presented as the ccp_alpha objective.',
74: 'The explicitly supplied weighted criterion gives 3.2 versus 2.0. Every alternative is independently computed or identified as ignoring weights/purity of the other child; formula variables and units are defined.',
75: 'Both strictness and the oblique intersection are checked: only (3,1) satisfies both tests. The region need not be bounded.',
76: 'Changing the split seed can change allocation without changing already generated arrays, distribution parameters or class labels. Independent execution checks both stages separately.'
}
reviews = []
for a in e['independentAnswers']:
    q = qs[a['questionId']]
    assert q['version'] == a['questionVersion'] == hm[q['id']]['questionVersion']
    assert question_hash(q) == a['questionSha256'] == hm[q['id']]['questionSha256']
    assert q['correctOptionIds'] == a['independentAnswerOptionIds']
    assert e['reviewerId'] not in {q['authorId'], *q.get('revisionAuthors', [])}
    assert a['currentVersionSolvedBeforeKeyedAccess'] and not a['solvedBeforeAnswerSeen']
    pages = sorted({x['physicalPage'] for x in q['citations']} | ({876} if q['id'] in flags else set()))
    checks = {k: True for k in ['sourceSupport', 'assumptions', 'answerSet', 'distractors', 'calculations', 'figureFidelity', 'explanation', 'difficulty', 'duplication']}
    for criterion, _ in flags.get(q['id'], []): checks[criterion] = False
    explanation = a['reasoning'] + ' ' + closures[int(q['id'][-3:])] + ' Eighteen relevant actual source pages were freshly inspected and reconciled with extracted text. Current answers, 16 independent assertions and 500 two-check weighted-error trials were frozen before opening this version’s keys and solutions. Prior v1 exposure is disclosed; this is not represented as wholly blind. All nine criteria, complete option rationales, steps, formula metadata, source assumptions and cross-question overlap were assessed. '
    explanation += 'The exact current object remains blocked only by the finding below.' if q['id'] in flags else 'All nine item-level criteria pass for this exact object.'
    rv = dict(id=q['id'] + f'-v{q["version"]}-contracts-independent-repair-quality', questionId=q['id'], questionVersion=q['version'], questionSha256=question_hash(q), reviewerId=e['reviewerId'], decision='flagged' if q['id'] in flags else 'verified', reviewedAt=now, sourceVersions=e['sourceVersions'], reviewedSlideIds=[f'lectures-p{p:04}' for p in pages], independentAnswerOptionIds=a['independentAnswerOptionIds'], solvedBeforeAnswerSeen=False, checks=checks, reasoning=explanation, findings=[msg for _, msg in flags.get(q['id'], [])], blindAnswersPath=ap, blindAnswersSha256=sha(ap), independentSolvedAt=e['frozenAt'], priorAuthorExposure=True, priorItemKeyExposure=a['priorItemKeyExposure'], currentVersionSolvedBeforeKeyedAccess=True, sourceAnswerExposure=e['exposureDisclosure'], computationsPath=e['independentCheckPath'], externalEvidence=e['externalEvidence'], sourceInspectionEvidence=[dict(inspectorId=e['reviewerId'], **{k: obs[p][k] for k in ['physicalPage', 'previewPath', 'previewSha256', 'dimensions', 'inspectedAt']}) for p in pages])
    assert not schema_errors(rv, read('data/schema.review.json'))
    reviews.append(rv)
assert len(reviews) == 25
out = 'data/reviews/W06-L29-v2-independent-contracts.json'
write(out, reviews)
old = [rv for rv in read('data/reviews/W06-L29-v1-independent-contracts.json') if rv['decision'] == 'verified' and rv['questionId'] in m['preservedQuestionHashes'] and rv['questionSha256'] == question_hash(qs[rv['questionId']])]
assert len(old) == 51
allr = old + reviews
rb = {rv['questionId']: rv for rv in allr}
assert len(rb) == 76
qq, cs = copy.deepcopy(b['questions']), copy.deepcopy(b['concepts'])
for q in qq:
    q['status'] = rb[q['id']]['decision']
    q['reviewIds'] = [rb[q['id']]['id']]
verified = {q['id'] for q in qq if q['status'] == 'verified'}
for co in cs: co['status'] = 'verified' if any(qid in verified for qid in co['questionIds']) else 'drafted'
sm = read('sources/manifest.json')
slides = [json.loads(line) for sid in ['lectures', 'assignments'] for line in (ROOT / f'sources/page_maps/{sid}.jsonl').read_text().splitlines()]
updates = {v['id']: v for v in read('data/inspection-batches/W06-L29.json')['slides']}
slides = [copy.deepcopy(updates.get(v['id'], v)) for v in slides]
for sl in slides:
    if sl['id'] in updates: sl['conceptIds'] = [co['id'] for co in cs if sl['id'] in co['slideIds']]
tmp = {'schemaVersion': '1.0.0', 'bankVersion': 'L29-v2-contracts-isolated', 'title': 'L29 independent repair validation', 'complete': False, 'sources': sm['sources'], 'assets': sm['assets'], 'slides': slides, 'questions': qq, 'concepts': cs, 'reviews': allr, 'learningTools': {k: [] for k in ['formulaSheet', 'confusionPairs', 'traps', 'algorithmVisualizations', 'numericalFamilies']}}
v = validate_bank(tmp, ROOT, check_files=True)
assert v['valid'], v
history = read('audits/W06-L29-contracts-coverage-challenge.json')
links = {'L29-GAP-870-leaf-cap': [72], 'L29-GAP-870-reduced-error': [73], 'L29-GAP-862-865-split-objective': [74], 'L29-GAP-862-864-multivariate-region': [75], 'L29-GAP-868-full-generation-trace': [71, 76]}
gaps = []
for gap in history['gaps']:
    item = copy.deepcopy(gap)
    item['status'] = 'closed-for-bounded-lecture-challenge'
    item['closingQuestionIds'] = [f'W06-L29-Q{x:03}' for x in links[gap['id']]]
    assert all(qid in verified for qid in item['closingQuestionIds'])
    item['closureEvidence'] = [closures[x] for x in links[gap['id']]]
    gaps.append(item)
coverage = dict(completedAt=now, reviewerId=e['reviewerId'], status='five-bounded-gaps-closed-one-item-citation-residual', historicalFullSourceChallengePath='audits/W06-L29-contracts-coverage-challenge.json', historicalFullSourceAnswerPath=e['historicalFullSourceReview'], historicalActualPagesInspected=31, currentActualPagesReinspected=sorted(obs), currentAnswerEvidencePath=ap, currentReviewPath=out, gaps=gaps, currentSubstantivePageCitationCount=26, sourceQualifications='The original source issues remain qualified, not globally resolved; current official API references are explicit for Q028 and Q061.', scope='All five previously identified, bounded source-concept gaps now have independently verified current items. This closes those findings, not the entire course or every conceivable question angle. Q059 remains blocked for exact citation completeness. Prior full-page coverage evidence is preserved rather than relabeled as a fresh 31-page inspection.', difficultyCounts={d: sum(q['difficulty'] == d for q in b['questions']) for d in ['easy', 'medium', 'hard', 'extremely-tricky']}, selectionModes={'single': 76, 'multiple': 0}, remainingCourseLevelEnrichment='This lecture still has no hard or multiple-select items. Genuine harder and varied-format synthesis remains a course-level enrichment need; do not inflate difficulty labels.', answerPresentation=history['answerPresentation'])
write('audits/W06-L29-v2-contracts-coverage-challenge.json', coverage)
su = dict(completedAt=now, reviewerId=e['reviewerId'], reviewed=25, revisedObjects=20, newGapObjects=5, verified=24, flagged=1, keyDisagreements=0, preservedAcceptedHashes=51, totalCurrentVerified=len(verified), totalCurrentQuestions=76, actualPagesReinspected=18, historicalActualPagesInspected=31, priorVersionExposure=True, independentAssertions=16, randomTrials=500, checksPerTrial=2, reviewFile=out, reviewSha256=sha(out), blindAnswersSha256=sha(ap), validation=v, flaggedQuestionIds=list(flags), findings=[{'questionId': qid, 'criteria': [k for k, _ in fs], 'findings': [msg for _, msg in fs]} for qid, fs in flags.items()], boundedCoverageGapsClosed=5, coverageChallengePath='audits/W06-L29-v2-contracts-coverage-challenge.json', sourceQualificationsPreserved=True, mutations='Reviewer evidence, snapshot, check/finalizer scripts, reviews, summary, bounded coverage record and handoff only. No author questions, canonical bank, sources or Git edits.')
write('audits/W06-L29-v2-contracts-review-summary.json', su)
(ROOT / 'docs/handoffs/L29-v2-contracts-review.md').write_text(f'''# L29 v2 independent review frozen

24 of 25 changed/new objects verified; Q059 remains flagged only for its missing page 876 bootstrap-sampling citation. All 25 intended keys agree. All 51 previously accepted hashes remain exact, so 75 of 76 current questions have matching accepted reviews. The five bounded coverage gaps are closed by Q071–Q076, not treated as complete-course certification.

Eighteen relevant actual source pages were freshly inspected. Current source-derived answers, 16 independent assertions and 500 two-check weighted-error trials were frozen before current keyed access. Prior v1 exposure is disclosed; solvedBeforeAnswerSeen is conservatively false for all 25, including five new items for which there was no prior item-key exposure. Historical full 31-page review evidence is preserved separately.

Review: {out}
Review SHA256: {sha(out)}
Blind answer SHA256: {sha(ap)}
Summary: audits/W06-L29-v2-contracts-review-summary.json
Coverage: audits/W06-L29-v2-contracts-coverage-challenge.json
Independent checks: audits/W06-L29-v2-contracts-independent-checks.json

The weighted split scores are 3.2 versus 2.0; the leaf cap rejects 4−1+2=5 leaves; reduced-error pruning permits equality; only (3,1) satisfies the two oblique tests; seeded row draws differ from their distribution means; changing only the split seed does not regenerate X,y. Official ccp_alpha and max_features semantics were independently checked and source conflicts remain visible. All 76 current questions are single-select; the recorded difficulty inventory is an observation, not a claim of universal difficulty coverage.

No author, bank, source or Git edits. Do not rerun the finalizer after author revisions or overwrite frozen answer evidence. Only the lead may assign repairs; another current-version review is needed after Q059 changes.
''')
print(json.dumps({'verified': 24, 'flagged': 1, 'currentVerified': len(verified), 'reviewSha256': sha(out), 'validation': v}, indent=2))
