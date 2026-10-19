#!/usr/bin/env python3
"""Freeze author drafts, never independent approval or canonical integration."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1];B='W11-L54'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert not (R/f'audits/{B}-review-manifest.json').exists(),'Already frozen'
b=read(f'data/question-batches/{B}.json');ins=read(f'data/inspection-batches/{B}.json');pre=read(f'audits/{B}-preflight.json');checks=read(f'audits/{B}-author-checks.json');issues=read(f'audits/source-disputes-{B}.json')
qs=sorted(b['questions'],key=lambda q:q['id']);nf=sum(len(q['solution']['formulas'])for q in qs)
assert pre['validation']['valid']and checks['checkGroups']==49 and len(qs)==87 and nf==35
assert len(ins['slides'])==30 and all(s['visualInspection']['status']=='complete'for s in ins['slides'])
assert all(q['status']=='draft'and not q['reviewIds']for q in qs)
blind=[]
for q in qs:
 z={**{k:q[k]for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions']},'citations':[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]}
 if q.get('primaryEvidence'):z['externalSources']=[{k:v for k,v in e.items()if k in ['title','url','version','localEvidence']}for e in q['primaryEvidence']]
 blind.append(z)
write(f'audits/blind-{B}.json',blind);packetsha=sha(f'audits/blind-{B}.json')
write(f'audits/blind-binding-{B}.json',{'packetSha256':packetsha,'questions':[dict(id=q['id'],version=q['version'],sha256=qhash(q))for q in qs]})
coverage=[]
for s in ins['slides']:
 ids=[q['id']for q in qs if any(c['physicalPage']==s['physicalPage']for c in q['citations'])]
 assert s['disposition']!='examinable'or ids
 coverage.append(dict(physicalPage=s['physicalPage'],printedSlideNumber=s['printedSlideNumber'],disposition=s['disposition'],exclusionReason=s['exclusionReason'],conceptIds=s['conceptIds'],questionIds=ids,actualVisualInspectionComplete=True,inspectionTimestamp=s['visualInspection']['inspectedAt'],notes=s['visualInspection']['notes']))
write(f'audits/{B}-coverage-author.json',{'status':'Author coverage claim pending independent challenge','pages':coverage,'conceptFamilies':22,'draftQuestions':87,'formulaRecords':nf,'conceptAngles':[dict(id=c['id'],angles=c['examinationAngles'],questionIds=c['questionIds'],status='Draft coverage pending independent challenge')for c in b['concepts']],'excludedPages':[1715,1716,1717,1743,1744],'repeatedSummaryPage':1742,'codeTranscriptions':['sources/supplemental/L54-slide-fault-code.py.txt','sources/supplemental/L54-slide-ik-code.py.txt'],'executionScope':checks['executionScope'],'scopeCaveats':['No original notebook URL among the actual PDF annotations; no original notebook run claimed.','SVC source seed0 is printed. IK generator and split are unseeded in source; fresh full run uses explicitly supplied external np.random.seed(54).','Printed historical9.82cm test mean and1.6773/1.5809rad target prediction are not the fresh run outputs.','mglearn architecture-display fragment inspected but not executed because package absent; no installation.','Additional numerical configurations and the hard-margin constraint are explicitly supplied/derived, not asserted to be printed examples.']})
write(f'audits/{B}-review-manifest.json',{'batchId':B,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blindPacket':f'audits/blind-{B}.json','blindPacketSha256':packetsha,'blindBinding':f'audits/blind-binding-{B}.json','questionSha256':{q['id']:qhash(q)for q in qs},'questionCount':87,'sourceBounds':[1715,1744],'sourceSha256':ins['slides'][0]['sourceSha256'],'inspectionCount':30,'conceptCount':22,'formulaRecordCount':nf,'sourceQualificationCount':len(issues),'sourceQualificationSha256':sha(f'audits/source-disputes-{B}.json'),'authorChecks':f'audits/{B}-author-checks.json','authorCheckGroups':49,'randomCases':1000,'randomAssertions':4000,'fullCodeReport':f'audits/{B}-full-code-author.json','independentReviewPending':True,'preflightValid':True,'integrityTestsPassed':58})
(R/f'audits/handoffs/{B}.md').write_text(f'''L54 frozen: 87 draft questions, 22 concept families, 35 formula records. All 30 actual pages 1715–1744 inspected and persisted in data/inspection-batches/{B}.json, footer strings 1–30 separate. Five non-examinable pages excluded; summary1742 is repeated. All24 examinable pages have citations. Independent review pending; author checks are not independent verification.

Answer-free packet: audits/blind-{B}.json
SHA256: {packetsha}
Minimal answer-free binding: audits/blind-binding-{B}.json
Binding SHA256: {sha(f'audits/blind-binding-{B}.json')}
Post-answer manifest: audits/{B}-review-manifest.json
Coverage ledger: audits/{B}-coverage-author.json
Source qualifications: audits/source-disputes-{B}.json ({len(issues)} records)

Author checks:49 groups,1000 random cases/4000 assertions, all passed. Full SVC and40000-point IK model executable statements transcribed from actual slides and executed in the existing default Python, no installations. Runtime report audits/{B}-full-code-author.json records exact command interpreter, package versions/paths/hashes, times and outputs. Source SVC seed0 gives100% synthetic score. IK has an explicitly supplied external seed54 because source generator/split are unseeded; it completed48epochs and printed9.34cm. This is not the historical9.82cm/1.6773,1.5809rad output. All numeric options checked, including historical FK norm15.74cm. No original notebook link among PDF annotations; no original notebook claim. mglearn absent, plotting-library fragment not executed. In-memory schema validation,258 local preflight checks and58 integrity tests pass. Author and refiner are guarded against post-freeze regeneration.

Restrictions: no /tmp/robotics-l35-venv use after the installation incident; no L49 original-notebook retrieval or alternate route; no NLTK corpus download; no denied L48 dependency/model route. Actual downloaded-file browser QA remains blocked. Default deterministic environment and supported source reads remain permitted. L52 runtime boundary remains audits/W11-L52-runtime-boundary.json; frozen L52 unchanged.
Next assigned: L56 pages1777–1802. L53/L55 belong to UI author. No Git, canonical-bank or accepted-object writes.
''')
print('FROZEN',packetsha);print('BINDING',sha(f'audits/blind-binding-{B}.json'))
