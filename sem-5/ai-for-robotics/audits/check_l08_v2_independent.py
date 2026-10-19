#!/usr/bin/env python3
"""Independent mathematical checks for frozen L08 revision review; no author helpers."""
import math,json,random,datetime,hashlib
from pathlib import Path
import numpy as np
rng=random.Random(813729)
checks=[]
def record(name,n,detail): checks.append({'name':name,'cases':n,'passed':True,'detail':detail})
def close(x,y,tol=2e-9): assert np.allclose(x,y,atol=tol,rtol=tol),(x,y)
def fk(l1,l2,a,b,c):return np.array([l1*math.cos(a)+l2*math.cos(a+b),l1*math.sin(a)+l2*math.sin(a+b),math.cos(a+b+c),math.sin(a+b+c)])
def branches(l1,l2,x,y,phi):
 if l1<=0 or l2<=0: raise ValueError('positive lengths required')
 c=(x*x+y*y-l1*l1-l2*l2)/(2*l1*l2)
 if c < -1-1e-12 or c > 1+1e-12: return []
 if abs(x)+abs(y)<1e-12 and abs(l1-l2)<1e-12:return None
 c=max(-1.,min(1.,c))
 # Exact-boundary targets can incur a few ulps in the radius subtraction.
 if abs(abs(c)-1)<1e-12:c=math.copysign(1.,c)
 out=[]
 for sign in [-1,1]:
  s=sign*math.sqrt(max(0,1-c*c));b=math.atan2(s,c)
  a=math.atan2(y,x)-math.atan2(l2*s,l1+l2*c);z=phi-a-b
  out.append((a,b,z))
 return out
for _ in range(1000):
 l1,l2=[rng.uniform(.2,8) for i in range(2)];a=rng.uniform(-math.pi,math.pi);b=rng.uniform(.02,math.pi-.02)*rng.choice([-1,1]);phi=rng.uniform(-4*math.pi,4*math.pi)
 target=fk(l1,l2,a,b,phi-a-b);bs=branches(l1,l2,*target[:2],phi)
 assert len(bs)==2
 for aa,bb,cc in bs:close(fk(l1,l2,aa,bb,cc),target)
 assert abs(math.sin(bs[0][1]))>.001 and math.sin(bs[0][1])*math.sin(bs[1][1])<0
record('Two-branch planar IK reconstructs complete pose',2000,'1000 seeded nondegenerate targets, two independently reconstructed elbow/shoulder/wrist solutions each.')
for l1,l2 in [(1.,1.),(2.,1.),(1.,2.),(.4,3.7)]:
 for r in [abs(l1-l2),l1+l2]:
  if r==0:assert branches(l1,l2,0,0,.3) is None;continue
  bs=branches(l1,l2,r,0,.3)
  for b in bs: close(fk(l1,l2,*b),[r,0,math.cos(.3),math.sin(.3)])
  close([math.cos(bs[0][1]),math.sin(bs[0][1])],[math.cos(bs[1][1]),math.sin(bs[1][1])])
record('Boundary elbow coalescence',7,'Outer and nonzero inner annulus boundaries; plus/minus zero sine correspond to the same elbow rotation modulo2π.')
for _ in range(1000):
 l=rng.uniform(.1,10);a=rng.uniform(-10,10);phi=rng.uniform(-10,10)
 close(fk(l,l,a,math.pi,phi-a-math.pi),[0,0,math.cos(phi),math.sin(phi)])
record('Equal-link origin continuous family',1000,'Arbitrary shoulder with folded elbow and compensating wrist reconstructs zero translation and desired orientation.')
for args in [(0,1,1,0,0),(1,0,1,0,0),(-1,1,1,0,0)]:
 try:branches(*args);raise AssertionError('invalid length accepted')
 except ValueError:pass
assert branches(2,1,.5,0,0)==[] and branches(2,1,3.1,0,0)==[]
record('Length domains and unreachable annulus',5,'Zero/negative lengths rejected; inner hole and beyond outer radius both unreachable.')
for _ in range(1000):
 gamma,theta=[rng.uniform(-10,10) for i in range(2)]
 close(math.cos(gamma)*math.cos(theta)-math.sin(gamma)*math.sin(theta),math.cos(gamma+theta))
