#!/usr/bin/env python3
"""Freeze nine changed L56 objects, preserving every earlier accepted hash."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1];B='W12-L56'
def rd(p):return json.loads((R/p).read_text())
def wr(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qh(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert not(R/f'audits/{B}-v2-repair-manifest.json').exists()
b=rd(f'data/question-batches/{B}.json');n=rd(f'audits/{B}-v2-author-repair-notes.json');a=rd(f'audits/{B}-v2-author-checks.json');p=rd(f'audits/{B}-v2-preflight.json');qs=sorted([q for q in b['questions']if q['id']in n['changedQuestionIds']],key=lambda q:q['id'])
assert len(b['questions'])==68 and len(qs)==9 and a['checkGroups']==44 and a['randomAssertions']==6000
assert a['questionBatchSha256']==sha(f'data/question-batches/{B}.json')and p['validation']['valid']and len(p['localChecks'])==59
assert sha(f'audits/source-disputes-{B}.json')==n['sourceQualificationsUnchangedSha256']
for i,h in n['acceptedQuestionHashes'].items():assert qh(next(q for q in b['questions']if q['id']==i))==h
assert 'Ran 63 tests'in(R/f'audits/{B}-v2-integrity-run.txt').read_text()and(R/f'audits/{B}-v2-integrity-run.txt').read_text().rstrip().endswith('OK')
blind=[]
for q in qs:
 z={k:q[k]for k in['id','version','stem','selectionMode','type','difficulty','options','assumptions']};z['citations']=[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]
 if q.get('primaryEvidence'):z['externalSources']=[{k:v for k,v in e.items()if k in['title','url','version','localEvidence']}for e in q['primaryEvidence']]
 blind.append(z)
wr(f'audits/blind-{B}-v2.json',blind);ph=sha(f'audits/blind-{B}-v2.json')
wr(f'audits/blind-binding-{B}-v2.json',{'packetSha256':ph,'questions':[{'id':q['id'],'version':q['version'],'sha256':qh(q)}for q in qs]})
wr(f'audits/{B}-v2-repair-manifest.json',{'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'batchId':B,'currentQuestions':68,'revisedFlags':8,'newQuestions':1,'acceptedPreserved':59,'acceptedQuestionHashes':n['acceptedQuestionHashes'],'packet':f'audits/blind-{B}-v2.json','packetSha256':ph,'binding':f'audits/blind-binding-{B}-v2.json','bindingSha256':sha(f'audits/blind-binding-{B}-v2.json'),'sourceBounds':[1777,1802],'revisitedPages':15,'uniqueInspectionCountUnchanged':26,'sourceQualificationsUnchangedSha256':n['sourceQualificationsUnchangedSha256'],'gapMapping':n['gapMapping'],'authorCheckGroups':44,'randomCases':1000,'randomAssertions':6000,'preflightChecks':59,'integrityTests':63,'independentReviewRequired':True,'archive':n['archive'],'executionScope':'Default Python standard-library models only; no original source code, ROS, model, live API, audio device or hardware run.','currentPrimarySources':[{'url':'https://developers.openai.com/api/docs/guides/realtime-conversations','inspectedAt':'2026-10-20','region':'Interruptions and WebSocket client playback/truncation responsibilities'},{'url':'https://developers.openai.com/api/docs/guides/realtime-vad','inspectedAt':'2026-10-20','region':'Conversation create_response/interrupt_response controls'}]})
(R/f'audits/handoffs/{B}-repair.md').write_text(f'''L56 v2 frozen: eight revised flags plus one new whole-graph gap;68 current questions, all59 accepted content hashes unchanged. Two replacements close the interruption-state and joint-resource gaps; the addition closes the declared graph-failure gap. Independent re-review is required.
Packet audits/blind-{B}-v2.json SHA256 {ph}
Minimal binding audits/blind-binding-{B}-v2.json SHA256 {sha(f'audits/blind-binding-{B}-v2.json')}
Post-answer manifest audits/{B}-v2-repair-manifest.json. Fifteen actual source revisits are recorded separately; unique26page inspection coverage is unchanged. All7 source qualification records remain byte-identical. Source functional diagrams are not treated as exact API implementation or required-input contracts; supplied policies are explicit. Primary OpenAI interruption/VAD documentation was rechecked without executing the API.
Author checks:44 groups plus1000 varied cases/6000 assertions.59 local preflight checks and63 integrity tests passed. First-draft spacing cleanup briefly altered identifiers; identifier-safe refinement caught and restored them before freeze, with accepted objects always untouched. Do not rerun the old full author script or guarded repairs after freeze.
Next: assignment Weeks7–12, preserving immutable original item text/options/keys and defects under the contracts reviewer’s minimal preservation rules. No audit review is inherited by authored questions.
Restrictions: no /tmp/robotics-l35-venv; no L49 original-notebook retrieval or alternate route; no NLTK corpus download; no denied L48 dependency/model route; no denied ROS2 documentation retry/bypass; no canonical/Git writes. Actual downloaded-file browser QA remains blocked. Supported source reads and default Python deterministic checks allowed.
''')
print('PACKET',ph);print('BINDING',sha(f'audits/blind-binding-{B}-v2.json'))
