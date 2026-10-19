"""Author checks for L44: explicit code repairs and independent-of-print algebra, not independent review."""
from pathlib import Path
import os
os.environ.setdefault('MPLBACKEND','Agg');os.environ.setdefault('MPLCONFIGDIR','/tmp/l44-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/l44-cache')
import inspect,json,hashlib,datetime,platform,math,importlib.metadata,warnings
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal,chi2
from roboticstoolbox.mobile import Unicycle,RandomPath,EKF,RangeBearingSensor,LandmarkMap
R=Path(__file__).resolve().parents[1];checks=[]
def ck(name,predicate,result=None):
 assert predicate,name
 checks.append({'name':name,'passed':True,'result':result})
plain=lambda x:np.asarray(x).tolist()
# Literal snippets transcribed from pixels. Imports are the only supplied context.
code1397='''Vt = np.diag([0.02, np.deg2rad(0.5)]) ** 2
robot = Unicycle(covar=Vt, animation="car")
robot.control = RandomPath(workspace=5)
E0 = np.diag([0.05, 0.05, np.deg2rad(0.5)]) ** 2
ekf = EKF(robot=(robot, V), P0=E0)
ekf.run(T=20)
html = ekf.run_animation(T=20, format="html")
HTML(html)
robot.plot_xy(color="b")
ekf.plot_xy(color="r")
ekf.plot_ellipse(filled=True, facecolor="g", alpha=0.3)
'''
code1400='''map = LandmarkMap(20, workspace=10)
V = np.diag([0.02, np.deg2rad(0.5)]) ** 2
robot = Unicycle(covar=V, animation="car")
robot.control = RandomPath(workspace=map)
W = np.diag([0.1, np.deg2rad(1)]) ** 2
sensor = RangeBearingSensor(robot=robot, map=map, covar=W,
    angle=[-np.pi/2, np.pi/2], range=4, animate=True)
P0 = np.diag([0.05, 0.05, np.deg2rad(0.5)]) ** 2
ekf = EKF(robot=(robot, V), P0=P0, map=map, sensor=(sensor, W))
ekf.run(T=20)
map.plot()
robot.plot_xy(color="b")
ekf.plot_xy(color="r")
ekf.plot_ellipse()
'''
contexts=dict(np=np,Unicycle=Unicycle,RandomPath=RandomPath,EKF=EKF,RangeBearingSensor=RangeBearingSensor,LandmarkMap=LandmarkMap)
errors={};literal_results={}
for page,code in [(1397,code1397),(1400,code1400)]:
 (R/f'sources/supplemental/L44-p{page}-literal.py').write_text(code)
 try:
  ctx=dict(contexts)
  with warnings.catch_warnings(record=True) as ws:
   warnings.simplefilter('always');exec(code,ctx)
  literal_results[str(page)]={'completed':True,'steps':len(ctx['ekf'].history),'warnings':[str(w.message) for w in ws]}
 except Exception as e:errors[str(page)]={'type':type(e).__name__,'message':str(e)}
 plt.close('all')
