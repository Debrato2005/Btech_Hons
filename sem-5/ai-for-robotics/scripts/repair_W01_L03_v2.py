from pathlib import Path
import json,copy,datetime
from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W01-L03.json';b=json.loads(p.read_text());old=copy.deepcopy(b)
reviews=json.loads((R/'data/reviews/W01-L03-v1-targeted-quality-independent.json').read_text()); fixes={x['questionId']:x['recommendedDifficulty'] for x in reviews}
a=R/'audits/batch-history/W01-L03-v1-before-difficulty-repair.json';assert not a.exists();a.write_text(json.dumps([q for q in b['questions'] if q['id'] in fixes],ensure_ascii=False,indent=2)+'\n')
for q in b['questions']:
 if q['id'] not in fixes:continue
 assert q['version']==1; h=question_hash(q);author='robotics-integration-L03-v2-revision-author';q.update(version=2,difficulty=fixes[q['id']],status='draft',reviewIds=[])
 q.setdefault('revisionAuthors',[]).append(author);q.setdefault('revisionHistory',[]).append({'version':2,'authorId':author,'priorQuestionSha256':h,'revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reason':'Independent targeted coverage challenge found inflated difficulty; content and key unchanged.'})
assert sum(question_hash(q)==question_hash(o) for q,o in zip(b['questions'],old['questions']))==69
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in b['questions']:
 if q['id'] not in fixes:continue
 x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
(R/'audits/blind-W01-L03-v2.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print('18 difficulty repairs; 69 prior accepted hashes preserved.')
