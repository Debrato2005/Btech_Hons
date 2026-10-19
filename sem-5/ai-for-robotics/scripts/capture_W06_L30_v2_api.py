"""Record item-addressable API evidence for L30 source qualifications."""
from pathlib import Path
import inspect,hashlib,json,datetime,importlib.metadata as md
import gymnasium as gym
import gymnasium_robotics
import numpy as np
from gymnasium_robotics.envs.fetch.reach import MujocoFetchReachEnv
from gymnasium_robotics.envs.fetch.fetch_env import MujocoFetchEnv
from gymnasium_robotics.envs.robot_env import BaseRobotEnv
R=Path(__file__).resolve().parents[1]
def binding(obj,description):
 p=Path(inspect.getfile(obj));_,line=inspect.getsourcelines(obj)
 return {'packageRelativePath':str(p).split('site-packages/')[-1],'fileSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'startLine':line,'symbol':obj.__qualname__,'observation':description}
sections={
'registration':{'primaryUrl':'https://gymnasium.farama.org/api/registry/','bindings':[binding(gym.register_envs,'Compatibility helper has no runtime registration body.'),binding(gym.make,'Constructs the selected registered environment.')],'observation':'Importing gymnasium_robotics installs registrations; gym.make constructs the selected instance. The register_envs helper is a no-op in Gymnasium 1.4.0.'},
'reachFlags':{'primaryUrl':'https://robotics.farama.org/envs/fetch/reach/','bindings':[binding(BaseRobotEnv.compute_terminated,'Returns false for the continuing task.')],'observation':'FetchReachDense-v4 inherits the continuing-task termination behavior; its registration applies the default 50-step TimeLimit wrapper.'},
'reachAction':{'primaryUrl':'https://robotics.farama.org/envs/fetch/reach/','bindings':[binding(MujocoFetchReachEnv.__init__,'Constructs the reach task with block_gripper enabled.'),binding(MujocoFetchEnv._set_action,'The inherited action preparation zeroes blocked gripper control.')],'observation':'This reach task has no manipulated object and ignores the fourth action channel. Reaching is not a stable-grasp objective.'},
'denseReward':{'primaryUrl':'https://robotics.farama.org/envs/fetch/reach/','bindings':[binding(MujocoFetchEnv.compute_reward,'Dense reward is negative Euclidean distance between achieved and desired goals.')],'observation':'Error (-0.03,0,0) metres therefore yields dense reward -0.03, not -0.1.'},
 'timeLimits':{'primaryUrl':'https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/','observation':'External collection truncation and a true finite-horizon task terminal condition are distinct; the continuing-task update retains successor bootstrap at the external limit.'}}
env=gym.make('FetchReachDense-v4');obs,info=env.reset(seed=30002)
assert env.spec.max_episode_steps==50 and env.unwrapped.block_gripper
flags=[]
for i in range(50):
 obs,r,terminated,truncated,info=env.step(np.zeros(4,np.float32));flags.append([bool(terminated),bool(truncated)])
assert all(not t for t,tr in flags) and not any(tr for t,tr in flags[:-1]) and flags[-1][1]
r=float(env.unwrapped.compute_reward(np.array([.03,0,0]),np.zeros(3),{}));assert np.isclose(r,-.03)
sections['reachFlags']['runtimeCheck']={'seed':30002,'steps':50,'terminatedCount':sum(t for t,tr in flags),'truncatedCount':sum(tr for t,tr in flags),'lastFlags':flags[-1],'envMaxEpisodeSteps':env.spec.max_episode_steps}
sections['denseReward']['runtimeCheck']={'suppliedDistance':.03,'reward':r}
env.close()
record={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'versions':{p:md.version(p) for p in ['gymnasium','gymnasium-robotics','mujoco','numpy']},'sections':sections,'relatedRunPath':'audits/W06-L30-author-simulation.json','relatedRunSha256':hashlib.sha256((R/'audits/W06-L30-author-simulation.json').read_bytes()).hexdigest(),'role':'Author qualification evidence, not independent verification; no lecture page silently corrected.'}
(R/'audits/W06-L30-v2-api-evidence.json').write_text(json.dumps(record,indent=2)+'\n');print('API evidence saved; 50-step and dense-reward checks passed.')
