"""Read-only course inspection, writes only a separate reviewer snapshot and audit."""
from pathlib import Path
import base64,datetime,hashlib,importlib.util,json
R=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reviewer_real_visual104',R/'scripts/question_visuals.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
b=json.loads((R/'data/bank.json').read_text());qbefore=v.digest(b['questions']);x=v.prepare_question_visuals(b,R);b['questionVisuals']=x
ids={a['id'] for a in x['assets']};b['assets']=[a for a in b['assets'] if a['id'] not in ids]+v.projected_visual_assets(x)
a={z['id']:{**z,'kind':'diagram','data':base64.b64encode((R/z['path']).read_bytes()).decode()} for z in x['assets']}
assert v.digest(b['questions'])==qbefore
p=Path('/workspace/shared/robotics-verification-logs/visual-104-review-bank.json');p.write_text(json.dumps({'bank':b,'embeddedAssets':a},ensure_ascii=False,separators=(',',':')))
out={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'snapshotPath':str(p),'snapshotSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'questionCollectionSha256':qbefore,'mode':'No-write visual preparation from current genuine independent crop/classification reviews. No pixel fidelity approval by this code reviewer. This is a bounded snapshot; content review is ongoing.','ready':len(x['bindings']),'required':sum(z['dependencyStatus']=='required' for z in x['bindings'].values()),'blocked':len(x['diagnostics']),'embeddedAssets':len(a),'producerSha256':hashlib.sha256((R/'scripts/question_visuals.py').read_bytes()).hexdigest()};(D/'actual-visual-producer.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
