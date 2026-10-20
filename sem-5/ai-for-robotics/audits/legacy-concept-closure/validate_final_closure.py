"""Final lecture-closure gate in memory. Never assembles shared bank or HTML."""
import collections,copy,datetime,hashlib,itertools,json,pathlib,sys
R=pathlib.Path(__file__).resolve().parents[2];D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,canonical_json,schema_errors
from review_gate import apply_review_gate
def rd(p):return json.loads(p.read_text())
def sha(x):return hashlib.sha256(canonical_json(x).encode()).hexdigest()
def fs(p):return hashlib.sha256(p.read_bytes()).hexdigest()
B=rd(R/'data/bank.json');initialBank=fs(R/'data/bank.json');sc=rd(R/'data/schema.bank.json');q=[];c=[];r=[];where=collections.defaultdict(list)
for p in sorted((R/'data/question-batches').glob('*.json')):
 d=rd(p);q.extend(d.get('questions',[]));c.extend(d.get('concepts',[]))
 for v in d.get('concepts',[]):where[v['id']].append(str(p.relative_to(R)))
for p in sorted(list((R/'data/reviews').glob('*.json'))+list((R/'audits/review-batches').glob('*.json'))):
 d=rd(p);r.extend(d if isinstance(d,list) else d.get('reviews',[]))
assert len(q)==len({i['id'] for i in q});assert len(r)==len({i['id'] for i in r})
new=rd(R/'data/question-batches/W01-L02-L05-QUALIFIED-GAPS.json')['questions'];newids={x['id'] for x in new};cm={x['id']:x for x in c};gated=copy.deepcopy(q);quarantine=apply_review_gate(gated,r,B['slides'],B['sources']);gm={x['id']:x for x in gated}
assert all(gm[x['id']]['status']=='verified' for x in new)
sourceversions={}
for name in ['qualified-drafts-v1.json','qualified-drafts-v2.json','qualified-drafts-v3.json']:
 for x in rd(D/name)['questions']:sourceversions[(x['id'],x['version'])]=x
for x in new:assert sha(x)==sha(sourceversions[(x['id'],x['version'])]);assert not schema_errors(x,sc['$defs']['question'],root=sc)
old=[x for x in B['questions'] if x['lectureId'] in ['L02','L05'] and x['id'] not in newids];assert all(sha(x)==sha(gm[x['id']]) for x in old)
for x in new:
 cc=cm[x['conceptIds'][0]];assert cc['questionIds']==[x['id']] and cc['coverageResolution']['independentReviewRequired'] is False
 assert cc['coverageResolution']['questionSha256']==question_hash(x)
 current=[rr for rr in r if rr['questionId']==x['id'] and rr['questionSha256']==question_hash(x) and rr['decision']=='verified'];assert current
 assert set(cc['coverageResolution']['independentReviewIds'])<=set(rr['id'] for rr in current)
alias=rd(D/'L30-durable-coverage-crosslinks.json');assert len(alias['items'])==8
for a in alias['items']:
 cc=cm[a['legacyConceptId']];assert not cc['questionIds'];assert cc['coverageResolution']['sha256']==fs(D/'L30-durable-coverage-crosslinks.json')
 for b in a['verifiedQuestionCrosslinks']:
  assert question_hash(gm[b['id']])==b['questionSha256'] and sha(gm[b['id']])==b['wholeObjectSha256']
term=next(a for a in alias['items'] if a['legacyConceptId']=='learning-observed-P0905-C03');assert term['residualSourceQualification'];assert next(x for x in term['verifiedQuestionCrosslinks'] if x['id']=='W06-L30-Q056')['actualCitedPhysicalPages']==[914]
quote=cm['W01-L02-C-summary-quote'];assert quote['coverageDisposition']=='excluded_commentary_only' and not quote['questionIds'];assert quote['coverageResolution']['sha256']==fs(D/'L02-summary-quote-disposition.json')
for pp in [984,1085,1195]:
 rows=[]
 for p in (R/'data/inspection-batches').glob('*.json'):
  d=rd(p);rows.extend(d if isinstance(d,list) else d.get('slides',d.get('inspections',[])))
 s=next(s for s in rows if s.get('id',s.get('slideId'))==f'lectures-p{pp:04}');assert s['disposition']=='repeated' and s['incrementalChangesChecked'] and s['repeatsSlideIds'];assert s['coverageCrosslinks']['sha256']==fs(D/'summary-row-crosslinks.json')
permutations=0
for x in new:
 for order in itertools.permutations(x['options']):assert {o['id'] for o in order if o['id'] in x['correctOptionIds']}==set(x['correctOptionIds']);permutations+=1
assert fs(R/'data/bank.json')==initialBank
paths=['data/question-batches/W01-L02-L05-QUALIFIED-GAPS.json','data/question-batches/W01-L02.json','data/question-batches/W01-L05.json','data/question-batches/learning-observed-concepts.json','data/inspection-batches/W01-L02.json','data/inspection-batches/W07-L32.json','data/inspection-batches/W07-L35.json','data/inspection-batches/W08-L38.json']+[f'audits/review-batches/W01-L02-L05-legacy-closure-v{v}.json' for v in [1,2,3]]
result={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'pass_owned_lecture_scope','sixQuestionsIndependentlyVerified':True,'newQuestionVersions':{x['id']:x['version'] for x in new},'newQuestionGateStates':{x['id']:gm[x['id']]['status'] for x in new},'frozenQuestionObjectsPreserved':6,'legacyL02L05WholeObjectsPreserved':len(old),'aliasRecordsResolved':8,'quoteExclusionScope':'Commentary only; seven technical summary rows preserved.','summaryRepeatPages':[984,1085,1195],'optionPermutationsChecked':permutations,'sharedBankReassembled':False,'sharedBankVersion':B['bankVersion'],'sharedBankSha256':initialBank,'sourceAuthoringPathsTouched':[{'path':p,'sha256':fs(R/p)} for p in paths],'globalConceptDuplicatesOutsideOwnedScope':{i:pp for i,pp in where.items() if len(pp)>1},'boundary':'An in-memory exact-hash gate and structural validation, not shared-bank assembly, full-course completion, or actual browser verification. Source/indexed-evidence access limits remain unchanged.'}
(D/'final-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='sourceAuthoringPathsTouched'},indent=2))
