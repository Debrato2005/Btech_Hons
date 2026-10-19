"""One-time L25 quality revisions and two source-linked synthesis gaps."""
from pathlib import Path
import json,copy,hashlib,datetime
import numpy as np
from authoring_helpers import DraftBatch,formula
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W05-L25.json';old=json.loads(p.read_text());summary=json.loads((R/'audits/W05-L25-contracts-review-summary.json').read_text());nums={int(x[-3:])for x in summary['flaggedQuestionIds']}
b=DraftBatch('W05-L25',5,'L25',old['questions'][0]['topic'],751,'robotics-integration-author-L25-repairs');b.questions=copy.deepcopy(old['questions']);b.concepts={c['id']:copy.deepcopy(c)for c in old['concepts']};qs={int(q['id'][-3:]):q for q in b.questions}
h=lambda q:hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in['status','reviewIds']},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();keep={q['id']:h(q)for q in old['questions']if int(q['id'][-3:])not in nums};assert len(nums)==20 and all(qs[n]['version']==1 for n in nums)
a=R/'audits/batch-history/W05-L25-before-quality-repairs.json';assert not a.exists();a.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
def options(n,texts,reasons):
 for o in qs[n]['options']:o['text']=texts[int(o['id'][1:])-1]
 qs[n]['solution']['optionExplanations']=dict(zip(['o1','o2','o3','o4'],reasons))
def oneopt(n,i,text,reason):
 next(o for o in qs[n]['options']if o['id']==f'o{i}')['text']=text;qs[n]['solution']['optionExplanations'][f'o{i}']=reason
options(3,[
 'It fully specifies a normalized acceleration law with unit gains for every derivative channel.',
 'It specifies a position-only controller, so the desired velocity and acceleration inputs can be discarded.',
 'It abbreviates joint-reference and error processing; position, velocity and acceleration need appropriately defined channels and gains.',
 'It defines the angular displacement δθ=θ_d+θ̇_d+θ̈_d−θ without any scaling.'],[
 'The drawing does not specify those numerical gains or a complete normalized servo law.',
 'A single abbreviated return arrow does not justify discarding the other labeled reference channels.',
 'This preserves the architecture without treating quantities with unlike units as a literal unweighted sum.',
 'Position, velocity and acceleration cannot be added directly to produce an angular displacement.'])
oneopt(4,1,'Apply one local Jacobian inverse directly to the finite Cartesian target without a reference configuration or iterative update.','A Jacobian inverse converts local derivatives or increments; it is not generally a global inverse of finite forward kinematics.')
qs[12]['solution']['formulas']=[formula('δX=X_d−X',{'δX':'desired-minus-actual Cartesian position error','X_d':'desired Cartesian position','X':'actual Cartesian position obtained from measured joint coordinates'},{'δX,X_d,X':'m'},['All position vectors use the same frame and reference origin.'])]
oneopt(13,4,'Both architectures convert only the desired path outside feedback and then compare desired and actual joint coordinates.','That describes joint-error tracking, not the direct diagram that computes Cartesian feedback from measured joints.')
options(14,[
 'Specifying the task in Cartesian coordinates removes the need for current forward kinematics in direct Cartesian feedback.',
 'A fixed joint-angle error then corresponds to the same Cartesian position error at every arm configuration.',
 'Direct Cartesian error control avoids feedback-coordinate conversion by treating measured joint angles as Cartesian positions.',
 'Workspace tasks can be specified naturally, while tracking quality still depends on controller design and implementation.'],[
 'Direct Cartesian feedback still needs a map from measured joints to actual task coordinates.',
 'The relation between joint and Cartesian changes depends on the configuration-dependent Jacobian.',
 'Joint angles are not the same quantities as Cartesian positions.',
 'This retains the useful task-space specification without assuming perfect tracking.'])
