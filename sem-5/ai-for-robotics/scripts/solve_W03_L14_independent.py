#!/usr/bin/env python3
"""Freeze L14 source-first answers before keyed-batch access."""
import datetime,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'audits/blind-W03-L14.json';raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
assert h=='ad665f85829be04fc59c10dba43895e8424366d2bd6f36bf2c3b1c8a75d08f92'
b=json.loads(raw)
keys=['o2','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1,o2','o2','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1,o2','o2','o3','o4','o1','o2','o3','o4','o1','o2']
reasons=[
'The comparison explicitly contrasts linkwise force/moment balance with scalar system energy and says both yield the same motion equations under a common model.',
'The source emphasizes recursive Newton–Euler for real-time computation and systematic Lagrangian derivation for model formulation; this is not a universal benchmark claim.',
'For ideal constraints and independent coordinates, constraint forces do no allowed virtual work. This eliminates separate constraint-reaction unknowns from generalized actuator equations, not the physical reactions themselves.',
'Translational K=mv²/2 scales with squared speed, so replacing v by 2v multiplies K by four.',
'The translational contribution is 0.5*2*3²=9 J and COM spin contribution 0.5*0.5*4²=4 J, totaling 13 J.',
'The quadratic form needs matching angular-velocity and inertia bases. The tensor is about the COM when the COM translational energy is separately included.',
'Reversing the conservative line-integral limits reverses its sign: integral r to r0 f·dr equals minus integral r0 to r.',
'Total E=K+U=17 J whereas L=K−U=7 J.',
'The source requires a total time derivative of the velocity partial, then subtraction of the coordinate partial: d/dt(L_qdot_i)−L_q_i=Q_i.',
'Because U has no qdot dependence, L_qdot=K_qdot and L_q=K_q−U_q. Subtracting gives d/dt(K_qdot)−K_q+U_q.',
'The exact named extension on p434 is a Rayleigh potential function. This is source terminology, not a proof that every dissipative law requires or admits that representation.',
'The source explicitly prints the gyroscopic/non-potential circulatory limitation. The stem is restricted to identifying that printed assertion, not endorsing it as a theorem about every generalized-force formulation.',
'U=−m g0 dot r=−2*((0,−10,0) dot (2,3,0))=60 J.',
'An additive constant independent of q and qdot has zero relevant derivatives, so the actuator equations are unchanged.',
'Generalized effort is conjugate to its coordinate: torque for angles, force for length. The mixed vector has units (N·m,N,N·m).',
'The stated minimal six-DOF description uses six independent coordinates, and qdot is their time derivative. Angular-rate components need not have linear-velocity units.',
'The source figure has downward Y and theta from rightward X toward Y. Thus y=l sin(theta), with downward gravity potential −mgy=−mgl sin(theta).',
'An undeflected-at-zero torsional spring stores U_s=kt theta²/2. Its physical generalized torque is −dU_s/dtheta=−kt theta.',
'The partial derivative holds thetadot independent and fixed; constant m and l leave no explicit theta dependence in K.',
'The final zero right-hand side is the unforced specialization tau=0 of the earlier general actuator equation, not deletion of gravity or spring contributions.',
'The kinetic derivative contributes ml² thetaddot, while U_theta=kt theta−mgl cos(theta). Their sum equals the applied positive-theta torque.',
'ml² thetaddot=2*.25*4=2; kt theta=3*pi/6=pi/2; mgl cos(theta)=10*(sqrt(3)/2)=5sqrt(3). Required torque is 2+pi/2−5sqrt(3), approximately −5.09 N·m.',
'At theta=0, spring torque is zero but gravity torque is mgl. Divide ml² thetaddot=mgl by ml² to get positive g/l.',
'A static unforced state has thetaddot=0, so kt theta_e=mgl cos(theta_e). Zero spring deflection is not generally an equilibrium under gravity.',
'For radians use pi/2−theta, not literal 90 radians. The geometric gravity moment is positive mgl cos(theta) in the stated downward-angle convention.',
'90°=pi/2 rad. The spring torque magnitude is kt*|theta|=4*pi/2=2pi N·m.',
'Differentiate K+U and use the driven equation: dE/dt=thetadot*(ml² thetaddot+kt theta−mgl cos(theta))=tau*thetadot.',
'Divide by ml² and match the supplied oscillator coefficient omega_n²=kt/(ml²), so omega_n is its positive square root.',
'The figure and text define d2 from the first joint axis to the second link COM, not merely the exposed slider stroke.',
'Both links share z-axis angular velocity, so the spin quadratic forms select Izz1 and Izz2. A prismatic joint does not remove the inherited rotation of link2.',
'The radial and tangential unit vectors are orthogonal. Squaring their velocity sum gives d2dot²+d2² thetadot1² with zero dot-product cross term.',
'The total rotational speed coefficient is the first COM orbital inertia, both COM spin inertias, and second COM orbital inertia: m1l1²+Izz1+Izz2+m2d2².',
'A=2*.5²+.2+.3+3*.4²=1.48 kg·m². K=0.5*1.48*2²+0.5*3*.5²=2.96+.375=3.335 J.',
'Hold theta1 and d2max fixed while differentiating d2: the derivative is m2*g*sin(theta1); the fixed reference term contributes zero.',
'At theta1=−pi/2 and d2=d2max, both individual nonnegative reference-adjusted gravitational potentials are zero. At shorter extension link2 retains m2*g*(d2max−d2).',
'K has no explicit theta1 dependence; differentiating its m2*d2²*w²/2 term in d2 gives m2*d2*w². The potential gradient is (g(m1*l1+m2*d2)cos(theta1),m2*g*sin(theta1)). The two distractors that say "same stated U vector" need a self-contained referent.',
'For K=A(d2)*w²/2+m2*v²/2, the velocity partial is (A*w,m2*v). A needs a definition in this standalone question, not only in earlier bank items.',
'Use product rule: A*thetaddot1+Adot*thetadot1, with Adot=2*m2*d2*d2dot.',
'The d2 Euler–Lagrange component is m2*d2ddot−m2*d2*w²+m2*g*sin(theta1). The radial velocity-square force is inward under the outward-positive convention.',
'The kinetic energy and clear upper torque/matrix expressions have +m2*d2². The underscore-like lower display is inconsistent typography; the positive orbital kinetic term establishes the intended positive coefficient.',
'Diagonal M eliminates cross-acceleration coefficients, not d2-dependent rotational inertia, mixed velocity terms, or gravity configuration dependence.',
'M11 multiplies angular acceleration to give torque and has kg·m² units. M22 multiplies radial acceleration to give force and has kg units.',
'A=1.48. Rotational inertia term 1.48, Coriolis term 2*3*.4*2*.5=2.4, gravity torque (2*.5+3*.4)*10=22, so tau1=25.88 N·m. Radial force=3*(−.2)−3*.4*2²+0=−5.4 N.',
'Reversing w alone negates the mixed first component 2*m2*d2*w*v while leaving the squared second component −m2*d2*w² unchanged. G depends on q, which is held fixed.',
'With fixed radial coordinate and zero gravity, F2=−m2*d2*w²=−2*.5*3²=−9 N, inward.',
'At horizontal theta=0, G=(g(m1l1+m2d2),0). At vertical theta=pi/2, G=(0,m2g), so zero revolute moment does not eliminate radial support force.',
'When g=tau1=0, d/dt(A(d2)*thetadot1)=0. The radial actuator can change kinetic energy while the axial angular momentum is conserved. The standalone item should explicitly define its A shorthand.',
'Ainitial=1+.5+.5+2*.5²=2.5; Afinal=1+.5+.5+2*1²=4. Conserved momentum gives final rate=2.5*4/4=2.5 rad/s.',
'qdot transpose V=2*m2*d2*w²*v−m2*d2*w²*v=m2*d2*w²*v. Mdot has only entry 11=2*m2*d2*v, producing the same half quadratic form.',
'Actuator power is the generalized-effort/velocity dot product: tau1*thetadot1+F2*d2dot.',
'The single-joint angle grows downward while the RP angle raises the COM. Opposite potential signs follow these coordinate conventions, not different physical gravity directions.',
'V in L=K−V is scalar potential energy; V(q,qdot) in the manipulator equation is a generalized-effort vector of velocity-product terms. Identical letters do not make their meanings or units interchangeable.',
'Independent coordinates and conventions come first, followed by system energies, the correct partial/total derivatives, and then collected actuator equations.'
]
assert len(b)==len(keys)==len(reasons)==53
answers=[{'questionId':q['id'],'questionVersion':q['version'],'independentAnswerOptionIds':k.split(','),'reasoning':r,'reviewedSlideIds':[c['slideId'] for c in q['citations']],'blindItemSha256':hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()} for q,k,r in zip(b,keys,reasons)]
out={'reviewerId':'build_offline_study_interface-L14-independent','frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete':True,'solvedBeforeAnswerSeen':True,'keyedBatchOpened':False,'sourcePacketPath':str(p.relative_to(R)),'sourcePacketSha256':h,'sourcePagesInspected':list(range(428,450)),'sourceInspectionMethod':'Read all 22 actual 1800x1013 page images at readable scale and all extracted text. Inspected both diagrams, signs, energy integrals, exact derivatives, the lower mass-matrix glyph and summary notation. Neither keyed L14 questions nor author computation/source-dispute records were opened.','answers':answers,'sourceNotes':['p434 contains a blanket gyroscopic/circulatory limitation; a source-attributed recall answer must not turn it into a universal theorem.','p440 changes an earlier applied torque RHS to zero without an explicit nearby explanation; the consistent reading is unforced motion.','p441 uses 90 in a complement-angle expression while a physical torsion law needs radians; pi/2 is the consistent radian complement.','p446 lower standalone mass matrix contains an underscore-like glyph where the clear kinetic energy and upper matrix require plus m2*d2².','p447 reuses V for scalar potential and velocity-product effort vector; the symbols must be disambiguated.']}
t=R/'audits/blind-answers-W03-L14-independent.json';assert not t.exists();t.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Frozen',len(answers),out['frozenAt'])
