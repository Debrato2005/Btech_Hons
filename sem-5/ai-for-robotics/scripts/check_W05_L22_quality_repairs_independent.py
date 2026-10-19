#!/usr/bin/env python3
"""Independent, source-derived revised L22 algebra checks; no author-check imports."""
import json,math,random,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]
checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
check('consistent SI torque',math.isclose(.4*3,1.2))
check('consistent SI back EMF',math.isclose(.4*10,4))
check('electromechanical conversion power',math.isclose((.4*3)*10,(.4*10)*3))
check('current slope decreases with positive speed increment',(12-2*3-.4*11)/.5<(12-2*3-.4*10)/.5)
check('load inertia lower endpoint',2+30**2*.01==11)
check('load inertia upper endpoint',6+30**2*.01==15)
check('servo command',math.isclose(-8*(-.1)-16*.2,-2.4))
check('physical force compensation',math.isclose(-8*(-.1)-16*.2-.1+.2,-2.3))
check('wrong servo velocity sign distractor',math.isclose(8*(-.1)-16*.2-.1+.2,-3.9))
check('shaft resonance angular',math.sqrt(400/1)==20)
check('half resonance cyclic',math.isclose(10/(2*math.pi),1.5915494309189535))
check('critical normalized gains',10**2==100 and 2*10==20)
check('hertz distractor exceeds resonance',10*2*math.pi>20)
check('final effective inertia',2+30**2*.01==11)
check('final effective damping',math.isclose(.2+30**2*.05,45.2))
check('no-load friction uses all motor torque',.1*20==2)
check('explicit retained state counts',[len(x) for x in [('theta','omega'),('theta','omega','i'),('theta','omega','i','z','zdot')]]==[2,3,5])
rng=random.Random(5222026)
for _ in range(1000):
 eta=rng.uniform(1.01,60);I=rng.uniform(.1,10);Im=rng.uniform(.001,.1);b=rng.uniform(.01,2);bm=rng.uniform(.001,.2);w=rng.uniform(-10,10);a=rng.uniform(-20,20)
 tm=Im*(eta*a)+bm*(eta*w)+(I*a+b*w)/eta
 assert math.isclose(eta*tm,(I+eta**2*Im)*a+(b+eta**2*bm)*w,rel_tol=1e-11,abs_tol=1e-11)
 assert math.isclose(tm,(Im+I/eta**2)*(eta*a)+(bm+b/eta**2)*(eta*w),rel_tol=1e-11,abs_tol=1e-11)
 assert math.isclose(.5*(I+eta**2*Im)*w*w,.5*(Im+I/eta**2)*(eta*w)**2,rel_tol=1e-11)
report={'reviewerId':'build_offline_study_interface:L22-independent-reviewer','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'namedChecks':len(checks),'checks':checks,'randomizedCases':1000,'assertionsPerRandomCase':3,'status':'passed','scope':'Independent algebra and declared state-count checks, not physical validation of a motor or controller.'}
(R/'audits/W05-L22-quality-repairs-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
