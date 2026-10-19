"""Rebuild L05 authored slice. Source files are read-only; reviews remain separate."""
import json,datetime,hashlib,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash
BATCH='W01-L05';AUTHOR='define_robotics_data_contracts:L05-author';HASH='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'
NOTES={171: 'Printed 1. Title slide identifies Lecture Number 5 and Introduction to ROS; logos and building '
      'photograph, no independent technical proposition.',
 172: 'Printed 2. Learning objectives list middleware, nodes/packages/graph, topics/services/parameters, '
      'sensing-compute-actuation, Jetson and URDF/TF. Objectives only.',
 173: 'Printed 3. Content outline covers history, middleware, MOSA, Jetson, communication, sensor loop, '
      'URDF/TF and sim-to-real. Agenda only.',
 174: 'Printed 4. Definition and four cards: open source with BSD/Apache-2.0/community wording; middleware '
      'abstraction; ecosystem counts of 1000+ packages and 10000+ users; ROS 2 support for Linux, macOS and '
      'Windows. Counts are source claims, not current measurements.',
 175: 'Printed 5. Timeline rows: 2007 Stanford/Player-Stage; 2010 ROS 1.0/Willow Garage; 2013 OSRF; 2017 ROS '
      '2 Alpha to Crystal, first stable; 2020 Noetic/Foxy; 2022 Humble, five years; 2024 Jazzy, latest. '
      'Exact chronology and latest wording remain flagged, especially the 2017/Crystal row.',
 176: 'Printed 6. Six cards: multi-robot without central authority; embedded systems; real-time '
      'deterministic execution; production reliability; security encryption/authentication; vendor-neutral '
      'DDS. These are capabilities or goals, not automatic configured guarantees.',
 177: 'Printed 7. Four-layer figure, bottom to top: hardware; Ubuntu host OS on Jetson; ROS middleware with '
      'communication/messages/tools; application with Python AI/navigation. Body distinguishes middleware '
      'from traditional operating system.',
 178: 'Printed 8. Plumbing analogy: programs are rooms, data is water, ROS communication is pipes/IPC. '
      'Images, sensor readings and movement commands illustrate exchanged data.',
 179: 'Printed 9. MOSA uses a standardized outlet analogy. Navigation and speech modules can be '
      'developed/tested separately, and compatible drivers reused. Standardization is not a plug-anything '
      'guarantee.',
 180: 'Printed 10. Slow CNN perception is decoupled from faster control/safety processing. Standard message '
      'inputs connect AI to drivers. Essential wording does not establish that ROS is uniquely necessary.',
 181: 'Printed 11. The course uses a Jetson Orin Nano host for GPU-assisted vision and middleware '
      'coordination, alongside a simpler Arduino motor-control role. Centralization is the example '
      'architecture, not a universal requirement.',
 182: 'Printed 12. Six building blocks: nodes perform tasks; topics carry continuous data; services provide '
      'request/response; actions combine communication for goals; messages define data formats; packages '
      'organize files. Final package line overlaps the footer but is readable.',
 183: 'Printed 13. Single-purpose computational nodes divide camera, detection and motor responsibilities. '
      'The camera/LiDAR/control and SLAM/navigation diagram has lines without arrowheads, so it does not '
      'define a directed message trace.',
 184: 'Printed 14. Separate-process example limits direct crash propagation. GPU vision and CPU planning '
      'appear in the diagram. Process survival does not prove safe control, and one-node-one-process or '
      'automatic scheduling is not a universal invariant.',
 185: 'Printed 15. A package groups source, configuration and data. Worker/workplace analogy contrasts '
      'running nodes and organizational folders; camera/detection/motor folders appear above runtime-node '
      'boxes.',
 186: 'Printed 16. Directed chain: Camera Node -- /camera/raw --> AI Detection -- /detected_objects --> '
      'Navigation -- /cmd_vel --> Drive. These exact names differ from the /image_raw example elsewhere.',
 187: 'Printed 17. Visually read code imports rclpy and Node, declares class MyNode(Node), calls '
      "super().__init__('my_node'), and uses main with init, node construction, spin and shutdown. "
      'Screenshot code was absent from extracted text.',
 188: 'Printed 18. Camera publisher at 30 Hz sends sensor_msgs/Image through /image_raw to a vision '
      'subscriber/callback. Pub-sub is asynchronous and permits multiple publishers/subscribers.',
 189: 'Printed 19. Radio transmitter maps to publisher, frequency/channel to topic and receivers to '
      'subscribers. The 98.7 FM illustration fans out to three receivers. Agreement on topic name and '
      'message type is highlighted but is not a complete QoS/network guarantee.',
 190: 'Printed 20. Messages are structured interfaces. sensor_msgs/Image carries raw camera data; '
      'geometry_msgs/Twist expresses linear/angular velocities. The 4K-transfer discussion gives no measured '
      'throughput or zero-copy guarantee.',
 191: 'Printed 21. Publisher uses create_publisher and create_timer to invoke publish_msg; subscriber uses '
      'create_subscription and callback(msg) on message arrival. Timer and subscription triggers differ.',
 192: 'Printed 22. PubSubNode screenshot creates a String publisher and subscriber on topic, with argument '
      '10, plus create_timer(0.1, self.publish_msg), commented 10 Hz. publish_msg sets data to Hello ROS and '
      'publishes. callback prints Received: followed by msg.data. Imports/main are omitted in this excerpt.',
 193: 'Printed 23. Services use on-demand client/server request-response rather than continuous streams. '
      'Guaranteed-response and universally synchronous wording is overbroad; printed slide 29 explicitly '
      'uses call_async.',
 194: 'Printed 24. Client request and server response, phone-call analogy, typical waiting, multiple clients '
      'and one intended server. Reset-map and snapshot examples. One-server wording is treated as a design '
      'convention rather than a universal enforcement claim.',
 195: 'Printed 25. Untitled diagram: Nav Node client on the left sends get_map() to Map Node server on the '
      'right. A reverse arrow returns OccupancyGrid. Both arrow directions were visually inspected.',
 196: 'Printed 26. Action diagram includes goal, accepted, feedback, result and cancel; text allows '
      'acceptance/rejection and uses navigate_to_pose. Cancellation capability does not imply unconditional '
      'success after completion. The three-topics-internally statement remains flagged rather than treated '
      'as a complete ROS 2 transport inventory.',
 197: 'Printed 27. Node-local named configuration values include string/integer/boolean examples and runtime '
      'exposure/brightness adjustments. Runtime effects require supported updates consumed by active logic.',
 198: 'Printed 28. Services use a name and request-response interface with availability checking. Parameters '
      'are declared with defaults in construction and read later. Availability is distinct from a completed '
      'result.',
 199: 'Printed 29. MyNode screenshot declares speed with default 1.0, creates AddTwoInts service/client '
      'named add, waits using wait_for_service(timeout_sec=1.0), and invokes send_request. Handler sets '
      'response.sum = request.a + request.b. Request operands are 2 and 3; call_async returns future, but no '
      'result read appears. The later print reads the speed parameter.',
 200: 'Printed 30. Depth camera/LiDAR input, with USB/CSI examples, is published through sensor drivers. GPU '
      'perception subscribes and detects; decision logic selects movement. Connection examples are not '
      'universal for every sensor.',
 201: 'Printed 31. Chain: 3D camera; sensor_msgs/Image; Jetson ROS/Python AI/GPU; serial-data/PWM label; '
      'Arduino/motor shield; H-bridge; DC motors; physical motion. Body assigns precise PWM timing to the '
      'low-level microcontroller, not to CNN inference.',
 202: 'Printed 32. URDF is XML for appearance, dimensions and kinematic structure. Rigid links have visual, '
      'collision and inertial properties. Joint examples are fixed camera mount, continuous wheel and '
      'revolute arm hinge. A model property alone is not a safety certificate.'}
