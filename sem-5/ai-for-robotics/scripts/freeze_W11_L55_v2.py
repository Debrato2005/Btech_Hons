"""Freeze changed-only L55 packet; no canonical assembly or Git writes."""
from pathlib import Path
import json,copy,hashlib,datetime,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors,validate_bank
from authoring_helpers import SHA
B='W11-L55';WHO='build_offline_study_interface:L55-v2-repair';bp=R/f'data/question-batches/{B}.json';b=json.loads(bp.read_text());old=json.loads((R/f'data/history/{B}/{B}-v1.json').read_text());rev=json.loads((R/f'audits/{B}-integration-review-summary.json').read_text());oq={q['id']:q for q in old['questions']};flags=set(rev['flaggedFindings']);changed=[q for q in b['questions'] if q['id'] in flags or q['id'] not in oq];checks=R/f'audits/{B}-v2-author-checks.json';ch=json.loads(checks.read_text());now=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert len(changed)==5 and len(flags)==3 and len(b['questions'])==74
for q in changed:
 assert q['version']==(2 if q['id'] in oq else 1) and q['status']=='draft' and not q['reviewIds']
 q['difficultyRationale']={'easy':'Direct recognition of explicitly printed settings or literal code order.','medium':'Applies stated device/layout premises or distinguishes complete integrated validation from partial testing.','hard':'Combines local inertia derivatives, physical kinetic energy, Euler–Lagrange torque and a limited positive-definiteness conclusion.'}[q['difficulty']]
 if True:q['authorCheckEvidence']={'path':str(checks.relative_to(R)),'sha256':hashlib.sha256(checks.read_bytes()).hexdigest(),'independentReview':False,'scope':ch['scope']}
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
bank=json.loads((R/'data/bank.json').read_text());canonical_q={q['id']:q for q in bank['questions']};bank['questions']=[q for q in bank['questions'] if not q['id'].startswith(B+'-')]+[copy.deepcopy(canonical_q[q['id']]) if q['id'] in rev['acceptedQuestionHashes'] and q['id'] in canonical_q and question_hash(canonical_q[q['id']])==question_hash(q) else copy.deepcopy(q) for q in b['questions']];bank['concepts']=[c for c in bank['concepts'] if not c['id'].startswith(B+'-')]+copy.deepcopy(b['concepts']);sm={s['id']:s for s in ins['slides']}
for i,s in enumerate(bank['slides']):
 if s['id'] in sm:
  ns=copy.deepcopy(sm[s['id']]);ns['conceptIds']=list(dict.fromkeys([c for c in s['conceptIds'] if not c.startswith(B+'-')]+ns['conceptIds']));bank['slides'][i]=ns
report=validate_bank(bank,root=R,check_files=False);(R/f'audits/{B}-v2-preflight-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');assert report['valid'],report['errors']
issues={'batchId':B,'updatedAt':now,'sourceId':'lectures','sourceSha256':SHA,'originalIssueLedger':f'audits/{B}-source-issues.json','originalIssueLedgerSha256':hashlib.sha256((R/f'audits/{B}-source-issues.json').read_bytes()).hexdigest(),'originalSourceClaimsPreserved':True,'globalSourceResolution':False,'changedLocalQualifications':{q['id']:q['conflictResolution'] for q in changed if 'conflictResolution' in q},'addedPremises':['Q060 detached CUDA tensor with compatible layout and explicit force=False conversion','Q074 fully specified local inertia and derivatives, state and gravity; physical kinetic energy and corrected Euler–Lagrange relation'],'reviewerObservationCorrectionHonored':'Q056 now follows the actual source prediction/loss before zero_grad order; the valid clear-before-forward convention is not misrepresented as the printed order. Q019 acknowledges held-out one-step validation while requiring the full source trajectory-validation sequence.'};(R/f'audits/{B}-v2-source-issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n')
obs=json.loads((R/f'audits/{B}-v2-repair-source-observations.json').read_text())
m={'batchId':B,'revisionAuthorId':WHO,'frozenAt':now,'sourceId':'lectures','sourceSha256':SHA,'physicalPages':[1745,1776],'revisionCount':3,'newQuestionCount':2,'totalCurrentQuestions':74,'acceptedPreserved':69,'acceptedQuestionHashes':rev['acceptedQuestionHashes'],'packet':str(pp.relative_to(R)),'packetSha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'questionHashes':{q['id']:question_hash(q) for q in changed},'previousQuestionHashes':{q['id']:question_hash(oq[q['id']]) for q in changed if q['id'] in oq},'repairedFindingIds':sorted(flags),'boundedGapDispositions':{'L55-G1':'New Q073 contrasts the forward sigmoid/backpropagation diagram with the inverse tanh/0.001 MLP code without output-layer assumptions.','L55-G2':'New Q074 derives coupled two-joint torque from physical energy and tests local inertia structure versus fit accuracy.'},'actualRepairPagesReinspected':[r['physicalPage'] for r in obs['pages']],'originalActualPagesInspected':32,'authorChecks':{'named':ch['namedChecks'],'varied':ch['variedChecks'],'independent':False},'independentReviewComplete':False,'history':f'data/history/{B}/{B}-v1.json','preflight':'All local question/concept/slide schemas and read-only in-memory real-bank validation pass. All 69 accepted whole objects/hashes remain exact. Original local source qualifications are preserved.'}
paths=[f'data/question-batches/{B}.json',f'data/inspection-batches/{B}.json',f'audits/blind-{B}-v2.json',f'audits/{B}-v2-author-checks.json',f'audits/{B}-v2-repair-source-observations.json',f'audits/{B}-v2-source-issues.json',f'audits/{B}-v2-preflight-validation.json','scripts/repair_W11_L55_v2.py','scripts/check_W11_L55_v2_author.py'];m['files']={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in paths}
(R/f'audits/{B}-v2-repair-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');minimal={k:m[k] for k in ['batchId','revisionAuthorId','sourceId','sourceSha256','physicalPages','packet','packetSha256','questionHashes']};minimal['reviewInstructions']='Revision re-review with prior exposure disclosed. Inspect changed items and actual source before keyed revisions or repair narrative. Q073 and Q074 are new gap questions; Q074 requires an independent coupled energy/torque derivation. Q019, Q056 and Q060 are versioned revisions.';(R/f'audits/{B}-v2-minimal-bindings.json').write_text(json.dumps(minimal,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:m[k] for k in ['revisionCount','newQuestionCount','acceptedPreserved','packetSha256','authorChecks']}))
