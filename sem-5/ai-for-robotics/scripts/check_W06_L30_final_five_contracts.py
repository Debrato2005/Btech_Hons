"""Independent reviewer checks for five final L30 repairs, before current-key access."""
from pathlib import Path
import json,datetime,hashlib,inspect,importlib.metadata
import numpy as np
import gymnasium as gym
import gymnasium_robotics
R=Path(__file__).resolve().parents[1]
res={'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'purpose':'Independent source-first checks; synthetic two-policy/value fixtures are not source data or course questions.','versions':{n:importlib.metadata.version(n) for n in ['gymnasium','gymnasium-robotics','mujoco','numpy']},'assertions':[]}
def chk(name,condition,detail=None):
 assert bool(condition),name
 res['assertions'].append({'name':name,'passed':True,'detail':detail})
A=np.array([-1.,3.]);B=np.array([.9,.9]);chk('Higher expected return can have one inferior realization',A.mean()>B.mean() and A[0]<B[0]);chk('Higher mean need not minimize variance',A.var()>B.var())
row=np.array([-.5,0.]);chk('Untried zero beats learned negative value',int(row.argmax())==1);row[0]=.1;chk('A later estimate can reverse prior ranking',int(row.argmax())==0)
e1=gym.make('FetchReachDense-v4',render_mode='rgb_array');e2=gym.make('FetchReachDense-v4')
try:
 reset1=e1.reset(seed=3075);reset2=e2.reset(seed=3075)
 chk('Reset returns observation and info',len(reset1)==2 and isinstance(reset1[1],dict));chk('Default wrapper limit is 50',e1.spec.max_episode_steps==50)
 term=[];trunc=[]
 for i in range(50):
  o1,r1,t1,tr1,info1=e1.step(np.array([.01,0,0,1.],dtype=np.float32));o2,r2,t2,tr2,info2=e2.step(np.array([.01,0,0,-1.],dtype=np.float32));term.append(bool(t1));trunc.append(bool(tr1))
  assert np.array_equal(o1['observation'],o2['observation']) and r1==r2
 chk('Opposite fourth-channel commands yield identical trajectories',True,{'steps':50,'seed':3075})
 chk('All true termination flags remain false',not any(term));chk('Only step 50 truncates',trunc==[False]*49+[True]);chk('Task configuration blocks gripper and contains no grasped object',e1.unwrapped.block_gripper and not e1.unwrapped.has_object)
 before=float(e1.unwrapped.data.time);qpos=e1.unwrapped.data.qpos.copy();frame=e1.render()
 chk('RGB rendering returns a three-channel frame',frame.ndim==3 and frame.shape[2]==3,list(frame.shape));chk('Rendering does not advance physics time',float(e1.unwrapped.data.time)==before);chk('Rendering does not alter joint positions',np.array_equal(qpos,e1.unwrapped.data.qpos))
 res['render']={'shape':list(frame.shape),'dtype':str(frame.dtype),'sha256':hashlib.sha256(frame.tobytes()).hexdigest(),'simulationTimeBeforeAndAfter':before}
 res['methods']=[]
 for name in ['compute_terminated','_set_action','render']:
  fn=getattr(type(e1.unwrapped),name);p=Path(inspect.getsourcefile(fn));lines,start=inspect.getsourcelines(fn);res['methods'].append({'method':name,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'firstLine':start,'source':''.join(lines)})
finally:e1.close();e2.close()
res['completedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();res['assertionCount']=len(res['assertions']);res['scriptSha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();(R/'audits/W06-L30-final-five-contracts-checks.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'assertions':res['assertionCount'],'render':res['render']}))
