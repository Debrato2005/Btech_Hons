"""Reviewer reconstruction from source pixels, not original notebook or author script."""
import os
os.environ['MPLBACKEND']='Agg';os.environ['MPLCONFIGDIR']='/tmp/l45-reviewer-mpl';os.environ['XDG_CACHE_HOME']='/tmp/l45-reviewer-cache'
import numpy as np, json, pathlib, hashlib, datetime, sys, ast
from scipy.ndimage import binary_erosion
import matplotlib.pyplot as plt
from roboticstoolbox.mobile import LandmarkMap, Unicycle, RandomPath, RangeBearingSensor, EKF
import roboticstoolbox as rtb
checks=[]
def ck(name, cond):
 assert bool(cond),name
 checks.append(name)
def g(v,z):
 a=v[2]+z[1];return v[:2]+z[0]*np.array([np.cos(a),np.sin(a)])
def gj(v,z):
 a=v[2]+z[1];r=z[0]
 return np.array([[1,0,-r*np.sin(a)],[0,1,r*np.cos(a)]]),np.array([[np.cos(a),-r*np.sin(a)],[np.sin(a),r*np.cos(a)]])
def h(v,p):
 d=p-v[:2];return np.array([np.linalg.norm(d),np.arctan2(d[1],d[0])-v[2]])
def hp(v,p):
 d=p-v[:2];r=np.linalg.norm(d);return np.array([d/r,[-d[1]/r**2,d[0]/r**2]])
def numjac(f,x):
 eps=1e-6;return np.column_stack([(f(x+np.eye(len(x))[i]*eps)-f(x-np.eye(len(x))[i]*eps))/(2*eps) for i in range(len(x))])
