"""Freeze current L51 drafts, without assembly or Git mutation."""
from pathlib import Path
import json,hashlib,datetime,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors
from authoring_helpers import SHA
B='W11-L51'; b=json.loads((R/f'data/question-batches/{B}.json').read_text()); packet=R/f'audits/blind-{B}.json'; p=json.loads(packet.read_text()); check=json.loads((R/f'audits/{B}-author-checks.json').read_text()); ins=json.loads((R/f'data/inspection-batches/{B}.json').read_text())
assert len(p)==len(b['questions'])==76
for q,h in zip(b['questions'],p):
 assert q['id']==h['id'] and q['status']=='draft' and not q['reviewIds']
 assert not {'correctOptionIds','solution','conflictResolution','primaryEvidence'} & set(h)
 assert all('evidenceText' not in c for c in h['citations'])
for key,items in [('question',b['questions']),('concept',b['concepts']),('slide',ins['slides'])]:
 schema=json.loads((R/f'data/schema.{key}.json').read_text())
 for x in items:
  e=schema_errors(x,schema);assert not e,(x['id'],e)
paths=[f'data/question-batches/{B}.json',f'data/inspection-batches/{B}.json',f'audits/blind-{B}.json']+[f'audits/{B}-{s}.json' for s in ['author-coverage','source-issues','primary-evidence','page-observations','author-checks']]+['scripts/author_W11_L51.py','scripts/inspect_W11_L51.py','scripts/check_W11_L51_author.py']
m={'batchId':B,'authorId':b['authorId'],'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Frozen drafts awaiting distinct source-first independent review.','sourceId':'lectures','sourceSha256':SHA,'physicalPages':[1595,1619],'printedLectureNumber':51,'actualPagesInspected':25,'substantivePages':20,'questionCount':76,'conceptCount':len(b['concepts']),'packet':str(packet.relative_to(R)),'packetSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'questionHashes':{q['id']:question_hash(q) for q in b['questions']},'files':{x:hashlib.sha256((R/x).read_bytes()).hexdigest() for x in paths},'authorChecks':{'named':check['namedChecks'],'varied':check['variedChecks'],'independent':False},'sourceCodePresent':False,'hardwareExecuted':False,'coverageChallengePending':True,'preflight':['All 25 actual pages viewed; 20 substantive pages each have a cited question.','Physical 1598 has no visible footer and is recorded as absent, not inferred.','Formula records include variables, units and explicit added-model assumptions.','No battery or actuator physical experiment, inference benchmark or network timing test is claimed.','Draft answer choices refined for plausible same-domain misconceptions.','Primary-source qualifications are item-bound and source conflicts remain explicit.']}
(R/f'audits/{B}-frozen-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
a={k:m[k] for k in ['batchId','authorId','sourceId','sourceSha256','physicalPages','packet','packetSha256','questionHashes']};a['reviewInstructions']='Inspect actual pixels and freeze source-derived answers before opening keyed batch, issue ledger, author checks or script. Author analysis is not independent evidence.'
(R/f'audits/{B}-minimal-bindings.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:m[k] for k in ['questionCount','packetSha256','authorChecks']}))
