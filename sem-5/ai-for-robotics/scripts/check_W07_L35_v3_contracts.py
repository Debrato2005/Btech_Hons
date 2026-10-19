"""Independent pre-key computations and actual source notebook execution for L35 v3."""
from pathlib import Path
import os,json,hashlib,datetime,contextlib,io,inspect,math,random
os.environ['YOLO_CONFIG_DIR']='/tmp/robotics-l35-contracts-v3-config';os.environ['MPLCONFIGDIR']='/tmp/robotics-l35-contracts-v3-mpl'
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import torch,numpy as np,ultralytics
from ultralytics import YOLO
from ultralytics.utils.nms import non_max_suppression
R=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();checks=[]
def check(name,actual,expected):
 assert actual==expected,(name,actual,expected);checks.append(dict(name=name,actual=actual,expected=expected))
def size(i,k,s=1,p=0):return (i-k+2*p)//s+1
h1=size(32,5);p1=size(h1,2,2);h2=size(p1,5);p2=size(h2,2,2);flat=p2*p2*32;parts=[16*(25*3+1),32*(25*16+1),128*(flat+1),10*(128+1)]
check('CNN spatial chain',[h1,p1,h2,p2,flat],[28,14,10,5,800]);check('CNN parameter components',parts,[1216,12832,102528,1290]);check('CNN total',sum(parts),117866);check('No biases distractor',sum(parts)-16-32-128-10,117680);check('One input channel first convolution distractor',sum(parts)-16*25*2,117066);check('Old flatten width distractor',parts[0]+parts[1]+128*(512+1)+parts[3],81002)
def decode(cell,v):
 x,y,w,h,_=v;cx=(cell[0]+x)*100;cy=(cell[1]+y)*100;return [cx-w*200,cy-h*200,cx+w*200,cy+h*200]
