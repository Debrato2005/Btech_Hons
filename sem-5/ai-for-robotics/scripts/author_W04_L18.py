#!/usr/bin/env python3
"""Source-inspected L18 drafts. No self-verification or bank writes."""
import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from authoring_helpers import DraftBatch,formula,SHA
from validate import schema_errors,question_hash
AUTHOR='build_offline_study_interface:L18-author';BATCH='W04-L18'
b=DraftBatch(BATCH,4,'L18','Manipulator mechanism design',544,AUTHOR)
NOW='2026-10-19T17:38:07+00:00'
NOTES={
544:('Lecture18 title, Mechanism Design-I, author/institution and campus image.','Title and branding only.'),
545:('Learning outcomes name design, DOF, configurations, workspace/load/speed/repeatability/accuracy, wrists, indices and Python.','Roadmap only; detailed content follows.'),
546:('Contents list task requirements, configuration, quantitative workspace attributes and Python.','Contents only.'),
547:('Design creates physical robot structure for performance; construction affects kinematics/dynamics and availability of closed-form solutions. Four system parts include manipulator, tool, external sensing/effecting and controller. Drawing distinguishes entire arm from distal gripper.',None),
548:('Programmable does not mean universally optimal. Heavy welding versus high-speed circuit insertion illustrates task domains. Iterative choices include joint count/arrangement and actuation/sensing.',None),
549:('DOF means independent configuration variables; typical serial one-DOF joints versus closed-loop Grübler criterion. Three shown rotations theta1/base,theta2/middle,theta3/distal. Task matching, not universal six. Last sentence overbroad if fewer DOF: only excess is redundancy.',None),
550:('Arbitrary 3D pose needs three position and three orientation coordinates. Task-dependent redundancy; symmetric tool axial roll can be irrelevant, assuming task/tool symmetry actually removes that requirement.',None),
551:('Workspace is reachable end-effector volume/work envelope; task scale, singularity locations, fixtures and structural intrusion matter. Three-dimensional dot cloud with arm overlay is illustrative, not a universal shape; tiny cursor numerals are incidental plotting readout, not a specified calculation.',None),
552:('Load depends on links, transmission and actuator output; configuration and dynamic loads matter. Distinguish guaranteed whole-workspace rating from configuration-dependent allowable load; source wording otherwise appears contradictory.',None),
553:('Cycle time differs from peak speed. Acceleration/deceleration dominates many short pick/place moves; process paint/weld rate can cap useful speed.',None),
554:('Repeatability returns to taught point; accuracy reaches mathematical target. Match precision/cost to task; 0.001-inch accuracy compared with 8±2-inch spray is an example. Manufacturing tolerances and kinematic calibration influence accuracy.',None),
555:('Select joint configuration after task DOF. Wrist partition: first three position wrist point; last n−3 orient. Intersecting wrist axes and twists0/±90 with zero offsets/lengths simplify kinematics. Drawing circles positioning versus wrist portions.',None),
556:('Cartesian first three joints are mutually perpendicular prismatic axes. Side view labels d2 vertical,d3 horizontal; top view labels d1 orthogonal travel. Hatched sections rectangular. Positioning structure has no internal kinematic singularity under ideal independent-axis model; stiff gantry heavy-work applications.',None),
557:('Cartesian payload/rigidity, linear-actuator speed limits, direct Cartesian inverse map. Fixture/feeders must fit support envelope for shown design, complicating retrofit. Repeats positioning singularity claim, not entire-wrist guarantee.',None),
558:('Articulated/jointed/elbow/anthropomorphic: shoulder yaw theta1, elevation theta2, parallel elbow theta3. Side/top shaded curved sections illustrate nearly spherical, not exact spherical, envelope. Boundary and internal alignment singularities; need well-conditioned region.',None),
559:('Cantilevering lowers typical stiffness versus Cartesian but less structure/intrusion enables confined access. Cost and complex IK/control are design-dependent comparisons, not universal performance orders.',None),
560:('SCARA source expands Selectively Compliant Assembly Robot Arm; three parallel R motions plus normal P. Prose calls P fourth but diagram labels its displacement d3; use content/counts not silently unified index order. Figure shows horizontal rotation arcs and vertical displacement. Source cites roughly10× speed, Adept One30ft/s,1984,Adept Technology,first commercial direct-drive SCARA as historical claims only.',None),
561:('SCARA first two motors can be at base to reduce moving mass/high acceleration. Vertical stiffness and horizontal compliance suit insertion/electronics. Equal links often chosen. Phrase joints do not support weight is overbroad: actuator axial gravity torque differs from structural bearing load.',None),
562:('Spherical replaces articulated elbowR with P: two rotations theta1,theta2 and radial d3; spherical shell/wedge. Retraction may telescope or protrude behind; symmetric-tool applications.',None),
563:('Cylindrical provides independent vertical, azimuth and radial coordinates with two P and vertical R. Prose ordering P,R,P versus figure labels theta1,d2,d3; distinguish enumeration and labels. Side shaded rectangle, top annular-sector shape. Material handling application.',None),
564:('Orienting wrist after positioning. Diagram theta4,theta5,theta6 versus arm theta1–theta3. Two/three R wrist; orthogonal intersecting three-axis wrist reaches orientations absent joint limits, not absence of singularity. Nonorthogonal three-roll has continuous rotation feature.',None),
565:('Continuation of nonorthogonal discussion: excluded orientation cone for third axis. Separate picture explicitly captioned orthogonal wrist, remote actuators through three concentric shafts A4,A5,A6, outputtheta4,theta5,theta6. Any manipulator/three intersecting axes closed-form statement lacks usual manipulator scope; retain source attribution, not universal theorem.',None),
566:('Length sum L=sum_i(a_(i−1)+d_i), DH link lengths and offsets. Prismatic d_i is constant total travel, not instantaneous displacement. Treat supplied contributions as nonnegative physical lengths when interpreting structural index.',None),
567:('Q_L=L/cuberoot(W), lower structural length per work volume better by this criterion. Cartesian minimum 3 at equal travels; ideal articulated 0.62 is supplied benchmark, not general minimum for every arm. Scaling dimensionless.',None),
568:('Singularity is rank loss of task Jacobian; detJ0 only square. w=sqrt(det(JJᵀ)); square case absolute determinant. Near singularity ill-conditioned; movement/force uniformity design goal not equivalent to merely large determinant.',None),
569:('Asada inertia ellipsoid contrasts velocity manipulability with Cartesian inertia/acceleration directionality. Mx=J^(−T) M J^(−1) requires square nonsingular J. XᵀMxX=1 is shown normalized quadratic-form surface, not literally physical displacement times kg equals dimensionless1. Figure shows position-dependent oriented ellipses and some circles. Isotropic means equal principal values under consistent normalization; no unrestricted actuator-bound claim.',None),
570:('Planar2R example l1=5,l2=4, both angles−pi..pi. FK x=l1cosθ1+l2cos(θ1+θ2),y=l1sinθ1+l2sin(θ1+θ2). No physical length unit printed.',None),
571:('Repeats model/FK and substituted coefficients. Diagram labels l1 base→elbow,l2 elbow→tool,theta1base,theta2relative. Theta2 not global orientation.',None),
572:('Continuous ideal workspace annulus 1≤R≤9,R=sqrt(x²+y²). Wording plotted points represent all positions must be qualified for subsequent finite sampling. Boundaries straight/folded; no collision/joint exclusions specified.',None),
573:('Literal code uses NumPy/Matplotlib, two inclusive200-point linspaces, nested loops and paired x/y append lists;40,000 pairs. Figure8×8,scatter s=1,labelsX/Y,axis equal,gridTrue,show. Title string wraps inside single quotes; literal newline copy invalidPython, intended one-line title clear from output. Even200 grid omitszero; periodic endpoints duplicate configurations.',None),
574:('Displayed plot is annular with empty radius~1,outer~9,equal X/Y scale,finite dots/rings and apparent gaps. Red arrows annotate inner/outer radii. Do not read finite scatter gaps as continuous geometric holes beyond inner disk.',None),
575:('Summary repeats task-based design effects, configuration choice, structural/manipulability indices and FKworkspaceplotting. No incremental formula; mapped to earlier concepts.',None),
576:('Craig2005third-edition reference.','Bibliographic reference only; not additional assigned book content.'),
577:('Thank-you closing with branding.','Closing only.')}
ISSUES=[
(549,'Task mismatch is not always redundancy: fewer independent freedoms can be insufficient; only excess task freedoms are redundant.','Use explicit excess-DOF definition on p550 and task-scoped premises.'),
(550,'Six freedoms are a general pose dimension count, not a reachability guarantee at every point. Axial tool-roll irrelevance is task/symmetry dependent.','State reachable-region and symmetry assumptions; do not infer universal feasibility.'),
(552,'Whole-workspace maximum rating wording and configuration-dependent capacity appear together.','Ask separately about a guaranteed rating and a per-configuration allowable load; account for dynamics.'),
(560,'SCARA prose calls the P joint fourth; diagram labels vertical displacement d3. Historical speed and priority claims have no benchmark conditions.','Preserve figure labels and test joint types/counts without inventing sequence; attribute performance/history to this slide.'),
(561,'The statement that joints do not support the weight is not literally true of structural bearing/support loads.','Distinguish gravity torque about vertical actuation axes from physical weight support; base-mounted motors reduce moving mass.'),
(565,'Any manipulator with three consecutive intersecting axes has closed-form solution is broader than the usual nonredundant serial wrist-partition setting.','Source-attributed statement only; no universal theorem or guarantee under arbitrary constraints/limits.'),
(566,'DH parameters may be signed, but literal length-sum formula has no absolute values or sign convention.','Use nonnegative physical length/travel inputs for numerical index questions; no arbitrary signed-DH cancellation.'),
(568,'detJ condition requires square J; full 6D Jacobian cannot describe a 2-DOF planar task with square determinant.','Specify selected task and dimension; use task rank and det(JJᵀ) for full-row-rank rectangular case.'),
(569,'Inverse-J mass formula excludes singular and rectangular cases. Normalization/effort limits of ellipse are not stated.','Use square nonsingular J and normalized same-unit task coordinates; compare quadratic-form shapes without promising physical acceleration bounds under arbitrary actuators.'),
(572,'Finite scatter is described as representing all possible reachable positions.','Separate the continuous ideal FK image from 40,000 evaluated samples; finite holes are not proof of unreachable continuous points.'),
(573,'Title is visually wrapped within a single-quoted string across two lines. Literal copy produces unterminated-string SyntaxError.','When discussing intended execution, explicitly rejoin the title on one line; preserve literal-copy issue separately.')]
def add(p,key,title,stem,opts,why,**kw):
 correct=kw.pop('correct',(0,));correct=list(correct)
 # Rotate content positions and answer IDs deterministically, avoiding an all-o1 key pattern.
 k=len(b.questions)%4;opts=opts[k:]+opts[:k];correct=[(i-k)%4 for i in correct]
 q=b.add(p,key,title,stem,[o[0] for o in opts],correct,why,[o[1] for o in opts],**kw)
 for c in q['citations']:c['locator']=f"Lecture 18, physical PDF page {c['physicalPage']}, printed slide {c['physicalPage']-543}: {title}"
 if q.get('conflictResolution'):q['conflictResolution'].update(sourceId='lectures',sourceSha256=SHA,physicalPages=sorted(set([p] if isinstance(p,int) else p)))
 return q

def save(frozen=False):
 b.save();path=R/f'data/question-batches/{BATCH}.json';batch=json.loads(path.read_text());batch['sourceIssues']=[dict(physicalPage=p,description=t,qualification=q,status='preserved_with_explicit_scope_not_globally_resolved') for p,t,q in ISSUES];batch['coverageNote']='All 34 actual pages visually inspected; source-bound drafts only, independent review and coverage challenge required.';path.write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
 maps={s['physicalPage']:s for s in map(json.loads,(R/'sources/page_maps/lectures.jsonl').read_text().splitlines())};slides=[]
 for p,(note,exclude) in NOTES.items():
  s=copy.deepcopy(maps[p]);s['disposition']='excluded' if exclude else 'examinable';s['exclusionReason']=exclude;s['conceptIds']=[c['id'] for c in b.concepts.values() if s['id'] in c['slideIds']]
  s['visualInspection']={'status':'complete','inspectorId':AUTHOR,'inspectedAt':NOW,'method':'rendered_page','notes':note+' Viewed actual readable 1800×1013 source pixels alongside extracted text.','previewSha256':hashlib.sha256((R/s['previewPath']).read_bytes()).hexdigest(),'dimensions':[1800,1013]};slides.append(s)
 for typ,records in [('question',b.questions),('concept',list(b.concepts.values())),('slide',slides)]:
  schema=json.loads((R/f'data/schema.{typ}.json').read_text());errors=[e for x in records for e in schema_errors(x,schema)];assert not errors,(typ,errors)
 (R/f'data/inspection-batches/{BATCH}.json').write_text(json.dumps({'batchId':BATCH,'slides':slides},ensure_ascii=False,indent=2)+'\n')
 (R/f'audits/{BATCH}-author-progress.json').write_text(json.dumps({'frozen':frozen,'questions':len(b.questions),'concepts':len(b.concepts),'inspectedPages':list(NOTES),'authorId':AUTHOR,'blindPacketSha256':hashlib.sha256((R/f'audits/blind-{BATCH}.json').read_bytes()).hexdigest(),'next':'Independent review required' if frozen else 'Continue remaining meaningful question angles; do not treat partial question coverage as complete.'},indent=2)+'\n')
 print('Saved',len(b.questions),'drafts;',len(b.concepts),'concepts;',len(slides),'inspected pages; frozen=',frozen)

# Questions are appended below in stable source order.
save()

add(547,'design','Physical mechanism and system parts',
 'Why can changing the physical arrangement of a robot arm change the difficulty of its kinematics and dynamics?',[
 ('The arrangement changes the equations and may determine whether convenient closed-form solutions exist.','Joint geometry enters the kinematic and dynamic models, so physical design and mathematical complexity are linked.'),
 ('The arrangement changes only the controller enclosure, leaving the arm equations unchanged.','This confuses controller packaging with link and joint geometry.'),
 ('Any arrangement with the same number of joints has identical kinematic equations.','Joint count alone does not specify axis directions, link lengths or offsets.'),
 ('Programmability makes the mechanical arrangement irrelevant to mathematical modeling.','Software does not remove the geometric constraints imposed by the mechanism.')],
 'The slide explicitly links physical construction to the complexity of the kinematic and dynamic equations and the availability of closed-form solutions.',difficulty='easy')
