#!/usr/bin/env python3
"""Literal L28 source reproductions plus explicitly identified author extensions.
These checks are author evidence, NOT independent answer verification.
"""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/robotics-matplotlib')
import contextlib, io, json, platform, hashlib
from pathlib import Path
import numpy as np
import scipy
from scipy import sparse
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Explicit headless substitution for notebook inline display.
import matplotlib.pyplot as plt
import sklearn, IPython
from IPython.display import display
from sklearn.datasets import make_classification,load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
R=Path(__file__).resolve().parents[1]
checks=[]; outputs={}
def check(name,value):
 assert bool(value),name
 checks.append(name)
# Page 831, literal source values.
a=np.array([[1,2,3],[4,5,6]])
check('p831 shape, ndim, size',a.shape==(2,3) and a.ndim==2 and a.size==6)
outputs['p831']={'shape':a.shape,'dtype':str(a.dtype),'ndim':a.ndim,'size':a.size,'strides':a.strides}
check('p831 C-order stride relationship',a.strides==(3*a.itemsize,a.itemsize))
check('p831 explicit int64 byte-offset extension',np.array(a,dtype=np.int64).strides==(24,8) and 1*24+2*8==40)
# Page 832, literal constructors. Do not inspect/use uninitialized contents.
zeros=np.zeros((3,4));ones=np.ones((2,5));eye=np.eye(4);full=np.full((3,3),7.0);empty=np.empty((100,4))
check('p832 zeros',zeros.shape==(3,4) and np.all(zeros==0))
check('p832 ones',ones.shape==(2,5) and np.all(ones==1))
check('p832 identity',eye.shape==(4,4) and np.trace(eye)==4 and np.count_nonzero(eye)==4)
check('p832 full',full.shape==(3,3) and np.all(full==7))
check('p832 empty allocation only',empty.shape==(100,4))
# Page 833. Seed/draw order is part of reproducibility.
arange=np.arange(0,10,0.5);lin=np.linspace(0,2*np.pi,500)
rng=np.random.default_rng(seed=42);rand=rng.standard_normal((100,4));ints=rng.integers(0,100,size=(6,4))
check('p833 arange endpoint/count',len(arange)==20 and arange[0]==0 and arange[-1]==9.5)
check('p833 linspace endpoint/count/spacing',len(lin)==500 and lin[0]==0 and lin[-1]==2*np.pi and np.allclose(np.diff(lin),2*np.pi/499))
check('p833 normal shape and no bounded-support guarantee',rand.shape==(100,4) and np.any(abs(rand)>1))
check('p833 integer bounds',ints.shape==(6,4) and ints.min()>=0 and ints.max()<100)
# Page 834 fresh RNG, exact displayed page 835 output.
rng=np.random.default_rng(seed=42);X=rng.integers(0,100,size=(6,4))
expected=np.array([[8,77,65,43],[43,85,8,69],[20,9,52,97],[73,76,71,78],[51,12,83,45],[50,37,18,92]])
check('p834/835 complete printed matrix',np.array_equal(X,expected))
row0=X[0];col2=X[:,2];subarray=X[1:4,0:2];selected=X[[0,2,5],:];mask=X[:,0]>50;filtered=X[mask]
check('p835 row selection',row0.tolist()==[8,77,65,43])
check('p835 column selection',col2.tolist()==[65,8,52,71,83,18])
check('p835 slice',subarray.tolist()==[[43,85],[20,9],[73,76]])
check('p835 advanced selection',selected.tolist()==expected[[0,2,5],:].tolist())
check('p835 mask strict boundary',mask.tolist()==[False,False,False,True,True,False])
check('p835 filter',filtered.tolist()==[[73,76,71,78],[51,12,83,45]])
check('p833 versus p834 RNG draw order matters',not np.array_equal(ints,X))
outputs['p835']={'X':X.tolist(),'row0':row0.tolist(),'col2':col2.tolist(),'subarray':subarray.tolist(),'selected':selected.tolist(),'mask':mask.tolist(),'filtered':filtered.tolist()}
# Pages 837/838, source code.
eye=np.eye(4);sparse_matrix=sparse.csr_matrix(eye)
check('p837 identity CSR values',sparse_matrix.nnz==4 and np.array_equal(sparse_matrix.toarray(),eye))
check('p837 CSR structure author inspection',sparse_matrix.indices.tolist()==[0,1,2,3] and sparse_matrix.indptr.tolist()==[0,1,2,3,4])
data=np.array([1.0,1.0,1.0,1.0]);row_indices=np.array([0,1,2,3]);col_indices=np.array([0,1,2,3])
eye_coo=sparse.coo_matrix((data,(row_indices,col_indices)))
buf=io.StringIO()
with contextlib.redirect_stdout(buf):print('COO representation:\n{}',eye_coo)
check('p838 literal braces persist',buf.getvalue().startswith('COO representation:\n{} '))
check('p838 COO inferred shape',eye_coo.shape==(4,4) and np.array_equal(eye_coo.toarray(),eye))
outputs['p838_literal_print']=buf.getvalue()
outputs['p837_payload_bytes']={'dense':eye.nbytes,'CSR_arrays':sum(z.nbytes for z in (sparse_matrix.data,sparse_matrix.indices,sparse_matrix.indptr)),'note':'Array payload only; excludes Python object overhead.'}
# Page 842: magic is not ordinary Python. Remaining exact plotting calls run with Agg.
try:compile('%matplotlib inline','<source-magic>','exec')
except SyntaxError:check('p842 notebook magic not Python syntax',True)
else:raise AssertionError('Magic unexpectedly compiled')
x=np.linspace(-10,10,100);y=np.sin(x);fig,ax=plt.subplots();line,=ax.plot(x,y,marker='x')
check('p842 sample count and interval',len(x)==100 and np.allclose(np.diff(x),20/99))
check('p842 sine/radians/marker',np.allclose(line.get_ydata(),np.sin(x)) and line.get_marker()=='x')
check('p842 endpoints agree with graph',np.isclose(y[0],0.5440211108893698) and np.isclose(y[-1],-0.5440211108893698))
fig.savefig(R/'audits/W06-L28-author-sine.png');plt.close(fig)
# Page 843 exact synthetic data, class mapping and plotting options.
X_cls,y_cls=make_classification(n_samples=200,n_features=2,n_redundant=0,random_state=0)
fig,ax=plt.subplots();scatter=ax.scatter(X_cls[:,0],X_cls[:,1],c=y_cls,cmap='bwr',edgecolors='k',linewidths=0.5,alpha=0.8)
ax.set_xlabel('Feature 1');ax.set_ylabel('Feature 2');ax.set_title('Two-Class Dataset');fig.colorbar(scatter,label='Class');fig.tight_layout()
check('p843 data and label shapes',X_cls.shape==(200,2) and y_cls.shape==(200,) and set(y_cls)=={0,1})
check('p843 coordinate/colour mapping',np.allclose(scatter.get_offsets(),X_cls) and np.array_equal(scatter.get_array(),y_cls))
check('p843 bwr endpoints',np.allclose(scatter.cmap(0.0)[:3],[0,0,1]) and np.allclose(scatter.cmap(1.0)[:3],[1,0,0]))
check('p843 styling',scatter.get_alpha()==0.8 and scatter.get_linewidths()[0]==0.5)
fig.savefig(R/'audits/W06-L28-author-scatter.png');plt.close(fig)
# Page 846, explicit display import is added standalone-script context.
data={'Name':['John','Anna','Peter','Linda'],'Location':['New York','Paris','Berlin','London'],'Age':[24,13,53,33]}
data_pandas=pd.DataFrame(data)
check('p846 table construction',data_pandas.shape==(4,3) and list(data_pandas.columns)==['Name','Location','Age'])
check('p846 head/tail names',data_pandas.head(2).Name.tolist()==['John','Anna'] and data_pandas.tail(2).Name.tolist()==['Peter','Linda'])
check('p846 filter retains index',data_pandas[data_pandas.Age>30].index.tolist()==[2,3])
check('p847 Series versus DataFrame',isinstance(data_pandas['Age'],pd.Series) and isinstance(data_pandas[['Age']],pd.DataFrame))
check('p847 positional selection',data_pandas.iloc[1,2]==13)
buf=io.StringIO()
check('p847 info returns None',data_pandas.info(buf=buf) is None)
with contextlib.redirect_stdout(io.StringIO()):ret=display(data_pandas)
check('p847 ordinary display returns None',ret is None)
try:eval('Data_pandas.iloc[1,2]')
except NameError:check('p847 case mismatch NameError',True)
else:raise AssertionError('Unexpected uppercase name')
obj=np.array([1,'x'],dtype=object)
check('p830/845 object dtype qualification',obj.dtype==object and isinstance(obj[0],int) and isinstance(obj[1],str))
outputs['p846_dtypes']={k:str(v) for k,v in data_pandas.dtypes.items()}
# Pages 851/852 exactly omit random_state. No assertion that this run matches source 93.33%.
X,y=load_iris(return_X_y=True)
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2)
scaler=StandardScaler();X_train_clean=scaler.fit_transform(X_train);X_test_clean=scaler.transform(X_test)
model=KNeighborsClassifier();fit_return=model.fit(X_train_clean,y_train)
new_flower=[[5.1,3.5,1.4,0.2]];new_flower_clean=scaler.transform(new_flower);guess=model.predict(new_flower_clean);final_grade=model.score(X_test_clean,y_test)
outputs['p851_852_unseeded_run']={'prediction':guess.tolist(),'accuracy':float(final_grade),'claim':'One execution, not a guaranteed or independently verified source output.'}
check('p851 Iris shapes',X.shape==(150,4) and y.shape==(150,))
check('p851 split shapes',X_train.shape==(120,4) and X_test.shape==(30,4) and y_train.shape==(120,) and y_test.shape==(30,))
check('p852 standardization training moments',np.allclose(X_train_clean.mean(axis=0),0,atol=1e-12) and np.allclose(X_train_clean.var(axis=0),1))
check('p852 transformer preserves training statistics',np.allclose(scaler.mean_,X_train.mean(axis=0)))
check('p852 fit returns self',fit_return is model)
check('p852 new sample and probability shapes',new_flower_clean.shape==(1,4) and guess.shape==(1,) and model.predict_proba(new_flower_clean).shape==(1,3))
check('p852 classifier score accuracy',final_grade==np.mean(model.predict(X_test_clean)==y_test))
check('p852 printed percentage implies 28/30',np.isclose(28/30*100,93.33333333333333))
# Explicit added seeded trials demonstrate split dependence; they are not literal slide seeds.
scores=[]
for seed in range(100):
 A,B,c,d=train_test_split(X,y,test_size=.2,random_state=seed)
 s=StandardScaler();A=s.fit_transform(A);B=s.transform(B)
 m=KNeighborsClassifier().fit(A,c);scores.append(m.score(B,d))
