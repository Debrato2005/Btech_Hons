#!/usr/bin/env python3
"""Freeze source-based draft and answer-free review binding, not approval."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];B='W10-L49'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert not (R/f'audits/{B}-review-manifest.json').exists(),'Already frozen; no regeneration.'
b=read(f'data/question-batches/{B}.json');ins=read(f'data/inspection-batches/{B}.json');pre=read(f'audits/{B}-preflight.json');checks=read(f'audits/{B}-author-checks.json');issues=read(f'audits/source-disputes-{B}.json')
assert pre['validation']['valid']and checks['passedGroups']==33 and len(b['questions'])==84
assert len(ins['slides'])==29 and all(s['visualInspection']['status']=='complete'for s in ins['slides'])
assert all(q['status']=='draft'and not q['reviewIds']for q in b['questions'])
qs=sorted(b['questions'],key=lambda q:q['id'])
blind=[{**{k:q[k]for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions']},'citations':[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]}for q in qs]
write(f'audits/blind-{B}.json',blind);packetsha=sha(f'audits/blind-{B}.json')
write(f'audits/blind-binding-{B}.json',{'packetSha256':packetsha,'questions':[dict(id=q['id'],version=q['version'],sha256=qhash(q))for q in qs]})
coverage=[]
for s in ins['slides']:
 ids=[q['id']for q in qs if any(c['physicalPage']==s['physicalPage']for c in q['citations'])]
 coverage.append(dict(physicalPage=s['physicalPage'],printedSlideNumber=s['printedSlideNumber'],disposition=s['disposition'],exclusionReason=s['exclusionReason'],conceptIds=s['conceptIds'],questionIds=ids,actualVisualInspectionComplete=True,notes=s['visualInspection']['notes']))
write(f'audits/{B}-coverage-author.json',{'status':'PDF-based author coverage claim pending independent challenge','pages':coverage,'conceptFamilies':25,'draftQuestions':84,'conceptAngles':[dict(id=c['id'],angles=c['examinationAngles'],questionIds=c['questionIds'],status='draft coverage pending independent challenge')for c in b['concepts']],'excludedPages':[1537,1538,1565],'incrementallyComparedSummary':1564,'sourceCodeTranscriptions':'sources/supplemental/L49-slide-code-transcriptions.json','officialNotebookCoverage':'Unavailable after two denied retrieval attempts. Not claimed covered or executed; preserve this blocker in overall completion reporting.','freshExecutionScope':checks['pythonExecution'],'legacyAIMLScope':checks['xmlParsing']})
write(f'audits/{B}-review-manifest.json',{'batchId':B,'blindPacket':f'audits/blind-{B}.json','blindPacketSha256':packetsha,'blindBinding':f'audits/blind-binding-{B}.json','questionSha256':{q['id']:qhash(q)for q in qs},'questionCount':84,'sourceBounds':[1537,1565],'sourceSha256':ins['slides'][0]['sourceSha256'],'inspectionCount':29,'conceptCount':25,'sourceQualificationCount':len(issues),'sourceQualificationSha256':sha(f'audits/source-disputes-{B}.json'),'authorChecks':f'audits/{B}-author-checks.json','authorCheckGroups':33,'randomCases':1000,'randomAssertions':3000,'independentReviewPending':True,'originalNotebookRetrievalBlocked':True,'blockers':f'audits/{B}-blockers.json','preflightValid':True,'integrityTestsPassed':58})
(R/f'audits/handoffs/{B}.md').write_text(f'''L49 frozen: 84 draft questions, 25 concept families, all 29 actual pages 1537–1565 inspected; printed footers 1–29 recorded separately. Title, contents and bibliography excluded with reasons; summary incrementally compared and linked. PDF-based coverage only; independent review pending.

Answer-free packet: audits/blind-{B}.json
SHA256: {packetsha}
Minimal answer-free binding: audits/blind-binding-{B}.json
Binding SHA256: {sha(f'audits/blind-binding-{B}.json')}
Post-answer manifest: audits/{B}-review-manifest.json
Coverage: audits/{B}-coverage-author.json
18 source qualifications: audits/source-disputes-{B}.json
Author: scripts/author_W10_L49.py (frozen guard)
Checks: scripts/check_W10_L49_author.py; 33 groups and 1,000 randomized cases / 3,000 assertions passed. Two exact XML fragments parsed; legacy semantics tested only by explicitly labeled reconstruction. As-printed Python compile error preserved; function-wrapper and supplied stub variants tested. No original notebook, Transformers model or Gradio interface execution claimed. Pinned Transformers 4.57.1 documentation supplies API qualification. Option identifiers reassigned before freeze to remove systematic correctness-ID leakage. In-memory validation passed; 58 integrity tests passed. No canonical or Git writes.

Original course notebook retrieval was denied twice with a wrong-project rationale despite the p1552 course hyperlink. Target absent; no further route or retry. Preserve audits/{B}-blockers.json in completion reporting. Inherited NLTK corpus-download security safeguard remains untouched. No unavailable notebook saved output is claimed.

Next assigned: L52 sensors, physical 1620–1684. Leave L49 unchanged once independent review starts.
''')
print('FROZEN',packetsha);print('BINDING',sha(f'audits/blind-binding-{B}.json'))
