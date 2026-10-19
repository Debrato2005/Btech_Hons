#!/usr/bin/env python3
"""L21 source-first author drafts; independent verification is required."""
import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from authoring_helpers import DraftBatch,formula,SHA
from validate import schema_errors,question_hash
AUTHOR='build_offline_study_interface:L21-author';BATCH='W05-L21'
b=DraftBatch(BATCH,5,'L21','Linear control of manipulators',637,AUTHOR)
INSPECTED_AT='2026-10-19T18:01:20+00:00'
NOTES={
637:('Title: Lecture 21, Linear Control of Manipulators, with author and institution.','Title and branding only.'),
638:('Learning objective is understanding the basics of linear control.','Learning-objective roadmap only.'),
639:('Contents list feedback, second-order systems, control-law partitioning, trajectory following and disturbances.','Contents roadmap only.'),
640:('Linear differential-equation models support linear control methods. Actual manipulator dynamics are nonlinear; justified approximations can permit linear theory.',None),
641:('Open-loop diagram: trajectory generator supplies desired position, velocity and acceleration to model-based torque computation. Torque is M(Θ_d)Θ̈_d+V(Θ_d,Θ̇_d)+G(Θ_d). No measured-output feedback branch exists. Perfect-model idealization also needs compatible initial state and no unmodeled disturbance. Stepper motors are an example of open-loop use, not universally incapable of feedback.',None),
642:('Feedback diagram returns actual Θ and Θ̇ to the controller; trajectory generator supplies three desired signals, torque drives robot. Signals are N×1 vectors, N is joint count. Sensors measure joint position and sometimes velocity. The repeated desired-only inverse-dynamics formula is a feedforward component, not a complete feedback law.',None),
643:('Servo error is E=Θ_d−Θ and Ė=Θ̇_d−Θ̇. A 4× PDF detail confirms the desired-velocity dot is present; OCR can miss it. Stability is explained informally as keeping errors small under moderate disturbances. Feedback must be designed for stability; its mere presence is not a guarantee.',None),
644:('Manipulator control is coupled MIMO. Independent joint control replaces it approximately with N SISO loops. The arm photograph is illustrative and adds no numbered kinematic data.',None),
645:('Mass–spring–damper diagram has positive x to the right and restoring/viscous forces −kx and −bẋ. The homogeneous equation is mẍ+bẋ+kx=0. m is mass, b viscous damping coefficient, k stiffness. Weak spring/heavy damping can be sluggish; stiff spring/light damping can oscillate, with formal threshold on following slides.',None),
646:('Characteristic polynomial ms²+bs+k=0 and roots [−b±√(b²−4mk)]/(2m). Pole locations determine response. Stability classifications require the relevant physical/gain signs, not discriminant alone.',None),
647:('Positive-parameter damping classification: discriminant positive gives real unequal overdamped poles; negative gives complex underdamped poles; zero gives critical damping. Fastest non-oscillatory language requires a fixed natural-frequency/model comparison, not arbitrary initial conditions or arbitrary design limits. The interactive link targets a local second_order_simulator_v2.html file not present in supplied files; no executable code is printed on this page.',None),
648:('Distinct real-root solution is c₁e^(s₁t)+c₂e^(s₂t), constants from initial position and velocity. Plot shows two negative real poles, s₁ farther left than s₂. The farther-left term decays faster for stable real poles; slow-pole dominance needs a nonzero slow-mode coefficient and a sufficiently late time.',None),
649:('Conjugate roots λ±iμ are expanded using Euler’s identity into e^(λt)[C₁cos(μt)+C₂sin(μt)]. Real motion requires the appropriate conjugate coefficients; C₁=c₁+c₂ and C₂=i(c₁−c₂). The final real constants can be written r cosδ and r sinδ.',None),
650:('Amplitude-phase form is r e^(λt) cos(μt−δ), with r from the real cosine/sine coefficients and δ=atan2(sine coefficient,cosine coefficient). The slide reuses lowercase constants after uppercase constants on page 649; do not apply that real amplitude formula directly to the earlier complex coefficients. Pole diagram shows a left-half-plane conjugate pair and decaying oscillations; decay assumes λ<0.',None),
651:('Normalized polynomial s²+2ζω_n s+ω_n²=0. ζ=b/(2√km), ω_n=√(k/m), λ=−ζω_n, and μ=ω_n√(1−ζ²) for the underdamped case. No damping has b=ζ=0; positive critical damping has ζ=1. Natural frequency is not damped oscillation frequency.',None),
652:('Repeated-root solution is (c₁+c₂t)e^(−bt/(2m)); the independent t factor is essential. Plot shows coincident negative real poles and non-oscillatory decay. The polynomial-times-exponential limit uses a>0. Fastest-response wording has the same scope qualification as page 647.',None),
653:('A right-directed actuator force f is added to the mass–spring–damper diagram, giving mẍ+bẋ+kx=f. Sensing and actuation can change the natural response.',None),
654:('Direct zero-reference feedback is f=−k_p x−k_v ẋ. The diagram routes position through k_p and velocity through k_v to negative summing inputs. Effective coefficients become b′=b+k_v and k′=k+k_p; inertia remains m.',None),
655:('Critical direct-feedback design uses b′=2√(mk′). Gains themselves may be negative while total effective damping/stiffness stay positive. Example m=b=k=1, desired k′=16 gives k_p=15,k_v=7 and repeated poles −4. For m>0, asymptotic stability requires both b′>0 and k′>0; equality cases need separate treatment.',None),
656:('Control-law partitioning separates a model-based portion that simplifies the plant from a servo portion designed around the simplified model.',None),
657:('Partitioned force f=αf′+β uses α=m and β=bẋ+kx. Exact matching cancels damping/stiffness, yielding ẍ=f′, a normalized acceleration input. Physical parameters remain in the model-based part. The actual plant is not physically stripped of mass, damping or stiffness.',None),
658:('Servo f′=−k_v ẋ−k_p x yields ẍ+k_v ẋ+k_p x=0. Critical damping is k_v=2√k_p for k_p>0. These normalized gains have different units and values from direct force-feedback gains; parameter independence assumes exact model compensation.',None),
659:('Partitioned diagram shows servo negative feedback, multiplication by m, and positive cancellation feedforward bẋ+kx. Example m=b=k=1,k_p=16 gives α=1,β=ẋ+x,k_v=8. Combined physical force equals −15x−7ẋ, matching the earlier direct design.',None),
660:('Trajectory following needs smooth desired x_d, ẋ_d and ẍ_d. Error e=x_d−x; servo acceleration f′=ẍ_d+k_v ė+k_p e. The feedback acts in error coordinates and includes desired acceleration feedforward.',None),
661:('Substitution yields ë+k_v ė+k_p e=0 under exact unit-mass model. Diagram has desired-minus-actual comparators, positive error gains and acceleration feedforward, then model-based scaling/cancellation. Any response wording means choosing this ideal second-order polynomial, not arbitrary realizable hardware performance.',None),
662:('Forced error model is printed ë+k_v ė+k_p e=f_dist. A high-resolution detail confirms the physical disturbance arrow enters a MINUS summing input after the mass gain. Thus a resisting physical force F_dist gives normalized error forcing F_dist/m; the reused symbol needs an explicit mass/unit convention. This is a forced second-order error model.',None),
663:('BIBO means bounded disturbance magnitude implies bounded error for a stable closed-loop transfer function. Printed max f_dist<a omits absolute value; an upper bound alone does not bound negative excursions. Closed-loop stability must be assumed, and bounded does not mean zero error.',None),
664:('For constant normalized error forcing d and stable positive k_p,k_v, steady-state derivatives vanish and e_ss=d/k_p. Larger positive k_p reduces magnitude for a fixed nonzero d. Error is never zero requires nonzero disturbance and finite gain; it is not true for zero forcing.',None),
665:('Integral action adds k_i∫e dt to servo and error equation. High-resolution rendering confirms the differentiated equation has e triple-dot and f_dist DOT on the right. Constant forcing has zero derivative after its onset. Stable steady state with k_i≠0 can yield e=0. The characteristic polynomial is s³+k_v s²+k_p s+k_i; positive gains alone do not guarantee stability. Initial integrator state and onset discontinuities must not be erased by differentiation.',None),
666:('Summary repeats linear approximation, feedback/MIMO-to-SISO approximation, damping classes, partitioning, trajectory errors and disturbance/integral control. Link it to the substantive earlier questions rather than padding with duplicate recall.',None),
667:('Craig third edition (2005) bibliographic reference.','Reference only; textbook contents are not provided on this page.'),
668:('Thank-you closing.','Closing only.')}
ISSUES=[
(641,'Exact feedforward is presented as needing a perfect model; matching initial state and absence of unmodeled forcing are additional prerequisites for exact desired motion.','Use explicitly ideal premises; do not promise disturbance correction without feedback.'),
(642,'The closed-loop diagram includes measurements, but its displayed torque equation uses only desired variables.','Identify it as the displayed feedforward model term, not a complete measurement-dependent controller.'),
(643,'Feedback and small-error stability wording is informal and can be read as an automatic guarantee.','Require a correctly designed stable closed loop; distinguish boundedness from asymptotic zero error.'),
(647,'Critical damping is described as the fastest response without a fully stated comparison class.','Use fixed positive mass/stiffness or natural frequency and the usual non-oscillatory comparison; do not claim universal minimum settling time for every initial condition.'),
(648,'The farther pole may be neglected is stated without amplitude/time qualifications.','Restrict to stable well-separated real poles, late times, and a nonzero slow-mode coefficient.'),
(650,'The real amplitude-phase constants reuse lowercase names previously used for complex exponential coefficients.','Explicitly define real cosine/sine coefficients before applying radius and atan2 formulas.'),
(657,'Parameter-independent servo design assumes exact model compensation.','Retain model mismatch, saturation and measurement limitations as qualifications, not contradictions to the ideal algebra.'),
(661,'Any response we wish overstates physical realizability.','Limit the claim to choosing the ideal second-order coefficients under the stated assumptions.'),
(662,'The diagram uses a subtractive physical force disturbance, whereas the scalar error equation uses the same symbol without division by mass.','Define normalized signed error forcing d=F_dist/m for this resisting-force convention, or explicitly set unit mass. Preserve the diagram minus sign.'),
(663,'The bounded-input condition omits absolute value and the stable-loop hypothesis.','Use sup |d(t)|<∞ and a stable transfer function, not merely an upper bound or arbitrary gains.'),
(664,'Error is never zero omits the zero-disturbance special case.','Assume a fixed nonzero constant forcing and finite positive gain when asserting a nonzero offset.'),
(665,'Integral action eliminates offset only when the augmented loop is stable and the forcing settles to a constant; positive gains alone are insufficient.','Retain the printed disturbance derivative correctly and state stability/nonzero integral gain assumptions.')]
def add(p,key,title,stem,opts,why,**kw):
 correct=list(kw.pop('correct',(0,)));k=len(b.questions)%4;opts=opts[k:]+opts[:k];correct=[(i-k)%4 for i in correct]
 conflict_pages=kw.pop('conflict_pages',None)
 q=b.add(p,key,title,stem,[o[0] for o in opts],correct,why,[o[1] for o in opts],**kw)
 q['options'].sort(key=lambda o:o['id'])
 for c in q['citations']:c['locator']=f"Lecture 21, physical PDF page {c['physicalPage']}, printed slide {c['physicalPage']-636}: {title}"
 if q.get('conflictResolution'):
  pages=conflict_pages or ([p] if isinstance(p,int) else p);q['conflictResolution'].update(sourceId='lectures',sourceSha256=SHA,physicalPages=pages)
  for c in q['citations']:c['role']='conflict' if c['physicalPage'] in pages else 'premise'
 return q

