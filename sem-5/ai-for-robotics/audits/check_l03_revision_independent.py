"""Independent fixed/body derivative checks. Does not import author keys/checks."""
import json, math
from pathlib import Path
import numpy as np

def S(w):
 x,y,z=w; return np.array([[0,-z,y],[z,0,-x],[-y,x,0]],float)
R=np.array([[0,-1,0],[1,0,0],[0,0,1]],float);w=np.array([2,0,0.]);D=S(w)@R
assert np.array_equal(D,[[0,0,0],[0,0,-2],[2,0,0]])
assert np.array_equal(R@S(w),[[0,0,2],[0,0,0],[0,2,0]])
assert not np.array_equal(D,-D.T)
assert np.array_equal(D@R.T,S(w))
assert np.array_equal(R.T@D,S(R.T@w))
assert np.array_equal(R@S(R.T@w),D)
assert np.array_equal(S(np.zeros(3))@R,np.zeros((3,3)))
rng=np.random.default_rng(310419)
for _ in range(1000):
 Q,T=np.linalg.qr(rng.normal(size=(3,3))); Q[:,0]*=np.linalg.det(Q)
 w=rng.normal(size=3); D=S(w)@Q
 assert np.allclose(D@Q.T,S(w))
 assert np.allclose(Q.T@D,S(Q.T@w))
 assert np.allclose(Q@S(Q.T@w),D)
 assert np.allclose(D@Q.T+Q@D.T,0)
 assert np.allclose(Q.T@D+D.T@Q,0)
assert not np.array_equal(np.array([[0,1],[1,0]]),-np.array([[0,1],[1,0]]).T)
for q,v,u in [(0,0,0),(1,2,3),(-1,4,-2)]:
 acc=-2*q-3*v+u;assert acc+3*v+2*q==u
for likelihood in [[.2,.7,.1],[0,1,0],[.999,.0009,.0001]]:
 post=np.array(likelihood)*(1/3);post/=post.sum();assert np.argmax(post)==np.argmax(likelihood)
report={'fixedMatrixChecks':7,'randomProperRotationCases':1000,'seed':310419,'skewCounterexamples':2,'stateEquationCases':3,'uniformPriorCases':3,'allPassed':True,'scope':'Two fixed standalone gap items, not a numerical variant generator. No author computation script read.'}
Path('audits/W01-L03-v2-GAP-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
