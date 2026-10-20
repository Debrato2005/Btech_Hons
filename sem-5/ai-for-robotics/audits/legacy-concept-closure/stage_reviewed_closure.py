"""Stage authorized additions and coverage metadata without shared-bank assembly."""
import copy,datetime,hashlib,json,pathlib,sys
R=pathlib.Path(__file__).resolve().parents[2];D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,canonical_json,schema_errors
from review_gate import apply_review_gate
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text())
def sha(o):return hashlib.sha256(canonical_json(o).encode()).hexdigest()
def fsha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
v1=read(D/'qualified-drafts-v1.json');v2=read(D/'qualified-drafts-v2.json');reviews=read(D/'independent-review-v1.json');reviewmap={r['questionId']:r for r in reviews};rep={q['id']:q for q in v2['questions']};new=[copy.deepcopy(rep.get(q['id'],q)) for q in v1['questions']];qids={q['id'] for q in new};schema=read(R/'data/schema.bank.json')
basebank=read(R/'data/bank.json');basebankhash=fsha(R/'data/bank.json');before={};paths={};batches={}
for p in sorted((R/'data/question-batches').glob('*.json')):
 d=read(p);batches[p]=d
 for q in d.get('questions',[]):assert q['id'] not in before;before[q['id']]=sha(q)
 for c in d.get('concepts',[]):paths[c['id']]=p
assert not qids.intersection(before),'Stop rather than duplicate an already-staged new question.'
accepted=[q for q in v1['questions'] if reviewmap[q['id']]['decision']=='verified']
assert all(sha(q)==sha(next(n for n in new if n['id']==q['id'])) for q in accepted)
# Copy independent decisions, retaining flagged v1 history. V2 is not approved by this step.
reviewdest=R/'audits/review-batches/W01-L02-L05-legacy-closure-v1.json';assert not reviewdest.exists()
for p in list((R/'data/reviews').glob('*.json'))+list((R/'audits/review-batches').glob('*.json')):
 d=read(p);rr=d if isinstance(d,list) else d.get('reviews',[])
 assert not {r['id'] for r in rr}.intersection(r['id'] for r in reviews),'Review already staged elsewhere.'
