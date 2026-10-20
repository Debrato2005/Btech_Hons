"""Four narrow assignment quality repairs; keep all accepted hashes exact."""
from pathlib import Path
import json,copy,hashlib,datetime,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import question_hash,schema_errors,validate_bank
B='ASSIGN-W01';WHO='build_offline_study_interface:assignment-W01-v2-repair'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
mp=f'audits/assignment-coverage/{B}-v2-repair-manifest.json';assert not(R/mp).exists();p=f'data/question-batches/{B}.json';old=read(p);b=copy.deepcopy(old);h=R/f'data/history/{B}';h.mkdir(exist_ok=True,parents=True);assert not(h/'v1.json').exists();(h/'v1.json').write_bytes((R/p).read_bytes());(h/'blind-v1.json').write_bytes((R/f'audits/blind-{B}.json').read_bytes());summary=read('audits/assignment-coverage/W01-independent-review-summary.json');accepted=summary['acceptedQuestionHashes'];flags={x['questionId']for x in summary['flaggedQuestions']};qq={q['id']:q for q in b['questions']}
for i in flags:
 q=qq[i];q.update(version=2,status='draft',reviewIds=[],revisionAuthors=list(dict.fromkeys(q.get('revisionAuthors',[])+[WHO])))
 if q.get('conflictResolution'):q['conflictResolution']['questionVersion']=2
q=qq[f'{B}-Q002'];o=next(o for o in q['options']if 'execution speed' in o['text']);o['text']='Treat factory joint calibration alone as proof that the CAD workpiece frame already matches the installed physical fixture.';q['solution']['optionExplanations'][o['id']]='Factory joint calibration does not by itself register a separately installed fixture or tool/work-frame relationship to the CAD cell.'
q=qq[f'{B}-Q003'];q['stem']='A robot learns a reward-maximizing policy represented by a deep neural network. Which description applies to this learning method?'
q=qq[f'{B}-Q004'];o=next(o for o in q['options']if 'positive' in o['text']);o['text']='The transition rule is stationary over time, even though predicting the next state still requires unrecorded earlier states.';q['solution']['optionExplanations'][o['id']]='Time invariance is not state sufficiency: a stationary process can still require past information absent from s_t.'
q=qq[f'{B}-Q009'];q['stem']='Navigation and speech-recognition responsibilities are divided into separately developed, replaceable components connected by agreed messages. Which principle names this division into functional units?';correct=q['correctOptionIds'][0];others=[o['id']for o in q['options']if o['id']!=correct];pairs=[('Modularity.','Modularity names the division of system responsibilities into separately developed and integrated functional units.'),('Inheritance.','Inheritance shares or specializes implementation through a class hierarchy; no such hierarchy is the design decision described.'),('Polymorphism.','Polymorphism supports alternative implementations of a common operation or interface; it does not name the functional division itself.'),('Encapsulation.','Encapsulation controls access to internal state and implementation. It can support modular design, but the specified decision is partitioning responsibilities, not an access-hiding rule.')];mpids=dict(zip([correct]+others,pairs))
for o in q['options']:o['text']=mpids[o['id']][0]
q['solution']['optionExplanations']={i:pair[1]for i,pair in mpids.items()};q['solution']['justification']=q['solution']['simpleExplanation']=pairs[0][1];q['assumptions']=['Classify the explicitly stated division of responsibilities; the scenario does not assert an inheritance hierarchy, runtime substitution mechanism or private-state access rule. Other principles can coexist without being the named division.']
for q in b['questions']:
 if q['id']in flags:
  q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']]for o in q['options']if o['id']not in q['correctOptionIds']];q['revisionCheckScope']='Four conceptual quality repairs only; keys and original-source records unchanged. No new numerical execution claim.'
  for cid in q['conceptIds']:next(c for c in b['concepts']if c['id']==cid)['description']=q['solution']['justification']
for i,hsh in accepted.items():assert qq[i]==next(q for q in old['questions']if q['id']==i) and question_hash(qq[i])==hsh
for q in b['questions']:assert sha(q['originalRecordPath'])==q['originalRecordSha256'];assert not schema_errors(q,read('data/schema.question.json'))
bank=read('data/bank.json');cq={q['id']:q for q in bank['questions']};bank['questions']=[q for q in bank['questions']if q['id']not in qq]+[copy.deepcopy(cq[q['id']])if q['id']in accepted and q['id']in cq and question_hash(cq[q['id']])==question_hash(q)else q for q in b['questions']];ids={c['id']for c in b['concepts']};bank['concepts']=[c for c in bank['concepts']if c['id']not in ids]+b['concepts'];rep=validate_bank(bank,root=R,check_files=False);write(f'audits/assignment-coverage/{B}-v2-validation.json',rep);assert rep['valid'],rep['errors'];write(p,b)
packet=[]
for q in b['questions']:
 if q['id']not in flags:continue
 x={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None);c['locator']=f"Assignment Week 1, source item {int(q['assignmentSourceItemId'][-2:])}, physical page {c['physicalPage']}: inspect the item region visible on this page."
 packet.append(x)
pp=f'audits/blind-{B}-v2.json';write(pp,packet);m={'batchId':B,'revisionAuthorId':WHO,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packet':pp,'packetSha256':sha(pp),'questionHashes':{q['id']:question_hash(q)for q in b['questions']if q['id']in flags},'acceptedQuestionHashes':accepted,'acceptedPreserved':6,'keysUnchanged':True,'originalRecordsUnchanged':True,'independentReviewComplete':False,'scope':'Narrow distractor/stem repairs. Existing 28-page source inspection and original-source evidence retained. No additional mathematical or runtime result claimed.'};write(mp,m);write(f'audits/assignment-coverage/{B}-v2-minimal-bindings.json',{k:m[k]for k in ['batchId','revisionAuthorId','packet','packetSha256','questionHashes']});print(json.dumps({'packet':pp,'sha256':sha(pp),'acceptedPreserved':6}))
