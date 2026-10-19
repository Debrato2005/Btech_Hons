"""Independent execution transcribed from actual L27 source pixels plus derived checks."""
import os
os.environ.setdefault('MPLBACKEND','Agg')
os.environ.setdefault('MPLCONFIGDIR','/tmp/l27-independent-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/l27-independent-cache')
import json, math, platform, datetime, importlib.util, ast
import numpy as np
import matplotlib.pyplot as plt
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import sympy as sp
from pathlib import Path
checks=[]
def ck(label,actual,expected,tol=1e-10):
 ok=bool(np.allclose(actual,expected,atol=tol,rtol=tol));checks.append({'label':label,'actual':np.asarray(actual).tolist(),'expected':np.asarray(expected).tolist(),'passed':ok});assert ok,label
# Exact source data and estimator calls, independently typed from pixels803–805.
X_lifting=np.array([[1.0,.5],[2.0,.5],[1.0,1.0],[5.0,1.0]])
y_torque=np.array([4.9,9.8,9.8,49.0])
regressor=LinearRegression()
regressor.fit(X_lifting,y_torque)
new_box=[[3.5,.8]]
pred_torque=regressor.predict(new_box)[0]
A=sp.Matrix([[1,1,sp.Rational(1,2)],[1,2,sp.Rational(1,2)],[1,1,1],[1,5,1]])
y=sp.Matrix([sp.Rational(49,10),sp.Rational(49,5),sp.Rational(49,5),49])
beta=(A.T*A).inv()*A.T*y
exactpred=(sp.Matrix([[1,sp.Rational(7,2),sp.Rational(4,5)]])*beta)[0]
ck('feature shape',X_lifting.shape,[4,2]);ck('target shape',y_torque.shape,[4]);ck('row3 feature',[*X_lifting[3],y_torque[3]],[5,1,49])
ck('coefficients versus independent rational normal equations',[regressor.intercept_,*regressor.coef_],list(map(float,beta)))
ck('prediction versus exact rational',pred_torque,float(exactpred));ck('displayed two-decimal torque',float(f'{pred_torque:.2f}'),31.04)
ck('physical model training values',X_lifting[:,0]*X_lifting[:,1]*9.8,y_torque)
ck('new physical product',3.5*.8*9.8,27.44)
ck('omitting mass factor produces 9.8, not o2 value4.9',9.8*1,9.8)
ck('affine swapped-feature distractor',float(f'{regressor.predict([[.8,3.5]])[0]:.2f}'),47.39)
ck('affine intercept-omitted distractor',float(f'{regressor.coef_ @ np.array([3.5,.8]):.2f}'),45.74)
ck('different implied mass slopes',[(9.8-4.9)/(2-1),(49-9.8)/(5-1)],[4.9,9.8])
res=y-A*beta;assert A.T*res==sp.zeros(3,1)
ck('OLS residual orthogonality numeric',np.array(A.T*res,dtype=float),np.zeros((3,1)))
ck('nearest one-dimensional squared distances',[(6-2)**2,(6-8)**2],[16,4])
ck('coordinate mean',np.array([[0,0],[2,0],[4,6]]).mean(axis=0),[2,2])
ck('temperature rescaling squared weight',100**2,10000)
ck('ideal mean-center squared distances',np.sum((np.array([[10,20],[22,90],[25,40]])-[23,85])**2,axis=1),[4394,26,2029])
ck('ideal center nearest index',np.argmin([4394,26,2029]),1)
ck('two-step cumulative returns',[5-4,1+3],[1,4])
# Exact source random generation and clustering, from813–815, no substitutions.
np.random.seed(42)
zone_A=np.random.normal([10,20],[2,5],(100,2))
zone_B=np.random.normal([22,90],[2,5],(100,2))
zone_C=np.random.normal([25,40],[2,5],(100,2))
X_sensors=np.vstack([zone_A,zone_B,zone_C])
clustering_model=KMeans(n_clusters=3,random_state=42)
clustering_model.fit(X_sensors)
new_reading=[[23,85]]
predicted_zone=clustering_model.predict(new_reading)[0]
ck('each zone shape',zone_A.shape,[100,2]);ck('stacked sensor shape',X_sensors.shape,[300,2])
ck('learned center shape',clustering_model.cluster_centers_.shape,[3,2]);ck('source run new zone',predicted_zone,0)
ck('source run centroid association',np.argsort(clustering_model.cluster_centers_[:,1]),[2,1,0])
ck('no-target fit retains both input features',clustering_model.n_features_in_,2)
ck('predict array then scalar extraction',clustering_model.predict(new_reading).shape,[1])
d2=((clustering_model.cluster_centers_-new_reading[0])**2).sum(axis=1)
ck('prediction equals nearest learned centroid',predicted_zone,int(np.argmin(d2)))
# Rerun exact draw sequence under same seed to test reproducibility, not altered implementation.
np.random.seed(42)
X_again=np.vstack([np.random.normal(mu,[2,5],(100,2)) for mu in ([10,20],[22,90],[25,40])])
ck('same-seed same-setup arrays',np.max(np.abs(X_sensors-X_again)),0)
# The unbounded Gaussian source actually yields readings above100.
ck('Gaussian source includes Wi-Fi above100',bool(np.any(X_sensors[:,1]>100)),True)
# Property: the arithmetic mean uniquely minimizes SSE for a nonempty cluster.
rng=np.random.default_rng(271019)
for i in range(500):
 pts=rng.normal(size=(int(rng.integers(1,30)),int(rng.integers(1,6))))
 mean=pts.mean(axis=0);trial=mean+rng.normal(size=pts.shape[1])
 lhs=np.sum((pts-trial)**2)-np.sum((pts-mean)**2)
 rhs=len(pts)*np.sum((trial-mean)**2)
 assert np.allclose(lhs,rhs,rtol=1e-9,atol=1e-9)
# Optional package is checked honestly: parsing is not execution.
optional='import mglearn\nmglearn.plots.plot_kmeans_algorithm()\n'
ast.parse(optional)
mglearn_present=importlib.util.find_spec('mglearn') is not None
optional_execution=False
if mglearn_present:
 exec(optional,{});optional_execution=True;plt.close('all')
report={'reviewerId':'independent-reviewer-robotics-batches-v2','recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourcePages':[803,804,805,811,813,814,815,817],'sourceBasis':'Actual 1800px source render inspection; source code independently transcribed. No author checks or author scripts accessed.','versions':{'python':platform.python_version(),'numpy':np.__version__,'sklearn':sklearn.__version__},'checks':checks,'passed':len(checks),'failed':0,'variedMeanSSECases':500,'exactOLS':{'coefficients':list(map(str,beta)),'prediction':str(exactpred),'residuals':list(map(str,res))},'regressionExecution':{'prediction':float(pred_torque),'formatted':f'{pred_torque:.2f}'},'kmeansExecution':{'prediction':int(predicted_zone),'centers':clustering_model.cluster_centers_.tolist(),'clusterSizes':np.bincount(clustering_model.labels_).tolist(),'inertia':float(clustering_model.inertia_),'iterations':int(clustering_model.n_iter_),'params':clustering_model.get_params(),'newReadingSquaredDistances':d2.tolist(),'wifiMax':float(X_sensors[:,1].max())},'optionalMglearn':{'syntaxParsed':True,'dependencyPresent':mglearn_present,'executed':optional_execution,'scope':'When unavailable, only source figure interpretation and syntax parsing are claimed; neither is call execution.'}}
Path('audits/W06-L27-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