ck('inverse observation world frame',np.allclose(g(np.array([2.,3.,np.pi/2]),np.array([4.,-np.pi/2])),[6,3]))
Gv,Gz=gj(np.zeros(3),np.array([4.,0.]));ck('inverse Jacobian and covariance',np.allclose(Gz,np.diag([1,4])) and np.allclose(Gz@np.diag([.01,.0004])@Gz.T,np.diag([.01,.0064])))
ck('known pose does not zero derivative',np.array_equal(Gv[:,:2],np.eye(2)))
ck('quadrant and wrap',np.isclose(np.degrees(np.arctan2(1,-1)),135) and np.isclose((-179-179+180)%360-180,2))
ck('range bearing observation derivative',np.allclose(hp(np.zeros(3),np.array([3.,4.])),[[.6,.8],[-.16,.12]]))
P=np.diag([.5,1]);H=np.array([[-1.,1.]]);R=.25;S=H@P@H.T+R;K=P@H.T/S.item();I=np.eye(2);Pnew=(I-K@H)@P;Pj=(I-K@H)@P@(I-K@H).T+K*R@K.T
ck('1D innovation variance and gain',np.isclose(S.item(),1.75) and np.allclose(K[:,0],[-2/7,4/7]))
ck('1D mean correction',np.allclose(np.array([3.,5.])+K[:,0]*.3,[102/35,181/35]))
ck('1D covariance Joseph agreement and printed conflict',np.allclose(Pnew,Pj) and np.allclose(Pnew,[[5/14,2/7],[2/7,3/7]]) and not np.isclose(Pnew[0,1],.143))
ck('posterior covariance PSD and reduced variance',np.linalg.eigvalsh(Pnew).min()>0 and np.all(np.diag(Pnew)<np.diag(P)))
W=np.diag([.1,np.deg2rad(1)])**2;V=np.diag([.02,np.deg2rad(.5)])**2;P0=np.diag([.05,.05,np.deg2rad(.5)])**2
ck('sensor variance unit conversion',np.isclose(W[0,0],.01) and np.isclose(W[1,1],(np.pi/180)**2))
ck('planar dimensions',3+2*8==19 and (3,2*8)==(3,16))
ck('pixel count and aspect',640*480/(320*240)==4 and not np.isclose(1900/1200,320/240))
ker=np.ones(5);ker3=np.convolve(np.convolve(ker,ker),ker);ck('three full five tap convolution support',len(ker3)==13 and np.all(ker3>0))
ck('inclusive threshold', [x for x in[116,84,115,130] if abs(x-100)<=15]==[115])
a=np.pad(np.ones((5,7),bool),1);e=binary_erosion(a,structure=np.ones((3,3)),border_value=0);ck('full kernel erosion rectangle',int(e.sum())==15)
a=np.zeros((5,5),bool);a[2,2]=True;ck('isolated pixel removed',not binary_erosion(a,structure=np.ones((3,3))).any())
a=np.ones((7,7),bool);a[3,3]=False;ck('erosion does not fill hole',not binary_erosion(a,structure=np.ones((3,3)))[3,3])
ck('connected ray prefix',np.argmax(~np.array([1,1,0,1,1],bool))==2)
z=lambda fy,ht,v,v0:fy*ht/(v-v0)
ck('ground depth and resolution invariance',z(500,.4,250,200)==4 and z(250,.4,125,100)==4)
zz=z(500,.4,290,200);xx=(160-320)*zz/500;ck('off axis ground point',np.allclose([xx,zz],[-32/45,20/9]))
ck('horizon limiting row',np.isclose(200+200/1e12,200) and 200!=300)
ck('ground depth order',np.argmax([z(500,.4,v,200) for v in[250,300,270,290]])==0)
ck('weighted cost',[1*2**2,4*2**2]==[4,16])
rng=np.random.default_rng(4501)
for k in range(1000):
 v=rng.uniform(-4,4,3); zz=np.array([rng.uniform(.2,10),rng.uniform(-2,2)])
 A,B=gj(v,zz)
 assert np.allclose(A,numjac(lambda vv:g(vv,zz),v),atol=1e-7)
 assert np.allclose(B,numjac(lambda zzz:g(v,zzz),zz),atol=1e-7)
 p=g(v,zz);assert np.allclose(hp(v,p),numjac(lambda pp:h(v,pp),p),atol=1e-6)
 C=rng.normal(size=(2,2));P=C@C.T+.1*np.eye(2);H=rng.normal(size=(1,2));RR=rng.uniform(.01,2);K=P@H.T/(H@P@H.T+RR).item();Pn=(I-K@H)@P;Pj=(I-K@H)@P@(I-K@H).T+K*RR@K.T
 assert np.allclose(Pn,Pj) and np.linalg.eigvalsh(Pn).min()>-1e-10
 fy=rng.uniform(50,1000);height=rng.uniform(.05,2);v0=rng.uniform(50,200);vv=v0+rng.uniform(1,200);scale=rng.uniform(.1,3);depth=z(fy,height,vv,v0)
 assert np.isclose(depth,z(fy*scale,height,vv*scale,v0*scale))
 step=1e-4;dnum=(z(fy,height,vv+step,v0)-z(fy,height,vv-step,v0))/(2*step)
 assert np.isclose(dnum,-fy*height/(vv-v0)**2,rtol=1e-6)
ck('1000 varied Jacobian pose cases',True);ck('1000 varied Jacobian measurement cases',True);ck('1000 varied forward observation cases',True);ck('1000 varied covariance Joseph cases',True);ck('1000 varied camera scaling and sensitivity cases',True)
def T(t,a):
 c,s=np.cos(a),np.sin(a);return np.array([[c,-s,t[0]],[s,c,t[1]],[0,0,1.]])
for k in range(1000):
 Ti=T(rng.normal(size=2),rng.uniform(-3,3));Tj=T(rng.normal(size=2),rng.uniform(-3,3));rel=np.linalg.inv(Ti)@Tj
 assert np.allclose(np.linalg.inv(rel)@np.linalg.inv(Ti)@Tj,np.eye(3))
 assert np.allclose(rel[:2,:2].T@rel[:2,:2],np.eye(2)) and np.isclose(np.linalg.det(rel[:2,:2]),1)
