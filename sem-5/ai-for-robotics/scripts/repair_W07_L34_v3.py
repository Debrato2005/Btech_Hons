from pathlib import Path
import json,copy,hashlib,datetime
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W07-L34.json';b=json.loads(p.read_text());old=copy.deepcopy(b);ids={'W07-L34-P1052-Q03','W07-L34-P1052-Q04','W07-L34-P1056-Q03'}
for q in b['questions']:
 if q['id']not in ids:continue
 q['version']+=1;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append('build_robotics_study_app:L34-v3')
 if 'P1052' in q['id']:
  q['difficulty']='medium'
  for k in ['justification','simpleExplanation']:q['solution'][k]=q['solution'][k].replace('is[','is [')
  q['solution']['optionExplanations']={k:v.replace('requireeta','require eta').replace('have|','have |')for k,v in q['solution']['optionExplanations'].items()}
 else:
  q['stem']='The slide places “Embodied AI” in both “What has already been done” and “What we aim for”; which interpretation follows from those broad labels?'
  texts={'o1':'The categories can overlap: a field can have demonstrated applications and continuing aims.','o2':'The repeated field has reached the same task-level maturity on both sides.','o3':'The left-hand examples mean the field has no remaining research aims.','o4':'The right-hand aims mean the field has no demonstrated applications.'}
  ex={'o1':'The repeated label directly shows that the two broad categories need not be mutually exclusive.','o2':'The word clouds do not provide task-level maturity measurements or establish equivalence.','o3':'The same field is also listed among continuing aims.','o4':'The same field is also listed among demonstrated applications.'}
  for o in q['options']:o['text']=texts[o['id']]
  q['solution']['justification']=q['solution']['simpleExplanation']=ex['o1'];q['solution']['optionExplanations']=ex
 for c in q['citations']:c['locator']=c['locator'].replace('EmbodiedAI','Embodied AI')
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']]for o in q['options']if o['id']not in q['correctOptionIds']]
assert all(q==n for q,n in zip(old['questions'],b['questions'])if q['id']not in ids)
p.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n');qs=[q for q in b['questions']if q['id']in ids];packet=[]
for q in qs:
 a={k:copy.deepcopy(q[k])for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
 for c in a['citations']:c.pop('evidenceText',None)
 packet.append(a)
pp=R/'audits/blind-W07-L34-v3.json';pp.write_text(json.dumps(packet,indent=2,ensure_ascii=False)+'\n');bind={'packetSha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'questions':[{'id':q['id'],'version':q['version'],'questionHash':hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ['status','reviewIds']},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()}for q in qs]};(R/'audits/blind-binding-W07-L34-v3.json').write_text(json.dumps(bind,indent=2)+'\n');(R/'audits/W07-L34-v3-repair-manifest.json').write_text(json.dumps({**bind,'repaired':3,'acceptedObjectsPreserved':135,'actualPageRevisited':1056,'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'changeScope':'Difficulty tags on two derived recurrence items; stronger diagram-interpretation distractors; small spacing cleanup only within these objects.'},indent=2)+'\n');print(bind['packetSha256'])
