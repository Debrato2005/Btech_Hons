"""Independent targeted checks, not an author script; no question mutations."""
import os
os.environ.setdefault('MUJOCO_GL','egl')
import json,datetime,hashlib,inspect
from pathlib import Path
import numpy as np
import gymnasium as gym
import gymnasium_robotics as gr
import mujoco
from fractions import Fraction as F
root=Path(__file__).resolve().parents[1];rows=[]
def check(name,condition,detail):
 assert condition,(name,detail)
 rows.append({'name':name,'passed':True,'detail':detail})
check('Q010 targets',np.allclose([2+.9*4,2+.9*1],[5.6,2.9]),[5.6,2.9])
check('Q012 finite undiscounted return',sum([2,-1,4])==5,5)
Q=np.zeros((8,8,8,6));check('Q042 memory',Q.nbytes==24576,{'shape':list(Q.shape),'dtype':str(Q.dtype),'bytes':Q.nbytes})
def enc(error):return tuple(np.clip(((np.asarray(error)+.16)/.04).astype(int),0,7))
check('Q044 encoder',enc(np.array([.10,.20,.30])-np.array([.05,.21,.28]))==(5,3,4),[5,3,4])
check('Q053 TD update',np.isclose(.1*(-.1+.95*0),-.01),-.01)
check('Q055 update old entry',np.isclose(5+.1*(1+.9*7-5),5.23),5.23)
width=F(32,100)/12;bins=[min(11,max(0,int((e+F(16,100))/width))) for e in [F(-16,100),F(0),F(16,100)]]
check('Q068 exact boundary bins',bins==[0,6,11],{'width':str(width),'indices':bins})
a=int(np.argmax(Q[4,4,4]));ns=enc([-.03,0,0]);Q[4,4,4,a]+=.1*(-.03+.95*np.max(Q[ns])-Q[4,4,4,a]);check('Q071 complete trace',a==0 and ns==(3,4,4) and np.isclose(Q[4,4,4,0],-.003) and np.all(Q[ns]==0),{'action':a,'old_entry':float(Q[4,4,4,0]),'next_state':[int(x) for x in ns]})
steps=(20000-5000)*50;expect=steps*F(5,100)*F(5,6);check('Q076 additional budget',steps==750000 and expect==31250,{'steps':steps,'non_greedy_expected':int(expect),'exploration_expected':steps*.05})
rng=np.random.default_rng(301976)
for i in range(500):
 r,old,nxt=rng.uniform(-5,5,3);alpha,gamma=rng.random(2)
 assert np.isclose(old+alpha*(r+gamma*nxt-old),(1-alpha)*old+alpha*(r+gamma*nxt))
 for k in [2,6,9]:
  eps=rng.random();probs=np.full(k,eps/k);probs[0]+=1-eps
  assert np.isclose(probs[1:].sum(),eps*(k-1)/k)
check('500 varied TD and epsilon-greedy arithmetic cases',True,{'cases':500,'action_counts':[2,6,9]})
gym.register_envs(gr);env=gym.make('FetchReachDense-v4');base=env.unwrapped
check('Q037 and Q052 construction/default limit',env.spec.id=='FetchReachDense-v4' and env.spec.max_episode_steps==50,{'id':env.spec.id,'max_episode_steps':env.spec.max_episode_steps,'class':type(base).__name__})
check('Q070 gripper/object flags',base.block_gripper and not base.has_object,{'block_gripper':bool(base.block_gripper),'has_object':bool(base.has_object)})
implementation={}
for name in ['compute_terminated','compute_reward','_set_action']:
 fn=getattr(base,name);file=inspect.getsourcefile(fn);implementation[name]={'file':file,'fileSha256':hashlib.sha256(Path(file).read_bytes()).hexdigest(),'source':inspect.getsource(fn)}
results=[]
for seed in range(10):
 obs,info=env.reset(seed=seed);check(f'reset signature seed{seed}',isinstance(obs,dict) and isinstance(info,dict),{'keys':sorted(obs)})
 for t in range(50):
  action=np.zeros(4);action[t%3]=.2 if t%2 else -.2
  ret=env.step(action);assert len(ret)==5
  obs,r,term,trunc,info=ret
  assert not term and bool(trunc)==(t==49)
  assert np.isclose(r,-np.linalg.norm(obs['desired_goal']-obs['achieved_goal']))
 results.append({'seed':seed,'steps':50,'terminated':bool(term),'truncated':bool(trunc),'lastReward':float(r)})
check('500 actual simulation steps: negative distance and time limit',True,results)
obs,_=env.reset(seed=3019);base.goal=obs['achieved_goal'].copy();check('success is not termination',not base.compute_terminated(obs['achieved_goal'],base.goal,{}),{'zeroDistanceReward':float(base.compute_reward(base.goal,base.goal,{}))})
# Same initial simulator state and Cartesian actions; only gripper channel differs.
env2=gym.make('FetchReachDense-v4');maxdiff=0.
for seed in range(5):
 env.reset(seed=seed);env2.reset(seed=seed)
 for t in range(20):
  xyz=np.array([.1,-.1,0.]);r1=env.step(np.r_[xyz,-1.]);r2=env2.step(np.r_[xyz,1.])
  delta=float(np.max(np.abs(r1[0]['observation']-r2[0]['observation'])));maxdiff=max(maxdiff,delta);assert delta==0 and r1[1]==r2[1]
check('Q070 100 paired steps: fourth channel ignored',maxdiff==0,{'paired_steps':100,'max_observation_difference':maxdiff})
env.close();env2.close()
render={'attempted':True}
try:
 e=gym.make('FetchReachDense-v4',render_mode='rgb_array',width=320,height=240);e.reset(seed=30);before=e.unwrapped.data.qpos.copy();frame=e.render();after=e.unwrapped.data.qpos.copy()
 check('Q075 actual configured render',frame.shape==(240,320,3) and np.array_equal(before,after),{'shape':list(frame.shape),'physics_qpos_unchanged':True})
 from PIL import Image
 f=root/'audits/W06-L30-v2-independent-render.png';Image.fromarray(frame).save(f);render.update({'executed':True,'path':str(f.relative_to(root))});e.close()
except Exception as exc:render.update({'executed':False,'error':repr(exc),'qualification':'Official API checked, render not claimed executed if this fails.'})
report={'reviewerId':'independent-reviewer-robotics-batches-v2','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'versions':{'gymnasium':gym.__version__,'gymnasium_robotics':gr.__version__,'numpy':np.__version__,'mujoco':mujoco.__version__},'passed':len(rows),'checks':rows,'implementation':implementation,'render':render,'scope':'Targeted independent arithmetic/API checks and 700 actual simulator transitions. Not a reproduction of the full 5000-segment training run or exact unseeded slide curve.'}
(root/'audits/W06-L30-v2-independent-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':len(rows),'render':render,'report':'audits/W06-L30-v2-independent-checks.json'}))
