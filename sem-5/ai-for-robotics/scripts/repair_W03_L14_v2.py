from pathlib import Path
import json,copy,datetime
from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W03-L14.json';b=json.loads(p.read_text());old=copy.deepcopy(b)
ids={2,11,12,15,16,25,29,30,34,36,37,40,47,48,49,53};a=R/'audits/batch-history/W03-L14-v1-before-quality-repair.json';assert not a.exists();a.write_text(json.dumps([q for q in b['questions'] if int(q['id'][-3:]) in ids],ensure_ascii=False,indent=2)+'\n')
def choices(q,changes,why):
 for o in q['options']:
  if o['id'] in changes:o['text']=changes[o['id']]
 q['solution']['optionExplanations'].update(why)
 q['solution']['misconceptions']=[v for k,v in q['solution']['optionExplanations'].items() if k not in q['correctOptionIds']]
for q in b['questions']:
 n=int(q['id'][-3:])
 if n not in ids:continue
 assert q['version']==1;h=question_hash(q);author='robotics-integration-L14-v2-revision-author';q.update(version=2,status='draft',reviewIds=[]);q.setdefault('revisionAuthors',[]).append(author);q.setdefault('revisionHistory',[]).append({'version':2,'authorId':author,'priorQuestionSha256':h,'reason':'Repair independently identified clarity, source-conflict, distractor or difficulty issues.','revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 if n in [12,15,16,29,30,53]:q['difficulty']='easy'
 if n in [48,49]:q['difficulty']='medium'
 if n==2:choices(q,{'o4':'Recursive Newton–Euler for systematic energy-based analytical models; Lagrangian formulation for linkwise real-time force recursion','o2':'Recursive Newton–Euler for minimizing the number of joint coordinates; Lagrangian formulation for recovering every joint constraint force','o1':'Recursive Newton–Euler for selecting the potential-energy reference; Lagrangian formulation for separating forces link by link'},{'o4':'This reverses the specific emphases and computational descriptions on the slide.','o2':'Both can use the robot’s coordinates; these are not the contrasted purposes.','o1':'The energy reference belongs to energy modelling, whereas linkwise force balance describes Newton–Euler.'})
 if n==11:choices(q,{'o1':'A Hamiltonian function for total mechanical energy','o2':'A gravitational potential function for height-dependent energy','o3':'A constraint multiplier for an ideal holonomic joint constraint'},{'o1':'This is a different analytical-mechanics function, not the named dissipative addition.','o2':'Gravitational potential models a conservative load, not the stated dissipative extension.','o3':'Constraint multipliers account for constraint reactions, not the named dissipation function.'})
 if n==12:choices(q,{'o2':'The shown approach cannot model gravity when the reference height is nonzero','o3':'The shown approach cannot include configuration-dependent inertia in kinetic energy','o4':'The shown approach cannot combine revolute and prismatic generalized coordinates'},{'o2':'The lecture explicitly includes gravitational potentials with constant reference offsets.','o3':'Its manipulator examples include configuration-dependent kinetic coefficients.','o4':'The lecture includes an RP example and a mixed-coordinate description; this is not its printed limitation.'})
 if n==25:q['solution']['steps'][-1]='The combined gravity-and-spring torque is mgl cos(theta)−kt theta; including the stated actuator gives total torque tau+mgl cos(theta)−kt theta.'
 if n==34:
  q['solution']['optionExplanations']['o2']='This incorrectly replaces sin(theta1) by cos(theta1); even the full angle derivative would be m2 g d2 cos(theta1), with the radius factor.'
  q['solution']['misconceptions']=[v for k,v in q['solution']['optionExplanations'].items() if k not in q['correctOptionIds']]
 if n==36:choices(q,{'o2':'(m2 d2 thetadot1²,0)ᵀ and (g(m1 l1+m2 d2)cos(theta1),m2 g sin(theta1))ᵀ','o3':'(0,2m2 d2 thetadot1²)ᵀ and (g(m1 l1+m2 d2)cos(theta1),m2 g sin(theta1))ᵀ'}, {})
 if n in [37,47]:
  q['stem']='Let A(d2)=m1 l1²+Izz1+Izz2+m2 d2². '+q['stem']
  q['assumptions'].append('A(d2) is the total coefficient of thetadot1² in twice the kinetic energy, with units kg·m².')
 if n==40:
  next(c for c in q['citations'] if c['physicalPage']==446)['role']='conflict'
  q['conflictResolution']={'status':'explicit-qualification-awaiting-independent-review','sourceClaim':'The lower standalone M display on physical page446 has an unclear underscore-like glyph before m2 d2²; the upper scalar and matrix equations on that page show a plus.','basis':'The clear positive kinetic-energy coefficient on physical page443 and the upper equations on page446 give M11=m1 l1²+Izz1+Izz2+m2 d2²; differentiating K twice with respect to thetadot1 agrees.','method':'Use the mutually consistent energy and upper equations for this item while preserving the local lower-display glyph ambiguity.','sourceId':'lectures','sourceSha256':'2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c','physicalPages':[443,446]}
 if n==53:choices(q,{'o3':'Choose coordinates → form K and U → differentiate K with respect to q before taking its time derivative → use this in place of d(K_qdot)/dt','o4':'Choose coordinates → form K and U → take the time derivative of K_qdot while holding every configuration-dependent coefficient constant → collect efforts','o1':'Choose coordinates → form K and U → set qdot=0 before differentiating → use the resulting equations for arbitrary motion'},{'o3':'Euler–Lagrange requires the total time derivative of the velocity partial K_qdot, not of the coordinate partial K_q.','o4':'Configuration-dependent coefficients vary along motion and contribute product-rule terms.','o1':'Specializing to rest before differentiation removes velocity-dependent terms needed for arbitrary motion.'})
assert sum(question_hash(q)==question_hash(o) for q,o in zip(b['questions'],old['questions']))==37
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');packet=[]
for q in b['questions']:
 if int(q['id'][-3:]) not in ids:continue
 x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
(R/'audits/blind-W03-L14-v2.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print('16 repairs saved;37 accepted hashes unchanged.')