NOTES.update({
203: 'Printed 33. TF represents mathematical relations between coordinate frames in 3D. The tree example places camera_link below base_link; non-root frames have one parent and may have children. URDF is the blueprint, while TF supplies changing frame relations. The /tf topic distributes transforms. Exactness and availability require valid, timely transforms, not merely subscription.',
204: 'Printed 34. robot_state_publisher takes robot_description (URDF structure) and /joint_states (current joint positions), applies forward kinematics, and publishes frame transforms. The diagram labels /tf as a live 3D map; this is not an occupancy map or a physics simulation. The slide omits the fixed-transform /tf_static distinction, so questions avoid treating all transforms as dynamic /tf messages.',
205: 'Printed 35. Sim-to-real uses middleware abstraction and common interfaces to reuse robot computation. Gazebo supplies simulated physical effects; RViz visualizes robot data. Minimal code changes is a design aim, not proof of identical real-world behavior.',
206: 'Printed 36. Replace a Simulation Bridge with a Hardware Driver while keeping interfaces such as /cmd_vel stable. The diagram contrasts Gazebo/RViz and a Jetson robot. Interface reuse does not guarantee matching friction, noise, delay, or dynamics.',
207: 'Printed 37. RViz2 display cards show TF Frames, PointCloud2, LaserScan, Image, OccupancyGrid, MarkerArray, Path, and RobotModel. PointCloud2 is a 3D point cloud; LaserScan is a 2D scan; Path shows planned trajectories; RobotModel shows URDF geometry. The OccupancyGrid card says 2D or 3D maps, an overbroad interface claim held for adjudication.',
208: 'Printed 38. Gazebo cards cover rigid-body physics and collisions, simulated cameras/LiDAR/IMU/GPS, bidirectional ros_gz topic bridging, SDF worlds/models, Ignition-to-Gz naming, and hardware-in-the-loop. Engine and release names are version-dependent examples rather than current installation guidance; bridge configuration matters for ROS messages.',
209: 'Printed 39. Summary connects small cooperating programs, topics/services/parameters, Jetson AI processing, the sense-think-act loop, and URDF/TF body-space representation. No numerical timing or unconditional real-time guarantee is provided.',
210: 'Printed 40. Four bibliography entries only, with no independent technical proposition. Reference-only exclusion.',
211: 'Printed 41. Thank You closing courtesy slide only; no technical content.'
})
CONCEPTS=[];QUESTIONS=[]
def C(key,pages,title,description,subtopic='ROS foundations',status='identified'):
 if isinstance(pages,int):pages=[pages]
 cid=BATCH+'-C-'+key
 CONCEPTS.append({'id':cid,'title':title,'description':description,'slideIds':[f'lectures-p{p:04d}' for p in pages],'questionIds':[],'status':status,'topic':'Robot Operating System','subtopic':subtopic,'prerequisiteConceptIds':[]})
 return cid

