"""Independent L21 v2 computations from the answer-free packet and source pixels."""
import json,datetime,math,random
from pathlib import Path
import sympy as s
ROOT=Path(__file__).resolve().parents[1];checks=[]
def ck(name,e):
 assert s.simplify(e)==0,(name,e);checks.append(name)
t=s.symbols('t',real=True);x=s.exp(-t)*(s.Rational(1,5)*s.cos(2*t)+s.Rational(3,10)*s.sin(2*t))
ck('Q049 true ODE',2*s.diff(x,t,2)+4*s.diff(x,t)+10*x)
ck('Q049 initial displacement',x.subs(t,0)-s.Rational(1,5));ck('Q049 initial velocity',s.diff(x,t).subs(t,0)-s.Rational(2,5))
ck('Q049 decay rate',-s.Rational(4,2*2)+1);ck('Q049 damped frequency',s.sqrt(s.Rational(10,2)-1)-2)
ck('Q049 sine coefficient',(s.Rational(2,5)+s.Rational(1,5))/2-s.Rational(3,10))
alt2=s.exp(-t)*(s.Rational(1,5)*s.cos(2*t)+s.Rational(1,5)*s.sin(2*t));ck('Q049 o2 actual initial velocity',s.diff(alt2,t).subs(t,0)-s.Rational(1,5))
alt3=s.exp(-t)*(s.Rational(1,5)*s.cos(s.sqrt(5)*t)+s.Rational(3,5)/s.sqrt(5)*s.sin(s.sqrt(5)*t));ck('Q049 o3 initial velocity',s.diff(alt3,t).subs(t,0)-s.Rational(2,5));ck('Q049 o3 wrong stiffness ODE',2*s.diff(alt3,t,2)+4*s.diff(alt3,t)+12*alt3)
alt4=s.exp(-2*t)*(s.Rational(1,5)*s.cos(2*t)+s.Rational(2,5)*s.sin(2*t));ck('Q049 o4 initial velocity',s.diff(alt4,t).subs(t,0)-s.Rational(2,5));ck('Q049 o4 wrong model ODE',2*s.diff(alt4,t,2)+8*s.diff(alt4,t)+16*alt4)
for label,alt in [('o2',alt2),('o3',alt3),('o4',alt4)]:
 assert s.simplify(2*s.diff(alt,t,2)+4*s.diff(alt,t)+10*alt)!=0 or s.simplify(s.diff(alt,t).subs(t,0)-s.Rational(2,5))!=0;checks.append('Q049 '+label+' fails model or IC')
ck('Q009 error',s.Rational(8,10)-s.Rational(5,10)-s.Rational(3,10));ck('Q009 error derivative',-s.Rational(2,10)-s.Rational(1,10)+s.Rational(3,10))
ck('Q044 gain',2*s.sqrt(25)-10);ck('Q047 gain',2*s.sqrt(16)-8)
xv,vel,fp,m,mh,b,bh,k,kh,ed,ev,kp,kv,xdacc,F=s.symbols('x vel fp m mh b bh k kh ed ev kp kv xdacc F')
ck('Q043 true mismatch',(mh*fp+bh*vel+kh*xv-b*vel-k*xv)-(mh*fp+(bh-b)*vel+(kh-k)*xv))
ck('Q048 force expansion',(-16*xv-8*vel)+(xv+vel)-(-15*xv-7*vel))
ck('Q053 modified error forcing',(xdacc-(kv*ev+kp*ed))+kv*ev+kp*ed-xdacc)
ck('Q057 additive force sign',(xdacc-(xdacc+kv*ev+kp*ed+F/m))+kv*ev+kp*ed+F/m)
ck('Q062 settled error',kp*(F/kp)-F)
rng=random.Random(210220);maxres=0
for _ in range(300):
 mass=rng.uniform(.2,8);omega=rng.uniform(.2,8);zeta=rng.uniform(.01,.95);stiff=mass*omega**2;damp=2*zeta*mass*omega;lam=-damp/(2*mass);mu=math.sqrt(stiff/mass-lam**2);A=rng.uniform(-2,2);v0=rng.uniform(-3,3);B=(v0-lam*A)/mu;time=rng.uniform(0,3)
 C=A*math.cos(mu*time)+B*math.sin(mu*time);Cp=mu*(-A*math.sin(mu*time)+B*math.cos(mu*time));xx=math.exp(lam*time)*C;vv=math.exp(lam*time)*(lam*C+Cp);aa=math.exp(lam*time)*((lam*lam-mu*mu)*C+2*lam*Cp)
 res=abs(mass*aa+damp*vv+stiff*xx);assert res<1e-9;maxres=max(maxres,res);assert abs(lam*A+mu*B-v0)<1e-12
out={'reviewerId':'define_robotics_data_contracts:L21-independent-reviewer','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'currentAuthorKeysSeen':False,'priorV1Exposure':True,'exactAssertions':len(checks),'assertions':checks,'randomUnderdampedTrials':300,'checksPerTrial':2,'maxOdeResidual':maxres,'newQ049IndependentSolution':{'lambda':-1,'mu':2,'A':.2,'B':.3,'option':'o1','o2InitialVelocity':.2,'o3EquivalentStiffness':12,'o4EquivalentDamping':8,'o4EquivalentStiffness':16},'status':'passed'}
(ROOT/'audits/W05-L21-v2-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
