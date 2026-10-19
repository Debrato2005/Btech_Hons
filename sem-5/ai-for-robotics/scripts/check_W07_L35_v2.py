#!/usr/bin/env python3
"""L35 repair-author calculations/API checks, NOT independent verification."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,datetime,inspect,math,shutil,os
import numpy as np,torch,torch.nn as nn,torch.nn.functional as tf
from torchvision.ops import batched_nms
import ultralytics
from ultralytics import YOLO
from ultralytics.engine.results import Boxes
from ultralytics.nn.modules.head import Detect
from ultralytics.utils.tal import dist2bbox
R=Path(__file__).resolve().parents[1];torch.set_num_threads(2);checks=[]
def ck(name,ok,detail):
 assert bool(ok),name
 checks.append(dict(name=name,passed=True,detail=detail,independent=False))
count=lambda m:sum(p.numel()for p in m.parameters())
ck('Dense question and all alternatives',[78500,78400,785000,88400]==[(784+1)*100,784*100,(784+1)*1000,784*100+10000],'Correct one bias per neuron; alternatives omit biases, substitute1000outputs, or add10000biases.')
ck('Correlation correct and all foils',sum(x*k for x,k in zip([1,2,3,4],[1,0,0,-1]))==-3 and sum(x*k for x,k in zip([1,2,3,4],[-1,0,0,1]))==3 and 1-3==-2 and sum([1,2,3,4])==10,'Unflipped−3; rotated3; wrong first-column contrast−2; unweighted sum10.')
ck('Convolution first count and alternatives',[416,400,9216,432]==[(25+1)*16,25*16,24*24*16,400+16+16],'ReLU contributes no separate bias.')
ck('Stride correct and all alternatives',[3,F(7,2),4,6]==[math.floor(F(8-3,2))+1,F(8-3,2)+1,math.ceil(F(8-3,2))+1,(8-3)+1],'Floor3, no-floor3.5, ceil4, stride1gives6.')
M=torch.tensor([[8.,16,8,20],[13,3,14,6],[20,14,2,14],[6,32,6,22]])[None,None]
ck('Pooling matrix outputs',tf.max_pool2d(M,2,2)[0,0].tolist()==[[16,20],[32,22]] and tf.avg_pool2d(M,2,2)[0,0].tolist()==[[10,12],[18,11]],'Four window sums40,48,72,44; divide by4 for averages.')
ck('Pooling numeric foils',M[0,0,::2,::2].tolist()==[[8,8],[20,2]] and [[40/2,48/2],[72/2,44/2]]==[[20,24],[36,22]],'Top-left samples and divide-by2 foils reproduced.')
ck('Max nonadditivity counterexample',max([1,0])+max([0,1])==2 and max([1,1])==1,'Average linearity is a fixed weighted sum; max fails additivity.')
ck('ReLU values and foils',tf.relu(torch.tensor([-2.,0,3])).tolist()==[0,0,3] and torch.abs(torch.tensor([-2.,0,3])).tolist()==[2,0,3],'Identity, absolute-value and unit-clipped outputs are distinct.')
c1=nn.Conv2d(1,16,5);c2=nn.Conv2d(16,32,5);d1=nn.Linear(512,128);d2=nn.Linear(128,10)
x=torch.zeros(1,1,28,28);a=c1(x);p1=tf.max_pool2d(a,2);a2=c2(p1);p2=tf.max_pool2d(a2,2)
ck('Actual CNN shape trace',[list(t.shape)for t in[a,p1,a2,p2]]==[[1,16,24,24],[1,16,12,12],[1,32,8,8],[1,32,4,4]],'Ordinary convolution and fixed pooling reproduce the lecture shapes.')
ck('Actual learned layer counts',[count(m)for m in[c1,c2,d1,d2]]==[416,12832,65664,1290],'Actual PyTorch modules count the supplied biases.')
ck('Second convolution alternatives',[12832,832,12800,204832]==[(25*16+1)*32,(25+1)*32,25*16*32,(25*16*16+1)*32],'Correct; missing input channels; omitted bias; squared input-channel factor.')
ck('Flatten options',[512,128,16,2048]==[4*4*32,4*32,4*4,8*8*32],'Correct count and missing-axis/channel/prior-map alternatives.')
ck('Hidden dense alternatives',[65664,65536,16512,65546]==[(512+1)*128,512*128,(128+1)*128,512*128+10],'Hidden bias versus output bias distinctions.')
ck('Output dense alternatives',[1290,1280,1408,138]==[(128+1)*10,128*10,128*10+128,128+10],'Correct, no bias, input biases, additive widths.')
total=sum(count(m)for m in[c1,c2,d1,d2]);ck('Total count alternatives',[80202,80016,79690,89418]==[total,total-186,total-512,total+9216],'Bias count186;512flattenactivations;9216firstconvactivations.')
ck('Padding and output length',nn.Conv2d(1,1,5,padding=2)(torch.zeros(1,1,8,8)).shape[-1]==8 and nn.Conv2d(1,1,3,stride=2)(torch.zeros(1,1,8,8)).shape[-1]==3,'Odd-kernel size preservation and floor operation tested.')
ck('Channel connectivity groups',list(nn.Conv2d(16,32,5).weight.shape)==[32,16,5,5] and list(nn.Conv2d(16,32,5,groups=2).weight.shape)==[32,8,5,5],'Full convolution spans16;two groups spans8perfilter.')
ck('1x1 spatial/channel distinction',list(nn.Conv2d(16,8,1)(torch.zeros(1,16,7,9)).shape)==[1,8,7,9],'Channels reduced without spatial downsampling.')
ck('Activation normalization',torch.allclose(torch.softmax(torch.tensor([2.,2.]),0).sum(),torch.tensor(1.)) and torch.sigmoid(torch.tensor([2.,2.])).sum()>1,'Separate sigmoids need not sum to1.')
ck('Cell conversion and all options',[(2+F(1,4))*100,(3+F(1,2))*100]==[225,350] and [F(1,4)*100,F(1,2)*100]==[25,50] and [F(1,4)*700,F(1,2)*700]==[175,350],'Omitting cell offset, image-normalized offsets, or swapped coordinates explain foils.')
ck('IoU limits',F(0,5)==0 and F(5,5)==1,'Positive union required; zero intersection vsidenticalregions.')
ck('Confidence and class-score products',F(8,10)*F(5,10)==F(4,10) and F(7,10)*F(4,10)==F(28,100),'Foils keep one factor or add factors1.3and1.1instead ofmultiplying.')
ck('Original tensor dimensions',5*2+20==30 and 2*(5+20)==50 and 5+20==25 and 7*7*30==1470 and 7*7*2==98,'One class vector per cell; candidate boxes are not scalar count.')
boxes=torch.tensor([[0.,0,10,10],[1,1,11,11]]);scores=torch.tensor([.9,.8]);classes=torch.tensor([0,1])
ck('Actual NMS policy distinction',batched_nms(boxes,scores,classes,.5).tolist()==[0,1] and batched_nms(boxes,scores,torch.zeros(2),.5).tolist()==[0],'Class-aware keeps different-class boxes; agnostic suppresses lower score.')
ck('Three supplied stride grids',[640//s for s in[8,16,32]]==[80,40,20] and [640//s for s in[2,4,8]]==[320,160,80],'Stride values themselves are not map sizes.')
cx,cy,w,h=map(F,['413.94','494.06','782.13','525.56']);xy=[cx-w/2,cy-h/2,cx+w/2,cy+h/2]
ck('Exact rounded bus corners',xy==list(map(F,['22.875','231.28','805.005','756.84'])),'Exact rational arithmetic, not binary-rounding assumptions.')
ck('Bus corner all foils',[cx,cy,cx+w,cy+h]==list(map(F,['413.94','494.06','1196.07','1019.62'])) and [xy[0],xy[1],w,h]==list(map(F,['22.875','231.28','782.13','525.56'])),'Top-left misinterpretation, half-conversion and x/y permutation are distinct.')
ck('Threshold fixed score',F(255,1000)>F(25,100),'0.255passes0.25;notcalibrationproof.')
ck('Repeated block correct and foils',[10,6,8,14]==[2*4+2,4+2,2*4,3*4+2],'Four repeats count pairs,notindividual/single/triplelayers.')
ck('Later repeat and total counts',2*2+2==6 and sum([1,1,4,10,6,2])==24 and 24+2==26 and 24+4==28,'Six-conv later block;24conv plus2dense;poolingnotconv.')
api=Boxes(torch.tensor([[float(v)for v in xy]+[.873,5]],dtype=torch.float64),(1080,810))
ck('Actual Boxes field meanings',np.allclose(api.xywh[0].numpy(),[413.94,494.06,782.13,525.56]) and api.cls.item()==5 and abs(api.conf.item()-.873)<1e-12,'Geometry/score/class-index fields independently read.')
ck('Reference-point distance decode',torch.equal(dist2bbox(torch.tensor([[2.,3.,4.,5.]]),torch.tensor([[10.,20.]]),xywh=False),torch.tensor([[8.,17.,14.,25.]])),'Left/top/right/bottomdistancesaroundreferencepointgiveextentaswellasposition.')
rng=np.random.default_rng(351926)
for i in range(500):
 ar=rng.normal(size=(4,4));br=rng.normal(size=(4,4));alpha,beta=rng.normal(size=2)
 ta=torch.tensor(ar)[None,None];tb=torch.tensor(br)[None,None]
 assert torch.allclose(tf.avg_pool2d(alpha*ta+beta*tb,2),alpha*tf.avg_pool2d(ta,2)+beta*tf.avg_pool2d(tb,2))
 assert np.allclose(tf.max_pool2d(ta,2)[0,0].numpy(),ar.reshape(2,2,2,2).transpose(0,2,1,3).max(axis=(2,3)))
 center=rng.uniform(0,100,size=2);extent=rng.uniform(.1,20,size=2);xyxy=np.r_[center-extent/2,center+extent/2]
 assert np.allclose((xyxy[:2]+xyxy[2:])/2,center)
ck('500 varied tensor/coordinate cases',True,'Eachcasechecksaveragelinearity,max-windowselection,centerconversion.')
# Actual source inference uses existing local inputs and installed package; no download or install.
os.environ['YOLO_CONFIG_DIR']='/tmp/robotics-l35-repair-v2-settings'
model=YOLO('/tmp/robotics-l35-runtime/yolov8n.pt')
def weights_hash():
 h=hashlib.sha256()
 for p in model.model.parameters():h.update(p.detach().cpu().numpy().tobytes())
 return h.hexdigest()
before=weights_hash();results=model.predict('/tmp/robotics-l35-runtime/bus.jpg',save=True,conf=.25,device='cpu',project='/tmp/robotics-l35-repair-v2-output',name='bus',exist_ok=True,verbose=False);r=results[0]
ck('Actual local source inference and no parameter update',weights_hash()==before and len(results)==1 and len(r.boxes)==6,'ReturnedoneResultswithsixboxes;parameterbytesunchanged.')
ck('Prediction output directory',Path(r.save_dir).is_dir() and (Path(r.save_dir)/'bus.jpg').exists(),'save_dir isdirectory containingannotatedimage,notcheckpoint/inputpath.')
ck('Printed scores reproduced to precision',[round(float(v)*100,1)for v in r.boxes.conf]==[87.3,86.6,85.3,82.5,26.1,25.5],'Singleexampleonly;nogroundtruthoraccuracyclaim.')
dest=R/'audits/code-output/W07-L35-v2-bus-annotated.jpg';shutil.copyfile(Path(r.save_dir)/'bus.jpg',dest)
pkg=Path(ultralytics.__file__).parent
files=['engine/results.py','engine/model.py','engine/predictor.py','nn/modules/head.py','utils/tal.py','cfg/models/v8/yolov8.yaml']
report={'authorId':'L35-repair-author-20261019','independentReview':False,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'allPassed':True,'checkGroups':len(checks),'checks':checks,'randomCases':500,'assertionsPerRandomCase':3,'runtimeVersions':{'torch':torch.__version__,'ultralytics':ultralytics.__version__,'numpy':np.__version__},'installedSourceFiles':[{'packageRelativePath':str(p),'sha256':hashlib.sha256((pkg/p).read_bytes()).hexdigest()}for p in files],'outputImage':str(dest.relative_to(R)),'outputImageSha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'inferenceInputs':{p:hashlib.sha256(Path('/tmp/robotics-l35-runtime',p).read_bytes()).hexdigest()for p in['bus.jpg','yolov8n.pt']},'scope':'Repair-author exact mathematics, tensor/API behavior and one local source inference. No independent approval or general accuracy validation.'}
(R/'audits/W07-L35-v2-author-computations.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k]for k in['allPassed','checkGroups','randomCases','runtimeVersions','outputImage']}))
