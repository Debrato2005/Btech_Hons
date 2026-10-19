"""Independent symbolic and exact numeric checks, derived without author solutions."""
import json,datetime
from pathlib import Path
import sympy as s
ROOT=Path(__file__).resolve().parents[1];checks=[]
def eq(name,actual,expected):
 delta=actual-expected
 good=all(s.simplify(v)==0 for v in delta) if isinstance(delta,s.MatrixBase) else s.simplify(delta)==0
 assert good,(name,actual,expected)
 checks.append({'name':name,'actual':str(actual),'expected':str(expected),'passed':True})
def rx(a):return s.Matrix([[1,0,0,0],[0,s.cos(a),-s.sin(a),0],[0,s.sin(a),s.cos(a),0],[0,0,0,1]])
def rz(t):return s.Matrix([[s.cos(t),-s.sin(t),0,0],[s.sin(t),s.cos(t),0,0],[0,0,1,0],[0,0,0,1]])
def trans(x,y,z):m=s.eye(4);m[:3,3]=s.Matrix([x,y,z]);return m
a,d,alpha,theta=s.symbols('a d alpha theta',real=True)
T=rx(alpha)*trans(a,0,0)*rz(theta)*trans(0,0,d)
eq('Q024 modified-DH translation',T[:3,3],s.Matrix([a,-d*s.sin(alpha),d*s.cos(alpha)]))
eq('Q025 corrected row3 column2',T[2,1],s.sin(alpha)*s.cos(theta))
eq('Q026 right-angle translation',T[:3,3].subs({alpha:s.pi/2,a:2,theta:0,d:3}),s.Matrix([2,-3,0]))
eq('modified-DH rotation orthonormal',T[:3,:3].T*T[:3,:3],s.eye(3))
eq('modified-DH rotation determinant',T[:3,:3].det(),1)
t1,t2,t3,L1,L2,d2=s.symbols('theta1 theta2 theta3 L1 L2 d2',real=True)
planar=rz(t1)*trans(L1,0,0)*rz(t2)*trans(L2,0,0)*rz(t3)
eq('Q033 planar translation',planar[:3,3],s.Matrix([L1*s.cos(t1)+L2*s.cos(t1+t2),L1*s.sin(t1)+L2*s.sin(t1+t2),0]))
eq('Q033 planar rotation',planar[:3,:3],rz(t1+t2+t3)[:3,:3])
eq('Q034 third-joint origin-position derivative',planar[:3,3].diff(t3),s.zeros(3,1))
sub={L1:2,L2:1,t1:s.pi/2,t2:-s.pi/2,t3:s.pi/6}
eq('Q035 frame3 origin',planar[:3,3].subs(sub),s.Matrix([1,2,0]))
eq('Q035 orientation', (t1+t2+t3).subs(sub),s.pi/6)
eq('Q036 rotated tool offset',s.Matrix([3,0,0])+rz(s.pi/2)[:3,:3]*s.Matrix([1,0,0]),s.Matrix([3,1,0]))
rpr=rz(t1)*rx(s.pi/2)*trans(0,0,d2)*rz(t3)*trans(0,0,L2)
eq('Q039 RPR position',rpr[:3,3],s.Matrix([(L2+d2)*s.sin(t1),-(L2+d2)*s.cos(t1),0]))
eq('Q040 corrected RPR entry',rpr[1,2],-s.cos(t1))
eq('RPR rotation orthonormal',rpr[:3,:3].T*rpr[:3,:3],s.eye(3))
eq('RPR rotation determinant',rpr[:3,:3].det(),1)
err=s.Matrix([s.sin(t1),-s.cos(t3),0]).subs({t1:0,t3:s.pi/2})
eq('Q041 erroneous column',err,s.zeros(3,1));eq('Q041 erroneous norm squared',err.dot(err),0)
eq('Q042 RPR numeric origin',rpr[:3,3].subs({t1:s.pi/2,d2:s.Rational(2,5),L2:s.Rational(3,5)}),s.Matrix([1,0,0]))
r,w,ul,ur,phi=s.symbols('r d u_l u_r phi',real=True,nonzero=True)
v=r*(ur+ul)/2;omega=r*(ur-ul)/(2*w)
eq('Q045 equal-speed yaw',omega.subs(ur,ul),0)
eq('Q047 opposite-speed yaw',omega.subs(ul,-ur),r*ur/w)
sub={r:s.Rational(1,10),w:s.Rational(1,4),ul:2,ur:4}
eq('Q051 forward speed',v.subs(sub),s.Rational(3,10));eq('Q051 yaw',omega.subs(sub),s.Rational(2,5))
eq('Q052 ordered pose rates',s.Matrix([v*s.cos(phi),v*s.sin(phi),omega]).subs(sub).subs(phi,s.pi/2),s.Matrix([0,s.Rational(3,10),s.Rational(2,5)]))
M=s.Matrix([-r/(2*w),r*s.cos(phi)/2,r*s.sin(phi)/2]).row_join(s.Matrix([r/(2*w),r*s.cos(phi)/2,r*s.sin(phi)/2]))
eq('Q053/054 ordered matrix product',M*s.Matrix([ul,ur]),s.Matrix([omega,v*s.cos(phi),v*s.sin(phi)]))
eq('Q055 doubled track yaw',omega.subs(w,2*w),omega/2)
eq('Q056 doubled radius forward',v.subs(r,2*r),2*v);eq('Q056 doubled radius yaw',omega.subs(r,2*r),2*omega)
V,O=s.symbols('V Omega',real=True);uil=(V-w*O)/r;uir=(V+w*O)/r
eq('Q057 inverse commands forward',v.subs({ul:uil,ur:uir}),V);eq('Q057 inverse commands yaw',omega.subs({ul:uil,ur:uir}),O)
sub={V:s.Rational(1,2),O:1,w:s.Rational(1,5),r:s.Rational(1,10)}
eq('Q058 left command',uil.subs(sub),3);eq('Q058 right command',uir.subs(sub),7)
sub={r:s.Rational(1,10),w:s.Rational(1,4),ul:-3,ur:3}
eq('Q059 in-place forward',v.subs(sub),0);eq('Q059 yaw sign and magnitude',omega.subs(sub),s.Rational(6,5))
eq('Q060 lateral constraint',-(v*s.cos(phi))*s.sin(phi)+(v*s.sin(phi))*s.cos(phi),0)
x={'schemaVersion':'1.0.0','batchId':'W02-L07','reviewerId':'define_robotics_data_contracts:L07-independent-reviewer','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent SymPy matrix products, symbolic identities, exact rational and right-angle substitutions derived from actual source factors/equations and frozen blind questions before reading author solutions. Not physical-robot validation or a complete-coverage certificate.','checks':checks}
(ROOT/'audits/independent-checks-W02-L07.json').write_text(json.dumps(x,indent=2)+'\n');print(len(checks),'independent checks passed')
