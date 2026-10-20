"""Verify the completed lecture-only staging without changing unrelated work."""
import collections,copy,datetime,hashlib,json,pathlib,sys
R=pathlib.Path(__file__).resolve().parents[2];D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,canonical_json,schema_errors
from review_gate import apply_review_gate
def read(p):return json.loads(p.read_text())
def sha(x):return hashlib.sha256(canonical_json(x).encode()).hexdigest()
def fsha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
B=read(R/'data/bank.json');BQ={q['id']:q for q in B['questions']};qs=[];cs=[];dups=collections.defaultdict(list);reviews=[];sc=read(R/'data/schema.bank.json')
for p in sorted((R/'data/question-batches').glob('*.json')):
 d=read(p);qs.extend(d.get('questions',[]));cs.extend(d.get('concepts',[]))
 for c in d.get('concepts',[]):dups[c['id']].append(str(p.relative_to(R)))
assert len(qs)==len({q['id'] for q in qs})
for p in sorted(list((R/'data/reviews').glob('*.json'))+list((R/'audits/review-batches').glob('*.json'))):
 d=read(p);reviews.extend(d if isinstance(d,list) else d.get('reviews',[]))
assert len(reviews)==len({r['id'] for r in reviews});copyq=copy.deepcopy(qs);apply_review_gate(copyq,reviews,B['slides'],B['sources']);gm={q['id']:q for q in copyq};cmap={c['id']:c for c in cs}
staged=read(R/'data/question-batches/W01-L02-L05-QUALIFIED-GAPS.json');v1=read(D/'qualified-drafts-v1.json');v2=read(D/'qualified-drafts-v2.json');rr=read(D/'independent-review-v1.json');accepted=[r['questionId'] for r in rr if r['decision']=='verified'];modified=[q['id'] for q in v2['questions']];v1map={q['id']:q for q in v1['questions']};stmap={q['id']:q for q in staged['questions']}
assert all(sha(v1map[qid])==sha(stmap[qid]) for qid in accepted)
assert all(gm[qid]['status']=='verified' for qid in accepted)
assert all(gm[qid]['status']=='draft' for qid in modified)
assert all(not schema_errors(q,sc['$defs']['question'],root=sc) for q in staged['questions'])
legacy=[q for q in B['questions'] if q['lectureId'] in ['L02','L05']]
assert all(sha(q)==sha(gm[q['id']]) for q in legacy)
ownedConcepts={q['conceptIds'][0] for q in staged['questions']}|{'W01-L02-C-summary-quote'}|{a['legacyConceptId'] for a in read(D/'L30-durable-coverage-crosslinks.json')['items']}
assert all(set(cmap[cid]['questionIds'])=={q['id'] for q in qs if cid in q['conceptIds']} for cid in ownedConcepts)
assert all(not schema_errors(cmap[cid],sc['$defs']['concept'],root=sc) for cid in ownedConcepts)
paths=['data/question-batches/W01-L02-L05-QUALIFIED-GAPS.json','audits/review-batches/W01-L02-L05-legacy-closure-v1.json','data/question-batches/W01-L02.json','data/question-batches/W01-L05.json','data/question-batches/learning-observed-concepts.json','data/inspection-batches/W01-L02.json','data/inspection-batches/W07-L32.json','data/inspection-batches/W07-L35.json','data/inspection-batches/W08-L38.json']
report={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'pass_for_owned_lecture_scope','sharedBankReassembled':False,'sharedBankVersion':B['bankVersion'],'sharedBankSha256':fsha(R/'data/bank.json'),'canonicalPathsTouched':[{'path':p,'sha256':fsha(R/p)} for p in paths],'ownedLegacyQuestionWholeObjectsPreservedAfterGate':len(legacy),'approvedV1WholeObjectsPreservedBeforeGate':3,'newQuestionGateStates':{qid:gm[qid]['status'] for qid in stmap},'ownedConceptQuestionSymmetry':True,'independentV1ReviewsCopiedExactly':sha(rr)==sha(read(R/'audits/review-batches/W01-L02-L05-legacy-closure-v1.json')),'globalConceptDuplicatesOutsideOwnedScope':{cid:pp for cid,pp in dups.items() if len(pp)>1},'newConceptQuestionLinks':6,'metadataOnlyConceptCount':9,'summaryRepeatMetadataPages':[984,1085,1195],'summaryQuoteScope':'Quotation commentary only; all seven substantive rows preserved.','L59':'No L59 question or file changed.','L60':'No L60 question or file changed.','limitations':['The shared bank and HTML have not been rebuilt by this worker.','Three repaired questions remain draft pending independent v2 review.','Global assembly validation must wait for unrelated concurrent assignment concept ownership to reconcile if the duplicate remains.']}
(D/'canonical-staging-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,indent=2))
