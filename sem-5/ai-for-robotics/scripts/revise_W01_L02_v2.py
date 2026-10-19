"""Apply independent review findings only to 26 flagged L02 items. Preserve 79 approved hashes."""
import json,copy,hashlib,datetime,sys,heapq
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash,validate_bank,schema_errors
p=ROOT/'data/question-batches/W01-L02.json';b=json.loads(p.read_text());before=copy.deepcopy(b)
reviews=json.loads((ROOT/'data/reviews/W01-L02-v1-independent.json').read_text())
verified={r['questionId']:r for r in reviews if r['decision']=='verified'}
flagged={r['questionId']:r for r in reviews if r['decision']=='flagged'}
assert len(verified)==79 and len(flagged)==26
qs={q['id']:q for q in b['questions']}
assert all(qs[i]['version']==1 for i in flagged),'Do not reapply to revised or reviewer-edited items.'
assert all(question_hash(qs[i])==r['questionSha256'] for i,r in verified.items())
def q(n):return qs[f'W01-L02-Q-{n:03d}']
def option(n,k,text,reason):
 x=q(n);oid=x['id']+f'-o{k}';next(o for o in x['options'] if o['id']==oid)['text']=text;x['solution']['optionExplanations'][oid]=reason
for i in flagged:
 qs[i]['version']=2;qs[i]['status']='draft';qs[i]['reviewIds']=[]
