"""L26 independent source/code calculations before any current or prior key access."""
import datetime,json,math
from pathlib import Path
import numpy as np
import sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
checks=[]
def ck(name,actual,expected):
 assert np.allclose(actual,expected) if not isinstance(expected,str) else actual==expected,(name,actual,expected)
 checks.append(name)
blacklist=['free money','click here','win prize','urgent']
def spam(text):
 for word in blacklist:
  if word in text.lower():return f"SPAM (trigger: '{word}')"
 return 'NOT SPAM'
ck('Q007 substring urgent inside insurgent',spam('insurgent'),"SPAM (trigger: 'urgent')")
ck('Q008 no exact blacklist phrase',spam('Get your FREE product today at no cost.'),'NOT SPAM')
ck('case normalization',spam('FREE MONEY'),"SPAM (trigger: 'free money')")
ck('first blacklist order not first occurrence',spam('urgent then free money'),"SPAM (trigger: 'free money')")
ck('Q009 left aligned minimum width',f"{'abc':<20}",'abc'+' '*17)
ck('Q009 long output not truncated',f"{'x'*25:<20}",'x'*25)
ck('Q009 slice length',len(('x'*60)[:55]),55)
ck('Q009 slice exclusive end',list(range(60))[:55][-1],54)
ck('Q011 independent pixel choices',int(256**64==2**512),1)
ck('Q012 flattened length',np.arange(64).reshape(8,8).ravel().shape[0],64)
ck('Q016 percentage formatting',f'{37/38:.0%}','97%')
def rule(sepal,petal):
 if sepal<5:return 'setosa'
 elif petal<2.5:return 'setosa'
 return 'versicolor'
ck('Q018 early return',rule(4.9,5),'setosa');ck('Q019 strict boundaries',rule(5,2.5),'versicolor')
ck('Q034 Euclidean distance',np.linalg.norm([3,4]),5);ck('Q035 majority label',np.bincount([1,0,1]).argmax(),1)
X=np.array([[1.,10],[1.2,12],[.8,60],[.5,65],[.9,30],[1.,35]]);y=np.array([0,0,1,1,2,2]);q=np.array([[.7,62]])
ck('Q040 feature shape',X.shape,[6,2]);ck('Q040 target shape',y.shape,[6]);ck('Q041 fifth target',y[4],2)
d2=((X-q)**2).sum(axis=1);ck('Q042 six distances squared',d2,[2704.09,2500.25,4.01,9.04,1024.04,729.09]);ck('Q042 nearest row',np.argmin(d2),2)
model=KNeighborsClassifier(n_neighbors=1).fit(X,y);pred=model.predict(q)
ck('Q043 class prediction',pred[0],1);ck('Q043 name lookup',{0:'Smooth Floor (Blue)',1:'Gravel (Red)',2:'Grass (Green)'}[pred[0]],'Gravel (Red)')
ck('Q044 sample shape',q.shape,[1,2]);ck('Q044 prediction shape',pred.shape,[1]);ck('Q050 linear predictor',np.dot([2,-1],[3,4])+.5,2.5)
res=np.array([1,3,5])-np.array([2,2,4]);ck('Q053 SSE',sum(res**2),3);ck('Q053 MSE',np.mean(res**2),1)
# A direct full-column-rank least-squares construction, not a claim that the source gives this solver.
a=np.column_stack([np.arange(4),np.ones(4)]);target=np.array([1,3,4,6]);beta=np.linalg.lstsq(a,target,rcond=None)[0]
ck('Q056 direct least-squares stationary residual',a.T@(a@beta-target),[0,0])
iris=load_iris();xt,xv,yt,yv=train_test_split(iris.data,iris.target,random_state=0);predi=KNeighborsClassifier(n_neighbors=1).fit(xt,yt).predict(xv)
ck('local exact Iris snippet held-out count',len(yv),38);ck('local exact Iris snippet correct count',np.sum(predi==yv),37);ck('local exact Iris output',f'{np.mean(predi==yv):.0%}','97%')
rng=np.random.default_rng(260226)
for _ in range(500):
 query=rng.uniform([.4,0],[1.3,75],size=(1,2));manual=y[np.argmin(((X-query)**2).sum(axis=1))]
 assert model.predict(query)[0]==manual
 n=int(rng.integers(1,100));objectives=rng.uniform(0,100,size=12);assert np.argmin(objectives)==np.argmin(objectives/n)
out={'reviewerId':'define_robotics_data_contracts:L26-independent-reviewer','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorKeysSeen':False,'priorVersionExposure':False,'exactAssertions':len(checks),'assertions':checks,'randomTrials':500,'checksPerTrial':2,'randomChecks':['manual Euclidean 1NN agrees with fitted local estimator','fixed-positive objective scaling preserves sampled minimizer'],'localVersions':{'numpy':np.__version__,'scikit-learn':sklearn.__version__},'scope':'Reproduction is bound to the recorded installed versions; 37/38 is supplied explicitly in the question. No network/API assumptions made.','status':'passed'}
r=Path(__file__).resolve().parents[1];(r/'audits/W06-L26-v2-contracts-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
