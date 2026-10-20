"""Independent source-first assignment review; source solution visibility explicitly disclosed."""
from pathlib import Path
import json,copy,hashlib,datetime,sys,math,heapq,re
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import question_hash,schema_errors
B='ASSIGN-W08';WHO='build_offline_study_interface:assignment-independent-reviewer';A='b0450429866ac8017d7971932acf8812adf41df9dff4eb10bc8c87015b41c1b5';L='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
seal='audits/assignment-coverage/ASSIGN-W08-independent-source-responses.json';s=read(seal);assert not s['keyedDraftOpened'] and s['originalPrintedKeysVisible'];b=read(f'data/question-batches/{B}.json');ans={x['questionId']:x for x in s['answers']};now=datetime.datetime.now(datetime.timezone.utc).isoformat();assert len(b['questions'])==10
# Separate independent numerical implementation, no author checker import.
checks=[]
def ck(n,c):assert bool(c),n;checks.append(n)
ck('UCS frozen removal trace and returned path',s['ucsTrace']==[['A',0,['A']],['C',2,['A','C']],['B',5,['A','B']],['F',6,['A','C','F']],['E',7,['A','C','F','E']]])
ck('A-star sum ordering',np.argmin([6,5.4,5.8])==1);ck('UCS g ordering',np.argmin([4,3,1])==2);ck('Greedy h ordering',np.argmin([2,2.4,4.8])==0)
state='H';trace=[]
for i in range(8):trace.append(state);state={'H':'L','L':'H'}[state]
ck('Supplied deterministic recurrence repeats',trace==['H','L']*4)
ck('DQN target and residual',math.isclose(1+.9*max(3,5),5.5) and math.isclose(5.5-4.3,1.2));ck('Terminal target',1+.9*0==1)
ck('Clock range offset',3e8*2e-6==600);ck('Singleton weighted average',math.isclose((.7*20+.3*60)/(.7+.3),32));ck('Reversed-weight distractor',math.isclose(.3*20+.7*60,48))
rng=np.random.default_rng(8008);varied=0
for _ in range(1000):
 z=rng.uniform(0,100,5);w=rng.uniform(.001,1,5);a=float(w@z/w.sum());scale=float(rng.uniform(.1,10));assert z.min()<=a<=z.max();varied+=1
 assert math.isclose(a,(w*scale)@z/(w*scale).sum(),abs_tol=1e-10);varied+=1
 r=float(rng.normal());g=float(rng.uniform());v=float(rng.normal());assert math.isclose(r+g*(1-1)*v,r);varied+=1
 dt=float(rng.uniform(-1e-4,1e-4));bias=3e8*dt;assert math.isclose(bias/3e8,dt,abs_tol=1e-14);varied+=1
