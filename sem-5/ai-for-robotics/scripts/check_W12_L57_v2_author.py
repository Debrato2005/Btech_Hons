"""Permitted author-only algebra and inert concurrency models; no controller/vision runtime."""
from pathlib import Path
import json,datetime,hashlib,itertools
import numpy as np
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,ok):
 assert bool(ok),name
 checks.append(name)
def rz(a):
 c,s=np.cos(a),np.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1.]])
def ry(a):
 c,s=np.cos(a),np.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def tx(r,t):
 T=np.eye(4);T[:3,:3]=r;T[:3,3]=t;return T
A=tx(rz(.7),[1,2,3]);B=tx(ry(.4),[4,1,2])
check('Left inverse cancels common world factor',np.allclose(np.linalg.inv(A)@(A@B),B))
check('Right inverse generally fails left cancellation',not np.allclose(A@B@np.linalg.inv(A),B))
check('Full homogeneous transpose is not the inverse',not np.allclose(A.T@A,np.eye(4)))
check('Transforms generally do not commute',not np.allclose(A@B,B@A))
RR=[np.eye(3)]*4;D=np.vstack([r-RR[0]for r in RR[1:]])
check('Repeated TCP orientations have zero rank',np.linalg.matrix_rank(D)==0)
RR=[np.eye(3),rz(.4),ry(.6),ry(-.2)@rz(.7)];D=np.vstack([r-RR[0]for r in RR[1:]])
check('Declared varied TCP example has full rank',np.linalg.matrix_rank(D)==3)
p=np.array([.2,-.1,.3]);c=np.array([1.,2.,3.]);tt=[c-r@p for r in RR];rhs=np.concatenate([tt[0]-t for t in tt[1:]])
check('Full-rank added TCP observations recover offset',np.allclose(np.linalg.lstsq(D,rhs,rcond=None)[0],p))
# Added pinhole homography constraints demonstrate information diversity, not OpenCV execution.
def vij(H,i,j):
 return np.array([H[0,i]*H[0,j],H[0,i]*H[1,j]+H[1,i]*H[0,j],H[1,i]*H[1,j],H[2,i]*H[0,j]+H[0,i]*H[2,j],H[2,i]*H[1,j]+H[1,i]*H[2,j],H[2,i]*H[2,j]])
K=np.array([[600.,0,320],[0,580,240],[0,0,1.]])
def rows(rot):
 H=K@np.column_stack([rot[:,:2],np.array([.1,.2,2.])]);return np.stack([vij(H,0,1),vij(H,0,0)-vij(H,1,1)])
V=np.vstack([rows(ry(.2)@rz(.1))]*8);Vvar=np.vstack([rows(ry(a)@rz(b))for a,b in [(.2,.1),(-.4,.3),(.6,-.8),(-.3,-.2)]])
check('Repeated camera view adds no geometric rank',np.linalg.matrix_rank(V)==2)
check('Varied planar views constrain more intrinsic combinations',np.linalg.matrix_rank(Vvar)==5)
# Enumerate all order-preserving interleavings of writer and reader event streams.
def schedules(n,m):
 for pos in itertools.combinations(range(n+m),n):
  s=set(pos);yield ['W' if k in s else 'R' for k in range(n+m)]
mixed=0
for seq in schedules(3,3):
 vals=[0,0,0];seen=[];wi=ri=0
 for op in seq:
  if op=='W':vals[wi]=1;wi+=1
  else:seen.append(vals[ri]);ri+=1
 mixed+=len(set(seen))>1
check('Independent scalar updates allow mixed pose',mixed>0)
# W: write three staged fields, publish; R: capture published immutable record, read three fields.
coherent=0
for seq in schedules(4,4):
 old=[0,0,0];staged=[None]*3;published=old;wi=ri=0;chosen=None;seen=[]
 for op in seq:
  if op=='W':
   if wi<3:staged[wi]=1
   else:published=staged
   wi+=1
  else:
   if ri==0:chosen=published
   else:seen.append(chosen[ri-1])
   ri+=1
 assert seen in ([0,0,0],[1,1,1]);coherent+=1
check('Atomic immutable-record publication keeps all 70 schedules coherent',coherent==70)
# Explicit bad interleaving: version published before payload, then a reader sees new X but old Y/Z.
vals=[0,0,0];version=1;vals[0]=1;seen=vals.copy()
check('Sequence-first single-read design has a mixed-record counterexample',version==1 and seen==[1,0,0])
check('Equal pressure does not force equal force with unequal areas',2*3!=2*5)
check('Equal travel does not force equal force with unequal stiffness',2*3!=2*7)
q={q['id']:q for q in json.loads((R/'data/question-batches/W12-L57.json').read_text())['questions']}
check('Tool-number association is now exercised', 'tool number' in q['W12-L57-Q015']['stem'] or 'tool-number' in q['W12-L57-Q015']['stem'])
check('Both cable roles are in correct answer',all(s in next(o['text']for o in q['W12-L57-Q003']['options']if o['id']in q['W12-L57-Q003']['correctOptionIds'])for s in ('communication','power')))
check('Metric pose citations are qualified premises',all(c['role']=='premise'for c in q['W12-L57-Q036']['citations']))
check('Generic duplicate stem replaced','KSS responsibility groups' in q['W12-L57-Q005']['stem'])
rng=np.random.default_rng(57157)
for trial in range(2000):
 a,b=rng.uniform(-3,3,2);A=tx(rz(a),rng.normal(size=3));B=tx(ry(b),rng.normal(size=3));assert np.allclose(np.linalg.inv(A)@(A@B),B)
 p=rng.normal(size=3);c=rng.normal(size=3);ts=[c-r@p for r in RR];rhs=np.concatenate([ts[0]-t for t in ts[1:]]);assert np.allclose(np.linalg.lstsq(D,rhs,rcond=None)[0],p)
out={'batchId':'W12-L57','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentReview':False,'scope':'Author-only added linear algebra, planar-calibration constraint-rank example, explicit force counterexamples and inert exhaustive concurrency model. No OpenCV, robot/controller/network, omitted robosync.src or video runtime executed. Official OpenCV 4.13.0 pose prerequisites were read separately.','namedChecks':len(checks),'unsafeInterleavings':20,'unsafeMixedInterleavings':mixed,'safeInterleavings':coherent,'variedChecks':2000,'variedAssertions':4000,'checks':checks,'numpyVersion':np.__version__,'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(R/'audits/W12-L57-v2-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
