from pathlib import Path
import json,copy,hashlib,datetime
R=Path('/workspace/shared/Btech_Hons/sem-5/ai-for-robotics');p=R/'data/question-batches/W04-L17.json';b=json.loads(p.read_text());old=copy.deepcopy(b);nums={3,16,18,22,50}
h=lambda q:hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in['status','reviewIds']},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert all(q['version']==2 for q in b['questions']if int(q['id'][-3:])in nums)
a=R/'audits/batch-history/W04-L17-before-final-metadata-repairs.json';assert not a.exists();a.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n');preserved={q['id']:h(q)for q in old['questions']if int(q['id'][-3:])not in nums}
for q in b['questions']:
 n=int(q['id'][-3:])
 if n not in nums:continue
 q['version']+=1;q['status']='draft';q['reviewIds']=[];q['revisionAuthors']=list(dict.fromkeys(q.get('revisionAuthors',[])+['robotics-integration-author-L17']))
 if n==3:
  q['stem']='In the introductory Cartesian-path diagram, what do the three yellow intermediate markers explicitly show, as distinct from the general text about Cartesian pose trajectories?'
  ts={'o1':'Ordered XYZ position points along the path; intermediate orientation axes are not drawn at those markers','o2':'Alternative final XYZ goals, any one replacing the red END point','o3':'Three complete pose frames with visibly drawn orientation axes at every yellow marker','o4':'Position-error tolerance boundaries surrounding only the final END point'}
  reasons={'o1':'The markers are labeled(x1,y1,z1),(x2,y2,z2),(x3,y3,z3), without orientation triads at those points.','o2':'They lie in sequence between START and END rather than replacing END.','o3':'The page discusses orientation generally, but no intermediate orientation axes are drawn at the yellow markers.','o4':'They are separate path points, not a tolerance region around one endpoint.'}
  for o in q['options']:o['text']=ts[o['id']]
  why='The actual diagram shows yellow XYZ via-position dots; the adjacent text states that Cartesian schemes can specify both position and orientation, but the dots alone do not display intermediate orientations.'
  q['solution']['justification']=q['solution']['simpleExplanation']=why;q['solution']['optionExplanations']=reasons;q['solution']['misconceptions']=[reasons[k]for k in reasons if k not in q['correctOptionIds']];q['solution']['steps']=[]
  for c in b['concepts']:
   if c['id']in q['conceptIds']:c['description']=why
 if n in[16,18]:
  for c in q['citations']:
   if c['physicalPage']==514:c['kind']='statement';c['role']='premise'
 if n==22:
  for c in q['citations']:c['kind']={517:'statement',518:'figure',520:'equation'}[c['physicalPage']]
 if n==50:
  for c in q['citations']:
   if c['physicalPage']in[536,537]:c['kind']={536:'table',537:'figure'}[c['physicalPage']]
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');assert all(h(next(q for q in b['questions']if q['id']==k))==v for k,v in preserved.items())
packet=[]
for q in b['questions']:
 if int(q['id'][-3:])not in nums:continue
 d={k:copy.deepcopy(q[k])for k in['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
 for c in d['citations']:c.pop('evidenceText',None)
 packet.append(d)
f=R/'audits/blind-W04-L17-final-repairs.json';f.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');m={'changedIds':[q['id']for q in packet],'preservedHashes':preserved,'packetSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'review':'pending; prior exposure disclosed','visualCorrection':'P508 yellow XYZ dots are not intermediate orientation frames; fresh actual render inspected.'};(R/'audits/W04-L17-final-repair-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(m['packetSha256'],len(preserved),'accepted hashes preserved')
# Answer-free exact current version map requested by L23 reviewer.
x=json.loads((R/'data/question-batches/W05-L23.json').read_text());(R/'audits/W05-L23-question-hashes.json').write_text(json.dumps({q['id']:{'version':q['version'],'questionSha256':h(q)}for q in x['questions']},indent=2)+'\n')
