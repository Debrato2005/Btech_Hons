"""Freeze L51 changed-only repair packet; never changes canonical bank or Git."""
from pathlib import Path
import json,copy,hashlib,datetime,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors,validate_bank
from authoring_helpers import SHA
B='W11-L51';WHO='build_offline_study_interface:L51-v2-repair';bp=R/f'data/question-batches/{B}.json';b=json.loads(bp.read_text());old=json.loads((R/f'data/history/{B}/{B}-v1.json').read_text());review=json.loads((R/f'audits/{B}-contracts-review-summary.json').read_text());flags=set(review['flaggedFindings']);oldq={q['id']:q for q in old['questions']};changed=[q for q in b['questions'] if q['id'] in flags or q['id'] not in oldq];checkp=R/f'audits/{B}-v2-author-checks.json';check=json.loads(checkp.read_text());now=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert len(changed)==40 and len(flags)==37 and len(b['questions'])==79
for q in changed:
 assert q['status']=='draft' and not q['reviewIds']
 assert q['version']==(2 if q['id'] in oldq else 1)
 q['difficultyRationale']={'easy':'Direct source distinction or a short specified operation.','medium':'Combines supplied conditions, arithmetic or a qualified interpretation.','hard':'Integrates energy, framed transmission, camera bandwidth and serial deadline constraints across four candidate designs.'}[q['difficulty']]
 if q['type']=='numerical' or int(q['id'][-3:]) in [33,59,71]:
  q['authorCheckEvidence']={'path':str(checkp.relative_to(R)),'sha256':hashlib.sha256(checkp.read_bytes()).hexdigest(),'independentReview':False,'scope':check['scope']}
 if 'conflictResolution' in q:
  q['conflictResolution'].update(sourceId='lectures',sourceSha256=SHA,physicalPages=[c['physicalPage'] for c in q['citations'] if c['role']=='conflict'],basis=q['solution']['justification'])
for cid in {cid for q in changed for cid in q['conceptIds']}:
 c=next(c for c in b['concepts'] if c['id']==cid);linked=[q for q in b['questions'] if cid in q['conceptIds']];c['description']=linked[0]['solution']['justification'];c['examinationAngles']=list(dict.fromkeys([q['type'] for q in linked]+(['integrated-application'] if any('gapChallengeIds' in q for q in linked) else [])))
for ident,h in review['acceptedQuestionHashes'].items():
 q=next(q for q in b['questions'] if q['id']==ident);assert q==oldq[ident] and question_hash(q)==h,ident
assert {q['id'] for q in b['questions'] if q['id'] in oldq and q!=oldq[q['id']]}==flags
ip=R/f'data/inspection-batches/{B}.json';ins=json.loads(ip.read_text())
for s in ins['slides']:s['conceptIds']=list(dict.fromkeys(s['conceptIds']+[c['id'] for c in b['concepts'] if s['id'] in c['slideIds']]))
for key,items in [('question',b['questions']),('concept',b['concepts']),('slide',ins['slides'])]:
 schema=json.loads((R/f'data/schema.{key}.json').read_text())
 for x in items:assert not schema_errors(x,schema),(x['id'],schema_errors(x,schema))
bp.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');ip.write_text(json.dumps(ins,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in changed:
 x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
pp=R/f'audits/blind-{B}-v2.json';pp.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
bank=json.loads((R/'data/bank.json').read_text());bank['questions']=[q for q in bank['questions'] if not q['id'].startswith(B+'-')]+copy.deepcopy(b['questions']);bank['concepts']=[c for c in bank['concepts'] if not c['id'].startswith(B+'-')]+copy.deepcopy(b['concepts']);sm={s['id']:s for s in ins['slides']}
for i,s in enumerate(bank['slides']):
 if s['id'] in sm:
  ns=copy.deepcopy(sm[s['id']]);ns['conceptIds']=list(dict.fromkeys([c for c in s['conceptIds'] if not c.startswith(B+'-')]+ns['conceptIds']));bank['slides'][i]=ns
report=validate_bank(bank,root=R,check_files=False)
# Do not hide pre-existing errors from another owned batch or normalize its data.
import re
baseline=json.loads((R/'data/bank.json').read_text());baseline_report=validate_bank(baseline,root=R,check_files=False)
def bound_errors(data,rep):
 out=[]
 for error in rep['errors']:
  match=re.match(r'\$\.questions\[(\d+)\](.*)',error)
  assert match,('unmapped integrity error',error)
  ident=data['questions'][int(match.group(1))]['id'];out.append((ident,match.group(2)))
 return sorted(out)