def save(frozen=False):
 b.save();path=R/f'data/question-batches/{BATCH}.json';data=json.loads(path.read_text());data['sourceIssues']=[{'physicalPage':p,'description':desc,'qualification':qual,'status':'preserved with explicit scope; not globally resolved'} for p,desc,qual in ISSUES];data['coverageNote']='All 32 actual lecture pages inspected; question coverage is a draft proposal until independent source and completeness review.';path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 maps={s['physicalPage']:s for s in map(json.loads,(R/'sources/page_maps/lectures.jsonl').read_text().splitlines())};slides=[]
 for p,(note,excluded) in NOTES.items():
  s=copy.deepcopy(maps[p]);s['disposition']='excluded' if excluded else 'examinable';s['exclusionReason']=excluded;s['conceptIds']=[c['id'] for c in b.concepts.values() if s['id'] in c['slideIds']]
  s['visualInspection']={'status':'complete','inspectorId':AUTHOR,'inspectedAt':INSPECTED_AT,'method':'rendered_page','notes':note+' Actual readable 1800×1013 source pixels and extracted text were inspected; ambiguous dots/signs on pages 643,662,665 were re-rendered at 4× PDF resolution.','previewSha256':hashlib.sha256((R/s['previewPath']).read_bytes()).hexdigest(),'dimensions':[1800,1013]};slides.append(s)
 for typ,rows in [('question',b.questions),('concept',list(b.concepts.values())),('slide',slides)]:
  schema=json.loads((R/f'data/schema.{typ}.json').read_text());errors=[e for row in rows for e in schema_errors(row,schema)];assert not errors,(typ,errors)
 (R/f'data/inspection-batches/{BATCH}.json').write_text(json.dumps({'batchId':BATCH,'slides':slides},ensure_ascii=False,indent=2)+'\n')
 (R/f'audits/{BATCH}-author-progress.json').write_text(json.dumps({'frozen':frozen,'authorId':AUTHOR,'questionCount':len(b.questions),'conceptCount':len(b.concepts),'inspectedPages':list(NOTES),'missingSupplement':'The PDF links to local second_order_simulator_v2.html on page 647; that file is not in the supplied repository. No source code is printed in this lecture.','next':'Independent review required.' if frozen else 'Continue source-bound question drafting; inspection is not verified question coverage.'},indent=2)+'\n')
 print('Saved',len(b.questions),'L21 drafts;',len(b.concepts),'concepts;',len(slides),'page inspections; frozen=',frozen)
save()

FF=formula('τ=M(Θ_d)Θ̈_d+V(Θ_d,Θ̇_d)+G(Θ_d)',{'τ':'commanded joint-torque vector','Θ_d':'desired joint-angle vector','Θ̇_d':'desired joint-velocity vector','Θ̈_d':'desired joint-acceleration vector','M':'joint-space inertia matrix evaluated on the desired trajectory','V':'velocity-dependent joint-torque vector evaluated on the desired trajectory','G':'gravity joint-torque vector evaluated at desired joint position'},{'τ,V,G':'N·m per revolute joint','Θ_d':'rad','Θ̇_d':'rad/s','Θ̈_d':'rad/s²','M':'kg·m² with radians treated dimensionlessly'},['All joints in this example are revolute; exact feedforward assumes an accurate model and compatible initial state.'])
ERR=formula('E=Θ_d−Θ; Ė=Θ̇_d−Θ̇',{'E':'joint-position servo-error vector','Ė':'joint-velocity servo-error vector','Θ_d,Θ':'desired and measured joint-angle vectors','Θ̇_d,Θ̇':'desired and measured joint-velocity vectors'},{'E,Θ_d,Θ':'rad per revolute joint','Ė,Θ̇_d,Θ̇':'rad/s per revolute joint'},['Desired and actual signals use matching joints, frames, units and time.'])
MSD=formula('mẍ+bẋ+kx=f',{'m':'positive translating mass','b':'linear viscous damping coefficient','k':'linear spring stiffness','x':'displacement from the equilibrium reference','ẋ':'velocity','ẍ':'acceleration','f':'externally applied actuator force in the positive x direction'},{'m':'kg','b':'N·s/m','k':'N/m','x':'m','ẋ':'m/s','ẍ':'m/s²','f':'N'},['One translational DOF, ideal linear spring and viscous damper; f=0 for the natural response.'])
ROOT=formula('ms²+bs+k=0; s₁,₂=[−b±√(b²−4mk)]/(2m)',{'m':'positive mass','b':'viscous damping coefficient','k':'spring stiffness','s':'complex exponential growth/decay rate','s₁,s₂':'characteristic roots/poles'},{'m':'kg','b':'N·s/m','k':'N/m','s,s₁,s₂':'s⁻¹'},['Constant coefficients and m>0; damping classifications additionally require the stated coefficient signs.'])
add(640,'linear-approximation','Linear approximation of manipulator dynamics',
 'Why can linear control theory be useful for a manipulator whose full equations of motion are nonlinear?',[
 ('A justified approximation can provide a linear differential-equation model over a suitable operating regime.','The lecture distinguishes the full nonlinear model from a useful approximation.'),
 ('Writing joint angles as a vector automatically makes their dynamics linear.','Vector notation does not remove nonlinear dependence on angles and velocities.'),
 ('Using position sensors removes all nonlinear terms from the mechanical equations.','Measurement alone does not change the underlying dynamics.'),
 ('Every multi-joint manipulator has an exactly linear model at all configurations and speeds.','The slide explicitly describes the more complete dynamics as nonlinear.')],
 'Linear methods can be applied to a suitable approximate model. Their usefulness does not establish global exactness for the full manipulator.',difficulty='easy')
add(641,'feedforward','Open-loop model-based torque and assumptions',
 'Which signals go from the trajectory generator into the open-loop controller in the shown diagram?',[
 ('Desired joint position, velocity and acceleration.','The three arrows are Θ_d, Θ̇_d and Θ̈_d.'),
 ('Measured position, measured velocity and measured torque only.','There are no measured-state return arrows in this open-loop figure.'),
 ('Desired end-effector position alone, without joint derivatives.','The diagram explicitly supplies joint-space position and both time derivatives.'),
 ('Position error, velocity error and integrated error.','Those error-feedback signals are not the trajectory-generator outputs in this figure.')],
 'The controller evaluates the desired-trajectory model using Θ_d, Θ̇_d and Θ̈_d, then sends torque τ to the robot.',typ='diagram',difficulty='easy',formulas=[FF])
add(641,'feedforward','Open-loop model-based torque and assumptions',
 'An unmeasured external torque changes the robot’s actual motion while its desired trajectory stays unchanged. What corrective action does the shown purely open-loop controller obtain from the actual error?',[
 ('None from measured error, because the diagram contains no actual-state feedback path.','Its command remains based on the desired trajectory and model.'),
 ('It automatically adds a proportional torque based on measured position error.','No measured position-error signal is present in the shown controller.'),
 ('It automatically integrates the disturbance until the position error vanishes.','There is no integral error path in the diagram.'),
 ('It updates the desired acceleration from an actual-velocity return signal.','The figure supplies desired acceleration from the generator and has no velocity return branch.')],
 'The open-loop architecture cannot use an error it does not measure. The slide’s disturbance-rejection warning refers to this absence of error-driven correction.',typ='scenario',difficulty='easy')
add(641,'feedforward','Open-loop model-based torque and assumptions',
 'At a desired state of a two-revolute-joint model, M=[[2,1],[1,3]], Θ̈_d=[1,−2]ᵀ, V=[1,0]ᵀ and G=[3,4]ᵀ in consistent SI units. What torque vector follows from the displayed feedforward law?',[
 ('[4,−1]ᵀ N·m.','MΘ̈_d=[0,−5]ᵀ, then adding V and G gives [4,−1]ᵀ.'),
 ('[6,−2]ᵀ N·m.','This drops the off-diagonal inertia terms and uses only the diagonal products.'),
 ('[0,−5]ᵀ N·m.','This includes only the inertia contribution and omits V and G.'),
 ('[−4,−9]ᵀ N·m.','This subtracts V and G instead of adding them as prescribed.')],
 'Matrix multiplication must include the joint-coupling terms. The inertial torque is [2−2,1−6]ᵀ=[0,−5]ᵀ, and the total is [4,−1]ᵀ.',typ='numerical',difficulty='medium',steps=['Multiply the first matrix row by the acceleration vector: 2·1+1·(−2)=0.','Multiply the second row: 1·1+3·(−2)=−5.','Add the corresponding V and G entries to obtain [4,−1]ᵀ.'],formulas=[FF],assumptions=['All quantities are evaluated at the same desired state; inertia entries use kg·m², accelerations rad/s², and V/G entries N·m.'])
add(641,'feedforward','Open-loop model-based torque and assumptions',
 'Which premises support exact tracking by the ideal desired-trajectory inverse-dynamics feedforward law, rather than merely an accurate computed torque?',[
 ('An exact model, compatible desired and actual initial state, and no unmodeled forcing.','The desired motion must also be the solution selected by the plant’s initial state and actual forcing.'),
 ('An exact model alone, regardless of actual initial position and velocity.','The same input does not erase an arbitrary initial-state mismatch without an error-correction mechanism.'),
 ('A matching initial position only; initial velocity and disturbance torque are irrelevant.','Velocity is an independent initial condition for second-order dynamics, and disturbances change the motion.'),
 ('A desired trajectory with no derivatives, because inverse dynamics does not use acceleration.','The displayed inverse-dynamics input explicitly requires desired velocity and acceleration.')],
 'The slide’s perfect-model condition is necessary for its ideal prediction but not a complete exact-tracking statement. Compatible initial conditions and no unmodeled input are also needed.',difficulty='medium',conflict='The slide lists a perfect model but does not explicitly state compatible initial conditions when describing ideal open-loop trajectory following.')
add([641,642],'feedback-diagram','Feedback signals and incomplete displayed law',
 'What structural change distinguishes the closed-loop diagram from the preceding open-loop one?',[
 ('Actual joint position and velocity return from the robot to the controller.','These measured-state branches allow the controller to react to actual motion.'),
 ('The desired acceleration arrow is removed.','The closed-loop diagram still includes desired acceleration.'),
 ('The torque command is fed directly back into the trajectory generator instead of driving the robot.','Torque still drives the robot, and measured state returns to the controller.'),
 ('The actual output is replaced by the desired state, so no sensor information is used.','The feedback branches explicitly carry actual position and velocity.')],
 'The closed-loop figure adds actual Θ and Θ̇ return paths while retaining the desired trajectory signals and torque output.',typ='diagram',difficulty='easy')
add(642,'feedback-diagram','Feedback signals and incomplete displayed law',
 'For the N-joint control diagram, what is the size of each joint position, velocity, acceleration or torque signal vector?',[
 ('N×1.','Each vector contains one scalar quantity per joint.'),
 ('N×N.','That is the inertia-matrix size, not the size of each listed signal vector.'),
 ('3×1 for every manipulator, regardless of N.','The signals are joint-space vectors, not always three-dimensional Cartesian positions.'),
 ('1×1 even when N>1.','A scalar cannot represent all N joint entries without a separate channel interpretation.')],
 'The slide states that the signals are N×1 vectors, where N is the number of joints. The model matrix multiplying an acceleration vector is a different object.',typ='definition',difficulty='easy')
add(642,'feedback-diagram','Feedback signals and incomplete displayed law',
 'The page shows a feedback diagram but repeats τ=M(Θ_d)Θ̈_d+V(Θ_d,Θ̇_d)+G(Θ_d). What limitation of this displayed equation should be recognized?',[
 ('By itself it contains only desired-trajectory feedforward terms; a measurement-dependent correction is not written in that equation.','The measured-state arrows in the diagram are not represented by any actual-state/error term in the expression.'),
 ('It already contains explicit proportional and derivative error gains through the symbols M and G.','M is inertia and G is gravity; neither is an explicit error-feedback gain here.'),
 ('It proves that actual-state measurements are never needed in closed-loop control.','The diagram and accompanying sensor discussion explicitly include feedback.'),
 ('The desired acceleration term is itself measured position error.','Acceleration and position error are distinct signals.')],
 'The expression can be identified as a feedforward component. It should not be presented as a complete feedback law merely because it appears beside a feedback architecture.',difficulty='medium',conflict='The page places the desired-only inverse-dynamics expression alongside a closed-loop diagram that also uses actual position and velocity.')
add(643,'servo-error','Servo error and derivative sign conventions',
 'A joint has desired position 0.8 rad and measured position 0.5 rad; desired velocity is −0.2 rad/s and measured velocity is 0.1 rad/s. Using the lecture’s desired-minus-actual convention, what are E and Ė?',[
 ('E=0.3 rad and Ė=−0.3 rad/s.','Subtract actual from desired separately for position and velocity.'),
 ('E=−0.3 rad and Ė=0.3 rad/s.','This uses the opposite actual-minus-desired convention.'),
 ('E=0.3 rad and Ė=0.3 rad/s.','The position sign is right, but the velocity subtraction is reversed.'),
 ('E=0.3 rad and Ė=0.7 rad/s.','This incorrectly subtracts actual velocity from desired position, mixing units and signals.')],
 'E=0.8−0.5=0.3 rad, and Ė=−0.2−0.1=−0.3 rad/s. The desired-velocity dot is present in the actual slide.',typ='numerical',difficulty='medium',steps=['Compute the position difference 0.8−0.5=0.3 rad.','Compute the velocity difference −0.2−0.1=−0.3 rad/s.'],formulas=[ERR])
