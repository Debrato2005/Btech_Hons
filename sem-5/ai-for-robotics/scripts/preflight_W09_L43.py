"""One-time pre-freeze quality strengthening; not an independent review."""
from pathlib import Path
import json,re,copy,hashlib,datetime
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W09-L43.json';b=json.loads(p.read_text());by={q['id']:q for q in b['questions']};changes=[]
def revise(n,stem,correct,wrong,why=None):
 q=by[f'W09-L43-Q{n:03d}'];key=q['correctOptionIds'][0];ids=[o['id']for o in q['options']if o['id']!=key]
 if stem:q['stem']=stem
 for o in q['options']:
  if o['id']==key:o['text']=correct
  else:o['text']=wrong[ids.index(o['id'])][0]
 if why:q['solution']['justification']=q['solution']['simpleExplanation']=why
 q['solution']['optionExplanations']={key:q['solution']['justification'],**{id_:v[1]for id_,v in zip(ids,wrong)}}
 q['solution']['misconceptions']=[v[1]for v in wrong];changes.append(q['id'])
revise(1,None,'CNNs: visual feature learning; VLMs: image and language understanding',[
 ('CNNs: temporal memory; VLMs: image-only feature extraction','Temporal memory is associated with recurrent models; VLMs combine vision and language.'),
 ('CNNs: hand-written symbolic rules; VLMs: action-value updates','These associations confuse model families with rule-based control and reinforcement-learning updates.'),
 ('CNNs: image and language understanding; VLMs: visual feature learning only','This swaps the timeline’s CNN and VLM roles.')])
revise(14,None,'Predict → compare with the label → compute gradients → update weights',[
 ('Predict → update weights → compare with the label → compute gradients','Updating before computing current gradients does not match the learning loop.'),
 ('Compute gradients → predict → update weights → compare with the label','The gradient of the current supervised loss requires its prediction and label comparison first.'),
 ('Predict → compute gradients → compare with the label → update weights','The supervised loss must be formed from the label comparison before backpropagation.')])
revise(15,None,'MLP: feature vectors; CNN: images; RNN/LSTM: sequences',[
 ('MLP: feature vectors; CNN: sequences; RNN/LSTM: images','This swaps the lecture’s CNN and recurrent-network associations.'),
 ('MLP: images; CNN: feature vectors; RNN/LSTM: sequences','This swaps the lecture’s MLP and CNN associations.'),
 ('MLP: sequences; CNN: images; RNN/LSTM: feature vectors','This swaps the lecture’s MLP and recurrent-network associations.')])
revise(18,None,'Max pooling',[
 ('ReLU alone','ReLU changes activation values without reducing tensor dimensions by itself.'),
 ('Final Softmax','Softmax normalizes class scores rather than performing the depicted spatial downsampling.'),
 ('Bias addition','Adding a bias does not reduce the feature grid.')])
revise(28,None,'Every such move changes Manhattan distance by +1 or −1, so an equal-distance neighbor does not exist',[
 ('A horizontal move leaves Manhattan distance unchanged, while a vertical move changes it','Both horizontal and vertical unit moves change one absolute-coordinate term by one.'),
 ('An equal-distance move exists whenever two directions are equally preferred','A tie between two candidate distances does not mean either candidate equals the current distance.'),
 ('Every legal move changes Manhattan distance by an even integer','A single unit four-neighbor move changes total Manhattan distance by one, not by an even number.')])
revise(37,None,'It disables gradient recording during inference',[
 ('It changes the model into evaluation mode by calling model.eval()','no_grad disables gradient tracking; it is not a call to model.eval().'),
 ('It clears accumulated parameter gradients with zero_grad()','Disabling recording is different from clearing existing gradient buffers.'),
 ('It permanently marks every model parameter as non-trainable','The context disables recording for these operations rather than permanently changing parameter trainability.')])
revise(44,None,'An explicit handler for an empty valid-action list',[
 ('A check that the highest unmasked score is positive','Positive logits are not required, and such a check does not handle an empty list.'),
 ('A Softmax normalization of the remaining scores','Normalizing an empty candidate set does not supply a legal action.'),
 ('A tie-breaking rule for equal valid scores','A tie rule applies to multiple candidates, not to the absence of candidates.')])