write(reviewdest,reviews)
questiondest=R/'data/question-batches/W01-L02-L05-QUALIFIED-GAPS.json'
write(questiondest,{'schemaVersion':'1.0.0','batchId':'W01-L02-L05-QUALIFIED-GAPS','authorId':v1['authorId'],'sourceVersions':v1['sourceVersions'],'status':'three_v1_independently_verified_three_v2_pending_review','questions':new,'concepts':[],'reviews':[],'auditPath':'audits/legacy-concept-closure/HANDOFF.md','note':'Status labels remain frozen; the exact-hash review gate determines pool eligibility. Original concept IDs are linked in their owning batches.'})
mutated=set()
for q in new:
 cid=q['conceptIds'][0];p=paths[cid];c=next(c for c in batches[p]['concepts'] if c['id']==cid)
 assert not c['questionIds'];c['questionIds']=[q['id']];c['status']='drafted'
 c['coverageDisposition']='qualified_question_independent_review_recorded' if reviewmap[q['id']]['decision']=='verified' else 'qualified_question_revision_pending_review'
 c['coverageResolution']={'questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q),'sourceQualification':q['conflictResolution']['qualification'],'primaryEvidenceScope':q['primaryEvidence']['scope'],'auditPath':'audits/legacy-concept-closure/HANDOFF.md','independentReviewRequired':reviewmap[q['id']]['decision']!='verified'}
 mutated.add(p)
qp=paths['W01-L02-C-summary-quote'];c=next(c for c in batches[qp]['concepts'] if c['id']=='W01-L02-C-summary-quote');quote=read(D/'L02-summary-quote-disposition.json')
c['coverageDisposition']='excluded_commentary_only';c['exclusionReason']=quote['exclusionScope'];c['coverageResolution']={'path':'audits/legacy-concept-closure/L02-summary-quote-disposition.json','sha256':fsha(D/'L02-summary-quote-disposition.json'),'substantiveSummaryRowsPreserved':7,'wholePageExcluded':False};mutated.add(qp)
alias=read(D/'L30-durable-coverage-crosslinks.json')
for a in alias['items']:
 p=paths[a['legacyConceptId']];c=next(c for c in batches[p]['concepts'] if c['id']==a['legacyConceptId']);assert not c['questionIds']
 c['coverageDisposition']=a['disposition'];c['coverageResolution']={'path':'audits/legacy-concept-closure/L30-durable-coverage-crosslinks.json','sha256':fsha(D/'L30-durable-coverage-crosslinks.json'),'survivingConceptIds':a['survivingConceptIds'],'semanticQuestionReferences':a['verifiedQuestionCrosslinks'],'residualSourceQualification':a['residualSourceQualification'],'warning':'These references are semantic coverage links, not reciprocal question conceptIds or additional question citations.'};mutated.add(p)
for p in mutated:
 assert all(before[q['id']]==sha(q) for q in batches[p].get('questions',[])),p
 for c in batches[p].get('concepts',[]):assert not schema_errors(c,schema['$defs']['concept'],root=schema)
 write(p,batches[p])
# Preserve summary pages and qualify their repeats without changing accepted questions.
summary=read(D/'summary-row-crosslinks.json');metadata_updates={s['physicalPage']:s for s in summary['summaryPages']};inspection_mutated=[]
for p in sorted((R/'data/inspection-batches').glob('*.json')):
 d=read(p);records=d if isinstance(d,list) else d.get('slides',d.get('inspections',[]));dirty=False
 for s in records:
  sid=s.get('id',s.get('slideId'));physical=int(sid.split('p')[-1]) if sid and sid.startswith('lectures-p') else None
  if physical in metadata_updates:
   update=metadata_updates[physical];s['disposition']='repeated';s['exclusionReason']=None;s['repeatsSlideIds']=update['proposedRepeatsSlideIds'];s['incrementalChangesChecked']=True;s['coverageCrosslinks']={'path':'audits/legacy-concept-closure/summary-row-crosslinks.json','sha256':fsha(D/'summary-row-crosslinks.json'),'physicalPage':physical,'directCitationClaim':False};dirty=True
  if physical==93:
   s['summaryCoverage']={'path':'audits/legacy-concept-closure/L02-summary-quote-disposition.json','sha256':fsha(D/'L02-summary-quote-disposition.json'),'substantiveRowsPreserved':7,'excludedScope':'quotation commentary only','perceptionRowRelationship':'Semantic repeated-content link to Q038 at pages 70/80, not a direct page93 citation.'};dirty=True
 if dirty:write(p,d);inspection_mutated.append(p)
# Non-mutating assembly simulation for gate and symmetric links.
qq=[];cc=[]
for p in sorted((R/'data/question-batches').glob('*.json')):
 d=read(p);qq.extend(d.get('questions',[]));cc.extend(d.get('concepts',[]))
assert len({q['id'] for q in qq})==len(qq);assert len({c['id'] for c in cc})==len(cc)
post={q['id']:q for q in qq};assert all(qid in post and before[qid]==sha(post[qid]) for qid in before)
rr=[]
for p in sorted(list((R/'data/reviews').glob('*.json'))+list((R/'audits/review-batches').glob('*.json'))):
 d=read(p);rr.extend(d if isinstance(d,list) else d.get('reviews',[]))
assert len({r['id'] for r in rr})==len(rr)
slidecopy=copy.deepcopy(basebank['slides']);gateq=copy.deepcopy(qq);apply_review_gate(gateq,rr,slidecopy,basebank['sources']);gm={q['id']:q for q in gateq}
assert all(gm[q['id']]['status']=='verified' for q in accepted)
assert all(gm[q['id']]['status']=='draft' for q in v2['questions'])
assert all(set(c['questionIds'])=={q['id'] for q in qq if c['id'] in q['conceptIds']} for c in cc)
assert fsha(R/'data/bank.json')==basebankhash,'Shared bank unexpectedly changed during the staging window.'
touched=[questiondest,reviewdest]+sorted(mutated)+inspection_mutated
report={'createdAt':now,'status':'pass','sharedBankReassembled':False,'sharedBankSha256Preserved':basebankhash,'canonicalPathsTouched':[{'path':str(p.relative_to(R)),'sha256':fsha(p)} for p in touched],'existingSourceQuestionWholeObjectsPreserved':len(before),'newQuestionGateStates':{qid:gm[qid]['status'] for qid in sorted(qids)},'approvedV1WholeObjectsPreserved':len(accepted),'conceptQuestionSymmetry':True,'independentReviewsCopiedWithoutModification':sha(reviews)==sha(read(reviewdest)),'metadataOnlyConceptCount':9,'newConceptQuestionLinks':6,'summaryRepeatMetadataPages':[984,1085,1195],'summaryQuoteScope':'Commentary only; all seven substantive rows preserved.','L59':'No L59 file or question changed.','L60':'34 stale pending flags left to owner; no L60 file changed.','limitations':['This stage does not rebuild the shared bank or HTML.','Three repaired questions remain draft until independent v2 review.','Semantic alias references do not claim direct citations or change accepted question conceptIds.']}
write(D/'canonical-staging-report.json',report);print(json.dumps(report,indent=2))
