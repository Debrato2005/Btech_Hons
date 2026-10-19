#!/usr/bin/env python3
"""Nonduplicative L36 completeness gap authoring. Never edits accepted search-foundations."""
import json,hashlib,copy,sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];B='W08-L36-COVERAGE-GAP';A='L36-gap-author-20261019';S='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
if (R/f'audits/{B}-review-manifest.json').exists():raise SystemExit('L36 gap packet frozen: do not rerun over reviewed drafts.')
protected=read('audits/W08-L36-original-accepted-hashes.json');original=read(protected['sourceBatch']);existing=[q for q in original['questions'] if q['lectureId']=='L36']
assert len(existing)==39 and sha(protected['sourceBatch'])==protected['wholeBatchSha256']
assert all(qhash(q)==protected['questionSha256'][q['id']] for q in existing)
obs=read('audits/L36-completeness-observations.json');assert len(obs)==39 and all(x['actualPixelsViewed'] for x in obs.values())
Qs=[];Cs={};counter=defaultdict(int);issues=[]
for q in existing:
 p=int(q['id'].split('-P')[1].split('-')[0]);counter[p]=max(counter[p],int(q['id'].split('-Q')[1]))
titles={1091:'Feasible paths and physical constraints',1092:'Safety efficiency and autonomy',1093:'Planning components and objectives',1094:'Domain-specific planning constraints',1095:'Planning architecture feedback and commands',1096:'Perception localization and estimation',1097:'Global and local planning scope',1098:'Hybrid planning architecture',1099:'Binary occupancy grids and resolution',1100:'Directed topological map interpretation',1101:'Edge weights and chosen objectives',1102:'Grid connectivity and graph conversion',1103:'Random-hop limitations and DAG qualification',1104:'Generic graph-search termination and duplicates',1112:'UCS optimality assumptions',1119:'Heuristic labels and exact cost-to-go',1120:'Heuristic units and lower-bound scope',1121:'Initial A-star cost-to-come and priority',1124:'Search effort versus runtime guarantee'}
def citation(p,kind,locator,role='premise',evidence=None):return dict(slideId=f'lectures-p{p:04d}',sourceId='lectures',sourceSha256=S,physicalPage=p,kind=kind,locator=f'Printed slide {obs[str(p)]["printedFooter"]}: '+locator,evidenceText=evidence if evidence is not None else (R/f'sources/text/lectures/page-{p:04d}.txt').read_text(),role=role,region=None)
def add(p,stem,rows,kind='conceptual',cites=None,assumptions=None,steps=None,formulas=None,difficulty='easy',keys=None,conflict=None):
 counter[p]+=1;qid=f'W08-L36-P{p:04d}-Q{counter[p]:02d}';cid=f'W08-L36-P{p:04d}-C01';keys=keys or ['o1'];opts=[dict(id=f'o{i+1}',text=t) for i,(t,r) in enumerate(rows)];shift=len(Qs)%len(opts);opts=opts[shift:]+opts[:shift]
 why={f'o{i+1}':r for i,(t,r) in enumerate(rows)};just=' '.join(why[k] for k in keys)
 item=dict(id=qid,version=1,status='draft',authorId=A,stem=stem,selectionMode='multi' if len(keys)>1 else 'single',type=kind,difficulty=difficulty,cognitiveSkill='numerical' if kind=='numerical' else 'algorithm' if kind=='algorithm_trace' else 'application' if kind=='scenario' else 'conceptual',week=8,lectureId='L36',topic='Path planning, graph searches and A-star',subtopic=titles[p],tags=['path-planning','coverage-gap',titles[p]],conceptIds=[cid],assumptions=assumptions or [],options=opts,correctOptionIds=keys,citations=cites or [citation(p,'statement',titles[p])],solution=dict(justification=just,optionExplanations={k:('Correct. ' if k in keys else 'Incorrect. ')+v for k,v in why.items()},steps=steps or [],formulas=formulas or [],simpleExplanation=just,memoryAid=None,misconceptions=[v for k,v in why.items() if k not in keys],examTraps=[],prerequisiteConceptIds=[]),origin='generated',reviewIds=[])
 if conflict:item['conflictResolution']=dict(status='derived-qualification-pending-independent-review',questionVersion=1,sourceId='lectures',sourceSha256=S,physicalPage=p,sourceClaim=conflict[0],basis=conflict[1],method=conflict[2],scope='This question version only; independent review required.')
 if kind in ('numerical','algorithm_trace'):assert steps,qid
 Qs.append(item)
 if cid not in Cs:Cs[cid]=dict(id=cid,title=titles[p],description=titles[p]+'; distinct source angles supplement, rather than replace, the 39 accepted questions.',slideIds=[f'lectures-p{p:04d}'],questionIds=[],status='drafted',topic=item['topic'],subtopic=titles[p],prerequisiteConceptIds=[],examinationAngles=[])
 Cs[cid]['questionIds'].append(qid);Cs[cid]['examinationAngles'].append(stem)
 return item
def formula(expr,variables,units,assumptions):return dict(expression=expr,variables=variables,units=units,assumptions=assumptions)
PATH=formula('C(P)=Σ c(e)',{'P':'a route consisting of successive permitted edges','e':'one edge of the route','c(e)':'edge cost','C(P)':'total route cost'},{'c(e),C(P)':'the same declared cost unit'},['Additive edge costs; use permitted directed edges when arrows are present.'])
add(1091,'A drawn route avoids every obstacle outline but requires a turn tighter than the robot can execute. Which conclusion follows from the lecture’s definition?',[
 ('It is collision-free for the drawn point path but not feasible for the stated robot','Feasibility also includes physical constraints such as turning radius; obstacle avoidance alone is insufficient.'),
 ('It is feasible because its geometric curve does not cross an obstacle','This ignores the explicitly stated turning constraint.'),
 ('It becomes feasible if it is shorter than the other routes','A better objective value does not remove a violated physical constraint.'),
 ('It is infeasible only if the goal configuration is outside the map','The turning-radius violation already makes this route infeasible, even with a mapped goal.')],kind='scenario',cites=[citation(1091,'statement','Core Challenge lists size, speed limits and turning radius.')])
add(1091,'What can the dashed start-to-goal route around the three rectangles establish by itself?',[
 ('It illustrates obstacle avoidance, but does not prove global optimality or clearance for a finite-size robot','The sketch supplies neither a numerical objective comparison nor a robot-footprint clearance analysis.'),
 ('It proves the shortest feasible route because its endpoints are labeled start and goal','Endpoint labels do not provide an optimality proof.'),
 ('It proves finite-body clearance because the centerline avoids the rectangles','A point centerline can avoid an obstacle while the robot’s body intersects it.'),
 ('It proves dynamic feasibility because the curve is drawn smoothly','A smooth-looking curve does not specify speed, acceleration or turning constraints.')],kind='diagram',cites=[citation(1091,'figure','Dashed route from black start marker to goal flag around Obstacle 1, 2 and 3.'),citation(1091,'statement','Core Challenge: physical constraints.')])
add(1092,'Which assignment matches the three motivations on the slide?',[
 ('Avoid damage: safety; reduce battery use: efficiency; navigate without continual human intervention: autonomy','The three examples instantiate the slide’s safety, efficiency and autonomy motivations.'),
 ('Avoid damage: autonomy; reduce battery use: safety; navigate without continual human intervention: efficiency','This rotates the stated roles instead of matching the three motivations.'),
 ('Avoid damage: safety; reduce battery use: autonomy; navigate without continual human intervention: efficiency','Safety matches, but battery/resource use and reduced human intervention are exchanged.'),
 ('Avoid damage: efficiency; reduce battery use: autonomy; navigate without continual human intervention: safety','This assigns resource and intervention effects to the wrong motivation labels.')],kind='match',cites=[citation(1092,'statement','Why Does It Matter? Safety, Efficiency and Autonomy bullets.')])
