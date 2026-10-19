from pathlib import Path
import json,copy,datetime
from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W02-L08.json';b=json.loads(p.read_text());old=copy.deepcopy(b)
easy=['P0278-Q02','P0278-Q03','P0279-Q01','P0280-Q01','P0281-Q02','P0284-Q02','P0285-Q01','P0290-Q01'];suffix=set(easy+['P0280-Q03','P0284-Q03','P0287-Q05']);ids={'W02-L08-'+s for s in suffix}
a=R/'audits/batch-history/W02-L08-v2-flagged-before-v3.json';assert not a.exists();a.write_text(json.dumps([q for q in b['questions'] if q['id'] in ids],ensure_ascii=False,indent=2)+'\n')
for q in b['questions']:
 if q['id'] not in ids:continue
 assert q['version']==2
 h=question_hash(q);q.update(version=3,status='draft',reviewIds=[]);author='robotics-integration-L08-v3-revision-author';q.setdefault('revisionAuthors',[]).append(author)
 q.setdefault('revisionHistory',[]).append({'version':3,'authorId':author,'priorQuestionSha256':h,'revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reason':'Frozen independent difficulty, standalone-context or rationale finding.'})
 if q['id'][8:] in easy:q['difficulty']='easy'
 if q['id'].endswith('P0280-Q03'):q['stem']='For a six-revolute-joint manipulator, the slide gives three neighboring joint axes intersecting at one point as a sufficient condition for a closed-form inverse-kinematics solution; what does “sufficient” mean here?'
 if q['id'].endswith('P0284-Q03'):
  q['solution']['optionExplanations']['o3']='Incorrect. The first θ1 factor should be cosθ1, and the second term should be subtracted; the second sinθ1 factor is already correct.'
  q['solution']['misconceptions']=[q['solution']['optionExplanations'][o].removeprefix('Incorrect. ') for o in ('o2','o3','o4')]
 if q['id'].endswith('P0287-Q05'):next(o for o in q['options'] if o['id']=='o3')['text']='It implies θ2 and θ2′ always describe the same configuration'
# Preserve the full prefix when testing difficulty IDs.
for q in b['questions']:
 if q['id'] in {'W02-L08-'+s for s in easy}:q['difficulty']='easy'
assert all(question_hash(q)==question_hash(next(x for x in old['questions'] if x['id']==q['id'])) for q in b['questions'] if q['id'] not in ids)
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in b['questions']:
 if q['id'] not in ids:continue
 x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
(R/'audits/blind-W02-L08-v3.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print('11 repaired; 99 accepted hashes preserved.')
