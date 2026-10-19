#!/usr/bin/env python3
"""Execute visually transcribed source code in existing default runtime, never original notebook claim."""
from pathlib import Path
import sys,json,datetime,hashlib,time,contextlib,io,warnings
assert not sys.prefix.startswith('/tmp/robotics-l35-venv'),'Restricted runtime'
import numpy as np,scipy,sklearn
R=Path(__file__).resolve().parents[1];O=R/'audits/W11-L54-full-code-author.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write():O.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
report={'batchId':'W11-L54','status':'running_author_check','startedAt':now(),'interpreter':sys.executable,'packages':{m.__name__:{'version':m.__version__,'file':m.__file__,'fileSha256':sha(Path(m.__file__))}for m in[np,scipy,sklearn]},'scope':'Exact executable statements manually transcribed from visually inspected slide images; whitespace/comments normalized. Not an original notebook. SVC has its printed seed. IK receives an explicit external np.random.seed(54) context because source does not fix dataset/split RNG; source statements/architecture/N/max_iter unchanged. No hardware or new packages.','runs':[]};write()
for label,filename in [('fault','L54-slide-fault-code.py.txt'),('ik','L54-slide-ik-code.py.txt')]:
 p=R/'sources/supplemental'/filename;buf=io.StringIO();ns={};t=time.monotonic();started=now()
 if label=='ik':np.random.seed(54)
 with warnings.catch_warnings(record=True)as w,contextlib.redirect_stdout(buf):
  warnings.simplefilter('always');exec(compile(p.read_text(),str(p),'exec'),ns)
 r={'name':label,'sourcePath':str(p.relative_to(R)),'sourceSha256':sha(p),'startedAt':started,'completedAt':now(),'seconds':time.monotonic()-t,'stdout':buf.getvalue(),'warnings':[str(v.message)for v in w],'XShape':list(ns['X'].shape),'trainShape':list(ns['X_tr'].shape),'testShape':list(ns['X_te'].shape)}
 if label=='fault':
  from sklearn.metrics import confusion_matrix
  m=ns['svm'];r.update(confusionMatrix=confusion_matrix(ns['y_te'],ns['y_pred']).tolist(),classWeights=m['svc'].class_weight_.tolist(),gamma=m['svc']._gamma,supportCounts=m['svc'].n_support_.tolist(),scalerMean=m['sc'].mean_.tolist(),scalerVariance=m['sc'].var_.tolist());assert r['XShape']==[600,3]and r['confusionMatrix']==[[60,0],[0,60]]
 else:
  m=ns['model']['mlp'];r.update(externalSuppliedSeed=54,iterations=m.n_iter_,coefficientShapes=[list(a.shape)for a in m.coefs_],parameterCount=sum(a.size for a in m.coefs_+m.intercepts_),outputActivation=m.out_activation_,meanPositionErrorCm=float(ns['err'].mean()*100),prediction=ns['prediction'].tolist(),lossCurve=m.loss_curve_,finalLoss=m.loss_);assert r['parameterCount']==99714 and r['testShape']==[4000,2]and m.out_activation_=='identity'and m.n_iter_<=300
 report['runs'].append(r);write();print(label,'complete in',round(r['seconds'],2),'seconds',flush=True)
report['status']='passed_author_check_not_independent_review';report['completedAt']=now();write()