# Reviewer-approved answer content remains unchanged when difficulty was the sole issue.
for n in [22,35,41,47,49,53,54,58,68,71,74,75,84,85,89,90,98,100,102,103,105]:q(n)['difficulty']='easy' if n in [22,53,58] else 'medium'
# A plausible nearby application-category confusion replaces the absolute falsehood.
option(30,4,'Anomaly/fault detection is the application that forecasts pedestrian paths using social-force or attention models','This assigns the separate Path Prediction box to anomaly/fault detection. The anomaly box instead concerns sensor failures and unusual robot behavior.')
q(30)['difficulty']='medium'
q(30)['solution'].update({'justification':'The slide separately lists learned locomotion, imitation, human-robot interaction, anomaly/fault detection and path prediction. Forecasting pedestrian trajectories belongs to Path Prediction, not the anomaly/fault-detection box.','simpleExplanation':'Detecting an abnormal robot or sensor is not the same task as forecasting a pedestrian’s path.','misconceptions':['Nearby application boxes are related robot capabilities, but their stated tasks differ.'],'examTraps':['The stem asks for the statement that is NOT faithful; select the misassigned application.']})
# Correct the numerical distractor itself so its stated single-error explanation is exact.
option(32,4,'9','This flips the sign of the second input but keeps the bias: 3×2 + 4×1 − 1 = 9. The actual second input is −1, so this is not the correct output.')
# Concrete finite graph replaces the insufficient universal theorem wording.
x=q(56);x.update({'stem':'Compare two A-star graph-search implementations on the directed graph S→A (3), S→B (1), B→A (1), A→G (2), B→G (9). Use h(S)=4, h(A)=0, h(B)=3, h(G)=0. Both expand a minimum-f frontier state, where f=g+h, and accept G only when it is selected for expansion. R reopens an expanded state when a strictly smaller g is found; C permanently closes expanded states and ignores later improvements to them. Both update improved frontier entries. What final goal costs do R and C return, respectively?','difficulty':'hard','type':'algorithm-trace','cognitiveSkill':'algorithm','assumptions':['The finite directed graph contains only the five stated edges; S is the start and G the only goal.','All edge costs are nonnegative, and g(S)=0.','The heuristic is admissible for this graph and h(G)=0; it is not required to be consistent.','Expand a minimum-f frontier state, accept a goal only on selection for expansion, and update frontier g values on strict improvement.','R reopens previously expanded states on strict improvement; C discards improvements to permanently closed states. There are no consequential ties in these traces.','The graph and implementation policies are explicit author-specified analytical premises. The cited slide supplies f=g+h and a summary optimality claim, not this graph or full implementation proof.']})
option(56,1,'R returns 4; C returns 5','R reopens A after B improves g(A) from 3 to 2, yielding S→B→A→G with cost 4. C discards that improvement and retains S→A→G with cost 5.')
option(56,2,'R returns 5; C returns 5','This misses the stated reopening in R. Its second expansion of A improves the goal cost from 5 to 4.')
option(56,3,'R returns 4; C returns 4','C has permanently closed A before B finds the better route, so under the explicitly stated discard rule it cannot use that improved A path to lower G to 4.')
option(56,4,'R returns 5; C returns 4','This reverses the effect of reopening: R can propagate the improved path, whereas C discards it.')
x['citations'][0]['kind']='derivation';x['citations'][0]['role']='premise';x['citations'][0]['locator']='Printed slide 27, A-star box: f(n)=g(n)+h(n), summary admissibility statement. The graph and detailed duplicate/termination policies are author-specified premises, not depicted on the slide.'
x['solution'].update({'justification':'Both runs first expand S, creating A with g=3,f=3 and B with g=1,f=4. A is selected first and generates G with g=5,f=5. B is then selected and finds a better route to A with g=2. R reopens A at f=2 and then lowers G to g=4; C ignores the improvement to closed A and keeps G at g=5. The heuristic is admissible but inconsistent on B→A, demonstrating why improved-path handling matters in this fully specified example.','steps':['From S: A has g=3,h=0,f=3; B has g=1,h=3,f=4. Expand A next.','First expansion of A: G has g=3+2=5 and f=5. B still has f=4, so expand B before G.','B proposes A with g=1+1=2, improving the old g=3; its direct G proposal costs 1+9=10 and is rejected.','R reopens A with f=2 and expands it, improving G to g=2+2=4. R then selects G and returns 4.','C discards the improved route to closed A. Its remaining best G has g=5, so C selects G and returns 5.','True remaining costs are h*(G)=0, h*(A)=2, h*(B)=3 and h*(S)=4. Given h never exceeds these values, but h(B)=3 > 1+h(A)=1, so the heuristic is not consistent on B→A.'],'formulas':[{'expression':'f(n)=g(n)+h(n); candidate_g(v)=g(u)+cost(u,v)','variables':{'f(n)':'frontier priority','g(n)':'best currently stored path cost from S','h(n)':'given estimate of remaining cost','cost(u,v)':'directed edge cost'},'units':{'all':'abstract cost units'},'assumptions':['Explicit finite directed graph and duplicate/termination policies in the stem.']}],'simpleExplanation':'A looked promising early, but B later found a cheaper way to it. Reopening lets that improvement reach the goal.','misconceptions':['Admissibility and consistency are different conditions.','Discovering a goal is not the same as selecting it from the frontier.','Permanently closing states can discard necessary improvements with an inconsistent heuristic.'],'examTraps':['Track f for selection but g for the returned cost.','Reopen A only in R; do not silently give C the same policy.']})
# Distinguish the feedback-induced shift from nearby learning failure explanations.
x=q(70);x['stem']='A behavioral-cloning policy has low error on expert demonstration observations. During deployment, an early action mistake leads to observations poorly represented in those demonstrations, and subsequent mistakes lead to further deviations. Which mechanism most directly explains this pattern?';x['difficulty']='medium'
option(70,1,'Policy-induced distribution shift with compounding errors','The policy’s own actions change the states it encounters; errors on unfamiliar observations can cause further deviations.')
option(70,2,'Independent prediction noise on a fixed observation distribution','This misses the central feedback: the policy changes which observations it encounters, so the distribution is not fixed independently of its actions.')
option(70,3,'A failure to infer the expert’s reward function in inverse reinforcement learning','The specified training is behavioral cloning of observation-action pairs; no reward-inference stage is given. This is a different learning mechanism.')
option(70,4,'A simulation-to-real gap caused specifically by different rendering textures','The scenario does not establish a simulator or a rendering change. The stated mechanism is deviation into poorly represented states due to the policy’s own actions.')
x['solution'].update({'justification':'Low supervised error on expert observations does not ensure low error on the observations induced by the learned policy. An early mistake can change the next observation, move the robot away from the demonstration distribution and make later prediction errors compound.','simpleExplanation':'Training covers expert trajectories; the policy’s own mistakes can take it somewhere else.','misconceptions':['Training-set prediction quality does not alone control the state distribution induced by deployment.'],'examTraps':['Identify the action-to-next-observation feedback rather than assuming independent errors on fixed inputs.']})
# Replace a universal guarantee with a plausible panel/algorithm-role confusion.
x=q(82);x['difficulty']='medium'
option(82,4,'Stanley and PurePursuit are listed as formal-verification methods in the Safety panel','They appear in the separate Control panel as lateral-control examples, not as formal-verification methods in Safety.')
x['solution'].update({'justification':'The Safety panel lists formal verification, shadow mode, human monitoring and takeover. Stanley and PurePursuit appear in Control, specifically for lateral control. Their presence in the same vehicle architecture does not make them formal-verification methods.','simpleExplanation':'Control algorithms and safety-assurance practices occupy different roles in the diagram.','misconceptions':['Do not infer an algorithm’s role solely from its presence somewhere in an autonomous-vehicle system.'],'examTraps':['The stem asks for the unsupported Safety-panel claim, not for a nonexistent algorithm.']})
# Exact trace checks independently executed by this author; not a second-agent approval.
edges={'S':[('A',3),('B',1)],'A':[('G',2)],'B':[('A',1),('G',9)],'G':[]};h={'S':4,'A':0,'B':3,'G':0}
def run(reopen):
 g={'S':0};frontier=[(4,'S',0)];closed=set();trace=[]
 while frontier:
  f,u,old=heapq.heappop(frontier)
  if old!=g[u] or u in closed:continue
  trace.append(u)
  if u=='G':return g[u],trace
  closed.add(u)
  for v,c in edges[u]:
   if v in closed and not reopen:continue
   cand=g[u]+c
   if cand<g.get(v,float('inf')):
    g[v]=cand;closed.discard(v);heapq.heappush(frontier,(cand+h[v],v,cand))
