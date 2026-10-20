"""Freeze L59 quality repairs and bounded gaps without modifying accepted records."""
from pathlib import Path
import json,copy,hashlib,sys,datetime
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import question_hash,schema_errors,validate_bank
from authoring_helpers import SHA
B='W12-L59';WHO='build_offline_study_interface:L59-v2-repair'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
mp=f'audits/{B}-v2-repair-manifest.json';assert not(R/mp).exists(),'Frozen'
b=read(f'data/question-batches/{B}.json');old=read(f'data/history/{B}/{B}-v1.json');summary=read(f'audits/{B}-independent-review-summary.json');accepted=summary['acceptedQuestionHashes'];flags={x['questionId']for x in summary['flaggedQuestions']};oq={q['id']:q for q in old['questions']};changed=[q for q in b['questions']if q['id']not in accepted];checkpath=f'audits/{B}-v2-author-checks.json';checks=read(checkpath);assert checks['allPassed']
assert len(b['questions'])==70 and len(changed)==16
for q in changed:
 assert q['status']=='draft' and not q['reviewIds'] and q['version']==(2 if q['id']in flags else 1)
 q['authorCheckEvidence']={'path':checkpath,'sha256':sha(checkpath),'independentReview':False,'scope':checks['scope']}
qq={q['id']:q for q in b['questions']}
for i,h in accepted.items():assert qq[i]==oq[i] and question_hash(qq[i])==h,i
for q in old['questions']:
 if q.get('conflictResolution'):assert q['conflictResolution']['sourceClaim']==qq[q['id']]['conflictResolution']['sourceClaim']
assert sha(f'audits/{B}-source-issues.json')==sha(f'data/history/{B}/source-issues-v1.json')
ins=read(f'data/inspection-batches/{B}.json')
for s in ins['slides']:s['conceptIds']=list(dict.fromkeys(s['conceptIds']+[c['id']for c in b['concepts']if s['id']in c['slideIds']]))
for kind,items in [('question',b['questions']),('concept',b['concepts']),('slide',ins['slides'])]:
 for x in items:assert not schema_errors(x,read(f'data/schema.{kind}.json')),(x['id'],schema_errors(x,read(f'data/schema.{kind}.json')))
bank=read('data/bank.json');cq={q['id']:q for q in bank['questions']};bank['questions']=[q for q in bank['questions']if not q['id'].startswith(B+'-')]+[copy.deepcopy(cq[q['id']])if q['id']in accepted and q['id']in cq and question_hash(cq[q['id']])==question_hash(q)else copy.deepcopy(q)for q in b['questions']];bank['concepts']=[c for c in bank['concepts']if not c['id'].startswith(B+'-')]+copy.deepcopy(b['concepts']);sm={s['id']:s for s in ins['slides']}
for i,s in enumerate(bank['slides']):
 if s['id']in sm:
  ns=copy.deepcopy(sm[s['id']]);ns['conceptIds']=list(dict.fromkeys([c for c in s['conceptIds']if not c.startswith(B+'-')]+ns['conceptIds']));bank['slides'][i]=ns
report=validate_bank(bank,root=R,check_files=False);write(f'audits/{B}-v2-preflight-validation.json',report);assert report['valid'],report['errors']
write(f'data/question-batches/{B}.json',b);write(f'data/inspection-batches/{B}.json',ins);packet=[]
for q in changed:
 p={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in p['citations']:c.pop('evidenceText',None);c['locator']=f"Lecture L59, physical PDF page {c['physicalPage']}, printed footer {c['physicalPage']-1876}: inspect the {c['kind']} content on this page. Neutral review locator."
 packet.append(p)
pp=f'audits/blind-{B}-v2.json';write(pp,packet);obs=read(f'audits/{B}-v2-source-observations.json')
manifest={'batchId':B,'revisionAuthorId':WHO,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceId':'lectures','sourceSha256':SHA,'revisionCount':11,'newQuestionCount':5,'totalQuestionCount':70,'acceptedPreserved':54,'acceptedQuestionHashes':accepted,'packet':pp,'packetSha256':sha(pp),'questionHashes':{q['id']:question_hash(q)for q in changed},'previousQuestionHashes':{q['id']:question_hash(oq[q['id']])for q in changed if q['id']in oq},'boundedGapDispositions':{f'L59-GAP-{n:02d}':f'{B}-Q{65+n:03d}, draft pending independent coverage review'for n in range(1,6)},'actualRepairPagesViewed':[p['physicalPage']for p in obs['pages']],'originalSourceIssuesUnchanged':True,'originalSourceIssuesSha256':sha(f'audits/{B}-source-issues.json'),'authorChecks':checks,'independentReviewComplete':False,'preflight':'All schemas and read-only integrated integrity validation pass; all 54 accepted whole objects and original source claims preserved. Added pinhole model is self-contained. Original implementation and denied-document boundaries unchanged.'};manifest['files']={p:sha(p)for p in [f'data/question-batches/{B}.json',f'data/inspection-batches/{B}.json',pp,checkpath,f'audits/{B}-v2-source-observations.json','scripts/repair_W12_L59_v2.py','scripts/check_W12_L59_v2_author.py']};write(mp,manifest)
minimal={k:manifest[k]for k in ['batchId','revisionAuthorId','sourceId','sourceSha256','packet','packetSha256','questionHashes']};minimal['reviewBoundary']='Eleven revisions require prior-exposure disclosure where applicable. Five new bounded items can be solved before key access. Actual source pixels first; do not use author checks or mapping narrative as independent evidence.';write(f'audits/{B}-v2-minimal-bindings.json',minimal);print(json.dumps({k:manifest[k]for k in ['revisionCount','newQuestionCount','acceptedPreserved','packetSha256','actualRepairPagesViewed']}))
