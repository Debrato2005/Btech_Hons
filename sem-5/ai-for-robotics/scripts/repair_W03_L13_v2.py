from pathlib import Path
import json,copy,datetime
from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W03-L13.json';b=json.loads(p.read_text());old=copy.deepcopy(b);changes={14:'easy',16:'easy',21:'medium',22:'easy',23:'easy',28:None,32:'easy',42:'easy'}
a=R/'audits/batch-history/W03-L13-v1-before-quality-repair.json';assert not a.exists();a.write_text(json.dumps([q for q in b['questions'] if int(q['id'][-3:]) in changes],ensure_ascii=False,indent=2)+'\n')
for q in b['questions']:
 n=int(q['id'][-3:])
 if n not in changes:continue
 assert q['version']==1;h=question_hash(q);author='robotics-integration-L13-v2-revision-author';q.update(version=2,status='draft',reviewIds=[]);q.setdefault('revisionAuthors',[]).append(author);q.setdefault('revisionHistory',[]).append({'version':2,'authorId':author,'priorQuestionSha256':h,'reason':'Independent difficulty calibration or explicit local source-conflict binding.','revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 if changes[n]:q['difficulty']=changes[n]
 if n==28:
  next(c for c in q['citations'] if c['physicalPage']==421)['role']='conflict'
  q['conflictResolution']={'status':'explicit-qualification-awaiting-independent-review','sourceClaim':'Physical page421, printed slide18, has an extra transpose after an already3×1 displayed n2 column in one expanded term; literal R12 n2ᵀ is not conformable.','basis':'The unexpanded recurrence on the same page and the following column expansion on physical page422 use R12 n2; a3×3 rotation times a3×1 moment column gives the required3×1 vector.','method':'Preserve the visible local notation defect; use the consistent column interpretation only for this question, not a global correction of the page.','sourceId':'lectures','sourceSha256':'2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c','physicalPages':[421,422]}
assert sum(question_hash(q)==question_hash(o) for q,o in zip(b['questions'],old['questions']))==38
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in b['questions']:
 if int(q['id'][-3:]) not in changes:continue
 x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
(R/'audits/blind-W03-L13-v2.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print('8 repairs saved;38 accepted hashes unchanged.')