def iou(a,b):
 inter=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]));return inter/((a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-inter)
boxes={'A':decode((1,1),(.8,.5,.5,.5,.9)),'B':decode((1,1),(.9,.5,.5,.5,.8)),'C':decode((2,1),(.4,.5,.25,.25,.7))};scores={'A':.8*.9,'B':.8*.8,'C':.5*.7}
check('Decoded corners',boxes,{'A':[80.,50.,280.,250.],'B':[90.,50.,290.,250.],'C':[190.,100.,290.,200.]});check('Scores',[round(scores[k],2) for k in 'ABC'],[.72,.64,.35]);check('A-B IoU',iou(boxes['A'],boxes['B']),19/21)
def nms(sc):
 keep=[]
 for k in sorted(sc,key=sc.get,reverse=True):
  if sc[k]>.4 and all(iou(boxes[k],boxes[j])<=.5 for j in keep):keep.append(k)
 return keep
check('Class score plus NMS survivors',nms(scores),['A']);check('Raw box confidence distractor',nms(dict(A=.9,B=.8,C=.7)),['A','C']);check('Report percent',f'{.8734*100:.1f}%','87.3%')
# Execute the genuine saved notebook computation cells, not author expected results.
nbp=R/'audits/review-snapshots/W07-L35-official-notebook-contracts.ipynb';nb=json.loads(nbp.read_text());env={'plt':plt,'YOLO':YOLO};buf=io.StringIO();transforms=[]
for i in [5,7,9,11,12]:
 src=''.join(nb['cells'][i]['source']);run=src
 if i==5:
  run=run.replace('from IPython.display import Image, display','').replace("YOLO('yolov8n.pt')","YOLO('/tmp/robotics-l35-runtime/yolov8n.pt')").replace("'https://ultralytics.com/images/bus.jpg'","'/tmp/robotics-l35-runtime/bus.jpg'").replace('display(Image(url=image_source))','')
 transforms.append(dict(cell=i,sourceCodeSha256=hashlib.sha256(src.encode()).hexdigest(),executedCode=run))
 with contextlib.redirect_stdout(buf):exec(compile(run,f'actual-notebook-cell-{i}','exec'),env)
check('Notebook default save',env['model'].predictor.args.save,False);check('Notebook detection count',len(env['results'][0].boxes),6);check('Notebook bus report','Object: BUS\nConfidence: 87.3%' in buf.getvalue(),True)
shown=plt.gca().images[0].get_array();bgr=env['results'][0].plot();check('Notebook RGB reversal',np.array_equal(shown,bgr[:,:,::-1]),True);plt.savefig('/tmp/robotics-l35-v3-contracts-notebook.png');plt.close('all')
# Printed PDF variant explicitly saves while returning Results; fresh model avoids inherited predictor settings.
m=YOLO('/tmp/robotics-l35-runtime/yolov8n.pt');state={k:v.clone() for k,v in m.model.state_dict().items()}
with contextlib.redirect_stdout(buf):res=m.predict(source='/tmp/robotics-l35-runtime/bus.jpg',save=True,conf=.25,project='/tmp/robotics-l35-contracts-v3-printed',name='run',exist_ok=True,verbose=False)
check('Printed variant returns Results',type(res[0]).__name__,'Results');check('Printed variant saved output',(Path(res[0].save_dir)/'bus.jpg').is_file(),True)
# Predictor may fuse convolution/batchnorm, changing state structure without training; compare repeated inference state after fusion.
post={k:v.clone() for k,v in m.model.state_dict().items()}
with contextlib.redirect_stdout(buf):m.predict(source='/tmp/robotics-l35-runtime/bus.jpg',save=True,conf=.25,project='/tmp/robotics-l35-contracts-v3-printed',name='run',exist_ok=True,verbose=False)
check('No training updates in repeated inference',all(torch.equal(v,m.model.state_dict()[k]) for k,v in post.items()),True)
pred=torch.tensor([[[10.,30.,50.],[10.,30.,50.],[2.,2.,2.],[2.,2.,2.],[.25,.2501,.2499]]]);kept=non_max_suppression(pred.clone(),conf_thres=.25,iou_thres=.5,nc=1)[0];check('Strict confidence boundary',len(kept),1);check('Only above threshold kept',abs(float(kept[0,4])-.2501)<1e-6,True)
# Varied numerical invariants: CNN shape enumeration and IoU scaling preserve distinct laws.
rng=random.Random(3503)
for _ in range(1000):
 i=rng.randint(20,100);k=rng.randint(1,7);s=rng.randint(1,4);p=rng.randint(0,3);expected=len(list(range(0,i+2*p-k+1,s)));assert size(i,k,s,p)==expected
 scale=rng.uniform(.1,10);assert math.isclose(iou([x*scale for x in boxes['A']],[x*scale for x in boxes['B']]),19/21,rel_tol=1e-12)
out=dict(reviewerId='robotics-contracts-independent-reviewer',completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase='Before current keyed content; prior revision exposure disclosed separately',assertionCount=len(checks),variedCases=1000,variedAssertions=2000,checks=checks,cnnShapes=[h1,p1,h2,p2,flat],cnnParameterComponents=parts,yoloBoxes=boxes,yoloScores=scores,yoloIoUAB=iou(boxes['A'],boxes['B']),notebookPath=str(nbp.relative_to(R)),notebookSha256=sha(nbp),notebookExecutedCells=transforms,setupOmission='Cell 2 Colab installer and IPython-only display omitted; installed runtime and Agg plotting supplied. Local paths replace same original assets. No installation or source modification.',versions={'ultralytics':ultralytics.__version__,'torch':torch.__version__},inputSha256=sha('/tmp/robotics-l35-runtime/bus.jpg'),modelSha256=sha('/tmp/robotics-l35-runtime/yolov8n.pt'),executionOutput=buf.getvalue(),thresholdSourceLines=[l.strip() for l in inspect.getsource(non_max_suppression).splitlines() if '> conf_thres' in l],renderPath='/tmp/robotics-l35-v3-contracts-notebook.png',renderSha256=sha('/tmp/robotics-l35-v3-contracts-notebook.png'),predictionWeightQualification='Inference may fuse layers structurally; no optimizer or training updates are invoked. State equality was checked across repeated post-fusion inference.')
p=R/'audits/W07-L35-v3-contracts-independent-checks.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(checks),'explicit checks and 2000 varied assertions; original notebook computation cells executed.')
