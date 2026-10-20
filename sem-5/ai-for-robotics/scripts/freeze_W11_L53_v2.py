"""Freeze changed-only L53 packet; no canonical assembly or Git writes."""
from pathlib import Path
import json,copy,hashlib,datetime,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors,validate_bank
from authoring_helpers import SHA
B='W11-L53';WHO='build_offline_study_interface:L53-v2-repair';bp=R/f'data/question-batches/{B}.json';b=json.loads(bp.read_text());old=json.loads((R/f'data/history/{B}/{B}-v1.json').read_text());rev=json.loads((R/f'audits/{B}-contracts-review-summary.json').read_text());oq={q['id']:q for q in old['questions']};flags=set(rev['flaggedFindings']);changed=[q for q in b['questions'] if q['id'] in flags or q['id'] not in oq];checks=R/f'audits/{B}-v2-author-checks.json';ch=json.loads(checks.read_text());now=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert len(changed)==31 and len(flags)==29 and len(b['questions'])==93
for q in changed:
 assert q['version']==(2 if q['id'] in oq else 1) and q['status']=='draft' and not q['reviewIds']
 q['difficultyRationale']={'easy':'Direct source distinction or short specified arithmetic.','medium':'Combines given relations, sign conventions or a multistep current/alignment trace.','hard':'Combines gear conversion, motor current and back EMF, voltage feasibility, peak current and time-weighted heating across four candidate designs.'}[q['difficulty']]
 if q['type']=='numerical' or q['id'].endswith(('Q046','Q093')):q['authorCheckEvidence']={'path':str(checks.relative_to(R)),'sha256':hashlib.sha256(checks.read_bytes()).hexdigest(),'independentReview':False,'scope':ch['scope']}
 if 'conflictResolution' in q:q['conflictResolution'].update(sourceId='lectures',sourceSha256=SHA,physicalPages=[c['physicalPage'] for c in q['citations'] if c['role']=='conflict'],basis=q['solution']['justification'])
for cid in {c for q in changed for c in q['conceptIds']}:
 c=next(c for c in b['concepts'] if c['id']==cid);linked=[q for q in b['questions'] if cid in q['conceptIds']];c['description']=linked[0]['solution']['justification'];c['examinationAngles']=list(dict.fromkeys([q['type'] for q in linked]+(['integrated-application'] if any('gapChallengeIds' in q for q in linked) else [])))
qq={q['id']:q for q in b['questions']}
for i,h in rev['acceptedQuestionHashes'].items():assert qq[i]==oq[i] and question_hash(qq[i])==h,i
assert {q['id'] for q in b['questions'] if q['id'] in oq and q!=oq[q['id']]}==flags
assert all('conflictResolution' not in q or q['conflictResolution']['sourceClaim']==qq[q['id']]['conflictResolution']['sourceClaim'] for q in old['questions'])
ip=R/f'data/inspection-batches/{B}.json';ins=json.loads(ip.read_text())
for s in ins['slides']:s['conceptIds']=list(dict.fromkeys(s['conceptIds']+[c['id'] for c in b['concepts'] if s['id'] in c['slideIds']]))
for kind,items in [('question',b['questions']),('concept',b['concepts']),('slide',ins['slides'])]:
 schema=json.loads((R/f'data/schema.{kind}.json').read_text())
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
report=validate_bank(bank,root=R,check_files=False);(R/f'audits/{B}-v2-preflight-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');assert report['valid'],report['errors']
issues={'batchId':B,'updatedAt':now,'sourceId':'lectures','sourceSha256':SHA,'originalIssueLedger':f'audits/{B}-source-issues.json','originalIssueLedgerSha256':hashlib.sha256((R/f'audits/{B}-source-issues.json').read_bytes()).hexdigest(),'originalSourceClaimsPreserved':True,'globalSourceResolution':False,'changedLocalQualifications':{q['id']:q['conflictResolution'] for q in changed if 'conflictResolution' in q},'addedPremises':['Q046 ideal diode orientation, initial current, all-off transition and absorbing supply','Q061 explicitly supplied slip definition','Q092 complete candidate ratings, ideal gear and duty/thermal model','Q093 declared phase axes, nearest alignment and marked-tooth unwrapped angle'],'reviewerObservationCorrectionHonored':'No new claim that the p1697 compound field coils are simply parallel is introduced.'};(R/f'audits/{B}-v2-source-issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n')
obs=json.loads((R/f'audits/{B}-v2-repair-source-observations.json').read_text())
m={'batchId':B,'revisionAuthorId':WHO,'frozenAt':now,'sourceId':'lectures','sourceSha256':SHA,'physicalPages':[1685,1714],'revisionCount':29,'newQuestionCount':2,'totalCurrentQuestions':93,'acceptedPreserved':62,'acceptedQuestionHashes':rev['acceptedQuestionHashes'],'packet':str(pp.relative_to(R)),'packetSha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'questionHashes':{q['id']:question_hash(q) for q in changed},'previousQuestionHashes':{q['id']:question_hash(oq[q['id']]) for q in changed if q['id'] in oq},'repairedFindingIds':sorted(flags),'boundedGapDispositions':{'L53-G01':'New Q092 constrained motor/drive selection: gear, voltage/current and duty heating.','L53-G02':'Revised Q046 traces actual diode continuation, terminal voltage and energy sense.','L53-G03':'New Q093 traces four phases and reversal with unwrapped marked-tooth movement.'},'actualRepairPagesReinspected':[r['physicalPage'] for r in obs['pages']],'originalActualPagesInspected':30,'authorChecks':{'named':ch['namedChecks'],'varied':ch['variedChecks'],'independent':False},'independentReviewComplete':False,'history':f'data/history/{B}/{B}-v1.json','preflight':'All local question/concept/slide schemas and read-only in-memory real-bank validation pass. All 62 accepted whole objects/hashes remain exact. Original local source qualifications are preserved.'}
paths=[f'data/question-batches/{B}.json',f'data/inspection-batches/{B}.json',f'audits/blind-{B}-v2.json',f'audits/{B}-v2-author-checks.json',f'audits/{B}-v2-repair-source-observations.json',f'audits/{B}-v2-source-issues.json',f'audits/{B}-v2-preflight-validation.json','scripts/repair_W11_L53_v2.py','scripts/check_W11_L53_v2_author.py'];m['files']={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in paths}
(R/f'audits/{B}-v2-repair-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');minimal={k:m[k] for k in ['batchId','revisionAuthorId','sourceId','sourceSha256','physicalPages','packet','packetSha256','questionHashes']};minimal['reviewInstructions']='Revision re-review with prior exposure disclosed. Inspect changed items and actual source before keyed revisions or repair narrative. Q046, Q092 and Q093 include new integrated exercises requiring independent derivation.';(R/f'audits/{B}-v2-minimal-bindings.json').write_text(json.dumps(minimal,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:m[k] for k in ['revisionCount','newQuestionCount','acceptedPreserved','packetSha256','authorChecks']}))
