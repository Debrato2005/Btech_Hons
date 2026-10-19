"""Independent targeted L23 repair/gap checks before current key access."""
from pathlib import Path
import json,datetime,math
import sympy as s
import numpy as np
M=s.Matrix;R=s.Rational;checks=[]
def ck(name,a,b=0):
 delta=a-b;assert (all(s.simplify(z)==0 for z in delta) if isinstance(delta,s.MatrixBase) else s.simplify(delta)==0),(name,delta);checks.append(name)
t,e0=s.symbols('t e0',real=True);err=e0*(1+4*t)*s.exp(-4*t);speed=16*e0*t*s.exp(-4*t)
ck('Q048 ODE',s.diff(err,t,2)+8*s.diff(err,t)+16*err);ck('Q048 displacement IC',err.subs(t,0),e0);ck('Q048 velocity IC',s.diff(err,t).subs(t,0));ck('Q049 speed derivative',s.diff(speed,t),16*e0*s.exp(-4*t)*(1-4*t));ck('Q049 stationary time',s.diff(speed,t).subs(t,R(1,4)));ck('Q049 peak speed',speed.subs(t,R(1,4)),4*e0/s.E)
peak=float((4*(110*s.pi/180)/s.E).evalf());assert abs(peak-2.825)<.0005;checks.append('Q049 rounded numeric peak')
x,q=s.symbols('x q');ck('Q013 tangent stiffness',s.diff(q*x**3,x),3*q*x*x)
th=s.symbols('theta');position=M([s.cos(th),s.sin(th)]);ck('Q054 tangent velocity',s.diff(position,th).subs(th,s.pi/2)*2,M([-2,0]));ck('Q054 radial dot velocity',position.subs(th,s.pi/2).dot(M([-2,0])),0)
mat=M([[2,1],[1,3]]);beta=M([R(1,2),1]);ck('Q059 correct torque',mat*M([1,-2])+beta,M([R(1,2),-4]));ck('Q059 changed sign alternative',mat*M([1,2])+beta,M([R(9,2),8]));ck('Q059 diagonal-only alternative',s.diag(2,3)*M([1,-2])+beta,M([R(5,2),-5]));ck('Q059 compensation-sign alternative',mat*M([1,-2])-beta,M([-R(1,2),-6]))
ref=M([1+t+t*t,-1+2*t-R(1,2)*t*t]);pos=M([R(1,2),-R(1,2)]);vel=M([R(1,2),R(3,2)]);ep=ref.subs(t,0)-pos;ev=s.diff(ref,t).subs(t,0)-vel;acc=s.diff(ref,t,2).subs(t,0);kp=s.diag(4,9);kv=s.diag(4,6);u=acc+kv*ev+kp*ep
ck('Q064 position error',ep,M([R(1,2),-R(1,2)]));ck('Q064 velocity error',ev,M([R(1,2),R(1,2)]));ck('Q064 desired acceleration',acc,M([2,-1]));ck('Q064 normalized command',u,M([6,-R(5,2)]));ck('Q064 physical command',mat*u+beta,M([10,-R(1,2)]));ck('Q064 omit feedforward alternative',mat*(kv*ev+kp*ep)+beta,M([7,R(1,2)]));ck('Q064 diagonal inertia alternative',s.diag(2,3)*u+beta,M([R(25,2),-R(13,2)]));ck('Q064 reverse both errors alternative',mat*(acc-kv*ev-kp*ep)+beta,M([-3,R(1,2)]))
rng=np.random.default_rng(230225);maxres=0
for _ in range(500):
 z=rng.normal(size=(3,3));mass=z.T@z+np.eye(3);beta=rng.normal(size=3);acc=rng.normal(size=3);ep=rng.normal(size=3);ev=rng.normal(size=3);kp=np.diag(rng.uniform(.2,10,3));kv=np.diag(rng.uniform(.2,10,3));u=acc+kv@ev+kp@ep;torque=mass@u+beta;actual=np.linalg.solve(mass,torque-beta);res=np.max(np.abs(acc-actual+kv@ev+kp@ep));assert res<1e-10;maxres=max(maxres,res)
out={'reviewerId':'define_robotics_data_contracts:L23-independent-reviewer','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'currentAuthorKeysSeen':False,'priorV1Exposure':True,'exactAssertions':len(checks),'assertions':checks,'peakSpeedRadPerSecond':peak,'randomCoupledTrials':500,'maxResidual':float(maxres),'status':'passed'}
r=Path(__file__).resolve().parents[1];(r/'audits/W05-L23-v2-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
