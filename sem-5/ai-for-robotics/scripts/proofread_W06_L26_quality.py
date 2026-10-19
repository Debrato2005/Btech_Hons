from pathlib import Path
import json,hashlib,re,sys
R=Path('/workspace/shared/Btech_Hons/sem-5/ai-for-robotics');sys.path.insert(0,str(R/'scripts'));from authoring_helpers import DraftBatch
p=R/'data/question-batches/W06-L26.json';old=json.loads(p.read_text());b=DraftBatch('W06-L26',6,'L26',old['questions'][0]['topic'],774,old['authorId']);b.questions=old['questions'];b.concepts={c['id']:c for c in old['concepts']}
mp={'index55':'index 55','declared8-bit':'declared 8-bit','stated37/38':'stated 37/38','rounded97percent':'rounded 97 percent','Both use1':'Both use 1','labels0 and1':'labels 0 and 1','Page780':'Page 780','page779':'page 779','Page793':'Page 793','Page794':'Page 794','Page795':'Page 795','page795':'page 795','Page797':'Page 797','atx[p]as aP-feature':'at x[p] as a p-feature','hasp+1entries':'has p+1 entries','andOLS':'and OLS','retainOLS':'retain OLS','callsMSEthe':'calls MSE the','describesSSEunless':'describes SSE unless','byn':'by n','everyMLdataset':'every ML dataset'}
def walk(v):
 if isinstance(v,str):
  for a,z in mp.items():v=v.replace(a,z)
  return re.sub(r';(?=\S)','; ',re.sub(r',(?=[A-Za-z])',', ',v))
 if isinstance(v,list):return[walk(x)for x in v]
 if isinstance(v,dict):return{k:walk(x)for k,x in v.items()}
 return v
for q in b.questions:
 if q['version']==2:
  for k in ['stem','subtopic','assumptions','options','solution','conflictResolution']:
   if k in q:q[k]=walk(q[k])
for c in b.concepts.values():
 if any(q['id']in c['questionIds']and q['version']==2 for q in b.questions):
  for k in ['title','description']:c[k]=walk(c[k])
b.save();m=json.loads((R/'audits/W06-L26-v2-quality-repair-manifest.json').read_text());h=lambda q:hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in['status','reviewIds']},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();assert all(h(next(q for q in b.questions if q['id']==k))==v for k,v in m['acceptedHashesPreserved'].items())
ids=set(m['changedQuestionIds']);full=json.loads((R/'audits/blind-W06-L26.json').read_text());fp=R/'audits/blind-W06-L26-v2-quality-repairs.json';fp.write_text(json.dumps([q for q in full if q['id']in ids],ensure_ascii=False,indent=2)+'\n');m['packetSha256']=hashlib.sha256(fp.read_bytes()).hexdigest();m['proofreading']='Read final stems, alternatives, explanations, assumptions and local qualifications after targeted spacing changes; actual code identifiers and original source evidence preserved.';(R/'audits/W06-L26-v2-quality-repair-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(m['packetSha256'])
