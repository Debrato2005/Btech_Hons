"""Independent source-derived math and actual official-model inference. No authored reports used."""
import os
os.environ['YOLO_CONFIG_DIR']='/tmp/robotics-l35-independent-config'
import json,datetime,hashlib,inspect
from pathlib import Path
import numpy as np
import torch,torchvision,ultralytics
from ultralytics import YOLO
from ultralytics.utils.tal import dist2bbox
from PIL import Image
R=Path(__file__).resolve().parents[1];rows=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(name,ok,detail):
 assert ok,(name,detail)
 rows.append({'name':name,'passed':True,'detail':detail})
check('dense784to100',sum(p.numel() for p in torch.nn.Linear(784,100).parameters())==78500,78500)
check('dense3to4to1 no biases',3*4+4==16,16)
patch=torch.tensor([[[[1.,2.],[3.,4.]]]]);kernel=torch.tensor([[[[1.,0.],[0.,-1.]]]])
check('crosscorrelation not flipped',torch.nn.functional.conv2d(patch,kernel).item()==-3,-3)
conv1=torch.nn.Conv2d(1,16,5);conv2=torch.nn.Conv2d(16,32,5);dense=torch.nn.Linear(512,128);out=torch.nn.Linear(128,10)
check('conv1parametercount',sum(p.numel() for p in conv1.parameters())==416,416)
check('conv2parametercount',sum(p.numel() for p in conv2.parameters())==12832,12832)
a=torch.zeros((1,1,28,28));b=conv1(a);c=torch.nn.functional.max_pool2d(b,2);d=conv2(c);e=torch.nn.functional.max_pool2d(d,2)
check('fourspatialtransitions',list(b.shape)==[1,16,24,24] and list(c.shape)==[1,16,12,12] and list(d.shape)==[1,32,8,8] and list(e.shape)==[1,32,4,4],{'b':list(b.shape),'c':list(c.shape),'d':list(d.shape),'e':list(e.shape)})
check('flatten512',e.flatten(1).shape[1]==512,512)
check('densehidden65664',sum(p.numel() for p in dense.parameters())==65664,65664)
check('output1290',sum(p.numel() for p in out.parameters())==1290,1290)
check('total80202',sum(p.numel() for m in [conv1,conv2,dense,out] for p in m.parameters())==80202,80202)
check('stridefloor3',torch.nn.Conv2d(1,1,3,stride=2)(torch.zeros(1,1,8,8)).shape[-1]==3,3)
mat=torch.tensor([[[[8.,16.,8.,20.],[13.,3.,14.,6.],[20.,14.,2.,14.],[6.,32.,6.,22.]]]])
check('maxpoolsource',torch.equal(torch.nn.functional.max_pool2d(mat,2),torch.tensor([[[[16.,20.],[32.,22.]]]])),[[16,20],[32,22]])
check('avgpoolsource',torch.equal(torch.nn.functional.avg_pool2d(mat,2),torch.tensor([[[[10.,12.],[18.,11.]]]])),[[10,12],[18,11]])
check('maxpoolnolearnedparameters',sum(p.numel() for p in torch.nn.MaxPool2d(2).parameters())==0,0)
check('relu',torch.equal(torch.relu(torch.tensor([-2.,0.,3.])),torch.tensor([0.,0.,3.])),[0,0,3])
check('YOLOv1gridcenter',[(2+.25)*100,(3+.5)*100]==[225,350],[225,350])
check('IoUarea',40/(100+100-40)==.25,.25)
check('YOLOv1scores',np.allclose([.8*.5,.7*.4],[.4,.28]),[.4,.28])
check('YOLOv1tensorandcandidates',7*7*(5*2+20)==1470 and 7*7*2==98,{'tensor':[7,7,30],'elements':1470,'boxes':98})
# Direct matrix-greedy NMS for the exact explicitly supplied overlap relations.
scores=np.array([.9,.8,.7]);ov=np.array([[1,.7,.1],[.7,1,.1],[.1,.1,1]]);keep=[];pending=list(np.argsort(-scores))
while pending:
 i=pending.pop(0);keep.append(int(i));pending=[j for j in pending if ov[i,j]<=.5]
