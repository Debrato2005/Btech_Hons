"""Author-side independent implementations of the stated algebra, not independent peer review."""
import math,random,json,hashlib,datetime,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import schema_errors,question_hash
checks=[]
def check(name,ok,detail):
 assert ok,(name,detail);checks.append({'name':name,'passed':True,'detail':detail})
def close(a,b):return math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10)
def softmax(q,t):
 z=[math.exp((v-max(q))/t) for v in q];return [v/sum(z) for v in z]
check('Tabular update',close(2+.2*(1+.9*5-2),2.7),'Old value2, reward1, gamma0.9, next maximum5, rate0.2.')
check('Wrong immediate discount distractor',close(2+.2*(.9*(1+5)-2),2.68),'Discounting reward as well as bootstrap gives2.68, not the correct2.7.')
check('Storage count',10**9*100*4==400*10**9,'400 decimal GB, excluding overhead.')
check('Grid action max',[1.9,6,3,5.2].index(max([1.9,6,3,5.2]))==1,'Down.')
check('Runner-up gap',close(6-5.2,.8),'Maximum minus second maximum.')
check('Fetch original table',8**3*6==3072,'512 position states and six action entries each.')
check('Refined table',16**3*6==24576 and (16**3*6)/(8**3*6)==8,'Refine all three position coordinates.')
check('Network weights',sum(a*b for a,b in zip([3,4,4],[4,4,4]))==44,'3×4+4×4+4×4.')
check('Network biases',sum([4,4,4])==12,'One bias per non-input unit.')
check('Network total',sum(a*b+b for a,b in zip([3,4,4],[4,4,4]))==56,'44+12.')
rows=[[.91,.2,.35],[.1,.55,.8],[-.9,.7,.6]]
check('Corridor greedy mapping',[r.index(max(r)) for r in rows]==[0,2,1],'Forward, Turn, Stop.')
check('Raw Q not probability',any(v<0 for v in rows[-1]) and not close(sum(rows[-1]),1),'Negative values and no unit sum.')
phi=2;history=[]
for i,theta in enumerate([3,5,8],1):
 if i%3==0:phi=theta
 history.append(phi)
