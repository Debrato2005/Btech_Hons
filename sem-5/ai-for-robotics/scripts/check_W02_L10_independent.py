"""Independent source-derived L10 algebra, written before author-answer access."""
import json,hashlib,datetime
from pathlib import Path
import sympy as s
R=Path(__file__).resolve().parents[1]; checks=[]
def eq(name,a,b):
 d=a-b
 assert (all(s.simplify(v)==0 for v in d) if isinstance(d,s.MatrixBase) else s.simplify(d)==0), name
 checks.append(name)
t1,t2,a,L1,L2,q1,q2,fx,fy=s.symbols('theta1 theta2 alpha L1 L2 q1dot q2dot fx fy',real=True)
rz=lambda t:s.Matrix([[s.cos(t),-s.sin(t),0],[s.sin(t),s.cos(t),0],[0,0,1]])
rx=s.Matrix([[1,0,0],[0,s.cos(a),-s.sin(a)],[0,s.sin(a),s.cos(a)]])
eq('modified-DH row3col2',(rx*rz(t1))[2,1],s.sin(a)*s.cos(t1))
w=s.Matrix([0,0,q1]);p=s.Matrix([L1,0,0]);v2=rz(-t2)*w.cross(p)
eq('elbow velocity rotation',v2,s.Matrix([L1*s.sin(t2)*q1,L1*s.cos(t2)*q1,0]))
v3=v2+s.Matrix([0,0,q1+q2]).cross(s.Matrix([L2,0,0]));J3=v3[:2,0].jacobian([q1,q2]);J0=rz(t1+t2)[:2,:2]*J3
position=s.Matrix([L1*s.cos(t1)+L2*s.cos(t1+t2),L1*s.sin(t1)+L2*s.sin(t1+t2)])
eq('base Jacobian from independent position differentiation',J0,position.jacobian([t1,t2]))
eq('body determinant',J3.det(),L1*L2*s.sin(t2));eq('base determinant',J0.det(),L1*L2*s.sin(t2))
eq('Q006',v2.subs({L1:2,t2:s.pi/6,q1:1}),s.Matrix([1,s.sqrt(3),0]))
eq('Q009',v3.subs({L1:2,L2:1,t2:s.pi/2,q1:1,q2:-s.Rational(1,2)}),s.Matrix([2,s.Rational(1,2),0]))
eq('Q011',rz(s.pi/2)*s.Matrix([2,s.Rational(1,2),0]),s.Matrix([-s.Rational(1,2),2,0]))
eq('Q020',J3.subs({L1:1,L2:1,t2:s.pi}),s.Matrix([[0,0],[0,1]]))
eq('Q021',J0.subs({L1:1,L2:1,t1:0,t2:s.pi/2})*s.Matrix([0,-1]),s.Matrix([1,0]))
qinv=s.Matrix([s.cos(t1+t2)/(L1*s.sin(t2)),-s.cos(t1)/(L2*s.sin(t2))-s.cos(t1+t2)/(L1*s.sin(t2))])
eq('inverse command identity',J0*qinv,s.Matrix([1,0]))
assert s.limit(qinv[0].subs({L1:1,L2:1,t1:-t2/2}),t2,0,dir='+')==s.oo;checks.append('Q022 positive unbounded q1')
assert s.limit(qinv[1].subs({L1:1,L2:1,t1:-t2/2}),t2,0,dir='+')==-s.oo;checks.append('Q022 negative unbounded q2')
eq('Q023 finite exception',qinv.subs(t1,s.pi/2),s.Matrix([-1/L1,1/L1]))
eq('Q029',s.Matrix([s.Rational(2,5),0,0]).cross(s.Matrix([0,5,0]))+s.Matrix([0,0,1]),s.Matrix([0,0,3]))
eq('Q036',rz(s.pi/2)*s.Matrix([3,4,0]),s.Matrix([-4,3,0]))
tau=J3.T*s.Matrix([fx,fy]);eq('Q037',tau.subs({L1:2,L2:1,t2:s.pi/2,fx:3,fy:4}),s.Matrix([10,4]))
eq('Q040 axial null effort',tau.subs({t2:0,fy:0}),s.zeros(2,1))
J=s.Matrix([[1,0,1],[0,2,1]]);F=s.Matrix([3,4]);qd=s.Matrix([s.Rational(1,5),-s.Rational(1,10),s.Rational(3,10)])
eq('Q046',J.T*F,s.Matrix([3,8,7]));eq('Q047 Cartesian power',F.dot(J*qd),s.Rational(19,10));eq('Q047 joint power',(J.T*F).dot(qd),s.Rational(19,10))
eq('Q052',rz(-s.pi/2)*(s.Matrix([1,0,0])+s.Matrix([0,0,2]).cross(s.Matrix([1,0,0]))),s.Matrix([2,-1,0]))
eq('Q054',rz(s.pi/2)*s.Matrix([0,0,3])+s.Matrix([1,0,0]).cross(rz(s.pi/2)*s.Matrix([2,0,0])),s.Matrix([0,0,5]))
px,py,pz=s.symbols('px py pz',real=True);P=s.Matrix([[0,-pz,py],[pz,0,-px],[-py,px,0]]);Rot=rz(t1);X=Rot.row_join(-Rot*P).col_join(s.zeros(3).row_join(Rot));expected=Rot.T.row_join(s.zeros(3)).col_join((P*Rot.T).row_join(Rot.T));eq('Q055 full symbolic dual map',X.T,expected)
out={'reviewerId':'define_robotics_data_contracts:L10-independent-reviewer','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'Actual lecture pages329–348; calculations authored independently before keyed access','assertions':len(checks),'checks':checks,'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(R/'audits/W02-L10-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
