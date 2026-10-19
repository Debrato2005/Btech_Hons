"""Independent L30 calculations and source-transcribed FetchReach experiment.
Written before keyed batch access. Seeds are explicitly added, not source seeds.
Run with /tmp/robotics-l30-venv/bin/python; --train executes all 5000 episodes.
"""
import argparse, json, math, hashlib, inspect, datetime
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name, value):
    assert value, name
    checks.append(name)
def state(error, width=.04):
    return tuple(np.clip(((np.asarray(error)+.16)/width).astype(int),0,7))
def update(q,r,g,m,a): return q+a*(r+g*m-q)
check('Undiscounted return',sum([2,-1,4])==5)
check('Discounted return',sum(x*.5**i for i,x in enumerate([2,-1,4]))==2.5)
check('Infinite geometric return',np.isclose(2/(1-.9),20))
check('Weighted Bellman backup',np.isclose(1+.9*(.25*8+.75*4),5.5))
check('Expectation of state-conditioned maxima',.5*max(10,0)+.5*max(0,10)==10)
check('Q update positive case',np.isclose(update(2,1,.9,4,.1),2.26))
check('Exploration can choose greedy action',np.isclose(.5+.5/6,7/12))
check('Dense Euclidean reward',np.isclose(-np.linalg.norm([.03,.04,0]),-.05))
check('Zero-distance reward',-np.linalg.norm([0,0,0])==0)
check('State/action count',8**3*6==3072)
check('Raw table storage',np.zeros((8,8,8,6)).nbytes==24576)
check('Three-component encoding',state(np.array([.10,.20,.30])-np.array([.05,.21,.28]))==(5,3,4))
check('Zero error encoding',state([0,0,0])==(4,4,4))
check('Clipped aliasing',state([-.5,.5,0])==state([-.9,.9,0]))
check('First argmax on tie',int(np.argmax(np.zeros(6)))==0)
check('Negative argmax',int(np.argmax([-2,-3,-1,-4,-5,-6]))==2)
check('First negative update',np.isclose(update(0,-.1,.95,0,.1),-.01))
check('Second negative update',np.isclose(update(-.01,-.05,.95,-.02,.1),-.0159))
check('True-terminal masking',np.isclose(update(2,1,.9,0,.5),1.5))
check('One epsilon decay',max(.05,.5*.998)==.499)
n=math.ceil(math.log(.1)/math.log(.998))
check('First epsilon floor crossing',n==1151 and .5*.998**1150>.05 and .5*.998**1151<.05)
check('Last-100 logging interval',list(range(500))[-100:]==list(range(400,500)))
check('Valid convolution count',len(np.convolve(np.zeros(5000),np.ones(50)/50,mode='valid'))==4951)
check('First valid window',np.isclose(np.convolve(np.arange(1,5001),np.ones(50)/50,mode='valid')[0],25.5))
check('Grid expansion',12**3*6==10368 and 12**3/8**3==3.375)
check('Hard clip bound independent of Q shape',max(state([999,999,999]))==7)
check('Narrower bins change zero-error saturation',state([0,0,0],.02)==(7,7,7))
check('Supplied transition arithmetic',state([-.03,0,0])==(3,4,4) and np.isclose(update(0,-.1,.95,0,.1),-.01))
check('Supplied transition reward is not FetchReach dense reward',not np.isclose(-np.linalg.norm([-.03,0,0]),-.1))
check('Non-greedy probability at floor',np.isclose(.05*5/6,1/24))
check('Optimistic zero values exceed negatives',0>-.01)
rng=np.random.default_rng(3030)
for _ in range(1000):
    q,r,m=rng.normal(size=3);alpha,gamma=rng.random(2)
    assert np.isclose(update(q,r,gamma,m,alpha),(1-alpha)*q+alpha*(r+gamma*m))
    e=rng.uniform(-2,2,3);s=state(e)
    assert len(s)==3 and all(0<=i<=7 for i in s)
    vals=rng.normal(size=6);assert vals[np.argmax(vals)]==max(vals)
