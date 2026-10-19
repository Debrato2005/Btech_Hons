#!/usr/bin/env python3
"""L25 source-inspected author proposal, not independent verification."""
import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from authoring_helpers import DraftBatch,formula,SHA
from validate import schema_errors,question_hash
AUTHOR='build_offline_study_interface:L25-author';BATCH='W05-L25'
b=DraftBatch(BATCH,5,'L25','Cartesian-based control systems and examples',751,AUTHOR)
INSPECTED_AT='2026-10-19T18:36:19+00:00'
NOTES={
751:('Lecture 25 title, Cartesian-Based Control Systems and Examples; institution and author. Footer 1.','Title and attribution only.'),
752:('Objectives: understand and implement Cartesian-based control. Footer 2.','Learning-outcome roadmap only.'),
753:('Contents: comparison, intuitive Cartesian schemes, Cartesian decoupling and adaptive control. Footer 3.','Contents roadmap only.'),
754:('Joint-based errors concern joint coordinates and derivatives; workspace tasks motivate Cartesian trajectories, including straight lines. Footer 4.',None),
755:('Cartesian-path input X_d and two derivatives enter trajectory conversion, which outputs desired joint position and derivatives. Feedback in the shown joint-based loop remains joint position; gains output torque. The common summing icon compresses several signals of different units and is not a literal dimensionally valid unweighted sum. X=[x y z]^T is position-only here. Footer 5.',None),
756:('Inverse kinematics gives desired joint position; desired velocity J^-1 times desired Cartesian velocity; acceleration uses product rule J^-1 times desired acceleration plus time derivative of J^-1 times desired velocity. The printed J(Θ) does not explicitly say Θ_d: a derivative-consistent reference conversion must evaluate along the selected desired branch. Ordinary inversion requires square nonsingular J; derivative is of the inverse, not inverse of derivative. Cost, noise amplification and delay are listed. Footer 6.',None),
757:('Direct Cartesian feedback forms δX=X_d−X, obtains X from Kin(θ), maps Cartesian error to torque and drives arm. Bottom arrow returns θ through forward kinematics to the negative comparator port. Footer 7.',None),
758:('Workspace specification/direct end-effector motion and straight-line tracking are benefits; transformations/Jacobian calculations inside the loop increase load. Benefits are not automatic perfect tracking or universal cost rankings. Footer 8.',None),
759:('Intuitive inverse-Jacobian and transpose-Jacobian methods both seek to reduce Cartesian error and produce joint torque, but their intermediate quantities differ. Footer 9.',None),
760:('Inverse-Jacobian diagram: δX→J^-1→δθ→gains→τ→arm, with forward-kinematics return. δθ=J^-1δX and τ=Kδθ. Local displacement approximation, square nonsingular Jacobian and suitable dynamics/gains are unstated scope limits. Footer 10.',None),
761:('Transpose-Jacobian diagram: δX→gains→virtual Cartesian force F→J^T→τ→arm. F=KδX,τ=J^TF. J^T is a force mapping, not generally an inverse displacement mapping. Same frame and work-conjugate coordinates are required. Footer 11.',None),
762:('Cartesian decoupling target: configuration-independent uniform task tracking, fixed closed-loop dynamics, decoupled and critically damped error channels. These are design goals under model/regularity/gain conditions. Footer 12.',None),
763:('Cartesian dynamics ℱ=M_x(Θ)χ̈+V_x(Θ,Θ̇)+G_x(Θ). χ includes position and orientation, ℱ force/moment. Diagram distinguishes base uppercase XYZ at O and endpoint lowercase xyz at P(x,y,z); schematic sphere is not a computed exact workspace boundary. Coordinate-rate/wrench conjugacy and local orientation coordinates are not specified. Footer 13.',None),
764:('Model-based command ℱ=M_xℱ′+V_x+G_x; ℱ′ servo component has acceleration units in a translation-only task. Joint actuators realize command through torque rather than directly applying an independent endpoint force. Exact matching and nonsingular inertia are required for cancellation. Footer 14.',None),
765:('τ=J^Tℱ and ℱ′=χ̈_d+K_v Ė+K_p E. Actual θ feeds Kin and configuration-dependent matrices; θ̇ enters J to obtain Cartesian velocity and enters velocity compensation. Desired-minus-actual comparisons feed positive gains; compensation adds after M_x and before J^T. Footer 15.',None),
766:('Same model-based diagram repeated with architecture explanation. Forward kinematics, Jacobian velocity conversion, model compensation, transpose map and arm all lie inside loop. No new equation beyond page765; incremental text explicitly locates coordinate conversion. Footer 16.',None),
767:('Dual-rate: fast servo, slower background configuration-dependent model updates when variation permits. Diagram separates G(θ) and B_x(θ)+C_x(θ); actual θ̇ still enters the lower block, so the abbreviated label must not erase velocity dependence established on page763. B_x/C_x are not separately defined here. Footer 17.',None),
768:('Same practical diagram, now benefit/implementation-cost comparison. Claimed disturbance rejection and improved tracking are intended achievable benefits, not unconditional guarantees with arbitrary delay or model mismatch. Footer 18.',None),
769:('Adaptive control motivation: uncertain/changing payload, friction, wear, inertia and center of mass cause model mismatch and lost exact cancellation. Diagram is joint-coordinate θ not Cartesian χ: desired acceleration plus K_v Ė+K_p E yields τ′, dynamic model outputs τ. Adaptation receives E,Ė,θ,θ̇ and changes model. Footer 19.',None),
770:('Same adaptive diagram; online parameter estimation updates model during operation. Structure: servo law, dynamic model, adaptation mechanism. No specific update equation, learning rate, stability proof or convergence conditions supplied, so do not invent a source algorithm or guarantee exact identification. Footer 20.',None),
771:('Summary of conversions, intuitive schemes, Cartesian dynamics/transpose torque mapping, practical cost and adaptation. No new mathematical premise; share existing concept questions. Footer 21.',None),
772:('Craig 2004 third-edition bibliographic entry. Footer 22.','Reference only; referenced textbook contents are not present here.'),
773:('Thank-you closing. Footer 23.','Closing only.')}
ISSUES=[
(755,'Joint desired position, velocity and acceleration arrows share one summing icon although the output is labeled δθ.','Treat the picture as a compressed architecture, not an instruction to add unlike units without separate error/gain channels.'),
(756,'Reference-conversion Jacobian is printed at Θ, not explicitly Θ_d; inverse and inverse-derivative regularity are not stated.','For derivatives of a chosen desired IK branch use J(Θ_d) and its derivative along that branch, with square nonsingular differentiable J.'),
(760,'δθ=J^-1δX is displayed without a local-displacement or invertibility qualification.','Use a local linearization and a square nonsingular Jacobian; do not claim exact finite nonlinear IK or global convergence.'),
(762,'Configuration-independent critically damped decoupling is a goal without all implementation hypotheses.','Require accurate compensation, nonsingular task inertia, suitable diagonal gains, coordinate regularity and feasible actuation.'),
(763,'Position/orientation coordinates and physical force/moment are named without specifying an orientation-rate representation or conjugate wrench convention.','Use translation-only examples or explicitly work-conjugate generalized coordinates and forces; do not equate arbitrary Euler-angle rates with angular velocity.'),
(767,'The practical diagram writes B_x(θ)+C_x(θ) while feeding actual θ̇ into that block; slow-variation prose is conditional.','Preserve velocity dependence and restrict slow coefficient updates to adequately slowly varying configurations; no rate value is supplied.'),
(768,'Improved disturbance rejection and tracking are listed without a comparator or quantified universal bound.','Treat as potential benefits of a well-designed accurate implementation, not a proof of superiority for arbitrary mismatch/delay.'),
(770,'Online learning/reduced tracking-error prose gives no adaptation equation or stability/convergence conditions.','Describe the architecture and purpose only; no universal monotonic improvement or guaranteed parameter identification is claimed.')]
def add(p,key,title,stem,opts,why,**kw):
 correct=list(kw.pop('correct',(0,)));k=len(b.questions)%4;opts=opts[k:]+opts[:k];correct=[(i-k)%4 for i in correct]
 conflict_pages=kw.pop('conflict_pages',None)
 q=b.add(p,key,title,stem,[o[0] for o in opts],correct,why,[o[1] for o in opts],**kw);q['options'].sort(key=lambda o:o['id'])
 for c in q['citations']:c['locator']=f"Lecture 25, physical PDF page {c['physicalPage']}, actual printed footer {c['physicalPage']-750}: {title}"
 if q.get('conflictResolution'):
  pages=conflict_pages or ([p] if isinstance(p,int) else p);q['conflictResolution'].update(sourceId='lectures',sourceSha256=SHA,physicalPages=pages)
  for c in q['citations']:c['role']='conflict' if c['physicalPage'] in pages else 'premise'
 return q

