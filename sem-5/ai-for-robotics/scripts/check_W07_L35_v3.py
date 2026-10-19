#!/usr/bin/env python3
"""Author-only exact L35 v3 calculations and installed-runtime checks, not independent review."""
import json,hashlib,inspect,io,contextlib,random,os
from pathlib import Path
from fractions import Fraction as F
R=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR','/tmp/robotics-l35-v3-mpl');os.environ['MPLBACKEND']='Agg'
import numpy as np,torch,ultralytics
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ultralytics.utils.nms import non_max_suppression
from ultralytics.engine.model import Model
from ultralytics.engine.results import Results
checks=[]
def check(name,p):
 assert bool(p),name;checks.append(name)
def out(i,k,s=1,p=0):return (i-k+2*p)//s+1
shapes=[];i=32
for k,s,c in [(5,1,16),(2,2,16),(5,1,32),(2,2,32)]:i=out(i,k,s);shapes.append([i,i,c])
counts=[(5*5*3+1)*16,(5*5*16+1)*32,(5*5*32+1)*128,(128+1)*10]
check('CNN spatial chain and flatten width',shapes==[[28,28,16],[14,14,16],[10,10,32],[5,5,32]]and i*i*32==800)
check('CNN four parameter counts and sum',counts==[1216,12832,102528,1290]and sum(counts)==117866)
check('CNN credible distractor totals',sum([416,*counts[1:]])==117066 and sum(counts)-(16+32+128+10)==117680 and sum([*counts[:2],(512+1)*128,counts[3]])==81002)
net=torch.nn.Sequential(torch.nn.Conv2d(3,16,5),torch.nn.ReLU(),torch.nn.MaxPool2d(2),torch.nn.Conv2d(16,32,5),torch.nn.ReLU(),torch.nn.MaxPool2d(2),torch.nn.Flatten(),torch.nn.Linear(800,128),torch.nn.ReLU(),torch.nn.Linear(128,10))
check('CNN actual torch parameter count',sum(p.numel()for p in net.parameters())==117866)
with torch.no_grad(): y=net(torch.zeros(1,3,32,32))
check('CNN actual torch output shape',list(y.shape)==[1,10])
def decode(col,row,x,y,w,h,cell=100,W=400,H=400):
 cx=(col+x)*cell;cy=(row+y)*cell;bw=w*W;bh=h*H
 return(cx-bw/2,cy-bh/2,cx+bw/2,cy+bh/2)
def iou(a,b):
 I=max(F(0),min(a[2],b[2])-max(a[0],b[0]))*max(F(0),min(a[3],b[3])-max(a[1],b[1]));aa=(a[2]-a[0])*(a[3]-a[1]);bb=(b[2]-b[0])*(b[3]-b[1]);return I/(aa+bb-I)
boxes={'A':decode(1,1,F(8,10),F(1,2),F(1,2),F(1,2)),'B':decode(1,1,F(9,10),F(1,2),F(1,2),F(1,2)),'C':decode(2,1,F(4,10),F(1,2),F(1,4),F(1,4))};scores={'A':F(9,10)*F(8,10),'B':F(8,10)*F(8,10),'C':F(7,10)*F(5,10)}
check('YOLO all decoded corners',boxes=={'A':(80,50,280,250),'B':(90,50,290,250),'C':(190,100,290,200)})
check('YOLO all class scores',scores=={'A':F(72,100),'B':F(64,100),'C':F(35,100)})
check('YOLO pair overlaps',iou(boxes['A'],boxes['B'])==F(19,21)and iou(boxes['A'],boxes['C'])==F(9,41))
def nms(b,s,threshold=F(4,10)):
 ordered=sorted([k for k in b if s[k]>threshold],key=lambda k:s[k],reverse=True);keep=[]
 while ordered:
  k=ordered.pop(0);keep.append(k);ordered=[j for j in ordered if iou(b[k],b[j])<=F(1,2)]
 return keep
check('YOLO confidence filter then NMS',nms(boxes,scores)==['A'])
wrongboxes={k:decode(c,r,x,y,w,h,W=100,H=100)for k,c,r,x,y,w,h in [('A',1,1,F(8,10),F(1,2),F(1,2),F(1,2)),('B',1,1,F(9,10),F(1,2),F(1,2),F(1,2)),('C',2,1,F(4,10),F(1,2),F(1,4),F(1,4))]}
check('YOLO cell-normalized size distractor',wrongboxes['A']==(155,125,205,175)and nms(wrongboxes,scores)==['A'])
check('YOLO box-confidence-only distractor',nms(boxes,{'A':F(9,10),'B':F(8,10),'C':F(7,10)})==['A','C'])
check('YOLO no-intersection-subtraction distractor',F(38000,80000)==F(475,1000)and F(475,1000)<F(1,2))
# Exact scale/translation invariance and two equivalent independent area expressions.
rng=random.Random(3503)
for _ in range(500):
 scale=F(rng.randint(1,100),rng.randint(1,100));dx=F(rng.randint(-500,500));dy=F(rng.randint(-500,500))
 transformed={k:(a[0]*scale+dx,a[1]*scale+dy,a[2]*scale+dx,a[3]*scale+dy)for k,a in boxes.items()}
 assert iou(transformed['A'],transformed['B'])==F(19,21)
 assert nms(transformed,scores)==['A']