add(1093,'Which pair correctly separates a feasibility constraint from a path-selection objective?',[
 ('Respect a maximum joint acceleration; minimize energy among feasible paths','A physical limit constrains admissible motion, while energy can rank the feasible alternatives.'),
 ('Minimize energy; treat the acceleration limit as a preference that may be exceeded','The acceleration limit is a feasibility requirement, not merely a preference in this scenario.'),
 ('Reach the required goal; ignore obstacle occupancy when comparing routes','The goal alone does not remove the environment’s collision constraints.'),
 ('Use the shortest route; accept any turning radius it requires','Shortest length is an objective, not permission to violate kinematic limits.')],kind='scenario',cites=[citation(1093,'statement','Robot Constraints and Path Selection Criteria bullets.')])
add(1093,'Two collision-free feasible routes reach the same goal. Route P is 8 m and uses 12 J; route Q is 10 m and uses 9 J. Which choice follows from the declared objective?',[
 ('Minimum length selects P; minimum energy selects Q','P has smaller distance, while Q has smaller energy. “Optimal” is relative to the selected objective.'),
 ('Both objectives select P because distance is always the primary cost','The supplied energy objective is minimized by Q, regardless of P’s shorter distance.'),
 ('Both objectives select Q because feasibility makes length irrelevant','Feasibility does not remove the minimum-length objective; P remains shorter.'),
 ('The objectives tie because both routes reach the same goal','Equal endpoints do not imply equal route lengths or energy costs.')],kind='numerical',assumptions=['The given distance and energy are exact illustrative values; both routes satisfy all constraints.'],steps=['Compare distances: 8 m < 10 m, so choose P for length.','Compare energies: 9 J < 12 J, so choose Q for energy.'],cites=[citation(1093,'statement','Path Selection Criteria: length, smoothness or energy efficiency.')])
add(1093,'Which planning component describes the obstacles and free space available to the search?',[
 ('Environment representation','The source defines this component as creating a digital map of obstacles and free space.'),
 ('Start and goal configurations','These specify the endpoints rather than the environment’s traversable region.'),
 ('Robot constraints','These describe physical kinematic/dynamic limits rather than the map itself.'),
 ('Path-selection criteria','These rank candidate routes, rather than describe where obstacles lie.')],kind='definition',cites=[citation(1093,'statement','Four Key components bullets.')])
add(1093,'A robot repeatedly patrols an assigned area to detect changes, while another robot enters an unexplored area to learn its layout. Which listed application pair best fits?',[
 ('Surveillance/monitoring; exploration','Repeated observation matches monitoring; discovering an unknown layout matches exploration.'),
 ('Logistics/delivery; surveillance/monitoring','The first scenario transports no goods, while the second emphasizes learning an unknown area rather than a repeated patrol.'),
 ('Search/rescue; logistics/delivery','Neither a rescue target nor goods transport is specified.'),
 ('Exploration; search/rescue','The first area is assigned for repeated monitoring, and the second scenario gives no rescue objective.')],kind='scenario',cites=[citation(1093,'statement','Advanced Applications: Surveillance & Monitoring, Search & Rescue, Logistics & Delivery, Exploration.')])
add(1094,'Which planning concern is specifically illustrated by passing a cup of coffee with a fixed-base robotic arm?',[
 ('Coordinate end-effector motion while respecting kinematic/dynamic limits and avoiding abrupt motion','The arm example emphasizes multi-axis constraints and smooth transfer without spilling.'),
 ('Choose a 3D aerial route around restricted flight zones','That is the UAV example, not the fixed-base arm task.'),
 ('Choose a road route while reacting to city traffic','That is the mobile-robot traffic example, not the arm task.'),
 ('Ignore intermediate motion as long as the final cup position is reachable','Intermediate motion matters to constraints and spilling; endpoint reachability alone is insufficient.')],kind='scenario',cites=[citation(1094,'statement','Manipulators (Robotic Arms) environment, challenge and coffee-passing example.')])
add(1094,'A delivery UAV must plan around tall structures and a restricted region. Which aspect of the lecture’s drone example matters beyond a ground-plane route?',[
 ('The route occupies 3D airspace and must respect obstacle and restricted-zone constraints','The UAV section explicitly describes 3D aerial navigation around obstacles and restricted zones.'),
 ('Only horizontal distance matters once the launch and landing points are known','The example requires 3D obstacle and zone constraints, not just horizontal endpoint distance.'),
 ('A fixed-base arm’s joint sequence can be used without an airspace representation','The problem requires an aerial route representation rather than treating the vehicle as the slide’s fixed-base arm.'),
 ('Restricted zones can be ignored if the geometric route avoids buildings','Restricted-zone constraints are separately listed and are not removed by building avoidance.')],kind='scenario',cites=[citation(1094,'statement','Drones (UAVs) environment and key challenge.')])
add(1094,'What makes the city-traffic example especially relevant to the mobile-robot row?',[
 ('Nearby obstacles can move while the robot is navigating','The mobile-robot row highlights dynamic obstacle avoidance in complex indoor/outdoor environments.'),
 ('The base stays fixed while only the end-effector moves','That describes the manipulator row rather than a moving vehicle in traffic.'),
 ('The route is planned solely through restricted aerial volumes','That describes the UAV airspace issue, not the road-traffic emphasis.'),
 ('The environment representation removes the need to observe moving obstacles','A map does not remove the need to handle dynamic obstacles highlighted by the example.')],kind='scenario',cites=[citation(1094,'statement','Mobile Robots row: dynamic obstacle avoidance and city traffic.')])
add(1095,'Which inputs feed the planning block directly in the displayed architecture?',[
 ('Feedback from both perception and localization','Separate arrows from perception and localization enter the planning block.'),
 ('Only localization, after perception has been removed from the loop','The diagram also includes a direct perception-to-planning feedback arrow.'),
 ('Only perception, with localization performed after execution','Localization appears upstream and also feeds planning directly.'),
 ('Controller commands, with no sensing or pose feedback','Controller commands are downstream of execution; the diagram explicitly includes sensing and localization feedback.')],kind='diagram',cites=[citation(1095,'figure','Two feedback arrows from Perception and Localization into Planning.')])
add(1095,'In the architecture figure, which labels distinguish Planning→Plan Execution from Plan Execution→Controller/Actuator?',[
 ('Plan; command','The downward arrow to execution is labeled plan, and the leftward arrow to controller/actuator is labeled command.'),
 ('Command; plan','This exchanges the two arrow labels.'),
 ('Feedback; command','The execution-to-controller label matches, but feedback labels the perception/localization inputs to planning.'),
 ('Plan; localization','The planning-to-execution label matches, but localization is a separate upstream block, not the controller arrow.')],kind='diagram',cites=[citation(1095,'figure','Plan and command arrows below Planning and Plan Execution.')])
add(1096,'A robot produces a map of nearby obstacles and an estimate of its pose relative to that map. Which pair matches the source’s two functions?',[
 ('Obstacle map: perception; map-relative pose: localization','The source separates sensing the surrounding world from locating the robot within the map.'),
 ('Obstacle map: localization; map-relative pose: perception','This reverses the two output roles.'),
 ('Obstacle map: planning; map-relative pose: execution','Planning selects actions/routes and execution performs them; neither label matches the two stated estimates.'),
 ('Obstacle map: execution; map-relative pose: planning','The two outputs are sensing/estimation products, not motion execution or route selection.')],kind='match',cites=[citation(1096,'statement','Localization and Perception panels.')])