ck('Literal p1397 undefined V',errors['1397']['type']=='NameError' and "'V'" in errors['1397']['message'],errors['1397'])
ck('Literal p1400 runs with deprecated animate alias',literal_results['1400']['completed'] and literal_results['1400']['steps']==200 and any('deprecated' in w for w in literal_results['1400']['warnings']),literal_results['1400'])
# Source snapshots bind pinned implementation behavior, not the original lecture notebook.
snapshots={}
for cls in [Unicycle,RangeBearingSensor,EKF,LandmarkMap]:
 src=Path(inspect.getfile(cls));dest=R/f'sources/supplemental/L44-rtb-{src.name}';dest.write_bytes(src.read_bytes());snapshots[cls.__name__]={'path':str(dest.relative_to(R)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
V=np.diag([.02,np.deg2rad(.5)])**2;P0=np.diag([.05,.05,np.deg2rad(.5)])**2;W=np.diag([.1,np.deg2rad(1)])**2
ck('Angular standard deviations converted then squared',np.allclose(np.diag(V),[.0004,(np.pi/360)**2]) and np.allclose(np.diag(W),[.01,(np.pi/180)**2]),{'V':plain(V),'P0':plain(P0),'W':plain(W)})
map_=LandmarkMap(20,workspace=10);ck('Scalar workspace bounds',np.allclose(map_.workspace,[-10,10,-10,10]),plain(map_.workspace))
robot=Unicycle(covar=V);robot.control=RandomPath(workspace=5);ekf=EKF(robot=(robot,V),P0=P0,animate=False);ekf.run(T=20)
odom={'steps':len(ekf.history),'trueFinal':plain(robot.q),'estimatedFinal':plain(ekf.x_est),'PFinal':plain(ekf.P_est)}
ck('Repaired odometry run',len(ekf.history)==200 and np.isfinite(ekf.x_est).all(),odom)
fig,ax=plt.subplots();robot.plot_xy(color='b',label='True');ekf.plot_xy(color='r',label='Estimate');ekf.plot_ellipse(filled=True,facecolor='g',alpha=.3);ax.set_title('L44 repaired odometry-only run, RTB 1.4.4');ax.legend();fig.savefig(R/'audits/W09-L44-odometry-author.png',dpi=140);plt.close(fig)
robot2=Unicycle(covar=V);robot2.control=RandomPath(workspace=map_);sensor=RangeBearingSensor(robot=robot2,map=map_,covar=W,angle=[-np.pi/2,np.pi/2],range=4,plot=False)
ekf2=EKF(robot=(robot2,V),P0=P0,map=map_,sensor=(sensor,W),animate=False);ekf2.run(T=20)
fused={'steps':len(ekf2.history),'trueFinal':plain(robot2.q),'estimatedFinal':plain(ekf2.x_est),'PFinal':plain(ekf2.P_est)}
ck('Repaired known-landmark run',len(ekf2.history)==200 and np.isfinite(ekf2.x_est).all(),fused)
fig,ax=plt.subplots();map_.plot();robot2.plot_xy(color='b',label='True');ekf2.plot_xy(color='r',label='Estimate');ekf2.plot_ellipse(filled=True,facecolor='g',alpha=.3);ax.set_title('L44 repaired known-landmark run, RTB 1.4.4');ax.legend();fig.savefig(R/'audits/W09-L44-landmarks-author.png',dpi=140);plt.close(fig)
ck('q is a property',isinstance(Unicycle.q,property));ck('Ellipse default confidence',inspect.signature(EKF.plot_ellipse).parameters['confidence'].default==.95)
ck('Unicycle wheel-speed difference convention',np.allclose(Unicycle(W=2).deriv([0,0,0],[3,4],limits=False),[3,0,2]))
ck('LiDAR time of flight',math.isclose(3e8*40e-9/2,6),6)
ck('Illustrative scan rate',360*5.5==1980 and math.isclose(1/5.5,.1818181818),{'samplesPerSecond':1980,'secondsPerScan':1/5.5})
ck('Encoder travel',math.isclose(2*np.pi*.05*620/1000,.1947787445225672),2*np.pi*.05*620/1000)
ck('Gyro integration',30*2==60,60)
a=np.array([1.98,2.03,2.01,1.97,2.02,2,1.99,2.04,1.96,2.01]);ck('Ten wall measurements',math.isclose(a.mean(),2.001),{'mean':a.mean(),'populationVariance':a.var(),'populationStd':a.std(),'sampleStd':a.std(ddof=1)})
prior=np.array([.6,.4]);T=np.array([[.8,.3],[.2,.7]]);pred=T@prior;like=np.array([.25,.75]);unn=pred*like;post=unn/unn.sum();ck('Discrete Bayes prediction and correction',np.allclose(pred,[.6,.4]) and np.allclose(post,[1/3,2/3]),{'prediction':plain(pred),'unnormalized':plain(unn),'normalizer':1/unn.sum(),'posterior':plain(post)})
ck('Gaussian center density',math.isclose(multivariate_normal(mean=[0,0],cov=np.diag([4,9])).pdf([0,0]),1/(12*np.pi)),1/(12*np.pi))
ck('Covariance positive semidefinite counterexample',np.linalg.eigvalsh([[1,2],[2,1]])[0]<0,plain(np.linalg.eigvalsh([[1,2],[2,1]])))
ck('Scalar Kalman source example',np.allclose([.75/1.05,4+.75/1.05,(1-.75/1.05)*.75],[5/7,33/7,3/14]),{'gain':5/7,'mean':33/7,'variance':3/14})
def motion(q,u,v=np.zeros(2)):
 x,y,t=q;d,dt=u;vd,vt=v;return np.array([x+(d+vd)*np.cos(t),y+(d+vd)*np.sin(t),t+dt+vt])
def fx(q,u):
 t=q[2];d=u[0];return np.array([[1,0,-d*np.sin(t)],[0,1,d*np.cos(t)],[0,0,1]])
def fv(q):return np.array([[np.cos(q[2]),0],[np.sin(q[2]),0],[0,1]])
q=np.array([1.,2.,np.pi/2]);u=np.array([2.,np.pi/2]);ck('Translate then rotate',np.allclose(motion(q,u),[1,4,np.pi]),plain(motion(q,u)))
predP=fx(q,u)@np.diag([.01,.04,.09])@fx(q,u).T+fv(q)@np.diag([.0025,.0004])@fv(q).T
ck('Odometry covariance example',np.allclose(predP,[[.37,0,-.18],[0,.0425,0],[-.18,0,.0904]]),plain(predP))
def obs(q,p):
 dx,dy=np.array(p)-np.array(q[:2]);return np.array([np.hypot(dx,dy),((np.arctan2(dy,dx)-q[2]+np.pi)%(2*np.pi))-np.pi])
def hx(q,p):
 dx,dy=np.array(p)-np.array(q[:2]);r=np.hypot(dx,dy);return np.array([[-dx/r,-dy/r,0],[dy/r**2,-dx/r**2,-1]])
ck('Range bearing model',np.allclose(obs([1,2,np.pi/2],[4,6]),[5,-.6435011087932843]),plain(obs([1,2,np.pi/2],[4,6])))
ck('Corrected measurement Jacobian',np.allclose(hx([1,2,np.pi/2],[4,6]),[[-.6,-.8,0],[.16,-.12,-1]]),plain(hx([1,2,np.pi/2],[4,6])))
ck('Quadrant-safe bearing',math.isclose(obs([0,0,0],[-1,1])[1],3*np.pi/4),3*np.pi/4)
ck('Wrapped angular residual',math.isclose(((np.deg2rad(-179)-np.deg2rad(179)+np.pi)%(2*np.pi))-np.pi,np.deg2rad(2)))
P=np.diag([.1,.1,.01]);H=hx([0,0,0],[2,0]);Rm=np.diag([.04,.01]);S=H@P@H.T+Rm;K=np.linalg.solve(S,H@P).T;mu=K@np.array([.2,.1]);Pc=(np.eye(3)-K@H)@P
ck('Integrated landmark correction',np.allclose(mu,[-1/7,-1/9,-1/45]) and np.all(np.linalg.eigvalsh(Pc)>0),{'H':plain(H),'S':plain(S),'K':plain(K),'mean':plain(mu),'covariance':plain(Pc)})
ck('95 percent positional ellipse radius',math.isclose(np.sqrt(chi2.ppf(.95,2)),2.44774683068,rel_tol=1e-10),np.sqrt(chi2.ppf(.95,2)))
ck('Scalar conditional transition',np.allclose([2*1+3*2,.4],[8,.4]))
ck('Scalar conditional observation',np.allclose([3*2,.09],[6,.09]))
ck('Scalar covariance scaling',math.isclose(2*.25*2+.5,1.5))
ck('Nonlinear EKF versus exact second moment',2**2==4 and 2**2+.25==4.25)
ck('Differential drive rates',np.allclose([(.6+.2)/2,(.6-.2)/(2*.2)],[.4,1]))
ck('Pure opposite-wheel turn',np.allclose([(.2-.2)/2,(.2-(-.2))/(2*.2)],[0,1]))
ck('World velocity projection',np.allclose([.4*np.cos(np.pi/2),.4*np.sin(np.pi/2),1],[0,.4,1]))
ck('Source strict segmentation threshold',[g>.2 for g in [.2,.21]]==[False,True])
ck('Added sensor visibility example',[(r<=4 and -np.pi/2<=a<=np.pi/2) for r,a in [(3,np.pi/4),(5,0),(3,2*np.pi/3),(4.5,-np.pi/4)]]==[True,False,False,False])
# Finite-difference and covariance checks for 1000 varied cases, all separated from source claims.
rng=np.random.default_rng(441019);comparisons=0;eps=1e-6
for _ in range(1000):
 q=rng.uniform([-5,-5,-2],[5,5,2]);u=rng.uniform([-1,-.5],[1,.5]);p=q[:2]+rng.uniform([1,1],[5,5])
 fd=np.column_stack([(motion(q+np.eye(3)[i]*eps,u)-motion(q-np.eye(3)[i]*eps,u))/(2*eps) for i in range(3)])
 assert np.allclose(fd,fx(q,u),atol=2e-8);comparisons+=1
 fdv=np.column_stack([(motion(q,u,np.eye(2)[i]*eps)-motion(q,u,-np.eye(2)[i]*eps))/(2*eps) for i in range(2)])
 assert np.allclose(fdv,fv(q),atol=2e-8);comparisons+=1
 fdh=np.column_stack([(obs(q+np.eye(3)[i]*eps,p)-obs(q-np.eye(3)[i]*eps,p))/(2*eps) for i in range(3)])
 assert np.allclose(fdh,hx(q,p),atol=2e-8);comparisons+=1
 assert np.allclose(sensor.Hx(q,p),hx(q,p)) and np.allclose(sensor.h(q,p),obs(q,p));comparisons+=1
 A=rng.normal(size=(3,3));P=A@A.T+.01*np.eye(3);H=hx(q,p);S=H@P@H.T+Rm;K=np.linalg.solve(S,H@P).T;C=(np.eye(3)-K@H)@P;J=(np.eye(3)-K@H)@P@(np.eye(3)-K@H).T+K@Rm@K.T
 assert np.allclose(C,J,atol=1e-10) and np.linalg.eigvalsh(C).min()>-1e-9;comparisons+=1
ck('Varied checks',comparisons==5000,{'trials':1000,'comparisons':comparisons})
report={'authorId':'build_offline_study_interface:L44-author','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentReview':False,'literalSourcePages':[1397,1400],'literalErrors':errors,'literalResults':literal_results,'declaredRepairs':['Provide numpy and Robotics Toolbox imports.','p1397 use Vt consistently, supplying it to EKF instead of undefined V.','p1400 literal animate=True is supported but deprecated in RTB 1.4.4; use plot=False only for the separate headless numerical reconstruction.','Disable robot/EKF animation and omit the HTML display sequence; run numerical simulation and save static plots.','Do not reproduce a historical random trajectory as exact notebook output; pin RTB 1.4.4 default seed behavior.'],'versions':{p:importlib.metadata.version(p) for p in ['roboticstoolbox-python','spatialmath-python','numpy','scipy','matplotlib']},'snapshots':snapshots,'checks':checks,'namedChecks':len(checks),'variedComparisons':comparisons,'odometryRun':odom,'landmarkRun':fused,'allPass':True}
(R/'audits/W09-L44-author-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'variedComparisons':comparisons,'literalErrors':errors,'allPass':True}))
