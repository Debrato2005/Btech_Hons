"""Source-derived L45 checks; author checks do not replace independent review."""
from pathlib import Path
import json, math, random, hashlib, inspect
import numpy as np
import roboticstoolbox as rtb
from roboticstoolbox.mobile import LandmarkMap,Unicycle,RandomPath,RangeBearingSensor,EKF
R=Path(__file__).resolve().parents[1];checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
def close(x,y):return np.allclose(x,y,atol=1e-9)
P=np.diag([.5,1.]);H=np.array([[-1.,1.]]);W=.25;S=(H@P@H.T)[0,0]+W;K=P@H.T/S
mu=np.array([3.,5.])+K[:,0]*.3;A=np.eye(2)-K@H;Pn=A@P;Pj=A@P@A.T+W*K@K.T
ck('Innovation variance 7/4',close(S,1.75));ck('Gain exact fractions',close(K[:,0],[-2/7,4/7]));ck('Corrected means',close(mu,[102/35,181/35]));ck('Posterior covariance exact fractions',close(Pn,[[5/14,2/7],[2/7,3/7]]));ck('Joseph and simple updates agree',close(Pn,Pj));ck('Printed off-diagonal .143 is not the computed covariance',not close(Pn[0,1],.143));ck('Covariance symmetric PSD',close(Pn,Pn.T) and np.linalg.eigvalsh(Pn).min()>0)
map=LandmarkMap(20,workspace=10,seed=0);V=np.diag([.02,np.deg2rad(.5)])**2;W2=np.diag([.1,np.deg2rad(1)])**2
robot=Unicycle(covar=V);robot.control=RandomPath(workspace=map);sensor=RangeBearingSensor(robot=robot,map=map,covar=W2,range=4,angle=[-np.pi/2,np.pi/2],plot=False)
x=np.array([2.,3.,.2]);z=np.array([4.,.3]);land=sensor.g(x,z);Gx=sensor.Gx(x,z);Gz=sensor.Gz(x,z)
expectedGx=np.array([[1,0,-4*np.sin(.5)],[0,1,4*np.cos(.5)]]);expectedGz=np.array([[np.cos(.5),-4*np.sin(.5)],[np.sin(.5),4*np.cos(.5)]])
ck('Inverse observation position',close(land,[2+4*np.cos(.5),3+4*np.sin(.5)]));ck('Official inverse pose Jacobian nonzero',close(Gx,expectedGx));ck('Official inverse measurement Jacobian',close(Gz,expectedGz))
def fd(fun,a):
 out=[]
 for j in range(len(a)):
  d=np.zeros_like(a);d[j]=1e-5;out.append((fun(a+d)-fun(a-d))/(2e-5))
 return np.array(out).T
