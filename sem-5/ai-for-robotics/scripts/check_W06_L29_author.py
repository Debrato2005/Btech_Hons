"""Reproduce the supplied L29 example and explicitly labeled derived checks."""
from pathlib import Path
import json,datetime,numpy as np,sklearn
from sklearn.tree import DecisionTreeClassifier,DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
np.random.seed(42);N=150
stable=np.random.normal([9.8,0],[.5,10],(N,2));fwd=np.random.normal([4,150],[2,30],(N,2));bwd=np.random.normal([4,-150],[2,30],(N,2))
X=np.vstack([stable,fwd,bwd]);y=np.array([0]*N+[1]*N+[2]*N)
check('X shape 450 by 2',X.shape==(450,2));check('y shape 450',y.shape==(450,));check('label block alignment',all((y[i*150:(i+1)*150]==i).all() for i in range(3)))
Xt,Xv,yt,yv=train_test_split(X,y,test_size=.3,stratify=y,random_state=42)
check('315 training and 135 test rows',len(yt)==315 and len(yv)==135);check('105 training rows per class',np.array_equal(np.bincount(yt),[105]*3));check('45 test rows per class',np.array_equal(np.bincount(yv),[45]*3))
m=DecisionTreeClassifier(max_depth=3,random_state=42).fit(Xt,yt)
check('actual depth 2 under maximum 3',m.get_depth()==2);check('3 leaves and 5 total nodes',m.get_n_leaves()==3 and m.tree_.node_count==5);check('both internal nodes use feature index 1',np.array_equal(m.tree_.feature,[1,-2,1,-2,-2]));check('printed threshold rounding',round(m.tree_.threshold[0],3)==-45.452 and round(m.tree_.threshold[2],3)==61.097);check('node sample counts',np.array_equal(m.tree_.n_node_samples,[315,105,210,105,105]));check('typical class predictions',np.array_equal(m.predict([[4,-150],[9.8,0],[4,150]]),[2,0,1]));check('actual held-out accuracy in this installed execution',m.score(Xv,yv)==1.0)
check('supports cost-complexity post-pruning','ccp_alpha' in m.get_params());check('classifier max_features default sqrt',RandomForestClassifier().max_features=='sqrt');check('regressor max_features default 1.0',RandomForestRegressor().max_features==1.0);check('bootstrap remains enabled with all features',RandomForestClassifier(max_features=None).bootstrap)
soft=np.array([[.51,.49],[.51,.49],[.01,.99]])
check('hard vote class 0 differs from averaged-probability class 1',sum(soft.argmax(axis=1)==0)==2 and soft.mean(axis=0).argmax()==1)
check('regression tree mean 2,4,9 equals 5',np.mean([2,4,9])==5);check('regression leaf MSE equals 26/3',np.isclose(np.mean((np.array([2,4,9])-5)**2),26/3));check('bootstrap omission probability for n5',(4/5)**5==.3276800000000001)
r=DecisionTreeRegressor(random_state=42).fit([[0],[1],[2]],[0,1,2]);check('out of input range still produces a prediction',r.predict([[10]])[0]==2)
forest=RandomForestClassifier(n_estimators=5,random_state=2).fit(Xt,yt)
check('five fitted trees',len(forest.estimators_)==5);check('forest probabilities equal per-tree mean',np.allclose(forest.predict_proba(Xv),np.mean([t.predict_proba(Xv) for t in forest.estimators_],axis=0)))
report={'batchId':'W06-L29','status':'author execution only; independent verification pending','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'versions':{'numpy':np.__version__,'sklearn':sklearn.__version__},'assertionCount':len(checks),'assertions':checks,'sourceExample':{'trainCount':315,'testCount':135,'depth':2,'leafCount':3,'thresholds':m.tree_.threshold.tolist(),'nodeSamples':m.tree_.n_node_samples.tolist(),'testAccuracy':m.score(Xv,yv)},'scope':'Source pages 868, 871 and 873 reproduced; forest example fitted to explicitly supplied earlier synthetic data only as an extension, not a reproduction of binary plots on page 881. Optional mglearn illustration was not executed.'}
(R/'audits/W06-L29-author-code-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