add(547,'design','Physical mechanism and system parts',
 'In the labeled robot drawing, which pairing correctly distinguishes the manipulator from the end-effector?',[
 ('Manipulator: articulated arm structure; end-effector: the distal gripper/tool.','The arm carries and positions the tool; the distal gripper is the task interface.'),
 ('Manipulator: distal gripper only; end-effector: the entire supporting arm.','This reverses the two labels in the drawing.'),
 ('Manipulator: external camera; end-effector: controller cabinet.','External sensing and control are different system parts.'),
 ('Manipulator: controller cabinet; end-effector: every joint motor.','The controller and internal actuators are not the labeled arm and tool.')],
 'The figure labels the multi-link arm as the manipulator and its terminal gripper as the end-effector. The text separately lists external sensors/effectors and the controller.',typ='diagram',difficulty='easy')
add(548,'task-design','Task-dependent iterative design',
 'A factory compares a robot carrying heavy automotive welding equipment with one inserting small circuit components rapidly. What is the slide’s main design lesson?',[
 ('Different task domains favor different compromises in payload, speed and mechanism design.','The examples contrast heavy-load and rapid small-component tasks.'),
 ('The higher-payload robot must also have the shortest component-insertion cycle time.','Payload capability does not imply superior short-move acceleration or cycle time.'),
 ('Any programmable robot is mechanically optimal for both tasks after a software change.','Programmability does not eliminate task-dependent mechanical compromises.'),
 ('Both tasks should be assigned identical joints and actuators because both are industrial automation.','The shared industry label does not specify matching mechanical requirements.')],
 'Economical and practical manipulators are designed for classes of tasks. Joint arrangement, actuation and sensing are chosen iteratively with the required performance.',typ='scenario',difficulty='easy')
add([549,550],'dof','Independent freedoms and task redundancy',
 'For a typical open serial chain whose three independent joints each have one degree of freedom, how many independent joint coordinates describe its configuration?',[
 ('Three.','The three independent one-DOF joints supply three independent configuration variables.'),
 ('Six, because every robot operates in three-dimensional space.','Six describes unrestricted rigid-body pose, not every mechanism’s configuration dimension.'),
 ('Nine, because each joint contributes three spatial coordinates.','A one-DOF joint contributes one independent parameter, not three independent translations.'),
 ('Two, because one coordinate must always be removed for the base.','A fixed base is already implicit; it does not remove one of the stated independent joint coordinates.')],
 'DOF counts independent configuration variables. Under the stated open-chain, independent one-DOF-joint assumptions, the count is three.',typ='definition',difficulty='easy',assumptions=['Fixed base, open serial chain, three independent one-DOF joints, and no additional constraints.'])
add(549,'dof','Independent freedoms and task redundancy',
 'Why should the number of joints not automatically be used as the mobility of a closed-loop mechanism?',[
 ('Loop-closure constraints can make joint coordinates dependent; the slide points to a mobility criterion such as Grübler’s.','Closed loops impose geometric constraints not present in an unconstrained serial-joint count.'),
 ('Closed loops always have zero mobility regardless of geometry.','A closed linkage can move while satisfying its constraints.'),
 ('Every closed-loop joint necessarily contributes two independent variables.','Joint freedoms and closure constraints must both be considered; there is no such general doubling.'),
 ('Mobility is determined only by actuator power once a loop is present.','Actuator power concerns performance, not the number of independent configuration variables.')],
 'The slide distinguishes typical serial one-DOF-joint counting from closed-loop mobility analysis. It names Grübler’s criterion but does not provide a numerical formula on this page.',difficulty='easy')
add(550,'dof','Independent freedoms and task redundancy',
 'Which statement correctly interprets the general six-DOF requirement for arbitrary three-dimensional end-effector pose?',[
 ('Three independent position coordinates and three orientation coordinates are needed locally; six joints alone do not guarantee every desired pose is reachable.','The pose dimension count is distinct from workspace, joint-limit and singularity feasibility.'),
 ('Six independent position coordinates are needed, while orientation is determined automatically.','A 3D position has three coordinates; orientation contributes the other three local freedoms.'),
 ('Any six-joint arm can attain every position and orientation in unlimited space.','Finite link lengths, limits and singularities prevent that conclusion.'),
 ('Three position coordinates are sufficient for arbitrary pose even when tool orientation is constrained.','A full pose task also imposes orientation requirements.')],
 'General spatial pose has three positional and three orientational freedoms. Mechanism geometry, limits and singularities still constrain attainable poses.',difficulty='medium',assumptions=['General rigid-body pose, interpreted locally away from parameterization singularities.'])
add(550,'task-redundancy','Symmetry and task-relative redundancy',
 'A reachable welding task fixes tool position and tool-axis direction, but rotation about that axis has no effect because the tool and task are axially symmetric. What does the sixth independent arm freedom represent relative to this five-coordinate task?',[
 ('An extra task-relative freedom that can be redundant.','The task has removed the axial-roll requirement, leaving an extra independent motion if the arm has six freedoms.'),
 ('An automatically missing position coordinate.','Ignoring axial roll removes an orientation requirement, not a position coordinate.'),
 ('A proof that the arm cannot perform the task.','An extra freedom need not prevent task execution.'),
 ('A requirement to impose an arbitrary axial-roll target before every weld.','The premise explicitly makes axial roll irrelevant to task success.')],
 'Redundancy is relative to the task. With position and axis direction fixed but roll irrelevant, the task needs five independent pose coordinates rather than six.',typ='scenario',difficulty='medium',assumptions=['The chosen pose is reachable, relevant Jacobians have the needed rank, and axial roll is genuinely irrelevant to this tool and task.'])
add([549,550],'task-redundancy','Symmetry and task-relative redundancy',
 'A mechanism has fewer independent freedoms than a general task requires. Is calling this mismatch “redundancy” justified?',[
 ('No. Redundancy means excess task-relative freedom; too few freedoms can make the general task infeasible.','Insufficient mobility and redundant mobility are opposite situations.'),
 ('Yes. Any mismatch between mechanism DOF and task DOF is redundancy.','This repeats an overbroad reading of the task-matching sentence.'),
 ('Yes, provided the mechanism is serial rather than closed-loop.','Serial topology does not turn a shortage of freedoms into an excess.'),
 ('No, because redundancy refers only to duplicated controllers and never to robot motion.','Robot kinematic redundancy is a standard task-relative concept used on the next slide.')],
 'The explicit excess-DOF definition on page 550 controls the interpretation. A shortage of freedoms may fail a general task rather than provide redundant motion.',difficulty='medium',conflict='Page 549 says the DOF should match the task, otherwise the robot becomes redundant; this cannot correctly include too few freedoms.')
add(551,'workspace','Workspace and installation constraints',
 'Two arms have similarly sized reachable end-effector volumes. Why is this alone insufficient to choose an arm for a crowded assembly cell?',[
 ('Workspace shape, singularity locations, and interference with fixtures or the robot structure also matter.','A volume total does not describe access or usable configurations.'),
 ('Equal workspace volume guarantees equal collision-free access to every fixture.','Different shapes and structural intrusion can give different access despite equal volume.'),
 ('The arm with greater maximum joint speed is automatically collision-free.','Speed does not remove geometric interference.'),
 ('Only end-effector positions at the outer boundary need to be checked.','Internal obstructions and singularities may affect positions inside the boundary.')],
 'Workspace design must consider scale and shape, singularities and how the robot’s own structure intrudes into the cell.',typ='scenario',difficulty='medium')
add(552,'load','Load rating and configuration dependence',
 'An arm can safely carry 12 kg near its base but only 7 kg at full extension under the same required performance. If a single rating must be guaranteed over this stated workspace, what upper bound follows from these two configurations alone?',[
 ('At most 7 kg; another configuration could lower the guaranteed rating further.','A whole-workspace guarantee cannot exceed the weakest evaluated configuration.'),
 ('12 kg, because a maximum rating uses the largest observed capacity.','That is a best-configuration capacity, not a whole-workspace guarantee.'),
 ('9.5 kg, the average of the two capacities.','An average does not satisfy the lower-capacity configuration.'),
 ('19 kg, because the two configurations contribute capacities additively.','The robot occupies configurations separately; capacities do not add.')],
 'A guarantee over all configurations must respect each configuration’s allowable load. From the given pair it cannot exceed 7 kg, and untested configurations may impose a tighter bound.',typ='scenario',difficulty='medium',assumptions=['The two capacities use identical safety and performance requirements; only these two configurations are specified.'])
add(552,'load','Load rating and configuration dependence',
 'Which factors should be included when assessing load capacity during rapid motion? Select all that apply.',[
 ('Link strength and stiffness, transmission capacity, and available actuator torque or force.','These physical components limit supported and driven loads.'),
 ('Configuration-dependent leverage and inertial or velocity-dependent loads.','Dynamic loading and configuration affect the required joint effort.'),
 ('Only the payload’s static weight, because motion does not change joint effort.','Accelerations and velocity-dependent effects can change loads substantially.'),
 ('Only the end-effector’s peak speed, independent of geometry and acceleration.','Peak speed alone does not determine actuator or structural loading.')],
 'The slide connects load to links, transmissions and actuators, and warns that dynamic conditions and configuration must be considered.',correct=(0,1),difficulty='medium')
add(553,'speed','Speed, cycle time and process limits',
 'For a short pick-and-place move, two robots have the same maximum velocity. Why can their move times still differ substantially?',[
 ('Different acceleration and deceleration capabilities can dominate a short move before either robot reaches its speed limit.','Short moves often spend most of their time speeding up and slowing down.'),
 ('Equal maximum velocity forces equal travel time for every path length.','This ignores the acceleration-limited portions of motion.'),
 ('Only the final tool orientation matters once maximum velocities match.','Orientation requirements do not remove translational acceleration effects.'),
 ('The heavier robot must always be faster because its links store more momentum.','Mass alone does not establish better acceleration or shorter cycle time.')],
 'Maximum speed is not cycle time. The lecture emphasizes acceleration and deceleration for short pick-and-place operations.',typ='scenario',difficulty='medium')
add(553,'speed','Speed, cycle time and process limits',
 'A welding process requires a fixed travel rate to obtain the specified weld. What is the safest design inference from a robot’s much higher maximum speed?',[
 ('The extra peak speed may not shorten the welding portion of the cycle because the process sets its useful rate.','The process constraint can dominate the robot’s speed capability.'),
 ('The weld should always be executed at the robot’s maximum speed.','This disregards the specified process requirement.'),
 ('The higher-speed robot necessarily produces a stronger weld.','Weld quality is not implied by robot peak speed.'),
 ('Acceleration and positioning time become zero when the welding rate is fixed.','Non-welding motion and transitions still consume time.')],
 'Painting and welding can impose process-limited motion rates. More robot speed is not automatically more productive during the constrained operation.',typ='scenario',difficulty='easy')
add(554,'precision','Accuracy, repeatability and task economics',
 'A robot repeatedly returns close to a taught point, but that cluster lies several millimeters from the position calculated from its nominal model. Which description fits?',[
 ('Good repeatability but poor absolute accuracy for that modeled target.','Repeatability describes return consistency; accuracy compares with the intended mathematical target.'),
 ('Good accuracy but poor repeatability.','This reverses the two performance measures.'),
 ('Both are necessarily good because the cluster is tight.','A tight cluster can be consistently displaced from the target.'),
 ('Both are necessarily poor because the cluster is displaced.','The displacement does not imply a wide return scatter.')],
 'Repeatability is the ability to return to a taught location; accuracy is the ability to reach a mathematically specified location.',typ='scenario',difficulty='medium')
add(554,'precision','Accuracy, repeatability and task economics',
 'What is the design lesson of comparing 0.001-inch positioning accuracy with a paint spray approximately 8±2 inches in diameter?',[
 ('Match accuracy requirements and cost to the actual process rather than demand unnecessary precision.','The example illustrates disproportionate precision relative to a coarse process footprint.'),
 ('Every painting robot can safely ignore position accuracy entirely.','The example does not eliminate task-specific path or edge requirements.'),
 ('A wide spray proves that repeatability and accuracy are identical.','Process footprint does not change their definitions.'),
 ('The spray diameter directly specifies the robot’s maximum load.','Spray width is not a payload rating.')],
 'Excessive precision can add cost without useful benefit for a particular task. The example is an economic task-matching argument, not a universal paint-position tolerance.',difficulty='easy')
add(554,'precision','Accuracy, repeatability and task economics',
 'Why can estimating actual link parameters improve absolute positioning accuracy even when the mechanical structure is unchanged?',[
 ('The model used to command a mathematical target can better match the manufactured geometry.','Kinematic calibration addresses discrepancies between nominal and actual parameters.'),
 ('Calibration necessarily removes all backlash and compliance from the hardware.','Parameter estimation does not physically remove mechanical errors.'),
 ('Calibration adds independent joints and therefore increases DOF.','Updating model parameters does not add mechanism freedoms.'),
 ('Calibration guarantees identical accuracy at all payloads without a deflection model.','Load-dependent deformation may require additional modeling and remains a separate limitation.')],
 'Manufacturing tolerances and how accurately the kinematic parameters are known affect absolute accuracy; calibration can improve the model without changing the physical design.',difficulty='medium')
add(555,'partition','Positioning arm, wrist and kinematic simplicity',
 'In the lecture’s common arm–wrist partition of an n-joint manipulator, which description is intended?',[
 ('The first three joints position a wrist point and the remaining n−3 joints orient the end-effector.','This is the stated conceptual partition for the discussed designs.'),
 ('The first three joints determine orientation only and all remaining joints translate the base.','This reverses the stated roles and introduces base translation.'),
 ('Every joint must independently control one Cartesian coordinate with no coupling.','The partition does not imply uncoupled Cartesian control by individual joints.'),
 ('The wrist always contributes exactly three translational freedoms.','An orienting wrist is based on rotational motions, not three translations.')],
 'The slide groups the positioning structure separately from the orienting wrist. This is a common design decomposition, not a universal property of every possible mechanism.',typ='diagram',difficulty='easy',assumptions=['Use the common arm–wrist architecture discussed on this slide, not an arbitrary redundant or coupled mechanism.'])