add(643,'stability-scope','Feedback and stability qualifications',
 'Which statement is the defensible interpretation of feedback helping to reduce servo error?',[
 ('A suitably designed feedback law can reduce errors, but the presence of a feedback path alone does not prove stability.','Gain signs, dynamics and implementation must still produce a stable closed loop.'),
 ('Every feedback connection is stable regardless of gain sign or magnitude.','Incorrect feedback can enlarge errors rather than suppress them.'),
 ('Stability means the error is exactly zero at every instant, including an initial mismatch.','Stable error transients may be nonzero while remaining bounded or converging.'),
 ('If error is bounded, it must converge to zero under every bounded disturbance.','A bounded disturbance can produce a nonzero bounded or steady error.')],
 'The slide gives an informal stability objective. It should not be read as a universal guarantee from feedback alone, nor as a claim that bounded error must always vanish.',difficulty='medium',conflict='The slide says feedback reduces error and hence makes the system stable; correct controller design and the distinction between bounded and vanishing error must be retained.')
add(644,'mimo-siso','Coupled manipulator versus independent joint approximation',
 'What does independent joint control do to the manipulator’s coupled MIMO control problem?',[
 ('It approximately treats the N joints as N separate SISO loops.','This is the simplification explicitly described by the lecture.'),
 ('It proves all inter-joint coupling terms are physically zero.','Treating joints separately does not prove that the true dynamics are uncoupled.'),
 ('It replaces the N-joint robot by one single SISO loop carrying every joint error as one scalar.','The slide describes N separate loops, not one scalar aggregate loop.'),
 ('It requires every joint to share the same trajectory and same torque at all times.','Independent loops need not have identical setpoints or control outputs.')],
 'Independent joint control is an approximate simplification of the coupled multi-input, multi-output system. Its adequacy depends on the dynamics and operating conditions.',typ='definition',difficulty='easy')
add(645,'mass-spring-damper','Mass–spring–damper force balance',
 'For positive displacement x and positive velocity ẋ in the diagram’s rightward coordinate, which directions do the linear spring and viscous-damper forces on the mass have?',[
 ('Both act leftward: −kx and −bẋ.','The spring restores toward equilibrium and the viscous force opposes the positive velocity.'),
 ('Both act rightward: +kx and +bẋ.','This would make the passive elements reinforce the stated displacement and velocity.'),
 ('The spring acts rightward and the damper leftward.','The spring restoring sign is reversed for positive displacement.'),
 ('The spring acts leftward and the damper rightward.','The viscous damping sign is reversed for positive velocity.')],
 'The free-body diagram shows leftward kx and bẋ arrows for the stated positive x and ẋ. Newton’s law gives mẍ=−kx−bẋ.',typ='diagram',difficulty='easy',assumptions=['x and ẋ are both positive; a force component reverses if its corresponding displacement or velocity changes sign.'],formulas=[MSD])
add(645,'mass-spring-damper','Mass–spring–damper force balance',
 'For m=2 kg, b=3 N·s/m, k=8 N/m, x=0.5 m and ẋ=−1 m/s, with no applied force, what is ẍ?',[
 ('−0.5 m/s².','The spring force is −4 N and damping force is +3 N, leaving −1 N on a 2 kg mass.'),
 ('−3.5 m/s².','This incorrectly makes the damping force negative even though velocity is negative.'),
 ('0.5 m/s².','This reverses the net-force sign.'),
 ('−1 m/s².','This gives the net force numerically but omits division by mass.')],
 'Use ẍ=(−kx−bẋ)/m=(−4+3)/2=−0.5 m/s². Damping opposes velocity, so its force is positive in this case.',typ='numerical',difficulty='medium',steps=['Calculate the restoring spring force −8·0.5=−4 N.','Calculate the damping force −3·(−1)=+3 N.','Divide their −1 N sum by 2 kg.'],formulas=[MSD])
add(645,'mass-spring-damper','Mass–spring–damper force balance',
 'Which friction model is represented by the force term −bẋ in this linear mass–spring–damper equation?',[
 ('Linear viscous damping proportional to velocity.','The coefficient multiplies velocity directly.'),
 ('A constant-magnitude Coulomb force proportional only to sign(ẋ).','That would use a sign function and is not the displayed linear term.'),
 ('A restoring force proportional to displacement.','That role is already represented by −kx.'),
 ('An inertial force proportional to acceleration with coefficient b.','The mass m, not b, multiplies acceleration.')],
 'Although the slide informally calls b friction, its equation specifically models viscous damping. The units of b are force divided by velocity.',typ='definition',difficulty='easy',formulas=[MSD])
add([645,646],'characteristic','Characteristic roots and response parameters',
 'Substituting a nonzero exponential mode x(t)=Ce^(st) into mẍ+bẋ+kx=0 leads to which characteristic equation?',[
 ('ms²+bs+k=0.','Differentiation gives factors s and s², and the common nonzero exponential factor cancels.'),
 ('ms+bs²+k=0.','This interchanges the mass and damping derivative orders.'),
 ('ms²+bs−k=0.','The restoring stiffness term has a positive coefficient on the left side.'),
 ('m+b+k=0.','This discards the time-derivative factors that determine the modal rate.')],
 'For x=Ce^(st), ẋ=sx and ẍ=s²x. Factoring x gives ms²+bs+k=0.',typ='derivation',difficulty='medium',steps=['Differentiate the exponential once and twice to obtain sx and s²x.','Substitute into the differential equation.','Cancel the nonzero modal factor to obtain the characteristic polynomial.'],formulas=[ROOT])
add(646,'characteristic','Characteristic roots and response parameters',
 'For m=1 kg, b=5 N·s/m and k=6 N/m, which poles follow from the characteristic equation?',[
 ('−2 s⁻¹ and −3 s⁻¹.','The polynomial s²+5s+6 factors as (s+2)(s+3).'),
 ('2 s⁻¹ and 3 s⁻¹.','This reverses the signs of the stable roots.'),
 ('−5 s⁻¹ and −6 s⁻¹.','The coefficients are not themselves the roots.'),
 ('−2.5±i√6 s⁻¹.','The discriminant is 25−24=1>0, so the roots are real rather than complex.')],
 'The characteristic polynomial factors into (s+2)(s+3). Both real roots are negative and unequal.',typ='numerical',difficulty='medium',steps=['Form s²+5s+6=0.','Factor as (s+2)(s+3)=0.','Set each factor to zero.'],formulas=[ROOT])
save()

DR=formula('ω_n=√(k/m); ζ=b/(2√(km)); λ=−ζω_n; μ=ω_n√(1−ζ²)',{'ω_n':'undamped natural angular frequency','ζ':'damping ratio','λ':'real part of each underdamped pole','μ':'positive damped oscillation angular frequency','m':'positive mass','b':'viscous damping coefficient','k':'positive spring stiffness'},{'ω_n,μ':'rad/s','λ':'s⁻¹','ζ':'dimensionless','m':'kg','b':'N·s/m','k':'N/m'},['m,k>0; the real damped-frequency expression applies to 0≤ζ<1, and decaying underdamping requires ζ>0.'])
REAL=formula('x(t)=c₁e^(s₁t)+c₂e^(s₂t)',{'x(t)':'free displacement response','t':'time','s₁,s₂':'distinct real characteristic roots','c₁,c₂':'real modal amplitudes fixed by initial position and velocity'},{'x,c₁,c₂':'m','t':'s','s₁,s₂':'s⁻¹'},['Distinct real roots; both must be negative for a decaying response.'])
OSC=formula('x(t)=e^(λt)[A cos(μt)+B sin(μt)]=r e^(λt)cos(μt−δ); r=√(A²+B²); δ=atan2(B,A)',{'x(t)':'real free displacement response','t':'time','λ':'real part of the conjugate poles','μ':'positive imaginary part/damped angular frequency','A,B':'real cosine and sine amplitudes fixed by initial conditions','r':'nonnegative amplitude coefficient','δ':'phase angle measured with atan2(y,x) convention'},{'x,A,B,r':'m','t':'s','λ':'s⁻¹','μ':'rad/s','δ':'rad'},['Complex-conjugate poles; A and B are real coefficients, not the earlier complex exponential amplitudes; λ<0 for decay.'])
CRIT=formula('x(t)=(c₁+c₂t)e^(−at), a=b/(2m)=√(k/m)',{'x(t)':'critically damped free displacement','t':'time','c₁':'initial displacement coefficient','c₂':'coefficient of the independent t mode','a':'positive repeated-pole decay rate','b':'critical viscous damping coefficient','m':'positive mass','k':'positive stiffness'},{'x,c₁':'m','c₂':'m/s','t':'s','a':'s⁻¹','b':'N·s/m','m':'kg','k':'N/m'},['b=2√(mk)>0, m,k>0 and a>0.'])
add([646,647],'damping-class','Damping classes and discriminant conditions',
 'For m>0, k>0 and b>0, which discriminant relation corresponds to an underdamped natural response?',[
 ('b²<4mk.','The negative discriminant gives a conjugate pair with nonzero imaginary parts and negative real part.'),
 ('b²>4mk.','This gives two real unequal roots and an overdamped response.'),
 ('b²=4mk.','This is the repeated-root critical-damping boundary.'),
 ('b<0 with no condition on b²−4mk.','Negative damping violates the premise and does not establish a decaying underdamped response.')],
 'With the positive physical parameters stated, b²−4mk<0 produces complex-conjugate poles with real part −b/(2m)<0.',typ='definition',difficulty='easy',formulas=[ROOT])
add([646,647],'damping-class','Damping classes and discriminant conditions',
 'For m=k=1 in consistent units, classify b=1, b=2 and b=3 in that order.',[
 ('Underdamped, critically damped, overdamped.','Their discriminants are −3, 0 and 5.'),
 ('Overdamped, critically damped, underdamped.','This reverses the effects of low and high positive damping.'),
 ('Underdamped, overdamped, critically damped.','Critical damping occurs at b=2, not b=3.'),
 ('Critically damped, underdamped, overdamped.','The b=1 discriminant is negative, not zero.')],
 'The critical threshold is b²=4mk=4. Comparing each squared damping coefficient with 4 gives the three stated classes.',typ='numerical',difficulty='medium',steps=['For b=1, b²−4mk=1−4=−3.','For b=2, the discriminant is zero.','For b=3, the discriminant is 9−4=5.'],formulas=[ROOT])
add([647,652],'critical-scope','Scope of the fastest non-oscillatory description',
 'What qualification is needed when using the lecture’s description of critical damping as the fastest non-oscillatory response?',[
 ('It concerns the usual fixed-natural-frequency second-order comparison, not a universal minimum settling time over arbitrary gains, initial states and actuator constraints.','Changing the natural frequency or response criterion changes the comparison.'),
 ('Critical damping guarantees zero settling time for every nonzero initial displacement.','The critically damped transient decays over time rather than vanishing instantaneously.'),
 ('Every critically damped system is faster than every underdamped or overdamped system with any natural frequency.','A slow critical system need not outperform a much faster system with different parameters.'),
 ('The description means all initial velocities produce an identical monotonic response.','Initial velocity affects the modal coefficients and can change transient behavior.')],
 'The repeated negative pole gives the familiar boundary between oscillatory and overdamped behavior for fixed natural frequency. The shorthand should not be turned into an unqualified optimization theorem.',difficulty='medium',conflict='Pages 647 and 652 describe critical damping as fastest without fully specifying the comparison class or initial-condition and hardware limits.',conflict_pages=[647,652])
add(648,'real-modes','Real modes, initial conditions and dominant poles',
 'Which two quantities determine the constants in the second-order free response x(t)=c₁e^(s₁t)+c₂e^(s₂t), once distinct roots are fixed?',[
 ('Initial position and initial velocity.','They give two independent equations for the two constants.'),
 ('Initial position alone, regardless of initial velocity.','One scalar condition is generally insufficient to determine both amplitudes.'),
 ('Only the pole locations; initial state does not affect amplitudes.','The poles describe modal rates, not how strongly each mode is excited.'),
 ('Only the final equilibrium position, without initial information.','Many different transients can approach the same equilibrium.')],
 'At t=0, x(0)=c₁+c₂ and ẋ(0)=s₁c₁+s₂c₂. Distinct roots make this a solvable two-equation system.',typ='definition',difficulty='easy',formulas=[REAL])
add(648,'real-modes','Real modes, initial conditions and dominant poles',
 'For poles s₁=−2 s⁻¹ and s₂=−3 s⁻¹, x(0)=1 m and ẋ(0)=0, which free response satisfies both initial conditions?',[
 ('x(t)=3e^(−2t)−2e^(−3t) m.','Its initial value is 3−2=1 and initial derivative is −6+6=0.'),
 ('x(t)=e^(−2t) m.','It has the right initial position but initial velocity −2 m/s.'),
 ('x(t)=−2e^(−2t)+3e^(−3t) m.','It has initial position 1 but initial velocity 4−9=−5 m/s.'),
 ('x(t)=3e^(−2t)+2e^(−3t) m.','Its initial position is 5 m, not 1 m.')],
 'Solving c₁+c₂=1 and −2c₁−3c₂=0 gives c₁=3 m and c₂=−2 m.',typ='numerical',difficulty='medium',steps=['Apply x(0)=1 to get c₁+c₂=1.','Apply ẋ(0)=0 to get −2c₁−3c₂=0.','Solve for c₁=3 and c₂=−2 and substitute into the modal response.'],formulas=[REAL])
