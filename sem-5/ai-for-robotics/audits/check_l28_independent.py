"""Independent L28 source transcriptions and question checks. Does not read authored answers."""
import os
os.environ['MPLCONFIGDIR']='/tmp/l28-independent-mpl'
os.environ['XDG_CACHE_HOME']='/tmp/l28-independent-cache'
import json,sys,platform,io,contextlib,datetime
from pathlib import Path
import numpy as np,scipy,pandas as pd,sklearn,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import sparse
from sklearn.datasets import make_classification,load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from IPython.display import display
from IPython.utils.capture import capture_output
checks=[]
def ck(name,condition,actual=None):
 checks.append({'name':name,'passed':bool(condition),'actual':actual})
def eq(name,a,b):ck(name,np.array_equal(a,b),np.asarray(a).tolist())
# Stateful notebook model, independently executed with a shared namespace.
ns={};exec('x=2',ns);exec('x=x+3',ns);exec('x=x+3',ns);ck('Q007 live state',ns['x']==8,ns['x'])
try:exec('x=x+3',{})
except NameError:ck('Q007 restart undefined',True,'NameError')
else:ck('Q007 restart undefined',False)
a=np.array([[1,2,3],[4,5,6]],dtype=np.int64)
ck('Q010 attributes',(a.shape,a.ndim,a.size)==((2,3),2,6),[list(a.shape),a.ndim,a.size])
ck('Q011 offset',sum(i*s for i,s in zip((1,2),a.strides))==40, list(a.strides))
ck('Q012 item size and strides',a.itemsize==8 and a.strides==(24,8))
o=np.array([1,'name',{'x':3}],dtype=object);ck('Q008 object dtype',o.dtype==object and len({type(v) for v in o})==3)
eq('Q013 zeros',np.zeros((3,4)),[[0]*4]*3);eq('Q013 full',np.full((3,3),7.),[[7]*3]*3)
ck('Q014 constructors',np.eye(4).sum()==4 and np.ones((2,5)).sum()==10)
work=np.empty((100,4));work[:]=7;ck('Q015 overwrite before reading',np.all(work==7))
ar=np.arange(0,10,.5);ck('Q016 arange',ar.shape==(20,) and ar[-1]==9.5)
lin=np.linspace(0,2*np.pi,500);ck('Q017 linspace',len(lin)==500 and np.allclose(np.diff(lin),2*np.pi/499))
rng=np.random.default_rng(seed=42);rand=rng.standard_normal((100,4));ints=rng.integers(0,100,size=(6,4))
ck('Q018 random shape and range',rand.shape==(100,4) and np.any(np.abs(rand)>1) and ints.min()>=0 and ints.max()<100)
rng=np.random.default_rng(seed=42);X=rng.integers(0,100,size=(6,4))
expected=[[8,77,65,43],[43,85,8,69],[20,9,52,97],[73,76,71,78],[51,12,83,45],[50,37,18,92]]
eq('Exact p834 source matrix',X,expected);ck('Q019 distinct RNG histories',not np.array_equal(X,ints),{'normalThenInts':ints.tolist(),'freshInts':X.tolist()})
eq('Q020 column',X[:,2],[65,8,52,71,83,18]);eq('Q021 slice',X[1:4,0:2],[[43,85],[20,9],[73,76]])
eq('Q022 advanced rows',X[[0,2,5],:],np.array(expected)[[0,2,5]])
eq('Q023 mask',X[:,0]>50,[False,False,False,True,True,False]);eq('Q023 filtered',X[X[:,0]>50],[[73,76,71,78],[51,12,83,45]])
eye=np.eye(4);csr=sparse.csr_matrix(eye);ck('Q025 CSR identity',csr.nnz==4 and np.all(csr.data==1) and np.array_equal(csr.toarray(),eye),{'data':csr.data.tolist(),'indices':csr.indices.tolist(),'indptr':csr.indptr.tolist()})
explicit_zero=sparse.csr_matrix(([0.,1.],([0,1],[0,1])),shape=(2,2));tiny=sparse.csr_matrix(np.ones((1,1)))
ck('Q026 storage qualification',explicit_zero.nnz==2 and tiny.data.nbytes+tiny.indices.nbytes+tiny.indptr.nbytes>8)
data=np.array([1.,1.,1.,1.]);rows=np.array([0,1,2,3]);cols=np.array([0,1,2,3]);coo=sparse.coo_matrix((data,(rows,cols)))
eq('Q027 COO identity',coo.toarray(),eye)
buf=io.StringIO()
with contextlib.redirect_stdout(buf):print('COO representation:\n{}',coo)
ck('Q028 literal braces','{}' in buf.getvalue(),buf.getvalue())
fig,axs=plt.subplots(1,2);arr=np.arange(12);line=axs[0].plot(arr,arr)[0];axs[0].set_xlim(0,10)
ck('Q029 object tree',axs[0].figure is fig and line.axes is axs[0]);ck('Q031 layout and limits',len(axs)==2 and axs[0].get_position().x0<axs[1].get_position().x0 and np.array_equal(line.get_xdata(),arr))
axs[1].semilogy([1,2],[1,10]);ck('Q032 scales',axs[1].get_yscale()=='log' and axs[1].get_xscale()=='linear');plt.close(fig)
x=np.linspace(-10,10,100);y=np.sin(x);fig,ax=plt.subplots();line=ax.plot(x,y,marker='x')[0]
ck('Q035 and Q036 sine samples',len(x)==100 and len(np.diff(x))==99 and line.get_marker()=='x' and np.allclose(y[[0,-1]],[np.sin(-10),np.sin(10)]))
fig.savefig('audits/W06-L28-independent-sine.png');plt.close(fig)
try:compile('%matplotlib inline','<IPython-only>','exec')
except SyntaxError:ck('Q036 ordinary Python rejects magic',True)
else:ck('Q036 ordinary Python rejects magic',False)
X_cls,y_cls=make_classification(n_samples=200,n_features=2,n_redundant=0,random_state=0)
fig,ax=plt.subplots();sc=ax.scatter(X_cls[:,0],X_cls[:,1],c=y_cls,cmap='bwr',edgecolors='k',linewidths=.5,alpha=.8)
ax.set_xlabel('Feature 1');ax.set_ylabel('Feature 2');ax.set_title('Two-Class Dataset');fig.colorbar(sc,label='Class');fig.tight_layout();fig.canvas.draw()
ck('Q037 data dimensions',X_cls.shape==(200,2) and y_cls.shape==(200,))
eq('Q038 colors',sc.get_array(),y_cls);eq('Q038 vertical coordinates',sc.get_offsets()[:,1],X_cls[:,1])
ck('Q039 styles',np.allclose(sc.cmap(0.),[0,0,1,1]) and np.allclose(sc.cmap(1.),[1,0,0,1]) and sc.get_alpha()==.8 and np.allclose(sc.get_edgecolor()[0],[0,0,0,.8]) and sc.get_linewidths()[0]==.5)
fig.savefig('audits/W06-L28-independent-scatter.png');plt.close(fig)
df=pd.DataFrame({'Name':['John','Anna','Peter','Linda'],'Location':['New York','Paris','Berlin','London'],'Age':[24,13,53,33]})
ck('Q042 frame shape',df.shape==(4,3));eq('Q043 head',df.head(2).Name,['John','Anna']);eq('Q043 tail',df.tail(2).Name,['Peter','Linda']);eq('Q044 filtering labels',df[df.Age>30].index,[2,3])
ck('Q045 series versus dataframe',isinstance(df['Age'],pd.Series) and isinstance(df[['Age']],pd.DataFrame) and df[['Age']].shape==(4,1))
ck('Q046 iloc',df.iloc[1,2]==13)
try:eval('Data_pandas.iloc[1,2]',{'data_pandas':df})
except NameError:ck('Q046 capitalization',True)
else:ck('Q046 capitalization',False)
with capture_output() as cap:r=display(df);s=df.info()
ck('Q047 displayed versus returned',r is None and s is None)
obj=pd.Series([1,'s',None],dtype=object);ck('Q048 object not just strings',obj.dtype==object and isinstance(obj[0],int))
Xi,yi=load_iris(return_X_y=True);Xtr,Xte,ytr,yte=train_test_split(Xi,yi,test_size=.2)
ck('Q056 to Q058 Iris',Xi.shape==(150,4) and yi.shape==(150,) and Xtr.shape==(120,4) and Xte.shape==(30,4))
scaler=StandardScaler();Xtc=scaler.fit_transform(Xtr);Xec=scaler.transform(Xte);model=KNeighborsClassifier();fitted=model.fit(Xtc,ytr)
ck('Q052 fit returns self',fitted is model)
pred=model.predict(Xec[:12]);prob=model.predict_proba(Xec[:12]);ck('Q053 output shapes',pred.shape==(12,) and prob.shape==(12,3))
ck('Q054 and Q065 classifier score',np.isclose(model.score(Xec,yte),np.mean(model.predict(Xec)==yte)))
ck('Q059 train moments',np.allclose(Xtc.mean(axis=0),0,atol=1e-12) and np.allclose(Xtc.var(axis=0),1))
const=StandardScaler().fit_transform([[2],[2],[2]]);ck('Q059 constant stays constant',np.all(const==0))
mean_before=scaler.mean_.copy();new=scaler.transform([[5.1,3.5,1.4,.2]]);guess=model.predict(new);ck('Q060 and Q061 unchanged fitted scaler',np.array_equal(mean_before,scaler.mean_) and new.shape==(1,4) and guess.shape==(1,))
ck('Q063 accuracy count',round(30*93.33333333333333/100)==28)
small=StandardScaler().fit([[2],[4],[6]]);z=small.transform([[8]])[0,0];ck('Q064 exact extension',np.isclose(z,np.sqrt(6)),float(z))
# Varied cases independently check layout offsets, Boolean filtering, scaling and split variability.
rg=np.random.default_rng(628);varied=0
for _ in range(250):
 n,m=rg.integers(1,20,size=2);a=rg.integers(-100,101,size=(n,m),dtype=np.int64);i,j=int(rg.integers(n)),int(rg.integers(m))
 assert a.strides==(int(m)*8,8) and i*a.strides[0]+j*a.strides[1]==8*(i*m+j)
 mask=a[:,0]>0;assert np.array_equal(a[mask],np.array([row for row in a if row[0]>0]).reshape((-1,m)))
 varied+=1
