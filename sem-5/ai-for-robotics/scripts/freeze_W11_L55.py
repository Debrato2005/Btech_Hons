"""Freeze L55 authored drafts. No canonical assembly or Git operation."""
from pathlib import Path
import json,hashlib,datetime,sys,copy
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors,validate_bank
from authoring_helpers import SHA
B='W11-L55';bp=R/f'data/question-batches/{B}.json';b=json.loads(bp.read_text());packet=R/f'audits/blind-{B}.json';checkp=R/f'audits/{B}-author-checks.json';check=json.loads(checkp.read_text());ins=json.loads((R/f'data/inspection-batches/{B}.json').read_text())
assert len(b['questions'])==72 and len(ins['slides'])==32
for q in b['questions']:
 if q['type'] in ('numerical','derivation','code'):
  q['authorCheckEvidence']={'path':str(checkp.relative_to(R)),'sha256':hashlib.sha256(checkp.read_bytes()).hexdigest(),'independentReview':False,'scope':'Author-only symbolic/NumPy equation checks and source-transcribed MLP runtime with an explicit added seed. No omitted DeLaN class or hardware execution.'}
 assert q['status']=='draft' and not q['reviewIds']
for key,items in [('question',b['questions']),('concept',b['concepts']),('slide',ins['slides'])]:
 schema=json.loads((R/f'data/schema.{key}.json').read_text())
 for x in items:
  e=schema_errors(x,schema);assert not e,(x['id'],e)
bp.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
p=[]
for q in b['questions']:
 h={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in h['citations']:c.pop('evidenceText',None)
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
paths=[f'data/question-batches/{B}.json',f'data/inspection-batches/{B}.json',f'audits/blind-{B}.json']+[f'audits/{B}-{s}.json' for s in ['author-coverage','source-issues','primary-evidence','page-observations','author-checks','preflight-validation']]+['scripts/author_W11_L55.py','scripts/inspect_W11_L55.py','scripts/check_W11_L55_author.py','scripts/check_W11_L55_mlp_runtime.py','audits/W11-L55-mlp-runtime.json','audits/W11-L55-author-mlp-trajectory.png']
m={'batchId':B,'authorId':b['authorId'],'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Frozen drafts awaiting distinct source-first independent review.','sourceId':'lectures','sourceSha256':SHA,'physicalPages':[1745,1776],'printedLectureNumber':55,'actualPagesInspected':32,'substantivePages':28,'questionCount':len(b['questions']),'conceptCount':len(b['concepts']),'packet':str(packet.relative_to(R)),'packetSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'questionHashes':{q['id']:question_hash(q) for q in b['questions']},'files':{x:hashlib.sha256((R/x).read_bytes()).hexdigest() for x in paths},'authorChecks':{'named':check['namedChecks'],'varied':check['variedChecks'],'independent':False},'sourceCodePresent':True,'fullMLPExecuted':True,'DeLaNExecuted':False,'hardwareExecuted':False,'coverageChallengePending':True,'preflight':['All 32 actual rendered pages viewed; all 28 substantive pages have question/concept coverage.','All footer numbers were inspected separately from physical pagination.','Exact figure and table locators, explicit added-model assumptions and full formula records are supplied.','Weak distractors replaced with same-domain connection, sign, unit, classification and control misconceptions.','Source contradictions remain local and bound to original source SHA; no global resolution is invented.','42 named and 5000 varied checks passed. Full printed-parameter MLP executed with declared seed; exact slide output and omitted DeLaN class are not claimed reproduced.']}
(R/f'audits/{B}-frozen-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
a={k:m[k] for k in ['batchId','authorId','sourceId','sourceSha256','physicalPages','packet','packetSha256','questionHashes']};a['reviewInstructions']='Inspect actual pixels and freeze source-derived answers before opening keyed batch, source issue ledger, author script/checks or full manifest narrative. Author checks are not independent evidence.'
(R/f'audits/{B}-minimal-bindings.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:m[k] for k in ['questionCount','packetSha256','authorChecks']}))