def save(frozen=False):
 b.save();path=R/f'data/question-batches/{BATCH}.json';data=json.loads(path.read_text());data['sourceIssues']=[{'physicalPage':p,'description':d,'qualification':q,'status':'preserved with explicit scope; not globally resolved'} for p,d,q in ISSUES];data['coverageNote']='All 23 source pages visually inspected; author coverage proposal requires independent source-based answer and substantive coverage review.';path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 maps={s['physicalPage']:s for s in map(json.loads,(R/'sources/page_maps/lectures.jsonl').read_text().splitlines())};slides=[]
 for p,(note,excluded) in NOTES.items():
  s=copy.deepcopy(maps[p]);s['disposition']='excluded' if excluded else 'examinable';s['exclusionReason']=excluded;s['conceptIds']=[c['id'] for c in b.concepts.values() if s['id'] in c['slideIds']]
  s['printedSlideNumber']=str(p-750);s['printedSlideNumberStatus']='present';s['printedNumberEvidence']='Actual bottom-right footer visually inspected independently; physical page is retained separately.'
  s['visualInspection']={'status':'complete','inspectorId':AUTHOR,'inspectedAt':INSPECTED_AT,'method':'rendered_page','notes':note+' Actual readable 1800×1013 page pixels and extracted text inspected. Diagrams on pages 755,765,767,769 additionally rendered at 4× PDF scale.','previewSha256':hashlib.sha256((R/s['previewPath']).read_bytes()).hexdigest(),'dimensions':[1800,1013]};slides.append(s)
 for typ,rows in [('question',b.questions),('concept',list(b.concepts.values())),('slide',slides)]:
  schema=json.loads((R/f'data/schema.{typ}.json').read_text());errors=[e for row in rows for e in schema_errors(row,schema)];assert not errors,(typ,errors)
 (R/f'data/inspection-batches/{BATCH}.json').write_text(json.dumps({'batchId':BATCH,'slides':slides},ensure_ascii=False,indent=2)+'\n')
 (R/f'audits/{BATCH}-author-progress.json').write_text(json.dumps({'frozen':frozen,'authorId':AUTHOR,'questionCount':len(b.questions),'conceptCount':len(b.concepts),'inspectedPages':list(NOTES),'sourceCodeStatus':'No executable code, pseudocode, numerical table or simulation trace printed in this lecture; author checks are explicitly new computations from source equations.','next':'Independent answer and coverage review required.' if frozen else 'Continue drafting distinct source-grounded angles.'},indent=2)+'\n')
 print('Saved',len(b.questions),'L25 drafts;',len(b.concepts),'concepts;',len(slides),'page inspections; frozen=',frozen)
save()

KIN=formula('Ẋ=J(θ)θ̇; θ̇_d=A Ẋ_d; θ̈_d=A Ẍ_d+Ȧ Ẋ_d; A=J(θ_d)^−1',{'X':'task-position vector','X_d':'desired task position','θ':'joint-position vector','θ_d':'selected desired IK branch','J':'task-position Jacobian','A':'Jacobian inverse evaluated on the desired branch','Ȧ':'time derivative of that inverse along the desired branch'},{'X,X_d':'m','θ,θ_d':'rad for revolute joints','J':'m/rad','A':'rad/m','Ȧ':'rad/(m·s)','Ẋ_d':'m/s','Ẍ_d':'m/s²','θ̇_d':'rad/s','θ̈_d':'rad/s²'},['Translation-only task; smooth desired IK branch and square nonsingular J.'])
INV=formula('δθ≈J^−1δX; τ=K_q δθ',{'δX':'desired-minus-actual Cartesian position error','δθ':'local joint-position correction','J':'position Jacobian at current configuration','K_q':'joint-space proportional torque gain matrix','τ':'joint torque'},{'δX':'m','δθ':'rad','J':'m/rad','K_q':'N·m/rad','τ':'N·m'},['Revolute joints, translation-only task, small displacement, square nonsingular J; gain dimensions match joint coordinates.'])
TRANS=formula('F=K_x δX; τ=J^T F; Ẋ=Jθ̇',{'F':'virtual Cartesian force expressed in the Jacobian task frame','K_x':'Cartesian stiffness gain matrix','δX':'desired-minus-actual Cartesian position error in the same frame','τ':'joint torque','J':'position Jacobian','Ẋ':'Cartesian velocity','θ̇':'joint angular velocity'},{'F':'N','K_x':'N/m','δX':'m','J':'m/rad','τ':'N·m','Ẋ':'m/s','θ̇':'rad/s'},['Translation-only task and revolute joints; radians dimensionless in virtual work; compatible frames.'])
DYN=formula('F=M_x Ẍ+V_x+G_x; F_cmd=M_x u+V_x+G_x; u=Ẍ_d+K_v Ė+K_p E; E=X_d−X',{'F':'Cartesian generalized force acting through the model','F_cmd':'commanded Cartesian force','M_x':'Cartesian inertia matrix at actual configuration','V_x':'velocity-dependent Cartesian force vector','G_x':'gravity Cartesian force vector','u':'servo acceleration command (source ℱ′)','X':'actual task position','X_d':'desired task position','E':'desired-minus-actual error','K_v':'velocity-error gain matrix','K_p':'position-error gain matrix'},{'F,F_cmd,V_x,G_x':'N','M_x':'kg','u,Ẍ,Ẍ_d':'m/s²','X,X_d,E':'m','Ė':'m/s','K_v':'s^−1','K_p':'s^−2'},['Translation-only task; matching coordinates/frame, exact model and feasible actuation; invertible M_x for cancellation.'])
add(754,'task-motivation','Workspace task versus joint-coordinate regulation',
 'A manipulator must trace a straight seam specified by points in the workspace. What motivates Cartesian-based control in the lecture?',[
 ('The task is naturally expressed as an end-effector path in workspace coordinates.','Cartesian coordinates directly describe the required seam.'),
 ('A straight joint-angle interpolation necessarily produces a straight end-effector path.','The kinematic mapping is generally nonlinear, so these two path shapes need not coincide.'),
 ('A workspace path removes the need to account for manipulator kinematics.','Kinematic transformations still connect the task to joint measurements and actuators.'),
 ('Cartesian control changes joint torque actuators into independent x, y and z actuators.','The physical joint actuation remains; the controller changes the coordinates used for the task.')],
 'Workspace motion objectives, including straight-line paths, motivate expressing tracking errors in Cartesian coordinates rather than assuming joint interpolation has the desired geometric effect.',difficulty='easy',typ='scenario')
add(755,'joint-cartesian-input','Trajectory conversion before joint feedback',
 'In the joint-based diagram with Cartesian-path input, which sequence correctly describes the main forward path?',[
 ('Cartesian desired trajectory → joint trajectory conversion → joint-error/gain processing → torque → arm.','This preserves the shown conversion, feedback coordinates and actuator command.'),
 ('Cartesian desired trajectory → direct Cartesian-error gain → Cartesian force actuator, without joint conversion.','That omits the trajectory-conversion block and changes the shown actuation architecture.'),
 ('Measured joint position → inverse kinematics → Cartesian reference → torque.','Inverse kinematics maps a Cartesian target toward joint coordinates, not measured joint position toward a reference.'),
 ('Cartesian desired trajectory → forward kinematics → joint desired trajectory → arm position command.','Forward kinematics has the opposite coordinate direction, and the diagram drives the arm with torque.')],
 'A Cartesian input does not by itself make the feedback loop Cartesian. Here the reference is converted into joint quantities before the joint-based control path.',typ='sequence',difficulty='easy')
add(755,'joint-schematic-scope','Mixed-unit signals in a compressed block diagram',
 'The diagram sends θ_d, θ̇_d and θ̈_d toward a common summing icon labeled δθ. Which interpretation avoids treating that schematic as an invalid equation?',[
 ('It compresses joint-reference/error processing; position, velocity and acceleration require appropriately defined channels and gains.','The three quantities have different units and cannot simply be added unweighted as one angular displacement.'),
 ('It defines δθ=θ_d+θ̇_d+θ̈_d−θ with no unit conversion or gain scaling.','Angles, angular velocities and angular accelerations are not directly addable in that expression.'),
 ('Every dot is decorative, so all three arrows carry the same joint position.','The labels explicitly distinguish position and its time derivatives.'),
 ('The single return θ arrow proves that actual joint velocity equals θ̇_d at every instant.','A schematic omission is not an equality between actual and desired motion.')],
 'The architecture can be read faithfully without inventing a literal sum of unlike quantities. The printed common summing icon is an abbreviated drawing, not a complete implementable control equation.',typ='diagram',difficulty='medium',conflict='The printed joint-loop diagram places desired angle and both time derivatives at one summing icon whose output is labeled δθ.')
add([755,756],'inverse-kinematics','Desired joint position and branch choice',
 'Which operation produces a desired joint-position configuration from a reachable desired Cartesian pose before joint-based tracking?',[
 ('Solve inverse kinematics and select a suitable consistent solution branch.','The slide writes Θ_d=INVKIN(χ_d); a chosen branch supplies a joint trajectory.'),
 ('Multiply the desired position by the Jacobian transpose.','The transpose maps a compatible force to joint torque, not finite pose to joint configuration.'),
 ('Apply forward kinematics to the desired Cartesian pose.','Forward kinematics takes joint configuration as input.'),
 ('Integrate the Cartesian position once and call it joint angle.','Integration changes derivative order and does not perform inverse kinematics.')],
 'Inverse kinematics supplies desired joint positions. Jacobian relations handle local derivatives, not a universal finite-pose inverse.',difficulty='easy')
add(756,'desired-branch','Evaluation along the desired inverse-kinematics branch',
 'Let θ_d(t) be a smooth chosen IK branch satisfying X(θ_d(t))=X_d(t). Where must J be evaluated when differentiating this identity to obtain the exact desired joint velocity?',[
 ('At θ_d(t), along that same desired branch.','The chain rule differentiates X evaluated at θ_d.'),
 ('At any fixed home configuration, regardless of the desired motion.','A fixed Jacobian is only a local approximation and generally does not differentiate the changing branch.'),
 ('At actual θ(t), even when it differs from θ_d(t), without changing the interpretation.','That may define another feedback construction but is not the derivative of X(θ_d)=X_d.'),
 ('At the Cartesian velocity vector Ẋ_d, because it is the right-hand factor.','J is a function of joint configuration, not a function evaluated at a Cartesian velocity.')],
 'Differentiating the selected desired kinematic path gives Ẋ_d=J(θ_d)θ̇_d. The source abbreviates the argument as Θ; this question explicitly fixes the desired-path interpretation.',difficulty='medium',formulas=[KIN],conflict='The slide writes J^-1(Θ) in desired-trajectory conversion without explicitly identifying the argument as the selected desired joint branch.')
