"""L13 author-side executable checks, not independent review approval."""
import sympy as s,numpy as np,json,hashlib,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1];checks=[]
t1,t2,d1,d2,a1,a2,m1,m2,l1,l2,g=s.symbols('theta1 theta2 q1dot q2dot q1ddot q2ddot m1 m2 l1 l2 g',real=True)
q=s.Matrix([t1,t2]);qd=s.Matrix([d1,d2]);qdd=s.Matrix([a1,a2]);rz=lambda t:s.Matrix([[s.cos(t),-s.sin(t),0],[s.sin(t),s.cos(t),0],[0,0,1]])
def eq(name,a,b):
 d=a-b;assert (all(s.trigsimp(s.expand(v))==0 for v in d) if isinstance(d,s.MatrixBase) else s.trigsimp(s.expand(d))==0),name
 checks.append(name)
# Independent position/energy derivation, not copied Newton–Euler recurrence.
p1=s.Matrix([l1*s.cos(t1),l1*s.sin(t1)]);p2=p1+s.Matrix([l2*s.cos(t1+t2),l2*s.sin(t1+t2)]);v1=p1.jacobian(q)*qd;v2=p2.jacobian(q)*qd
T=s.expand((m1*v1.dot(v1)+m2*v2.dot(v2))/2);U=m1*g*p1[1]+m2*g*p2[1]
lag=s.Matrix([sum(s.diff(s.diff(T,qd[i]),q[j])*qd[j]+s.diff(s.diff(T,qd[i]),qd[j])*qdd[j] for j in range(2))-s.diff(T,q[i])+s.diff(U,q[i]) for i in range(2)])
source=s.Matrix([m2*l2*l2*(a1+a2)+m2*l1*l2*s.cos(t2)*(2*a1+a2)+(m1+m2)*l1*l1*a1-m2*l1*l2*s.sin(t2)*(d2*d2+2*d1*d2)+m2*l2*g*s.cos(t1+t2)+(m1+m2)*l1*g*s.cos(t1),m2*l1*l2*s.cos(t2)*a1+m2*l1*l2*s.sin(t2)*d1*d1+m2*l2*g*s.cos(t1+t2)+m2*l2*l2*(a1+a2)])
eq('both source torques equal position-based Euler–Lagrange derivation',lag,source)
# Newton–Euler vector recurrence, gravity seeded exactly once.
w1=s.Matrix([0,0,d1]);al1=s.Matrix([0,0,a1]);w2=s.Matrix([0,0,d1+d2]);al2=s.Matrix([0,0,a1+a2]);r1=s.Matrix([l1,0,0]);r2=s.Matrix([l2,0,0]);ao1=rz(-t1)*s.Matrix([0,g,0]);ac1=ao1+al1.cross(r1)+w1.cross(w1.cross(r1));ao2=rz(-t2)*ac1;ac2=ao2+al2.cross(r2)+w2.cross(w2.cross(r2));F1=m1*ac1;F2=m2*ac2;f2=F2;n2=r2.cross(F2);f1=rz(t2)*f2+F1;n1=rz(t2)*n2+r1.cross(F1)+r1.cross(rz(t2)*f2);rec=s.Matrix([n1[2],n2[2]])
eq('full vector inward/outward recursion equals source torques',rec,source)
M=s.simplify(source.jacobian(qdd));expected=s.Matrix([[(m1+m2)*l1*l1+m2*l2*l2+2*m2*l1*l2*s.cos(t2),m2*l2*l2+m2*l1*l2*s.cos(t2)],[m2*l2*l2+m2*l1*l2*s.cos(t2),m2*l2*l2]])
eq('mass matrix coefficient extraction',M,expected);eq('mass matrix symmetry',M,M.T);eq('mass determinant',M.det(),m2*l1*l1*l2*l2*(m1+m2*s.sin(t2)**2))
eq('velocity simultaneous reversal invariant',source.subs({d1:-d1,d2:-d2},simultaneous=True),source)
eq('static gravity equals potential gradient',source.subs({d1:0,d2:0,a1:0,a2:0}),s.Matrix([s.diff(U,x) for x in q]))
eq('two-link inertial energy equals mass-matrix quadratic',2*T,(qd.T*M*qd)[0])
eq('first force numeric',F1.subs({l1:s.Rational(1,2),m1:2,t1:0,d1:2,a1:3,g:10}),s.Matrix([-4,23,0]))
vals={l1:1,l2:s.Rational(1,2),t1:0,t2:s.pi/2,d1:2,d2:-1,a1:3,a2:1,g:10,m2:2}
eq('elbow acceleration numeric',ao2.subs(vals),s.Matrix([13,4,0]));eq('second COM acceleration numeric',ac2.subs(vals),s.Matrix([s.Rational(25,2),6,0]));eq('second force numeric',F2.subs(vals),s.Matrix([25,12,0]));eq('second joint moment numeric',n2.subs(vals),s.Matrix([0,0,6]))
eq('zero-spin nonzero translational acceleration',ac2.subs({g:0,l1:1,t2:s.pi/2,d1:2,d2:-2,a1:0,a2:0}),s.Matrix([0,4,0]))
eq('inward force numeric',rz(s.pi/2)*s.Matrix([25,12,0])+s.Matrix([-4,23,0]),s.Matrix([-16,48,0]))
base={l1:1,l2:1,m1:1,m2:1,t1:0,t2:s.pi/2,d1:1,d2:2,a1:3,a2:4,g:10}
eq('full torque example',source.subs(base),s.Matrix([25,8]));eq('straight inertia matrix',M.subs({l1:1,l2:1,m1:1,m2:1,t2:0}),s.Matrix([[5,2],[2,1]]))
eq('horizontal static gravity torques',source.subs({**base,t2:0,d1:0,d2:0,a1:0,a2:0}),s.Matrix([30,10]));eq('vertical static gravity torques',source.subs({**base,t1:s.pi/2,t2:0,d1:0,d2:0,a1:0,a2:0}),s.zeros(2,1))
eq('zero-acceleration velocity coupling',source.subs({**base,g:0,d1:2,d2:0,a1:0,a2:0}),s.Matrix([0,4]))
# Cross method randomized checks over signed rates/accelerations and varied configurations.
args=[t1,t2,d1,d2,a1,a2,m1,m2,l1,l2,g];fun=[s.lambdify(args,x,'numpy') for x in [source,rec,lag]];rng=np.random.default_rng(130404);err=0
for _ in range(300):
 values=[*rng.uniform(-np.pi,np.pi,2),*rng.uniform(-3,3,4),*rng.uniform(.1,4,4),rng.uniform(0,12)]
 x,y,z=[np.array(f(*values),dtype=float) for f in fun];err=max(err,float(np.max(np.abs(x-y))),float(np.max(np.abs(x-z))));assert np.allclose(x,y,rtol=1e-10,atol=1e-10) and np.allclose(x,z,rtol=1e-10,atol=1e-10)
out={'batchId':'W03-L13','authorId':'define_robotics_data_contracts:L13-author','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentReview':False,'method':'Author-side cross-method verification: position/energy Euler–Lagrange, vector Newton–Euler recursion and printed closed-form torques. This is not second-agent answer review.','symbolicAndNumericalAssertions':len(checks),'checks':checks,'randomCases':300,'randomSeed':130404,'maximumAbsoluteCrossMethodDifference':err,'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(R/'audits/W03-L13-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
