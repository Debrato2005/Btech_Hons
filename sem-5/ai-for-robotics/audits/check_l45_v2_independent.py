"""Independent changed/new L45 math checks. Reuses, but does not repeat, own v1 source-reconstructed simulations."""
import numpy as np, json, pathlib, datetime, hashlib
checks=[]
def check(name, condition):
 assert bool(condition), name
 checks.append(name)
def observation(state):
 dx,dy=state[3:5]-state[:2]
 return np.array([np.hypot(dx,dy),np.arctan2(dy,dx)-state[2]])
def joint_jacobian(state):
 dx,dy=state[3:5]-state[:2]; r=np.hypot(dx,dy)
 return np.array([[-dx/r,-dy/r,0,dx/r,dy/r,0,0],[dy/r**2,-dx/r**2,-1,-dy/r**2,dx/r**2,0,0]])
def numerical_jacobian(fun,x):
 eps=1e-6
 return np.column_stack([(fun(x+eps*np.eye(len(x))[i])-fun(x-eps*np.eye(len(x))[i]))/(2*eps) for i in range(len(x))])
x=np.array([0.,0.,0.,3.,4.,8.,9.]); H=joint_jacobian(x)
check('new Q079 exact joint two-by-seven derivative',np.allclose(H,[[-.6,-.8,0,.6,.8,0,0],[.16,-.12,-1,-.16,.12,0,0]]))
check('new Q079 centered finite difference',np.allclose(H,numerical_jacobian(observation,x),atol=1e-8))
check('new Q079 unobserved landmark has zero direct columns',np.array_equal(H[:,5:],np.zeros((2,2))))
check('map-state versus dense covariance growth',[3+2*5,(3+2*5)**2]==[13,169])
rng=np.random.default_rng(4526)
for trial in range(1000):
 state=rng.normal(size=7);state[3:5]=state[:2]+rng.uniform(.2,6,2)
 assert np.allclose(joint_jacobian(state),numerical_jacobian(observation,state),atol=2e-7)
 M=int(rng.integers(1,7));A=rng.normal(size=(2*M,2*M));P=A@A.T+.1*np.eye(2*M);C=rng.normal(size=(2,2));W=C@C.T+.01*np.eye(2);angle=rng.uniform(-3,3);r=rng.uniform(.1,8);G=np.array([[np.cos(angle),-r*np.sin(angle)],[np.sin(angle),r*np.cos(angle)]])
 J=np.zeros((2*M+2,2*M+2));J[:2*M,:2*M]=np.eye(2*M);J[-2:,-2:]=G;initial=np.zeros_like(J);initial[:2*M,:2*M]=P;initial[-2:,-2:]=W;aug=J@initial@J.T
 assert np.allclose(aug[:2*M,:2*M],P) and np.allclose(aug[-2:,-2:],G@W@G.T) and np.array_equal(aug[:2*M,-2:],np.zeros((2*M,2))) and np.linalg.eigvalsh(aug).min()>0
 fy=rng.uniform(100,1000);height=rng.uniform(.1,2);v0=rng.uniform(50,400);row=v0+rng.uniform(.2,300);eps=(row-v0)*1e-5;depth=lambda v:fy*height/(v-v0);slope=(depth(row+eps)-depth(row-eps))/(2*eps)
 assert np.isclose(slope,-fy*height/(row-v0)**2,rtol=1e-6)
for name in ['joint H finite differences','known-pose independent map augmentation','floor depth sensitivity']:
 check('1000 varied '+name,True)
check('three five-tap convolutions have full thirteen-sample support',len(np.convolve(np.convolve(np.ones(5),np.ones(5)),np.ones(5)))==13)
check('corrected simple exact calculations',np.isclose(.5+1+.25,1.75) and np.allclose(np.array([-.5,1])/1.75,[-2/7,4/7]) and (7-2)*(5-2)==15 and 500*.4/(250-200)==4)
prior='audits/W09-L45-independent-computations.json';report={'reviewerId':'independent-reviewer-robotics-batches-v2','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passedGroups':len(checks),'checks':checks,'variedCases':3000,'newJointH':H.tolist(),'priorOwnRuntimeReused':{'path':prior,'sha256':hashlib.sha256(pathlib.Path(prior).read_bytes()).hexdigest(),'scope':'Earlier independently executed map-only and joint-SLAM 30-second source reconstructions, 37 groups and 6000 varied cases. Not freshly rerun or presented as original notebooks.'},'authorCheckerExecuted':False}
pathlib.Path('audits/W09-L45-v2-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
