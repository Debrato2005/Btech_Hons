"""Non-blind code/numerical challenge after an independent all-page visual pass.
No package installation, networking, or source/bank mutation. Own transcriptions.
"""
import contextlib,datetime,hashlib,io,json,math,sys
from pathlib import Path
import numpy as np
import pandas as pd
import scipy
from scipy.spatial.distance import euclidean
out=[]
def check(name,condition,details):
 assert bool(condition),(name,details)
 out.append({'name':name,'passed':True,'observed':details})
def raises(name,fn,kind):
 try:fn()
 except kind as e:check(name,True,{'errorType':type(e).__name__,'message':str(e)});return
 raise AssertionError(name+' did not raise '+kind.__name__)
q=np.array([.1,-.5,1.2,.8]);R=np.eye(3)
check('array_shape',q.shape==(4,) and q.ndim==1,{'shape':list(q.shape),'ndim':q.ndim})
check('identity',np.array_equal(R,[[1,0,0],[0,1,0],[0,0,1]]),R.tolist())
ns={'np':np,'R':R}
raises('literal_np_block_depth',lambda:exec('T=np.block([[R,np.zeros((3,1))],[np.zeros((1,3)),[[1]]]])\nq_offset=1',ns),ValueError)
check('block_stops_later_assignment','T' not in ns and 'q_offset' not in ns,sorted(k for k in ns if k!='__builtins__'))
T=np.block([[R,np.zeros((3,1))],[np.zeros((1,3)),np.array([[1]])]])
check('explicit_block_repair',np.array_equal(T,np.eye(4)),T.tolist())
o=q+np.array([.05]*4)
check('offset',np.allclose(o,[.15,-.45,1.25,.85]),o.tolist())
check('norm_rounded',f'{np.linalg.norm(q):.3f}'=='1.530',{'norm':float(np.linalg.norm(q)),'square':float(q@q),'sum':float(q.sum()),'mean':float(q.mean())})
check('norm_zero',np.linalg.norm(np.zeros(4))==0,0)
check('broadcast_compatible',np.array_equal(np.ones((2,1))+np.arange(3),[[1,2,3],[1,2,3]]),[2,3])
raises('broadcast_incompatible',lambda:np.ones((2,))+np.ones((3,)),ValueError)
check('noncontiguous_view_exists',not np.arange(10)[::2].flags.c_contiguous,'Stride-two view is not C contiguous; universal memory claim rejected.')
code="df['vel_j1'] = df['pos_j1'].diff() /\ndf.index.to_series().diff().dt.total_seconds()"
raises('literal_pandas_newline',lambda:compile(code,'source_p160','exec'),SyntaxError)
idx=pd.to_datetime([0,.02,.04,.06],unit='s');df=pd.DataFrame({'pos_j1':[0,.02,.06,.12],'pos_j2':[0,1,2,3]},index=idx)
df['vel_j1']=(df.pos_j1.diff()/df.index.to_series().diff().dt.total_seconds())
check('velocity_data',np.allclose(df.vel_j1.iloc[1:],[1,2,3]),df.vel_j1.iloc[1:].tolist())
check('velocity_first_undefined',pd.isna(df.vel_j1.iloc[0]),'First difference is NaN.')
r=df.vel_j1.rolling('50ms').mean()
check('rolling_window',np.isclose(r.iloc[-1],2),r.iloc[1:].tolist())
s=pd.Series([1.,2.,3.],index=pd.to_datetime([.01,.02,.06],unit='s'))
check('rolling_left_boundary_excluded',s.rolling('50ms').mean().iloc[-1]==2.5,s.rolling('50ms').mean().tolist())
check('summary_columns',list(df[['pos_j1','pos_j2']].describe().columns)==['pos_j1','pos_j2'],'Two selected position columns remain; describe returns separate summary.')
b=io.StringIO();df.to_csv(b);check('csv_write',b.getvalue().startswith(',pos_j1,pos_j2,vel_j1'),b.getvalue().splitlines()[0])
check('hdf_source_typo',hasattr(pd,'read_hdf') and not hasattr(pd,'read_hdf5'),{'read_hdf':hasattr(pd,'read_hdf'),'read_hdf5':hasattr(pd,'read_hdf5')})
check('zero_index', [1.2,1.5,.9,2.][2]==.9,.9)
check('tuple_set',isinstance((2.3,1.2,.5),tuple) and len({'chair','table','wall','chair'})==3,{'tuple':True,'distinctSetMembers':3})
function='def compute_distance(speed,time):\n    distance=speed*time\n    return distance\n'
ns={};exec(function,ns)
raises('function_name_mismatch',lambda:exec('d=compute_travel_distance(10,5)',ns),NameError)
check('repaired_distance',ns['compute_distance'](10,5)==50,50)
check('sqrt',math.sqrt(441)==21.,21.)
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
ns={'sensor_data':[2.,1.5,.8,.4,.2]};buf=io.StringIO()
with contextlib.redirect_stdout(buf):exec(loop,ns)
lines=buf.getvalue().splitlines()
check('sensor_trace_final',ns['reading']==.4 and ns['action']=='STOP',{'reading':ns['reading'],'action':ns['action']})
check('sensor_print_count',len(lines)==4,lines)
for value,action in [(-1,'STOP'),(0,'STOP'),(.499,'STOP'),(.5,'Reduce speed'),(.999,'Reduce speed'),(1.,'MOVE_FORWARD'),(2.,'MOVE_FORWARD')]:
 ns={'sensor_data':[value]}
 with contextlib.redirect_stdout(io.StringIO()):exec(loop,ns)
 check('sensor_boundary_'+str(value),ns['action']==action,ns['action'])