add(1096,'Which interpretation avoids treating the slide’s phrase “estimates its exact position” as a guarantee?',[
 ('Localization estimates pose from measurements; an estimate can retain uncertainty','Estimating map-relative position or pose does not by itself eliminate measurement or model uncertainty.'),
 ('Every localization output is exact because a map gives a coordinate reference','A reference frame defines coordinates but does not make the measurements exact.'),
 ('Combining GPS and encoders makes a confidence estimate unnecessary','Combining measurements does not logically establish zero uncertainty.'),
 ('A displayed decimal position proves its final digit is physically exact','Numeric formatting does not establish the accuracy of a pose estimate.')],cites=[citation(1096,'statement','Localization first bullet: estimates its exact position relative to the map.','conflict')],conflict=('The robot estimates its exact position relative to the map.','Use the output as an estimate, not a promise of zero uncertainty.','Distinguish the meaning of estimation from a guarantee of exactness; the source supplies no zero-noise or perfect-model assumption.'))
add(1096,'Which list is placed under localization tools in the slide, rather than the separate perception-sensor list?',[
 ('GPS, IMU, wheel encoders and SLAM','These are explicitly listed in the localization panel. This is a slide grouping, not a claim that sensing modalities can serve only one function.'),
 ('Ultrasonic sensor, camera, LiDAR and radar','These are the tools listed in the separate perception panel.'),
 ('GPS, radar, wheel encoders and ultrasonic sensor','This mixes two localization-list entries with two entries from the perception list.'),
 ('Camera, IMU, LiDAR and SLAM','This also mixes the two printed lists instead of reproducing the localization grouping.')],kind='match',assumptions=['Classify the source’s lists, not exclusive real-world uses of a sensor.'],cites=[citation(1096,'statement','Uses tools like lines in the Localization and Perception panels.')])
add(1097,'The map illustration shows a long A-to-B route and a magnified car steering around a pothole. Which interpretation matches the intended comparison?',[
 ('The whole trip illustrates global planning; the nearby avoidance maneuver illustrates local planning','The long route provides overall goal-directed guidance, while the inset illustrates adapting motion near an observed obstacle.'),
 ('The whole trip illustrates local planning; the pothole maneuver illustrates global planning','This reverses the long-horizon and immediate-obstacle roles.'),
 ('Both illustrations show only global planning because they are on the same map','The inset deliberately distinguishes immediate local obstacle handling from the overall route.'),
 ('Both illustrations show only localization because their positions are mapped','The illustrated outputs are routes/maneuvers rather than estimates of the vehicle’s current pose.')],kind='diagram',cites=[citation(1097,'figure','Lower A-to-B map route and magnified vehicle/pothole inset.')])
add(1097,'Suppose a planner recomputes a whole-map route to the destination after a road closure while the robot is moving. How should the slide’s offline/global contrast be qualified?',[
 ('It is still whole-route planning in this example, although it is recomputed online','The scope of the route remains global; the slide’s offline/full-map description is a simplified comparison rather than a rule forbidding global replanning during motion.'),
 ('It must be local planning solely because computation occurs during motion','Online timing alone does not make a whole-map route a short-range reactive maneuver.'),
 ('It stops being planning because an initial route already exists','Updating a route after changed conditions is still a planning operation.'),
 ('It must ignore the road closure to retain a global route','Global routing need not preserve stale map information merely because the initial plan was computed earlier.')],kind='scenario',cites=[citation(1097,'statement','Global Planning bullet: complete pre-existing map and offline before movement.','conflict')],conflict=('Global planning computes an optimal path offline before movement starts.','Treat this as the lecture’s comparison, not a universal prohibition on online global replanning.','Apply the explicitly supplied whole-map replanning scenario and separate spatial planning scope from execution timing.'))
add(1098,'Why does the comparison recommend combining global and local planning?',[
 ('An overall route supplies destination guidance while local reactions handle nearby changes','The two approaches address different horizons: whole-path guidance and immediate obstacle adaptation.'),
 ('Local reactions make a destination or long-range route unnecessary','The recommendation combines roles rather than removing the overall task or route.'),
 ('A fixed global map makes live sensing unnecessary during motion','The local side is specifically motivated by current sensor data and dynamic obstacles.'),
 ('Combining them guarantees an optimal collision-free route under any sensor failure','The diagram gives complementary functions, not an unconditional guarantee despite missing or incorrect sensing.')],kind='scenario',cites=[citation(1098,'statement','Box below comparison: advanced robots combine both to reach the goal safely.')])
add(1098,'Which algorithms are named in the global-planning column of this lecture?',[
 ('Dijkstra’s algorithm and A-star','These are the two examples printed under Global Path Planning.'),
 ('Dijkstra’s algorithm and greedy best-first search','Dijkstra’s algorithm is named, but greedy best-first search is not the second example in this column.'),
 ('Breadth-first search and depth-first search','These are graph-search algorithms, but they are not the pair named in this particular column.'),
 ('Uniform-cost search and greedy best-first search','Uniform-cost search is closely related to Dijkstra’s method, but this is not the two-name pair printed in the column.')],kind='definition',cites=[citation(1098,'statement','Global Path Planning final bullet: Common algorithm: Dijkstra’s or A-star.')])

def persist(stage):
 batch=dict(schemaVersion='1.0.0',batchId=B,authorId=A,questions=Qs,concepts=list(Cs.values()),sourceIssues=issues,authorChecks=[],coverageNote=stage+'; existing 39 accepted L36 objects remain in search-foundations.json unchanged. All 39 source pages actually viewed; new questions remain draft pending independent review.')
 write(f'data/question-batches/{B}.json',batch)
 ins=read(f'data/inspection-batches/{B}.json')
 for s in ins['slides']:
  for c in Cs.values():
   if s['id'] in c['slideIds'] and c['id'] not in s['conceptIds']:s['conceptIds'].append(c['id'])
 ins['sourceIssues']=issues;write(f'data/inspection-batches/{B}.json',ins)
 (R/f'audits/handoffs/{B}.md').write_text(f'# L36 gap authoring in progress\nAll 39 source pages inspected, physical1088–1126. {len(Qs)} draft gap questions saved; 39 accepted originals protected by audits/W08-L36-original-accepted-hashes.json.\nStage: {stage}.\nScript: scripts/author_W08_L36_gap.py\nNotes: audits/L36-completeness-observations.json\nNo canonical/Git/accepted-object writes; author checks and blind freeze still pending.\n')
persist('Stable slice: constraints, objectives, domains, architecture and planning scope')
add(1099,'Under the slide’s binary occupancy convention, what does a cell value of 1 indicate?',[
 ('Occupied; it is excluded from the allowed cells of this simplified map','The slide explicitly uses 1 for occupied and 0 for free.'),
 ('Free; it is the preferred value for a traversable cell','This reverses the source’s binary convention.'),
 ('Unknown; it must be explored before being classified','The slide presents a binary free/occupied map, not an unknown-value encoding.'),
 ('The cell has traversal cost one regardless of obstacles','Occupancy is not the same quantity as a move’s edge cost.')],kind='definition',cites=[citation(1099,'statement','Occupancy-grid bullet: 0 free and 1 occupied.')])
add(1099,'In the displayed 8×8 grid, black cells are occupied and white cells are free. How many free-cell vertices would a graph contain if it includes one vertex per free cell?',[
 ('48','The 64 cells include 16 black occupied cells, leaving 64−16=48 free cells.'),
 ('16','This counts the occupied cells rather than the free cells.'),
 ('64','This includes occupied cells despite the explicit free-cell-only graph rule.'),
 ('49','This is an off-by-one free-cell count; the eight rows contain 16 occupied cells in total.')],kind='diagram',cites=[citation(1099,'figure','Upper-right 8×8 binary grid; count filled black cells by row.','premise','Occupied columns by row: [6,7,8];[4,6];[1,2];[];[4,5,6];[1,4,5];[4];[4,8].')],assumptions=['Count the displayed cells, with rows top to bottom and columns left to right. Include all free cells, without filtering by reachability from a particular start.'],steps=['There are 8×8=64 total cells.','Occupied counts by row are 3,2,2,0,3,3,1,2; their sum is 16.','Free-cell vertices: 64−16=48.'])
