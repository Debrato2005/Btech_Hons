"""One-shot narrow repairs after actual source-pixel reinspection; never self-approve."""
from pathlib import Path
import json,copy,hashlib,datetime,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors,validate_bank
WHO='repair_assignment_source_bindings:W01-v3-W03-v2-author'
D='audits/assignment-coverage'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads((R/p).read_text())
def write(p,x):
 path=R/p;path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists(),p;path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
source_hash=sha('sources/raw/AI_for_Robotics_All_Assignment_Solutions.pdf')
assert source_hash==read('sources/preview_source_versions.json')['assignments']
observations={
1:'Week 1 Q3 appears at bottom with ML-from-data, DL-deep-networks and RL-rewards definitions. Source highlighted key is visible; not a blind author check.',
2:'The top Q3 continuation contains only Explanation (B) and the lecture slide references, not a further category-exclusivity premise.',
8:'Week 3 Q2 lower half contains the solid-cylinder axial-rotation diagram and candidate moment-of-inertia formulas.',
9:'The top Q2 continuation contains Answer A and Lecture 11 slide 20 reference, not the cylinder formula or diagram.',
10:'Q5 occupies the main diagram. Q6 begins at the bottom with its zero terminal wrench prompt only; Q6 diagram and options are not on this page.',
11:'Q6 continuation begins with the two-link geometry, terminal frame 3 labels, options, Answer B and lecture reference. There is no separate worked derivation.',
12:'Q9 begins at the bottom with only the mass-matrix question prompt. No Q9 geometry, angle labels or candidate matrices appear here.',
13:'Q9 continuation shows the two point masses, relative elbow angle, candidate inertia matrices, Answer A and lecture reference. There is no worked explanation. Q10 begins below with dynamics expression and options A-C.',
14:'Q10 continuation contains final option D, Answer B and Lecture 15 slide 8 reference. No derivation appears.'}
inspection={'inspectorId':WHO,'inspectedAt':now,'method':'Actual existing rendered source pixels opened with view_image, alongside source-bound text. All listed pages were viewed in this recovery pass.','sourceId':'assignments','sourceSha256':source_hash,'printedKeyExposure':True,'independentReview':False,'pages':[{'physicalPage':p,'imagePath':f'sources/previews/assignments/page-{p:04d}.webp','imageSha256':sha(f'sources/previews/assignments/page-{p:04d}.webp'),'observation':o}for p,o in observations.items()]}
ip=f'{D}/W01-v3-W03-v2-author-reinspection.json';write(ip,inspection)
results=[]
for week,version,nums,sp,accepted_key in [(1,3,[3],f'{D}/W01-v2-independent-review-summary.json','currentAcceptedHashes'),(3,2,[2,6,9,10],f'{D}/W03-independent-review-summary.json','acceptedQuestionHashes')]:
 B=f'ASSIGN-W{week:02d}';bp=f'data/question-batches/{B}.json';raw=(R/bp).read_bytes();old=json.loads(raw);b=copy.deepcopy(old);qs={q['id']:q for q in b['questions']};accepted=read(sp)[accepted_key];ids={f'{B}-Q{n:03d}'for n in nums};assert set(qs)==set(accepted)|ids
 hp=R/f'data/history/{B}/v{version-1}.json';hp.parent.mkdir(parents=True,exist_ok=True);assert not hp.exists();hp.write_bytes(raw)
 changes={}
 for qid in sorted(ids):
  q=qs[qid];assert q['version']==version-1
  q.update(version=version,status='draft',reviewIds=[],revisionAuthors=list(dict.fromkeys(q.get('revisionAuthors',[])+[WHO])))
  if q.get('conflictResolution'):q['conflictResolution']['questionVersion']=version
  if week==1:
   q['assumptions']=['The reward-learning scenario and deep policy representation are an added example.']
   changes[qid]='Removed the pre-answer category-overlap conclusion from assumptions. The neutral scenario, answer, options and explanation remain unchanged.'
  else:
   n=int(qid[-3:]);cs={c['physicalPage']:c for c in q['citations']}
   if n==2:
    cs[9]['kind']='statement';cs[9]['locator']='Assignment physical PDF page 9, printed footer 2: top continuation of Week 3 item 2, printed answer and Lecture 11 slide 20 reference only.'
   elif n==6:
    cs[10]['kind']='statement';cs[10]['locator']='Assignment physical PDF page 10, printed footer 3: bottom Week 3 item 6 prompt stating terminal boundary values; the item diagram continues on physical page 11.'
    cs[11]['kind']='figure';cs[11]['locator']='Assignment physical PDF page 11, printed footer 4: upper Week 3 item 6 continuation, two-link diagram with frame 3 labels, options, printed answer and Lecture 13 slide 5 reference.'
   elif n==9:
    cs[12]['kind']='statement';cs[12]['locator']='Assignment physical PDF page 12, printed footer 5: bottom Week 3 item 9 introductory mass-matrix prompt only; the diagram and candidate matrices continue on physical page 13.'
    cs[13]['locator']='Assignment physical PDF page 13, printed footer 6: Week 3 item 9 candidate inertia matrices, printed answer and Lecture 15 slide 6 reference; no worked derivation is printed.'
    figure=copy.deepcopy(cs[13]);figure['kind']='figure';figure['locator']='Assignment physical PDF page 13, printed footer 6: upper Week 3 item 9 two-link point-mass geometry with link lengths, mass positions and relative elbow-angle labels.';figure['evidenceText']='The actual upper diagram shows m1 at the elbow, m2 at the tip, lengths l1 and l2, base angle theta1, and theta2 measured from the first-link continuation to the second link.';q['citations'].insert(1,figure)
   elif n==10:
    cs[14]['kind']='statement';cs[14]['locator']='Assignment physical PDF page 14, printed footer 7: top Week 3 item 10 continuation, final option, printed answer and Lecture 15 slide 8 reference only; no derivation is printed.'
   changes[qid]='Corrected only exact per-page evidence kinds/locators; Q009 also separately binds its geometry to physical page 13. Numerical content, keys, options and solutions unchanged.'
  q['revisionCheckScope']=changes[qid]+' Author-only source-pixel reinspection, not independent approval.'
 for q in b['questions']:
  assert sha(q['originalRecordPath'])==q['originalRecordSha256']
  assert not schema_errors(q,read('data/schema.question.json'))
  before=next(x for x in old['questions']if x['id']==q['id'])
  if q['id']in accepted:assert q==before and question_hash(q)==accepted[q['id']]
  else:
   assert q['correctOptionIds']==before['correctOptionIds'] and q['options']==before['options'] and q['solution']==before['solution'] and q['stem']==before['stem']
 assert b['concepts']==old['concepts']
 bank=read('data/bank.json');cq={q['id']:q for q in bank['questions']};bank['questions']=[q for q in bank['questions']if q['id']not in qs]+[copy.deepcopy(cq[q['id']])if q['id']in accepted and q['id']in cq and question_hash(cq[q['id']])==question_hash(q)else q for q in b['questions']];cids={c['id']for c in b['concepts']};bank['concepts']=[c for c in bank['concepts']if c['id']not in cids]+b['concepts'];report=validate_bank(bank,root=R,check_files=False);vp=f'{D}/{B}-v{version}-validation.json';write(vp,report);assert report['valid'],report['errors']
 assert (R/bp).read_bytes()==raw,'Concurrent edit detected';(R/bp).write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
 packet=[]
 for q in b['questions']:
  if q['id']not in ids:continue
  x={k:copy.deepcopy(q[k])for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
  for c in x['citations']:c.pop('evidenceText',None);c['locator']=f"Assignment Week {week}, source item {int(q['assignmentSourceItemId'][-2:])}, physical page {c['physicalPage']}: inspect the item region visible on this page."
  packet.append(x)
 pp=f'audits/blind-{B}-v{version}.json';write(pp,packet)
 m={'batchId':B,'revisionAuthorId':WHO,'frozenAt':now,'packet':pp,'packetSha256':sha(pp),'questionHashes':{i:question_hash(qs[i])for i in sorted(ids)},'acceptedQuestionHashes':accepted,'acceptedPreserved':len(accepted),'keysUnchanged':True,'originalRecordsUnchanged':True,'sourceInspectionPath':ip,'sourceInspectionSha256':sha(ip),'historyPath':str(hp.relative_to(R)),'historySha256':sha(str(hp.relative_to(R))),'validationPath':vp,'validationSha256':sha(vp),'independentReviewComplete':False,'changes':changes,'scope':'Narrow source metadata and visible-assumption repairs. No numerical/runtime claim, no self-approval, no canonical bank or Git changes.'}
 write(f'{D}/{B}-v{version}-repair-manifest.json',m);write(f'{D}/{B}-v{version}-minimal-bindings.json',{k:m[k]for k in ['batchId','revisionAuthorId','packet','packetSha256','questionHashes']});results.append(m)
print(json.dumps([{k:m[k]for k in ['batchId','packet','packetSha256','acceptedPreserved']}for m in results],indent=2))
