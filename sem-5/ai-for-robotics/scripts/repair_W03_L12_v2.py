from pathlib import Path
import json,copy,datetime
from validate import question_hash
from authoring_helpers import formula
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W03-L12.json';b=json.loads(p.read_text());old=copy.deepcopy(b)
reviews=json.loads((R/'data/reviews/W03-L12-v1-independent.json').read_text());ids={x['questionId'] for x in reviews if x['decision']=='flagged'}
a=R/'audits/batch-history/W03-L12-v1-before-quality-repair.json';assert not a.exists();a.write_text(json.dumps([q for q in b['questions'] if q['id'] in ids],ensure_ascii=False,indent=2)+'\n')
def option(q,oid,text,why):
 next(o for o in q['options'] if o['id']==oid)['text']=text;q['solution']['optionExplanations'][oid]=why
def explanation(q,text):q['solution']['justification']=text;q['solution']['simpleExplanation']=text
for q in b['questions']:
 if q['id'] not in ids:continue
 assert q['version']==1;h=question_hash(q);author='robotics-integration-L12-v2-revision-author';q.update(version=2,status='draft',reviewIds=[]);q.setdefault('revisionAuthors',[]).append(author);q.setdefault('revisionHistory',[]).append({'version':2,'authorId':author,'priorQuestionSha256':h,'revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reason':'Repair frozen independent source, distractor, rationale, difficulty and duplication findings.'})
 n=int(q['id'][-3:])
 if n in [4,8,12,25,36,38,39,41,45]:q['difficulty']='easy'
 if n==5:
  option(q,'o4','Flexible-link bending vibration','The source lists rigid-body inertial, Coriolis, centrifugal and gravity effects, not flexible deformation modes.')
  explanation(q,'The slide explicitly lists inertial, Coriolis, centrifugal and gravitational effects; flexible-link bending is not part of that listed rigid-body model.')
 if n==7:
  option(q,'o2','F is only the force from the proximal joint, regardless of other forces on the link','Newton’s equation uses the net resultant force, which need not equal a single joint contribution.')
 if n==21:
  option(q,'o3','F_i,N_i are the distal loads on the link, while f_i,n_i are the net center-of-mass resultants','This swaps a transmitted joint load with the whole-link resultant.')
  option(q,'o4','The pairs represent the same resultant, distinguished only by using base versus link coordinates','The distinction is their physical role and reference point, not merely a coordinate change.')
 if n==26:q['solution']['optionExplanations']['o3']='This subtracts the distal force and moment and also omits both moment-arm terms: the displayed moment −1 equals1−2, whereas retaining the arms with those wrong signs would give−3.'
 if n==35:
  for page in [386,394,395]:
   c=copy.deepcopy(q['citations'][0]);c.update(slideId=f'lectures-p{page:04d}',physicalPage=page,kind='equation',locator=f'Lecture12, physical PDF page{page}, printed slide{page-378}: force law, moment-arm recursion or joint-axis projection premise',evidenceText=(R/f'sources/text/lectures/page-{page:04d}.txt').read_text().strip(),role='premise');q['citations'].append(c)
 if n==41:
  q['stem']='Which statement matches the source’s sim-to-real training and learned inverse-dynamics ideas, respectively?'
  option(q,'o2','Keep every simulated mass fixed to prevent model variation; train the inverse model to map τ to qddot','The source describes varying inertial parameters; τ-to-acceleration is forward, not inverse, dynamics.')
  option(q,'o3','Randomize only the target labels without changing the simulated dynamics; train the inverse model using q alone','The source randomizes physical mass/inertia parameters, and its inverse input includes position, velocity and acceleration.')
  option(q,'o4','Remove inertial variation from simulation; train the inverse model to predict only gravity for all motions','The source includes inertial randomization and a full motion-state-to-effort map, not only static gravity.')
  explanation(q,'The source associates sim-to-real with mass/inertia variation and learned inverse dynamics with the map(q,qdot,qddot) to τ.')
 if n==42:
  q['stem']='According to the source table, which descriptions belong to Peter Corke Robotics Toolbox and ROS2 + MoveIt, respectively?'
  option(q,'o1','MATLAB/Python with DH-oriented educational simulation; KDL recursive Newton–Euler for real robots','This matches the two named source rows in order.')
  option(q,'o2','KDL recursive Newton–Euler for real robots; MATLAB/Python with DH-oriented educational simulation','This reverses the two requested row descriptions.')
  option(q,'o3','Python/JAX differentiable dynamics; physics simulators for reinforcement-learning environments','These descriptions are assigned to the Brax and PyBullet/MuJoCo rows, not the requested pair.')
  option(q,'o4','A C++/Python library listing ABA and CRBA; multibody dynamics with model-predictive control','These descriptions belong to the Pinocchio and Drake rows.')
  explanation(q,'The Corke row states MATLAB/Python and DH-oriented educational simulation; the ROS2 + MoveIt row mentions KDL recursive Newton–Euler.')
 if n==43:
  q['stem']='According to the source table, which descriptions belong to Pinocchio and JAX Robotics(Brax), respectively?'
  option(q,'o1','A C++/Python rigid-body library listing Newton–Euler, ABA and CRBA; Python/JAX differentiable dynamics for gradient-based optimization','This matches both named rows in the stated order.')
  option(q,'o2','MATLAB/Python DH-oriented educational simulation; Python/JAX differentiable dynamics for gradient-based optimization','The first description belongs to Corke, not Pinocchio; the second matches Brax.')
  option(q,'o3','KDL recursive Newton–Euler in ROS2; a C++/Python library listing Newton–Euler, ABA and CRBA','These are the ROS2 + MoveIt and Pinocchio descriptions, not Pinocchio and Brax in order.')
  option(q,'o4','A C++/Python library listing Newton–Euler, ABA and CRBA; MATLAB/Python DH-oriented educational simulation','The first description matches Pinocchio, but the second is Corke, not Brax.')
 if n==44:
  option(q,'o2','A Python/JAX differentiable dynamics library; a MATLAB/Python DH-oriented teaching toolbox','These are the Brax and Corke row descriptions, not the requested simulator/Drake pair.')
  option(q,'o3','KDL recursive Newton–Euler in ROS2; a C++/Python library listing ABA and CRBA','These are the ROS2 + MoveIt and Pinocchio rows.')
  option(q,'o4','Multibody dynamics with model-predictive control; physics simulators for reinforcement-learning environments','This reverses the requested PyBullet/MuJoCo and Drake associations.')
 if n==47:
  q.update(stem='A nominal Newton–Euler model predicts τ_NE=(4,6) N·m, but measured torque is(5,4) N·m at the same(q,qdot,qddot); to retain known mechanics and learn an additive residual, which training target and reconstruction are correct?',selectionMode='single',type='scenario',cognitiveSkill='application',difficulty='medium',correctOptionIds=['o1'])
  option(q,'o1','Target(1,−2) N·m; reconstruct τ=τ_NE+predicted residual','Subtract the nominal effort from the measured effort, then add the learned mismatch to the nominal model.')
  option(q,'o2','Target(−1,2) N·m; reconstruct τ=τ_NE+predicted residual','This reverses the residual sign; adding it would move the prediction away from the measurement.')
  option(q,'o3','Target(5,4) N·m; reconstruct τ=τ_NE+predicted residual','This uses total measured effort as a residual and would count the nominal contribution twice.')
  option(q,'o4','Target(1,−2) N·m; reconstruct τ=predicted residual only','The residual target is right, but dropping the known model loses the nominal dynamics.')
  explanation(q,'The additive target is τ_measured−τ_NE=(5−4,4−6)=(1,−2) N·m; adding that target back recovers(5,4).')
  q['solution']['steps']=['Use paired measurements and nominal predictions at the same state and acceleration.','Compute target=(5,4)−(4,6)=(1,−2) N·m.','Reconstruct total effort as nominal plus learned residual.'];q['solution']['formulas']=[formula('r=τ_measured−τ_NE; τ_hat=τ_NE+r_hat',{'r':'residual training target','τ_measured':'measured joint effort','τ_NE':'nominal Newton–Euler effort','r_hat':'learned residual prediction','τ_hat':'hybrid effort prediction'},{'r,τ_measured,τ_NE,r_hat,τ_hat':'N·m'},['Measurements and model predictions correspond to the same state and acceleration.'])]
  q['subtopic']='Build an additive residual training target';q['assumptions']=['Known mechanics is retained; the residual model learns additive effort mismatch from matched samples.']
  for c in q['citations']:c['role']='premise'
 # Regenerate repeated misconceptions after each option explanation repair.
 q['solution']['misconceptions']=[v for k,v in q['solution']['optionExplanations'].items() if k not in q['correctOptionIds']]
assert all(question_hash(q)==question_hash(o) for q,o in zip(b['questions'],old['questions']) if q['id'] not in ids)
assert len(ids)==18
# Keep the gap-replacement concept metadata aligned with its new reasoning demand.
for c in b['concepts']:
 if c['id']=='W03-L12-C-ai-model-role':c.update(title='Build an additive residual training target',description='Subtract nominal model effort from matched measured effort and add the learned residual back.',subtopic='Build an additive residual training target',examinationAngles=['scenario'])
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in b['questions']:
 if q['id'] not in ids:continue
 x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
(R/'audits/blind-W03-L12-v2.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print('18 versioned repairs saved;29 accepted objects/hashes unchanged; Q047 replaced with residual-target application.')