add(555,'partition','Positioning arm, wrist and kinematic simplicity',
 'Which geometric choices are described as simplifying the kinematics of common manipulator designs? Select all that apply.',[
 ('Intersecting wrist axes and many zero link lengths or offsets.','These special geometries can simplify the equations.'),
 ('Link twists chosen from 0° and ±90° where appropriate.','The associated trigonometric terms simplify for these common twist values.'),
 ('Arbitrary skew wrist axes must always produce the same simple inverse equations.','Arbitrary geometry does not preserve the simplifying structure.'),
 ('Making every link longer guarantees a closed-form inverse solution.','Length scale alone does not establish algebraic solvability.')],
 'The lecture highlights special axis intersections, zero dimensions and 0/±90-degree twists as useful kinematic simplifications.',correct=(0,1),difficulty='medium')
save()

add([556,557],'cartesian','Cartesian positioning structure',
 'Which combination describes the Cartesian positioning structure in the lecture?',[
 ('Three mutually orthogonal prismatic motions producing a box-shaped workspace.','Independent linear travels along three perpendicular axes generate a Cartesian box.'),
 ('Three parallel revolute motions producing only a planar annulus.','This is not the Cartesian PPP positioning structure.'),
 ('Two rotations and a radial translation producing a spherical shell sector.','This describes the spherical configuration.'),
 ('A vertical rotation with vertical and radial translations producing a cylindrical sector.','This describes the cylindrical configuration.')],
 'The Cartesian positioning joints are prismatic and mutually orthogonal, directly corresponding to Cartesian coordinate directions.',typ='match',difficulty='easy')
add(556,'cartesian-figure','Cartesian diagram labels and geometry',
 'In the Cartesian manipulator’s side and top views, which label denotes vertical displacement in the side view?',[
 ('d₂.','The vertical double-headed arrow beside the column is labeled d₂.'),
 ('d₁.','d₁ labels the other travel visible in the top view, not the side-view vertical arrow.'),
 ('d₃.','d₃ labels the side-view horizontal slide.'),
 ('θ₂.','The illustrated Cartesian positioning motions are displacement variables, not a revolute θ₂ motion.')],
 'The side view labels vertical column travel d₂ and horizontal extension d₃; the top view shows the orthogonal d₁ travel.',typ='diagram',difficulty='easy')
add([556,557],'cartesian','Cartesian positioning structure',
 'For an ideal Cartesian positioner with independent coordinates x=d₁, y=d₂, z=d₃ after fixed axis relabeling and offsets, what is the positioning Jacobian and its internal singularity implication?',[
 ('J=I₃, so it has full rank throughout the interior of its allowed travel.','Each coordinate responds independently to its corresponding displacement.'),
 ('J=0, because all joints are prismatic rather than rotational.','Prismatic motion changes position directly; it does not give a zero positioning Jacobian.'),
 ('J has rank one because the tool is a single point.','A single point can have three independent velocity components.'),
 ('det(J) depends on sin(d₂), so every zero displacement is singular.','This imports a revolute-angle dependency into the stated linear Cartesian map.')],
 'Differentiating the stated map gives the identity matrix. This concerns the ideal positioning substructure; it does not promise that an attached wrist, travel boundary or collision constraint is unrestricted.',typ='derivation',difficulty='medium',steps=['Differentiate x=d₁, y=d₂ and z=d₃ with respect to the three displacement coordinates.','The resulting 3×3 derivative is I₃, whose determinant is 1 and rank is 3.'],formulas=[formula('J = ∂(x,y,z)/∂(d₁,d₂,d₃) = I₃',{'J':'Cartesian positioning Jacobian','x,y,z':'Cartesian position coordinates','d₁,d₂,d₃':'independent prismatic displacements after fixed axis relabeling','I₃':'3×3 identity matrix'},{'x,y,z,d₁,d₂,d₃':'length','J,I₃':'dimensionless'},['Ideal independent perpendicular slides; fixed coordinate offsets do not affect derivatives.'])])
add(557,'cartesian-layout','Cartesian performance and cell layout',
 'Which trade-off is described for the shown Cartesian structure?',[
 ('High rigidity and payload capability can come with a supporting envelope that constrains fixtures and retrofit layout.','The frame benefits stiffness but can intrude into the usable installation space.'),
 ('Its open elbow geometry always gives better access around obstacles than an articulated arm.','The described support structure is not an open articulated elbow.'),
 ('Simple inverse positioning guarantees unlimited linear actuator speed.','Kinematic simplicity does not remove actuator speed limits.'),
 ('Its supporting structure is irrelevant because workspace volume alone determines installation.','Fixtures and feeders must be compatible with the physical support envelope.')],
 'The slide couples high rigidity and load capability with linear-actuator limitations and a support geometry that can complicate machine integration.',typ='scenario',difficulty='medium')
add(558,'articulated','Articulated arm geometry and singularities',
 'In the illustrated articulated arm, how does the elbow revolute axis relate to the shoulder elevation axis?',[
 ('They are parallel in the discussed arrangement.','This relationship permits elbow motion in the shoulder-elevation plane.'),
 ('The elbow axis is always parallel to the vertical shoulder-yaw axis instead.','The slide specifies parallelism to shoulder elevation, not the vertical yaw axis.'),
 ('The elbow is prismatic and therefore has no revolute axis.','Replacing the elbow with a prismatic joint gives the later spherical configuration.'),
 ('All three positioning axes must be mutually orthogonal in every configuration.','The depicted articulated arm includes parallel shoulder-elevation and elbow axes.')],
 'The articulated arrangement uses shoulder yaw, shoulder elevation and an elbow whose axis is parallel to the shoulder-elevation axis.',typ='diagram',difficulty='easy')
add(558,'articulated','Articulated arm geometry and singularities',
 'Which reading of the articulated-arm workspace drawing and text is justified?',[
 ('The reachable region is complex and nearly spherical, with possible boundary and internal axis-alignment singularities.','The figure shows curved restricted sectors, and the text explicitly mentions both kinds of singular location.'),
 ('The workspace is always an exact solid sphere with no internal singular configurations.','“Nearly spherical” and the internal-alignment warning contradict this.'),
 ('A point strictly inside the outer workspace boundary must be well-conditioned.','Internal singularities or poor conditioning can exist away from the outer boundary.'),
 ('Articulated arms can reach around obstacles only by making all axes parallel.','The reach-around advantage does not require that special singular-looking alignment.')],
 'A useful design seeks a large well-conditioned region, not merely a large outer envelope. Joint limits and internal alignments affect the actual reachable and usable set.',typ='diagram',difficulty='medium')
add([558,559],'articulated-tradeoff','Articulated access, stiffness and control trade-offs',
 'Relative to the Cartesian designs discussed, what trade-off is associated with a cantilevered articulated arm?',[
 ('It can use less intrusive structure and reach confined locations, while tending to be less stiff and potentially harder to model or control.','The lecture contrasts access and compactness with stiffness and kinematic complexity.'),
 ('Cantilevering necessarily makes every articulated arm stiffer than every Cartesian arm.','The source gives the opposite typical comparison, not a universal superiority theorem.'),
 ('Less surrounding structure means inverse kinematics no longer depends on geometry.','Geometry still determines the inverse mapping.'),
 ('Confined access is impossible because all articulated workspaces are rectangular boxes.','This misidentifies the configuration and its workspace.')],
 'The stated comparisons are design-dependent tendencies: cantilevering reduces typical stiffness, but less surrounding structure can improve access. Careful geometry can simplify inverse kinematics.',typ='scenario',difficulty='medium')
add(560,'scara','SCARA joint freedoms and task',
 'Ignoring the slide’s inconsistent numbering of its vertical joint, which set of motions defines the SCARA described there?',[
 ('Three parallel-axis revolute motions for planar positioning/orientation and one prismatic motion normal to that plane.','This preserves the joint types and roles without inventing a common numbering convention.'),
 ('Three mutually orthogonal prismatic motions and no end-effector rotation.','This is a Cartesian positioner, not the SCARA described.'),
 ('Two intersecting shoulder rotations followed by radial extension only.','This is the spherical positioning structure.'),
 ('Three revolute axes that independently provide arbitrary 3D orientation plus three vertical slides.','The discussed SCARA has four motions, not six, and its rotations are parallel-axis.')],
 'The text specifies three parallel R motions and one normal P motion. It calls the P motion fourth, whereas the figure labels its vertical displacement d₃; the types and roles are clear despite that numbering mismatch.',difficulty='easy',conflict='The prose calls the prismatic motion fourth, while the side-view figure marks its displacement d₃; the question deliberately does not infer a unique joint sequence.')
add(560,'scara-figure','SCARA figure and motion coordinates',
 'What does the double-headed arrow labeled d₃ indicate in the SCARA side-view figure, regardless of the prose’s separate joint numbering?',[
 ('Linear motion normal to the horizontal arm plane.','The arrow is vertical and uses a displacement label.'),
 ('Rotation of the base through θ₁.','The base rotation is shown by an angular arc in the top view.'),
 ('Rotation of the elbow through θ₂.','The elbow rotation is another top-view arc, not the vertical displacement.'),
 ('An increase in the fixed length of the first horizontal link.','The arrow describes vertical travel rather than stretching a horizontal link.')],
 'The figure’s d₃ arrow shows vertical translation at the distal structure. This figure-specific observation does not resolve the text’s fourth-joint numbering.',typ='diagram',difficulty='easy',conflict='The figure labels the vertical displacement d₃, while the prose calls the normal prismatic joint fourth.')
add(560,'scara','SCARA joint freedoms and task',
 'For the ideal SCARA motions described, which end-effector task coordinates are naturally controlled?',[
 ('Planar x and y position, height z, and yaw about the plane normal.','The planar R motions supply planar placement and yaw, while the P motion supplies height.'),
 ('All three positions and all three independent orientations using only those four freedoms.','Four independent motions cannot generally impose a six-coordinate spatial pose.'),
 ('Only x and y, because parallel revolute axes cannot change orientation.','Their net rotation changes planar yaw.'),
 ('Only roll, pitch and yaw, with position fixed.','The arm links and vertical slide also change position.')],
 'The architecture is adapted to planar assembly with height adjustment and rotation about the normal, not arbitrary independent roll and pitch.',difficulty='medium',assumptions=['Ideal four-DOF SCARA, away from planar positioning singularities.'])
add(560,'scara-history','Source-attributed SCARA performance example',
 'Which statement is presented as the lecture’s historical example, rather than as an independently established current benchmark for every SCARA?',[
 ('Adept One is described as a direct-drive SCARA introduced by Adept Technology in 1984, with a cited speed of 30 ft/s.','This accurately attributes the specific name, date, maker and speed to the slide.'),
 ('Adept One is described as a three-prismatic-axis gantry whose 30 ft/s speed is a payload rating.','The slide calls it a direct-drive SCARA; speed is not payload.'),
 ('The slide proves that every SCARA has exactly ten times the speed of every articulated robot under all loads.','The approximate comparison lacks the conditions needed for such a universal claim.'),
 ('The historical example establishes 30 ft/s as a guaranteed minimum speed for all SCARA tasks today.','A cited example does not create a universal or current guarantee.')],
 'The slide gives this historical example and an approximate speed comparison. It does not supply benchmark conditions or evidence making the comparison universal; the answer is explicitly source-attributed.',typ='definition',difficulty='easy',assumptions=['Answer only what the lecture attributes to this example; do not treat it as externally verified historical priority or a current purchasing specification.'])
add(561,'scara-design','SCARA mass, compliance and equal links',
 'Why can placing the first two SCARA actuators in the base help achieve high acceleration?',[
 ('It reduces actuator mass carried by the moving links.','Less moving mass and inertia can reduce the effort required for acceleration.'),
 ('It removes the need for mechanical transmissions between the base and joints.','Remote actuation can still require transmissions.'),
 ('It makes payload inertia identically zero.','Payload inertia remains even if some motor mass is stationary.'),
 ('It converts all revolute joints into frictionless prismatic joints.','Motor location does not change those joint types or eliminate friction.')],
 'The lecture connects base-housed actuators with reduced moving mass and high acceleration.',difficulty='easy')
add(561,'scara-design','SCARA mass, compliance and equal links',
 'Which directional stiffness pattern explains the SCARA’s suitability for many insertion and electronic assembly tasks?',[
 ('Relatively stiff vertically and compliant in the horizontal plane.','This is the selective compliance described on the slide.'),
 ('Relatively compliant vertically and rigid in every horizontal direction.','This reverses the lecture’s directional comparison.'),
 ('Identical zero stiffness in all directions.','Selective compliance is not absence of structural support.'),
 ('High rotational speed eliminates the need to consider directional stiffness.','Speed and compliance are different design attributes.')],
 'SCARA means Selectively Compliant Assembly Robot Arm in this lecture. Its stated vertical stiffness and horizontal compliance are useful in assembly/insertion.',typ='match',difficulty='easy')
add([560,561],'scara-load-scope','SCARA gravity torque versus structural support',
 'For a SCARA revolute joint whose axis is vertical, assume gravity is vertical. Which qualification best handles the slide’s phrase that the joints “do not support the weight”?',[
 ('Gravity need not create torque about that vertical rotation axis, but bearings and links still transmit weight and other loads.','Zero axial gravity torque is not the same as zero structural support force or bending load.'),
 ('Every bearing and link force is zero whenever a rotation axis is vertical.','Weight must still be supported by the structure.'),
 ('No actuator ever needs torque because payload inertia also disappears.','Acceleration, friction and other effects can still demand torque.'),
 ('A vertical revolute axis turns gravity into a horizontal force.','The axis direction does not change the gravitational force direction.')],
 'The component of r×F along a vertical axis is zero for a vertical gravity force. Structural members nevertheless carry the forces and bending loads. This distinction qualifies the overbroad wording rather than accepting it literally.',typ='scenario',difficulty='medium',assumptions=['Ideal vertical revolute axis and vertical gravity; no inference of zero friction, inertial torque or bearing load.'],conflict='Page 561 broadly states that the first three joints do not support link or load weight. The question distinguishes actuation-axis gravity torque from physical structural support.')
