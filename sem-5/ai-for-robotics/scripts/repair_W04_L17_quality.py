"""One-time independent-review repairs; preserve unchanged reviewed hashes."""
from pathlib import Path
import json,copy,datetime,hashlib
from validate import question_hash
from authoring_helpers import SHA,formula
R=Path(__file__).resolve().parents[1];path=R/'data/question-batches/W04-L17.json';b=json.loads(path.read_text());old=copy.deepcopy(b)
a=R/'audits/batch-history/W04-L17-before-quality-repairs.json'
if a.exists():assert json.loads(a.read_text())==old,'Already applied or changed; do not overwrite reviewed work.'
else:a.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
summary=json.loads((R/'audits/W04-L17-v1-independent-summary.json').read_text())
flagged={r['questionId'] for r in summary['flaggedQuestions']};changed=flagged|{'W04-L17-Q022'};qs={int(q['id'][-3:]):q for q in b['questions']}
for q in b['questions']:
 if q['id'] not in changed:continue
 h=question_hash(q);q['version']+=1;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append('robotics-integration-L17-quality-revision')
 q.setdefault('revisionHistory',[]).append({'version':q['version'],'authorId':'robotics-integration-L17-quality-revision','priorQuestionSha256':h,'reason':'Independent quality flags and three source-angle gap closures.','revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
for r in summary['flaggedQuestions']:
 if any(x.startswith('Difficulty:') for x in r['findings']):qs[int(r['questionId'][-3:])]['difficulty']='easy'
def setq(n,stem,opts,why,exps):
 q=qs[n];q['stem']=stem
 for o in q['options']:o['text']=opts[int(o['id'][1:])-1]
 q['correctOptionIds']=['o1'];q['selectionMode']='single';q['solution']['justification']=why;q['solution']['simpleExplanation']=why;q['solution']['optionExplanations']={f'o{i+1}':e for i,e in enumerate(exps)};q['solution']['misconceptions']=exps[1:]
def cite(n,page,kind='statement'):
 q=qs[n]
 if any(c['physicalPage']==page for c in q['citations']):return
 q['citations'].append(dict(slideId=f'lectures-p{page:04d}',sourceId='lectures',sourceSha256=SHA,physicalPage=page,kind=kind,locator=f'Lecture 17, physical PDF page {page}, printed slide {page-504}: relevant runtime or programming statement',evidenceText=(R/f'sources/text/lectures/page-{page:04d}.txt').read_text().strip(),role='explicit',region=None))
def concept(n,key,title,description,pages):
 cid=f'W04-L17-C-{key}';qs[n]['conceptIds'].append(cid);b['concepts'].append(dict(id=cid,title=title,description=description,slideIds=[f'lectures-p{p:04d}' for p in pages],questionIds=[qs[n]['id']],status='drafted',topic=b['concepts'][0]['topic'],subtopic=title,prerequisiteConceptIds=[],examinationAngles=['scenario']))
setq(3,'In the introductory XYZ diagram, which interpretation matches the ordered intermediate frame markers between START and END?',[
 'Specified via poses along the tool path, including intermediate position and orientation',
 'Alternative final tool poses, any one of which replaces END as the goal',
 'Position-only samples whose frame-axis orientations impose no pose information',
 'Tolerance bounds around a single endpoint rather than intermediate path specifications'],
 'The intermediate frame markers specify via poses along the motion, rather than alternative goals, scalar positions alone or endpoint tolerance limits.',[
 'The position and axes together represent the intermediate tool poses.',
 'The sequence lies between the specified START and END rather than replacing END.',
 'The frame axes carry orientation information as well as the origins carrying position.',
 'The markers are distributed along the desired path, not drawn as one endpoint tolerance boundary.'])
setq(4,'Which pose relation is stated for describing the tool trajectory in this lecture?',[
 'The tool frame expressed relative to the station frame',
 'The station frame expressed relative to the tool frame',
 'The tool frame expressed relative to its wrist attachment frame',
 'The tool frame expressed relative to a camera frame'],
 'The stated trajectory is the tool pose relative to the station; reversing that relation or using another reference changes the represented transform.',[
 'This is the specified task-space pose relation.',
 'This is the inverse relation, not the one stated.',
 'This describes a tool attachment relation rather than the stated station-referenced motion.',
 'A camera-referenced pose is a different relation not selected in this description.'])
setq(5,'In the source-described runtime-IK workflow, how are Cartesian pose samples converted into joint configurations?',[
 'Interpolate a desired Cartesian pose at each update, then solve inverse kinematics for that pose',
 'Solve inverse kinematics for every time sample before execution, then only replay the stored joint table',
 'Interpolate a desired Cartesian pose at each update, then apply forward kinematics to obtain its joints',
 'Interpolate only joint endpoints at each update, then apply forward kinematics to prescribe a straight tool line'],
 'The described workflow performs pose interpolation followed by inverse kinematics during execution; other planning architectures are possible but are not this stated sequence.',[
 'This gives the source runtime conversion sequence.',
 'This is a plausible fully precomputed alternative, not the source-described runtime solve.',
 'Forward kinematics maps joints to pose, not pose to joints.',
 'Joint interpolation followed by forward kinematics does not itself prescribe a straight Cartesian path.'])
setq(6,'Relative to direct evaluation of a precomputed joint polynomial, which added operation explains the source runtime-IK workflow’s extra work?',[
 'Solving inverse kinematics for each newly interpolated Cartesian pose',
 'Reading the current segment clock before evaluating the interpolation',
 'Evaluating the planned interpolation polynomial at the current time',
 'Advancing the control update counter and checking the segment end'],
 'The extra pose-to-joint solve is specific to the described Cartesian runtime workflow; clock handling, interpolation and segment bookkeeping can occur in either scheme.',[
 'This is the additional conversion highlighted by the source.',
 'A joint-polynomial generator also needs current time.',
 'Direct joint trajectory evaluation also performs interpolation arithmetic.',
 'Both implementations can require this update and segment bookkeeping.'])
setq(9,'Which position/orientation representation matches the stated six-component vector χ=[p;K]?',[
 'Three Cartesian position coordinates and a three-component orientation parameterization',
 'Three Cartesian position coordinates and a four-component unit quaternion',
 'Three Cartesian position coordinates and all nine entries of a rotation matrix',
 'Two planar position coordinates and one planar orientation angle'],
 'The stated vector uses three translation entries plus three orientation parameters; other common pose representations have different entry counts.',[
 'This gives the specified three-plus-three arrangement.',
 'A quaternion-based pose has seven stored scalar entries, even though the quaternion has a constraint.',
 'Storing the full matrix plus position uses twelve entries; matrix entries are constrained and not nine independent rotation freedoms.',
 'This is a three-component planar pose, not the stated spatial six-vector.'])
setq(10,'To resolve the slide’s ROT notation explicitly, adopt the three-component rotation vector K=θk with unit axis k and θ in radians; which K represents a +90° rotation about the z-axis?',[
 '(0,0,π/2)',
 '(0,0,1)',
 '(0,π/2,0)',
 '(0,0,90)'],
 'The angle is π/2 radians and the unit axis is (0,0,1), so K=(0,0,π/2); this vector is a parameterization, not the full rotation matrix.',[
 'This multiplies the correct axis by the angle in the declared unit.',
 'This stores only the unit axis and omits the 90° magnitude.',
 'This places the rotation about y rather than z.',
 'This uses degrees despite the explicit radian convention.'])
qs[10]['difficulty']='easy';qs[10]['assumptions']=['This question explicitly defines ROT’s three-parameter interpretation as K=θk; it does not silently identify a 3×3 matrix with a vector.']
qs[10]['solution']['steps']=['Convert 90° to π/2 rad.','Multiply (0,0,1) by π/2.'];qs[10]['solution']['formulas']=[formula('K=θk',{'K':'rotation vector','θ':'rotation angle','k':'unit rotation axis'},{'K,θ':'rad','k':'dimensionless'})]
setq(18,'For a one-unit straight task move with constant J=diag(1,0.01), no first-component motion and |qdot2|≤10, what is the fastest constant second-component speed and its travel time, compared with an intended one-second move?',[
 'Speed 0.1 and travel time 10 s; the geometric move is retained but its intended timing is slowed',
 'Speed 0.1 and travel time 1 s; reducing speed does not affect the scheduled arrival',
 'Speed 1 and travel time 1 s; the joint-rate limit remains satisfied',
 'Speed 0.01 and travel time 100 s; this is the fastest permitted motion'],
 'The task-rate bound is 0.01×10=0.1 units/s, so a one-unit move requires at least 10 s under the given constant-speed model; slowing preserves the path but changes its temporal specification.',[
 'This satisfies the rate limit and accounts for the required timing change.',
 'A one-unit displacement at 0.1 units/s cannot finish in one second.',
 'A task rate of 1 would require qdot2=100, exceeding the limit.',
 'This is feasible but unnecessarily ten times slower than the maximum permitted speed.'])
qs[18]['difficulty']='medium';qs[18]['assumptions']=['This is a hypothetical locally scaled example with the displayed diagonal Jacobian assumed constant over the move.','Task units are consistently scaled, joint2 rate units match the bound, and endpoint acceleration transitions are excluded.','Slowing a feasible direction does not make an infeasible direction attainable at an exact singularity.'];qs[18]['solution']['steps']=['Compute the allowed task speed 0.01×10=0.1 units/s.','Compute time=distance/speed=1/0.1=10 s.','Compare with the intended 1 s and retain the source caveat about changed temporal attributes.'];qs[18]['solution']['formulas']=[formula('xdot_2=0.01 qdot_2; T=Δx_2/|xdot_2|',{'xdot_2':'second task speed','qdot_2':'second joint rate','T':'move duration','Δx_2':'task displacement'},{'xdot_2':'scaled task units/s','qdot_2':'scaled joint units/s','T':'s','Δx_2':'scaled task units'})]
concept(18,'time-scaling-tradeoff','Rate-limit timing trade-off','Reducing speed can preserve a feasible geometric path while changing the requested timing; it does not solve unreachable singular directions.',[514])
setq(20,'Which three joint references does the source trajectory generator provide at successive updates?',[
 'Joint position, joint velocity and joint acceleration',
 'Joint position, joint velocity and joint torque',
 'Joint position, joint acceleration and joint jerk',
 'Joint velocity, joint acceleration and joint torque'],
 'The source lists position and its first two time derivatives; torque belongs to dynamic control rather than this stated trajectory-output triple.',[
 'This is the listed reference set.',
 'This substitutes torque for the listed acceleration reference.',
 'This substitutes jerk for the listed velocity reference.',
 'This omits position and substitutes torque.'])
setq(22,'An LSPB segment starts at global time 5 s, lasts 2 s and uses blend duration 0.3 s at each end; at global times 5.2, 6.0 and 6.8 s, which local times and regions should the runtime selector use?',[
 'Local times 0.2,1.0,1.8 s: initial blend, linear region, final blend',
 'Local times 5.2,6.0,6.8 s: final blend at all three updates',
 'Local times 0.2,1.0,1.8 s: linear region, initial blend, final blend',
 'Local times 0.2,1.0,1.8 s: initial blend, final blend, linear region'],
 'Subtract the segment start time, then compare elapsed time with t_b=0.3 and t_f−t_b=1.7; the three samples fall in the initial blend, middle line and final blend.',[
 'This applies both the local-clock reset and the two region thresholds.',
 'This fails to reset the elapsed clock at the segment start.',
 'The first sample precedes 0.3 s and the middle sample lies between 0.3 and 1.7 s.',
 'The middle sample is below 1.7 s, while the last sample is above it.'])
qs[22]['difficulty']='medium';qs[22]['type']='scenario';qs[22]['cognitiveSkill']='application';qs[22]['assumptions']=['Use the stated hypothetical symmetric LSPB timing; no sample lies exactly at a boundary.','This selection test does not silently correct the source’s separate blend-position/velocity inconsistency.'];qs[22]['solution']['steps']=['Subtract 5 s to obtain 0.2,1.0,1.8 s.','Use first boundary 0.3 s and second boundary 2−0.3=1.7 s.','Select blend, line and blend respectively.'];qs[22]['solution']['formulas']=[formula('t_local=t_global−t_start; t_second=t_f−t_b',{'t_local':'elapsed segment time','t_global':'global clock','t_start':'segment start','t_second':'start of final blend','t_f':'segment duration','t_b':'blend duration'},{'all times':'s'})];cite(22,518,'equation');cite(22,520,'figure')
concept(22,'runtime-region-selection','Choose the active linear or blend equation','At each update, compare elapsed segment time against blend boundaries before evaluating the appropriate regional law.',[517,518,520])
setq(28,'For a fixed planned LSPB segment, which planning/runtime allocation is correct?',[
 'Plan durations, slopes and blend coefficients; update elapsed time and select the active region during execution',
 'Plan elapsed time and active region once; recalculate segment durations and all coefficients on every clock tick',
 'Plan only the final pose; derive all segment slopes and blend coefficients from the current measured acceleration at every update',
 'Plan durations and freeze the first region selection; update elapsed time but keep using that initial regional equation'],
 'The planned parameters can be reused, but the clock and corresponding region change as motion advances.',[
 'This separates fixed trajectory parameters from runtime evaluation variables.',
 'Elapsed time and region cannot remain fixed while the segment is executed.',
 'This is not the source’s preplanned coefficient-evaluation scheme.',
 'Using only the initial region would miss the transitions between blend and line.'])
setq(34,'For MOVE ARM TO C VIA B with specified speed and smoothness attributes, which interpretation and software sequence match the lecture?',[
 'B is an intermediate pose before C; the programming system interprets the motion attributes and invokes the path generator',
 'C is an intermediate pose before B; the programming system interprets the motion attributes and invokes the path generator',
 'B and C are alternative final poses; the path generator chooses one without preserving an ordered via sequence',
 'B is an intermediate pose before C; the programming system discards speed and smoothness because those attributes never affect generated trajectories'],
 'The user supplies an ordered via sequence plus motion attributes; the programming system interprets it and invokes trajectory generation, with B preceding final pose C.',[
 'This preserves waypoint order, attributes and interpreter-to-generator roles.',
 'This reverses the VIA and TO roles.',
 'The command describes an ordered path, not a choice between alternative final poses.',
 'The source explicitly includes speed and smoothness as motion attributes.'])
concept(34,'language-attributes-pipeline','Interpret motion attributes before trajectory generation','The robot programming system interprets the user’s via sequence, speed and smoothness and invokes the path generator.',[522])
setq(38,'A path has one region with a low feasible acceleration and another with a much higher feasible acceleration; what trade-off can follow from imposing the lower bound throughout?',[
 'It can respect the limiting region while underusing acceleration capability and increasing travel time elsewhere',
 'It necessarily gives the shortest travel time because both regions use one common value',
 'It removes the physical configuration dependence of the robot’s available acceleration',
 'It automatically increases the bound in the easier region without needing any timing adaptation'],
 'A single conservative bound may be safe with respect to the modeled limit but does not exploit easier configurations as an adaptive dynamics-aware timing plan could.',[
 'This is the conservative-bound trade-off described.',
 'Using a common conservative value does not establish time optimality.',
 'A planning bound does not change the robot’s configuration-dependent dynamics.',
 'A fixed global bound is not automatically adapted to local capability.'])
setq(40,'Which model set supplies the geometric information required by the source collision-free planning description?',[
 'Manipulator geometry and configurations, workspace geometry, and obstacle geometry',
 'Tool-point positions, workspace geometry, and obstacle geometry, with no model of the robot links',
 'Manipulator geometry and configurations, joint actuator limits, and no obstacle geometry',
 'Manipulator geometry and configurations, workspace dimensions, and only the final target pose instead of obstacle locations'],
 'Collision checking must relate the robot’s occupied geometry to the workspace and obstacles; neither a tool point alone nor actuator limits or a goal alone replace those geometric models.',[
 'This includes all three stated geometric model categories.',
 'A clear tool point does not guarantee that the robot links avoid obstacles.',
 'Actuator limits do not identify occupied obstacle regions.',
 'A target pose does not specify the obstacles along a path.'])
setq(41,'Which pairing matches the two planning approaches described by the source?',[
 'Free-space graph: search connectivity between feasible regions; potential field: follow goal attraction combined with obstacle repulsion',
 'Free-space graph: choose the spatially closest region without checking graph edges; potential field: follow goal attraction combined with obstacle repulsion',
 'Free-space graph: search connectivity between feasible regions; potential field: descend a goal-distance field with no obstacle contribution',
 'Free-space graph: interpolate one direct edge between endpoints without checking intermediate free space; potential field: globally enumerate every graph path before moving'],
 'The graph method uses feasible connectivity, while the artificial-field method combines an attractive goal effect with repulsive obstacle effects.',[
 'Both mechanisms match the source.',
 'Graph reachability depends on feasible edges, not only spatial closeness.',
 'Removing obstacle effects loses the stated potential-field obstacle avoidance mechanism.',
 'This substitutes unchecked direct interpolation and exhaustive graph enumeration for the stated methods.'])
setq(42,'Away from the goal, attractive and repulsive artificial forces cancel and the local descent direction vanishes; what can happen?',[
 'The planner can stall at a local minimum rather than reach the goal',
 'The zero net force guarantees that the next update will pass through the stationary point toward the goal',
 'Every stationary point must be the global goal because attraction is included in the field',
 'The local cancellation certifies that the path taken so far is globally shortest'],
 'A local stationary point can trap a basic descent-based potential-field planner; zero net artificial force alone is not a goal or optimality certificate.',[
 'This is the source-listed local-minimum failure mode.',
 'Without an escape mechanism, a zero descent direction does not guarantee progress.',
 'Attraction and repulsion can cancel away from the global goal.',
 'A local force balance does not prove shortest-path optimality.'])
q=qs[46];q['solution']['optionExplanations']['o4']='This both omits the initial position and reverses the x-displacement sign: the actual displacement at 2 s is (−0.200 m,−0.300 m,30°), not the offered (+0.200 m,−0.300 m,30°).';q['solution']['misconceptions']=[q['solution']['optionExplanations'][o] for o in ['o2','o3','o4']]
q=qs[56];q['solution']['steps']=['Use zero-based t[7]=7×0.2=1.4 s.','Compute x=0.7−0.1×1.4=0.560 m.','Compute y=0.2−0.15×1.4=−0.010 m.','Compute φ=15×1.4=21.0°.','Apply .1f to time/orientation and .3f to x/y.'];q['solution']['formulas']=[formula('t_i=0.2i; x=0.7−0.1t; y=0.2−0.15t; φ=15t',{'i':'zero-based sample index','t,t_i':'elapsed sample time','x,y':'Cartesian positions','φ':'planar tool orientation'},{'i':'dimensionless','t,t_i':'s','x,y':'m','φ':'degrees'})]
setq(57,'Which precision assignment does the printed Python f-string apply to t, x, y and φ?',[
 't: one decimal; x,y: three decimals; φ: one decimal',
 't: three decimals; x,y: one decimal; φ: three decimals',
 't: one decimal; x,y: one decimal; φ: three decimals',
 't: three decimals; x,y: three decimals; φ: one decimal'],
 'The displayed format specifiers use .1f for t and φ and .3f for x and y.',[
 'This matches all four printed format choices.',
 'This exchanges the time/orientation precision with the position precision.',
 'This gives the position and orientation fields the wrong precision.',
 'This changes only the time field from the printed .1f to .3f.'])
setq(62,'The plot labels orientation θ while the code calls it φ; without a specified robot and inverse-kinematics solution, which interpretation is justified?',[
 'The angle is the planar task orientation; no specific joint-angle history is established',
 'The angle is necessarily joint 1’s angle, regardless of the mechanism',
 'The angle is necessarily the direction of the XY path tangent rather than the tool orientation',
 'The angle is necessarily every joint’s common rotation, so each joint turns at 15°/s'],
 'The example prescribes task orientation independently of the translational path; a label change does not identify a robot joint or solve inverse kinematics.',[
 'This retains the task/joint distinction supported by the source.',
 'A mechanism-specific kinematic relation is needed to identify an individual joint.',
 'The source’s tool orientation can differ from the direction of travel.',
 'A task orientation rate does not assign the same rate to every joint.'])
# Give touched citations narrower locators without changing accepted question hashes.
locators={3:'introductory START/via-pose/END XYZ figure',4:'tool-relative-to-station pose description',5:'runtime inverse-kinematics and path-update description',6:'additional runtime inverse-kinematics operation',9:'six-component pose vector χ=[p;K]',10:'ROT(k,θ) notation inside the six-component pose vector',18:'joint-rate limitation and changed temporal attributes under slowing',20:'successive position, velocity and acceleration trajectory outputs',22:'local-clock reset and elapsed-time choice of linear or blend region',28:'preplanned coefficients and runtime trajectory evaluation',34:'via sequence, speed/smoothness attributes, interpreter and path generator',38:'conservative acceleration bound and unused speed capability',40:'manipulator/workspace/obstacle model requirement',41:'free-space graph and attractive/repulsive potential-field mechanisms',42:'potential-field local minimum limitation',46:'worked x/y/orientation values at the temporal midpoint',56:'0.2 s array, formatting loop and index-seven printed row',57:'.1f and .3f field-format specifiers',62:'task-orientation labels and tool-axis arrows'}
for n,desc in locators.items():
 if qs[n]['id'] in changed:
  for c in qs[n]['citations']:c['locator']=f"Lecture 17, physical PDF page {c['physicalPage']}, printed slide {c['physicalPage']-504}: {desc}"
unchanged=[q for q in b['questions'] if q['id'] not in changed];oldmap={q['id']:q for q in old['questions']}
assert all(question_hash(q)==question_hash(oldmap[q['id']]) for q in unchanged)
path.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in b['questions']:
 if q['id'] not in changed:continue
 z={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in z['citations']:c.pop('evidenceText',None)
 packet.append(z)
p=R/'audits/blind-W04-L17-quality-repairs.json';p.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
manifest={'changedQuestions':len(changed),'unchangedAcceptedHashes':len(unchanged),'questionIds':sorted(changed),'packetPath':str(p.relative_to(R)),'packetSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'gapClosures':{'runtime-region-selection':'W04-L17-Q022','time-scaling-tradeoff':'W04-L17-Q018','language-attributes-pipeline':'W04-L17-Q034'},'questionHashes':{q['id']:question_hash(q) for q in b['questions']},'independentReview':'pending'}
(R/'audits/W04-L17-quality-repair-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:manifest[k] for k in ('changedQuestions','unchangedAcceptedHashes','packetSha256')},indent=2))