add(648,'real-modes','Real modes, initial conditions and dominant poles',
 'In the pole diagram, s₁ lies farther left on the negative real axis than s₂. With nonzero comparable modal amplitudes, which term dominates sufficiently late in the response?',[
 ('The s₂ term, because the pole nearer the origin has the slower exponential decay.','The farther-left s₁ exponential disappears more rapidly.'),
 ('The s₁ term, because a larger pole magnitude always makes a response persist longer.','For negative real poles, greater magnitude gives faster decay.'),
 ('Both terms must remain equal at every time because both poles are real.','Different real decay rates do not preserve equal amplitudes over time.'),
 ('Neither term decays, because zero imaginary parts imply constant displacement.','Negative real parts produce exponential decay even without oscillation.')],
 'For stable negative real poles, the mode closer to the origin is slower. Late-time dominance additionally requires that this mode actually has a nonzero coefficient.',typ='diagram',difficulty='medium',assumptions=['Distinct stable poles, nonzero comparable initial modal amplitudes, and sufficiently late time.'])
add(648,'real-modes','Real modes, initial conditions and dominant poles',
 'A free response has poles −1 and −20 s⁻¹, but its coefficient of e^(−t) is exactly zero. Which caution applies to the “dominant pole” shortcut?',[
 ('The slow pole is not excited in this response, so its exponential cannot dominate despite its location.','Actual modal amplitudes matter as well as pole positions.'),
 ('The missing coefficient becomes nonzero automatically after a long time in the homogeneous solution.','A fixed zero modal coefficient remains zero without added forcing.'),
 ('The −20 pole becomes unstable because the −1 mode is absent.','Removing an excited mode does not change the pole sign.'),
 ('A zero slow-mode coefficient makes the displacement identically zero even if the fast coefficient is nonzero.','The fast exponential can still contribute a nonzero decaying response.')],
 'The homogeneous response is a weighted modal sum. A pole with zero weight is absent from this particular trajectory, so pole separation alone does not establish its dominance.',typ='scenario',difficulty='medium',conflict='The slide’s pole-neglect approximation does not explicitly mention modal amplitudes or the time interval of validity.')
add(649,'complex-modes','Conjugate poles and real sinusoidal form',
 'For roots λ+iμ and λ−iμ of a real system, which form expresses the corresponding real motion using real constants A and B?',[
 ('e^(λt)[A cos(μt)+B sin(μt)].','Euler’s identity combines the conjugate exponentials into real sine and cosine terms.'),
 ('e^(μt)[A cos(λt)+B sin(λt)].','This swaps the decay rate and oscillation frequency.'),
 ('A cos(μt)+B sin(μt), with no exponential factor for every λ.','The exponential envelope is required unless λ=0.'),
 ('e^(λt)[A cos(μt)+iB sin(μt)] for arbitrary real A and B.','The additional i generally makes the displacement complex rather than real.')],
 'Euler’s identity separates the common exponential envelope from the real oscillatory basis. For decaying underdamping, λ<0 and μ>0.',typ='derivation',difficulty='medium',steps=['Factor e^(λt) out of the conjugate exponential terms.','Expand e^(±iμt) using cosine and sine.','Combine coefficients into real cosine and sine amplitudes for a real response.'],formulas=[OSC])
add(649,'complex-modes','Conjugate poles and real sinusoidal form',
 'Let x(t)=c₁e^((λ+iμ)t)+c₂e^((λ−iμ)t). Which coefficient mapping follows from Euler’s identity for x(t)=e^(λt)[A cos(μt)+B sin(μt)]?',[
 ('A=c₁+c₂ and B=i(c₁−c₂).','The cosine terms add, while the sine terms have opposite imaginary signs.'),
 ('A=c₁−c₂ and B=i(c₁+c₂).','This reverses which coefficients add and subtract.'),
 ('A=c₁+c₂ and B=c₁−c₂ without i.','The sine contribution includes the imaginary-unit factor from Euler’s identity.'),
 ('A=c₁c₂ and B=c₁/c₂.','Products and ratios do not arise when linearly combining the exponentials.')],
 'Expanding both exponentials gives cosine coefficient c₁+c₂ and sine coefficient i(c₁−c₂). If c₂ is the conjugate of c₁, these resulting coefficients are real.',typ='derivation',difficulty='medium',steps=['Use e^(iμt)=cos(μt)+i sin(μt).','Use e^(−iμt)=cos(μt)−i sin(μt).','Collect cosine and sine coefficients separately.'],formulas=[formula('A=c₁+c₂; B=i(c₁−c₂)',{'A,B':'real cosine/sine amplitudes when c₂ is the conjugate of c₁','c₁,c₂':'possibly complex exponential-mode coefficients','i':'imaginary unit with i²=−1'},{'A,B,c₁,c₂':'displacement units','i':'dimensionless'},['A real response is obtained with conjugate coefficient pairing.'])])
add([649,650],'amplitude-phase','Amplitude, phase and coefficient notation',
 'For real cosine/sine coefficients A=−3 m and B=4 m, what amplitude-phase description matches A cos(μt)+B sin(μt)=r cos(μt−δ)?',[
 ('r=5 m and δ=atan2(4,−3), in quadrant II.','The amplitude is √(9+16), and atan2 keeps the signs of both coefficients.'),
 ('r=5 m and δ=atan2(−3,4), in quadrant IV.','This swaps the sine and cosine inputs to atan2.'),
 ('r=1 m and δ=atan2(4,−3).','Amplitude is not the algebraic sum −3+4.'),
 ('r=5 m and δ=atan(4/−3) with its principal quadrant-IV value.','The simple ratio loses the required quadrant and reverses both reconstructed coefficient signs.')],
 'Expanding r cos(μt−δ) gives r cosδ cosμt+r sinδ sinμt. Therefore A=r cosδ, B=r sinδ and atan2(B,A) selects the correct quadrant.',typ='numerical',difficulty='medium',steps=['Compute r=√(A²+B²)=5 m.','Use δ=atan2(B,A)=atan2(4,−3).','A negative cosine coefficient and positive sine coefficient place δ in quadrant II.'],formulas=[OSC],assumptions=['A and B are the real trigonometric coefficients, not the earlier complex exponential coefficients.'],conflict='Page 650 reuses lowercase c₁,c₂ after page 649 introduced real coefficients with uppercase names; the question explicitly defines the real coefficients to avoid ambiguity.',conflict_pages=[650])
add(650,'amplitude-phase','Amplitude, phase and coefficient notation',
 'Which pole feature determines exponential decay of the oscillation envelope in the shown left-half-plane conjugate-pole diagram?',[
 ('The negative real part λ.','The envelope contains e^(λt), which decays when λ<0.'),
 ('The sign of μ alone, regardless of λ.','μ determines oscillatory frequency; conjugate signs do not determine exponential growth or decay.'),
 ('The phase δ alone, regardless of λ.','Phase shifts the oscillation but not its envelope decay rate.'),
 ('The initial amplitude r alone, regardless of λ.','Amplitude sets the initial scale; λ controls its exponential time evolution.')],
 'The plotted conjugate poles lie to the left of the imaginary axis. Their negative real part produces the decreasing envelope, while their imaginary parts produce oscillation.',typ='diagram',difficulty='easy',formulas=[OSC])
add([651,646],'damping-parameters','Damping ratio, natural frequency and poles',
 'For m=4 kg, b=8 N·s/m and k=16 N/m, what are the damping ratio and undamped natural frequency?',[
 ('ζ=0.5 and ω_n=2 rad/s.','ω_n=√(16/4)=2 and ζ=8/(2√64)=0.5.'),
 ('ζ=1 and ω_n=2 rad/s.','This omits the factor two in the damping-ratio denominator.'),
 ('ζ=0.5 and ω_n=4 rad/s.','This uses k/m rather than its square root for natural frequency.'),
 ('ζ=2 and ω_n=0.5 rad/s.','This reverses the key ratios instead of applying the stated definitions.')],
 'Normalize the polynomial by mass and compare with s²+2ζω_n s+ω_n². The parameters are ζ=0.5 and ω_n=2 rad/s.',typ='numerical',difficulty='medium',steps=['Compute ω_n=√(k/m)=√4=2 rad/s.','Compute 2√(km)=2√64=16 N·s/m.','Divide b by that quantity: ζ=8/16=0.5.'],formulas=[DR])
add(651,'damping-parameters','Damping ratio, natural frequency and poles',
 'For ω_n=2 rad/s and ζ=0.5, what are λ and the positive damped frequency μ?',[
 ('λ=−1 s⁻¹ and μ=√3 rad/s.','λ=−ζω_n and μ=ω_n√(1−ζ²).'),
 ('λ=1 s⁻¹ and μ=√3 rad/s.','The real part needs the negative sign for positive damping.'),
 ('λ=−1 s⁻¹ and μ=2 rad/s.','The damped frequency is smaller than ω_n when ζ>0.'),
 ('λ=−2 s⁻¹ and μ=0.5 rad/s.','This confuses the damping ratio and natural frequency with the pole components.')],
 'The poles are −1±i√3 s⁻¹. Natural frequency and damped frequency are not the same except in the zero-damping case.',typ='numerical',difficulty='medium',steps=['Compute λ=−0.5·2=−1 s⁻¹.','Compute μ=2√(1−0.25)=√3 rad/s.'],formulas=[DR])
add(651,'damping-parameters','Damping ratio, natural frequency and poles',
 'For m,k>0 and zero damping b=0, which free-response statement is correct?',[
 ('ζ=0 and the poles are purely imaginary; a nonzero natural oscillation does not decay.','There is no negative real part to reduce its envelope.'),
 ('ζ=1 and the response is critically damped.','Critical damping requires a positive coefficient b=2√(mk), not zero.'),
 ('The natural frequency is zero because b=0.','ω_n=√(k/m) remains positive independently of b.'),
 ('Every initial displacement vanishes immediately because there is no friction.','Without damping, mechanical energy can persist as oscillation.')],
 'Zero viscous damping gives s²+ω_n²=0 and poles ±iω_n. This undamped free system is not asymptotically convergent to zero.',difficulty='medium',formulas=[DR])
add(652,'critical-response','Repeated poles and independent critical solution',
 'Why is the critically damped general solution (c₁+c₂t)e^(st), rather than simply c₁e^(st)+c₂e^(st)?',[
 ('The two identical exponentials are dependent; t e^(st) provides the second independent solution.','A second-order equation still needs two independent solution coefficients.'),
 ('The extra t is required only to convert seconds to radians.','It is a distinct solution mode, not a unit conversion.'),
 ('Repeated roots reduce the differential equation to first order for all initial states.','The second-order equation still requires initial position and velocity.'),
 ('The t factor makes the response periodic even though the pole is real.','A polynomial times a real exponential does not introduce sinusoidal periodicity.')],
 'Coincident roots require a generalized solution basis e^(st) and t e^(st). Combining two copies of e^(st) leaves only one independent amplitude.',typ='derivation',difficulty='medium',steps=['Observe c₁e^(st)+c₂e^(st)=(c₁+c₂)e^(st), which has only one independent coefficient.','Use the repeated-root basis e^(st) and t e^(st).','Write the general solution as (c₁+c₂t)e^(st).'],formulas=[CRIT])
add(652,'critical-response','Repeated poles and independent critical solution',
 'A critically damped free system has repeated pole −4 s⁻¹, x(0)=1 m and ẋ(0)=0. Which response satisfies these conditions?',[
 ('x(t)=(1+4t)e^(−4t) m, with t measured in seconds.','Its initial position is 1 and derivative is zero because the linear factor offsets the exponential’s initial slope.'),
 ('x(t)=e^(−4t) m.','Its initial velocity is −4 m/s rather than zero.'),
 ('x(t)=(1−4t)e^(−4t) m.','Its initial velocity is −8 m/s.'),
 ('x(t)=4t e^(−4t) m.','Its initial position is zero, not 1 m.')],
 'For x=(c₁+c₂t)e^(−4t), c₁=x(0)=1 m and ẋ(0)=c₂−4c₁=0 gives c₂=4 m/s.',typ='numerical',difficulty='medium',steps=['Set c₁=1 m from initial displacement.','Differentiate to obtain ẋ(0)=c₂−4c₁.','Set that expression to zero and obtain c₂=4 m/s.'],formulas=[CRIT])