check('Hard target history',history==[2,2,8],'Copies after third optimizer step.')
check('Soft target update',close(.9*2+.1*10,2.8),'Retention convention beta=0.9.')
check('Soft endpoint copy',0*2+(1-0)*10==10,'Beta0 copies main parameter.')
check('Soft endpoint freeze',1*2+(1-1)*10==2,'Beta1 freezes target parameter.')
y=1+.9*max([3,5]);delta=y-4.3
check('Worked target',close(y,5.5),'Reward1 plus discounted maximum5.')
check('Worked TD error',close(delta,1.2),'Target minus chosen main prediction4.3.')
check('Worked full squared error',close(delta**2,1.44),'An auxiliary check; no unspecified loss convention imposed on the lecture.')
check('True terminal target',1+.9*0==1,'Zero terminal continuation, observed reward retained.')
x=4.3;h=1e-5;y=5.5
finite=(.5*(x+h-y)**2-.5*(x-h-y)**2)/(2*h)
check('Toy gradient',abs(finite-(x-y))<1e-8,'Central finite difference agrees with theta−y.')
check('Toy optimizer step',close(x-.1*(x-y),4.42),'Half squared loss and identity output parameter.')
check('Epsilon greedy mass',close(1-.2+.2/4,.85) and close(.2/4,.05),'Uniform random branch includes greedy action.')
check('Epsilon normalization',close(.85+3*.05,1),'Four action probabilities sum to1.')
p=softmax([0,math.log(2)],1)
check('Boltzmann example',close(p[0],1/3) and close(p[1],2/3),'Normalized weights1 and2.')
p=softmax([5,5,1],.001)
check('Low-temperature tie',p==[.5,.5,0],'Two maxima share limiting mass; no first-index tie break.')
check('High temperature',max(abs(v-1/3) for v in softmax([5,5,1],1e9))<1e-8,'Uniform limiting distribution.')
check('Grid resolution',close(12/40,.3) and close(9/30,.3),'Both cells have0.3m side.')
check('Grid counts',40**2==1600 and 30**2==900,'Position cells only, not full state cardinality.')
labels=[max(abs(i),abs(j)) for i in range(-2,3) for j in range(-2,3)]
check('Inflated ring geometry',[labels.count(i) for i in [0,1,2]]==[1,8,16],'Chebyshev-distance square rings.')
check('Buffer side',close(5*.3,1.5),'Five cell widths.')
check('Physical diameter',close(2*150/1000,.3),'Convert millimetres to metres.')
check('Disjoint event reward',500+10*(-1)+2*(-2)==486,'Explicit added additive undiscounted accounting.')
check('No-move comparison',2*(-1)==-2 and -4<2*(-1),'Concourse ties; home has greater immediate no-move cost.')
check('Home reward target',close(-2+.9*5,2.5) and close(-2+.9*5-1,1.5),'Isolated home outer-ring reward.')
check('Reported obstacle count',16+16==2*(8+8),'Reported test count doubles training count; not a universal generalization proof.')
random.seed(381165);comparisons=0
for _ in range(1000):
 q=[random.uniform(-100,100) for _ in range(random.randint(2,8))];t=random.uniform(.2,10);c=random.uniform(-1000,1000)
 a=softmax(q,t);b=softmax([v+c for v in q],t)
 assert all(abs(x-y)<1e-12 for x,y in zip(a,b));comparisons+=1
 assert close(sum(a),1) and all(v>=0 for v in a);comparisons+=1
 phi,theta,beta=[random.uniform(-10,10),random.uniform(-10,10),random.random()]
 new=beta*phi+(1-beta)*theta
 assert close(new-theta,beta*(phi-theta));comparisons+=1
 old,r,nextq,eta,gamma=[random.uniform(-10,10),random.uniform(-5,5),random.uniform(-10,10),random.random(),random.random()]
 target=r+gamma*nextq;u=old+eta*(target-old)
 assert close(u,(1-eta)*old+eta*target);comparisons+=1
batch=json.loads((R/'data/question-batches/W08-L38.json').read_text());schema=json.loads((R/'data/schema.question.json').read_text())
errors=[e for q in batch['questions'] for e in schema_errors(q,schema)];check('Question schema',not errors,errors)
check('No self-approved status',all(q['status']=='draft' and not q['reviewIds'] for q in batch['questions']),'Every authored object remains draft.')
check('Unique options',all(len({o['text'] for o in q['options']})==4 for q in batch['questions']),'Exact-text option uniqueness only; semantic review remains required.')
check('Nonempty calculation steps',all(q['solution']['steps'] for q in batch['questions'] if q['type'] in ('numerical','algorithm','derivation')),'Every declared computation has explanatory steps.')
check('Source-version conflict binding',all(q.get('conflictResolution',{}).get('sourceSha256')==q['citations'][0]['sourceSha256'] for q in batch['questions'] if any(c['role']=='conflict' for c in q['citations'])),'All conflict citations have source-version-bound qualification metadata.')
for q in batch['questions']:
 for e in q.get('externalEvidence',[]):assert hashlib.sha256((R/e['savedEvidencePath']).read_bytes()).hexdigest()==e['savedEvidenceSha256']
packet=json.loads((R/'audits/blind-W08-L38.json').read_text())
check('Answer-hidden packet',all('correctOptionIds' not in q and 'solution' not in q and all('evidenceText' not in c for c in q['citations']) for q in packet),'No keys, solutions or author citation transcriptions in blind packet.')
result={'authorId':'build_offline_study_interface:L38-author','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceCodePresent':False,'scope':'All source equations, diagrams and numeric tables are inspected. This script is author-added algebra testing, not source code or peer verification. No claimed reproduction of full case-study training.','namedChecks':checks,'namedChecksPassed':len(checks),'randomizedTrials':1000,'randomizedComparisonsPassed':comparisons,'independentReviewRequired':True}
(R/'audits/W08-L38-author-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(len(checks),'named author checks;',comparisons,'varied comparisons passed.')
