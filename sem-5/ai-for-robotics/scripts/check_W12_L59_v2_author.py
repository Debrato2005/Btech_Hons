"""Author-only checks of changed numerical premise and transcribed schematic relations."""
from pathlib import Path
import json,datetime,math
import numpy as np
R=Path(__file__).resolve().parents[1];checks=[]
def ck(name,c):assert bool(c),name;checks.append(name)
def point(d,s,u,v,cx,cy,fx,fy):
 if d<=0 or s<=0 or fx<=0 or fy<=0:raise ValueError('Invalid declared camera/depth geometry')
 z=s*d;return np.array([(u-cx)*z/fx,(v-cy)*z/fy,z])
p=point(1500,.001,420,240,320,240,500,500);ck('Q054 corrected supplied equation gives intended point',np.allclose(p,[.3,0,1.5]));ck('Q054 axial depth is not off-axis Euclidean range',np.linalg.norm(p)>p[2]);ck('Q054 central pixel',np.allclose(point(1500,.001,320,240,320,240,500,500),[0,0,1.5]))
ekf={'Sensor Fusion (EKF)':['SLAM','Localisation (AMCL)']};ck('Q067 two actual diagram branches',ekf['Sensor Fusion (EKF)']==['SLAM','Localisation (AMCL)'])
chain=['Desired Velocity','PID Controller','PWM Output','DC Motor','Wheel Encoder Feedback'];ck('Q068 motor chain transcription',chain.index('PWM Output')==chain.index('PID Controller')+1 and chain[-1]=='Wheel Encoder Feedback')
branches={'Processing Nodes':['Navigation','Motor Controller'],'Motor Controller':['Mobile Robot']};ck('Q070 independent processing outputs',len(branches['Processing Nodes'])==2 and branches['Motor Controller']==['Mobile Robot'])
ck('Q069 source label pairing',{'longer green':'Global Planned Path','short near robot':'Local Planner Path'}['short near robot']=='Local Planner Path')
rng=np.random.default_rng(20261020);varied=0
for _ in range(2000):
 d=float(rng.uniform(1,6000));s=float(rng.uniform(.0001,.01));fx,fy=rng.uniform(100,2000,2);cx,cy=rng.uniform(100,1000,2);u,v=rng.uniform(0,2000,2);p=point(d,s,u,v,cx,cy,fx,fy)
 assert np.allclose([fx*p[0]/p[2]+cx,fy*p[1]/p[2]+cy],[u,v]);varied+=1
 assert math.isclose(p[2],d*s) and np.linalg.norm(p)>=p[2]-1e-12;varied+=1
rejected=0
for args in [(0,.001,1,1,0,0,1,1),(1,0,1,1,0,0,1,1),(1,.001,1,1,0,0,0,1),(1,.001,1,1,0,0,1,-1)]:
 try:point(*args)
 except ValueError:rejected+=1
ck('Invalid geometry is rejected',rejected==4)
out={'authorOnly':True,'independentReview':False,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Changed pinhole exercise and explicit source-diagram transcriptions only. No ROS/Gazebo/camera/model/controller/network/browser runtime or denied-document retrieval. Diagram assertions audit the authored transcription, not an independent reading.','namedChecks':len(checks),'checks':checks,'variedAssertions':varied,'invalidGeometryRejections':rejected,'allPassed':True};(R/'audits/W12-L59-v2-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['namedChecks','variedAssertions','invalidGeometryRejections','allPassed']}))
