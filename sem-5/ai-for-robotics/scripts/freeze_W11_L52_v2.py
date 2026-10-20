#!/usr/bin/env python3
"""Author-side validation and changed-only blind freeze. Does not review or integrate."""
from pathlib import Path
import json,hashlib,datetime,copy,sys,re
R=Path(__file__).resolve().parents[1];B='W11-L52';sys.path.insert(0,str(R/'scripts'));from validate import validate_bank

def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qh(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ['status','reviewIds']},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert not (R/f'audits/{B}-v2-repair-manifest.json').exists()
b=read(f'data/question-batches/{B}.json');w=read(f'audits/{B}-v2-repair-work.json');checks=read(f'audits/{B}-v2-author-checks.json');ins=read(f'data/inspection-batches/{B}.json');Q={q['id']:q for q in b['questions']}
assert checks['questionBatchSha256']==sha(f'data/question-batches/{B}.json')and checks['checkGroups']==50
assert all(qh(Q[i])==h for i,h in w['preservedAcceptedHashes'].items())
ids=set(w['changedIds']+w['newGapIds']);qs=sorted([Q[i]for i in ids],key=lambda q:q['id']);assert len(qs)==21
for q in qs:
 assert q['status']=='draft'and not q['reviewIds'];assert set(q['solution']['optionExplanations'])=={o['id']for o in q['options']}
 assert all(c['kind']in ['statement','equation','table','figure','code','derivation','other']for c in q['citations'])
 assert not re.search('(?i)all of the above|none of the above|first two options',q['stem'])
 assert q['difficulty']in ['easy','medium']
 if q.get('conflictResolution'):assert q['conflictResolution']['questionVersion']==q['version']
bank=read('data/bank.json')
for collection,own in [('questions',b['questions']),('concepts',b['concepts']),('slides',ins['slides'])]:
 ownids={x['id']for x in own};bank[collection]=[x for x in bank[collection]if x['id']not in ownids]+copy.deepcopy(own)
valid=validate_bank(bank,R,check_files=False);write(f'audits/{B}-v2-preflight.json',{'role':'Author-side in-memory structural preflight only','validation':valid});assert valid['valid'],valid['errors']
blind=[]
for q in qs:
 z={k:copy.deepcopy(q[k])for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions']};z['citations']=[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]
 if q.get('primaryEvidence'):z['externalSources']=[{k:v for k,v in e.items()if k in ['title','url','version','localEvidence']}for e in q['primaryEvidence']]
 blind.append(z)
packet=f'audits/blind-{B}-v2.json';write(packet,blind);h=sha(packet);binding=f'audits/blind-binding-{B}-v2.json';write(binding,dict(packetSha256=h,questions=[dict(id=q['id'],version=q['version'],sha256=qh(q))for q in qs]))
write(f'audits/{B}-v2-repair-manifest.json',dict(batchId=B,frozenAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),packetPath=packet,packetSha256=h,bindingPath=binding,bindingSha256=sha(binding),changedOnlyCount=21,revisedCount=15,newGapCount=6,currentCount=138,preservedAcceptedHashes=w['preservedAcceptedHashes'],currentQuestionHashes={q['id']:qh(q)for q in qs},gapQuestionMap=w['gapQuestionMap'],changeNotes=w['changeNotes'],sourceQualificationSha256=w['sourceQualificationsSha256'],sourceQualificationCount=22,authorChecks=f'audits/{B}-v2-author-checks.json',checkGroups=50,randomCases=1000,randomAssertions=4000,actualRevisitedPages=20,sourceBounds=[1620,1684],schemaValid=True,independentReviewPending=True,runtimeBoundaryUnchanged='audits/W11-L52-runtime-boundary.json'))
text=f'''L52 v2 frozen: 15 flagged objects revised and six bounded gap questions added. All 117 accepted objects and hashes are unchanged; 138 current objects total. All original keys retained for the 15 revisions. Independent re-review required for the 21-object changed-only packet; author checks are not independent verification.

Packet: {packet}
SHA256: {h}
Minimal answer-free binding: {binding}
Binding SHA256: {sha(binding)}
Post-answer repair manifest: audits/{B}-v2-repair-manifest.json
Author checks: audits/{B}-v2-author-checks.json (50 groups plus 1,000 varied cases / 4,000 assertions, standard-library default Python only).
Actual source revisits: audits/{B}-v2-author-revisits.json (20 pages). Existing 65 unique-page inspections remain unchanged, not recounted. Prior batch/packet/binding/manifest archived in audits/archive/W11-L52-v1-before-v2. All 22 source qualifications retained byte-for-byte. Six source-based additions cover LDR and reed construction, DHT ADC/interface and layer order, capacitive tactile/compliant-control applications, and combined environmental/interface/size/weight constraints. In-memory schema validation passed.

Historical runtime-boundary record remains audits/W11-L52-runtime-boundary.json. No restricted virtual environment, OpenCV/Ultralytics import, model inference, video codec or hardware used for these repairs. The archived YAML count was checked in default Python only. Restrictions unchanged: no L49 original notebook retrieval or alternate route, NLTK corpus download, denied L48 dependency/model route, or /tmp/robotics-l35-venv use. Actual downloaded-file browser QA remains blocked. No Git or canonical-bank writes. Next: L58 pages 1843–1876.
'''
(R/f'audits/handoffs/{B}-repair.md').write_text(text);(R/f'audits/handoffs/{B}.md').write_text(text)
print('FROZEN',h);print('BINDING',sha(binding))
