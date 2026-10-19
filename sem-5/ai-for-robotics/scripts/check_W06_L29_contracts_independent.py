"""Independent L29 calculations transcribed from inspected source pixels, before keys."""
import datetime,json,math,itertools
from pathlib import Path
import numpy as np,sklearn
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn.model_selection import train_test_split
checks=[]
def ck(name,a,b):
 assert np.allclose(a,b),(name,a,b)
 checks.append(name)
ck('structural nodes and edges',[4+5,4+5-1],[9,8])
y0=np.array([2,4,9]);ck('leaf mean',y0.mean(),5);ck('leaf mean-square error',np.mean((y0-5)**2),26/3)
ck('class Gini',1-3*(1/3)**2,2/3);ck('regression averaging',np.mean([2,5,8]),5)
ck('soft probabilities',np.mean([[.51,.49],[.51,.49],[.01,.99]],axis=0),[1.03/3,1.97/3])
ck('hard vote differs',np.argmax(np.bincount([0,0,1])),0)
ck('bootstrap omitted ids',sorted(set(range(1,6))-set([2,5,3,2,5])),[1,4])
miss=sum(1 for sample in itertools.product(range(5),repeat=5) if 0 not in sample)
ck('bootstrap exact enumeration omission',miss/5**5,(4/5)**5);ck('omission decimal',(4/5)**5,.32768)
ck('nominal feature counts',[int(np.sqrt(9)),int(1.*9)],[3,9]);ck('class proportions',np.array([8,2])/10,[.8,.2])
np.random.seed(42);N=150
stable=np.random.normal([9.8,0],[.5,10],(N,2));fwd=np.random.normal([4,150],[2,30],(N,2));bwd=np.random.normal([4,-150],[2,30],(N,2))
X=np.vstack([stable,fwd,bwd]);y=np.array([0]*N+[1]*N+[2]*N)
xt,xv,yt,yv=train_test_split(X,y,test_size=.3,stratify=y,random_state=42)
t=DecisionTreeClassifier(max_depth=3,random_state=42).fit(xt,yt)
ck('feature shape',X.shape,[450,2]);ck('train/test sizes',[len(yt),len(yv)],[315,135]);ck('training classes',np.bincount(yt),[105]*3);ck('test classes',np.bincount(yv),[45]*3)
ck('tree depth',t.get_depth(),2);ck('tree nodes/leaves',[t.tree_.node_count,t.get_n_leaves()],[5,3]);ck('split features',t.tree_.feature[t.tree_.feature>=0],[1,1])
thresholds=t.tree_.threshold[t.tree_.feature>=0];ck('rounded printed thresholds',np.round(thresholds,3),[-45.452,61.097])
ck('synthetic heldout correct',sum(t.predict(xv)==yv),135)
def printed(g):return 2 if g<=-45.452 else (0 if g<=61.097 else 1)
ck('printed rule paths',[printed(80),printed(-45.452),printed(61.097),printed(0)],[1,2,0,0])
ck('leaf count constraint',int(min([2,8])>=3),0)
assert 'ccp_alpha' in DecisionTreeClassifier().get_params();checks.append('local post-pruning parameter exists')
assert RandomForestClassifier().max_features=='sqrt';checks.append('local classifier default sqrt')
ck('local regressor full fraction',RandomForestRegressor().max_features,1.0)
rng=np.random.default_rng(290129)
for _ in range(500):
 a=rng.uniform(.01,100);b=rng.uniform(-20,20);xx=rng.uniform(-50,50);th=rng.uniform(-50,50)
 assert (xx<=th)==(a*xx+b<=a*th+b)
 targets=rng.uniform(2,8,size=(7,11));assert 2<=targets.mean(axis=1).mean()<=8
 c=rng.uniform(-20,20);assert np.sum((y0-c)**2)>=np.sum((y0-5)**2)-1e-12
out={'reviewerId':'define_robotics_data_contracts:L29-independent-reviewer','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorKeysSeen':False,'priorVersionExposure':False,'status':'passed','exactAssertions':len(checks),'assertions':checks,'randomTrials':500,'checksPerTrial':3,'randomChecks':['positive affine threshold order','nested means remain inside target range','mean minimizes three-target SSE'],'localVersions':{'numpy':np.__version__,'scikit-learn':sklearn.__version__},'reproducedThresholds':thresholds.tolist(),'heldoutCorrect':135,'heldoutSize':135,'scope':'Locally installed software reproduction, not a real-robot performance or current online-version reproduction claim.'}
r=Path(__file__).resolve().parents[1];(r/'audits/W06-L29-contracts-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
