"""Independent changed-only L27 v3 checks; no author code or checks imported."""
import json,platform
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from sklearn.linear_model import LinearRegression
checks=[]
def ck(n,c,d):
 checks.append({'name':n,'passed':bool(c),'detail':d});assert c,n
X=np.array([[1,.5],[2,.5],[1,1],[5,1.]])
y=np.array([4.9,9.8,9.8,49.]);Z=np.column_stack([np.ones(4),X]);b=np.linalg.lstsq(Z,y,rcond=None)[0]
ck('printed static labels',np.allclose(9.8*X[:,0]*X[:,1],y),'All four labels, not just one target.')
ck('OLS rank',np.linalg.matrix_rank(Z)==3,'Unique intercept/raw-feature coefficient vector for the printed design.')
ck('OLS coefficients',np.allclose(b,[-14.7,9.511764705882353,15.56470588235294]),'Independent least-squares result.')
model=LinearRegression().fit(X,y);p=model.predict([[3.5,.8]])[0];supplied=-14.7+9.511764705882353*3.5+15.56470588235294*.8
ck('source sklearn fit and prediction',np.allclose([model.intercept_,*model.coef_],b) and np.isclose(p,supplied) and f'{p:.2f}'=='31.04','Actual installed sklearn run; full precision 31.04294117647059. The before-reveal reasoning had a mistyped unrounded decimal, corrected here without rewriting that frozen record; selected option unchanged.')
ck('numeric distractors',f'{9.8*3.5*.8:.2f}'=='27.44' and f'{supplied+14.7:.2f}'=='45.74' and f'{b@[1,.8,3.5]:.2f}'=='47.39','All three proposed wrong numerical values correspond to their stated mistakes.')
ck('fixed-slope versus interaction',np.isclose((9.8*2*1-9.8*1*1)-(9.8*2*.5-9.8*1*.5),4.9),'Changing extension changes physical mass slope; affine raw-feature plane slope remains b1.')
# Two indistinguishable incomplete inputs with different targets cannot be perfectly fit by any deterministic function of that input.
missing_x=np.array([0.,0.]);targets=np.array([0.,2.]);best=targets.mean()
ck('missing-information lower bound',np.isclose(np.mean((targets-best)**2),1),'The best common scalar prediction for identical observed inputs has MSE1; measuring the missing distinguishing feature can remove this collision.')
train=np.array([4,2,1,.5]);held=np.array([5,3,2,3])
ck('held-out stopping example',np.argmin(train)==3 and np.argmin(held)==2,'Supplied illustrative sequence shows why continued training-error reduction alone is not a stopping criterion.')
# Run the source Gaussian generation exactly, not a clipped or substituted RNG.
np.random.seed(42);A=np.random.normal([10,20],[2,5],(100,2));B=np.random.normal([22,90],[2,5],(100,2));C=np.random.normal([25,40],[2,5],(100,2))
ck('normal scales not hard intervals',np.any((A[:,0]<8)|(A[:,0]>12)) and np.any((A[:,1]<15)|(A[:,1]>25)),'Actual source draws exceed the one-standard-deviation intervals.')
ck('source samples above physical bound',np.max(B[:,1])>100,'Untruncated Gaussian source example exceeds100% Wi-Fi; source plot shows this too.')
labels=np.array([0,0,1,1,2,2]);perm=np.array([2,0,1])[labels];changed=labels.copy();changed[0]=1
ck('consistent permutation invariance',np.array_equal(labels[:,None]==labels,perm[:,None]==perm) and not np.array_equal(labels[:,None]==labels,changed[:,None]==changed),'Compare pairwise partitions, including a genuinely changed one-point label.')
colors=np.array([[10,10,10],[12,12,12],[250,250,250]]);palette=np.array([[11,11,11],[250,250,250]]);recon=palette[[0,0,1]]
ck('palette loss and reduction',len(palette)<len(colors) and np.mean((recon-colors)**2)>0,'Reducing distinct representatives can introduce reconstruction error; no net byte savings claimed without encoding overhead.')
ck('action versus set','left' in {'left','right','forward'} and 'left'!={'left','right','forward'},'Selected element differs from the available set.')
def env(s,a):
 ns=s+(1 if a=='right' else -1);return ns,int(ns==2)
ck('simulated functional interaction',env(1,'right')==(2,1) and env(1,'left')==(0,0),'Minimal supplied simulator responds differently to alternate actions; this is not a trained policy or a hardware-fidelity claim.')
report={'reviewerId':'independent-reviewer-robotics-batches-v2','executedAt':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),'numpy':np.__version__,'checks':checks,'passed':len(checks),'failed':0,'prediction':float(p),'sourceWiFiMaximum':float(B[:,1].max()),'priorSourceAndKeysExposed':True,'authorScriptReadOrExecuted':False,'optionalMglearnFigureExecuted':False,'scope':'Targeted v3 checks plus earlier immutable v1/v2 computation evidence, not a new claim of optional plotting dependency execution.'}
Path('audits/W06-L27-v3-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':len(checks),'prediction':float(p),'maxWifi':float(B[:,1].max())}))
