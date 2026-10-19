"""Targeted readability/citation repairs; no key or calculation changes."""
from pathlib import Path
import json,copy,hashlib,re
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W05-L22.json';b=json.loads(p.read_text());old=copy.deepcopy(b);find=json.loads((R/'audits/W05-L22-quality-repairs-independent-summary.json').read_text())['findings'];ids={f['questionId']for f in find};archive=R/'audits/batch-history/W05-L22-before-final-readability-repairs.json';assert not archive.exists();archive.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
h=lambda q:hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in['status','reviewIds']},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();preserved={q['id']:h(q)for q in old['questions']if q['id']not in ids}
def readable(t):
 if t is None:return t
 t=re.sub(r'([A-Za-z])(?=\d)',r'\1 ',t)
 t=re.sub(r'(?<=\d)(?=(?:rad\b|N\b|Hz\b|m\b|I\b))',' ',t)
 t=re.sub(r'(?<=[A-Za-z])(?=\[)',' ',t)
 t=t.replace('byη','by η').replace('ω=2πf','ω = 2πf')
 return t
for q in b['questions']:
 if q['id']not in ids:continue
 q['version']+=1;q['status']='draft';q['reviewIds']=[];q['revisionAuthors']=list(dict.fromkeys(q.get('revisionAuthors',[])+['robotics-integration-author-L22']))
 for k in['stem']:q[k]=readable(q[k])
 q['assumptions']=[readable(t)for t in q['assumptions']]
 for o in q['options']:o['text']=readable(o['text'])
 for k in['justification','simpleExplanation','memoryAid']:q['solution'][k]=readable(q['solution'].get(k))
 for k in['steps','misconceptions','examTraps']:q['solution'][k]=[readable(t)for t in q['solution'][k]]
 q['solution']['optionExplanations']={k:readable(v)for k,v in q['solution']['optionExplanations'].items()}
 pages=[679,680]if q['id'].endswith('Q025')else[676]if q['id'].endswith('Q059')else[]
 for page in pages:
  c=next(copy.deepcopy(c)for x in old['questions']for c in x['citations']if c['physicalPage']==page);c['role']='premise';q['citations'].append(c)
  for concept in b['concepts']:
   if concept['id']in q['conceptIds']and c['slideId']not in concept['slideIds']:concept['slideIds'].append(c['slideId'])
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');assert all(h(next(q for q in b['questions']if q['id']==k))==v for k,v in preserved.items())
packet=[]
for q in b['questions']:
 if q['id']not in ids:continue
 d={k:copy.deepcopy(q[k])for k in['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
 for c in d['citations']:c.pop('evidenceText',None)
 packet.append(d)
f=R/'audits/blind-W05-L22-final-readability-repairs.json';f.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');m={'changedIds':sorted(ids),'unchangedAcceptedHashes':preserved,'packetSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'changes':'Normal prose/quantity spacing;Q025 adds679/680,Q059 adds676;no keys or math changed.','review':'pending;prior exposure disclosed'};(R/'audits/W05-L22-final-readability-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(m['packetSha256'],len(preserved),'accepted hashes preserved')
for q in b['questions']:
 if q['id']in ids:
  print(q['id'],q['stem']);print([o['text']for o in q['options']]);print(q['solution']['steps'])