add(1099,'A 20 m by 10 m rectangular map uses square cells and one byte per cell. Refining cell width from 0.5 m to 0.25 m changes the cell-storage requirement how?',[
 ('From 800 bytes to 3200 bytes, a factor of four','Both grid dimensions double, so the total number of cells and the stipulated storage multiply by four.'),
 ('From 800 bytes to 1600 bytes, a factor of two','This doubles only one dimension rather than both.'),
 ('From 400 bytes to 1600 bytes, a factor of four','The scale factor matches, but the initial 40×20 grid has 800 cells, not 400.'),
 ('From 800 bytes to 6400 bytes, a factor of eight','A two-dimensional refinement by two in each direction gives four times as many cells, not eight.')],kind='numerical',cites=[citation(1099,'statement','Cons: high memory for large environments and precision limited by grid resolution.')],assumptions=['The map dimensions are exact multiples of each cell width; count only one-byte cell storage and no metadata.'],steps=['Initial dimensions are 20/0.5=40 and 10/0.5=20 cells: 800 bytes.','Refined dimensions are 20/0.25=80 and 10/0.25=40 cells: 3200 bytes.','Storage factor is 3200/800=4.'],formulas=[formula('N=(L/s)(W/s); M=bN',{'L,W':'rectangular map dimensions','s':'square-cell side length','N':'cell count','b':'bytes stored per cell','M':'cell-storage requirement'},{'L,W,s':'m','N':'dimensionless count','b':'bytes per cell','M':'bytes'},['Dimensions are integer multiples of s; fixed storage per cell; no metadata.'])])
add(1099,'A free-cell centerline passes through a corridor 0.8 m wide, but the robot is 1.0 m wide and cannot rotate to reduce that width. What additional issue must the planner handle?',[
 ('The robot footprint does not fit; free centerline cells alone are insufficient','The 1.0 m body exceeds the 0.8 m corridor width. The source’s physical-size constraint must be respected in addition to free-cell labels.'),
 ('The centerline’s free labels prove the robot fits','A free center point does not establish clearance for the entire body.'),
 ('Choosing smaller cells changes the physical corridor width enough to admit the robot','Finer resolution can describe the geometry better but does not widen the corridor.'),
 ('Replacing the grid with a graph removes the physical width constraint','Changing the representation does not remove the robot’s actual size.')],kind='scenario',cites=[citation(1099,'statement','Binary free-cell description.'),citation(1091,'statement','Core Challenge: physical size constraint.')],assumptions=['Corridor and robot widths are exact illustrative values; no deformation or alternate orientation reduces the required width.'])
add(1100,'What information does the graph-map abstraction retain more directly than a detailed occupancy grid?',[
 ('Connections among recognizable places and their route costs','The source models places as vertices and connections as edges, trading fine physical detail for a useful large-scale representation.'),
 ('The exact shape of every obstacle boundary between connected places','The slide explicitly notes reduced physical-layout detail.'),
 ('A uniform square-cell occupancy value for every map location','That is the occupancy-grid representation, not the place-and-connection abstraction.'),
 ('The robot’s full joint configuration at every point along each edge','The diagram does not encode complete continuous robot configurations along each route.')],cites=[citation(1100,'statement','Graph G=(V,E), recognizable places, costed routes and pros/cons.')])
add(1100,'According to the arrow directions in the five-node map, which statement about B and C is correct?',[
 ('C→B is shown with cost 7; B→C is not drawn','The arrow on their connection points from C up toward B and bears the label 7.'),
 ('B→C is shown with cost 7; C→B is not drawn','This reverses the displayed arrow direction.'),
 ('Both C→B and B→C are drawn with cost 7','The figure contains one directed arrow, not a bidirectional pair.'),
 ('There is no B–C connection; the cost 7 belongs only to D→E','The figure separately shows both C→B and D→E with the label 7.')],kind='diagram',cites=[citation(1100,'figure','Directed edge from River Crossing C up to Central Park Hub B, labeled 7.')],assumptions=['Follow the displayed arrows; do not assume an undrawn reverse road.'])
add(1100,'Using the five-node map’s directed edges and additive weights, which A-to-E route has minimum total cost?',[
 ('A→B→E, cost 4','The route uses weights 3 and 1, totaling 4; the other listed directed routes have larger totals.'),
 ('A→C→D→E, cost 10','This valid route costs 1+2+7=10, larger than 4.'),
 ('A→C→B→E, cost 9','This valid route costs 1+7+1=9, larger than 4.'),
 ('A→B→D→E, cost 15','This valid route costs 3+5+7=15, larger than 4.')],kind='numerical',cites=[citation(1100,'figure','All seven directed edges and weights in the A–E map.')],assumptions=['Weights are abstract cost units because the figure does not label a physical unit. Only displayed directed edges are allowed.'],steps=['From B, direct B→E costs 1, less than B→D→E=12.','From C, C→B→E costs 8 and C→D→E costs 9.','From A, A→B→E costs 3+1=4; any route via C costs at least 1+8=9.'],formulas=[PATH])
add(1101,'A route planner changes every edge weight from distance to estimated travel time. What does a minimum-weight route now optimize?',[
 ('The sum of modeled travel times, not necessarily the sum of distances','The optimum is relative to the meaning of the weights. Changing them changes the objective being minimized.'),
 ('Distance, because graph edges physically connect places','Physical connections do not force the numeric weights to represent distance.'),
 ('Both time and distance simultaneously, regardless of their trade-off','Minimizing one weighted criterion does not guarantee simultaneous minima of all other criteria.'),
 ('The number of visited places, because every edge remains one connection','Hop count ignores the newly supplied unequal time weights.')],cites=[citation(1101,'statement','Edge weights may represent distance or estimated travel time; absolute-best wording.','conflict')],conflict=('Edge weights help determine the absolute best path based on real-world constraints.','Best means minimum modeled cost for the declared objective and feasible represented routes, not every objective at once.','Compare two different meanings of the edge weights explicitly listed by the source.'))
add(1101,'On the displayed A–E map, a rule chooses the smallest outgoing edge at each current vertex without looking ahead. Starting at A, which result demonstrates the limitation of this rule?',[
 ('It takes A→C→D→E with cost 10, although A→B→E costs 4','The rule chooses AC=1 over AB=3, then CD=2 over CB=7, and finally DE=7. Locally smallest edges do not minimize the whole route.'),
 ('It takes A→B→E with cost 4 because it accounts for the final edge at A','The specified rule does not look ahead to BE=1 when choosing A’s outgoing edge.'),
 ('It takes A→C→B→E with cost 9 because CB has the lowest weight from C','From C, CD=2 is smaller than CB=7, so the stated rule chooses D, not B.'),
 ('It takes A→B→D→E with cost 15 because BD is the lowest edge from B','The rule would first choose C at A; furthermore BE=1 is cheaper than BD=5.')],kind='algorithm_trace',cites=[citation(1101,'figure','Directed A–E graph and weights; abstract cost units.')],assumptions=['Choose only among outgoing arrows by immediate edge weight; stop at E; there are no relevant ties.'],steps=['At A choose C because 1<3.','At C choose D because 2<7.','At D the only outgoing edge is E with cost 7.','Total is 1+2+7=10, compared with 3+1=4 for A→B→E.'],formulas=[PATH])