add([561,572],'scara-equal','Equal links and the ideal planar inner hole',
 'For an ideal two-link planar positioning section with unrestricted joint angles and no collision constraints, what happens to the minimum reachable radius when positive link lengths are made equal?',[
 ('It becomes zero because |L₁−L₂|=0.','The folded links can cancel their position vectors.'),
 ('It becomes L₁+L₂.','The sum is the maximum straight-arm radius, not the minimum.'),
 ('It becomes twice either link length.','That is also the maximum radius for equal links.'),
 ('It remains nonzero solely because the links rotate about parallel axes.','Parallel planar revolute axes do not by themselves force a nonzero central hole.')],
 'The planar reach interval is |L₁−L₂| to L₁+L₂. Equal lengths remove the ideal central position hole, but do not eliminate singular configurations or guarantee all orientations.',typ='derivation',difficulty='medium',assumptions=['Ideal planar two-link position model, full angular range, no self-collision or joint constraints.'],steps=['The minimum distance occurs when the two link vectors oppose each other.','Their residual length is |L₁−L₂|, which is zero for L₁=L₂.'],formulas=[formula('r_min=|L₁−L₂|',{'r_min':'minimum radial distance of the planar endpoint','L₁,L₂':'positive planar link lengths'},{'r_min,L₁,L₂':'length'},['Full joint-angle range and ideal collision-free links.'])])
add(562,'spherical','Spherical configuration and installation',
 'How is the spherical positioning configuration described relative to the articulated arm?',[
 ('Replace the elbow revolute motion with radial prismatic extension, retaining two positioning rotations.','Two angles and a radial displacement naturally describe spherical positioning.'),
 ('Replace both shoulder rotations with independent horizontal prismatic slides.','This does not match the two-rotation spherical structure.'),
 ('Keep all three articulated positioning revolute joints and add no translation.','This retains the articulated rather than the described spherical configuration.'),
 ('Remove the radial degree of freedom so that only one fixed-radius spherical surface is reachable.','The prismatic extension is precisely what varies radial distance.')],
 'The spherical configuration combines two rotations with one radial linear translation, producing a portion of a spherical shell or wedge.',typ='match',difficulty='easy')
add(562,'spherical','Spherical configuration and installation',
 'In the spherical configuration figure, what does d₃ represent, and what installation issue accompanies its retraction?',[
 ('Radial extension; the sliding member may telescope or protrude behind the mechanism when retracted.','The figure shows extension along the arm, and the text calls out rearward clearance.'),
 ('Vertical column height; retraction changes only the floor elevation.','The d₃ arrow is radial along the arm, not a vertical base slide.'),
 ('Base azimuth; retraction means reducing an angular coordinate to zero.','d₃ is linear, while azimuth is labeled θ₁.'),
 ('Shoulder elevation; only the tool tip needs collision checks.','Elevation is θ₂, and the moving structure also needs clearance.')],
 'Radial prismatic travel can change the volume occupied behind the robot as well as the tool position. Work-cell collision checks must include that structure.',typ='diagram',difficulty='medium')
add(563,'cylindrical','Cylindrical coordinates and diagram labels',
 'Which mapping matches the cylindrical manipulator’s diagram labels?',[
 ('θ₁: azimuth; d₂: vertical motion; d₃: radial reach.','The top-view rotation, side-view column slide and horizontal extension carry these labels.'),
 ('θ₁: elevation; d₂: radial reach; d₃: fixed link length.','The rotation is about the vertical axis, and the side-view displacement arrows are swapped or omitted here.'),
 ('θ₁: wrist roll only; d₂ and d₃: two angular rotations.','The drawing concerns positioning and labels d₂/d₃ as linear travel.'),
 ('θ₁: radial displacement; d₂: azimuth; d₃: vertical motion.','This exchanges angular and displacement coordinates and misreads the arrows.')],
 'The figure labels azimuth θ₁, height d₂ and radial extension d₃. The prose enumerates the vertical slide before the rotation, so the question uses the actual figure labels rather than deriving numbering from sentence order.',typ='diagram',difficulty='easy')
add(563,'cylindrical','Cylindrical coordinates and diagram labels',
 'Which task requirement most directly matches the cylindrical configuration described in the lecture?',[
 ('Material handling organized around independent vertical travel, rotation about a vertical axis and radial reach.','Those motions follow cylindrical coordinates and suit the stated application.'),
 ('Independent roll and pitch at a fixed point with no translation.','This is an orientation task rather than the cylindrical positioning functions.'),
 ('Only motion on a fixed-radius spherical surface.','The radial slide permits changing radius, and the vertical slide is independent.'),
 ('Three independent mutually perpendicular linear travels with no base rotation.','That is the Cartesian positioning structure.')],
 'The cylindrical design supplies height, azimuth and reach directly, making its wrist-point positioning comparatively straightforward for these material-handling tasks.',typ='scenario',difficulty='easy')
add(564,'wrist','Wrist partition and attainable orientation',
 'Which joint labels lie in the circled orienting wrist of the lecture’s six-joint arm drawing?',[
 ('θ₄, θ₅ and θ₆.','These distal rotations are grouped in the wrist circle.'),
 ('θ₁, θ₂ and θ₃.','These label the proximal positioning portion outside the wrist circle.'),
 ('θ₂, θ₃ and θ₄.','This mixes two arm joints with one wrist joint.'),
 ('d₁, d₂ and d₃.','The displayed wrist is rotational and uses θ labels, not three prismatic coordinates.')],
 'The diagram separates the first three positioning joints from the distal three orienting wrist joints.',typ='diagram',difficulty='easy')
add(564,'wrist','Wrist partition and attainable orientation',
 'The slide states that its ideal three-DOF orthogonal-axis wrist can attain any orientation. Which qualification is explicitly required, and which extra claim does not follow?',[
 ('No joint limits are assumed; global orientation reach does not imply absence of singular configurations.','Coverage of the orientation set and local differential rank are different properties.'),
 ('Finite joint limits of any size are harmless; all wrist Jacobians are nonsingular.','Arbitrary restrictive limits can exclude orientations, and singular configurations may still exist.'),
 ('The wrist must contain three prismatic joints; rotations then become unnecessary.','The discussed wrist consists of revolute motions.'),
 ('The arm must have unlimited Cartesian reach; otherwise the wrist cannot rotate at all.','Arm reach and wrist orientation are distinct aspects of the partition.')],
 'The lecture’s orientation-reach statement assumes no joint limits. It should not be strengthened into a claim of a nonsingular wrist at every configuration.',difficulty='medium',assumptions=['The conventional intersecting orthogonal-axis wrist architecture described by the lecture, with unrestricted joint travel.'])
add([564,565],'wrist-tradeoff','Non-orthogonal wrist and separate orthogonal drawing',
 'Which trade-off is described for the non-orthogonal three-roll wrist in the text spanning these two slides?',[
 ('Continuous rotation is a cited advantage, but an orientation cone can remain unattainable for the third axis.','Unlimited rotation of individual joints does not guarantee all axis directions are attainable.'),
 ('Continuous rotation proves the third axis can point in every direction.','The next slide explicitly describes an excluded cone.'),
 ('Non-orthogonality forces the wrist to have only prismatic motion.','The design still uses intersecting rotational axes.'),
 ('The excluded cone concerns end-effector positions only, not orientation.','The text describes unattainable orientations and directions for the third axis.')],
 'The continuation lists an orientation limitation despite continuous-rotation capability. Do not confuse that text with the separately captioned orthogonal-wrist illustration.',difficulty='medium')
add(565,'wrist-transmission','Remote wrist actuation through concentric shafts',
 'What does the caption of the cross-section drawing on this page identify?',[
 ('An orthogonal-axis wrist driven by remotely located actuators through three concentric shafts.','This is the drawing’s explicit caption, despite adjacent non-orthogonal-wrist discussion.'),
 ('A non-orthogonal wrist with all motors mounted at the distal tool and no shafts.','This contradicts both the caption and the drawn concentric inputs.'),
 ('A Cartesian positioner driven by three parallel linear cylinders.','The drawing labels rotational actuator and wrist coordinates.'),
 ('A single-shaft wrist with one rotational degree of freedom.','Three concentric drive shafts and three wrist rotations are shown.')],
 'The caption specifies orthogonal axes and remote actuation through three concentric shafts, labeled with A₄, A₅ and A₆ at the inputs and θ₄, θ₅ and θ₆ for the wrist motions.',typ='diagram',difficulty='easy')
add(565,'wrist-scope','Scope of the intersecting-axis closed-form claim',
 'What geometric feature does the lecture associate with a closed-form kinematic solution, without treating its broad wording as a theorem for every constrained or redundant robot?',[
 ('Three consecutive intersecting joint axes.','This is the geometric condition stated in the slide.'),
 ('Any three nonconsecutive parallel links, regardless of their joints.','The slide specifies consecutive intersecting axes, not this different geometry.'),
 ('A sufficiently large payload rating, independent of joint geometry.','Payload rating does not establish the stated algebraic simplification.'),
 ('Three actuators sharing one power supply, even when their axes are skew.','Electrical supply arrangement is not the geometric criterion.')],
 'The slide associates three consecutive intersecting axes with a closed-form kinematic solution. Its wording lacks full manipulator, task and constraint scope, so this item tests the attributed geometric statement, not a universal solvability guarantee.',typ='definition',difficulty='easy',assumptions=['Source-attributed geometric claim only; do not infer feasibility for every pose or unrestricted validity for arbitrary redundant/closed-loop mechanisms.'],conflict='The slide says any manipulator with three consecutive intersecting axes has a closed-form kinematic solution without the usual mechanism and task qualifications.')
save()

LFORM=formula('L=Σ_(i=1)^N(a_(i−1)+d_i)',{'L':'structural length sum','N':'number of joint/link contributions','i':'summation index','a_(i−1)':'nonnegative link-length contribution from the chosen DH-based description','d_i':'nonnegative offset contribution, or full travel for a prismatic joint'},{'L,a_(i−1),d_i':'length','N,i':'dimensionless'},['Use nonnegative physical length contributions; a prismatic contribution is its total travel, not its instantaneous coordinate.'])
QFORM=formula('Q_L=L/W^(1/3)',{'Q_L':'structural length index','L':'structural length sum','W':'positive three-dimensional workspace volume'},{'Q_L':'dimensionless','L':'length','W':'length³'},['L and the cube root of W use consistent length units; W>0.'])
add(566,'length-sum','Structural length sum and prismatic travel',
 'For the lecture’s structural length sum L=Σ(a_(i−1)+d_i), how should d_i be treated for a prismatic joint?',[
 ('As a constant equal to its total travel between joint limits.','The index measures physical design size rather than the instantaneous configuration.'),
 ('As the current prismatic coordinate, so the structural size changes whenever the robot moves.','This contradicts the explicit constant-travel convention.'),
 ('As the current joint velocity.','Velocity is not a length contribution.'),
 ('As zero because prismatic joints have no rotational link twist.','A prismatic travel contribution is not removed by its lack of rotation.')],
 'The slide explicitly replaces the configuration-dependent prismatic coordinate with the total available travel when calculating this structural measure.',typ='definition',difficulty='easy',formulas=[LFORM])
add(566,'length-sum','Structural length sum and prismatic travel',
 'Use nonnegative length contributions. Two terms have a₀=0.4 m, d₁=0.1 m, a₁=0.3 m; the second joint is prismatic with limits 0.2 m and 0.7 m. What is L?',[
 ('1.3 m.','The second prismatic contribution is its travel 0.7−0.2=0.5 m; the sum is 0.4+0.1+0.3+0.5.'),
 ('1.5 m.','This incorrectly uses the upper coordinate limit 0.7 m instead of total travel.'),
 ('1.0 m.','This incorrectly uses the lower coordinate limit 0.2 m as the contribution.'),
 ('0.8 m.','This omits the prismatic travel entirely.')],
 'The fixed contributions total 0.8 m, and the prismatic joint contributes 0.5 m of total travel, giving L=1.3 m.',typ='numerical',difficulty='medium',steps=['Calculate the second joint travel: 0.7−0.2=0.5 m.','Sum both link lengths and both offset/travel contributions: 0.4+0.1+0.3+0.5=1.3 m.'],formulas=[LFORM],assumptions=['The supplied a and fixed-offset values are nonnegative physical length contributions in the lecture’s index convention.'])
add(567,'structural-index','Structural length index interpretation and scaling',
 'For L=6 m and W=8 m³, what is the structural length index?',[
 ('3, dimensionless.','The cube root of 8 m³ is 2 m, so the ratio is 6/2.'),
 ('0.75 m⁻².','This divides by volume directly instead of its cube root.'),
 ('12 m².','This multiplies the length by the cube root of volume instead of dividing.'),
 ('3 m.','The numerical ratio is right, but the two length units cancel.')],
 'Q_L=L/W^(1/3)=6/2=3 and has no units.',typ='numerical',difficulty='medium',steps=['Take W^(1/3)=(8 m³)^(1/3)=2 m.','Divide 6 m by 2 m to obtain 3.'],formulas=[QFORM])
add(567,'structural-index','Structural length index interpretation and scaling',
 'Two designs generate the same positive work volume. Design A has a smaller nonnegative length sum than design B. What follows from Q_L alone?',[
 ('A has the lower structural length index, indicating less length per cube-root work volume under this criterion.','With equal denominator, the smaller numerator gives the smaller index.'),
 ('A necessarily has greater payload, accuracy and acceleration as well.','Those performance measures are not contained in Q_L.'),
 ('B has the better structural index because larger linkage length is always preferred.','The lecture favors smaller length for the same work volume.'),
 ('Both have identical Q_L because only volume appears in the definition.','The length sum is the numerator and matters directly.')],
 'Q_L measures one structural/workspace trade-off. A lower value is favorable by that measure but does not determine all mechanical or control performance.',typ='scenario',difficulty='easy')
add(567,'structural-index','Structural length index interpretation and scaling',
 'A geometrically similar ideal design is enlarged by a factor s>0 in every length, with unchanged angular limits. If L becomes sL and W becomes s³W, how does Q_L change?',[
 ('It is unchanged.','The factor s in the numerator cancels the factor s from the cube root of s³W.'),
 ('It is multiplied by s.','This ignores the scaling of workspace volume.'),
 ('It is divided by s².','This would result from dividing by W rather than its cube root.'),
 ('It is multiplied by s³.','This confuses the volume scaling with the dimensionless ratio.')],
 'Q′_L=sL/(s³W)^(1/3)=sL/(sW^(1/3))=Q_L. This scale invariance applies to the stated geometric assumptions, not necessarily to stiffness, mass or speed.',typ='derivation',difficulty='medium',steps=['Scale the structural length by s and the three-dimensional volume by s³.','Take the positive cube root: (s³W)^(1/3)=sW^(1/3).','Cancel s to recover the original Q_L.'],formulas=[QFORM,formula('Q′_L=sL/(s³W)^(1/3)=Q_L',{'Q′_L':'index after geometric scaling','Q_L':'original index','s':'positive common length scale factor','L':'original structural length sum','W':'original workspace volume'},{'Q′_L,Q_L,s':'dimensionless','L':'length','W':'length³'},['Geometric similarity and unchanged angular/relative travel constraints.'])])