add(652,'critical-response','Repeated poles and independent critical solution',
 'Under which condition does (c₁+c₂t)e^(−at) tend to zero as t→∞ for arbitrary finite c₁,c₂?',[
 ('a>0.','Exponential decay dominates the linear polynomial factor.'),
 ('a=0 for every c₂.','With a=0 the expression is c₁+c₂t and need not decay.'),
 ('a<0 for every nonzero coefficient pair.','That changes the exponential into growth.'),
 ('Any real a, because the t factor always decays.','t grows rather than decays; the exponential’s sign is decisive.')],
 'For a>0, both e^(−at) and t e^(−at) tend to zero, the latter by comparing t with e^(at) or applying l’Hôpital’s rule.',typ='derivation',difficulty='medium',steps=['Separate the expression into c₁e^(−at)+c₂t e^(−at).','For a>0, the first term tends to zero.','Write t e^(−at)=t/e^(at); l’Hôpital gives 1/(a e^(at))→0.'],formulas=[CRIT])
save()

DIRECT=formula('f=−K_p x−K_v ẋ; mẍ+(b+K_v)ẋ+(k+K_p)x=0',{'f':'actuator force','m':'positive mass','b':'physical viscous damping','k':'physical spring stiffness','x,ẋ,ẍ':'displacement, velocity and acceleration','K_p':'direct force-feedback position gain','K_v':'direct force-feedback velocity gain'},{'f':'N','m':'kg','b,K_v':'N·s/m','k,K_p':'N/m','x':'m','ẋ':'m/s','ẍ':'m/s²'},['Zero desired position; uppercase K distinguishes these physical-force gains from the normalized servo gains.'])
PART=formula('f=m f′+bẋ+kx; ẍ=f′',{'f':'physical actuator force','f′':'normalized acceleration command','m':'positive mass','b':'physical viscous damping','k':'physical stiffness','x,ẋ,ẍ':'actual displacement, velocity and acceleration'},{'f':'N','f′,ẍ':'m/s²','m':'kg','b':'N·s/m','k':'N/m','x':'m','ẋ':'m/s'},['Exact model parameters and state, ideal actuator, no external disturbance.'])
SERVO=formula('f′=−k_v ẋ−k_p x; ẍ+k_v ẋ+k_p x=0; k_v=2√k_p for critical damping',{'f′':'normalized acceleration command','x,ẋ,ẍ':'displacement, velocity and acceleration','k_p':'normalized servo position gain','k_v':'normalized servo velocity gain'},{'f′,ẍ':'m/s²','x':'m','ẋ':'m/s','k_p':'s⁻²','k_v':'s⁻¹'},['Exact model compensation; zero reference; k_p>0 and positive critical k_v.'])
add([653,654],'direct-feedback','Direct force-feedback coefficient changes',
 'After adding the applied force f and choosing f=−K_p x−K_v ẋ, which closed-loop equation follows?',[
 ('mẍ+(b+K_v)ẋ+(k+K_p)x=0.','Moving the negative feedback terms to the left adds them to the passive coefficients.'),
 ('mẍ+(b−K_v)ẋ+(k−K_p)x=0.','This reverses the signs when moving the feedback force to the left.'),
 ('(m+K_v)ẍ+bẋ+(k+K_p)x=0.','Velocity feedback changes the damping coefficient, not the coefficient of acceleration.'),
 ('mẍ+(b+K_p)ẋ+(k+K_v)x=0.','This swaps the position- and velocity-feedback roles.')],
 'The actuator force appears on the right of the forced equation. Substitution gives effective damping b+K_v and stiffness k+K_p, with mass m unchanged.',typ='derivation',difficulty='medium',steps=['Start with mẍ+bẋ+kx=f.','Substitute f=−K_p x−K_v ẋ.','Move both feedback terms to the left and group like derivatives.'],formulas=[MSD,DIRECT])
add(654,'direct-feedback','Direct force-feedback coefficient changes',
 'In the direct-feedback block diagram, which measured signal is multiplied by the position gain and which by the velocity gain?',[
 ('x is multiplied by K_p, and ẋ by K_v; both contributions are subtracted at the force summation.','These paths implement f=−K_p x−K_v ẋ.'),
 ('x is multiplied by K_v, and ẋ by K_p; both are subtracted.','This exchanges the gain labels shown on the branches.'),
 ('x is multiplied by K_p, and ẋ by K_v; both contributions are added as positive feedback.','The shown control law has negative signs for both terms.'),
 ('Only ẋ is measured, and the position branch is obtained by differentiating ẋ.','The figure has position and velocity feedback, not acceleration substituted for position.')],
 'The two feedback branches correspond directly to the negative displacement and negative velocity terms in the force law.',typ='diagram',difficulty='easy',formulas=[DIRECT])
add([654,655],'direct-critical-design','Direct-feedback critical damping design',
 'For m=b=k=1 in consistent SI units, choose a critically damped closed loop with effective stiffness k′=16 N/m. What direct force-feedback gains are required?',[
 ('K_p=15 N/m and K_v=7 N·s/m.','k′=k+K_p gives 15, while b′=2√(mk′)=8 and K_v=b′−b=7.'),
 ('K_p=16 N/m and K_v=8 N·s/m.','These values forget to subtract the physical stiffness and damping.'),
 ('K_p=15 N/m and K_v=8 N·s/m.','The position gain is correct, but the velocity gain must subtract b=1.'),
 ('K_p=7 N/m and K_v=15 N·s/m.','This interchanges the two calculated gains.')],
 'The direct controller adds to the existing physical coefficients. It requires K_p=16−1=15 and K_v=2√16−1=7.',typ='numerical',difficulty='medium',steps=['Set K_p=k′−k=16−1=15 N/m.','For critical damping compute b′=2√(1·16)=8 N·s/m.','Set K_v=b′−b=8−1=7 N·s/m.'],formulas=[DIRECT])
add(655,'direct-critical-design','Direct-feedback critical damping design',
 'A plant has m=1 kg, b=10 N·s/m and k=9 N/m. The direct controller uses K_p=−5 N/m and K_v=−6 N·s/m. Which conclusion follows?',[
 ('The effective coefficients are k′=4 N/m and b′=4 N·s/m, giving a stable critically damped loop.','The resulting polynomial is s²+4s+4=(s+2)².'),
 ('The loop is necessarily unstable because both feedback gains are negative.','Stability depends on the total effective coefficients, which remain positive here.'),
 ('The loop is undamped because negative K_v exactly cancels b.','The remaining damping is 10−6=4, not zero.'),
 ('The loop has negative effective stiffness k′=−14 N/m.','The physical stiffness and gain add: 9+(−5)=4.')],
 'Negative controller gains need not make this particular plant unstable. Here both effective coefficients are positive and b′²=4mk′=16.',typ='numerical',difficulty='medium',steps=['Calculate k′=9−5=4 and b′=10−6=4.','Form s²+4s+4=(s+2)².','Both poles are −2 s⁻¹, so the ideal loop is critically damped and asymptotically stable.'],formulas=[DIRECT],assumptions=['The exact linear model applies and there are no actuator limits or delays.'])
add(655,'effective-stability','Stability depends on effective coefficient signs',
 'For m>0 in mẍ+b′ẋ+k′x=0, which conditions give strict asymptotic stability of the second-order system?',[
 ('b′>0 and k′>0.','For this real second-order polynomial, these conditions put both poles in the open left half-plane.'),
 ('b′≥0 and k′≥0, including both boundary equalities.','Zero damping can leave undamped oscillations; zero stiffness leaves a zero pole.'),
 ('Only k′>0; any sign of b′ is acceptable.','Negative damping produces growth even with a positive restoring coefficient.'),
 ('Only b′>0; any sign of k′ is acceptable.','Negative stiffness gives a positive real root, and zero stiffness leaves a zero mode.')],
 'Strictly positive effective damping and stiffness are needed for asymptotic stability with positive mass. The slide’s warning about negative values should not be expanded into a guarantee for zero boundary cases.',difficulty='medium',formulas=[ROOT],assumptions=['In ROOT, substitute b=b′ and k=k′; strict asymptotic stability is stronger than bounded motion for selected initial states.'])
add(656,'partition-architecture','Model-based and servo control-law portions',
 'What is the purpose of separating the controller into a model-based portion and a servo portion?',[
 ('Use the model-based portion to simplify the effective plant, then design feedback for that simpler plant.','This is the stated motivation for control-law partitioning.'),
 ('Remove all state measurements so that the controller becomes purely open-loop.','The servo portion still uses feedback.'),
 ('Design an unrelated force for each physical parameter and never combine them.','The portions combine into one physical actuator command.'),
 ('Replace the mechanical plant with a simulated unit mass and stop applying force to the actual plant.','The unit-mass appearance is obtained by control of the actual plant, not by replacing it.')],
 'Partitioning is an architectural design choice: model compensation creates a simpler input-to-motion relation for the servo controller.',typ='definition',difficulty='easy')
add(657,'model-cancellation','Exact model cancellation and normalized input',
 'In f=αf′+β, which choice produces ẍ=f′ from mẍ+bẋ+kx=f under the ideal model?',[
 ('α=m and β=bẋ+kx.','The added β cancels the same damping and spring terms on the left, then division by m leaves ẍ=f′.'),
 ('α=1/m and β=bẋ+kx.','After cancellation this gives ẍ=f′/m², not f′, for a general mass.'),
 ('α=m and β=−bẋ−kx.','Negative β adds rather than cancels the passive terms when equations are rearranged.'),
 ('α=m and β=0.','This retains the damping and spring terms in the normalized plant.')],
 'Exact matching gives mẍ+bẋ+kx=mf′+bẋ+kx. Cancelling and dividing by positive m yields the unit-mass-form input relation.',typ='derivation',difficulty='medium',steps=['Substitute α=m and β=bẋ+kx into the actuator force.','Cancel bẋ+kx on both sides of the plant equation.','Divide mẍ=mf′ by m>0.'],formulas=[PART])
add(657,'model-cancellation','Exact model cancellation and normalized input',
 'If the physical actuator force f is measured in newtons and α=m is measured in kilograms, what are the SI units of f′ in f=mf′+bẋ+kx?',[
 ('m/s², because f′ is an acceleration command.','Multiplication by mass converts it to physical force.'),
 ('N, because every signal named f must have force units.','The prime denotes the normalized input; m times a force would have incorrect units here.'),
 ('m/s, because the compensator includes velocity.','The mass-scaled command must match a force, requiring acceleration rather than velocity.'),
 ('s⁻² with no length factor, because the command is a gain.','f′ is the input acceleration, not the position gain that multiplies displacement.')],
 'The simplified equation ẍ=f′ establishes the same units directly. Calling it a unit-mass force does not justify retaining newtons for f′ when an arbitrary physical mass is explicitly multiplied.',difficulty='medium',formulas=[PART])
add(657,'model-cancellation','Exact model cancellation and normalized input',
 'For m=2 kg, b=3 N·s/m, k=5 N/m, x=0.4 m, ẋ=−0.2 m/s and f′=1.5 m/s², what physical actuator force does exact partitioning command?',[
 ('4.4 N.','mf′=3 N and bẋ+kx=−0.6+2=1.4 N, so f=4.4 N.'),
 ('1.6 N.','This subtracts the compensation term rather than adding it.'),
 ('2.9 N.','This adds f′ directly without first multiplying it by mass.'),
 ('5.6 N.','This takes the magnitude of negative velocity instead of its signed value in bẋ.')],
 'The model-based command contains mass scaling and signed damping/stiffness compensation: f=2·1.5+3·(−0.2)+5·0.4=4.4 N.',typ='numerical',difficulty='medium',steps=['Compute β=−0.6+2=1.4 N.','Compute αf′=2·1.5=3 N.','Add them: f=4.4 N.'],formulas=[PART])
add(657,'model-mismatch','Limits of exact model compensation',
 'Suppose a controller uses estimates m̂,b̂,k̂ in f=m̂f′+b̂ẋ+k̂x, while the true plant has m,b,k. Which actual equation follows before assuming the estimates are exact?',[
 ('mẍ=m̂f′+(b̂−b)ẋ+(k̂−k)x.','Subtract the true passive terms from the estimated command.'),
 ('ẍ=f′ for every possible parameter estimate.','Exact cancellation is not guaranteed when the estimates differ from the plant.'),
 ('mẍ=m̂f′+(b̂+b)ẋ+(k̂+k)x.','The true passive terms are subtracted, not added, when solving for acceleration.'),
 ('mẍ=mf′ with no residual terms whenever b̂ and k̂ are positive.','Positivity is not equality and does not cancel parameter errors.')],
 'The claimed parameter-independent servo model is an ideal result of exact compensation. Model mismatch leaves residual state-dependent terms and potentially an input scaling error.',typ='derivation',difficulty='medium',steps=['Insert the estimated-model actuator law into the true plant equation.','Subtract bẋ+kx from both sides.','Group coefficient differences to obtain the residual dynamics.'],conflict='The slide’s servo-parameter independence assumes exact model matching; it does not extend to arbitrary estimates.',assumptions=['Hatted quantities are controller estimates, not additional measured states.'])
