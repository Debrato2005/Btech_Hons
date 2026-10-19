"""Fresh source-derived L29 repair/gap checks before current keyed access."""
from pathlib import Path
import json,datetime,hashlib
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor
checks=[]
def ck(name,condition):
 assert condition,name
 checks.append(name)
ck('Split replaces one leaf with two',4-1+2==5)
ck('Equal pruning error accepted',3<=3)
ck('Increased pruning error rejected',not 4<=3)
a=(2*0+8*4)/10;b=(5*2+5*2)/10
ck('Weighted split scores',a==3.2 and b==2 and b<a)
ck('Unweighted averages misleadingly tie',np.mean([0,4])==np.mean([2,2])==2)
def leaf(p):x,y=p;return x+y<=4 and x-y>0
ck('Only stated correct point enters region',[leaf(p) for p in [(3,1),(1,3),(3,2),(2,2)]]==[True,False,False,False])
ck('Boundary strictness',leaf((2.5,1.5)) and not leaf((2,2)))
np.random.seed(42);N=150
stable=np.random.normal([9.8,0],[.5,10],(N,2));forward=np.random.normal([4,150],[2,30],(N,2));backward=np.random.normal([4,-150],[2,30],(N,2));X=np.vstack([stable,forward,backward]);y=np.array([0]*N+[1]*N+[2]*N);old=X.copy();oldy=y.copy()
ck('Block beginnings',y[150]==1 and y[300]==2 and np.array_equal(X[150],forward[0]) and np.array_equal(X[300],backward[0]))
ck('Draws differ from their means',not np.array_equal(X[150],[4,150]) and not np.array_equal(X[300],[4,-150]))
i=np.arange(450);tr42,te42=train_test_split(i,test_size=.3,stratify=y,random_state=42);tr43,te43=train_test_split(i,test_size=.3,stratify=y,random_state=43)
ck('Split seed changes allocation',not np.array_equal(tr42,tr43))
ck('Split does not mutate generated data',np.array_equal(X,old) and np.array_equal(y,oldy))
ck('Stratification keeps counts',np.bincount(y[tr42]).tolist()==[105,105,105] and np.bincount(y[te42]).tolist()==[45,45,45])
tree=DecisionTreeClassifier(max_depth=3,random_state=42).fit(X[tr42],y[tr42]);ck('Depth bound not equality',tree.get_depth()==2 and tree.max_depth==3)
ck('Post-pruning parameter exists','ccp_alpha' in tree.get_params())
rng=np.random.default_rng(292);features=rng.normal(size=(80,9));target=rng.normal(size=80)
for mf,want in [('sqrt',3),(1.0,9)]:
 forest=RandomForestRegressor(n_estimators=2,max_features=mf,random_state=42).fit(features,target)
 ck(f'Nominal feature count {mf}',all(t.max_features_==want for t in forest.estimators_))
for _ in range(500):
 n1,n2=rng.integers(1,40,2);v1,v2=rng.uniform(0,50,2);score=(n1*v1+n2*v2)/(n1+n2)
 assert min(v1,v2)-1e-12<=score<=max(v1,v2)+1e-12
 assert np.isclose(score,np.average([v1,v2],weights=[n1,n2]))
result={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':'Before current L29 v2/new-gap keys; original v1 exposure disclosed','assertionCount':len(checks),'assertions':checks,'randomWeightedCases':500,'checksPerCase':2,'versions':{'numpy':np.__version__,'sklearn':sklearn.__version__},'weightedScores':{'A':a,'B':b},'firstForwardRow':X[150].tolist(),'firstBackwardRow':X[300].tolist(),'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
out=Path(__file__).resolve().parents[1]/'audits/W06-L29-v2-contracts-independent-checks.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
