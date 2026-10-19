"""Independent L15 equations from point-mass Cartesian kinematics, not author code."""
import sympy as s
import numpy as np
from pathlib import Path
import json,datetime,hashlib
ROOT=Path(__file__).resolve().parents[1]
q1,q2,w1,w2,a1,a2=s.symbols('q1 q2 w1 w2 a1 a2',real=True)
m1,m2,l1,l2,g=s.symbols('m1 m2 l1 l2 g',positive=True)
q=s.Matrix([q1,q2]);w=s.Matrix([w1,w2]);a=s.Matrix([a1,a2]);checks=[]
def ck(name,actual,expected):
 d=actual-expected
 ok=all(s.trigsimp(s.expand_trig(x))==0 for x in d) if isinstance(d,s.MatrixBase) else s.trigsimp(s.expand_trig(d))==0
 assert ok,(name,actual,expected);checks.append(name)
p1=s.Matrix([l1*s.cos(q1),l1*s.sin(q1)]);p2=p1+s.Matrix([l2*s.cos(q1+q2),l2*s.sin(q1+q2)])
J1=p1.jacobian(q);J0=p2.jacobian(q)
K=(m1*(J1*w).dot(J1*w)+m2*(J0*w).dot(J0*w))/2;U=g*(m1*p1[1]+m2*p2[1]);Md=s.simplify(s.hessian(K,w));Gd=s.simplify(U.diff(q));Vd=s.simplify((K.diff(w)).jacobian(q)*w-K.diff(q))
h=m2*l1*l2*s.sin(q2)
M=s.Matrix([[m2*l2*l2+2*m2*l1*l2*s.cos(q2)+(m1+m2)*l1*l1,m2*l2*l2+m2*l1*l2*s.cos(q2)],[m2*l2*l2+m2*l1*l2*s.cos(q2),m2*l2*l2]])
V=s.Matrix([-h*(w2*w2+2*w1*w2),h*w1*w1]);G=s.Matrix([m2*l2*g*s.cos(q1+q2)+(m1+m2)*l1*g*s.cos(q1),m2*l2*g*s.cos(q1+q2)])
ck('M from Cartesian point-mass kinetic-energy Hessian',Md,M)
ck('V from independent Euler-Lagrange kinetic derivatives',Vd,V)
ck('G from Cartesian gravitational-potential gradient',Gd,G)
ck('Mass determinant',M.det(),l1*l1*l2*l2*m2*(m1+m2*s.sin(q2)**2))
ck('Straight-arm mass determinant remains positive under assumptions',M.det().subs(q2,0),l1*l1*l2*l2*m1*m2)
R=s.Matrix([[s.cos(q1+q2),-s.sin(q1+q2)],[s.sin(q1+q2),s.cos(q1+q2)]])
J=s.Matrix([[l1*s.sin(q2),0],[l1*s.cos(q2)+l2,l2]])
ck('Tool Jacobian from rotated base point-position derivative',R.T*J0,J)
Jdot=J.diff(q2)*w2;ck('Printed moving-component J derivative',Jdot,s.Matrix([[l1*s.cos(q2)*w2,0],[-l1*s.sin(q2)*w2,0]]))
ck('Task determinant',J.det(),l1*l2*s.sin(q2))
JI=J.inv();ck('Printed inverse',JI,s.Matrix([[l2,0],[-l1*s.cos(q2)-l2,l1*s.sin(q2)]])/(l1*l2*s.sin(q2)))
MX=s.diag(m2+m1/s.sin(q2)**2,m2);ck('Task inertia from independent M and rotated J',JI.T*M*JI,MX)
VX=s.Matrix([-(m2*l1*s.cos(q2)+m2*l2)*w1*w1-m2*l2*w2*w2-(2*m2*l2+m2*l1*s.cos(q2)+m1*l1*s.cos(q2)/s.sin(q2)**2)*w1*w2,m2*l1*s.sin(q2)*(w1*w1+w1*w2)])
ck('Expanded Vx with moving-component derivative',JI.T*(V-M*JI*Jdot*w),VX)
GX=s.Matrix([m1*g*s.cos(q1)/s.sin(q2)+m2*g*s.sin(q1+q2),m2*g*s.cos(q1+q2)])
ck('Expanded Gx from source joint potential',JI.T*G,GX)
ck('Torque gravity identity, not Gx=G',J.T*GX,G)
B=s.Matrix([-2*h,0]);C=s.Matrix([[0,-h],[h,0]]);ck('Separated-rate reconstruction',B*w1*w2+C*s.Matrix([w1*w1,w2*w2]),V)
baseacc=J0*a+sum((J0.diff(qi)*wi for qi,wi in zip(q,w)),s.zeros(2))*w
S=s.Matrix([[0,-1],[1,0]])
ck('Inertial acceleration versus rotating component derivative',R.T*baseacc,J*a+Jdot*w+(w1+w2)*S*J*w)
sub={m1:2,m2:3,l1:1,l2:2,q1:0,q2:s.pi/2,w1:1,w2:2,g:10}
ck('Q006 numerical inertia',M.subs(sub),s.Matrix([[17,12],[12,12]]))
ck('Q010 numerical V',V.subs(sub),s.Matrix([-48,6]))
ck('Q012 numerical G',G.subs(sub),s.Matrix([50,0]))
ck('Q022 inverse acceleration command',s.diag(s.Rational(1,2),1)*(s.Matrix([5,4])-s.Matrix([1,-2])),s.Matrix([2,6]))
ck('Q028 inverse',JI.subs(sub),s.Matrix([[1,0],[-1,s.Rational(1,2)]]))
ck('Q029 Jdot',Jdot.subs(sub),s.Matrix([[0,0],[-2,0]]))
ck('Q031 task inertia at30deg',MX.subs({m1:2,m2:3,q2:s.pi/6}),s.diag(11,3))
ck('Q032 task velocity effort',VX.subs(sub),s.Matrix([-54,9]))
ck('Q033 task gravity',GX.subs(sub),s.Matrix([50,0]))
ck('Q038 compensation',2*s.sign(-4)+s.Rational(1,2)*(-4),-4)
ck('Q044 forward acceleration',s.Matrix([[2,1],[1,2]]).inv()*(s.Matrix([8,7])-s.Matrix([1,0])-s.Matrix([2,3])-s.Matrix([1,0])),s.Matrix([s.Rational(4,3),s.Rational(4,3)]))
ck('Q048 displayed velocity update',2-4*s.Rational(1,10),s.Rational(8,5))
ck('Q048 displayed position update',1+2*s.Rational(1,10)-2*s.Rational(1,10)**2,s.Rational(59,50))
ck('Four-joint mixed-rate count',s.Integer(4)*3/2,s.Integer(6))
params=[m1,m2,l1,l2,g,q1,q2,w1,w2,a1,a2]
f=s.lambdify(params,[M,V,G,J,Jdot,MX,VX,GX,J1,J0],modules='numpy');rng=np.random.default_rng(31515);maxeff=0.;maxpower=0.;maxenergy=0.
for _ in range(400):
 masses=rng.uniform(.2,6,2);lengths=rng.uniform(.3,2.5,2);angles=[rng.uniform(-3,3),rng.uniform(.2,2.9)];rates=rng.uniform(-3,3,2);acc=rng.uniform(-4,4,2)
 vals=[*masses,*lengths,9.81,*angles,*rates,*acc];mm,vv,gg,j,jd,mx,vx,gx,j1,j0=f(*vals);ww=np.array(rates);aa=np.array(acc)
 vv=vv.ravel();gg=gg.ravel();vx=vx.ravel();gx=gx.ravel();component_acc=j@aa+jd@ww
 tau=mm@aa+vv+gg;eff=mx@component_acc+vx+gx
 residual=np.max(np.abs(j.T@eff-tau));maxeff=max(maxeff,float(residual));assert np.allclose(j.T@eff,tau,atol=1e-9)
 power=float(tau@ww-eff@(j@ww));maxpower=max(maxpower,abs(power));assert abs(power)<1e-8
 kin=.5*masses[0]*np.dot(j1@ww,j1@ww)+.5*masses[1]*np.dot(j0@ww,j0@ww)
 e=float(.5*ww@mm@ww-kin);maxenergy=max(maxenergy,abs(e));assert abs(e)<1e-9
 assert np.linalg.eigvalsh(mm).min()>0 and np.linalg.eigvalsh(mx).min()>0
 c,nu=rng.uniform(0,3,2);vel=rng.uniform(-4,4);assert np.isclose(-(-c*np.sign(vel)-nu*vel)*vel,c*abs(vel)+nu*vel*vel)
result=dict(reviewerId='define_robotics_data_contracts:L15-independent-reviewer',createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),authorKeysSeen=False,exactAssertions=len(checks),assertionNames=checks,randomCases=400,randomProperties=['joint/task effort equivalence','joint/task power','point-velocity kinetic energy','positive inertia eigenvalues','friction dissipation sign'],maximumEffortResidual=maxeff,maximumPowerResidual=maxpower,maximumEnergyResidual=maxenergy,scriptSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(ROOT/'audits/W03-L15-independent-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
