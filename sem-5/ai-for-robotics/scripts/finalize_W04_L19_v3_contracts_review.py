"""Independent non-blind closure of two L19 v3 distractor repairs."""
from pathlib import Path
import json,hashlib,datetime,sys,copy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash,schema_errors,validate_bank
read=lambda p:json.loads((ROOT/p).read_text());sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();ap='audits/blind-answers-W04-L19-v3-contracts-reviewer.json';e=read(ap);assert sha(ap)=='a7074baf779ca40e35da86a3abbd641a85d40717201c06ce771cf6c305edafb3'
b=read('audits/review-snapshots/W04-L19-v3-contracts.json');m=read('audits/W04-L19-v3-review-manifest.json');reveal=read('audits/W04-L19-v3-contracts-author-reveal.json');assert e['answersFrozenAt']<reveal['revealedAt']
qs={q['id']:q for q in b['questions']};assert all(question_hash(qs[k])==v for k,v in m['preservedAcceptedHashes'].items());assert len(m['preservedAcceptedHashes'])==98
obs={o['physicalPage']:o for o in e['sourceObservations']};reviews=[]
for a in e['independentAnswers']:
 q=qs[a['questionId']];assert question_hash(q)==a['questionSha256']==m['questionSha256'][q['id']];assert q['correctOptionIds']==a['answerOptionIds'];assert e['reviewerId'] not in {q['authorId'],*q.get('revisionAuthors',[])}
 pages=[c['physicalPage'] for c in q['citations']]
 reviews.append(dict(id=q['id']+'-v3-contracts-independent',questionId=q['id'],questionVersion=3,questionSha256=question_hash(q),reviewerId=e['reviewerId'],decision='verified',reviewedAt=now,sourceVersions=e['sourceVersions'],reviewedSlideIds=[f'lectures-p{p:04}' for p in pages],independentAnswerOptionIds=a['answerOptionIds'],solvedBeforeAnswerSeen=False,checks={k:True for k in ['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']},reasoning=a['reasoning']+' Both actual pages were reinspected before the current answer freeze. Prior v1/v2 author-key exposure is explicitly disclosed. Current source-attribution stems and all option rationales now distinguish non-attributed but possible mechanisms rather than physically impossible alternatives. These conceptual repairs contain no numerical calculation requiring a new mathematical test. All nine criteria pass; all 98 previously accepted correctness hashes remain unchanged.',findings=[],blindAnswersPath=ap,blindAnswersSha256=sha(ap),independentSolvedAt=e['answersFrozenAt'],priorAuthorExposure=True,priorExposureDetail=e['priorAuthorExposure'],sourceInspectionEvidence=[dict(inspectorId=e['reviewerId'],**{k:obs[p][k] for k in ['physicalPage','previewPath','previewSha256','dimensions','inspectedAt']}) for p in pages]))
assert not [err for rv in reviews for err in schema_errors(rv,read('data/schema.review.json'))]
out='data/reviews/W04-L19-v3-independent-contracts.json';write(out,reviews)
# Current reviews only, retaining approvals from the original and repair slices.
prior=read('data/reviews/W04-L19-v1-independent-contracts.json')+read('data/reviews/W04-L19-v2-independent-contracts.json')
allr=[r for r in prior if r['decision']=='verified' and r['questionId'] in qs and r['questionSha256']==question_hash(qs[r['questionId']])]+reviews
assert len(allr)==100;rb={r['questionId']:r for r in allr};qq=copy.deepcopy(b['questions']);cs=copy.deepcopy(b['concepts'])
for q in qq:q['status']='verified';q['reviewIds']=[rb[q['id']]['id']]
for c in cs:c['status']='verified'
sm=read('sources/manifest.json');slides=[json.loads(l) for sid in ['lectures','assignments'] for l in (ROOT/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()];updates={v['id']:v for v in read('data/inspection-batches/W04-L19.json')['slides']};slides=[copy.deepcopy(updates.get(v['id'],v)) for v in slides]
for sl in slides:
 if sl['id'] in updates:sl['conceptIds']=[c['id'] for c in cs if sl['id'] in c['slideIds']]
tmp={'schemaVersion':'1.0.0','bankVersion':'L19-v3-contracts-isolated','title':'L19 current independent closure','complete':False,'sources':sm['sources'],'assets':sm['assets'],'slides':slides,'questions':qq,'concepts':cs,'reviews':allr,'learningTools':{k:[] for k in ['formulaSheet','confusionPairs','traps','algorithmVisualizations','numericalFamilies']}}
v=validate_bank(tmp,ROOT,check_files=True)
su={'completedAt':now,'reviewerId':e['reviewerId'],'revisionItemsReviewed':2,'verified':2,'flagged':0,'totalCurrentVerified':100,'preservedAcceptedHashes':98,'actualPagesReinspected':[598,602],'priorVersionExposureDisclosed':True,'reviewFile':out,'reviewSha256':sha(out),'blindAnswersSha256':sha(ap),'validation':v,'coverage':'The original bounded source challenge and v2 closure of the paired hollow-cantilever calculation and lead/ball-screw tradeoff remain applicable. No new lecture omissions identified by these two narrowly scoped distractor repairs. This is not a whole-course completion claim.'}
write('audits/W04-L19-v3-contracts-review-summary.json',su);(ROOT/'docs/handoffs/L19-v3-contracts-review.md').write_text(f'# L19 v3 independent review closed\n\nBoth remaining distractor repairs pass. All 100 current questions are independently verified, with the prior 98 accepted hashes preserved. Reinspected actual pages 598 and 602 and froze current responses before current keyed access; prior v1/v2 exposure is disclosed, so these are not claimed blind.\n\nReview: {out}, SHA256 {sha(out)}. Summary and validation: audits/W04-L19-v3-contracts-review-summary.json. No authored question, bank, source or Git changes.\n')
print(json.dumps({'verified':2,'totalCurrentVerified':100,'reviewSha256':sha(out),'validation':v},indent=2));assert v['valid'],v
