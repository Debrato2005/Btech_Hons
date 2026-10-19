import math,io,json,contextlib,platform
from pathlib import Path
import numpy as np
C=[]
def ck(n,a,e):assert a==e,(n,a,e);C.append({'name':n,'actual':a,'expected':e,'passed':True})
def compute_distance(speed,time):return speed*time
ck('repaired named function',compute_distance(10,5),50)
ck('distance zero time boundary',compute_distance(10,0),0)
ck('sqrt441 value',math.sqrt(441),21.0)
ck('sqrt441 returns float',isinstance(math.sqrt(441),float),True)
class Robot:
 def __init__(self,name,speed):self.name=name;self.speed=speed
 def status(self):print('Robot:',self.name);print('Speed:',self.speed)
b=io.StringIO()
with contextlib.redirect_stdout(b):ret=Robot('rover_1',1.5).status()
ck('status literal output',b.getvalue(),'Robot: rover_1\nSpeed: 1.5\n');ck('status no explicit return',ret,None)
pose=np.array([0,0]);path=[pose]
ck('initial list length',len(path),1);ck('initial pose reference',path[0] is pose,True)
for m in np.array([[1,1],[1,.5],[1,.5],[1,1]]):pose=pose+m;path.append(pose)
ck('source path coordinates',[x.tolist() for x in path],[[0,0],[1.0,1.0],[2.0,1.5],[3.0,2.0],[4.0,3.0]])
ck('source goal separate',[5,4]!=path[-1].tolist(),True)
# Pure state model for revised command sequences: no shell/package install is executed.
def trace(seq):
 active=False;op=[]
 for s in seq:
  if s=='activate':active=True
  elif s=='deactivate':active=False
  else:op.append((s,'vrenv' if active else 'outside'))
 return op,active
ck('correct install sequence',trace(['activate','install','deactivate']),([('install','vrenv')],False))
ck('install before activation',trace(['install','activate','deactivate']),([('install','outside')],False))
ck('install after deactivation',trace(['activate','deactivate','install']),([('install','outside')],False))
ck('uninstall is different operation',trace(['activate','uninstall','deactivate']),([('uninstall','vrenv')],False))
Path('audits/W01-L04-coverage-repairs-independent-computations.json').write_text(json.dumps({'scope':'Independent current-repair arithmetic/code and explicit virtual-environment state model; no package install, current SciPy API audit or physical hardware testing.','pythonVersion':platform.python_version(),'numpyVersion':np.__version__,'checks':C,'passed':len(C),'failed':0},indent=2)+'\n')
print('PASS',len(C))
