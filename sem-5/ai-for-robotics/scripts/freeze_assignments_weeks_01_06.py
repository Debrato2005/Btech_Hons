"""Freeze all sixty explicit assignment-item drafts with answer-hidden review packets."""
from pathlib import Path
import json,copy,sys,hashlib,datetime
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import question_hash,schema_errors,validate_bank
SHA='b0450429866ac8017d7971932acf8812adf41df9dff4eb10bc8c87015b41c1b5';WHO='build_offline_study_interface:assignments-W01-W06-author'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
mp='audits/assignment-coverage/W01-W06-frozen-manifest.json';assert not(R/mp).exists(),'Already frozen'
checkpath='audits/assignment-coverage/W01-W06-author-checks.json';checks=read(checkpath);assert checks['allPassed']
questions=[];concepts=[];slides=[];packets={};coverage=[];originals={};sourceissues=[]
for w in range(1,7):
 bid=f'ASSIGN-W{w:02d}';b=read(f'data/question-batches/{bid}.json');ins=read(f'data/inspection-batches/{bid}.json');assert len(b['questions'])==10
 packet=[]
 for q in b['questions']:
  assert q['version']==1 and q['status']=='draft' and not q['reviewIds'] and q['lectureId']is None
  q['authorCheckEvidence']={'path':checkpath,'sha256':sha(checkpath),'independentReview':False,'scope':checks['scope']}
  assert q['originalRecordSha256']==sha(q['originalRecordPath']);originals[q['originalRecordPath']]=sha(q['originalRecordPath'])
  assert set(q['solution']['optionExplanations'])=={o['id']for o in q['options']} and len({o['text']for o in q['options']})==4
  for c in q['citations']:assert c['sourceId']=='assignments' and c['sourceSha256']==SHA
  p={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
  for c in p['citations']:
   c.pop('evidenceText',None);c['locator']=f"Assignment Week {w}, source item {int(q['assignmentSourceItemId'][-2:])}, physical PDF page {c['physicalPage']}: inspect that item's visible region and any continuation. Neutral review locator."
  packet.append(p);orig=read(q['originalRecordPath'])
  coverage.append({'assignmentSourceItemId':q['assignmentSourceItemId'],'questionId':q['id'],'questionSha256':question_hash(q),'originalRecordPath':q['originalRecordPath'],'originalRecordSha256':q['originalRecordSha256'],'physicalPages':[c['physicalPage']for c in q['citations']],'status':'adaptation_drafted_pending_independent_review','literalOriginalDisposition':orig['literalOriginalDisposition'],'originalSourceKeyAuditIsNotApproval':True})
  if q.get('conflictResolution'):sourceissues.append({'questionId':q['id'],**q['conflictResolution']})
 for kind,records in [('question',b['questions']),('concept',b['concepts']),('slide',ins['slides'])]:
  for r in records:assert not schema_errors(r,read(f'data/schema.{kind}.json')),(r['id'],schema_errors(r,read(f'data/schema.{kind}.json')))
 write(f'data/question-batches/{bid}.json',b);pp=f'audits/blind-{bid}.json';write(pp,packet);packets[bid]={'path':pp,'sha256':sha(pp),'count':10};questions+=b['questions'];concepts+=b['concepts'];slides+=ins['slides']
assert len(questions)==60 and len({x['assignmentSourceItemId']for x in questions})==60 and len(slides)==28
bank=read('data/bank.json');ids={q['id']for q in questions};cids={c['id']for c in concepts};sm={s['id']:s for s in slides}
bank['questions']=[q for q in bank['questions']if q['id']not in ids]+questions;bank['concepts']=[c for c in bank['concepts']if c['id']not in cids]+concepts
for i,s in enumerate(bank['slides']):
 if s['id']in sm:
  ns=copy.deepcopy(sm[s['id']]);ns['conceptIds']=list(dict.fromkeys([c for c in s['conceptIds']if c not in cids]+ns['conceptIds']));bank['slides'][i]=ns
report=validate_bank(bank,root=R,check_files=False);write('audits/assignment-coverage/W01-W06-preflight-validation.json',report);assert report['valid'],report['errors']
write('audits/assignment-coverage/W01-W06-item-coverage.json',coverage)
write('audits/assignment-coverage/W01-W06-source-qualifications.json',{'sourceId':'assignments','sourceSha256':SHA,'explicitConflictAdaptations':sourceissues,'otherQualificationTopics':['Asimov fictional scope','ML/DL/RL overlap','Task-relative model fidelity','Column-vector transform convention','Joint count versus task rank','Geometry-specific IK multiplicity','Inertia axes and COM frames','Six independent quintic endpoint constraints','Same-axis angle metric','Workspace/joint-limit qualifications','SCARA relative stiffness','Motor back EMF versus terminal voltage','Resonance separation as a guideline','Exact-model cancellation and units','Object/structured dtype distinction','Squared-error regression leaf assumptions','Nonterminal versus terminal Q bootstrap'],'mapperCorrection':'audits/assignment-coverage/correction-W04-Q10.json','globalSourceResolution':False,'independentReviewComplete':False})
manifest={'scope':'Assignment Weeks 1–6, all sixty original items, all twenty-eight actual pages','authorId':WHO,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceId':'assignments','sourceSha256':SHA,'actualPages':list(range(1,29)),'questionCount':60,'conceptCount':60,'packets':packets,'questionHashes':{q['id']:question_hash(q)for q in questions},'originalRecordHashes':originals,'coveragePath':'audits/assignment-coverage/W01-W06-item-coverage.json','sourceQualificationPath':'audits/assignment-coverage/W01-W06-source-qualifications.json','authorChecks':{'named':checks['namedChecks'],'varied':checks['variedAssertions'],'independent':False,'path':checkpath,'sha256':sha(checkpath)},'independentReviewComplete':False,'preflight':'All question/concept/slide schemas and read-only real-bank integrity validation pass. Original source keys were visible during authoring. Every literal original is preserved outside the study-question pool.','restrictions':'No installation, downloads, restricted environment, robot/controller/network runtime, original-notebook retrieval, NLTK corpus or browser execution. Installed default-environment symbolic/numeric and toy estimator checks only.'}
manifest['files']={p:sha(p)for p in ['scripts/author_assignments_weeks_01_06.py','scripts/check_assignments_weeks_01_06_author.py',manifest['coveragePath'],manifest['sourceQualificationPath'],'audits/assignment-coverage/W01-W06-author-page-observations.json']+[f'data/question-batches/ASSIGN-W{w:02d}.json'for w in range(1,7)]+[f'data/inspection-batches/ASSIGN-W{w:02d}.json'for w in range(1,7)]};write(mp,manifest)
minimal={k:manifest[k]for k in ['scope','authorId','sourceId','sourceSha256','actualPages','packets','questionHashes']};minimal['reviewBoundary']='Answer-hidden packets omit evidence text, author reasoning and original records. Inspect source pixels and freeze responses before current keyed drafts. The source PDF itself displays original keys, so disclose that unavoidable original-key exposure; generated keys/solutions must remain hidden until the freeze. Original mapper arithmetic and author checks are not independent acceptance.';write('audits/assignment-coverage/W01-W06-minimal-bindings.json',minimal)
print(json.dumps({'questions':60,'pages':28,'originals':60,'manifest':mp,'manifestSha256':sha(mp),'packets':packets,'authorChecks':manifest['authorChecks']}))
