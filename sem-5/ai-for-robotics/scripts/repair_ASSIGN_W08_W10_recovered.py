"""Repair only the five independent flags; preserve fifteen accepted objects byte-exact in JSON form."""
from assignment_second_half_common import *
from validate import validate_bank,question_hash,schema_errors
import sys,re
w=int(sys.argv[1]);assert w in (8,10);B=f'ASSIGN-W{w:02}';WHO='finish_assignment_authoring:W08-W10-narrow-repair'
path=f'data/question-batches/{B}.json';manifest=f'audits/assignment-coverage/{B}-v2-repair-manifest.json'
assert not (ROOT/manifest).exists(),'Already repaired'
old=json.loads((ROOT/path).read_text());b=copy.deepcopy(old);qq={q['id']:q for q in b['questions']}
review=json.loads((ROOT/f'audits/assignment-coverage/{B}-independent-review-summary.json').read_text());accepted=review['acceptedQuestionHashes'];flags={f['questionId']for f in review['flaggedQuestions']}
assert flags==({f'{B}-Q{i:03}'for i in [1,2,6,8]}if w==8 else {f'{B}-Q004'})
originals={q['originalRecordPath']:sha(q['originalRecordPath']) for q in b['questions']}
history=ROOT/f'data/history/{B}';history.mkdir(parents=True,exist_ok=True)
for src,dest in [(path,'v1.json'),(f'audits/blind-{B}.json','blind-v1.json'),(f'audits/blind-binding-{B}.json','blind-binding-v1.json')]:
 if (history/dest).exists():
  assert (history/dest).read_bytes()==(ROOT/src).read_bytes(),'Existing history mismatch'
 else:(history/dest).write_bytes((ROOT/src).read_bytes())
for qid in flags:
 q=qq[qid];q.update(version=2,status='draft',reviewIds=[],revisionAuthors=list(dict.fromkeys(q.get('revisionAuthors',[])+[WHO])))
 if q.get('conflictResolution'):q['conflictResolution']['questionVersion']=2
if w==8:
 q=qq[B+'-Q001'];q['stem']=q['stem'].replace('Which path and cost are returned?','Which path is returned?')
 for o in q['options']:o['text']=o['text'].split(', ')[0]
 q['difficultyRationale']='Requires path-cost calculation and/or frontier relaxation; no option prints its total cost.'
 q=qq[B+'-Q002'];q['citations']=[C(35,'Week 8 item 2, heuristic prompt and choices','The heuristic estimates cost-to-go from the current node to the goal.'),C(35,'Week 8 item 3, explanatory equation immediately below the choices','A* expands the smallest total estimated cost f(n)=g(n)+h(n).','equation')]
 q=qq[B+'-Q006'];q['citations'][0]['locator']='Assignment physical page 36: Week 8 item 6, opening numeric prompt at page bottom, ending before the first next-state value.';q['citations'][1]['locator']='Assignment physical page 37: Week 8 item 6 continuation at page top, remaining numeric prompt and Bellman-target worked equations; no multiple-choice options are printed.'
 q=qq[B+'-Q008'];q['citations']=[C(37,'Week 8 item 8, conceptual clock-bias prompt and four choices','The prompt names cδt and the identified clock discrepancy is between the satellite atomic clock and receiver clock.','statement')]
 q['assumptions'].append('The full equation ρ=R+cδt, numerical constants and sign convention are explicit added premises of this adaptation, not a transcription of a full equation on the cited assignment page.')
 next(o for o in q['options']if o['id']=='o3')['text']='A receiver timing offset contributes +600000 m to pseudorange.'
 q['solution']['optionExplanations']['o3']='600000 m would follow from using 2×10⁻³ s (2 ms), not the supplied 2 μs=2×10⁻⁶ s.'
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']]for o in q['options']if o['id']not in q['correctOptionIds']]
else:
 qq[B+'-Q004']['conflictResolution']['physicalPage']=47
