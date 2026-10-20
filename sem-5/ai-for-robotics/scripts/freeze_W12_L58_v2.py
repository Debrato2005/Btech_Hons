"""Freeze ten L58 changed drafts, preserving the 77 accepted whole objects."""
from pathlib import Path
import json,copy,hashlib,datetime,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors,validate_bank
from authoring_helpers import SHA
B='W12-L58';WHO='build_offline_study_interface:L58-v2-repair'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
assert not (R/f'audits/{B}-v2-repair-manifest.json').exists(),'Already frozen'
b=read(f'data/question-batches/{B}.json');old=read(f'data/history/{B}/{B}-v1.json');rev=read(f'audits/{B}-integration-review-summary.json');oq={q['id']:q for q in old['questions']};flags={x['questionId'] for x in rev['flaggedQuestions']};changed=[q for q in b['questions'] if q['id'] in flags or q['id'] not in oq];ch=read(f'audits/{B}-v2-author-checks.json');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert len(b['questions'])==87 and len(changed)==10 and len(flags)==8
for q in changed:
 assert q['version']==(2 if q['id'] in oq else 1) and q['status']=='draft' and not q['reviewIds']
 q['authorCheckEvidence']={'path':f'audits/{B}-v2-author-checks.json','sha256':sha(f'audits/{B}-v2-author-checks.json'),'independentReview':False,'scope':ch['scope']}
 q.setdefault('difficultyRationale',{'easy':'Direct source recognition or a single stated distinction.','medium':'Apply explicit added premises and distinguish competing interface or diagnostic actions.'}[q['difficulty']])
 # Readability of new metadata, with no changes to accepted records.
 for e in q.get('primaryEvidence',[]):
  for k in ('title','version'): 
   if k in e:e[k]=e[k].replace('DDS1.4','DDS 1.4').replace('Version1.4','Version 1.4').replace('specification1.12','specification 1.12')
 q['assumptions']=[s.replace('DDS1.4','DDS 1.4') for s in q['assumptions']]
 if 'conflictResolution' in q:
  cr=q['conflictResolution'];cr.update(sourceId='lectures',sourceSha256=SHA,questionVersion=q['version'],basis=q['solution']['justification'])
  cr['sourceClaim']=cr['sourceClaim'].replace('page1845','page 1845').replace('DDS1.4','DDS 1.4') if q['id'] not in oq else cr['sourceClaim']
for cid in {c for q in changed for c in q['conceptIds']}:
 c=next(c for c in b['concepts'] if c['id']==cid);linked=[q for q in b['questions'] if cid in q['conceptIds']];c['examinationAngles']=list(dict.fromkeys(c['examinationAngles']+['integrated-application'] if any('gapChallengeIds' in q for q in linked) else c['examinationAngles']))
qq={q['id']:q for q in b['questions']}
for i,h in rev['acceptedQuestionHashes'].items():assert qq[i]==oq[i] and question_hash(qq[i])==h,i
assert {q['id'] for q in b['questions'] if q['id'] in oq and q!=oq[q['id']]}==flags
for q in old['questions']:
 if 'conflictResolution' in q:assert q['conflictResolution']['sourceClaim']==qq[q['id']]['conflictResolution']['sourceClaim']
ins=read(f'data/inspection-batches/{B}.json')
for s in ins['slides']:s['conceptIds']=list(dict.fromkeys(s['conceptIds']+[c['id'] for c in b['concepts'] if s['id'] in c['slideIds']]))
for kind,items in [('question',b['questions']),('concept',b['concepts']),('slide',ins['slides'])]:
 schema=read(f'data/schema.{kind}.json')
 for x in items:assert not schema_errors(x,schema),(x['id'],schema_errors(x,schema))
# Validate against a read-only copy of the real bank, retaining accepted review bindings.
bank=read('data/bank.json');cq={q['id']:q for q in bank['questions']};bank['questions']=[q for q in bank['questions'] if not q['id'].startswith(B+'-')]+[copy.deepcopy(cq[q['id']]) if q['id'] in rev['acceptedQuestionHashes'] and q['id'] in cq and question_hash(cq[q['id']])==question_hash(q) else copy.deepcopy(q) for q in b['questions']];bank['concepts']=[c for c in bank['concepts'] if not c['id'].startswith(B+'-')]+copy.deepcopy(b['concepts']);sm={s['id']:s for s in ins['slides']}
for i,s in enumerate(bank['slides']):
 if s['id'] in sm:
  ns=copy.deepcopy(sm[s['id']]);ns['conceptIds']=list(dict.fromkeys([c for c in s['conceptIds'] if not c.startswith(B+'-')]+ns['conceptIds']));bank['slides'][i]=ns
