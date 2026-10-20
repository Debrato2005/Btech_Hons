"""Freeze fourteen L57 repairs for a different reviewer, with neutral blind locators."""
from pathlib import Path
import json,copy,hashlib,datetime,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors,validate_bank
from authoring_helpers import SHA
B='W12-L57';WHO='build_offline_study_interface:L57-v2-repair'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
assert not(R/f'audits/{B}-v2-repair-manifest.json').exists(),'Already frozen'
b=read(f'data/question-batches/{B}.json');old=read(f'data/history/{B}/{B}-v1.json');rev=read(f'audits/{B}-independent-review-summary.json');later=read(f'audits/{B}-later-duplicate-review-summary.json');accepted=later['acceptedQuestionHashes'];flags={x['questionId']for x in rev['flaggedQuestions']}|{later['questionId']};oq={q['id']:q for q in old['questions']};changed=[q for q in b['questions']if q['id']in flags];ch=read(f'audits/{B}-v2-author-checks.json');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert len(b['questions'])==86 and len(changed)==14 and len(accepted)==72
for q in changed:
 assert q['version']==2 and q['status']=='draft' and not q['reviewIds'];q['authorCheckEvidence']={'path':f'audits/{B}-v2-author-checks.json','sha256':sha(f'audits/{B}-v2-author-checks.json'),'independentReview':False,'scope':ch['scope']}
 if 'conflictResolution'in q:q['conflictResolution'].update(sourceId='lectures',sourceSha256=SHA,questionVersion=q['version'],basis=q['solution']['justification'])
qq={q['id']:q for q in b['questions']}
for i,h in accepted.items():assert qq[i]==oq[i] and question_hash(qq[i])==h,i
assert {q['id']for q in b['questions']if q!=oq[q['id']]}==flags
for q in old['questions']:
 if 'conflictResolution'in q:assert q['conflictResolution']['sourceClaim']==qq[q['id']]['conflictResolution']['sourceClaim']
ins=read(f'data/inspection-batches/{B}.json')
for s in ins['slides']:s['conceptIds']=list(dict.fromkeys(s['conceptIds']+[c['id']for c in b['concepts']if s['id']in c['slideIds']]))
for kind,items in [('question',b['questions']),('concept',b['concepts']),('slide',ins['slides'])]:
 schema=read(f'data/schema.{kind}.json')
 for x in items:assert not schema_errors(x,schema),(x['id'],schema_errors(x,schema))
bank=read('data/bank.json');cq={q['id']:q for q in bank['questions']};bank['questions']=[q for q in bank['questions']if not q['id'].startswith(B+'-')]+[copy.deepcopy(cq[q['id']])if q['id']in accepted and q['id']in cq and question_hash(cq[q['id']])==question_hash(q)else copy.deepcopy(q)for q in b['questions']];bank['concepts']=[c for c in bank['concepts']if not c['id'].startswith(B+'-')]+copy.deepcopy(b['concepts']);sm={s['id']:s for s in ins['slides']}
for i,s in enumerate(bank['slides']):
 if s['id']in sm:
  ns=copy.deepcopy(sm[s['id']]);ns['conceptIds']=list(dict.fromkeys([c for c in s['conceptIds']if not c.startswith(B+'-')]+ns['conceptIds']));bank['slides'][i]=ns