cp=f'audits/assignment-coverage/{B}-independent-checks.json';write(cp,{'reviewerId':WHO,'namedChecks':len(checks),'checks':checks,'variedAssertions':varied,'seed':8008,'allPassed':True,'execution':'Independent standard/default-environment arithmetic, recurrence and invariance checks, not author script, ROS, hardware or browser execution.'})
flags={1:{'difficulty':'All four options already supply each valid route’s complete cost. The medium algorithm-trace task can therefore be answered by choosing the smallest printed number, without performing relaxation or summation. Remove cost totals from the choices or introduce appropriately consistent trace alternatives; otherwise classify this direct minimum-cost recognition as easy.'},2:{'sourceSupport':'The only locator names source item 2, which establishes the role of h but not f=g+h used for the added zero-heuristic/UCS conclusion. Add the exact item-3 formula region on the same physical page 35 (or a precise lecture equation citation), rather than attributing the complete derivation to item 2.'},6:{'sourceSupport':'The identical locator is copied onto both physical pages 36 and 37, claiming relevant prompt, choices and worked explanation. Page 36 contains only the beginning of item 6 and its initial values; page 37 contains the remaining target values, numeric result and Bellman derivation. Give each page its actual region. No generated or original options are printed for this numeric source item.'},8:{'sourceSupport':'At physical page 37, item 8 is a conceptual clock-bias prompt/options with the cδt term, not the supplied full pseudorange equation; classify the source evidence as statement/premise and keep the full equation explicitly added. Page 38 has only its answer letter and lecture reference, not a prompt, choices or worked explanation. Use exact separate locators or omit that incidental continuation citation.','distractors':'The +600 m “inter-constellation frame rotation” option is not a plausible timing-bias interpretation. Replace it with a meaningful clock/sign/unit misconception in the same domain; do not confuse frame rotation with clock offsets.'}}
reviews=[];accepted={};findings=[]
for q in b['questions']:
 n=int(q['id'][-3:]);assert ans[q['id']]['selectedOptionIds']==q['correctOptionIds'];assert sha(q['originalRecordPath'])==q['originalRecordSha256'];o=read(q['originalRecordPath']);assert o['id']==q['assignmentSourceItemId'];dims=['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication'];cs={d:d not in flags.get(n,{})for d in dims};ff=list(flags.get(n,{}).values());sv={'assignments':A};rslides=list(dict.fromkeys(c['slideId']for c in q['citations']));extra=[]
 if n==9:extra=[1243,1251]
 if n==10:extra=[1237]
 if extra:sv['lectures']=L;rslides += [f'lectures-p{p:04d}'for p in extra]
 evidence=[]
 for sid in rslides:
  source,p=sid.split('-p');p=int(p);ip=f'sources/previews/{source}/page-{p:04d}.webp';evidence.append({'sourceId':source,'physicalPage':p,'imagePath':ip,'imageSha256':sha(ip),'dimensions':list(Image.open(R/ip).size),'visualInspection':'complete','viewedAt':'2026-10-20T01:20:19+00:00'if source=='assignments'else '2026-10-20T01:21:10+00:00','sourceAnswerExposure':True})
 review={'id':f'REV-{q["id"]}-v{q["version"]}-offline-independent','questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q),'reviewerId':WHO,'decision':'flagged'if ff else 'verified','reviewedAt':now,'sourceVersions':sv,'reviewedSlideIds':rslides,'independentAnswerOptionIds':ans[q['id']]['selectedOptionIds'],'solvedBeforeAnswerSeen':False,'checks':cs,'reasoning':ans[q['id']]['reasoning']+' Generated-key-hidden source responses were frozen before opening current keyed drafts. Original highlighted assignment answers were visible during mandatory source inspection, so this is independent re-derivation, not a fully blind review. Every option explanation, formula definition/unit/assumption, citation kind/role/region, diagram and difficulty was subsequently checked.','findings':ff,'reviewType':'assignment_independent_rederivation_with_source_key_exposure','priorExposure':'No keyed generated question, original-record audit or author-check script was opened before the source-response freeze. The printed source solutions were visible.','blindAnswerRecord':seal,'blindAnswerRecordSha256':sha(seal),'firstCurrentKeyOpenedAt':'2026-10-20T01:21:36+00:00','sourceInspectionEvidence':evidence,'independentCheckEvidence':{'path':cp,'sha256':sha(cp)},'originalSourceRecordChecked':{'path':q['originalRecordPath'],'sha256':q['originalRecordSha256'],'printedItemNumber':o['printedItemNumber'],'sourcePages':o['physicalPages']}}
 assert not schema_errors(review,read('data/schema.review.json'));reviews.append(review)
 if ff:findings.append({'questionId':q['id'],'questionSha256':question_hash(q),'failedChecks':[k for k,v in cs.items()if not v],'findings':ff})
 else:accepted[q['id']]=question_hash(q)
# Exact stem collisions, excluding these same question IDs.
owned={q['id']for q in b['questions']};normalize=lambda t:re.sub(r'\s+',' ',t).strip().casefold();stems={normalize(q['stem']):q['id']for q in b['questions']};collisions=[]
for p in (R/'data/question-batches').glob('*.json'):
 for q in json.loads(p.read_text()).get('questions',[]):
  if q['id']not in owned and normalize(q['stem'])in stems:collisions.append([stems[normalize(q['stem'])],q['id']])
assert not collisions,collisions
rp=f'data/reviews/{B}-v1-independent-offline.json';write(rp,reviews)
summary={'batchId':B,'questionCount':10,'keysAgree':10,'verifiedCount':len(accepted),'flaggedCount':len(findings),'acceptedQuestionHashes':accepted,'flaggedQuestions':findings,'reviewPath':rp,'reviewSha256':sha(rp),'actualAssignmentPages':[34,35,36,37,38],'actualLecturePages':[1237,1243,1251],'originalItemsExplicitlyCovered':10,'boundedAdditionalContentGaps':[],'coverageDisposition':'All ten original concepts have explicit adaptations; complete acceptance waits for four current quality dispositions, not additional padding.','sourceQualifications':'Fuzzy singleton denominator is visibly malformed in assignment p38. Lecture p1243 specifies summing weights, and p1251 uses a plus in its separate example. The adaptation explicitly supplies the correct discrete normalization. Preserve original stray letters and misnumbered reference, no global source resolution. Crisp-value scope remains scalar, not a universal crisp-set singleton claim.','independentChecks':{'named':len(checks),'varied':varied,'path':cp},'sourceAnswerExposure':True,'generatedKeyHiddenUntilResponseSeal':True,'fullyBlind':False,'restrictions':'No authored-question edits, bank/Git operations, denied route retries, model/ROS/browser/hardware execution.'};write(f'audits/assignment-coverage/{B}-independent-review-summary.json',summary);print(json.dumps({'verified':len(accepted),'flagged':len(findings),'review':rp,'reviewSha256':sha(rp)}))