add(1102,'Which neighborhood matches the two connectivity diagrams for an unobstructed interior cell?',[
 ('4-connected: four edge-sharing cells; 8-connected: those four plus four corner-sharing cells','The diagrams differ by adding the four diagonal neighbors.'),
 ('4-connected: four corner-sharing cells; 8-connected: those four plus the center cell','This misidentifies cardinal neighbors and incorrectly counts the center as its own neighbor.'),
 ('4-connected: four edge-sharing cells; 8-connected: cells up to two steps away on each axis','The additional 8-connected neighbors are diagonals one row and one column away, not two-axis-step cells.'),
 ('4-connected: four edge-sharing cells; 8-connected: eight neighbors with no diagonals','The diagonals are precisely the four additional neighbors in the figure.')],kind='diagram',cites=[citation(1102,'figure','Upper-right 4-Connected and lower-right 8-Connected 3×3 neighborhoods.')])
add(1102,'An obstacle-free square grid has cell width 0.5 m. What geometric distance is traveled by two cardinal moves and three diagonal moves?',[
 ('1+1.5√2 m, approximately 3.121 m','Each cardinal move has length 0.5 m and each diagonal has length 0.5√2 m; total 2(0.5)+3(0.5√2).'),
 ('2.5 m','This assigns the same 0.5 m length to diagonal and cardinal moves.'),
 ('4.0 m','This treats each diagonal as two full cardinal lengths, giving 2(0.5)+3(1).'),
 ('2+3√2 m, approximately 6.243 m','This uses unit-metre cells and omits the specified 0.5 m scale.')],kind='numerical',cites=[citation(1102,'equation','Printed cardinal cost 1 and diagonal cost √2≈1.414.')],assumptions=['Count the length of the given sequence, not the minimum start-to-goal path. Every move is permitted.'],steps=['For cell width s=0.5 m, diagonal length is √(s²+s²)=s√2.','Add two cardinals and three diagonals: 2s+3s√2=1+1.5√2 m.','Using √2≈1.41421356 gives 3.12132034 m, rounded to 3.121 m.'],formulas=[formula('D=s(n_c+√2 n_d)',{'D':'total geometric length','s':'square-cell width','n_c':'number of cardinal moves','n_d':'number of diagonal moves'},{'D,s':'m','n_c,n_d':'dimensionless counts'},['Permitted center-to-center moves on a square grid.'])])
add(1102,'To turn the binary occupancy map into a traversable graph, what must “reachable neighboring cells” mean?',[
 ('Include only transitions permitted by free space, connectivity and the robot/motion model','A geometric neighbor is not automatically traversable; the graph must respect occupancy and the declared motion constraints.'),
 ('Connect every adjacent pair even when one cell is occupied','That would allow the search to enter cells marked as obstacles.'),
 ('Connect every pair of free cells regardless of distance or intervening obstacles','Free endpoints alone do not establish a feasible connecting motion.'),
 ('Delete all edge weights because grid vertices are regularly spaced','Regular spacing does not make diagonal and cardinal costs equal under the source’s metric.')],cites=[citation(1102,'statement','Grid-to-graph conversion connects reachable neighboring cells.'),citation(1099,'statement','Occupied cells cannot be entered.'),citation(1091,'statement','Physical constraints.')])
add(1102,'In a 2×2 grid, only the top-left and bottom-right cells are free. An explicit no-corner-cutting rule permits a diagonal only when both adjacent side cells are free. Can the top-left reach the bottom-right within this grid?',[
 ('No; the diagonal is disallowed and both cardinal neighbors are blocked','Both side cells are occupied, so the supplied corner rule excludes the only geometric diagonal connection.'),
 ('Yes; all 8-connected diagonals are legal regardless of neighboring obstacles','That ignores the explicitly supplied no-corner-cutting rule.'),
 ('Yes; take two cardinal moves through one occupied side cell','Occupied cells are not traversable under the supplied binary map.'),
 ('Yes; because the two free endpoints have the same occupancy value','Equal free endpoint labels do not establish a legal transition between them.')],kind='scenario',assumptions=['The no-corner-cutting rule is supplied for this question; the slide itself does not choose a corner policy. The robot stays inside these four cells.'],cites=[citation(1102,'figure','8-connected diagram shows geometric diagonal adjacency; obstacle policy is not specified.'),citation(1099,'statement','Binary occupied/free interpretation.')])
add(1102,'Why does changing a free grid from unit-cost 4-connected moves to cardinal-cost 1 and diagonal-cost √2 affect the usual BFS cost-optimality argument?',[
 ('BFS still minimizes hops, but unequal step costs no longer make hop count equal total path cost','With equal unit costs, route cost equals the number of edges. The source’s diagonal weights break that equality.'),
 ('BFS starts sorting its frontier by √2 as soon as diagonal edges are added','BFS remains FIFO unless its algorithm is changed; edge weights do not automatically change its priority rule.'),
 ('Every diagonal grid forces BFS to return a nonoptimal route','Unequal costs remove the general guarantee but do not prove failure on every particular grid.'),
 ('BFS loses the ability to reach a goal because a diagonal cost is irrational','The numeric edge cost does not affect BFS reachability on a finite graph with correct repeated-state handling.')],kind='synthesis',cites=[citation(1102,'equation','4-connected unit costs and 8-connected diagonal cost √2.'),citation(1107,'statement','BFS uses FIFO and ignores actual edge weight.')])
persist('Stable slice: occupancy, directed-map objectives and grid-connectivity gaps added')
add(1103,'For the displayed directed A–E graph specifically, assume a walker must choose an outgoing arrow at each step and stops at E. Which statement qualifies the slide’s generic “no guarantee” warning?',[
 ('Every such walk reaches E in at most four moves, although it need not be minimum-cost','This displayed graph is acyclic and E is its only terminal vertex reachable from A. Its longest A-to-E directed path is A→C→B→D→E with four edges.'),
 ('A walk can cycle indefinitely through B and C','Only C→B is drawn; the reverse B→C needed for that cycle is absent.'),
 ('A walk can become stuck at D without reaching E','D has the outgoing edge D→E, so the supplied rule cannot stop at D.'),
 ('Every such walk reaches E in exactly two moves and has minimum cost','A→B→E uses two moves, but the figure also contains longer and more costly directed paths.')],kind='diagram',assumptions=['Use exactly the displayed directed arrows, always move along an outgoing edge when not at E, and stop at E. This is not a guarantee for arbitrary graphs.'],cites=[citation(1103,'figure','Five-node directed graph with terminal E and no directed cycles.'),citation(1103,'statement','Naive-strategy cons: no guarantee of reaching the goal.','conflict')],conflict=('Randomly hopping between neighboring vertices has no guarantee of reaching the goal.','The generic warning must be distinguished from this particular finite directed acyclic graph, whose every A-started outgoing walk reaches E.','Enumerate the five directed A-to-E paths and observe that all branches terminate at E within four moves.'))
add(1103,'Add the explicit rule that each outgoing arrow is chosen uniformly and independently at the current vertex in the pictured A–E graph. What is the probability of taking its minimum-cost route A→B→E?',[
 ('1/4','At A there are two outgoing choices and at B there are two. The route probability is (1/2)(1/2)=1/4.'),
 ('1/2','This counts only one of the two necessary choices.'),
 ('1/5','The five full paths are not equally probable under uniform local edge choices; some require an additional branch decision.'),
 ('1/8','This adds a third binary branch choice that the two-edge route does not contain.')],kind='numerical',assumptions=['Uniform local choices are supplied for this question, not stated by the slide. Follow arrow directions and stop at E.'],cites=[citation(1103,'figure','Outgoing arrows A→B/A→C and B→E/B→D in the weighted graph.'),citation(1103,'statement','Naive strategy: randomly hop between neighboring vertices.')],steps=['A has two outgoing edges, so P(A→B)=1/2.','B has two outgoing edges, so P(B→E | at B)=1/2.','Multiply the conditional branch probabilities: 1/2×1/2=1/4.'],formulas=[formula('P(route)=∏ P(next vertex | current vertex)',{'P(route)':'probability of the specified directed route','P(next vertex | current vertex)':'conditional transition probability at one step'},{'all probabilities':'dimensionless'},['Use the stated uniform local transition rule and stop on reaching E.'])])
