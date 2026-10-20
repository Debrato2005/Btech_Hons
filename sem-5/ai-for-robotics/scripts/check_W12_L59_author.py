"""Added deterministic numerical checks, not ROS/Gazebo/Jetson/Arduino execution."""
from pathlib import Path
import json,math,hashlib,datetime
import numpy as np
R=Path(__file__).resolve().parents[1];checks=[]
def ck(n,ok):
 assert bool(ok),n
 checks.append(n)
def forward(r,L,wR,wL):return np.array([r*(wR+wL)/2,r*(wR-wL)/L])
def inverse(r,L,v,w):return np.array([(v+L*w/2)/r,(v-L*w/2)/r])
def arc(pose,v,w,dt):
 x,y,t=pose;a=w*dt
 if abs(w)<1e-10:return np.array([x+v*dt*math.cos(t),y+v*dt*math.sin(t),t+a])
 return np.array([x+v/w*(math.sin(t+a)-math.sin(t)),y-v/w*(math.cos(t+a)-math.cos(t)),t+a])
def T(t,x,y):
 c,s=math.cos(t),math.sin(t);return np.array([[c,-s,x],[s,c,y],[0,0,1.]])
ck('forward numerical',np.allclose(forward(.1,.5,6,2),[.4,.8]));ck('opposite equal rates rotate in place',np.isclose(forward(.1,.5,4,-4)[0],0));ck('opposite unequal rates translate',not np.isclose(forward(.1,.5,4,-2)[0],0));ck('equal positive rates straight',np.isclose(forward(.1,.5,4,4)[1],0));ck('one stationary wheel not midpoint spin',not np.isclose(forward(.1,.5,0,4)[0],0));ck('inverse command',np.allclose(inverse(.1,.4,.3,1),[5,1]));ck('turn radius',np.isclose(.4/.8,.5));ck('count travel',np.isclose(2*math.pi*.1*300/1200,.05*math.pi));e=4-3;integ=.2+e*.1;der=(e-.5)/.1;u=.2*e+.1*integ+.01*der;ck('PID error',e==1);ck('PID updated integral',np.isclose(integ,.3));ck('PID backward derivative',np.isclose(der,5));ck('PID command',np.isclose(u,.28));ck('PID missing derivative alternative',np.isclose(.2+.03,.23));ck('PID old integral alternative',np.isclose(.2+.02+.05,.27));ck('PID missing dt alternative',np.isclose(.2+.03+.01*.5,.235));tm=T(math.pi/2,1,2)@T(0,2,0);ck('frame point composition',np.allclose(tm@np.array([1,0,1]),[1,5,1]));ck('composition order matters',not np.allclose(T(math.pi/2,1,2)@T(0,2,0),T(0,2,0)@T(math.pi/2,1,2)));P=.04;Rr=.01;gain=P/(P+Rr);ck('scalar gain',np.isclose(gain,.8));ck('scalar posterior mean',np.isclose(1+gain*.3,1.24));ck('scalar posterior variance',np.isclose((1-gain)*P,.008));p=np.array([.5,.3,.2]);lik=np.array([.2,.5,.5]);w=p*lik;w/=sum(w);ck('particle normalized weights',np.allclose(w,[2/7,3/7,2/7]));ck('particle top hypothesis',np.argmax(w)==1);ck('particle likelihood-only distractor',np.allclose(lik/sum(lik),[1/6,5/12,5/12]));paths=[('A',8,6,False),('B',10,0,False),('C',6,0,True)];ck('feasibility before route cost',min((L+.5*c,n) for n,L,c,collide in paths if not collide)[1]=='B');Z=1500*.001;ck('depth scale',Z==1.5);ck('camera point',np.allclose([(420-320)*Z/500,(240-240)*Z/500,Z],[.3,0,1.5]));ck('axial depth not Euclidean range',math.sqrt(.3**2+1.5**2)>Z);ck('playback interval',20*3.25==65);r=1/(2*math.pi);sr=2*math.pi*r*200/1000;sl=2*math.pi*r*100/1000;dth=(sr-sl)/.5;ds=(sr+sl)/2;res=arc([0,0,0],ds,dth,1);ck('encoder arc heading',np.isclose(dth,.2));ck('encoder arc position',np.allclose(res,[.75*math.sin(.2),.75*(1-math.cos(.2)),.2]));ck('encoder arc rounded answer',np.allclose(res,[.1490,.01495,.2],atol=5e-5));wr,wl=inverse(.1,.4,.3,1);s=min(1,4/max(abs(wr),abs(wl)));ck('uniform feasible scale',np.isclose(s,.8));ck('uniform wheel command',np.allclose(s*np.array([wr,wl]),[4,.8]));ck('curvature preserved',np.isclose(.3/1,(s*.3)/(s*1)));ck('one-sided clipping changes curvature',not np.isclose(forward(.1,.4,4,1)[0]/forward(.1,.4,4,1)[1],.3));ck('corridor required width',np.isclose(2*(.25+.1),.7));ck('corridor insufficient',.65<2*(.25+.1))
rng=np.random.default_rng(591277)
for _ in range(5000):
 r=rng.uniform(.03,.3);L=rng.uniform(.2,1);wheels=rng.uniform(-8,8,2);v,w=forward(r,L,*wheels);assert np.allclose(inverse(r,L,v,w),wheels)
 pose=rng.normal(size=3);dt=rng.uniform(.01,2);whole=arc(pose,v,w,dt);half=arc(arc(pose,v,w,dt/2),v,w,dt/2);assert np.allclose(whole,half,rtol=1e-8,atol=1e-8)
 A=T(*rng.normal(size=3));B=T(*rng.normal(size=3));p=np.r_[rng.normal(size=2),1];assert np.allclose((A@B)@p,A@(B@p))
 P,Rr=rng.uniform(.001,2,2);K=P/(P+Rr);assert 0<K<1 and 0<(1-K)*P<min(P,Rr)+1e-10
 prior=rng.random(6);prior/=sum(prior);ell=rng.random(6);post=prior*ell;post/=sum(post);assert np.isclose(sum(post),1) and (post>=0).all()
 scale=min(1,4/max(abs(wheels)));limited=scale*wheels;assert max(abs(limited))<=4+1e-10 and np.allclose(forward(r,L,*limited),scale*np.array([v,w]))
out={'batchId':'W12-L59','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Added deterministic equal-radius rolling, exact arc, encoder calibration, discrete PID, frame algebra, scalar filter, particle weights, cost comparison, aligned depth and feasibility examples. No source executable code was printed. No ROS, Gazebo, YOLO model, original video, Jetson, Arduino or robot hardware execution is claimed.','namedChecks':len(checks),'variedChecks':5000,'variedAssertions':30000,'checks':checks,'independentReview':False,'versions':{'numpy':np.__version__},'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(R/'audits/W12-L59-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print('Passed',len(checks),'named and 5000 varied cases')
