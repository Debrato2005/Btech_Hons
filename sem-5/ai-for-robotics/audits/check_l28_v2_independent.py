"""Independent changed-task execution. Does not import author code or edit questions."""
import contextlib, hashlib, io, json, platform
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import scipy
from scipy import sparse
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.artist import Artist
import sklearn
from sklearn.datasets import make_classification, load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from IPython.display import display
checks=[]
def ck(name,condition,actual=None):
    checks.append({'name':name,'passed':bool(condition),'actual':actual})
# A saved document stores serializable display output, not a Python namespace.
ns={};exec('x=2\nx=x+3\nx=x+3',ns)
ck('Q007 repeated cell state',ns['x']==8,ns['x'])
doc={'cells':[{'cell_type':'code','source':'x','outputs':[{'output_type':'execute_result','data':{'text/plain':'8'},'execution_count':3}]}]}
saved=json.dumps(doc); restored=json.loads(saved); fresh={}
try:exec('x=x+3',fresh); err=None
except NameError as e:err=type(e).__name__
ck('Q006/Q007 saved display does not create a fresh namespace binding',restored['cells'][0]['outputs'][0]['data']['text/plain']=='8' and 'x' not in fresh and err=='NameError',err)
ck('Q014 eye and ones',np.array_equal(np.diag(np.eye(4)),np.ones(4)) and np.count_nonzero(np.eye(4))==4 and np.ones((2,5)).sum()==10)
r=np.random.default_rng(42);normal=r.standard_normal((100,4));ints=r.integers(0,100,size=(6,4))
ck('Q018 dimensions, exclusive integer bound, normal values outside unit interval',normal.shape==(100,4) and ints.shape==(6,4) and ints.min()>=0 and ints.max()<100 and np.any(abs(normal)>1))
X=np.array([[8,77,65,43],[43,85,8,69],[20,9,52,97],[73,76,71,78],[51,12,83,45],[50,37,18,92]])
ck('Q021 exact printed slice',np.array_equal(X[1:4,0:2],[[43,85],[20,9],[73,76]]))
rows=np.array([0,0,2,3]);cols=np.array([0,2,1,3]);vals=np.array([2.,3.,4.,5.]);coo=sparse.coo_matrix((vals,(rows,cols)),shape=(4,4));csr=coo.tocsr()
ck('Q024 coordinate construction then compressed-row conversion',coo.format=='coo' and csr.format=='csr' and np.array_equal(coo.toarray(),csr.toarray()))
ck('Q024 row operation and matrix-vector arithmetic',np.array_equal(csr.getrow(0).toarray(),[[2,0,3,0]]) and np.array_equal(csr@np.ones(4),[5,0,4,5]))
# Distractor explanation must not imply that CSR cannot accept coordinate triples.
ck('Q024 CSR also accepts triples; roles are not exclusivity claims',np.array_equal(sparse.csr_matrix((vals,(rows,cols)),shape=(4,4)).toarray(),csr.toarray()))
dense=np.ones((4,4));cs=sparse.csr_matrix(dense)
ck('Q024 sparse storage not universally smaller',cs.data.nbytes+cs.indices.nbytes+cs.indptr.nbytes>dense.nbytes)
fig,axes=plt.subplots(1,2);line=axes[0].plot([-1,0,20],[1,2,3])[0];axes[0].set_xlim(0,10)
ck('Q029 Figure/Axes/line are Artists',all(isinstance(a,Artist)for a in [fig,axes[0],line]))
ck('Q031 side-by-side Axes and limits preserve input',len(axes)==2 and axes[0].get_position().x0<axes[1].get_position().x0 and np.array_equal(line.get_xdata(),[-1,0,20]))
axes[0].semilogy([1,2],[1,10]);ck('Q032 semilogy scales',axes[0].get_xscale()=='linear' and axes[0].get_yscale()=='log');plt.close(fig)
x=np.linspace(-10,10,100);y=np.sin(x);fig,ax=plt.subplots();ln=ax.plot(x,y,marker='x')[0]
ck('Q035 opposite endpoint values',np.allclose(y[[0,-1]],[.5440211108893698,-.5440211108893698]),y[[0,-1]].tolist())
ck('Q035 amplitude and markers at each sample',np.all(abs(y)<=1) and ln.get_marker()=='x' and ln.get_markevery() is None and len(ln.get_xdata())==100)
ck('Q036 samples versus intervals',len(x)==100 and len(np.diff(x))==99 and x[0]==-10 and x[-1]==10)
fig.savefig('/tmp/l28-v2-independent-sine.png');plt.close(fig)
xc,yc=make_classification(n_samples=200,n_features=2,n_redundant=0,random_state=0)
fig,ax=plt.subplots();sc=ax.scatter(xc[:,0],xc[:,1],c=yc,cmap='bwr',edgecolors='k',linewidths=.5,alpha=.8);fig.colorbar(sc);fig.canvas.draw()
ck('Q038 scatter coordinates and label-color input',np.array_equal(sc.get_offsets(),xc) and np.array_equal(sc.get_array(),yc))
ck('Q039 color endpoints',np.allclose(sc.cmap(0.0)[:3],[0,0,1]) and np.allclose(sc.cmap(1.0)[:3],[1,0,0]))
ck('Q039 outline and opacity',np.allclose(sc.get_edgecolors()[0],[0,0,0,.8]) and sc.get_alpha()==.8)
# Bounding-box intersection is only supplementary; actual source pixels establish visible mixing.
lo=np.maximum(xc[yc==0].min(0),xc[yc==1].min(0));hi=np.minimum(xc[yc==0].max(0),xc[yc==1].max(0))
ck('Q039 feature-region overlap, not an accuracy measurement',np.all(hi>lo),{'intersectionLower':lo.tolist(),'intersectionUpper':hi.tolist(),'classifierFitted':False})
fig.savefig('/tmp/l28-v2-independent-scatter.png');plt.close(fig)
df=pd.DataFrame({'Name':['John','Anna','Peter','Linda'],'Location':['New York','Paris','Berlin','London'],'Age':[24,13,53,33]})
ck('Q043 row ordering',df.head(2).Name.tolist()==['John','Anna'] and df.tail(2).Name.tolist()==['Peter','Linda'])
ck('Q045 scalar versus list column selection',df['Age'].shape==(4,) and df[['Age']].shape==(4,1))
ck('Q046 iloc independent of locator typo',df.iloc[1,2]==13)
try:eval('Data_pandas.iloc[1,2]',{'data_pandas':df});case=None
except NameError as e:case=type(e).__name__
ck('Q046 case sensitivity',case=='NameError',case)
with contextlib.redirect_stdout(io.StringIO()):d=display(df);inf=df.info()
ck('Q047 side effects versus return',d is None and inf is None)
mixed=pd.Series(['x',3,None],dtype=object);ck('Q048 object is not string-only',mixed.dtype==object and isinstance(mixed[1],int))
X,y=load_iris(return_X_y=True);tr,te,yr,ye=train_test_split(X,y,test_size=.2,random_state=18)
s=StandardScaler(); z=s.fit_transform(tr); old=s.mean_.copy();zt=s.transform(te)
ck('Q059 default population training statistics',np.allclose(z.mean(0),0,atol=1e-12) and np.allclose(z.var(0),1))
ck('Q059/Q060 held-out transformation reuses training statistics',np.array_equal(s.mean_,old) and np.allclose(zt,(te-s.mean_)/s.scale_))
constant=StandardScaler().fit_transform(np.ones((6,1)));ck('Q059 constant remains zero variance',np.all(constant==0))
knn=KNeighborsClassifier();ret=knn.fit(z,yr);ck('Q050/Q052 fit returns self',ret is knn)
ck('Q053 single-output classifier shapes',knn.predict(zt[:12]).shape==(12,) and knn.predict_proba(zt[:12]).shape==(12,3))
ck('Q065 classifier score is accuracy',knn.score(zt,ye)==np.mean(knn.predict(zt)==ye))
lr=LinearRegression().fit([[0],[1],[2]],[0,2,4]);ck('Q054 estimator metric is not universally accuracy',lr.score([[0],[1],[2]],[0,2,4])==1 and not hasattr(lr,'predict_proba'))
ck('Q055 transform returns data, not self',s.transform(te) is not s and z.shape==tr.shape)
scores=[]
for seed in range(20):
 tr,te,yr,ye=train_test_split(X,y,test_size=.2,random_state=seed);s=StandardScaler();tr=s.fit_transform(tr);te=s.transform(te);scores.append(KNeighborsClassifier().fit(tr,yr).score(te,ye))
