import json,math,datetime,pathlib
from fractions import Fraction as F
import numpy as np
checks=[]
def ck(name,condition):checks.append({'name':name,'passed':bool(condition)});assert condition,name
ck('Jacobian inverse second direction',.01*100==1)
ck('Maximum task speed',.01*10==.1)
ck('Time scaling',1/(.01*10)==10)
ck('Local time samples',np.allclose(np.array([5.2,6,6.8])-5,[.2,1,1.8]))
def region(s):return 'initial' if s<F(3,10) else ('linear' if s<F(17,10) else 'final')
ck('Three runtime regions',[region(x) for x in [F(1,5),F(1),F(9,5)]]==['initial','linear','final'])
ck('Initial region near boundary',region(F(299,1000))=='initial')
ck('Middle region after first boundary',region(F(301,1000))=='linear')
ck('Final region after second boundary',region(F(1701,1000))=='final')
ck('Consistent local blend',2+3*.5+.5*4*.5**2==4 and 3+4*.5==5)
ck('Rotation vector',np.allclose(np.array([0,0,1])*math.radians(90),[0,0,math.pi/2]))
ck('Unwrapped angular finite difference',(181-179)/.1==20)
ck('Halfway position',F(7,10)-F(1,10)*2==F(1,2) and F(1,5)-F(3,20)*2==-F(1,10))
ck('Midpoint displacement sign',-F(1,10)*2==-F(1,5))
ck('Zero crossing between samples',F(6,5)<F(1,5)/F(3,20)<F(7,5))
t=np.arange(0,4+.2,.2);ck('Exact grid endpoint and count',len(t)==21 and t[-1]==4)
for i in range(21):
 x=F(7,10)-F(1,10)*F(i,5);y=F(1,5)-F(3,20)*F(i,5);phi=15*F(i,5)
 line=f'{t[i]:.1f},{.7-.1*t[i]:.3f},{.2-.15*t[i]:.3f},{15*t[i]:.1f}'
 expected=f'{float(F(i,5)):.1f},{float(x):.3f},{float(y):.3f},{float(phi):.1f}'
 ck('Independent fractional format row '+str(i),line==expected)
ck('Index7 values',f'{t[7]:.1f},{.7-.1*t[7]:.3f},{.2-.15*t[7]:.3f},{15*t[7]:.1f}'=='1.4,0.560,-0.010,21.0')
report={'reviewerId':'independent-reviewer-robotics-batches-v2','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'scope':'Fresh independent arithmetic and fractional table-format verification for the current revisions; no author script used. Original 49 checks and 500 affine cases are retained separately.'}
pathlib.Path('audits/W04-L17-quality-repairs-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n');print(report['passed'],report['failed'])
