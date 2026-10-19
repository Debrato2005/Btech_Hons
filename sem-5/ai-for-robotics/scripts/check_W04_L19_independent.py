#!/usr/bin/env python3
"""Independent source-derived L19 checks; authored before proposed-key access."""
import datetime, hashlib, json, math, random
from pathlib import Path
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name, assertion):
    assert bool(assertion), name
    checks.append(name)
# Spatial mobility and attachment geometry.
l,n,fs=s.symbols('l n fs')
check('Gruebler equivalent constraint-count forms',s.expand(6*(l-n-1)+fs-(6*(l-1)-(6*n-fs)))==0)
check('Six legs contain eighteen joints',6*3==18)
check('Six telescoping members contribute twelve links',6*2==12)
check('Base and platform included in fourteen links',12+2==14)
check('Universal spherical prismatic freedom sum',6*(2+3+1)==36)
check('Generic Stewart mobility',6*(14-18-1)+36==6)
p=s.Matrix([0,0,2]);a=s.Matrix([1,0,0]);b=s.Matrix([1,0,0]);R=s.eye(3)
check('Specified Stewart attachment distance',s.sqrt((p+R*a-b).dot(p+R*a-b))==2)
J=s.eye(6).row_join(s.zeros(6,1))
check('Regular six-task seven-coordinate nullity',J.rank()==6 and len(J.nullspace())==1)
# Ideal and lossy gear relations, speed and power.
eta,ki,ti,wi,eps=s.symbols('eta ki ti wi eps',positive=True)
wo=wi/eta;to=eta*ti;theta_i=s.symbols('theta_i',positive=True)
check('Ideal gear power identity',s.simplify(to*wo-ti*wi)==0)
check('Lossy output torque identity',s.simplify((eps*eta*ti)*wo-eps*ti*wi)==0)
check('Reflected rotational stiffness',s.simplify((eta*ki*theta_i)/(theta_i/eta)-eta**2*ki)==0)
check('Gear speed 100 over 5',s.Rational(100,5)==20)
check('Gear torque 5 times 2',5*2==10)
check('Lossy gear torque eight',s.Rational(4,5)*5*2==8)
check('Pulley ratio three',s.Rational(60,20)==3)
check('Pulley output speed four',s.Rational(12,3)==4)
# Linear stiffness, coordinate referral and dimensions.
k1,k2,F,A,E,L,G,d=s.symbols('k1 k2 F A E L G d',positive=True)
kp=k1+k2;ks=k1*k2/(k1+k2)
check('Series from summed deflections',s.simplify(F/(F/k1+F/k2)-ks)==0)
check('Parallel from summed forces',s.simplify((k1*F+k2*F)/F-kp)==0)
check('Series 100 and 300',ks.subs({k1:100,k2:300})==75)
check('Parallel load displacement',s.Rational(40,100+300)==s.Rational(1,10))
check('Motor-side stiffness referred to output',3**2*100==900)
check('Series total after common-coordinate referral',s.Rational(900*900,900+900)==450)
axial=A*E/L;shaft=G*s.pi*d**4/(32*L)
check('Axial compliance linear in length',s.simplify(1/axial-L/(A*E))==0)
check('Belt unit conversion and value',axial.subs({A:s.Rational(2,10**6),E:10**9,L:s.Rational(1,2)})==4000)
check('Shaft exact value',shaft.subs({G:80*10**9,d:s.Rational(2,100),L:s.Rational(1,2)})==800*s.pi)
check('Shaft approximate value',abs(float(800*s.pi)-2513.2741228718346)<1e-10)
check('Shaft diameter doubles factor sixteen',s.simplify(shaft.subs(d,2*d)/shaft)==16)
check('Shaft length doubles factor one half',s.simplify(shaft.subs(L,2*L)/shaft)==s.Rational(1,2))
check('Fixed-torque twist doubles with length',s.simplify((ti/shaft.subs(L,2*L))/(ti/shaft))==2)
Cg,width,r=s.symbols('Cg width r',positive=True);gear=Cg*width*r*r
check('Gear width radius combined scaling',s.simplify(gear.subs({width:2*width,r:r/2})/gear)==s.Rational(1,2))
do,di,wo_,wi_=s.symbols('do di wo wi',positive=True)
round_k=3*s.pi*E*(do**4-di**4)/(64*L**3)
square_k=E*(wo_**4-wi_**4)/(4*L**3)
check('Round cantilever equals three EI over L cubed',s.simplify(round_k-3*E*(s.pi*(do**4-di**4)/64)/L**3)==0)
check('Square cantilever equals three EI over L cubed',s.simplify(square_k-3*E*((wo_**4-wi_**4)/12)/L**3)==0)
check('Vanishing wall round beam limit',s.limit(round_k,di,do,dir='-')==0)
check('Round cantilever length scale',s.simplify(round_k.subs(L,2*L)/round_k)==s.Rational(1,8))
check('Square cantilever length scale',s.simplify(square_k.subs(L,2*L)/square_k)==s.Rational(1,8))
check('Round half-inner-diameter retained stiffness',s.simplify(round_k.subs(di,do/2)/round_k.subs(di,0))==s.Rational(15,16))
check('Square section subtracts inner fourth power',s.expand(square_k*4*L**3/E)==wo_**4-wi_**4)
check('Motor torque in constant-flux range',s.Rational(4,10)*3==s.Rational(12,10))
check('Servo desired-minus-measured angle',30-26==4)
signal,bias=s.symbols('signal bias')
check('Differential sensor cancels common bias',s.expand(((signal+bias)-(-signal+bias))/2)==signal)
check('Linear flexure inverse stiffness sensitivity',s.diff(F/k1,F)==1/k1)
# A simple support triangle illustrates, without adding a course-pool item,
# why wheel count is insufficient. Barycentric weights must be nonnegative.
S=s.Matrix([[0,1,0],[0,0,1],[1,1,1]])
inside=S.inv()*s.Matrix([s.Rational(1,4),s.Rational(1,4),1])
outside=S.inv()*s.Matrix([1,1,1])
check('Interior COM support reactions can be nonnegative',all(x>=0 for x in inside))
check('Exterior COM would require a negative unilateral reaction',any(x<0 for x in outside))
rng=random.Random(190619);max_power_error=0.0
for _ in range(500):
    x,y=[10**rng.uniform(-2,5) for _ in range(2)]
    series=x*y/(x+y)
    assert 0<series<min(x,y)
    assert max(x,y)<x+y
    ratio=rng.uniform(1,100);torque=rng.uniform(.01,100);speed=rng.uniform(.01,100)
    max_power_error=max(max_power_error,abs((ratio*torque)*(speed/ratio)-torque*speed))
    assert math.isclose((ratio*torque)*(speed/ratio),torque*speed,rel_tol=1e-12)
    stiffness=rng.uniform(.1,1000);angle=rng.uniform(.0001,.1)
    assert math.isclose((ratio*stiffness*angle)/(angle/ratio),ratio**2*stiffness,rel_tol=1e-12)
report={'batchId':'W04-L19','reviewerId':'define_robotics_data_contracts:L19-independent-reviewer','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorKeysSeen':False,'exactAssertionCount':len(checks),'exactAssertions':checks,'randomTrials':500,'randomChecksPerTrial':4,'maximumAbsoluteGearPowerResidual':max_power_error,'testFixturesAreSynthetic':True,'coursePoolModified':False,'source':'Source equations and answer-free packet only; no author solution or author computation script was opened.'}
(ROOT/'audits/W04-L19-independent-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'exactAssertions':len(checks),'randomTrials':500,'maxPowerResidual':max_power_error}))
