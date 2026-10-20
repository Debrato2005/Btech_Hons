"""Independent source-first L55 working, not author answer data."""
import json,hashlib,pathlib,datetime,math,random,sys
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from threadpoolctl import threadpool_limits
P=pathlib.Path(__file__).resolve().parents[1]; A=P/'audits'
packet=A/'blind-W11-L55.json'; expected='cfa26d0c2ae85df95cd0986c82a20cefe88e1a4a2138e642d70429d29cae5366'
assert hashlib.sha256(packet.read_bytes()).hexdigest()==expected
answers=[1,4,3,2,1,4,3,2,1,4,3,2,1,4,3,2,1,4,3,2,1,4,3,2,1,4,3,2,1,4,3,2,1,4,3,2,1,4,3,2,1,4,3,2,1,4,3,2,1,4,3,2,1,4,3,None,1,4,3,2,1,4,3,2,1,4,3,2,1,4,3,2]
notes='''Backlash and compliance are omitted physical effects, not ideal identities.
New payload requires relevant data and model update; a network is not automatically adaptive.
Observed minus nominal torque is (2,-3) N m.
Inverse dynamics computes torque from state and acceleration; forward dynamics computes acceleration from state and torque.
C already denotes an n-vector of velocity-product torques in this displayed convention.
Matrix times acceleration gives (5,0), then C+G=(5,1), hence (10,1).
Solving the 2x2 system M a=(5,0) gives (2,-1).
Explicit Euler uses the old velocity for q and old acceleration for velocity: (.2,.9) and (1.6,-.7).
Universal approximation is a capacity statement, not a training or extrapolation guarantee.
Differentiable maps support gradient calculations and physics-derived learning.
The listed physics-informed families are DeLaN, Hamiltonian networks and PINNs.
Forward dynamics has 6 inputs for 2 joints and 2 acceleration outputs.
The illustrative 32/32 drawing is not the later specified 30/20 example.
Parameter count is (6+1)*30+(30+1)*20+(20+1)*2=872.
Nominal-data pretraining precedes fine-tuning on real-robot data.
The reported iterations and tolerance are historical setup choices, not universal stopping guarantees.
A 5 ms interval is 200 Hz; 58000 endpoint samples span 57999*0.005=289.995 s.
For natural frequency 8 Hz the strict sub-half condition is f<4 Hz; 3 qualifies.
Novel input tests require integration and comparison with physical-robot motion.
The drawing uses massless links, tip masses, horizontal q1 and relative q2.
Analytical dynamics generate supervised labels; the fitted mapping does not call the generator at inference.
The distal-mass coupling uses m2; equal masses hide the printed m1 discrepancy.
True M11=3+1+2=6; the printed m1 coupling would give 8.
The unit-arm determinant is 2-cos(q2)^2, at least 1, and its first principal minor is positive.
C1=-1+4=3 and C2=4.
At rest q=0, gravity is (3g,g)=(29.43,9.81).
M a=(1,-1), C=(3,4), G=(19.62,0), giving (23.62,3).
The feature order is positions, velocities, then accelerations.
Only the first state meets all three coordinate bounds.
Independent uniform marginals do not imply Cartesian-uniform density or compatible time derivatives.
The input has 6 columns, torque has 2, and the 90:10 split is 45000/5000.
Split and MLP seeds do not seed earlier NumPy sampling.
The pipeline fits training statistics once and reuses them for held-out inputs.
(10-2)/4=2.
A zero-variance feature gets scale 1 and becomes zero after default centering; official API documentation checked.
6-256-256-128-2 affine layers contain 100738 parameters with biases.
For default Adam max_iter limits epochs; convergence can stop earlier and each epoch has minibatches.
The displayed drawing lacks aggregation; the code computes sqrt(mean(square(error))).
The RMS of 3 and 4 is sqrt(12.5).
The plots show close but nonidentical trajectory torque estimates, not universal or closed-loop guarantees.
Position alone inputs H/V networks, but full torque computation also uses velocity and acceleration.
H is a symmetric positive-definite inertia matrix and V is scalar potential.
L L transpose is [[4,2],[2,2]]; half v transpose H v equals 1.
The first energy equation defines twice physical kinetic energy, so its half gradient is the physical gradient.
When the flowchart already includes half in kinetic energy, the further half gradient is erroneous.
H a=6, Hdot*v=8, dK/dq=4 and dV/dq=2; torque is 12.
Total Hdot is the sum of configuration partial derivatives weighted by their joint velocities.
The configuration gradient of V is gravity-compensation torque.
The two historical examples suggest data efficiency but do not establish a universal 10x rule.
The analytical function labels sampled states; it does not supply the missing network definition.
Q_tr is 4500 by 2 and TAU_te is 500 by 2, explicitly float32.
One torque row must stay paired with the state that generated it.
The lecture instantiates but does not define DeLaN2R, so this is not standalone executable training code.
Floor division gives 35 full batches, 4480 rows used and 20 omitted.
35*500=17500 updates; random permutation changes which rows can be omitted.
No option matches the literal source order: prediction, loss, zero_grad, backward, step. Option o2 is an equivalent conventional reordering, but the question asks what matches the source.
Mean squared error over all four entries is (1+1+4+4)/4=2.5.
The log-loss curve has local increases despite its overall decline; training loss is not test RMSE.
Evaluation mode and recording derivatives are separate mechanisms, and energy differentiation still needs gradients.
A GPU tensor must move to CPU for this NumPy conversion; detach only removes gradient attachment.
(0.6311-0.2826)/0.6311*100 is approximately 55.22 percent.
Differentiating 0.5 sin(2t) twice yields cos(2t) and -2 sin(2t).
300 inclusive time samples have 299 intervals, and each state has 2 positions.
At t=0 accelerations and velocity products are zero, so torque equals gravity.
M at q2=0 is [[5,2],[2,1]]; a=(-1,0), C=0, G=(3g cos1,g cos1).
Robust closed-loop claims need an explicit controller and disturbance/limit tests or analysis.
For a time-invariant conservative model dE/dt equals applied power tau dot velocity, not zero for arbitrary actuation.
A residual learned from suitable data can capture speed-dependent friction while retaining known rigid-body terms.
The displayed constructor sets hidden_size=64,n_layers=2 and Adam lr=.001,weight_decay=.0001; missing implementation limits stronger structural claims.
Thirty-five minibatch means of .2 sum to 7 before normalization.
The summary names RNEA and ABA.
Feedforward torque uses inverse dynamics; simulation acceleration uses forward dynamics.'''.splitlines()
assert len(answers)==len(notes)==72
checks=[]
def ck(name,value):
 assert bool(value),name
 checks.append(name)