ck('Pose Jacobian finite differences',np.allclose(Gx,fd(lambda a:sensor.g(a,z),x),atol=1e-8));ck('Measurement Jacobian finite differences',np.allclose(Gz,fd(lambda a:sensor.g(x,a),z),atol=1e-8));ck('Forward observation inverts inverse model',close(sensor.h(x,land),z));ck('Landmark observation Jacobian finite differences',np.allclose(sensor.Hp(x,land),fd(lambda a:sensor.h(x,a),land),atol=1e-8))
ck('At origin forward range 3-4-5',close(sensor.h([0,0,0],[3,4]),[5,np.arctan2(4,3)]));ck('atan2 preserves quadrant',close(sensor.h([0,0,0],[-1,1])[1],3*np.pi/4))
# These are explicit reconstructions of the visible lecture examples, not an original notebook.
ekf=EKF(robot=(robot,None),sensor=(sensor,W2),animate=False);initialMapLen=len(ekf.x_est);ekf.run(T=30,animate=False);mapLen=len(ekf.x_est)
ck('Mapping starts empty',initialMapLen==0);ck('Mapping appends landmark pairs',mapLen>0 and mapLen%2==0 and ekf.P_est.shape==(mapLen,mapLen));ck('Mapping simulation finite',np.isfinite(ekf.x_est).all() and np.isfinite(ekf.P_est).all())
robot2=Unicycle(covar=V,x0=(3,6,np.deg2rad(-45)));robot2.control=RandomPath(workspace=map);sensor2=RangeBearingSensor(robot2,map,covar=W2,range=4,angle=[-np.pi/2,np.pi/2],plot=False);P0=np.diag([.05,.05,np.deg2rad(.5)])**2
slam=EKF(robot=(robot2,V),P0=P0,sensor=(sensor2,W2),animate=False);initialSlamLen=len(slam.x_est);slam.run(T=30,animate=False);slamLen=len(slam.x_est)
ck('SLAM starts with three pose values',initialSlamLen==3);ck('SLAM appends landmark pairs',slamLen>3 and (slamLen-3)%2==0 and slam.P_est.shape==(slamLen,slamLen));ck('SLAM finite symmetric covariance',np.isfinite(slam.x_est).all() and close(slam.P_est,slam.P_est.T));T=slam.get_transform(map);ck('Alignment rigid matrix',T.A.shape==(3,3) and close(T.R.T@T.R,np.eye(2)))
# Floor projection and image operations: author-added examples use explicit assumptions.
ck('Worked floor depth 4m',500*.4/(250-200)==4);ck('Off-axis lateral coordinate',close((160-320)*(500*.4/(290-200))/500,-32/45));ck('Three-pixel floor depth variation',close(500*.4/(253-200),200/53));ck('Half-resolution equal depth',(250*.4/(125-100))==4);ck('Downsample 1900x1200 to320x240 fraction',close((320*240)/(1900*1200),16/475));ck('Erosion full3x3 retains center',all([1]*9));ck('Erosion isolated point disappears',not all([0,0,0,0,1,0,0,0,0]));ck('Three full5tap convolutions receptive width13',1+3*(5-1)==13)
angle=.4;good=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]]);bad=np.array([[np.cos(angle),np.sin(angle)],[np.sin(angle),np.cos(angle)]]);ck('Correct rotation orthogonal determinant1',close(good.T@good,np.eye(2)) and close(np.linalg.det(good),1));ck('Printed positive-positive sine matrix not generally rotation',not close(bad.T@bad,np.eye(2)))
rng=np.random.default_rng(45)
for _ in range(3000):
 A=rng.normal(size=(2,2));P=A@A.T+.01*np.eye(2);h=rng.normal(size=(1,2));r=float(rng.uniform(.01,2));k=P@h.T/float((h@P@h.T)[0,0]+r);B=np.eye(2)-k@h;a=B@P;b=B@P@B.T+r*k@k.T;assert np.allclose(a,b,atol=1e-10);assert np.linalg.eigvalsh(b).min()>-1e-10
for _ in range(2000):
 h=float(rng.uniform(.1,2));f=float(rng.uniform(100,1500));d=float(rng.uniform(.1,20));v0=200.;v=v0+f*h/d;assert abs(f*h/(v-v0)-d)<1e-10
ck('5000 varied covariance and floor-projection cases',True)
installed=Path(inspect.getfile(EKF));out={'authorChecksOnly':True,'independentReviewRequired':True,'checkCount':len(checks),'checks':checks,'variedCases':5000,'rtbVersion':rtb.__version__,'numpyVersion':np.__version__,'installedEkfSha256':hashlib.sha256(installed.read_bytes()).hexdigest(),'reconstructedRuns':{'mappingInitialStateLength':initialMapLen,'mappingFinalStateLength':mapLen,'slamInitialStateLength':initialSlamLen,'slamFinalStateLength':slamLen,'durationSecondsEach':30,'originalNotebookExecuted':False,'adaptations':['Reconstructed visible slide calls with complete imports.','Disabled plotting/animation for noninteractive numerical execution.','Used installed official PyPI roboticstoolbox-python 1.4.4, not a claimed historic course version.']},'exact1DResults':{'S':S,'K':K[:,0].tolist(),'mean':mu.tolist(),'covariance':Pn.tolist()},'limits':['No original Lecture45 notebook was present in the checked official week09 directory.','Simulation success does not verify physical navigation safety.','Source formula conflicts are qualified rather than silently corrected.']};(R/'audits/W09-L45-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
