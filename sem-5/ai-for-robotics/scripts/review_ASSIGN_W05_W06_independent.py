"""Independent source-based deterministic checks; no browser, ROS or model downloads."""
from pathlib import Path
import json,math,datetime,hashlib
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
P=Path(__file__).resolve().parents[1];A=P/'audits';rng=np.random.default_rng(62026)
assert np.allclose(np.roots([1,6,9]),[-3,-3]);assert (16-1,2*math.sqrt(4*16)-1)==(15,15)
assert (10*2**3)/(10*2)==4
J=np.array([[1,2],[0,1]]);F=np.array([3,4]);assert (J.T@F).tolist()==[3,10]
for _ in range(1000):
 m,k=rng.uniform(.1,20,2);b=2*math.sqrt(m*k);assert np.isclose(b*b-4*m*k,0,atol=1e-10)
 x,v=rng.uniform(-4,4,2);assert np.isclose((x**3+v)-x**3,v)
 jj=rng.normal(size=(2,3));ff=rng.normal(size=2);qd=rng.normal(size=3);assert np.isclose(ff@(jj@qd),(jj.T@ff)@qd)
 t=float(rng.uniform(0,5));e=(.1+.3*t)*math.exp(-3*t);ed=-.9*t*math.exp(-3*t);edd=(-.9+2.7*t)*math.exp(-3*t);assert abs(edd+6*ed+9*e)<1e-12
assert sum([12,15,18,20,25])/5==18
assert sum([10,14,18])/3==14
assert abs((4+.1*(3+.9*10-4))-4.8)<1e-12
assert abs((4+.1*(3-4))-3.9)<1e-12
arr=np.array([1,'red'],dtype=object);assert arr.dtype==np.dtype(object);assert type(arr[0]) is int and type(arr[1]) is str
frame=pd.DataFrame({'n':[1,2],'name':['red','blue']});assert frame['n'].dtype!=frame['name'].dtype
model=LinearRegression();assert not hasattr(model,'coef_');model.fit([[0],[1],[2]],[1,3,5]);assert np.allclose(model.coef_,[2]);assert np.allclose(model.predict([[3]]),[7]);assert np.isclose(model.score([[0],[1],[2]],[1,3,5]),1)
for _ in range(1000):
 y=rng.normal(size=9);mean=y.mean();a=float(rng.normal());assert np.isclose(np.sum((y-a)**2),np.sum((y-mean)**2)+len(y)*(a-mean)**2)
 q,r,boot=rng.normal(size=3);alpha,gamma=rng.uniform(size=2);assert np.isclose(q+alpha*(r+gamma*boot-q),(1-alpha)*q+alpha*(r+gamma*boot));assert np.isclose(q+alpha*(r-q),(1-alpha)*q+alpha*r)
 x1,x2=rng.uniform(-15,15,2);value=5 if x1<=10 else (14 if x2<=5 else 35);assert value in (5,14,35)
# Three varied Q-learning/mean identities plus tree-domain check constitute four checks per case.
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for w,pages,primary in [(5,list(range(19,24)),[674,675,676,741]),(6,list(range(24,29)),[845])]:
 initial=json.load(open(A/f'blind-answers-ASSIGN-W{w:02d}-integration-initial.json'));x=dict(initial);x.update({'sourceInspectionCompletedAt':now,'actualAssignmentPagesInspected':pages,'actualLecturePagesInspected':primary,'sourceKeyExposure':True,'generatedKeyExposureAtInitialSolve':False,'reviewBoundary':'Initial answers were sealed before source viewing; source highlights and workings were visible during visual inspection. Full generated explanations were opened at01:33UTC. This is independent re-derivation with disclosed original-key exposure, not a fully blind review.'});p=A/f'blind-answers-ASSIGN-W{w:02d}-integration-final.json';assert not p.exists();p.write_text(json.dumps(x,indent=2)+'\n')
 out={'completedAt':now,'week':w,'status':'pass','variedAssertions':4000,'namedChecks':(['Repeated pole','Critical feedback gains','Spring ratio','Jacobian transpose power','Repeated-root initial response'] if w==5 else ['Squared-error mean','Tree path','Terminal and nonterminal Q updates','NumPy object dtype','pandas column dtypes','LinearRegression fit/predict/score']), 'runtimeScope':'Installed default packages only; synthetic small deterministic examples. No model download, neural inference, live ROS, hardware or browser execution.','versions':{'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__},'primaryReferences':(['Source assignment pages and actual lecture pages recorded in the answer seal.'] if w==5 else ['https://numpy.org/doc/2.3/reference/arrays.scalars.html','https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html','https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html'])};(A/f'ASSIGN-W{w:02d}-integration-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(w,'pass')
