#!/usr/bin/env python3
"""Independent recomputation from the visually read assignment PDF. Printed answers were visible: not blind solves."""
import math,json,pathlib,hashlib,heapq,datetime
from fractions import Fraction as F
import numpy as np
R=pathlib.Path(__file__).resolve().parents[2];out=[]
def check(item,label,value,expected,assumptions=''):
 assert np.allclose(value,expected,rtol=1e-10,atol=1e-10),(item,value,expected)
 out.append({'sourceItemId':item,'check':label,'independentResult':np.asarray(value).tolist(),'comparison':'matches independently specified expected calculation','assumptions':assumptions})
def I(w,q):return f'ASSIGN-W{w:02}-Q{q:02}'
check(I(1,6),'Differentiate 3x²+2xy+y², then evaluate at (1,2)',[6*1+2*2,2*1+2*2],[10,6])
check(I(2,3),'Independent one-DOF serial joints',4+2,6)
q1,q2=0,math.pi/2
check(I(2,4),'2R forward kinematics',[2*math.cos(q1)+2*math.cos(q1+q2),2*math.sin(q1)+2*math.sin(q1+q2)],[2,2])
c2=F(4**2-3**2-2**2,2*3*2);check(I(2,6),'Cosine value, not the requested angle',float(c2),.25)
check(I(2,6),'Angle reconstructs the target radius',3**2+2**2+2*3*2*math.cos(math.acos(float(c2))),16)
out.append({'sourceItemId':I(2,6),'check':'Literal source conflict','cosine':float(c2),'twoLinkAnglesRadians':[math.acos(float(c2)),-math.acos(float(c2))],'twoLinkAnglesDegrees':[math.degrees(math.acos(float(c2))),-math.degrees(math.acos(float(c2)))],'literalPrompt':'3-link arm is underdetermined; no literal option established','conditionalModel':'2R planar arm with stated lengths'})
check(I(2,7),'Rank of dependent nonzero rows',np.linalg.matrix_rank([[1,2],[2,4]]),1)
check(I(2,9),'Local-frame conditional torque',.3*5,1.5,'Local lever arm x with force y component5N.')
out.append({'sourceItemId':I(2,9),'check':'Base-frame counterexample','phiRadians':math.pi/4,'torqueNm':.3*(-math.sin(math.pi/4)*10+math.cos(math.pi/4)*5),'meaning':'The same lengths/force with a different force-frame interpretation do not imply1.5Nm.'})
check(I(3,4),'Resultant-force magnitude',np.linalg.norm(4*np.array([3,0,4])),20)
# Independent velocity-Jacobian kinetic-energy assembly for two point masses.
a,b,m1,m2,t=2.,3.,4.,5.,.6
J1=np.array([[0.,0.],[a,0.]])
J2=np.array([[-b*math.sin(t),-b*math.sin(t)],[a+b*math.cos(t),b*math.cos(t)]])
M=m1*J1.T@J1+m2*J2.T@J2
expected=np.array([[(m1+m2)*a*a+m2*b*b+2*m2*a*b*math.cos(t),m2*b*b+m2*a*b*math.cos(t)],[m2*b*b+m2*a*b*math.cos(t),m2*b*b]])
check(I(3,9),'All four mass-matrix entries from point-mass velocity energy',M,expected,'Diagram masses at elbow and tip; relative theta2; massless rods.')
check(I(3,10),'Unordered pair counts for n1..6',[len([(i,j) for i in range(n) for j in range(i+1,n)]) for n in range(1,7)],[n*(n-1)//2 for n in range(1,7)])
check(I(4,6),'Reachable radial interval',[abs(5-4),5+4],[1,9],'Unrestricted 2R joints.')
check(I(4,10),'Both singular branches',[math.sin(0),math.sin(math.pi)],[0,0])
out.append({'sourceItemId':I(4,3),'check':'LSPB acceleration counterexample','leftAccelerationAtBlendJoin':2,'rightAccelerationAtBlendJoin':0,'continuousVelocity':True,'continuousAcceleration':False,'meaning':'Parabolic blend joined to constant-velocity line is generally C1 but not C2.'})
check(I(5,1),'Critical damping discriminant',6**2-4*1*9,0)
check(I(5,2),'Physical PD gains',[16-1,2*math.sqrt(4*16)-1],[15,15])
check(I(5,6),'Linear/cubic forces and ratio',[10*2,10*2**3,(10*2**3)/(10*2)],[20,80,4])
check(I(5,8),'Damping ratio',6/(2*math.sqrt(9)),1)
check(I(6,7),'Squared-error leaf minimizer',np.mean([12,15,18,20,25]),18)
x1,x2=12,3;leaf=[3,5,7] if x1<=10 else [10,14,18] if x2<=5 else [30,40]
check(I(6,8),'Read and route full tree then mean',np.mean(leaf),14)
check(I(6,10),'Nonterminal Q learning update',4+.1*(3+.9*10-4),4.8)
check(I(7,1),'Pinhole image separation',abs(20*1/2-20*1/4),5,'World coordinates assumed aligned with camera frame.')
check(I(7,3),'Installed NumPy uint8 array addition',(np.array([230],dtype=np.uint8)+50).tolist(),[24],f'NumPy{np.__version__}; ndarray uint8 operation, not saturating image API.')
img=np.arange(1,10).reshape(3,3);kernel=np.array([[1,2,0],[0,-1,1],[2,0,-2]])
check(I(7,4),'Full asymmetric correlation and convolution',[np.sum(img*kernel),np.sum(img*kernel[::-1,::-1])],[2,28])
check(I(7,5),'Circularity',4*math.pi*100/(40*40),math.pi/4)
check(I(7,8),'Bias conventions, same output',[.5*2-1*3+1,.5*2-1*3-1],[-1,-3])
check(I(7,9),'Kernel size from output',28+1-24,5)
edges=[('A','B',5),('A','C',2),('B','D',6),('B','E',3),('C','F',4),('D','E',2),('D','G',6),('E','F',1),('F','G',3)]
g={n:[] for n in 'ABCDEFG'}
for u,v,w in edges:g[u].append((v,w));g[v].append((u,w))
heap=[(0,'A',['A'])];seen={};trace=[]
while heap:
 cost,u,path=heapq.heappop(heap)
 if u in seen:continue
 seen[u]=cost;trace.append({'node':u,'settledCost':cost})
 if u=='E':break
 for v,w in g[u]:
  if v not in seen:heapq.heappush(heap,(cost+w,v,path+[v]))
assert path==['A','C','F','E'];check(I(8,1),'UCS shortest path cost',cost,7)
out.append({'sourceItemId':I(8,1),'check':'Actual graph full UCS settled trace','trace':trace,'path':path,'graphUndirected':True,'goalTest':'pop from priority queue'})
check(I(8,3),'A-star priorities',[4+2,3+2.4,1+4.8],[6,5.4,5.8])
check(I(8,6),'DQN nonterminal target',1+.9*max(3,5),5.5)
check(I(8,9),'Singleton weighted average',(.7*20+.3*60)/(.7+.3),32)
children=[.5*(2+6),1.5*2-.5*6,-.5*2+1.5*6]
check(I(9,1),'Linear crossover candidate coordinates',children,[4,0,8])
out.append({'sourceItemId':I(9,1),'check':'Missing fitness counterexample','maximize_x_top_two':sorted(children,reverse=True)[:2],'maximize_negative_square_top_two':sorted(children,key=lambda x:-x*x,reverse=True)[:2],'meaning':'Maximization alone is insufficient to select source pair4,8.'})
check(I(9,2),'6-bit code for real value11',(11-1)*(2**6-1)/(16-1),42)
points=[(0,0),(0,1),(2,4),(5,5)];obstacles={(1,1),(2,1),(2,2),(4,2),(2,3),(3,4)}
def route(order):
 p=[points[0]]
 for target in points[1:]:
  for axis in order:
   while p[-1][axis]!=target[axis]:
    nxt=list(p[-1]);nxt[axis]+=1 if target[axis]>nxt[axis] else -1;p.append(tuple(nxt))
 directions=[(b[0]-a[0],b[1]-a[1]) for a,b in zip(p,p[1:])]
 return {'path':p,'length':len(p)-1,'blockedEntries':sum(v in obstacles for v in p[1:]),'turns':sum(a!=b for a,b in zip(directions,directions[1:]))}
h=route([0,1]);v=route([1,0]);check(I(9,3),'Horizontal-first complete path components',[h['length'],h['blockedEntries'],h['turns']],[10,5,4])
check(I(9,3),'Fitness from path components',1/(1+h['length']+10*h['blockedEntries']+h['turns']),1/65)
out.append({'sourceItemId':I(9,4),'check':'Decode-order actual grid counterfactual','horizontalFirst':h,'verticalFirst':v})
check(I(9,6),'Input-hidden weight count',6*16,96)
check(I(9,7),'Linear Gaussian mean',np.array([2,2])+np.array([2,1]),[4,3])
check(I(9,7),'Linear Gaussian covariance',np.diag([.25,.16])+np.diag([.5,.4]),np.diag([.75,.56]))
check(I(9,9),'Augmented SLAM dimension',3+2*6,15)
J=np.eye(5);J[1,2]=2;P=np.diag([.04,.04,.01,.09,.09]);noise=np.diag([.01,.01,.0025,0,0]);cov=J@P@J.T+noise
check(I(9,10),'Full augmented covariance propagation',cov,[[.05,0,0,0,0],[0,.09,.02,0,0],[0,.02,.0125,0,0],[0,0,0,.09,0],[0,0,0,0,.09]])
check(I(10,2),'Alphabetical versus displayed one-hot index',[sorted(['chair','pick','red','ball','near']).index('near'),['chair','pick','red','ball','near'].index('near')],[2,4])
scores=np.array([7.,4.,1.])/math.sqrt(2);exps=np.exp(scores-scores.max());softmax=exps/exps.sum()
check(I(10,3),'Attention normalization',softmax.sum(),1)
out.append({'sourceItemId':I(10,3),'check':'Independent stable softmax','scaledScores':scores.tolist(),'probabilities':softmax.tolist(),'selectedApproximateOption':'A'})
check(I(10,4),'Q K V dimensions',[np.zeros((12,64)).dot(np.zeros((64,k))).shape[1] for k in [16,16,20]],[16,16,20])
check(I(10,5),'Valid convolution stride2 and stride1',[math.floor((100-2)/2)+1,(100-2)+1],[50,99])
check(I(10,6),'Sequence chain probability',.5*.4*.2,.04)
check(I(11,1),'Ideal energy-budget minutes',12*2.5/(10+5+5)*60,90)
check(I(11,3),'Distinct ADC reference models',[1023/1023*5,1023/1024*5,1023/1023*3.3],[5,4.9951171875,3.3])
check(I(11,4),'Matched count convention',1800/600,3)
check(I(11,5),'Effective torque-transfer model',.25*20*.85,4.25)
check(I(11,8),'SVM raw score and signed geometric distance',[2.5*3.2-7.5,(2.5*3.2-7.5)/abs(2.5)],[.5,.2])
check(I(11,10),'Toy torque predictor and absolute error',[2*.5+.5*2+1.5*3+.8,abs(8-(2*.5+.5*2+1.5*3+.8))],[7.3,.7])
check(I(12,2),'Parallel availability latency',max(80,120),120)
distance=24*math.hypot(.3,.2);speed=.6*8.2
check(I(12,4),'Repeated path distance',distance,8.653323061113573)
out.append({'sourceItemId':I(12,4),'check':'Ideal time','distanceMetres':distance,'speedMetresPerSecond':speed,'timeSeconds':distance/speed,'scope':'Given ideal speed, no acceleration/deceleration or hardware validation.'})
check(I(12,8),'Differential-drive twist',[.1*(5+(-5))/2,.1*(5-(-5))/.5],[0,2])
record={'reviewerId':'robotics-contracts-assignment-coverage-reviewer','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'Independent nonblind recomputation from actual assignment pixels; printed source keys visible.','scriptSha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'sourceSha256':hashlib.sha256((R/'sources/raw/AI_for_Robotics_All_Assignment_Solutions.pdf').read_bytes()).hexdigest(),'runtime':{'python':'default installed Python','numpy':np.__version__,'downloads':False,'modelsOrHardware':False},'checks':out,'checkRecordCount':len(out),'itemCount':len({x['sourceItemId'] for x in out})}
(R/'audits/assignment-coverage/independent-checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checkRecords':len(out),'items':record['itemCount'],'result':'passed; explicit counterexamples preserved'}))
