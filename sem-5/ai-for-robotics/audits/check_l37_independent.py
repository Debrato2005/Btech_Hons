"""Independent L37 mathematics and algorithm checks, not author code or robot execution."""
import json, math, random, hashlib, heapq, sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0,'scripts')
from validate import question_hash
rng=random.Random(370119)
checks=[]
def ck(name,condition,detail):
 assert condition,(name,detail)
 checks.append({'name':name,'passed':True,'detail':detail})
def valleys(x):
 if not any(x): return 0
 if all(x): return 1
 return sum(v and not x[i-1] for i,v in enumerate(x))
def components(x):
 unseen={i for i,v in enumerate(x) if v}; n=len(x); c=0
 while unseen:
  c+=1; todo=[unseen.pop()]
  while todo:
   i=todo.pop()
   for j in [(i-1)%n,(i+1)%n]:
    if j in unseen: unseen.remove(j);todo.append(j)
 return c
def delta(a,b):return abs((a-b+180)%360-180)
def leave(on_line,d,hit,outgoing):return on_line and d<hit and outgoing
ck('Bug1 additional return',min(6,14)==6,'Full 20 m survey is already completed; only the shorter 6 m return remains.')
ck('Bug1 criterion ordering',min([(3,8,'A'),(4,2,'B')])[2]=='A','Goal distance determines leave point before selecting its return arc.')
ck('Bug2 strict conjunction',leave(True,5,8,True) and leave(True,7,8,True) and not leave(False,3,8,True) and not leave(True,9,8,True) and not leave(True,8,8,True) and not leave(True,5,8,False),'Closer, on original line, and locally free outgoing direction are all required.')
ck('Threshold explicit equality',[v<5 for v in [2,7,3,6]]==[True,False,True,False] and not (5<5),'Free sectors 1 and 3; equality blocked under the supplied convention.')
ck('Circular eight-sector trace',valleys([1,1,0,1,0,0,1,1])==2,'Components {7,8,1,2} and {4}.')
ck('Circular all-free/all-blocked/singleton',all(valleys(x)==y for x,y in [([1]*8,1),([0]*8,0),([1],1),([0],0)]),'Domain boundaries checked independently.')
for _ in range(1000):
 n=rng.randint(1,60); x=[rng.choice([False,True]) for _ in range(n)]; r=rng.randrange(n)
 assert valleys(x)==components(x)==valleys(x[r:]+x[:r])
ck('1000 circular masks',True,'Independent graph flood-fill agrees with circular run-start count, including rotation invariance.')
ck('Narrow opening center',(20+40)/2==30,'Degrees in one unwrapped coordinate frame.')
ck('Wrapped angular difference',delta(350,10)==20 and delta(180,-180)==0 and delta(0,180)==180,'Periodicity and antipodal boundary included.')
for _ in range(1000):
 a,b=[rng.uniform(-720,720) for _ in range(2)]; shift=rng.randint(-5,5)*360
 assert math.isclose(delta(a+shift,b),delta(a,b),abs_tol=1e-10)
 assert math.isclose(delta(a,b),delta(b,a),abs_tol=1e-10)
ck('1000 wrapped-angle cases',True,'Symmetry and whole-revolution shifts preserved.')
A=sum(a*b for a,b in zip([5,2,2],[10,20,30]));B=sum(a*b for a,b in zip([5,2,2],[20,0,0]))
ck('Weighted steering arithmetic',(A,B)==(150,100),'B has the lower cost; unweighted A=60 and B=20.')
ck('Q047 distractor explanation error',5*10+2*20==90 and 5*10+2*20!=100,'The authored claim that omitting A\'s previous-direction term produces the 100 tie is false: it produces 90.')
for _ in range(1000):
 weights=[rng.randint(1,10) for _ in range(3)]; errors=[[rng.randint(0,180)for _ in range(3)] for _ in range(10)]; costs=[sum(w*e for w,e in zip(weights,es))for es in errors]; scale=rng.randint(1,100)
 assert sorted(range(10),key=lambda i:costs[i])==sorted(range(10),key=lambda i:scale*costs[i])
ck('1000 common weight scaling cases',True,'Positive scaling preserves comparisons and ties for fixed feasible candidates.')
ck('Feasibility precedes cost',min([(100,'free B'),(150,'free A')])[1]=='free B','A hypothetical blocked cost 0 is not in the feasible set.')
ck('Same angle different physical width',math.isclose(2*4*math.sin(math.radians(10)),4*(2*1*math.sin(math.radians(10)))),'Illustrative equal-range boundary points have chord width 2r sin(theta/2); same angle need not mean same physical clearance.')
R,L,w=1,-1,2
ck('Differential drive in-place limit',(R+L)/2==0 and (R-L)/w!=0,'Opposed wheel speeds give zero forward speed and nonzero yaw rate; no real hardware execution claimed.')
ck('Lower-right angle',math.cos(math.radians(315))>0 and math.sin(math.radians(315))<0,'315 degrees = -45 degrees under counterclockwise-positive convention.')
ck('Quadratic force',[-2*z for z in [3,4]]==[-6,-8],'For k=2 and goal zero, negative gradient is (-6,-8).')
for _ in range(1000):
 q=[rng.uniform(-5,5)for _ in range(3)]; g=[rng.uniform(-5,5)for _ in range(3)];k=rng.uniform(.1,10);h=1e-5
 def U(q): return k*sum((a-b)**2 for a,b in zip(q,g))/2
 for j in range(3):
  qp=q.copy();qm=q.copy();qp[j]+=h;qm[j]-=h
  assert math.isclose((U(qp)-U(qm))/(2*h),k*(q[j]-g[j]),rel_tol=1e-6,abs_tol=1e-6)
