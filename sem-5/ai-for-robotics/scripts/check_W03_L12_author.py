"""Author checks, not independent answer approval."""
from pathlib import Path
import json, sympy as s, hashlib,datetime
R=Path(__file__).resolve().parents[1];M=s.Matrix;I=s.eye(3);checks=[]
def ck(name,a,e):
 assert s.simplify(a-e)==s.zeros(*a.shape) if isinstance(a,s.MatrixBase) else s.simplify(a-e)==0,name
 checks.append(name)
ck('Newton force',3*M([2,-1,0]),M([6,-3,0]))
w=M([1,2,3]);alpha=M([s.Rational(1,2),-1,2]);Ic=s.diag(2,3,4)
ck('Euler gyroscopic cross',w.cross(Ic*w),M([6,-6,2]));ck('Full Euler moment',Ic*alpha+w.cross(Ic*w),M([7,-9,10]))
ck('Revolute angular velocity',M([1,0,2])+3*M([0,0,1]),M([1,0,5]))
ck('Angular transport',M([1,0,0]).cross(M([0,0,2]))+M([0,0,3]),M([0,-2,3]))
r=M([s.Rational(1,2),0,0]);w=M([0,0,2]);alpha=M([0,0,3])
ck('COM acceleration',M([1,0,0])+alpha.cross(r)+w.cross(w.cross(r)),M([-1,s.Rational(3,2),0]))
ck('Prismatic Coriolis',2*M([1,0,0]).cross(M([0,0,2]))+M([0,0,3]),M([0,-4,3]))
F=M([0,2,0]);fn=M([0,3,0]);N=M([0,0,1]);nn=M([0,0,2]);p=M([1,0,0])
ck('Inward force',F+fn,M([0,5,0]));ck('Inward moment',N+nn+r.cross(F)+p.cross(fn),M([0,0,7]))
Rot=M([[0,-1,0],[1,0,0],[0,0,1]]);fn=M([2,0,0]);nn=M([0,0,3]);F=M([0,1,0])
ck('Rotated inward moment',N+Rot*nn+r.cross(F)+p.cross(Rot*fn),M([0,0,s.Rational(13,2)]))
ck('Revolute projection',M([3,4,-2]).dot(M([0,0,1])),s.Integer(-2));ck('Prismatic projection',M([5,-1,6]).dot(M([0,0,1])),s.Integer(6))
g=s.Rational(981,100);ck('Gravity force moment',r.cross(2*M([0,g,0])),M([0,0,g]))
ck('Scalar impedance',2+s.Rational(1,2)*(100*s.Rational(2,100)+10*s.Rational(-1,10)),s.Rational(5,2))
# Exact symbolic cancellation of the mass-center moment balance.
r=M(s.symbols('rx ry rz'));p=M(s.symbols('px py pz'));F=M(s.symbols('Fx Fy Fz'));f=M(s.symbols('fx fy fz'))
ck('Moment-arm cancellation',-r.cross(F+f)-(p-r).cross(f),-r.cross(F)-p.cross(f))
# Euler principal-axis/spherical cases.
wx,wy,wz,lam=s.symbols('wx wy wz lam');w=M([wx,wy,wz]);ck('Spherical inertia gyro zero',w.cross(lam*w),s.zeros(3,1));ck('Principal-axis gyro zero',M([0,0,wz]).cross(s.diag(2,3,4)*M([0,0,wz])),s.zeros(3,1))
b=json.loads((R/'data/question-batches/W03-L12.json').read_text());cited={c['physicalPage'] for q in b['questions'] for c in q['citations']};assert set(range(382,402))<=cited
assert all(q['solution']['steps'] and q['solution']['formulas'] for q in b['questions'] if q['type']=='numerical')
x={'scope':'Author checks only; independent review pending','passed':len(checks),'checks':checks,'allTwentySubstantivePagesCited':True,'allNumericalItemsHaveStepsAndFormulaMetadata':True,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(R/'audits/W03-L12-author-checks.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x))
