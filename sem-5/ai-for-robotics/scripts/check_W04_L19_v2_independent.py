#!/usr/bin/env python3
"""Independent repair/gap checks, before current-version keyed access; prior v1 exposure disclosed."""
import datetime, json, math, random
from pathlib import Path
import sympy as s
ROOT=Path(__file__).resolve().parents[1];checks=[]
def check(name,expr):
 assert bool(expr),name
 checks.append(name)
check('Four independent coordinates and rank three leave one null direction',4-3==1)
p=s.Matrix([0,0,2]);R=s.eye(3);a=b=s.Matrix([1,0,0]);v=p+R*b-a
check('Stated attachment-frame vector',v==s.Matrix([0,0,2]))
check('Stated leg length',s.sqrt(v.dot(v))==2)
ratio,theta,ki,torque=s.symbols('ratio theta ki torque',positive=True)
check('Common-coordinate reflected stiffness',s.simplify((ratio*ki*theta)/(theta/ratio))==ratio**2*ki)
A,E,L=s.symbols('A E L',positive=True)
check('Axial compliance',s.simplify(1/(A*E/L))==L/(A*E))
r1,r2,w1=s.symbols('r1 r2 w1',positive=True);w2=w1*r1/r2
check('Pulley no-slip speed ratio',s.simplify(w1/w2)==r2/r1)
lag=s.Rational(50,100)/10-s.Rational(4,100)
check('Motor angle referred to output',s.Rational(50,100)/10==s.Rational(5,100))
check('Two-encoder elastic lag',lag==s.Rational(1,100))
check('Output-referred stiffness',2/lag==200)
check('Wrong unscaled encoder subtraction',s.Rational(50,100)-s.Rational(4,100)==s.Rational(46,100))
check('Wrong unscaled stiffness',abs(float(2/s.Rational(46,100))-4.35)<0.005)
check('Using ideal angle instead of lag gives forty',2/s.Rational(5,100)==40)
check('Input torque paired with output lag gives twenty',s.Rational(2,10)/lag==20)
outer=s.Rational(20,1000);inner=s.Rational(10,1000);length=s.Rational(20,100);young=64*10**9;load=s.Integer(3)
difference=outer**4-inner**4
Iround=s.pi*difference/64;Isquare=difference/12
kr=3*young*Iround/length**3;ks=3*young*Isquare/length**3
dr=load/kr;ds=load/ks
check('Fourth-power section difference',difference==s.Rational(15,10**8))
check('Square second moment',Isquare==s.Rational(125,10**10))
check('Round stiffness',kr==56250*s.pi)
check('Square stiffness',ks==300000)
check('Round deflection millimetres',s.simplify(dr*1000)==s.Rational(4,75)/s.pi)
check('Square deflection millimetres',ds*1000==s.Rational(1,100))
check('Rounded round deflection',round(float(dr*1000),5)==0.01698)
check('Rounded square deflection',round(float(ds*1000),5)==0.01)
check('Missing cantilever factor-three round distractor',round(float(3*dr*1000),5)==0.05093)
check('Missing cantilever factor-three square distractor',float(3*ds*1000)==0.03)
check('Metres mislabelled as millimetres round distractor',round(float(dr),8)==0.00001698)
check('Metres mislabelled as millimetres square distractor',float(ds)==0.00001)
F,k=s.symbols('F k',positive=True);signal,bias=s.symbols('signal bias')
check('Flexure displacement sensitivity',s.diff(F/k,F)==1/k)
check('Common bias cancellation',s.expand(((signal+bias)-(-signal+bias))/2)==signal)
# Normalized vertical reaction weights are barycentric coordinates on a support triangle.
S=s.Matrix([[0,1,0],[0,0,1],[1,1,1]])
check('Interior projection admits nonnegative reactions',all(x>=0 for x in S.inv()*s.Matrix([s.Rational(1,4),s.Rational(1,4),1])))
check('Exterior projection requires a tensile contact',any(x<0 for x in S.inv()*s.Matrix([1,1,1])))
rng=random.Random(190202);maxres=0
for _ in range(300):
 o=rng.uniform(.01,.1);i=rng.uniform(0,.9)*o;ee=rng.uniform(1e9,2e11);ll=rng.uniform(.1,2);ff=rng.uniform(.1,20)
 kround=3*math.pi*ee*(o**4-i**4)/(64*ll**3);ksquare=ee*(o**4-i**4)/(4*ll**3)
 assert math.isclose(kround/ksquare,3*math.pi/16,rel_tol=1e-12)
 assert math.isclose((ff/kround)/(ff/ksquare),16/(3*math.pi),rel_tol=1e-12)
report={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'batchId':'W04-L19-v2','reviewerId':'define_robotics_data_contracts:L19-independent-reviewer','currentAuthorKeysSeen':False,'priorV1AuthorExposure':True,'newGapFirstAuthorExposure':False,'exactAssertionCount':len(checks),'exactAssertions':checks,'randomTrials':300,'randomChecksPerTrial':2,'beamValues':{'roundStiffnessNPerM':float(kr),'squareStiffnessNPerM':float(ks),'roundDeflectionMM':float(dr*1000),'squareDeflectionMM':float(ds*1000)},'testFixturesAreSynthetic':True,'coursePoolModified':False}
(ROOT/'audits/W04-L19-v2-independent-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['beamValues']));print('Assertions',len(checks))