add(567,'cartesian-index','Cartesian structural minimum',
 'For an ideal Cartesian positioner with positive travels u,v,w, assume L=u+v+w and W=uvw. Which condition attains the stated minimum Q_L=3?',[
 ('u=v=w.','The arithmetic–geometric mean inequality gives u+v+w≥3(uvw)^(1/3), with equality at equal travels.'),
 ('One travel approaches zero while the other two remain fixed.','The volume approaches zero and the index grows rather than attaining its minimum.'),
 ('One travel equals the sum of the other two.','That relation does not generally give equality in the arithmetic–geometric mean inequality.'),
 ('All travel triples have Q_L=3 regardless of proportions.','Unequal positive travels generally give a larger ratio.')],
 'The minimum is obtained by equal travel on all three axes. Under the stated simplified structural model, AM–GM proves the lower bound 3.',typ='derivation',difficulty='medium',assumptions=['Positive travels and idealized length sum equal to their sum, with no additional fixed structural contributions.'],steps=['Write Q_L=(u+v+w)/(uvw)^(1/3).','Apply u+v+w≥3(uvw)^(1/3).','Equality requires u=v=w, producing Q_L=3.'],formulas=[formula('Q_L=(u+v+w)/(uvw)^(1/3)≥3',{'Q_L':'Cartesian structural length index','u,v,w':'positive independent Cartesian travel lengths'},{'Q_L':'dimensionless','u,v,w':'length'},['Ideal length sum u+v+w and full rectangular workspace volume uvw.'])])
add(567,'cartesian-index','Cartesian structural minimum',
 'Using the ideal model L=u+v+w and W=uvw, compare Cartesian travels (1,1,8) m with (2,2,2) m. Which conclusion is correct?',[
 ('Both have W=8 m³, but their indices are 5 and 3 respectively.','Length sums are 10 m and 6 m; both cube-root volumes are 2 m.'),
 ('Both indices are 3 because their workspace volumes match.','The length sums differ, so equal volume does not imply equal index.'),
 ('The (1,1,8) design has index 1.25 because Q_L=L/W.','The denominator should be the cube root of volume.'),
 ('The (2,2,2) design has a larger index because every axis exceeds 1 m.','The full sums, not selected axis comparisons, determine the numerator.')],
 'The elongated box requires more total travel length for the same volume in this ideal model, giving Q_L=10/2=5 rather than 6/2=3.',typ='numerical',difficulty='medium',steps=['Compute both products: 1·1·8=2·2·2=8 m³.','Compute sums: 10 m and 6 m.','Divide each by 2 m to obtain 5 and 3.'],formulas=[QFORM])
add(567,'index-benchmark','Scope of the structural benchmark',
 'How should the slide’s “ideal articulated robots achieve Q_L=0.62” be used?',[
 ('As the slide’s idealized structural/workspace benchmark, not a guarantee that every articulated arm has that value or is best on every criterion.','The wording is idealized and the index measures only one trade-off.'),
 ('As a universal lower bound on cycle time measured in seconds.','Q_L is dimensionless and is not a time metric.'),
 ('As proof that every real articulated installation is collision-free.','The index does not establish collision-free installation.'),
 ('As the Cartesian equal-travel minimum.','The slide separately gives the Cartesian minimum as 3.0.')],
 'The lecture contrasts an ideal articulated benchmark of 0.62 with a Cartesian minimum of 3.0. Neither value alone establishes complete task suitability.',typ='definition',difficulty='easy')
WFORM=formula('w=√det(JJᵀ); for square J, w=|det J|',{'w':'velocity manipulability measure for the selected task','J':'task-velocity Jacobian at the evaluated configuration','Jᵀ':'transpose of J'},{'w':'product of the chosen task-velocity per joint-rate scale units','J':'task-velocity units per joint-rate units'},['Use a fixed task definition and consistent coordinate scaling; square-determinant shortcut only for square J.'])
add(568,'singularity','Task rank loss and conditioning',
 'What does “loss of DOF” at a manipulator singularity mean in the Jacobian discussion?',[
 ('Loss of one or more independent instantaneous task-velocity directions through a rank drop.','The relevant loss is differential task mobility, not disappearance of physical joints.'),
 ('A physical joint is removed from the mechanism at that instant.','The number of hardware joints does not change at a kinematic singularity.'),
 ('Every joint motor necessarily fails electrically.','Kinematic rank loss is not equivalent to motor failure.'),
 ('The end-effector position becomes undefined in forward kinematics.','Forward position can be well-defined even when the differential mapping loses rank.')],
 'Singularity concerns the rank of the task Jacobian. Some instantaneous task directions become unattainable or require problematic inverse rates near the singularity.',difficulty='medium')
add(568,'manipulability','Velocity manipulability and square/rectangular Jacobians',
 'For a consistently normalized square Jacobian J=diag(2,−3), what is w=√det(JJᵀ)?',[
 ('6.','JJᵀ=diag(4,9), so the determinant is 36 and its nonnegative square root is 6.'),
 ('−6.','This is det(J), but manipulability takes its absolute value for square J.'),
 ('36.','This is det(JJᵀ), before taking the square root.'),
 ('√13.','This takes a square root of a sum of squared diagonal entries, not the determinant product.')],
 'The square-J shortcut gives w=|det J|=|−6|=6; the measure is nonnegative.',typ='numerical',difficulty='medium',assumptions=['Dimensionless normalized task and joint-rate coordinates.'],steps=['Form JJᵀ=diag(4,9).','Compute its determinant 36.','Take √36=6, equivalently |2·(−3)|.'],formulas=[WFORM])
add(568,'manipulability','Velocity manipulability and square/rectangular Jacobians',
 'For a two-coordinate task with three normalized joint rates, let J=[[1,0,0],[0,2,0]]. Which statement is correct?',[
 ('JJᵀ=diag(1,4), so w=2 and the task Jacobian has full row rank despite having a redundant joint-rate direction.','Both task directions are supported; the third column being zero provides a null direction, not task rank loss.'),
 ('det(J)=0, so the task must be singular.','A determinant is not defined for this 2×3 matrix.'),
 ('w=0 because every rectangular Jacobian has zero manipulability.','The Gram matrix JJᵀ can be positive definite when J has full row rank.'),
 ('The task rank is three because there are three joint-rate inputs.','A two-row task Jacobian has rank at most two.')],
 'Use the Gram determinant for the rectangular task Jacobian. Its two rows are independent, giving w=√4=2; redundancy is not itself singularity.',typ='numerical',difficulty='hard',assumptions=['Fixed dimensionless normalization and a two-dimensional task, not a six-dimensional spatial task.'],steps=['Multiply J by Jᵀ to obtain [[1,0],[0,4]].','Its determinant is 4 and w=2.','The task rank is 2, equal to its number of rows; there is one joint-space null direction.'],formulas=[WFORM])
add(568,'manipulability','Velocity manipulability and square/rectangular Jacobians',
 'Two normalized square task Jacobians are J_A=diag(10,0.1) and J_B=diag(1,1). What comparison is valid?',[
 ('Both have w=1, but B is isotropic while A has strongly unequal directional gains.','The determinant is a product and does not alone measure directional uniformity.'),
 ('A has ten times B’s manipulability because its largest diagonal entry is ten.','The smaller entry 0.1 must also enter the determinant product.'),
 ('Equal w proves equal conditioning and identical velocity ellipsoid shapes.','Equal volume factors can coexist with very different axis ratios.'),
 ('A is exactly singular because one entry is below one.','Its entries are nonzero, so its determinant is nonzero; it is anisotropic, not exactly singular.')],
 'Both determinant magnitudes equal 1. B has equal singular values, whereas A has a ratio of 100 between its directional gains. A scalar volume measure does not replace a conditioning check.',typ='numerical',difficulty='medium',assumptions=['Both matrices use identical dimensionless task and joint-coordinate normalization.'],steps=['Calculate |10·0.1|=1 and |1·1|=1.','Compare diagonal singular values: (10,0.1) versus (1,1).','The corresponding maximum/minimum ratios are 100 and 1.'],formulas=[WFORM])
add(568,'manipulability','Velocity manipulability and square/rectangular Jacobians',
 'For a real m×n task Jacobian with m≤n, what does w=0 imply about the m task rows?',[
 ('They are linearly dependent, so the Jacobian lacks full row rank.','A singular Gram matrix JJᵀ is equivalent to dependent rows.'),
 ('Every element of J must be zero.','Nonzero rows can still be dependent, such as two identical rows.'),
 ('The mechanism must have exactly m−1 physical joints.','Rank loss does not determine the hardware joint count.'),
 ('The determinant of a nonsquare J must be a negative number.','A nonsquare J has no determinant, and w is nonnegative.')],
 'The Gram determinant vanishes exactly when the rows are dependent. The interpretation is relative to the chosen m-dimensional task.',difficulty='medium',formulas=[WFORM],assumptions=['Real task Jacobian, m≤n, and w computed as √det(JJᵀ).'])
MXFORM=formula('M_x=J^(−T) M J^(−1)',{'M_x':'Cartesian/task-space inertia matrix at the same configuration','M':'joint-space inertia matrix','J':'Jacobian mapping joint rates to task velocity','J^(−1)':'matrix inverse of J','J^(−T)':'transpose of J inverse'},{'M_x':'units consistent with task-coordinate kinetic energy','M':'units consistent with joint-coordinate kinetic energy','J':'task-velocity units per joint-rate units'},['Square nonsingular J; matrices evaluated at the same configuration; consistent task-coordinate normalization.'])
ELLFORM=formula('Xᵀ M_x X=1',{'X':'vector in the normalized Cartesian quadratic-form coordinates','M_x':'symmetric positive-definite inertia metric in those same normalized coordinates','Xᵀ':'transpose of X'},{'X,M_x':'normalized units chosen so the quadratic form is dimensionless'},['Consistent common normalization; interpret this as the stated metric ellipsoid, not an arbitrary actuator-limited acceleration set.'])
add(569,'inertia','Cartesian inertia transformation and ellipsoid',
 'What additional property distinguishes the inertia-ellipsoid discussion from velocity manipulability based only on J?',[
 ('It includes the joint-space mass matrix, capturing configuration-dependent inertial directionality.','The transformation uses M as well as J.'),
 ('It depends only on the robot’s color and external shape.','Those are not variables in the given inertia formula.'),
 ('It replaces the mass matrix by the total workspace volume.','Workspace volume belongs to the structural index, not this inertia transformation.'),
 ('It makes the actuator effort limits irrelevant for every physical acceleration claim.','Physical acceleration bounds still depend on the available forces/torques and other dynamics.')],
 'The slide attributes the inertia-ellipsoid approach to Asada and uses the Cartesian mass matrix to discuss acceleration-related directional behavior, unlike a velocity-only Jacobian measure.',difficulty='easy')
add(569,'inertia','Cartesian inertia transformation and ellipsoid',
 'When can the displayed formula M_x=J^(−T) M J^(−1) be applied directly with ordinary matrix inverses?',[
 ('When J is square and nonsingular, with consistent coordinates and all matrices at the same configuration.','Ordinary two-sided inverses require a square full-rank matrix.'),
 ('For every rectangular J by treating J^(−1) as an ordinary inverse.','Rectangular matrices do not have that ordinary inverse.'),
 ('At any singular configuration because M cancels the missing inverse.','Multiplication by M does not create an inverse for singular J.'),
 ('Only when the joint-space mass matrix is zero.','A physical positive-definite mass matrix need not vanish, and zero mass is not the stated requirement.')],
 'The printed expression requires an invertible square J. Other task dimensions or singularities need different treatment, not an unannounced replacement by an ordinary inverse.',difficulty='medium',formulas=[MXFORM])
add(569,'inertia','Cartesian inertia transformation and ellipsoid',
 'In consistently normalized coordinates, J=diag(2,1) and M=diag(8,3). What is M_x?',[
 ('diag(2,3).','Multiplying diag(1/2,1) on both sides of M divides its first diagonal entry by four.'),
 ('diag(32,3).','This uses J on both sides rather than J inverse.'),
 ('diag(4,3).','This applies only one inverse factor, not both.'),
 ('diag(1/2,1/3).','This is not the required coordinate transformation and incorrectly inverts the resulting inertia.')],
 'J inverse and its transpose are diag(1/2,1), so M_x=diag(8/4,3)=diag(2,3).',typ='numerical',difficulty='medium',assumptions=['All entries are given in mutually consistent normalized coordinates; J is square and invertible.'],steps=['Invert J to obtain diag(1/2,1).','Its inverse transpose is the same diagonal matrix.','Multiply the three diagonal matrices to obtain diag(2,3).'],formulas=[MXFORM])
add(569,'inertia-geometry','Inertia ellipsoid shape and isotropy',
 'For normalized coordinates X=(u,v) and M_x=diag(4,1), what are the semiaxis lengths of XᵀM_xX=1 along u and v?',[
 ('1/2 along u and 1 along v.','The equation is 4u²+v²=1; each intercept is the reciprocal square root of its coefficient.'),
 ('4 along u and 1 along v.','The matrix coefficients are not the semiaxis lengths.'),
 ('2 along u and 1 along v.','Taking square roots rather than reciprocal square roots reverses the relation.'),
 ('1/4 along u and 1 along v.','The coefficient multiplies a squared coordinate, so a square root is required.')],
 'Setting the other coordinate to zero gives |u|=1/2 and |v|=1. This is an ellipse in the stated normalized metric coordinates.',typ='numerical',difficulty='medium',assumptions=['Normalized dimensionless quadratic-form coordinates; no claim that these intercepts equal a particular actuator-limited physical acceleration.'],steps=['Expand XᵀM_xX as 4u²+v².','At v=0, 4u²=1 gives |u|=1/2.','At u=0, v²=1 gives |v|=1.'],formulas=[ELLFORM])
add(569,'inertia-geometry','Inertia ellipsoid shape and isotropy',
 'In the same normalized two-dimensional coordinates, which positive-definite inertia matrix produces a circular rather than elongated metric ellipse?',[
 ('M_x=diag(3,3).','Equal positive eigenvalues give equal semiaxes.'),
 ('M_x=diag(1,9).','Unequal eigenvalues give unequal semiaxes.'),
 ('M_x=[[2,1],[1,2]].','Its eigenvalues are 3 and 1, so the ellipse is rotated but not circular.'),
 ('M_x=diag(0,3).','This is not positive definite and gives an unbounded degenerate quadratic-form set.')],
 'Isotropy requires equal principal values under the chosen normalization. A positive scalar multiple of the identity produces a circle in 2D or a sphere in 3D.',difficulty='medium',assumptions=['Compare all options in the same normalized Cartesian coordinate system.'],formulas=[ELLFORM])
