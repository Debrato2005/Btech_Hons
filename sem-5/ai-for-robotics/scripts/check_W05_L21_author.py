#!/usr/bin/env python3
"""Author-side independent-of-serialization algebra checks, not independent review."""
import datetime,json,math
from pathlib import Path
import numpy as np
import sympy as s
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
x,v,acc,m,b,k,Kp,Kv,kp,kv,ki,fp,xd,vd,ad,e,ed,edd,z,d,F=s.symbols('x v acc m b k Kp Kv kp kv ki fp xd vd ad e ed edd z d F',real=True)
check('Feedforward coupled matrix calculation',np.allclose(np.array([[2,1],[1,3]])@np.array([1,-2])+[1,0]+np.array([3,4]),[4,-1]))
check('Joint error signs',math.isclose(.8-.5,.3) and math.isclose(-.2-.1,-.3))
check('Passive acceleration example',math.isclose((-8*.5-3*(-1))/2,-.5))
t=s.symbols('t',real=True);ss=s.symbols('s')
check('Distinct real roots',s.factor(ss**2+5*ss+6)==(ss+2)*(ss+3))
response=3*s.exp(-2*t)-2*s.exp(-3*t)
check('Distinct-root initial conditions',response.subs(t,0)==1 and s.diff(response,t).subs(t,0)==0)
check('Distinct-root response satisfies equation',s.simplify(s.diff(response,t,2)+5*s.diff(response,t)+6*response)==0)
A,B,lam,mu,c1,c2=s.symbols('A B lam mu c1 c2',real=True)
check('Amplitude phase example',math.isclose(math.hypot(-3,4),5) and math.pi/2<math.atan2(4,-3)<math.pi)
check('Damping example',math.isclose(math.sqrt(16/4),2) and math.isclose(8/(2*math.sqrt(16*4)),.5))
check('Damped pole components',math.isclose(-.5*2,-1) and math.isclose(2*math.sqrt(1-.25),math.sqrt(3)))
crit=(1+4*t)*s.exp(-4*t)
check('Critical initial conditions',crit.subs(t,0)==1 and s.diff(crit,t).subs(t,0)==0)
check('Critical response equation',s.simplify(s.diff(crit,t,2)+8*s.diff(crit,t)+16*crit)==0)
check('Direct feedback collection',s.expand(m*acc+b*v+k*x-(-Kp*x-Kv*v))==s.expand(m*acc+(b+Kv)*v+(k+Kp)*x))
check('Direct critical example',16-1==15 and 2*math.sqrt(16)-1==7)
check('Negative gain stable example',9-5==4 and 10-6==4 and s.factor(ss**2+4*ss+4)==(ss+2)**2)
check('Exact model cancellation',s.simplify((m*fp+b*v+k*x-b*v-k*x)/m)==fp)
check('Partition force example',math.isclose(2*1.5+3*(-.2)+5*.4,4.4))
check('Normalized critical example',2*math.sqrt(25)==10)
check('Equivalent physical controller',s.expand((-16*x-8*v)+(v+x))==-15*x-7*v)
check('Tracking command example',math.isclose(-.2+6*(.4-.1)+9*(.5-.3),3.4))
check('Swapped error distractor',math.isclose(-.2+6*.2+9*.3,3.7))
check('Desired acceleration cancels',s.expand(ad-(ad+kv*ed+kp*e)+kv*ed+kp*e)==0)
check('Resisting force error sign',s.simplify(ad-(ad+kv*ed+kp*e-F/m)+kv*ed+kp*e)==F/m)
check('Additive force error sign',s.simplify(ad-(ad+kv*ed+kp*e+F/m)+kv*ed+kp*e)==-F/m)
check('Physical force normalized steady offset',math.isclose(6/(2*3),1))
check('Integral balancing state',6/3==2)
check('Positive-gain unstable cubic factorization',s.expand((ss+3)*(ss**2-ss+4))==ss**3+2*ss**2+ss+12)
roots=np.roots([1,2,1,12]);check('Positive-gain unstable roots',sum(float(r.real)>0 for r in roots)==2 and np.allclose(sorted(roots.real),[-3,.5,.5]))
rng=np.random.default_rng(21637)
for _ in range(1000):
 mm,bb,kk=rng.uniform(.1,10,3);xx,vv,ff=rng.normal(size=3)
 force=mm*ff+bb*vv+kk*xx
 assert np.isclose((force-bb*vv-kk*xx)/mm,ff)
 p=float(rng.uniform(.1,25));vv_gain=2*np.sqrt(p)
 assert np.isclose(vv_gain**2-4*p,0)
 desired= float(rng.normal());ee,ev=rng.normal(size=2);forcing=float(rng.normal())
 command=desired+vv_gain*ev+p*ee
 actual=command-forcing
 error_acc=desired-actual
 assert np.isclose(error_acc+vv_gain*ev+p*ee,forcing)
 err_ss=forcing/p;assert np.isclose(p*err_ss,forcing)
 # Separate arbitrary positive stable second-order coefficients from the special critical design.
 damping=float(rng.uniform(.1,10));assert np.all(np.roots([1,damping,p]).real<0)
 # Stable integral polynomial constructed from three strictly negative real poles.
 rates=rng.uniform(.1,5,3);coeff=np.poly(-rates)
 assert np.all(np.roots(coeff).real<0)
 ii=float(coeff[-1]);zz=forcing/ii;assert np.isclose(ii*zz,forcing)
check('1000 deterministic compensation, tracking, damping and integral-equilibrium cases',True)
report={'authorId':'build_offline_study_interface:L21-author','checkKind':'author calculations only, not independent answer verification','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'namedCheckCount':len(checks),'namedChecks':checks,'randomizedCases':1000,'randomSeed':21637,'result':'pass','printedExecutableCodePresent':False,'missingSupplement':'second_order_simulator_v2.html is linked on p647 but not supplied; no source-code execution is claimed.','independentReviewStillRequired':True}
(R/'audits/W05-L21-author-computations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['result','namedCheckCount','randomizedCases','independentReviewStillRequired']}))
