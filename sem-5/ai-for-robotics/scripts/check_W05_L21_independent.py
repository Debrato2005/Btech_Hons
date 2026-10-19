#!/usr/bin/env python3
"""Reviewer-owned source/answer-free L21 computations, before keyed access."""
import datetime, json, math, random
from pathlib import Path
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name, expr):
    assert bool(expr), name
    checks.append(name)
t,z=s.symbols('t z', real=True);m,b,k,Kv,Kp,kv,kp,ki=s.symbols('m b k Kv Kp kv kp ki', positive=True)
x,v,u,xd,vd,ad,F,d=s.symbols('x v u xd vd ad F d', real=True)
check('Two-joint feedforward torque',s.Matrix([[2,1],[1,3]])*s.Matrix([1,-2])+s.Matrix([1,0])+s.Matrix([3,4])==s.Matrix([4,-1]))
check('Desired-minus-actual position error',s.Rational(8,10)-s.Rational(5,10)==s.Rational(3,10))
check('Desired-minus-actual velocity error',-s.Rational(2,10)-s.Rational(1,10)==-s.Rational(3,10))
check('Free-mass acceleration sign',(-8*s.Rational(1,2)-3*(-1))/2==-s.Rational(1,2))
trial=s.exp(z*t)
check('Exponential characteristic substitution',s.simplify((m*s.diff(trial,t,2)+b*s.diff(trial,t)+k*trial)/trial)==m*z*z+b*z+k)
check('Overdamped polynomial factor',s.expand((z+2)*(z+3))==z*z+5*z+6)
for bv,sg in [(1,-1),(2,0),(3,1)]:check('Discriminant at damping '+str(bv),s.sign(bv*bv-4)==sg)
xover=3*s.exp(-2*t)-2*s.exp(-3*t)
check('Overdamped initial displacement',xover.subs(t,0)==1)
check('Overdamped initial velocity',s.diff(xover,t).subs(t,0)==0)
check('Overdamped ODE residual',s.simplify(s.diff(xover,t,2)+5*s.diff(xover,t)+6*xover)==0)
A,B,lam,mu=s.symbols('A B lam mu',real=True)
c1=(A-s.I*B)/2;c2=(A+s.I*B)/2
check('Cosine coefficient from conjugate modes',s.simplify(c1+c2-A)==0)
check('Sine coefficient from conjugate modes',s.simplify(s.I*(c1-c2)-B)==0)
check('Amplitude from real coefficients',s.sqrt((-3)**2+4**2)==5)
phase=math.atan2(4,-3)
check('Phase quadrant two',math.pi/2<phase<math.pi)
check('Phase reconstructs negative cosine coefficient',math.isclose(5*math.cos(phase),-3,abs_tol=1e-12))
check('Phase reconstructs positive sine coefficient',math.isclose(5*math.sin(phase),4,abs_tol=1e-12))
wn=s.sqrt(s.Rational(16,4));zeta=s.Rational(8,1)/(2*s.sqrt(4*16))
check('Natural frequency',wn==2)
check('Damping ratio',zeta==s.Rational(1,2))
check('Real pole part',-zeta*wn==-1)
check('Imaginary pole part',wn*s.sqrt(1-zeta*zeta)==s.sqrt(3))
crit=(1+4*t)*s.exp(-4*t)
check('Critical initial position',crit.subs(t,0)==1)
check('Critical initial velocity',s.diff(crit,t).subs(t,0)==0)
check('Critical ODE residual',s.simplify(s.diff(crit,t,2)+8*s.diff(crit,t)+16*crit)==0)
check('Critical response decays',s.limit(crit,t,s.oo)==0)
check('Direct force feedback coefficients',s.expand(b*v+k*x-(-Kv*v-Kp*x)-(b+Kv)*v-(k+Kp)*x)==0)
check('Direct proportional gain',16-1==15)
check('Direct derivative gain',2*s.sqrt(16)-1==7)
check('Negative individual gains stable effective polynomial',s.factor(z*z+4*z+4)==(z+2)**2)
check('Model cancellation',s.expand((m*u+b*v+k*x-b*v-k*x)/m)==u)
check('Physical force example',2*s.Rational(3,2)+3*(-s.Rational(1,5))+5*s.Rational(2,5)==s.Rational(22,5))
mh,bh,kh=s.symbols('mh bh kh')
check('Model mismatch identity',s.expand(mh*u+bh*v+kh*x-b*v-k*x-(mh*u+(bh-b)*v+(kh-k)*x))==0)
check('Normalized critical gain ten',2*s.sqrt(25)==10)
check('Partition and direct-force example equivalence',s.expand(-16*x-8*v+x+v)==-15*x-7*v)
e,ed=s.symbols('e ed'); command=ad+kv*ed+kp*e
check('Homogeneous tracking error',s.expand(ad-command+kv*ed+kp*e)==0)
check('Tracking numeric command',-s.Rational(1,5)+6*s.Rational(3,10)+9*s.Rational(1,5)==s.Rational(17,5))
check('Missing feedforward forcing',s.expand(ad-(kv*ed+kp*e)+kv*ed+kp*e)==ad)
check('Resisting physical force sign and mass',s.expand(ad-(command-F/m)+kv*ed+kp*e)==F/m)
check('Assisting physical force sign and mass',s.expand(ad-(command+F/m)+kv*ed+kp*e)==-F/m)
check('Constant disturbance equilibrium',s.solve(kp*e-d,e)[0]==d/kp)
check('Physical force normalized before steady error',s.Rational(6,2)/3==1)
check('Proportional gain doubles halve equilibrium',s.simplify((d/(2*kp))/(d/kp))==s.Rational(1,2))
efun=s.Function('e')(t);dfun=s.Function('d')(t);Z=s.Function('Z')(t)
orig=s.diff(efun,t,2)+kv*s.diff(efun,t)+kp*efun+ki*Z-dfun
expected=s.diff(efun,t,3)+kv*s.diff(efun,t,2)+kp*s.diff(efun,t)+ki*efun-s.diff(dfun,t)
check('Differentiated disturbance includes derivative',s.expand(s.diff(orig,t).subs(s.diff(Z,t),efun)-expected)==0)
check('Integral stored-state equilibrium',s.Rational(4,2)==2)
check('Positive-gain unstable factorization',s.expand((z+3)*(z*z-z+4))==z**3+2*z*z+z+12)
check('Unstable pair real parts',all(s.re(root)==s.Rational(1,2) for root in s.solve(z*z-z+4,z)))
check('Original equation fixes integral initial state',s.solve(s.Symbol('e2')+kv*s.Symbol('e1')+kp*s.Symbol('e0')+ki*Z-d,Z)[0]==(d-s.Symbol('e2')-kv*s.Symbol('e1')-kp*s.Symbol('e0'))/ki)
# Synthesize a non-special underdamped initial-condition response for coverage challenge.
under=s.exp(-t)*(s.cos(s.sqrt(3)*t)+s.sin(s.sqrt(3)*t)/s.sqrt(3))
check('Underdamped example initial position',under.subs(t,0)==1)
check('Underdamped example initial velocity',s.diff(under,t).subs(t,0)==0)
check('Underdamped example ODE',s.simplify(s.diff(under,t,2)+2*s.diff(under,t)+4*under)==0)
rng=random.Random(21637668);max_residual=0.0
for _ in range(500):
    mm,bb,kk=[rng.uniform(.2,20) for _ in range(3)];xx,vv,uu,aa,ee,de,ff=[rng.uniform(-10,10) for _ in range(7)]
    vp,pp=[rng.uniform(.5,10) for _ in range(2)]
    force=mm*uu+bb*vv+kk*xx
    residual=(force-bb*vv-kk*xx)/mm-uu
    max_residual=max(max_residual,abs(residual));assert abs(residual)<1e-11
    cmd=aa+vp*de+pp*ee
    assert math.isclose(aa-(cmd-ff/mm)+vp*de+pp*ee,ff/mm,rel_tol=1e-10,abs_tol=1e-10)
    assert math.isclose(aa-(cmd+ff/mm)+vp*de+pp*ee,-ff/mm,rel_tol=1e-10,abs_tol=1e-10)
    av,bv=[rng.uniform(-10,10) for _ in range(2)]
    rr=math.hypot(av,bv);delta=math.atan2(bv,av)
    assert math.isclose(rr*math.cos(delta),av,abs_tol=1e-11) and math.isclose(rr*math.sin(delta),bv,abs_tol=1e-11)
report={'batchId':'W05-L21','reviewerId':'define_robotics_data_contracts:L21-independent-reviewer','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorKeysSeen':False,'exactAssertionCount':len(checks),'exactAssertions':checks,'randomTrials':500,'randomChecksPerTrial':4,'maximumModelCancellationResidual':max_residual,'testFixturesAreSynthetic':True,'coursePoolModified':False,'source':'Actual source pixels and answer-free packet, without author proposed keys or computations.'}
(ROOT/'audits/W05-L21-independent-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'exactAssertions':len(checks),'randomTrials':500,'maxResidual':max_residual}))