add(569,'inertia-geometry','Inertia ellipsoid shape and isotropy',
 'What does the figure containing many small ellipses across a two-DOF arm’s workspace illustrate?',[
 ('The local inertia metric’s size, orientation and anisotropy can vary with the arm configuration.','Different plotted locations have differently shaped and oriented ellipses, including near-circular ones.'),
 ('Every reachable point has the same circular inertia metric.','The drawing visibly includes elongated and differently oriented ellipses.'),
 ('Each small ellipse is a separate collision obstacle introduced into the cell.','The caption identifies these shapes as inertia ellipsoids, not obstacles.'),
 ('The ellipses are trajectories that the end-effector must follow during every motion.','They depict local directional properties rather than prescribed time paths.')],
 'The figure is a configuration-dependent field of local inertia ellipses. Circular instances represent isotropic points under the metric, not proof of identical behavior throughout the workspace.',typ='diagram',difficulty='medium')
save()

FKFORM=formula('x=l₁cosθ₁+l₂cos(θ₁+θ₂); y=l₁sinθ₁+l₂sin(θ₁+θ₂)',{'x,y':'endpoint coordinates in the fixed planar base frame','l₁':'base-to-elbow link length','l₂':'elbow-to-endpoint link length','θ₁':'first-link angle from the positive base x direction','θ₂':'second joint angle relative to the first link'},{'x,y,l₁,l₂':'same length unit','θ₁,θ₂':'radians'},['Ideal planar two-revolute-joint chain with fixed base and relative second-joint angle.'])
RFORM=formula('r²=x²+y²=l₁²+l₂²+2l₁l₂cosθ₂; |l₁−l₂|≤r≤l₁+l₂',{'r':'radial distance from the base to the endpoint','x,y':'endpoint coordinates in the base plane','l₁,l₂':'positive planar link lengths','θ₂':'relative elbow angle'},{'r,x,y,l₁,l₂':'same length unit','θ₂':'radians'},['Full angular ranges for both joints, ideal links and no collision constraints for the full annulus.'])
add([570,571],'planar-fk','Planar 2R geometry and forward kinematics',
 'In the two-link diagram, why does the second link contribute l₂cos(θ₁+θ₂) rather than l₂cosθ₂ to the fixed-frame x coordinate?',[
 ('θ₂ is relative to the first link, so the second link’s fixed-frame orientation is θ₁+θ₂.','Adding the relative rotations gives the absolute second-link direction.'),
 ('θ₂ is already the absolute orientation and θ₁+θ₂ is only a plotting shortcut.','This contradicts the relative-joint model and would generally double-count θ₁ if θ₂ were absolute.'),
 ('The cosine sum is necessary because the second link length changes with both angles.','The link length is fixed; its direction changes.'),
 ('The second link’s contribution should use θ₁ only because elbow rotation cannot affect position.','Elbow motion changes the second-link direction and the endpoint position.')],
 'The base-to-elbow link has orientation θ₁, and the elbow adds θ₂. Resolving both vectors in the fixed frame therefore uses θ₁ and θ₁+θ₂.',typ='diagram',difficulty='medium',formulas=[FKFORM])
add([570,571],'planar-fk','Planar 2R geometry and forward kinematics',
 'For l₁=5, l₂=4, θ₁=π/2 and θ₂=−π/2, what is the endpoint position in the stated fixed frame?',[
 ('(4,5) length units.','The first link points along +y and the second along +x.'),
 ('(0,1) length units.','This incorrectly treats θ₂ as an absolute second-link angle.'),
 ('(5,4) length units.','This corresponds to the different configuration θ₁=0, θ₂=π/2.'),
 ('(0,9) length units.','This would require both links to point along +y, which means θ₂=0.')],
 'The absolute second-link angle is zero. Thus x=5cos(π/2)+4cos0=4 and y=5sin(π/2)+4sin0=5.',typ='numerical',difficulty='medium',steps=['Add the joint angles: θ₁+θ₂=0.','Compute x=5·0+4·1=4.','Compute y=5·1+4·0=5.'],formulas=[FKFORM],assumptions=['Angles are in radians; the source gives no named physical length unit, so use consistent length units.'])
add([570,572],'radial-reach','Planar radial reach and continuous workspace',
 'For the lecture’s planar arm with l₁=5 and l₂=4, which expression follows by squaring and adding the forward-kinematics coordinates?',[
 ('r²=41+40cosθ₂.','The squared lengths sum to 25+16, and the cross term is 2·5·4cosθ₂.'),
 ('r²=81cosθ₁.','This incorrectly makes the radius depend on a global rotation and can even become negative.'),
 ('r²=41+40cos(θ₁+θ₂).','The cross term depends on the angle between the link vectors, which is θ₂.'),
 ('r²=9+sinθ₂.','This confuses the maximum reach with squared radial distance and omits the link products.')],
 'Using cosAcosB+sinAsinB=cos(A−B), the cross term reduces to 2l₁l₂cosθ₂. The base angle rotates the endpoint but does not change its radius.',typ='derivation',difficulty='medium',steps=['Expand x²+y² using the two link-vector components.','Each link contributes l_i² through sin²+cos²=1.','The cross term is 2l₁l₂cos[(θ₁+θ₂)−θ₁]=2l₁l₂cosθ₂.','Substitute 5 and 4 to obtain 41+40cosθ₂.'],formulas=[FKFORM,RFORM])
add([572,574],'radial-reach','Planar radial reach and continuous workspace',
 'Which pair gives the ideal continuous workspace’s inner and outer radii for l₁=5, l₂=4 and full joint-angle ranges?',[
 ('1 and 9 length units.','The folded and straight reaches are |5−4| and 5+4.'),
 ('0 and 9 length units.','The unequal links leave an unreachable central disk.'),
 ('4 and 5 length units.','Individual link lengths are not the endpoint’s radial extremes.'),
 ('1 and 41 length units.','41 is the sum of squared link lengths, not the maximum radius.')],
 'The ideal continuous position set is the annulus 1≤r≤9, matching the central hole and outer radius indicated in the plot.',typ='diagram',difficulty='easy',assumptions=['Continuous full joint-angle ranges and no collision or additional limits.'],formulas=[RFORM])
add(572,'radial-reach','Planar radial reach and continuous workspace',
 'With both angles continuously allowed in [−π,π], which target is outside the ideal position workspace of the l₁=5, l₂=4 planar arm?',[
 ('(0.6,0.6) length units.','Its radius √0.72≈0.849 is below the minimum reach 1.'),
 ('(1,0) length units.','This is on the reachable inner boundary.'),
 ('(0,9) length units.','This is on the reachable outer boundary.'),
 ('(3,4) length units.','Its radius is 5, inside the reachable annulus.')],
 'Check each target’s distance from the base against 1≤r≤9. Only (0.6,0.6) lies in the unreachable central disk.',typ='numerical',difficulty='medium',steps=['Compute r=√(x²+y²) for each target.','The radii are √0.72, 1, 9 and 5 respectively.','Only √0.72 is below 1.'],formulas=[RFORM],assumptions=['Ideal continuous full-angle workspace, not merely the finite plotted grid; boundary configurations are allowed.'])
add([570,572],'radial-reach','Planar radial reach and continuous workspace',
 'Which relative elbow angles give the maximum and minimum radii of this ideal two-link arm?',[
 ('Maximum at θ₂=0; minimum at θ₂=±π.','The links are aligned in the same direction at zero and oppose each other at π.'),
 ('Maximum at θ₁=0 regardless of θ₂; minimum at θ₁=π regardless of θ₂.','Changing θ₁ alone rotates the endpoint without changing its radius.'),
 ('Maximum at θ₂=±π; minimum at θ₂=0.','This reverses the straight and folded configurations.'),
 ('Both extrema occur only at θ₂=π/2.','At π/2 the radius is √41, between the extremes.')],
 'The radial formula depends on cosθ₂. Its largest and smallest values are 1 and −1, producing the straight and folded extremes.',difficulty='medium',formulas=[RFORM])
add([572,567],'planar-area','Planar area versus three-dimensional workspace volume',
 'The continuous workspace is the planar annulus 1≤r≤9. What is its area, and can that number be substituted directly for the three-dimensional volume W in Q_L=L/W^(1/3)?',[
 ('80π square length units; no, area is not the volume required by that index.','The annular area is π(9²−1²), and substituting area would make the ratio dimensionally different.'),
 ('80π cubic length units; yes, because every robot workspace is a volume.','This workspace is planar, so its measure is area, not cubic volume.'),
 ('8π square length units; yes, because subtracting radii gives the annulus measure.','Area uses squared radii, and the volume requirement still remains.'),
 ('81π square length units; no, because the entire disk is reachable.','The central disk of radius 1 is excluded and must be subtracted.')],
 'The area equals 80π in squared length units. The structural index on page 567 is defined using a three-dimensional work volume; replacing it with area silently changes its dimensions.',typ='numerical',difficulty='medium',steps=['Compute outer disk area 81π and subtract inner disk area π.','Obtain 80π square length units.','Note that the cube root of area has units length^(2/3), so it cannot cancel a length numerator in the defined dimensionless index.'],formulas=[QFORM,formula('A=π(r_max²−r_min²)',{'A':'area of the planar annulus','r_max':'outer radius','r_min':'inner radius','π':'circle constant'},{'A':'length²','r_max,r_min':'length','π':'dimensionless'},['Full planar annulus.'])])
add([572,573,574],'continuous-sampled','Continuous reachable set versus finite sample plot',
 'The lecture plots a 200×200 joint-angle grid. Which interpretation separates the actual computed data from the continuous model?',[
 ('The code evaluates finitely many reachable positions; the continuous angle model has infinitely many positions filling the ideal annulus.','Finite samples illustrate the continuum but do not enumerate every point.'),
 ('The code enumerates every point in the annulus exactly once.','A finite list cannot enumerate the continuous set, and repeated configurations may occur.'),
 ('Every blank space between plotted dots is a genuine unreachable region.','Plotting gaps may simply arise from finite sampling.'),
 ('Because the plot is finite, the analytic annular bounds are invalid.','Finite sampling does not invalidate the continuous geometric derivation.')],
 'The continuous forward-kinematic image and a sampled scatter plot are different objects. The statement that plotted points represent all reachable positions must be read as an illustration, not literal exhaustive enumeration.',difficulty='medium',conflict='Page 572 describes the plotted points as all possible positions, but page 573 evaluates only a finite 200×200 angle grid.')
CODEASS=['Interpret the visually wrapped title as the valid one-line statement plt.title(\'Articulated Robot Workspace\'); all other discussed code is as shown.']
add(573,'python-literal','Literal code wrapping versus intended execution',
 'If the displayed title is copied with a literal newline inside the ordinary single-quoted string, as in "plt.title(\'Articulated Robot\nWorkspace\')", what happens before the file can run?',[
 ('Python raises a SyntaxError for the unterminated ordinary string literal.','An ordinary single-quoted string cannot contain that unescaped physical newline.'),
 ('Python automatically inserts a space and continues the string because the call has parentheses.','Parentheses allow expression continuation, not an unescaped newline inside a short string token.'),
 ('The code runs but sets the title to the variable Workspace.','The source fails lexical parsing before such a variable interpretation.'),
 ('The loops run and then raise a numerical division-by-zero error.','No division causes this issue, and a syntax error prevents the module from executing.')],
 'The visible slide wrap is not valid literal Python if preserved inside a single-quoted string. Rejoin the title on one line, or use an explicitly valid multiline-string construction, before discussing the intended execution.',typ='code',difficulty='medium',conflict='Page 573 visually wraps a single-quoted title across lines. The intended title is clear from page 574, but a literal newline copy is a syntax error.')
add(573,'python-sampling','Angle grids, nested loops and paired coordinates',
 'After treating the title wrap as one valid line, what do the nested loops over two 200-element angle arrays append?',[
 ('40,000 x values and 40,000 corresponding y values, one pair for each grid combination.','There are 200×200 combinations, and each iteration appends both coordinates.'),
 ('200 x values and 200 y values, because the arrays have equal length.','That would match paired iteration such as zip, not nested Cartesian-product loops.'),
 ('400 coordinate pairs, because the array lengths add.','Nested-loop counts multiply rather than add.'),
 ('80,000 distinct endpoint positions, because x and y are appended separately.','Two scalar coordinates form one point, and uniqueness is not guaranteed.')],
 'For each of 200 first-joint values, the inner loop evaluates all 200 second-joint values. It appends one aligned coordinate pair per evaluation.',typ='code',difficulty='medium',assumptions=CODEASS,steps=['Count 200 outer iterations.','For each, count 200 inner iterations.','Each of the 40,000 iterations appends one x and one y.'])
add(573,'python-sampling','Angle grids, nested loops and paired coordinates',
 'In the shown loop order, what remains fixed during one complete pass of the inner loop?',[
 ('The first-joint angle t1; t2 sweeps its angle array.','The outer-loop value is held while the nested loop runs.'),
 ('The second-joint angle t2; t1 sweeps all values inside.','This reverses the indentation and loop order.'),
 ('Both angles, while only the link lengths change.','The link lengths are constants and t2 changes in the inner loop.'),
 ('The endpoint x coordinate, while y alone changes.','Changing t2 generally changes both x and y.')],
 'The outer loop assigns t1 once per inner sweep; the inner loop then varies t2 and recomputes both coordinates.',typ='code',difficulty='easy',assumptions=CODEASS)
add(573,'python-sampling','Angle grids, nested loops and paired coordinates',
 'Replacing the two nested loops with "for t1, t2 in zip(theta1, theta2):" while keeping both 200-element arrays would have which effect?',[
 ('Only 200 paired configurations would be evaluated, rather than the 40,000-element Cartesian product.','zip pairs matching array positions instead of nesting every combination.'),
 ('It would evaluate the same Cartesian product in a faster syntax.','zip does not generate all pair combinations.'),
 ('It would evaluate 400 configurations by concatenating the arrays.','zip pairs elements; it neither concatenates nor adds the lengths.'),
 ('It would necessarily raise an error because both arrays have the same length.','Equal-length iterable arrays are valid inputs to zip.')],
 'The nested loops explore all combinations. With these identical grids, zip instead follows matching-index pairs t1=t2 and misses most joint combinations.',typ='code',difficulty='medium',assumptions=CODEASS)