add(756,'inverse-product-rule','Acceleration conversion and the inverse-Jacobian derivative',
 'With A(t)=J(θ_d(t))^−1, differentiating θ̇_d=A Ẋ_d gives which desired acceleration?',[
 ('θ̈_d=A Ẍ_d+Ȧ Ẋ_d.','Both factors in the velocity product can change with time.'),
 ('θ̈_d=A Ẍ_d only, for every moving configuration.','This omits the inverse-Jacobian derivative unless its contribution vanishes.'),
 ('θ̈_d=Ȧ Ẍ_d+A Ẋ_d.','The derivative order is assigned to the wrong factors in both terms.'),
 ('θ̈_d=A Ẍ_d−Ȧ Ẋ_d.','The product rule adds the derivative contribution; any minus sign belongs inside a separately derived formula for Ȧ.')],
 'The product rule yields A Ẍ_d+Ȧ Ẋ_d. A dot on the inverse Jacobian means its time derivative, not an inverse of J̇.',difficulty='medium',typ='derivation',steps=['Differentiate the product A(t)Ẋ_d(t).','Differentiate A for the first contribution and Ẋ_d for the second.','Collect Ȧ Ẋ_d+A Ẍ_d.'],formulas=[KIN],assumptions=['J is square, invertible and differentiable along the desired branch.'])
add(756,'inverse-derivative','Matrix inverse derivative identity',
 'For differentiable invertible J(t), derive Ȧ where A=J^−1. Which expression follows from differentiating JA=I?',[
 ('Ȧ=−J^−1 J̇ J^−1.','J̇A+JȦ=0, then premultiplication by J^−1 yields this order and sign.'),
 ('Ȧ=(J̇)^−1.','Differentiating a matrix inverse is not taking the inverse of its derivative; J̇ might not even be invertible.'),
 ('Ȧ=J^−1 J̇ J^−1.','This loses the minus sign when moving J̇A to the other side.'),
 ('Ȧ=−J̇ J^−2 for arbitrary J and J̇.','This silently commutes J̇ through J^−1, which is invalid in general.')],
 'This author derivation supplies the derivative needed by the source acceleration relation. Matrix order matters: −J^−1J̇J^−1.',typ='derivation',difficulty='medium',steps=['JA=I implies J̇A+JȦ=0.','Move J̇A to the right and premultiply by J^−1.','Replace A by J^−1.'],formulas=[formula('Ȧ=−J^−1J̇J^−1',{'J':'square task Jacobian along a smooth joint path','J̇':'time derivative of J along that path','A':'J^−1','Ȧ':'time derivative of J^−1'},{'J':'m/rad for translational task and revolute joints','J̇':'m/(rad·s)','A':'rad/m','Ȧ':'rad/(m·s)'},['J is invertible; no commutativity is assumed.'])])
add(756,'velocity-calculation','Coupled inverse-Jacobian velocity calculation',
 'At a desired configuration, J=[[1,1],[0,2]] m/rad and Ẋ_d=[0.3,0.4]ᵀ m/s. What is θ̇_d?',[
 ('[0.1,0.2]ᵀ rad/s.','The second row gives θ̇₂=0.2; the first then gives θ̇₁=0.1.'),
 ('[0.3,0.2]ᵀ rad/s.','This divides by the diagonal entries but drops the first-row coupling.'),
 ('[0.7,0.8]ᵀ rad/s.','This multiplies J by the task velocity instead of solving Jθ̇_d=Ẋ_d.'),
 ('[0.3,1.1]ᵀ rad/s.','This uses J^T instead of the required inverse velocity mapping.')],
 'Solve the coupled linear system: 2θ̇₂=0.4 and θ̇₁+θ̇₂=0.3, hence [0.1,0.2]ᵀ.',typ='numerical',difficulty='medium',steps=['Solve the second row: θ̇₂=0.4/2=0.2.','Substitute into the first row: θ̇₁=0.3−0.2=0.1.'],formulas=[KIN],assumptions=['J is evaluated on the selected desired branch; the task has two translational coordinates and two revolute joints.'])
add(756,'acceleration-calculation','Configuration-change contribution to acceleration',
 'For a one-coordinate reference conversion, J=2 m/rad, J̇=0.5 m/(rad·s), Ẋ_d=0.4 m/s and Ẍ_d=0.6 m/s² at one instant. What is θ̈_d?',[
 ('0.25 rad/s².','A=0.5 and Ȧ=−0.5/4=−0.125, so 0.5·0.6−0.125·0.4=0.25.'),
 ('0.30 rad/s².','This ignores the changing-Jacobian contribution.'),
 ('0.35 rad/s².','This gives Ȧ the wrong sign.'),
 ('1.10 rad/s².','This treats the derivative of the inverse as 1/J̇=2, producing 0.3+0.8.')],
 'The inverse Jacobian changes even if the task acceleration is specified separately. Its contribution is −0.05 rad/s², reducing 0.30 to 0.25.',typ='numerical',difficulty='medium',steps=['A=1/J=0.5 rad/m.','Ȧ=−J̇/J²=−0.125 rad/(m·s).','θ̈_d=A Ẍ_d+Ȧ Ẋ_d=0.30−0.05=0.25 rad/s².'],formulas=[KIN],assumptions=['Scalar smooth nonsingular desired-path mapping; all stated values refer to the same instant.'])
add(756,'noise-differentiation','Numerical differentiation and measurement noise',
 'A finite-difference velocity estimate is (x_k−x_{k−1})/Δt. Two position samples have errors +ε and −ε, respectively. What noise contribution enters the estimate?',[
 ('2ε/Δt.','Subtracting the errors gives ε−(−ε)=2ε before division.'),
 ('2εΔt.','Finite differentiation divides by the time step rather than multiplying.'),
 ('Zero because equal-magnitude noise always cancels.','The sample errors have opposite signs, so subtraction adds their magnitudes.'),
 ('ε/2, independent of sampling interval.','This resembles averaging, not the specified derivative estimate.')],
 'The added finite-difference example illustrates the slide’s noise-amplification warning: smaller Δt can magnify a given alternating position error in the derivative estimate.',typ='numerical',difficulty='easy',steps=['Subtract the sample errors: ε−(−ε)=2ε.','Divide by Δt to get 2ε/Δt.'],formulas=[formula('v̂_k=(x_k−x_{k−1})/Δt; δv̂=2ε/Δt',{'v̂_k':'finite-difference velocity estimate','x_k,x_{k−1}':'successive measured positions','Δt':'positive sampling interval','ε':'positive position-error magnitude','δv̂':'noise contribution to the estimated velocity'},{'v̂_k,δv̂':'m/s','x_k,x_{k−1},ε':'m','Δt':'s'},['Sample errors are exactly +ε and −ε; this is a generated illustration, not printed source code.'])])
add(757,'cartesian-feedback','Forward kinematics in the feedback branch',
 'Which route returns the actual position to the direct Cartesian-error comparator in the diagram?',[
 ('Measured θ → Kin(θ) → actual X → negative input of X_d−X.','Forward kinematics supplies the Cartesian actual position.'),
 ('Measured θ → inverse kinematics → desired θ_d → positive input.','This reverses the mapping and confuses actual feedback with the reference.'),
 ('Commanded torque → J^T → actual X → positive input.','The transpose does not convert torque directly into actual position.'),
 ('Desired X_d → Kin(X_d) → actual X, with no joint measurement.','Forward kinematics needs joint configuration and cannot infer the actual state from the desired reference alone.')],
 'The return path converts actual joint position to actual task position, then subtracts it from the desired task position.',typ='diagram',difficulty='easy')
add(757,'cartesian-error','Cartesian error sign and coordinate consistency',
 'In a common Cartesian frame, X_d=[0.4,0.2,0.5]ᵀ m and measured-joint forward kinematics gives X=[0.3,0.25,0.45]ᵀ m. What error enters the direct Cartesian controller?',[
 ('[0.1,−0.05,0.05]ᵀ m.','Subtract actual position from desired component by component.'),
 ('[−0.1,0.05,−0.05]ᵀ m.','This reverses the prescribed desired-minus-actual sign.'),
 ('[0.7,0.45,0.95]ᵀ m.','This adds reference and measurement instead of subtracting.'),
 ('[0.1,0.05,0.05]ᵀ m.','This discards the sign of the y error and changes the correction direction.')],
 'δX=X_d−X=[0.4−0.3,0.2−0.25,0.5−0.45]ᵀ. The negative y component is meaningful.',typ='numerical',difficulty='easy',steps=['Subtract each actual coordinate from its desired coordinate.','Keep the negative y component: 0.2−0.25=−0.05 m.'],formulas=[TRANS])
add([755,757,758],'architecture-tradeoff','Coordinate-conversion location and cost',
 'Which comparison accurately distinguishes the two illustrated architectures?',[
 ('Joint-based Cartesian input converts the desired path before joint-error control; direct Cartesian control converts measured joints inside Cartesian feedback.','The location and coordinates of the error computation differ.'),
 ('Both diagrams compute only joint error; the label Cartesian merely changes the units displayed.','The direct diagram explicitly forms X_d−X.'),
 ('Direct Cartesian control eliminates forward kinematics, while the joint-based input diagram uses it to generate θ_d.','Direct control uses forward kinematics on feedback; desired joint generation is inverse kinematics.'),
 ('Moving coordinate conversion into the feedback loop necessarily removes all real-time computation delay.','The source lists computational load and delay as implementation concerns, not automatically eliminated effects.')],
 'Direct workspace error computation is useful, but it moves coordinate/Jacobian operations into the loop rather than making kinematic computation disappear.',difficulty='medium')
