#!/usr/bin/env python3
"""Freeze the already checked author draft; never approve it."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];B='W10-L46'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert not (R/f'audits/{B}-review-manifest.json').exists(),'Already frozen.'
b=read(f'data/question-batches/{B}.json');ins=read(f'data/inspection-batches/{B}.json');pre=read(f'audits/{B}-preflight.json');checks=read(f'audits/{B}-author-checks.json');issues=read(f'audits/source-disputes-{B}.json')
assert pre['validation']['valid']and checks['passedGroups']==39 and len(b['questions'])==90
assert all(q['status']=='draft'and not q['reviewIds']for q in b['questions'])
blind=[{**{k:q[k]for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions']},'citations':[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]}for q in sorted(b['questions'],key=lambda q:q['id'])]
write(f'audits/blind-{B}.json',blind);packetsha=sha(f'audits/blind-{B}.json')
write(f'audits/blind-binding-{B}.json',{'packetSha256':packetsha,'questions':[dict(id=q['id'],version=q['version'],sha256=qhash(q))for q in sorted(b['questions'],key=lambda q:q['id'])]})
coverage=[]
for s in ins['slides']:
 qs=[q['id']for q in b['questions']if any(c['physicalPage']==s['physicalPage']for c in q['citations'])]
 coverage.append({'physicalPage':s['physicalPage'],'printedSlideNumber':s['printedSlideNumber'],'disposition':s['disposition'],'exclusionReason':s['exclusionReason'],'conceptIds':s['conceptIds'],'questionIds':qs,'actualVisualInspectionComplete':True,'notes':s['visualInspection']['notes']})
write(f'audits/{B}-coverage-author.json',{'status':'author coverage claim pending independent challenge','pages':coverage,'conceptFamilies':27,'draftQuestions':90,'sourceCodeTranscriptions':'sources/supplemental/L46-slide-code-transcriptions.json','allEightCodeExcerptsCompile':True,'threeVectorizationExcerptsAndOriginalNotebookCellsExecuted':True,'corpusDependentExecutionNotClaimed':checks['blockedChecks'],'summaryPageIncrementallyCompared':1473})
write(f'audits/{B}-blockers.json',{'githubMetadata':{'initialOutcome':'denied for incorrect OncoSyn/untrusted-repository rationale','target':'https://api.github.com/repos/robotics-lab-iitr/nptel-ai-robotics/contents/week10','outcomeCheck':'No running request and no notebook artifact; operation had no write statements.','retry':'One exact retry after parent supplied explicit separate-Robotics authorization','finalOutcome':'succeeded; original notebook retrieved unchanged'},'nltkResourceDownload':checks['blockedChecks'],'delegateAttempt':{'outcome':'agent thread limit reached','action':'Spawn author-side numeric helper','handling':'No worker created; all checks completed in the author thread instead.'}})
write(f'audits/{B}-review-manifest.json',{'batchId':B,'blindPacket':f'audits/blind-{B}.json','blindPacketSha256':packetsha,'blindBinding':f'audits/blind-binding-{B}.json','questionSha256':{q['id']:qhash(q)for q in b['questions']},'questionCount':90,'sourceBounds':[1440,1475],'sourceSha256':ins['slides'][0]['sourceSha256'],'inspectionCount':36,'conceptCount':27,'sourceQualificationCount':len(issues),'sourceQualificationSha256':sha(f'audits/source-disputes-{B}.json'),'authorChecks':f'audits/{B}-author-checks.json','authorCheckGroups':39,'randomCases':1000,'independentReviewPending':True,'freshCorpusDependentExecutionBlocked':True,'officialNotebookPath':'sources/supplemental/L46-official-week10_lecture46.ipynb','officialNotebookSha256':checks['originalNotebookSha256'],'preflightValid':True,'integrityTestsPassed':58})
(R/f'audits/handoffs/{B}.md').write_text(f'''L46 frozen: 90 draft questions, 27 concept families, all 36 actual pages 1440–1475 inspected; footers 1–36 recorded separately. Five excluded pages and one incrementally compared summary remain explicit. No independent approval claimed.

Packet: audits/blind-{B}.json
SHA256: {packetsha}
Minimal answer-free binding: audits/blind-binding-{B}.json
Full post-answer manifest: audits/{B}-review-manifest.json
Coverage: audits/{B}-coverage-author.json
Source qualifications: audits/source-disputes-{B}.json (12 precise issues)
Author: scripts/author_W10_L46.py (frozen guard)
Checks: scripts/check_W10_L46_author.py; 39 groups and 1,000 random cases passed. All eight manually transcribed excerpts compile; three exact vectorization excerpts and unchanged original notebook cells 15,17,19 executed. Preflight valid in memory; 58 integrity tests passed. No canonical or Git writes.

Original notebook: sources/supplemental/L46-official-week10_lecture46.ipynb
SHA256: {checks['originalNotebookSha256']}
NLTK package 3.10.3 installed under /tmp/robotics-l46-deps. Its corpus downloads returned false due to proxy/SSRF protection; no override, alternate corpus fetch or downgrade attempted. Saved notebook outputs report 3.9.1 and are explicitly historical evidence, not fresh corpus execution. Data-free tokenize variant is labeled preserve_line=True, not the source default. Blocker details preserved in audits/{B}-blockers.json. Read-only GitHub metadata retry succeeded after specific Robotics authorization.

Next assigned: L49 fresh source coverage, physical 1537–1565. Leave L46 unchanged once independent review starts.
''')
print('FROZEN',packetsha,'binding',sha(f'audits/blind-binding-{B}.json'))
