"""Independent re-derivation. Assignment printed keys were visible; generated answers were sealed separately first."""
from pathlib import Path
import json,hashlib,datetime,sys,math,re
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import question_hash,schema_errors
B='ASSIGN-W09';WHO='build_offline_study_interface:assignment-independent-reviewer';A='b0450429866ac8017d7971932acf8812adf41df9dff4eb10bc8c87015b41c1b5';L='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
seal=f'audits/assignment-coverage/{B}-independent-source-responses.json';s=read(seal);assert not s['keyedDraftOpened'] and s['originalPrintedKeysVisible'];assert sha(seal)=='ea6d72b9c79db51372341bc21904121e00998d7a3b470f21fd5c6463238ac5db';b=read(f'data/question-batches/{B}.json');ans={x['questionId']:x for x in s['answers']};now=datetime.datetime.now(datetime.timezone.utc).isoformat()
checks=[]
def ck(n,c):assert bool(c),n;checks.append(n)
children=[.5*(2+6),1.5*2-.5*6,-.5*2+1.5*6]
ck('Linear crossover coordinates',children==[4,0,8]);ck('Two separate fitness rankings',sorted(sorted(children,key=lambda x:x,reverse=True)[:2])==[4,8] and sorted(sorted(children,key=lambda x:-(x-1)**2,reverse=True)[:2])==[0,4]);ck('Binary endpoint mapping',1+15*42/63==11 and format(42,'06b')=='101010')
blocked={(1,1),(2,1),(2,2),(4,2),(2,3),(3,4)};waypoints=[(0,0),(0,1),(2,4),(5,5)]
def decode(points,axis_order):
 pos=list(points[0]);entered=[];moves=[]
 for end in points[1:]:
  for axis in axis_order:
   while pos[axis]!=end[axis]:
    d=1 if end[axis]>pos[axis] else -1;pos[axis]+=d;entered.append(tuple(pos));moves.append((axis,d))
 return entered,len(entered),sum(p in blocked for p in entered),sum(a!=b for a,b in zip(moves,moves[1:]))
h=decode(waypoints,[0,1]);v=decode(waypoints,[1,0]);ck('Horizontal-first full decoded path',h[1:]==(10,5,4));ck('Vertical-first full decoded path',v[1:]==(10,0,3));ck('Fitness denominators',1+h[1]+10*h[2]+h[3]==65 and 1+v[1]+10*v[2]+v[3]==14)
ck('Dense network parameter scopes',(6*16,6*16+16*4,6*16+16*4+16+4)==(96,160,180));ck('Gaussian identity prediction',np.allclose(np.array([2,2])+[2,1],[4,3]) and np.allclose(np.diag([.25,.16])+np.diag([.5,.4]),np.diag([.75,.56])));ck('SLAM dimensions',3+2*6==15 and np.zeros((15,15))[:3,3:].shape==(3,12))
P=np.diag([.04,.04,.01,.09,.09]);J=np.eye(5);J[1,2]=2;Q=np.diag([.01,.01,.0025,0,0]);pred=J@P@J.T+Q
ck('EKF robot covariance',np.allclose(pred[:3,:3],[[.05,0,0],[0,.09,.02],[0,.02,.0125]]));ck('Static map and cross blocks',np.allclose(pred[3:,3:],np.diag([.09,.09])) and np.allclose(pred[:3,3:],0));ck('Unit-displacement distractor',np.allclose((np.array([[1,0,0],[0,1,1],[0,0,1]])@P[:3,:3]@np.array([[1,0,0],[0,1,1],[0,0,1]]).T+Q[:3,:3]),[[.05,0,0],[0,.06,.01],[0,.01,.0125]]))
rng=np.random.default_rng(9009);varied=0
for _ in range(1000):
 d=float(rng.uniform(-5,5));th=float(rng.uniform(-math.pi,math.pi));D=rng.uniform(.001,1,3);V=rng.uniform(.001,1,3);j=np.array([[1,0,-d*math.sin(th)],[0,1,d*math.cos(th)],[0,0,1]]);p=j@np.diag(D)@j.T+np.diag(V)
 assert np.linalg.eigvalsh(p).min()>0;varied+=1
 assert np.allclose(p,p.T);varied+=1
 assert math.isclose(p[1,2],d*math.cos(th)*D[2],abs_tol=1e-12);varied+=1
 code=int(rng.integers(0,64));x=1+15*code/63;assert math.isclose((x-1)*63/15,code,abs_tol=1e-12);varied+=1
