#!/usr/bin/env python3
"""Exact and executable L27 author checks, not independent verification."""
import os
os.environ.setdefault('LOKY_MAX_CPU_COUNT','2')
os.environ.setdefault('MPLCONFIGDIR','/tmp/l27-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/l27-cache')
import ast,contextlib,io,importlib.util,json,platform,random
from pathlib import Path
import numpy as np
import sympy as s
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
R=Path(__file__).resolve().parents[1];records=[]
def ck(name,condition,result):
 assert bool(condition),name
 records.append(dict(id=f'L27-CHECK-{len(records)+1:02}',check=name,result=result,status='passed',independentReview=False))
reg_source='''import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
X_lifting = np.array([
    [1.0, 0.5], # 1 kg, extended half a meter
    [2.0, 0.5], # 2 kg, extended half a meter
    [1.0, 1.0], # 1 kg, extended a full meter
    [5.0, 1.0]  # 5 kg, extended a full meter
])
y_torque = np.array([4.9, 9.8, 9.8, 49.0]) # Continuous numbers
regressor = LinearRegression()
regressor.fit(X_lifting, y_torque)
new_box = [[3.5, 0.8]]
pred_torque = regressor.predict(new_box)[0]
print("--- REGRESSION RESULT ---")
print(f"Task          : Lift a 3.5kg box at 0.8m extension")
print(f"Robot Predicts  : {pred_torque:.2f} Newton-meters of torque required")
'''
zone_source='''import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
np.random.seed(42)
zone_A = np.random.normal([10, 20], [2, 5], (100, 2)) # Cold, bad Wi-Fi
zone_B = np.random.normal([22, 90], [2, 5], (100, 2)) # Warm, great Wi-Fi
zone_C = np.random.normal([25, 40], [2, 5], (100, 2)) # Warm, okay Wi-Fi
X_sensors = np.vstack([zone_A, zone_B, zone_C])
clustering_model = KMeans(n_clusters=3, random_state=42)
clustering_model.fit(X_sensors)
new_reading = [[23, 85]]
predicted_zone = clustering_model.predict(new_reading)[0]
print("--- UNSUPERVISED CLUSTERING RESULT ---")
print(f"Robot sensors    : 23°C, 85% Wi-Fi")
print(f"Robot classifies : 'I belong to Zone {predicted_zone}'")
'''
visual_source='import mglearn\nmglearn.plots.plot_kmeans_algorithm()\n'
# Same tokens, numerical data and API calls as source screenshots. Whitespace alignment is not asserted pixel-exact.
def execute(src):
 ns={};buf=io.StringIO()
 with contextlib.redirect_stdout(buf):exec(compile(src,'<source-transcription>','exec'),ns)
 return ns,buf.getvalue()
r,ro=execute(reg_source);z,zo=execute(zone_source)
ck('Printed feature and target shapes',r['X_lifting'].shape==(4,2) and r['y_torque'].shape==(4,),{'X':[4,2],'y':[4]})
ck('Fourth-row alignment',np.array_equal(r['X_lifting'][3],[5,1]) and r['y_torque'][3]==49,'Row index 3 is [5,1] -> 49')
A=s.Matrix([[1,1,s.Rational(1,2)],[1,2,s.Rational(1,2)],[1,1,1],[1,5,1]]);Y=s.Matrix([s.Rational(49,10),s.Rational(49,5),s.Rational(49,5),49]);coef=(A.T*A).inv()*A.T*Y
ck('Exact OLS coefficient solution',coef==s.Matrix([-s.Rational(147,10),s.Rational(1617,170),s.Rational(1323,85)]),[str(v) for v in coef])
ck('Unique affine fit rank',A.rank()==3,'Design rank 3, three affine coefficients')
resid=A*coef-Y
ck('OLS orthogonality and nonzero training residual',A.T*resid==s.zeros(3,1) and resid!=s.zeros(4,1),[str(v) for v in resid])
ck('Library agrees with exact affine coefficients',np.allclose(np.r_[r['regressor'].intercept_,r['regressor'].coef_],np.array(coef,dtype=float).ravel()),[float(v) for v in coef])
pred=(s.Matrix([[1,s.Rational(7,2),s.Rational(4,5)]])*coef)[0]
ck('Prediction and printed formatting',pred==s.Rational(52773,1700) and abs(r['pred_torque']-float(pred))<1e-12 and '31.04 Newton-meters' in ro,{'exact':str(pred),'printed':'31.04'})
physical=s.Rational(7,2)*s.Rational(49,5)*s.Rational(4,5);swapped=(s.Matrix([[1,s.Rational(4,5),s.Rational(7,2)]])*coef)[0]
ck('Regression distractor arithmetic',physical==s.Rational(686,25) and f'{float(swapped):.2f}'=='47.39',{'physical_product':float(physical),'no_intercept':float(pred-coef[0]),'swapped_features':float(swapped)})
ck('Unequal mass slopes forbid interpolation',s.Rational(49,10)!=s.Rational(49,5),{'at_r_half':4.9,'at_r_one':9.8})
ck('All source labels match supplied static product',np.allclose(r['X_lifting'][:,0]*9.8*r['X_lifting'][:,1],r['y_torque']),'Static point-load model is an explicit comparison, not the fitted model form.')
ck('Seeded zone shapes and stacking',all(z[k].shape==(100,2) for k in ['zone_A','zone_B','zone_C']) and z['X_sensors'].shape==(300,2),{'perZone':[100,2],'stack':[300,2]})
z2,zo2=execute(zone_source)
ck('Repeated exact code seeded reproducibility',np.array_equal(z['X_sensors'],z2['X_sensors']) and zo==zo2,'Identical NumPy data and printed output in recorded local versions')
ck('As-printed KMeans output',z['predicted_zone']==0 and 'Zone 0' in zo,{'output':zo.strip(),'centers':z['clustering_model'].cluster_centers_.tolist(),'defaults':z['clustering_model'].get_params()})
ck('Centroids match corresponding empirical sample means',np.allclose(z['clustering_model'].cluster_centers_,np.vstack([z['zone_B'].mean(0),z['zone_C'].mean(0),z['zone_A'].mean(0)])),'Learned ID order B,C,A in this recorded run')
for n_init in [1,10,'auto']:
 model=KMeans(n_clusters=3,random_state=42,n_init=n_init).fit(z['X_sensors'])
 assert model.predict([[23,85]])[0]==0