ck('1000 varied SE2 relative-transform cancellation cases',True)
try:ast.parse('sensor = RangeBearingSensor(robot=robot, map=map, covar=W, 4, angle=[-np.pi/2,np.pi/2], animate=True)')
except SyntaxError:ck('literal screenshot invalid bare range argument identified, not executed',True)
else:raise AssertionError('expected source syntax issue')
runs=[]
for joint in[False,True]:
 world=LandmarkMap(20,workspace=10,seed=0)
 robot=Unicycle(covar=V,x0=[3,6,np.deg2rad(-45)] if joint else [0,0,0],animation=None,seed=0)
 robot.control=RandomPath(workspace=world,seed=0)
 sensor=RangeBearingSensor(robot=robot,map=world,covar=W,range=4,angle=[-np.pi/2,np.pi/2],plot=False,seed=0)
 f=EKF(robot=(robot,V if joint else None),sensor=(sensor,W),P0=P0 if joint else None,animate=False)
 ck(('SLAM' if joint else 'map-only')+' mode initial state',len(f.x_est)==(3 if joint else 0) and f._est_vehicle==joint and f._est_ekf_map)
 f.run(T=30,animate=False)
 N=len(f.landmarks);ck(('SLAM' if joint else 'map-only')+' full 30s runtime',len(f.history)>0 and len(f.x_est)==(3 if joint else 0)+2*N and f.P_est.shape==(len(f.x_est),len(f.x_est)) and N>0 and N<=20)
 ck(('SLAM' if joint else 'map-only')+' finite PSD covariance',np.isfinite(f.x_est).all() and np.linalg.eigvalsh(f.P_est).min()>-1e-9)
 plt.figure(figsize=(6,6));world.plot();robot.plot_xy(color='blue');f.plot_map();
 if joint:f.plot_xy(color='red')
 plt.title(('SLAM' if joint else 'Map-only')+' reviewer reconstruction, unaligned');plt.savefig('audits/W09-L45-independent-'+('slam' if joint else 'mapping')+'.png',dpi=140);plt.close()
 run={'mode':'SLAM' if joint else 'mapping','simulationSeconds':30,'steps':len(f.history),'landmarks':N,'stateLength':len(f.x_est),'covarianceShape':list(f.P_est.shape),'finalState':f.x_est.tolist()}
 if joint:
  transform=f.get_transform(world).A;ck('rigid alignment output is SE2',np.allclose(transform[2],[0,0,1]) and np.isclose(np.linalg.det(transform[:2,:2]),1));run['alignmentTransform']=transform.tolist()
 runs.append(run)
report={'reviewer':'independent-reviewer-robotics-batches-v2','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Own source-pixel mathematical checks and reconstructed source examples using official RTB; not original notebook or exact source screenshot execution. No author checker executed.','python':sys.version,'numpy':np.__version__,'roboticstoolbox':rtb.__version__,'passedGroups':len(checks),'checks':checks,'variedCases':6000,'runs':runs,'qualifications':['Changed bare4 to range=4 in mapping screenshot to form legal Python; imported required classes and numpy.','np.pi used for bare pi in SLAM screenshot.','Disabled animation/display for numerical run and generated separate static plots; no original HTML animation reproduction claimed.','Used explicit deterministic seeds0.','SLAM plot before rigid alignment is deliberately in estimated frame; get_transform frame direction retained from API, no undocumented inversion.','Initial matplotlib probe used auto temporary cache after read-only default cache warning; following runs use writable /tmp config.']}
p=pathlib.Path('audits/W09-L45-independent-computations.json');p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':len(checks),'variedCases':6000,'runs':[(x['mode'],x['steps'],x['landmarks'],x['stateLength']) for x in runs]}))
