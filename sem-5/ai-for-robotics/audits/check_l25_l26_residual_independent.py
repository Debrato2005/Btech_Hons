"""Independent reviewer checks, authored after before-reveal inferences; no author scripts used."""
import json,datetime,platform,pathlib
import numpy as np
import sklearn
from sklearn.neighbors import KNeighborsClassifier
out={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewerId':'independent-reviewer-robotics-batches-v2','versions':{'python':platform.python_version(),'numpy':np.__version__,'sklearn':sklearn.__version__},'checks':[]}
def check(name,value,detail):
 assert bool(value),name
 out['checks'].append({'name':name,'passed':True,'detail':detail})
kp=np.array([4.,9.]);kv=2*np.sqrt(kp)
check('critical gains and stable poles',np.allclose(kv,[4,6]) and np.all(-kv/2<0),'gains 4,6; poles -2,-3')
check('overdamped option',np.all(np.array([8,18])**2-4*kp>0),'positive discriminants')
check('negative damping option unstable',np.all(-np.array([-4,-6])/2>0),'repeated positive poles')
check('underdamped option',np.all(np.array([2,3])**2-4*kp<0),'negative discriminants')
check('inertia mismatch',3*4/2==6,'F=12 N; acceleration 6 m/s^2')
check('reversed inertia ratio',np.isclose(2*4/3,8/3),'o4 arithmetic 8/3 distinct from 6')
J=np.array([[1,2],[0,1.]]);D=np.array([[0,1],[1,0.]]);xd=np.array([3.,1]);xdd=np.array([2.,4]);I=np.linalg.inv(J)
v=I@xd;a=I@(xdd-D@v)
check('joint velocity',np.allclose(v,[1,1]),v.tolist())
check('correct acceleration',np.allclose(a,[-5,3]),a.tolist())
check('omission distractor',np.allclose(I@xdd,[-6,4]),(I@xdd).tolist())
check('addition distractor',np.allclose(I@(xdd+D@v),[-7,5]),(I@(xdd+D@v)).tolist())
wrongorder=I@xdd-I@I@D@xd
check('noncommuting distractor',np.allclose(wrongorder,[5,1]),wrongorder.tolist())
check('acceleration residual',np.allclose(J@a+D@v,xdd),'original equation recovered')
X=np.array([[1,10],[1.2,12],[.8,60],[.5,65],[.9,30],[1,35]])
y=np.array([0,0,1,1,2,2]);names={0:'smooth',1:'gravel',2:'grass'}
check('fifth row alignment',np.allclose(X[4],[.9,30]) and names[y[4]]=='grass','target 2 grass')
m=KNeighborsClassifier(n_neighbors=1).fit(X,y);query=np.array([[.7,62]])
pred=m.predict(query)
check('one sample input shape',query.shape==(1,2),list(query.shape))
check('prediction vector shape',pred.shape==(1,),list(pred.shape))
check('scalar indexing',np.isscalar(pred[0]) and pred[0]==1,int(pred[0]))
d2=np.sum((X-query)**2,axis=1)
check('manual unique nearest neighbor',np.argmin(d2)==2 and (d2==d2.min()).sum()==1,d2.tolist())
try:m.predict(np.array([.7,62]));bad=False
except ValueError:bad=True
check('unbatched input rejected',bad,'actual ValueError, not syntax-only test')
check('prediction not score',pred.dtype.kind in 'iu' and names[pred[0]]=='gravel','class label; no known query target supplied')
check('image structured and flattening',np.zeros((1,8,8)).reshape(1,-1).shape==(1,64),'one sample can have two native spatial axes')
rng=np.random.default_rng(202610191937)
maxerr=0
for i in range(500):
 R,_=np.linalg.qr(rng.normal(size=(3,3)))
 if np.linalg.det(R)<0:R[:,0]*=-1
 vb=rng.normal(size=3);ft=rng.normal(size=3);jb=rng.normal(size=(3,4));qd=rng.normal(size=4)
 fb=R.T@ft;vt=R@vb
 assert np.allclose(ft@vt,fb@vb)
 assert np.allclose(jb.T@fb,(R@jb).T@ft)
 maxerr=max(maxerr,abs(ft@vt-fb@vb))
check('500 proper-rotation power and torque cases',True,{'count':500,'maxPowerError':maxerr})
R=np.array([[0,-1,0],[1,0,0],[0,0,1.]])
ft=np.array([1.,2,3]);vb=np.array([1.,0,0])
check('counterexample to wrong rotation direction',not np.isclose((R@ft)@vb,ft@(R@vb)),'R != R transpose for general rotation')
errs=[]
for i in range(500):
 n=int(rng.integers(5,20));p=int(rng.integers(1,min(5,n-1)))
 A=np.column_stack([rng.normal(size=(n,p)),np.ones(n)]);yy=rng.normal(size=n)
 assert np.linalg.matrix_rank(A)==p+1
 theta=np.linalg.solve(A.T@A,A.T@yy);qr=np.linalg.lstsq(A,yy,rcond=None)[0]
 assert np.allclose(theta,qr,rtol=1e-8,atol=1e-8)
 gradient=2*A.T@(A@theta-yy)
 assert np.linalg.norm(gradient)<1e-8
 delta=rng.normal(size=p+1)
 assert np.sum((A@(theta+delta)-yy)**2)>=np.sum((A@theta-yy)**2)-1e-9
 errs.append(float(np.linalg.norm(gradient)))
check('500 full-rank direct OLS cases',True,{'count':500,'maxGradientNorm':max(errs),'checks':'normal equations versus lstsq, stationary gradient and convex perturbation'})
A=np.array([[1.,1],[2,2],[3,3]])
check('rank-deficient boundary',np.linalg.matrix_rank(A)==1 and np.isclose(np.linalg.det(A.T@A),0),'inverse-form full-rank condition essential')
try:np.linalg.solve(A.T@A,A.T@np.ones(3));singular=False
except np.linalg.LinAlgError:singular=True
check('singular inverse solve rejected',singular,'actual LinAlgError for excluded domain')
out['checkCount']=len(out['checks']);out['executionScope']='Actual independent NumPy/sklearn computations and varied cases, no author check scripts accessed. No whole-lecture coverage claim.'
path=pathlib.Path('audits/L25-L26-residual-independent-computations.json');path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checks':out['checkCount'],'passed':True,'report':str(path)}))
