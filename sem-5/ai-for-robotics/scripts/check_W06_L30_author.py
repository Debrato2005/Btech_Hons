#!/usr/bin/env python3
"""Author algebra, exact source-code components, and pinned environment semantics.
This is not an independent answer review or proof of policy optimality.
"""
import json,math,inspect,hashlib,platform
from pathlib import Path
import numpy as np
import gymnasium as gym,gymnasium_robotics,mujoco
R=Path(__file__).resolve().parents[1];checks=[];out={}
def check(name,condition):
 assert bool(condition),name
 checks.append(name)
check('finite return extension',sum([2,-1,4])==5)
check('discounted return extension',2+.5*(-1)+.5**2*4==2.5)
check('constant infinite reward extension',math.isclose(sum(.9**k*2 for k in range(1000)),20))
check('Bellman expectation extension',1+.9*(.25*8+.75*4)==5.5)
check('Bellman max versus expectation',.5*max(10,0)+.5*max(0,10)==10 and max(.5*10+.5*0,.5*0+.5*10)==5)
check('Q update positive extension',math.isclose(2+.1*(1+.9*4-2),2.26))
check('Q update negative first sample',math.isclose(0+.1*(-.1+.95*0-0),-.01))
check('Q update negative subsequent sample',math.isclose(-.01+.1*(-.05+.95*(-.02)-(-.01)),-.0159))
check('terminal distinction extension',math.isclose(2+.5*(1-2),1.5) and math.isclose(2+.5*(1+.9*10-2),6))
# Exact source action map and state encoding.
NX=NY=NZ=8;BIN_SIZE=.04;N_ACTIONS=6
ACTION_MAP=np.array([[1,0,0,0],[-1,0,0,0],[0,1,0,0],[0,-1,0,0],[0,0,1,0],[0,0,-1,0]],dtype=np.float32)
Q=np.zeros((NX,NY,NZ,N_ACTIONS))
def get_state(obs):
 err=obs['desired_goal']-obs['achieved_goal']
 return tuple(np.clip(((err+.16)/BIN_SIZE).astype(int),0,7))
def state(e):return get_state({'desired_goal':np.array(e),'achieved_goal':np.zeros(3)})
check('source table dimensions and storage',Q.shape==(8,8,8,6) and Q.size==3072 and Q.nbytes==24576)
check('source action vectors',ACTION_MAP.shape==(6,4) and ACTION_MAP.dtype==np.float32 and np.all(ACTION_MAP[:,3]==0))
check('source negative-z action',ACTION_MAP[5].tolist()==[0,0,-1,0])
check('source zero-error state',state([0,0,0])==(4,4,4))
check('source interior state bins',state([-.15,.01,.15])==(0,4,7))
check('source clipping',state([-.3,0,.3])==(0,4,7))
check('source relative error sign',get_state({'desired_goal':np.array([.1,.2,.3]),'achieved_goal':np.array([.05,.21,.28])})==(5,3,4))
check('source argmax tie convention',np.argmax(np.zeros(6))==0)
check('source greedy action under negative values',np.argmax([-2,-3,-1,-4,-5,-6])==2)
check('epsilon greedy total greedy probability',math.isclose(1-.5+.5/6,7/12))
check('epsilon exploration can choose greedy',math.isclose(.5/6,1/12))
eps=.5;floor_first=None;logged={}
for n in range(1,5001):
 eps=max(.05,eps*.998)
 if eps==.05 and floor_first is None:floor_first=n
 if n%500==0:logged[n]=eps
check('epsilon first update',.5*.998==.499)
check('epsilon floor episode',floor_first==math.ceil(math.log(.1)/math.log(.998)))
check('epsilon printed checkpoints',f'{logged[500]:.3f}'=='0.184' and f'{logged[1000]:.3f}'=='0.068' and logged[1500]==.05)
out['epsilonFloorFirstCompletedEpisode']=floor_first
check('source logging episode indices',[ep for ep in range(5000) if (ep+1)%500==0]==list(range(499,5000,500)))
rewards=list(range(5000));smoothed=np.convolve(rewards,np.ones(50)/50,mode='valid')
check('source convolution length',len(smoothed)==4951)
check('source convolution first/last windows',np.isclose(smoothed[0],24.5) and np.isclose(smoothed[-1],4974.5))
check('logging last100 mean extension',np.mean(rewards[-100:])==4949.5)
check('grid resolution cost',12**3*6==10368 and (12/8)**3==3.375)
check('hardcoded clip leaves added bins unreachable',max(state([10,10,10]))==7)
check('dense reward zero distance is zero',-np.linalg.norm(np.zeros(3))==0)
# Installed official environment, controlled seeds added solely for semantics checks.
gym.register_envs(gymnasium_robotics);env=gym.make('FetchReachDense-v4');obs,info=env.reset(seed=30)
check('environment action space',env.action_space.shape==(4,) and env.action_space.dtype==np.float32)
check('environment observation goals',obs['achieved_goal'].shape==(3,) and obs['desired_goal'].shape==(3,))
check('FetchReach blocks gripper',env.unwrapped.block_gripper is True)
check('FetchReach success does not terminate',env.unwrapped.compute_terminated(obs['achieved_goal'],obs['achieved_goal'],{}) is False)
check('FetchReach zero-distance reward',env.unwrapped.compute_reward(obs['achieved_goal'],obs['achieved_goal'],{})==0)
check('FetchReach default limit',env.spec.max_episode_steps==50)
for i in range(50):
 obs,r,term,trunc,info=env.step(np.zeros(4,dtype=np.float32))
 if i<49:assert not term and not trunc
check('FetchReach truncates at step50',not term and trunc)
# Fourth action channel ignored: controlled equal initial conditions, otherwise identical actions.
env.reset(seed=77);a=env.step(np.array([0,0,0,1],dtype=np.float32))[0]
env.reset(seed=77);b=env.step(np.array([0,0,0,-1],dtype=np.float32))[0]
check('opposite gripper commands have same FetchReach outcome',all(np.allclose(a[k],b[k]) for k in a))
out['installedSources']={name:inspect.getsource(getattr(env.unwrapped,name)) for name in ['compute_reward','compute_terminated','_set_action']}
out['registerEnvSource']=inspect.getsource(gym.register_envs)
env.close()
# Independent implementations within author checks, explicitly not independent agent review.
rng=np.random.default_rng(30)
for _ in range(1000):
 old,r,nextv=rng.normal(size=3);alpha=rng.uniform();gamma=rng.uniform()
 assert np.isclose(old+alpha*(r+gamma*nextv-old),(1-alpha)*old+alpha*(r+gamma*nextv))
for _ in range(1000):
 e=rng.uniform(-1,1,size=3);s=state(e);manual=tuple(max(0,min(7,int((x+.16)/.04))) for x in e)
 assert s==manual
result={'status':'author checks passed; independent source/answer review pending','assertionCount':len(checks),'checks':checks,'randomUpdateIdentities':1000,'randomGridComparisons':1000,'versions':{'python':platform.python_version(),'numpy':np.__version__,'gymnasium':gym.__version__,'gymnasium_robotics':gymnasium_robotics.__version__,'mujoco':mujoco.__version__},'observations':out,'addedContext':'Controlled environment seeds, explicit arithmetic examples and comparison implementations are author tests, not source code or independent verification.'}
(R/'audits/W06-L30-author-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks),'checks + 2000 varied comparisons; epsilon floor',floor_first)
