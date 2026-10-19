"""One-time source-based repairs and compact gap closure, preserving untouched hashes."""
from pathlib import Path
import json,copy,datetime
from validate import question_hash
from authoring_helpers import SHA
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W01-L05.json';b=json.loads(p.read_text());old=copy.deepcopy(b)
archive=R/'audits/batch-history/W01-L05-before-coverage-repairs.json'
if archive.exists():assert json.loads(archive.read_text())==old, 'Already applied or source changed; do not overwrite.'
else:archive.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
reviews=json.loads((R/'data/reviews/W01-L05-coverage-quality-independent.json').read_text());flagged={r['questionId'] for r in reviews};changed=flagged|{'W01-L05-Q-009','W01-L05-Q-031'}
qs={int(q['id'][-3:]):q for q in b['questions']}
for q in b['questions']:
 if q['id'] not in changed:continue
 h=question_hash(q);q['version']+=1;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append('robotics-integration-L05-coverage-revision-author')
 q.setdefault('revisionHistory',[]).append({'version':q['version'],'authorId':'robotics-integration-L05-coverage-revision-author','priorQuestionSha256':h,'reason':'Targeted quality repairs and documented source-angle gap extensions after independent whole-lecture coverage challenge.','revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
for r in reviews:
 if not r['checks']['difficulty']:
  q=qs[int(r['questionId'][-3:])];q['difficulty']='easy';q['cognitiveSkill']='recall'
def setq(n,stem,opts,why,exps,key=1):
 q=qs[n];q['stem']=stem
 for o in q['options']:o['text']=opts[int(o['id'][1:])-1]
 q['correctOptionIds']=[f'o{key}'];q['selectionMode']='single';q['solution']['justification']=why;q['solution']['simpleExplanation']=why;q['solution']['optionExplanations']={f'o{i+1}':e for i,e in enumerate(exps)};q['solution']['misconceptions']=[e for i,e in enumerate(exps) if i+1!=key]
def cite(n,page,kind='statement'):
 q=qs[n]
 if any(c['physicalPage']==page for c in q['citations']):return
 q['citations'].append(dict(slideId=f'lectures-p{page:04d}',sourceId='lectures',sourceSha256=SHA,physicalPage=page,kind=kind,locator=f'Lecture 5, physical PDF page {page}, printed slide {page-170}: stated example',evidenceText=(R/f'sources/text/lectures/page-{page:04d}.txt').read_text().strip(),role='explicit',region=None))
def concept(n,key,title,description,pages):
 cid=f'W01-L05-C-{key}';qs[n]['conceptIds'].append(cid);b['concepts'].append(dict(id=cid,title=title,description=description,slideIds=[f'lectures-p{p:04d}'for p in pages],questionIds=[qs[n]['id']],status='drafted',topic='Robot Operating System',subtopic=title,prerequisiteConceptIds=[]))
setq(2,'Which interpretation correctly matches the ecosystem and cross-platform cards, using the slide as a course description rather than a current census?',[
 'Ecosystem means several CPU cores in one host; cross-platform means several motor types in one robot',
 'Ecosystem highlights reusable packages and users; cross-platform names Linux, macOS and Windows as ROS 2 hosts',
 'Ecosystem counts certify each package on every host; cross-platform guarantees identical drivers for those hosts',
 'Ecosystem counts measure communication latency; cross-platform identifies the required robot chassis geometries'],
 'The cards describe packages/users and named operating-system hosts; they do not provide current measurements, certification of every package, or timing data.',[
 'This confuses a software community with processing cores and host platforms with motor hardware.',
 'Correct: these are the two advertised categories, without turning source counts into a live inventory.',
 'The cards do not certify every package/driver combination merely by naming hosts.',
 'Package/user counts are not latency measurements, and the listed platforms are operating systems.'],key=2)
# Preserve the original four feature associations and add the missing production-readiness card.
q=qs[3];q['options'].append({'id':'o5','text':'Production Ready: the card associates mature reliability with commercial and industrial deployment'})
q['correctOptionIds'].append('o5');q['solution']['optionExplanations']['o5']='Correct as a description of the card’s claimed application; it does not certify this robot’s reliability or deadlines.'
q['solution']['justification']+=' The Production Ready card adds mature reliability for commercial and industrial deployment, not an automatic validation result.';q['solution']['simpleExplanation']=q['solution']['justification']
concept(3,'production-readiness','Production-readiness feature claim','The source associates maturity and reliability with commercial/industrial deployment; each actual system still requires validation.',[176])
setq(9,'Which allocation matches both the course’s Jetson/microcontroller example and its within-Jetson CPU/GPU illustration?',[
 'Jetson vision uses GPU assistance, path planning uses the CPU, and the microcontroller handles low-level motor control',
 'Jetson vision uses the CPU, path planning uses the GPU, and the microcontroller handles low-level motor control',
 'The microcontroller performs vision and path planning, while Jetson supplies only low-level PWM timing',
 'Jetson vision uses the GPU, the microcontroller performs path planning, and the CPU supplies the pictured low-level motor controller'],
 'The illustrated allocation places vision on the GPU, planning on the CPU, and actuator-facing low-level control on the microcontroller.',[
 'Correct: this combines the two stated architectural levels.',
 'This swaps the Vision Node GPU and Planning Node CPU labels in the illustration.',
 'This reverses the high-level versus low-level allocation.',
 'The example assigns the microcontroller the low-level motor role, not the planning role.'])
cite(9,184,'figure');concept(9,'heterogeneous-allocation','CPU/GPU node allocation','The source illustrates GPU-assisted vision and CPU path planning; it does not demonstrate automatic pinning, optimal scheduling, or deadline guarantees.',[184])
qs[9]['assumptions']=['This is the course’s illustrated allocation, not a requirement for every robot or an automatic scheduling guarantee.']
setq(14,'According to the directed graph, which full chain carries information from camera acquisition to drive commands?',[
 'Camera → /camera/raw → AI Detection → /detected_objects → Navigation → /cmd_vel → Drive',
 'Camera → /camera/raw → Navigation → /detected_objects → AI Detection → /cmd_vel → Drive',
 'Camera → /detected_objects → AI Detection → /cmd_vel → Navigation → /camera/raw → Drive',
 'Camera → /camera/raw → AI Detection → /cmd_vel → Drive → /detected_objects → Navigation'],
 'The arrows connect Camera to AI Detection through raw images, detection to navigation through objects, and navigation to Drive through velocity commands.',[
 'Correct: all three directed edges and node roles match.',
 'This exchanges the detection and navigation stages.',
 'This assigns the three topic labels to the wrong data stages.',
 'This routes velocity commands before navigation and puts navigation after Drive.'])
setq(31,'In the course’s get_map example, which request/response directions and client arrangement match its intended service model?',[
 'Nav sends get_map to Map; Map returns OccupancyGrid to Nav; several clients may call that intended Map service server',
 'Map sends get_map to Nav; Nav returns OccupancyGrid to Map; several clients may call that intended Nav service server',
 'Nav sends get_map to Map; Map returns OccupancyGrid to Nav; the service is restricted to one client for its lifetime',
 'Nav broadcasts OccupancyGrid to Map; Map returns get_map to Nav; the clients act as the intended map servers'],
 'The navigation client requests the map and receives the response; the source also allows multiple clients to call the intended server.',[
 'Correct: this preserves direction and the course-described multiple-client arrangement.',
 'This reverses the request/response roles.',
 'The source explicitly permits multiple clients; it does not restrict lifetime use to one client.',
 'This reverses request versus response content and server/client roles.'])
cite(31,194);concept(31,'service-client-fanin','Multiple clients of an intended service server','Several clients can call the intended named server in the course example; the slide’s global uniqueness wording is not treated as an enforced implementation theorem.',[194])
qs[31]['assumptions']=['Use the intended single named server in this course example; this is not an assertion that middleware enforces global uniqueness of server names.']
qs[31]['conflictResolution']={'status':'explicit-qualification-awaiting-independent-review','sourceClaim':'The slide says only one service server can exist at any time.','basis':'The question assesses the intended server with multiple clients, not an enforced global uniqueness theorem.','method':'Keep the source wording and restrict the assessed claim to the depicted intended arrangement.'}
setq(33,'A navigation task runs for several seconds and needs built-in progress feedback plus a cancellation-request mechanism. Which primitive best matches the lecture?',[
 'An action carrying a goal, feedback and an eventual result',
 'A service carrying a request and its final response',
 'A topic carrying a stream of velocity commands',
 'A node parameter storing a desired navigation target'],
 'The action interface is presented for long-running goal-oriented tasks with feedback and cancellation requests.',[
 'Correct: this primitive directly supplies the requested task lifecycle.',
 'A request/response service alone does not provide the stated action feedback/cancel lifecycle.',
 'A command stream alone does not define goal admission, progress and result semantics.',
 'A configuration value alone does not supply those task interactions.'])
setq(42,'Which hardware-interface and processing sequence matches the lecture’s sensing-to-decision example?',[
 'Sensor connects through a suitable USB or CSI interface; its driver publishes raw data; perception detects; decision logic chooses movement',
 'Sensor connects through a ROS topic as its physical port; its driver publishes raw data; perception detects; decision logic chooses movement',
 'Sensor connects through USB or CSI; its driver chooses movement; decision logic publishes raw data; perception detects',
 'Sensor connects through USB or CSI; perception publishes the movement decision; the driver detects objects; decision logic acquires raw samples'],
 'USB/CSI are the example physical interfaces; publication, perception and decision are separate software stages.',[
 'Correct: this follows the named port examples and source processing order.',
 'A ROS topic is a software communication channel, not a physical sensor connector.',
 'This swaps acquisition and decision responsibilities.',
 'This assigns the interpretation, decision and acquisition roles to the wrong stages.'])
qs[42]['assumptions']=['USB and CSI are example interfaces; do not assume that every camera or LiDAR supports both.']
concept(42,'sensor-ports','Physical sensor ports versus ROS topics','The source names USB/CSI sensor links before publication to software topics, without universal compatibility for every sensor.',[200])
setq(43,'Which stage is explicitly assigned precise low-level PWM timing in the illustrated Jetson-to-motor chain?',[
 'The Arduino or other low-level microcontroller',
 'The Jetson navigation process that chooses movement commands',
 'The serial-transfer stage that carries the selected command',
 'The motor-driver power stage downstream of the controller'],
 'The source assigns PWM timing to the low-level microcontroller, after high-level command selection and before the driver/motor stages.',[
 'Correct: this is the stage named in the text.',
 'The navigation stage selects movement commands rather than being the illustrated PWM timing component.',
 'Serial transfer carries the command; the source assigns the timing role to the receiving microcontroller.',
 'The diagram separates the controller from the downstream driver stage.'])
setq(45,'Heavy CNN inference is inserted into the precise motor-PWM loop. With command formats and wiring already checked, which concern follows most directly from the course’s separation of roles?',[
 'Variable perception workload can delay work assigned to the low-level timing loop',
 'The command message must acquire a camera-pixel field merely because inference is in the same process',
 'The motor driver must change its supply voltage merely because the controller now calls a CNN',
 'The camera-to-chassis transform must change merely because inference runs in the motor loop'],
 'The relevant architectural concern is interference with timing; process placement alone does not redefine message fields, motor supply or geometry.',[
 'Correct: computation in a time-sensitive loop can compete with its timing responsibilities.',
 'Process placement does not itself impose that message-field change.',
 'The given change does not specify any new motor electrical requirement.',
 'Moving computation does not physically remount the camera.'])
setq(50,'A detector reports an object in camera coordinates, but navigation needs chassis-relative coordinates. Which information supplies the required frame relationship?',[
 'A valid TF relation connecting camera_link to base_link at the relevant time',
 'The camera intrinsic calibration alone, without its pose relative to the chassis',
 'The base-to-world pose alone, without any camera-to-base connection',
 'The camera visual mesh alone, without a coordinate transform to base_link'],
 'The required relation is the extrinsic frame connection between the camera and chassis, supplied through valid transforms.',[
 'Correct: this connects the two coordinate frames.',
 'Intrinsics describe image formation but do not supply the camera’s chassis-relative mounting pose.',
 'A base-to-world pose alone leaves the camera frame disconnected.',
 'A rendered shape does not by itself specify the requested frame transform.'])
q=qs[51];q['type']='conceptual'
for c in q['citations']:
 if c['physicalPage']==203:c['kind']='statement';c['locator']='Physical PDF page 203, printed slide 33: TF Tree prose and base_link/camera_link textual example'
q['solution']['optionExplanations']['o4']='The text gives base_link as often the parent of camera_link; it does not state a universal camera-root requirement.'
q['solution']['misconceptions']=[v for k,v in q['solution']['optionExplanations'].items() if k not in q['correctOptionIds']]
setq(54,'Which pair of inputs feeds robot_state_publisher in the source illustration?',[
 'robot_description containing URDF structure, plus /joint_states containing current joint state',
 'robot_description containing URDF structure, plus /cmd_vel containing a requested base velocity',
 '/joint_states containing current joint state, plus /camera/raw containing camera images',
 '/tf containing output transforms, plus /cmd_vel containing a requested base velocity'],
 'The illustrated inputs are the robot structure and current joint states; the transforms are the output.',[
 'Correct: these provide structural relations and live articulated configuration.',
 'A commanded base velocity is not the shown joint-state input.',
 'Images do not replace the structural description.',
 'This treats the transform output as an input and omits both shown inputs.'])
setq(60,'The simulation and hardware both use /cmd_vel. Which validation plan best addresses whether real behaviour matches the model?',[
 'Check the interface and measure real actuator response, timing and friction across relevant operating conditions',
 'Check the interface and run more simulated trajectories, treating the model’s actuator response as the real response',
 'Check the interface and compare visual robot shapes, treating matched appearance as evidence of matched timing',
 'Check the interface and one unloaded motor speed, treating that one point as evidence for loaded dynamics'],
 'Matching the interface does not validate physical response; real dynamics and timing must be checked under relevant conditions.',[
 'Correct: this tests the model-to-hardware factors rather than assuming them.',
 'Further simulation alone does not measure the actual actuator response.',
 'Visual agreement does not establish matching physical timing.',
 'An unloaded operating point does not validate the full loaded operating range.'])
setq(74,'The visual mesh shows a protruding part, but the collision overlay omits it and contacts ignore it. Which configuration issue is most directly indicated?',[
 'The collision geometry omits the protrusion even though the visual geometry includes it',
 'The inertial mass is too small even though the collision geometry includes the full protrusion',
 'The visual material color is wrong even though collision geometry includes the full protrusion',
 'The camera image resolution is low even though collision geometry includes the full protrusion'],
 'The explicit collision overlay identifies missing collision geometry; visual and collision representations are distinct.',[
 'Correct: this matches the direct overlay evidence.',
 'Mass affects dynamics, but it does not explain why the collision overlay lacks that shape.',
 'Material color does not supply missing collision geometry.',
 'Image resolution does not change the collision shape shown in the overlay.'])
setq(79,'A package contains the shown guarded MyNode module. With imports available, what does the final if __name__ == "__main__": main() do in two cases: direct script execution and importing under another module name?',[
 'It calls main in direct execution; it does not call main merely from importing the module',
 'It does not call main in direct execution; it calls main when imported under another name',
 'It calls main in both cases because defining the function executes its body',
 'It calls main in neither case because only a class definition can invoke ROS initialization'],
 'The guard is true for direct execution and false when __name__ is another module name; storing/importing definitions is not the same as launching the shown lifecycle.',[
 'Correct: the conditional distinguishes the two stated name values.',
 'This reverses the guard’s equality test.',
 'Defining a function does not execute its body.',
 'The explicit main() call can invoke initialization when the guard is true.'])
qs[79]['type']='code_output';qs[79]['assumptions']=['Compare only the final guard with __name__ equal to "__main__" or a different module name; assume imports succeed and no external caller invokes main.', 'This is Python control flow, not a claim that a ROS runtime was executed during validation.']
concept(79,'entry-guard','Direct execution versus module import','The final __name__ guard invokes main for direct execution, but not merely for import under another name.',[187])
for c in qs[79]['citations']:
 if c['physicalPage']==187:c['kind']='code'
setq(80,'A mixed hardware/simulation experiment displays its sensor output in RViz. Which three-role mapping is correct?',[
 'HIL describes the real/simulated mix; Gazebo models simulated components; RViz displays the data',
 'HIL describes the real/simulated mix; RViz computes physical contact; Gazebo only displays the data',
 'Gazebo describes the real/simulated mix; HIL is the display program; RViz models physical components',
 'RViz defines the real/simulated mix; Gazebo is the real hardware controller; HIL names the sensor-message format'],
 'Hardware-in-the-loop describes the experimental composition, the simulator models components, and RViz provides visualization.',[
 'Correct: this separates setup, simulation and display.',
 'This swaps the simulation and visualization roles.',
 'HIL is not a display program, and RViz is not the physics model.',
 'The visualization program does not define HIL, and HIL is not a message format.'])
# No scientific/source annotation is silently removed or globally corrected.
assert {k:v for k,v in b.items() if k not in ['questions','concepts']}=={k:v for k,v in old.items() if k not in ['questions','concepts']}
unchanged=sum(question_hash(q)==question_hash(o) for q,o in zip(b['questions'],old['questions']))
assert unchanged==55,(unchanged,len(changed))
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in b['questions']:
 if q['id'] not in changed:continue
 a={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in a['citations']:c.pop('evidenceText',None)
 packet.append(a)
(R/'audits/blind-W01-L05-coverage-repairs.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
(R/'audits/W01-L05-coverage-repair-author-checks.json').write_text(json.dumps({'revisedExistingQuestions':25,'qualityFlagRepairs':23,'additionalAcceptedQuestionsExtended':2,'unchangedHashes':55,'sourceAnnotationsPreserved':16,'remainingNewGapQuestions':3,'actualRecheckedPages':[174,176,183,184,186,187,190,194,196,199,200,201,202,203,204,205,206,207,208],'independentReviewRequired':True},indent=2)+'\n')
print('25 existing items revised; 55 accepted hashes preserved; 3 distinct gap items next.')