add(658,'normalized-servo','Normalized servo equation and critical damping',
 'After exact model cancellation, f′=−k_v ẋ−k_p x gives a desired critically damped servo with k_p=25 s⁻². Which positive k_v is required?',[
 ('10 s⁻¹.','For s²+k_v s+k_p, critical damping requires k_v²=4k_p.'),
 ('5 s⁻¹.','This uses √k_p but omits the factor of two.'),
 ('50 s⁻¹.','This uses 2k_p instead of 2√k_p.'),
 ('9 s⁻¹.','Subtracting a physical damping coefficient belongs to the direct-force design, not this normalized servo gain.')],
 'The unit-mass-form characteristic polynomial has discriminant k_v²−4k_p. Set it to zero and take the positive gain: k_v=2√25=10 s⁻¹.',typ='numerical',difficulty='medium',steps=['Set k_v²−4·25=0.','Choose the positive critical-damping branch k_v=10 s⁻¹.'],formulas=[SERVO])
add([654,658],'gain-units','Direct force gains versus normalized servo gains',
 'Which unit pairing correctly distinguishes direct force-feedback position gain K_p from normalized acceleration-servo position gain k_p?',[
 ('K_p has units N/m, whereas k_p has units s⁻².','K_p x must be a force, while k_p x must be an acceleration.'),
 ('Both have units N/m for arbitrary mass because both multiply x.','Their outputs have different units, so their gain units differ.'),
 ('K_p has units s⁻², whereas k_p has units N/m.','This reverses the direct-force and normalized-acceleration roles.'),
 ('Both are dimensionless because feedback gains never carry units.','The multiplication must convert displacement to the required physical command.')],
 'Identical symbols on nearby slides should not hide different normalization conventions. The direct controller commands force, whereas the partitioned servo commands acceleration before multiplication by mass.',difficulty='medium',formulas=[DIRECT,SERVO])
add(659,'partition-diagram','Partitioned block diagram and numerical example',
 'In the partitioned controller diagram, what is added after multiplying the servo output f′ by m?',[
 ('The model compensation bẋ+kx, using actual velocity and displacement.','This reconstructs f=mf′+bẋ+kx.'),
 ('The negative compensation −bẋ−kx.','That would reinforce rather than cancel the plant’s passive terms in the resulting acceleration equation.'),
 ('Only the desired position x_d, with no physical coefficients.','The illustrated zero-reference partition uses the actual-state model compensation.'),
 ('The acceleration command f′ again without mass scaling.','No second unscaled copy of the servo command is the compensation branch shown.')],
 'The servo provides the desired normalized acceleration. The model-based portion scales it by mass and adds the force needed to cancel the physical damping and stiffness.',typ='diagram',difficulty='easy',formulas=[PART])
add(659,'partition-diagram','Partitioned block diagram and numerical example',
 'For the slide’s m=b=k=1 example with normalized k_p=16 s⁻² and critical damping, what are α, β and k_v?',[
 ('α=1 kg, β=ẋ+x in the stated unit-coefficient SI model, and k_v=8 s⁻¹.','α=m, β=bẋ+kx, and k_v=2√16.'),
 ('α=1 kg, β=−ẋ−x in that model, and k_v=8 s⁻¹.','The compensation signs must be positive in f=αf′+β.'),
 ('α=1 kg, β=ẋ+x in that model, and k_v=7 s⁻¹.','Seven is the earlier direct force-feedback velocity gain, not the normalized servo gain.'),
 ('α=16 kg, β=ẋ+x in that model, and k_v=8 s⁻¹.','α is the physical mass, not the normalized position gain.')],
 'The partitioned example uses α=m=1 and β=bẋ+kx=ẋ+x with the stated coefficients. Its normalized critical velocity gain is 8, not the direct design’s 7.',typ='numerical',difficulty='medium',steps=['Use α=m=1 kg.','Insert b=k=1 with their SI units into β=bẋ+kx.','Compute k_v=2√16=8 s⁻¹.'],formulas=[PART,SERVO])
add([655,659],'direct-partition-equivalence','Equivalence of the two numerical designs',
 'Why do the lecture’s direct gains (K_p,K_v)=(15,7) and partitioned servo gains (k_p,k_v)=(16,8) produce the same physical zero-reference controller when m=b=k=1?',[
 ('The partitioned force expands to (−16x−8ẋ)+(x+ẋ)=−15x−7ẋ.','Positive model compensation offsets part of the normalized negative servo command.'),
 ('The two controllers are identical only because the gain labels can be exchanged without changing the law.','Position and velocity gains cannot be freely exchanged.'),
 ('The partitioned force is −16x−8ẋ with no additional compensation.','That omits the β=x+ẋ term of the partitioned controller.'),
 ('Both designs remove the actual spring and damper from the physical plant.','The elements remain present; equivalent actuator forces produce equivalent closed-loop dynamics.')],
 'The gain values belong to different portions and normalizations. Expanding the complete partitioned law, not comparing isolated symbols, reveals the same force and closed-loop poles.',typ='derivation',difficulty='medium',steps=['Write f=mf′+bẋ+kx with m=b=k=1.','Substitute f′=−16x−8ẋ.','Combine like terms to obtain f=−15x−7ẋ.'],formulas=[DIRECT,PART,SERVO])
save()

TRACK=formula('e=x_d−x; ė=ẋ_d−ẋ; f′=ẍ_d+k_v ė+k_p e; ë+k_v ė+k_p e=0',{'x_d,ẋ_d,ẍ_d':'desired displacement, velocity and acceleration','x,ẋ,ẍ':'actual displacement, velocity and acceleration','e,ė,ë':'desired-minus-actual position error and its derivatives','f′':'normalized commanded acceleration','k_p':'normalized servo position gain','k_v':'normalized servo velocity gain'},{'x_d,x,e':'m','ẋ_d,ẋ,ė':'m/s','ẍ_d,ẍ,ë,f′':'m/s²','k_p':'s⁻²','k_v':'s⁻¹'},['Smooth twice-differentiable desired motion, exact compensated model ẍ=f′, no disturbance, constant gains.'])
DIST=formula('ë+k_v ė+k_p e=d; d=F_dist/m; e_ss=d/k_p',{'e,ė,ë':'desired-minus-actual displacement error and its time derivatives','k_v':'normalized velocity gain','k_p':'normalized position gain','F_dist':'physical disturbance force entering subtractively at the plant input','m':'positive physical mass','d':'normalized error forcing for the specified resisting-force sign convention','e_ss':'constant steady-state error'},{'e,e_ss':'m','ė':'m/s','ë,d':'m/s²','F_dist':'N','m':'kg','k_v':'s⁻¹','k_p':'s⁻²'},['Exact compensation, stable positive gains; e_ss expression additionally assumes constant d and settled transient.'])
PID=formula('ż=e; ë+k_v ė+k_p e+k_i z=d; e⁽³⁾+k_v ë+k_p ė+k_i e=ḋ',{'e,ė,ë,e⁽³⁾':'desired-minus-actual displacement error and its first three time derivatives','z':'integrator state z(0)+∫₀ᵗ e(τ)dτ','k_p,k_v,k_i':'normalized proportional, derivative and integral gains','d,ḋ':'normalized error forcing and its time derivative','τ':'integration time variable'},{'e':'m','ė':'m/s','ë,d':'m/s²','e⁽³⁾,ḋ':'m/s³','z':'m·s','k_p':'s⁻²','k_v':'s⁻¹','k_i':'s⁻³','τ':'s'},['Ideal compensated plant and constant gains. Differentiate on smooth intervals and retain the integrator initial condition; zero steady error requires stable augmented dynamics, nonzero k_i and constant settled d.'])
add(660,'trajectory-signals','Desired trajectory and error-space command',
 'Which desired-trajectory signals does the shown tracking servo assume are available?',[
 ('x_d(t), ẋ_d(t) and ẍ_d(t).','Position defines error, velocity defines error rate, and acceleration supplies feedforward.'),
 ('Only x_d(t), even when the specified law contains desired velocity and acceleration.','That would leave required terms of the stated controller unavailable.'),
 ('Only a final endpoint and a total duration, without a time-dependent trajectory.','Those values alone are not the time-varying signals assumed by this law.'),
 ('Actual x(t) and ẋ(t) only, with no desired motion input.','Actual feedback alone does not specify which trajectory to track.')],
 'The lecture assumes smooth desired position together with its first and second derivatives, not merely a fixed endpoint.',typ='definition',difficulty='easy',formulas=[TRACK])
add(660,'trajectory-signals','Desired trajectory and error-space command',
 'Using e=x_d−x and ė=ẋ_d−ẋ, which acceleration command is the lecture’s trajectory-following servo law?',[
 ('f′=ẍ_d+k_v ė+k_p e.','Positive error correction is consistent with desired-minus-actual error.'),
 ('f′=ẍ_d−k_v ė−k_p e.','Those signs would oppose the intended correction under the stated error convention.'),
 ('f′=k_v ė+k_p e, always omitting ẍ_d.','This omits the desired-acceleration feedforward term in the displayed tracking law.'),
 ('f′=ẍ_d+k_v ẋ+k_p x, with no desired-minus-actual differences.','This is positive actual-state feedback rather than the stated error-space controller.')],
 'The command combines desired acceleration with proportional and derivative corrections in error coordinates. Its sign convention differs in appearance from the zero-reference law because e=−x when x_d=0.',difficulty='easy',formulas=[TRACK])
add([660,661],'tracking-error-dynamics','Derivation of homogeneous tracking-error dynamics',
 'For the exactly compensated plant ẍ=f′ and f′=ẍ_d+k_v ė+k_p e, what equation does e=x_d−x satisfy?',[
 ('ë+k_v ė+k_p e=0.','Subtract actual acceleration from desired acceleration to get ë=−k_v ė−k_p e.'),
 ('ë−k_v ė−k_p e=0.','This reverses the signs when moving the error-feedback terms to the left.'),
 ('ë+k_v ė+k_p e=ẍ_d.','The desired acceleration cancels because it is included as feedforward.'),
 ('ẍ+k_v ẋ+k_p x=0 for every nonzero desired trajectory.','That is the zero-reference actual-state equation, not the general tracking-error equation.')],
 'In the ideal model the chosen desired trajectory disappears from the homogeneous error equation. Desired acceleration is not an uncancelled forcing term.',typ='derivation',difficulty='medium',steps=['Differentiate e=x_d−x twice: ë=ẍ_d−ẍ.','Insert ẍ=ẍ_d+k_v ė+k_p e.','Cancel ẍ_d and rearrange.'],formulas=[TRACK])
add(660,'trajectory-numerical','Numerical trajectory-following acceleration command',
 'At one instant, x_d=0.5 m, x=0.3 m, ẋ_d=0.4 m/s, ẋ=0.1 m/s and ẍ_d=−0.2 m/s². With k_p=9 s⁻² and k_v=6 s⁻¹, what is f′?',[
 ('3.4 m/s².','The command is −0.2+6(0.3)+9(0.2)=3.4.'),
 ('3.6 m/s².','This omits the negative desired-acceleration feedforward term.'),
 ('−3.8 m/s².','This reverses both error-feedback signs while retaining the feedforward term.'),
 ('2.8 m/s².','This exchanges the position and velocity error values in the two gain products.')],
 'Compute the position and velocity errors separately, then combine them with the desired acceleration. The position and velocity gains have different units.',typ='numerical',difficulty='medium',steps=['e=0.5−0.3=0.2 m and ė=0.4−0.1=0.3 m/s.','k_p e=1.8 m/s² and k_v ė=1.8 m/s².','Add ẍ_d=−0.2 m/s² to obtain 3.4 m/s².'],formulas=[TRACK])
add([660,661],'feedforward-tracking','Role of desired-acceleration feedforward',
 'A modified servo omits desired acceleration and uses f′=k_v ė+k_p e on the ideal plant ẍ=f′. What is the resulting tracking-error equation?',[
 ('ë+k_v ė+k_p e=ẍ_d.','Without feedforward, the desired acceleration remains as a forcing term.'),
 ('ë+k_v ė+k_p e=0 for every smooth trajectory.','That cancellation requires the omitted ẍ_d term.'),
 ('ë+k_v ė+k_p e=−ẍ_d.','The error is desired minus actual, so its second derivative contains +ẍ_d.'),
 ('ë+k_v ė+k_p e=x_d.','The leftover term is desired acceleration, not desired displacement.')],
 'The absence of acceleration feedforward changes the error dynamics for accelerating references. For a constant-velocity reference, ẍ_d=0 and this particular forcing disappears.',typ='derivation',difficulty='medium',steps=['Start from ë=ẍ_d−ẍ.','Substitute ẍ=k_v ė+k_p e.','Move feedback terms to the left and retain ẍ_d on the right.'],formulas=[TRACK],assumptions=['This is an explicitly modified controller, not a transcription of the full source law.'])
