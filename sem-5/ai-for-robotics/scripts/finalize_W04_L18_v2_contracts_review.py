"""Independent repair/gap gate: prior exposure is disclosed, not re-labelled blind."""
from pathlib import Path
import copy,datetime,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash,schema_errors,validate_bank
read=lambda p:json.loads((ROOT/p).read_text())
sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();R='define_robotics_data_contracts:L18-independent-reviewer'
ap='audits/blind-answers-W04-L18-v2-and-gaps-contracts-reviewer.json';assert sha(ap)=='3040c46ed12edaaaf3b24c5811abe50d4499c1fe7a2400d90dde177fcffabc67'
e=read(ap);m=read('audits/W04-L18-v2-repair-manifest.json');rv=read('audits/W04-L18-v2-contracts-author-reveal.json')
assert e['answersFrozenAt']<rv['revealedAt'];assert sha(rv['snapshotPath'])==rv['batchSha256'];assert sha(e['blindPacketPath'])==e['blindPacketSha256']==m['blindPacketSha256']
b=read(rv['snapshotPath']);old=read('audits/review-snapshots/W04-L18-v1-contracts.json');oldqs={q['id']:q for q in old['questions']};qs={q['id']:q for q in b['questions']};answers={a['questionId']:a for a in e['independentAnswers']};hashes={x['questionId']:x['questionSha256'] for x in m['questions']}
prior=read('data/reviews/W04-L18-v1-independent-contracts.json');accepted=[r for r in prior if r['decision']=='verified'];assert len(accepted)==67
assert {r['questionId'] for r in accepted}==set(m['preservedAcceptedQuestionHashes'])
for r in accepted:
    q=qs[r['questionId']];assert question_hash(q)==question_hash(oldqs[q['id']])==r['questionSha256']==m['preservedAcceptedQuestionHashes'][q['id']]
observations={o['physicalPage']:o for o in e['sourceObservations']};observations.update({o['physicalPage']:o for o in e['sourceReinspections']})
for o in observations.values():assert sha(o['previewPath'])==o['previewSha256']
repair_explanation={
'Q005':'Alternatives now test loop-constraint counting and actuator-versus-mobility mistakes rather than actuator power or automatic doubling.',
'Q008':'The direct task-relative redundancy recognition is now labelled easy.',
'Q011':'The complete load-factor lists remain correct and the simple multi-select recognition is now easy.',
'Q018':'The source-listed geometric simplifications are correctly retained and difficulty is now easy.',
'Q033':'The former duplicated equal-link distractor was replaced by one link length, distinct from the two-link maximum. Its rationale now explains cancellation.',
'Q051':'The alternatives now distinguish configuration dimension, instantaneous task rank and global finite reachability. Difficulty is corrected to easy.',
'Q055':'The replacement distractors test exactly-one rank deficit and dependent redundant columns, with correct Gram-matrix explanations.',
'Q057':'Ordinary inverse prerequisite recognition is now easy, while square/non-singular and coordinate assumptions remain explicit.',
'Q064':'The cross-term alternatives now represent omitted factor two, reversed sign and absolute-versus-relative angle errors. All four rationales match their actual formulas.',
'Q066':'The working names each coordinate target explicitly, making the radius-to-target mapping correct and safe under option shuffling.',
'Q070':'Literal string parsing is correctly separated from the intended repaired plot code, and difficulty is now easy.',
'Q071':'The nested-loop Cartesian-product count is now easy and distinguishes aligned scalar lists from unique Cartesian points.',
'Q076':'The new alternatives accurately encode 200-versus-199 interval counting and full-versus-half grid spacing. Independent evaluation reproduces 8.999723083556866.',
'Q077':'Doubling both loop dimensions is now easy; evaluation and storage counts remain correctly quadrupled.',
'Q082':'The alternatives now distinguish unneeded axial roll, constrained tool-axis direction and a missing orienting wrist. The three-motion positioner scope is explicit.',
'Q083':'The stem no longer supplies a determinant as a premise; it asks for a complete derivative matrix with fixed row/column and angle conventions. All four derivatives and the cancelling determinant terms are shown. The plausible fourth alternative correctly illustrates that a matching determinant does not validate an incorrect full matrix. Medium difficulty is appropriate.',
'Q084':'The new scenario applies iterative coupled mechanical/actuation/sensing refinement to both an inertia/cycle-time problem and a precision/sensing problem. It closes the identified page548 design-process angle rather than repeating the task-domain comparison.',
'Q085':'The new combined match correctly uses jointed/elbow/anthropomorphic and the exact source-specific Assembly expansion. The answer o4 was frozen from actual page560 pixels before keyed access. Other literature usage is not denied.'}
reviews=[]
for qid,a in answers.items():
    q=qs[qid];assert question_hash(q)==a['questionSha256']==hashes[qid];assert set(q['correctOptionIds'])==set(a['answerOptionIds']);assert R not in {q['authorId'],*q.get('revisionAuthors',[])}
    fresh=q['version']==1;pages=sorted({c['physicalPage'] for c in q['citations']});detail=repair_explanation[qid.rsplit('-',1)[1]].replace('page548','page 548').replace('page560','page 560')
    reasoning=a['reasoning']+' '+detail+' All nine quality criteria were checked against the exact current object, including every option rationale and relevant formula variables, units and assumptions. Thirty new reviewer-owned symbolic/numerical/code assertions passed before current keyed access; the original 42 checks and 1,000 random identities remain preserved. '+('This is a first-exposure blind review of a new gap question, with source content visible but no proposed key or solution seen before its response was frozen.' if fresh else 'I previously reviewed the v1 question and saw its author solution. This repair review therefore records solvedBeforeAnswerSeen=false, despite freezing the current-version response before opening the new keyed object. It is not represented as a fresh blind review.')
    reviews.append(dict(id=qid+f'-v{q["version"]}-contracts-independent',questionId=qid,questionVersion=q['version'],questionSha256=question_hash(q),reviewerId=R,decision='verified',reviewedAt=now,sourceVersions=e['sourceVersions'],reviewedSlideIds=[f'lectures-p{p:04}' for p in pages],independentAnswerOptionIds=a['answerOptionIds'],solvedBeforeAnswerSeen=fresh,checks={k:True for k in ['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']},reasoning=reasoning,findings=[],blindAnswersPath=ap,blindAnswersSha256=sha(ap),independentSolvedAt=e['answersFrozenAt'],priorAuthorExposure=not fresh,exposureDisclosure='No prior question-author exposure.' if fresh else 'Prior v1 key and solution were inspected during the completed first review; current answers were frozen before current-version keyed access.',computationsPath='audits/W04-L18-v2-independent-checks.json',sourceInspectionEvidence=[dict(inspectorId=R,**{k:observations[p][k] for k in ['physicalPage','previewPath','previewSha256','dimensions','inspectedAt']}) for p in pages]))