for n in [23,31,35,37,44]:qs[n]['difficulty']='easy'
options(27,[
 'M_x: Cartesian inertia; V_x: gravity terms; G_x: velocity-dependent terms.',
 'M_x: velocity-dependent coefficient matrix; V_x: inertial acceleration force; G_x: gravity terms.',
 'M_x: Cartesian inertia; V_x: velocity-dependent terms; G_x: gravity terms.',
 'M_x: the joint-space inertia used unchanged; V_x and G_x: the joint-space torque vectors used unchanged.'],[
 'This swaps the velocity and gravity roles.',
 'The displayed acceleration coefficient is M_x, while V_x contains the velocity-dependent force terms.',
 'This matches the term definitions in the Cartesian plant equation.',
 'Cartesian and joint-space representations generally require coordinate-dependent transformation, not unchanged terms.'])
qs[27]['solution']['formulas']=[formula('ℱ=M_x(Θ)χ̈+V_x(Θ,Θ̇)+G_x(Θ)',{'ℱ':'Cartesian generalized force vector','M_x':'Cartesian inertia matrix','χ':'task position and declared orientation coordinates','V_x':'velocity-dependent generalized force','G_x':'gravity generalized force','Θ,Θ̇':'joint configuration and velocity'},{'ℱ,V_x,G_x':'N for force components and N·m for moment components','χ':'m for position coordinates and rad for declared angular coordinates','M_x':'component-dependent units mapping task acceleration to generalized force'},['Use consistent locally valid task coordinates and a work-conjugate force representation; orientation coordinates require the stated coordinate convention.'])]
options(29,[
 'Uppercase X,Y,Z mark base axes at O; lowercase x,y,z appear at P, and the dashed sphere is schematic.',
 'The dashed sphere provides enough numerical data to calculate the exact reachable-workspace volume.',
 'The lowercase axes are drawn at the base origin O, while the uppercase axes move with the tool point P.',
 'The picture alone gives the complete numerical rotation and translation between the base and tool frames.'],[
 'This reports the visible labels and avoids inferring an exact workspace from the illustration.',
 'No sphere radius or exact reachable-set specification is supplied.',
 'This reverses the visible locations of the two sets of axes.',
 'The schematic does not provide the numerical pose data needed for that complete transform.'])
plant=formula('F=M_x Ẍ+V_x+G_x',{'F':'Cartesian force vector','M_x':'Cartesian inertia matrix','Ẍ':'actual Cartesian acceleration','V_x':'velocity-dependent Cartesian force','G_x':'gravity Cartesian force'},{'F,V_x,G_x':'N','M_x':'kg','Ẍ':'m/s²'},['Translation-only task with all components in a common compatible frame.'])
command=formula('F_cmd=M_x u+V_x+G_x',{'F_cmd':'commanded Cartesian force','M_x':'Cartesian inertia matrix','u':'normalized servo acceleration command','V_x,G_x':'velocity-dependent and gravity force compensation'},{'F_cmd,V_x,G_x':'N','M_x':'kg','u':'m/s²'},['Translation-only task with compatible coordinates and frame.'])
qs[30]['solution']['formulas']=[copy.deepcopy(plant)]
qs[31]['solution']['formulas']=[copy.deepcopy(plant),copy.deepcopy(command),formula('M_x(Ẍ−u)=0 ⇒ Ẍ=u',{'M_x':'matched invertible Cartesian inertia','Ẍ':'actual task acceleration','u':'normalized acceleration command'},{'M_x':'kg','Ẍ,u':'m/s²'},['The same force is realized in the plant and controller, all model terms match, and no additional force is present.'])]
qs[32]['solution']['formulas']=[copy.deepcopy(command)]
qs[38]['solution']['formulas']=[formula('X=Kin(θ); Ẋ=J(θ)θ̇',{'X':'actual task position','Kin':'forward position map','θ':'measured joint configuration','J':'position Jacobian evaluated at the measured configuration','θ̇':'measured joint angular velocity','Ẋ':'actual task velocity'},{'X':'m','θ':'rad for revolute joints','J':'m/rad','θ̇':'rad/s','Ẋ':'m/s'},['Translation-only task with differentiable forward kinematics; these forward relations do not require a square or nonsingular Jacobian.'])]
force_map=formula('τ=J^T F; Ẋ=Jθ̇',{'τ':'joint torque','J':'position Jacobian at the actual configuration','F':'Cartesian force at the point represented by J','Ẋ':'velocity of that point','θ̇':'joint angular velocity'},{'τ':'N·m','J':'m/rad','F':'N','Ẋ':'m/s','θ̇':'rad/s'},['Translation-only task with revolute joints; force and velocity use the same point and frame, with radians dimensionless in virtual work.'])
qs[39]['solution']['formulas']=[copy.deepcopy(command),copy.deepcopy(force_map)]
oneopt(41,4,'Multiply the tool-frame force by the base-to-tool rotation and treat the result as a base-frame force.','That uses the rotation in the wrong direction; a tool-frame vector needs the tool-to-base transformation to match this Jacobian.')
qs[41]['solution']['formulas']=[copy.deepcopy(force_map)]
oneopt(44,1,'The held model coefficients remain within the chosen modeling-error budget throughout the update interval.','That supports the intended slow-update approximation rather than violating it.')
options(47,[
 'The added transformations are only offline trajectory preparation, so they impose no real-time feedback computation.',
 'Choosing a high nominal update rate is sufficient; the actual computation deadline can be assessed separately from controller behavior.',
 'Well-designed Cartesian model-based control can improve workspace response, but requires model computation and coordinate transformations.',
 'Cartesian model compensation makes tracking insensitive to parameter errors that would matter in joint-based model compensation.'],[
 'The architecture places coordinate and model calculations within feedback, even if some run at a slower rate.',
 'Missed computation deadlines and delay can affect the implemented feedback, not just its nominal rate.',
 'This retains both the stated intended benefit and implementation cost.',
 'Changing coordinates does not remove the dependence of exact cancellation on an accurate model.'])
