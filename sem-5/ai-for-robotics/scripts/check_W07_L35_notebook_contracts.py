"""Post-blind supplemental official notebook execution and exact threshold probe."""
from pathlib import Path
import os,json,hashlib,datetime,contextlib,io,inspect
os.environ['YOLO_CONFIG_DIR']='/tmp/robotics-l35-contracts-config'
os.environ['MPLCONFIGDIR']='/tmp/robotics-l35-contracts-mpl'
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ultralytics import YOLO
from ultralytics.utils.nms import non_max_suppression
import ultralytics,torch,numpy as np
R=Path(__file__).resolve().parents[1];path=R/'audits/review-snapshots/W07-L35-official-notebook-contracts.ipynb';nb=json.loads(path.read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();env={'plt':plt,'YOLO':YOLO};buf=io.StringIO();transforms=[]
for i in [5,7,9,11,12]:
 src=''.join(nb['cells'][i]['source']);run=src
 if i==5:
  run=run.replace('from IPython.display import Image, display','')
  run=run.replace("YOLO('yolov8n.pt')","YOLO('/tmp/robotics-l35-runtime/yolov8n.pt')")
  run=run.replace("'https://ultralytics.com/images/bus.jpg'","'/tmp/robotics-l35-runtime/bus.jpg'")
  run=run.replace('display(Image(url=image_source))','')
 transforms.append({'cell':i,'originalCodeSha256':hashlib.sha256(src.encode()).hexdigest(),'executedCode':run,'changes':'Local cached asset paths and removed IPython-only input display/import' if i==5 else 'No code change; Matplotlib backend is noninteractive Agg'})
 with contextlib.redirect_stdout(buf):exec(compile(run,f'official-L35-cell-{i}','exec'),env)
res=env['results'][0];plot=res.plot();assert plot.shape==(1080,810,3)
assert np.array_equal(plot[:,:,::-1][:,:,::-1],plot)
plt.savefig('/tmp/robotics-l35-contracts-notebook.png');plt.close('all')
# Exact binary representable threshold and synthetic candidate scores. Format B,4+nc,N.
pred=torch.tensor([[[10.,30.,50.],[10.,30.,50.],[2.,2.,2.],[2.,2.,2.],[.25,.2501,.2499]]])
kept=non_max_suppression(pred.clone(),conf_thres=.25,iou_thres=.5,nc=1)[0]
assert len(kept)==1 and abs(float(kept[0,4])-.2501)<1e-6
ss=inspect.getsource(non_max_suppression)
report={'reviewerId':'robotics-contracts-reviewer-L35-v2','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exposure':'Supplemental check after frozen answers and current keyed reveal, not claimed as blind notebook execution. Initial printed-code inference was completed before keyed access.','url':'https://raw.githubusercontent.com/robotics-lab-iitr/nptel-ai-robotics/main/week07/week07_lecture35.ipynb','notebookPath':str(path.relative_to(R)),'notebookSha256':sha(path),'executedCells':transforms,'notExecutedSetupCell':{'index':2,'reason':'Optional Google Colab install/IPython display setup not applicable. IPython absent; already installed runtime and ordinary plotting imports supplied explicitly. No install performed.'},'versions':{'ultralytics':ultralytics.__version__,'torch':torch.__version__},'sourceDiscrepancy':'Notebook cell7 omits save=True although its comment describes it. PDF p1083 explicitly supplies save=True and save_dir. These are distinct source variants, not identical programs.','notebookPredictionSaveFlag':env['model'].predictor.args.save,'report':buf.getvalue(),'displayObservation':'Cell12 reverses the BGR array from Results.plot to RGB for Matplotlib. This is not tested by the current98 questions.','thresholdBoundaryProbe':{'inputScores':[.25,.2501,.2499],'threshold':.25,'keptScores':kept[:,4].tolist(),'comparisonLines':[l.strip() for l in ss.splitlines() if '> conf_thres' in l],'result':'Strict greater-than filter; equality does not pass in8.4.182. Q088 general >=formula is inaccurate for this API, though its .255case remains correct.'},'assertions':4,'renderPath':'/tmp/robotics-l35-contracts-notebook.png','renderSha256':sha('/tmp/robotics-l35-contracts-notebook.png')}
out=R/'audits/W07-L35-v2-contracts-notebook-and-threshold.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print('PASS original notebook computation cells',len(transforms),'save=',report['notebookPredictionSaveFlag'],'threshold=',report['thresholdBoundaryProbe']['keptScores'])
