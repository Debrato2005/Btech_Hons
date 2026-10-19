#!/usr/bin/env python3
"""Fourteen versioned L27 author revisions; preserves58 accepted whole objects."""
import json,copy,hashlib
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction as F
R=Path(__file__).resolve().parents[1];B='W06-L27';A='L27-author-20261019'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def fhash(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
manifest=f'audits/{B}-v3-review-manifest.json'
if (R/manifest).exists():raise SystemExit('L27 v3 is frozen; do not regenerate over review.')
archive=f'data/question-batches/archive/{B}-v2.json'
if not (R/archive).exists():(R/archive).write_bytes((R/f'data/question-batches/{B}.json').read_bytes())
old=read(archive);b=copy.deepcopy(old);qm={q['id']:q for q in b['questions']};rv=read('data/reviews/W06-L27-v2-independent.json');flags={r['questionId']:r for r in rv if r['decision']=='flagged'}
assert len(flags)==14
accepted=[q for q in old['questions'] if q['id'] not in flags];assert len(accepted)==58
sourcehash=fhash('audits/source-disputes-W06-L27.json')
for qid,r in flags.items():
 q=qm[qid];assert qhash(q)==r['questionSha256'];assert q['version']==2
 q.update(version=3,status='draft',reviewIds=[]);q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+[A]))
 if 'conflictResolution' in q:q['conflictResolution']['questionVersion']=3

def q(short):return qm[B+'-'+short]
def cite(short,p,kind,locator,role='premise',evidence=None):
 ci=next(c for c in q(short)['citations'] if c['physicalPage']==p);ci.update(kind=kind,role=role,locator=locator)
 if evidence is not None:ci['evidenceText']=evidence
cite('P0803-Q05',803,'code','Printed slide 5: X_lifting fourth row [5.0,1.0] and aligned fourth y_torque target49.0; the static mgr relation is supplied by the question.','premise','X_lifting=np.array([[1.0,0.5],[2.0,0.5],[1.0,1.0],[5.0,1.0]]); y_torque=np.array([4.9,9.8,9.8,49.0]).')
cite('P0804-Q02',804,'statement','Printed slide 6: right-hand Algorithm goal list, underlined “Two features: A plane.”','explicit','One feature: A straight line. Two features: A plane. Higher dimensions: A hyperplane.')
for short in ['P0804-Q04','P0804-Q05']:
 cite(short,803,'code','Printed slide 5: four X_lifting mass/extension rows and aligned y_torque labels.','premise','X_lifting=np.array([[1.0,0.5],[2.0,0.5],[1.0,1.0],[5.0,1.0]]); y_torque=np.array([4.9,9.8,9.8,49.0]).')
 cite(short,804,'code','Printed slide 6: LinearRegression construction, fit(X_lifting,y_torque), new_box=[[3.5,0.8]] and predict(new_box)[0].','premise','regressor=LinearRegression(); regressor.fit(X_lifting,y_torque); new_box=[[3.5,0.8]]; pred_torque=regressor.predict(new_box)[0].')
 cite(short,805,'statement','Printed slide 7: displayed Print Output, Robot Predicts31.04 Newton-meters for3.5 kg and0.8 m extension.','premise','Task: Lift a3.5 kg box at0.8 m extension. Robot Predicts:31.04 Newton-meters of torque required.')
 # The plane is an additional precise source premise, not a nonexistent printed derivation.
 ci=copy.deepcopy(q('P0804-Q02')['citations'][0]);ci['role']='premise';q(short)['citations'].append(ci)
item=q('P0807-Q02')
next(o for o in item['options'] if o['id']=='o1')['text']='Add measurements of relevant informative features that are currently missing from the inputs'
why={
 'o1':'The stipulated cause is missing input information. Measuring relevant missing features directly addresses that cause; increasing model capacity alone does not recover genuinely unmeasured information.',
 'o2':'More samples can improve estimation, but do not directly supply the explicitly missing input information.',
 'o3':'After optimization has converged, repeating it longer does not add measurements of the missing features.',
 'o4':'Changing the evaluation split does not itself add the missing informative measurements.'}
