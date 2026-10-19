from pathlib import Path
import json,copy,datetime
from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W03-L13-GAP.json';b=json.loads(p.read_text());q=b['questions'][1];assert q['version']==1
(R/'audits/batch-history/W03-L13-GAP-Q002-v1.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');h=question_hash(q);author='robotics-integration-L13-gap-v2-revision-author';q.update(version=2,status='draft',reviewIds=[],revisionAuthors=[author],revisionHistory=[{'version':2,'authorId':author,'priorQuestionSha256':h,'reason':'Replace implausible distractors with common misconceptions about numerical recursion.','revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}])
opts={'o2':'It first requires every joint torque to be expanded into a closed-form symbolic expression before any numerical evaluation','o3':'It shortens the computation by treating each link as dynamically uncoupled from its neighbours','o4':'It avoids the long expressions by dropping velocity-product terms while retaining only acceleration and gravity terms'}
for o in q['options']:
 if o['id'] in opts:o['text']=opts[o['id']]
q['solution']['optionExplanations'].update({'o2':'The linkwise numerical recursions do not require full symbolic expansion first.','o3':'Outward motion propagation and inward force propagation retain coupling between links.','o4':'The exact recursions include velocity-product effects; neglecting them would be an additional approximation.'});q['solution']['misconceptions']=[q['solution']['optionExplanations'][k] for k in opts]
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
for c in x['citations']:c.pop('evidenceText',None)
(R/'audits/blind-W03-L13-GAP-v2.json').write_text(json.dumps([x],ensure_ascii=False,indent=2)+'\n');print(q['id'])