def Q(num,pages,keys,stem,options,answers,rationales,justification,*,difficulty='medium',type='conceptual',skill='conceptual',assumptions=None,steps=None,formulas=None,traps=None,simple=None,kind='statement'):
 if isinstance(pages,int):pages=[pages]
 if isinstance(keys,str):keys=[keys]
 assert len(options)==len(rationales)
 ids=[f'o{i+1}' for i in range(len(options))]
 qs={'id':f'{BATCH}-Q-{num:03d}','version':1,'status':'draft','authorId':AUTHOR,'stem':stem,'selectionMode':'multi' if len(answers)>1 else 'single','type':type,'difficulty':difficulty,'cognitiveSkill':skill,'week':1,'lectureId':'L05','topic':'Robot Operating System','subtopic':next(c['subtopic'] for c in CONCEPTS if c['id']==BATCH+'-C-'+keys[0]),'tags':['L05','ROS','source-bounded'],'conceptIds':[BATCH+'-C-'+k for k in keys],'assumptions':assumptions or [],'options':[{'id':oid,'text':t} for oid,t in zip(ids,options)],'correctOptionIds':[ids[i] for i in answers],'citations':[{'slideId':f'lectures-p{p:04d}','sourceId':'lectures','sourceSha256':HASH,'physicalPage':p,'kind':kind,'locator':f'Lecture 5, printed slide {p-170}; '+NOTES[p],'evidenceText':NOTES[p],'role':'premise' if skill in ['numerical','algorithm','synthesis'] else 'explicit','region':None} for p in pages],'solution':{'justification':justification,'optionExplanations':dict(zip(ids,rationales)),'steps':steps or [],'formulas':formulas or [],'simpleExplanation':simple or justification,'memoryAid':None,'misconceptions':traps or [],'examTraps':traps or [],'prerequisiteConceptIds':[]},'origin':'generated','reviewIds':[]}
 # Stable IDs never encode display positions; varied authored display orders.
 k=num%len(qs['options']);qs['options']=qs['options'][k:]+qs['options'][:k]
 QUESTIONS.append(qs)

