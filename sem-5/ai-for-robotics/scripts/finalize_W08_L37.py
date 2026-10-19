"""One-time L37 pre-review quality pass, exact provenance and frozen packet."""
from pathlib import Path
import json,copy,hashlib,datetime,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W08-L37.json';b=json.loads(p.read_text());before={q['id']:question_hash(q)for q in b['questions']};by={q['tags'][0]:q for q in b['questions']}
def alternatives(key,pairs):
 q=by[key]
 for i,(text,why)in enumerate(pairs,2):
  next(o for o in q['options']if o['id']==f'o{i}')['text']=text;q['solution']['optionExplanations'][f'o{i}']=why
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][f'o{i}']for i in range(2,5)]
alternatives('feasible-objective',[
('Only the static clearance of the selected ray.','A ray can be clear even though the robot’s turning trajectory is not feasible.'),('Only whether the direction reduces straight-line goal distance.','Goal progress alone does not resolve the turning limit.'),('Only the length of the original route before the obstacle appeared.','The previous route length does not establish current dynamic feasibility.')])
alternatives('bug-variants',[
('Only their choice of left-side versus right-side following.','Side choice can matter, but variants also differ in leave rules and retained state.'),('Only whether they optimize Euclidean distance or travel time.','The key distinction here is sensing, memory and boundary-departure logic.'),('Only their grid resolution for the same global occupancy map.','The classical Bug variants do not require that shared grid formulation.')])
alternatives('completeness-optimality',[
('Completeness means every returned route has minimum Euclidean length.','That defines a path-quality claim, not path-existence success.'),('Optimality means a planner will terminate with some route whenever one exists.','That describes completeness rather than minimum cost.'),('A planner cannot be complete unless it is also shortest-path optimal.','A complete planner may return a valid but longer path.')])
alternatives('bug1-memory',[
('It needs only the current goal bearing and can discard the best point found so far.','That loses the comparison needed to select the closest boundary point.'),('It needs only the first hit point and no information about candidate leave points.','The hit point alone cannot identify the closest-to-goal boundary departure.'),('It must store a complete global occupancy grid before the first encounter.','Selected boundary memory is sufficient in the classical model; a prebuilt global grid is not required.')])
q=by['bug1-total-distance'];q['stem']='After surveying a boundary, Bug1 has two candidate points: A is 3 m from the goal and 8 m along the shorter return arc; B is 4 m from the goal and 2 m along its shorter return arc. Which leave point follows the stated rule?';vals=[('A, because it is closer to the goal','The leave-point criterion is goal distance; the shorter return arc is chosen only after selecting that point.'),('B, because its return arc is shorter','This minimizes return travel instead of selecting the closest-to-goal boundary point.'),('A and B tie because both have a shorter return arc','Each point’s shorter arc does not make their goal distances equal.'),('Neither, because the goal distance must be zero before departure','A leave point need not already be the goal.')]
for i,(text,why)in enumerate(vals,1):next(o for o in q['options']if o['id']==f'o{i}')['text']=text;q['solution']['optionExplanations'][f'o{i}']=why
q.update(type='scenario',cognitiveSkill='application',difficulty='medium',subtopic='Bug1 leave-point objective');q['solution'].update(justification=vals[0][1],simpleExplanation=vals[0][1],steps=['Compare goal distances: 3 m is less than 4 m.','Select A, then use A’s shorter 8 m boundary return.'],misconceptions=[x[1]for x in vals[1:]])
c=next(c for c in b['concepts']if c['id']==q['conceptIds'][0]);c.update(title=q['subtopic'],subtopic=q['subtopic'],description=vals[0][1],examinationAngles=['scenario'])
alternatives('bug1-inefficiency',[
('It must reject every departure that is not on the original start–goal line.','That is a Bug2-style restriction, not Bug1’s full survey.'),('It must leave at the first locally clear goal direction.','That is the Bug0 rule rather than Bug1’s survey requirement.'),('It must choose the boundary point with the smallest distance back to the hit point.','Bug1 selects the boundary point closest to the goal, then finds its return route.')])
alternatives('bug2-modes',[
('Global shortest-path search and map reconstruction','Those are not the two local motion modes stated for Bug2.'),('Full boundary survey and shortest boundary return','Those are stages associated with Bug1’s full-loop procedure.'),('Random exploration and reward-based policy improvement','Those belong to a learning formulation rather than the stated deterministic modes.')])
alternatives('noise-contact',[
('A complete stored map becomes necessary at every control cycle.','Noise sensitivity does not by itself impose that particular map architecture.'),('The fixed goal line is geometrically redefined by every noisy return.','The reference line is defined by the start and goal, not individual obstacle readings.'),('The ideal completeness proof automatically compensates for arbitrary measurement error.','The proof’s ideal sensing assumptions do not cover arbitrary noise.')])
alternatives('vfh-reductions',[
('Angular histogram → Cartesian certainty grid → selected steering direction','This reverses the first two reductions.'),('Cartesian certainty grid → one selected obstacle cell → the cell’s heading only','VFH aggregates directional evidence rather than simply choosing one cell.'),('Cartesian certainty grid → complete global shortest path → steering direction','The described local histogram stage is not a complete global path search.')])
alternatives('polar-loss',[
('The nearest obstacle’s range as a function of elapsed time','This replaces the angular variable and density aggregation with a different signal.'),('A complete sequence of future collision-free configurations','The histogram is a local directional summary, not a trajectory.'),('The exact Cartesian coordinates of every sensor return without aggregation','The representation reduces information by direction.')])
alternatives('grid-figure',[
('Locations with stronger confidence that the cell is free','This reverses the displayed occupancy legend.'),('Locations nearer the global goal regardless of obstacle evidence','The shading encodes occupancy, not goal distance.'),('Locations visited more often by the planned path, independent of sensing','The legend describes occupancy confidence, not route visitation.')])
alternatives('histogram-figure',[
('Low obstacle density and a preferred free opening directly ahead','This reverses the meaning of a high peak.'),('A precise obstacle range encoded directly by the horizontal 0° label','The horizontal coordinate is angle, not range.'),('A record of the previous steering command’s frequency at 0°','The plotted quantity is obstacle density rather than a histogram of past commands.')])
alternatives('threshold-equality',[
('Assume equality is free because only strict excess can indicate a collision in every sensor model','The lecture has not supplied such a universal rule.'),('Assume equality is blocked while claiming the slide explicitly states that convention','A conservative choice can be specified, but it must not be falsely attributed.'),('Allow the result to depend on iteration order without documenting it','That creates an unstated boundary behavior.')])
alternatives('smoothing-weight',[
('Moving closer to the goal bearing regardless of the previous selected direction','That is principally the role of the goal-error weight a.'),('Moving closer to the present heading regardless of the last command','That is principally the current-heading term weighted by b.'),('Making previously masked directions feasible by changing the ranking','Changing objective weights does not change a hard feasibility mask.')])
alternatives('vfh-width-qualification',[
('Original VFH explicitly inflated obstacles by the same radius-plus-margin rule described for VFH+','The 1998 comparison distinguishes empirical smoothing from explicit enlargement.'),('VFH+ ignores robot width and changes only the goal-error weight','It explicitly improves width handling as well as other stages.'),('Width compensation alone makes every turning trajectory dynamically feasible','Turning-path feasibility is an additional concern.')])
alternatives('vfhstar-lookahead',[
('VFH+ and VFH* both use the same multi-step A* look-ahead, with no algorithmic distinction','The papers distinguish VFH*’s projection search from VFH+’s local choice.'),('VFH* replaces obstacle sensing with a guarantee based only on the target bearing','The search still uses the available obstacle representation.'),('Original VFH already performed the same projected search, and VFH+ only removed it','That is not the development described by the primary papers.')])
alternatives('forward-kinematics-direction',[
('Desired end-effector pose → candidate joint configurations','That is inverse kinematics.'),('Joint torques and initial state → acceleration or motion over time','That is a dynamics problem rather than geometric forward kinematics.'),('End-effector force → corresponding generalized joint torques','That is a force-transformation or statics relation rather than the forward-pose mapping.')])
alternatives('rl-action-spaces',[
('Mobile robot: state estimates only; manipulator: reward values only','States and rewards are not the stated control actions.'),('Both systems: an identical scalar steering angle regardless of mechanism','The action space must reflect each robot’s controls.'),('Mobile robot: goal coordinates only; manipulator: collision labels only','Those describe targets or observations rather than the example control commands.')])
# Direct recall and one-step classifications should not be labelled medium merely to inflate difficulty.
for key in ['bug0-memory','bug1-memory','bug1-inefficiency','bug2-memory-qualification','kinematics-dynamics','cost-terms','smoothing-weight','whole-arm','self-collision','workspace-vs-cspace','cspace-obstacles','forward-kinematics-direction','potential-force','virtual-not-physical','attraction-numeric','dynamic-cspace','rl-policy','reward-design','learned-perception']:
 by[key]['difficulty']='easy'
