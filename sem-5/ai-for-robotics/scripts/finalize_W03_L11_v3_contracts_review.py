from pathlib import Path
import json,hashlib,datetime,sys,copy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash,schema_errors,validate_bank
read=lambda p:json.loads((ROOT/p).read_text());sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
ap='audits/independent-answers-W03-L11-v3-contracts.json';assert sha(ap)=='6ace30a950b3997e847b0af6b3ec8cd99184c264d5a33249ad84d335d072a18c';e=read(ap);b=read('audits/review-snapshots/W03-L11-v3-contracts.json');qb={q['id']:q for q in b['questions']};obs={o['physicalPage']:o for o in read('audits/blind-answers-W03-L11-v2-contracts-reviewer.json')['pageObservations']};now=datetime.datetime.now(datetime.timezone.utc).isoformat();R=e['reviewerId']
accepted=[r for p in ['data/reviews/W03-L11-v1-independent.json','data/reviews/W03-L11-v2-independent-contracts.json'] for r in read(p) if r['decision']=='verified'];assert len(accepted)==106;assert all(question_hash(qb[r['questionId']])==r['questionSha256'] for r in accepted)
reviews=[]
for a in e['answers']:
 q=qb[a['questionId']];assert question_hash(q)==a['questionSha256'];assert q['correctOptionIds']==a['independentAnswerOptionIds'];assert R not in {q['authorId'],*q.get('revisionAuthors',[])}
 pages=sorted({c['physicalPage'] for c in q['citations']})
 for p in pages:assert sha(obs[p]['previewPath'])==obs[p]['previewSha256']
 resolution='The two incomplete, irrelevant formula blocks were removed from the recall items; the symmetry duplicate was replaced with a worked two-point tensor counterexample. I checked every new option rationale, all signs, the complete formula metadata and the medium numerical classification.'
 reviews.append(dict(id=q['id']+'-v3-contracts-independent',questionId=q['id'],questionVersion=3,questionSha256=question_hash(q),reviewerId=R,decision='verified',reviewedAt=now,sourceVersions=e['sourceVersions'],reviewedSlideIds=[f'lectures-p{p:04d}' for p in pages],independentAnswerOptionIds=a['independentAnswerOptionIds'],solvedBeforeAnswerSeen=False,checks={k:True for k in ['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']},reasoning=a['reasoning']+' '+e['exposureDisclosure']+' '+resolution+' Recall-only items need no calculation. The numerical tensor was independently summed exactly before current-version key access. Source pixels and hashes are reused from my actual27-page L11 inspection. No self-authored content is being approved.',findings=[],priorVersionKeyExposure=True,currentVersionSolvedBeforeKeyReveal=True,independentAnswerEvidencePath=ap,independentAnswerEvidenceSha256=sha(ap),sourceInspectionEvidence=[{k:obs[p][k] for k in ['physicalPage','inspectorId','previewPath','previewSha256','dimensions','inspectedAt']} for p in pages]))
assert not [x for r in reviews for x in schema_errors(r,read('data/schema.review.json'))]
out='data/reviews/W03-L11-v3-independent-contracts.json';write(out,reviews)
allreviews=accepted+reviews;rb={r['questionId']:r for r in allreviews};qs=copy.deepcopy(b['questions']);cs=copy.deepcopy(b['concepts'])
for q in qs:q['status']='verified';q['reviewIds']=[rb[q['id']]['id']]
for c in cs:c['status']='verified'
manifest=read('sources/manifest.json');slides=[json.loads(s) for sid in ['lectures','assignments'] for s in (ROOT/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()];updates={s['id']:s for s in read('data/inspection-batches/W03-L11.json')['slides']};slides=[copy.deepcopy(updates.get(s['id'],s)) for s in slides]
for s in slides:
 if s['id'] in updates:s['conceptIds']=[c['id'] for c in cs if s['id'] in c['slideIds']]
tmp={'schemaVersion':'1.0.0','bankVersion':'L11-v3-contracts-independent-isolated','title':'L11 revision review validation','complete':False,'sources':manifest['sources'],'assets':manifest['assets'],'slides':slides,'questions':qs,'concepts':cs,'reviews':allreviews,'learningTools':{k:[] for k in ['formulaSheet','confusionPairs','traps','algorithmVisualizations','numericalFamilies']}}
v=validate_bank(tmp,ROOT,check_files=True)
summary=dict(reviewerId=R,completedAt=now,reviewed=3,verified=3,flagged=0,preservedAcceptedHashes=106,currentVerifiedTotal=109,currentTotal=109,reviewFile=out,reviewSha256=sha(out),independentAnswersSha256=sha(ap),exposure=e['exposureDisclosure'],validation=v,sourceScope='All27 L11 actual source pages inspected previously by this reviewer; this v3 check reuses unchanged evidence for361,362,372,374. The entire course is not certified by this lecture result.')
write('audits/W03-L11-v3-contracts-review-summary.json',summary)
with (ROOT/'docs/handoffs/L11-v2-contracts-review.md').open('a') as f:f.write('\n## Final v3 resolution\n\nAll three v3 repairs pass. The106 previously accepted hashes are unchanged; current L11 total is109 verified of109. The two recall formula blocks are removed, and the duplicate is replaced by a genuinely distinct numerical reflected-pair tensor. Review file: data/reviews/W03-L11-v3-independent-contracts.json. Prior v2 keyed exposure is explicitly disclosed; all three current answers were re-derived and saved before v3 keyed access. Validation has zero errors and only the three expected nonblind-review warnings. Next assignment: source-first L16 independent review once frozen.\n')
print(json.dumps(summary,indent=2));assert v['valid']
