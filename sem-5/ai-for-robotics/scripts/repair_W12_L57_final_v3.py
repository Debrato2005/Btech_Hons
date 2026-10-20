"""Finish two disclosed residuals; preserve the remaining 84 whole objects."""
from pathlib import Path
import json,copy,hashlib,sys,datetime
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import question_hash,schema_errors
p=R/'data/question-batches/W12-L57.json';b=json.loads(p.read_text());old=copy.deepcopy(b);q=next(q for q in b['questions']if q['id'].endswith('Q014'));assert q['version']==2
q.update(version=3,difficulty='medium',assumptions=['Added ideal model of a rigid tool touching the same stationary point; all quantities are expressed in consistent frames and length units. Observations are exact and contain no measurement noise.'])
q['stem']='Use the added ideal TCP contact model R_i p + t_i = c, where R_i maps flange vectors to the base frame, p is the unknown fixed TCP offset in flange coordinates, t_i is the flange origin in base coordinates, and c is the unknown fixed contact point in base coordinates. Four observations repeat exactly the same flange orientation and contact pose. After subtracting observation 1 from the others to eliminate c, what can these equations establish about p?'
q['revisionAuthors'].append('build_offline_study_interface:L57-final-v3-repair');q['solution']['steps'].insert(0,'Subtract R_1 p + t_1 = c from each R_i p + t_i = c to eliminate the unknown contact point c.')
q['difficultyRationale']='Medium: form difference equations from a self-contained contact model, then infer identifiability under repeated geometry rather than recalling an answer-bearing rank assumption.'
changed=[q for q in b['questions']if q['id']in ('W12-L57-Q014','W12-L57-Q035')];assert all(q['version']==3 for q in changed)
for o,n in zip(old['questions'],b['questions']):assert o==n or n['id']=='W12-L57-Q014'
for q in changed:assert not schema_errors(q,json.loads((R/'data/schema.question.json').read_text()))
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');packet=[]
for q in changed:
 a={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in a['citations']:c.pop('evidenceText',None);c['locator']=f"Lecture L57, physical PDF page {c['physicalPage']}, printed footer {c['physicalPage']-1802}: inspect the source {c['kind']} content."
 packet.append(a)
pp='audits/blind-W12-L57-final-v3.json';(R/pp).write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');m={'packet':pp,'packetSha256':hashlib.sha256((R/pp).read_bytes()).hexdigest(),'questionHashes':{q['id']:question_hash(q)for q in changed},'other84CurrentQuestionsUnchanged':True,'independentReviewComplete':False,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'supersedes':'Only Q014 and Q035 from the v2 packet. Original frozen review and packet remain unchanged.'};(R/'audits/W12-L57-final-v3-minimal-bindings.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m))