add(661,'tracking-diagram','Tracking-controller comparator and model branches',
 'Which description matches the trajectory-following block diagram?',[
 ('Desired-minus-actual position and velocity errors pass through gains, add to desired acceleration, then pass through the model-based force reconstruction.','This follows the two comparators, acceleration summation, mass gain and cancellation branch.'),
 ('Actual-minus-desired errors pass through the same positive gains, with no other sign changes.','That reverses the source’s error convention and changes the feedback signs.'),
 ('Desired acceleration is fed back from the plant after the torque output.','It is a trajectory-generator feedforward signal, not a measured plant-output return.'),
 ('The compensation bẋ+kx is computed using only desired position and velocity in this figure.','The shown model cancellation uses the actual-state feedback signals.')],
 'The architecture implements error-space control followed by physical force reconstruction. The actual-state model cancellation and desired acceleration feedforward serve different purposes.',typ='diagram',difficulty='medium',formulas=[TRACK,PART])
add(661,'ideal-response-scope','Limits of selecting ideal error dynamics',
 'What is a defensible interpretation of the claim that choosing the error-equation coefficients lets us design “any response”?',[
 ('Within the ideal second-order model, gains shape its characteristic polynomial; real actuator, sensing and model limits still matter.','The equation permits pole shaping but does not eliminate implementation constraints.'),
 ('Any arbitrarily fast desired response is physically realizable regardless of force limits or delays.','The ideal differential equation does not establish unlimited hardware performance.'),
 ('Positive gains guarantee the same actual tracking response despite arbitrary model mismatch.','The derived homogeneous error equation assumes exact compensation.'),
 ('The gains can independently specify any number of poles in this second-order model.','A second-order characteristic polynomial has only two poles, with its two coefficients constrained by the chosen gains.')],
 'The design claim is about the chosen ideal error dynamics, not an unrestricted guarantee for a physical manipulator.',difficulty='medium',conflict='The slide’s any-response wording omits model validity, hardware bandwidth and actuator constraints.',formulas=[TRACK])
add(662,'disturbance-normalization','Physical force sign and normalized error forcing',
 'In the figure, a resisting physical disturbance F_dist enters with a minus sign after mass scaling. With exact compensation and e=x_d−x, which forced error equation has consistent mass scaling?',[
 ('ë+k_v ė+k_p e=F_dist/m.','The actual acceleration loses F_dist/m; desired-minus-actual error gains that same normalized term.'),
 ('ë+k_v ė+k_p e=F_dist for every physical mass.','The right side would have force rather than acceleration units unless a normalization or unit-mass convention is stated.'),
 ('ë+k_v ė+k_p e=−F_dist/m.','That sign would correspond to an additive disturbance in the plant, not the subtractive force shown.'),
 ('ë+k_v ė+k_p e=mF_dist.','Mass scaling must divide the physical force to produce acceleration.')],
 'After cancellation, mẍ=mf′−F_dist, hence ẍ=f′−F_dist/m. Using the desired-minus-actual error and tracking servo gives the stated positive forcing.',typ='derivation',difficulty='medium',steps=['Write mẍ=mf′−F_dist after cancelling passive model terms.','Divide by m to obtain ẍ=f′−F_dist/m.','Insert f′=ẍ_d+k_v ė+k_p e into ë=ẍ_d−ẍ and rearrange.'],formulas=[TRACK,DIST],conflict='The diagram’s physical subtractive disturbance is printed in the scalar error equation without explicit division by mass. This question distinguishes physical F_dist from normalized d=F_dist/m instead of silently identifying them.')
add(662,'disturbance-normalization','Physical force sign and normalized error forcing',
 'If the same plant instead receives an ADDITIVE physical force F_ext, so ẍ=f′+F_ext/m, what is the right side of ë+k_v ė+k_p e under e=x_d−x?',[
 ('−F_ext/m.','Additional actual acceleration reduces desired-minus-actual error acceleration.'),
 ('+F_ext/m.','This is the sign for a subtractive resisting force, not the additive force specified here.'),
 ('Zero for all F_ext because model compensation cancels any external force automatically.','The compensation cancels modeled passive terms, not an unspecified unmeasured external input.'),
 ('−mF_ext.','The disturbance acceleration requires division by mass.')],
 'A disturbance’s sign in the error equation depends jointly on its sign at the plant input and the error convention. This question explicitly changes the plant-input sign from the source figure.',typ='derivation',difficulty='medium',steps=['Use ë=ẍ_d−ẍ.','Substitute ẍ=ẍ_d+k_v ė+k_p e+F_ext/m.','Move the feedback terms left to obtain the forcing −F_ext/m.'],assumptions=['F_ext is a signed physical force in newtons; m>0; this is an explicitly modified additive-force scenario.'])
add(662,'disturbance-rejection','Meaning of disturbance rejection',
 'What objective does disturbance rejection describe in this tracking-control discussion?',[
 ('Maintain good performance by limiting errors despite external disturbances or noise.','The source defines the objective in terms of reducing the disturbance’s effect on performance.'),
 ('Guarantee that every external disturbance is physically removed before reaching the robot.','The controller can reduce effects without eliminating the external cause.'),
 ('Replace actual-state feedback by a purely open-loop trajectory command.','That would remove the error-driven correction emphasized here.'),
 ('Make a bounded disturbance produce exactly zero error at every instant without additional assumptions.','Boundedness and transient rejection do not imply perfect instantaneous cancellation.')],
 'Disturbance rejection is a performance objective. The following forced-error and steady-state analyses show why it is not synonymous with zero error under every disturbance.',typ='definition',difficulty='easy')
add(663,'bibo-scope','Bounded-input bounded-output qualification',
 'Which condition correctly expresses a bounded scalar disturbance magnitude over t≥0?',[
 ('There is a finite a such that |d(t)|≤a for all t≥0.','A magnitude bound limits both positive and negative excursions.'),
 ('There is a finite a such that d(t)<a, with no lower bound required.','A signal such as −t has a finite upper bound but unbounded magnitude.'),
 ('d(t) must tend to zero; no nonzero constant input can be bounded.','A finite constant is bounded without tending to zero.'),
 ('d(t) must be differentiable at every instant.','Boundedness concerns amplitude, not differentiability; a finite step is bounded.')],
 'BIBO uses bounded magnitude. The source’s upper-bound-only notation should not be taken literally as sufficient for arbitrary signed inputs.',difficulty='medium',conflict='The printed max_t f_dist(t)<a lacks absolute value and therefore does not bound a signed disturbance’s magnitude.')
add(663,'bibo-scope','Bounded-input bounded-output qualification',
 'What additional premise supports the lecture’s inference that bounded normalized disturbance produces bounded error for the linear closed-loop model?',[
 ('The disturbance-to-error system is stable, with finite initial conditions.','BIBO stability is a property of the system, not a consequence of the input being bounded by itself.'),
 ('The input is bounded; any feedback gain signs then suffice.','An unstable closed loop can have unbounded error for a bounded input or nonzero initial state.'),
 ('The position gain is zero, so the controller cannot amplify disturbance.','A zero position gain leaves a zero pole and can allow unbounded response to constant forcing.'),
 ('The disturbance is nonnegative, so the characteristic roots are irrelevant.','Input sign does not determine the system’s pole stability.')],
 'For the stated second-order model, positive k_p and k_v provide stable homogeneous dynamics. Bounded input alone is not a proof of stability.',difficulty='medium',conflict='The source’s bounded-disturbance discussion does not explicitly retain the stable-loop hypothesis.',formulas=[DIST])
add([663,664],'bounded-versus-zero','Bounded error versus vanishing error',
 'A stable loop receives a finite nonzero constant normalized disturbance d. What does BIBO stability alone guarantee, and what does the proportional-derivative steady-state equation generally show?',[
 ('Error remains bounded, but it can settle to the nonzero value d/k_p.','Bounded output does not mean zero output.'),
 ('Error is zero at every instant because the input is bounded.','BIBO does not eliminate transients or a constant offset.'),
 ('Error necessarily grows without limit under every nonzero constant input.','A stable loop can have a finite constant response.'),
 ('Error settles to zero regardless of k_p because k_v removes all constant disturbances.','Velocity feedback vanishes in steady state and does not by itself eliminate the position offset.')],
 'The constant forcing balances the proportional term at equilibrium. A finite nonzero bounded offset is compatible with BIBO stability.',difficulty='medium',formulas=[DIST],assumptions=['k_p>0, k_v>0, finite initial state, and no integral action.'])
add(664,'steady-error','Constant-disturbance steady-state error',
 'For ë+k_v ė+k_p e=d with constant d, a stable settled response and k_p≠0, what equation determines the steady error?',[
 ('k_p e_ss=d, hence e_ss=d/k_p.','Both time derivatives vanish at a constant equilibrium.'),
 ('k_v e_ss=d, hence e_ss=d/k_v.','The velocity-feedback term multiplies ė, which vanishes at this equilibrium.'),
 ('k_p e_ss=0 for every d, hence e_ss=0.','This drops the nonzero forcing from the equilibrium equation.'),
 ('e_ss=k_p d.','The equilibrium relation requires division by k_p, not multiplication.')],
 'Set ė=ë=0 only after assuming a stable response that settles. The remaining algebraic equation is k_p e_ss=d.',typ='derivation',difficulty='medium',steps=['Assume a constant settled error, so ė=ë=0.','Reduce the error equation to k_p e_ss=d.','Divide by nonzero k_p.'],formulas=[DIST])
add([662,664],'steady-error','Constant-disturbance steady-state error',
 'A 2 kg plant has a constant 6 N resisting disturbance entering subtractively and normalized k_p=3 s⁻², with stable positive velocity gain. What is the ideal steady position error e=x_d−x?',[
 ('1 m.','Normalize the force to d=6/2=3 m/s², then divide by k_p=3 s⁻².'),
 ('2 m.','This treats the physical 6 N force as a normalized acceleration and omits division by mass.'),
 ('−1 m.','This reverses the sign for the specified resisting-force input and desired-minus-actual error.'),
 ('4 m.','This multiplies the physical force by mass instead of dividing by mass before applying the gain.')],
 'The physical-to-normalized distinction matters numerically: e_ss=F_dist/(m k_p)=6/(2·3)=1 m.',typ='numerical',difficulty='medium',steps=['Compute d=F_dist/m=6/2=3 m/s².','Use e_ss=d/k_p=3/3=1 m.'],formulas=[DIST],conflict='The source reuses a disturbance symbol between the physical-force diagram and normalized error equation. This calculation explicitly retains the missing mass normalization.',conflict_pages=[662])
add(664,'gain-offset-tradeoff','Position and velocity gain effects on constant offset',
 'With a fixed nonzero constant normalized disturbance, no integral action and stable positive gains, which gain change halves |e_ss|?',[
 ('Double k_p while keeping the new loop stable.','The offset magnitude is |d|/k_p.'),
 ('Double k_v while keeping k_p fixed.','This can change the transient but leaves the constant-equilibrium formula unchanged.'),
 ('Halve k_p while keeping the new loop stable.','This doubles rather than halves the offset magnitude.'),
 ('Double both the disturbance magnitude and k_p.','Their ratio stays unchanged, so the offset is not halved.')],
 'Only the proportional coefficient appears in the constant-equilibrium balance. Increasing it reduces, but for finite gain and nonzero d does not eliminate, the ideal offset.',difficulty='medium',formulas=[DIST])
add(664,'zero-disturbance-exception','Scope of the nonzero-offset statement',
 'Which qualification is needed for the slide’s statement that the proportional-derivative steady-state error is “never zero”?',[
 ('The constant forcing must be nonzero and the positive position gain finite.','If d=0, the stable equilibrium can have e_ss=0.'),
 ('The statement is true even for d=0 and a stable loop.','For d=0, e_ss=d/k_p is zero.'),
 ('The velocity gain must be infinite for a nonzero constant offset to exist.','Finite positive velocity gain is compatible with the same equilibrium offset.'),
 ('The actual and desired trajectories must always both be stationary.','The ideal error equation can have a constant offset while following a smooth moving reference.')],
 'The displayed expression e_ss=d/k_p contains its own exception: zero forcing gives zero equilibrium error. The nonzero-offset conclusion concerns a nonzero constant disturbance without integral action.',difficulty='medium',formulas=[DIST],conflict='The source’s never-zero wording omits the zero-disturbance exception and finite-gain scope.')
add(665,'integral-augmentation','Integral action, state and controller order',
 'Which added servo term is the integral component in the lecture’s PID-style trajectory controller?',[
 ('k_i z, where z(t)=z(0)+∫₀ᵗ e(τ)dτ.','It accumulates the position error over time.'),
 ('k_i ė, a second velocity-error term.','That is derivative action rather than an accumulated error.'),
 ('k_i e², the squared instantaneous error.','Squaring is not time integration and would change the controller nonlinearly.'),
 ('k_i ẍ_d alone, a rescaling of feedforward acceleration.','This does not accumulate tracking error or supply integral feedback.')],
 'The controller adds an integrator state driven by the error. Together with proportional and derivative error terms, this is the PID-style structure described.',typ='definition',difficulty='easy',formulas=[PID])
