"""Independent source-based L53 mathematics, before keyed answer access."""
from pathlib import Path
import math,json,datetime,random,hashlib
R=Path(__file__).resolve().parents[1];out=R/'audits/W11-L53-contracts-independent-checks.json';assert not out.exists();checks=[]
def ck(q,label,got,expected):
 if isinstance(got,(list,tuple)):ok=all(math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10)for a,b in zip(got,expected))and len(got)==len(expected)
 else:ok=math.isclose(got,expected,rel_tol=1e-10,abs_tol=1e-10)
 assert ok,(q,label,got,expected)
 checks.append(dict(questionId='W11-L53-Q'+f'{q:03}',label=label,result=got,expected=expected,passed=True))
ck(5,'BIL sin30 degrees',.5*3*.2*math.sin(math.pi/6),.15)
ck(8,'Minus turns times per-turn flux derivative',-100*(.003-.001)/.020,-10)
kt=20*.4*.1*.05;ck(16,'Effective-N torque constant and torque',(kt,kt*2),(.04,.08))
ck(18,'Back EMF',.1*100,10)
I=(24-.1*100)/2;ck(19,'Armature current and torque',(I,.1*I),(7,.7))
ck(20,'Quasi-steady stall and ideal no-load intercepts',(.1*24/2,24/.1),(1.2,240))
ck(21,'Constant-flux torque-speed slope',-.1*.1/2,-.005)
ck(23,'Initial inductive derivative with zero current/back EMF',12/.020,600)
tau=.020/2;ck(24,'Electrical time constant and current after one tau',(tau,12/2*(1-math.exp(-1))),(.010,3.792723352971346))
ck(25,'Converted mechanical power and copper loss',(.1*7*100,7**2*2),(70,98))
ck(25,'Electrical power balance',24*7,70+98)
w=1.2/(2*.005);ck(26,'Maximum converted power speed and value',(w,(1.2-.005*w)*w),(120,72))
ck(29,'Unsaturated series-current torque ratio',(3/2)**2,2.25)
ck(32,'Shunt field plus armature line current',24/120+(24-20)/2,2.2)
ck(40,'Ideal 10-to-one gear speed and torque',(100/10,.2*10),(10,2))
ck(40,'Ideal gear power conservation',(100/10)*(.2*10),100*.2)
ck(41,'PWM duty and mean voltage',(30/50,24*30/50),(.6,14.4))
ck(42,'Doubling frequency at fixed duty leaves mean unchanged',24*.6,14.4)
ck(50,'Target minus tachogenerator-derived speed',100-1.6/.02,20)
ck(60,'One pole pair at 50 Hz',60*50/1,3000)
ns=120*50/4;ck(61,'Four-pole speed and induction slip',(ns,(ns-1440)/ns),(1500,.04))
for N,angle in [(12,30),(24,15),(72,5),(144,2.5),(180,2),(200,1.8)]:ck(64,f'{N} steps per revolution',360/N,angle)
ck(65,'Fifty full steps and pulse-train duration',(50*360/200,50/500),(90,.1))
ck(66,'Full-step speed in rpm',500/200*60,150)
ck(70,'Nearest next-phase rotor alignment',min(abs(45-k*60)for k in range(-3,4)),15)
def equilibrium(V,R,K,t0,b):return (K*V/R-t0)/(K*K/R+b)
w=equilibrium(24,2,.1,.2,.005);ck(76,'Motor-load equilibrium',(w,.2+.005*w),(100,.7))
w2=equilibrium(12,2,.1,.2,.005);ck(77,'Half-duty equilibrium',(w2,.2+.005*w2),(40,.4))
ck(79,'Motor-minus-load slope',-.1*.1/2-.005,-.010)
ck(80,'Rigid-shaft angular acceleration',(.8-.6)/.02,10)
ck(82,'Nominal eight-way microstep increment',360/(200*8),.225)
meanloss=((.6/.1)**2*2*2+(.2/.1)**2*2*6)/8;ck(87,'Time-weighted copper loss',meanloss,24)
ck(87,'Incorrect square of mean current yields o4',((.6/.1*2+.2/.1*6)/8)**2*2,18)
ck(87,'Incorrect unweighted segment average yields o1',(((.6/.1)**2*2)+((.2/.1)**2*2))/2,40)
ck(88,'Halving flux doubles ideal speed and same-torque current',(1/.5,1/.5),(2,2))
ck(91,'Stall shaft mechanical power',1.2*0,0)
rng=random.Random(5319);varied=0
for _ in range(1000):
 Rm=rng.uniform(.1,5);K=rng.uniform(.01,.5);V=rng.uniform(2,50);t0=rng.uniform(0,.8*K*V/Rm);b=rng.uniform(0,.05);w=equilibrium(V,Rm,K,t0,b);i=(V-K*w)/Rm;T=K*i
 assert math.isclose(T,t0+b*w,rel_tol=1e-9,abs_tol=1e-9);varied+=1
 assert math.isclose(V*i,i*i*Rm+T*w,rel_tol=1e-9,abs_tol=1e-9);varied+=1
 assert -(K*K/Rm+b)<0;varied+=1
 assert equilibrium(V*1.2,Rm,K,t0,b)>w;varied+=1
 lo=rng.uniform(0,V);on=rng.uniform(0,1);assert lo<=on*V+(1-on)*lo<=V+1e-12;varied+=1
report=dict(completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewerId='robotics-contracts-reviewer-L53',sourceSha256='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c',explicitChecks=len(checks),checks=checks,variedCases=1000,variedAssertions=varied,runtime='Default standard-library Python deterministic calculations only. The lecture contains equations, diagrams and examples, not a program/notebook. No dependency/model/audio/NLTK retrieval or restricted temporary environment used.',graphEvidence=dict(physicalPage=1709,renderPath='/tmp/L53-contracts/p1709-graph.png',renderSha256=hashlib.sha256(Path('/tmp/L53-contracts/p1709-graph.png').read_bytes()).hexdigest(),method='Personally inspected actual PDF crop rendered at 4x before any keyed material.',finding='At 2000 rpm, continuous boundary is below 1 N m and peak curve above it. Driver peak, continuous and commutation boundaries are distinct. No exact limit interpolated from a blurry thumbnail.'),primarySources=[dict(url='https://openstax.org/books/university-physics-volume-2/pages/11-4-magnetic-force-on-a-current-carrying-conductor',finding='Wire force depends on current, length, field and cross-product direction; no body translation needed.'),dict(url='https://openstax.org/books/university-physics-volume-2/pages/13-1-faradays-law',finding='Identical linked turns contribute total flux linkage N times per-turn flux; induced sign opposes change.'),dict(url='https://www.ti.com/video/6173360561001',finding='Official TI sensorless startup description includes alignment and initial position detection rather than universal external mechanical spinning.'),dict(url='https://www.ti.com/document-viewer/lit/html/SLAAE95A/GUID-46F248D2-1B32-4D5F-82E0-D1509641BB4F',finding='Official technical source describes BEMF-based sensorless rotor-position estimation.'),dict(url='https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-overview.html',finding='Independent stator winding phases, energized holding torque, load-dependent angle accuracy and nominal subdivisions are distinct. Source-specific two-type classification is not exhaustive of hybrid motors.')])
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'explicitChecks':len(checks),'variedAssertions':varied,'meanCopperLoss':meanloss}))
