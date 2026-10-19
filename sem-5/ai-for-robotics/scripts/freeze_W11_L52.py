#!/usr/bin/env python3
"""Freeze L52 source-based drafts and answer-free binding; no approval or canonical writes."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1];B='W11-L52'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert not (R/f'audits/{B}-review-manifest.json').exists(),'Already frozen; use versioned repair.'
b=read(f'data/question-batches/{B}.json');ins=read(f'data/inspection-batches/{B}.json');pre=read(f'audits/{B}-preflight.json');checks=read(f'audits/{B}-author-checks.json');issues=read(f'audits/source-disputes-{B}.json')
assert pre['validation']['valid']and checks['checkGroups']==58 and len(b['questions'])==132
assert len(ins['slides'])==65 and all(s['visualInspection']['status']=='complete'for s in ins['slides'])
assert all(q['status']=='draft'and not q['reviewIds']for q in b['questions'])
qs=sorted(b['questions'],key=lambda q:q['id']);blind=[]
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
write(f'audits/{B}-coverage-author.json',{'status':'Author coverage claim pending independent challenge','pages':coverage,'conceptFamilies':54,'draftQuestions':132,'formulaRecords':33,'conceptAngles':[dict(id=c['id'],angles=c['examinationAngles'],questionIds=c['questionIds'],status='Draft coverage pending independent challenge')for c in b['concepts']],'excludedPages':[1620,1621,1684],'sourceCodeTranscriptions':'sources/supplemental/L52-slide-code-transcriptions.json','freshDefaultExecutionScope':checks['executionScope'],'freshDefaultMetadata':'audits/W11-L52-default-metadata-author.json','historicalRuntimeBoundary':'audits/W11-L52-runtime-boundary.json','historicalVisionScope':'Five author observations after the reported 22:59 installation and before receipt of restriction; not independent validation. Four codec observations not rerun. Fresh default metadata count only.'})
write(f'audits/{B}-review-manifest.json',{'batchId':B,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blindPacket':f'audits/blind-{B}.json','blindPacketSha256':packetsha,'blindBinding':f'audits/blind-binding-{B}.json','questionSha256':{q['id']:qhash(q)for q in qs},'questionCount':132,'sourceBounds':[1620,1684],'sourceSha256':ins['slides'][0]['sourceSha256'],'inspectionCount':65,'conceptCount':54,'formulaRecordCount':33,'sourceQualificationCount':len(issues),'sourceQualificationSha256':sha(f'audits/source-disputes-{B}.json'),'authorChecks':f'audits/{B}-author-checks.json','authorCheckGroups':58,'randomCases':1000,'randomAssertions':4000,'freshDefaultMetadataChecks':3,'historicalVisionChecksExcludedFromIndependentValidation':5,'runtimeBoundary':f'audits/{B}-runtime-boundary.json','independentReviewPending':True,'preflightValid':True,'integrityTestsPassed':58})
(R/f'audits/handoffs/{B}.md').write_text(f'''L52 frozen: 132 draft questions, 54 concept families, 33 complete formula records. All 65 actual pages 1620–1684 inspected and persisted in data/inspection-batches/{B}.json; printed footer strings 1–65 are separate. Title, contents and thank-you pages excluded with reasons. All 62 examinable pages have question citations. Independent review pending.

Answer-free packet: audits/blind-{B}.json
SHA256: {packetsha}
Minimal answer-free binding: audits/blind-binding-{B}.json
Binding SHA256: {sha(f'audits/blind-binding-{B}.json')}
Post-answer manifest: audits/{B}-review-manifest.json
Page/concept ledger: audits/{B}-coverage-author.json
22 source qualifications: audits/source-disputes-{B}.json
11 exact statement transcriptions: sources/supplemental/L52-slide-code-transcriptions.json
Author scripts: scripts/author_W11_L52.py and scripts/refine_W11_L52.py are guarded against post-freeze regeneration.
Default-environment author checks: 58 groups, 1,000 random cases / 4,000 assertions. Ten C++ sketches use host Arduino-interface stubs, not AVR timing/hardware; exact missing-semicolon compile failure and explicitly repaired copy distinguished. Python vision code runs only with explicit cv2/YOLO/time stubs. Three additional default-runtime metadata/synthetic-array checks pass. No camera or checkpoint execution claimed. In-memory schema validation and 58 integrity tests pass.

Runtime boundary: audits/{B}-runtime-boundary.json. Five earlier vision observations occurred after the lead-reported 22:59 installation; dependency stability is NOT inferred. Artifact timestamps and unrecorded exact command start/end are disclosed. Four codec checks were not rerun. The preserved YAML label count was freshly checked in the default environment. Historical reproducer is disabled and original source archived. Never use /tmp/robotics-l35-venv again. No L49 original-notebook retrieval or alternate route, no NLTK corpus download, no denied L48 dependency/model route. Actual downloaded-file browser QA remains blocked.

Next assigned: L54 pages1715–1744, then L56 pages1777–1802. L53 and L55 belong to the UI author. No Git or canonical-bank writes. Leave L52 frozen during independent review.
''')
print('FROZEN',packetsha);print('BINDING',sha(f'audits/blind-binding-{B}.json'))