add(1104,'If the start vertex is already the goal, what does the displayed generic search procedure do before any successor expansion?',[
 ('Remove the start from the frontier, recognize the goal and stop','The procedure initializes the frontier with the start and checks the selected vertex for the goal before expanding its neighbors.'),
 ('Expand the start’s neighbors once before testing for the goal','The source places the goal test before successor expansion.'),
 ('Declare failure because the explored set is initially empty','An empty explored set at initialization is normal; it is not the failure condition.'),
 ('Require at least one edge in the route before it can report success','The source’s goal test does not require a nonzero-length route.')],kind='algorithm_trace',assumptions=['Start and goal are the same valid vertex. The empty route has zero accumulated edge cost.'],steps=['Initialize frontier=[start], explored=[].','Select start and test whether it is the goal.','The test succeeds, so stop with no successor expansions and zero route edges.'],cites=[citation(1104,'statement','General algorithm: initialize frontier, select vertex, test goal, otherwise expand.')])
add(1104,'After exhaustive search of a finite represented graph, the frontier is empty and the goal was never found. What conclusion is warranted?',[
 ('No route exists in that represented graph under its encoded transition rules','Exhausting all reachable represented states establishes failure in the chosen graph; it does not prove that every possible real-world route was represented.'),
 ('No physically possible route exists even if the map omitted valid passages','An incomplete representation can omit a real route, so the conclusion must be scoped to the searched graph.'),
 ('The cheapest route is the last expanded vertex because the goal was not found','A last-expanded vertex is not a route to an unreached goal.'),
 ('The search should report success whenever all frontier entries have been processed','Processing the frontier is not success unless the goal is reached.')],assumptions=['The graph is finite and fixed; every permitted successor of each expanded vertex is considered, with correct repeated-state handling.'],cites=[citation(1104,'statement','Final condition: empty frontier without finding goal means no path exists.')])
add(1104,'In the BFS example, just before D is expanded the frontier is [D,E,F]. D is connected to already explored B, queued E and new G. Which duplicate-handling interpretation matches the shown next frontier [E,F,G]?',[
 ('Do not add B again, retain the existing E entry, and enqueue G once','The trace excludes explored B and avoids duplicating E, which is already scheduled, while adding the newly discovered G.'),
 ('Re-enqueue every neighbor not yet explored, including a second E','That would duplicate E and would not match the shown frontier.'),
 ('Delete E because it was discovered before D was expanded','E remains in the displayed frontier; prior discovery does not require deleting it.'),
 ('Move G directly to the explored set when D first discovers it','The trace places G on the frontier and does not yet count it as expanded.')],kind='algorithm_trace',cites=[citation(1104,'statement','Generic expansion adds unexplored neighbors.'),citation(1109,'statement','Step 4: expand D and obtain frontier [E,F,G].'),citation(1109,'figure','D adjacent to B, E and G.')],steps=['Remove D from the front, leaving [E,F].','Skip B because it is already explored and keep E’s existing queued entry.','Append the new G, giving [E,F,G].'])
add(1112,'To test the scope of UCS’s optimality claim, consider a supplied directed graph S→G of cost 2, S→A of cost 3, and A→G of cost −2. UCS stops when it removes the goal with the smallest queued cumulative cost. What happens?',[
 ('It returns cost 2, although S→A→G costs 1; the negative edge breaks the usual nonnegative-cost premise','After expanding S, G(2) is removed before A(3). Yet the unexpanded route through A totals 3−2=1, demonstrating why the premise matters.'),
 ('It returns cost 1 because the negative edge is considered before A is removed','The stated UCS ordering removes the queued goal at cost 2 before expanding A and seeing its outgoing negative edge.'),
 ('It returns cost 3 because A was generated after G','UCS priority is cumulative cost, not generation position; G at 2 is removed first.'),
 ('It proves the graph has no finite optimum because every negative edge creates a cycle','This directed graph has no cycle. Its finite routes cost 2 and 1; a negative edge alone does not create a cycle.')],kind='algorithm_trace',difficulty='medium',assumptions=['This is an explicitly supplied counterexample graph, not the slide’s positive-distance road network.','Use the goal-on-removal stopping rule and do not inspect A’s outgoing edge before A is expanded.'],cites=[citation(1112,'statement','UCS described as optimal and ordered by lowest cumulative cost.','conflict'),citation(1104,'statement','Select a frontier vertex and stop if it is the goal.')],steps=['Expand S at g=0, creating queued G(2) and A(3).','Remove G because 2<3 and stop, returning 2.','The alternative directed route S→A→G costs 3+(−2)=1.','Thus the unrestricted claim fails on this negative-edge example.'],formulas=[PATH],conflict=('UCS is an optimal graph-search algorithm.','The lecture’s positive-distance example satisfies the required nonnegative-edge setting. Do not extend the guarantee to arbitrary negative edge costs.','Trace the fully specified acyclic negative-edge counterexample using the source’s cumulative-cost priority and goal-on-removal rule.'))
add(1119,'For the source’s undirected weighted A–G road graph, what are the exact minimum remaining costs to goal G in order (A,B,C,D,E,F,G)?',[
 ('(9,7,7,6,4,3,0) km','The best routes to G give F=3, E=1+3=4, D=6, B=3+1+3=7, C=4+3=7 and A=2+4+3=9; the goal itself has zero remaining cost.'),
 ('(7,6,5,4,3,2,0) km','These are the printed heuristic estimates, not the exact shortest remaining route costs.'),
 ('(0,5,2,9,7,6,9) km','These are shortest costs from start A, not remaining costs to G.'),
 ('(17,12,7,6,8,3,0) km','The entries for A, B and E use valid but longer routes through D; exact remaining costs require taking the minimum.')],kind='numerical',difficulty='medium',cites=[citation(1119,'figure','Nine weighted undirected edges and h labels A7,B6,C5,D4,E3,F2,G0.'),citation(1112,'statement','Road costs are distances in km.')],assumptions=['Use only the displayed undirected edges and add their nonnegative distance weights.'],steps=['Set remaining cost at G to 0; F→G costs 3 and D→G costs 6.','E→F→G costs 1+3=4, less than E→D→G=8.','B→E→F→G costs 3+1+3=7; C→F→G costs 4+3=7.','A→C→F→G costs 2+4+3=9. The D→E→F→G alternative also costs 2+1+3=6.','Collect the minima in A,B,C,D,E,F,G order.'],formulas=[PATH])
add(1120,'Keep the source road graph unchanged. Which one of these proposed heuristic replacements would overestimate the true remaining distance to G?',[
 ('Set h(E)=5 km','E→F→G costs 1+3=4 km, so 5 km exceeds the true minimum remaining cost.'),
 ('Set h(A)=8 km','The true minimum from A is 9 km, so 8 km is still a lower estimate.'),
 ('Set h(B)=7 km','The best B→E→F→G route costs 7 km; equality is allowed by admissibility.'),
 ('Set h(F)=3 km','The direct F→G edge costs 3 km; this is an exact, non-overestimating value.')],kind='numerical',difficulty='medium',cites=[citation(1119,'figure','Road-edge distances and original heuristic labels.'),citation(1120,'statement','Admissibility: never overestimate actual remaining cost.')],assumptions=['Change only the named heuristic in each separate candidate; edge costs remain the source’s km distances.'],steps=['Compute h*(E)=1+3=4 km, h*(A)=2+4+3=9 km, h*(B)=3+1+3=7 km and h*(F)=3 km.','Compare the proposed values: 5>4, 8≤9, 7≤7 and 3≤3.','Only the E replacement overestimates.'],formulas=[formula('h(v)≤h*(v)',{'v':'a graph vertex','h(v)':'proposed remaining-cost estimate','h*(v)':'actual minimum remaining cost to G'},{'h(v),h*(v)':'km'},['Admissibility comparison for the fixed source graph and distance objective.']),PATH])