report=validate_bank(bank,root=R,check_files=False);write(f'audits/{B}-v2-preflight-validation.json',report);assert report['valid'],report['errors']
write(f'data/question-batches/{B}.json',b);write(f'data/inspection-batches/{B}.json',ins)
packet=[]
for q in changed:
 x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:
  c.pop('evidenceText',None);c['locator']=f"Lecture L58, physical PDF page {c['physicalPage']}, printed footer {c['physicalPage']-1842}: inspect the {c['kind']} content on this source page. Neutral review locator."
 if q.get('primaryEvidence'):x['externalSources']=[{k:v for k,v in e.items() if k in ('title','url','version')} for e in q['primaryEvidence']]
 packet.append(x)
pp=f'audits/blind-{B}-v2.json';write(pp,packet)
issues={'batchId':B,'updatedAt':now,'sourceId':'lectures','sourceSha256':SHA,'originalIssueLedger':f'audits/source-disputes-{B}.json','originalIssueLedgerSha256':sha(f'audits/source-disputes-{B}.json'),'originalSourceClaimsPreserved':True,'globalSourceResolution':False,'changedLocalQualifications':{q['id']:q['conflictResolution'] for q in changed if 'conflictResolution' in q},'addedPremises':['Mean latency and deadline example, not measured source performance.','Two navigation logs, explicit one-recovery/one-replan budget and time-consistency prerequisite.','Illustrative /sim_scan and /drive_command topic names; no exact plugin API is asserted.'],'executionLimit':'No ROS/Gazebo runtime, hardware, simulator process, denied documentation route or browser check was attempted. Official OMG and SDF pages were read through the permitted web tool.'};write(f'audits/{B}-v2-source-issues.json',issues)
obs=read(f'audits/{B}-v2-repair-source-observations.json')
m={'batchId':B,'revisionAuthorId':WHO,'frozenAt':now,'sourceId':'lectures','sourceSha256':SHA,'physicalPages':[1843,1876],'revisionCount':8,'newQuestionCount':2,'totalCurrentQuestions':87,'acceptedPreserved':77,'acceptedQuestionHashes':rev['acceptedQuestionHashes'],'packet':pp,'packetSha256':sha(pp),'questionHashes':{q['id']:question_hash(q) for q in changed},'previousQuestionHashes':{q['id']:question_hash(oq[q['id']]) for q in changed if q['id'] in oq},'repairedFindingIds':sorted(flags),'boundedGapDispositions':{'L58-GAP-DDS-expansion':'New P1845-Q03 distinguishes the literal slide from the official standard title and middleware role.','L58-GAP-plugin-ROS-interface':'New P1852-Q03 tests explicitly supplied bidirectional sensor/actuator interfaces.','L58-GAP-integrated-navigation-diagnosis':'Revised P1866-Q03 separates exhausted route failure from reset-clock/transform prerequisites across two added logs.'},'actualRepairPagesReinspected':[r['physicalPage'] for r in obs['pages']],'originalActualPagesInspected':34,'authorChecks':{'named':ch['namedChecks'],'exhaustivePolicyStates':ch['exhaustivePolicyStates'],'varied':ch['variedChecks'],'independent':False},'independentReviewComplete':False,'history':f'data/history/{B}/{B}-v1.json','preflight':'Question, concept and slide schemas plus read-only real-bank validation pass. All 77 accepted whole objects/hashes and all original local source claims remain exact. Blind locators are neutral; citation evidence text is omitted.'}
paths=[f'data/question-batches/{B}.json',f'data/inspection-batches/{B}.json',pp,f'audits/{B}-v2-author-checks.json',f'audits/{B}-v2-repair-source-observations.json',f'audits/{B}-v2-source-issues.json',f'audits/{B}-v2-preflight-validation.json','scripts/repair_W12_L58_v2.py','scripts/check_W12_L58_v2_author.py'];m['files']={p:sha(p) for p in paths};write(f'audits/{B}-v2-repair-manifest.json',m)
minimal={k:m[k] for k in ['batchId','revisionAuthorId','sourceId','sourceSha256','physicalPages','packet','packetSha256','questionHashes']};minimal['reviewInstructions']='Inspect actual source and answer the revised packet before opening keyed revisions or repair narrative. Disclose prior-version answer exposure for the eight revisions. Two new gap items are P1845-Q03 and P1852-Q03. Author checks are not independent verification.';write(f'audits/{B}-v2-minimal-bindings.json',minimal)
print(json.dumps({k:m[k] for k in ['revisionCount','newQuestionCount','acceptedPreserved','packetSha256','authorChecks']}))