assert len(reviews)==18 and sum(r['solvedBeforeAnswerSeen'] for r in reviews)==2
errors=[er for r in reviews for er in schema_errors(r,read('data/schema.review.json'))];assert not errors,errors
out='data/reviews/W04-L18-v2-and-gaps-independent-contracts.json';write(out,reviews)
allreviews=accepted+reviews;rb={r['questionId']:r for r in allreviews};current=copy.deepcopy(b['questions']);cs=copy.deepcopy(b['concepts'])
for q in current:q['status']='verified';q['reviewIds']=[rb[q['id']]['id']]
for c in cs:c['status']='verified' if c['questionIds'] else 'drafted'
sm=read('sources/manifest.json');slides=[json.loads(line) for sid in ['lectures','assignments'] for line in (ROOT/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()];updates={v['id']:v for v in read('data/inspection-batches/W04-L18.json')['slides']};slides=[copy.deepcopy(updates.get(v['id'],v)) for v in slides]
for slide in slides:
    if slide['id'] in updates:slide['conceptIds']=[c['id'] for c in cs if slide['id'] in c['slideIds']]
tmp={'schemaVersion':'1.0.0','bankVersion':'L18-v2-repair-gap-independent-isolated','title':'L18 repair and gap review validation','complete':False,'sources':sm['sources'],'assets':sm['assets'],'slides':slides,'questions':current,'concepts':cs,'reviews':allreviews,'learningTools':{k:[] for k in ['formulaSheet','confusionPairs','traps','algorithmVisualizations','numericalFamilies']}}
v=validate_bank(tmp,ROOT,check_files=True)
summary={'reviewerId':R,'completedAt':now,'currentSliceReviewed':18,'repairsAccepted':16,'newGapsAccepted':2,'flagged':0,'keyDisagreements':0,'previousAcceptedHashesPreserved':67,'currentLectureVerified':85,'priorActualPagesInspected':34,'currentActualPageReinspections':7,'newIndependentAssertions':30,'reviewFile':out,'reviewSha256':sha(out),'answerEvidencePath':ap,'answerEvidenceSha256':sha(ap),'exposure':'Sixteen nonblind re-reviews with prior-v1 disclosure; two fresh blind gap reviews. All current-version answers frozen before current keyed access.','coverageChallenge':[{'id':'L18-COVERAGE-01','status':'closed_by_verified_question','questionId':'W04-L18-Q084','version':1},{'id':'L18-COVERAGE-02','status':'closed_by_verified_question','questionId':'W04-L18-Q085','version':1},{'id':'L18-COVERAGE-03','status':'closed_by_verified_repair','questionId':'W04-L18-Q083','version':2}],'validation':v,'sourceCaveats':'All prior source qualifications remain. This closes the identified L18 findings, not the full-course coverage claim.','mutations':'Reviewer evidence, check scripts, reviews and handoff only. No question, bank, source or Git edits.'}
write('audits/W04-L18-v2-contracts-review-summary.json',summary)
(ROOT/'docs/handoffs/L18-v2-contracts-review.md').write_text(f'# L18 repair and gap review frozen\n\nAll 16 repairs and both new gaps pass: 18 verified, no flags or key disagreements. All 67 previously accepted correctness hashes match the original review snapshot, so the current L18 batch has 85 verified questions. Thirty new independent assertions passed, and seven relevant actual source pages were reinspected. The prior 34-page observations and computations are preserved.\n\nReview: {out}, SHA256 {sha(out)}. Summary and isolated validation: audits/W04-L18-v2-contracts-review-summary.json. Answer freeze: {ap}. Sixteen repairs explicitly disclose prior v1 key exposure; only the two new gap items are recorded as first-exposure blind.\n\nThe three identified coverage findings are closed by Q084 iterative design, Q085 exact terminology, and Q083 v2 full Jacobian/determinant derivation. The source-specific SCARA expansion is Assembly, correctly keyed as Q085 option o4. No global source uncertainty or complete-course coverage is claimed.\n\nNo author objects, bank, sources or Git changed. Next parent-assigned review is L21 when its frozen answer-free packet is ready.\n')
print(json.dumps({k:summary[k] for k in ['repairsAccepted','newGapsAccepted','previousAcceptedHashesPreserved','currentLectureVerified','reviewSha256','validation']},indent=2));assert v['valid'],v