options(50,[
 'τ′ is already physical torque, so the dynamic-model block only performs a dimensionless change of labels.',
 'τ′ is applied directly to the arm, while the dynamic-model block only stores parameter estimates outside the torque path.',
 'The model should add physical gravity torque directly to τ′ before any inertia scaling, treating their units as identical.',
 'τ′ is the normalized servo input; the dynamic-model block scales and compensates it to produce actuator torque τ.'],[
 'The acceleration-like servo input requires physical model scaling and compensation to become torque.',
 'The diagram puts the dynamic-model block between τ′ and the arm torque input.',
 'Acceleration-like input and physical torque cannot be added without the required model conversion.',
 'This distinguishes the normalized servo signal from the physical actuator command.'])
options(51,[
 'A bounded tracking error is sufficient by itself to conclude that every unknown physical parameter has been identified exactly.',
 'The presence of measured position and velocity feedback establishes all excitation and identifiability conditions without further analysis.',
 'Online model updates address uncertainty, but stability or parameter-convergence claims need a specified update law and assumptions.',
 'The block diagram determines a unique numerical parameter-update equation even though no such equation is shown.'],[
 'Tracking behavior alone does not establish that all unknown parameters have been identified.',
 'Available measurements do not by themselves establish the trajectory and model conditions needed for identification.',
 'The lecture provides the architecture, not a complete update law or convergence proof.',
 'Many different update laws could be placed in the adaptation block; the diagram does not specify one.'])
for n in nums:
 q=qs[n];q['version']=2;q['status']='draft';q['reviewIds']=[];q['revisionAuthors']=['robotics-integration-author-L25-repairs'];q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']]for o in q['options']if o['id']not in q['correctOptionIds']]