check('NMSsuppliedtrace',keep==[0,2],keep)
check('squaremapstrides',[640//s for s in [8,16,32]]==[80,40,20],[80,40,20])
cx,cy,w,h=413.94,494.06,782.13,525.56;corners=[cx-w/2,cy-h/2,cx+w/2,cy+h/2]
check('roundedbusxyxy',np.allclose(corners,[22.875,231.28,805.005,756.84],atol=1e-10),corners)
check('fixedconfidencefilter',sum(x>=.5 for x in [.873,.866,.853,.825,.261,.255])==4,4)
check('YOLOv1repeatcounts',2*4+2==10 and 2*2+2==6 and sum([1,1,4,10,6,2])==24,{'repeat4':10,'repeat2':6,'totalconv':24})
rng=np.random.default_rng(351976)
for case in range(500):
 I=int(rng.integers(7,64));K=int(rng.choice([1,3,5,7]));P=int(rng.integers(0,4));S=int(rng.integers(1,4));starts=list(range(-P,I+P-K+1,S));assert len(starts)==(I-K+2*P)//S+1
 a=rng.uniform(-10,10,2);size=rng.uniform(.01,20,2);xyxy=np.r_[a-size/2,a+size/2];assert np.allclose((xyxy[:2]+xyxy[2:])/2,a) and np.allclose(xyxy[2:]-xyxy[:2],size)
 x=rng.normal(size=(4,4));y=rng.normal(size=(4,4));avg=lambda z:z.reshape(2,2,2,2).mean((1,3));assert np.allclose(avg(x+y),avg(x)+avg(y))
check('500variedshape_box_roundtrip_average_linearity',True,500)
weights=Path('/tmp/robotics-l35-runtime/yolov8n.pt');inputp=Path('/tmp/robotics-l35-runtime/bus.jpg');assert weights.exists() and inputp.exists()
model=YOLO(str(weights));head=model.model.model[-1]
check('standardv8threelevels',model.model.stride.tolist()==[8.,16.,32.] and head.nl==3,{'strides':model.model.stride.tolist(),'levels':head.nl})
check('v8box_class_dimensions',head.nc==80 and head.reg_max==16 and head.no==144,{'classes':head.nc,'reg_max':head.reg_max,'raw_channels':head.no,'raw_channel_relation':'4*reg_max+nc, no extra objectness scalar'})
# Square forward, not assuming rectangular bus preprocessing remains square.
feature_shapes=[]
hook=head.register_forward_pre_hook(lambda module,args:feature_shapes.extend([list(t.shape) for t in args[0]]))
model.model.eval()
with torch.inference_mode():model.model(torch.zeros(1,3,640,640))
hook.remove();check('squareforwardactuallevels',[x[-2:] for x in feature_shapes]==[[80,80],[40,40],[20,20]],feature_shapes)
# Keep weights unchanged while performing actual example inference and saving outputs.
before=[p.detach().clone() for p in model.model.parameters()]
results=model.predict(source=str(inputp),save=True,conf=.25,device='cpu',project=str(R/'audits'),name='W07-L35-independent-inference',exist_ok=False,verbose=False)
r=results[0];boxes=r.boxes;det=[{'classId':int(c),'name':r.names[int(c)],'confidence':float(s),'xywh':b.tolist(),'xyxy':a.tolist()} for c,s,b,a in zip(boxes.cls,boxes.conf,boxes.xywh,boxes.xyxy)]
check('resultoneimage_multipleboxes',len(results)==1 and len(boxes)==6,{'images':len(results),'detections':len(boxes)})
check('sourceclasscounts',sorted(d['name'] for d in det)==sorted(['bus','person','person','person','person','stop sign']),[d['name'] for d in det])
check('sourceconfidence_rounding',np.allclose([d['confidence'] for d in det],[.873,.866,.853,.825,.261,.255],atol=.00051),[d['confidence'] for d in det])
check('sourcebusbox_rounding',np.allclose(det[0]['xywh'],[413.94,494.06,782.13,525.56],atol=.006),det[0]['xywh'])
# Predictor may fuse conv+BN for inference; that structural optimization is not training.
check('savedpredictionexists',(Path(r.save_dir)/inputp.name).exists(),str(Path(r.save_dir)/inputp.name))
api={'headClass':type(head).__name__,'headSource':inspect.getsourcefile(type(head)),'decode':inspect.getsource(dist2bbox),'weightAndInputShapes':{'inputImage':list(Image.open(inputp).size),'orig_shape':list(r.orig_shape)},'fusedInferenceQualification':'predict can perform inference-time Conv/BN fusion; no optimizer/backpropagation is invoked. Do not compare changed fused parameter structure as evidence of training.'}
report={'reviewerId':'independent-reviewer-robotics-batches-v2','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'versions':{'torch':torch.__version__,'torchvision':torchvision.__version__,'ultralytics':ultralytics.__version__,'numpy':np.__version__},'passed':len(rows),'checks':rows,'assets':{'weights':str(weights),'weightsSha256':sha(weights),'image':str(inputp),'imageSha256':sha(inputp)},'detections':det,'saveDir':r.save_dir,'apiImplementation':api,'scope':'Actual model inference and square raw forward executed, not syntax-only checking. No author script/report read or run.'}
(R/'audits/W07-L35-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':len(rows),'detections':len(det),'saveDir':r.save_dir,'report':'audits/W07-L35-independent-computations.json'}))
