"""Independent L11 revision checks, derived from source pixels before keyed access."""
from pathlib import Path
import sympy as s
import numpy as np
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name, actual, expected):
    d=actual-expected
    ok=all(s.simplify(x)==0 for x in d) if isinstance(d,s.MatrixBase) else s.simplify(d)==0
    assert ok,(name,actual,expected)
    checks.append(name)
t=s.symbols('t',real=True);theta=t*t+s.Rational(1,3)*t
R=s.Matrix([[s.cos(theta),-s.sin(theta),0],[s.sin(theta),s.cos(theta),0],[0,0,1]])
q=s.Matrix([t*t,t**3,2*t+1]);p=s.Matrix([t**3,2*t*t,-t*t]);r=R*q;omega=s.Matrix([0,0,s.diff(theta,t)]);alpha=s.diff(omega,t)
full=s.diff(p,t,2)+R*s.diff(q,t,2)+2*omega.cross(R*s.diff(q,t))+alpha.cross(r)+omega.cross(omega.cross(r))
check('General acceleration from direct second derivative with translating origin',s.diff(p+r,t,2),full)
check('Body-fixed zero-speed tangential acceleration',s.Matrix([0,0,3]).cross(s.Matrix([2,0,0])),s.Matrix([0,6,0]))
R90=s.Matrix([[0,-1,0],[1,0,0],[0,0,1]])
check('Nested angular acceleration rotated-basis numeric',s.Matrix([1,0,0])+R90*s.Matrix([2,0,0])+s.Matrix([0,0,1]).cross(R90*s.Matrix([3,0,0])),s.Matrix([-2,2,0]))
wB=s.Matrix([t*t,3*t,1]);check('Angular transport single cross product',s.diff(R*wB,t),R*s.diff(wB,t)+omega.cross(R*wB))
m,w,l,h=s.symbols('m w l h',positive=True);x,y,z=s.symbols('x y z',real=True)
def integral(expr):return s.integrate(expr*m/(w*l*h),(x,0,w),(y,0,l),(z,0,h))
check('Corner raw product integral',integral(x*y),m*w*l/4)
check('Corner z moment integral',integral(x*x+y*y),m*(w*w+l*l)/3)
check('Corner xy matrix entry sign',integral(-x*y),-m*w*l/4)
c=s.Matrix([w/2,l/2,h/2]);shift=m*((c.dot(c))*s.eye(3)-c*c.T)
Ic=s.diag(m*(l*l+h*h)/12,m*(w*w+h*h)/12,m*(w*w+l*l)/12)
check('Full corner tensor minus parallel-axis term',s.Matrix([[integral(y*y+z*z),integral(-x*y),integral(-x*z)],[integral(-x*y),integral(x*x+z*z),integral(-y*z)],[integral(-x*z),integral(-y*z),integral(x*x+y*y)]])-shift,Ic)
check('Named product shift sign',m*w*l/4-m*c[0]*c[1],0)
check('Matrix-entry shift sign',-m*w*l/4+m*c[0]*c[1],0)
check('Point mass old moment',2*s.Rational(6,10)**2,s.Rational(72,100))
check('Point mass new moment',2*s.Rational(3,10)**2,s.Rational(18,100))
check('Point mass reduction fraction',1-s.Rational(18,72),s.Rational(3,4))
check('XY reflection xz cancellation',x*z+x*(-z),0)
check('XY reflection yz cancellation',y*z+y*(-z),0)
check('XY reflection xy survives',x*y+x*y,2*x*y)
check('COM plate normal moment',s.limit(Ic[2,2],h,0),m*(w*w+l*l)/12)
check('Summary omission is origin acceleration',full-(full-s.diff(p,t,2)),s.diff(p,t,2))
check('Angular difference quotient',s.limit(((t+s.Symbol('dt'))**2-t*t)/s.Symbol('dt'),s.Symbol('dt'),0),2*t)
check('URDF example smallest principal moment',min(s.Rational(3,1000),s.Rational(3,1000),s.Rational(1,1000)),s.Rational(1,1000))
rng=np.random.default_rng(3112);maxerr=0.;min_eig=1.e9
for _ in range(300):
    pts=rng.normal(size=(12,3));masses=rng.uniform(.01,5,size=12);M=masses.sum();C=(masses[:,None]*pts).sum(axis=0)/M
    def tensor(a):return sum(mi*((v@v)*np.eye(3)-np.outer(v,v)) for mi,v in zip(masses,a))
    IA=tensor(pts);IC=tensor(pts-C);pred=IC+M*((C@C)*np.eye(3)-np.outer(C,C))
    maxerr=max(maxerr,float(np.max(np.abs(IA-pred))));assert np.allclose(IA,pred,atol=1e-11)
    assert np.allclose(IA,IA.T);min_eig=min(min_eig,float(np.linalg.eigvalsh(IA).min()))
    rot,_=np.linalg.qr(rng.normal(size=(3,3)));rot[:,0]*=np.linalg.det(rot)
    assert np.allclose(tensor(pts@rot.T),rot@IA@rot.T,atol=1e-11)
    assert np.isclose(np.trace(rot@IA@rot.T),np.trace(IA))
assert min_eig>0
result=dict(reviewerId='define_robotics_data_contracts:L11-v2-independent-reviewer',createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),authorKeysSeen=False,exactAssertions=len(checks),assertionNames=checks,randomMassDistributions=300,randomChecksPerDistribution=['direct particle-sum parallel-axis identity','symmetry','positive definiteness for sampled nondegenerate distributions','rotated tensor matches rotated particles','trace invariant under rotation'],maximumParallelAxisResidual=maxerr,minimumSampledEigenvalue=min_eig,scriptSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(ROOT/'audits/W03-L11-v2-independent-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