for _ in range(250):
 v=rg.normal(size=(int(rg.integers(2,30)),1));h=rg.normal(size=(4,1));s=StandardScaler().fit(v)
 assert np.allclose(s.transform(h),(h-v.mean())/v.std(ddof=0))
 assert np.allclose(s.transform(v).mean(),0,atol=1e-12) and np.allclose(s.transform(v).var(),1)
 varied+=1
scores=[]
for seed in range(20):
 tr,te,yr,ye=train_test_split(Xi,yi,test_size=.2,random_state=seed);s=StandardScaler();tr=s.fit_transform(tr);te=s.transform(te);m=KNeighborsClassifier().fit(tr,yr);scores.append(m.score(te,ye))
ck('Q062 varied split scores',len(set(scores))>1,sorted(set(scores)))
ck('500 varied indexing/scaling cases',varied==500,varied)
result={'reviewerId':'independent-reviewer-robotics-batches-v2','runAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__,'matplotlib':matplotlib.__version__},'checks':checks,'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'sourceIrisOneRun':{'prediction':guess.tolist(),'testAccuracy':float(model.score(Xec,yte))},'executionScope':'NumPy, sparse, matplotlib, pandas and Iris code independently transcribed and executed. IPython magic was tested for ordinary Python SyntaxError only; headless Agg plotting replaces inline display and is disclosed. No author check script was opened or run.','variedCaseCount':varied,'variedIrisSplits':20}
Path('audits/W06-L28-independent-computations.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['versions','passed','failed','sourceIrisOneRun','variedCaseCount','variedIrisSplits']},indent=2));assert result['failed']==0
