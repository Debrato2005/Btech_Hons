"""One-time repairs limited to seven independently flagged L43 objects."""
from pathlib import Path
import copy,json,hashlib,datetime
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W09-L43.json';b=json.loads(p.read_text());old=copy.deepcopy(b)
ids={'W09-L43-Q'+x for x in ['008','009','022','034','041','047','061']};qs=[]
for q in b['questions']:
 if q['id'] not in ids:continue
 assert q['version']==(1 if q['id'].endswith('061') else 2)
 q['version']+=1;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append('build_robotics_study_app:L43-residual-v3');qs.append(q)
 byp={c['physicalPage']:c for c in q['citations']}
 def cite(page,kind,text):
  c=byp[page];c['kind']=kind;c['role']='premise';c['locator']=f'Lecture 43, physical PDF page {page}, printed slide {page-1339}: '+text
 if q['id'].endswith('008'):cite(1348,'figure','Two sensor inputs, three hidden neurons and one output command with all adjacent-layer connections drawn; the weight count is derived from this figure.')
 elif q['id'].endswith('009'):q['citations']=[c for c in q['citations'] if c['physicalPage']==1347]
 elif q['id'].endswith('022'):
  cite(1354,'code','Demo pseudocode specifies two position inputs and links the complete implementation; the normalization formula is in the separately pinned notebook.')
  cite(1356,'table','Displayed feature vectors show row increments of 0.25 and column increments of 0.2; the separately pinned notebook specifies r/ROWS and c/COLS.')
  q['solution']['steps'][0]='Use ROWS=4 and COLS=5.';q['solution']['formulas'][0]['variables'].update(r='Row index 3',c='Column index 4',ROWS='Number of rows: 4',COLS='Number of columns: 5')
 elif q['id'].endswith('034'):
  s='The code uses y_t = torch.from_numpy(y).long(), producing one long-integer class index per training example.'
  q['solution']['justification']=q['solution']['simpleExplanation']=q['solution']['optionExplanations']['o3']=s
  for page in byp:
   cite(page,'code' if page==1354 else 'table','Demo pseudocode and complete-code link; exact target conversion is in the pinned notebook.' if page==1354 else 'The output display uses one-hot direction labels; this display differs from the long-integer class-index targets used for training in the pinned notebook.')
 elif q['id'].endswith('041'):
  cite(1355,'figure','Maze figure and text locate start (0,0), goal (3,4) and the three walls; these supply premises for the independently derived Manhattan lower bound.')
  cite(1357,'statement','The printed route lists eight positions and reports seven steps; its legality and attainment of the lower bound are checked separately.')
 elif q['id'].endswith('047'):
  cite(1358,'table','Advantages/challenges table states dependence on training data quality, computing cost and possible difficulty in unseen environments; these qualify benefit claims.');byp[1358]['role']='conflict'
 else:
  cite(1365,'statement','Foundation Models for Robotics bullet describes performing multiple robotic tasks using one AI model; only the final role is supported here.')
  roles=['Hand-programmed rules/maps','learned obstacle avoidance from sensor data','multiple robotic tasks using one model']
  order={'o1':[0,2,1],'o2':[0,1,2],'o3':[2,1,0],'o4':[1,0,2]}
  for o in q['options']:o['text']=' → '.join(roles[i] for i in order[o['id']])
  q['solution']['optionExplanations'].update(o1='This swaps the learned obstacle-avoidance role of early ANN navigation with the multi-task role of foundation models.',o3='This swaps the rule-based and foundation-model roles while retaining the middle ANN role.',o4='This swaps rule-based navigation with learned obstacle avoidance while retaining the final foundation-model role.')
  q['solution']['misconceptions']=[q['solution']['optionExplanations'][i] for i in ['o1','o3','o4']]
assert len(qs)==7
assert all(a==z for a,z in zip(old['questions'],b['questions']) if a['id'] not in ids)
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in qs:
 a={k:copy.deepcopy(q[k]) for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
 for c in a['citations']:c.pop('evidenceText',None)
 packet.append(a)
out=R/'audits/blind-W09-L43-v3.json';out.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
h=lambda q:hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ['status','reviewIds']},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
bind={'packetSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'questions':[{'id':q['id'],'version':q['version'],'questionHash':h(q)} for q in qs]}
(R/'audits/blind-binding-W09-L43-v3.json').write_text(json.dumps(bind,indent=2)+'\n')
(R/'audits/W09-L43-v3-repair-manifest.json').write_text(json.dumps({**bind,'actualPagesRevisited':[1348,1354,1355,1356,1357,1358,1365],'unrelatedObjectsPreserved':58,'time':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
print(bind['packetSha256'])
