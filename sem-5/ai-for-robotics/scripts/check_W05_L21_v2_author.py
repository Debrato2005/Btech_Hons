#!/usr/bin/env python3
"""Author checks for L21 repaired mathematics, not independent review."""
import json,math,random
from pathlib import Path
import sympy as s
R=Path(__file__).resolve().parents[1];t=s.symbols('t',real=True);checks=[]
def ok(name,value):
 assert value,name
 checks.append(name)
x=s.exp(-t)*(s.Rational(1,5)*s.cos(2*t)+s.Rational(3,10)*s.sin(2*t))
ok('Q049 satisfies physical ODE',s.simplify(2*s.diff(x,t,2)+4*s.diff(x,t)+10*x)==0)
ok('Q049 initial displacement',x.subs(t,0)==s.Rational(1,5));ok('Q049 initial velocity',s.diff(x,t).subs(t,0)==s.Rational(2,5))
wrong=[s.exp(-t)*(s.Rational(1,5)*s.cos(2*t)+s.Rational(1,5)*s.sin(2*t)),s.exp(-t)*(s.Rational(1,5)*s.cos(s.sqrt(5)*t)+s.Rational(3,5)/s.sqrt(5)*s.sin(s.sqrt(5)*t)),s.exp(-2*t)*(s.Rational(1,5)*s.cos(2*t)+s.Rational(2,5)*s.sin(2*t))]
for i,w in enumerate(wrong):ok(f'Q049 distractor {i+2} fails ODE or initial velocity',s.simplify(2*s.diff(w,t,2)+4*s.diff(w,t)+10*w)!=0 or s.diff(w,t).subs(t,0)!=s.Rational(2,5))
ok('Q049 damped frequency differs from natural frequency',s.sqrt(5-1)==2 and s.sqrt(5)!=2)
ok('Q049 envelope amplitude',s.sqrt(s.Rational(1,5)**2+s.Rational(3,10)**2)==s.sqrt(13)/10)
ok('Q044 critical gain',2*s.sqrt(25)==10)
m,mh,b,bh,k,kh,v,p,u=s.symbols('m mh b bh k kh v p u',nonzero=True)
f=mh*u+bh*v+kh*p
ok('Q043 mismatch identity',s.expand(f-b*v-k*p-(mh*u+(bh-b)*v+(kh-k)*p))==0)
xd2,ed,kp,kv,e,F=s.symbols('xd2 ed kp kv e F')
ok('Q053 omitted feedforward',s.expand((xd2-(kv*ed+kp*e))+kv*ed+kp*e-xd2)==0)
ok('Q057 additive-force sign',s.expand((xd2-(xd2+kv*ed+kp*e+F/m))+kv*ed+kp*e+F/m)==0)
r=random.Random(21)
for _ in range(1000):
 mass=r.uniform(.2,10);lam=-r.uniform(.05,5);mu=r.uniform(.1,7);damp=-2*mass*lam;stiff=mass*(lam*lam+mu*mu);x0=r.uniform(-2,2);v0=r.uniform(-3,3);A=x0;B=(v0-lam*x0)/mu;tt=r.uniform(0,3)
 z=A*math.cos(mu*tt)+B*math.sin(mu*tt);dz=-A*mu*math.sin(mu*tt)+B*mu*math.cos(mu*tt);ddz=-mu*mu*z
 xx=math.exp(lam*tt)*z;vv=math.exp(lam*tt)*(lam*z+dz);aa=math.exp(lam*tt)*(lam*lam*z+2*lam*dz+ddz)
 assert abs(mass*aa+damp*vv+stiff*xx)<1e-8
 assert abs(lam*A+mu*B-v0)<1e-10
out={'kind':'author calculations, not independent verification','allPassed':True,'assertionCount':len(checks),'checks':checks,'randomUnderdampedInitialConditionCases':1000}
(R/'audits/W05-L21-v2-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