revise(49,'Which design specifically combines learned perception with conventional navigation components?','A learned perception module supplying a conventional planner and safety checks',[
 ('A single trained network mapping raw camera images directly to wheel commands','This is the end-to-end learned design, not the specified learned-perception/conventional-planning combination.'),
 ('A classical range-sensor threshold controller followed by a classical graph planner','This contains conventional components but no learned perception module.'),
 ('Two learned networks, one for perception and one for action selection, with no conventional planner','Both main components are learned, unlike the specific combination in the question.')])
revise(51,'Which row correctly matches the table’s sensor roles?','Camera: visual appearance; LiDAR: range; ultrasound: nearby obstacles; GPS: outdoor position',[
 ('Camera: visual appearance; LiDAR: range; ultrasound: outdoor position; GPS: nearby obstacles','This swaps ultrasound’s nearby-obstacle role and GPS’s outdoor-position role.'),
 ('Camera: range; LiDAR: visual appearance; ultrasound: nearby obstacles; GPS: outdoor position','This swaps the table’s camera and LiDAR roles.'),
 ('Camera: visual appearance; LiDAR: outdoor position; ultrasound: nearby obstacles; GPS: range to nearby surfaces','This confuses local range measurement with satellite-based outdoor positioning.')])
revise(52,None,'IMU measurements support motion and orientation estimation, with modeling and drift considerations',[
 ('An IMU directly reports absolute orientation without integrating or interpreting its measurements','Raw inertial measurements must be processed; absolute orientation is not automatically supplied without error.'),
 ('An IMU’s accelerometer measures angular velocity while its gyroscope measures linear acceleration','These accelerometer and gyroscope roles are reversed.'),
 ('An IMU estimates position by measuring distances to navigation satellites','Satellite ranging is a GNSS function, not an IMU measurement mechanism.')])
revise(54,None,'Camera input → CNN processing → object detection → safe navigation planning',[
 ('Camera input → object detection → CNN processing → safe navigation planning','The shown CNN stage precedes its object-detection output.'),
 ('Camera input → CNN processing → safe navigation planning → object detection','Detection supplies information before the planning stage in the shown chain.'),
 ('Safe navigation planning → camera input → CNN processing → object detection','Planning is the downstream output in this diagram, not the source of the camera input.')])
revise(55,'What does sensor fusion mean in the humanoid-navigation context?','Combining complementary measurements from multiple sensors to estimate the surroundings',[
 ('Selecting only the highest-resolution sensor and discarding every other stream','Selecting one sensor alone does not combine information from multiple sensors.'),
 ('Displaying multiple sensor streams separately without combining their information','Separate display is not itself the estimation-level combination meant by fusion.'),
 ('Duplicating one sensor’s samples and treating each copy as an independent observation','Duplicated measurements are not independent complementary evidence.')],why='Sensor fusion combines information from different measurements; it does not remove uncertainty or replace navigation planning.')
revise(56,'In an added constant-velocity example, an obstacle was at x = 2 m when observed and moves at +1 m/s; where is it after a 0.5 s processing delay?','x = 2.5 m',[
 ('x = 2.0 m','This ignores motion during the processing delay.'),
 ('x = 1.5 m','This subtracts displacement despite the stated positive velocity.'),
 ('x = 3.0 m','This uses one second rather than the stated half-second delay.')],why='The obstacle moves 1×0.5 = 0.5 m during the delay, so its position becomes 2.5 m.')
q=by['W09-L43-Q056'];q.update(type='numerical',cognitiveSkill='numerical',assumptions=['This is an author-added example illustrating the slide’s real-time constraint.','The obstacle maintains constant velocity in one fixed coordinate frame.']);q['solution']['steps']=['Compute displacement:1m/s×0.5s=0.5m.','Add displacement to initial position:2+0.5=2.5m.'];q['solution']['formulas']=[{'expression':'x(t)=x0+v*t','variables':{'x':'position after delay','x0':'initial position2m','v':'velocity1m/s','t':'delay0.5s'},'units':{'x':'m','x0':'m','v':'m/s','t':'s'},'assumptions':['Constant velocity in one fixed coordinate frame.']}]
revise(57,None,'Learning visual scene representations with relationships across image regions',[
 ('Learning only the final motor-current values while excluding visual input','That is not the visual-scene role assigned to vision transformers.'),
 ('Applying fixed local image thresholds without learning relationships between image regions','This describes a fixed image-processing rule rather than the stated learned representation.'),
 ('Constructing a graph-search frontier directly from manually supplied edge costs','That is a graph-search operation rather than the listed vision-transformer role.')])
