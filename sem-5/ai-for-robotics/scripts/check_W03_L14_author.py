"""L14 author calculations, not independent second-agent verification."""
from pathlib import Path
import json,hashlib,random,math,datetime
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name,condition):
 assert bool(condition),name
 checks.append(name)
t,w,a,m,l,kt,g,T=s.symbols('theta w a m l kt g tau',real=True)
K=s.Rational(1,2)*m*l*l*w*w;U=s.Rational(1,2)*kt*t*t-m*g*l*s.sin(t)
L=K-U
EL=s.diff(s.diff(L,w),t)*w+s.diff(s.diff(L,w),w)*a-s.diff(L,t)
check('Single-joint Euler–Lagrange matches displayed energies',s.simplify(EL-(m*l*l*a+kt*t-m*g*l*s.cos(t)))==0)
check('Single-joint K coordinate partial is zero',s.diff(K,t)==0)
check('Single-joint energy derivative equals required-torque power',s.simplify(s.diff(K+U,t)*w+s.diff(K+U,w)*a-EL*w)==0)
check('Single-joint torque sample exact',s.simplify(EL.subs({m:2,l:s.Rational(1,2),kt:3,g:10,t:s.pi/6,a:4})-(2+s.pi/2-5*s.sqrt(3)))==0)
check('Horizontal unforced acceleration g/l',s.simplify(s.solve(EL.subs(t,0),a)[0]-g/l)==0)
check('Spring 90-degree magnitude is 2 pi',4*s.pi/2==2*s.pi)
check('Translation and spin energy example 13 J',s.Rational(1,2)*2*9+s.Rational(1,2)*s.Rational(1,2)*16==13)
check('Gravity-vector potential example 60 J',-2*s.Matrix([0,-10,0]).dot(s.Matrix([2,3,0]))==60)
d,v,b,m1,m2,l1,I1,I2,D=s.symbols('d v b m1 m2 l1 I1 I2 D',real=True)
A=m1*l1*l1+I1+I2+m2*d*d
Kr=s.Rational(1,2)*A*w*w+s.Rational(1,2)*m2*v*v
Ur=g*(m1*l1+m2*d)*s.sin(t)+m1*l1*g+m2*g*D
Lr=Kr-Ur
q=s.Matrix([t,d]);qd=s.Matrix([w,v]);qdd=s.Matrix([a,b])
p=s.Matrix([s.diff(Lr,x) for x in qd]);e=p.jacobian(q)*qd+p.jacobian(qd)*qdd-s.Matrix([s.diff(Lr,x) for x in q])
expect=s.Matrix([A*a+2*m2*d*w*v+g*(m1*l1+m2*d)*s.cos(t),m2*b-m2*d*w*w+m2*g*s.sin(t)])
check('Both RP equations from symbolic Euler–Lagrange',s.simplify(e-expect)==s.zeros(2,1))
check('RP kinetic Hessian is diag(A,m2)',s.hessian(Kr,qd)==s.diag(A,m2))
check('RP generalized momenta',s.simplify(p-s.Matrix([A*w,m2*v]))==s.zeros(2,1))
check('RP fixed dmax derivative vanishes',s.diff(m2*g*D,d)==0)
check('RP kinetic coordinate derivatives',s.Matrix([s.diff(Kr,x) for x in q])==s.Matrix([0,m2*d*w*w]))
check('RP gravity derivatives',s.simplify(s.Matrix([s.diff(Ur,x) for x in q])-s.Matrix([g*(m1*l1+m2*d)*s.cos(t),m2*g*s.sin(t)]))==s.zeros(2,1))
check('RP datum reaches zero at downward maximum extension',s.simplify(Ur.subs({t:-s.pi/2,d:D}))==0)
V=s.Matrix([2*m2*d*w*v,-m2*d*w*w]);M=s.diag(A,m2);Mdot=M.diff(d)*v
check('RP velocity-power consistency',s.simplify((qd.T*V)[0]-(qd.T*Mdot*qd)[0]/2)==0)
Edot=(s.Matrix([s.diff(Kr+Ur,x) for x in q]).T*qd)[0]+(s.Matrix([s.diff(Kr+Ur,x) for x in qd]).T*qdd)[0]
check('Full RP energy-power identity',s.simplify(Edot-(expect.T*qd)[0])==0)
check('RP no-gravity angular equation is momentum derivative',s.simplify(e[0].subs(g,0)-(s.diff(A*w,d)*v+s.diff(A*w,w)*a))==0)
sample={m1:2,l1:s.Rational(1,2),I1:s.Rational(1,5),I2:s.Rational(3,10),m2:3,d:s.Rational(2,5),t:0,w:2,v:s.Rational(1,2),a:1,b:-s.Rational(1,5),g:10}
check('RP kinetic numeric sample 3.335 J',Kr.subs(sample)==s.Rational(667,200))
check('RP mixed effort sample (25.88,-5.4)',expect.subs(sample)==s.Matrix([s.Rational(647,25),-s.Rational(27,5)]))
check('RP half-product distractor 24.68',expect[0].subs(sample)-s.Rational(6,5)==s.Rational(617,25))
check('RP wrong centripetal sign distractor 4.2',expect[1].subs(sample)+s.Rational(48,5)==s.Rational(21,5))
check('RP fixed-radius inward force -9',expect[1].subs({m2:2,d:s.Rational(1,2),w:3,b:0,g:0})==-9)
check('RP conservation sample 2.5 rad/s',s.Rational(5,2)*4/4==s.Rational(5,2))
check('RP reversing one rate changes only first V component',V.subs(w,-w)==s.Matrix([-V[0],V[1]]))
check('RP scalar coordinate order gives force second',e[1].has(I1)==False and e[1].has(I2)==False)
# Cartesian Newton check independent of energy differentiation: polar acceleration,
# COM gravity, and link spin acceleration projected into generalized directions.
rng=random.Random(14428);maxerr=0.0
# Plain scalar generated functions avoid a numpy dependency.
f1=s.lambdify((t,d,w,v,a,b,m1,m2,l1,I1,I2,g),e[0],'math');f2=s.lambdify((t,d,w,v,a,b,m1,m2,l1,I1,I2,g),e[1],'math')
for _ in range(400):
 theta=rng.uniform(-math.pi,math.pi);radius=rng.uniform(.05,2);omega=rng.uniform(-4,4);speed=rng.uniform(-2,2);alpha=rng.uniform(-5,5);radacc=rng.uniform(-4,4);mass1=rng.uniform(.2,5);mass2=rng.uniform(.2,5);r1=rng.uniform(.1,2);i1=rng.uniform(.01,1);i2=rng.uniform(.01,1);grav=rng.uniform(0,10)
 er=(math.cos(theta),math.sin(theta));et=(-math.sin(theta),math.cos(theta))
 acc1=(r1*(-omega**2*er[0]+alpha*et[0]),r1*(-omega**2*er[1]+alpha*et[1]))
 acc2=((radacc-radius*omega**2)*er[0]+(radius*alpha+2*speed*omega)*et[0],(radacc-radius*omega**2)*er[1]+(radius*alpha+2*speed*omega)*et[1])
 # Required non-gravity COM force is mass*(a-gvec); lever-arm cross products give torque.
 force1=(mass1*acc1[0],mass1*(acc1[1]+grav));force2=(mass2*acc2[0],mass2*(acc2[1]+grav))
 newton_tau=r1*(er[0]*force1[1]-er[1]*force1[0])+radius*(er[0]*force2[1]-er[1]*force2[0])+(i1+i2)*alpha
 newton_f=er[0]*force2[0]+er[1]*force2[1]
 args=(theta,radius,omega,speed,alpha,radacc,mass1,mass2,r1,i1,i2,grav)
 error=max(abs(newton_tau-f1(*args)),abs(newton_f-f2(*args)));maxerr=max(maxerr,error);assert error<1e-9
summary={'batchId':'W03-L14','authorId':'define_robotics_data_contracts:L14-author','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'symbolicAndNumericAssertions':len(checks),'checks':checks,'randomCases':400,'seed':14428,'maximumAbsoluteDifference':maxerr,'methods':['Differentiate stated scalar energies symbolically to obtain both RP and single-joint equations.','Compare RP equations with Cartesian COM accelerations, gravity forces, moment arms and COM spin moments in400 randomized cases.','Verify mixed-coordinate energy/power, datum independence, explicit numerical distractor mechanisms and momentum conservation.'],'limitation':'Author checks only. These do not replace independent source-based answer and omission review.','scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT/'audits/W03-L14-author-checks.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
