"""Author checks only; independent verification remains required."""
from pathlib import Path
import json,hashlib,datetime
import sympy as s
import numpy as np
r=Path(__file__).resolve().parents[1];checks=[]
def ok(name,cond):
 assert cond,name
 checks.append(name)
m1,m2,l1,l2,t,u,v=s.symbols('m1 m2 l1 l2 t u v',real=True);c=s.cos(t);z=s.sin(t)
M=s.Matrix([[m2*l2**2+2*m2*l1*l2*c+(m1+m2)*l1**2,m2*l2**2+m2*l1*l2*c],[m2*l2**2+m2*l1*l2*c,m2*l2**2]])
J=s.Matrix([[l1*z,0],[l1*c+l2,l2]]);V=s.Matrix([-m2*l1*l2*z*(v*v+2*u*v),m2*l1*l2*z*u*u]);Ji=J.inv();Jd=J.diff(t)*v
Mx=s.simplify(Ji.T*M*Ji);Vx=s.simplify(Ji.T*(V-M*Ji*Jd*s.Matrix([u,v])))
ok('Mass determinant',s.simplify(M.det()-l1**2*l2**2*m2*(m1+m2*z**2))==0)
ok('Jacobian determinant',s.simplify(J.det()-l1*l2*z)==0)
ok('Cartesian diagonal inertia',s.simplify(Mx-s.diag(m2+m1/z**2,m2))==s.zeros(2))
expected=s.Matrix([-(m2*l1*c+m2*l2)*u**2-m2*l2*v**2-(2*m2*l2+m2*l1*c+m1*l1*c/z**2)*u*v,m2*l1*z*u**2+l1*m2*z*u*v])
ok('Expanded Vx equals transform',s.simplify(Vx-expected)==s.zeros(2,1))
a,g=s.symbols('a g',real=True);G=s.Matrix([m2*l2*g*s.cos(a+t)+(m1+m2)*l1*g*s.cos(a),m2*l2*g*s.cos(a+t)])
Gx=s.simplify(Ji.T*G);expectedG=s.Matrix([m1*g*s.cos(a)/z+m2*g*s.sin(a+t),m2*g*s.cos(a+t)])
ok('Expanded Gx equals transform',s.trigsimp(Gx-expectedG)==s.zeros(2,1))
S={m1:2,m2:3,l1:1,l2:2,t:s.pi/2,u:1,v:2}
ok('Numerical M',M.subs(S)==s.Matrix([[17,12],[12,12]]))
ok('Numerical V',V.subs(S)==s.Matrix([-48,6]))
ok('Numerical inverse',Ji.subs(S)==s.Matrix([[1,0],[-1,s.Rational(1,2)]]))
ok('Numerical Jdot',Jd.subs(S)==s.Matrix([[0,0],[-2,0]]))
ok('Numerical Vx',Vx.subs(S)==s.Matrix([-54,9]))
ok('Numerical G',G.subs(S|{a:0,g:10})==s.Matrix([50,0]))
ok('Numerical Gx',Gx.subs(S|{a:0,g:10})==s.Matrix([50,0]))
ok('30degree inertia',Mx.subs({m1:2,m2:3,t:s.pi/6})==s.diag(11,3))
ok('Inverse acceleration',(s.diag(2,1).inv()*(s.Matrix([5,4])-s.Matrix([1,-2])))==s.Matrix([2,6]))
ok('Four-joint pair count',4*3//2==6)
ok('Three-joint pairs',len({(i,j) for i in range(3) for j in range(i+1,3)})==3)
ok('Combined friction negative speed',2*(-1)+s.Rational(1,2)*(-4)==-4)
ok('Coupled forward solve',s.Matrix([[2,1],[1,2]]).inv()*s.Matrix([4,4])==s.Matrix([s.Rational(4,3)]*2))
ok('Displayed integration position',1+2*s.Rational(1,10)+s.Rational(1,2)*(-4)*s.Rational(1,100)==s.Rational(118,100))
ok('Displayed integration velocity',2-4*s.Rational(1,10)==s.Rational(16,10))
# Independent author-side random substitution checks of the algebraic mapping.
rng=np.random.default_rng(1515);fn=s.lambdify((m1,m2,l1,l2,t,u,v),(M,J,V,Jd,Mx,Vx),'numpy')
for i in range(400):
 pars=[*rng.uniform(.2,4,4),rng.uniform(.15,2.9),*rng.uniform(-3,3,2)];mn,jn,vn,jdn,mxn,vxn=fn(*pars);qd=np.array(pars[-2:]);qdd=rng.normal(size=2);taskdot=jdn@qd+jn@qdd;torque=mn@qdd+vn.ravel();taskforce=mxn@taskdot+vxn.ravel()
 assert np.allclose(jn.T@taskforce,torque,rtol=1e-9,atol=1e-9)
 assert np.all(np.linalg.eigvalsh(mn)>0) and np.all(np.linalg.eigvalsh(mxn)>0)
 assert np.isclose(float((jn@qd)@taskforce),float(qd@torque),rtol=1e-9,atol=1e-9)
checks.append('400 random congruence/dynamics/power cases, three assertions each')
report={'status':'author-checks-passed','notIndependentReview':True,'fixedCheckCount':20,'randomCases':400,'randomAssertions':1200,'checks':checks,'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(r/'audits/W03-L15-author-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
