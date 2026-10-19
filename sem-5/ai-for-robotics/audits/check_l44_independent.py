"""Independent mathematical tests and explicitly source-reconstructed L44 runs."""
import os
os.environ['MPLBACKEND']='Agg'; os.environ['MPLCONFIGDIR']='/tmp/robotics-l44-mpl';os.environ['XDG_CACHE_HOME']='/tmp/robotics-l44-cache'
import numpy as np, matplotlib.pyplot as plt, json, pathlib, datetime, inspect, warnings, sys
from roboticstoolbox.mobile import LandmarkMap,Unicycle,RandomPath,RangeBearingSensor,EKF
import roboticstoolbox as rtb
checks=[]
def ck(n,c):
 assert bool(c),n
 checks.append(n)
def f(x,u):
 return x+np.array([u[0]*np.cos(x[2]),u[0]*np.sin(x[2]),u[1]])
def jac(x,u):
 t=x[2];d=u[0];return np.array([[1,0,-d*np.sin(t)],[0,1,d*np.cos(t)],[0,0,1]]),np.array([[np.cos(t),0],[np.sin(t),0],[0,1]])
def h(x,p):
 d=p-x[:2];return np.array([np.linalg.norm(d),np.arctan2(d[1],d[0])-x[2]])
def hx(x,p):
 a,b=p-x[:2];r=np.hypot(a,b);return np.array([[-a/r,-b/r,0],[b/r**2,-a/r**2,-1]])
def numjac(fun,x):
 eps=1e-6;return np.column_stack([(fun(x+np.eye(len(x))[i]*eps)-fun(x-np.eye(len(x))[i]*eps))/(2*eps) for i in range(len(x))])