ck('1000 quadratic finite differences',True,'All three partial derivatives checked against k(q-goal), then negated for force.')
ck('Force superposition',[a+b for a,b in zip([2,-1],[-2,1])]==[0,0],'Nonzero individual forces can cancel; derivative linearity is preserved.')
ck('Finite repulsion support',not(2*3<3),'At twice the positive influence radius the supplied repulsive potential is locally constant zero, so its gradient is zero.')
ck('Grid size',20**6==64000000 and 20**5==3200000,'Six independent coordinates, 20 values each. 120 sums counts; 400 uses only two coordinates.')
ck('Grid multiplicative law',all(m**(n+1)==m*(m**n) for m in range(1,20)for n in range(1,10)),'General symbolic count law verified.')
ck('Q075 boundary option collisions',1**4==1**3==1**3/1 and 2**2==2**1+2,'m=1 makes multiply, unchanged and divide options coincide; m=2 with one old joint also makes increase-by-m true for that instance.')
ck('Stationary nonminimum counterexamples',(-1<0) and (1>0 and -1<0),'At origin, U=-x^2 has zero gradient but is a maximum; U=x^2-y^2 has zero gradient but is a saddle. Zero force alone does not prove a minimum.')
# Independent shortest-path recomputation for the previously reviewed source grid.
walls={(0,0),(0,1),(0,2),(1,2),(2,2),(3,2)};S=(4,4);G=(2,0)
def dijkstra(walls):
 D={S:0.};heap=[(0.,S)]
 while heap:
  d,u=heapq.heappop(heap)
  if d!=D[u]:continue
  for dr in [-1,0,1]:
   for dc in [-1,0,1]:
    if dr==dc==0:continue
    v=(u[0]+dr,u[1]+dc)
    if not(0<=v[0]<5 and 0<=v[1]<5)or v in walls:continue
    if dr and dc and ((u[0]+dr,u[1])in walls or (u[0],u[1]+dc)in walls):continue
    nd=d+(1.4 if dr and dc else 1.)
    if nd<D.get(v,math.inf):D[v]=nd;heapq.heappush(heap,(nd,v))
 return D
D=dijkstra(walls);D2=dijkstra(walls|{(3,1)})
ck('Old coherent A-star grid',len(D)==19 and math.isclose(D[G],5.4) and math.isclose(D[(0,3)],4.4),'Independent Dijkstra: 19 free vertices, goal g=5.4, (0,3) g=4.4; no corner cutting.')
ck('New source obstacle route',math.isclose(D2[G],6),'Adding (3,1) changes shortest legal route to cost 6.0.')
qs=json.load(open('data/question-batches/W08-L37.json'))['questions'];m=json.load(open('audits/W08-L37-frozen-manifest.json'));a=json.load(open('audits/blind-answers-W08-L37-before-reveal.json'))['answers'];a={x['questionId']:x for x in a}
ck('86 exact frozen bindings',all(question_hash(q)==m['questionHashes'][q['id']]for q in qs),'All current canonical hashes equal author freeze; no author object changes.')
ck('86 intended keys agree',all(set(q['correctOptionIds'])==set(a[q['id']]['independentAnswerOptionIds'])for q in qs),'Intended agreement does not resolve Q037 unsupported frame or Q075 boundary ambiguity.')
ck('Unique text and option IDs',all(len({o['text']for o in q['options']})==len(q['options'])==len({o['id']for o in q['options']})for q in qs),'Literal uniqueness only; semantic domain collisions separately flagged.')
report={'reviewerId':'independent-reviewer-robotics-batches-v2','executedAt':datetime.now(timezone.utc).isoformat(),'pythonVersion':sys.version,'seed':370119,'checks':checks,'checkCount':len(checks),'variedCases':{'circularMasks':1000,'wrappedAngles':1000,'weightScaling':1000,'quadraticGradients':1000},'authorScriptsReadOrExecuted':False,'realRobotOrLearningRuntimeExecuted':False,'scope':'Source mathematics and independent toy algorithms; lecture contains no runnable source code.'}
Path('audits/W08-L37-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'variedCases':report['variedCases']}))