for q in b['questions']:
 if q['id']in flags:
  assert q['correctOptionIds']==next(z for z in old['questions']if z['id']==q['id'])['correctOptionIds']
  for cid in q['conceptIds']:next(c for c in b['concepts']if c['id']==cid)['description']=q['solution']['justification']
for qid,hsh in accepted.items():
 assert qq[qid]==next(q for q in old['questions']if q['id']==qid),'Accepted object changed'
 assert qhash(qq[qid])==hsh,'Accepted hash changed'
for p,hsh in originals.items():assert sha(p)==hsh,'Original record changed'
# Exact computations for affected mathematical questions only, stdlib.
from fractions import Fraction as R
import heapq
checks=[]
def ck(n,v):assert v,n;checks.append(n)
if w==8:
 graph={n:[] for n in 'ABCDEFG'}
 for a,c,cost in [('A','B',5),('A','C',2),('B','D',6),('B','E',3),('C','F',4),('D','E',2),('D','G',6),('E','F',1),('F','G',3)]:graph[a].append((c,cost));graph[c].append((a,cost))
 frontier=[(0,'A',['A'])];best={'A':0};popped=[]
 while frontier:
  cost,u,pathnodes=heapq.heappop(frontier)
  if cost!=best[u]:continue
  popped.append((u,cost))
  if u=='E':break
  for v,costedge in graph[u]:
   new=cost+costedge
   if new<best.get(v,float('inf')):best[v]=new;heapq.heappush(frontier,(new,v,pathnodes+[v]))
 ck('UCS selected route and trace',(cost,pathnodes,popped)==(7,['A','C','F','E'],[('A',0),('C',2),('B',5),('F',6),('E',7)]))
 ck('UCS choices hide costs',all(not re.search(r'\d',o['text'])for o in qq[B+'-Q001']['options']))
 ck('A-star zero heuristic',all(g+0==g for g in range(100)))
 ck('DQN values',(R(1)+R('.9')*5,R(1)+R('.9')*5-R('4.3'),R(1))==(R('5.5'),R('1.2'),R(1)))
 ck('clock range contribution',300000000*R(2,1000000)==600)
 ck('clock millisecond distractor',300000000*R(2,1000)==600000)
 ck('clock nanosecond distractor',300000000*R(2,1000000000)==R('.6'))
else:
 ck('correct premise page',qq[B+'-Q004']['citations'][0]['physicalPage']==46)
 ck('correct conflict page',qq[B+'-Q004']['conflictResolution']['physicalPage']==47 and any(c['physicalPage']==47 and c['role']=='conflict'for c in qq[B+'-Q004']['citations']))
 oldq=next(q for q in old['questions']if q['id']==B+'-Q004');newq=copy.deepcopy(qq[B+'-Q004']);newq['version']=oldq['version'];newq['conflictResolution']['questionVersion']=oldq['conflictResolution']['questionVersion'];newq['conflictResolution']['physicalPage']=oldq['conflictResolution']['physicalPage'];newq.pop('revisionAuthors',None)
 ck('only metadata and version changed',newq==oldq)
