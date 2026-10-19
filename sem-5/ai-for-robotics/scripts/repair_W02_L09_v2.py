#!/usr/bin/env python3
"""Author repair from immutable L09 v1; never self-verify. Do not rerun v1 author script."""
import json,copy,hashlib,collections,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUTHOR='L09-author-20261019'
BATCH='W02-L09'
original=json.loads((ROOT/'data/question-batches/archive/W02-L09-v1.json').read_text())
batch=copy.deepcopy(original)
summary=json.loads((ROOT/'audits/W02-L09-independent-summary.json').read_text())
reviews=json.loads((ROOT/'data/reviews/W02-L09-v1-independent.json').read_text())
flags=set(summary['actionableFlags']);accepted={r['questionId']:r['questionSha256'] for r in reviews if r['decision']=='verified'}
Q={q['id']:q for q in batch['questions']};oldQ={q['id']:q for q in original['questions']};modified=set();new=[];author_checks=[]
def digest(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert len(flags)==48 and len(accepted)==54
assert all(digest(oldQ[r['questionId']])==r['questionSha256'] for r in reviews)
def q(short):
 key=BATCH+'-'+short
 assert key in flags
 modified.add(key);return Q[key]
def rewrite(short,options,why,stem=None):
 x=q(short);assert len(options)==len(why)==len(x['options'])
 if stem:x['stem']=stem
 for o in x['options']:o['text']=options[int(o['id'][1:])-1]
 x['solution']['optionExplanations']={f'o{i+1}':('Correct. ' if f'o{i+1}' in x['correctOptionIds'] else 'Incorrect. ')+v for i,v in enumerate(why)}
 x['solution']['justification']=' '.join(why[int(k[1:])-1] for k in x['correctOptionIds'])
 x['solution']['simpleExplanation']=x['solution']['justification']
 x['solution']['misconceptions']=[v for i,v in enumerate(why) if f'o{i+1}' not in x['correctOptionIds']]
def fm(expr,variables,units,assumptions):return dict(expression=expr,variables=variables,units=units,assumptions=assumptions)
def save(final=False):
 for key in modified:
  x=Q[key];x['version']=2;x['status']='draft';x['reviewIds']=[]
  x['revisionAuthors']=list(dict.fromkeys(x.get('revisionAuthors',[])+[AUTHOR]))
 for key,h in accepted.items():assert Q[key]==oldQ[key] and digest(Q[key])==h
 batch['revisionNote']='48 flagged v1 objects repaired as v2; 54 accepted v1 objects preserved exactly. New gap drafts require independent review.' if final else 'Incremental v2 author repair; independent review not yet requested.'
 (ROOT/'data/question-batches/W02-L09.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
 report={'batchId':BATCH,'final':final,'revisedIds':sorted(modified),'preservedAcceptedHashes':accepted,'newQuestionIds':[x['id'] for x in new],'checks':author_checks,'independentReviewPending':True}
 report['revisionBindings']=[{'questionId':k,'previousVersion':1,'previousQuestionSha256':digest(oldQ[k]),'currentVersion':2,'currentQuestionSha256':digest(Q[k]),'reviewerFindingsAddressedByAuthor':summary['actionableFlags'][k],'requiresNewIndependentReview':True} for k in sorted(modified)]
 (ROOT/'audits/W02-L09-v2-author-repair.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 if final:
  assert modified==flags
  blind=[]
  for x in batch['questions']:
   if x['id'] in modified or x['id'] in {v['id'] for v in new}:
    v={k:x[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions')}
    v['citations']=[{k:z for k,z in c.items() if k!='evidenceText'} for c in x['citations']];blind.append(v)
  path=ROOT/'audits/blind-W02-L09-v2.json';path.write_text(json.dumps(blind,ensure_ascii=False,indent=2)+'\n')
  sha=hashlib.sha256(path.read_bytes()).hexdigest()
  manifest={'batchId':BATCH,'revisedQuestions':len(modified),'preservedAcceptedQuestions':len(accepted),'newQuestions':len(new),'blindQuestions':len(blind),'blindPacketSha256':sha,'acceptedHashesPreserved':True,'independentReviewPending':True,'blindEvidenceTextOmitted':True,'questionBatchSha256':hashlib.sha256((ROOT/'data/question-batches/W02-L09.json').read_bytes()).hexdigest()}
  (ROOT/'audits/W02-L09-v2-packet-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('FROZEN',len(blind),sha)
 else:print('CHECKPOINT',len(modified),'revised objects')
rewrite('P0301-Q01',[
 'The differentiation/reference observer and the basis used to express the resulting vector',
 'The frame attached to the moving body and the frame attached to the point, with no separate observer role',
 'The expression basis at the initial time and the expression basis at the final time only',
 'The origin used for position and the axis used for scalar speed only'],[
 'The source distinguishes the observer defining relative motion from the coordinates representing that same vector.',
 'Body and point attachment alone do not distinguish the observer from the expression basis.',
 'Time samples do not replace the two simultaneous reference and representation roles.',
 'A position origin and a scalar magnitude do not define the velocity’s observer and vector basis.'])
rewrite('P0301-Q04',[
 'No; rotating zero keeps it zero, while changing the observer requires the frame-motion terms',
 'Yes; the coordinate rotation alone includes the frame-origin and rotational transport velocities',
 'No; changing the observer requires only an origin-translation term, even for a rotating frame',
 'No; therefore a marker fixed in B has zero velocity relative to every observer'],[
 'Re-expression preserves a zero B-relative vector. A different observer can measure motion from the B-origin translation and frame rotation.',
 'R only changes vector components; the origin velocity and ω×r terms must be added separately.',
 'A rotating frame also contributes ω×r, which can be nonzero even when the two origins coincide.',
 'Being fixed relative to B does not make the marker fixed relative to A.'])
rewrite('P0302-Q02',[
 'C identifies the moving origin, U the reference observer, and A the expression basis',
 'A identifies the moving origin, U the reference observer, and C the expression basis',
 'C identifies the moving origin, A the reference observer, and U the expression basis',
 'U identifies the moving origin, C the reference observer, and A the expression basis'],[
 'The shorthand defines the velocity of origin C relative to U and allows it to be expressed in A.',
 'This interchanges the moving-origin and expression-basis labels.',
 'This interchanges the observer and expression-basis labels.',
 'This reverses the moving-origin and observer roles.'])
rewrite('P0305-Q01',[
 'Origin translation p_AB, point coordinates q_B within B, and orientation R_AB',
 'Origin translation p_AB, point coordinates q_B within B, and a fixed R_AB',
 'Origin translation p_AB, a fixed point q_B within B, and orientation R_AB',
 'A fixed origin p_AB, point coordinates q_B within B, and orientation R_AB'],[
 'The general position relation p_A=p_AB+R_AB q_B permits all three factors to vary.',
 'This is the translation-only orientation special case, not the general changing-orientation case.',
 'This restricts the point to be body-fixed and omits general relative point motion.',
 'This omits general origin translation.'])
rewrite('P0311-Q02',[
 'From known base velocities to each successive child link and the end effector',
 'From a prescribed end-effector velocity to each parent link, without solving joint rates',
 'From the base to the end effector for angular velocity, but from tip to base for linear velocity',
 'From tip to base for angular velocity, but from base to tip for linear velocity'],[
 'Both angular and linear velocity recurrences propagate known upstream quantities outward.',
 'This describes an inverse task rather than the source’s outward velocity recurrence.',
 'The linear recurrence is also outward, using the parent-origin velocity and parent angular velocity.',
 'The angular recurrence is also outward, using inherited parent rotation plus the local joint rate.'])
rewrite('P0318-Q04',[
 'No; the block rotation is invertible and therefore preserves Jacobian rank',
 'Yes; choosing axes aligned with the image of J turns a missing output direction into an attainable one',
 'Yes; mixing linear and angular components can increase the number of independent task directions',
 'No; because rotating the basis preserves each individual Jacobian entry'],[
 'Premultiplication by an invertible coordinate map changes representation but not rank.',
 'An aligned basis can make the missing direction easier to identify, but it does not create it.',
 'An invertible basis change cannot increase the span dimension, and this block map rotates the two blocks without exchanging them.',
 'Individual entries generally change; rank is preserved because the transformation is invertible, not because entries are unchanged.'])
rewrite('P0319-Q03',[
 'The unavailable direction can be a linear combination of named axes, depending on configuration and basis',
 'The unavailable direction must always coincide with the first named world-coordinate axis',
 'Renaming the task axes can restore the missing physical output direction',
 'Each zero Jacobian entry identifies one lost Cartesian direction'],[
 'Rank loss concerns a subspace of task velocities; its representation need not align with one named world axis.',
 'The mathematical deficiency does not universally select the world x direction.',
 'An invertible coordinate change preserves rank and cannot restore physical capability.',
 'Individual zero entries do not determine the image dimension; full-rank matrices may contain many zeros.'])
rewrite('P0319-Q06',[
 'Near-singular inversion can amplify some rates; at exact rank loss, incompatible targets lack exact solutions while compatible targets may have finite solutions',
 'At exact rank loss, all targets lack finite solutions, including targets lying in the Jacobian image',
 'At exact rank loss, a least-squares rate is an exact solution for every desired task velocity',
 'Near-singular amplification proves that every bounded target needs an unbounded rate, including targets along well-conditioned directions'],[
 'Solvability at exact rank loss depends on membership in the image of J; inverse-rate growth near a singularity is a separate limiting issue.',
 'Compatible targets can have finite solutions; for J=diag(1,0), the target(2,0) is achieved by rate(2,0).',
 'For an incompatible target, least squares leaves a nonzero residual rather than producing an exact solution.',
 'Amplification depends on the target direction; a rate can remain bounded when the demand avoids the weakening direction.'])
rewrite('P0319-Q07',[
 'Joint-axis alignment in the workspace interior and configurations at workspace edges',
 'Joint-axis alignment only at workspace edges and all nonaligned interior configurations',
 'All orthogonal-axis configurations and all configurations halfway between joint limits',
 'All redundant-arm configurations and all configurations with a rectangular task Jacobian'],[
 'These are the two geometric examples named by the source; whether either is singular still depends on the task and rank.',
 'The source places the alignment example in the workspace interior and does not call every nonaligned interior pose singular.',
 'Orthogonality and midrange joint values do not by themselves establish the listed singularity examples.',
 'Redundancy and a rectangular Jacobian do not automatically imply a loss of attainable task rank.'])
rewrite('P0321-Q01',[
 'Compute joint velocities online from a desired Cartesian velocity',
 'Compute Cartesian velocity online from prescribed joint velocities',
 'Solve directly for a joint pose from a desired end-effector pose without rate integration',
 'Compute joint accelerations online from prescribed joint torques'],[
 'The source defines RMRC as real-time inverse velocity control followed by integration.',
 'This is the forward velocity map, the opposite input/output direction.',
 'This is position-level inverse kinematics rather than the stated rate-control update.',
 'This is a dynamics operation rather than the kinematic rate mapping.'])
rewrite('P0321-Q04',[
 'J depends on configuration, which generally changes while the joint rates are integrated',
 'Changing the desired Cartesian velocity changes J even when the configuration and kinematic model stay fixed',
 'Changing the integration timestep changes the geometric derivative J at an otherwise fixed configuration',
 'Integrating the joint rates makes the previous configuration’s J exact for every later configuration'],[
 'As q changes, J(q) may change, so a controller generally reevaluates the local map.',
 'The desired velocity changes the right-hand side of the rate equation; it does not by itself change a fixed model’s J(q).',
 'The timestep affects the numerical update, not the geometric derivative at the same q.',
 'Rate integration updates q; it does not make one local derivative globally valid.'])
rewrite('P0321-Q05',[
 'Singularity issues, accumulated trajectory drift, and dependence on an accurate kinematic model',
 'Singularity issues, ambiguity of inertia parameters, and dependence on an accurate mass matrix',
 'Accumulated trajectory drift, multiple static IK branches, and dependence on a global pose lookup table',
 'Dependence on an accurate kinematic model, fixed joint-space sampling resolution, and minimum-time trajectory search'],[
 'These are the three limitations explicitly named in the RMRC slide.',
 'Only singularity issues match; the listed method is kinematic and the slide does not list inertia or mass-matrix identification.',
 'Only drift matches; the bullet does not list static branch selection or a pose lookup table.',
 'Only kinematic-model dependence matches; those sampling and planning limitations are not the listed trio.'])
save(False)
rewrite('P0322-Q01',[
 'Analytic Jacobians from DH parameters versus online Jacobian estimates from data',
 'Finite-difference Jacobians from a geometric model versus symbolic differentiation of a fitted neural model',
 'Offline calibration of DH parameters versus lookup of a fixed precomputed Jacobian',
 'Online estimation in both columns, distinguished only by the chosen coordinate basis'],[
 'The table’s first row contrasts an analytic DH-based model with data-driven online estimation.',
 'These are plausible derivative strategies, but they are not the displayed first-row contrast.',
 'The learning column explicitly says estimated online, not merely a fixed precomputed lookup.',
 'The traditional column is described as analytic computation from DH parameters, not as the same online estimator in another basis.'])
rewrite('P0322-Q02',[
 'Broyden updates','Neural networks','Finite differences of a calibrated forward-kinematics model','Symbolic differentiation of DH transformation matrices'],[
 'Broyden updates are explicitly named in the table’s online-estimation parentheses.',
 'Neural networks are the other explicitly named technique in those parentheses.',
 'Finite differences can estimate derivatives, but this technique is not named in that table entry.',
 'Symbolic DH differentiation belongs to an analytic-model route and is not one of the two named online techniques.'])
rewrite('P0322-Q03',[
 'RMRC, operational-space control and impedance control',
 'PID control, sliding-mode control and model-predictive control',
 'Computed-torque control, adaptive control and iterative learning control',
 'Visual servoing, force-admittance control and gain-scheduled joint control'],[
 'This is the exact three-method group listed in the traditional-control column.',
 'These are plausible control methods, but not the three-method group printed in this row.',
 'This is another plausible robotics-control group, not the source’s stated list.',
 'These methods do not reproduce the printed RMRC/operational-space/impedance group.'])
rewrite('P0322-Q07',[
 'KUKA, ABB and UR','FANUC, Yaskawa and Stäubli','KUKA, FANUC and Kawasaki','ABB, Yaskawa and DENSO'],[
 'The source lists precisely these three industrial-arm examples.',
 'These are plausible industry names, but not the trio printed in the table.',
 'Only KUKA overlaps the printed trio; the other two differ.',
 'Only ABB overlaps the printed trio; the other two differ.'])
rewrite('P0322-Q08',[
 'Using Jacobian-related structure as a bridge for domain adaptation',
 'Using an unchanged simulator Jacobian only for nominal inverse-velocity commands',
 'Using the Jacobian chiefly to replace a contact-dynamics model with an inertia model',
 'Using the Jacobian only to rank static configurations by geometric reach'],[
 'The sim-to-real bullet specifically associates the Jacobian with domain adaptation.',
 'Nominal inverse-velocity control does not state the source’s cross-domain adaptation role.',
 'The cited row concerns adaptation across domains, not replacing contact dynamics with inertia modeling.',
 'A static reach ranking is not the sim-to-real bridge described in that row.'])
rewrite('P0322-Q09',[
 'A neural inverse model replaces an explicit pseudoinverse computation',
 'A neural forward model is differentiated and then followed by an explicit pseudoinverse',
 'A neural torque model replaces the actuator dynamics while analytic IK is retained',
 'A neural geometry estimator supplies DH parameters to an otherwise analytic inverse solver'],[
 'The learning column explicitly describes learned IK as a neural network replacing the pseudoinverse.',
 'This retains the explicit pseudoinverse and uses the network for a different intermediate role.',
 'This changes a dynamics model rather than the inverse-kinematics computation named in the table.',
 'This learns geometric parameters but retains an analytic inverse solver, unlike the stated replacement.'])
rewrite('P0322-Q10',[
 'Backpropagating gradients through the kinematic mapping',
 'Forward-integrating joint rates through the kinematic mapping without a backward derivative pass',
 'Applying only a Jacobian determinant test before choosing a pose',
 'Integrating Cartesian velocities numerically to reconstruct the task trajectory'],[
 'The table explicitly names backpropagation through kinematics; derivatives propagate a learning objective backward through the map.',
 'Forward simulation is distinct from the stated gradient-backpropagation operation.',
 'A determinant test detects some square-map singularities but is not the stated differentiable-learning operation.',
 'Trajectory integration is a forward accumulation process, not backpropagation through kinematics.'])
rewrite('P0322-Q12',[
 'Fast adaptation to new robot morphologies',
 'Calibration of one fixed robot morphology from a single data set',
 'Learning one task-specific inverse map for one fixed robot',
 'Optimizing one prescribed trajectory without adapting robot geometry'],[
 'The final learning-side bullet explicitly names adaptation to new robot morphologies.',
 'Single-morphology calibration does not state the cross-morphology adaptation objective.',
 'A fixed task/robot inverse map lacks the named adaptation to new morphologies.',
 'A single trajectory optimization does not capture the listed meta-learning purpose.'])
rewrite('P0322-Q13',[
 'A derivative used in learning need not be the robot’s analytic joint-to-twist Jacobian',
 'A policy-parameter gradient is the same matrix as the joint-to-twist Jacobian because both are derivatives',
 'A learned forward-model Jacobian necessarily has the same inputs and outputs as the geometric Jacobian',
 'A Jacobian-like policy update must differentiate a DH model even when its policy is parameterized directly'],[
 'Jacobians are derivatives of particular maps; the policy or learned model may have different inputs, outputs and dimensions from the robot’s geometric map.',
 'Policy parameters and joint coordinates are different variables, so these derivatives are not identified merely by the word gradient.',
 'A forward model may map states/actions to future states rather than joint coordinates to end-effector velocity; its derivative need not be the geometric Jacobian.',
 'The source’s analogy does not require every model-free policy update to include an analytic DH model.'])
rewrite('P0323-Q04',[
 'The Jacobian transpose J^T','The untransposed Jacobian J','The ordinary Jacobian inverse J^−1','The Moore–Penrose pseudoinverse J^+'],[
 'The summary explicitly associates force control with J^T; matching virtual-power conventions give joint effort from task force through the transpose.',
 'J is the forward joint-rate-to-task-velocity map, not the transpose force association named here.',
 'J^−1 is used for square nonsingular inverse velocity mapping, not this task-force-to-joint-effort association.',
 'A pseudoinverse can be used in rate-solving contexts, but it is not the operation named for force control in this summary.'])
# The reviewer requested modest difficulty labels for direct conceptual checks.
for short in ['P0301-Q04','P0303-Q04','P0315-Q05','P0316-Q02','P0318-Q04','P0319-Q02','P0319-Q03','P0319-Q05','P0319-Q09','P0322-Q04','P0323-Q03']:
 q(short)['difficulty']='medium'
q('P0319-Q08')['difficulty']='hard'
save(False)
# Self-contained formula-sheet metadata and independently readable numerical workings.
x=q('P0299-Q02');x['solution']['formulas']=[fm('speed=sqrt(vx²+vy²+vz²)',{'vx':'x component of the point velocity in the specified Cartesian basis and reference frame','vy':'y component of the same velocity vector','vz':'z component of the same velocity vector','speed':'nonnegative Euclidean norm of that velocity vector'},{'vx':'m/s','vy':'m/s','vz':'m/s','speed':'m/s'},['Orthonormal Cartesian axes; all three components refer to the same observer, point and basis.'])]
x['solution']['justification']='The speed is the nonnegative velocity norm: sqrt(3²+4²+0²)=5 m/s.';x['solution']['simpleExplanation']=x['solution']['justification'];x['solution']['optionExplanations']['o1']='Correct. The nonnegative norm is sqrt(9+16)=5 m/s.'
FRAME=['Right-handed orthonormal frames. R_AB maps B-basis components into A-basis components.','When only re-expressing a vector, keep the same physical point and reference observer. Changing the observer is a different operation and requires the frame-motion terms.']
transport=fm('v_Q^A=v_origin^A+R_AB v_relative^B+omega^A×(R_AB q_B)',{
 'v_Q^A':'velocity of point Q relative to observer A, expressed in the A basis',
 'v_origin^A':'velocity of the B-frame origin relative to A, expressed in A',
 'v_relative^B':'velocity of Q relative to observer B, expressed in B',
 'q_B':'position offset from the B origin to Q, expressed in B',
 'omega^A':'angular velocity of frame B relative to A, expressed in A',
 'R_AB':'rotation mapping B components into A components'},
 {'v_Q^A':'m/s','v_origin^A':'m/s','v_relative^B':'m/s','q_B':'m','omega^A':'rad/s','R_AB':'dimensionless'},FRAME)
for short in ['P0306-Q02','P0310-Q02']:q(short)['solution']['formulas']=[copy.deepcopy(transport)]
x=q('P0306-Q02');x['stem']='For constant R_AB=Rz(90°), v_origin^A=(1, 0, 0) m/s and v_relative^B=(2, 0, 0) m/s, what is v_Q^A?'
x['assumptions']=FRAME+['Rz(90°)=[[0, −1, 0], [1, 0, 0], [0, 0, 1]] is constant in time, so omega^A=0.']
x['solution']['formulas'][0]['assumptions']+=['Constant relative orientation implies omega^A=0, reducing the general formula to v_Q^A=v_origin^A+R_AB v_relative^B.']
x['solution']['steps']=['Constant R_AB implies omega^A=0, so the rotational transport term vanishes.','Rotate the B-relative vector: Rz(90°)(2, 0, 0)=(0, 2, 0) m/s.','Add the origin velocity: (1, 0, 0)+(0, 2, 0)=(1, 2, 0) m/s.']
x=q('P0310-Q02');x['solution']['steps']=['Rotate q_B: R_AB q_B=(0, 2, 0) m.','Compute rotational velocity: (0, 0, 2)×(0, 2, 0)=(−4, 0, 0) m/s.','Rotate the relative velocity: R_AB v_relative^B=(0, 1, 0) m/s.','Add origin, relative and rotational terms: (1, 0, 0)+(0, 1, 0)+(−4, 0, 0)=(−3, 1, 0) m/s.']
REC=['Both link velocities are measured relative to the same fixed base observer, not differentiated relative to the moving link itself.','R maps parent-basis components into the child basis. P points from the parent origin to the child origin and is expressed in the parent basis.','All cross products are evaluated in one basis before rotation. The joint-axis unit vector z_child is expressed in the child basis.']
variables={'omega_parent':'parent-link angular velocity relative to the fixed base observer, expressed in the parent basis','omega_child':'child-link angular velocity relative to the same base observer, expressed in the child basis','v_parent':'parent-origin linear velocity relative to the fixed base observer, expressed in the parent basis','v_child':'child-origin linear velocity relative to the same base observer, expressed in the child basis','R':'parent-to-child coordinate rotation','P':'vector from parent origin to child origin in parent components','z_child':'unit vector of the joint axis expressed in the child basis'}
units={'omega_parent':'rad/s','omega_child':'rad/s','v_parent':'m/s','v_child':'m/s','R':'dimensionless','P':'m','z_child':'dimensionless'}
rev_formula=fm('omega_child=R omega_parent+theta_dot z_child; v_child=R(v_parent+omega_parent×P)',dict(variables,theta_dot='relative revolute-joint angle’s first time derivative'),dict(units,theta_dot='rad/s'),REC+['For this revolute recurrence, P is constant in the parent frame and the new revolute axis passes through the child origin.'])
prism_formula=fm('omega_child=R omega_parent; v_child=R(v_parent+omega_parent×P)+d_dot z_child',dict(variables,d_dot='first time derivative of prismatic-joint displacement d'),dict(units,d_dot='m/s'),REC+['An ideal prismatic joint adds translation along z_child but no relative angular velocity. P is the instantaneous origin offset; it need not remain constant during prismatic extension.'])
for short in ['P0312-Q05','P0313-Q03','P0313-Q04']:q(short)['solution']['formulas']=[copy.deepcopy(rev_formula)]
for short in ['P0314-Q03','P0314-Q04']:q(short)['solution']['formulas']=[copy.deepcopy(prism_formula)]
x=q('P0312-Q05');x['assumptions']=REC+['For this revolute joint, P is constant in the parent frame and z_child=(0, 0, 1).','The given Rx(90°)=[[1, 0, 0], [0, 0, −1], [0, 1, 0]] maps parent components into child components.']
x['solution']['steps']=['Apply Rx(90°) to omega_parent=(0, 0, 2), obtaining (0, −2, 0) rad/s.','The local revolute contribution is theta_dot z_child=3(0, 0, 1)=(0, 0, 3) rad/s.','Add the two child-basis vectors to obtain omega_child=(0, −2, 3) rad/s.']
x['solution']['optionExplanations']['o1']='Correct. Rotate the inherited angular velocity into child −y, then add the local +z joint rate: (0, −2, 0)+(0, 0, 3)=(0, −2, 3) rad/s.'
x['solution']['justification']='The inherited angular velocity is re-expressed before adding the child-local revolute rate, giving (0, −2, 3) rad/s.';x['solution']['simpleExplanation']=x['solution']['justification']
x=q('P0313-Q03');x['assumptions']=REC+['Revolute frame placement: P is constant in the parent basis and the new joint axis passes through the child origin.','R=I is the parent-to-child component map at this instant.']
x['solution']['optionExplanations']['o1']='Correct. omega_parent×P=(0, 6, 0) m/s; adding v_parent gives (1, 8, 0) m/s, unchanged by R=I.'
x['solution']['justification']='The inherited linear velocity plus the rotational sweep is (1, 2, 0)+(0, 6, 0)=(1, 8, 0) m/s.';x['solution']['simpleExplanation']=x['solution']['justification']
x=q('P0313-Q04');x['stem']='Given v_parent=(1, 2, 0) m/s, omega_parent=(0, 0, 2) rad/s, P=(3, 0, 0) m, and R_child,parent=Rz(−90°), what is v_child?'
x['assumptions']=REC+['Revolute frame placement: P is constant in the parent basis and the new joint axis passes through the child origin.','Rz(−90°)=[[0, 1, 0], [−1, 0, 0], [0, 0, 1]] maps parent components to child components.']
x['solution']['steps']=['Compute omega_parent×P=(0, 6, 0) m/s.','The parent-basis sum is v_parent+omega_parent×P=(1, 8, 0) m/s.','Multiply the complete sum by Rz(−90°) to obtain (8, −1, 0) m/s.']
x=q('P0314-Q01');next(o for o in x['options'] if o['id']=='o2')['text']='It adds the linear joint speed d_dot z_child directly to angular velocity'
x['assumptions']=REC+['d_dot denotes the first time derivative of prismatic displacement d, measured in m/s; it is not a second derivative or an angular rate.']
x=q('P0314-Q03');x['stem']='Use v_parent=(1, 2, 0) m/s, omega_parent=(0, 0, 2) rad/s, P=(3, 0, 0) m, R=Rz(−90°), and prismatic speed d_dot=4 m/s along child z. What is v_child?'
x['assumptions']=REC+['d_dot=dd/dt is the first time derivative of the prismatic displacement, not acceleration.','z_child=(0, 0, 1); Rz(−90°)=[[0, 1, 0], [−1, 0, 0], [0, 0, 1]].']
x['solution']['steps']=['The parent-basis sum is (1, 2, 0)+(0, 0, 2)×(3, 0, 0)=(1, 8, 0) m/s.','Rz(−90°) maps this sum to (8, −1, 0) m/s.','Add d_dot z_child=4(0, 0, 1)=(0, 0, 4) m/s.','The child-origin velocity is (8, −1, 4) m/s.']
x=q('P0314-Q04');x['assumptions']=REC+['At this instant v_parent=(0, 0, 0) m/s, P=(0, 0, 0) m and R=I.','The first derivative of prismatic displacement is d_dot=3 m/s, with z_child=(0, 0, 1).']
x['solution']['steps']=['R=I leaves omega_parent=(0, 0, 2) rad/s unchanged.','Coincident origins give P=0, so omega_parent×P=0; the parent-origin linear velocity is also zero.','The child linear velocity is solely d_dot z_child=(0, 0, 3) m/s.','Thus omega_child=(0, 0, 2) rad/s and v_child=(0, 0, 3) m/s.']
x['solution']['examTraps']=['A prismatic joint adds a linear speed, not an angular rate or acceleration.']
x=q('P0315-Q04');x['stem']='For F(q1,q2)=q1²+q2 and G(q1,q2)=q1 q2 at (q1,q2)=(2,3), what output rate results from q_dot=(0.5,−1) per second?'
x['assumptions']=['The task output is x=(F,G). All joint/input and task coordinates are dimensionless; time is in seconds.','Evaluate the derivatives at q1=2 and q2=3.']
x['solution']['steps']=['Differentiate: J=[[2q1, 1], [q2, q1]].','At (2,3), J=[[4, 1], [3, 2]].','F_dot=4(0.5)+1(−1)=1 per second.','G_dot=3(0.5)+2(−1)=−0.5 per second.']
x['solution']['formulas']=[fm('J_ij=∂f_i/∂q_j; x_dot=J(q) q_dot',{'f_i':'ith component of f=(F,G), the task-position map','q_j':'jth input coordinate of q=(q1,q2)','i':'task-component index','j':'input-coordinate index','J_ij':'row i, column j of the Jacobian J','J':'matrix of task derivatives with respect to q','q':'input-coordinate vector at which derivatives are evaluated','x_dot':'time derivative of task vector x=(F,G)','q_dot':'time derivative of input vector q'},{'f_i':'dimensionless','q_j':'dimensionless','i':'dimensionless index','j':'dimensionless index','J_ij':'dimensionless','J':'dimensionless','q':'dimensionless','x_dot':'s^−1','q_dot':'s^−1'},x['assumptions'])]
x=q('P0318-Q03');x['solution']['formulas']=[fm('twist_A=diag(R_AB,R_AB) twist_B',{'twist_A':'stacked [v_A; omega_A] for the same physical point/body motion and fixed reference observer, expressed in basis A','twist_B':'the same stacked [linear; angular] velocity expressed in basis B','v_A':'point linear velocity in A components','v_B':'the same point linear velocity in B components','omega_A':'body angular velocity in A components','omega_B':'the same body angular velocity in B components','R_AB':'rotation mapping B components into A components','diag(R_AB,R_AB)':'6×6 block-diagonal basis-change matrix'},{'v_A':'m/s','v_B':'m/s','omega_A':'rad/s','omega_B':'rad/s','twist_A':'first three entries m/s; last three entries rad/s','twist_B':'first three entries m/s; last three entries rad/s','R_AB':'dimensionless','diag(R_AB,R_AB)':'dimensionless'},FRAME+['No shift of the physical reference point and no change of the reference observer.'])]
x['solution']['justification']='The same rotation acts on both blocks: +x becomes +y, and +y becomes −x.';x['solution']['simpleExplanation']=x['solution']['justification'];x['solution']['optionExplanations']['o1']='Correct. Rotate both vectors: v_A=(0, 1, 0) m/s and omega_A=(−1, 0, 0) rad/s.'
x['solution']['steps']=['Multiply Rz(90°) by v_B=(1, 0, 0) to obtain v_A=(0, 1, 0) m/s.','Multiply the same Rz(90°) by omega_B=(0, 1, 0) to obtain omega_A=(−1, 0, 0) rad/s.','Stack the linear block first and the angular block second.']
x=q('P0321-Q03');x['solution']['formulas']=[fm('q_dot=J^−1 v; q_next=q+q_dot delta_t',{'q_dot':'computed first time derivative of the joint/input-coordinate vector','q_next':'joint/input-coordinate vector at the end of this Euler step','q':'current joint/input-coordinate vector','v':'desired task-coordinate time derivative','J':'specified nonsingular local Jacobian relating joint and task rates','delta_t':'duration of this integration step'},{'q_dot':'s^−1','q_next':'dimensionless','q':'dimensionless','v':'s^−1','J':'dimensionless in this example','delta_t':'s'},['Generated dimensionless-coordinate example. Hold the computed q_dot constant for one forward-Euler step.'])]
x=q('P0322-Q05');x['stem']='What role does null-space joint-rate control have in the table?'
next(o for o in x['options'] if o['id']=='o1')['text']='Redundancy resolution using joint rates whose contribution to the primary instantaneous task velocity is zero'
x['solution']['optionExplanations']['o1']='Correct. A null-space joint-rate vector z satisfies Jz=0, so its instantaneous primary-task velocity contribution is zero.'
x['solution']['optionExplanations']['o2']='Incorrect. A null-space rate contributes zero instantaneous velocity to the specified primary task; it does not add an arbitrary end-effector velocity. This is not a guarantee about a finite displacement under nonlinear kinematics.'
x['solution']['justification']='The table associates null-space control with redundancy resolution. Its defining local relation is Jz=0 for a joint-rate vector z.';x['solution']['simpleExplanation']='The robot can use suitable joint rates for a secondary purpose without adding instantaneous velocity to the selected primary task.'
x['assumptions']=['z is a joint-rate vector in the null space of the current task Jacobian J: Jz=0.','The statement is instantaneous; a finite displacement in a null space computed at one configuration need not preserve the finite task pose.']
x['solution']['misconceptions']=['A local null-space rate is not an arbitrary task velocity.','A finite displacement along a locally null direction can change a nonlinear task pose.','Null spaces are defined with respect to a specified task Jacobian.']
save(False)
# Explicit, version-bound handling of literal source conflicts. These are proposed
# question-scope resolutions awaiting a different reviewer's approval, not PDF repairs.
resolutions={
 'P0316-Q02':(316,'The Jacobian will vary as a function of time.','The source writes J(θ). Therefore time dependence occurs through θ(t); a fixed configuration or a constant derivative map can leave J unchanged. For the explicit linear task f(q)=q, J=I at every time.','Restrict the claim to possible configuration-induced time variation, not mandatory change in every entry.'),
 'P0319-Q02':(319,'No instantaneous motion along one of the Cartesian coordinates is possible; the manipulator loses one or more DOF.','For the specified map v=J(q)q_dot, attainable instantaneous task velocities form image(J). A drop below the attainable regular rank reduces this image dimension without removing any physical joint.','Define singularity for the stated differential task and model; do not identify every zero entry or constrained joint with rank loss.'),
 'P0319-Q03':(319,'No instantaneous motion along one of the Cartesian coordinates is possible.','An invertible task-basis change D sends image(J) to D image(J) and preserves rank. The unavailable direction need not align with a named world axis; it may be a linear combination of coordinate directions.','Interpret the sentence geometrically as loss of an instantaneous output direction, not necessarily one named Cartesian axis.'),
 'P0319-Q06':(319,'At the actual singularity we would require infinite motion from the joint.','For J=diag(1,0), v=(2,0) has the finite solution q_dot=(2,0), whereas v=(0,1) has no exact solution. For J_epsilon=diag(1,epsilon), epsilon>0, the latter target gives q_dot=(0,1/epsilon), which diverges only as a near-singular limit.','Separate exact compatibility from near-singular inverse-rate amplification; do not interpret an infinite rate as an exact executable solution.'),
 'P0319-Q10':(319,'Additional singularities may exist that are not predicted by the Jacobian.','A differential singularity of the explicitly modeled task is defined and diagnosed by its task-Jacobian rank. Collision, joint-limit, representation and unmodeled physical failures need their own models or definitions; full rank alone does not exclude them.','Bound the answer to the specified task Jacobian rather than claiming that one kinematic model diagnoses every physical failure.'),
 'P0321-Q06':(321,'Explicit Jacobian provides interpretability and safety guarantees.','The equation v=Jq_dot describes a local rate map. It contains no collision clearance, actuator-limit or model-validity constraints by itself. The same slide lists singularity and model-accuracy limitations.','Preserve the interpretability benefit but require explicit constraints and controller/model checks before any physical-safety guarantee.'),
 'P0323-Q03':(323,'The summary states J(θ) is 6×n and then writes Singularities (det J = 0).','An ordinary determinant is defined only for a square matrix. A full spatial 6×n task is square only when n=6; otherwise task rank, rather than an undefined ordinary determinant, diagnoses differential rank loss.','Restrict determinant testing to square maps; use the specified task’s attainable regular rank for rectangular maps.')}
for short,(page,claim,basis,method) in resolutions.items():
 x=q(short)
 x['conflictResolution']={'status':'derived-qualification-pending-independent-review','questionVersion':2,'sourceId':'lectures','sourceSha256':x['citations'][0]['sourceSha256'],'physicalPage':page,'sourceClaim':claim,'basis':basis,'method':method,'scope':'This question version only. The source PDF remains unchanged and the global source-dispute record is retained.'}
 for c in x['citations']:
  c['role']='conflict' if c['physicalPage']==page else 'premise'
  if c['physicalPage']==page:c['locator']=f'Printed slide {page-295}: '+{316:'time-variation statement next to the J(θ) rate map',319:'singularity interpretation and rank/inverse-rate claims',321:'final AI-connection bullet claiming interpretability and safety guarantees',323:'6×n Jacobian description and unqualified det J = 0 statement'}[page]
# Avoid labeling correct incidental equations as conflicts in the determinant item.
x=q('P0323-Q03');x['citations']=[c for c in x['citations'] if c['physicalPage']!=316]
for short in ['P0316-Q03','P0316-Q04']:
 x=q(short);x['citations']=[c for c in x['citations'] if c['physicalPage']!=316]
 for c in x['citations']:
  if c['physicalPage']==317:c['role']='premise'
  if c['physicalPage']==323:
   c['role']='explicit';c['locator']='Printed slide 28: the explicit 6×n Jacobian dimension and joint-rate-to-end-effector-velocity description'
   c['evidenceText']='The Jacobian J(θ) is a 6×n matrix mapping joint velocities to end-effector Cartesian velocities.'
x=q('P0316-Q03');x['assumptions']=['A full six-component geometric velocity task, with three linear and three angular components, and n independent joint coordinates.']
x=q('P0316-Q04');x['solution']['optionExplanations']['o3']='Incorrect. A 6×6 matrix cannot multiply the given 7×1 joint-rate vector.';x['solution']['misconceptions']=['Swapping input and output dimensions reverses the velocity map.','A 6×6 Jacobian has only six joint-rate input columns.','A 3×7 map omits the angular-velocity task components.']
# Human-readable source-dispute ledger; identifiers and meanings are preserved.
issue_prose={
 'notation_roles':('Nested reference/expression superscripts and derivative notation can be confused. Rotating a zero B-relative velocity does not produce its generally nonzero A-relative motion.','Name the differentiation observer and expression basis separately. Add transport terms only when changing the physical observer.'),
 'moving_vector_labels':('The diagram labels successive geometric vectors even though the point is fixed in its body frame. Their directions in the fixed frame change, but the body-coordinate tuple remains constant.','Interpret the picture geometrically in fixed frame A; do not subtract coordinate tuples expressed in different moving bases.'),
 'finite_chord_scope':('The small-motion equation uses radius times angle for displacement length. A finite tip chord differs from the circular arc; the intermediate scalar/vector notation is compressed.','Use the infinitesimal limit or an explicitly first-order approximation. The exact instantaneous vector result is omega×r.'),
 'frame_placement':('The revolute linear recurrence assumes the parent-to-child origin offset is constant in the parent frame and the new joint axis passes through the child origin.','Preserve that frame placement. Do not apply the formula unchanged to arbitrary frame choices or an offset tool point.'),
 'general_shape_and_time':('The printed most-general 6×6 claim conflicts with the nonsquare statement and later 6×n summary. Mandatory time variation is also too broad.','Use 6×n for the full spatial task with n joint-rate inputs; 6×6 is the n=6 case. Configuration-induced time variation can vanish.'),
 'rotation_only_scope':('Blockdiag(R,R) changes the expression basis of the same point/body velocity. It does not include a physical reference-point shift or change of moving observer.','Keep the same physical point and observer. A point shift requires the appropriate omega×r term. The source equation is valid within its proper scope.'),
 'rank_direction_and_infinity':('The descriptions of losing one Cartesian coordinate and requiring infinite motion at the actual singularity are overbroad.','Use task-rank loss; unavailable directions can combine named axes. Near-singular inverse mapping may amplify rates. At exact rank loss, compatible targets may have finite solutions while incompatible targets have no exact solution.'),
 'geometric_examples_and_other_singularities':('Joint-axis alignment and workspace-edge examples are context dependent. Claims about additional singularities and singularity-free structures need task/model bounds.','Use the correct task-map rank test. Joint limits can bound a workspace without differential rank loss, and duplicate columns need not eliminate full row rank in a redundant task. Treat other failure modes separately.'),
 'safety_and_learning_claims':('The explicit-Jacobian safety claim and the RL/RMRC behavioral connection are not qualified on the slide.','Treat the RL connection as an analogy. Interpretability alone does not guarantee safety without explicit constraints, valid models and controller checks.'),
 'overdot_rendering':('Enlarged PDF pixels make combining overdots overlap the theta glyph. Encoded PDF text contains U+0307 on the computed rate and Euler-rate factor; the same rendering issue occurs on p323.','Do not label these as missing-dot source equations. Transcribe theta_dot explicitly and retain the rejected defect allegation.'),
 'learning_table_scope':('Exact analytic-model and neural-inverse wording can be overread. Learning derivatives are not necessarily the robot’s geometric Jacobian; named software examples are not current-API guarantees.','Use conditional model fidelity and source-attributed examples. Do not claim every neural IK map equals the Moore–Penrose pseudoinverse or every model-free RL method uses an analytic robot Jacobian.'),
 'determinant_scope':('The summary introduces a 6×n Jacobian and then uses det J=0 without restricting the matrix to square dimensions.','Use an ordinary determinant only for square matrices; otherwise use task rank. Force-transpose questions state their virtual-power scope and do not claim to model all robot dynamics.')}
for item in batch['sourceIssues']:
 key=next(k for k in issue_prose if item['id'].endswith('-'+k));item['finding'],item['handling']=issue_prose[key]
(ROOT/'audits/source-disputes-W02-L09.json').write_text(json.dumps(batch['sourceIssues'],ensure_ascii=False,indent=2)+'\n')
assert modified==flags
save(False)
# Three new IDs close the independently identified source gaps without changing
# the content of any of the 54 accepted questions.
SHA=original['questions'][0]['citations'][0]['sourceSha256']
def add_gap(page,num,stem,options,why,*,kind='conceptual',difficulty='medium',assumptions=None,locator='',region=None):
 cid=f'W02-L09-P{page:04}-C01';qid=f'W02-L09-P{page:04}-Q{num:02}';assert qid not in Q
 c=next(v for v in batch['concepts'] if v['id']==cid)
 oo=[{'id':f'o{i+1}','text':v} for i,v in enumerate(options)];shift=int(hashlib.sha256(qid.encode()).hexdigest()[:4],16)%len(oo);oo=oo[shift:]+oo[:shift]
 x=dict(id=qid,version=1,status='draft',authorId=AUTHOR,stem=stem,selectionMode='single',type=kind,difficulty=difficulty,cognitiveSkill='application' if kind=='diagram' else 'recall' if difficulty=='easy' else 'conceptual',week=2,lectureId='L09',topic=original['questions'][0]['topic'],subtopic=c['title'],tags=['jacobian-velocity','robotics','independent-coverage-gap-repair'],conceptIds=[cid],assumptions=assumptions or [],options=oo,correctOptionIds=['o1'],citations=[dict(slideId=f'lectures-p{page:04}',sourceId='lectures',sourceSha256=SHA,physicalPage=page,kind='figure' if kind=='diagram' else 'table' if page==322 else 'statement',locator=locator,evidenceText=(ROOT/f'sources/text/lectures/page-{page:04}.txt').read_text().strip(),role='explicit',region=region)],solution=dict(justification=why[0],optionExplanations={f'o{i+1}':('Correct. ' if i==0 else 'Incorrect. ')+v for i,v in enumerate(why)},steps=[],formulas=[],simpleExplanation=why[0],memoryAid=None,misconceptions=why[1:],examTraps=[],prerequisiteConceptIds=[]),origin='generated',reviewIds=[])
 batch['questions'].append(x);Q[qid]=x;new.append(x);c['questionIds'].append(qid);c['examinationAngles'].append(stem);return x
x=add_gap(309,8,'In the rotational-motion figure with axis origin O, circle center A, old point B and new point C, which mapping of line segments is correct?',[
 'OA: axial projection; AB and AC: circular radii; OB and OC: full old/new point vectors; BC: finite tip chord',
 'OA: circular radius; AB and AC: axial projections; OB and OC: full old/new point vectors; BC: finite tip chord',
 'OA: axial projection; AB and AC: full point-vector lengths; OB and OC: circular radii; BC: finite tip chord',
 'OA: axial projection; AB and AC: circular radii; OB and OC: full old/new point vectors; BC: circular arc'],[
 'A is the projection of the point onto the rotation axis. AB and AC measure perpendicular distance to that axis; OB and OC are the full position vectors. The straight segment BC is the finite displacement chord.',
 'The axial projection lies along OA, whereas AB and AC extend from the axis to the circle.',
 'This swaps the full vectors from O with the perpendicular circular radii from A.',
 'BC is the straight chord joining the two point positions, not the curved arc. Chord and arc agree only to first order for a small rotation.'],kind='diagram',assumptions=['Interpret the labeled source figure geometrically in one fixed frame. The point is fixed in the rotating body.','The instantaneous derivation uses the small-angle limit; no finite-angle chord/arc equality is assumed.'],locator='Printed slide 14: upper-right O/A/B/C circular-motion figure, old Q(t), new Q(t+Δt), and ΔQ chord',region={'x':0.66,'y':0.04,'width':0.34,'height':0.56})
x['solution']['formulas']=[fm('radius=|Q| sin(theta); |BC|=2 radius sin(delta/2)',{'radius':'perpendicular distance AB=AC from the point to the rotation axis','|Q|':'full point-vector length OB=OC','theta':'angle between O-to-point vector and the rotation axis','delta':'finite rotation angle between AB and AC','|BC|':'straight displacement-chord length'},{'radius':'m','|Q|':'m','theta':'rad','delta':'rad','|BC|':'m'},['Fixed point undergoing pure rotation about the illustrated axis.','The finite chord formula is a geometric derivation; |BC|≈radius·delta only for small delta.'])]
x=add_gap(321,9,'Which application pair is explicitly associated with RMRC in the lecture’s “simple, efficient” usefulness bullet?',[
 'Industrial robot teleoperation and AI manipulation',
 'Offline DH-parameter calibration and static workspace reconstruction',
 'Actuator inertia identification and inverse-dynamics torque fitting',
 'One-shot pose-level IK and global collision-free path search'],[
 'The slide explicitly names industrial robot teleoperation and AI manipulation as RMRC applications. Its online velocity-level update fits these contexts; the wording is not a universal performance guarantee.',
 'These are plausible robotics modeling tasks, but they are not the application pair named in that bullet.',
 'These concern dynamic parameter/torque modeling rather than the named RMRC application pair.',
 'These are position/planning-level tasks, not the two application contexts identified in the usefulness bullet.'],difficulty='easy',assumptions=['Source-specific application recall. “Simple, efficient” is the lecture’s characterization, not a guarantee for every robot or control objective.'],locator='Printed slide 26: third bullet naming industrial robot teleoperation and AI manipulation')
x=add_gap(322,14,'What does the traditional-control table mean by Jacobian-based singularity avoidance?',[
 'Use the task Jacobian to identify problematic configurations and steer the control or trajectory away from them when feasible',
 'Rotate only the Cartesian coordinate basis until a rank-deficient configuration becomes full rank',
 'Add joint-limit inequalities to an unchanged Jacobian and assume its rank automatically increases',
 'Replace an analytic controller with a learned policy and omit singularity analysis for the same mechanism'],[
 'The named use is avoidance of problematic configurations, not a claim that evaluating J changes the mechanism. Avoidance may require feasible alternative configurations or trajectories.',
 'An invertible coordinate rotation preserves rank; it cannot remove a physical task-rank loss.',
 'Joint-limit constraints affect feasibility but do not automatically add independent columns or increase the local task-map rank.',
 'A learned controller does not remove a mechanism’s kinematic singularities merely by replacing an analytic control law.'],assumptions=['A specified task Jacobian and its appropriate regular-rank criterion. Avoidance is considered only when the robot and task permit a feasible alternative.'],locator='Printed slide 27: traditional-control column, Jacobian-based singularity avoidance bullet')
# Add mathematical/source premises used by the avoidance distinctions.
for page,loc in [(318,'Printed slide 23: invertible block-diagonal Jacobian basis-change equation'),(319,'Printed slide 24: using the Jacobian to predict singularities')]:
 x['citations'].append(dict(slideId=f'lectures-p{page:04}',sourceId='lectures',sourceSha256=SHA,physicalPage=page,kind='equation' if page==318 else 'statement',locator=loc,evidenceText=(ROOT/f'sources/text/lectures/page-{page:04}.txt').read_text().strip(),role='premise',region=None))
# Tighten all revised citations to readable, actual source text; leave every accepted
# object and its citation bytes unchanged. Focused dimension citations remain focused.
for key in modified:
 x=Q[key]
 for cite in x['citations']:
  if not (key in ('W02-L09-P0316-Q03','W02-L09-P0316-Q04') and cite['physicalPage']==323):
   cite['evidenceText']=(ROOT/f'sources/text/lectures/page-{cite["physicalPage"]:04}.txt').read_text().strip()
# Scoped exact readability substitutions only in the already-versioned objects.
replacements={'Uis':'U is','Uthe':'U the','Cthe':'C the','Ais':'A is','whenn':'when n','ofJ':'of J','UseJ=':'Use J=','Rotateq_B':'Rotate q_B','suppliedRx':'supplied Rx','UseRx':'Use Rx','child−y':'child −y','local+zrate':'local +z rate','addv_parent':'add v_parent','90°rotation':'90° rotation','A6×6':'A 6×6','qdot 2':'q_dot,2','qdot 1':'q_dot,1'}
def polish(v):
 if isinstance(v,str):
  for a,b in replacements.items():v=v.replace(a,b)
  return v
 if isinstance(v,list):return [polish(i) for i in v]
 if isinstance(v,dict):return {k:polish(z) for k,z in v.items()}
 return v
for key in modified:
 x=Q[key]
 for field in ('stem','assumptions','solution'):x[field]=polish(x[field])
 for option in x['options']:option['text']=polish(option['text'])
# Keep concept examination-angle text synchronized with revised stems; no accepted
# question content is edited, and no author claims independent coverage completion.
for c in batch['concepts']:
 c['examinationAngles']=[Q[k]['stem'] for k in c['questionIds']]
# Existing inspection attribution and actual visual evidence remain untouched.
ins=json.loads((ROOT/'data/inspection-batches/W02-L09.json').read_text())
ins['sourceIssues']=copy.deepcopy(batch['sourceIssues']);ins['summary']['questions']=len(batch['questions']);ins['summary']['authorComplete']=True
(ROOT/'data/inspection-batches/W02-L09.json').write_text(json.dumps(ins,ensure_ascii=False,indent=2)+'\n')
save(False)
# Re-run the changed numerical workings and the new geometric premise exactly.
import numpy as np
import sympy as sp
def check(key,passed,detail,ids=None):
 author_checks.append({'id':key,'passed':bool(passed),'kind':'author_check_not_independent_review','detail':detail,'questionIds':ids or []})
 if not passed:raise AssertionError(key)
def ids(*s):return [BATCH+'-'+v for v in s]
Rz=sp.Matrix([[0,-1,0],[1,0,0],[0,0,1]]);Rm=Rz.T;Rx=sp.Matrix([[1,0,0],[0,0,-1],[0,1,0]])
check('speed-components',sp.sqrt(3**2+4**2+0**2)==5,'Nonnegative norm is5 m/s.',ids('P0299-Q02'))
check('translation-only-velocity',sp.Matrix([1,0,0])+Rz*sp.Matrix([2,0,0])==sp.Matrix([1,2,0]),'Constant R gives omega=0; rotate relative velocity then add origin velocity.',ids('P0306-Q02'))
transport=sp.Matrix([1,0,0])+Rz*sp.Matrix([1,0,0])+sp.Matrix([0,0,2]).cross(Rz*sp.Matrix([2,0,0]))
check('full-velocity-transport',transport==sp.Matrix([-3,1,0]),str(transport),ids('P0310-Q02'))
check('revolute-angular-rotation',Rx*sp.Matrix([0,0,2])+sp.Matrix([0,0,3])==sp.Matrix([0,-2,3]),'Parent-to-child rotation precedes child-local rate addition.',ids('P0312-Q05'))
vparent=sp.Matrix([1,2,0]);omega=sp.Matrix([0,0,2]);P=sp.Matrix([3,0,0]);inherit=vparent+omega.cross(P)
check('revolute-linear-parent',inherit==sp.Matrix([1,8,0]),str(inherit),ids('P0313-Q03'))
check('revolute-linear-child',Rm*inherit==sp.Matrix([8,-1,0]),str(Rm*inherit),ids('P0313-Q04'))
check('prismatic-child-rate',Rm*inherit+sp.Matrix([0,0,4])==sp.Matrix([8,-1,4]),'d_dot is the first derivative with units m/s.',ids('P0314-Q03'))
check('mixed-chain-instant',sp.eye(3)*omega==sp.Matrix([0,0,2]) and sp.zeros(3,1)+omega.cross(sp.zeros(3,1))+sp.Matrix([0,0,3])==sp.Matrix([0,0,3]),'R=I,P=0,v_parent=0; inherit angular velocity and add linear extension.',ids('P0314-Q04'))
a,b=sp.symbols('a b',real=True);F=sp.Matrix([a*a+b,a*b]);J=F.jacobian([a,b]).subs({a:2,b:3});vel=J*sp.Matrix([sp.Rational(1,2),-1])
check('explicit-map-rate',J==sp.Matrix([[4,1],[3,2]]) and vel==sp.Matrix([1,sp.Rational(-1,2)]),str(vel),ids('P0315-Q04'))
check('twist-block-rotation',Rz*sp.Matrix([1,0,0])==sp.Matrix([0,1,0]) and Rz*sp.Matrix([0,1,0])==sp.Matrix([-1,0,0]),'Same rotation applied to both blocks, preserving point and reference observer.',ids('P0318-Q03'))
rate=sp.diag(2,1).inv()*sp.Matrix([sp.Rational(2,5),-sp.Rational(1,5)]);nxt=sp.Matrix([1,2])+sp.Rational(1,10)*rate
check('Euler-update',nxt==sp.Matrix([sp.Rational(51,50),sp.Rational(99,50)]),'Rate=(.2,−.2)/s; next=(1.02,1.98).',ids('P0321-Q03'))
Jsing=sp.diag(1,0)
check('singular-target-compatibility',Jsing*sp.Matrix([2,0])==sp.Matrix([2,0]) and Jsing.row_join(sp.Matrix([0,1])).rank()>Jsing.rank(),'Finite compatible target; inconsistent incompatible target.',ids('P0319-Q06'))
eps=sp.symbols('eps',positive=True)
check('near-singular-directional-limit',sp.diag(1,eps).inv()*sp.Matrix([2,0])==sp.Matrix([2,0]) and sp.limit(1/eps,eps,0,dir='+')==sp.oo,'Only the selected weak-direction rate diverges; an orthogonal target remains bounded.',ids('P0319-Q06'))
check('redundant-nullspace-rate',sp.Matrix([[1,1]])*sp.Matrix([1,-1])==sp.zeros(1,1),'A null-space joint RATE gives zero instantaneous task velocity, not a finite pose guarantee.',ids('P0322-Q05'))
r,theta,delta=sp.symbols('r theta delta',positive=True)
O=sp.zeros(3,1);A=sp.Matrix([0,0,r*sp.cos(theta)]);B=sp.Matrix([r*sp.sin(theta),0,r*sp.cos(theta)]);C=sp.Matrix([r*sp.sin(theta)*sp.cos(delta),r*sp.sin(theta)*sp.sin(delta),r*sp.cos(theta)])
check('figure-label-geometry',sp.trigsimp((B-A).dot(B-A)-(r*sp.sin(theta))**2)==0 and sp.trigsimp((C-A).dot(C-A)-(r*sp.sin(theta))**2)==0 and sp.trigsimp(B.dot(B)-r*r)==0 and sp.trigsimp(C.dot(C)-r*r)==0,'OA is axial projection; AB=AC are radius; OB=OC are full length.',ids('P0309-Q08'))
check('finite-chord-small-angle',sp.trigsimp((C-B).dot(C-B)-4*r*r*sp.sin(theta)**2*sp.sin(delta/2)**2)==0 and sp.limit(2*sp.sin(delta/2)/delta,delta,0)==1,'BC is a chord; its ratio to the arc tends to1 for small angle.',ids('P0309-Q08'))
check('accepted-objects-unchanged',all(Q[k]==oldQ[k] and digest(Q[k])==h for k,h in accepted.items()),'All54 accepted objects remain exactly equal to the archived v1 objects and their independent review hashes.')
check('flagged-only-old-object-repairs',modified==flags and all(Q[k]['version']==2 for k in flags),'Exactly the48 flagged original IDs are revised; no other original question is edited.')
check('keys-preserved',all(Q[k]['correctOptionIds']==oldQ[k]['correctOptionIds'] for k in oldQ),'All102 original answer sets are preserved; quality repairs do not assert a new independent answer review.')
check('conflicts-version-bound',all(x.get('conflictResolution',{}).get('questionVersion')==2 for x in batch['questions'] if x['id'] in flags and any(c['role']=='conflict' for c in x['citations'])),'Every revised conflicting citation has a question-version2 resolution proposal.')
# Every review finding is explicitly tracked by the revised object and its new hash.
for key in flags:
 Q[key]['revisionAuthors']=list(dict.fromkeys(Q[key].get('revisionAuthors',[])+[AUTHOR]))
batch['authorChecksV2']=author_checks
if __name__=='__main__':save(True)
