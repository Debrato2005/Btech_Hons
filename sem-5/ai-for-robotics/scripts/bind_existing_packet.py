"""Create only ID/version/content-hash bindings for an existing answer-free packet."""
from pathlib import Path
import json,hashlib,sys,copy
R=Path(__file__).resolve().parents[1];name=sys.argv[1];p=R/f'audits/blind-{name}.json';packet=json.loads(p.read_text());ids={q['id']for q in packet};keyed={}
for f in (R/'data/question-batches').glob('*.json'):
 b=json.loads(f.read_text())
 for q in b.get('questions',[]):
  if q['id']in ids:keyed[q['id']]=q
assert set(keyed)==ids
bindings=[]
for x in packet:
 q=keyed[x['id']];expected={k:copy.deepcopy(q[k])for k in x}
 for c in expected.get('citations',[]):c.pop('evidenceText',None)
 assert x==expected,x['id']
 h=hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ['status','reviewIds']},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest();bindings.append({'id':q['id'],'version':q['version'],'questionHash':h})
out={'packetSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'questions':bindings};(R/f'audits/blind-binding-{name}.json').write_text(json.dumps(out,indent=2)+'\n');print(name,out['packetSha256'],len(bindings))