add(758,'workspace-benefits','Potential benefits without automatic tracking guarantees',
 'Which is a defensible interpretation of the listed Cartesian-control advantages?',[
 ('Workspace tasks can be specified naturally, while actual tracking still depends on controller design and implementation.','Convenient task coordinates do not alone establish perfect tracking.'),
 ('Every straight workspace reference is tracked exactly even with arbitrary actuator saturation.','Reference representation does not remove physical actuation limits.'),
 ('A Cartesian controller always uses fewer computations than every joint-space controller.','The slide explicitly lists additional coordinate calculations as a drawback.'),
 ('The end-effector trajectory is accurate whenever the Cartesian error is written down, even without using it in feedback.','Defining an error is not a control law or a performance proof.')],
 'The stated advantages concern direct end-effector objectives and workspace specification. They are not unconditional accuracy or computational-efficiency theorems.',difficulty='easy')
save()
add([759,760,761],'intuitive-intermediates','Distinct intermediate quantities in intuitive controllers',
 'Match each intuitive Cartesian controller to the intermediate quantity immediately before torque generation.',[
 ('Inverse Jacobian: joint displacement correction; transpose Jacobian: virtual Cartesian force.','The inverse maps position error to δθ, whereas the transpose maps F to torque.'),
 ('Inverse Jacobian: virtual Cartesian force; transpose Jacobian: joint displacement correction.','This swaps the roles of the two schemes.'),
 ('Both create a joint displacement by multiplying Cartesian error by J^T.','Only the inverse scheme computes δθ, and it uses J^−1.'),
 ('Both solve full inverse kinematics before applying the same joint gain.','The drawn intuitive schemes use local Jacobian mappings rather than a full finite-pose IK stage.')],
 'The inverse scheme applies a joint-space gain after δθ=J^−1δX; the transpose scheme applies a Cartesian gain to generate F before τ=J^TF.',typ='match',difficulty='easy',formulas=[INV,TRANS])
add(760,'inverse-torque-calculation','Inverse-Jacobian correction followed by joint gains',
 'For J=[[1,1],[0,2]] m/rad, δX=[0.02,0.04]ᵀ m and K_q=diag(2,3) N·m/rad, what torque follows from the stated inverse-Jacobian scheme?',[
 ('[0,0.06]ᵀ N·m.','The local joint correction is [0,0.02]ᵀ rad, then joint gains scale it.'),
 ('[0.04,0.06]ᵀ N·m.','This omits the off-diagonal Jacobian coupling when computing the first correction.'),
 ('[0.04,0.30]ᵀ N·m.','This applies J^T to the position error instead of J^−1 before the gain.'),
 ('[−0.02,0.06]ᵀ N·m.','This interchanges the inverse-Jacobian and gain matrix order.')],
 'Solve Jδθ=δX: δθ₂=0.02 and δθ₁=0.02−0.02=0. Torque is K_qδθ=[0,0.06]ᵀ.',typ='numerical',difficulty='medium',steps=['δθ₂=0.04/2=0.02 rad.','δθ₁=0.02−δθ₂=0 rad.','τ=[2·0,3·0.02]ᵀ=[0,0.06]ᵀ N·m.'],formulas=[INV])
add(760,'local-inverse-scope','Local displacement mapping is not finite inverse kinematics',
 'For nonlinear forward kinematics X=f(θ), what is the proper scope of δθ=J(θ)^−1δX in the intuitive controller?',[
 ('A local first-order correction near a configuration with invertible J.','It comes from δX≈Jδθ, not an exact finite-displacement global inverse.'),
 ('An exact solution of f(θ+δθ)=f(θ)+δX for every finite δX.','Nonlinear higher-order terms generally prevent that equality.'),
 ('A mapping valid at every singular configuration because δX is a position error.','A singular ordinary Jacobian inverse does not exist.'),
 ('A direct Cartesian-force-to-joint-torque mapping that requires no gain.','The source first computes a joint displacement and then applies a joint-space gain.')],
 'The displayed inverse-Jacobian law needs local-linearization and invertibility qualifications. It should not be mistaken for an exact finite IK solver.',difficulty='medium',formulas=[INV],conflict='The slide gives δθ=J^-1δX without explicitly stating the local displacement and ordinary-inverse conditions.')
add(760,'near-singular','Near-singular inverse amplification',
 'At a configuration J=diag(1,ε) m/rad with ε>0, a task correction δX=[0,0.01]ᵀ m is requested. What happens to the inverse-Jacobian correction as ε approaches zero?',[
 ('Its second component 0.01/ε grows without bound in the linear formula.','Small Jacobian sensitivity requires a large local joint correction.'),
 ('Its second component approaches zero as 0.01ε.','That multiplies by J instead of its inverse.'),
 ('It stays exactly 0.01 rad regardless of ε.','The sensitivity scaling cannot be omitted.'),
 ('The ordinary inverse remains well-defined at ε=0 with a finite second component.','At ε=0 the Jacobian is singular, so this ordinary-inverse law is undefined.')],
 'This derived example exposes the invertibility boundary of the printed law. Large predicted corrections also undermine the small-displacement approximation.',typ='scenario',difficulty='medium',steps=['J^−1=diag(1,1/ε).','δθ=[0,0.01/ε]ᵀ rad.','For ε→0⁺ the second component diverges; at zero the ordinary inverse does not exist.'],formulas=[INV],assumptions=['The Jacobian entries are the numerical values in m/rad; no pseudoinverse, damping or saturation is added.'])
add(760,'gain-order','Matrix order in inverse-Jacobian control',
 'The diagram places J^−1 before a joint gain matrix K_q. Which torque expression preserves this order, without assuming that the matrices commute?',[
 ('τ=K_q J^−1δX.','The rightmost matrix acts first on δX.'),
 ('τ=J^−1K_qδX for all J and K_q.','This changes the multiplication order and may even apply a joint-coordinate gain to a task-coordinate vector.'),
 ('τ=(K_qJ)^−1δX.','This inverts K_q as well as J and reverses the intended gain effect.'),
 ('τ=J K_qδX.','This uses the forward Jacobian rather than the inverse and changes the coordinate roles.')],
 'Matrix products encode the block order: δX first becomes δθ, then a joint-space gain produces torque. General matrices cannot be swapped.',difficulty='easy',formulas=[INV])
add(761,'transpose-flow','Virtual Cartesian stiffness and torque mapping',
 'Which block order is shown in the transpose-Jacobian Cartesian controller?',[
 ('Cartesian error → Cartesian gain → virtual force → J^T → joint torque.','The gain creates a force before the transpose maps it to actuators.'),
 ('Cartesian error → J^T → joint displacement → Cartesian gain → force.','J^T is not the inverse displacement map and the shown gain precedes it.'),
 ('Joint torque → J^−1 → desired Cartesian position → comparator.','This reverses the shown signal direction and misidentifies the mapped quantities.'),
 ('Cartesian error → inverse kinematics → desired acceleration → direct Cartesian actuator.','Those blocks are not in the pictured intuitive transpose scheme.')],
 'The force is virtual in the controller computation. Physical joint torques, obtained through J^T, drive the arm.',typ='diagram',difficulty='easy',formulas=[TRANS])
add(761,'transpose-torque-calculation','Coupled force-to-torque numerical mapping',
 'Let J=[[1,2],[3,4]] m/rad, δX=[0.10,−0.05]ᵀ m and K_x=diag(10,20) N/m. What is τ in the transpose-Jacobian controller?',[
 ('[−2,−2]ᵀ N·m.','F=[1,−1]ᵀ N and J^TF=[1−3,2−4]ᵀ.'),
 ('[−1,−1]ᵀ N·m.','This uses JF rather than J^TF.'),
 ('[−3,2]ᵀ N·m.','This applies J^−1 to F instead of the force-to-torque transpose.'),
 ('[−0.5,0]ᵀ N·m.','This multiplies by J^T before the Cartesian gain, changing both the order and coordinate role.')],
 'First form the virtual force, including its negative second component. Then each joint torque is the corresponding column of J dotted with F.',typ='numerical',difficulty='medium',steps=['F=K_xδX=[10·0.10,20·(−0.05)]ᵀ=[1,−1]ᵀ N.','J^T=[[1,3],[2,4]].','τ=[1·1+3·(−1),2·1+4·(−1)]ᵀ=[−2,−2]ᵀ N·m.'],formulas=[TRANS])
add([756,761],'virtual-power','Why the transpose preserves virtual power',
 'Given Ẋ=Jθ̇ and compatible work-conjugate force F, which derivation supports τ=J^TF?',[
 ('FᵀẊ=FᵀJθ̇=(JᵀF)ᵀθ̇, so the joint torque for equal power is JᵀF.','The scalar work/power pairing determines the transpose.'),
 ('FᵀẊ=(J^−1F)ᵀθ̇ for any square J, so τ=J^−1F.','That equality does not follow from Ẋ=Jθ̇.'),
 ('Since J maps velocity forward, the same untransposed J must map force forward.','Dual force coordinates transform by the transpose when the velocity relation is substituted into power.'),
 ('Equal power requires τ=F componentwise even when J is not the identity.','The kinematic leverage represented by J changes the force components seen at joints.')],
 'The transpose mapping can be derived from the source velocity and torque relations through equality of virtual power. This is a mathematical derivation, not an additional actuator assumption.',typ='derivation',difficulty='medium',steps=['Start with Cartesian power FᵀẊ.','Substitute Ẋ=Jθ̇.','Use FᵀJ=(JᵀF)ᵀ and identify the joint-power coefficient.'],formulas=[TRANS],assumptions=['The force and velocity refer to the same point/frame; all task coordinates are translational here and no dissipation is included in the instantaneous mapping.'])