assert run(True)==(4,['S','A','B','A','G'])
assert run(False)==(5,['S','A','B','G'])
assert 3*2+4*(-1)-1==1 and 3*2+4*1-1==9
# Prove that every approved correctness hash is unchanged and exactly the 26 flagged IDs changed.
old={z['id']:z for z in before['questions']}
changed={i for i in qs if question_hash(old[i])!=question_hash(qs[i])}
assert changed==set(flagged),(changed,set(flagged))
assert all(question_hash(qs[i])==r['questionSha256'] for i,r in verified.items())
schema=json.loads((ROOT/'data/schema.question.json').read_text())
assert not [e for z in b['questions'] for e in schema_errors(z,schema)]
b['status']='v2_revisions_awaiting_independent_review';b['coverage'].update({'questionsIndependentlyVerified':79,'questionsIndependentlyFlagged':0,'questionsRevisedAwaitingReview':26,'questionsReviewedAtCurrentVersion':79,'meaningfulAngleReview':'79 v1 questions retain independent approval; 26 revised v2 questions await exact-version review. Historical v1 flagged reviews remain in the audit trail. Full-section coverage challenge remains pending.'})
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet={'schemaVersion':'1.0.0','batchId':'W01-L02','revision':2,'status':'frozen_revisions_ready_for_independent_review','exposureNotice':'The original reviewer knows v1 answers. Record that exposure accurately; independently rederive the changed v2 content and review exact current hashes. Difficulty-only changes are enumerated in the revision summary.','questions':[{**{k:z[k] for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']},'questionSha256':question_hash(z)} for z in b['questions'] if z['id'] in flagged]}
pp=ROOT/'audits/blind-W01-L02-v2-revisions.json';pp.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
summary={'schemaVersion':'1.0.0','batchId':'W01-L02','revision':2,'revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preservedApprovedCount':79,'preservedApprovedHashes':{i:question_hash(qs[i]) for i in verified},'revisedCount':26,'changes':[{'questionId':i,'oldVersion':1,'newVersion':2,'oldSha256':question_hash(old[i]),'newSha256':question_hash(qs[i]),'changedFields':[k for k in qs[i] if qs[i][k]!=old[i].get(k)],'findingsAddressed':flagged[i]['findings']} for i in sorted(flagged)],'authorChecks':{'Q032CorrectOutput':1,'Q032SignErrorDistractor':9,'Q056ReopenTrace':run(True),'Q056PermanentCloseTrace':run(False),'independentVerification':False},'blindPacketSha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'authorBatchSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'Only the 26 independently flagged questions changed. Historical review records retained. No updated question marked verified by its author.'}
(ROOT/'audits/W01-L02-v2-revision-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['preservedApprovedCount','revisedCount','blindPacketSha256','authorBatchSha256','authorChecks']},indent=2))