class Robot:
 def __init__(self,name,speed):self.name=name;self.speed=speed
 def move(self,time,action='moved'):
  distance=self.speed*time
  print(self.name,action,distance,'meters')
 def status(self):print('Robot:',self.name);print('Speed:',self.speed)
class MobileRobot(Robot):
 def move(self,time):
  distance=self.speed*time
  print(self.name,'drives',distance,'m')
class Drone(Robot):
 def move(self,time):super().move(time,'flies')
r=Robot('rover_1',1.5);buf=io.StringIO()
with contextlib.redirect_stdout(buf):r.status();ret=r.move(4)
check('robot_init',r.name=='rover_1' and r.speed==1.5,vars(r))
check('robot_print_and_return',buf.getvalue().splitlines()==['Robot: rover_1','Speed: 1.5','rover_1 moved 6.0 meters'] and ret is None,{'lines':buf.getvalue().splitlines(),'returnValue':ret})
buf=io.StringIO()
with contextlib.redirect_stdout(buf):MobileRobot('rover',1.5).move(3);Drone('quadrotor',3.5).move(3)
check('inheritance_and_super',buf.getvalue().splitlines()==['rover drives 4.5 m','quadrotor flies 10.5 meters'],buf.getvalue().splitlines())
pose=np.array([0,0]);goal=np.array([5,4]);motions=np.array([[1,1],[1,.5],[1,.5],[1,1]]);path=[pose]
for m in motions:pose=pose+m;path.append(pose)
check('distinct_pose_buffers',len({id(p) for p in path})==5,[p.tolist() for p in path])
path=np.array(path)
check('cumulative_path',np.array_equal(path,[[0,0],[1,1],[2,1.5],[3,2],[4,3]]),path.tolist())
check('path_shape_slicing',motions.shape==(4,2) and path.shape==(5,2) and np.array_equal(path[:,0],[0,1,2,3,4]) and np.array_equal(path[:,1],[0,1,1.5,2,3]),{'motions':list(motions.shape),'path':list(path.shape)})
check('goal_distance',f'{euclidean(path[-1],goal):.3f}'=='1.414',float(euclidean(path[-1],goal)))
L=np.linalg.norm(np.diff(path,axis=0),axis=1).sum()
check('polyline_length',f'{L:.3f}'=='5.064' and np.isclose(L,2*math.sqrt(2)+math.sqrt(5)),float(L))
check('distance_distractors',len({f'{x:.3f}' for x in [math.sqrt(2),L,math.sqrt(41),2]})==4,[f'{x:.3f}' for x in [math.sqrt(2),L,math.sqrt(41),2]])
check('length_distractors',len({f'{x:.3f}' for x in [L,math.sqrt(2),5,math.sqrt(41)]})==4,[f'{x:.3f}' for x in [L,math.sqrt(2),5,math.sqrt(41)]])
ns={'pose':np.array([0,0]),'motions':motions}
raises('integer_inplace_first_row',lambda:exec('pose += motions[0]',ns),np._core._exceptions._UFuncOutputCastingError)
check('failed_inplace_not_mutated',np.array_equal(ns['pose'],[0,0]),ns['pose'].tolist())
a=np.array([0.,0.]);refs=[a]
for m in motions:a+=m;refs.append(a)
check('float_inplace_alias_counterexample',all(np.array_equal(p,[4,3]) for p in refs),[p.tolist() for p in refs])
for increments in [np.zeros((0,2)),np.array([[0.,0.]]),np.array([[1.,0.],[-1.,0.]]),np.array([[-1.,-2.],[1.,2.]])]:
 pp=np.vstack([np.zeros((1,2)),np.cumsum(increments,axis=0)])
 length=np.linalg.norm(increments,axis=1).sum()
 check('path_boundary_'+str(len(out)),length+1e-12>=np.linalg.norm(pp[-1]),{'increments':increments.tolist(),'pathLength':float(length),'displacement':float(np.linalg.norm(pp[-1]))})
report={'reviewerId':'independent-reviewer-robotics-batches-v2','scope':'Non-blind L04 coverage/quality challenge; independently transcribed after visually inspecting source. Not a new blinded answer review.','runAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'versions':{'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__},'checks':out,'passed':len(out),'failed':0}
Path('audits/W01-L04-coverage-challenge-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':len(out),'failed':0,'versions':report['versions']}))
