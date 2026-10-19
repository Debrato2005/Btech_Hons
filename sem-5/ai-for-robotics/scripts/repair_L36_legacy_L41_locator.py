"""One-time, narrow repairs after independent source and quality challenges."""
from pathlib import Path
import copy, json, hashlib, datetime
R=Path(__file__).resolve().parents[1]
def digest(q):
 return hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ['status','reviewIds']},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def freeze(name,qs,unchanged,pages):
 packet=[]
 for q in qs:
  x={k:copy.deepcopy(q[k]) for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
  for c in x['citations']:c.pop('evidenceText',None)
  packet.append(x)
 path=R/f'audits/blind-{name}.json';path.write_text(json.dumps(packet,indent=2,ensure_ascii=False)+'\n')
 binding={'packetSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'questions':[{'id':q['id'],'version':q['version'],'questionHash':digest(q)} for q in qs]}
 (R/f'audits/blind-binding-{name}.json').write_text(json.dumps(binding,indent=2)+'\n')
 (R/f'audits/{name}-repair-manifest.json').write_text(json.dumps({**binding,'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'unchangedObjectsPreserved':unchanged,'actualPagesRevisited':pages},indent=2)+'\n')
 print(name,binding['packetSha256'])
p=R/'data/question-batches/search-foundations.json';b=json.loads(p.read_text());old=copy.deepcopy(b)
ids={'W08-L36-P1120-Q02','W08-L36-P1124-Q02'}
qs=[q for q in b['questions'] if q['id'] in ids]
assert len(qs)==2 and all(q['version']==1 for q in qs)
for q in qs:
 q['version']=2;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append('build_robotics_study_app:L36-legacy-v2')
 q['difficulty']='easy'
 if 'P1120' in q['id']:
  q['type']='conceptual';q['cognitiveSkill']='conceptual';q['difficultyRationale']='Single symbolic lower-bound relation with compatible units, not a hard multistep numerical calculation.'
  q['citations'][0]['role']='premise'
 else:
  texts={'o1':'Global planning uses the known full map; local planning reacts to recent nearby observations.','o2':'Global planning reacts to nearby observations; local planning first computes the whole-map route.','o3':'Both terms describe whole-map planning, differing only in whether the path is a grid or a graph.','o4':'Both terms describe nearby reactive planning, differing only in whether the objective is time or distance.'}
  ex={'o1':'This matches the summary and the later response to a newly detected obstacle.','o2':'This reverses the course roles of global and local planning.','o3':'Grid versus graph is a representation choice, not the global versus local distinction.','o4':'Time versus distance is an objective choice, not the global versus local distinction.'}
  for o in q['options']:o['text']=texts[o['id']]
  q['solution']['optionExplanations']=ex;q['solution']['misconceptions']=[ex[o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']]
  q['difficultyRationale']='Direct comparison of the course planning roles.'
assert all(a==z for a,z in zip(old['questions'],b['questions']) if a['id'] not in ids)
p.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n');freeze('W08-L36-legacy-v2',qs,len(b['questions'])-2,[1120,1124,1136])
p=R/'data/question-batches/W09-L41.json';b=json.loads(p.read_text());old=copy.deepcopy(b);q=next(q for q in b['questions'] if q['id']=='W09-L41-Q069');assert q['version']==2
q['version']=3;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append('build_robotics_study_app:L41-Q069-v3')
c=next(c for c in q['citations'] if c['physicalPage']==1290)
c['locator']='Lecture L41, physical PDF page 1290, printed footer 28: Four-row one-parameter-at-a-time stage table.'
assert all(a==z for a,z in zip(old['questions'],b['questions']) if a['id']!=q['id'])
p.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n');freeze('W09-L41-Q069-v3',[q],len(b['questions'])-1,[1290])