add(761,'rectangular-transpose','Dimensions of the transpose mapping',
 'For a task with m Cartesian velocity components and n joint velocities, J is m×n. What dimensions make τ=J^TF valid?',[
 ('F is m×1 and τ is n×1; J^T is n×m.','The transpose converts the task-force vector into one torque per joint.'),
 ('F is n×1 and τ is m×1; J^T is m×n.','This reverses the vector roles and transpose dimensions.'),
 ('Both F and τ must be m×1, so the formula requires m=n.','The transpose product is dimensionally valid even when J is rectangular.'),
 ('J^T must be inverted before multiplication whenever m≠n.','The displayed force mapping is a transpose product, not an inverse operation.')],
 'The transpose mapping itself does not require a square inverse. Whether a controller can realize an arbitrary task motion is a separate rank and dynamics question.',difficulty='medium',formulas=[TRANS],assumptions=['J and F are defined for a compatible task velocity/force pair.'])
add(761,'singular-force-nullspace','Transpose exists without guaranteeing task correction',
 'At an instant, J=[[1,0],[0,0]] m/rad and the virtual force is F=[0,2]ᵀ N. What torque does the transpose law produce, and what does this demonstrate?',[
 ('τ=[0,0]ᵀ; a nonzero task force can lie in the nullspace of J^T.','The second task direction has no instantaneous joint-velocity sensitivity in this J.'),
 ('τ=[0,2]ᵀ; the transpose always copies force into torque.','The zero second row/column prevents that component from contributing here.'),
 ('The product J^TF is undefined because J is singular.','The transpose product exists even though an ordinary inverse does not.'),
 ('τ=[2,0]ᵀ; every unavailable task direction is automatically redirected into an available joint.','The stated linear map contains no such redirection rule.')],
 'Unlike an ordinary inverse, J^T remains computable at singularity. Computability alone does not prove that every Cartesian error produces a correcting torque.',typ='numerical',difficulty='medium',steps=['Transpose the diagonal J, which leaves it unchanged.','Multiply by F to obtain [0,0]ᵀ N·m.','A nonzero F with J^TF=0 belongs to the transpose nullspace.'],formulas=[TRANS])
add([760,761],'gain-units','Different physical meanings of intuitive gain matrices',
 'For translation-only tasks and revolute joints, compare K_q in τ=K_qδθ with K_x in F=K_xδX. Which units are appropriate?',[
 ('K_q: N·m/rad; K_x: N/m.','The gains map angular displacement to torque and linear displacement to force, respectively.'),
 ('Both gains: N/m because both ultimately reduce Cartesian error.','Their immediate input/output quantities differ, so their units need not match.'),
 ('K_q: N·m·rad; K_x: N·m.','Gain units divide output by input, not multiply them.'),
 ('K_q: rad/(N·m); K_x: m/N.','Those are compliance-like inverse gain units.')],
 'The same letter K does not make the gains physically identical or interchangeable. Their placement and coordinate systems determine the units.',difficulty='easy',formulas=[INV,TRANS])
add(762,'decoupling-goal','Desired Cartesian error dynamics',
 'Which behavior is the stated target of Cartesian decoupling rather than simply applying a Cartesian position gain?',[
 ('Fixed, decoupled Cartesian error dynamics with a chosen damping behavior across configurations.','The goal is uniform task-space behavior, not just a torque proportional to error.'),
 ('Fixed joint torques independent of both configuration and tracking error.','Configuration-independent error dynamics do not require constant actuator torques.'),
 ('A physical inertia matrix that becomes identical at every arm configuration.','Model compensation can shape closed-loop behavior without physically changing inertia.'),
 ('Independent joint errors only, with no requirement on Cartesian behavior.','The stated target is explicitly in workspace coordinates.')],
 'The slide names uniform tracking, fixed dynamics and critically damped decoupled Cartesian errors as design goals. Accurate compensation and suitable gains are needed to realize them.',difficulty='easy')
add(763,'cartesian-dynamics','Cartesian dynamic terms and state dependence',
 'Match the terms in ℱ=M_x(Θ)χ̈+V_x(Θ,Θ̇)+G_x(Θ).',[
 ('M_x: Cartesian inertia; V_x: velocity-dependent terms; G_x: gravity terms.','This follows the definitions under the displayed equation.'),
 ('M_x: Jacobian transpose; V_x: Cartesian position error; G_x: proportional gain.','These are different controller quantities, not the dynamic terms defined here.'),
 ('M_x: joint-angle vector; V_x: desired acceleration; G_x: measured joint torque.','The source assigns matrix/force-vector roles, not these signals.'),
 ('M_x: gravity matrix; V_x: inertia force only; G_x: damping ratio.','This interchanges physical meanings and confuses gains with model terms.')],
 'The Cartesian model has the same broad inertia, velocity-dependent and gravity structure as the joint-space dynamic model, but expressed in task coordinates.',typ='match',difficulty='easy',formulas=[DYN])
add([755,763],'task-coordinate-scope','Position-only notation versus position and orientation',
 'How should X=[x,y,z]ᵀ on the early page be distinguished from χ on the Cartesian-dynamics page?',[
 ('X there is position-only; χ is described as including position and orientation, so its precise representation must be specified.','A three-position-vector example does not define every later task coordinate.'),
 ('Both symbols necessarily mean the same three position coordinates and never orientation.','The later page explicitly includes orientation in χ.'),
 ('χ always equals the joint-angle vector Θ because both appear in the same equation.','The page distinguishes Cartesian task coordinates from joint configuration.'),
 ('Any three orientation-angle rates can be substituted for physical angular velocity without changing the Jacobian or force convention.','Orientation rates and angular velocity require a representation-dependent relation; the slide does not specify it.')],
 'Do not silently conflate a translational example with a general pose vector. Later force/moment equations need consistent task-rate and work-conjugate force conventions.',difficulty='medium',conflict='The lecture shifts from position-only X to position/orientation χ without defining orientation coordinates or their conjugate-force convention.',conflict_pages=[763])
save()
ERR=formula('Ë+K_v Ė+K_p E=0',{'E':'desired-minus-actual Cartesian position error vector','Ė':'its first time derivative','Ë':'its second time derivative','K_v':'velocity-error gain matrix','K_p':'position-error gain matrix'},{'E':'m','Ė':'m/s','Ë':'m/s²','K_v':'s^−1','K_p':'s^−2'},['Translation-only coordinates, exact model cancellation and no unmodeled force; diagonal gains give coordinate-wise decoupling.'])
add(763,'workspace-figure','Base axes and end-effector axes in the schematic',
 'Which reading is supported by the Cartesian-dynamics illustration without inferring geometry that is not supplied?',[
 ('Uppercase X,Y,Z identify the base axes at O; lowercase x,y,z appear at the end-effector point P, and the dashed sphere is schematic.','The drawing shows frames and a task point but supplies no link dimensions or exact reachable-set calculation.'),
 ('The dashed sphere proves every orientation is attainable at every point inside it.','No reachability or orientation proof is supplied by this schematic.'),
 ('The lowercase axes label three extra translational joints at P.','They are coordinate axes drawn at the task point, not three new joints.'),
 ('Uppercase and lowercase axes must coincide because they use the same axis letters.','The drawing explicitly locates the axes at different origins and does not establish coincident frames.')],
 'The picture illustrates Cartesian coordinates and an end-effector point. It should not be promoted into a precise workspace or dexterity theorem.',typ='diagram',difficulty='easy')
add(763,'cartesian-force-calculation','Cartesian dynamic force with coupled inertia',
 'For a two-coordinate translational task, M_x=[[2,1],[1,3]] kg, Ẍ=[1,−2]ᵀ m/s², V_x=[0.5,1]ᵀ N and G_x=[1,4]ᵀ N. What force follows from the displayed model?',[
 ('[1.5,0]ᵀ N.','M_xẌ=[0,−5]ᵀ N, then V_x+G_x=[1.5,5]ᵀ N.'),
 ('[3.5,−1]ᵀ N.','This ignores off-diagonal inertia coupling.'),
 ('[−1.5,−10]ᵀ N.','This subtracts the velocity and gravity terms instead of adding them.'),
 ('[1,−1]ᵀ N.','This omits V_x while retaining inertia and gravity.')],
 'The matrix product includes cross-coordinate acceleration effects. Add both remaining force vectors after computing the full product.',typ='numerical',difficulty='medium',steps=['M_xẌ=[2·1+1·(−2),1·1+3·(−2)]ᵀ=[0,−5]ᵀ N.','V_x+G_x=[1.5,5]ᵀ N.','F=[1.5,0]ᵀ N.'],formulas=[DYN])
add([763,764],'model-cancellation','Exact Cartesian model compensation',
 'For the exact plant F=M_xẌ+V_x+G_x, apply F=M_xu+V_x+G_x with invertible M_x. Which reduced equation results?',[
 ('Ẍ=u.','Cancel matching V_x and G_x, then multiply M_xẌ=M_xu by M_x^−1.'),
 ('Ẍ=M_xu.','This omits the division by the plant inertia after matching the force equation.'),
 ('Ẍ=u+2(V_x+G_x).','The compensation terms cancel in the equality; they do not double.'),
 ('Ẍ=J^Tu.','The transpose is the subsequent force-to-torque mapping, not the remaining Cartesian acceleration dynamics.')],
 'Matching model compensation produces a normalized acceleration input. It changes the closed-loop equation, not the physical inertia or gravity of the robot.',typ='derivation',difficulty='medium',steps=['Equate plant force and commanded force.','Subtract V_x+G_x from both sides.','Premultiply by M_x^−1 to obtain Ẍ=u.'],formulas=[DYN],assumptions=['Task coordinates and generalized forces are consistent; the commanded force is realized, model terms match, and no additional force is present.'])