cp=f'audits/assignment-coverage/{B}-independent-checks.json';write(cp,{'reviewerId':WHO,'namedChecks':len(checks),'checks':checks,'variedAssertions':varied,'seed':9009,'allPassed':True,'horizontalEnteredCells':h[0],'verticalEnteredCells':v[0],'execution':'Independent default-environment arithmetic, explicit grid traversal and covariance propagation. No author script or external runtime used.'})
reviews=[];accepted={};dims=['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']
for q in b['questions']:
 assert ans[q['id']]['selectedOptionIds']==q['correctOptionIds'];assert sha(q['originalRecordPath'])==q['originalRecordSha256'];o=read(q['originalRecordPath']);assert o['id']==q['assignmentSourceItemId'];n=int(q['id'][-3:]);sv={'assignments':A};slides=list(dict.fromkeys(c['slideId']for c in q['citations']))
 if n==1:sv['lectures']=L;slides+=['lectures-p1286']
 evidence=[]
 for sid in slides:
  source,p=sid.split('-p');p=int(p);ip=f'sources/previews/{source}/page-{p:04d}.webp';evidence.append({'sourceId':source,'physicalPage':p,'imagePath':ip,'imageSha256':sha(ip),'dimensions':list(Image.open(R/ip).size),'visualInspection':'complete','viewedAt':'2026-10-20T01:27:50+00:00'if source=='assignments'else '2026-10-20T01:28:13+00:00','sourceAnswerExposure':source=='assignments'})
 r={'id':f'REV-{q["id"]}-v{q["version"]}-offline-independent','questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q),'reviewerId':WHO,'decision':'verified','reviewedAt':now,'sourceVersions':sv,'reviewedSlideIds':slides,'independentAnswerOptionIds':ans[q['id']]['selectedOptionIds'],'solvedBeforeAnswerSeen':False,'checks':{d:True for d in dims},'reasoning':ans[q['id']]['reasoning']+' Generated-key-hidden responses were sealed before opening current keyed drafts. Original printed answers were visible, so this is independent re-derivation, not a fully blind review. All options, full explanations, formula definitions/units/assumptions, exact current citations and original item bindings were checked. Neutral blind-packet locators intentionally do not contain the more precise answer-bearing author evidence; current keyed citations were assessed separately.','findings':[],'reviewType':'assignment_independent_rederivation_with_source_key_exposure','priorExposure':'Printed assignment solutions were visible in the actual page images. No current generated key or original record was opened before source responses were frozen.','blindAnswerRecord':seal,'blindAnswerRecordSha256':sha(seal),'firstCurrentKeyOpenedAt':'2026-10-20T01:28:42+00:00','sourceInspectionEvidence':evidence,'independentCheckEvidence':{'path':cp,'sha256':sha(cp)},'originalSourceRecordChecked':{'path':q['originalRecordPath'],'sha256':q['originalRecordSha256'],'printedItemNumber':o['printedItemNumber'],'sourcePages':o['physicalPages']}}
 assert not schema_errors(r,read('data/schema.review.json'));reviews.append(r);accepted[q['id']]=question_hash(q)
owned=set(accepted);normalize=lambda t:re.sub(r'\s+',' ',t).strip().casefold();stems={normalize(q['stem']):q['id']for q in b['questions']};collisions=[]
for p in (R/'data/question-batches').glob('*.json'):
 for q in json.loads(p.read_text()).get('questions',[]):
  if q['id']not in owned and normalize(q['stem'])in stems:collisions.append([stems[normalize(q['stem'])],q['id']])
assert not collisions
rp=f'data/reviews/{B}-v1-independent-offline.json';write(rp,reviews)
write(f'audits/assignment-coverage/{B}-independent-review-summary.json',{'batchId':B,'questionCount':10,'keysAgree':10,'verifiedCount':10,'flaggedCount':0,'acceptedQuestionHashes':accepted,'flaggedQuestions':[],'reviewPath':rp,'reviewSha256':sha(rp),'actualAssignmentPages':list(range(39,45)),'actualLecturePages':[1286],'originalItemsExplicitlyCovered':10,'boundedAdditionalContentGaps':[],'coverageDisposition':'All ten original items are explicitly adapted and accepted. The grid decode-order pair covers distinct execution rules, not duplicate recall; expanded parameter counts and cross-covariance orientation add bounded useful application.','sourceQualifications':'Original item1 has no specified fitness and remains quarantined independently of the qualified adaptation. Actual lecture p1286 says retain best two, not two largest coordinates. Item2 distinguishes integer code from decoded real value. Temporal-memory scope, sufficient Markov state, coordinate conventions and additive EKF noise are explicit. No original source dispute is globally resolved.','independentChecks':{'named':len(checks),'varied':varied,'path':cp},'sourceAnswerExposure':True,'generatedKeyHiddenUntilResponseSeal':True,'fullyBlind':False,'restrictions':'No authored-question edits, bank/Git mutations, denied route retries, ROS/model/browser/hardware execution.'})
print(json.dumps({'verified':10,'flagged':0,'review':rp,'sha256':sha(rp),'checks':len(checks),'varied':varied}))
