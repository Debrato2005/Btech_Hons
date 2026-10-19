#!/usr/bin/env python3
"""Independent checks written from the answer-free L25 v2 packet and actual source pixels.
Does not load the keyed batch or any author script. Never writes question data.
"""
import json, hashlib, random
from pathlib import Path
from datetime import datetime, timezone
import sympy as s
R=Path(__file__).resolve().parents[1]
checks=[]
def eq(name,actual,expected):
    assert actual==expected,(name,actual,expected)
    checks.append({'check':name,'actual':str(actual),'expected':str(expected),'passed':True})
M=s.Matrix([[2,1],[1,3]]);J=s.Matrix([[1,2],[0,1]])
eq('Q012 desired-minus-actual error',s.Matrix([s.Rational(4,10),s.Rational(2,10),s.Rational(5,10)])-s.Matrix([s.Rational(3,10),s.Rational(25,100),s.Rational(45,100)]),s.Matrix([s.Rational(1,10),-s.Rational(5,100),s.Rational(5,100)]))
a=s.Matrix([1,-2]);V=s.Matrix([s.Rational(1,2),1]);G=s.Matrix([1,4])
eq('Q030 coupled inertia contribution',M*a,s.Matrix([0,-5]))
eq('Q030 full force',M*a+V+G,s.Matrix([s.Rational(3,2),0]))
eq('Q030 o1 drops off-diagonal inertia',s.diag(2,3)*a+V+G,s.Matrix([s.Rational(7,2),-1]))
eq('Q030 o2 subtracts load',M*a-V-G,s.Matrix([-s.Rational(3,2),-10]))
eq('Q030 o3 omits V',M*a+G,s.Matrix([1,-1]))
x=s.symbols('x');
for kp,kv in [(4,4),(9,6)]:
 eq(f'Q035 discriminant kp={kp}',kv**2-4*kp,0)
 eq(f'Q035 repeated pole kp={kp}',s.solve(x*x+kv*x+kp,x),[-s.sqrt(kp)])
eq('Q037 physical force',3*4,12)
eq('Q037 actual acceleration',s.Rational(12,2),6)
eq('Q037 o2 treats estimate as exact',s.Rational(3*4,3),4)
eq('Q037 o4 reverses inertia ratio',s.Rational(2*4,3),s.Rational(8,3))
u=s.Matrix([1,-1]);h=s.Matrix([1,2])
eq('Q039 normalized model input',M*u,s.Matrix([1,-2]))
eq('Q039 force',M*u+h,s.Matrix([2,0]))
eq('Q039 torque',J.T*(M*u+h),s.Matrix([2,4]))
eq('Q039 o2 treats normalized input as force',J.T*u,s.Matrix([1,1]))
eq('Q039 o4 omits transpose mapping',M*u+h,s.Matrix([2,0]))
E=s.Matrix([s.Rational(1,2),-s.Rational(1,2)]);Ed=E;ad=s.Matrix([1,2]);Kp=s.diag(4,6);Kv=s.diag(2,4)
eq('Q053 proportional acceleration',Kp*E,s.Matrix([2,-3]))
eq('Q053 derivative acceleration',Kv*Ed,s.Matrix([1,-2]))
u=ad+Kv*Ed+Kp*E
eq('Q053 servo acceleration',u,s.Matrix([4,-3]))
eq('Q053 inertia force',M*u,s.Matrix([5,-5]))
eq('Q053 total force',M*u+h,s.Matrix([6,-3]))
eq('Q053 commanded torque',J.T*(M*u+h),s.Matrix([6,9]))
eq('Q053 o2 omits desired acceleration',J.T*(M*(u-ad)+h),s.Matrix([2,-6]))
eq('Q053 o3 deletes coupling',J.T*(s.diag(2,3)*u+h),s.Matrix([9,11]))
eq('Q053 o4 uses J rather than transpose',J*(M*u+h),s.Matrix([0,-3]))
Jd=s.Matrix([[0,1],[1,0]]);vd=s.Matrix([3,1]);ad=s.Matrix([2,4])
qd=J.inv()*vd;qdd=J.inv()*(ad-Jd*qd)
eq('Q054 nonsingular Jacobian',J.det(),1)
eq('Q054 joint velocity',qd,s.Matrix([1,1]))
eq('Q054 changing-Jacobian term',Jd*qd,s.Matrix([1,1]))
eq('Q054 joint acceleration',qdd,s.Matrix([-5,3]))
eq('Q054 reconstruct task acceleration',J*qdd+Jd*qd,ad)
eq('Q054 inverse derivative identity',-J.inv()*Jd*J.inv(),s.Matrix([[2,-5],[-1,2]]))
eq('Q054 derivative-of-inverse formulation',J.inv()*ad+(-J.inv()*Jd*J.inv())*vd,qdd)
eq('Q054 o2 neglects Jdot',J.inv()*ad,s.Matrix([-6,4]))
eq('Q054 o3 adds rather than subtracts',J.inv()*(ad+Jd*qd),s.Matrix([-7,5]))
eq('Q054 o4 numerically matches wrong J times task velocity',J*vd,s.Matrix([5,1]))
# Orthogonal frame change: both force and velocity rotate by the same mapping.
Rot=s.Matrix([[0,-1],[1,0]]);Fb=s.Matrix([2,3]);qb=s.Matrix([1,2]);vt=Rot*J*qb;Ft=Rot*Fb
teq=J.T*Fb
eq('Q041 frame-consistent torque',(Rot*J).T*Ft,teq)
eq('Q041 power invariance', (Ft.T*vt)[0], (teq.T*qb)[0])
# 500 exact integer/rational tests; independently chosen matrices.
rng=random.Random(2502)
for k in range(500):
 while True:
  A=s.Matrix(2,2,[rng.randint(-4,4) for _ in range(4)])
  if A.det()!=0:break
 B=s.Matrix(2,2,[rng.randint(-3,3) for _ in range(4)])
 qv=s.Matrix([rng.randint(-4,4) for _ in range(2)]);qa=s.Matrix([rng.randint(-4,4) for _ in range(2)])
 vv=A*qv;aa=A*qa+B*qv
 assert A.inv()*(aa-B*A.inv()*vv)==qa
 assert A.inv()*aa-A.inv()*B*A.inv()*vv==qa
 P=A.T*A+s.eye(2);z=s.Matrix([rng.randint(-5,5) for _ in range(2)]);load=s.Matrix([rng.randint(-5,5) for _ in range(2)])
 assert P.inv()*(P*z+load-load)==z
 F=P*z+load;t=A.T*F
 assert (qv.T*t)[0]==((A*qv).T*F)[0]
report={'reviewerId':'L25-v2-independent-python-coverage','basis':'Fresh answer-free packet plus all 23 actual source renders; no keyed batch or author checks read.','createdAt':datetime.now(timezone.utc).isoformat(),'checks':checks,'exactAssertions':len(checks),'randomCases':500,'randomAssertions':2000,'randomSeed':2502,'allPassed':True}
(R/'audits/W05-L25-v2-python-independent-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'exactAssertions':len(checks),'randomCases':500,'allPassed':True}))
