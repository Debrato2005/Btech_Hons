"""Actual CPU tensor/API checks and source-specific arithmetic; no independent approval."""
from pathlib import Path
import json,datetime,hashlib,math
import numpy as np,torch,torch.nn as nn,torch.nn.functional as F
from torchvision.ops import nms
from ultralytics.engine.results import Boxes
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,condition,actual=None):
 assert bool(condition),name
 checks.append({'name':name,'passed':True,'actual':actual})
count=lambda m:sum(p.numel()for p in m.parameters())
check('dense 784 to100',count(nn.Linear(784,100))==78500)
check('3 to4 to1 weights without biases',count(nn.Sequential(nn.Linear(3,4,bias=False),nn.Linear(4,1,bias=False)))==16)
c1=nn.Conv2d(1,16,5);c2=nn.Conv2d(16,32,5);d1=nn.Linear(512,128);d2=nn.Linear(128,10)
x=torch.zeros(1,1,28,28);a=c1(x);check('conv1 actual shape',list(a.shape)==[1,16,24,24],list(a.shape));check('conv1 count',count(c1)==416)
p1=F.max_pool2d(a,2,2);check('pool1 actual shape',list(p1.shape)==[1,16,12,12]);a2=c2(p1);check('conv2 actual shape',list(a2.shape)==[1,32,8,8]);check('conv2 count',count(c2)==12832);p2=F.max_pool2d(a2,2,2);check('pool2 actual shape',list(p2.shape)==[1,32,4,4]);flat=p2.flatten(1);check('flatten actual shape',list(flat.shape)==[1,512]);check('dense hidden count',count(d1)==65664);check('dense output count',count(d2)==1290);check('total parameter count',sum(map(count,[c1,c2,d1,d2]))==80202)
check('weights-only total',sum(p.numel()for m in[c1,c2,d1,d2]for name,p in m.named_parameters()if name=='weight')==80016)
M=torch.tensor([[8.,16,8,20],[13,3,14,6],[20,14,2,14],[6,32,6,22]])[None,None]
check('actual max pool',F.max_pool2d(M,2,2)[0,0].tolist()==[[16,20],[32,22]])
check('actual average pool',F.avg_pool2d(M,2,2)[0,0].tolist()==[[10,12],[18,11]])
check('max pool has no parameters',count(nn.MaxPool2d(2))==0)
check('ReLU values',F.relu(torch.tensor([-2.,0,3])).tolist()==[0,0,3])
patch=torch.tensor([[[[1.,2],[3,4]]]]);kernel=torch.tensor([[[[1.,0],[0,-1]]]])
check('actual conv2d cross correlation',F.conv2d(patch,kernel).item()==-3)
check('stride floor',nn.Conv2d(1,1,3,stride=2)(torch.zeros(1,1,8,8)).shape[-1]==3)
check('same padding',nn.Conv2d(1,1,5,padding=2)(torch.zeros(1,1,8,8)).shape[-1]==8)
check('cell coordinate',[(2+.25)*100,(3+.5)*100]==[225,350])
check('IoU worked',40/(100+100-40)==.25)
check('confidence product',np.isclose(.8*.5,.4));check('class score',np.isclose(.7*.4,.28))
check('YOLOv1 output width',5*2+20==30);check('YOLOv1 scalars',7*7*30==1470);check('YOLOv1 candidates',7*7*2==98)
boxes=torch.tensor([[0.,0,10,10],[1,1,11,11],[20,20,30,30]]);scores=torch.tensor([.9,.8,.7]);check('actual NMS distant object survives',nms(boxes,scores,.5).tolist()==[0,2])
check('three scale grids',[640//s for s in[8,16,32]]==[80,40,20]);check('printed detection count',1+4+1==6);check('printed score threshold',sum(v>=.5 for v in[.873,.866,.853,.825,.261,.255])==4)
xywh=np.array([413.94,494.06,782.13,525.56]);corners=np.r_[xywh[:2]-xywh[2:]/2,xywh[:2]+xywh[2:]/2];check('printed rounded center conversion',np.allclose(corners,[22.875,231.28,805.005,756.84]),corners.tolist())
api=Boxes(torch.tensor([[22.875,231.28,805.005,756.84,.873,5.]],dtype=torch.float64),(1080,810));check('actual Boxes xywh center convention',np.allclose(api.xywh[0].numpy(),xywh));check('actual Boxes conf and cls',np.isclose(api.conf.item(),.873)and api.cls.item()==5)
rng=np.random.default_rng(350019)
for i in range(500):
 ar=rng.normal(size=(4,4));br=rng.normal(size=(4,4));A=torch.tensor(ar)[None,None];B=torch.tensor(br)[None,None]
 assert torch.allclose(F.avg_pool2d(A+B,2),F.avg_pool2d(A,2)+F.avg_pool2d(B,2))
 expected=ar.reshape(2,2,2,2).transpose(0,2,1,3).max(axis=(2,3));assert np.allclose(F.max_pool2d(A,2)[0,0].numpy(),expected)
 center=rng.uniform(0,100,size=2);wh=rng.uniform(.1,20,size=2);xyxy=np.r_[center-wh/2,center+wh/2];assert np.allclose((xyxy[:2]+xyxy[2:])/2,center)
actual=json.loads((R/'audits/W07-L35-actual-source-inference.json').read_text());ds=actual['detections'];check('actual source inference one Results',actual['resultsCount']==1);check('actual source inference class sequence',[d['className']for d in ds]==['bus','person','person','person','person','stop sign']);check('actual source printed score rounding',[round(d['confidence']*100,1)for d in ds]==[87.3,86.6,85.3,82.5,26.1,25.5]);check('actual source box rounds to slide',np.allclose(np.round(ds[0]['xywh'],2),xywh))
report={'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'allPassed':True,'assertions':len(checks),'checks':checks,'variedTrials':500,'checksPerTrial':3,'torchVersion':torch.__version__,'numpyVersion':np.__version__,'inferenceReport':'audits/W07-L35-actual-source-inference.json','inferenceReportSha256':hashlib.sha256((R/'audits/W07-L35-actual-source-inference.json').read_bytes()).hexdigest(),'visualOutputInspection':{'path':'audits/code-output/W07-L35-bus-annotated.jpg','sha256':hashlib.sha256((R/'audits/code-output/W07-L35-bus-annotated.jpg').read_bytes()).hexdigest(),'inspectedAt':'2026-10-19T20:06:48Z','notes':'Actual saved 810×1080 image viewed; one bus, four person boxes and one low-score stop-sign box are visible. This is a visualization check, not ground-truth correctness.'},'scope':'Actual PyTorch/torchvision tensor and NMS operations, Results Boxes API, 500 varied numerical cases, plus recorded actual official pretrained YOLOv8n bus inference. No training or webcam access.'}
(R/'audits/W07-L35-author-code-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'allPassed':True,'assertions':len(checks),'variedTrials':500,'checksPerTrial':3}))
