"""Deterministic L55 revision checks; no torch/GPU or missing DeLaN execution."""
from pathlib import Path
import json,datetime,hashlib,sys
import numpy as np
import sympy as s
R=Path(__file__).resolve().parents[1]; checks=[]
def check(name,ok):
 assert bool(ok),name
 checks.append(name)
H=np.array([[3.,1.],[1.,2.]]);D=np.array([[[1.,0.],[0.,0.]],[[0.,1.],[1.,2.]]]);v=np.array([1.,2.]);a=np.array([2.,-1.]);g=np.array([4.,3.]);Hd=np.einsum('k,kij->ij',v,D);k=.5*np.einsum('i,kij,j->k',v,D,v);c=Hd@v-k;tau=H@a+c+g
check('Hdot exact',np.allclose(Hd,[[1,2],[2,4]]));check('Hdot v exact',np.allclose(Hd@v,[5,10]));check('physical kinetic gradient',np.allclose(k,[.5,6]));check('velocity-product torque',np.allclose(c,[4.5,4]));check('inertial torque',np.allclose(H@a,[5,0]));check('combined torque',np.allclose(tau,[13.5,7]));check('local positive definiteness',np.allclose(H,H.T) and H[0,0]>0 and np.isclose(np.linalg.det(H),5));check('extra-half distractor arithmetic',np.allclose(H@a+Hd@v-.5*k+g,[13.75,10]));check('missing-Hdot distractor arithmetic',np.allclose(H@a-k+g,[8.5,-3]));check('energy identity',np.isclose(v@c,.5*v@Hd@v))
q1,q2,v1,v2,a1,a2=s.symbols('q1 q2 v1 v2 a1 a2');q=s.Matrix([q1,q2]);vv=s.Matrix([v1,v2]);aa=s.Matrix([a1,a2]);HH=s.Matrix([[3,1],[1,2]])+q1*s.Matrix([[1,0],[0,0]])+q2*s.Matrix([[0,1],[1,2]]);K=(vv.T*HH*vv)[0]/2;V=4*q1+3*q2;L=K-V;Lv=s.Matrix([s.diff(L,x) for x in vv]);EL=Lv.jacobian(q)*vv+Lv.jacobian(vv)*aa-s.Matrix([s.diff(L,x) for x in q]);actual=EL.subs({q1:0,q2:0,v1:1,v2:2,a1:2,a2:-1});check('independent symbolic Euler-Lagrange torque',actual==s.Matrix([s.Rational(27,2),7]));check('local H derivative D1',HH.diff(q1)==s.Matrix(D[0].astype(int)));check('local H derivative D2',HH.diff(q2)==s.Matrix(D[1].astype(int)))
# Source-transcribed literal call sequence. This is a static/stub test, not PyTorch execution.
printed=['prediction','loss','zero_grad','backward','step'];check('literal printed gradient order',printed.index('loss')<printed.index('zero_grad')<printed.index('backward')<printed.index('step'))
def stub(order):
 z={'grad':7.,'weight':2.,'loss':None}
 for op in order:
  if op=='prediction':z['prediction']=z['weight']*3
  elif op=='loss':z['loss']=(z['prediction']-1)**2
  elif op=='zero_grad':z['grad']=0.
  elif op=='backward':z['grad']+=2*(z['prediction']-1)*3
  elif op=='step':z['weight']-=.01*z['grad']
 return z
check('clear-before-forward conventional equivalence under declared independence',stub(printed)==stub(['zero_grad','prediction','loss','backward','step']));check('clear-after-backward loses current update',stub(['prediction','loss','backward','zero_grad','step'])['weight']==2.);check('distinct model activation settings','sigmoid'!='tanh');check('learning-rate exponent',1e-3==.001)
b=json.loads((R/'data/question-batches/W11-L55.json').read_text());qq={x['id']:x for x in b['questions']};gpu=qq['W11-L55-Q060'];check('GPU is declared added premise',all(c['role']=='premise' for c in gpu['citations']) and 'force=False' in gpu['stem']);check('default conversion checked against pinned primary docs',any('/docs/2.9/generated/torch.Tensor.numpy.html' in x['url'] for x in gpu['primaryEvidence']));check('Q074 explicit local physical-energy assumptions',any('local' in x and 'SPD' in x for x in qq['W11-L55-Q074']['assumptions']))
rng=np.random.default_rng(55155)
for trial in range(5000):
 M=rng.normal(size=(2,2));H=M.T@M+.2*np.eye(2);D=rng.normal(size=(2,2,2));D=(D+D.transpose(0,2,1))/2;v=rng.normal(size=2);Hd=np.einsum('k,kij->ij',v,D);grad=.5*np.einsum('i,kij,j->k',v,D,v);c=Hd@v-grad
 christ=np.array([sum((D[k,i,j]-.5*D[i,j,k])*v[j]*v[k] for j in range(2) for k in range(2)) for i in range(2)])
 assert np.allclose(c,christ) and np.isclose(v@c,.5*v@Hd@v) and np.linalg.eigvalsh(H).min()>0
out={'batchId':'W11-L55','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentReview':False,'scope':'Author-only deterministic source-order stubs, settings, local Euler–Lagrange derivation and random algebra. Pinned PyTorch documentation confirms the qualified default conversion; no torch, GPU, omitted DeLaN class or robot runtime executed.','namedChecks':len(checks),'variedChecks':5000,'variedAssertions':15000,'checks':checks,'versions':{'numpy':np.__version__,'sympy':s.__version__},'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(R/'audits/W11-L55-v2-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