add(573,'python-sampling','Angle grids, nested loops and paired coordinates',
 'Why is 40,000 loop evaluations not a proof of 40,000 distinct physical endpoint positions?',[
 ('The included endpoints −π and π represent the same angular orientation, and different configurations can also share an endpoint.','Periodic duplicates and inverse-kinematic multiplicity can reduce the number of distinct points.'),
 ('A scatter plot is restricted to displaying only 200 markers.','The plotting call can display the full list; that is not the source of duplicates.'),
 ('Each evaluation omits its y value.','Both append statements are present inside the inner loop.'),
 ('NumPy automatically deletes repeated configurations from the arrays.','linspace supplies the requested samples; the code does not deduplicate them.')],
 'The arrays include both periodic endpoints. The code stores every evaluation, not a deduplicated set of geometrically distinct positions; floating-point rounding may also affect exact equality tests.',typ='code',difficulty='medium',assumptions=CODEASS+['Discuss mathematical physical equivalence rather than bit-for-bit equality of floating-point coordinates.'])
add([572,573],'sampling-grid','Even inclusive grid and sampled boundary',
 'An inclusive 200-point linspace from −π to π has samples θ_k=−π+2πk/199 for k=0,…,199. Does it contain zero, and what is the smallest absolute sampled angle?',[
 ('No; the closest samples are ±π/199.','Zero would require k=199/2=99.5, which is not an integer index.'),
 ('Yes; k=100 gives exactly zero.','At k=100 the sample is π/199, not zero.'),
 ('No; the closest samples are ±2π/200.','The step denominator is 199 for 200 inclusive samples, and the closest magnitude is half a step.'),
 ('Yes; both k=99 and k=100 give zero.','The two distinct central samples straddle zero rather than coincide there.')],
 'An even number of equally spaced inclusive samples over this symmetric interval puts zero between the two central samples.',typ='derivation',difficulty='medium',steps=['Solve −π+2πk/199=0, obtaining k=99.5.','The nearest integer indices are 99 and 100.','Substitution gives −π/199 and +π/199.'],formulas=[formula('θ_k=−π+2πk/199',{'θ_k':'sampled joint angle at integer index k','k':'integer index from 0 through 199','π':'circle constant'},{'θ_k':'radians','k,π':'dimensionless'},['200 equally spaced samples include both endpoints.'])],assumptions=CODEASS)
add([570,572,573],'sampling-grid','Even inclusive grid and sampled boundary',
 'For the l₁=5, l₂=4 arm sampled with the inclusive 200-point grids, what is the maximum sampled radius in exact arithmetic, compared with the continuous maximum 9?',[
 ('√(41+40cos(π/199)), slightly less than 9.','The nearest sampled elbow angles to zero are ±π/199, which maximize the sampled cosine.'),
 ('Exactly 9, because both angle endpoints ±π are included.','Those elbow endpoints give the folded minimum, not the straight maximum.'),
 ('Exactly √41, because the grid necessarily stops at an elbow angle of π/2.','The grid spans the full interval and includes elbow angles much closer to zero.'),
 ('Greater than 9, because numerical sampling expands the physical workspace.','The forward model cannot exceed the sum-of-link-length bound in exact arithmetic.')],
 'The radial formula is 41+40cosθ₂. The even grid omits θ₂=0, so its largest sampled radius uses ±π/199 and is about 8.999723 rather than exactly 9.',typ='numerical',difficulty='hard',steps=['Use r²=41+40cosθ₂.','The grid’s closest elbow samples to zero are ±π/199.','Substitute either to obtain r_max,sample=√(41+40cos(π/199))<9.'],formulas=[RFORM,formula('r_max,sample=√(41+40cos(π/199))',{'r_max,sample':'largest radius in the stated finite joint grid','π':'circle constant','41':'l₁²+l₂² for link lengths 5 and 4','40':'2l₁l₂ for those links'},{'r_max,sample':'length units','41,40':'squared length units','π/199':'radians'},['Exact arithmetic and inclusive 200-point elbow grid.'])],assumptions=CODEASS+['Exact arithmetic; the first-joint angle does not affect radial distance.'])
add(573,'python-complexity','Workspace enumeration cost and display settings',
 'If both angle grids are increased from 200 to 400 samples with the same nested-loop and stored-list method, how do the number of FK evaluations and stored coordinate pairs change?',[
 ('Both become four times as large, from 40,000 to 160,000.','The Cartesian-product count scales with the product of the two sample counts.'),
 ('Both become twice as large, from 40,000 to 80,000.','This accounts for doubling only one grid.'),
 ('They remain unchanged because workspace geometry is unchanged.','The continuous geometry is unchanged, but the sampled computation grows.'),
 ('The number of evaluations quadruples but the lists still contain only 200 pairs.','Every evaluation still appends a pair, so storage grows with evaluation count.')],
 'The shown method uses one forward evaluation and one stored coordinate pair for each grid combination: N₁N₂. Doubling both dimensions multiplies both quantities by four.',typ='code',difficulty='medium',assumptions=CODEASS,steps=['Original count is 200²=40,000.','New count is 400²=160,000.','The ratio is 4.'])
add([573,574],'python-complexity','Workspace enumeration cost and display settings',
 'Which shown plotting instruction explicitly ensures that equal distances along x and y use equal display scale?',[
 ("plt.axis('equal').",'This requests equal data-axis scaling, preserving circular geometry.'),
 ('plt.figure(figsize=(8,8)).','A square figure size alone does not guarantee equal data-axis scaling.'),
 ('plt.grid(True).','Grid visibility does not impose an equal aspect ratio.'),
 ('plt.scatter(x_points,y_points,s=1).','The scatter marker-size argument changes marker area, not the data-axis scaling.')],
 'Equal data scaling is needed to read an annular workspace without aspect distortion. Figure size, grid lines and marker size serve different display purposes.',typ='code',difficulty='easy',assumptions=CODEASS)
add([573,574],'sample-interpretation','Plot density, reachability and motion interpretation',
 'The scatter plot shows rings and gaps within the ideal annulus. What can be concluded about them from this computation?',[
 ('They reflect finite joint-space sampling and its nonlinear position map; they do not by themselves prove internal continuous-workspace obstacles.','Uniform angle samples need not give uniformly spaced Cartesian samples.'),
 ('Each visible gap is a physical collision boundary encoded by the program.','The shown code contains no collision or obstacle model.'),
 ('Uniform angle spacing guarantees uniform point density in Cartesian area.','The forward map has configuration-dependent area scaling.'),
 ('The dot ordering proves a feasible time-optimal robot trajectory.','The code sweeps configurations without a time law, dynamic feasibility check or motion optimization.')],
 'This is a sampled position-set visualization, not a collision map or a timed trajectory. The FK mapping and sample density create visual patterns.',typ='diagram',difficulty='medium',assumptions=CODEASS)
add([548,551,552,553,554,567,568,569,575],'design-synthesis','Task-based mechanism selection synthesis',
 'A proposed arm has an excellent structural length index. Before selecting it for a task with tight cycle-time and placement requirements, which conclusion is justified?',[
 ('The index is useful, but payload over required configurations, cycle time, accuracy/repeatability, usable conditioning and cell access still need evaluation.','The lecture presents these as complementary task and design criteria.'),
 ('The low index alone proves all accuracy and cycle-time requirements are satisfied.','Structural length per workspace volume does not encode those requirements.'),
 ('The index replaces the need to check singularities because it uses workspace volume.','A large or efficient workspace may still include poorly conditioned regions.'),
 ('Only peak speed matters once the index is low; acceleration and process rate can be ignored.','The speed discussion explicitly distinguishes peak speed from useful cycle performance.')],
 'The summary combines task-driven performance, configuration choices and quantitative metrics. No single index substitutes for a complete task-specific mechanism assessment.',typ='scenario',difficulty='medium')
# Code reasoning is algorithmic rather than generic recall.
for q in b.questions:
 if q['type']=='code':q['cognitiveSkill']='algorithm'
save()

add(547,'design','Physical mechanism and system parts',
 'Which grouping matches the four main robot-system parts listed in the lecture?',[
 ('Manipulator, end-effector, external sensors/effectors, and controller.','These are the four listed functional parts.'),
 ('Manipulator, end-effector, workspace volume, and payload rating.','Workspace and payload are attributes, not the external sensing/effecting and control components.'),
 ('Controller, repeatability, accuracy, and speed.','The last three are performance measures rather than system parts.'),
 ('Base, shoulder, elbow, and wrist only.','These name portions of a common manipulator rather than all four listed system-level parts.')],
 'The lecture separates the arm structure, task tool, external interaction/sensing equipment and controller. These should not be confused with performance requirements or subdivisions of the arm.',typ='definition',difficulty='easy')
add([550,562],'spherical-task','Spherical configuration and symmetric-tool task scope',
 'The spherical-configuration slide mentions symmetric-tool applications. Which interpretation avoids overstating the three positioning joints’ capability?',[
 ('Tool/task symmetry may reduce orientation requirements, but the two rotations and radial slide do not alone guarantee an arbitrary six-coordinate pose.','Reduced task requirements can make a positioning architecture suitable without granting it six independent freedoms.'),
 ('Any symmetric tool makes every desired orientation reachable with any three joints.','Symmetry removes only the requirements it actually makes irrelevant, not all reachability restrictions.'),
 ('Spherical workspace shape itself supplies three extra independent orientation freedoms.','The shape of a position set does not add mechanical DOF.'),
 ('A radial prismatic joint can independently set roll, pitch and yaw.','It changes radial extension rather than supplying three rotations.')],
 'The application remark must be matched to the actual tool and task. Symmetry can make some orientation coordinates unnecessary, but does not turn a three-DOF positioner into a general six-DOF pose mechanism.',typ='scenario',difficulty='medium',assumptions=['Discuss only the three positioning motions shown, without assuming an additional unmentioned orienting wrist.'])
add([568,570,572],'planar-singularity','Planar Jacobian determinant and radial boundaries',
 'Differentiate the stated planar 2R forward map for the two-coordinate position task. For positive l₁ and l₂, det(J)=l₁l₂sinθ₂. Which configurations are singular in the allowed interval θ₂∈[−π,π]?',[
 ('θ₂=0 and θ₂=±π, corresponding to straight and folded radial boundaries.','These are exactly the zeros of sinθ₂ in the interval.'),
 ('Only θ₁=0, regardless of θ₂.','The determinant is independent of the overall base rotation.'),
 ('Only θ₂=π/2, because the links are perpendicular.','sin(π/2)=1 gives nonzero determinant for positive link lengths.'),
 ('Every configuration, because a two-joint arm lacks six spatial-pose freedoms.','The selected task has two coordinates, so a 2×2 position Jacobian can have full rank.')],
 'For the selected planar position task, differentiating and expanding the determinant gives l₁l₂sinθ₂. Both the fully extended and fully folded positions lose one independent instantaneous position direction.',typ='derivation',difficulty='hard',steps=['Differentiate x and y with respect to θ₁ and θ₂ to form the 2×2 planar position Jacobian.','Expand its determinant; the l₂² terms cancel, leaving l₁l₂sinθ₂.','For positive lengths, rank loss occurs when sinθ₂=0: θ₂=0 or ±π within the stated range.','These correspond to r=l₁+l₂ and r=|l₁−l₂|.'],formulas=[FKFORM,RFORM,formula('det J=l₁l₂sinθ₂',{'J':'2×2 Jacobian of fixed-frame endpoint position (x,y) with respect to (θ₁,θ₂)','l₁,l₂':'positive planar link lengths','θ₂':'relative elbow angle'},{'J':'length per radian','det J':'length² per radian², with radians treated dimensionlessly in differentiation','l₁,l₂':'length','θ₂':'radians'},['Selected task is planar endpoint position only.'])],assumptions=['Ideal planar 2R chain, positive link lengths, fixed base, and a two-coordinate position task rather than full spatial pose.'])
# Tighten local conflict bindings: unaffected premise pages are not themselves labeled conflicts.
for number,pages in {8:[549],26:[560],27:[560],32:[561],42:[565],69:[572],70:[573]}.items():
 q=b.questions[number-1];q['conflictResolution']['physicalPages']=pages
 for c in q['citations']:
  c['role']='conflict' if c['physicalPage'] in pages else 'premise'
# Figure-specific evidence remains explicit about the cylindrical prose/diagram ordering.
q=b.questions[35]
q['conflictResolution']={'status':'explicit-qualification-awaiting-independent-review','sourceClaim':'The prose enumerates a vertical prismatic motion before a vertical-axis revolute motion, whereas the figure labels the azimuth θ₁ and the vertical displacement d₂.','basis':q['solution']['justification'],'method':'Test the actual figure labels explicitly; do not silently infer or reconcile a universal kinematic sequence from the prose order.','sourceId':'lectures','sourceSha256':SHA,'physicalPages':[563]}
q['citations'][0]['role']='conflict'
ISSUES.append((563,'The prose enumeration P,R,P and the figure labels θ₁,d₂,d₃ use different apparent ordering.','Use the explicit diagram labels or the motion types, and do not silently claim a universally numbered sequence.'))
# Exact algorithm reasoning steps are retained even for simple code items.
CODESTEPS={
70:['Identify an ordinary single-quoted string beginning before Articulated Robot.','Observe that its physical line ends before the closing quote.','Python cannot tokenize that short string across an unescaped newline, so parsing raises SyntaxError before execution.'],
72:['Enter one iteration of the outer loop and bind t1.','Run the inner loop over every t2 while that t1 stays fixed.','Recompute both endpoint coordinates for each pair.'],
73:['zip pairs one element from theta1 with the corresponding element from theta2.','Both arrays have 200 elements, so there are 200 pairs.','This differs from the 200×200 combinations of the nested loops.'],
74:['Observe that both inclusive angle arrays contain −π and π.','These endpoints give equivalent physical link orientations by trigonometric periodicity.','The code appends each evaluation and does not remove duplicates; distinctness cannot be inferred from list length.'],
78:['Separate figure dimensions, marker size and grid visibility from data-axis scaling.','Identify plt.axis(\'equal\') as the explicit equal-data-scale instruction.','Use equal scale to interpret circular and annular geometry without display stretching.']}
for number,steps in CODESTEPS.items():b.questions[number-1]['solution']['steps']=steps
# Remove the helper's second display rotation while retaining varied immutable option IDs.
for q in b.questions:q['options'].sort(key=lambda o:o['id'])
# Refresh source evidence for diagram questions with exact visual labels not reliably captured by text extraction.
VISUAL={2:'Visual transcription: the multi-link structure is labeled manipulator and the distal gripper is labeled end-effector.',20:'Visual transcription: side view has vertical arrow d₂ and horizontal arrow d₃; top view has arrow d₁ and a rectangular hatched workspace section.',23:'Visual transcription: side view has shoulder-elevation θ₂ and elbow θ₃ arcs; top view has base-azimuth θ₁ arc. The shoulder-elevation and elbow axes are parallel.',27:'Visual transcription: SCARA side view marks the vertical translation d₃; top view shows θ₁ and θ₂ angular arcs. This preserves the diagram label despite prose calling the prismatic joint fourth.',36:'Visual transcription: cylindrical side view shows vertical arrow d₂ and radial arrow d₃; top view shows the azimuth arc θ₁.',38:'Visual transcription: the wrist circle encloses θ₄, θ₅, θ₆, while the positioning arm carries θ₁, θ₂, θ₃.',41:'Visual transcription: three concentric input shafts are labeled A₄, A₅, A₆, and output motions θ₄, θ₅, θ₆. The caption explicitly identifies an orthogonal-axis wrist driven by remotely located actuators.'}
for number,txt in VISUAL.items():
 for c in b.questions[number-1]['citations']:c['evidenceText']=txt+'\n'+c['evidenceText']
