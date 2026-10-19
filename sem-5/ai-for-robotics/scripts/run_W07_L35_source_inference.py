import os,json,hashlib,datetime,platform
from pathlib import Path
R=Path(__file__).resolve().parents[1]
runtime=Path('/tmp/robotics-l35-runtime');runtime.mkdir(exist_ok=True)
os.chdir(runtime)
os.environ['YOLO_CONFIG_DIR']=str(runtime/'settings')
from ultralytics import YOLO,__version__
import torch,numpy as np
model=YOLO('yolov8n.pt')
results=model.predict(source='https://ultralytics.com/images/bus.jpg',save=True,conf=0.25,device='cpu',project='/tmp/robotics-l35-runtime/output',name='bus',exist_ok=True)
r=results[0]
out={'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ultralyticsVersion':__version__,'torchVersion':torch.__version__,'pythonVersion':platform.python_version(),'sourceUrl':'https://ultralytics.com/images/bus.jpg','weightsPath':'yolov8n.pt','weightsSha256':hashlib.sha256(Path('yolov8n.pt').read_bytes()).hexdigest(),'resultsCount':len(results),'originalShape':list(r.orig_shape),'saveDir':r.save_dir,'detections':[{'classId':int(b.cls.item()),'className':r.names[int(b.cls.item())],'confidence':float(b.conf.item()),'xywh':b.xywh[0].tolist(),'xyxy':b.xyxy[0].tolist()} for b in r.boxes],'scope':'Actual official pretrained YOLOv8n inference on the source bus URL, on CPU. Versions and output may differ from the unpinned lecture. No training, webcam, or user images accessed.'}
for p in Path('.').glob('bus.*'):out['imageSha256']=hashlib.sha256(p.read_bytes()).hexdigest()
(R/'audits/W07-L35-actual-source-inference.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
