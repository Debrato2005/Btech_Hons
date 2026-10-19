#!/usr/bin/env python3
"""Freeze source-derived L13 answers without opening the keyed batch."""
import datetime,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'audits/blind-W03-L13.json';h=hashlib.sha256(p.read_bytes()).hexdigest()
assert h=='b74060d514c868c0ae78c6cc88c26b725f5a457b3c929dcc0254092a009169f5'
b=json.loads(p.read_text())
keys=['o2','o3','o4','o1,o2','o2','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1','o2,o3','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1','o2','o3','o4','o1','o2,o3','o3']
reasons=[
'The diagram puts m1 at the elbow and m2 at the distal tip; the connecting links are massless.',
'Zero inertia about a point mass COM does not eliminate its offset force moment about a joint. Parallel-axis inertia about the joint is generally nonzero.',
'For one mass rotating about a fixed joint, tau=m r² alpha=2*(0.5)²*3=1.5 N·m.',
'The terminal force and moment are both zero. The stationary base uses +g Y0 as an algorithmic gravity-compensation acceleration, not physical base acceleration. Base nonrotation does not constrain the joint rates.',
'The inward loads require compensation against physical gravity −g Y0. Seed +g Y0 once; adding the same gravity load again would double count it.',
'Components in the rotated frame use R21=Rz(−theta2). Rz(−90°)*(1,0,0)=(0,−1,0).',
'With nonrotating base, omega1=(0,0,q1dot), so its z component is −2 rad/s.',
'The transported upstream and relative joint angular velocities are coaxial z vectors, so their cross product vanishes. At the first link the upstream vector is also zero.',
'The frame1-origin gravity-augmented acceleration is (g sin(theta1),g cos(theta1),0), giving (10,0,0). It is not a physical acceleration of the fixed base.',
'Crossing alpha=(0,0,q1ddot) with r=(l1,0,0) gives (0,l1 q1ddot,0); nesting the omega cross gives (−l1 q1dot²,0,0).',
'Instantaneous rest kills the squared-rate centripetal term but not the angular-acceleration tangential term.',
'aC1=(−0.5*2²,0.5*3+10,0)=(−2,11.5,0); F1=m1*aC1=(−4,23,0) N.',
'Capital N is the local spin moment about the point-mass COM, while lowercase n includes inward force-arm and downstream moments. N1=N2=0 does not force actuator torque to zero.',
'The coaxial angular rates and accelerations add: 3+(−1)=2 rad/s and −2+5=3 rad/s².',
'The first COM is exactly at the elbow. The same physical point acceleration can therefore be expressed in frame2 simply by rotation; arbitrary placement elsewhere on link1 would require further transport.',
'The shorthand s12 denotes sin(theta1+theta2), not a product or sum of separate sines.',
'In frame1, aC1=(−4,13,0). R21=Rz(−90°) maps this to a2=(13,4,0) m/s².',
'Joint2 rotates about the elbow origin, whose world position depends only on link1. Its components depend on the choice of rotated frame2 axes, but its physical acceleration has no joint2-motion contribution.',
'At the elbow a2=(13,4,0). Absolute link2 rate is 1 and angular acceleration is 4, so the tip offset adds (−0.5,2,0), giving (12.5,6,0).',
'Expanding −l2(q1dot+q2dot)² yields an additional mixed term −2 l2 q1dot q2dot.',
'The second link absolute angular velocity and acceleration are zero, so its COM shares the translating elbow acceleration. At theta2=90° the rotated elbow centripetal acceleration is (0,4,0), not zero.',
'F2=2*(12.5,6,0)=(25,12,0) N. A point mass has zero inertia tensor about its own COM, hence N2=0.',
'The inward equation is f2=R23 f3+F2. Its reduction to F2 follows from the zero terminal force, not a universal identity.',
'The z component of (0.5,0,0) cross (25,12,0) is 0.5*12=6 N·m; all other stipulated moments vanish.',
'The zero COM tensor removes N2, while zero terminal n3 and f3 remove their rotated and force-arm contributions. The mass force acting at rC2 survives.',
'R12=Rz(+90°) maps (25,12,0) to (−12,25,0). Adding F1=(−4,23,0) gives (−16,48,0) N.',
'The surviving inward contributions are the rotated downstream moment, own COM force moment, and rotated downstream force moment at the elbow offset.',
'The source shows a transpose after an already column-shaped n2 expression. A 3-by-3 matrix times a 1-by-3 row is undefined, whereas the general recurrence and next slide require R12*n2 with n2 a 3-by-1 column. This is a local typography conflict, not an algebraic alternative.',
'The third row of the cross-product matrix for (l1,0,0) is (0,l1,0). Multiplying it by Rz(theta2) gives (l1 sin(theta2),l1 cos(theta2),0).',
'The identity cos(A−B)=cos A cos B+sin A sin B gives cos((theta1+theta2)−theta2)=cos(theta1).',
'Expanding and cancelling k q1dot² gives −k(q2dot²+2 q1dot q2dot). The isolated first squared-rate term cancels but the mixed and second squared-rate terms remain.',
'The scalar actuator effort is the moment projection on the allowed joint axis. Both positive revolute axes are +z.',
'At theta2=90°, M=[[3,1],[1,1]], so M*qddot=(13,7). The velocity contribution is (−8,1) and gravity contribution (20,0); total tau=(25,8) N·m.',
'Collecting q2ddot in tau1 and q1ddot in tau2 gives the identical coefficient m2 l2²+m2 l1 l2 cos(theta2), confirming symmetry.',
'The coefficients are M11=1+2+2=5, M12=M21=1+1=2, M22=1; the matrix is [[5,2],[2,1]] kg·m².',
'At theta2=0, det M=m1*m2*l1²*l2²>0. Singularity of the task position Jacobian does not imply a singular joint-space mass matrix.',
'At horizontal rest, tau2=m2*l2*g=10 and tau1=m2*l2*g+(m1+m2)*l1*g=30 N·m.',
'Both gravity force lines pass through their upstream joint axes at the vertical configuration, so gravity moments vanish. The support forces balancing the nonzero weights do not vanish.',
'Pure squared rates and the mixed product are unchanged when both rates change sign. No friction term is present to break this invariance.',
'With zero accelerations and gravity, h1=−k(q2dot²+2q1dot q2dot)=0 and h2=k q1dot²=4 N·m.',
'This is inverse dynamics: model parameters together with positions, rates, accelerations and terminal wrench determine the actuator efforts.',
'Outward recursion first obtains kinematics and local inertial forces/moments; inward recursion then propagates transmitted loads and projects actuator efforts.',
'Uniform rods have different COM offsets and nonzero COM inertia tensors. Newton–Euler still applies, but the endpoint-point-mass formulas are not unchanged rod formulas.',
'The first point mass lies at the joint2 axis. Changing joint2 alone does not change that mass position and therefore contributes no joint2 generalized effort in this model.',
'Every displayed velocity-dependent torque has a sin(theta2) factor and vanishes at zero angle. Cosine-based acceleration coupling remains, and radial COM acceleration can still be nonzero.',
'The stipulated boundary moment M points along the common z direction. Its rotation leaves the z component unchanged, so it propagates inward and adds M to both joint efforts under the supplied sign convention.'
]
assert len(b)==len(keys)==len(reasons)==46
answers=[]
for q,k,r in zip(b,keys,reasons):
 answers.append({'questionId':q['id'],'questionVersion':q['version'],'independentAnswerOptionIds':k.split(','),'reasoning':r,'reviewedSlideIds':[c['slideId'] for c in q['citations']],'blindItemSha256':hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()})
out={'reviewerId':'build_offline_study_interface-L13-independent','frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete':True,'solvedBeforeAnswerSeen':True,'keyedBatchOpened':False,'sourcePacketPath':str(p.relative_to(R)),'sourcePacketSha256':h,'sourcePagesInspected':list(range(404,428)),'sourceInspectionMethod':'Read all 24 actual 1800x1013 page images at readable scale, together with full extracted text, before opening keyed questions or author source-dispute ledger. Inspected axes, endpoint placements, frame rotations, all outward/inward equations, transpose anomaly, torque cancellations and algorithm summary.','answers':answers,'sourceNotes':['The p421 expanded n2 column has an extraneous transpose mark inconsistent with multiplication dimensions and p422. This local conflict must be explicitly bound rather than silently corrected.','The +g base acceleration is a gravity-compensation recursion seed, not physical acceleration of the fixed base.','Zero COM inertia for endpoint point masses does not mean zero joint-space inertia or joint torque.']}
t=R/'audits/blind-answers-W03-L13-independent.json';assert not t.exists();t.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Frozen',len(answers),'answers',out['frozenAt'])