# Two distinct synthesis gaps requested by the independent coverage challenge.
b.add([763,764,765],'full-cartesian-command-chain','Combine feedback, coupled dynamics and torque mapping',
 'At one instant, X_d=[1,2]ᵀ m, X=[0.5,2.5]ᵀ m, Ẋ_d=[0.8,−0.2]ᵀ m/s, Ẋ=[0.3,0.3]ᵀ m/s and Ẍ_d=[1,2]ᵀ m/s². With K_p=diag(4,6) s⁻², K_v=diag(2,4) s⁻¹, M_x=[[2,1],[1,3]] kg, V_x+G_x=[1,2]ᵀ N and J=[[1,2],[0,1]] m/rad, what torque follows from u=Ẍ_d+K_v(Ẋ_d−Ẋ)+K_p(X_d−X), F=M_xu+V_x+G_x and τ=J^TF?',
 ['[6,9]ᵀ N·m','[2,−6]ᵀ N·m','[9,11]ᵀ N·m','[0,−3]ᵀ N·m'],0,
 'Position and velocity errors are both [0.5,−0.5]ᵀ; therefore u=[4,−3]ᵀ, the compensated force is [6,−3]ᵀ and the joint torque is [6,9]ᵀ.',
 ['This includes feedforward, both feedback terms, coupled inertia, compensation and the transpose map.',
 'This omits desired-acceleration feedforward, yielding u=[3,−5]ᵀ and F=[2,−10]ᵀ.',
 'This drops the off-diagonal inertia terms, yielding F=[9,−7]ᵀ.',
 'This incorrectly multiplies the correct force by J instead of J^T.'],typ='numerical',difficulty='hard',
 assumptions=['This is an explicitly supplied translation-only instantaneous example with two revolute actuators, compatible frames and no saturation.','The desired-minus-actual error convention is used; the Jacobian and dynamics correspond to the actual configuration.'],
 steps=['Subtract actual from desired position and velocity to obtain E=Ė=[0.5,−0.5]ᵀ in their respective units.','Compute K_pE=[2,−3]ᵀ and K_vĖ=[1,−2]ᵀ m/s².','Add desired acceleration to obtain u=[4,−3]ᵀ m/s².','Compute M_xu=[5,−5]ᵀ N and add compensation to obtain F=[6,−3]ᵀ N.','Apply J^T=[[1,0],[2,1]] to obtain τ=[6,9]ᵀ N·m.'],
 formulas=[formula('E=X_d−X; Ė=Ẋ_d−Ẋ; u=Ẍ_d+K_vĖ+K_pE',{'E':'position error','Ė':'velocity error','X,X_d':'actual and desired task position','u':'normalized task acceleration command','K_v,K_p':'velocity and position gains','dot and double dot':'time derivatives'},{'X,X_d,E':'m','Ė':'m/s','u,Ẍ_d':'m/s²','K_v':'s⁻¹','K_p':'s⁻²'}),copy.deepcopy(command),copy.deepcopy(force_map)])
b.add(756,'coupled-reference-acceleration','Preserve matrix order in acceleration conversion',
 'On a smooth desired inverse-kinematics branch, let J=[[1,2],[0,1]] m/rad and its total time derivative J̇=[[0,1],[1,0]] m/(rad·s). For Ẋ_d=[3,1]ᵀ m/s and Ẍ_d=[2,4]ᵀ m/s², what desired joint acceleration follows from Ẋ_d=Jθ̇_d and Ẍ_d=Jθ̈_d+J̇θ̇_d?',
 ['[−5,3]ᵀ rad/s²','[−6,4]ᵀ rad/s²','[−7,5]ᵀ rad/s²','[5,1]ᵀ rad/s²'],0,
 'First solve θ̇_d=J⁻¹Ẋ_d=[1,1]ᵀ, so J̇θ̇_d=[1,1]ᵀ; then θ̈_d=J⁻¹[1,3]ᵀ=[−5,3]ᵀ.',
 ['This retains the velocity-dependent term and the correct matrix order.',
 'This omits J̇θ̇_d and uses only J⁻¹Ẍ_d.',
 'This adds J̇θ̇_d instead of subtracting it before applying J⁻¹.',
 'This uses −J⁻²J̇Ẋ_d instead of −J⁻¹J̇J⁻¹Ẋ_d; the matrices do not commute.'],typ='numerical',difficulty='hard',
 assumptions=['The 2×2 Jacobian is nonsingular at this instant, and all task vectors use the same translation frame.','J and J̇ are evaluated along the selected desired branch; J̇ is supplied as the total derivative along that branch, not a matrix inverse of a derivative.'],
 steps=['Compute J⁻¹=[[1,−2],[0,1]] rad/m.','Compute θ̇_d=J⁻¹[3,1]ᵀ=[1,1]ᵀ rad/s.','Compute J̇θ̇_d=[1,1]ᵀ m/s².','Subtract this term from Ẍ_d to obtain [1,3]ᵀ m/s².','Left-multiply by J⁻¹ to obtain [−5,3]ᵀ rad/s².'],
 formulas=[formula('θ̇_d=J⁻¹Ẋ_d; θ̈_d=J⁻¹(Ẍ_d−J̇θ̇_d); d(J⁻¹)/dt=−J⁻¹J̇J⁻¹',{'θ̇_d,θ̈_d':'desired joint velocity and acceleration','Ẋ_d,Ẍ_d':'desired task velocity and acceleration','J':'Jacobian on the desired branch','J̇':'total derivative along that branch'},{'θ̇_d':'rad/s','θ̈_d':'rad/s²','Ẋ_d':'m/s','Ẍ_d':'m/s²','J':'m/rad','J̇':'m/(rad·s)'},['Smooth desired branch, square nonsingular Jacobian and compatible task coordinates.'])])
