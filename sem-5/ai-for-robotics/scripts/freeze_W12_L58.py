#!/usr/bin/env python3
"""Freeze authored drafts and answer-free evidence binding. No independent approval or canonical writes."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1];B='W12-L58'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert not(R/f'audits/{B}-review-manifest.json').exists()
b=read(f'data/question-batches/{B}.json');ins=read(f'data/inspection-batches/{B}.json');pre=read(f'audits/{B}-preflight.json');checks=read(f'audits/{B}-author-checks.json');issues=read(f'audits/source-disputes-{B}.json');qs=sorted(b['questions'],key=lambda q:q['id'])
assert len(qs)==85 and len(ins['slides'])==34 and len(b['concepts'])==29
assert checks['checkGroups']==41 and checks['questionBatchSha256']==sha(f'data/question-batches/{B}.json')
assert pre['validation']['valid']and len(pre['localChecks'])==209
assert all(q['status']=='draft'and not q['reviewIds']for q in qs)
assert 'Ran 63 tests' in(R/f'audits/{B}-integrity-run.txt').read_text()and(R/f'audits/{B}-integrity-run.txt').read_text().rstrip().endswith('OK')
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
 assert s['visualInspection']['status']=='complete'and(s['disposition']!='examinable'or ids)
 coverage.append(dict(physicalPage=s['physicalPage'],printedSlideNumber=s['printedSlideNumber'],disposition=s['disposition'],exclusionReason=s['exclusionReason'],conceptIds=s['conceptIds'],questionIds=ids,actualVisualInspectionComplete=True,inspectionTimestamp=s['visualInspection']['inspectedAt'],notes=s['visualInspection']['notes']))
write(f'audits/{B}-coverage-author.json',dict(status='Author coverage claim pending independent challenge',pages=coverage,conceptFamilies=29,draftQuestions=85,formulaRecords=7,conceptAngles=[dict(id=c['id'],angles=c['examinationAngles'],questionIds=c['questionIds'],status='Draft coverage pending independent challenge')for c in b['concepts']],excludedPages=[1843,1844,1875,1876],repeatedSummaryPage=1874,executionScope=checks['executionScope'],scopeCaveats=['Gazebo Classic editor interfaces are version-scoped; source still carries January2025 end-of-life notice.','Legacy move_base message labels are not claimed to be ROS2 interfaces.','Nav2 diagram has later components; Humble demonstration does not establish all diagram components are installed. Behavior Server docking extensibility is not called a source error.','SDF also models individual robots; global costmaps can include live obstacle updates.','Literal waffle. and visual command wraps are preserved separately from explicit repairs; map path is a placeholder.','SLAM toolbox overview and concrete Cartographer commands are not silently conflated.','Demonstration screenshot names burger while setup specifies waffle; no unchanged model continuity is claimed.','Eight command groups are transcribed and parsed, not executed. No ROS/Gazebo executables available; no installation attempted.','Video-labeled page inspected as a still; no video/notebook link is embedded. Screenshot status/ETA is historical evidence, not fresh execution.','All seven numerical formula examples and the abstract behavior-tree policy are explicitly supplied/derived exercises.']))
write(f'audits/{B}-review-manifest.json',dict(batchId=B,frozenAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),blindPacket=f'audits/blind-{B}.json',blindPacketSha256=packetsha,blindBinding=f'audits/blind-binding-{B}.json',questionSha256={q['id']:qhash(q)for q in qs},questionCount=85,sourceBounds=[1843,1876],sourceSha256=ins['slides'][0]['sourceSha256'],inspectionCount=34,conceptCount=29,formulaRecordCount=7,sourceQualificationCount=len(issues),sourceQualificationSha256=sha(f'audits/source-disputes-{B}.json'),authorChecks=f'audits/{B}-author-checks.json',authorCheckGroups=41,randomCases=1000,randomAssertions=4000,independentReviewPending=True,preflightValid=True,preflightChecks=209,integrityTestsPassed=63))
(R/f'audits/handoffs/{B}.md').write_text(f'''L58 frozen: 85 drafts, 29 concept families, 7 complete formula records. All34 actual pages1843–1876 persisted in data/inspection-batches/{B}.json, footers1–34. Title/objectives/references/thanks excluded; summary1874 repeated with incremental check. Independent review required, not self-approved.
Answer-free packet: audits/blind-{B}.json
SHA256: {packetsha}
Minimal binding: audits/blind-binding-{B}.json
Binding SHA256: {sha(f'audits/blind-binding-{B}.json')}
Post-answer manifest: audits/{B}-review-manifest.json
Page/concept ledger: audits/{B}-coverage-author.json
Source qualifications: audits/source-disputes-{B}.json,9records.
Author checks: audits/{B}-author-checks.json,41groups plus1000varied cases/4000assertions. DefaultPython standardlibrary only. Eight source command groups parsed, not executed; ROS2/Gazebo executables absent, no installation attempted. Formula checks cover grid coordinates, feasible paths, reaction/braking clearance, footprint margin, particle normalization, simulation-clock ratio and conditional screenshot ETA. Actual legacy/Nav2 graph paths and status changes checked. Primary version documentation linked at item level. All209preflight checks and63integrity tests pass; no canonical writes. Commands/period/placeholder repairs explicitly labeled; no video or notebook executed. Author/refiner/inspection scripts guarded after freeze.
Next: L54 now17flags/3gaps, preserve70accepted objects. Read both audits/W11-L54-contracts-review-summary.json and audits/W11-L54-later-duplicate-review-summary.json. Seven metre/mm errors are author text errors; distinguish raw mislabeled historical print from physical mean. Then L60 source coverage, then L56eight flags/three gaps preserving59accepted objects unless parent reallocates.
Restrictions: no /tmp/robotics-l35-venv, L49 original-notebook retrieval or alternate route, NLTK corpus download, denied L48 dependency/model route, Git or canonical-bank writes. Actual downloaded-file browser QA remains blocked. Supported source reads/defaultPython deterministic checks allowed.
''')
print('FROZEN',packetsha);print('BINDING',sha(f'audits/blind-binding-{B}.json'))