item['solution'].update(justification=why['o1'],simpleExplanation=why['o1'],optionExplanations={k:('Correct. ' if k=='o1' else 'Incorrect. ')+v for k,v in why.items()},misconceptions=[why[k] for k in ('o2','o3','o4')])
cite('P0807-Q02',807,'statement','Printed slide 9: right-hand Underfitting column, high training/test error and Causes: Insufficient features.','premise','Underfitting: Symptoms both training error and test error HIGH. Causes: Insufficient features; Strong regularization that stifles the model’s ability to learn.')
cite('P0812-Q02',812,'statement','Printed slide 14: Data Architecture lists only temperature and Wi-Fi inputs, no labeled output data; motivation asks for three zones.','premise','Input Features: Temperature(°C) and Wi-Fi(%) signal strength. Target Output: No labeled output data. Motivation: Based on sensor reading divide the area into3 distinct zones.')
cite('P0815-Q03',815,'figure','Printed slide 17: scatter plot labels Zone0, Zone1 and Zone2 around the three sensor groups, and marks the new reading in Zone0.','premise','Scatter plot annotations: Zone0 at the upper high-Wi-Fi group, Zone1 at the middle-right group, Zone2 at the lower-left group; new reading(23°C,85% Wi-Fi) in the upper group.')
cite('P0816-Q02',816,'table','Printed slide 18: Unsupervised Task/Robotics Application table, Anomaly detection row about abnormal joint-torque patterns and mechanical failure.','premise','Anomaly detection | Identifying abnormal in joint-torque patterns due to mechanical failure.')
cite('P0816-Q03',816,'table','Printed slide 18: Unsupervised Task/Robotics Application table, Image Compression row about similar pixel colors and fewer bits.','premise','Image Compression | Grouping similar pixel colors to represent an image using fewer bits.')
for short,prefix in [('P0812-Q02','Inference from the listed feature set: '),('P0815-Q03','Inference about a consistent renaming of the displayed groups: '),('P0816-Q02','Qualification of the table’s application example: '),('P0816-Q03','Inference from reducing representative colors: ')]:
 item=q(short);oldjust=item['solution']['justification'];item['solution']['justification']=prefix+oldjust;item['solution']['simpleExplanation']=prefix+oldjust;item['solution']['optionExplanations']['o1']='Correct. '+prefix+oldjust
methods={
 'P0807-Q04':'Interpret the prose list of potential overfitting causes in context: compare training and held-out behavior rather than infer a universal monotonic rule from iteration count. No slide equation is invoked.',
 'P0813-Q05':'Read the np.random.normal arguments and standard-deviation annotation on page813, then inspect the page815 markers beyond100% Wi-Fi; distinguish spread parameters from hard bounds. No printed equation is claimed.',
 'P0817-Q02':'Apply the supplied concrete distinction between the set {left,right,forward} and the selected member left to clarify the source’s prose definition of action.',
 'P0817-Q03':'Compare page817’s prose restriction with page818’s visible action→reward→update loop; retain delayed reward as an example while allowing the illustrated stepwise feedback.',
 'P0817-Q04':'Test the source’s agent/environment interaction definition against the explicitly supplied simulator that responds to actions; distinguish the physical-world parenthetical from a necessary condition.'}
for short,method in methods.items():q(short)['conflictResolution']['method']=method
cite('P0807-Q04',807,'statement','Printed slide 9: left-hand Overfitting Causes line including too many training iterations.','conflict')
cite('P0817-Q02',817,'statement','Printed slide 19: Core Elements, Action(a) definition as a set of possible moves.','conflict')
cite('P0817-Q03',817,'statement','Printed slide 19: learning-with-a-critic bullet, rewards or penalties only after a sequence of actions.','conflict')
cite('P0817-Q03',818,'figure','Printed slide 20: reinforcement-learning loop arrows,2 Takes ACTION →3 Environment gives REWARD →4 Robot updates its Brain → repeat.','premise','Reinforcement Learning Loop:1 Robot observes STATE;2 Takes ACTION;3 Environment gives REWARD;4 Robot updates its Brain; Loop repeats!')
cite('P0817-Q04',817,'statement','Printed slide 19: Environment definition with parenthetical physical world, alongside trial-and-error agent/environment interaction.','conflict')
# Only the14 flagged objects can differ. The58 accepted objects are byte-equivalent at object level.
for prev in accepted:assert prev==qm[prev['id']] and qhash(prev)==qhash(qm[prev['id']])
for prev in old['questions']:assert qm[prev['id']]['correctOptionIds']==prev['correctOptionIds']
assert b['sourceIssues']==old['sourceIssues'] and fhash('audits/source-disputes-W06-L27.json')==sourcehash
checks=[]
def ck(name,ok,detail):
 assert ok,name;checks.append(dict(name=name,passed=True,detail=detail,independent=False))