result={'reviewer':'define_robotics_data_contracts:L30-independent-reviewer','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'assertions':checks,'randomizedCases':1000,'assertionsPerRandomizedCase':3,'numpyVersion':np.__version__,'priorL30KeyExposure':False}
if argparse.ArgumentParser().parse_known_args()[1]==['--train']:
    import gymnasium as gym, gymnasium_robotics, mujoco
    gym.register_envs(gymnasium_robotics)
    env=gym.make('FetchReachDense-v4')
    methods={}
    for cls in type(env.unwrapped).__mro__:
        for name in ['compute_reward','compute_terminated','compute_truncated','_set_action']:
            if name in cls.__dict__:
                methods[f'{cls.__module__}.{cls.__name__}.{name}']=inspect.getsource(cls.__dict__[name])
    methods['register_envs']=inspect.getsource(gym.register_envs)
    result['apiInspection']={'versions':{'gymnasium':gym.__version__,'gymnasium_robotics':gymnasium_robotics.__version__,'mujoco':mujoco.__version__},'maxEpisodeSteps':env.spec.max_episode_steps,'blockGripper':env.unwrapped.block_gripper,'hasObject':env.unwrapped.has_object,'methods':methods}
    # Same seed and initial conditions: fourth-channel changes have no effect.
    o,_=env.reset(seed=3031);a=env.step(np.array([0,0,0,1],dtype=np.float32));env.reset(seed=3031);b=env.step(np.array([0,0,0,-1],dtype=np.float32))
    check('Blocked gripper channel has no effect',np.allclose(a[0]['observation'],b[0]['observation']) and np.isclose(a[1],b[1]))
    Q=np.zeros((8,8,8,6));alpha=.1;gamma=.95;epsilon=.5
    actions=np.array([[1,0,0,0],[-1,0,0,0],[0,1,0,0],[0,-1,0,0],[0,0,1,0],[0,0,-1,0]],dtype=np.float32)
    np.random.seed(3030);rewards=[];stats=[];terminatedCount=truncatedCount=steps=successSteps=0
    for ep in range(5000):
        obs,_=env.reset(seed=3030 if ep==0 else None);s=state(obs['desired_goal']-obs['achieved_goal']);total=0
        for _ in range(50):
            a=np.random.randint(6) if np.random.rand()<epsilon else np.argmax(Q[s])
            obs,r,terminated,truncated,info=env.step(actions[a]);sn=state(obs['desired_goal']-obs['achieved_goal'])
            assert np.isclose(r,-np.linalg.norm(obs['desired_goal']-obs['achieved_goal']))
            Q[s][a]+=alpha*(r+gamma*np.max(Q[sn])-Q[s][a]);s,total=sn,total+r
            steps+=1;successSteps+=int(info.get('is_success',0));terminatedCount+=int(terminated);truncatedCount+=int(truncated)
            if terminated or truncated:break
        rewards.append(float(total));epsilon=max(.05,epsilon*.998)
        if (ep+1)%500==0:
            entry={'episode':ep+1,'meanLast100':float(np.mean(rewards[-100:])),'epsilon':epsilon};stats.append(entry);print(json.dumps(entry),flush=True)
    env.close()
    result['experiment']={'episodes':5000,'steps':steps,'numpySeed':3030,'initialResetSeed':3030,'laterResets':'None, advance seeded environment RNG','terminationCount':terminatedCount,'truncationCount':truncatedCount,'successfulSteps':successSteps,'checkpoints':stats,'finalQDataSha256':hashlib.sha256(Q.tobytes()).hexdigest(),'episodeTotalsSha256':hashlib.sha256(np.asarray(rewards).tobytes()).hexdigest(),'interpretation':'An independently seeded reproduction of the shown algorithm, not reproduction of the unseeded slide checkpoints, not an independent greedy evaluation, and not proof of convergence, grasping or safety.'}
result['scriptSha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
out=ROOT/'audits/W06-L30-contracts-independent-checks.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'assertions':len(checks),'randomizedCases':1000,'output':str(out),'experiment':result.get('experiment')},indent=2))
