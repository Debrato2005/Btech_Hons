"""One-time two-item L28 residual repair; no accepted-object changes."""
from pathlib import Path
import json,copy,hashlib,datetime
from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W06-L28.json';b=json.loads(p.read_text());old=copy.deepcopy(b);ids={'W06-L28-Q003','W06-L28-Q046'};preserved={q['id']:question_hash(q) for q in b['questions'] if q['id']not in ids};changed=[]
for q in b['questions']:
 if q['id']not in ids:continue
 assert q['version']==2
 if q['id'].endswith('Q003'):
  next(o for o in q['options'] if o['id']=='o4')['text']='NumPy supplies plots, matplotlib supplies numerical arrays, and IPython/Jupyter supplies interactive notebooks.'
  q['solution']['optionExplanations']['o4']='The notebook role is correct, but the numerical-array and plotting-library roles are swapped.'
 else:
  c=next(c for c in q['citations'] if c['physicalPage']==847);c['locator']='Lecture28, physical PDF page847, printed footer26: table row Data_pandas.iloc[n,m] gives general zero-based position indexing; substituting n=1 and m=2 is the question’s derived application, not a literal printed call.'
 q['version']=3;q['status']='draft';q['reviewIds']=[];q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+['robotics-integration-L28-residual-repairs']));q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']]for o in q['options']if o['id']not in q['correctOptionIds']];changed.append(q)
assert len(preserved)==67 and preserved=={q['id']:question_hash(q)for q in b['questions']if q['id']not in ids}
(R/'audits/batch-history/W06-L28-before-residual-repairs.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n');p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');packet=[]
for q in changed:
 x={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
pp=R/'audits/blind-W06-L28-residual-repairs.json';pp.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');m={'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blindPacketPath':str(pp.relative_to(R)),'blindPacketSha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'questionCount':2,'questions':[{'questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q)}for q in changed],'preservedQuestionHashes':preserved}
(R/'audits/W06-L28-residual-repairs-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(m['blindPacketSha256'])
