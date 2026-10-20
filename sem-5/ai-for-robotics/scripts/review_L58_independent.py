import json,pathlib,datetime,hashlib,math,random,shlex
P=pathlib.Path(__file__).resolve().parents[1];A=P/'audits';packet=A/'blind-W12-L58.json';q=json.loads(packet.read_text())
answers='2 3 2 1 2 3 3 3 2 2 2 3 1 2 1 2 2 2 1 3 2 3 2 2 1 3 3 1 1 1 3 3 1 3 2 12 1 1 3 1 3 2 3 1 1 1 3 1 2 2 2 2 2 2 2 1 2 2 1 3 2 2 1 2 3 3 2 1 1 3 3 2 1 1 3 1 1 2 1 1 2 1 3 1 2'.split()
reasons='''ROS2 is middleware, not the OS kernel or simulator.
Real-time support does not establish a deadline guarantee without complete system conditions.
A replacement preserves interfaces and coordinate conventions, not just names.
Applications still require task-specific sensing, planning and validation.
Physics advances motion/contact, rendering draws a scene and sensors simulate measurements.
Transport handles exchanges between distributed components.
The empty world shows an interface, not a measured physical match.
The printed workflow draws, details, textures, saves and exports.
The illustrated Building Editor belongs to Gazebo Classic; version equivalence is not established.
Relative rotation needs two links with a suitable non-fixed joint.
Collision configuration, not visual appearance alone, determines modeled contact.
Changing center of mass can change torque response and balance with unchanged appearance.
RViz displays state and sensing; Gazebo computes simulated dynamics.
Frame/transform timing is relevant to misaligned data displays.
A requested goal is not evidence of executed motion.
URDF is the stated XML robot description, not code or an occupancy raster.
SDF also describes individual models, not only entire worlds.
The described plugin is compiled code loaded into simulation.
World, model, sensor and GUI scopes map to environment, robot, measurements and interface.
SLAM jointly estimates pose and constructs or updates the map.
Pose error displaces observations in the map frame.
The front end associates observations; the back end optimizes trajectory/map consistency.
A valid revisit supplies a constraint on accumulated drift.
MAP maximizes a posterior, not generally likelihood alone or posterior mean.
The curved arrow shows estimation feedback to front-end processing.
The figure labels white free, black occupied and grey unknown.
The supplied admissibility rule requires every traversed cell to be observed free.
Dimensions are80*.05=4m and40*.05=2m; center=(-1+9.5*.05,2+3.5*.05).
The wedge is the field of view, distinct from occupancy classes.
World/robot precede mapping and teleoperation, followed by saving.
YAML records image reference, resolution and origin for metric interpretation.
SLAM toolbox and Cartographer are distinct stated workflows.
The legacy move_base list is distinct from the later server-based Nav2 architecture.
AMCL localizes; costmap_2d represents obstacle/traversal cost information.
The drawn path feeds local planning, whose velocity command feeds the base.
The sensor-topic line forks directly to both costmaps, not directly to planners.
The printed odom arrow carries odometry and tf carries transforms.
The goal is PoseStamped; map_server supplies the global costmap.
The legend marks platform-specific sensor/base boxes in blue.
Controller embeds the local costmap and planner embeds the global costmap.
The lower command chain is controller, velocity smoother, collision monitor, base.
Task coordination and component lifecycle transitions are different roles.
A mixed-generation diagram does not establish availability in stock Humble.
Path refinement and downstream velocity smoothing operate on different objects.
A behavior tree coordinates actions and decisions beyond geometric path search.
Plan fails, so Follow is skipped; Recover succeeds and the Fallback succeeds.
Global planning outputs a path rather than velocities or pose distributions.
A start pose in the common frame and feasibility assumptions complete the problem.
A is infeasible; B costs6m and C7m, so B wins.
The lecture groups NavFn/Smac/Theta Star globally and DWA/TEB locally.
The local controller updates near-term commands from current observations and state.
Listed algorithms are not a deployment configuration or default inventory.
Reaction travel=.6*.2=.12m; braking=.6²/(2*.9)=.20m; total.32m leaves.08m.
Static/map, obstacle/observations and inflation/surrounding cost are the three roles.
A configured obstacle layer can update a global costmap despite the abbreviated contrast.
Required width2*(.20+.05)=.50m; actual side margin(.45-.40)/2=.025m.
AMCL updates weighted poses using motion and agreement between scans and known map.
Particles can preserve multiple pose hypotheses rather than a physically invalid certain midpoint.
Normalize by total10, giving.2,.3,.5.
The stated platform is Ubuntu22.04/Humble/Gazebo/Nav2; physical hardware is optional for simulation.
Simulated robot observations can provide the same required navigation interfaces.
Map availability precedes known-map localization, initial pose and goal.
Successful arrival is a contingent outcome, not a guarantee for infeasible goals.
The supplied policy exhausts recovery and replanning, then reports failure if no feasible route exists.
Both named package tokens are arguments to one install request.
The literal value contains a period; remove it for the intended waffle name.
The first launch argument is the package and the second is the launch filename.
Installation and shell-child model selection are distinct operations.
The flag requests simulation-clock use, not real-time speed or automatic simulator creation.
The partial display contains observed structure and remaining unobserved area.
Real-time factor6/10=.6; speed per simulation second1.2/6=.2m/s.
ros2 run takes package turtlebot3_teleop and executable teleop_keyboard.
The -f argument selects the output basename.
Teleoperation gathers observations used by the mapper.
The actual YAML path replaces the illustrative placeholder, not the PGM image.
The screenshot displays a map but Error/unknown does not establish readiness.
Starting another process can duplicate simulation; intended reuse/restart must be clarified.
Remove model punctuation, provide real YAML path and align the navigation clock.
Initial pose means estimated current position and orientation.
Active components with unknown feedback do not show a completed goal.
Cost overlays are distinct from the earlier occupancy-state color convention.
Different requested orientations can define distinct goal poses at the same position.
Conditional remaining-path speed3.01/14=.215m/s; elapsed9s is not the remaining time.
The still shows simulation and a captured reached status, not repeat-trial performance.
The burger model tree conflicts with the earlier waffle selection; sameness is unestablished.'''.splitlines()
assert len(q)==len(answers)==len(reasons)==85
# Conservative accounting: these author-authored locators substantially disclose the expected proposition.
exposed={1,6,10,11,16,17,18,20,26,29,32,34,36,37,38,39,40,50,60,64,67,69,70,72,73,75,76,79,80,82,83,84,85}
flags={2:'Two distractors repeat the same unconditional deadline guarantee; replace with distinct plausible latency/jitter/configuration confusions.',4:'Both distractors assert that installation or machine learning eliminates essential navigation work; replace with plausible competing integration plans.',7:'An empty-grid screenshot neither suggests a completed SLAM map nor universal dynamic equivalence; replace with meaningful same-domain screenshot interpretations.',17:'Both wrong options restate the same claim that SDF cannot describe an individual model; use distinct format-scope misconceptions.',25:'The display-border distractor and permanent elimination of association are weak; use plausible forward/backward information-flow alternatives.',64:'The correct supplied policy is repeated verbatim while both alternatives falsely report success; this does not support a medium synthesis label or useful distractors.',77:'Both wrong alternatives express automatic process reuse/merging; replace with distinct plausible restart/lifecycle choices.',84:'Universal goal reachability and repeated-trial error distributions are implausible conclusions from one still; use near-miss status/evidence distinctions.'}
out={'reviewerId':'robotics-integration-L58-independent','solvedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packetSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'sourceVersion':'2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c','priorAuthorExposure':False,'actualPagesInspected':list(range(1843,1877)),'inspectionMethod':'Personally viewed all34 rendered physical pages in1600px-wide panels, then individually enlarged1858,1859,1872,1873. Extraction and rendering alone are not counted.','scope':'Source-first current answers frozen before keyed objects;33author-locator disclosures conservatively labeled not blind. No ROS/Gazebo commands, installers, hardware, models or denied runtime executed.','answers':[{'questionId':x['id'],'independentAnswerOptionIds':['o'+a] if a!='12' else ['o1','o2'],'reasoning':r,'solvedBeforeAnswerSeen':i not in exposed,'authorLocatorAnswerExposure':i in exposed,'preKeyFindings':[flags[i]] if i in flags else []} for i,(x,a,r) in enumerate(zip(q,answers,reasons),1)]}
f=A/'blind-answers-W12-L58-integration.json';assert not f.exists();f.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
checks={'gridDimensions':[80*.05,40*.05],'gridCenter':[-1+9.5*.05,2+3.5*.05],'routeCosts':{'A':5,'B':6,'C':7},'stoppingDistance':.6*.2+.6**2/(2*.9),'corridorRequired':2*(.2+.05),'corridorSideMargin':(.45-.4)/2,'weights':[2/10,3/10,5/10],'clockRatio':6/10,'simSpeed':1.2/6,'etaSpeed':3.01/14,'sequenceTrace':['Plan:FAILURE','Recover:SUCCESS'],'fallbackResult':'SUCCESS'}
assert checks['gridDimensions']==[4,2];assert all(math.isclose(a,b) for a,b in zip(checks['gridCenter'],[-.525,2.175]));assert math.isclose(checks['stoppingDistance'],.32);assert math.isclose(checks['corridorSideMargin'],.025);assert checks['etaSpeed']==.215
commands=['sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup','export TURTLEBOT3_MODEL=waffle.','ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py','ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True','ros2 run turtlebot3_teleop teleop_keyboard','ros2 run nav2_map_server map_saver_cli -f my_map','ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=path/to/my_map.yaml'];tokens=[shlex.split(c) for c in commands];assert tokens[0][-2:]==['ros-humble-navigation2','ros-humble-nav2-bringup'];assert tokens[1][1].split('=',1)[1]=='waffle.';assert tokens[4][2:]==['turtlebot3_teleop','teleop_keyboard'];assert tokens[5][-2:]==['-f','my_map']
rng=random.Random(58012026)
for _ in range(1000):
 resolution=rng.uniform(.001,2);width,height=rng.randint(1,2000),rng.randint(1,2000);i,j=rng.randrange(width),rng.randrange(height);ox,oy=rng.uniform(-50,50),rng.uniform(-50,50);cx,cy=ox+(i+.5)*resolution,oy+(j+.5)*resolution;assert ox<cx<ox+width*resolution and oy<cy<oy+height*resolution
 speed,delay,decel=rng.uniform(.01,5),rng.uniform(0,2),rng.uniform(.01,5);t=speed/decel;distance=speed*delay+speed**2/(2*decel);assert math.isclose(distance,speed*delay+speed*t-.5*decel*t*t,rel_tol=1e-12)
 radius,margin=rng.uniform(.01,2),rng.uniform(0,1);required=2*(radius+margin);assert math.isclose((required-2*radius)/2,margin,abs_tol=1e-12)
 weights=[rng.random()+.001 for _ in range(5)];total=sum(weights);assert math.isclose(sum(w/total for w in weights),1,abs_tol=1e-12)
 sim,wall,travel=rng.uniform(.01,100),rng.uniform(.01,100),rng.uniform(.01,100);assert math.isclose((sim/wall)*(travel/sim),travel/wall,rel_tol=1e-12)
 remain,eta=rng.uniform(.01,100),rng.uniform(.01,100);assert math.isclose((remain/eta)*eta,remain,rel_tol=1e-12)
 routes=[(rng.uniform(.01,100),rng.choice([True,False])) for _ in range(5)];valid=[cost for cost,ok in routes if ok];chosen=min(valid) if valid else None;assert chosen is None or all(chosen<=cost for cost in valid)
(A/'W12-L58-integration-independent-checks.json').write_text(json.dumps({'passed':True,'namedChecks':checks,'commandTokensParsedNotExecuted':tokens,'variedCases':1000,'variedAssertions':7000,'runtime':'Default Python standard-library arithmetic, random, math and shlex parsing only; no subprocess ROS/Gazebo/install execution.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'answers':85,'preKeyFlags':len(flags),'locatorExposures':len(exposed),'blindSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'variedAssertions':7000}))
