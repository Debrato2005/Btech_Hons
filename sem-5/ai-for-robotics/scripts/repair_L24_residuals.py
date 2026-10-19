"""One-time L24 residual repairs; do not rerun after review."""
from pathlib import Path
import json,copy,hashlib,datetime
from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W05-L24.json';b=json.loads(p.read_text());old=copy.deepcopy(b)
ids=['W05-L24-P0733-Q02','W05-L24-P0735-Q02','W05-L24-P0738-Q01'];preserved={q['id']:question_hash(q) for q in b['questions'] if q['id'] not in ids};changed=[]
for q in b['questions']:
 if q['id'] not in ids:continue
 assert q['version']==2
 if q['id']==ids[0]:
  next(o for o in q['options'] if o['id']=='o4')['text']='Repeating one stored sensor reading at several faster cycles supplies a new physical measurement at each cycle'
  q['solution']['optionExplanations']['o4']='Repeating stored data changes command timing but does not create a new physical measurement; a fresh measurement requires a new sensor observation.'
 elif q['id']==ids[1]:
  q['assumptions']=['Use the printed homogeneous-error approximation, with zero or neglected forcing residual and invertible actual inertia M.']
  q['solution']['formulas']=[{'expression':'Ë + M⁻¹K_v Ė + M⁻¹K_p E = 0; (M⁻¹D)_ij = (M⁻¹)_ij D_jj for diagonal D','variables':{'M':'actual inertia matrix at the current configuration','E,Ė,Ë':'desired-minus-actual errors and time derivatives','K_v,K_p':'torque-domain diagonal feedback gains','D':'one of the diagonal gain matrices','i,j':'row and column indices'},'units':{'M':'kg·m² for revolute joints','E':'rad','Ė':'rad/s','Ë':'rad/s²','K_v':'N·m·s/rad','K_p':'N·m/rad'},'assumptions':['The zero-residual homogeneous approximation is stipulated; the matrix identity holds for any compatible diagonal D.']}]
  q['solution']['steps']=['For diagonal D, evaluate (M⁻¹D)_ij=Σ_k(M⁻¹)_ikD_kj.','Only k=j survives, giving (M⁻¹)_ijD_jj.','An off-diagonal inertia-inverse entry remains nonzero when multiplied by a nonzero corresponding gain.']
 else:
  f=q['solution']['formulas'][0];f['expression']='Ë+K_vĖ+K_pE=M(q(t))⁻¹τ_d; E_ss=K_p⁻¹M(q_eq)⁻¹τ_d'
  f['variables']['M']='actual inertia evaluated at current configuration q(t) in the transient equation and at equilibrium configuration q_eq in the steady equation';f['variables']['q(t),q_eq']='current actual joint configuration and reached equilibrium configuration'
 q['version']=3;q['status']='draft';q['reviewIds']=[];q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+['robotics-integration-L24-residual-repairs']))
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']];changed.append(q)
assert preserved=={q['id']:question_hash(q) for q in b['questions'] if q['id'] not in ids}
(R/'audits/batch-history/W05-L24-before-residual-repairs.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n');p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in changed:
 x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
pp=R/'audits/blind-W05-L24-residual-repairs.json';pp.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
m={'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blindPacketPath':str(pp.relative_to(R)),'blindPacketSha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'questionCount':3,'questions':[{'questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q)} for q in changed],'preservedQuestionHashes':preserved}
(R/'audits/W05-L24-residual-repairs-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({k:v for k,v in m.items() if k not in ['questions','preservedQuestionHashes']}))