# Exact source types and locators: numerical questions use supplied examples derived from prose, not nonexistent slide equations.
figures={'detour-figure':(1139,'Red detour around a cylindrical obstacle, rejoining a dashed desired path.'),'bug1-hit-leave-figure':(1143,'Boundary path with H1/L1 and H2/L2 hit and leave markers.'),'grid-figure':(1149,'Grayscale occupancy-grid illustration; legend Light = Free and Dark = Likely occupied.'),'histogram-figure':(1150,'Polar histogram with horizontal angles approximately −180° through +180°, density P vertically, a high central peak and threshold line.'),'angle-diagram-error':(1152,'Angle compass at right: 0° rightward, 90° upward; lower-right diagonal is erroneously labelled 45°.'),'cspace-obstacles':(1156,'Workspace-to-C-space illustration with θ1 and θ2 axes, shaded forbidden regions and a red configuration point.')}
for q in b['questions']:
 key=q['tags'][0]
 for c in q['citations']:
  page=c['physicalPage'];c['kind']='statement';c['locator']=f'Lecture 37, physical page {page}, printed slide {page-1126}: prose under the displayed section heading; application assumptions are stated in the question.'
  if key in figures:
   c.update(kind='figure',locator=f'Physical page {page}, printed slide {page-1126}: {figures[key][1]}');c['evidenceText']+='\nManual visual observation: '+figures[key][1]
  elif page==1152:
   c['kind']='equation';c['locator']='Physical page 1152, printed slide 26: weighted sum of target, current-heading and previous-direction angular differences, with weight effects.'
  if q['type'] in ['numerical','derivation','scenario'] and not q.get('conflictResolution'):c['role']='premise'
 if key in ['quadratic-attraction','attraction-numeric','sum-fields','grid-explosion','joint-addition-cost']:
  q['notes']='This is an explicitly specified application or derivation of the cited source concept, not a claim that the worked formula or numbers are printed on the slide.'
