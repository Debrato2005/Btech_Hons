"""One-time isolated repairs after frozen independent reviews."""
from pathlib import Path
import copy,json,hashlib,datetime
R=Path(__file__).resolve().parents[1]
def freeze(name,qs,pages):
 packet=[]
 for q in qs:
  a={k:copy.deepcopy(q[k]) for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
  for c in a['citations']:c.pop('evidenceText',None)
  packet.append(a)
 p=R/f'audits/blind-{name}.json';p.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
 h=lambda q:hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ['status','reviewIds']},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
 bind={'packetSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'questions':[{'id':q['id'],'version':q['version'],'questionHash':h(q)}for q in qs]}
 (R/f'audits/blind-binding-{name}.json').write_text(json.dumps(bind,indent=2)+'\n');(R/f'audits/{name}-repair-manifest.json').write_text(json.dumps({**bind,'actualPagesRevisited':pages,'unrelatedObjectsPreserved':True,'time':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n');print(name,bind['packetSha256'])
def revise(q,expected):
 assert q['version']==expected
 q['version']+=1;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append('build_robotics_study_app:residual-2217')
p=R/'data/question-batches/search-foundations.json';b=json.loads(p.read_text());old=copy.deepcopy(b);ids={'W08-L36-P1120-Q02','W08-L37-P1135-Q03'}
q=next(q for q in b['questions']if q['id']=='W08-L36-P1120-Q02');revise(q,2);q['solution']['formulas'][0]['variables']['h_time']='Optimistic remaining-travel-time heuristic, measured in seconds';q36=q
q=next(q for q in b['questions']if q['id']=='W08-L37-P1135-Q03');revise(q,1)
q['stem']='Before the first move, a path has no initial entry cost and g is the sum of costs of moves already taken. With h(start)=4.8, what are g(start) and f(start)=g+h?'
q['type']='numerical';q['difficulty']='easy';q['cognitiveSkill']='numerical';q['assumptions']=['No move has yet occurred and there is no separate start-entry charge.','Use the explicitly stated accumulated-move-cost definition, not the contradictory g=1.0 label on page 1135.']
texts={'o1':'g=0 and f=4.8','o2':'g=1 and f=5.8','o3':'g=4.8 and f=9.6','o4':'g=0 and f=0'}
ex={'o1':'Zero moves contribute zero accumulated cost; add the given heuristic 4.8.','o2':'This copies the conflicting start label despite the stated zero-entry-cost convention.','o3':'This mistakes the remaining-cost estimate h for accumulated cost g.','o4':'This omits the nonzero heuristic from f.'}
for o in q['options']:o['text']=texts[o['id']]
q['solution']['justification']=q['solution']['simpleExplanation']='The empty path has g=0; therefore f=0+4.8=4.8 under the stated convention.'
q['solution']['optionExplanations']=ex;q['solution']['misconceptions']=[ex[o['id']]for o in q['options']if o['id']not in q['correctOptionIds']];q['solution']['steps']=['The sum of costs of zero moves is 0.','Add the given remaining-cost estimate h=4.8.','Obtain f=4.8.'];q['solution']['formulas']=[{'expression':'f=g+h','variables':{'f':'A* priority score','g':'Accumulated cost of moves taken','h':'Estimated remaining path cost'},'units':{'f,g,h':'The same path-cost units'},'assumptions':q['assumptions']}]
for c in q['citations']:c['locator']=f"Physical PDF page {c['physicalPage']}, printed footer {c['physicalPage']-1126}: "+('Accumulated-move-cost definition and green start cell labeled 0.0.'if c['physicalPage']==1133 else 'Green start cell labeled g=1.0, h=4.8, and f=g+h equation; conflicting g label retained as source evidence.')
q['conflictResolution']={'status':'explicit-qualification-awaiting-independent-review','sourceClaim':'Page 1133 labels the start g=0.0, while page 1135 labels it g=1.0.','basis':'The question explicitly uses zero entry cost and the accumulated-move-cost definition, which gives zero before any move.','method':'Preserve both printed labels and evaluate the declared mathematical convention.'};q['notes']='The printed start-cost contradiction is disclosed; this version tests a stated convention and requires a matching independent review.'
assert all(a==z for a,z in zip(old['questions'],b['questions'])if a['id']not in ids);p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');freeze('W08-L36-P1120-Q02-v3',[q36],[1120]);freeze('W08-L37-P1135-Q03-v2',[q],[1133,1135])
p=R/'data/question-batches/W08-L39.json';b=json.loads(p.read_text());old=copy.deepcopy(b);qs=[]
for q in b['questions']:
 if q['id']not in ['W08-L39-Q037','W08-L39-Q042']:continue
 revise(q,2);qs.append(q)
 if q['id'].endswith('Q037'):
  next(o for o in q['options']if o['id']=='o4')['text']='The search may insert a transfer at the crossing whenever doing so lowers its heuristic estimate'
  q['solution']['optionExplanations']['o4']='A heuristic guides search over the encoded graph; it does not authorize inventing a missing connection.'
  q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']]for o in q['options']if o['id']not in q['correctOptionIds']]
 else:next(c for c in q['citations']if c['physicalPage']==1219)['locator']='Lecture 39, physical PDF page 1219, printed footer 23: acquire_gnss_fix samples synthetic x,y coordinates within the map bounds; the cosmetic latitude/longitude conversion is in the separately cited notebook.'
assert all(a==z for a,z in zip(old['questions'],b['questions'])if a['id']not in [q['id']for q in qs]);p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');freeze('W08-L39-v3',qs,[1217,1219])