# Incremental files hold explicit authored content, not templates expanded into paraphrases.
for name in ['author_W01_L05_concepts.py','author_W01_L05_questions.py','refine_W01_L05.py']:
 p=ROOT/'scripts'/name
 if p.exists():exec(compile(p.read_text(),str(p),'exec'))

def save():
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 for q in QUESTIONS:
  for cid in q['conceptIds']:
   c=next(c for c in CONCEPTS if c['id']==cid);c['questionIds'].append(q['id'])
   if c['status']=='identified':c['status']='drafted'
 maps={s['physicalPage']:s for s in [json.loads(l) for l in (ROOT/'sources/page_maps/lectures.jsonl').read_text().splitlines()]}
 slides=[]
 for p,n in NOTES.items():
  s=copy.deepcopy(maps[p]);s.update({'disposition':'excluded' if p in [171,172,173,210,211] else 'examinable','exclusionReason':'Title, objectives, outline, references, or closing courtesy only; no independent technical proposition.' if p in [171,172,173,210,211] else None,'conceptIds':[c['id'] for c in CONCEPTS if s['id'] in c['slideIds']],'printedSlideNumber':str(p-170),'printedSlideNumberStatus':'present','text':(ROOT/f'sources/text/lectures/page-{p:04d}.txt').read_text(),'visualInspection':{'status':'complete','inspectorId':AUTHOR,'inspectedAt':now,'method':'rendered_page','notes':f'Individually viewed sources/previews/lectures/page-{p:04d}.webp at 1800x1013 with extracted text. '+n}});slides.append(s)
 for directory in ['data/question-batches','data/inspection-batches','audits']:(ROOT/directory).mkdir(exist_ok=True)
 obj={'schemaVersion':'1.0.0','batchId':BATCH,'authorId':AUTHOR,'sourceVersions':{'lectures':HASH},'physicalPageRange':[171,211],'status':'draft_partial_coverage','questions':QUESTIONS,'concepts':CONCEPTS,'reviews':[],'coverage':{'pagesInspected':len(slides),'pagesTotal':41,'questionsDraft':len(QUESTIONS),'questionsVerified':0,'identifiedConcepts':len(CONCEPTS),'conceptsWithDrafts':sum(bool(c['questionIds']) for c in CONCEPTS),'complete':False,'notes':'Incremental authored slice; source issues and unanswered concepts stay visible. Independent answer review and exhaustive coverage challenge are pending.'}}
 (ROOT/f'data/question-batches/{BATCH}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 (ROOT/f'data/inspection-batches/{BATCH}.json').write_text(json.dumps({'schemaVersion':'1.0.0','batchId':BATCH,'slides':slides},ensure_ascii=False,indent=2)+'\n')
 blind=[{**{k:q[k] for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']},'questionSha256':question_hash(q)} for q in QUESTIONS]
 (ROOT/f'audits/blind-{BATCH}.json').write_text(json.dumps({'schemaVersion':'1.0.0','batchId':BATCH,'status':'not_frozen_authoring','questions':blind},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(obj['coverage']))
if __name__=='__main__':
 if (ROOT/'audits/FROZEN-W01-L05.json').exists():
  raise SystemExit('L05 is frozen. Reconcile its freeze and review state before any author regeneration.')
 save()
