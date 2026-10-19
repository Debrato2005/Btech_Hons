"""Independent calculations from L25 source pixels and answer-free questions, before key reveal."""
import datetime,json,random
from pathlib import Path
import sympy as s
import numpy as np
R=s.Rational;M=s.Matrix;checks=[]
def ck(name,actual,expected=0):
 delta=actual-expected
 assert (all(s.simplify(x)==0 for x in delta) if isinstance(delta,s.MatrixBase) else s.simplify(delta)==0),(name,delta)
 checks.append(name)
J=M([[1,1],[0,2]]);v=M([R(3,10),R(4,10)])
ck('Q008 desired joint velocity',J.inv()*v,M([R(1,10),R(1,5)]));ck('Q008 transpose distractor',J.T*v,M([R(3,10),R(11,10)]));ck('Q008 forward distractor',J*v,M([R(7,10),R(4,5)]))
ck('Q009 scalar acceleration',(R(6,10)-R(1,2)*R(4,10)/2)/2,R(1,4))
ck('Q009 missing inverse derivative',R(6,10)/2,R(3,10));ck('Q009 wrong derivative sign',R(6,10)/2+R(1,2)*R(4,10)/4,R(7,20));ck('Q009 J instead of inverse on direct acceleration',2*R(6,10)-R(1,2)*R(4,10)/2,R(11,10))
t=s.symbols('t',real=True);jt=M([[1,t],[0,2+t*t]]);a=jt.inv();ad=s.diff(a,t)
ck('Q007 matrix inverse derivative',ad,-a*s.diff(jt,t)*a)
vect=M([t*t,s.sin(t)]);ck('Q006 matrix product differentiation',s.diff(a*vect,t),ad*vect+a*s.diff(vect,t))
e,dt=s.symbols('epsilon dt',nonzero=True);ck('Q010 noise difference',(e-(-e))/dt,2*e/dt)
ck('Q012 Cartesian position error',M([R(4,10),R(2,10),R(5,10)])-M([R(3,10),R(25,100),R(45,100)]),M([R(1,10),-R(5,100),R(5,100)]))
dx=M([R(2,100),R(4,100)]);Kq=s.diag(2,3)
ck('Q016 inverse correction',J.inv()*dx,M([0,R(2,100)]));ck('Q016 torque',Kq*J.inv()*dx,M([0,R(6,100)]));ck('Q016 wrong order',J.inv()*Kq*dx,M([-R(2,100),R(6,100)]));ck('Q016 transpose instead inverse',Kq*J.T*dx,M([R(4,100),R(30,100)]))
J=M([[1,2],[3,4]]);Kx=s.diag(10,20);dx=M([R(1,10),-R(5,100)]);force=Kx*dx
ck('Q021 virtual force',force,M([1,-1]));ck('Q021 transpose torque',J.T*force,M([-2,-2]));ck('Q021 nontransposed alternative',J*force,M([-1,-1]));ck('Q021 inverse alternative',J.inv()*force,M([-3,2]));ck('Q021 reversed gain mapping',Kx*J.T*dx,M([-R(1,2),0]))
ck('Q024 nullspace',s.diag(1,0)*M([0,2]),s.zeros(2,1))
mx=M([[2,1],[1,3]]);acc=M([1,-2]);vv=M([R(1,2),1]);gg=M([1,4])
ck('Q030 inertia force',mx*acc,M([0,-5]));ck('Q030 complete force',mx*acc+vv+gg,M([R(3,2),0]));ck('Q030 diagonal-only alternative',s.diag(2,3)*acc+vv+gg,M([R(7,2),-1]));ck('Q030 subtract-compensation alternative',mx*acc-vv-gg,M([-R(3,2),-10]));ck('Q030 omitted velocity terms',mx*acc+gg,M([1,-1]))
edd=M([R(1,2),-R(1,5)]);ed=M([-R(5,100),R(1,10)]);err=M([R(1,10),-R(1,5)]);kp=s.diag(4,9);kv=s.diag(4,6);u=edd+kv*ed+kp*err
ck('Q033 servo command',u,M([R(7,10),-R(14,10)]));ck('Q033 omit feedforward',kv*ed+kp*err,M([R(2,10),-R(12,10)]));ck('Q033 reverse full feedback',edd-kv*ed-kp*err,M([R(3,10),1]));ck('Q033 reverse derivative only',edd-kv*ed+kp*err,M([R(11,10),-R(26,10)]))
ck('Q035 first critical gain',2*s.sqrt(4),4);ck('Q035 second critical gain',2*s.sqrt(9),6)
ck('Q036 coupled error acceleration',-M([[4,1],[1,9]])*M([0,1]),M([-1,-9]));ck('Q037 inertia mismatch',R(3,2)*4,6)
J=M([[1,2],[0,1]]);F=mx*M([1,-1])+M([1,2]);ck('Q039 force',F,M([2,0]));ck('Q039 torque',J.T*F,M([2,4]));ck('Q039 omitted compensation',J.T*(mx*M([1,-1])),M([1,0]));ck('Q039 diagonal inertia alternative',J.T*(s.diag(2,3)*M([1,-1])+M([1,2])),M([3,5]))
xdacc,ev,ep,kvv,kpp=s.symbols('xdacc ev ep kv kp');ck('Q034 normalized error equation',xdacc-(xdacc+kvv*ev+kpp*ep)+kvv*ev+kpp*ep);ck('Q040 missing feedforward forcing',xdacc-(kvv*ev+kpp*ep)+kvv*ev+kpp*ep,xdacc)
ck('Q043 periods',R(20,1),20)
rng=np.random.default_rng(250119);maxres=0
for _ in range(500):
 j=rng.normal(size=(2,2))+3*np.eye(2);jd=rng.normal(size=(2,2));iv=np.linalg.inv(j);ivd=-iv@jd@iv;xd=rng.normal(size=2);xdd=rng.normal(size=2);qd=iv@xd;qdd=iv@xdd+ivd@xd
 qvel=rng.normal(size=2);f=rng.normal(size=2);err=rng.normal(size=2);ed=rng.normal(size=2);kp=np.diag(rng.uniform(.2,10,2));kv=np.diag(rng.uniform(.2,10,2));z=rng.normal(size=(2,2));mass=z.T@z+np.eye(2);h=rng.normal(size=2);u=xdd+kv@ed+kp@err;plantacc=np.linalg.solve(mass,mass@u+h-h)
 residuals=[np.max(np.abs(j@qdd+jd@qd-xdd)),abs(f@(j@qvel)-(j.T@f)@qvel),np.max(np.abs(xdd-plantacc+kv@ed+kp@err))]
 assert max(residuals)<1e-8,residuals;maxres=max(maxres,max(residuals))
out={'reviewerId':'define_robotics_data_contracts:L25-independent-reviewer','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorKeysSeen':False,'exactAssertions':len(checks),'assertions':checks,'randomTrials':500,'checksPerTrial':3,'randomChecks':['inverse-Jacobian acceleration identity','transpose work-conjugacy','exact normalized Cartesian error dynamics'],'maxResidual':float(maxres),'status':'passed'}
root=Path(__file__).resolve().parents[1];(root/'audits/W05-L25-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