add(1121,'Before A* expands the start A, the source assigns h(A)=7 km and no route edges have been traversed. What are g(A) and f(A)?',[
 ('g(A)=0 km; f(A)=7 km','The empty route has zero cost-to-come, and f=g+h gives 0+7=7 km.'),
 ('g(A)=7 km; f(A)=14 km','This incorrectly counts the heuristic as already-traversed route cost and then adds it again.'),
 ('g(A)=0 km; f(A)=0 km','This drops the nonzero heuristic from the initial priority.'),
 ('g(A)=7 km; f(A)=0 km','This exchanges the roles of the initial accumulated cost and the heuristic-guided priority.')],kind='numerical',cites=[citation(1121,'statement','Initialize frontier [A(0+7=7)] and explored [].'),citation(1119,'equation','f(v)=g(v)+h(v).')],steps=['The initial route is empty, so g(A)=0 km.','Use f(A)=g(A)+h(A)=0+7=7 km.'],formulas=[formula('f(v)=g(v)+h(v)',{'v':'a graph vertex','f(v)':'A-star frontier priority','g(v)':'accumulated route cost from start','h(v)':'estimated remaining route cost to goal'},{'f(v),g(v),h(v)':'km'},['All three costs use the same distance unit.'])])
add(1124,'The example expands three non-goal nodes with A* and six with UCS. Which inference properly qualifies the summary’s statement that A* is faster?',[
 ('It demonstrates fewer expansions in this example, not a universal elapsed-time advantage','Expansion count is the stated comparison metric. Heuristic evaluation and implementation costs affect elapsed time, and a zero heuristic can give UCS-equivalent priorities.'),
 ('It proves A* takes exactly half the elapsed time on every input','The ratio concerns this example’s node counts, not a universal runtime ratio.'),
 ('It proves every admissible heuristic strictly reduces expansions compared with UCS','The admissible zero heuristic uses the same g-based priority as UCS, so strict reduction is not guaranteed.'),
 ('It proves UCS returned a longer route because it expanded more nodes','Both source searches return the same cost-9 route despite different expansion counts.')],cites=[citation(1124,'statement','Last summary bullet: A* reaches the optimal path faster than UCS.','conflict'),citation(1123,'statement','A* cost9 and three explored nodes.'),citation(1117,'statement','UCS cost9 and six explored nodes.'),citation(1119,'equation','f=g+h, permitting the explicitly discussed h=0 limiting case.')],conflict=('A* uses a heuristic to reach the optimal path faster than UCS.','The example establishes an expansion-count advantage, not an unconditional elapsed-time guarantee.','Compare the printed node counts and equal route costs, then use f=g when h=0 as a counterexample to universal strict search reduction.'))
persist('All identified meaningful gaps drafted; source-issue records, exact author checks and final freeze pending')
# Final author quality pass: parallel technical alternatives and complete numerical relations.
def edit_options(qid,updates):
 item=next(q for q in Qs if q['id']==qid)
 for oid,(text,why) in updates.items():
  next(o for o in item['options'] if o['id']==oid)['text']=text
  item['solution']['optionExplanations'][oid]='Incorrect. '+why
 item['solution']['misconceptions']=[item['solution']['optionExplanations'][o['id']].removeprefix('Incorrect. ') for o in item['options'] if o['id'] not in item['correctOptionIds']]
edit_options('W08-L36-P1094-Q01',{
 'o2':('Check endpoint reachability while ignoring the intermediate arm configurations','A feasible pair of endpoints does not ensure that the intervening motion respects joint and collision constraints.'),
 'o3':('Minimize end-effector distance while treating joint acceleration limits as optional','The source emphasizes kinematic and dynamic limits, not length minimization at their expense.'),
 'o4':('Keep the cup center at one height and leave the motion speed unconstrained','Constant height alone does not ensure smooth transfer or compliance with the robot’s dynamic limits.')})
edit_options('W08-L36-P1094-Q02',{'o3':('Optimize the 3D centerline but check clearance only at takeoff and landing','Intermediate aerial motion must also respect obstacles and restricted regions; endpoint clearance alone is insufficient.')})
edit_options('W08-L36-P1094-Q03',{
 'o2':('All relevant obstacles can be treated as fixed once a street map is available','Traffic includes moving obstacles, which are not fully captured by a fixed map.'),
 'o3':('A minimum-distance map route automatically preserves clearance from moving vehicles','Distance optimality on a map does not establish safe separation from dynamic traffic.'),
 'o4':('The initial route can replace live obstacle observations until the destination is reached','An initial route does not remove the need to respond to changing traffic conditions.')})
edit_options('W08-L36-P1098-Q01',{'o4':('Local avoidance lets the robot keep a stale global route unchanged after any lasting blockage','A lasting blockage can require revising the overall route; local reactions do not justify retaining every stale global plan.')})
edit_options('W08-L36-P1102-Q01',{'o2':('4-connected: four corner-sharing cells; 8-connected: those four plus four edge-sharing cells','The second set has eight neighbors, but 4-connected specifically means the four edge-sharing cardinal cells, not the diagonals.')})
edit_options('W08-L36-P1112-Q02',{'o3':('It returns cost 2, which must be optimal because the goal was removed first','The first goal removal is not an optimality proof with negative edges; the supplied route through A has cost 1.')})
for item in Qs:
 if item['id']=='W08-L36-P1093-Q02':item['solution']['formulas']=[formula('L_P<L_Q; E_Q<E_P',{'L_P,L_Q':'route lengths for P and Q','E_P,E_Q':'route energy expenditures for P and Q'},{'L_P,L_Q':'m','E_P,E_Q':'J'},['Both routes are feasible; minimize one declared objective at a time.'])]
 if item['id']=='W08-L36-P1099-Q02':item['solution']['formulas']=[formula('N_free=N_r N_c−N_occ',{'N_free':'number of free cells','N_r':'number of grid rows','N_c':'number of grid columns','N_occ':'number of occupied cells'},{'all N quantities':'dimensionless counts'},['Binary grid; each cell is either free or occupied.'])]
 if item['id']=='W08-L36-P1104-Q01':item['solution']['formulas']=[formula('g(s)=0',{'s':'start vertex','g(s)':'cost of the empty route from start to itself'},{'g(s)':'the declared edge-cost unit'},['No initial traversal fee; additive edge costs.'])]
 if item['id']=='W08-L36-P1112-Q02':item['solution']['formulas'].append(formula('g_candidate(v)=g(u)+c(u,v)',{'u':'currently expanded vertex','v':'its successor','g(u)':'cost-to-come of the current route to u','c(u,v)':'cost of the directed edge from u to v','g_candidate(v)':'candidate extended-route cost'},{'all cost quantities':'abstract cost units'},['Additive directed edge costs for the explicitly supplied example.']))
 if item['id']=='W08-L36-P1100-Q01':item['stem']='What information does this lecture’s place-based graph map represent directly, while trading away fine physical-layout detail?'
for c in Cs.values():c['examinationAngles']=[q['stem'] for q in Qs if c['id'] in q['conceptIds']]

# Bound all source qualifications to the precise claims rather than silently changing the source.
def issue(name,pages,claim,basis,method,question_ids=None):
 issues.append(dict(id='L36-'+name,sourceId='lectures',sourceSha256=S,physicalPages=pages,sourceClaim=claim,qualification=basis,method=method,questionIds=question_ids or [],status='author-qualified-pending-independent-review',independentReview=False))
for item in Qs:
 if item['id'].startswith('W08-L36-P1112'):
  item['difficulty']='easy';item['assumptions'].append('All supplied counterexample weights use the same abstract cost unit.')
 if item['id'].startswith('W08-L36-P1120'):item['difficulty']='easy'