add(764,'servo-units','Servo component is acceleration rather than force',
 'In a translation-only model F=M_xℱ′+V_x+G_x, with M_x in kg and the other terms in N, what are the units of ℱ′?',[
 ('m/s².','Multiplication by inertia converts acceleration into force.'),
 ('N.','Then M_xℱ′ would have kg·N rather than N.'),
 ('m.','Multiplication by kg alone would not supply the necessary inverse-time-squared factor.'),
 ('N·m.','That is torque, not the normalized translational servo input.')],
 'The prime in ℱ′ labels the servo-law component. Despite the force-like symbol, its role in the normalized translational model is acceleration.',difficulty='easy',formulas=[DYN])
add(765,'servo-calculation','Desired acceleration plus Cartesian error feedback',
 'For a translation-only task, Ẍ_d=[0.5,−0.2]ᵀ m/s², E=[0.1,−0.2]ᵀ m, Ė=[−0.05,0.1]ᵀ m/s, K_p=diag(4,9) s^−2 and K_v=diag(4,6) s^−1. What is the servo command u?',[
 ('[0.7,−1.4]ᵀ m/s².','K_vĖ=[−0.2,0.6]ᵀ and K_pE=[0.4,−1.8]ᵀ; add the desired acceleration.'),
 ('[0.2,−1.2]ᵀ m/s².','This omits the desired-acceleration feedforward.'),
 ('[0.3,1.0]ᵀ m/s².','This subtracts both error-feedback terms instead of adding them for desired-minus-actual error.'),
 ('[1.1,−2.6]ᵀ m/s².','This reverses only the velocity-error feedback sign.')],
 'The servo sums feedforward acceleration with positive gains on desired-minus-actual position and velocity errors.',typ='numerical',difficulty='medium',steps=['K_vĖ=[4·(−0.05),6·0.1]ᵀ=[−0.2,0.6]ᵀ.','K_pE=[4·0.1,9·(−0.2)]ᵀ=[0.4,−1.8]ᵀ.','Add Ẍ_d to obtain [0.7,−1.4]ᵀ m/s².'],formulas=[DYN])
add([763,764,765],'error-dynamics','Derived Cartesian error equation',
 'Under exact cancellation Ẍ=u, define E=X_d−X and use u=Ẍ_d+K_vĖ+K_pE. Which error equation follows?',[
 ('Ë+K_vĖ+K_pE=0.','Subtract actual acceleration from desired acceleration and move the feedback terms left.'),
 ('Ë−K_vĖ−K_pE=0.','This uses the wrong sign when forming desired-minus-actual acceleration.'),
 ('M_xË+K_vĖ+K_pE=0 after exact normalization.','The matching M_x has already canceled; retaining it changes the normalized dynamics.'),
 ('Ė+K_vĖ+K_pE=Ẍ_d.','This confuses the second derivative and fails to cancel desired acceleration.')],
 'Ë=Ẍ_d−Ẍ=Ẍ_d−u=−K_vĖ−K_pE. Desired acceleration cancels because it is present in the servo command.',typ='derivation',difficulty='medium',steps=['Differentiate E=X_d−X twice.','Substitute Ẍ=u.','Substitute the servo law and cancel Ẍ_d.','Rearrange into Ë+K_vĖ+K_pE=0.'],formulas=[DYN,ERR],assumptions=['The exact model conditions of the cited cancellation law hold.'])
add([762,764,765],'critical-gain-design','Critically damped decoupled Cartesian channels',
 'The exact normalized error dynamics use K_p=diag(4,9) s^−2. Which diagonal K_v makes both channels critically damped with stable repeated real poles?',[
 ('diag(4,6) s^−1.','For each s²+k_vs+k_p, critical damping requires k_v=2√k_p>0.'),
 ('diag(2,3) s^−1.','These give k_v²<4k_p, so both channels are underdamped.'),
 ('diag(8,18) s^−1.','These give positive discriminants and overdamped distinct poles.'),
 ('diag(−4,−6) s^−1.','The discriminants vanish but the repeated poles are positive, so these are not stable critical responses.')],
 'Channel polynomials are s²+4s+4=(s+2)² and s²+6s+9=(s+3)². The positive sign of the damping gain is essential.',typ='numerical',difficulty='medium',steps=['For each scalar channel set the quadratic discriminant k_v²−4k_p to zero.','Choose the positive damping value k_v=2√k_p.','Evaluate 2√4=4 and 2√9=6; poles are −2 and −3.'],formulas=[ERR,formula('k_v=2√k_p; s=−k_v/2',{'k_p':'positive scalar position-error gain','k_v':'positive scalar velocity-error gain','s':'repeated characteristic root'},{'k_p':'s^−2','k_v,s':'s^−1'},['Independent normalized second-order error channel; critical discriminant zero and stable negative root.'])])
add([762,765],'diagonal-decoupling','Off-diagonal gains can retain cross-coordinate coupling',
 'With Ë+K_vĖ+K_pE=0, K_v=diag(4,6) and K_p=[[4,1],[1,9]] in consistent units, take E=[0,1]ᵀ m and Ė=0. What is Ë, and are the original coordinate errors decoupled?',[
 ('[−1,−9]ᵀ m/s²; no, the second error drives the first acceleration.','The off-diagonal 1 in K_p couples the coordinate equations.'),
 ('[0,−9]ᵀ m/s²; yes, diagonal K_v alone guarantees decoupling.','This drops the off-diagonal position-error gain.'),
 ('[1,9]ᵀ m/s²; yes, model cancellation reverses all restoring signs.','The error equation gives negative K_pE, not positive.'),
 ('[−4,−1]ᵀ m/s²; no, because the first column must always be used.','Multiplication by [0,1]ᵀ selects the second column.')],
 'Removing nonlinear model coupling is not enough to ensure coordinate-wise independence if the chosen servo gains themselves contain cross terms.',typ='numerical',difficulty='medium',steps=['Ė=0 removes the velocity term.','K_pE=[1,9]ᵀ.','Ë=−K_pE=[−1,−9]ᵀ; the first coordinate reacts to the second error.'],formulas=[ERR])
add([763,764,769],'model-mismatch','Inertia mismatch prevents exact normalization',
 'In a scalar translation-only example, the actual inertia is 2 kg and actual V_x+G_x=0. The controller uses an inertia estimate of 3 kg, exact zero compensation and servo command u=4 m/s². What actual acceleration results?',[
 ('6 m/s².','The command is 3·4=12 N, and the actual plant acceleration is 12/2=6.'),
 ('4 m/s².','That would require matching inertia or a corrected command, not the stated estimate.'),
 ('8 m/s².','This multiplies u by the actual inertia and mislabels force as acceleration.'),
 ('8/3 m/s².','This inverts the actual/estimated inertia ratio.')],
 'The exact cancellation proof depends on a matching model. Here Ẍ=(3/2)u=6 m/s², so the normalized command is not realized exactly.',typ='numerical',difficulty='medium',steps=['Compute commanded force F_cmd=3 kg·4 m/s²=12 N.','Apply the actual plant relation 2 kg·Ẍ=12 N.','Ẍ=6 m/s².'],formulas=[formula('F_cmd=m̂u; mẌ=F_cmd; Ẍ=(m̂/m)u',{'F_cmd':'commanded Cartesian force','m̂':'controller inertia estimate','m':'actual scalar Cartesian inertia','u':'servo acceleration command','Ẍ':'actual Cartesian acceleration'},{'F_cmd':'N','m̂,m':'kg','u,Ẍ':'m/s²'},['Scalar translational model; actual and estimated velocity/gravity compensation are both zero.'])])
add([765,766],'model-block-feedback','Different maps for position and velocity feedback',
 'In the Cartesian model-based diagram, which pairing correctly reconstructs the actual feedback signals from measured joints?',[
 ('Kin(θ) gives X; J(θ)θ̇ gives Ẋ.','Position uses nonlinear forward kinematics; velocity uses the configuration-dependent Jacobian.'),
 ('J(θ)θ gives exact X; Kin(θ̇) gives Ẋ.','A Jacobian is not generally the finite-position map, and velocity is not a joint configuration for Kin.'),
 ('J^Tθ gives X; J^−1θ̇ gives Ẋ.','These do not follow the shown coordinate mappings or compatible dimensions.'),
 ('Kin(X_d) gives actual X; J(X_d)Ẋ_d gives actual Ẋ.','The actual feedback must depend on actual joint measurements, not desired Cartesian inputs.')],
 'The same current configuration determines forward position and the Jacobian used for velocity; the two operations are not interchangeable.',typ='diagram',difficulty='easy',formulas=[KIN])
add([764,765],'full-command-chain','Model compensation before torque conversion',
 'At one instant, u=[1,−1]ᵀ m/s², M_x=[[2,1],[1,3]] kg, V_x+G_x=[1,2]ᵀ N, and J=[[1,2],[0,1]] m/rad. What actuator torque is commanded?',[
 ('[2,4]ᵀ N·m.','M_xu=[1,−2]ᵀ, so F=[2,0]ᵀ and J^TF=[2,4]ᵀ.'),
 ('[2,0]ᵀ N·m.','This reports Cartesian force components as joint torques without the transpose map.'),
 ('[1,0]ᵀ N·m.','This maps only M_xu and omits the compensation vector.'),
 ('[1,1]ᵀ N·m.','This maps u directly through J^T, omitting both inertia scaling and compensation.')],
 'The order is servo acceleration, Cartesian inertia scaling plus compensation, then Jacobian-transpose torque mapping.',typ='numerical',difficulty='medium',steps=['M_xu=[2−1,1−3]ᵀ=[1,−2]ᵀ N.','Add [1,2]ᵀ to obtain F=[2,0]ᵀ N.','J^TF=[[1,0],[2,1]][2,0]ᵀ=[2,4]ᵀ N·m.'],formulas=[DYN,TRANS])
