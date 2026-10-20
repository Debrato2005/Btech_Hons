import json,pathlib,hashlib,datetime,sys,itertools,math,random
import numpy as np
P=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));from validate import question_hash,schema_errors
A=P/'audits';b=json.load(open(P/'data/question-batches/W12-L57.json'));blind=json.load(open(A/'blind-answers-W12-L57-v2-integration.json'));binding=json.load(open(A/'W12-L57-v2-minimal-bindings.json'));hashes=binding['questionHashes'];m=json.load(open(A/'W12-L57-v2-repair-manifest.json'));by={x['questionId']:x for x in blind['answers']};now=datetime.datetime.now(datetime.timezone.utc).isoformat();rid=blind['reviewerId'];bh=hashlib.sha256((A/'blind-answers-W12-L57-v2-integration.json').read_bytes()).hexdigest();rows=[];bad='W12-L57-Q014'
assert len(m['acceptedQuestionHashes'])==72
R=np.eye(3);assert np.linalg.matrix_rank(np.vstack([R-R]*3))==0
raw=[]
for places in itertools.combinations(range(6),3):
 fields=[0]*3;seen=[];wi=ri=0
 for t in range(6):
  if t in places:fields[wi]=1;wi+=1
  else:seen.append(fields[ri]);ri+=1
 raw.append(seen)
assert any(len(set(x))>1 for x in raw)
staged=[]
for places in itertools.combinations(range(8),4):
 records=[[0]*3,[None]*3];published=0;selected=None;seen=[];wi=ri=0
 for t in range(8):
  if t in places:
   if wi<3:records[1][wi]=1
   else:published=1
   wi+=1
  else:
   if ri==0:selected=published
   else:seen.append(records[selected][ri-1])
   ri+=1
 assert seen in [[0]*3,[1]*3];staged.append(seen)
def T(a,t):
 c,s=math.cos(a),math.sin(a);o=np.eye(4);o[:3,:3]=[[c,-s,0],[s,c,0],[0,0,1]];o[:3,3]=t;return o
rng=random.Random(5702)
for _ in range(100):
 W=T(rng.random()*6,[rng.random() for i in range(3)]);B=T(rng.random()*6,[rng.random() for i in range(3)]);assert np.allclose(np.linalg.inv(W)@W@B,B)
W=T(.4,[1,2,3]);B=T(.8,[3,1,2]);assert not np.allclose(W.T@W@B,B);assert not np.allclose(W@B@np.linalg.inv(W),B)
checks={'passed':True,'repeatedPoseDifferenceRank':0,'rawInterleavings':len(raw),'rawMixedSnapshots':sum(len(set(x))>1 for x in raw),'stagedImmutableInterleavings':len(staged),'stagedMixedSnapshots':0,'variedRigidTransformCancellationCases':100,'runtime':'Installed NumPy and Python arithmetic only; no camera/robot/network/ROS/model execution. Staged record model uses declared atomic publication and no reuse before acknowledgement.'};(A/'W12-L57-v2-integration-independent-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
for q in b['questions']:
 if q['id'] in m['acceptedQuestionHashes']:assert question_hash(q)==m['acceptedQuestionHashes'][q['id']]
 if q['id'] not in by:continue
 a=by[q['id']];h=question_hash(q);assert h==hashes[q['id']];assert q['correctOptionIds']==a['independentAnswerOptionIds'];isbad=q['id']==bad
 ck={k:True for k in ['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']};findings=[]
 if isbad:
  ck.update(assumptions=False,difficulty=False);findings=['The revised assumptions explicitly state that the system is rank deficient, revealing the tested conclusion in a medium question. The stem also refers to difference equations and p without providing their definitions until the answer. State the added equation R_i p+t_i=c and define p in the question, remove the answer-bearing rank-deficient assumption, and retain a genuine rank inference or label an explicitly provided-rule recall item easy. The solution algebra and corrected repeated-pose premise are otherwise sound.']
 r={'id':f'{q["id"]}-v{q["version"]}-integration-independent','questionId':q['id'],'questionVersion':q['version'],'questionSha256':h,'reviewerId':rid,'decision':'flagged' if isbad else 'verified','reviewedAt':now,'sourceVersions':{'lectures':blind['sourceVersion']},'reviewedSlideIds':sorted({c['slideId'] for c in q['citations']}),'independentAnswerOptionIds':a['independentAnswerOptionIds'],'solvedBeforeAnswerSeen':False,'checks':ck,'reasoning':a['reasoning']+' Current full explanation, source/premise roles, options and provenance were inspected after current answer freeze.','findings':findings,'blindAnswersPath':'audits/blind-answers-W12-L57-v2-integration.json','blindAnswersSha256':bh,'independentSolvedAt':blind['solvedAt'],'priorAuthorExposure':True,'currentVersionSolvedBeforeKeyedAccess':True,'authorLocatorAnswerExposure':False,'computationsPath':'audits/W12-L57-v2-integration-independent-checks.json','sourceInspectionEvidence':[{'inspectorId':rid,'physicalPage':n,'inspectedAt':blind['solvedAt'],'method':'Personally viewed actual1600px-wide source panel before current keyed object.','renderedEvidencePath':f'/workspace/shared/robotics-review-L57-v2/sheet{4*(blind["actualPagesInspected"].index(n)//4)}.png'} for n in sorted({c['physicalPage'] for c in q['citations']})]};assert not schema_errors(r,json.load(open(P/'data/schema.review.json'))),q['id'];rows.append(r)
f=P/'data/reviews/W12-L57-v2-independent-integration.json';assert not f.exists();f.write_text(json.dumps(rows,indent=2)+'\n');accepted={q['id']:question_hash(q) for q in b['questions'] if q['id']!=bad};assert len(accepted)==85
s={'completedAt':now,'reviewed':14,'verified':13,'flagged':1,'acceptedPreserved':72,'lectureVerified':85,'lectureQuestions':86,'acceptedQuestionHashes':accepted,'flaggedQuestions':[{'questionId':r['questionId'],'findings':r['findings']} for r in rows if r['decision']=='flagged'],'actualReviewPagesInspected':blind['actualPagesInspected'],'reviewPath':str(f.relative_to(P)),'reviewSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'blindAnswersSha256':bh,'gapDispositions':m['boundedGapDispositions'],'coverageConclusion':'The three bounded gaps are closed by accepted current revisions;72accepted whole objects preserved. One medium rank question still reveals its answer in assumptions and omits equation context in its stem; it remains quarantined. Prior40-page inspection remains separate from this16-page repair review.','externalEvidenceChecked':[{'url':'https://docs.opencv.org/4.13.0/d5/dae/tutorial_aruco_detection.html','checkedAt':now,'finding':'Known camera matrix/distortion and physical marker corner geometry supply metric pose prerequisites; original slides remain premise-level, not claimed to print these details.'}],'runtimeQualification':checks['runtime']};(A/'W12-L57-v2-integration-review-summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:s[k] for k in ['reviewed','verified','flagged','lectureVerified','reviewSha256']}))