ck('valid scan returns',360-4==356)
ck('round trip time of flight',np.isclose(3e8*40e-9/2,6))
ck('scanner stated rate product',5.5*360==1980)
ck('encoder distance',np.isclose(620*2*np.pi*.05/1000,.1947787445225672))
ck('gyro integration',30*2==60)
a=np.array([1.98,2.03,2.01,1.97,2.02,2.,1.99,2.04,1.96,2.01]);ck('wall mean and summed deviations',np.isclose(a.mean(),2.001) and np.isclose(((a-a.mean())**2).sum(),.00609))
ck('population versus sample standard deviation',np.isclose(a.std(),.0246779253585061) and np.isclose(a.std(ddof=1),.0260128173535044))
ck('discrete prediction and normalization',np.allclose(np.array([[.8,.3],[.2,.7]])@np.array([.6,.4]),[.6,.4]) and np.allclose(np.array([.15,.3])/.45,[1/3,2/3]))
ck('Gaussian at mean and determinant',np.isclose(1/np.sqrt(np.linalg.det(2*np.pi*np.diag([4,9]))),1/(12*np.pi)))
ck('symmetric not PSD',np.allclose(np.linalg.eigvalsh([[1,2],[2,1]]),[-1,3]))
ck('conditioned linear process and observation',2*1+3*2==8 and 3*2==6)
ck('linear propagated variance',2*.25*2+.5==1.5)
mu,P=2+2,.25+.5;K=P/(P+.3);postmu=mu+K*(5-mu);postP=(1-K)*P
ck('worked scalar prediction',mu==4 and P==.75)
ck('worked gain and posterior',np.isclose(K,5/7) and np.isclose(postmu,33/7) and np.isclose(postP,3/14))
ck('EKF mean versus exact transformed mean',2**2==4 and 2**2+.25==4.25)
ck('incremental world pose',np.allclose(f(np.array([1.,2.,np.pi/2]),np.array([2.,np.pi/2])),[1,4,np.pi]))
A,B=jac(np.array([0.,0.,np.pi/2]),np.array([2.,0.]));Pc=A@np.diag([.01,.04,.09])@A.T+B@np.diag([.0025,.0004])@B.T
ck('nonlinear covariance with mapped odometry noise',np.allclose(Pc,[[.37,0,-.18],[0,.0425,0],[-.18,0,.0904]]))
ck('differential drive average and half track',np.allclose([(.6+.2)/2,(.6-.2)/(.2*2)],[.4,1]))
ck('opposite wheel velocity pivot',np.allclose([(.4-.4)/2,(.4+.4)/(2*.2)],[0,2]))
V=np.diag([.02,np.deg2rad(.5)])**2;W=np.diag([.1,np.deg2rad(1)])**2;P0=np.diag([.05,.05,np.deg2rad(.5)])**2
ck('odometry and sensor covariance units',np.isclose(V[0,0],.0004) and np.isclose(V[1,1],(np.pi/360)**2) and np.isclose(W[1,1],(np.pi/180)**2))
ck('range and relative bearing',np.allclose(h(np.array([1.,2.,np.pi/2]),np.array([4.,6.])),[5,-.6435011087932844]))
ck('atan versus atan2 quadrant',np.isclose(np.arctan(-1),-np.pi/4) and np.isclose(np.arctan2(1,-1),3*np.pi/4))
ck('wrapped innovation shortest sign',(-179-179+180)%360-180==2)
H=hx(np.zeros(3),np.array([2.,0.]));Pb=np.diag([.1,.1,.01]);Wlocal=np.diag([.04,.01]);S=H@Pb@H.T+Wlocal;Kg=Pb@H.T@np.linalg.inv(S);m=Kg@np.array([.2,.1])
ck('local H and innovation covariance',np.allclose(H,[[-1,0,0],[0,-.5,-1]]) and np.allclose(S,np.diag([.14,.045])))
ck('local gain and posterior mean',np.allclose(Kg,[[-5/7,0],[0,-10/9],[0,-2/9]]) and np.allclose(m,[-1/7,-1/9,-1/45]))
ck('sensor visibility strict example', [r<=4 and abs(b)<=90 for r,b in [(4.5,-45),(3,45),(5,0),(3,120)]]==[False,True,False,False])
ck('segmentation strict threshold',[x>.2 for x in [.2,.21]]==[False,True])
ck('world derivatives',np.allclose([.4*np.cos(np.pi/2),.4*np.sin(np.pi/2),1],[0,.4,1]))
rng=np.random.default_rng(4401)
for k in range(1000):
 x=rng.uniform(-2,2,3);u=rng.uniform(-1,1,2);A,B=jac(x,u)
 assert np.allclose(A,numjac(lambda xx:f(xx,u),x),atol=1e-7)
 assert np.allclose(B,numjac(lambda uu:f(x,uu),u),atol=1e-7)
 p=x[:2]+rng.uniform(.5,4,2);assert np.allclose(hx(x,p),numjac(lambda xx:h(xx,p),x),atol=1e-7)
 C=rng.normal(size=(3,3));P=C@C.T+.05*np.eye(3);D=rng.normal(size=(2,2));VV=D@D.T+.02*np.eye(2);pred=A@P@A.T+B@VV@B.T
 assert np.linalg.eigvalsh(pred).min()>0
 H=hx(x,p);WW=np.diag(rng.uniform(.02,1,2));Kg=pred@H.T@np.linalg.inv(H@pred@H.T+WW);I=np.eye(3);pn=(I-Kg@H)@pred;pj=(I-Kg@H)@pred@(I-Kg@H).T+Kg@WW@Kg.T
 assert np.allclose(pn,pj) and np.linalg.eigvalsh(pn).min()>0 and np.linalg.eigvalsh(pred-pn).min()>-1e-9