add(765,'feedforward-role','Effect of omitting desired-acceleration feedforward',
 'Keep exact Ẍ=u and E=X_d−X, but deliberately modify the servo to u=K_vĖ+K_pE by removing Ẍ_d. Which error equation now holds?',[
 ('Ë+K_vĖ+K_pE=Ẍ_d.','The uncanceled reference acceleration becomes a forcing term.'),
 ('Ë+K_vĖ+K_pE=0 for every desired trajectory.','That is the nominal equation only when feedforward cancels Ẍ_d or when Ẍ_d=0.'),
 ('Ë−K_vĖ−K_pE=Ẍ_d.','The desired-minus-actual convention still produces positive feedback coefficients on the left.'),
 ('Ë+K_vĖ+K_pE=−Ẍ_d.','Differentiating E=X_d−X places Ẍ_d with a positive sign.')],
 'This question intentionally changes the printed law. Substitution gives Ë=Ẍ_d−K_vĖ−K_pE; acceleration feedforward is what removed this reference forcing in the source design.',typ='derivation',difficulty='medium',steps=['Use Ë=Ẍ_d−Ẍ.','Insert the modified u without feedforward.','Move the feedback terms to the left.'],formulas=[formula('u=K_vĖ+K_pE; Ë+K_vĖ+K_pE=Ẍ_d',{'u':'modified servo acceleration, without source feedforward','E':'X_d−X Cartesian position error','Ė,Ë':'first and second error derivatives','X_d':'desired Cartesian position','Ẍ_d':'desired Cartesian acceleration','K_v':'velocity-error gain matrix','K_p':'position-error gain matrix'},{'u,Ë,Ẍ_d':'m/s²','E,X_d':'m','Ė':'m/s','K_v':'s^−1','K_p':'s^−2'},['Translation-only task and exact Ẍ=u; this deliberately modified law is not the nominal source controller.'])])
add([761,765],'force-frame','Compatible frames in Jacobian-transpose torque mapping',
 'A position Jacobian maps joint velocity to tool-point velocity expressed in the base frame, but a force measurement is expressed in the tool frame. Before using τ=J^TF, what is needed?',[
 ('Express the force at that same point in the base frame, or consistently transform both force and Jacobian.','The power pairing must use compatible coordinate representations.'),
 ('Use the tool-frame force entries unchanged because a transpose automatically rotates frames.','Transposition swaps indices; it does not supply the missing tool-to-base rotation.'),
 ('Replace J^T by J^−1 while keeping the unmatched force frame.','An inverse does not repair incompatible coordinate representations.'),
 ('Subtract the Cartesian position error from the force before applying J^T.','Position error and force have different units, and subtraction does not perform a frame transformation.')],
 'The displayed torque mapping presumes that J and F describe the same task point and compatible frame. This translation-only example avoids additional moment-shift issues.',difficulty='medium',formulas=[TRANS],assumptions=['Both representations concern the same tool point; only a force vector, not a displaced wrench, is involved.'])
save()
add(767,'dual-rate','Fast servo and slower model-coefficient updates',
 'What allocation is proposed by the practical dual-rate architecture?',[
 ('Run the error-feedback servo quickly and update expensive configuration-dependent model quantities more slowly when their variation permits.','This separates fast correction from slower background model recomputation.'),
 ('Run the model update quickly but hold the servo error fixed until the next slow update.','This reverses the source allocation.'),
 ('Stop using feedback between background updates and run the manipulator open-loop throughout each interval.','A fast servo loop continues to use feedback between slower model updates.'),
 ('Compute all model quantities once at startup and never update them as the arm moves.','Slower updates are still updates; the quantities depend on changing configuration.')],
 'Dual rate is a computational scheduling strategy. The slower update is justified only relative to how quickly the relevant model quantities vary.',difficulty='easy')
add(767,'dual-rate-periods','Illustrative servo and background update periods',
 'An illustrative implementation runs the servo every 1 ms and updates model coefficients every 20 ms. How many servo periods fit in one model-update period, and what remains active between model updates?',[
 ('20 servo periods; error-feedback correction continues using the available coefficients.','20/1=20, and fast feedback does not wait for each background recomputation.'),
 ('20 servo periods; all feedback must be disabled between model updates.','The period count is correct but disabling the servo defeats the dual-rate architecture.'),
 ('0.05 servo periods; the model update is faster than the servo.','This reverses the period ratio and misidentifies the faster loop.'),
 ('19 servo periods; the twentieth period must always be skipped to recompute the model.','The stated periods do not imply a skipped servo period or a specific scheduling conflict.')],
 'The source supplies no numerical rate. In this explicitly generated schedule, T_model/T_servo=20; whether these rates are sufficient still needs a system-specific check.',typ='numerical',difficulty='easy',steps=['Convert or compare periods in the same unit: 20 ms and 1 ms.','Divide 20/1=20.','The fast loop continues between coefficient updates.'],formulas=[formula('N=T_model/T_servo',{'N':'number of servo periods per model-update period','T_model':'background coefficient-update period','T_servo':'servo execution period'},{'N':'dimensionless','T_model,T_servo':'s or the same time unit'},['Illustrative exact integer ratio; no source-prescribed rate or real-time schedulability guarantee.'])])
add(767,'stale-model','When slow background updates become questionable',
 'Which circumstance most directly undermines the slide’s reason for using a slower background model update?',[
 ('Configuration-dependent model quantities change substantially during one update interval.','Held coefficients can then become inaccurate relative to the ongoing fast servo.'),
 ('The desired trajectory is expressed in Cartesian coordinates rather than joint coordinates.','That motivates this architecture; it does not by itself invalidate slow coefficient updates.'),
 ('The servo uses current measured position error while coefficients are held briefly.','That is the intended separation, not by itself a failure condition.'),
 ('The background model is mathematically a matrix rather than a scalar.','Matrix dimension affects computation but does not alone determine variation over time.')],
 'Slow updates depend on sufficiently slow variation relative to the update interval and acceptable modeling error. The slide’s configuration-speed premise is not universally true.',typ='scenario',difficulty='medium',conflict='The source states that configuration changes relatively slowly as the motivation for slower parameter updates; this is operating-condition dependent.')
add([763,767,768],'velocity-block','Actual velocity still feeds practical compensation',
 'In the practical diagram, the lower block is labeled B_x(θ)+C_x(θ), and an actual θ̇ arrow enters it. What is the defensible interpretation?',[
 ('The abbreviated coefficient labels do not erase velocity dependence; the actual velocity input must still be accounted for.','The arrow and the earlier V_x(θ,θ̇) description both show velocity dependence.'),
 ('The block is independent of velocity because its printed label contains only θ.','This ignores the explicit θ̇ input and the preceding dynamic model.'),
 ('The θ̇ arrow means the output is simply joint velocity, with no force compensation.','The block feeds the model-force summation; its output is not merely the measured velocity signal.'),
 ('The block supplies the desired trajectory and therefore needs no actual measurements.','Its shown inputs come from actual arm state and its output is compensation, not trajectory generation.')],
 'Read the diagram together with the defined Cartesian dynamics. The lecture does not give separate B_x and C_x formulas here, so no more specific coefficient law is invented.',typ='diagram',difficulty='medium',conflict='The practical diagram abbreviates the lower block as B_x(θ)+C_x(θ), although actual θ̇ enters it and earlier V_x explicitly depends on velocity.',conflict_pages=[767,768])
add([767,769,770],'update-versus-adaptation','Configuration recomputation versus parameter estimation',
 'Which change distinguishes adaptive parameter estimation from merely recomputing a fixed-parameter model at a new configuration?',[
 ('Adaptation changes estimates of uncertain physical/model parameters using online information; configuration recomputation can keep those estimates fixed.','A known model evaluated at a new θ is not itself parameter learning.'),
 ('Any evaluation of M_x at a different θ proves that the payload estimate has been identified online.','Configuration dependence can change M_x even with a fixed payload estimate.'),
 ('Adaptation means only increasing the servo execution rate while leaving the model unchanged.','That is a scheduling change, not the source’s online model update mechanism.'),
 ('A slower background update necessarily estimates unknown friction even without an estimation law.','Update timing alone does not define how uncertain parameters are learned.')],
 'Dual-rate computation and adaptive estimation can coexist, but they address different issues: computational scheduling versus uncertainty or change in the model parameters.',difficulty='medium')
add(768,'practical-tradeoff','Model-based Cartesian performance and implementation burden',
 'Which statement best captures the practical trade-off described on the page?',[
 ('Well-designed Cartesian model-based control can improve workspace tracking and disturbance response, at the cost of computation and coordinate transformations.','This retains both the intended benefits and implementation burden without asserting a universal guarantee.'),
 ('The improved tracking claim proves that arbitrary model mismatch can no longer affect errors.','The following adaptive-control discussion explicitly identifies mismatch as a cause of lost cancellation.'),
 ('More coordinate transformations guarantee worse tracking even when implemented accurately and on time.','Computation is a burden, but its existence alone does not establish worse control performance.'),
 ('A higher model-update rate always improves disturbance rejection, regardless of computation delay or servo stability.','Timing and stability effects cannot be dismissed merely by increasing a nominal update rate.')],
 'The benefits are design objectives and achievable outcomes under suitable conditions, not unconditional performance bounds for every implementation.',difficulty='easy',conflict='The source lists improved disturbance rejection and tracking without specifying a universal comparison baseline or bound.')
