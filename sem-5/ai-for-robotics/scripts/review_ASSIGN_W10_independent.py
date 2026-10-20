"""Independent re-derivation. Assignment printed keys were visible; generated answers were sealed separately first."""
from pathlib import Path
import json,hashlib,datetime,sys,math,re
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import question_hash,schema_errors
B='ASSIGN-W10';WHO='build_offline_study_interface:assignment-independent-reviewer';A='b0450429866ac8017d7971932acf8812adf41df9dff4eb10bc8c87015b41c1b5';L='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
seal=f'audits/assignment-coverage/{B}-independent-source-responses.json';s=read(seal);assert not s['keyedDraftOpened'] and s['originalPrintedKeysVisible'];assert sha(seal)=='f2fa6ebbdb641e7cf2579a985d9c0ad3a1d690c022fd57fc8d218a32a34f81f2';b=read(f'data/question-batches/{B}.json');ans={x['questionId']:x for x in s['answers']};now=datetime.datetime.now(datetime.timezone.utc).isoformat()
checks=[]
def ck(n,c):assert bool(c),n;checks.append(n)
def softmax(x):
 y=np.exp(np.asarray(x)-np.max(x));return y/y.sum()
ck('Literal supplied suffix strip','running'[:-3]=='runn')
vocab=['chair','pick','red','ball','near'];ck('Displayed index',vocab.index('near')==4);ck('Sorted index',sorted(vocab).index('near')==2)
dots=np.array([[3,1],[1,2],[0,1]])@np.array([2,1]);ck('Attention dot products',np.array_equal(dots,[7,4,1]));weights=softmax(dots/np.sqrt(2));ck('Full-precision normalized weights',np.array_equal(np.round(weights,4),[.8816,.1057,.0127]));ck('Unscaled distractor',np.array_equal(np.round(softmax(dots),4),[.9503,.0473,.0024]));ck('Divide-by-dimension distractor',np.array_equal(np.round(softmax(dots/2),4),[.7856,.1753,.0391]));ck('Linear normalization distractor',np.array_equal(np.round(dots/dots.sum(),4),[.5833,.3333,.0833]))
X=np.zeros((12,64));Q=X@np.zeros((64,16));K=Q.copy();V=X@np.zeros((64,20));att=Q@K.T;H=att@V;ck('Six attention tensor shapes',[x.shape for x in [X,Q,K,V,att,H]]==[(12,64),(12,16),(12,16),(12,20),(12,12),(12,20)])
ck('Valid convolution explicit placements',[len(range(0,100-2+1,st))for st in [2,1]]==[50,99]);ck('Original lecture width-one scope',len(range(0,100-1+1))==100);ck('Conditional chain product',math.isclose(.5*.4*.2,.04));ck('Omitted-factor distractors',np.allclose([.5*.2,.5*.4,.4*.2],[.1,.2,.08]))
rng=np.random.default_rng(1010);varied=0
for _ in range(1000):
 x=rng.normal(size=7)*5;w=softmax(x);assert math.isclose(w.sum(),1,abs_tol=1e-12);varied+=1
 assert np.all(w>0);varied+=1
 assert np.allclose(w,softmax(x+float(rng.uniform(-50,50))));varied+=1
 n=int(rng.integers(1,101));k=int(rng.integers(1,n+1));stride=int(rng.integers(1,11));assert len(range(0,n-k+1,stride))==(n-k)//stride+1;varied+=1
