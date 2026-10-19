#!/usr/bin/env python3
"""L30 pages 910–916 transcribed from pixels.
Explicit additions: headless plotting, persisted outputs/versions/timing, close().
Source loop has no seed and is not expected to reproduce the printed curve.
A compatibility-pinned MuJoCo run is recorded separately from unpinned failure.
"""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/robotics-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/robotics-cache')
import json,time,platform
from pathlib import Path
import gymnasium as gym
import gymnasium_robotics
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mujoco
R=Path(__file__).resolve().parents[1]
gym.register_envs(gymnasium_robotics)
env=gym.make('FetchReachDense-v4')
NX=NY=NZ=8
BIN_SIZE=0.04
N_ACTIONS=6
ACTION_MAP=np.array([[1,0,0,0],[-1,0,0,0],[0,1,0,0],[0,-1,0,0],[0,0,1,0],[0,0,-1,0]],dtype=np.float32)
Q=np.zeros((NX,NY,NZ,N_ACTIONS))
alpha=0.1
gamma=0.95
epsilon=0.5
def get_state(obs):
 err=obs['desired_goal']-obs['achieved_goal']
 return tuple(np.clip(((err+0.16)/BIN_SIZE).astype(int),0,7))
rewards=[]
started=time.monotonic();logs=[];termination_count=0;truncation_count=0
for ep in range(5000):
 obs,_=env.reset()
 s,total=get_state(obs),0
 for _ in range(50):
  a=np.random.randint(N_ACTIONS) if np.random.rand()<epsilon else np.argmax(Q[s])
  obs,r,terminated,truncated,_=env.step(ACTION_MAP[a])
  s_next=get_state(obs)
  Q[s][a]+=alpha*(r+gamma*np.max(Q[s_next])-Q[s][a])
  s,total=s_next,total+r
  if terminated or truncated:
   termination_count+=int(terminated);truncation_count+=int(truncated)
   break
 rewards.append(total)
 epsilon=max(0.05,epsilon*0.998)
 if (ep+1)%500==0:
  line=f'Ep {ep+1:5d} | Avg: {np.mean(rewards[-100:]):.2f} | ε: {epsilon:.3f}'
  print(line,flush=True);logs.append(line)
  (R/'audits/W06-L30-simulation-progress.json').write_text(json.dumps({'episodesCompleted':ep+1,'elapsedSeconds':time.monotonic()-started,'logs':logs,'status':'running' if ep+1<5000 else 'loop completed'},indent=2)+'\n')
smoothed=np.convolve(rewards,np.ones(50)/50,mode='valid')
plt.figure(figsize=(10,4));plt.plot(smoothed);plt.xlabel('Episode');plt.ylabel('Total reward (smoothed)');plt.title('Q-learning — FetchReachDense-v4');plt.grid(True)
plt.savefig(R/'audits/W06-L30-author-reproduced-curve.png');plt.close();env.close()
np.savez_compressed(R/'audits/W06-L30-author-simulation-arrays.npz',Q=Q,rewards=np.array(rewards),smoothed=smoothed)
result={'status':'5000 source-loop episodes executed; author reproduction, not independent verification','versions':{'python':platform.python_version(),'gymnasium':gym.__version__,'gymnasium_robotics':gymnasium_robotics.__version__,'mujoco':mujoco.__version__,'numpy':np.__version__},'addedContext':['MuJoCo pinned to 3.3.7 after unpinned 3.16.0 initialization failed; see initial-runtime-attempt.json.','Agg backend and savefig replace interactive show; no rendering or physical robot used.','Progress/output recording and environment close added; source actions, update, hyperparameters and episode counts unchanged.'],'seed':'None, matching source; exact score reproducibility is not claimed.','episodes':len(rewards),'stepsUpperBound':250000,'trueTerminations':termination_count,'timeLimitTruncations':truncation_count,'epsilonFinal':epsilon,'smoothedLength':len(smoothed),'elapsedSeconds':time.monotonic()-started,'logs':logs,'first100Mean':float(np.mean(rewards[:100])),'last100Mean':float(np.mean(rewards[-100:])),'optimalityProven':False}
(R/'audits/W06-L30-author-simulation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