for item in Qs:
 if 'conflictResolution' in item:
  cr=item['conflictResolution'];issue(item['id'].split('-P')[1].lower(),[cr['physicalPage']],cr['sourceClaim'],cr['basis'],cr['method'],[item['id']])
issue('illustrative-pose-axes',[1096],'The illustrative pose panel’s small coordinate triad appears to label two axes Y.','Treat the illustration as a pose-versus-point-cloud example, not a reliable rotation-frame definition. Position and angle numbers are illustrative, not a derived computation.','Actual pixel inspection of the pose inset; no rotation is inferred from its ambiguous triad.')
issue('binary-grid-scope',[1099,1102],'Binary free cells and geometric 8-neighbor adjacency are described without specifying footprint inflation, unknown-cell treatment or corner cutting.','Use the source’s binary convention as stated; supply any finite-body or corner-cutting policy explicitly rather than inventing a universal default.','Compare the mapping bullets with the earlier physical-size constraint and the explicit assumptions of the new footprint/corner questions.',[q['id'] for q in Qs if 'footprint' in q['solution']['justification'] or 'no-corner-cutting' in q['stem']])
issue('frontier-duplicates',[1104,1109],'Generic expansion adds unexplored neighbors without explicitly separating already scheduled frontier entries.','The displayed BFS trace retains one queued E rather than appending E again. Distinguish discovered/frontier from expanded/closed.','Compare the literal generic pseudocode with the D-expansion frontier shown on page1109.',[q['id'] for q in Qs if 'duplicate-handling' in q['stem']])
issue('goal-expansion-count',[1117,1123],'The source says Expand G on goal removal but omits G from its reported explored count.','Retain the established convention: count successor expansions, not the successful goal removal. Existing approved questions already disclose this convention.','Compare printed explored-node lists with the final goal-removal step; no accepted question is modified.',['W08-L36-P1110-Q02','W08-L36-P1116-Q03','W08-L36-P1123-Q01'])
issue('astar-guarantee-scope',[1119,1120],'The A-star prose states optimality in terms of an admissible heuristic without spelling out graph-search reopening/consistency conditions.','Do not interpret admissibility as an unconditional theorem for every implementation. The supplied positive finite graph has an admissible, consistent heuristic, verified directly on all18 directed edge uses.','Compare all source heuristic labels with exact remaining costs, and test h(u)≤c(u,v)+h(v). General implementation conditions are explanatory qualifications, not asserted as printed course content.')
# Improve ordinary spaces in metadata without modifying literal code or existing accepted objects.
for entry in issues:
 for key in ('method','qualification'):entry[key]=entry[key].replace('page1109','page 1109').replace('all18','all 18')
write('audits/source-disputes-W08-L36.json',issues)
persist('43 nonduplicative gap drafts complete; exact author checks passed, awaiting independent review')
batch=read(f'data/question-batches/{B}.json');batch['authorChecks']=read('audits/W08-L36-gap-author-computations.json')['checks'];write(f'data/question-batches/{B}.json',batch)
# A page-by-page completeness ledger distinguishes coverage from existing accepted questions and new drafts.
ledger=[]
for p in range(1088,1127):
 oldids=[q['id'] for q in existing if any(c['physicalPage']==p for c in q['citations'])]
 newids=[q['id'] for q in Qs if any(c['physicalPage']==p for c in q['citations'])]
 ledger.append(dict(physicalPage=p,printedFooter=obs[str(p)]['printedFooter'],actualPixelsViewed=True,disposition=obs[str(p)]['disposition'],visualNotes=obs[str(p)]['notes'],originalAcceptedQuestionIds=oldids,newDraftQuestionIds=newids,coverageBasis='Excluded with recorded reason' if obs[str(p)]['disposition']=='excluded' else 'Source concepts compared against all39 original stems/solutions; new questions address distinct missing angles only.',exclusionReason=obs[str(p)]['exclusionReason']))
assert all(x['disposition']=='excluded' or x['originalAcceptedQuestionIds'] or x['newDraftQuestionIds'] for x in ledger)
write('audits/W08-L36-completeness-ledger.json',dict(batchId=B,role='author-completeness-audit-not-independent-review',sourceBounds=[1088,1126],actualPagesInspected=39,originalAcceptedCount=39,newDraftCount=len(Qs),combinedCount=39+len(Qs),pages=ledger,remainingKnownMeaningfulGaps=[],independentCoverageChallengePending=True,sourceCodePresent=False,scopeNotes=['No source programming code or notebook link is present in L36; its pseudocode and graph traces are reproduced in the author check script.','Decorative photographs and pose-panel numbers are inspected but not treated as empirical outputs or physical guarantees.','Existing approved BFS/UCS/A-star traces and summary questions are retained rather than duplicated.']))
# Validate only an in-memory integration; never write the canonical bank.
sys.path.insert(0,str(R/'scripts'));from validate import validate_bank
bank=read('data/bank.json');ins=read(f'data/inspection-batches/{B}.json')
for typ,entries in [('questions',Qs),('concepts',list(Cs.values())),('slides',ins['slides'])]:
 mp={x['id']:x for x in bank[typ]};mp.update({x['id']:x for x in entries});bank[typ]=list(mp.values())
result=validate_bank(bank,R,check_files=False);write(f'audits/{B}-integration-validation.json',result)
assert result['valid'],result['errors']
assert sha(protected['sourceBatch'])==protected['wholeBatchSha256']
if '--freeze' in sys.argv:
 blind=[{**{k:q[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions')},'citations':[{k:v for k,v in c.items() if k!='evidenceText'} for c in q['citations']]} for q in Qs]
 write(f'audits/blind-{B}.json',blind);packetsha=sha(f'audits/blind-{B}.json')
 write(f'audits/{B}-review-manifest.json',dict(batchId=B,blindPacket=f'audits/blind-{B}.json',blindPacketSha256=packetsha,questionSha256={q['id']:qhash(q) for q in Qs},preservedAcceptedCount=39,preservedAcceptedHashes=protected['questionSha256'],preservedSourceBatch=protected['sourceBatch'],preservedSourceBatchSha256=protected['wholeBatchSha256'],sourceIssuesSha256=sha('audits/source-disputes-W08-L36.json'),newQuestionCount=len(Qs),sourceBounds=[1088,1126],independentReviewPending=True))
 (R/f'audits/handoffs/{B}.md').write_text(f'# L36 coverage gap frozen\n\n43 new draft questions supplement all 39 accepted originals, whose entire search-foundations batch file and correctness hashes are unchanged. Combined L36 count82. All 39 actual pages1088–1126 were inspected, with printed footers1–39; five title/objectives/agenda/reference/closing exclusions have reasons. Nineteen new concept records and a complete page ledger distinguish new angles from original accepted coverage.\n\nPacket: audits/blind-{B}.json\nSHA256: {packetsha}\nManifest: audits/{B}-review-manifest.json\nNew batch: data/question-batches/{B}.json\nInspection: data/inspection-batches/{B}.json\nCoverage: audits/W08-L36-completeness-ledger.json\nSource issues: audits/source-disputes-W08-L36.json\nScripts: scripts/author_W08_L36_gap.py and scripts/check_W08_L36_gap.py\nChecks: audits/W08-L36-gap-author-computations.json\n\n29 author-check groups and500 generated nonnegative-graph cases pass; source BFS/UCS/A-star traces also reproduced. No source Python code is printed in L36; these are author implementations, not independent verification. All new questions need independent review and a coverage challenge. No self-approval, canonical or Git writes. Do not rerun the frozen author script. Next assigned work: L35 quality repairs.\n')
 print('FROZEN',len(Qs),'DRAFTS',packetsha)
else:print('Draft integration valid:',len(Qs),'questions')