current_errors=bound_errors(bank,report);prior_errors=bound_errors(baseline,baseline_report)
assert current_errors==prior_errors and all(not i.startswith(B+'-') for i,e in current_errors),(current_errors,prior_errors)
report['batchScopeValid']=True;report['newErrorsIntroduced']=[];report['preExistingExternalErrors']=[{'questionId':i,'error':e} for i,e in current_errors]
(R/f'audits/{B}-v2-preflight-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
source={'batchId':B,'updatedAt':now,'sourceId':'lectures','sourceSha256':SHA,'scope':'Local repair qualifications only; original source issue ledger and source bytes are unchanged.','originalIssueLedger':f'audits/{B}-source-issues.json','originalIssueLedgerSha256':hashlib.sha256((R/f'audits/{B}-source-issues.json').read_bytes()).hexdigest(),'allOriginalConflictRecordsPreserved':all(('conflictResolution' not in q or q['conflictResolution']['sourceClaim']==next(z for z in b['questions'] if z['id']==q['id'])['conflictResolution']['sourceClaim']) for q in old['questions']),'changedLocalQualifications':{q['id']:q['conflictResolution'] for q in changed if 'conflictResolution' in q},'addedModels':['Q028 declared memory and timing allocation','Q033 bounded cloud round-trip comparison','Q049–Q050 observation, action and incomplete-state scenarios','Q053 force-band plus target-region reward rule','Q059 explicitly supplied ideal band-limited sampling criterion','Q065 visible inverse-variance rule','Q066 independent noise plus shared fixed bias','Q071 declared reach and local rank','Q072 controlled floor-friction mismatch','Q076 calibrated wrench versus model-dependent estimates','Q077 structure/actuator/tool constraints','Q078 energy/framing/camera/latency candidate constraints','Q079 declared faults, timestamp offset and independently validated loop closure'],'globalSourceResolution':False}
assert source['allOriginalConflictRecordsPreserved'];(R/f'audits/{B}-v2-source-issues.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
m={'batchId':B,'revisionAuthorId':WHO,'frozenAt':now,'sourceId':'lectures','sourceSha256':SHA,'physicalPages':[1595,1619],'revisionCount':37,'newQuestionCount':3,'totalCurrentQuestions':79,'acceptedPreserved':39,'acceptedQuestionHashes':review['acceptedQuestionHashes'],'packet':str(pp.relative_to(R)),'packetSha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'questionHashes':{q['id']:question_hash(q) for q in changed},'previousQuestionHashes':{q['id']:question_hash(oldq[q['id']]) for q in changed if q['id'] in oldq},'repairedFindingIds':sorted(flags),'boundedGapDispositions':{'L51-G01':'Q077 integrates inertia, torque, material cost, commutation and gripper command/capability; Q014 tests all brushless tradeoff bullets.','L51-G02':'Q078 jointly evaluates all loads, usable energy, framed command transmission, separate camera bandwidth and measured inference latency.','L51-G03':'Q079 requires fault-aware complementary sensor roles, timing correction and validated loop closure; Q066 quantifies retained common bias.'},'actualRepairPagesReinspected':list(range(1599,1618)),'originalActualPagesInspected':25,'authorChecks':{'named':check['namedChecks'],'varied':check['variedChecks'],'independent':False},'independentReviewComplete':False,'originalQualificationsPreserved':True,'history':f'data/history/{B}/{B}-v1.json','preflight':'All L51 question/concept/slide schemas pass; read-only in-memory integration introduces no errors. Existing external canonical errors are preserved in the validation report, not normalized. All 39 accepted whole objects are exact.','fullCanonicalValidationPassed':report['valid'],'preExistingExternalErrors':report['preExistingExternalErrors']}
paths=[f'data/question-batches/{B}.json',f'data/inspection-batches/{B}.json',f'audits/blind-{B}-v2.json',f'audits/{B}-v2-author-checks.json',f'audits/{B}-v2-repair-source-observations.json',f'audits/{B}-v2-source-issues.json',f'audits/{B}-v2-preflight-validation.json','scripts/repair_W11_L51_v2.py','scripts/check_W11_L51_v2_author.py'];m['files']={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in paths}
(R/f'audits/{B}-v2-repair-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');minimal={k:m[k] for k in ['batchId','revisionAuthorId','sourceId','sourceSha256','physicalPages','packet','packetSha256','questionHashes']};minimal['reviewInstructions']='Revision re-review with prior exposure disclosed. Inspect changed questions and actual source before keyed revisions, author checks or repair narrative. Q077–Q079 are new author-added integrated exercises requiring independent solution.';(R/f'audits/{B}-v2-minimal-bindings.json').write_text(json.dumps(minimal,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:m[k] for k in ['revisionCount','newQuestionCount','acceptedPreserved','packetSha256','authorChecks']}))
