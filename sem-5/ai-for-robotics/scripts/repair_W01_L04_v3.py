#!/usr/bin/env python3
"""Apply two frozen quality findings while preserving 129 accepted objects."""
from pathlib import Path
import copy, json
from datetime import datetime,timezone
from validate import question_hash
R=Path(__file__).resolve().parents[1]
p=R/'data/question-batches/W01-L04.json';b=json.loads(p.read_text());original=copy.deepcopy(b)
ids={'W01-L04-P0144-Q02','W01-L04-P0160-Q02'}
author='robotics-integration-L04-v3-revision-author'
assert all(q['version']==2 for q in b['questions'] if q['id'] in ids)
archive=R/'audits/batch-history/W01-L04-v2-flagged-before-v3.json'
assert not archive.exists();archive.write_text(json.dumps([q for q in b['questions'] if q['id'] in ids],ensure_ascii=False,indent=2)+'\n')
for q in b['questions']:
 if q['id'] not in ids:continue
 oldhash=question_hash(q);q.update(version=3,status='draft',reviewIds=[])
 q.setdefault('revisionAuthors',[]).append(author)
 q.setdefault('revisionHistory',[]).append({'version':3,'authorId':author,'revisedAt':datetime.now(timezone.utc).isoformat(),'priorQuestionSha256':oldhash,'reason':'Repair two frozen independent distractor-quality findings; keys unchanged and new independent review required.'})
 if q['id'].endswith('P0144-Q02'):
  opts={'o2':'The discrepancy proves an implementation bug rather than an inadequate physical model'}
  ex={'o2':'Incorrect. A faithful implementation of an inadequate model can also disagree with the physical robot, so an implementation bug is not established.'}
 else:
  opts={'o2':'It automatically joins the two lines and computes velocity','o3':'It reads the CSV, then raises TypeError when the velocity division executes','o4':'It stores the position difference as velocity, then evaluates the next line as an unused expression'}
  ex={'o2':'Incorrect. This assignment has neither an enclosing continuation context nor an explicit continuation character.','o3':'Incorrect. Python parses the complete file before execution; the dangling division operator causes SyntaxError before the CSV read, not a later runtime TypeError.','o4':'Incorrect. The trailing division operator prevents the first line from being a complete assignment; it cannot silently be discarded.'}
 for o in q['options']:
  if o['id'] in opts:o['text']=opts[o['id']]
 q['solution']['optionExplanations'].update(ex)
 q['solution']['misconceptions']=[v.removeprefix('Incorrect. ') for k,v in q['solution']['optionExplanations'].items() if k not in q['correctOptionIds']]
before={q['id']:question_hash(q) for q in original['questions']}
assert all(question_hash(q)==before[q['id']] for q in b['questions'] if q['id'] not in ids)
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in b['questions']:
 if q['id'] not in ids:continue
 x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
(R/'audits/blind-W01-L04-v3.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
print('Two v3 quality repairs saved; all other 129 question hashes unchanged.')