save()

# Author quality pass: replace noncompetitive distractors with mechanism/modeling misconceptions.
def replace_option(number,old,new,rationale):
 q=b.questions[number-1];o=next(o for o in q['options'] if o['text']==old);o['text']=new;q['solution']['optionExplanations'][o['id']]=rationale
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']]
replace_option(2,'Manipulator: external camera; end-effector: controller cabinet.','Manipulator: only the first three positioning joints; end-effector: the orienting wrist joints.','The wrist remains part of the manipulator; the distal task tool is the end-effector.')
replace_option(10,'19 kg, because the two configurations contribute capacities additively.','12 kg after kinematic calibration, because calibration removes the effect of extension on load capacity.','Improving geometric parameter accuracy does not remove configuration-dependent leverage or structural limits.')
replace_option(24,'Articulated arms can reach around obstacles only by making all axes parallel.','A large outer workspace guarantees the required force and motion capability is uniform throughout it.','The text specifically calls for a well-conditioned workspace; outer reach alone does not establish uniform local capability.')
replace_option(25,'Confined access is impossible because all articulated workspaces are rectangular boxes.','Lower typical stiffness proves the articulated arm must have a smaller reachable volume for the same task.','Stiffness and workspace volume are different attributes; the stated stiffness comparison does not determine the reach-volume ordering.')
replace_option(29,'Adept One is described as a three-prismatic-axis gantry whose 30 ft/s speed is a payload rating.','Adept One is described as a geared Cartesian gantry introduced in 1984 with three mutually perpendicular linear axes.','The lecture identifies this example as a direct-drive SCARA, not the Cartesian PPP configuration.')
replace_option(30,'It converts all revolute joints into frictionless prismatic joints.','Base mounting alone guarantees equal acceleration at every payload and configuration.','Other moving masses, configuration-dependent inertia, available torque and transmissions still influence acceleration.')
replace_option(31,'Identical zero stiffness in all directions.','Uniform high stiffness in every direction, with no intentionally compliant plane.','The lecture emphasizes selective horizontal compliance rather than identical stiffness in all directions.')
replace_option(32,'A vertical revolute axis turns gravity into a horizontal force.','Vertical-axis bearings need no weight-load allowance, even though the motor must still overcome inertia.','Zero gravity torque about the rotation axis does not remove bearing forces or structural bending loads.')
replace_option(42,'Three actuators sharing one power supply, even when their axes are skew.','Three consecutive skew axes separated by nonzero common-normal distances.','Skew axes do not have the intersection geometry cited by the slide.')
replace_option(50,'As a universal lower bound on cycle time measured in seconds.','As an experimentally guaranteed index for every commercial articulated arm.','The slide explicitly describes an idealized benchmark and provides no universal commercial-robot guarantee.')
replace_option(50,'As proof that every real articulated installation is collision-free.','As proof that an articulated arm attaining it is also stiffer than any Cartesian arm.','Structural length per work volume does not by itself determine stiffness.')
replace_option(56,'It depends only on the robot’s color and external shape.','It uses only total link length and workspace volume, ignoring the mass distribution.','Those variables describe the structural length index; the inertia metric explicitly uses a mass matrix.')
replace_option(56,'It replaces the mass matrix by the total workspace volume.','It includes mass distribution but does not need the Jacobian or the evaluated configuration.','The stated Cartesian mass matrix includes J and M evaluated at the configuration.')
replace_option(74,'A scatter plot is restricted to displaying only 200 markers.','All evaluated configurations must lie on the outer circle because the link lengths sum to nine.','The elbow angle changes radial distance; the link-length sum specifies only the outer bound.')
# The rectangular example is a short Gram-product computation, not a long hard derivation.
b.questions[52]['difficulty']='medium'
# A direct caption interpretation is easy even though the underlying inertia theory is advanced.
b.questions[60]['difficulty']='easy'
# Human-readable page inspection notes and the author coverage ledger.
CLEAN_NOTES={
544:'Lecture 18 title, Mechanism Design I, with author/institution identification and a campus image.',
545:'Learning outcomes list task-driven design, DOF, workspace/load/speed/accuracy requirements, configurations, wrists, quantitative indices and Python workspace plotting.',
546:'Contents page organizes task requirements, configurations, quantitative workspace attributes and the programming example.',
547:'Physical design affects kinematic/dynamic complexity and closed-form solvability. Four system parts are listed. The drawing distinguishes the articulated manipulator from the distal end-effector.',
548:'Programmability does not imply universal task optimality. Heavy automotive welding and fast circuit assembly motivate different compromises. Joint count, arrangement, actuation and sensing are iterative decisions.',
549:'DOF is the number of independent configuration variables. Typical serial one-DOF joints are contrasted with closed-loop mobility criteria. The three-rotation drawing labels the base, middle and distal motions. The sentence calling every task mismatch redundant is overbroad.',
550:'General spatial pose has three position and three orientation coordinates. Task-relative redundancy is illustrated by an axially symmetric tool whose roll can be irrelevant; reachability and actual task symmetry remain necessary qualifications.',
551:'Workspace means reachable end-effector volume. Size, shape, singularities and structural/fixture interference matter. The three-dimensional point-cloud drawing is illustrative; its tiny cursor coordinates are not stated problem data.',
552:'Load depends on link strength/stiffness, transmission and actuator output, configuration and dynamics. Whole-workspace guaranteed capacity must be distinguished from the allowable load at a particular configuration.',
553:'Peak speed is not cycle time. Short pick-and-place moves can be acceleration/deceleration limited. Painting or welding can impose a process-limited useful travel rate.',
554:'Repeatability means returning consistently to a taught point; accuracy means reaching a mathematical target. Manufacturing tolerances and kinematic calibration matter. The 0.001-inch versus 8±2-inch spray example motivates task-appropriate precision and cost.',
555:'The common arm–wrist partition separates first-three-joint wrist positioning from the remaining orientation motions. Intersecting axes, zero dimensions and 0/±90-degree twists can simplify kinematics. The drawing highlights the arm and wrist portions.',
556:'Cartesian positioning uses three perpendicular prismatic axes, giving a rectangular/box workspace. The side view labels vertical travel d₂ and horizontal travel d₃; the top view shows d₁. The ideal independent positioning map has full rank. Stiff gantry construction suits heavy tasks.',
557:'Cartesian designs combine rigidity and payload capability with linear-actuator speed limits and simple position inverse kinematics. Fixtures/feeders must fit the surrounding structure; this can complicate retrofit. The singularity claim concerns the positioning substructure.',
558:'Articulated, jointed, elbow and anthropomorphic describe the arm arrangement. Shoulder yaw and elevation plus a parallel-axis elbow produce a complex nearly spherical envelope. The diagrams show curved restricted sectors. Boundary and internal alignments can be singular.',
559:'Typical cantilevered articulated structures are less stiff but less intrusive than Cartesian structures, aiding confined access. Cost and inverse-kinematics/control comparisons are design-dependent, not universal orderings.',
560:'SCARA is expanded as Selectively Compliant Assembly Robot Arm. Three parallel revolute motions and normal prismatic motion support planar assembly with height and yaw. Prose calls the prismatic joint fourth, while the figure labels d₃. The Adept One date, speed and priority statements are source-attributed historical examples, not verified universal benchmarks.',
561:'Base-mounted first-two actuators reduce moving mass. Vertical stiffness and horizontal compliance support assembly/insertion. Equal planar links are often chosen. The wording about joints not supporting weight must distinguish zero vertical-axis gravity torque from nonzero structural support loads.',
562:'Spherical positioning replaces the articulated elbow rotation with radial extension. The figure labels azimuth θ₁, elevation θ₂ and radial d₃, giving a shell/wedge region. Retraction can require rear clearance. Symmetric-tool suitability does not imply arbitrary spatial pose control.',
563:'Cylindrical positioning independently controls height, azimuth and radial reach. The figure labels θ₁, d₂ and d₃, while the prose enumerates the motions in a different order. Side and top sections are rectangular and annular-sector shaped. Vertical/radial material handling is the stated application.',
564:'The orienting wrist follows the positioning arm. The diagram places θ₄–θ₆ in the wrist. Conventional orthogonal-axis orientation reach assumes no joint limits, not absence of singularities. Non-orthogonal three-roll wrists can offer continuous joint rotation.',
565:'The non-orthogonal-wrist continuation describes an unattainable orientation cone. A separate picture is explicitly captioned as an orthogonal wrist remotely driven through three concentric shafts A₄–A₆. The broad intersecting-axis closed-form claim is retained only with explicit scope.',
566:'The structural length sum is Σ(a_(i−1)+d_i). The prismatic contribution is full travel, not the current coordinate. Numerical interpretations use nonnegative physical lengths; signed DH cancellation is not silently assumed.',
567:'The structural length index is L/W^(1/3), using positive three-dimensional workspace volume. Smaller ratios favor length efficiency only. Equal Cartesian travels give the ideal minimum 3.0; 0.62 is an ideal articulated benchmark, not a universal guarantee.',
568:'Task singularity is Jacobian rank loss. det(J)=0 applies to square J. Manipulability is √det(JJᵀ), reducing to |det J| for square J. Conditioning and directional uniformity are not fully described by the determinant product alone.',
569:'The inertia discussion attributed to Asada uses M_x=J^(−T)MJ^(−1), requiring square nonsingular J. The normalized quadratic form XᵀM_xX=1 gives an inertia metric ellipsoid. Equal principal values give isotropy. The figure displays changing local ellipse shapes and directions, not prescribed trajectories or universal actuator-limited acceleration bounds.',
570:'The programming problem specifies an ideal planar 2R arm with lengths 5 and 4 and both angles from −π to π. The fixed-frame FK uses θ₁ for the first link and θ₁+θ₂ for the second. No named physical length unit is supplied.',
571:'The diagram labels base-to-elbow length l₁, elbow-to-tool length l₂, base angle θ₁ and relative elbow angle θ₂. The equations substitute lengths 5 and 4 without changing the relative-angle convention.',
572:'The continuous ideal workspace is the annulus 1≤r≤9. The inner and outer bounds are the difference and sum of link lengths. The text describes plotted points as all positions; finite sampling must be distinguished from the continuous reachable set.',
573:'The actual code uses two inclusive 200-point linspaces, nested loops, and paired coordinate lists. It generates 40,000 evaluations. The even grid omits zero and includes periodically equivalent endpoints. The ordinary title string visually wraps across lines, requiring explicit repair for literal execution. Figure size, marker size, equal aspect, labels, grid and show have distinct roles.',
574:'The output has an inner hole of radius about 1, outer reach about 9, equal axis scale, and finite sampling rings/gaps. Red arrows indicate inner and outer radii. Blank regions between finite markers do not establish extra continuous-workspace obstacles.',
575:'The summary combines task-dependent requirements, configuration choice, structural and manipulability metrics, and FK workspace visualization. These are linked to the earlier concepts rather than padded with a duplicate summary quiz.',
576:'Bibliographic reference to Craig, third edition, 2005. No additional textbook material is supplied on this page.',
577:'Thank-you and closing branding only.'}
for p,note in CLEAN_NOTES.items():NOTES[p]=(note,NOTES[p][1])
save()

# Freeze only the author draft, never its verification status.
save(frozen=True)
packet=R/f'audits/blind-{BATCH}.json'
manifest={'batchId':BATCH,'authorId':AUTHOR,'frozenAt':'2026-10-19T17:56:30+00:00','questionCount':len(b.questions),'conceptCount':len(b.concepts),'physicalPages':list(NOTES),'sourceVersions':{'lectures':SHA},'blindPacketPath':str(packet.relative_to(R)),'blindPacketSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'questionHashConvention':'scripts.validate.question_hash; excludes only status and reviewIds','questions':[{'questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q)} for q in b.questions],'independentReviewStillRequired':True}
(R/f'audits/{BATCH}-frozen-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
coverage=[]
for p,(note,excluded) in NOTES.items():
 coverage.append({'physicalPage':p,'slideId':f'lectures-p{p:04d}','sourceSha256':SHA,'visualInspection':'complete','disposition':'excluded' if excluded else 'drafted-awaiting-independent-review','exclusionReason':excluded,'observedMeaningfulContent':note,'conceptIds':[c['id'] for c in b.concepts.values() if f'lectures-p{p:04d}' in c['slideIds']],'questionIds':[q['id'] for q in b.questions if any(c['physicalPage']==p for c in q['citations'])]})
assert all(row['exclusionReason'] or (row['conceptIds'] and row['questionIds']) for row in coverage)
(R/f'audits/{BATCH}-author-coverage-ledger.json').write_text(json.dumps({'batchId':BATCH,'status':'author coverage proposal, independent substantive challenge required','pageCount':len(coverage),'exclusions':sum(bool(x['exclusionReason']) for x in coverage),'pages':coverage},ensure_ascii=False,indent=2)+'\n')
assert all('correctOptionIds' not in q and 'solution' not in q and all('evidenceText' not in c for c in q['citations']) for q in json.loads(packet.read_text()))
print('FROZEN_PACKET_SHA256',manifest['blindPacketSha256'])
