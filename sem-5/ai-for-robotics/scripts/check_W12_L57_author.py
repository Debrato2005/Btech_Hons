"""Explicit added mathematical/software models. Not source hardware or omitted programs."""
from pathlib import Path
import json,datetime,math,colorsys,importlib.util
import numpy as np
import scipy
from scipy.spatial.transform import Rotation
from scipy import ndimage
R=Path(__file__).resolve().parents[1];checks=[]
def ck(name,ok):
 assert bool(ok),name
 checks.append(name)
def rz(a):return Rotation.from_euler('z',a,degrees=True).as_matrix()
def T(r,t):
 h=np.eye(4);h[:3,:3]=r;h[:3,3]=t;return h
def inv(h):return T(h[:3,:3].T,-h[:3,:3].T@h[:3,3])
def point(h,p):return (h@np.r_[p,1])[:3]
# Fixed questions and plausible distractor calculations.
p=np.array([2.,1.]);r=np.array([[0,-1],[1,0]])
ck('planar TCP contact equality',np.allclose(p+[8,4],r@p+[11,3]))
ck('planar TCP solve',np.allclose(np.linalg.solve(np.eye(2)-r,np.array([11,3])-[8,4]),p))
rots=[np.eye(3),Rotation.from_euler('x',90,degrees=True).as_matrix(),Rotation.from_euler('y',90,degrees=True).as_matrix(),rz(90)]
a=np.vstack([rr-np.eye(3) for rr in rots[1:]])
ck('four diverse orientations give rank three offset solve',np.linalg.matrix_rank(a)==3)
ck('identical orientations give rank zero difference constraints',np.linalg.matrix_rank(np.vstack([rots[0]-rots[0]]*3))==0)
q=np.array([20.,-10,100]);c=np.array([400.,50,200]);ts=[c-rr@q for rr in rots]
ck('3D pivot least squares',np.allclose(np.linalg.lstsq(a,np.concatenate([ts[0]-x for x in ts[1:]]),rcond=None)[0],q))
ck('two-contact friction per jaw',math.isclose(2*.8*10/(2*.4),20))
ck('reprojection RMS per corner',math.isclose(np.sqrt(np.mean(np.array([1,2,2,1])**2)),math.sqrt(2.5)))
def masks(h,s,v):return [k for k,lo,hi in [('cyan',87,128),('purple',130,155),('magenta',155,180)] if lo<=h<=hi and s>=60 and v>=60]
ck('overlapping hue 155',masks(155,100,100)==['purple','magenta'])
ck('cyan exact saturation/value endpoint',masks(100,60,60)==['cyan'])
ck('low saturation rejects',masks(100,59,200)==[])
ck('low value rejects',masks(100,200,59)==[])
ck('hue 129 gap',masks(129,200,200)==[])
ck('hue 179 valid upper-domain magenta',masks(179,255,255)==['magenta'])
ck('area inclusive endpoints',[800<=x<=60000 for x in [799,800,1200,60000,60001]]==[False,True,True,True,False])
mask=np.zeros((15,15),bool);mask[3:12,3:12]=True;mask[0,0]=True
opened=ndimage.binary_opening(mask,structure=np.ones((3,3)))
ck('added morphology opening removes island',not opened[0,0] and opened[5,5])
hole=np.zeros((15,15),bool);hole[3:12,3:12]=True;hole[7,7]=False
closed=ndimage.binary_closing(hole,structure=np.ones((3,3)))
ck('added morphology closing fills one-pixel hole',closed[7,7] and not closed[0,0])
ck('RGB/BGR hue distinction in declared ideal floating HSV',not math.isclose(colorsys.rgb_to_hsv(1,0,0)[0],colorsys.rgb_to_hsv(0,0,1)[0]))
ck('centroid moments',np.allclose([360000/1200,240000/1200],[300,200]))
ck('triangle and box centres differ',np.allclose(np.mean([[0,0],[6,0],[0,3]],axis=0),[2,1]) and not np.allclose([2,1],[3,1.5]))
ck('circularity descriptor',math.isclose(4*math.pi*100/40**2,math.pi/4))
pc=np.array([(380-320)*500/600,(190-240)*500/500,500.])
ck('camera deprojection',np.allclose(pc,[50,-50,500]))
ck('range not axial depth',math.isclose(np.linalg.norm([300,400,1200]),1300))
cm=T(rz(90),[100,200,50]);rm=T(np.eye(3),[600,100,0]);ft=T(np.eye(3),[0,0,100])
pm=point(inv(cm),pc);pr=point(rm,pm);fl=pr-[0,0,100]
ck('PnP inverse point',np.allclose(pm,[-250,50,450]))
ck('integrated target',np.allclose(fl,[350,150,350]))
ck('integrated forward-PnP distractor',np.allclose(point(rm,point(cm,pc))-[0,0,100],[750,350,450]))
ck('integrated omitted-marker distractor',np.allclose(point(rm,pc)-[0,0,100],[650,50,400]))
ck('rotated marker offset',np.allclose(point(T(rz(90),[100,200,0]),[30,10,50]),[90,230,50]))
ck('rotated translation distractor',np.allclose(rz(90)@(np.array([30,10,50])+[100,200,0]),[-210,130,50]))
ck('unit conversion',np.allclose(np.array([.1,.2,.3])*1000+[100,0,0],[200,200,300]))
ck('clearance condition',145-5==120+20)
counter=0;events=[]
for i,valid in enumerate([False,False,True,False,False,False],1):
 counter=0 if valid else counter+1
 if valid:events.append([i,'PICK'])
 elif counter>=3:events.append([i,'HOME'])