record('Corrected normalized x expansion',1000,'Correct cosine-sum identity holds; printed repeated-cosine factor is not used.')
# Concrete distractor counterexample also isolates the incorrect rationale in P0284-Q03 o3.
g,t=.4,.7
correct=math.cos(g)*math.cos(t)-math.sin(g)*math.sin(t)
wrong=[math.cos(g)*math.cos(t)-math.sin(g)*math.cos(t),math.cos(g)*math.sin(t)+math.sin(g)*math.sin(t),math.cos(g-t)]
assert all(abs(v-correct)>1e-4 for v in wrong)
record('P0284-Q03 distractor values',3,'o3 changes the first θ factor and subtraction sign; its second sinγ sinθ1 product is already the correct factor, disproving “both original factors changed incorrectly”.')
assert 2*(3*1)==6 and 3*1==3 and 3*(2*1)==6
record('Homogeneity counterexample',1,'f(3)=6; printed RHS3; repaired RHS6, exact integers.')
for _ in range(500):
 A=np.array([[rng.uniform(-2,2) for j in range(2)] for i in range(3)])
 if np.linalg.matrix_rank(A)<2:continue
 plus=np.linalg.solve(A.T@A,A.T)
 close(plus,np.linalg.pinv(A));close(plus@A,np.eye(2))
 W=A.T;wplus=W.T@np.linalg.inv(W@W.T);close(wplus,np.linalg.pinv(W));close(W@wplus,np.eye(2))
record('Tall and wide full-rank shortcuts',1000,'500 seeded3×2 matrices and their2×3 transposes; compare independent formulas and identity products to SVD pseudoinverse.')
A=np.array([[1.,2.],[2.,4.],[3.,6.]])
assert np.linalg.matrix_rank(A.T@A)==1
P=np.linalg.pinv(A);close(A@P@A,A)
record('Rank-deficient pseudoinverse exists while Gram inverse fails',1,'Dependent columns yield singular Gram matrix but satisfy Moore–Penrose reconstruction with SVD.')
J=np.array([[1.,1.]]);P=J.T@np.linalg.inv(J@J.T);u=P@np.array([2.]);close(u,[1,1])
for t in np.linspace(-20,20,1001):
 v=np.array([1+t,1-t]);close(J@v,[2]);close(v@v,2+2*t*t)
assert len({tuple(v) for v in [(1,1),(2,0),(0,0),(2,2)]})==4
record('Wide minimum-norm example and distinct options',1001,'Every exact solution[1+t,1−t] has squared norm2+2t²; only[1,1] minimizes it. Other choices are distinct.')
for _ in range(1000):
 r,d=rng.uniform(.01,4),rng.uniform(.01,4);phi=rng.choice([0,math.pi/2,math.pi,3*math.pi/2,rng.uniform(-20,20)])
 J=np.array([[-r/(2*d),r/(2*d)],[r*math.cos(phi)/2]*2,[r*math.sin(phi)/2]*2])
 assert np.linalg.matrix_rank(J)==2
 v,w=rng.uniform(-10,10),rng.uniform(-10,10);u=np.array([(v-d*w)/r,(v+d*w)/r]);q=J@u
 close(q,[w,v*math.cos(phi),v*math.sin(phi)]);close(np.linalg.pinv(J)@q,u)
record('Differential-drive ranks and feasible-rate inverse',1000,'Positive radius/half-track maintain rank2 including90°; signed wheel rates reconstruct yaw and world translation.')
out={'reviewerId':'independent-reviewer-robotics-batches-v2','runAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seed':813729,'source':'Actual lecture pages inspected; independently coded from persisted pre-key reasoning, not author scripts.','checks':checks,'allPassed':True,'testDevelopmentNote':'The initial floating-point endpoint test produced ±2.98e-8 sine for the exact inner radius with lengths0.4,3.7 because computed c2 was−0.9999999999999996. The test helper now snaps c2 to an endpoint only within1e-12, distinguishing roundoff from a new physical branch. No authored question content changed.','limitations':'No numerical question generator or runtime robot is claimed. These are mathematical checks for34 fixed review items; no instantiated variants are present.'}
p=Path(__file__).with_name('W02-L08-v2-independent-computations.json');p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checks':len(checks),'cases':sum(c['cases'] for c in checks),'allPassed':True,'path':str(p)}))
