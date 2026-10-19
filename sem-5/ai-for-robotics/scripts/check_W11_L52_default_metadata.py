#!/usr/bin/env python3
"""Permitted default-runtime checks of preserved metadata and synthetic input arrays only."""
from pathlib import Path
import sys,json,hashlib,datetime,numpy as np,yaml
R=Path(__file__).resolve().parents[1]
assert not str(Path(sys.prefix)).startswith('/tmp/robotics-l35-venv')
p=R/'sources/supplemental/L52-ultralytics-open-images-v7.yaml';cfg=yaml.safe_load(p.read_text());checks=[]
def ck(i,condition,detail):
 assert condition,i
 checks.append({'id':i,'passed':True,'detail':detail})
ck('L52-DEFAULT-META-01',len(cfg['names'])==601 and set(cfg['names'])==set(range(601)),'Preserved YAML contains 601 unique indexed names; no Ultralytics import or installation.')
frames=[np.full((480,640,3),i*60,dtype=np.uint8)for i in range(3)]
ck('L52-DEFAULT-ARRAY-01',all(f.shape==(480,640,3)and f.dtype==np.uint8 for f in frames),'Three synthetic 640x480 three-channel uint8 arrays; no video codec execution.')
ck('L52-DEFAULT-ARRAY-02',[float(f.mean())for f in frames]==[0.,60.,120.],'Synthetic intensities checked; no camera footage.')
r={'batchId':'W11-L52','status':'author_checks_only','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'interpreter':sys.executable,'numpyVersion':np.__version__,'pyyamlVersion':yaml.__version__,'metadataSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checks':checks,'repeatsHistoricalCheck':'Open Images label count only','notRepeated':['matching writer opened','Matching frames round trip','mismatched writer opened','Mismatched frames not silently resized'],'limitations':'Default environment lacks cv2 and ultralytics. No new installation, restricted virtual environment, camera, model or video codec used.'}
(R/'audits/W11-L52-default-metadata-author.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False))