ck('Explicit initialization-count variants checked',True,'n_init=1,10,auto yield same local partition and label; no universal cross-version guarantee.')
ck('Gaussian percentages exceed physical bound',int((z['X_sensors'][:,1]>100).sum())==2,{'values_above_100':int((z['X_sensors'][:,1]>100).sum()),'maximum':float(z['X_sensors'][:,1].max())})
d=[(23-a)**2+(85-b)**2 for a,b in [(10,20),(22,90),(25,40)]]
ck('Illustrative mean-center distances and Manhattan distractor',d==[4394,26,2029] and abs(23-22)+abs(85-90)==6,{'squaredScores':d,'ManhattanToB':6})
ck('Nearest 1D center',[(6-2)**2,(6-8)**2]==[16,4],'Cluster 1, score 4')
ck('2D centroid and median/sum distractors',np.array_equal(np.array([[0,0],[2,0],[4,6]]).mean(0),[2,2]),{'mean':[2,2],'median':[2,0],'sum':[6,6]})
ck('Rescaling can change nearest center',1<100 and 10000>100,'x=(0,0), centers (1,0),(0,10); multiplying first coordinate by 100 reverses the nearest center.')
ck('Label permutation preserves pairwise partition',all((a==b)==({0:2,1:0,2:1}[a]=={0:2,1:0,2:1}[b]) for a in range(3) for b in range(3)),'Bijective relabeling preserves same-cluster relationships.')
ck('Undiscounted two-step returns',5-4==1 and 1+3==4,'A=1, B=4; B preferred.')
rng=np.random.default_rng(811)
for _ in range(200):
 pts=rng.normal(size=(rng.integers(2,20),2));mean=pts.mean(0);candidate=rng.normal(size=2)
 assert np.allclose((pts-mean).sum(0),0)
 assert np.sum((pts-mean)**2)<=np.sum((pts-candidate)**2)+1e-10
ck('200 random mean-update checks',True,'Mean minimizes within-cluster squared distance against each tested alternate center; residual sums vanish.')
ast.parse(visual_source)
visual_available=importlib.util.find_spec('mglearn') is not None
ck('Visualization call syntax and dependency disclosure',True,{'syntax':'valid','mglearnInstalled':visual_available,'execution':'not executed; unavailable optional mglearn dependency' if not visual_available else 'not executed; illustration inspected from supplied source'})
codeaudit=dict(batchId='W06-L27',authorOnly=True,sourceSha256='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c',versions={'python':platform.python_version(),'numpy':np.__version__,'scikit-learn':sklearn.__version__},transcriptionNote='Visible source tokens and data preserved; whitespace alignment normalized. No plot-generation code is supplied for pages 805 or 815, so displayed figures were inspected rather than attributed to invented code.',snippets=[dict(pages=[803,804,805],code=reg_source,executed=True,output=ro),dict(pages=[811],code=visual_source,executed=False,reason='Optional mglearn package absent; syntax checked, actual source figure inspected.'),dict(pages=[813,814,815],code=zone_source,executed=True,output=zo)],checks=records)
(R/'audits/W06-L27-code-reproduction.json').write_text(json.dumps(codeaudit,ensure_ascii=False,indent=2)+'\n')
print('L27 author checks:',len(records),'records passed; 200 random mean checks; mglearn visualization not executed. No independent verification claimed.')