def model(q1,q2,v1,v2,a1,a2,m1=1.,m2=1.,l1=1.,l2=1.,g=9.81):
 c,s=np.cos(q2),np.sin(q2)
 M=np.array([[(m1+m2)*l1*l1+m2*l2*l2+2*m2*l1*l2*c,m2*l2*l2+m2*l1*l2*c],[m2*l2*l2+m2*l1*l2*c,m2*l2*l2]])
 h=m2*l1*l2*s;C=np.array([-h*v2*v2-2*h*v1*v2,h*v1*v1]);G=np.array([(m1+m2)*g*l1*np.cos(q1)+m2*g*l2*np.cos(q1+q2),m2*g*l2*np.cos(q1+q2)])
 return M@np.array([a1,a2])+C+G,M,C,G
ck('FD/ID inverse solve',np.allclose(np.linalg.solve([[3,1],[1,2]],[5,0]),[2,-1]))
ck('872 parameter small example',sum((a+1)*b for a,b in zip([6,30,20],[30,20,2]))==872)
ck('100738 parameter MLP',sum((a+1)*b for a,b in zip([6,256,256,128],[256,256,128,2]))==100738)
ck('C numerical',np.allclose(model(0,np.pi/2,2,-1,0,0)[2],[3,4]))
ck('static gravity',np.allclose(model(0,0,0,0,0,0)[0],[29.43,9.81]))
ck('full torque example',np.allclose(model(0,np.pi/2,2,-1,1,-2)[0],[23.62,3]))
ck('unequal mass typo counterexample',abs(model(0,0,0,0,0,0,m1=2)[1][0,0]-6)<1e-12)
L=np.array([[2,0],[1,1]]);H=L@L.T;v=np.array([1,-1]);ck('factor positive inertia',np.array_equal(H,[[4,2],[2,2]]) and .5*v@H@v==1)
ck('one joint Euler Lagrange',2*3+4*2-4+2==12)
sc=StandardScaler().fit(np.array([[2.,0],[2.,2]]));ck('constant feature supported behavior',sc.scale_[0]==1 and np.all(sc.transform([[2.,0],[2.,2]])[:,0]==0))
ck('RMSE',np.isclose(np.sqrt(np.mean(np.array([3.,4.])**2)),math.sqrt(12.5)))
ck('MSE batch',np.mean(np.array([[1.,-1.],[2.,-2.]])**2)==2.5)
ck('reported relative reduction',abs((.6311-.2826)/.6311*100-55.221042624)<1e-7)
ck('floor batches',4500//128==35 and 35*128==4480 and 500*35==17500)
ck('sinusoid at zero',np.allclose(model(0,0,1,1,0,0)[0],[29.43,9.81]))
ck('sinusoid at pi half',np.allclose(model(1,0,0,-1,-1,0)[0],[-5+29.43*np.cos(1),-2+9.81*np.cos(1)]))
rng=np.random.default_rng(20261020); varied=0
for row in rng.uniform(-2,2,(5000,6)):
 q1,q2,v1,v2,a1,a2=row; tau,M,C,G=model(*row);c=np.cos(q2)
 assert np.allclose(M,M.T) and np.linalg.det(M)>0
 assert abs(np.linalg.det(M)-(2-c*c))<1e-10
 assert np.allclose(np.linalg.solve(M,tau-C-G),[a1,a2])
 # Independently evaluate Coriolis terms from energy gradients and directional mass derivative.
 eps=1e-5;Mp=model(q1,q2+eps,0,0,0,0)[1];Mm=model(q1,q2-eps,0,0,0,0)[1];dM=(Mp-Mm)/(2*eps);vel=np.array([v1,v2]);gradK=np.array([0.,.5*vel@dM@vel]);energyC=dM*v2@vel-gradK
 assert np.allclose(C,energyC,atol=1e-8)
 varied+=4
# A deliberately small independent source-transcribed pipeline smoke test, not reproduction of the historical 50000-row training result.
X=rng.uniform(-1,1,(64,6));Y=np.stack([model(*r)[0] for r in X]);pipe=Pipeline([('sc',StandardScaler()),('mlp',MLPRegressor(hidden_layer_sizes=(256,256,128),activation='tanh',max_iter=2,learning_rate_init=.001,random_state=42))])
import warnings
with threadpool_limits(limits=1),warnings.catch_warnings():
 warnings.simplefilter('ignore');pipe.fit(X,Y)
ck('source-transcribed small pipeline shapes',pipe.predict(X[:3]).shape==(3,2) and sum(x.size for x in pipe['mlp'].coefs_+pipe['mlp'].intercepts_)==100738)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
working={'reviewerId':'robotics-integration-L55-independent','packetPath':str(packet.relative_to(P)),'packetSha256':expected,'solvedAt':now,'solvedBeforeKeyedAccess':True,'priorAuthorExposure':False,'sourcePagesPersonallyViewed':list(range(1745,1777)),'sourceVersion':'2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c','answers':[{'questionId':f'W11-L55-Q{i:03d}','independentAnswerOptionIds':[] if a is None else [f'o{a}'],'reasoning':n,**({'conditionalIntendedOptionIds':['o2'],'requiredRepairAssumption':'Reword to an equivalent valid update order, or change o2 to the literal displayed order.'} if a is None else {})} for i,(a,n) in enumerate(zip(answers,notes),1)],'externalSources':[{'url':'https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html','checkedAt':now,'claim':'Zero variance yields scale 1; training mean and variance determine transformation.'},{'url':'https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html','checkedAt':now,'claim':'Default Adam uses max_iter as epoch limit and can converge earlier.'}]}
out=A/'blind-answers-W11-L55-integration.json';assert not out.exists();out.write_text(json.dumps(working,ensure_ascii=False,indent=2)+'\n')
report={'passed':True,'explicitChecks':len(checks),'checkNames':checks,'variedStates':5000,'variedAssertions':varied,'runtime':'Default installed Python, NumPy, scikit-learn; source-derived algebra and a 64-row, 2-epoch pipeline smoke test, not exact historical reproduction. No PyTorch, model download, hardware or denied venv used.','blindAnswersSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'sourceProgramScope':'Analytical ID equations and MLP pipeline independently transcribed from inspected pages; full DeLaN cannot run without missing class.'}
(A/'W11-L55-integration-independent-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