add(665,'integral-augmentation','Integral action, state and controller order',
 'For normalized f′ measured in m/s², what units must k_i have when it multiplies z=∫e dt and e is in metres?',[
 ('s⁻³.','z has units m·s, so k_i z has units m/s².'),
 ('s⁻².','Those are the proportional gain’s units; multiplying by m·s would produce m/s rather than acceleration.'),
 ('s⁻¹.','Those are the velocity gain’s units; multiplying by m·s would produce displacement.'),
 ('N/m.','That is a direct force-position gain, not this normalized integral gain.')],
 'Integral gain must account for the extra unit of time in the accumulated error. Consistent normalization gives k_p in s⁻², k_v in s⁻¹ and k_i in s⁻³.',difficulty='medium',formulas=[PID])
add(665,'integral-derivative','Differentiated error equation and disturbance derivative',
 'On an interval where d(t) is differentiable, differentiating ë+k_v ė+k_p e+k_i z=d with ż=e and constant gains gives which equation?',[
 ('e⁽³⁾+k_v ë+k_p ė+k_i e=ḋ.','Every term is differentiated once, including the disturbance.'),
 ('e⁽³⁾+k_v ë+k_p ė+k_i e=d.','This fails to differentiate the right side; the actual source has the disturbance dot.'),
 ('ë+k_v ė+k_p e+k_i e=ḋ.','This fails to raise the derivative orders of the nonintegral terms.'),
 ('e⁽³⁾+k_v ë+k_p ė+k_i z=ḋ.','The derivative of the integrator state z is e, not z.')],
 'The readable source shows the disturbance derivative on the right. Differentiation produces a third-order equation and uses ḋ=0 only after a disturbance has become constant on the interval considered.',typ='derivation',difficulty='medium',steps=['Differentiate ë, ė and e to obtain e⁽³⁾, ë and ė.','Use ż=e for the integral term.','Differentiate d(t) to ḋ(t).'],formulas=[PID])
add(665,'integral-steady-state','Stable integral control and zero constant offset',
 'Under what premises does the integral-augmented model imply zero settled position error for a constant disturbance?',[
 ('The augmented closed loop is stable, reaches a steady state, and k_i≠0.','At a settled state ż=e=0, equivalently the differentiated equation gives k_i e=0.'),
 ('Any nonzero k_i guarantees zero error even if the augmented dynamics are unstable.','An unstable response need not reach the steady state used in the argument.'),
 ('k_i=0 is sufficient because the disturbance derivative is zero.','Without integral action, the constant disturbance can leave the earlier d/k_p offset.'),
 ('All initial tracking errors must already be zero and no disturbance may ever occur.','A stable integral controller is intended to remove constant offsets after transients, not only to preserve an undisturbed zero state.')],
 'The algebra establishes a possible zero-error equilibrium only under the stability and settling assumptions. It does not prove that arbitrary integral gains produce a stable controller.',difficulty='medium',formulas=[PID],conflict='The slide’s integral-elimination claim needs stable augmented dynamics and nonzero integral gain; the steady-state calculation is not itself a stability proof.')
add(665,'integrator-equilibrium','Nonzero integral state at zero error',
 'A stable integral-augmented loop has constant normalized disturbance d=6 m/s² and k_i=3 s⁻³. At its zero-error equilibrium, what value of the integrator state z supplies the balancing term?',[
 ('z=2 m·s.','At equilibrium e=ė=ë=0, leaving k_i z=d.'),
 ('z=0 because the current error is zero.','Zero current error means ż=0, not that the accumulated state z must be zero.'),
 ('z=18 m·s.','This multiplies d by k_i instead of dividing.'),
 ('z=−2 m·s.','The equation has +k_i z=d, so the state has the same sign as d for positive k_i.')],
 'The integral state holds a constant compensating contribution even after the instantaneous error reaches zero. It need not continue changing to maintain that force balance.',typ='numerical',difficulty='medium',steps=['Set all settled error derivatives and e to zero.','Reduce the original integral equation to k_i z=d.','Compute z=6/3=2 m·s.'],formulas=[PID])
add(665,'integral-stability-check','Positive integral gains are not a stability proof',
 'As a derived stability check, let k_v=2 s⁻¹, k_p=1 s⁻² and k_i=12 s⁻³. The characteristic polynomial factors as (s+3)(s²−s+4). What does this show about positive gains?',[
 ('Positive gains alone do not guarantee stability: the quadratic pair has real part +1/2 s⁻¹.','Its roots are (1±i√15)/2, so two modes grow.'),
 ('All roots are negative because every coefficient of the expanded cubic is positive.','Positive cubic coefficients are not sufficient for all roots to lie in the left half-plane.'),
 ('The loop is critically damped because the cubic has one negative real root.','The remaining pair is complex and unstable, not a repeated negative real pole.'),
 ('The constant disturbance derivative being zero makes the unstable homogeneous modes disappear for every initial condition.','Zero forcing does not eliminate an unstable system’s possible homogeneous response.')],
 'The expansion is s³+2s²+s+12. Although all three gains are positive, the quadratic roots have positive real part. This explicitly demonstrates why the integral controller needs a separate stability check.',typ='derivation',difficulty='medium',steps=['Expand (s+3)(s²−s+4)=s³+2s²+s+12.','Solve s²−s+4=0 to get (1±i√15)/2.','Their real part is +1/2, so the augmented loop is unstable.'],formulas=[PID],conflict='The slide’s steady-state integral argument does not establish augmented-loop stability. This counterexample is a derived qualification, not a numeric example printed in the source.',assumptions=['This explicit derived example uses the source’s normalized cubic characteristic equation; it is not claimed as a source-provided gain choice.'])
add(665,'integral-initial-state','Differentiation and integrator initial conditions',
 'Why must the integrator’s initial state still be retained after replacing the integral equation by its differentiated third-order equation?',[
 ('Differentiation removes an integration constant; the original equation supplies the compatibility condition involving z(0).','A solution of the differentiated equation must also satisfy the original force balance at an initial time.'),
 ('Differentiation proves z(0)=0 for every implementation.','The stored integrator state can be nonzero; differentiation does not reset it.'),
 ('The differentiated equation always has lower order and therefore needs no initial conditions.','It is third order and still needs compatible initial data.'),
 ('A step disturbance is differentiable with derivative zero at its jump, so no onset condition matters.','A step has a discontinuity at onset; the zero derivative applies on constant intervals away from that jump.')],
 'Use the original state form to preserve the integrator history and handle disturbance onset. The source’s t>0 differentiation should not silently discard the initial compatibility condition.',typ='derivation',difficulty='medium',steps=['The original equation includes k_i z(0) in its initial force balance.','Differentiating replaces z by its derivative e and removes the explicit constant.','Require the differentiated solution to satisfy the original equation initially; treat discontinuous forcing separately at its jump.'],formulas=[PID],assumptions=['k_i≠0; this is a mathematical qualification of differentiating the source’s integral equation.'])
save()

# Final author quality pass before freezing: keep units, explanations and classifications aligned.
def replace_option(number,old,new,explanation):
 q=b.questions[number-1];o=next(o for o in q['options'] if o['text']==old);o['text']=new;q['solution']['optionExplanations'][o['id']]=explanation
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']]
replace_option(52,'2.8 m/s².','3.7 m/s².','This exchanges the errors in the gain products: −0.2+6(0.2)+9(0.3)=3.7, which is not the specified controller.')
replace_option(31,'The extra t is required only to convert seconds to radians.','The repeated root requires a second mode e^(−st), independent of whether −s is a root.','A sign-reversed exponential is not generally a solution of the characteristic equation; the repeated-root mode is t e^(st).')
replace_option(33,'Any real a, because the t factor always decays.','a=0 is sufficient whenever c₁=0, even if c₂ is arbitrary.','With a=0 and c₁=0, the expression is c₂t and grows for nonzero c₂.')
replace_option(39,'Replace the mechanical plant with a simulated unit mass and stop applying force to the actual plant.','Make the model-based portion generate only a desired position, leaving all physical-parameter cancellation to the servo gain selection.','The model-based portion explicitly handles parameter compensation and mass scaling before the simplified servo design.')
replace_option(69,'All initial tracking errors must already be zero and no disturbance may ever occur.','No stability condition is needed if the desired reference is constant, even when initial error is nonzero.','A constant reference does not make unstable homogeneous modes converge; augmented-loop stability remains necessary for the settling argument.')
# Direct recognition/definition questions remain easy even when their surrounding theory is advanced.
for number in [22,24,30,41,45,54,59,60,64,65]:b.questions[number-1]['difficulty']='easy'
# The summary introduces no extra technical premise. Link its statements to the existing substantive concepts.
for number in [1,11,17,39,51,64,69]:
 q=b.questions[number-1];q['citations'].append({'slideId':'lectures-p0666','sourceId':'lectures','sourceSha256':SHA,'physicalPage':666,'kind':'statement','locator':'Lecture 21, physical PDF page 666, printed slide 30: summary bullet for '+q['subtopic'],'evidenceText':(R/'sources/text/lectures/page-0666.txt').read_text().strip(),'role':'premise','region':None})
 for cid in q['conceptIds']:
  if 'lectures-p0666' not in b.concepts[cid]['slideIds']:b.concepts[cid]['slideIds'].append('lectures-p0666')
# Bind summary qualification too where its integral claim repeats the same scope problem.
q=b.questions[68];q['conflictResolution']['physicalPages']=[665,666]
next(c for c in q['citations'] if c['physicalPage']==666)['role']='conflict'
# Record source-pixel evidence for glyphs/diagram paths that plain extraction loses.
VISUAL={9:'Visual check at 4× PDF resolution: Ė=Θ̇_d−Θ̇ includes the dot on both desired and actual velocity symbols.',35:'Visual transcription: actual x passes through k_p and actual ẋ passes through k_v; both gain paths enter the actuator-force summation negatively.',46:'Visual transcription: f′ passes through the m block; the bẋ+kx branch enters the later force summation positively.',54:'Visual transcription: both error comparators use desired plus and actual minus; desired acceleration adds to k_v ė+k_p e before m scaling; bẋ+kx is added for model cancellation.',56:'Visual transcription at 4× resolution: the f_dist arrow enters the upper MINUS port of the summing junction after the m block. The scalar displayed error equation uses f_dist without an explicit /m.',68:'Visual transcription at 4× resolution: the differentiated equation is e triple-dot + k_v e double-dot + k_p e dot + k_i e = f_dist dot. The right-side dot is present.'}
for number,txt in VISUAL.items():
 for c in b.questions[number-1]['citations']:
  if c['physicalPage']!=666:c['evidenceText']=txt+'\n'+c['evidenceText']
save()

# Freeze the author proposal only; all questions remain draft pending a different reviewer.
save(frozen=True)
packet=R/f'audits/blind-{BATCH}.json'
manifest={'batchId':BATCH,'authorId':AUTHOR,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'questionCount':len(b.questions),'conceptCount':len(b.concepts),'physicalPages':list(NOTES),'sourceVersions':{'lectures':SHA},'blindPacketPath':str(packet.relative_to(R)),'blindPacketSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'questionHashConvention':'scripts.validate.question_hash; excludes only status and reviewIds','questions':[{'questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q)} for q in b.questions],'independentReviewStillRequired':True}
(R/f'audits/{BATCH}-frozen-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
coverage=[]
for p,(note,excluded) in NOTES.items():
 coverage.append({'physicalPage':p,'slideId':f'lectures-p{p:04d}','sourceSha256':SHA,'visualInspection':'complete','disposition':'excluded' if excluded else 'drafted-awaiting-independent-review','exclusionReason':excluded,'observedMeaningfulContent':note,'conceptIds':[c['id'] for c in b.concepts.values() if f'lectures-p{p:04d}' in c['slideIds']],'questionIds':[q['id'] for q in b.questions if any(c['physicalPage']==p for c in q['citations'])]})
assert all(row['exclusionReason'] or (row['conceptIds'] and row['questionIds']) for row in coverage)
(R/f'audits/{BATCH}-author-coverage-ledger.json').write_text(json.dumps({'batchId':BATCH,'status':'author coverage proposal, independent substantive challenge required','pageCount':len(coverage),'exclusions':sum(bool(x['exclusionReason']) for x in coverage),'pages':coverage},ensure_ascii=False,indent=2)+'\n')
assert all('correctOptionIds' not in q and 'solution' not in q and all('evidenceText' not in c for c in q['citations']) for q in json.loads(packet.read_text()))
print('FROZEN_PACKET_SHA256',manifest['blindPacketSha256'])
