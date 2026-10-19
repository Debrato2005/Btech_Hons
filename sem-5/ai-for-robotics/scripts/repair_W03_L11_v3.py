#!/usr/bin/env python3
"""Only the three independently flagged v2 objects change. No self-approval."""
import json,copy,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text())
def write(p,o):(R/p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def sha(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
p='data/question-batches/archive/W03-L11-v2.json'
if not (R/p).exists():write(p,read('data/question-batches/W03-L11.json'))
b=read(p);old=copy.deepcopy(b);ids={'W03-L11-P0372-Q03','W03-L11-P0372-Q05','W03-L11-P0374-Q02'}
review=read('data/reviews/W03-L11-v2-independent-contracts.json')
assert {r['questionId'] for r in review if r['decision']=='flagged'}==ids
changed=[]
for q in b['questions']:
 if q['id'] not in ids:continue
 assert q['version']==2
 q.update(version=3,status='draft',reviewIds=[])
 q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+['L11-author-20261019']))
 if '-P0372-' in q['id']:
  q['solution']['formulas']=[]
 else:
  q.update(stem='Two point masses of 1 kg each are at (1,2,3) m and (1,2,−3) m in the same orthonormal frame. What is their signed inertia tensor about that frame’s origin? Use Ixy=−Σmxy for the matrix off-diagonal entry.',type='numerical',difficulty='medium',cognitiveSkill='numerical',assumptions=['Point-mass idealization; positions refer to one common fixed orthonormal frame and its stated origin, not the center of mass.','The requested matrix uses signed off-diagonal entries, the negatives of the raw products.'])
  values={'o1':'[[26,−4,0],[−4,20,0],[0,0,10]] kg·m²','o2':'[[26,4,0],[4,20,0],[0,0,10]] kg·m²','o3':'[[26,0,0],[0,20,0],[0,0,10]] kg·m²','o4':'[[2,−4,0],[−4,8,0],[0,0,18]] kg·m²'}
  for o in q['options']:o['text']=values[o['id']]
  why={'o1':'Both masses contribute: Ixx=2(2²+3²)=26, Iyy=2(1²+3²)=20 and Izz=2(1²+2²)=10. The signed xy entry is −2(1)(2)=−4; opposite z coordinates cancel xz and yz entries.','o2':'This inserts the positive raw product Σmxy=4 rather than its negative as the signed matrix entry.','o3':'Reflection in xy cancels products containing z, but does not cancel the nonzero xy product.','o4':'These diagonal entries use the coordinate along each axis squared instead of the sum of the two perpendicular coordinate squares.'}
  q['solution'].update(justification=why['o1'],simpleExplanation=why['o1'],optionExplanations={k:('Correct. ' if k=='o1' else 'Incorrect. ')+v for k,v in why.items()},steps=['Use the discrete-mass form I=Σm[(rᵀr)I3−rrᵀ].','Each point has squared coordinates (1,4,9), so add twice (13,10,5) for the diagonal.','The xy raw product is 2+2=4, while xz=3−3=0 and yz=6−6=0.','Negate raw products for the off-diagonal matrix entries: I=[[26,−4,0],[−4,20,0],[0,0,10]] kg·m².'],misconceptions=[why[k] for k in ['o2','o3','o4']],formulas=[dict(expression='I=Σ_j m_j[(r_jᵀr_j)I3−r_j r_jᵀ]',variables={'I':'signed inertia tensor about the chosen origin','j':'point-mass index, j=1,2','m_j':'mass of point j','r_j':'column vector (x_j,y_j,z_j) from origin to point j','I3':'3×3 identity matrix'},units={'I':'kg·m²','m_j':'kg','r_j':'m','j,I3':'dimensionless'},assumptions=q['assumptions'])])
  cite=copy.deepcopy(q['citations'][0]);cite['role']='premise'
  q['citations']=[cite]
  for page,loc in [(361,'symmetric inertia matrix with negative raw products'),(362,'six scalar mass-moment and raw-product integrals')]:
   t=copy.deepcopy(cite);t.update(slideId=f'lectures-p{page:04}',physicalPage=page,kind='derivation',locator=f'Printed slide {page-351}: {loc}',evidenceText=(R/f'sources/text/lectures/page-{page:04}.txt').read_text().strip());q['citations'].append(t)
 changed.append(q)
for c in b['concepts']:
 if c['id']=='W03-L11-P0374-C01':
  oldstem=next(q for q in old['questions'] if q['id']=='W03-L11-P0374-Q02')['stem']
  newstem=next(q for q in changed if q['id']=='W03-L11-P0374-Q02')['stem']
  c['examinationAngles']=[newstem if s==oldstem else s for s in c.get('examinationAngles',[])]
accepted=[q for q in old['questions'] if q['id'] not in ids]
assert len(accepted)==106
for x in accepted:assert x==next(q for q in b['questions'] if q['id']==x['id'])
import sympy as s
mat=s.zeros(3)
for r in [s.Matrix([1,2,3]),s.Matrix([1,2,-3])]:mat+=(r.dot(r)*s.eye(3)-r*r.T)
assert mat==s.Matrix([[26,-4,0],[-4,20,0],[0,0,10]])
write('data/question-batches/W03-L11.json',b)
blind=[{**{k:q[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions')},'citations':[{k:v for k,v in x.items() if k!='evidenceText'} for x in q['citations']]} for q in changed]
write('audits/blind-W03-L11-v3.json',blind)
h=hashlib.sha256((R/'audits/blind-W03-L11-v3.json').read_bytes()).hexdigest()
write('audits/W03-L11-v3-review-manifest.json',dict(batchId='W03-L11',blindPacketSha256=h,questionSha256={q['id']:sha(q) for q in changed},preservedAcceptedCount=106,preservedAcceptedHashes={q['id']:sha(q) for q in accepted},independentReviewPending=True))
write('audits/W03-L11-v3-author-checks.json',dict(changedCount=3,preservedCount=106,acceptedObjectsUnchanged=True,keysUnchanged=True,pointMassTensor=mat.tolist().__str__(),numericalCheckPassed=True,changes=['Remove unrelated formulas from P0372-Q03/Q05.','Replace duplicate P0374-Q02 with a complete discrete signed-tensor calculation.'],reviewInput='data/reviews/W03-L11-v2-independent-contracts.json'))
(R/'audits/handoffs/W03-L11-v3.md').write_text(f'# L11 v3 frozen\n\nThree v3 repairs; all 106 accepted objects and hashes remain unchanged. Blind packet audits/blind-W03-L11-v3.json; SHA256 {h}. Manifest audits/W03-L11-v3-review-manifest.json. SymPy exact tensor check passes. No self-approval; all three remain draft. Archive data/question-batches/archive/W03-L11-v2.json. Reproduce only with scripts/repair_W03_L11_v3.py, not the older generators. Independent re-review required; no canonical or Git writes.\n')
print(h)
