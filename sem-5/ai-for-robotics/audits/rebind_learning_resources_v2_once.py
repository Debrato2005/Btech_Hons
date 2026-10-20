"""One-time author metadata rebind after policy repair. Never creates approval."""
from pathlib import Path
import json,hashlib,importlib.util
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(ROOT.joinpath(p).read_text())
write=lambda p,v:ROOT.joinpath(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
sha=lambda p:hashlib.sha256(ROOT.joinpath(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('resource_rebind_v',ROOT/'scripts/validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
policy=read('data/learning-resource-policy.json');assert policy['version']=='1.0.0'
old=read('audits/resource-history/v1-before-policy-repairs/data/learning-tools-course.json');new=read('data/learning-tools-course.json');assert old==new
changed=[]
for group,records in new['learningTools'].items():
 for record in records:
  before=json.loads(json.dumps(record));changed_paths=[]
  for f in record['implementationFiles']:
   current=sha(f['path'])
   if current!=f['sha256']:changed_paths.append(f['path']);f['sha256']=current
  if changed_paths:
   record['version']+=1;record['status']='draft';record['reviewIds']=[]
   payload=lambda r:{k:x for k,x in r.items() if k not in ['version','status','reviewIds','implementationFiles']}
   assert payload(before)==payload(record)
   changed.append({'id':record['id'],'previousVersion':before['version'],'previousSha256':v.question_hash(before),'version':record['version'],'sha256':v.question_hash(record),'changedImplementationPaths':changed_paths,'unchangedComputationalPayloadSha256':hashlib.sha256(v.canonical_json(payload(record)).encode()).hexdigest()})
assert len(changed)==18
policy['version']='1.0.1';policy['status']='draft';policy['codeHashes']={p:sha(p)for p in policy['codeHashes']}
policy['description']='Exact complete-question context projections with current literal-answer/source/reviewer gates and revocable course resource activation. Computation checks are separate from actual browser QA.'
write('data/learning-tools-course.json',new);write('data/learning-resource-policy.json',policy)
write('audits/learning-resources-v2-author-rebinding.json',{'at':datetime.now(timezone.utc).isoformat(),'scope':'Implementation binding and policy repair only. Mathematical payloads are unchanged; prior tool approvals do not match these new hashes. No independent approval created.','resourceChanges':changed,'policySha256':hashlib.sha256(v.canonical_json(policy).encode()).hexdigest(),'policyEligible':False})
print('Rebound',len(changed),'draft tools; policy 1.0.1 remains draft.')