ck('Q062 varying independently specified split seeds give nonconstant scores',len(set(scores))>1,sorted(set(scores)))
# Vary construction and conversion, including duplicate coordinates and empty input.
rng=np.random.default_rng(2802);cases=500
for _ in range(cases):
 n,m=rng.integers(1,12,size=2);k=int(rng.integers(0,30));rr=rng.integers(0,n,size=k);cc=rng.integers(0,m,size=k);vv=rng.integers(-8,9,size=k)
 co=sparse.coo_matrix((vv,(rr,cc)),shape=(n,m));cr=co.tocsr();target=np.zeros((n,m),dtype=int);np.add.at(target,(rr,cc),vv)
 assert np.array_equal(co.toarray(),target) and np.array_equal(cr.toarray(),target) and np.array_equal(cr@np.ones(m),target@np.ones(m))
ck('Q024 varied sparse construction/conversion/arithmetic including empty and duplicate coordinates',True,{'cases':cases})
report={'reviewerId':'independent-reviewer-robotics-batches-v2','runAt':datetime.now(timezone.utc).isoformat(),'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'pandas':pd.__version__,'matplotlib':matplotlib.__version__,'sklearn':sklearn.__version__},'checks':checks,'checksPassed':sum(c['passed']for c in checks),'checksFailed':sum(not c['passed']for c in checks),'variedSparseCases':cases,'variedIrisSplits':20,'scope':'Actual independent numerical, sparse, pandas, matplotlib Agg and sklearn execution. Notebook persistence check is JSON plus separate Python namespaces, not a Jupyter server/kernel/browser execution. Language support is source-reviewed, not tested by running multiple kernels. No timing benchmark claims.','scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
path=Path('audits/W06-L28-v2-independent-computations.json');assert not path.exists();path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['checks','scope']},indent=2));assert not report['checksFailed']
