"""Three narrow metadata/cue repairs after independent W11/W12 review. Never rerun."""
from assignment_second_half_common import *
from validate import validate_bank,question_hash
import sys
w=int(sys.argv[1]);assert w in (11,12);B=f'ASSIGN-W{w:02}';WHO='finish_assignment_authoring:W11-W12-v2-narrow-repair'
manifest=f'audits/assignment-coverage/{B}-v2-repair-manifest.json';assert not(ROOT/manifest).exists()
p=f'data/question-batches/{B}.json';old=json.loads((ROOT/p).read_text());b=copy.deepcopy(old);qq={q['id']:q for q in b['questions']}
summary=json.loads((ROOT/f'audits/assignment-coverage/{B}-recovery-independent-review-summary.json').read_text());accepted=summary['acceptedQuestionHashes'];flags={q['questionId']for q in summary['flaggedQuestions']}
assert flags==({B+'-Q005'}if w==11 else {B+'-Q006',B+'-Q010'})
history=ROOT/f'data/history/{B}';history.mkdir(parents=True,exist_ok=True)
for src,dst in [(p,'v1.json'),(f'audits/blind-{B}.json','blind-v1.json'),(f'audits/blind-binding-{B}.json','blind-binding-v1.json')]:
 assert not(history/dst).exists();(history/dst).write_bytes((ROOT/src).read_bytes())
for qid in flags:
 q=qq[qid];q.update(version=2,status='draft',reviewIds=[],revisionAuthors=list(dict.fromkeys(q.get('revisionAuthors',[])+[WHO])))
 if q.get('conflictResolution'):q['conflictResolution']['questionVersion']=2
if w==11:
 q=qq[B+'-Q005'];c=next(c for c in q['citations']if c['physicalPage']==51);assert c['kind']=='equation';c['kind']='statement'
else:
 qq[B+'-Q006']['stem']='Which description best matches the role of ROS 2 for autonomous navigation presented in Week 12 item 6?'
 qq[B+'-Q010']['assumptions']=['Compare the physical mechanism rather than overall system safety certification; taking up energy need not imply irreversible energy dissipation.']
checks=[]
def ck(n,v):assert v,n;checks.append(n)
for qid,hsh in accepted.items():
 ck(qid+' accepted object unchanged',qq[qid]==next(q for q in old['questions']if q['id']==qid));ck(qid+' accepted hash unchanged',qhash(qq[qid])==hsh)
for q in b['questions']:
 prev=next(z for z in old['questions']if z['id']==q['id'])
 ck(q['id']+' original record unchanged',sha(q['originalRecordPath'])==q['originalRecordSha256']==prev['originalRecordSha256'])
 ck(q['id']+' options keys and numerical working unchanged',all(q[field]==prev[field] for field in ['options','correctOptionIds','solution']))
 if q['id']in flags:
  z=copy.deepcopy(q);z['version']=prev['version'];z.pop('revisionAuthors',None)
  if z.get('conflictResolution'):z['conflictResolution']['questionVersion']=prev['conflictResolution']['questionVersion']
  if w==11:next(c for c in z['citations']if c['physicalPage']==51)['kind']='equation'
  elif q['id'].endswith('006'):z['stem']=prev['stem']
  else:z['assumptions']=prev['assumptions']
  ck(q['id']+' only requested narrow changes',z==prev)
bank=json.loads((ROOT/'data/bank.json').read_text());baseline=validate_bank(copy.deepcopy(bank),ROOT,check_files=False);origbank={q['id']:q for q in bank['questions']}
rows=[copy.deepcopy(origbank[q['id']])if q['id']in accepted and q['id']in origbank and qhash(origbank[q['id']])==qhash(q)else copy.deepcopy(q)for q in b['questions']]
bank['questions']=[q for q in bank['questions']if q['id']not in qq]+rows
ids={c['id']for c in b['concepts']};bank['concepts']=[c for c in bank['concepts']if c['id']not in ids]+copy.deepcopy(b['concepts'])
# Merge author inspected metadata into memory only if not already integrated.
sm={s['id']:s for s in bank['slides']}
for s in json.loads((ROOT/f'data/inspection-batches/{B}-author.json').read_text())['slides']:
 new=copy.deepcopy(s);new['conceptIds']=sorted(set(sm[s['id']]['conceptIds'])|set(new['conceptIds']));sm[s['id']]=new
bank['slides']=list(sm.values());v=validate_bank(bank,ROOT,check_files=False)
allowed={'Learning extractor activation does not match independent approval/code hashes.','Extractor code hash mismatch: app/app.js'}
assert set(v['errors'])<=set(baseline['errors'])<=allowed,v['errors']
v['questionDeltaValid']=not(set(v['errors'])-set(baseline['errors']));v['baselineErrors']=baseline['errors'];v['scope']='Question-only delta; any unchanged app extractor-policy gap remains pending independent app revision.'
dump(f'audits/assignment-coverage/{B}-v2-author-validation.json',v);dump(p,b)
packet=[]
for q in b['questions']:
 if q['id']not in flags:continue
 z={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','cognitiveSkill','week','lectureId','topic','subtopic','assumptions','options')};z['citations']=[{k:copy.deepcopy(v)for k,v in c.items()if k!='evidenceText'}for c in q['citations']];packet.append(z)
pp=f'audits/blind-{B}-v2.json';dump(pp,{'batchId':B,'instructions':'Review only these revised objects against actual source pages before keyed reveal. Original source keys are visible; generated keys/solutions omitted. The prior reviewer saw version 1 keys; disclose this prior-version exposure.','questions':packet})
bind={'packetSha256':sha(pp),'questions':[{'id':q['id'],'version':q['version'],'sha256':qhash(q)}for q in b['questions']if q['id']in flags]};dump(f'audits/blind-binding-{B}-v2.json',bind)
dump(f'audits/{B}-v2-author-checks.json',{'role':'Narrow author metadata/wording checks, not independent review','checkedAt':NOW(),'checks':checks,'newNumericalComputationClaimed':False,'priorExactNumericalWorkUnchanged':True,'questionHashes':{q['id']:qhash(q)for q in b['questions']if q['id']in flags},'acceptedQuestionHashes':accepted,'originalRecordsUnchanged':True})
dump(manifest,{'batchId':B,'revisionAuthorId':WHO,'frozenAt':NOW(),'packet':pp,'packetSha256':sha(pp),'binding':f'audits/blind-binding-{B}-v2.json','questionHashes':{q['id']:qhash(q)for q in b['questions']if q['id']in flags},'acceptedQuestionHashes':accepted,'acceptedPreserved':len(accepted),'keysOptionsSolutionsUnchanged':True,'originalRecordsUnchanged':True,'independentReviewComplete':False,'sourceAnswerExposure':True,'globalPolicyPending':not v['valid'],'globalValidationErrors':v['errors'],'questionDeltaValid':v['questionDeltaValid'],'scope':'Change only the prose-input citation kind on page51.'if w==11 else 'Make Q006 stem neutral; remove named mechanism from Q010 assumptions while retaining physical-safety qualification in the unchanged solution.'})
print('FROZEN',B,'v2',sha(pp),'accepted preserved',len(accepted),len(checks),'checks')