check('extension: 100 seeded splits give multiple scores',len(set(scores))>1)
outputs['added_seeded_trials']={'count':100,'unique_scores':sorted(set(scores)),'new_context':'random_state=seed added only for controlled comparison.'}
# Explicit one-feature numerical standardization extension.
s=StandardScaler().fit([[2],[4],[6]])
check('extension: population variance and training-based transform',np.isclose(s.var_[0],8/3) and np.isclose(s.transform([[8]])[0,0],np.sqrt(6)))
result={'batchId':'W06-L28','status':'author checks passed; independent verification pending','versions':{m.__name__:m.__version__ for m in [np,scipy,pd,matplotlib,sklearn,IPython]},'python':platform.python_version(),'assertionCount':len(checks),'assertions':checks,'outputs':outputs,'addedContext':['Standalone imports, Agg backend and explicit Figure/Axes for saved inspection images replace inline rendering only.','Seeded Iris comparison, explicit int64 offset, CSR array inspection, object dtype and one-feature scaling are labeled extensions.'],'sourceCodePages':[827,831,832,833,834,837,838,842,843,846,851,852]}
(R/'audits/W06-L28-author-code-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'assertions':len(checks),'versions':result['versions'],'iris':outputs['p851_852_unseeded_run'],'trial_scores':outputs['added_seeded_trials']['unique_scores']},indent=2))
