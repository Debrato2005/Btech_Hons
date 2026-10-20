"""One-shot source-premise and pre-answer cue repairs. Execute only after integration hold releases."""
from pathlib import Path
import json,copy,hashlib,datetime,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors,validate_bank
WHO='repair_assignment_source_bindings:W05-W06-v2-author';D='audits/assignment-coverage';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(p,x):
 p=R/p;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists(),p;p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
obs=[('assignments',20,'Q3 states speed-proportional back EMF opposing applied voltage. Complete armature KVL is not printed here.'),('assignments',21,'Q7 prompt and first alpha/beta choices. The tau=alpha*u+beta equation is not printed.'),('assignments',22,'Q7 continuation contains identity/zero choice and lecture reference, not the full input decomposition.'),('assignments',25,'Q4 source separately offers plane and hyperplane for a two-feature scalar regression graph, an overlapping source option defect.'),('lectures',675,'Printed slide7 explicitly gives l_A*di_A/dt+r_A*i_A=v_A-k_e*theta_dot_m and the series armature circuit.')]
ip=f'{D}/W05-W06-v2-author-reinspection.json';write(ip,{'inspectorId':WHO,'inspectedAt':now,'independentReview':False,'method':'Actual source preview pixels viewed with view_image; printed assignment keys visible.','pages':[{'sourceId':s,'physicalPage':p,'imagePath':f'sources/previews/{s}/page-{p:04d}.webp','imageSha256':sha(f'sources/previews/{s}/page-{p:04d}.webp'),'observation':o}for s,p,o in obs]})
for week,nums in [(5,[3,7]),(6,[4])]:
 B=f'ASSIGN-W{week:02d}';bp=f'data/question-batches/{B}.json';raw=(R/bp).read_bytes();old=json.loads(raw);b=copy.deepcopy(old);qs={q['id']:q for q in b['questions']};ids={f'{B}-Q{n:03d}'for n in nums};summary=read(f'{D}/W{week:02d}-independent-review-summary.json');accepted=summary['acceptedQuestionHashes'];assert set(accepted)|ids==set(qs)
 hp=R/f'data/history/{B}/v1.json';hp.parent.mkdir(parents=True,exist_ok=True);assert not hp.exists();hp.write_bytes(raw);changes={}
 for qid in sorted(ids):
  q=qs[qid];assert q['version']==1;q.update(version=2,status='draft',reviewIds=[],revisionAuthors=list(dict.fromkeys(q.get('revisionAuthors',[])+[WHO])))
  if q.get('conflictResolution'):q['conflictResolution']['questionVersion']=2
  if week==5 and qid.endswith('003'):
   q['citations'].append({'slideId':'lectures-p0675','sourceId':'lectures','sourceSha256':read('sources/preview_source_versions.json')['lectures'],'physicalPage':675,'kind':'equation','locator':'Lecture 22, combined physical PDF page 675, lecture-relative page 7, original printed slide 7: central armature voltage equation below the circuit diagram.','evidenceText':'l_A di_A/dt + r_A i_A = v_A - k_e theta_dot_m. The same slide labels armature resistance, inductance and rotational back EMF in the series circuit.','role':'premise','region':None})
   changes[qid]='Added exact lecture physical675/printed7 KVL premise while preserving original assignment item20 and all question/solution content.'
  elif week==5:
   q['stem']='For this exercise, define the input map τ=αu+β and let u already contain the independently computed joint torque commands. Which α and β pass those commands through without model-based coupling compensation?'
   q['assumptions'].append('The input-map equation is an explicitly added exercise definition; the assignment source gives the α and β choices for individual-joint control.')
   q['solution']['justification']=q['solution']['simpleExplanation']='The source identifies identity scaling and zero offset for its independent-joint convention. Applying those choices to the explicitly added exercise map gives τ=Iu+0=u.'
   q['solution']['formulas'][0]['assumptions']=['The equation τ=αu+β is an explicitly added exercise definition; u already has joint-torque units; no model cancellation is claimed.']
   for cid in q['conceptIds']:next(c for c in b['concepts']if c['id']==cid)['description']=q['solution']['justification']
   changes[qid]='Labeled the input-map equation explicitly added, retaining torque-level command scope and source alpha/beta evidence.'
  else:
   q['stem']='For ŷ=b₀+b₁x₁+b₂x₂ plotted as a graph in (x₁,x₂,ŷ) space, which geometrical description is correct?'
   changes[qid]='Removed the pre-answer overlapping-choice conclusion while retaining two-independent-input scope and the unchanged corrected solution.'
  q['revisionCheckScope']=changes[qid]+' Author-only repair; requires independent re-review.'
 for q in b['questions']:
  before=next(x for x in old['questions']if x['id']==q['id'])
  assert sha(q['originalRecordPath'])==q['originalRecordSha256'];assert not schema_errors(q,read('data/schema.question.json'))
  if q['id']in accepted:assert q==before and question_hash(q)==accepted[q['id']]
  else:assert q['correctOptionIds']==before['correctOptionIds'] and q['options']==before['options']
 bank=read('data/bank.json');cq={q['id']:q for q in bank['questions']};bank['questions']=[q for q in bank['questions']if q['id']not in qs]+[copy.deepcopy(cq[q['id']])if q['id']in accepted and q['id']in cq and question_hash(cq[q['id']])==question_hash(q)else q for q in b['questions']];cids={c['id']for c in b['concepts']};bank['concepts']=[c for c in bank['concepts']if c['id']not in cids]+b['concepts'];report=validate_bank(bank,root=R,check_files=False);vp=f'{D}/{B}-v2-validation.json';write(vp,report);assert report['valid'],report['errors']
 assert (R/bp).read_bytes()==raw;(R/bp).write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
 packet=[]
 for q in b['questions']:
  if q['id']not in ids:continue
  x={k:copy.deepcopy(q[k])for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
  for c in x['citations']:
   c.pop('evidenceText',None);c['locator']=f"Assignment Week {week}, source item {int(q['assignmentSourceItemId'][-2:])}, physical page {c['physicalPage']}: inspect the item region visible on this page."if c['sourceId']=='assignments'else'Lecture 22, physical PDF page 675, printed slide 7: inspect the equation and circuit region.'
  packet.append(x)
 pp=f'audits/blind-{B}-v2.json';write(pp,packet);m={'batchId':B,'revisionAuthorId':WHO,'frozenAt':now,'packet':pp,'packetSha256':sha(pp),'questionHashes':{i:question_hash(qs[i])for i in sorted(ids)},'acceptedQuestionHashes':accepted,'acceptedPreserved':len(accepted),'keysUnchanged':True,'originalRecordsUnchanged':True,'sourceInspectionPath':ip,'sourceInspectionSha256':sha(ip),'historyPath':str(hp.relative_to(R)),'historySha256':sha(str(hp.relative_to(R))),'validationPath':vp,'validationSha256':sha(vp),'independentReviewComplete':False,'changes':changes,'scope':'Narrow citation/premise/stem repairs only. No new runtime or computation claim; no self-approval, canonical bank or Git writes.'};write(f'{D}/{B}-v2-repair-manifest.json',m);write(f'{D}/{B}-v2-minimal-bindings.json',{k:m[k]for k in ['batchId','revisionAuthorId','packet','packetSha256','questionHashes']});print(json.dumps({k:m[k]for k in ['batchId','packet','packetSha256','acceptedPreserved']}))
