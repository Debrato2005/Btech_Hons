#!/usr/bin/env python3
"""Independent L08 source-premise checks. Does not read question keys or author code."""
import json, math, datetime
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
rng=np.random.default_rng(812026)

def pose(L1,L2,q):
 a,b,c=q
 return np.array([L1*math.cos(a)+L2*math.cos(a+b),L1*math.sin(a)+L2*math.sin(a+b),a+b+c])
def wrap(a):return math.atan2(math.sin(a),math.cos(a))
def inverse(L1,L2,x,y,phi):
 c=(x*x+y*y-L1*L1-L2*L2)/(2*L1*L2)
 if c < -1-1e-12 or c > 1+1e-12:return []
 c=float(np.clip(c,-1,1));s=math.sqrt(max(0,1-c*c));out=[]
 for sign in [1,-1]:
  b=math.atan2(sign*s,c);a=math.atan2(y,x)-math.atan2(L2*sign*s,L1+L2*c)
  out.append((a,b,phi-a-b))
 return out

def matrix(r,d,phi):return np.array([[-r/(2*d),r/(2*d)],[r*math.cos(phi)/2,r*math.cos(phi)/2],[r*math.sin(phi)/2,r*math.sin(phi)/2]])
def pinv_formula(r,d,phi):return np.array([[-d/r,math.cos(phi)/r,math.sin(phi)/r],[d/r,math.cos(phi)/r,math.sin(phi)/r]])
checks=[]
def record(name,count,detail):checks.append({'name':name,'cases':count,'passed':True,'detail':detail})
maxerr=0
for _ in range(1000):
 L1,L2=rng.uniform(.2,4,2);q=rng.uniform(-math.pi,math.pi,3);x,y,phi=pose(L1,L2,q)
 branches=inverse(L1,L2,x,y,phi);assert len(branches)==2
 for branch in branches:
  back=pose(L1,L2,branch);err=max(np.max(np.abs(back[:2]-[x,y])),abs(wrap(back[2]-phi)));maxerr=max(maxerr,err);assert err<1e-10
  rho=math.hypot(x,y);psi=math.acos(float(np.clip((rho*rho+L1*L1-L2*L2)/(2*L1*rho),-1,1)))
  geo_a=math.atan2(y,x)+(psi if branch[1]<0 else -psi)
  assert abs(wrap(geo_a-branch[0]))<1e-8
record('Planar IK two-branch round trip and geometric shoulder equivalence',1000,{'maxPoseResidual':float(maxerr),'branchesPerCase':2})
for _ in range(100):
 L=rng.uniform(.1,5);a,phi=rng.uniform(-math.pi,math.pi,2);actual=pose(L,L,[a,math.pi,phi-a-math.pi]);assert np.linalg.norm(actual[:2])<1e-12 and abs(wrap(actual[2]-phi))<1e-12
record('Equal-link origin continuous solution family',100,'Position cancels for every tested shoulder; wrist preserves specified orientation.')
assert inverse(2,1,.5,0,0)==[] and inverse(2,1,3.5,0,0)==[]
for radius,elbow in [(3,0),(1,math.pi)]:
 branches=inverse(2,1,radius,0,0);assert all(abs(wrap(q[1]-elbow))<1e-12 for q in branches)
record('Inner/outer reachability and coincident boundary branches',4,{'innerCosine':(.5**2-5)/4,'outerCosine':(3.5**2-5)/4})
for _ in range(1000):
 r,d=rng.uniform(.03,1,2);phi=rng.uniform(-math.pi,math.pi);J=matrix(r,d,phi);P=pinv_formula(r,d,phi)
 assert np.linalg.matrix_rank(J)==2 and np.allclose(P,np.linalg.pinv(J),atol=1e-10)
 assert np.allclose(P@J,np.eye(2));projector=J@P
 assert np.allclose(projector@projector,projector) and np.allclose(projector,projector.T)
 u=rng.uniform(-10,10,2);assert np.allclose(P@J@u,u)
 b=rng.uniform(-2,2,3);res=b-projector@b;assert np.allclose(J.T@res,np.zeros(2),atol=1e-10)
 assert abs(-math.sin(phi)*(J@u)[1]+math.cos(phi)*(J@u)[2])<1e-10
record('Differential-drive rank, pseudoinverse, projection and no-slip checks',1000,'Compared derived pseudoinverse with independently computed SVD pseudoinverse.')
for phi in [0,math.pi/2,math.pi,3*math.pi/2]:assert np.linalg.matrix_rank(matrix(.1,.2,phi))==2
assert np.allclose(pinv_formula(.1,.2,0)@np.array([0,0,1]),[0,0])
record('Cardinal headings retain rank; pure lateral request projects to zero',5,'Zero entries do not imply rank loss; no instantaneous lateral actuator.')
J=np.array([[1,0],[0,1],[0,0]],float);b=np.array([2,3,4]);u=np.linalg.pinv(J)@b;assert np.allclose(u,[2,3]) and np.allclose(b-J@u,[0,0,4])
Jw=np.array([[1.,1.]]);assert np.allclose(np.linalg.pinv(Jw)@np.array([2]),[1,1]);Js=np.array([[1.,2.],[2.,4.],[0.,0.]]);assert np.linalg.matrix_rank(Js.T@Js)==1 and np.isfinite(np.linalg.pinv(Js)).all()
record('Tall residual, wide minimum norm and rank-deficient shortcut',3,'General pseudoinverse still exists when the ordinary Gram inverse fails.')
def se3():
 Q,_=np.linalg.qr(rng.normal(size=(3,3)));Q[:,0]*=np.linalg.det(Q);T=np.eye(4);T[:3,:3]=Q;T[:3,3]=rng.normal(size=3);return T
for _ in range(100):
 SB,ST,WT=se3(),se3(),se3();BW=np.linalg.inv(SB)@ST@np.linalg.inv(WT);assert np.allclose(SB@BW@WT,ST)
record('Task-to-wrist frame chain',100,'Random rigid calibrations satisfy ^S_B T ^B_W T ^W_T T = ^S_T T.')
assert np.allclose(pose(1,1,np.deg2rad([0,90,-90]))[:2],[1,1]);assert np.allclose(pose(1,1,np.deg2rad([90,-90,0]))[:2],[1,1]);assert np.allclose(matrix(.1,.2,math.pi/2)@np.array([3,7]),[1,0,.5])
for v,w,expected in [(.5,1,[3,7]),(0,1,[-2,2]),(-.4,0,[-4,-4])]:assert np.allclose([(v-.2*w)/.1,(v+.2*w)/.1],expected)
record('Question numerical examples',6,'Checked both complete planar triples, source state order, turning signs, half-track and backward speeds.')
report={'reviewerId':'build_offline_study_interface-L08-independent','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'usesQuestionKeys':False,'seed':812026,'passed':True,'checks':checks}
(ROOT/'audits/W02-L08-independent-computations.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'groups':len(checks),'cases':sum(x['cases'] for x in checks)}))
