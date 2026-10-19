#!/usr/bin/env python3
"""Versioned L11 author repair from immutable v1; no self-approval or bank writes."""
import copy, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BATCH='W03-L11'; AUTHOR='L11-author-20261019'
original=json.loads((ROOT/'data/question-batches/archive/W03-L11-v1.json').read_text())
batch=copy.deepcopy(original)
summary=json.loads((ROOT/'audits/W03-L11-independent-summary.json').read_text())
reviews=json.loads((ROOT/'data/reviews/W03-L11-v1-independent.json').read_text())
flags=set(summary['actionableFlags'])
accepted={r['questionId']:r['questionSha256'] for r in reviews if r['decision']=='verified'}
Q={x['id']:x for x in batch['questions']}; oldQ={x['id']:x for x in original['questions']}
modified=set(); new=[]; checks=[]
def digest(x):
 return hashlib.sha256(json.dumps({k:v for k,v in x.items() if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert len(flags)==39 and len(accepted)==69
assert all(digest(oldQ[r['questionId']])==r['questionSha256'] for r in reviews)
def q(short):
 key=BATCH+'-'+short; assert key in flags; modified.add(key); return Q[key]
def fm(expression,variables,units,assumptions):return dict(expression=expression,variables=variables,units=units,assumptions=assumptions)
def rewrite(short,options,why,stem=None):
 x=q(short); assert len(options)==len(why)==len(x['options'])
 if stem:x['stem']=stem
 for o in x['options']:o['text']=options[int(o['id'][1:])-1]
 x['solution']['optionExplanations']={f'o{i+1}':('Correct. ' if f'o{i+1}' in x['correctOptionIds'] else 'Incorrect. ')+v for i,v in enumerate(why)}
 x['solution']['justification']=' '.join(why[int(k[1:])-1] for k in x['correctOptionIds'])
 x['solution']['simpleExplanation']=x['solution']['justification']
 x['solution']['misconceptions']=[v for i,v in enumerate(why) if f'o{i+1}' not in x['correctOptionIds']]
def save(final=False):
 for key in modified:
  x=Q[key];x['version']=2;x['status']='draft';x['reviewIds']=[]
  x['revisionAuthors']=list(dict.fromkeys(x.get('revisionAuthors',[])+[AUTHOR]))
 assert all(Q[k]==oldQ[k] and digest(Q[k])==h for k,h in accepted.items())
 batch['revisionNote']='39 flagged v1 questions repaired as v2, 69 accepted v1 objects preserved exactly, and one new angular-acceleration gap draft. New independent review required.' if final else 'Incremental L11 v2 author repair. No independent approval claimed.'
 (ROOT/'data/question-batches/W03-L11.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
 report={'batchId':BATCH,'final':final,'revisedIds':sorted(modified),'preservedAcceptedHashes':accepted,'newQuestionIds':[x['id'] for x in new],'authorChecks':checks,'independentReviewPending':True}
 report['revisionBindings']=[{'questionId':key,'previousVersion':1,'previousQuestionSha256':digest(oldQ[key]),'currentVersion':2,'currentQuestionSha256':digest(Q[key]),'reviewerFindingsAddressedByAuthor':summary['actionableFlags'][key],'requiresNewIndependentReview':True} for key in sorted(modified)]
 (ROOT/'audits/W03-L11-v2-author-repair.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 if final:
  assert modified==flags
  blind=[]
  for x in batch['questions']:
   if x['id'] in flags or x['id'] in {v['id'] for v in new}:
    v={k:x[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions')}
    v['citations']=[{k:z for k,z in c.items() if k!='evidenceText'} for c in x['citations']]
    blind.append(v)
  path=ROOT/'audits/blind-W03-L11-v2.json';path.write_text(json.dumps(blind,ensure_ascii=False,indent=2)+'\n')
  sha=hashlib.sha256(path.read_bytes()).hexdigest()
  manifest={'batchId':BATCH,'revisedQuestions':len(modified),'preservedAcceptedQuestions':len(accepted),'newQuestions':len(new),'blindQuestions':len(blind),'blindPacketSha256':sha,'acceptedHashesPreserved':True,'independentReviewPending':True,'blindEvidenceTextOmitted':True,'questionBatchSha256':hashlib.sha256((ROOT/'data/question-batches/W03-L11.json').read_bytes()).hexdigest()}
  (ROOT/'audits/W03-L11-v2-packet-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  print('FROZEN',len(blind),sha)
 else:print('CHECKPOINT',len(modified),'revised questions')

# Replace exactly the 17 independently flagged distractor sets. Option IDs and keys stay fixed.
rewrite('P0356-Q02',[
 'Inverse dynamics: torques for a prescribed motion in control; forward dynamics: motion under applied torques in simulation',
 'Inverse dynamics: motion under applied torques in simulation; forward dynamics: torques for a prescribed motion in control',
 'Inverse dynamics: torques for a prescribed motion in control; forward dynamics: torques for a prescribed motion in simulation',
 'Inverse dynamics: motion under applied torques in control; forward dynamics: motion under applied torques in simulation'],[
 'The source associates the motion-to-torque inverse problem with control and the torque-to-motion forward problem with simulation.',
 'This reverses both the input/output directions and the application labels given on the slide.',
 'The inverse half is correct, but the forward problem predicts motion from torque rather than repeating the inverse torque calculation.',
 'The forward half is correct, but the inverse problem starts from the desired motion and computes its required torque.'],
 'Which pairing matches the inverse- and forward-dynamics applications explicitly listed in the lecture?')
rewrite('P0358-Q02',[
 'One term comes from differentiating R v_B, and one from the relative-motion part of differentiating ω×(R q_B)',
 'Both terms come from differentiating R v_B; differentiating ω×(R q_B) supplies no relative-velocity term',
 'Both terms come from differentiating ω×(R q_B); differentiating R v_B supplies only relative acceleration',
 'One term comes from differentiating ω itself, and one from differentiating R v_B; differentiating R q_B contributes neither'],[
 'The product rule gives d(R v_B)/dt=R a_B+ω×v_rel and ω×d(R q_B)/dt=ω×v_rel+ω×(ω×r). The two identical velocity terms add.',
 'Differentiating R v_B contributes one, not two, transport terms. The other comes from the relative-motion part of d(R q_B)/dt.',
 'Differentiating ω×(R q_B) contributes one relative-velocity term; the rotating basis in R v_B contributes the other.',
 'Differentiating ω gives α×r, not ω×v_rel. The omitted derivative of R q_B supplies the second velocity term.'])
x=q('P0358-Q02');x['assumptions']+=['v_B=dq_B/dt and a_B=d²q_B/dt² are the point’s relative velocity and acceleration expressed in B; v_rel=R v_B.']
x['solution']['steps']=['Differentiate v_Q=R v_B+ω×r for the coincident fixed-origin case, with r=R q_B.', 'Use d(R v_B)/dt=R a_B+ω×(R v_B).', 'Use d(ω×r)/dt=α×r+ω×(R v_B+ω×r).', 'Collect the two copies of ω×(R v_B) to obtain 2ω×v_rel.']
x['solution']['formulas']=[fm('d(R v_B)/dt=R a_B+ω×v_rel; d(ω×r)/dt=α×r+ω×v_rel+ω×(ω×r)',{'R':'rotation mapping B components into A','q_B':'point offset from B origin, expressed in B','v_B':'dq_B/dt measured relative to B','a_B':'d²q_B/dt² measured relative to B','r':'R q_B, expressed in A','v_rel':'R v_B, expressed in A','ω':'B angular velocity relative to A, expressed in A','α':'B angular acceleration relative to A, expressed in A','t':'time'},{'R':'dimensionless','q_B,r':'m','v_B,v_rel':'m/s','a_B':'m/s²','ω':'rad/s','α':'rad/s²','t':'s'},x['assumptions'])]
rewrite('P0363-Q04',[
 'No; diagonalization chooses principal directions for the tensor about the stated origin',
 'Yes; principal moments remain unchanged under every translation of the origin',
 'Yes; choosing principal directions automatically relocates the origin to the COM',
 'No; principal directions can be defined only when the origin is already at the COM'],[
 'Changing orientation diagonalizes the tensor for a specified origin; changing that origin generally changes the inertia tensor and its principal moments.',
 'Rotation at a fixed origin preserves eigenvalues, but origin translation generally changes them through the parallel-axis term.',
 'An orientation change does not translate the reference origin; a principal basis may be chosen about a non-COM origin.',
 'A symmetric inertia tensor can be diagonalized about a non-COM origin too; the origin must be stated, not necessarily placed at the COM.'])
rewrite('P0364-Q03',[
 'Uniform mass density throughout the occupied volume',
 'A symmetric outer shape with unrestricted internal density',
 'The same average density as a uniform body of that shape',
 'Constant density along one coordinate direction, with unrestricted variation in the others'],[
 'Uniform density makes mass weighting proportional to volume weighting, so the COM equals the volume centroid.',
 'Outer geometric symmetry alone does not constrain internal mass density; extra mass on one side can move the COM.',
 'Equal average density fixes total mass, not where that mass lies. The first mass moment can still differ.',
 'Variation in the other directions can shift the COM away from the volume centroid; constancy along one direction is insufficient.'],
 'Which condition is sufficient to guarantee that a solid’s COM equals its geometric volume centroid?')
rewrite('P0364-Q04',[
 'The point-mass replacement preserves total mass and COM but discards the body’s inertia about its COM',
 'The point-mass replacement preserves the full rotational inertia but changes the translational force balance',
 'The point-mass replacement preserves all moments once the COM offset from the rotation axis is known',
 'The point-mass replacement preserves rotational response because every applied torque acts through the COM'],[
 'Total mass and COM are enough for the translational mass description, but the distributed body can have nonzero central rotational inertia that a point at the COM lacks.',
 'This reverses the distinction: the translational mass description is retained, while the mass spread relevant to rotation is lost.',
 'The COM offset supplies only the parallel-axis contribution; the body’s intrinsic COM tensor must also be retained.',
 'A body can experience an applied couple or off-center forces, and its torque response depends on its inertia, not only on COM location.'])
rewrite('P0367-Q01',[
 'Symmetry and positive definiteness',
 'Symmetry and positive diagonal entries only',
 'Symmetry and a positive trace only',
 'Diagonal form in every rotated frame and positive diagonal entries'],[
 'These are the two properties explicitly named for a nondegenerate positive-mass solid. They are necessary constraints, not a complete physical-realizability test: the principal moments must also obey the source-integral triangle inequalities.',
 'Positive diagonal entries do not guarantee positive quadratic form in every direction; a symmetric matrix can still have a negative eigenvalue.',
 'A positive trace can coexist with negative eigenvalues, so it does not enforce positive definiteness.',
 'The tensor is diagonal in a principal basis, not generally in every rotated basis unless the inertia is isotropic.'])
rewrite('P0367-Q02',[
 'A constrained parameterization or enforcement step must impose the claimed properties on the predictions',
 'A finite penalty for constraint violations guarantees that every prediction satisfies the constraints exactly',
 'Checking finitely many training predictions proves that every future prediction obeys the constraints',
 'Replacing a matrix by its symmetric part also guarantees that it is positive definite'],[
 'The model must actually enforce the particular constraints being claimed; the name “physics-informed” alone supplies no mathematical guarantee.',
 'A soft penalty can discourage violations without making them impossible; an exact hard guarantee needs an appropriate constraint mechanism.',
 'Checks on a finite sample do not prove a property for every possible new input.',
 'Symmetrization enforces symmetry, but a symmetric matrix may still have zero or negative eigenvalues.'],
 'Which implementation requirement correctly qualifies the slide’s proposal to encode hard inertia constraints in a physics-informed model?')
rewrite('P0371-Q05',[
 'Its mass lies in a negligibly thin wall at geometric radius R',
 'It may have any wall thickness if R is the outside radius',
 'It may have any wall thickness if R is the arithmetic mean of the inner and outer radii',
 'Its central axis may be perpendicular to the cylinder’s length while R remains the wall radius'],[
 'About the longitudinal axis, every mass element of the ideal thin wall is at distance R, giving ∫R² dm=mR².',
 'A thick wall also contains mass at radii smaller than the outside radius, so using the outside radius for every element overstates its axial inertia.',
 'The arithmetic mean radius does not generally equal the root-mean-square radius required by the squared-distance integral.',
 'The table’s cylinder formula is for the longitudinal axis; a transverse-axis moment also depends on axial mass distribution and length.'],
 'For rotation about the longitudinal central axis, what missing geometric condition makes the table’s hollow-cylinder formula mR² valid when R is the wall radius?')
rewrite('P0372-Q03',[
 'Batteries, actuators and counterweights',
 'Sensors, wiring harnesses and protective covers',
 'Grippers, payloads and tool-changing fixtures',
 'Cooling fans, cable carriers and control boards'],[
 'This is the three-part list explicitly named in the COM-placement bullet.',
 'These components also have mass, but this is not the particular list given in the cited COM-placement bullet.',
 'These can affect mass distribution, but the source’s named examples are batteries, actuators and counterweights.',
 'These may matter in an actual design, but they are not the source’s stated three examples.'],
 'Which three component categories are explicitly listed in the source’s COM-placement bullet?')
rewrite('P0372-Q05',[
 'Reduce link mass while meeting the required stiffness',
 'Maximize link stiffness regardless of the added mass',
 'Minimize link mass regardless of the remaining stiffness',
 'Preserve link mass while minimizing its external volume'],[
 'The source links hollow tubes, I-beams, lattices and topology optimization to reducing mass while maintaining stiffness.',
 'This drops the mass-reduction objective and permits arbitrarily heavy designs, unlike the stated tradeoff.',
 'This drops the stiffness requirement; a lighter but excessively flexible link does not meet the stated goal.',
 'The source does not set fixed mass and minimum external volume as the objective of this bullet.'])
rewrite('P0373-Q01',[
 'Symmetry aligned with the relevant coordinate planes can cancel the corresponding off-diagonal products',
 'Any one symmetry plane makes all three principal moments equal',
 'Putting the origin at the COM makes every product vanish regardless of the axis directions',
 'Symmetry of the outer shape alone cancels products even when its mass density is asymmetric'],[
 'For a mass-symmetry reflection, products odd in the reflected coordinate cancel. This can remove off-diagonal coupling in suitably chosen axes.',
 'One symmetry plane imposes only particular product cancellations; it does not require equal principal moments.',
 'The COM condition removes first mass moments, not every second cross moment. Principal orientation is a separate issue.',
 'The symmetry must apply to the mass distribution, including density, not merely to the visible boundary.'])
rewrite('P0373-Q02',[
 'Motor inertia approximately equals the load inertia referred to the same drive coordinates',
 'Motor inertia approximately equals the load’s unreferred inertia regardless of the transmission ratio',
 'Motor mass approximately equals load mass regardless of their mass distributions',
 'Motor inertia approximately equals the sum of motor inertia and a positive reflected load inertia'],[
 'This retains the slide’s approximate matching heuristic while comparing inertia quantities in consistent drive coordinates.',
 'The comparison must account for the transmission reference; ignoring it conflicts with the source’s use of gear-ratio tuning.',
 'Equal masses can have different inertias because squared distance from the rotation axis matters.',
 'Adding the positive load contribution to the motor side is not the source’s motor-versus-load matching criterion.'])
rewrite('P0374-Q02',[
 'No; Pxz and Pyz vanish, but Pxy may remain nonzero',
 'Yes; Pxy, Pxz and Pyz all vanish solely from that reflection',
 'No; Pxy and Pxz vanish, but Pyz may remain nonzero',
 'No; Pxy and Pyz vanish, but Pxz may remain nonzero'],[
 'Reflection through xy changes z to −z, so xz and yz contributions cancel while xy is unchanged.',
 'The xy integrand does not change sign under z reflection, so this symmetry alone does not force Pxy to vanish.',
 'This uses the cancellation pattern for a plane normal to x rather than to z.',
 'This uses the cancellation pattern for a plane normal to y rather than to z.'])
rewrite('P0374-Q07',[
 'Eigenvalues are principal moments; eigenvectors give principal-axis directions',
 'Eigenvalues give principal-axis directions; eigenvectors are principal moments',
 'Eigenvalues are diagonal entries in every basis; eigenvectors are the current coordinate axes',
 'Eigenvalues are raw products of inertia; eigenvectors give their associated coordinate planes'],[
 'A real symmetric inertia tensor has an orthonormal eigenbasis; its eigenvalues are the moments in those principal directions.',
 'This reverses the scalar eigenvalue and vector eigenvector roles.',
 'Arbitrary coordinate axes need not be eigenvectors, and arbitrary diagonal components need not be eigenvalues.',
 'Raw products describe off-diagonal cross moments, not the eigenvalues of the tensor.'])
rewrite('P0374-Q09',[
 'An inertia-pendulum experiment',
 'A driven-rotation torque–acceleration experiment',
 'A turntable spin-up experiment with a calibrated motor',
 'A component-weighing and mass-location survey'],[
 'The slide explicitly names an inertia pendulum as an example measurement device.',
 'A suitable driven experiment can be relevant to inertia identification, but this is not the example named on the slide.',
 'A calibrated spin-up experiment may provide useful data, but the source explicitly names an inertia pendulum instead.',
 'Mass and position measurements can support an inertia estimate, but this is not the cited example device.'])
rewrite('P0375-Q04',[
 'All three off-diagonal entries are zero in the encoded inertial-frame basis',
 'The three diagonal entries are positive, even if the off-diagonal entries are nonzero',
 'The inertial origin is at the COM, regardless of the orientation of its axes',
 'The frame is translated along z, which by itself turns any inertia tensor into diagonal form'],[
 'Zero off-diagonal entries mean that the coordinate axes are eigenvector directions, so the diagonal entries are principal moments in this example.',
 'Positive diagonal entries do not make the coordinate axes eigenvectors when off-diagonal coupling remains.',
 'COM location fixes the reference point; a separate orientation choice is needed for principal axes.',
 'Translation changes the reference point through a parallel-axis correction; it is not a general diagonalizing rotation.'])
rewrite('P0375-Q07',[
 'Compute CAD mass properties in SolidWorks and export them with a SolidWorks-to-URDF plugin',
 'Measure inertia with a pendulum and manually enter the parameters into the URDF file',
 'Approximate each link by simple solids and manually assemble their inertial parameters in URDF',
 'Identify link parameters from measured robot motion and write the estimates into URDF'],[
 'The bottom of the source slide specifically recommends the CAD mass-properties and SolidWorks-to-URDF export workflow.',
 'Measurement is discussed on the preceding slide, but it is not the workflow explicitly recommended at the bottom of this slide.',
 'An approximate composite-solid calculation is possible, but it is not the named CAD-export workflow.',
 'Identification from motion is a different possible workflow, not the recommendation printed here.'])
save(False)

# Every independently flagged classification is changed to the requested level.
for key, findings in summary['actionableFlags'].items():
 for finding in findings:
  if finding['check']=='difficulty':
   m=re.search(r'Change (?:medium|hard|extremely_tricky) to (easy|medium|hard)',finding['finding'])
   assert m, finding
   q(key[len(BATCH)+1:])['difficulty']=m.group(1)

# Repair the two explanations without changing the accepted keys.
x=q('P0355-Q02')
old='One rotation is a planar constraint, not a general spatial body.'
replacement='Three translations plus one rotation provide only one independent orientation change, not the three needed for a free spatial body. A planar rigid body instead has two in-plane translations and one rotation.'
x['solution']['optionExplanations']['o2']='Incorrect. '+replacement
x['solution']['misconceptions']=[replacement if v==old else v for v in x['solution']['misconceptions']]
x=q('P0372-Q02')
x['stem']='A 2 kg point-like component is relocated from a perpendicular distance of 0.6 m to 0.3 m from the same fixed joint axis. What happens to its moment contribution?'
x['assumptions']=['The component mass remains 2 kg; only its perpendicular distance from the same fixed axis changes.', 'Treat the component as a point mass; other components and their locations remain unchanged.']
for o in x['options']:
 for a,b in [('remains0','remains 0'),('to2','to 2'),('from0','from 0'),('to0','to 0'),('of75','of 75'),('of50','of 50')]:o['text']=o['text'].replace(a,b)
x['solution']['justification']='At fixed mass, I=m r_perp². Halving the perpendicular distance quarters the moment: 0.72 kg·m² becomes 0.18 kg·m², a 75% reduction.'
x['solution']['optionExplanations']['o1']='Correct. '+x['solution']['justification']
x['solution']['simpleExplanation']='Moving the same mass twice as close to the axis makes its point-mass inertia four times smaller.'
x['solution']['steps']=['I_old=(2 kg)(0.6 m)²=0.72 kg·m².', 'I_new=(2 kg)(0.3 m)²=0.18 kg·m².', 'ΔI=I_new−I_old=2(0.3²−0.6²)=−0.54 kg·m².', 'The fractional reduction is (I_old−I_new)/I_old=0.54/0.72=0.75, or 75%.']
x['solution']['formulas']=[fm('I=m r_perp²; I_old=m r_old²; I_new=m r_new²; ΔI=I_new−I_old=m(r_new²−r_old²)',{'I':'point-mass moment about the fixed joint axis','m':'unchanged component mass','r_perp':'perpendicular distance from the axis','I_old,I_new':'moments before and after relocation','r_old,r_new':'old and new perpendicular distances from the same axis','ΔI':'new moment minus old moment'},{'I,I_old,I_new,ΔI':'kg·m²','m':'kg','r_perp,r_old,r_new':'m'},x['assumptions'])]

# Explicit body attachment and observer/basis distinctions resolve the two ambiguities.
x=q('P0358-Q05')
x['stem']='A point Q is fixed in rotating frame B. At the instant considered, ω=(0,0,0) rad/s, α=(0,0,3) rad/s² and its offset from the B origin is r=(2,0,0) m, all expressed in A. If the B-origin acceleration relative to A is a0=(0,0,0) m/s², what is Q’s acceleration relative to A, expressed in A?'
x['assumptions']+=['Q is body-fixed in B: q_B is constant, so v_rel=R dq_B/dt=0 and a_rel=R d²q_B/dt²=0.', 'r=R q_B is its instantaneous offset expressed in A; it is not assumed constant as an A-expressed vector over time.']
x['solution']['steps']=['Because q_B is constant, both relative velocity and relative acceleration vanish.', 'At this instant a0=0 and ω=0, so the origin, Coriolis and centripetal terms vanish.', 'The remaining term is α×r=(0,0,3)×(2,0,0)=(0,6,0) m/s².']
x['solution']['formulas'][0]['assumptions']=copy.deepcopy(x['assumptions'])
x=q('P0360-Q04')
x['stem']='At an instant, R_AB maps B components to A by a right-handed +90° rotation about z. Given α_AB=(1,0,0) rad/s² and ω_AB=(0,0,1) rad/s in A, and α_BC=(2,0,0) rad/s² and ω_BC=(3,0,0) rad/s in B, what is α_AC expressed in A?'
x['assumptions']=['α_AB and ω_AB describe B relative to A and are expressed in A.', 'α_BC and ω_BC describe C relative to B and are expressed in B.', 'α_AC is C’s angular acceleration relative to A, expressed in A. R_AB maps B-coordinate vectors to A.', 'The bases are right-handed and orthonormal; all summed vectors and cross-product operands are expressed in A.']
x['solution']['formulas']=[fm('α_AC=α_AB+R_AB α_BC+ω_AB×(R_AB ω_BC)',{'α_AC':'C angular acceleration relative to A, expressed in A','α_AB':'B angular acceleration relative to A, expressed in A','α_BC':'C angular acceleration relative to B, expressed in B','ω_AB':'B angular velocity relative to A, expressed in A','ω_BC':'C angular velocity relative to B, expressed in B','R_AB':'rotation mapping B components into A'},{'α_AC,α_AB,α_BC':'rad/s²','ω_AB,ω_BC':'rad/s','R_AB':'dimensionless'},x['assumptions'])]
x['solution']['steps']=['R_AB=[[0,−1,0],[1,0,0],[0,0,1]].', 'R_AB α_BC=(0,2,0) rad/s²; R_AB ω_BC=(0,3,0) rad/s.', 'ω_AB×(R_AB ω_BC)=(0,0,1)×(0,3,0)=(−3,0,0) rad/s².', 'α_AC=(1,0,0)+(0,2,0)+(−3,0,0)=(−2,2,0) rad/s².']

# Precise source conflicts are bound to the revised question, not treated as global PDF repairs.
def resolve(short,page,claim,basis,method,conflict_pages):
 x=q(short)
 x['conflictResolution']={'status':'derived-qualification-pending-independent-review','questionVersion':2,'sourceId':'lectures','sourceSha256':x['citations'][0]['sourceSha256'],'physicalPage':page,'sourceClaim':claim,'basis':basis,'method':method,'scope':'This question version only; the source PDF is unchanged, the source-dispute ledger remains in force, and independent re-review is required.'}
 for c in x['citations']:
  if c['role']=='conflict' and c['physicalPage'] not in conflict_pages:c['role']='premise'
resolve('P0368-Q05',368,
 'p362 defines Ixy=∫xyρ dV, while p368 prints Ixy,A=Ixy,C−m xc yc using the same scalar symbol; p369 substitutes the negative corner tensor entry −mwl/4.',
 'p362 raw-product integral, p368 matrix theorem, and p369 zero-COM-product example. In parallel axes about COM C, expand x=x_C+xc and y=y_C+yc. The first central moments vanish, giving Pxy,A=Pxy,C+m xc yc. For the signed matrix entry I12=−Pxy, I12,A=I12,C−m xc yc.',
 'Symbolic expansion of the supplied mass-product definition and the off-diagonal element of the matrix parallel-axis theorem; the author checks both signs and the box cancellation. Treat the later scalar minus rule as a signed-entry rule, not as a raw-product rule.', {362,368})
x=q('P0368-Q05')
for o in x['options']:
 if o['id']=='o1':o['text']='The same Ixy symbol is used first for the raw product ∫xy dm and later for its negative signed tensor entry'
x['assumptions']=['C is the COM and the axes are parallel. The explicit repair uses Pxy for the raw integral and I12=−Pxy for the signed tensor entry.', '“Raw product” does not mean the integral is necessarily positive; its sign depends on the mass distribution.']
x['solution']['steps']=['Name the p362 quantity Pxy=∫xy dm to distinguish it from the matrix entry.', 'With x=x_C+xc and y=y_C+yc, expand ∫xy dm. At the COM, ∫x_C dm=∫y_C dm=0.', 'Thus Pxy,A=Pxy,C+m xc yc, whereas I12,A=−Pxy,A=I12,C−m xc yc.', 'The p369 corner value −mwl/4 and its zero COM value use this signed-entry convention.']
resolve('P0372-Q04',372,
 'Strategic placement of batteries, actuators and counterweights keeps system COM stable across all configurations.',
 'p364 gives the mass-weighted COM. If a nonzero-mass link changes its base-frame COM position with configuration, the weighted sum generally changes unless other motions compensate. Component placement is therefore a design objective to verify over the intended configurations and support conditions, not an automatic universal guarantee.',
 'Configuration-dependent evaluation of the source COM formula; a two-component counterexample in the author checks changes one component position while keeping masses fixed.', {372})
x=q('P0372-Q04');x['solution']['steps']=['Use the source formula r_COM=Σ mi ri/Σ mi in one base frame.', 'In an articulated robot, component positions ri may depend on configuration, so the weighted sum may change.', 'Strategic placement may improve the design, but configuration-dependent COM and support checks remain necessary.']
x['solution']['formulas']=[fm('r_COM(q)=Σ mi ri(q)/Σ mi',{'r_COM(q)':'system COM in the fixed base frame at configuration q','q':'robot configuration, represented by joint coordinates','mi':'mass of component i','ri(q)':'COM position of component i in the same base frame'},{'r_COM,ri':'m','mi':'kg','q':'rad for revolute coordinates, m for prismatic coordinates'},['Positive total mass; sum over every component; all positions expressed in one base frame.'])]
resolve('P0373-Q03',373,
 'Motor inertia ≈ load inertia maximizes power transfer efficiency. AI tunes gear ratios to match this condition.',
 'The cited bullet states a heuristic but gives no drive equations, transmission-reference convention, loss model or optimization objective establishing an efficiency maximum. Approximate matching can be retained as a source-attributed design target, not promoted to a theorem for every drive.',
 'Scope qualification: one equality between inertia parameters cannot establish universal optimality without the missing relation between those parameters and the chosen objective. No alternative universal optimum is asserted.', {373})
resolve('P0374-Q03',374,
 'Moments of inertia must always be positive.',
 'p362 defines each moment as an integral of squared perpendicular coordinates against nonnegative mass. Thus every moment is nonnegative. It is zero if all idealized mass lies on the selected axis and strictly positive when nonzero mass lies off that axis.',
 'Direct squared-distance derivation and an axis-supported positive-mass counterexample. Ordinary nondegenerate three-dimensional solids retain strictly positive moments; the exception concerns ideal line/point distributions.', {374})
x=q('P0374-Q03');x['assumptions']=['Mass is nonnegative; idealized axis-supported point or line distributions are allowed.']
x['solution']['steps']=['For example, Ixx=∫(y²+z²) dm with dm≥0, so Ixx≥0.', 'If all mass lies on the x axis, y=z=0 on its support and Ixx=0.', 'If nonzero mass lies off the axis, the squared-distance integral is positive.']
x['solution']['formulas']=[fm('I_axis=∫r_perp² dm ≥ 0',{'I_axis':'moment of inertia about the selected axis','r_perp':'perpendicular distance of a mass element from that axis','dm':'nonnegative mass element'},{'I_axis':'kg·m²','r_perp':'m','dm':'kg'},x['assumptions'])]
for short in ['P0376-Q01','P0376-Q02']:
 resolve(short,376,
  'Under “Generalised case of linear acceleration”, p376 prints the relative, Coriolis, angular-acceleration and centripetal terms but no B-origin acceleration.',
  'p359 explicitly includes the B-origin acceleration relative to A in the separated-origin formula. p358 is the coincident fixed-origin case. With identical symbols and observer, subtracting the p376 expression from p359 leaves precisely a0. The shortened formula is valid only when this omitted vector is zero.',
  'Term-by-term comparison of the supplied equations and differentiation of p_A=p_AB+R_AB q_B. The author checks a purely accelerating translation as a counterexample and the a0=0 special case.', {376})
# Supplement the necessary inertia-integral premise used in the new distractor rationale.
x=q('P0367-Q01')
c=copy.deepcopy(oldQ[BATCH+'-P0362-Q01']['citations'][0]);c['role']='premise';x['citations'].append(c)
# Explicit definitions improve revised formula records without touching approved objects.
for key in modified:
 for f in Q[key]['solution']['formulas']:
  if 'Pxy=∫xy dm' in f['expression']:
   f['variables'].update({'r':'(x,y,z)ᵀ: mass-element position relative to the specified origin','x,y,z':'Cartesian components of r in the common orthonormal frame','dm':'differential mass, equal to ρ dV for a volumetric density','ρ':'mass density','dV':'differential volume','I3':'3×3 identity matrix','I[1,2]':'row 1, column 2 signed tensor entry, also written I12'})
   f['units'].update({'x,y,z':'m','ρ':'kg/m³','dV':'m³','I3':'dimensionless','I[1,2]':'kg·m²'})
  if f['expression']=='I_A=I_C+m[(pᵀp)I3−ppᵀ]':
   f['variables']['p']='(xc,yc,zc)ᵀ: COM position relative to A in the common orientation'
   f['variables']['xc,yc,zc']='Cartesian components of the COM offset p'
   f['units'].update({'xc,yc,zc':'m','I3':'dimensionless'})
# Natural spacing only inside the 39 revised objects.
replacements={'p362':'p362','factor2':'factor 2','mass3':'mass 3','length2':'length 2','mass6':'mass 6','sides2':'sides 2','and4':'and 4','mass1.5':'mass 1.5','byL/2':'by L/2','A3×3':'A 3×3','the3':'the 3'}
def polish(v):
 if isinstance(v,str):
  for a,b in replacements.items():v=v.replace(a,b)
  return v
 if isinstance(v,list):return [polish(i) for i in v]
 if isinstance(v,dict):return {k:polish(z) for k,z in v.items()}
 return v
for key in modified:
 for field in ('stem','assumptions','solution'):Q[key][field]=polish(Q[key][field])
 for option in Q[key]['options']:option['text']=polish(option['text'])
save(False)

# The independent coverage review found one unique p357 angular derivative/shorthand gap.
x=copy.deepcopy(oldQ[BATCH+'-P0357-Q01'])
x.update({'id':BATCH+'-P0357-Q05','version':1,'status':'draft','reviewIds':[],
 'stem':'The lecture writes ω̇_A when differentiation is understood relative to universal frame U. Let Ω_A^U(t) be the angular velocity of frame A relative to U, expressed in the fixed U basis. Which definition and interpretation of ω̇_A is correct?',
 'type':'definition','difficulty':'easy','cognitiveSkill':'recall',
 'assumptions':['All angular-velocity samples and the resulting angular acceleration use the same fixed U basis.', 'Ω_A^U is differentiable at the time considered. Time is in seconds and angular velocity is in rad/s.'],
 'options':[
  {'id':'o2','text':'lim Δt→0 [Ω_A^U(t)−Ω_A^U(t+Δt)]/Δt; angular acceleration of A relative to U'},
  {'id':'o3','text':'lim Δt→0 [Ω_A^U(t+Δt)−Ω_A^U(t)]/(Δt)²; angular acceleration of A relative to U'},
  {'id':'o1','text':'lim Δt→0 [Ω_A^U(t+Δt)−Ω_A^U(t)]/Δt; angular acceleration of A relative to U'},
  {'id':'o4','text':'lim Δt→0 [Ω_A^U(t+Δt)−Ω_A^U(t)]/Δt; linear acceleration of the origin of A relative to U'}],
 'correctOptionIds':['o1']})
x['citations'][0].update({'kind':'equation','locator':'Printed slide 6, angular-acceleration difference quotient (middle) and universal-reference shorthand ω̇_A=ᵁΩ̇_A (bottom).','evidenceText':'ᴬΩ̇_B=d(ᴬΩ_B)/dt=lim Δt→0 [ᴬΩ_B(t+Δt)−ᴬΩ_B(t)]/Δt. If the reference frame of differentiation is understood as {U}, ω̇_A=ᵁΩ̇_A.','region':{'x':0.02,'y':0.38,'width':0.86,'height':0.51}})
x['solution']={'justification':'The dot means a time derivative, formed from the forward angular-velocity difference divided by the time increment. The suppressed universal reference is U, and the subscript A identifies the rotating frame, not a point acceleration.',
 'optionExplanations':{'o1':'Correct. This is dΩ_A^U/dt, the angular acceleration of A relative to U, expressed in U, with units rad/s².','o2':'Incorrect. Reversing the difference gives the negative of the stated derivative.','o3':'Incorrect. A first derivative divides by Δt, not (Δt)². This expression generally has no finite derivative limit and has units rad/s³ before taking the limit.','o4':'Incorrect. The displayed difference is an angular-velocity derivative. Linear acceleration of A’s origin instead differentiates its linear velocity and is denoted v̇_A in the neighboring shorthand.'},
 'steps':['Hold the reference observer and expression basis fixed as U.', 'Subtract the earlier angular velocity from the later angular velocity and divide by Δt.', 'Take the Δt→0 limit to obtain the angular acceleration; the abbreviated symbol is ω̇_A.'],
 'formulas':[fm('ω̇_A=dΩ_A^U/dt=lim(Δt→0)[Ω_A^U(t+Δt)−Ω_A^U(t)]/Δt',{'ω̇_A':'angular acceleration of A relative to U, expressed in U','Ω_A^U':'angular velocity of A relative to U, expressed in U','t':'time','Δt':'time increment'},{'ω̇_A':'rad/s²','Ω_A^U':'rad/s','t,Δt':'s'},x['assumptions'])],
 'simpleExplanation':'A dot changes angular velocity into angular acceleration. A names the rotating frame; U remains the reference even when omitted in the shorthand.',
 'memoryAid':'A names whose rotation; U names the reference; the dot means rate of change.',
 'misconceptions':['Reversing the difference reverses the sign.','A first derivative uses one power of the time increment.','Angular acceleration is not the acceleration of a particular origin.'],
 'examTraps':['Do not change expression bases between the two angular-velocity samples.'],
 'prerequisiteConceptIds':[]}
new.append(x);Q[x['id']]=x;batch['questions'].append(x)
concept=next(c for c in batch['concepts'] if c['id']=='W03-L11-P0357-C01')
concept['questionIds'].append(x['id'])
concept['coverageNotes']='The four original questions plus Q05 cover the linear and angular derivative definitions, universal-frame shorthand, numerical linear differentiation and units. The new angular item requires independent review.'
for c in batch['concepts']:c['examinationAngles']=[Q[k]['stem'] for k in c['questionIds']]
ins_path=ROOT/'data/inspection-batches/W03-L11.json'
ins=json.loads(ins_path.read_text());ins['summary']['questions']=len(batch['questions'])
ins_path.write_text(json.dumps(ins,ensure_ascii=False,indent=2)+'\n')

# Additional actual-pixel inspections performed during repair, not inferred from extraction.
notes={
 357:'Printed 6. Visually read angular quotient with one Δt denominator, forward angular-velocity subtraction, and bottom ω̇_A=ᵁΩ̇_A shorthand. This supports new Q05.',
 358:'Printed 7. Product-rule line has two copies of angular velocity crossed with rotated relative velocity, plus angular-acceleration and nested centripetal terms. Body-fixed-point condition is an author clarification, not printed in the general equation.',
 359:'Printed 8. Separated-origin general acceleration explicitly starts with acceleration of BORG relative to A before the four relative/rotational terms.',
 360:'Printed 9. Angular composition re-expresses the B-relative C vector through R_AB before the cross product with A-expressed B angular velocity.',
 362:'Printed 11. Raw xy, xz and yz integrals appear without the matrix-entry minus sign. Moment integrands are sums of squares; density and volume element are defined.',
 368:'Printed 17. Scalar Ixy shift uses minus m xc yc; matrix theorem has minus p pᵀ. Offset is COM relative to A. This scalar convention differs from raw product on p362.',
 369:'Printed 18. Corner-to-COM worked example uses negative corner xy entry −mwl/4 and obtains zero COM entry; z moment uses 1/3 minus 1/4 = 1/12.',
 372:'Printed 21. COM-placement bullet names batteries, actuators, counterweights and makes the all-configurations stability claim. Shape-optimization bullet balances mass reduction and maintained stiffness.',
 373:'Printed 22. Inertia-matching bullet states approximate motor/load equality and power-transfer-efficiency claim without a drive/loss model; agility/stability bullet says per-task tradeoff.',
 374:'Printed 23. One-plane product cancellation, positive-moment wording, orientation-only trace invariant, eigenvalue/eigenvector distinction and inertia-pendulum example are all visible.',
 376:'Printed 25. Summary labelled generalized omits B-origin acceleration, but retains relative, factor-two Coriolis, angular-acceleration and nested centripetal terms.'}
observations=[]
for p,note in notes.items():
 path=ROOT/f'sources/previews/lectures/page-{p:04d}.webp'
 observations.append({'physicalPage':p,'sourceId':'lectures','sourceSha256':x['citations'][0]['sourceSha256'],'previewSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'inspectorId':AUTHOR,'method':'rendered_page','status':'complete','inspectedAt':'2026-10-19T17:15:19Z','notes':note})
(ROOT/'audits/L11-v2-repair-visual-inspections.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2)+'\n')
save(False)
# Keep every new explanatory premise explicit in these already-revised objects.
def cite_from(short,source_short,page=None):
 x=q(short)
 for c in oldQ[BATCH+'-'+source_short]['citations']:
  if page is None or c['physicalPage']==page:
   if c['slideId'] not in {v['slideId'] for v in x['citations']}:
    cc=copy.deepcopy(c);cc['role']='premise';x['citations'].append(cc)
cite_from('P0358-Q05','P0359-Q01',359)
cite_from('P0364-Q04','P0368-Q01',368)
cite_from('P0363-Q04','P0368-Q01',368)
cite_from('P0371-Q05','P0362-Q01',362)
cite_from('P0371-Q06','P0362-Q01',362)
x=q('P0371-Q05')
x['solution']['formulas']=[fm('I_axis=∫r_perp² dm; I_thin_wall=mR²',{'I_axis':'moment about the longitudinal central axis','r_perp':'perpendicular distance of a mass element from that axis','dm':'mass element','I_thin_wall':'longitudinal-axis moment of an ideal thin cylindrical wall','m':'total mass','R':'geometric wall radius'},{'I_axis,I_thin_wall':'kg·m²','r_perp,R':'m','dm,m':'kg'},['All thin-wall mass is at radial distance R; the axis is longitudinal, not transverse.'])]
x=q('P0374-Q02')
x['assumptions']=['Pxy=∫xy dm, Pxz=∫xz dm and Pyz=∫yz dm are raw products in the stated orthonormal frame.', 'The mass distribution, not just its outer shape, is invariant under (x,y,z)→(x,y,−z).']
x['solution']['formulas']=[fm('Pxz=∫xz dm=0; Pyz=∫yz dm=0; Pxy=∫xy dm need not vanish',{'Pxy,Pxz,Pyz':'raw products of inertia in the stated frame','x,y,z':'coordinates of a mass element relative to the specified origin','dm':'mass element'},{'Pxy,Pxz,Pyz':'kg·m²','x,y,z':'m','dm':'kg'},x['assumptions'])]
x['solution']['steps']=['Pair each mass element (x,y,z) with its reflected equal-mass element (x,y,−z).', 'The paired xz and yz products are opposite and cancel.', 'The paired xy products are equal, so this symmetry alone does not force their sum to zero.']

# Exact executable AUTHOR checks. These are not a replacement for independent re-review.
import sympy as sp
from fractions import Fraction
def ids(*shorts):return [BATCH+'-'+short for short in shorts]
def check(key,passed,detail,question_ids=None):
 checks.append({'id':key,'passed':bool(passed),'kind':'author_check_not_independent_review','detail':detail,'questionIds':question_ids or []})
 if not passed:raise AssertionError(key)
M=sp.Matrix;t,h=sp.symbols('t h',real=True)
omega=M([t*t,3*t,0]);quot=(omega.subs(t,t+h)-omega)/h
limit=quot.applyfunc(lambda e:sp.limit(e,h,0))
check('angular-difference-quotient',limit==omega.diff(t) and limit.subs(t,2)==M([4,3,0]),'Forward difference quotient equals angular derivative (2t,3,0); at t=2 the value is (4,3,0) rad/s².',ids('P0357-Q05'))
reverse=((omega-omega.subs(t,t+h))/h).applyfunc(lambda e:sp.limit(e,h,0))
check('angular-reversed-difference',reverse==-limit,'Reversing the difference reverses the derivative sign.',ids('P0357-Q05'))
a,k,v=sp.symbols('a k v',real=True)
def rz(angle):return M([[sp.cos(angle),-sp.sin(angle),0],[sp.sin(angle),sp.cos(angle),0],[0,0,1]])
R=rz(k*t);qb=M([a+v*t,0,0]);rr=R*qb
check('coriolis-two-product-contributions',rr.diff(t,2).subs(t,0)==M([-a*k*k,2*k*v,0]),'Directly differentiating Rz(kt)(a+vt,0,0) twice gives (−ak²,2kv,0) at t=0.',ids('P0358-Q02'))
term1=(R*qb.diff(t)).diff(t).subs(t,0);term2=(M([0,0,k]).cross(R*qb)).diff(t).subs(t,0)
check('coriolis-split',term1==M([0,k*v,0]) and term2==M([-a*k*k,k*v,0]),'The two differentiated velocity terms each supply kv in the y direction.',ids('P0358-Q02'))
bodypoint=rz(sp.Rational(3,2)*t*t)*M([2,0,0])
check('body-fixed-point-zero-instantaneous-omega',bodypoint.diff(t).subs(t,0)==sp.zeros(3,1) and bodypoint.diff(t,2).subs(t,0)==M([0,6,0]),'Constant B coordinates with αz=3 and ωz=0 at t=0 produce acceleration (0,6,0), not zero.',ids('P0358-Q05'))
R90=rz(sp.pi/2);alph= M([1,0,0])+R90*M([2,0,0])+M([0,0,1]).cross(R90*M([3,0,0]))
check('angular-composition-explicit-bases',alph==M([-2,2,0]),'R_AB rotates both B-expressed inputs before addition/cross product; α_AC=(−2,2,0) rad/s².',ids('P0360-Q04'))
old=2*sp.Rational(3,5)**2;newI=2*sp.Rational(3,10)**2
check('fixed-mass-relocation',old==sp.Rational(18,25) and newI==sp.Rational(9,50) and newI-old==-sp.Rational(27,50) and (old-newI)/old==sp.Rational(3,4),'0.72→0.18 kg·m²; ΔI=−0.54 kg·m²; reduction 75%.',ids('P0372-Q02'))
xC,yC,xc,yc,m=sp.symbols('x_C y_C xc yc m',real=True)
expanded=sp.expand((xC+xc)*(yC+yc))
check('raw-product-shift-expansion',expanded==xC*yC+xc*yC+yc*xC+xc*yc,'After integration, COM first moments vanish and the raw product gains +m xc yc; its signed negative loses that term.',ids('P0368-Q04','P0368-Q05'))
w,l=sp.symbols('w l',positive=True)
check('box-signed-entry-cancellation',sp.simplify(-m*w*l/4+m*(w/2)*(l/2))==0,'The signed corner entry plus m xc yc recovers zero at the COM.',ids('P0368-Q05'))
check('box-midpoint',sp.integrate(t,(t,0,w))/w==w/2 and sp.integrate(t,(t,0,l))/l==l/2,'Uniform first moments give midpoint coordinates.',ids('P0369-Q01'))
pts=[M([1,2,3]),M([1,2,-3])]
Pxy=sum(p[0]*p[1] for p in pts);Pxz=sum(p[0]*p[2] for p in pts);Pyz=sum(p[1]*p[2] for p in pts)
check('one-symmetry-plane-counterexample',(Pxy,Pxz,Pyz)==(4,0,0),'Two equal unit masses reflected through xy have raw products (4,0,0) kg·m².',ids('P0374-Q02','P0373-Q01'))
Iline=sum((p.dot(p)*sp.eye(3)-p*p.T for p in [M([1,0,0]),M([-1,0,0])]),sp.zeros(3))
check('axis-supported-zero-moment',Iline==sp.diag(0,2,2),'Positive mass on the x axis has Ixx=0: a counterexample to unqualified strict positivity.',ids('P0374-Q03'))
A=M([[1,2,0],[2,1,0],[0,0,1]])
check('positive-diagonal-not-positive-definite',all(A[i,i]>0 for i in range(3)) and min(A.eigenvals())==-1,'Symmetric positive-diagonal matrix has eigenvalues −1,1,3.',ids('P0367-Q01','P0367-Q02'))
check('positive-trace-not-positive-definite',sp.trace(sp.diag(-1,2,2))>0 and min(sp.diag(-1,2,2).eigenvals())<0,'Positive trace is weaker than positive definiteness.',ids('P0367-Q01'))
check('positive-definite-not-complete-physical-test',sp.diag(1,1,3).is_positive_definite and 1+1-3<0,'diag(1,1,3) is positive definite but violates the inertia triangle inequality.',ids('P0367-Q01'))
Icom=sp.diag(1,2,3);p=M([1,2,0]);Ishift=Icom+2*(p.dot(p)*sp.eye(3)-p*p.T)
check('origin-shift-not-principal-rotation',Ishift!=Icom and sp.trace(Ishift)!=sp.trace(Icom),'COM-to-origin shift changes the tensor and generally principal moments; rotating at the same origin is different.',ids('P0363-Q04','P0375-Q04'))
rotated=rz(sp.pi/4)*sp.diag(1,2,3)*rz(sp.pi/4).T
check('com-origin-not-enough-for-diagonal',rotated[0,1]!=0 and sorted(rotated.eigenvals())==[1,2,3],'A COM tensor rotated away from its principal basis has nonzero off-diagonal entries.',ids('P0373-Q01','P0375-Q04'))
J=M([[2,1,0],[1,2,0],[0,0,4]])
check('principal-eigenpair',J*M([1,1,0])==3*M([1,1,0]),'Eigenvalue is a scalar moment; eigenvector is an axis direction.',ids('P0374-Q07'))
r,Ri,Ro=sp.symbols('r Ri Ro',positive=True)
thick=sp.simplify(sp.integrate(r**3,(r,Ri,Ro))/sp.integrate(r,(r,Ri,Ro)))
check('thick-cylinder-not-mean-radius-square',sp.simplify(thick-(Ri*Ri+Ro*Ro)/2)==0 and sp.simplify(thick-((Ri+Ro)/2)**2-(Ri-Ro)**2/4)==0,'For a uniform annular section, mean r²=(Ri²+Ro²)/2, not the arithmetic-mean radius squared unless the wall thickness vanishes.',ids('P0371-Q05'))
check('thin-wall-limit',sp.limit(thick,Ri,Ro)==Ro*Ro,'The thin-wall radial limit recovers R² per unit mass.',ids('P0371-Q05'))
com_initial=(2*M([0,0,0])+M([1,0,0]))/3
com_final=(2*M([0,0,0])+M([2,0,0]))/3
check('configuration-dependent-com',com_initial!=com_final,'With masses 2 kg and 1 kg, moving the second COM from x=1 to x=2 changes system COM from x=1/3 to x=2/3 m.',ids('P0372-Q04'))
a0=M([1,2,3]);offset=M([2,0,0]);translation=M([t*t/2,t*t,3*t*t/2])+offset
check('summary-omission-translation-counterexample',translation.diff(t,2)==a0,'For a fixed point in a nonrotating but accelerating B frame, general acceleration equals a0; the omitted-origin summary would give zero.',ids('P0376-Q01','P0376-Q02'))
check('summary-zero-origin-special-case',sp.simplify((rr.diff(t,2)+a0)-rr.diff(t,2))==a0,'General minus omitted-origin expression is exactly a0, so equality requires a0=0.',ids('P0376-Q01','P0376-Q02'))
check('accepted-objects-unchanged',all(Q[k]==oldQ[k] and digest(Q[k])==h for k,h in accepted.items()),'All 69 accepted objects and independent-review hashes equal the immutable v1 archive.')
check('only-flagged-originals-revised',modified==flags and all(Q[k]['version']==2 for k in flags),'Exactly 39 flagged original question IDs are revised to v2; the additional question is a separate v1 draft.')
check('original-keys-preserved',all(Q[k]['correctOptionIds']==oldQ[k]['correctOptionIds'] for k in oldQ),'All 108 original correct-option sets remain unchanged.')
conflicted=[Q[k] for k in flags if any(c['role']=='conflict' for c in Q[k]['citations'])]
check('six-version-bound-conflict-resolutions',len(conflicted)==6 and all(x['conflictResolution']['questionVersion']==2 and x['conflictResolution']['sourceSha256']==x['citations'][0]['sourceSha256'] for x in conflicted),'Six question-version/source-hash-bound proposals remain pending independent review.')
batch['authorChecksV2']=checks
if __name__=='__main__':save(True)