ck('declared scan state trace',events==[[3,'PICK'],[6,'HOME']])
ck('marker size scale',50/40*400==500)
ck('latency displacement',math.isclose(.2*.15*1000,30))
ck('depth error propagation',60/600*10==1)
ck('independent variance',math.isclose(math.sqrt(2**2+3**2),math.sqrt(13)))
ck('wrist-dependent offset error',not np.allclose(rz(0)@[10,0,0],rz(90)@[10,0,0]))
# Independent implementation-level randomized checks of the stated formulas.
rng=np.random.default_rng(571903);varied=0
for _ in range(1000):
 ra=Rotation.random(random_state=rng).as_matrix();rb=Rotation.random(random_state=rng).as_matrix();ta=rng.normal(size=3);tb=rng.normal(size=3);x=rng.normal(size=3)
 ha,hb=T(ra,ta),T(rb,tb)
 assert np.allclose(inv(ha),np.linalg.inv(ha));varied+=1
 assert np.allclose(point(ha@hb,x),ra@(rb@x+tb)+ta);varied+=1
 assert np.allclose(point(inv(ha),point(ha,x)),x);varied+=1
 # Actual source chain equality with arbitrary desired object/grasp/tool poses.
 ro=T(Rotation.random(random_state=rng).as_matrix(),rng.normal(size=3));to=T(Rotation.random(random_state=rng).as_matrix(),rng.normal(size=3));rf=ro@inv(to)@inv(hb)
 assert np.allclose(rf@hb@to,ro);varied+=1
 fx,fy=rng.uniform(100,1000,2);cx,cy=rng.uniform(100,500,2);xyz=rng.normal(size=3);xyz[2]=rng.uniform(.1,5)
 u,v=fx*xyz[0]/xyz[2]+cx,fy*xyz[1]/xyz[2]+cy
 back=np.array([(u-cx)*xyz[2]/fx,(v-cy)*xyz[2]/fy,xyz[2]])
 assert np.allclose(back,xyz);varied+=1
report={'batchId':'W12-L57','authorId':'build_offline_study_interface:L57-author','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'namedChecks':len(checks),'checks':checks,'variedChecks':varied,'seed':571903,'versions':{'numpy':np.__version__,'scipy':scipy.__version__},'opencvInstalled':importlib.util.find_spec('cv2') is not None,'scope':'Added mathematical equations and synthetic input checks only. SciPy morphology and Python floating HSV are distinct declared checks, not OpenCV/source implementation reproduction. No original source code listing exists here; no source images, videos, robot/controller, pyrealsense2, OpenShowVar or KRL program executed.','independentReview':False,'passed':True}
(R/'audits/W12-L57-author-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(len(checks),'named;',varied,'varied checks passed')