b.save();assert all(h(next(q for q in b.questions if q['id']==k))==v for k,v in keep.items())
ids={qs[n]['id']for n in nums}|{'W05-L25-Q053','W05-L25-Q054'};full=json.loads((R/'audits/blind-W05-L25.json').read_text());fp=R/'audits/blind-W05-L25-v2-quality-repairs.json';fp.write_text(json.dumps([q for q in full if q['id']in ids],ensure_ascii=False,indent=2)+'\n')
M=np.array([[2.,1.],[1.,3.]]);J=np.array([[1.,2.],[0.,1.]]);D=np.array([[0.,1.],[1.,0.]]);beta=np.array([1.,2.]);A=np.linalg.inv(J);e=np.array([.5,-.5]);u=np.array([1.,2.])+np.diag([2.,4.])@e+np.diag([4.,6.])@e;F=M@u+beta
checks={'command':np.allclose(J.T@F,[6,9]),'omit_feedforward':np.allclose(J.T@(M@(u-[1,2])+beta),[2,-6]),'drop_coupling':np.allclose(J.T@(np.diag(np.diag(M))@u+beta),[9,11]),'wrong_transpose':np.allclose(J@F,[0,-3]),'joint_velocity':np.allclose(A@[3,1],[1,1]),'joint_acceleration':np.allclose(A@(np.array([2,4])-D@(A@[3,1])),[-5,3]),'omit_derivative':np.allclose(A@[2,4],[-6,4]),'wrong_sign':np.allclose(A@(np.array([2,4])+D@(A@[3,1])),[-7,5]),'wrong_order':np.allclose(A@[2,4]-A@A@D@[3,1],[5,1]),'noncommuting':not np.allclose(A@D,D@A)};assert all(checks.values())
(R/'audits/W05-L25-v2-author-checks.json').write_text(json.dumps({'checks':checks,'passed':len(checks),'independentReview':False},indent=2)+'\n')
hashes={q['id']:h(q)for q in b.questions if q['id']in ids};(R/'audits/W05-L25-v2-quality-repairs-question-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
manifest={'batchId':'W05-L25','updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'changedQuestionIds':sorted(ids),'acceptedHashesPreserved':keep,'packetSha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'authorChecksPassed':len(checks),'notes':['20 revisions address the frozen quality review without changing any correct option IDs.','32 approved objects remain hash-identical.','Two distinct coupled synthesis gaps were added.','Formula records are narrowed to cited premises and the tested controller, rather than recycling unrelated controller laws.','Source qualifications are retained, not globally resolved.'],'review':'Pending independent review with prior exposure disclosed.'};(R/'audits/W05-L25-v2-quality-repair-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(manifest['packetSha256'])
