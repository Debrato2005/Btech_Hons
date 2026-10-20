"""Freeze L59 authored drafts. No canonical assembly or Git operation."""
from pathlib import Path
import json,hashlib,datetime,sys,copy
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors,validate_bank
from authoring_helpers import SHA
B='W12-L59';bp=R/f'data/question-batches/{B}.json';b=json.loads(bp.read_text());packet=R/f'audits/blind-{B}.json';checkp=R/f'audits/{B}-author-checks.json';check=json.loads(checkp.read_text());ins=json.loads((R/f'data/inspection-batches/{B}.json').read_text())
assert len(b['questions'])==65 and len(ins['slides'])==32
for q in b['questions']:
 if q['type'] in ('numerical','derivation','code'):
  q['authorCheckEvidence']={'path':str(checkp.relative_to(R)),'sha256':hashlib.sha256(checkp.read_bytes()).hexdigest(),'independentReview':False,'scope':'Author-only explicitly added differential-drive, odometry, PID, frame, probability, depth and feasibility calculations. No ROS, Gazebo, original code, video or hardware execution.'}
 assert q['status']=='draft' and not q['reviewIds']
for key,items in [('question',b['questions']),('concept',b['concepts']),('slide',ins['slides'])]:
 schema=json.loads((R/f'data/schema.{key}.json').read_text())
 for x in items:
  e=schema_errors(x,schema);assert not e,(x['id'],e)
bp.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
p=[]
for q in b['questions']:
 h={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in h['citations']:
  c.pop('evidenceText',None)
  c['locator']=f"Lecture L59, physical PDF page {c['physicalPage']}, printed footer {c['physicalPage']-1876}: inspect the {c['kind']} content on this source page. Neutral review locator; no answer-bearing transcription."
 p.append(h)
packet.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
# Read-only in-memory integration validates reciprocal references against real corpus.
bank=json.loads((R/'data/bank.json').read_text());qids={q['id'] for q in b['questions']};cids={c['id'] for c in b['concepts']};sids={s['id'] for s in ins['slides']}
bank['questions']=[q for q in bank['questions'] if not q['id'].startswith(B+'-')]+copy.deepcopy(b['questions'])
bank['concepts']=[c for c in bank['concepts'] if not c['id'].startswith(B+'-')]+copy.deepcopy(b['concepts'])
sm={s['id']:s for s in ins['slides']}
for i,s in enumerate(bank['slides']):
 if s['id'] in sm:
  ns=copy.deepcopy(sm[s['id']]);ns['conceptIds']=list(dict.fromkeys([c for c in s['conceptIds'] if not c.startswith(B+'-')]+ns['conceptIds']));bank['slides'][i]=ns
report=validate_bank(bank,root=R,check_files=False)
(R/f'audits/{B}-preflight-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert report['valid'],report['errors']
paths=[f'data/question-batches/{B}.json',f'data/inspection-batches/{B}.json',f'audits/blind-{B}.json']+[f'audits/{B}-{s}.json' for s in ['author-coverage','source-issues','primary-evidence','page-observations','author-checks','preflight-validation','author-options-preflight']]+['scripts/author_W12_L59.py','scripts/inspect_W12_L59.py','scripts/check_W12_L59_author.py','scripts/preflight_W12_L59_options.py','scripts/finalize_W12_L59_author.py']
m={'batchId':B,'authorId':b['authorId'],'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Frozen drafts awaiting distinct source-first independent review.','sourceId':'lectures','sourceSha256':SHA,'physicalPages':[1877,1908],'printedLectureNumber':59,'actualPagesInspected':32,'substantivePages':26,'questionCount':len(b['questions']),'conceptCount':len(b['concepts']),'packet':str(packet.relative_to(R)),'packetSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'questionHashes':{q['id']:question_hash(q) for q in b['questions']},'files':{x:hashlib.sha256((R/x).read_bytes()).hexdigest() for x in paths},'authorChecks':{'named':check['namedChecks'],'varied':check['variedChecks'],'independent':False},'sourceCodePresent':False,'originalImplementationExecuted':False,'ROSExecuted':False,'hardwareExecuted':False,'coverageChallengePending':True,'preflight':['All 32 actual rendered pages viewed; all 26 substantive pages have source-concept/question coverage.','Footer numbers inspected separately from physical pagination. Source lecture number 59 agrees with sequence L59.','Thirty-one distractor sets were refined before first review to replace unrelated alternatives with relevant misconceptions.','Formula symbols, units, additional values and model assumptions are explicit; no source code or robot execution is invented.','Four local source qualifications remain original-source-version-bound; no global resolution is invented.','37 named and 5000 varied author checks pass. No ROS/Gazebo, original implementation, live device, video success rate or YOLO runtime is claimed.']}
(R/f'audits/{B}-frozen-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
a={k:m[k] for k in ['batchId','authorId','sourceId','sourceSha256','physicalPages','packet','packetSha256','questionHashes']};a['reviewInstructions']='Inspect actual pixels and freeze source-derived answers before opening keyed batch, source issue ledger, author script/checks or full manifest narrative. Author checks are not independent evidence.'
(R/f'audits/{B}-minimal-bindings.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:m[k] for k in ['questionCount','packetSha256','authorChecks']}))
