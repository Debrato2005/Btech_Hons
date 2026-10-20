#!/usr/bin/env python3
"""Author-side prefreeze quality edits, not independent review."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];B='W12-L58';assert not(R/f'audits/{B}-review-manifest.json').exists()
p=R/f'data/question-batches/{B}.json';b=json.loads(p.read_text());D={q['id'].split(B+'-')[1]:q for q in b['questions']}
def opt(qid,oid,t,r):
 q=D[qid];next(o for o in q['options']if o['id']==oid)['text']=t;q['solution']['optionExplanations'][oid]=('Correct. 'if oid in q['correctOptionIds']else'Incorrect. ')+r
# Same-domain misconceptions, rather than conspicuously unrelated technology.
opt('P1845-Q02','o2','DDS-based transport alone guarantees hard deadlines even if the executor and operating system are not configured for them','Communication support is only part of the end-to-end timing design.')
opt('P1846-Q01','o3','Preserve the topic name but change the pose message type and leave subscribers unchanged','A matching name does not preserve the required message type or semantic contract.')
opt('P1847-Q01','o1','Physics engine: sensor-image appearance; rendering engine: rigid-body contact; sensor engine: measurement publication','This swaps visual rendering with mechanical dynamics while retaining a plausible sensor role.')
opt('P1847-Q01','o3','Physics engine: motion/contact evolution; rendering engine: all inter-node transport; sensor engine: all scene lighting','The latter two roles belong to transport and rendering rather than the assigned engines.')
opt('P1847-Q02','o2','Physics engine','Physics computes the mechanical state; inter-component data delivery is the listed transport role.')
opt('P1848-Q01','o1','Draw walls/rooms → save and export the building → add doors/windows and textures without saving again','This exports before the final edits and omits persisting the completed building.')
opt('P1848-Q01','o2','Generate an occupancy grid with SLAM → treat that grid as the editable wall/door model → export it unchanged','A runtime occupancy raster is not the editor’s semantic building geometry workflow.')
opt('P1848-Q02','o1','It is a Gazebo Model Editor view whose primary purpose is defining robot joint constraints','The actual palette and plan concern walls, doors and buildings rather than robot link/joint authoring.')
opt('P1849-Q01','o1','Two visual shapes attached to one rigid link with no joint','Separate visual shapes inside one link remain part of the same rigid body.')
opt('P1849-Q01','o3','Two rigid links connected by a fixed joint','A fixed joint does not provide the required relative rotation.')
opt('P1849-Q02','o1','Only its inertia tensor, with collision geometry left absent','Changing inertia affects dynamics after forces are modeled; it does not supply missing contact geometry.')
opt('P1849-Q02','o3','Only its visual mesh resolution, with no collision element','A more detailed rendered surface does not automatically create the collision element.')
opt('P1849-Q03','o1','Its motion is unchanged because total mass alone determines every dynamic response','Mass distribution and the point of force application also matter for rotational response.')
opt('P1849-Q03','o2','Its contact boundary must move by the same amount even if collision geometry is unchanged','Moving the inertial center does not itself change the specified collision surface.')
opt('P1850-Q02','o1','Increase only the display refresh rate while keeping the same incorrect transforms','More frequent drawing does not repair a spatial frame mismatch.')
opt('P1850-Q02','o3','Change only the goal position until the two data layers appear aligned','A goal is navigation intent, not a calibration of the transform between displayed measurements.')
opt('P1851-Q02','o1','SDF can describe entire worlds, but each robot must always remain in a separate URDF-only representation','The individual-model SDF output on page1849 disproves the proposed restriction.')
opt('P1852-Q01','o1','A declarative XML element that, by itself, implements arbitrary C++ behavior without compiled code','A description can reference/configure a plugin, but the slide defines the plugin itself as compiled extension code.')
opt('P1852-Q01','o3','A separate ROS executable that must always run outside Gazebo and cannot be loaded into simulation','The slide specifically describes a shared library inserted into the simulator.')
opt('P1852-Q02','o2','World: one robot’s joints; Model: global environment; Sensor: toolbar extension; GUI: sensor output','This swaps world/model and sensor/GUI scopes.')
opt('P1853-Q02','o3','A scan’s correct ranges guarantee a correct global map even when the scan’s pose is wrong','Correct local measurements can still be placed at incorrect global positions.')
opt('P1854-Q01','o1','Front end solves the global trajectory optimization; back end detects and tracks sensor features','This reverses the estimation and sensor-facing roles printed in the diagram.')
opt('P1854-Q01','o2','Front end and back end independently estimate unrelated trajectories with no exchanged constraints','The arrows show observations/constraints flowing into estimation and feedback returning.')
opt('P1854-Q03','o1','Choosing the largest measurement likelihood while ignoring any prior even when it is informative','That describes maximum-likelihood rather than the supplied maximum-a-posteriori criterion.')
opt('P1854-Q03','o3','Taking the posterior mean, which must equal its maximum for every distribution','Posterior means and modes need not coincide.')
opt('P1854-Q04','o2','The estimate flows forward only, and the curved line represents an unrelated display border','The curved arrow explicitly connects the back end to the front end.')
opt('P1855-Q01','o1','White denotes occupied, black free and grey unknown in this figure','This keeps the unknown category but reverses the two observed-state labels.')
opt('P1856-Q01','o2','Launch world and spawn robot → teleoperate with no mapper or recorded sensor data → start SLAM after exploration → save','Without a mapper or recorded observations during exploration, later SLAM cannot reconstruct that unseen data from the command history alone.')
opt('P1856-Q01','o3','Launch world and spawn robot → run AMCL with no prebuilt map → treat its pose estimates as the generated occupancy map','AMCL known-map localization does not substitute for the missing mapping process.')
opt('P1856-Q02','o1','The PGM already specifies the metric resolution and map-frame origin, making YAML redundant','Those interpretation metadata are supplied by the map YAML, not by ordinary grayscale pixel values alone.')
opt('P1856-Q02','o2','The YAML is useful only for naming the robot model and has no effect on pixel-to-world interpretation','The YAML’s resolution and origin directly affect geometric interpretation.')
opt('P1857-Q01','o2','The move_base diagram and Nav2 diagram differ only in visual styling, with identical server interfaces','The different decomposition and labels should not be treated as unchanged interfaces.')
opt('P1857-Q02','o2','AMCL computes the path, while costmap_2d converts that path into velocity commands','This assigns planner/controller responsibilities to localization and map representation.')
opt('P1858-Q01','o1','Global planner → path → base controller directly, with no local velocity-generation stage','The actual figure routes the internal path through the local planner before cmd_vel.')
opt('P1858-Q01','o3','Global planner → velocity command → local planner → path → base controller','This exchanges the labeled path and velocity representations.')
opt('P1858-Q02','o3','Only to the global costmap, which then supplies all local sensor information indirectly','The figure also draws a direct sensor branch into the local costmap.')
opt('P1858-Q05','o1','Provided navigation nodes such as the planner components','The legend distinguishes provided components from the blue platform-specific ones.')
opt('P1858-Q05','o2','Optional provided nodes, such as a map source supplied by the framework','The legend uses a different category for optional provided nodes; blue marks platform-specific components.')
opt('P1859-Q03','o1','The BT Navigator manages activation states only, while the Lifecycle Manager selects recovery actions','This reverses task orchestration and lifecycle-state responsibilities.')
opt('P1859-Q03','o3','The Lifecycle Manager computes paths, while the BT Navigator directly calculates wheel velocities','Those functions belong to planner and controller algorithms rather than these coordination roles.')
opt('P1859-Q05','o2','They are aliases for the same server, so enabling both necessarily executes the same operation twice','The diagram separates path-level server work from downstream velocity-command processing.')
opt('P1859-Q05','o3','The Smoother Server filters velocity commands while the downstream Velocity Smoother refines path geometry','This reverses their path and command-level roles.')
opt('P1860-Q01','o2','It must replace every planner and controller with one monolithic geometric search algorithm','The modular task framework can call specialized algorithms rather than replace them all.')
opt('P1861-Q01','o1','A stream of near-term velocity commands sent directly to the base controller','That is the local controller’s role, distinct from a global path.')
opt('P1861-Q01','o2','A distribution of current pose hypotheses conditioned on LiDAR and odometry','That is localization rather than global path computation.')
opt('P1861-Q02','o2','A start pose expressed in odom coordinates, with no transform to the map frame','A numeric pose without a usable common-frame relation is insufficient for this map-based planning problem.')
opt('P1861-Q02','o3','A goal heading alone, while leaving the robot’s starting location unspecified','Goal orientation does not supply the missing start state.')
opt('P1862-Q01','o1','AMCL alone','AMCL estimates pose, but does not replace the local controller’s velocity computation.')
opt('P1862-Q01','o3','The global planner alone','Replanning can help, but the question asks which component generates near-term velocity commands from current state and sensing.')
opt('P1862-Q02','o3','The two algorithm names prove that their plugin parameters and message interfaces are identical','A shared task category does not establish identical implementations or interfaces.')
opt('P1863-Q01','o1','Static: current scans; obstacle: prebuilt map; inflation: elevated cost around obstacles','The static and obstacle input roles are reversed.')
opt('P1863-Q01','o3','Static: prebuilt map; obstacle: obstacle observations; inflation: delete obstacles whose cells are too close together','Inflation expands obstacle-related cost rather than erasing nearby obstacles.')
opt('P1863-Q02','o1','Only after restarting the map server and replacing the saved map image','A configured live obstacle layer can update without rewriting the static image.')
opt('P1864-Q01','o1','Use odometry alone and keep particle weights independent of the LiDAR-to-map agreement','This ignores the stated scan/map inputs to localization.')
opt('P1864-Q02','o1','Average the two corridor poses and declare that midpoint certain even if it lies inside a wall','A multimodal belief cannot generally be replaced by a physically valid certain midpoint.')
opt('P1865-Q01','o1','Ubuntu 22.04 with ROS2 Humble, but a physical LiDAR is mandatory even when Gazebo provides simulated scans','The hardware is explicitly optional for the simulation exercise.')
opt('P1865-Q01','o2','Any Ubuntu/ROS2/Gazebo combination can use exactly the same binary packages and launch files unchanged','The specified course stack is versioned; binary and launch compatibility are not universal.')
opt('P1865-Q02','o1','Feed only the rendered RGB screenshot into AMCL and omit its stated map and odometry inputs','A visualization image is not a replacement for all listed localization interfaces.')
opt('P1866-Q01','o1','Launch simulation → start known-map AMCL without a map → send goal → load the map after the robot arrives','This postpones a stated localization prerequisite until after the task.')
opt('P1866-Q01','o3','Launch simulation → load map → send goal as the initial-pose estimate → start AMCL using that destination as the current pose','The current pose estimate and desired future goal cannot be interchanged.')
opt('P1866-Q02','o2','Retrying the same goal indefinitely guarantees that a collision-free path will eventually exist','Retries do not change a persistent geometric infeasibility.')
opt('P1866-Q02','o3','Accurate localization alone is sufficient for reaching the goal despite the blocked path','Correct state estimation does not create a feasible route.')
opt('P1867-Q01','o1','Installation of navigation2 only, with nav2-bringup treated as its launch argument','Both names are apt package arguments, not a ROS launch argument.')
opt('P1867-Q01','o2','Installation of a single package whose name contains both printed package strings','Whitespace separates two package arguments in the joined command.')
opt('P1867-Q02','o1','Assigned value waffle.; repair by quoting it as TURTLEBOT3_MODEL="waffle."','Quoting preserves the unwanted period and does not change it to the recognized waffle value.')
opt('P1867-Q04','o3','The package command installs software, while export changes every already-running node’s model immediately','Export affects the current shell’s environment and subsequently launched child processes, not arbitrary existing process environments.')
opt('P1868-Q01','o3','Launch the simulator automatically even when no simulator or clock publisher is running','Choosing simulated time is not itself a simulator-launch operation.')
opt('P1869-Q01','o3','The teleop_keyboard launch description, which must be invoked with ros2 launch','The printed invocation is ros2 run with an executable, not a launch description.')
opt('P1869-Q02','o2','The input YAML map to load for localization','This is a saver output argument, not the later navigation map-input argument.')
opt('P1869-Q02','o3','The live ROS topic to remap all map messages onto','The -f option names the output map basename; topic remapping uses a separate mechanism.')
opt('P1869-Q03','o3','It guarantees that a fixed number of key presses fully observes every reachable cell','Coverage depends on actual sensor viewpoints and geometry, not solely on input count.')
opt('P1870-Q03','o2','Whether the second launch automatically attaches to the existing process without creating another instance','No such attachment behavior is established by simply repeating the launch command.')
opt('P1872-Q01','o3','They are identical whenever the robot passes through the requested position, regardless of its terminal heading','Under the explicitly enforced orientation premise, terminal heading remains part of goal satisfaction.')
opt('P1870-Q04','o3','Use waffle and the simulation clock, but pass /maps/lab.pgm instead of the YAML metadata','This fixes two faults but supplies the wrong file type for the stated map argument.')
# Narrow generic stems so distinct concepts never collide merely by wording.
stems={
'P1847-Q01':'Which mapping matches the Gazebo physics, rendering and sensor engines?',
'P1848-Q02':'How should the pictured Gazebo Building Editor interface be interpreted across versions?',
'P1852-Q02':'Which assignment matches the four Gazebo Classic plugin scopes?',
'P1854-Q01':'Which front-end/back-end division matches the SLAM architecture diagram?',
'P1857-Q02':'Which distinction between AMCL and costmap_2d matches the legacy NAV description?',
'P1858-Q01':'Which path-to-velocity chain matches the legacy move_base figure?',
'P1858-Q03':'Which odometry/transform pairing follows the legacy navigation diagram’s labels?',
'P1858-Q04':'Which goal-input/map-server distinction is directly supported by the legacy NAV figure?',
'P1859-Q01':'Which costmap-to-server association is drawn in the Nav2 architecture?',
'P1859-Q02':'Which controller-to-base command path is drawn below the Nav2 servers?',
'P1859-Q03':'Which distinction separates the BT Navigator and Lifecycle Manager in the Nav2 architecture?',
'P1859-Q04':'Which interpretation handles the Recovery/Behavior/Route server labels without conflating Nav2 distributions?',
'P1863-Q01':'Which mapping matches the static, obstacle and inflation costmap layers?',
'P1865-Q01':'Which operating-system, middleware and hardware description matches the L58 simulation platform?',
'P1869-Q01':'In ros2 run turtlebot3_teleop teleop_keyboard, which package and executable are identified?',
'P1870-Q02':'What does the navigation-launch screenshot’s Error/unknown status establish?',
'P1871-Q02':'What does navigation active, localization active and feedback unknown establish in the initial-pose screenshot?',
'P1873-Q01':'What evidence does the side-by-side Gazebo/RViz demonstration still provide?',
'P1873-Q02':'What should be recorded when comparing the burger model tree with the earlier waffle setup line?'}
for qid,s in stems.items():D[qid]['stem']=s
for q in b['questions']:
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']].removeprefix('Incorrect. ')for o in q['options']if o['id']not in q['correctOptionIds']]
p.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n');print('Refined',len(b['questions']),'drafts')
# Multi-select direct-edge reading, with separate plausible indirect targets.
q=D['P1858-Q02'];q['stem']='Select every costmap that receives a direct sensor-source branch in the displayed legacy NAV architecture.';q['selectionMode']='multi';q['options']=[{'id':'o1','text':'Global costmap'},{'id':'o2','text':'Local costmap'},{'id':'o3','text':'Global planner directly, bypassing its costmap'},{'id':'o4','text':'Local planner directly, bypassing its costmap'}];q['correctOptionIds']=['o1','o2'];q.pop('optionCountRationale',None)
q['solution']['optionExplanations']={'o1':'Correct. The sensor branch enters the global costmap before that map informs the global planner.','o2':'Correct. The sensor branch also enters the local costmap.','o3':'Incorrect. The drawn direct target is the global costmap, which then supplies the planner.','o4':'Incorrect. The drawn direct target is the local costmap, which then supplies the local planner.'};q['solution']['justification']='Both global and local costmaps receive the sensor branch; the planners consume the map representations downstream.';q['solution']['simpleExplanation']=q['solution']['justification'];q['solution']['misconceptions']=[v.removeprefix('Incorrect. ')for k,v in q['solution']['optionExplanations'].items()if k not in q['correctOptionIds']]
q=D['P1862-Q03'];f=q['solution']['formulas'][0];f['expression']=f['expression'].split('; d_clear=')[0]+'; d_clear=d_obstacle−d_stop';f['variables'].update(d_clear='Remaining clearance after ideal stopping',d_obstacle='Initial obstacle distance from leading robot boundary');f['units']['d_clear,d_obstacle']='m'
if 'P1861-Q04' in D:
 oid=next(o['id'] for o in D['P1861-Q04']['options'] if o['text'].startswith(('Global planning: AMCL','Global planning: NavFn and DWA')))
 opt('P1861-Q04',oid,'Global planning: NavFn and DWA; local planning/control: Smac, Theta Star and TEB','This mixes members of the two source lists rather than preserving their task grouping.')
p.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
D['P1867-Q02']['solution']['steps'][-1]='The explicitly repaired right-hand value is "waffle", without the period.'
for q in b['questions']:
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']].removeprefix('Incorrect. ')for o in q['options']if o['id']not in q['correctOptionIds']]
 for field in ['stem']:q[field]=q[field].replace('page1849','page 1849')
 q['solution']['optionExplanations']={k:v.replace('page1849','page 1849')for k,v in q['solution']['optionExplanations'].items()}
p.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
D['P1859-Q03']['primaryEvidence']=[dict(title='Nav2 Lifecycle Manager',url='https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/core_servers/configuring_lifecycle_manager/',locator='Managed nodes transition through configuration/activation in a controlled order.',version='Jazzy documentation inspected 2026-10-20; conceptual role only',checkedAt='2026-10-20')]
p.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
D['P1859-Q05'].setdefault('primaryEvidence',[]).append(dict(title='Nav2 Velocity Smoother',url='https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/configuring_velocity_smoother/',locator='Velocity/acceleration/deadband smoothing in the controller-to-robot command path.',version='Rolling documentation inspected 2026-10-20; role only, not asserted Humble defaults',checkedAt='2026-10-20'))
p.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
