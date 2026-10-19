#!/usr/bin/env python3
"""Repair only independently flagged L08 objects; preserve all accepted hashes.

This authoring repair does not approve its own revisions or change source files.
"""
import copy,datetime,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash
load=lambda p:json.loads((ROOT/p).read_text())
dump=lambda p,v:(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
path=ROOT/'data/question-batches/W02-L08.json';raw=path.read_bytes();batch=json.loads(raw);reviews=load('data/reviews/W02-L08-v1-independent.json');review={r['questionId']:r for r in reviews};assert len(review)==110
for q in batch['questions']:assert question_hash(q)==review[q['id']]['questionSha256'],f'Current content changed: {q["id"]}'
original=copy.deepcopy(batch);qs={q['id']:q for q in batch['questions']}
def qid(short):p,n=short.split('-');return f'W02-L08-P{int(p):04d}-Q{int(n):02d}'
def question(short):return qs[qid(short)]
def set_options(short,texts,explanations):
 q=question(short);assert len(texts)==len(explanations)==4
 for o in q['options']:o['text']=texts[int(o['id'][1:])-1]
 q['solution']['optionExplanations']={f'o{i+1}':e for i,e in enumerate(explanations)}
 q['solution']['misconceptions']=explanations[1:]
set_options('272-1',[
 'Convert to wrist pose relative to the base, then solve for joint variables',
 'Convert to tool pose relative to the base, then use that pose unchanged as the wrist target',
 'Convert to wrist pose relative to the station, then use it unchanged as a wrist-relative-to-base target',
 'Invert the desired tool-to-station pose matrix to obtain joint variables directly, without using the link model'
],[
 'Correct. The introduction first obtains the wrist pose in the base frame and then uses manipulator inverse kinematics to solve the joint variables.',
 'This handles station/base conversion but omits the tool/wrist calibration; the tool and wrist are distinct frames in the figure.',
 'This handles the tool/wrist distinction but omits station/base conversion; the link-model target must use the base frame.',
 'Inverting a rigid pose matrix reverses a coordinate map. It does not invert the nonlinear mapping from joint variables to that pose.'
])
set_options('272-2',[
 'Joint variables that achieve the specified pose',
 'The manipulator link lengths and joint-axis geometry',
 'The end-effector pose produced by a supplied joint configuration',
 'Joint rates corresponding to a supplied end-effector velocity'
],[
 'Correct. The stated inverse position-kinematics problem supplies a desired pose and seeks a compatible joint configuration.',
 'Link lengths and axis geometry specify the kinematic model; estimating them is calibration rather than this desired-pose inverse task.',
 'This is the forward-kinematics output for given joints, reversing the input/output direction in the stem.',
 'This is a velocity-level inverse problem. The stem supplies a pose and asks for a configuration, not a velocity and joint rates.'
])
set_options('275-6',[
 'The additional wrist angle can change orientation without moving the frame-3 origin',
 'The additional wrist angle enlarges the two-link position annulus even without a translational tool offset',
 'Unequal first-two-link lengths keep the dextrous set empty even when the wrist can rotate independently',
 'The additional wrist angle changes the frame-3 origin coordinates but leaves its orientation fixed'
],[
 'Correct. With no translated tool offset, the third angle changes only frame-3 orientation. Thus the 2R orientation restriction does not transfer unchanged.',
 'The frame-3 translation still depends only on L1, L2, θ1 and θ2; changing θ3 does not enlarge the position annulus.',
 'This carries the 2R limitation into a model with an independent orientation variable. The unrestricted wrist can supply the remaining planar orientation at reachable frame-3 positions.',
 'This reverses the roles shown in the transform: θ3 enters the rotation angle sum, not the position column.'
])
set_options('279-1',[
 'Intersecting joint axes and many zero or right-angle link twists',
 'Unequal link lengths and unrestricted non-right-angle link twists',
 'Equal link lengths and mutually skew joint axes',
 'Orthogonal translations of the base and tool frames, regardless of the joint-axis arrangement'
],[
 'Correct. The source highlights intersecting axes and many α_i values of 0° or 90° as helpful analytical structure.',
 'The source does not identify unequal lengths or unrestricted non-right-angle twists as its simplifying features; these do not reproduce the stated axis/twist pattern.',
 'Equal lengths are not the condition listed, and mutually skew axes do not have the cited intersections. This does not assert that the source condition is necessary for every analytical design.',
 'A change in base/tool coordinates is not the intrinsic joint-axis arrangement identified by the source; coordinate translations alone do not establish its stated simplifying condition.'
])
set_options('280-1',[
 'Algebraic: identities and substitution; geometric: spatial relations and the law of cosines; numerical: iteration',
 'Algebraic: spatial triangle construction; geometric: equation substitution; numerical: iteration',
 'Algebraic: iterative numerical updates; geometric: spatial triangle construction; numerical: direct closed-form substitution',
 'Algebraic: identities and substitution; geometric: iterative numerical updates; numerical: spatial triangle construction'
],[
 'Correct. These are the primary roles used in the lecture’s method taxonomy.',
 'This swaps the lecture’s algebraic and geometric descriptions, although geometric reasoning can of course use algebra during a derivation.',
 'This exchanges the iterative numerical method with direct algebraic substitution in the source taxonomy.',
 'This exchanges the geometric spatial construction with numerical iteration in the source taxonomy.'
])
set_options('280-4',[
 'Closed form exploits suitable geometry and can reduce repeated computation; numerical methods are more general but require safeguards',
 'Closed form applies without redesign to arbitrary robot geometry; numerical methods are restricted to intersecting-axis wrists',
 'Closed form and numerical IK differ only in notation and use the same iterative convergence process',
 'A numerical solution can be accepted solely because its joint-update step is small, without checking the remaining pose error'
],[
 'Correct. The lecture links analytical solutions to suitable geometry and contrasts their computational convenience with numerical iteration and singularity handling.',
 'This reverses the stated scope: the summary limits analytical formulas to specific geometries and discusses numerical methods more generally.',
 'A direct closed-form evaluation is not the same process as iterative numerical updates; their computational and convergence considerations differ.',
 'A small update can reflect stagnation or poor conditioning rather than a solved target. The computed configuration still needs a pose-residual and feasibility check.'
])
set_options('281-2',[
 'Joint 4: wrist rotation; joint 5: wrist bend; joint 6: flange rotation',
 'Joint 4: flange rotation; joint 5: wrist rotation; joint 6: wrist bend',
 'Joint 4: wrist bend; joint 5: wrist rotation; joint 6: flange rotation',
 'Joint 4: wrist rotation; joint 5: flange rotation; joint 6: wrist bend'
],[
 'Correct. The actual figure assigns wrist rotation to joint 4, wrist bend to joint 5 and flange rotation to joint 6.',
 'This cycles all three labels away from their printed joint numbers.',
 'This swaps the joint-4 rotation and joint-5 bend labels while retaining the flange label.',
 'This retains the joint-4 label but swaps the joint-5 bend and joint-6 flange labels.'
])
set_options('282-2',[
 'Frame-3 orientation changes, but its origin coordinates do not',
 'Both frame-3 orientation and its origin coordinates change',
 'Frame-3 origin coordinates change, but its orientation does not',
 'Neither frame-3 orientation nor its origin coordinates changes'
],[
 'Correct. θ3 appears in the orientation sum θ1+θ2+θ3 but not in the frame-3 translation column.',
 'This would require a translated tool point affected by wrist rotation. The stated frame-3 model explicitly has no added tool translation.',
 'This reverses the dependencies in the displayed transform: θ3 changes orientation rather than the frame-3 origin.',
 'The absence of θ3 from translation does not make it irrelevant to the transform; it remains in the rotation entries.'
])
set_options('284-2',[
 'Legs k1 and k2; hypotenuse r=√(k1²+k2²); angle γ=atan2(k2,k1)',
 'Legs k1 and k2; hypotenuse r=k1+k2; angle γ=atan2(k2,k1)',
 'Legs k1 and k2; hypotenuse r=√(k1²+k2²); angle γ=atan2(k1,k2)',
 'Legs x and y; hypotenuse √(x²+y²); angle γ=atan2(y,x)'
],[
 'Correct. The little coefficient triangle labels its horizontal and vertical legs k1 and k2, with the stated norm and polar-angle definitions.',
 'The hypotenuse is the Euclidean norm, not the sum of the two perpendicular leg lengths.',
 'This reverses atan2’s vertical/horizontal argument order and therefore does not give the shown coefficient-vector bearing.',
 'This describes the target-position triangle and its bearing β. The displayed little triangle is built from k1 and k2, and its angle is γ rather than β.'
])
set_options('285-6',[
 'Check c2 reachability → enumerate both sine signs and θ2 → compute θ1 separately for each branch → compute θ3 and check pose and constraints',
 'Check c2 reachability → keep only principal arccos(c2) → compute its θ1 → compute θ3 and check pose and constraints',
 'Check c2 reachability → enumerate both sine signs and θ2 → compute one θ1 and reuse it for both branches → compute θ3 and check constraints',
 'Check c2 reachability → enumerate both θ2 branches and their θ1 values → set θ3=φ for both branches → check only the position coordinates'
],[
 'Correct. This respects the dependencies, retains both nondegenerate elbow branches, closes the orientation and checks the complete pose and admissibility.',
 'The principal arccos branch alone omits the opposite sine/elbow branch even though no joint constraint has excluded it.',
 'The shoulder depends on k2=L2 sinθ2. Reversing the elbow sine generally changes the required shoulder, so it must be computed per branch.',
 'The wrist must subtract the shoulder and elbow contributions: θ3=φ−θ1−θ2. Checking only position misses the resulting orientation error.'
])
question('285-6')['solution']['steps']=[
 'Compute c2=(x²+y²−L1²−L2²)/(2L1L2) and reject values outside [−1,1].',
 'For the stated nondegenerate case, take both s2=±√(1−c2²) and compute θ2=atan2(s2,c2).',
 'For each sign, compute θ1=atan2(y,x)−atan2(L2 s2,L1+L2 c2).',
 'Set θ3=φ−θ1−θ2, reconstruct the full forward pose, and apply any stated joint or obstacle constraints.'
]
set_options('290-1',[
 'Desired body motion (v,ω) in; individual wheel rates (ul,ur) out',
 'Desired final world pose (x,y,φ) in; a unique pair of instantaneous wheel rates out, without a motion controller',
 'Individual wheel rates (ul,ur) in; resulting body motion (v,ω) out',
 'Wheel radius and track width in; individual wheel rates out without specifying a desired motion'
],[
 'Correct. The described inverse velocity task finds wheel angular rates for a requested instantaneous body-forward speed and yaw rate.',
 'A final pose alone does not specify an instantaneous velocity command or a unique trajectory. A controller or planner must supply the desired motion first.',
 'This is the forward velocity mapping, reversing the direction of the inverse task.',
 'Geometry determines the coefficients of the mapping, but the desired motion is also needed to determine wheel rates.'
])
# Apply only the calibrated difficulty flags, preserving the valid harder derivations.
for r in reviews:
 if not r['checks']['difficulty']:
  qs[r['questionId']]['difficulty']='hard' if r['questionId']==qid('285-4') else 'medium'
resolution_data={
'278-2':('The homogeneity line on p278 prints f(αx)=αx, omitting f on the right.', 'For a general linear map, scaling the input scales the mapped output. The supplied counterexample f(x)=2x gives f(3)=6 while 3×1=3, and αf(x)=6.', 'Preserve the literal source line as conflicting evidence; explicitly repair it to f(αx)=αf(x). This is not a claim that the source PDF was edited.'),
'278-3':('The homogeneity line on p278 prints f(αx)=αx.', 'For the explicitly supplied f(x)=2x, α=3, x=1, direct substitution gives f(αx)=6, αx=3 and αf(x)=6.', 'Use the exact counterexample to distinguish the printed expression from the corrected homogeneity law; retain both the source quotation and the worked calculation.'),
'278-4':('p278 defines solvable as having a unique solution, while p276 discusses multiple IK solutions and p279 asks an algorithm to find all possible joint values.', 'The cited internal lecture statements explicitly allow several solution branches. Existence or algorithmic solution does not imply uniqueness.', 'Read solvability as distinct from uniqueness in this question, retaining the contradictory definition as a documented source conflict rather than silently rewriting it.'),
'278-5':('p278 gives circle in a plane and sphere in XYZ as informal examples of a smaller-region sub-space.', 'Under the explicitly stated linear-vector-subspace interpretation, the unit circle contains (1,0) but not 2(1,0)=(2,0), so scalar closure fails.', 'Keep the source’s colloquial usage visible and limit the correction to linear vector subspaces. The counterexample is an explicit mathematical test, not a quotation of additional source text.'),
'284-3':('The middle p284 x/r expansion prints cosγ cosθ1−sinγ cosθ1, repeating the cosine factor.', 'The same page first states x=k1 cosθ1−k2 sinθ1 and k1/r=cosγ, k2/r=sinγ. Substitution therefore preserves sinθ1 in the second term, matching cos(γ+θ1).', 'Correct only the final factor of that middle expression to sinθ1 and retain the defective printed expression as conflicting evidence.'),
'285-1':('The last line on p288 prints θ3=φ−θ1+θ2, inconsistent with θ1+θ2+θ3=φ on p285 and p288.', 'Subtracting θ1 and θ2 from the printed angle-sum premise yields θ3=φ−θ1−θ2. Both complete unit-link branches reconstruct the stated orientation with this sign.', 'Use the angle-sum derivation and forward reconstruction as the basis; preserve the erroneous final source line rather than treating it as an alternative convention.'),
'290-2':('p290 writes J^−1 for a differential-drive Jacobian displayed on p289 as 3×2.', 'A 3×2 matrix cannot have an ordinary two-sided inverse. The following p291 explicitly supplies the full-column-rank pseudoinverse J+=(J^T J)^−1J^T.', 'Interpret the inverse task using the next-page pseudoinverse with its rank and feasibility conditions. Do not endorse an ordinary inverse of the non-square matrix.'),
'290-3':('The p290 forward-flow drawing labels qdot→J→pdot, opposite to the defining qdot=J pdot equation and wheel-rate definition.', 'The displayed J is 3×2, pdot=[ul,ur]^T is a 2-vector and qdot=[φdot,xdot,ydot]^T is a 3-vector. Their dimensions and the equation require pdot→J→qdot.', 'Correct the diagram’s variable roles in the question while retaining the original drawing as conflicting evidence. The source image itself remains unchanged.')}
for key,(claim,basis,method) in resolution_data.items():
 question(key)['conflictResolution']={'status':'derived-correction-pending-independent-review','sourceClaim':claim,'basis':basis,'method':method}
# Improve narrative spacing only in already changed objects; leave source evidence and formulas intact.
def readable(text):
 text=re.sub(r'([,;])(?=\S)',r'\1 ',text)
 text=re.sub(r'\b(the|a|an|with|from|to|for|and|of|only|both|all|in|at|than|is|by|has|gives|contains|reaches|radius|row|link|joint|rank|angle|reference|between|modulo|within|outside|above|below)(?=[0-9θφρψγβ])',r'\1 ',text)
 text=re.sub(r'\b(planar|Planar)(?=[23]R)',r'\1 ',text)
 for old,new in [('withpositive','with positive'),('theydot','the ydot'),('forr,d','for r, d'),('byzero','by zero'),('tozero','to zero'),('givezero','give zero'),('hasm×m','has m×m'),('wrongn×n','wrong n×n')]:text=text.replace(old,new)
 for old,new in {
  'unequal2R':'unequal 2R','frame3':'frame 3','have8':'have 8','promise8':'promise 8','exactly8':'exactly 8','All8':'All 8','All16':'All 16','equal3':'equal 3','Doubling(':'Doubling (','gives(':'gives (','values0':'values 0','or90degrees':'or 90 degrees','6DOF':'6-DOF','usesθ':'uses θ','orπ':'or π','beforeθ':'before θ','isolateθ':'isolate θ','returns0':'returns 0','restoresφ':'restores φ','Adding2π':'Adding 2π','and−1':'and −1','impliesθ':'implies θ','Every3':'Every 3','unique3':'unique 3','usesJ':'uses J','this3×2J':'this 3×2 J','The3':'The 3','withm':'with m','originalJ':'original J','displayed(':'displayed (','becauseJ':'because J','matrixJ':'matrix J','andb=':'and b=','giving[':'giving [','minimizesu':'minimizes u','underu':'under u','produces0':'produces 0','produces4':'produces 4','headingφ':'heading φ','forr, d':'for r, d','world+x':'world +x'
 }.items():text=text.replace(old,new)
 return text
changed=[];accepted=[]
for q in batch['questions']:
 prior=review[q['id']]
 if prior['decision']=='verified':
  assert question_hash(q)==prior['questionSha256'];accepted.append(q['id']);continue
 q['version']=2;q['status']='draft';q['reviewIds']=[]
 q['revisionAuthors']=list(dict.fromkeys(q.get('revisionAuthors',[])+['build_offline_study_interface-L08-independent']))
 q['stem']=readable(q['stem']);q['assumptions']=[readable(s) for s in q['assumptions']]
 for o in q['options']:o['text']=readable(o['text'])
 sol=q['solution']
 for key in ['justification','simpleExplanation']:
  sol[key]=readable(sol[key])
 sol['optionExplanations']={k:readable(v) for k,v in sol['optionExplanations'].items()}
 for key in ['steps','misconceptions','examTraps']:sol[key]=[readable(s) for s in sol[key]]
 changed.append(q['id']);assert q['correctOptionIds']==next(o for o in original['questions'] if o['id']==q['id'])['correctOptionIds']
assert len(changed)==34 and len(accepted)==76
history=ROOT/'audits/batch-history/W02-L08-v1-before-independent-repair.json';history.parent.mkdir(exist_ok=True);assert not history.exists(),'Archive already exists; check current revision before retrying'
history.write_bytes(raw)
# Check exact object equality, not only hashes, for all previously accepted questions.
orig={q['id']:q for q in original['questions']}
assert all(qs[i]==orig[i] for i in accepted)
path.write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
blind=[]
for i in changed:
 q=qs[i];entry={k:copy.deepcopy(q[k]) for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions']}
 entry['citations']=[{k:v for k,v in c.items() if k!='evidenceText'} for c in q['citations']]
 entry['questionSha256']=question_hash(q);blind.append(entry)
dump('audits/blind-W02-L08-v2-revisions.json',{'schemaVersion':'1.0.0','batchId':'W02-L08-v2-revisions','notice':'Answer-hidden revision packet: no proposed keys, solutions, conflict resolutions or citation evidenceText. Inspect the cited actual page pixels before solving. Prior v1 exposure must be disclosed by a returning reviewer.','questions':blind})
report={'revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviserId':'build_offline_study_interface-L08-independent','originalBatchSha256':hashlib.sha256(raw).hexdigest(),'historyPath':str(history.relative_to(ROOT)),'changedIds':changed,'changedCount':34,'newVersion':2,'status':'draft-pending-independent-review','answerSetsChanged':0,'acceptedPreservedCount':76,'acceptedPreservedHashes':{i:question_hash(qs[i]) for i in accepted},'newHashes':{i:question_hash(qs[i]) for i in changed},'conflictBindingsAdded':8,'difficultyAdjusted':19,'distractorSetsRepaired':11,'reviewPacket':'audits/blind-W02-L08-v2-revisions.json','sourceDisputesPreserved':True,'notes':['No source PDF, source-dispute ledger, inspection, bank or historical review was changed.','The reviser is recorded in revisionAuthors and cannot independently approve these changes.','Blind citations intentionally omit evidenceText to avoid revealing explanatory answers.']}
dump('audits/W02-L08-v2-revision-summary.json',report)
print(json.dumps({k:report[k] for k in ['changedCount','acceptedPreservedCount','answerSetsChanged','conflictBindingsAdded','difficultyAdjusted','distractorSetsRepaired']}))
