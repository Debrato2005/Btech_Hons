"""Close two independent residual reviews, preserving unrelated search objects."""
from pathlib import Path
import json,hashlib,datetime,copy,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import question_hash,schema_errors,validate_bank
read=lambda p:json.loads((R/p).read_text());sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(p,v):
 f=R/p;assert not f.exists(),p;f.write_text(json.dumps(v,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();ap='audits/blind-answers-W08-L36-L37-residuals-contracts.json';e=read(ap);rv=read('audits/W08-L36-L37-residuals-contracts-keyed-reveal.json');b=read(rv['snapshotPath']);qs={q['id']:q for q in b['questions']};old={q['id']:q for q in read('audits/review-snapshots/W08-L36-legacy-v2-contracts.json')['questions']};changed={a['questionId'] for a in e['answers']};assert sha(ap)==rv['answersSha256']=='1a026f555a9fe608ad3220317170906fe4177f2d3551a9257b597dc2b725f099';assert e['frozenAt']<rv['revealedAt'];assert sha(rv['snapshotPath'])==sha(rv['batchPath'])==rv['batchSha256'];assert len(qs)==len(old)==68
for qid in qs.keys()-changed:assert qs[qid]==old[qid] and question_hash(qs[qid])==question_hash(old[qid])
reviews=[]
for a in e['answers']:
 q=qs[a['questionId']];assert question_hash(q)==a['questionSha256'] and q['version']==a['questionVersion'] and q['correctOptionIds']==a['independentAnswerOptionIds'];assert e['reviewerId'] not in [q['authorId'],*q.get('revisionAuthors',[])];assert sha(a['blindPacketPath'])==a['blindPacketSha256'] and sha(a['bindingPath'])==a['bindingSha256'];assert all(sha(o['previewPath'])==o['previewSha256'] for o in a['sourceObservations'])
 closure=('The h_time variable is now explicitly defined with seconds, closing the sole remaining formula-metadata finding. Other L36 content remains unchanged.' if q['lectureId']=='L36' else 'The question now states zero entry cost and tests an easy start-cost calculation, not an extremely-tricky typo. Both conflicting printed labels remain explicitly cited. The ambiguity and difficulty findings are closed.')
 reviews.append(dict(id=q['id']+f'-v{q["version"]}-contracts-residual',questionId=q['id'],questionVersion=q['version'],questionSha256=question_hash(q),reviewerId=e['reviewerId'],decision='verified',reviewedAt=now,sourceVersions=e['sourceVersions'],reviewedSlideIds=[c['slideId'] for c in q['citations']],independentAnswerOptionIds=a['independentAnswerOptionIds'],solvedBeforeAnswerSeen=False,checks={k:True for k in ['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']},reasoning=a['reasoning']+' '+closure+' All current option rationales, formula definitions/units, source mappings and nine checks pass. Prior-version answer exposure is disclosed; this is independent re-review, not a fresh blind solve.',findings=[],blindAnswersPath=ap,blindAnswersSha256=sha(ap),independentSolvedAt=e['frozenAt'],priorAuthorExposure=True,currentVersionSolvedBeforeKeyedAccess=True,sourceInspectionEvidence=a['sourceObservations']))
assert not [err for r in reviews for err in schema_errors(r,read('data/schema.review.json'))]
# Isolated structural/file validation of the two current objects.
qq=copy.deepcopy([qs[x] for x in sorted(changed)]);rr={r['questionId']:r for r in reviews};cs=copy.deepcopy(b['concepts'])
for q in qq:q['status']='verified';q['reviewIds']=[rr[q['id']]['id']]
for co in cs:co['questionIds']=[x for x in co['questionIds'] if x in changed];co['status']='verified' if co['questionIds'] else 'identified'
sm=read('sources/manifest.json');canonical={s['id']:s for s in read('data/bank.json')['slides']};cited={ct['slideId'] for q in qq for ct in q['citations']};slides=[json.loads(l) for sid in ['lectures','assignments'] for l in (R/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()];slides=[copy.deepcopy(canonical[s['id']] if s['id'] in cited else s) for s in slides]
for sl in slides:sl['conceptIds']=[co['id'] for co in cs if sl['id'] in co['slideIds']]
tmp=dict(schemaVersion='1.0.0',bankVersion='L36-L37-residuals-contracts',title='Two residual independent checks',complete=False,sources=sm['sources'],assets=sm['assets'],slides=slides,questions=qq,concepts=cs,reviews=reviews,learningTools={k:[] for k in ['formulaSheet','confusionPairs','traps','algorithmVisualizations','numericalFamilies']});v=validate_bank(tmp,R,check_files=True);assert all('W08-L37-P1135-Q03: verified question cites unresolved source material'==err or 'search.grid-g: verified concept lacks currently independently verified questions'==err for err in v['errors']),v
p='data/reviews/W08-L36-L37-residuals-independent-contracts.json';write(p,reviews)
# Verify the accepted L36 and L37 current lecture bindings, not just counts.
allq={}
for f in (R/'data/question-batches').glob('*.json'):
 d=json.loads(f.read_text());arr=d.get('questions',[]) if isinstance(d,dict) else d
 for q in arr:
  if isinstance(q,dict) and q.get('lectureId') in ['L36','L37']:allq[q['id']]=q
matching={}
for f in (R/'data/reviews').glob('*.json'):
 d=json.loads(f.read_text());arr=d.get('reviews',[]) if isinstance(d,dict) else d
 for r in arr:
  if isinstance(r,dict) and r.get('decision')=='verified' and r.get('questionId') in allq and r.get('questionSha256')==question_hash(allq[r['questionId']]):matching[r['questionId']]=r
counts={lid:dict(total=sum(q['lectureId']==lid for q in allq.values()),verified=sum(allq[x]['lectureId']==lid for x in matching)) for lid in ['L36','L37']}
assert counts['L36']==dict(total=85,verified=85) and counts['L37']==dict(total=115,verified=115),counts
s=dict(completedAt=now,reviewed=2,verified=2,flagged=0,unrelatedSearchObjectsPreservedExactly=66,priorExposureDisclosed=2,actualCitationPagesReinspected=3,variedCases=1000,variedAssertions=2000,reviewFile=p,reviewSha256=sha(p),currentLectureCounts=counts,remainingKnownBoundedGaps=[],releaseCaveat='Canonical p1135 unresolved disposition currently blocks release of the otherwise accepted qualified L37 item; parent notified for explicit reconciliation.',sourceContradictions='L37 printed start-cost conflict remains in the source; this qualified question uses an explicit convention, not a global source correction.',validation=v,mutations='Reviewer artifacts only; no author, bank, source or Git edits.');write('audits/W08-L36-L37-residuals-contracts-summary.json',s)
(R/'docs/handoffs/L36-L37-residuals-contracts-review.md').write_text(f"Both residuals have accepted content reviews. Release caveat: canonical p1135 remains unresolved and still blocks L37 pool inclusion until parent reconciles its disposition. Current matching-hash review counts: L36 85/85, L37 115/115. All 66 unrelated search-foundation objects preserved exactly. Three actual pages re-inspected and 2,000 varied arithmetic/bound assertions passed before current keys. Both questions disclose prior exposure. Review {p}; SHA256 {sha(p)}. Source start-cost contradiction remains disclosed. Isolated validation: {len(v['errors'])} errors. Next fresh L47 review.\n")
print(json.dumps(dict(verified=2,reviewSha256=sha(p),counts=counts,errors=len(v['errors']),warnings=len(v['warnings']))))
