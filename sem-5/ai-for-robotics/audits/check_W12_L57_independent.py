"""Independent reviewer arithmetic; no author checks, CV runtime or hardware."""
from pathlib import Path
import json, math, random, sys, hashlib
from datetime import datetime, timezone
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
records=[]
def check(ids, label, value, expected):
    assert np.allclose(value,expected,rtol=1e-10,atol=1e-9),(label,value,expected)
    records.append({'questionIds':ids.split(','),'check':label,'value':np.asarray(value).tolist(),'expected':np.asarray(expected).tolist(),'passed':True})
def rot(a):
    c,s=math.cos(a),math.sin(a)
    return np.array([[c,-s,0],[s,c,0],[0,0,1.]])
def transform(r,t):
    out=np.eye(4);out[:3,:3]=r;out[:3,3]=t;return out
R=rot(math.pi/2);p=np.linalg.solve(R[:2,:2]-np.eye(2),np.array([8,4])-np.array([11,3]))
check('Q012,Q013','Planar pivot offset and common contact',np.r_[p,p+[8,4]],[2,1,10,5])
check('Q014','Repeated orientation gives rank-zero difference equations',np.linalg.matrix_rank(np.vstack([np.eye(3)-np.eye(3)]*3)),0)
check('Q022','Two-contact friction and safety factor',2*.8*10/(2*.4),20)
check('Q032','Corner Euclidean RMS',np.sqrt(np.mean(np.array([1,2,2,1])**2)),math.sqrt(2.5))
def masks(h,s,v):return [87<=h<=128 and s>=60 and v>=60,130<=h<=155 and s>=60 and v>=60,155<=h<=180 and s>=60 and v>=60]
check('Q043','Inclusive hue overlap',masks(155,100,100),[False,True,True])
check('Q044','Independent S,V boundary failures',[masks(*p)[0] for p in [(100,60,60),(100,59,200),(129,200,200),(100,200,59)]],[1,0,0,0])
check('Q047','Area boundaries',[800<=a<=60000 for a in [799,800,1200,60000,60001]],[0,1,1,1,0])
import colorsys
check('Q048','RGB red versus same bytes interpreted as BGR hue',[colorsys.rgb_to_hsv(1,0,0)[0],colorsys.rgb_to_hsv(0,0,1)[0]],[0,2/3])
check('Q049','Moment centroid',[360000/1200,240000/1200],[300,200])
check('Q050','Triangle centroid and box centre',np.r_[np.mean([[0,0],[6,0],[0,3]],axis=0),[3,1.5]],[2,1,3,1.5])
check('Q051','Circularity',4*math.pi*100/(40**2),math.pi/4)
pc=np.array([(380-320)*500/600,(190-240)*500/500,500])
check('Q052','Axial-depth deprojection',pc,[50,-50,500])
check('Q053','Axial depth and radial range',[1200,np.linalg.norm([300,400,1200])],[1200,1300])
check('Q061','Rotate before translate',R@np.array([30,10,50])+[100,200,0],[90,230,50])
pm=R.T@(pc-np.array([100,200,50]));pr=pm+[600,100,0]
check('Q067','Full camera-marker-robot-flange chain',np.r_[pm,pr,pr-[0,0,100]],[-250,50,450,350,150,450,350,150,350])
check('Q067','Wrong forward transform distractor arithmetic',R@pc+[100,200,50]+np.array([600,100,0])-[0,0,100],[750,350,450])
check('Q068','One common length unit',np.array([.1,.2,.3])*1000+[100,0,0],[200,200,300])
check('Q072','Worst-case downward clearance',120+20+5,145)
count=0;counts=[];events=[]
for i,valid in enumerate([False,False,True,False,False,False],1):
    if valid:count=0;events.append([i,'PICK'])
    else:
        count+=1
        if count==3:events.append([i,'HOME'])
    counts.append(count)
check('Q076','Consecutive invalid scan counter',counts,[1,2,0,1,2,3]);assert events==[[3,'PICK'],[6,'HOME']]
check('Q080','Marker metric-scale ambiguity',400*50/40,500)
check('Q081','Constant-speed latency displacement in mm',.20*.15*1000,30)
check('Q082','Lateral sensitivity to optical-depth error',60/600*10,1)
check('Q083','Independent additive error standard deviation',math.hypot(2,3),math.sqrt(13))
rng=np.random.default_rng(202610200037);varied={'pinhole_round_trip_and_depth_sensitivity':0,'homogeneous_inverse_and_noncommuting_flange_recovery':0,'marker_scale_and_same_projection':0,'pivot_and_rotating_tool_error':0}
for _ in range(1000):
    fx,fy=rng.uniform(50,2000,2);cx,cy=rng.uniform(-100,1000,2);x,y=rng.uniform(-500,500,2);z=rng.uniform(1,4000);dz=rng.uniform(-.5,.5)
    u,v=fx*x/z+cx,fy*y/z+cy
    assert np.allclose([(u-cx)*z/fx,(v-cy)*z/fy],[x,y]);assert np.isclose((u-cx)*(z+dz)/fx-x,(u-cx)*dz/fx)
    varied['pinhole_round_trip_and_depth_sensitivity']+=1
    # Three independently varying proper 3D rotations, not only commuting Z rotations.
    def random_T():
        a=rng.normal(size=(3,3));q,_=np.linalg.qr(a);q[:,0]*=np.linalg.det(q)
        return transform(q,rng.uniform(-1000,1000,3))
    trf,tft,ttc=random_T(),random_T(),random_T();tro=trf@tft@ttc
    assert np.allclose(tro@np.linalg.inv(ttc)@np.linalg.inv(tft),trf)
    inv=np.eye(4);inv[:3,:3]=trf[:3,:3].T;inv[:3,3]=-trf[:3,:3].T@trf[:3,3]
    assert np.allclose(inv@trf,np.eye(4));varied['homogeneous_inverse_and_noncommuting_flange_recovery']+=1
    length,assumed,depth=rng.uniform(.1,1000,3);inferred=depth*assumed/length
    assert np.isclose(fx*length/depth,fx*assumed/inferred);varied['marker_scale_and_same_projection']+=1
    tool=rng.uniform(-200,200,3);contact=rng.uniform(-500,500,3);r=trf[:3,:3];t=contact-r@tool
    assert np.allclose(r@tool+t,contact)
    error=rng.uniform(-10,10,3);assert np.allclose(r@(tool+error)+t-contact,r@error)
    varied['pivot_and_rotating_tool_error']+=1
report={'batchId':'W12-L57','reviewerId':'independent-reviewer-robotics-batches-v2','checkedAt':datetime.now(timezone.utc).isoformat(),'pythonExecutable':sys.executable,'numpyVersion':np.__version__,'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'fixedChecks':records,'scanEvents':events,'variedSeed':202610200037,'variedChecks':varied,'totalVariedCases':sum(varied.values()),'allPassed':True,'boundary':'Only default Python, NumPy and standard-library arithmetic. RGB/BGR example uses colorsys, not OpenCV. No original KRL or vision program, hardware, video, camera, model, restricted environment, installation or download executed.'}
ROOT.joinpath('audits/W12-L57-independent-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(len(records),'fixed checks;',sum(varied.values()),'varied cases; all passed')