checks.append('500 exact transformed YOLO cases, 1000 assertions')
# Ordinary single-class prediction shape (batch,4+nc,anchors), not end-to-end six-column shortcut.
pred=torch.tensor([[[10.,30.,50.],[10.,10.,10.],[2.,2.,2.],[2.,2.,2.],[.25,.2501,.2499]]])
ret=non_max_suppression(pred,conf_thres=.25,nc=1)[0]
check('Installed NMS threshold equality excluded',ret.shape[0]==1 and abs(ret[0,4].item()-.2501)<1e-7 and ret[0,0].item()==29.)
nbpath=R/'audits/review-snapshots/W07-L35-official-notebook-contracts.ipynb';nb=json.loads(nbpath.read_text());nbsha=hashlib.sha256(nbpath.read_bytes()).hexdigest()
check('Unmodified official notebook hash',nbsha=='5f2680c5d1089be24f5b5cc17e1429761777af79e47b31ab62f381150485881c')
source5=''.join(nb['cells'][5]['source']);adapted5=source5.replace('from IPython.display import Image, display','').replace("YOLO('yolov8n.pt')","YOLO('/tmp/robotics-l35-runtime/yolov8n.pt')").replace("'https://ultralytics.com/images/bus.jpg'","'/tmp/robotics-l35-runtime/bus.jpg'").replace('display(Image(url=image_source))','')
ns={'plt':plt};log=io.StringIO()
with contextlib.redirect_stdout(log):
 exec(compile(adapted5,'L35-original-cell-5-with-declared-local-asset-adaptations','exec'),ns)
 for c in [7,9,11,12]:exec(compile(''.join(nb['cells'][c]['source']),f'L35-original-cell-{c}','exec'),ns)
result=ns['results'][0];boxes_runtime=ns['boxes'];report=log.getvalue()
check('Actual notebook returns six structured detections',len(boxes_runtime)==6 and isinstance(result,Results))
check('Actual notebook save default is false',ns['model'].predictor.args.save is False)
check('Actual notebook class and confidence formatting','Object: BUS\nConfidence: 87.3%\n' in report and 'Object: STOP SIGN\nConfidence: 25.5%\n'in report)
check('Actual notebook xywh rounding','Coordinates (x, y, w, h): [413.94, 494.06, 782.13, 525.56]'in report)
plotted=plt.gca().images[0].get_array();expected=result.plot()[:,:,::-1]
check('Actual notebook display reverses BGR to RGB',np.array_equal(plotted,expected))
# This artifact write is author harness only; the source notebook calls plt.show(), not savefig.
render=R/'audits/W07-L35-v3-notebook-display.png';plt.gcf().savefig(render,dpi=120,bbox_inches='tight');plt.close('all')
(R/'audits/W07-L35-v3-notebook-stdout.txt').write_text(report)
primary=[]
for f in [non_max_suppression,Results.plot,Model.predict]:
 path=Path(inspect.getsourcefile(f));lines,start=inspect.getsourcelines(f);primary.append(dict(symbol=f.__qualname__,path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),startLine=start,endLine=start+len(lines)-1,extract=[{'line':i,'text':l.rstrip()}for i,l in enumerate(lines,start)if ('conf_thres'in l and '>'in l)or('save'in l and ('is_cli'in l or'False'in l))or'BGR'in l]))
data={'authorId':'L35-repair-author-20261019','independentVerification':False,'passed':True,'checks':checks,'checkGroups':len(checks),'variedCases':500,'variedAssertions':1000,'cnn':{'shapes':shapes,'parameters':counts,'total':sum(counts)},'yolo':{'decoded':{k:list(map(str,v))for k,v in boxes.items()},'scores':{k:str(v)for k,v in scores.items()},'AB_IoU':'19/21','AC_IoU':'9/41','survivors':['A']},'runtime':{'python':os.sys.executable,'ultralytics':ultralytics.__version__,'torch':torch.__version__,'numpy':np.__version__,'primaryCode':primary,'confidenceProbeRetained':ret.tolist(),'notebookPath':str(nbpath.relative_to(R)),'notebookSha256':nbsha,'codeCellsExecuted':[5,7,9,11,12],'unchangedCodeCellsExecuted':[7,9,11,12],'cell5Adaptations':['Local verified model path','Local verified image path','Omit unavailable IPython import and input display only'],'optionalSetupCellNotExecuted':2,'noInstallation':True,'sourceSaveFlag':bool(ns['model'].predictor.args.save),'authorHarnessSavedDisplay':str(render.relative_to(R)),'authorHarnessSaveIsNotNotebookBehavior':True,'displaySha256':hashlib.sha256(render.read_bytes()).hexdigest(),'detections':len(boxes_runtime)}}
(R/'audits/W07-L35-v3-author-computations.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(len(checks),'groups; 500 cases; all passed')