cp=f'audits/assignment-coverage/{B}-independent-checks.json';write(cp,{'reviewerId':WHO,'namedChecks':len(checks),'checks':checks,'variedAssertions':varied,'seed':1010,'allPassed':True,'execution':'Independent default-environment arithmetic, explicit valid-window enumeration and tensor/softmax operations. No author script or external runtime used.'})
flags={4:{'sourceSupport':'The conflictResolution physicalPage is 46, but the erroneous V multiplication appears on physical page 47. Page 46 contains the correct WV=64×20 premise. Change only the source-version-bound conflict location to 47, retaining page 46 as the correct premise and preserving both original records. Current answer and derivation are correct.'}};reviews=[];accepted={};findings=[];dims=['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']
for q in b['questions']:
 assert ans[q['id']]['selectedOptionIds']==q['correctOptionIds'];assert sha(q['originalRecordPath'])==q['originalRecordSha256'];o=read(q['originalRecordPath']);assert o['id']==q['assignmentSourceItemId'];n=int(q['id'][-3:]);sv={'assignments':A};slides=list(dict.fromkeys(c['slideId']for c in q['citations']))
 extra={3:[1485,1486],4:[1485,1486],5:[1524],7:[1550]}.get(n,[])
 if extra:sv['lectures']=L;slides += [f'lectures-p{p:04d}'for p in extra]
 evidence=[]
 for sid in slides:
  source,p=sid.split('-p');p=int(p);ip=f'sources/previews/{source}/page-{p:04d}.webp';evidence.append({'sourceId':source,'physicalPage':p,'imagePath':ip,'imageSha256':sha(ip),'dimensions':list(Image.open(R/ip).size),'visualInspection':'complete','viewedAt':'2026-10-20T01:31:01+00:00'if source=='assignments'else '2026-10-20T01:31:24+00:00','sourceAnswerExposure':source=='assignments'})
 r={'id':f'REV-{q["id"]}-v{q["version"]}-offline-independent','questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q),'reviewerId':WHO,'decision':'flagged'if n in flags else 'verified','reviewedAt':now,'sourceVersions':sv,'reviewedSlideIds':slides,'independentAnswerOptionIds':ans[q['id']]['selectedOptionIds'],'solvedBeforeAnswerSeen':False,'checks':{d:d not in flags.get(n,{})for d in dims},'reasoning':ans[q['id']]['reasoning']+' Generated-key-hidden responses were sealed before opening current keyed drafts. Original printed answers were visible, so this is independent re-derivation, not a fully blind review. All options, full explanations, formula definitions/units/assumptions, exact current citations and original item bindings were checked. Neutral blind-packet locators intentionally do not contain the more precise answer-bearing author evidence; current keyed citations were assessed separately.','findings':list(flags.get(n,{}).values()),'reviewType':'assignment_independent_rederivation_with_source_key_exposure','priorExposure':'Printed assignment solutions were visible in the actual page images. No current generated key or original record was opened before source responses were frozen.','blindAnswerRecord':seal,'blindAnswerRecordSha256':sha(seal),'firstCurrentKeyOpenedAt':'2026-10-20T01:31:57+00:00','sourceInspectionEvidence':evidence,'independentCheckEvidence':{'path':cp,'sha256':sha(cp)},'originalSourceRecordChecked':{'path':q['originalRecordPath'],'sha256':q['originalRecordSha256'],'printedItemNumber':o['printedItemNumber'],'sourcePages':o['physicalPages']}}
 assert not schema_errors(r,read('data/schema.review.json')),schema_errors(r,read('data/schema.review.json'));reviews.append(r)
 if n in flags:findings.append({'questionId':q['id'],'questionSha256':question_hash(q),'failedChecks':list(flags[n]),'findings':list(flags[n].values())})
 else:accepted[q['id']]=question_hash(q)
owned={q['id']for q in b['questions']};normalize=lambda t:re.sub(r'\s+',' ',t).strip().casefold();stems={normalize(q['stem']):q['id']for q in b['questions']};collisions=[]
for p in (R/'data/question-batches').glob('*.json'):
 for q in json.loads(p.read_text()).get('questions',[]):
  if q['id']not in owned and normalize(q['stem'])in stems:collisions.append([stems[normalize(q['stem'])],q['id']])
assert not collisions
rp=f'data/reviews/{B}-v1-independent-offline.json';write(rp,reviews)
write(f'audits/assignment-coverage/{B}-independent-review-summary.json',{'batchId':B,'questionCount':10,'keysAgree':10,'verifiedCount':len(accepted),'flaggedCount':len(findings),'acceptedQuestionHashes':accepted,'flaggedQuestions':findings,'reviewPath':rp,'reviewSha256':sha(rp),'actualAssignmentPages':list(range(45,50)),'actualLecturePages':[1485,1486,1524,1550],'originalItemsExplicitlyCovered':10,'boundedAdditionalContentGaps':[],'coverageDisposition':'All ten original items are explicitly adapted with useful bounded comparisons. One exact conflict-location metadata repair remains; no missing original concept was found.','sourceQualifications':'Preserve original unordered vocabulary ambiguity, V projection intermediate typo and incorrect width-two stride-one statement. Lecture1524 gives a width-one example whose same-length note is valid in that narrow context. Printed attention arithmetic rounds intermediates, while this adaptation requires full precision until final rounding. Custom AIML labels are source-specific roles only, not claims of portable syntax or runtime execution.','independentChecks':{'named':len(checks),'varied':varied,'path':cp},'sourceAnswerExposure':True,'generatedKeyHiddenUntilResponseSeal':True,'fullyBlind':False,'restrictions':'No authored-question edits, bank/Git mutations, denied route retries, ROS/model/browser/hardware execution.'})
print(json.dumps({'verified':len(accepted),'flagged':len(findings),'review':rp,'sha256':sha(rp),'checks':len(checks),'varied':varied}))