revise(58,None,'Use the image and the instruction “go to the door beside the red chair” together',[
 ('Use only the same instruction as text, with no current visual observation','This is language-only input rather than a combined visual-language input.'),
 ('Use only the image to detect doors, with no language instruction','This is vision-only input rather than the combined case.'),
 ('Use only the robot’s numeric pose and a numeric destination coordinate','Numeric pose-to-goal input lacks the image-language pairing.')])
revise(59,None,'The agent acts in an environment and learns from the resulting interactions',[
 ('The agent classifies stored images without taking actions in an environment','Static-image classification alone lacks the action-environment feedback emphasized here.'),
 ('The agent retrieves existing text descriptions without testing actions','Text retrieval alone does not establish embodied interaction.'),
 ('The agent predicts labels for a fixed dataset without receiving consequences of its actions','Offline label prediction alone lacks the described action-feedback loop.')])
revise(60,None,'Accuracy, response time, resource use and failure behavior under representative conditions',[
 ('Training accuracy and parameter count, without testing response time','These omit the explicit dynamic-obstacle response requirement.'),
 ('Image-classification accuracy on a different dataset, without navigation trials','This does not measure the robot’s actual navigation task and conditions.'),
 ('Inference speed on different hardware, without checking task accuracy','This omits both the target hardware constraints and whether the decisions are correct.')])
# Human-readable spacing for authored prose; do not alter IDs, URLs, hashes or formulas.
def prose(s):
 s=re.sub(r'(?<=[0-9%])(?=[A-Za-z])',' ',s)
 s=re.sub(r'(?<=[a-z])(?=[0-9])',' ',s)
 s=re.sub(r'(?<=\))(?=[a-z])',' ',s)
 s=re.sub(r'(?<=[a-z])(?=\()',' ',s)
 s=s.replace('1or','1 or').replace('−1,','−1,')
 return s
for q in b['questions']:
 q['stem']=prose(q['stem']);q['assumptions']=[prose(x)for x in q['assumptions']]
 for o in q['options']:o['text']=prose(o['text'])
 for k in ['justification','simpleExplanation'] :q['solution'][k]=prose(q['solution'][k])
 for k in ['steps','misconceptions','examTraps']:q['solution'][k]=[prose(x)for x in q['solution'][k]]
 q['solution']['optionExplanations']={k:prose(v)for k,v in q['solution']['optionExplanations'].items()}
 for c in q['citations']:c['locator']=prose(c['locator'])
 for c in b['concepts']:
  if q['id']in c['questionIds']:c['description']=q['solution']['justification'];c['examinationAngles']=[q['type']]
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in b['questions']:
 a={k:copy.deepcopy(q[k])for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
 for c in a['citations']:c.pop('evidenceText',None)
 if q.get('primaryEvidence'):a['primaryEvidence']=copy.deepcopy(q['primaryEvidence'])
 packet.append(a)
blind=R/'audits/blind-W09-L43.json';blind.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
qhash=lambda q:hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ['status','reviewIds']},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
files=['data/question-batches/W09-L43.json','data/inspection-batches/W09-L43.json','audits/blind-W09-L43.json','audits/W09-L43-author-checks.json','audits/W09-L43-official-code-execution.json','audits/W09-L43-source-qualifications.json','audits/W09-L43-author-coverage.json','sources/supplemental/L43-source-retrieval.json','sources/supplemental/L43-official-code.py','sources/supplemental/L43-official-notebook-output-stripped.ipynb']
manifest={'batchId':'W09-L43','frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorId':b['authorId'],'questions':[{'id':q['id'],'version':q['version'],'questionSha256':qhash(q)}for q in b['questions']],'files':{f:h(R/f)for f in files},'authorChecks':{'checkCount':26,'variedManhattanTrials':5000,'addedLatencyArithmetic':'2+1*0.5=2.5','independentVerification':False},'preFreezeQualityRevisions':changes,'independentReviewRequired':True,'coverageClaim':'All30actualpages inspected;24examinablepages mapped to60drafts. Independent completeness challenge remains required.'}
(R/'audits/W09-L43-frozen-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'questions':len(b['questions']),'blindSha256':h(blind),'qualityStrengthened':len(changes)}))