add(769,'changing-parameters','Sources of dynamic-model uncertainty and change',
 'Select all changes that directly match the lecture’s examples of physical dynamic-model parameters needing attention.',[
 ('Replacing the carried payload with one of different mass or inertia.','Payload variation and unknown inertia are explicit examples.'),
 ('Wear changing friction behavior during service.','Wear/ageing and friction changes are both listed.'),
 ('Moving the payload center of mass relative to the attachment.','A changing center of mass is explicitly listed.'),
 ('Changing only joint configuration while keeping physical masses, inertias, friction coefficients and payload attachment fixed.','Configuration changes model matrix values, but this stated change does not itself change the underlying physical parameter values.')],
 'Payload, friction, wear, inertia and center-of-mass changes can make a previously fitted dynamic model inaccurate. Configuration-dependent matrix changes alone need not mean those underlying physical parameters changed.',correct=(0,1,2),typ='statement',difficulty='easy')
add([769,770],'adaptive-diagram','Information paths into the adaptation mechanism',
 'In the adaptive-control diagram, which information enters the adaptation-law block, and what does its output modify?',[
 ('Tracking error and its derivative, plus actual θ and θ̇, enter; the output modifies the dynamic model.','The diagram shows these state/error branches and an update arrow into the model block.'),
 ('Only desired acceleration enters; the output retunes the desired path while leaving the dynamic model fixed.','The shown inputs include measured state and errors, and the update target is the dynamic model.'),
 ('Only the Cartesian virtual force enters; the output replaces forward kinematics.','This adaptive illustration uses joint-coordinate signals and updates the dynamic model.'),
 ('Only actual torque enters; the output replaces the servo gains while leaving the dynamic model unchanged.','The diagram shows state/error inputs and a model-update arrow, not this torque-only gain-tuning architecture.')],
 'The adaptive illustration is drawn in joint coordinates even within this Cartesian-control lecture. It adds a model-adjustment path using state and tracking information.',typ='diagram',difficulty='medium')
add([769,770],'adaptive-model-output','Normalized servo signal versus actuator torque',
 'In the adaptive diagram, desired θ̈_d and gain-weighted Ė and E are summed into τ′ before the dynamic-model block. What distinction is important?',[
 ('τ′ is the normalized servo-law input; the dynamic-model block converts it into the actuator torque τ.','The prime-labeled intermediate is not automatically a physical torque just because a tau symbol is used.'),
 ('τ′ and τ are necessarily numerically identical because the diagram uses tau for both.','The dynamic-model block generally scales and compensates the intermediate command.'),
 ('τ′ is the parameter-update law, while τ is measured Cartesian position.','The diagram separates the adaptation-law block and labels τ on the arm input.'),
 ('τ is desired joint acceleration and must be integrated twice before it reaches the arm.','The arm input is torque; desired acceleration appears earlier in the servo sum.')],
 'The source uses a normalized servo component followed by a dynamic model. With angular acceleration feedforward, τ′ has acceleration-like units; the model supplies inertia scaling and other required torque terms.',typ='diagram',difficulty='medium',assumptions=['The sum uses consistent normalized joint-coordinate gains; the question identifies the shown signal roles rather than inventing a specific adaptation equation.'])
add(770,'adaptation-scope','Online model learning is not an unconditional guarantee',
 'What conclusion about adaptation is justified by the lecture’s architecture and prose alone?',[
 ('It estimates and updates model parameters online to address uncertainty, but a specific stability or identification guarantee needs a specified update law and conditions.','No update equation or convergence hypotheses are given on these pages.'),
 ('Every parameter estimate becomes exact immediately after any nonzero tracking error occurs.','An error signal alone does not supply instantaneous exact parameter identification.'),
 ('Tracking error must decrease at every instant for any chosen parameter-update rule.','The source does not specify or prove such a monotonic guarantee.'),
 ('Adaptive control removes the need for the existing servo-law feedback because the dynamic model is being updated.','The diagram explicitly retains servo-law feedback together with adaptation.')],
 'The page describes online estimation and model adjustment, not a complete implementable adaptation algorithm or universal convergence theorem.',difficulty='medium',conflict='The source says the controller learns dynamics and reduces tracking error but supplies no adaptation update equation, stability proof or convergence assumptions.')
add([760,761,763,764,765],'controller-comparison','Intuitive transpose feedback versus model-based decoupling',
 'Why is τ=J^TK_x(X_d−X) not, by itself, the complete Cartesian model-based decoupling law developed later?',[
 ('It contains virtual stiffness feedback but omits the Cartesian inertia scaling, velocity/gravity compensation and desired-acceleration servo structure.','The later law computes a model-based Cartesian force before the same transpose torque map.'),
 ('It cannot produce a joint torque because J^T is reserved exclusively for velocity mapping.','J^T is precisely the force-to-torque map used in both designs.'),
 ('It already cancels all nonlinear dynamics simply because the error is Cartesian.','Choice of error coordinates alone does not cancel plant inertia or other dynamic terms.'),
 ('The later law replaces J^T by J^−1 to convert Cartesian force to torque.','The later diagram retains J^T; it changes how the commanded Cartesian force is computed.')],
 'A shared final transpose block does not make the controllers equivalent. Model-based decoupling adds the dynamics compensation and normalized acceleration servo law.',difficulty='medium',formulas=[TRANS,DYN])
# Summary supplies no new premise. Preserve links to existing substantive questions.
for n in [1,2,6,15,27,31,38,42,46,48,51,52]:
 q=b.questions[n-1];q['citations'].append({'slideId':'lectures-p0771','sourceId':'lectures','sourceSha256':SHA,'physicalPage':771,'kind':'statement','locator':'Lecture 25, physical PDF page 771, actual printed footer 21: summary of '+q['subtopic'],'evidenceText':(R/'sources/text/lectures/page-0771.txt').read_text().strip(),'role':'premise','region':None})
 for cid in q['conceptIds']:
  if 'lectures-p0771' not in b.concepts[cid]['slideIds']:b.concepts[cid]['slideIds'].append('lectures-p0771')
# Preserve pixel-only labels/arrows in the cited evidence, separate from generated explanations.
VISUAL={3:'Visual transcription: θ_d, θ̇_d and θ̈_d arrows approach a common summing icon; its output is δθ, then Gains produces τ; actual θ returns to its negative port.',11:'Visual transcription: arm output θ flows through Kin(θ); output X returns to the negative input of the Cartesian-error comparator.',20:'Visual transcription: δX enters Gains, output F enters J^T, output τ enters Arm, and actual θ returns via Kin(θ).',29:'Visual transcription: uppercase base axes X,Y,Z originate at O; lowercase x,y,z appear at endpoint P(x,y,z); dashed spherical outline has no numerical radius or link-length specification.',38:'Visual transcription: actual θ enters Kin(θ) to produce x; actual θ̇ enters J(θ) to produce ẋ; both measured task signals return to negative comparator inputs.',45:'Visual transcription: actual θ̇ enters the lower B_x(θ)+C_x(θ) block; its output and G(θ) add to the Cartesian force summation before J^T.',49:'Visual transcription: adaptation-law input branches carry E, Ė, θ and θ̇; its output updates the dynamic-model block. The outer actual-state labels are joint θ and θ̇.',50:'Visual transcription: θ̈_d, K_vĖ and K_pE enter the first sum; output τ′ enters Dynamic model; its output τ enters Arm.'}
for n,txt in VISUAL.items():
 for c in b.questions[n-1]['citations']:
  if c['physicalPage']!=771:c['evidenceText']=txt+'\n'+c['evidenceText']
save(frozen=True)
packet=R/f'audits/blind-{BATCH}.json'
manifest={'batchId':BATCH,'authorId':AUTHOR,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'questionCount':len(b.questions),'conceptCount':len(b.concepts),'physicalPages':list(NOTES),'sourceVersions':{'lectures':SHA},'blindPacketPath':str(packet.relative_to(R)),'blindPacketSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'questionHashConvention':'scripts.validate.question_hash; excludes only status and reviewIds','questions':[{'questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q)} for q in b.questions],'independentReviewStillRequired':True}
(R/f'audits/{BATCH}-frozen-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
coverage=[]
for p,(note,excluded) in NOTES.items():
 coverage.append({'physicalPage':p,'printedSlideNumber':str(p-750),'slideId':f'lectures-p{p:04d}','sourceSha256':SHA,'visualInspection':'complete','disposition':'excluded' if excluded else 'drafted-awaiting-independent-review','exclusionReason':excluded,'observedMeaningfulContent':note,'conceptIds':[c['id'] for c in b.concepts.values() if f'lectures-p{p:04d}' in c['slideIds']],'questionIds':[q['id'] for q in b.questions if any(c['physicalPage']==p for c in q['citations'])]})
assert all(row['exclusionReason'] or (row['conceptIds'] and row['questionIds']) for row in coverage)
(R/f'audits/{BATCH}-author-coverage-ledger.json').write_text(json.dumps({'batchId':BATCH,'status':'Author coverage proposal; independent substantive challenge required.','pageCount':len(coverage),'exclusions':sum(bool(x['exclusionReason']) for x in coverage),'pages':coverage},ensure_ascii=False,indent=2)+'\n')
assert all('correctOptionIds' not in q and 'solution' not in q and all('evidenceText' not in c for c in q['citations']) for q in json.loads(packet.read_text()))
print('FROZEN_PACKET_SHA256',manifest['blindPacketSha256'])