# Item-level primary evidence for qualifications that require more than the supplied slide.
refs={
 'bug':{'title':'Lumelsky and Stepanov, Path-planning strategies for a point mobile automaton (1987)','url':'https://robotics.caltech.edu/~jwb/courses/ME132/handouts/LumelskyBug.pdf','locator':'Section 2 model; Sections 4 and 5, Bug1/Bug2 procedures and assumptions.'},
 'vfh':{'title':'Borenstein and Koren, The Vector Field Histogram (1991)','url':'https://www.valentiniweb.com/piermo/robotica/doc/Borenstein/paper16.pdf','locator':'Sections 3.1 and 4: accumulated certainty counts, histogram reduction and steering.'},
 'plus':{'title':'Ulrich and Borenstein, VFH+: Reliable Obstacle Avoidance (1998)','url':'https://www.cs.cmu.edu/~iwan/papers/vfh%2B.pdf','locator':'Sections 2.1–2.4: width enlargement, hysteresis, trajectory masking and angular cost; conclusion identifies remaining local limitation.'},
 'star':{'title':'Ulrich and Borenstein, VFH*: Local Obstacle Avoidance with Look-Ahead Verification (2000)','url':'https://www.cs.cmu.edu/~iwan/papers/vfhstar.pdf','locator':'Sections 2–4: VFH+ versus multi-step projection using A*; Section 6 contrasts drive configurations.'},
 'cspace':{'title':'Lynch and Park, Modern Robotics 10.2.1: C-Space Obstacles','url':'https://modernrobotics.northwestern.edu/nu-gm-book-resource/10-2-c-space-obstacles/','locator':'Author transcript: forbidden configurations, whole-geometry collision detection and connected free space.'},
 'potential':{'title':'Lynch and Park, Modern Robotics 10.6: Virtual Potential Fields','url':'https://modernrobotics.northwestern.edu/nu-gm-book-resource/10-6-virtual-potential-fields/','locator':'Author transcript: negative gradient, quadratic attraction, force summation, saddle points and local minima.'},
 'fk':{'title':'Lynch and Park, Modern Robotics Chapter 4: Forward Kinematics','url':'https://modernrobotics.northwestern.edu/chapters/chapter4/','locator':'Forward kinematics of an open chain from its joint coordinates.'}}
