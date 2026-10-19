"""Reviewer-only arithmetic/code checks for changed/new L27 objects, no author script use."""
import json,datetime,pathlib,platform,importlib.util
import numpy as np
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.exceptions import NotFittedError
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'versions':{'python':platform.python_version(),'numpy':np.__version__,'sklearn':sklearn.__version__},'checks':[]}
def ck(n,v,d):
 assert bool(v),n
 out['checks'].append(dict(name=n,passed=True,detail=d))
X=np.array([[1,.5],[2,.5],[1,1],[5,1]]);y=np.array([4.9,9.8,9.8,49]);new=np.array([[3.5,.8]])
reg=LinearRegression().fit(X,y);v=reg.predict(new)[0]
ck('49 torque',5*9.8*1==49,'source label matched')
ck('4.9 distractor correction',.5*9.8*1==4.9 and 9.8*1==9.8,'factor-ten mass error, not omission of 5')
ck('OLS coefficients',np.allclose(reg.coef_,[1617/170,1323/85]) and np.isclose(reg.intercept_,-14.7),[reg.intercept_,*reg.coef_])
ck('affine answer',f'{v:.2f}'=='31.04',float(v))
ck('physical-product distractor',f'{3.5*9.8*.8:.2f}'=='27.44','27.44')
ck('omitted-intercept distractor',f'{v-reg.intercept_:.2f}'=='45.74','45.74')
ck('reversed-features distractor',f'{reg.predict(new[:,::-1])[0]:.2f}'=='47.39','47.39')
try:LinearRegression().predict(new);unfitted=False
except NotFittedError:unfitted=True
ck('unfitted sequence fails',unfitted,'actual NotFittedError')
wrong=LinearRegression().fit(X[:,::-1],y).predict(new)[0]
ck('unmatched feature reversal differs',not np.isclose(wrong,v),float(wrong))
ck('matched feature reversal preserves model',np.isclose(LinearRegression().fit(X[:,::-1],y).predict(new[:,::-1])[0],v),'same physical column meanings')
perm=np.array([3,0,2,1]);bad=LinearRegression().fit(X[perm],y).predict(new)[0]
ck('unpaired shuffle changes fit',not np.isclose(bad,v),float(bad))
ck('paired shuffle preserves fit',np.isclose(LinearRegression().fit(X[perm],y[perm]).predict(new)[0],v),'same examples')
# Identical measured features with different hidden-variable outcomes cannot be resolved by greater deterministic capacity.
ck('missing information counterexample',(0.5-0)**2+(0.5-1)**2==0.5,'same observed x, targets0and1; any single prediction has SSE>=0.5, regardless of capacity')
points=np.array([[0.,0],[0,1],[10,0],[10,1]])
cent=np.array([[5.,0],[5,1]])
labs=np.argmin(((points[:,None,:]-cent)**2).sum(2),axis=1)
updated=np.array([points[labs==i].mean(0) for i in range(2)])
sse=((points-cent[labs])**2).sum();vcent=np.array([[0.,.5],[10,.5]]);vlabs=np.array([0,0,1,1]);vsse=((points-vcent[vlabs])**2).sum()
ck('stable fixed point not global',np.allclose(cent,updated) and sse>vsse,{'horizontalSSE':float(sse),'verticalSSE':float(vsse)})
def generate(seed):
 np.random.seed(seed)
 return np.vstack([np.random.normal([10,20],[2,5],(100,2)),np.random.normal([22,90],[2,5],(100,2)),np.random.normal([25,40],[2,5],(100,2))])
data=generate(42);again=generate(42)
ck('global seed reproduces synthetic data',np.array_equal(data,again),'300x2 exactly repeated')
ck('other global seed changes synthetic data',not np.array_equal(data,generate(43)),'data seed distinct from estimator seed')
ck('normal output shape',data.shape==(300,2),'three 100x2 populations')
ck('normal samples exceed physical Wi-Fi bounds',np.any(data[:,1]>100),float(data[:,1].max()))
m=KMeans(n_clusters=3,random_state=42).fit(data)
base=m.cluster_centers_.copy();pred=m.predict([[23,85]])[0]
for n in [1,17,100,1000]:
 np.random.seed(100+n);np.random.normal(size=n)
 alt=KMeans(n_clusters=3,random_state=42).fit(data)
 assert np.array_equal(alt.cluster_centers_,base) and np.array_equal(alt.labels_,m.labels_)
ck('estimator integer seed independent of global RNG',True,'four different global states/additional draw counts, identical fixed-data fit')
ck('source prediction current environment',pred==0,{'label':int(pred),'nearestCenter':base[int(pred)].tolist(),'nInitDefault':m.get_params()['n_init']})
permutation=np.array([2,0,1]);renamed=permutation[m.labels_]
ck('consistent label permutation preserves pair membership',np.array_equal(m.labels_[:,None]==m.labels_[None,:],renamed[:,None]==renamed[None,:]),'300x300 pair-equivalence relation identical')
individual=m.labels_.copy();individual[0]=(individual[0]+1)%3
ck('unrelated per-point relabel can change membership',not np.array_equal(m.labels_[:,None]==m.labels_[None,:],individual[:,None]==individual[None,:]),'one point assigned a different cluster changes pair equivalence')
out['checkCount']=len(out['checks']);out['optionalMglearn']={'available':importlib.util.find_spec('mglearn') is not None,'executed':False,'scope':'Optional illustration not rerun; actual source figure inspected. No syntax-only check described as execution.'}
p=pathlib.Path('audits/W06-L27-v2-independent-computations.json');assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':True,'count':len(out['checks']),'report':str(p)}))