ck('All58 accepted whole objects preserved',len(accepted)==58,'Exact object and correctness-hash comparisons passed.')
ck('All72 existing answer sets preserved',all(qm[p['id']]['correctOptionIds']==p['correctOptionIds'] for p in old['questions']),'No key change was needed.')
ck('Seven source annotations unchanged',sourcehash=='5ce58c0a78bffd3b1df52d6b12acaa2bb47614f9825279970e45b2b62d51c9e1','Exact file SHA and batch-sourceIssues equality passed.')
# An information-collision example tests why greater capacity cannot resolve missing inputs.
import sympy as s
a=s.symbols('a',real=True);mse=(a*a+(a-2)**2)/2
ck('Missing-feature collision has positive irreducible fitted error',s.diff(mse,a)==2*a-2 and mse.subs(a,1)==1,'Two records share observed x but have targets0 and2; every deterministic predictor gives one a. Best mean squared error is1 at a=1.')
ck('Relevant missing feature resolves this illustrative collision',all(2*z==y for z,y in [(0,0),(1,2)]),'Measuring z permits y=2z in this example; this is an illustration, not a guarantee of perfect performance for arbitrary data.')
ck('Torque distractor arithmetic retained',5*F(98,10)==49 and F(1,2)*F(98,10)==F(49,10) and F(98,10)==F(98,10),'Correct49;0.5 kg error4.9; omitted factor5 gives9.8; half-arm24.5.')
ck('False generic equation methods removed',all('Derive from cited equations' not in q(x)['conflictResolution']['method'] for x in methods),'Five source-specific reasoning methods replace the inaccurate generic template.')
ck('Every revised object is v3 draft',all(qm[i]['version']==3 and qm[i]['status']=='draft' and not qm[i]['reviewIds'] for i in flags),'Independent re-review is required.')
# Pre-dispatch prose cleanup; sourceIssue records and accepted objects stay untouched.
def clean_prose(text):
 for old,new in [('target49.0','target 49.0'),('Predicts31.04','Predicts 31.04'),('for3.5','for 3.5'),('and0.8','and 0.8'),('a3.5','a 3.5'),('at0.8','at 0.8'),('Predicts:31.04','Predicts: 31.04'),('into3','into 3'),('Zone0','Zone 0'),('Zone1','Zone 1'),('Zone2','Zone 2'),('page813','page 813'),('page815','page 815'),('beyond100%','beyond 100%'),('page817','page 817'),('page818','page 818'),('arrows,2','arrows, 2'),('→3','→ 3'),('→4','→ 4'),('Loop:1','Loop: 1'),(';2','; 2'),(';3','; 3'),(';4','; 4')]:text=text.replace(old,new)
 return text
for qid in flags:
 item=qm[qid]
 for ci in item['citations']:
  ci['locator']=clean_prose(ci['locator'])
  # Only new prose transcriptions, never original full extracted source blocks.
  if '\n' not in ci['evidenceText']:ci['evidenceText']=clean_prose(ci['evidenceText'])
 if 'conflictResolution' in item:item['conflictResolution']['method']=clean_prose(item['conflictResolution']['method'])
b['authorChecks']=old['authorChecks']+checks
b['coverageNote']='All23 actual pages remain inspected. Version3 revises only14 remaining flagged objects, preserving58 accepted whole objects/hashes, all72 keys and all seven source annotations. Both bounded gaps remain closed by accepted unchanged objects. No self-approval.'
write(f'data/question-batches/{B}.json',b)
changed=[qm[qid] for qid in flags]
blind=[{**{k:x[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions')},'citations':[{k:v for k,v in c.items() if k!='evidenceText'} for c in x['citations']]} for x in changed]
write(f'audits/blind-{B}-v3.json',blind);packetsha=fhash(f'audits/blind-{B}-v3.json')
write(manifest,dict(batchId=B,blindPacket=f'audits/blind-{B}-v3.json',blindPacketSha256=packetsha,questionSha256={x['id']:qhash(x) for x in changed},preservedAcceptedCount=58,preservedAcceptedHashes={x['id']:qhash(x) for x in accepted},sourceIssuesSha256=sourcehash,revisedCount=14,newQuestionIds=[],independentReviewPending=True))
write(f'audits/{B}-v3-author-repair.json',dict(recordedAt=datetime.now(timezone.utc).isoformat(),authorId=A,independentReview=False,checks=checks,actualPagesRevisited=[803,804,805,807,812,813,815,816,817,818],printedFooters=['5','6 (clipped)','7','9','14','15','17','18','19','20'],acceptedCountPreserved=58,sourceIssuesUnchanged=True))
(R/f'audits/handoffs/{B}-v3.md').write_text(f'# L27 v3 frozen\n\n14 revised drafts;58 accepted whole objects/hashes preserved; total72 questions. No new questions or key changes. Both prior coverage gaps remain closed. Seven source annotations unchanged.\n\nPacket: audits/blind-{B}-v3.json\nSHA:{packetsha}\nManifest:{manifest}\nArchive:{archive}\nScript:scripts/repair_W06_L27_v3.py\nChecks:audits/{B}-v3-author-repair.json\n\nRepairs: missing-input remedy now requires relevant new measurements, not capacity alone; eight evidence kind/role/location fixes; five source-specific conflict methods. Ten source pages revisited. Eight author checks pass, including an exact missing-information collision counterexample. All edits require independent re-review; no self-approval, canonical or Git writes. Do not rerun frozen script.\n')
print('FROZEN14',packetsha)
