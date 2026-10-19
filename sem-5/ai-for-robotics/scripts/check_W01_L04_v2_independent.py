#!/usr/bin/env python3
"""Source-pixel-derived checks for L04 v2. Does not read author keys or code."""
import contextlib,io,json,math,platform
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def record(name,value):checks.append({'name':name,'passed':True,'observed':value})
q=np.array([0.1,-0.5,1.2,0.8]);offset=q+np.array([0.05]*4)
assert np.allclose(offset,[0.15,-0.45,1.25,0.85]);record('equal_shape_elementwise_offset',offset.tolist())
bad="sentinel=True\ndf['vel_j1'] = df['pos_j1'].diff() /\ndf.index.to_series().diff().dt.total_seconds()\n"
namespace={}
try:exec(bad,namespace)
except SyntaxError as exc:assert 'sentinel' not in namespace;record('literal_source_newline_parse_error',{'type':type(exc).__name__,'no_prior_line_executed':True})
else:raise AssertionError('Expected SyntaxError')
df=pd.DataFrame({'timestamp':[0,.02,.04,.06],'pos_j1':[0,.02,.06,.12],'pos_j2':[0,.01,.03,.06]})
df['time']=pd.to_datetime(df['timestamp'],unit='s');df=df.set_index('time')
df['vel_j1']=df['pos_j1'].diff()/df.index.to_series().diff().dt.total_seconds()
assert pd.isna(df['vel_j1'].iloc[0]);assert np.allclose(df['vel_j1'].iloc[1:],[1,2,3]);record('finite_difference_velocity',{'initial':'NaN','remaining':df['vel_j1'].iloc[1:].tolist(),'units':'m/s'})
summary=df[['pos_j1','pos_j2']].describe();assert list(summary.columns)==['pos_j1','pos_j2'] and summary.loc['count'].tolist()==[4,4]
buf=io.StringIO();df.to_csv(buf);assert 'vel_j1' in buf.getvalue() and len(pd.read_csv(io.StringIO(buf.getvalue())))==4;record('summary_separate_from_dataframe_export',{'summary_shape':list(summary.shape),'export_rows':4})
try:exec('def compute_distance(speed,time):\n    distance=speed*time\n    return distance\nd=compute_travel_distance(10,5)\n',{})
except NameError as exc:record('undefined_function_call',type(exc).__name__)
else:raise AssertionError('Expected NameError')
def decision(readings):
 output=[];action=None
 for reading in readings:
  if reading<.5:action='STOP';break
  if reading<1:action='Reduce speed';output.append((reading,action));continue
  else:action='MOVE_FORWARD'
  output.append((reading,action))
 return action,output
assert decision([.5])[0]=='Reduce speed';assert decision([1])[0]=='MOVE_FORWARD';assert decision([2,1.5,.8,.4,.2])[0]=='STOP';record('conditional_boundary_trace',{'0.5':decision([.5])[0],'1.0':decision([1])[0],'original_printed_readings':decision([2,1.5,.8,.4,.2])[1]})
class Robot:
 def __init__(self,name,speed):self.name=name;self.speed=speed
 def move(self,time,action='moved'):
  distance=self.speed*time
  print(self.name,action,distance,'meters')
class MobileRobot(Robot):
 def move(self,time):print(self.name,'drives',self.speed*time,'m')
class Drone(Robot):
 def move(self,time):super().move(time,'flies')
buf=io.StringIO()
with contextlib.redirect_stdout(buf):result=Robot('rover_1',1.5).move(4)
assert result is None and buf.getvalue().strip()=='rover_1 moved 6.0 meters';record('printed_value_not_return_value',{'printed':buf.getvalue().strip(),'returned':None})
r1=MobileRobot('rover',1.5);r2=Drone('quadrotor',3.5);assert (r1.name,r1.speed,r2.name,r2.speed)==('rover',1.5,'quadrotor',3.5);record('inherited_initializer',{'names':[r1.name,r2.name],'speeds':[r1.speed,r2.speed]})
motions=np.array([[1,1],[1,.5],[1,.5],[1,1]]);pose=np.array([0,0]);path=[pose]
for motion in motions:pose=pose+motion;path.append(pose)
path=np.array(path);assert np.allclose(path,[[0,0],[1,1],[2,1.5],[3,2],[4,3]])
length=sum(math.hypot(*motion) for motion in motions);assert round(length,3)==5.064;assert math.isclose(euclidean(path[-1],[5,4]),math.sqrt(2));assert math.isclose(euclidean(path[0],path[-1]),5);record('piecewise_path_length_and_distances',{'path':path.tolist(),'length':length,'goal_remainder':float(euclidean(path[-1],[5,4])),'start_to_end_displacement':5.0})
pose=np.array([0,0]);assert motions.dtype.kind=='f' and pose.dtype.kind=='i'
try:pose+=motions[0]
except TypeError as exc:
 assert 'cast' in str(exc).lower() and np.array_equal(pose,[0,0]);record('in_place_integer_pose_float_motion',{'type':type(exc).__name__,'message':str(exc),'first_row':motions[0].tolist(),'first_row_dtype':str(motions[0].dtype)})
else:raise AssertionError('Expected output casting error')
report={'passed':True,'groups':len(checks),'pythonVersion':platform.python_version(),'numpyVersion':np.__version__,'pandasVersion':pd.__version__,'method':'Independent transcription from inspected source page pixels, before author keys or solution access. No external files or network are used by these checks.','checks':checks}
(ROOT/'audits/W01-L04-v2-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
