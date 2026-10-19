"""Independent source-first L35 checks, not author expected outputs. Freeze after run."""
from pathlib import Path
import json,hashlib,datetime,inspect,os
os.environ['YOLO_CONFIG_DIR']='/tmp/robotics-l35-contracts-config'
os.environ['MPLCONFIGDIR']='/tmp/robotics-l35-contracts-mpl'
import torch,numpy as np,ultralytics,cv2
from ultralytics import YOLO
from ultralytics.nn.modules.head import Detect
from ultralytics.utils.tal import dist2bbox
from ultralytics.engine.results import Boxes
R=Path(__file__).resolve().parents[1];checks=[]
def ck(name,value,expected):
 assert np.allclose(value,expected), (name,value,expected)
 checks.append({'name':name,'observed':value,'expectedIndependentlyDerived':expected})
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for n,v,e in [('dense78500',(784+1)*100,78500),('conv1',(25+1)*16,416),('conv2',(25*16+1)*32,12832),('hidden dense',(512+1)*128,65664),('output dense',(128+1)*10,1290),('total',416+12832+65664+1290,80202),('stride floor',(8-3)//2+1,3),('conv1 side',28-5+1,24),('conv2 side',12-5+1,8),('flatten',4*4*32,512)]:ck(n,v,e)
x=torch.tensor([[[[1.,2.],[3.,4.]]]]);k=torch.tensor([[[[1.,0.],[0.,-1.]]]])
ck('actual cross correlation',torch.nn.functional.conv2d(x,k).item(),-3)
a=torch.tensor([[[[8.,16.,8.,20.],[13.,3.,14.,6.],[20.,14.,2.,14.],[6.,32.,6.,22.]]]])
ck('actual max pooling',torch.nn.functional.max_pool2d(a,2).tolist(),[[[[16,20],[32,22]]]])
ck('actual mean pooling',torch.nn.functional.avg_pool2d(a,2).tolist(),[[[[10,12],[18,11]]]])
ck('ReLU',torch.relu(torch.tensor([-2.,0.,3.])).tolist(),[0,0,3])
u=torch.tensor([1.,0.]);v=torch.tensor([0.,1.]);ck('max counterexample max(u+v)',(u+v).max().item(),1);ck('max(u)+max(v)',(u.max()+v.max()).item(),2)
for n,v,e in [('YOLOv1 center',[(2+.25)*700/7,(3+.5)*700/7],[225,350]),('YOLOv1 confidence',.8*.5,.4),('class score',.7*.4,.28),('YOLOv1 output',[7,7,5*2+20],[7,7,30]),('YOLOv1 candidates',7*7*2,98),('YOLOv1 values',7*7*30,1470),('four-repeat conv block',2*4+2,10),('two-repeat conv block',2*2+2,6),('conv total',sum([1,1,4,10,6,2]),24),('multiscale sides',[640//s for s in [8,16,32]],[80,40,20]),('printed bus corners',[413.94-782.13/2,494.06-525.56/2,413.94+782.13/2,494.06+525.56/2],[22.875,231.28,805.005,756.84])]:ck(n,v,e)
from torchvision.ops import nms,batched_nms
bs=torch.tensor([[0.,0.,10.,10.],[1.,1.,11.,11.]]);sc=torch.tensor([.9,.8]);classes=torch.tensor([0,1])
ck('class-aware retention',batched_nms(bs,sc,classes,.5).tolist(),[0,1]);ck('class-agnostic retention',nms(bs,sc,.5).tolist(),[0])
ck('distance decode',dist2bbox(torch.tensor([[2.,3.,4.,5.]]),torch.tensor([[10.,20.]]),xywh=False,dim=-1).tolist(),[[8,17,14,25]])
rng=np.random.default_rng(3535)
for _ in range(1000):
 cx,cy=rng.uniform(-100,100,2);w,h=rng.uniform(.01,200,2)
 p=np.array([cx-w/2,cy-h/2,cx+w/2,cy+h/2]);assert np.allclose([(p[0]+p[2])/2,(p[1]+p[3])/2,p[2]-p[0],p[3]-p[1]],[cx,cy,w,h])
 I=int(rng.integers(5,80));K=int(rng.integers(1,6));P=int(rng.integers(0,4));S=int(rng.integers(1,5));assert len(range(0,I+2*P-K+1,S))==(I+2*P-K)//S+1
# Independently transcribed PDF p1083 key lines, with local paths and isolated output.
mp=Path('/tmp/robotics-l35-runtime/yolov8n.pt');ip=Path('/tmp/robotics-l35-runtime/bus.jpg')
model=YOLO(str(mp));results=model.predict(source=str(ip),save=True,conf=.25,project='/tmp/robotics-l35-contracts-inference',name='source_run',exist_ok=True,device='cpu',verbose=False)
output_dir=results[0].save_dir
assert len(results)==1 and Path(output_dir,'bus.jpg').exists()
b=results[0].boxes
rows=[{'classIndex':int(c),'name':results[0].names[int(c)],'confidence':float(s),'xywh':[float(z) for z in a],'xyxy':[float(z) for z in bb]} for c,s,a,bb in zip(b.cls,b.conf,b.xywh,b.xyxy)]
ck('original source report count',len(rows),6)
expected=[('bus',87.3,[413.94,494.06,782.13,525.56]),('person',86.6,[146.95,650.63,196.8,504.15]),('person',85.3,[739.6,634.61,140.25,484.85]),('person',82.5,[283.24,631.67,123.45,451.74]),('person',26.1,[31.5,711.98,63.01,322.92]),('stop sign',25.5,[16.31,289.67,32.5,70.41])]
sourceMatches=[]
for actual,(name,score,xywh) in zip(rows,expected):
 ok=actual['name']==name and round(actual['confidence']*100,1)==score and np.max(np.abs(np.array(actual['xywh'])-xywh))<.011
 assert ok,(actual,name,score,xywh)
 sourceMatches.append({'class':name,'matchesPrintedRounding':bool(ok)})
out={'reviewerId':'robotics-contracts-reviewer-L35-v2','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'versions':{'ultralytics':ultralytics.__version__,'torch':torch.__version__,'opencv':cv2.__version__},'versionQualification':'PyTorch logical NCHW claim checked separately in official 2.9 documentation. Runtime is 2.14.1+cpu, not 2.9.','checks':checks,'assertions':len(checks)+len(sourceMatches),'variedBoxRoundTrips':1000,'variedConvolutionWindowCounts':1000,'sourceCode':'Independently transcribed PDF page1083 key lines; local asset paths and isolated output only. Notebook retrieval tracked separately.','modelPath':str(mp),'modelSha256':sha(mp),'imagePath':str(ip),'imageSha256':sha(ip),'resultsCount':len(results),'saveDir':str(output_dir),'annotatedPath':str(Path(output_dir,'bus.jpg')),'annotatedSha256':sha(Path(output_dir,'bus.jpg')),'detections':rows,'sourceReportComparisons':sourceMatches,'installedSource':{'Detect.decode_bboxes':inspect.getsource(Detect.decode_bboxes),'dist2bbox':inspect.getsource(dist2bbox),'Boxes.xywh':inspect.getsource(Boxes.xywh.func)},'authorExpectedOutputsRead':False,'initialRunNote':'All calculations and inference succeeded; report serialization initially used property.fget on a cached_property and failed. Corrected introspection to .func and reran before any keyed access.'}
p=R/'audits/W07-L35-v2-contracts-independent-checks.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('PASS',out['assertions'],'checks and 2000 varied cases; detections',len(rows));print('output',p)