maprefs={'bug1-assumptions':['bug'],'bug2-memory-qualification':['bug'],'bug2-efficiency':['bug'],'completeness-comparison':['bug','plus'],'vfh-reactive-statistical':['vfh'],'certainty-values':['vfh'],'wide-valley':['plus'],'vfh-width-qualification':['plus'],'vfhstar-lookahead':['plus','star'],'turning-radius-drive':['star'],'speed-feasibility':['plus'],'cost-terms':['plus'],'wrapped-angle':['plus'],'weight-scaling':['plus'],'cspace-obstacles':['cspace'],'forward-kinematics-direction':['fk'],'cspace-collision-construction':['cspace'],'path-in-cspace':['cspace'],'potential-force':['potential'],'quadratic-attraction':['potential'],'sum-fields':['potential'],'stationary-versus-minimum':['potential']}
for key,ids in maprefs.items():
 q=by[key];q['primaryEvidence']=[dict(refs[i],accessedAt='2026-10-19T20:29:25Z')for i in ids]
 note=' Primary cross-check: '+'; '.join(refs[i]['url']+' ('+refs[i]['locator']+')'for i in ids)
 q['notes']=q.get('notes','')+note
 if q.get('conflictResolution'):q['conflictResolution']['basis']+=note
for q in b['questions']:
 if q.get('conflictResolution'):q['conflictResolution']['method']='Compare the exact supplied prose or visual label with the item’s explicit mathematical reasoning and, where listed, the primary reference; retain the original source without silently changing it.'
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in b['questions']:
 a={k:copy.deepcopy(q[k])for k in('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in a['citations']:c.pop('evidenceText',None)
 packet.append(a)
pa=R/'audits/blind-W08-L37.json';pa.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
manifest={'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'questionCount':len(b['questions']),'questionHashes':{q['id']:question_hash(q)for q in b['questions']},'blindPacketSha256':hashlib.sha256(pa.read_bytes()).hexdigest(),'batchSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'existingBatchUnchanged':'search-foundations.json was not edited; all 29 existing L37 and 39 L36 objects remain intact.','note':'All 38 L37 pages visually inspected; completion questions cover missing p1138–1162. Independent full-lecture completeness challenge remains required.'}
(R/'audits/W08-L37-frozen-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(R/'audits/W08-L37-source-qualifications.json').write_text(json.dumps({'primaryReferences':refs,'qualifications':[{'questionId':q['id'],**q['conflictResolution']}for q in b['questions']if q.get('conflictResolution')],'preReviewChangedIds':[q['id']for q in b['questions']if before[q['id']]!=question_hash(q)]},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'frozen':True,'questions':len(b['questions']),'packetSha256':manifest['blindPacketSha256']}))