for q in b['questions']:ck(q['id']+' original unchanged',sha(q['originalRecordPath'])==q['originalRecordSha256'])
bank=json.loads((ROOT/'data/bank.json').read_text());baseline=validate_bank(copy.deepcopy(bank),ROOT,check_files=False);oldbank={q['id']:q for q in bank['questions']}
rows=[copy.deepcopy(oldbank[q['id']])if q['id']in accepted and q['id']in oldbank and qhash(oldbank[q['id']])==qhash(q)else copy.deepcopy(q)for q in b['questions']]
ids=set(qq);bank['questions']=[q for q in bank['questions']if q['id']not in ids]+rows
ids={c['id']for c in b['concepts']};bank['concepts']=[c for c in bank['concepts']if c['id']not in ids]+copy.deepcopy(b['concepts'])
rep=validate_bank(bank,ROOT,check_files=False)
allowed={'Learning extractor activation does not match independent approval/code hashes.','Extractor code hash mismatch: app/app.js'}
assert set(rep['errors'])<=set(baseline['errors'])<=allowed,rep['errors']
rep['authorValidationScope']='Question-only delta passes: no candidate errors beyond independently observed baseline app policy/code hash gap. Global integration pending independent app policy revision.'
rep['baselineErrors']=baseline['errors'];rep['candidateAdditionalErrors']=sorted(set(rep['errors'])-set(baseline['errors']))
dump(f'audits/assignment-coverage/{B}-v2-author-validation.json',rep)
dump(f'data/question-batches/{B}.json',b)
packet=[]
for q in b['questions']:
 if q['id']not in flags:continue
 x={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','cognitiveSkill','week','lectureId','topic','subtopic','assumptions','options')}
 x['citations']=[{k:copy.deepcopy(v)for k,v in c.items()if k!='evidenceText'}for c in q['citations']]
 packet.append(x)
pp=f'audits/blind-{B}-v2.json';dump(pp,{'batchId':B,'instructions':'Solve these narrow revisions from actual cited pages before revealing keyed batches or author repair records. Original printed source keys are visible; disclose that exposure. Exact page-region locators are retained; author evidenceText and generated answers are hidden.','questions':packet})
binding={'packetSha256':sha(pp),'questions':[{'id':q['id'],'version':q['version'],'sha256':qhash(q)}for q in b['questions']if q['id']in flags]};dump(f'audits/blind-binding-{B}-v2.json',binding)
dump(f'audits/{B}-v2-author-checks.json',{'role':'Narrow stdlib author checks, not independent review','checkedAt':NOW(),'pythonExecutable':sys.executable,'checks':checks,'acceptedObjectsPreserved':len(accepted),'acceptedQuestionHashes':accepted,'questionHashes':{q['id']:qhash(q)for q in b['questions']if q['id']in flags},'originalRecordsUnchanged':True})
mp={'batchId':B,'revisionAuthorId':WHO,'frozenAt':NOW(),'packet':pp,'packetSha256':sha(pp),'binding':f'audits/blind-binding-{B}-v2.json','questionHashes':{q['id']:qhash(q)for q in b['questions']if q['id']in flags},'acceptedQuestionHashes':accepted,'acceptedPreserved':len(accepted),'keysUnchanged':True,'originalRecordsUnchanged':True,'independentReviewComplete':False,'sourceAnswerExposure':True,'globalPolicyPending':not rep['valid'],'globalValidationErrors':rep['errors'],'questionDeltaValid':not rep['candidateAdditionalErrors'],'actualPagesRevisited':[34,35,36,37,38]if w==8 else [46,47],'scope':'Only independent flags: option cost clue, exact region bindings and a timing-unit distractor.'if w==8 else 'Only conflictResolution.physicalPage changes from 46 to 47, alongside required version/revision metadata.'};dump(manifest,mp)
dump(f'audits/assignment-coverage/{B}-v2-source-view-log.json',{'authorId':WHO,'viewedAt':NOW(),'sourceAnswerExposure':True,'fullyBlind':False,'method':'Actual full-page WEBP previews read with view_image, cross-checked with extracted text; no external routes or runtime.','pages':[{'physicalPage':p,'previewSha256':sha(f'sources/previews/assignments/page-{p:04}.webp'),'observation':{34:'Item 1 full graph and all weights; 7 km worked minimum via C/F.',35:'Item 2 heuristic role; item 3 lower-region f=g+h equation.',36:'Item 6 begins at bottom and breaks before next-state numeric values.',37:'Item 6 numeric continuation and Bellman working, no options; item 8 conceptual prompt and choices with cδt, not a full pseudorange equation.',38:'Item 8 answer letter/reference only at top.',46:'Item 4 premise explicitly WV64×20.',47:'Item 4 V multiplication line incorrectly uses64×16; this is the conflict location.'}[p]}for p in mp['actualPagesRevisited']]})
print('FROZEN narrow repair',B,sha(pp),'accepted preserved',len(accepted))
