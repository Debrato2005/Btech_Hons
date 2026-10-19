"""Reviewer-authored local checks from visually transcribed source, not author tests."""
import contextlib,io,json,math,pathlib,sys
import numpy as np
import pandas as pd
from datetime import datetime,timezone
out=[]
def add(name,value):out.append({'check':name,'result':value})
def run(code,env=None):
 env={} if env is None else env;buf=io.StringIO()
 with contextlib.redirect_stdout(buf):exec(code,env)
 return env,buf.getvalue().splitlines()
q=np.array([.1,-.5,1.2,.8]);R=np.eye(3)
add('q dimensions and shape',[q.ndim,list(q.shape)])
try: np.block([[R,np.zeros((3,1))],[np.zeros((1,3)),[[1]]]])
except Exception as e: add('literal np.block',type(e).__name__+': '+str(e))
add('repaired np.block',np.block([[R,np.zeros((3,1))],[np.zeros((1,3)),np.array([[1]])]]).tolist())
add('offset',(q+np.array([.05]*4)).tolist());add('norm',float(np.linalg.norm(q)))
try:compile("df['vel_j1'] = df['pos_j1'].diff() /\ndf.index.to_series().diff().dt.total_seconds()",'<literal>','exec')
except Exception as e:add('literal pandas multiline',type(e).__name__+': '+str(e))
df=pd.DataFrame({'pos_j1':[0,.02,.06,.12]},index=pd.to_datetime([0,.02,.04,.06],unit='s'))
vel=df.pos_j1.diff()/df.index.to_series().diff().dt.total_seconds()
add('velocity',['NaN' if pd.isna(x) else float(x) for x in vel]);add('last 50ms mean',float(vel.rolling('50ms').mean().iloc[-1]));add('pandas HDF function spelling',{'read_hdf5':hasattr(pd,'read_hdf5'),'read_hdf':hasattr(pd,'read_hdf')})
add('types',[type(x).__name__ for x in ('mobile robot',1.5,4)])
add('indexed item',[1.2,1.5,.9,2][2]);add('set unique members',len({'chair','table','wall','chair'}))
fn='def compute_distance(speed,time):\n distance=speed*time\n return distance\n'
try:run(fn+'d=compute_travel_distance(10,5)')
except Exception as e:add('literal function-name mismatch',type(e).__name__+': '+str(e))
env,_=run(fn+'d=compute_distance(10,5)');add('repaired distance',env['d']);add('sqrt441',math.sqrt(441))
loop='''for reading in sensor_data:
 if reading < 0.5:
  action = "STOP"
  break
 if reading < 1.0:
  action = "Reduce speed"
  print("Distance:", reading, "Robot action:", action)
  continue
 else:
  action = "MOVE_FORWARD"
 print("Distance:", reading, "Robot action:", action)
print("Distance:", reading, "Final Robot action:", action)
'''
for data in ([2,1.5,.8,.4,.2],[.5],[1.]):
 env,lines=run(loop,{'sensor_data':data});add('sensor loop '+str(data),{'lines':lines,'finalReading':env['reading'],'finalAction':env['action']})
classes='''class Robot:
 def __init__(self,name,speed):
  self.name=name
  self.speed=speed
 def move(self,time,action="moved"):
  distance=self.speed*time
  print(self.name,action,distance,"meters")
 def status(self):
  print("Robot:",self.name)
  print("Speed:",self.speed)
class MobileRobot(Robot):
 def move(self,time):
  distance=self.speed*time
  print(self.name,"drives",distance,"m")
class Drone(Robot):
 def move(self,time):
  super().move(time,"flies")
'''
env,lines=run(classes+'robot1=Robot("rover_1",1.5)\nrobot1.status()\nresult=robot1.move(4)\nr1=MobileRobot("rover",1.5)\nr2=Drone("quadrotor",3.5)\nr1.move(3)\nr2.move(3)')
add('Robot classes',{'lines':lines,'moveReturn':env['result'],'name':env['robot1'].name,'speed':env['robot1'].speed})
result={'reviewerId':'reviewer-independent-python-modeling-20261019','executedAt':datetime.now(timezone.utc).isoformat(),'authorAnswersNotSeen':True,'versions':{'python':sys.version.split()[0],'numpy':np.__version__,'pandas':pd.__version__},'checks':out}
pathlib.Path(__file__).with_name('W01-L04-v1-independent-code-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
