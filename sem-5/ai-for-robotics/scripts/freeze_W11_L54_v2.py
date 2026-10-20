#!/usr/bin/env python3
"""Freeze changed-only L54 v2 packet. No self-approval or canonical writes."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1];B='W11-L54'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert not (R/f'audits/{B}-v2-repair-manifest.json').exists()
b=read(f'data/question-batches/{B}.json');notes=read(f'audits/{B}-v2-author-repair-notes.json');checks=read(f'audits/{B}-v2-author-checks.json');pre=read(f'audits/{B}-v2-preflight.json');qs=sorted([q for q in b['questions']if q['id']in notes['changedQuestionIds']],key=lambda q:q['id'])
assert len(qs)==19 and len(b['questions'])==89 and checks['checkGroups']==31 and checks['questionBatchSha256']==sha(f'data/question-batches/{B}.json')
assert pre['validation']['valid']and len(pre['localChecks'])==125
assert all(q['status']=='draft'and not q['reviewIds']for q in qs)
for i,h in notes['acceptedQuestionHashes'].items():assert qhash(next(q for q in b['questions']if q['id']==i))==h
assert 'Ran 63 tests'in(R/f'audits/{B}-v2-integrity-run.txt').read_text()and(R/f'audits/{B}-v2-integrity-run.txt').read_text().rstrip().endswith('OK')
blind=[]
for q in qs:
 z={**{k:q[k]for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions']},'citations':[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]}
 if q.get('primaryEvidence'):z['externalSources']=[{k:v for k,v in e.items()if k in ['title','url','version','localEvidence']}for e in q['primaryEvidence']]
 blind.append(z)
write(f'audits/blind-{B}-v2.json',blind);ph=sha(f'audits/blind-{B}-v2.json')
write(f'audits/blind-binding-{B}-v2.json',{'packetSha256':ph,'questions':[dict(id=q['id'],version=q['version'],sha256=qhash(q))for q in qs]})
write(f'audits/{B}-v2-repair-manifest.json',{'batchId':B,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packet':f'audits/blind-{B}-v2.json','packetSha256':ph,'binding':f'audits/blind-binding-{B}-v2.json','bindingSha256':sha(f'audits/blind-binding-{B}-v2.json'),'currentQuestions':89,'changedPacketItems':19,'revisedFlags':17,'newQuestions':2,'acceptedQuestionHashes':notes['acceptedQuestionHashes'],'questionSha256':{q['id']:qhash(q)for q in qs},'sourceBounds':[1715,1744],'sourceQualificationsUnchangedSha256':notes['sourceQualificationSha256'],'gapMapping':{'L54-G01':'W11-L54-P1729-Q08','L54-G02':'W11-L54-P1737-Q01','L54-G03':'W11-L54-P1730-Q08'},'authorRevisits':16,'uniqueInspectionsUnchanged':30,'authorCheckGroups':31,'randomCases':1000,'randomAssertions':4000,'preflightChecks':125,'integrityTestsPassed':63,'independentReviewRequired':True,'priorVersions':'audits/archive/W11-L54-v1-before-v2','sourceDefectDistinction':'Seven dimensional defects were author text, not source errors. No source qualification was removed or silently normalized.'})
(R/f'audits/handoffs/{B}-repair.md').write_text(f'''L54 v2 frozen: 17 revised flags plus two new questions; the replaced duplicate IK item closes the third bounded gap. 89 current questions, all70 accepted objects/hashes unchanged. All12 source qualifications remain byte-identical. No independent approval of edits claimed.
Answer-free packet: audits/blind-{B}-v2.json
SHA256: {ph}
Minimal binding: audits/blind-binding-{B}-v2.json
SHA256: {sha(f'audits/blind-binding-{B}-v2.json')}
Post-answer manifest: audits/{B}-v2-repair-manifest.json. Author checks: audits/{B}-v2-author-checks.json,31groups plus1000varied cases/4000assertions in defaultPython standard library only.125local preflight checks and63integrity tests passed. Canonical eligibility of unchanged objects retained only in memory during validation; no canonical write.
16 actual author revisits are persisted in audits/{B}-v2-author-revisits.json; unique source inspection count remains30. Source regions and exact printed footers retained. Seven dimensional errors are author-text fixes; the deliberately wrong-unit supplied print scenario now distinguishes raw mislabeled output from physical mean. No model inference, installation or hardware claim.
All existing accepted work is unchanged; do not rerun old full author scripts or the guarded v2 repair after freeze. Next L60 coverage, followed by allocated L56 repairs.
Restrictions: no /tmp/robotics-l35-venv, L49 original-notebook retrieval or alternate route, NLTK corpus download, denied L48 dependency/model route, Git or canonical writes. Actual downloaded-file browser QA remains blocked. Supported source reads and defaultPython deterministic checks allowed.
''')
print('FROZEN',ph);print('BINDING',sha(f'audits/blind-binding-{B}-v2.json'))
