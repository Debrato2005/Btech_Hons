#!/usr/bin/env python3
"""Freeze source-first L60 draft packet and neutral hash binding."""
from pathlib import Path
import json,hashlib,datetime,collections
R=Path(__file__).resolve().parents[1];B='W12-L60'
def rd(p):return json.loads((R/p).read_text())
def wr(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qh(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert not(R/f'audits/{B}-review-manifest.json').exists()
b=rd(f'data/question-batches/{B}.json');ins=rd(f'data/inspection-batches/{B}.json');checks=rd(f'audits/{B}-author-checks.json');pre=rd(f'audits/{B}-preflight.json');obs=rd('audits/L60-page-observations.json');qs=b['questions']
assert len(qs)==74 and len(ins['slides'])==45 and len(b['concepts'])==36
assert checks['questionBatchSha256']==sha(f'data/question-batches/{B}.json')and checks['checkGroups']==32 and checks['randomAssertions']==5000
assert pre['validation']['valid']and not pre['validation']['errors']and len(pre['localChecks'])==391
assert 'Ran 63 tests'in(R/f'audits/{B}-integrity-run.txt').read_text()and(R/f'audits/{B}-integrity-run.txt').read_text().rstrip().endswith('OK')
packet=[]
for q in qs:
 z={k:q[k]for k in['id','version','stem','selectionMode','type','difficulty','options','assumptions']}
 z['citations']=[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]
 if q.get('primaryEvidence'):z['externalSources']=[{k:v for k,v in e.items()if k in['title','url','version','localEvidence']}for e in q['primaryEvidence']]
 packet.append(z)
wr(f'audits/blind-{B}.json',packet);ph=sha(f'audits/blind-{B}.json')
wr(f'audits/blind-binding-{B}.json',{'packetSha256':ph,'questions':[dict(id=q['id'],version=q['version'],sha256=qh(q))for q in qs]})
ledger=[]
for s in ins['slides']:
 p=s['physicalPage'];direct=[q['id']for q in qs if any(c['physicalPage']==p for c in q['citations'])]
 ledger.append(dict(physicalPage=p,printedSlideNumber=s['printedSlideNumber'],disposition=s['disposition'],exclusionReason=s['exclusionReason'],conceptIds=s['conceptIds'],questionIds=direct,actualObservation=obs[str(p)]['notes'],inspectionTimestamp=s['visualInspection']['inspectedAt'],coverageStatus='drafted_pending_independent_challenge'if direct else'excluded_with_specific_reason'))
assert all(x['questionIds']or x['disposition']=='excluded'for x in ledger)
wr(f'audits/{B}-page-concept-coverage.json',{'sourceId':'lectures','sourceSha256':'2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c','physicalBounds':[1909,1953],'role':'Author source/angle ledger; completeness requires independent challenge','pages':ledger,'sourceInventory':{'printedExecutableCode':0,'printedEquations':0,'technicalTables':0,'numericalCharts':0,'technicalDiagrams':0,'decorativeTitleImage':1,'emptyOutlinedPlaceholders':'Actually viewed blank, not counted as missing technical figures'},'suppliedMathematics':{q['id']:[f['expression']for f in q['solution']['formulas']]for q in qs if q['solution']['formulas']},'courseReviewHandling':'Pages1936–1939 retain distinct applied module-boundary questions rather than week-number recall; their source is a retrospective summary, not a fresh derivation.','externalEvidenceScope':'Primary ISO catalog abstracts only; no full standards text, certification or current legal advice.'})
wr(f'audits/{B}-review-manifest.json',{'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'batchId':B,'questions':74,'conceptFamilies':36,'actualPages':45,'examinablePages':39,'excludedPages':6,'packet':f'audits/blind-{B}.json','packetSha256':ph,'binding':f'audits/blind-binding-{B}.json','bindingSha256':sha(f'audits/blind-binding-{B}.json'),'questionHashes':{q['id']:qh(q)for q in qs},'sourceBounds':[1909,1953],'authorCheckGroups':32,'randomCases':1000,'randomAssertions':5000,'preflightChecks':391,'integrityTests':63,'sourceQualifications':8,'sourceQualificationsSha256':sha(f'audits/source-disputes-{B}.json'),'difficultyCounts':dict(collections.Counter(q['difficulty']for q in qs)),'formulaQuestions':sum(bool(q['solution']['formulas'])for q in qs),'independentReviewRequired':True,'runtimeScope':'Default Python standard library only; no executable lecture code, hardware run, model inference, installation or browser claim.'})
(R/f'audits/handoffs/{B}.md').write_text(f'''L60 frozen:74 draft questions,36 concept families,45 actual pages1909–1953;39 examinable and6 explicitly excluded. All observed footer strings and actual notes are persisted in data/inspection-batches/{B}.json. No printed code/equations/tables/technical diagrams; five supplied mathematical examples are clearly separate from source claims.
Packet: audits/blind-{B}.json
SHA256: {ph}
Minimal binding: audits/blind-binding-{B}.json
SHA256: {sha(f'audits/blind-binding-{B}.json')}
Page/angle ledger: audits/{B}-page-concept-coverage.json. Eight scope qualifications: audits/source-disputes-{B}.json. Primary ISO catalog abstracts are versioned; no full standard, legal advice or certification is claimed.
Author checks:32 deterministic groups plus1000 varied cases/5000 assertions in default Python standard library.391 preflight checks and63 integrity tests passed. Author review is not independent verification; all74 remain draft. Preserve packet and do not rerun full author/inspection scripts after freeze.
Next: L56 eight flags/three gaps, preserving59 accepted hashes, then allocated assignment Weeks7–12 from audits/assignment-coverage/author-handoff-weeks-07-12-v2.json. L54 v3 one-item source repair has been sent separately.
Restrictions: no restricted /tmp/robotics-l35-venv; no L49 original-notebook retrieval or alternate route; no NLTK corpus download; no denied L48 dependency/model route; no canonical/Git writes. Actual downloaded-file browser QA remains blocked. Supported source reads and default-environment deterministic checks remain available.
''')
print('PACKET',ph);print('BINDING',sha(f'audits/blind-binding-{B}.json'))
