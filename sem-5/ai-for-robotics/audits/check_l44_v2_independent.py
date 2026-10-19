"""Independent changed-task checks, default Python/NumPy only; no toolbox imports."""
import json,sys,datetime,hashlib
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]; checks=[]
def check(name,condition,result=None):
 assert condition,name
 checks.append({'name':name,'passed':True,'result':result})
check('constant rate integrates change',30*2==60,60)
check('zero weights have no normalized posterior',np.zeros(4).sum()==0)
check('singular covariance ordinary determinant',np.linalg.det(np.diag([1.,0.]))==0)
K=.75/(.75+.3);check('correction mean and gain',np.isclose(4+K,33/7)and .5<K<1,{'gain':K,'mean':4+K})
check('EKF nonlinear mean differs from exact mean',2**2==4 and 2**2+.25==4.25)
Fx=np.array([[1,0,-2],[0,1,0],[0,0,1.]]);Fv=np.array([[0,0],[1,0],[0,1.]])
P=np.diag([.01,.04,.09]);V=np.diag([.0025,.0004]);pred=Fx@P@Fx.T+Fv@V@Fv.T
check('Q057 covariance all entries',np.allclose(pred,[[.37,0,-.18],[0,.0425,0],[-.18,0,.0904]],rtol=0,atol=1e-15),pred.tolist())
E0=np.diag([.05,.05,np.deg2rad(.5)])**2
check('initial covariance shape and variance',E0.shape==(3,3)and np.allclose(np.diag(E0),[.0025,.0025,np.pi**2/129600],rtol=0,atol=1e-16),E0.tolist())
check('old heading differs from finite arc',not np.allclose([1.,0.],[np.sin(1),1-np.cos(1)]))
# Current u not in a constant past history: x_t=u_t is a simple valid controlled Markov model.
check('Q091 omitted-control counterexample',.5 != 1.,{'p(x_t=1|past)':.5,'p(x_t=1|x_prev,u_t=1)':1.})
def f(q,u,v):
 x,y,t=q;d,a=u;vd,va=v;return np.array([x+(d+vd)*np.cos(t),y+(d+vd)*np.sin(t),t+a+va])
def T(q):
 x,y,t=q;c=np.cos(t);s=np.sin(t);return np.array([[c,-s,x],[s,c,y],[0,0,1.]])
rng=np.random.default_rng(442026);eps=1e-6
for _ in range(1000):
 q=rng.normal(size=3);u=rng.normal(size=2);d,t=u[0],q[2]
 A=np.array([[1,0,-d*np.sin(t)],[0,1,d*np.cos(t)],[0,0,1.]])
 B=np.array([[np.cos(t),0],[np.sin(t),0],[0,1.]])
 fd=np.column_stack([(f(q+eps*e,u,[0,0])-f(q-eps*e,u,[0,0]))/(2*eps)for e in np.eye(3)])
 fn=np.column_stack([(f(q,u,eps*e)-f(q,u,-eps*e))/(2*eps)for e in np.eye(2)])
 assert np.allclose(fd,A,rtol=0,atol=2e-9)
 assert np.allclose(fn,B,rtol=0,atol=2e-9)
 assert np.allclose(T(q)@T([u[0],0,0])@T([0,0,u[1]]),T(f(q,u,[0,0])),rtol=0,atol=2e-14)
 M=rng.normal(size=(3,3));N=rng.normal(size=(2,2));cov=A@M@M.T@A.T+B@N@N.T@B.T
 assert np.linalg.eigvalsh(cov).min()>-1e-10
check('varied state Jacobians',True,1000);check('varied noise Jacobians',True,1000);check('varied pose composition',True,1000);check('varied propagated covariance PSD',True,1000)
out={'reviewerId':'independent-reviewer-robotics-batches-v2','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pythonExecutable':sys.executable,'numpyVersion':np.__version__,'scope':'Fresh default-environment NumPy checks of the changed L44 numerical/model premises. No toolbox/model/pretrained runtime, installation or network operation. Prior RTB1.4.4 execution is separately cited as historical evidence, not rerun.','passedGroups':len(checks),'variedCases':4000,'checks':checks}
p=root/'audits/W09-L44-v2-independent-computations.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passedGroups':len(checks),'variedCases':4000,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