report=validate_bank(bank,root=R,check_files=False);write(f'audits/{B}-v2-preflight-validation.json',report);assert report['valid'],report['errors']
write(f'data/question-batches/{B}.json',b);write(f'data/inspection-batches/{B}.json',ins)
packet=[]
for q in changed:
 x={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:
  c.pop('evidenceText',None);c['locator']=f"Lecture L57, physical PDF page {c['physicalPage']}, printed footer {c['physicalPage']-1802}: inspect the {c['kind']} content on this source page. Neutral review locator."
 if q.get('primaryEvidence'):x['externalSources']=[{k:v for k,v in e.items()if k in ('title','url','version')}for e in q['primaryEvidence']]
 packet.append(x)
pp=f'audits/blind-{B}-v2.json';write(pp,packet)
issues={'batchId':B,'updatedAt':now,'originalIssueLedger':f'audits/{B}-source-issues.json','originalIssueLedgerSha256':sha(f'audits/{B}-source-issues.json'),'allFiveOriginalSourceClaimsPreserved':True,'globalSourceResolution':False,'changedLocalQualifications':{q['id']:q['conflictResolution']for q in changed if 'conflictResolution'in q},'revisionScope':['Q014 separates validity of contact equations from conditional rank needed for unique recovery.','Q036 explicitly marks the lecture pose-detection pages as premises rather than complete printed prerequisites, adds p1820 and p1839, and retains official OpenCV 4.13.0 primary evidence.','Q059 makes scalar atomicity, arbitrary interleavings and immutable-record publication premises explicit.','Q005 replaces a generic exact duplicate stem with a specific KSS responsibility scenario.'],'executionLimit':'No OpenCV runtime, robot/controller/network operations, omitted robosync.src, video or browser execution. Only default NumPy and inert synthetic state models.'};write(f'audits/{B}-v2-source-issues.json',issues)
obs=read(f'audits/{B}-v2-repair-source-observations.json')
m={'batchId':B,'revisionAuthorId':WHO,'frozenAt':now,'sourceId':'lectures','sourceSha256':SHA,'physicalPages':[1803,1842],'revisionCount':14,'newQuestionCount':0,'totalCurrentQuestions':86,'acceptedPreserved':72,'acceptedQuestionHashes':accepted,'packet':pp,'packetSha256':sha(pp),'questionHashes':{q['id']:question_hash(q)for q in changed},'previousQuestionHashes':{q['id']:question_hash(oq[q['id']])for q in changed},'repairedFindingIds':sorted(flags),'boundedGapDispositions':{'L57-G1':'Revised Q003 tests both cable communication and power-transmission roles alongside software and optional hardware.','L57-G2':'Revised Q015 tests selecting the desired tool number before calibration observations and retaining separate verification.','L57-G3':'Revised Q031 tests varied checkerboard-view information versus repeated images, while retaining the camera/robot-frame distinction.'},'actualRepairPagesReinspected':[p['physicalPage']for p in obs['pages']],'originalActualPagesInspected':40,'authorChecks':{'named':ch['namedChecks'],'unsafeInterleavings':ch['unsafeInterleavings'],'safeInterleavings':ch['safeInterleavings'],'varied':ch['variedChecks'],'independent':False},'independentReviewComplete':False,'history':f'data/history/{B}/{B}-v1.json','preflight':'All local schemas and read-only real-bank validation pass. All 72 accepted whole objects/hashes and five original source claims remain exact. Fourteen versioned repairs incorporate all three bounded gaps; no redundant new questions.'}
paths=[f'data/question-batches/{B}.json',f'data/inspection-batches/{B}.json',pp,f'audits/{B}-v2-author-checks.json',f'audits/{B}-v2-repair-source-observations.json',f'audits/{B}-v2-source-issues.json',f'audits/{B}-v2-preflight-validation.json','scripts/repair_W12_L57_v2.py','scripts/check_W12_L57_v2_author.py'];m['files']={p:sha(p)for p in paths};write(f'audits/{B}-v2-repair-manifest.json',m)
minimal={k:m[k]for k in ['batchId','revisionAuthorId','sourceId','sourceSha256','physicalPages','packet','packetSha256','questionHashes']};minimal['reviewInstructions']='Revision re-review with prior exposure disclosed when applicable. Inspect actual source and freeze answers before keyed revisions or the repair narrative. Neutral locators omit evidence text. Q003, Q015 and Q031 incorporate gap angles; Q005 is the later generic-stem duplicate repair.';write(f'audits/{B}-v2-minimal-bindings.json',minimal);print(json.dumps({k:m[k]for k in ['revisionCount','newQuestionCount','acceptedPreserved','packetSha256','authorChecks']}))
