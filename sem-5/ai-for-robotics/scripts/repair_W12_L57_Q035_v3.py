"""Narrow disclosed correction of an omitted distractor repair, without self-approval."""
from pathlib import Path
import json,copy,sys,hashlib,datetime
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors
p=R/'data/question-batches/W12-L57.json';b=json.loads(p.read_text());q=next(x for x in b['questions']if x['id']=='W12-L57-Q035');assert q['version']==2
old=copy.deepcopy(b);h=R/'data/history/W12-L57/W12-L57-before-Q035-v3.json';assert not h.exists();h.write_bytes(p.read_bytes())
q['version']=3;q['revisionAuthors'].append('build_offline_study_interface:L57-Q035-v3-repair')
next(o for o in q['options']if o['id']=='o2')['text']='Assign each object to whichever bin is nearest to its current pick location, regardless of its detected class.'
q['solution']['optionExplanations']['o2']='Nearest-bin routing may shorten travel, but it need not respect the labelled colour-class destinations; proximity is not the specified sorting assignment.'
q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']]for o in q['options']if o['id']not in q['correctOptionIds']]
assert not schema_errors(q,json.loads((R/'data/schema.question.json').read_text()))
for o,n in zip(old['questions'],b['questions']):assert o==n or n['id']==q['id']
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
a={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
for c in a['citations']:c.pop('evidenceText',None);c['locator']='Lecture L57, physical PDF page 1822, printed footer 20: inspect the labelled system photograph.'
pp='audits/blind-W12-L57-Q035-v3.json';(R/pp).write_text(json.dumps([a],ensure_ascii=False,indent=2)+'\n')
m={'questionId':q['id'],'version':3,'questionSha256':question_hash(q),'packet':pp,'packetSha256':hashlib.sha256((R/pp).read_bytes()).hexdigest(),'supersedesOnly':'Q035 version 2 in the fourteen-item v2 packet; other thirteen versions unchanged.','reason':'Self-audit found the requested distractor repair had been omitted before v2 freeze.','acceptedPreserved':72,'otherCurrentWholeObjectsPreserved':85,'independentReviewComplete':False,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat()};(R/'audits/W12-L57-Q035-v3-minimal-bindings.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m))
