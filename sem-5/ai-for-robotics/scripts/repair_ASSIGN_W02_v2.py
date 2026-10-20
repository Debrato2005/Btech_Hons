"""One narrow assignment quality repair; keep all accepted hashes exact."""
from pathlib import Path
import json,copy,hashlib,datetime,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import question_hash,schema_errors,validate_bank
B='ASSIGN-W02';WHO='build_offline_study_interface:assignment-W02-v2-repair'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
mp=f'audits/assignment-coverage/{B}-v2-repair-manifest.json';assert not(R/mp).exists();p=f'data/question-batches/{B}.json';old=read(p);b=copy.deepcopy(old);h=R/f'data/history/{B}';h.mkdir(exist_ok=True,parents=True);assert not(h/'v1.json').exists();(h/'v1.json').write_bytes((R/p).read_bytes());(h/'blind-v1.json').write_bytes((R/f'audits/blind-{B}.json').read_bytes());summary=read('audits/assignment-coverage/W02-independent-review-summary.json');accepted=summary['acceptedQuestionHashes'];flags={x['questionId']for x in summary['flaggedQuestions']};qq={q['id']:q for q in b['questions']}
for i in flags:
 q=qq[i];q.update(version=2,status='draft',reviewIds=[],revisionAuthors=list(dict.fromkeys(q.get('revisionAuthors',[])+[WHO])))
 if q.get('conflictResolution'):q['conflictResolution']['questionVersion']=2
q=qq[f'{B}-Q005'];o=next(o for o in q['options']if o['id']=='o3');o['text']='Transfer the same eight-solution upper bound after confirming a₃ = a₅ = 0, without checking the remaining joint-axis geometry.';q['solution']['optionExplanations']['o3']='Matching two DH lengths does not establish matching full architecture. The same zeros alone do not justify transferring the source’s geometry-specific upper bound.'
for q in b['questions']:
 if q['id']in flags:
  q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']]for o in q['options']if o['id']not in q['correctOptionIds']];q['revisionCheckScope']='One conceptual distractor repair only; keys and original-source records unchanged. No new numerical execution claim.'
  for cid in q['conceptIds']:next(c for c in b['concepts']if c['id']==cid)['description']=q['solution']['justification']
for i,hsh in accepted.items():assert qq[i]==next(q for q in old['questions']if q['id']==i) and question_hash(qq[i])==hsh
for q in b['questions']:assert sha(q['originalRecordPath'])==q['originalRecordSha256'];assert not schema_errors(q,read('data/schema.question.json'))
bank=read('data/bank.json');cq={q['id']:q for q in bank['questions']};bank['questions']=[q for q in bank['questions']if q['id']not in qq]+[copy.deepcopy(cq[q['id']])if q['id']in accepted and q['id']in cq and question_hash(cq[q['id']])==question_hash(q)else q for q in b['questions']];ids={c['id']for c in b['concepts']};bank['concepts']=[c for c in bank['concepts']if c['id']not in ids]+b['concepts'];rep=validate_bank(bank,root=R,check_files=False);write(f'audits/assignment-coverage/{B}-v2-validation.json',rep);assert rep['valid'],rep['errors'];write(p,b)
packet=[]
for q in b['questions']:
 if q['id']not in flags:continue
 x={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None);c['locator']=f"Assignment Week 2, source item {int(q['assignmentSourceItemId'][-2:])}, physical page {c['physicalPage']}: inspect the item region visible on this page."
 packet.append(x)
pp=f'audits/blind-{B}-v2.json';write(pp,packet);m={'batchId':B,'revisionAuthorId':WHO,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packet':pp,'packetSha256':sha(pp),'questionHashes':{q['id']:question_hash(q)for q in b['questions']if q['id']in flags},'acceptedQuestionHashes':accepted,'acceptedPreserved':9,'keysUnchanged':True,'originalRecordsUnchanged':True,'independentReviewComplete':False,'scope':'Narrow geometry-scope distractor repair. Existing source inspection, including fresh actual page 6 reinspection, and original-source evidence retained. No additional mathematical or runtime result claimed.'};write(mp,m);write(f'audits/assignment-coverage/{B}-v2-minimal-bindings.json',{k:m[k]for k in ['batchId','revisionAuthorId','packet','packetSha256','questionHashes']});print(json.dumps({'packet':pp,'sha256':sha(pp),'acceptedPreserved':9}))
