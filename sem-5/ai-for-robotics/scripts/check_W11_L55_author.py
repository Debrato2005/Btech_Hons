"""Author-only checks of L55 transcribed and explicitly reconstructed equations.
No omitted DeLaN class is invented, no installation, no original notebook retrieval.
"""
from pathlib import Path
import json,datetime,hashlib,importlib.util,math,sys
import numpy as np
import sympy as S
from sklearn.preprocessing import StandardScaler
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from check_W11_L55_mlp_runtime import inverse_dynamics
checks=[]
def ck(name,value):
 assert bool(value),name
 checks.append(name)
q1,q2,v1,v2,a1,a2,m1,m2,l1,l2,g=S.symbols('q1 q2 v1 v2 a1 a2 m1 m2 l1 l2 g',real=True)
q=S.Matrix([q1,q2]);v=S.Matrix([v1,v2]);a=S.Matrix([a1,a2])
p1=S.Matrix([l1*S.cos(q1),l1*S.sin(q1)]);p2=p1+S.Matrix([l2*S.cos(q1+q2),l2*S.sin(q1+q2)])
u1=p1.jacobian(q)*v;u2=p2.jacobian(q)*v
K=S.trigsimp((m1*u1.dot(u1)+m2*u2.dot(u2))/2);V=g*(m1*p1[1]+m2*p2[1]);M=S.hessian(K,(v1,v2))
expected=S.Matrix([[(m1+m2)*l1*l1+m2*l2*l2+2*m2*l1*l2*S.cos(q2),m2*l2*l2+m2*l1*l2*S.cos(q2)],[m2*l2*l2+m2*l1*l2*S.cos(q2),m2*l2*l2]])
ck('Tip-mass velocity derivation gives the code-consistent mass matrix',all(S.trigsimp(x)==0 for x in M-expected))
momentum=S.Matrix([S.diff(K,x) for x in v]);tau=S.simplify(momentum.jacobian(q)*v+momentum.jacobian(v)*a-S.Matrix([S.diff(K,x) for x in q])+S.Matrix([S.diff(V,x) for x in q]))
h=m2*l1*l2*S.sin(q2);C=S.Matrix([-h*v2*v2-2*h*v1*v2,h*v1*v1]);G=S.Matrix([(m1+m2)*g*l1*S.cos(q1)+m2*g*l2*S.cos(q1+q2),m2*g*l2*S.cos(q1+q2)])
ck('Euler–Lagrange torque equals inertia plus printed C and G',all(S.trigsimp(x)==0 for x in tau-expected*a-C-G))
ck('Physical kinetic energy includes one-half',S.trigsimp(K-(v.T*expected*v)[0]/2)==0)
ck('Gravity is the configuration gradient of potential',all(S.simplify(x)==0 for x in S.Matrix([S.diff(V,x) for x in q])-G))
ck('Mass matrix symmetry',M==M.T)
unit={m1:1,m2:1,l1:1,l2:1};Mu=S.simplify(expected.subs(unit))
ck('Unit determinant 2-cos²q2',S.simplify(Mu.det()-(2-S.cos(q2)**2))==0)
ck('Unequal-mass correction is 6 rather than 8',expected[0,0].subs({m1:2,m2:1,l1:1,l2:1,q2:0})==6)
ck('General printed mass-coefficient error',S.simplify((2*m1*l1*l2*S.cos(q2)-2*m2*l1*l2*S.cos(q2))-2*(m1-m2)*l1*l2*S.cos(q2))==0)
E=K+V;Edot=(S.Matrix([S.diff(E,x) for x in q]).dot(v)+S.Matrix([S.diff(E,x) for x in v]).dot(a))
ck('Forced mechanical energy rate equals generalized torque power',S.trigsimp(Edot-tau.dot(v))==0)
x,w,aa=S.symbols('x w aa');H=1+x*x;Ks=H*w*w/2;Vs=2*x
Ts=H*aa+S.diff(H,x)*w*w-S.diff(Ks,x)+S.diff(Vs,x)
ck('Added scalar physical Euler–Lagrange result is 12',Ts.subs({x:1,w:2,aa:3})==12)
wrong=H*aa+S.diff(H,x)*w*w-S.diff(Ks,x)/2+S.diff(Vs,x)
ck('Flowchart double-half gives 14 in added scalar example',wrong.subs({x:1,w:2,aa:3})==14)
L=np.array([[2.,0.],[1.,1.]]);HH=L@L.T;vv=np.array([1.,-1.]);ck('Lower-factor H and kinetic energy',np.allclose(HH,[[4,2],[2,2]]) and np.isclose(vv@HH@vv/2,1))
ck('Transpose-order distractor kinetic energy',np.isclose(vv@(L.T@L)@vv/2,2))
ck('Added coupled inverse example',np.allclose(np.array([[3,1],[1,2]])@np.array([2,-1])+[1,-2]+np.array([4,3]),[10,1]))
ck('Added coupled forward solve',np.allclose(np.linalg.solve([[3,1],[1,2]],[5,0]),[2,-1]))
ck('Explicit Euler position and velocity',np.allclose(np.array([0,1])+.1*np.array([2,-1]),[.2,.9]) and np.allclose(np.array([2,-1])+.1*np.array([-4,3]),[1.6,-.7]))
ck('58000 samples at 5 ms endpoint duration',math.isclose(57999*.005,289.995) and 1/.005==200)
ck('Small network parameter count',sum((u+1)*v for u,v in zip([6,30,20],[30,20,2]))==872)
ck('Illustrative 32-width network count',sum((u+1)*v for u,v in zip([6,32,32],[32,32,2]))==1346)
ck('Large network parameter count',sum((u+1)*v for u,v in zip([6,256,256,128],[256,256,128,2]))==100738)
ck('Large network weights-only count',sum(u*v for u,v in zip([6,256,256,128],[256,256,128,2]))==100096)
ck('Training/test split row arithmetic',int(.9*50000)==45000 and int(.9*5000)==4500)
sc=StandardScaler().fit([[2,3],[2,7]]);ck('Constant feature fallback scale and centering',sc.scale_[0]==1 and np.all(sc.transform([[2,3],[2,7]])[:,0]==0))
ck('Added standardized score', (10-2)/4==2)
ck('Per-joint RMSE arithmetic',math.isclose(np.sqrt(np.mean(np.square([3,4]))),math.sqrt(12.5)))
ck('Mean-reduced torque MSE',np.mean(np.square([[1,-1],[2,-2]]))==2.5)
ck('Full-batch count and remainder',4500//128==35 and 35*128==4480 and 4500-35*128==20)
ck('Full training loop optimizer steps',500*(4500//128)==17500)
ck('Unnormalized sum of equal minibatch means',math.isclose(sum([.2]*35),7))
t=S.symbols('t');angle=S.sin(t);elbow=S.sin(2*t)/2
ck('Shoulder sinusoid derivatives',S.diff(angle,t)==S.cos(t) and S.diff(angle,t,2)==-S.sin(t))
ck('Elbow sinusoid derivatives',S.diff(elbow,t)==S.cos(2*t) and S.diff(elbow,t,2)==-2*S.sin(2*t))
ck('Trajectory grid intervals',math.isclose(np.linspace(0,4*np.pi,300)[1],4*np.pi/299))
ck('Source start-path torque',np.allclose(inverse_dynamics(0,0,1,1,0,0),[29.43,9.81]))
ck('Start-path wrong-acceleration foil',np.allclose(inverse_dynamics(0,0,1,1,1,1),[36.43,12.81]))
ck('Source quarter-period torque',np.allclose(inverse_dynamics(1,0,0,-1,-1,0),[-5+29.43*np.cos(1),-2+9.81*np.cos(1)]))
ck('Integrated nonzero-C example',np.allclose(inverse_dynamics(0,np.pi/2,2,-1,1,-2),[23.62,3]))
ck('Reported shoulder reduction',round(100*(.6311-.2826)/.6311,2)==55.22)
ck('Reported elbow reduction',round(100*(.3734-.1895)/.3734,2)==49.25)
rng=np.random.default_rng(5519);varied=0
for _ in range(1000):
 qq=rng.uniform(-np.pi,np.pi,2);vv=rng.uniform(-2*np.pi,2*np.pi,2);aa=rng.uniform(-10,10,2);c=np.cos(qq[1]);ss=np.sin(qq[1]);mm=np.array([[3+2*c,1+c],[1+c,1.]])
 cc=np.array([-ss*vv[1]**2-2*ss*vv[0]*vv[1],ss*vv[0]**2]);gg=np.array([19.62*np.cos(qq[0])+9.81*np.cos(qq.sum()),9.81*np.cos(qq.sum())]);tt=np.array(inverse_dynamics(*qq,*vv,*aa))
 assert np.allclose(tt,mm@aa+cc+gg);varied+=1
 assert np.allclose(np.linalg.solve(mm,tt-cc-gg),aa);varied+=1
 assert np.linalg.eigvalsh(mm).min()>0 and np.linalg.det(mm)>=1-1e-12;varied+=1
 mdot=np.array([[-2*ss,-ss],[-ss,0.]])*vv[1];assert np.isclose(vv@cc,.5*vv@mdot@vv);varied+=1
 assert .5*vv@mm@vv>=-1e-12;varied+=1
runtime=json.loads((R/'audits/W11-L55-mlp-runtime.json').read_text());ck('Executed MLP has expected shape and parameter count',runtime['shapes']['X']==[50000,6] and runtime['parameterCount']==100738)
ck('Executed MLP uses training-only scaler statistics',runtime['scalerTrainingMeanMatches'])
ck('Executed MLP stops within max_iter',0<runtime['epochsActuallyExecuted']<=500)
ck('Source report separated from seeded result',runtime['sourceExactOutputReproduced'] is False and runtime['seedAdded']==5519)
# Inspect absence, not attempt to install or use a restricted environment.
torch_available=importlib.util.find_spec('torch') is not None
result={'batchId':'W11-L55','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentReview':False,'status':'Author checks passed; distinct independent source-first review remains required.','namedChecks':len(checks),'checks':checks,'variedChecks':varied,'variedTrials':1000,'versions':{'numpy':np.__version__,'sympy':S.__version__},'runtimeEvidence':'audits/W11-L55-mlp-runtime.json','runtimeEvidenceSha256':hashlib.sha256((R/'audits/W11-L55-mlp-runtime.json').read_bytes()).hexdigest(),'executionBoundaries':{'MLP':'Full 50000-row printed-parameter MLP executed with disclosed added seed 5519.','DeLaN':'Not executed: DeLaN2R class absent from lecture; torch not installed in default environment at check time. No package installation or original-notebook retrieval attempted.','torchAvailableInDefaultEnvironment':torch_available,'physicalRobot':'Not executed.','browser':'Actual downloaded-file browser QA remains blocked; zero checks executed.'},'plotVisualQA':{'path':'audits/W11-L55-author-mlp-trajectory.png','viewedAt':'2026-10-19T23:47:40+00:00','result':'Both labelled joint plots legible; reference and seeded-MLP curves show small visible residuals. Not the source figure or DeLaN output.'}}
(R/'audits/W11-L55-author-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'named':len(checks),'varied':varied,'torchAvailable':torch_available}))