for name in ['motion state Jacobian','motion noise Jacobian','measurement pose Jacobian','mapped covariance PSD','Joseph covariance equivalence and reduction']:ck('1000 varied '+name,True)
# This reproduces the literal clean-name failure without correcting it silently.
ns={'np':np,'Unicycle':Unicycle,'EKF':EKF}
try:exec('Vt=np.diag([0.02,np.deg2rad(0.5)])**2\nrobot=Unicycle(covar=Vt)\nE0=np.diag([0.05,0.05,np.deg2rad(0.5)])**2\nekf=EKF(robot=(robot,V),P0=E0)',ns)
except NameError as e: ck('literal clean namespace undefined V runtime',"'V'" in str(e))
else:raise AssertionError('source must raise NameError')
robot=ns['robot'];ck('q is property not method',isinstance(inspect.getattr_static(type(robot),'q'),property) and not callable(robot.q) and np.allclose(robot.q,[0,0,0]))
ck('ellipse default confidence',inspect.signature(EKF.plot_ellipse).parameters['confidence'].default==.95)
world=LandmarkMap(20,workspace=10,seed=0);ck('scalar map workspace exact bounds',np.allclose(world.workspace,[-10,10,-10,10]))
with warnings.catch_warnings(record=True) as ww:
 warnings.simplefilter('always');sensor=RangeBearingSensor(robot=robot,map=world,covar=W,range=4,angle=[-np.pi/2,np.pi/2],animate=True)
 ck('animate accepted and deprecated not TypeError',any(issubclass(w.category,DeprecationWarning) and 'plot' in str(w.message) for w in ww))
runs=[]
for known in [False,True]:
 world=LandmarkMap(20,workspace=10,seed=0) if known else None
 robot=Unicycle(covar=V,animation=None,seed=0);robot.control=RandomPath(workspace=world if known else 5,seed=0)
 if known:
  sensor=RangeBearingSensor(robot=robot,map=world,covar=W,range=4,angle=[-np.pi/2,np.pi/2],plot=False,seed=0)
  filt=EKF(robot=(robot,V),P0=P0,map=world,sensor=(sensor,W),animate=False)
 else:filt=EKF(robot=(robot,V),P0=P0,animate=False)
 filt.run(T=20,animate=False);steps=len(filt.history)
 ck(('known-map' if known else 'odometry')+' full 20 second actual runtime',steps==200 and filt.x_est.shape==(3,) and filt.P_est.shape==(3,3))
 ck(('known-map' if known else 'odometry')+' finite state and PSD covariance',np.isfinite(filt.x_est).all() and np.linalg.eigvalsh(filt.P_est).min()>-1e-10)
 plt.figure(figsize=(7,7))
 if known:world.plot()
 robot.plot_xy(color='blue');filt.plot_xy(color='red');filt.plot_ellipse(filled=True,facecolor='green',alpha=.3)
 mode='landmarks' if known else 'odometry';plt.title('L44 reviewer source reconstruction: '+mode);plt.savefig('audits/W09-L44-independent-'+mode+'.png',dpi=140);plt.close()
 updates=sum(getattr(s,'innov',None) is not None for s in filt.history)
 runs.append({'mode':mode,'seconds':20,'steps':steps,'measurementUpdates':updates,'finalTruePose':robot.q.tolist(),'finalEstimate':filt.x_est.tolist(),'finalCovariance':filt.P_est.tolist()})
report={'reviewerId':'independent-reviewer-robotics-batches-v2','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent pixel-derived mathematics and source-reconstructed RTB examples; no original notebook supplied, no author checker executed.','python':sys.version,'numpy':np.__version__,'roboticstoolbox':rtb.__version__,'passedGroups':len(checks),'checks':checks,'variedCases':5000,'runs':runs,'qualifications':['Supplied numpy and official toolbox imports.','Odometry reconstruction consistently passes Vt covariance rather than undefined screenshot V; literal failure separately executed.','Used explicit deterministic seed0 for robot, RandomPath, map and sensor.','Numerical run uses Agg, animation=None and plot=False; independent static blue/red/green plots created. No HTML animation execution claimed.','Fresh API probes independently confirm q property, 0.95 ellipse default, scalar workspace expansion and animate deprecation.']}
pathlib.Path('audits/W09-L44-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passedGroups':len(checks),'variedCases':5000,'runs':runs}))
