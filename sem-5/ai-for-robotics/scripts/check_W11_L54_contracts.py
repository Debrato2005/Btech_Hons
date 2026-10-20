"""Independent source/blind-packet arithmetic, not author calculations."""
from pathlib import Path
import math, json, datetime, inspect, hashlib, random
import numpy as np, sklearn
from sklearn.svm import SVC
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,truth,result=None):
 assert bool(truth),name
 checks.append({'name':name,'result':result,'passed':True})
def close(a,b):return math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10)
def fk(a,b):return np.array([math.cos(a)+math.cos(a+b),math.sin(a)+math.sin(a+b)])
check('Seven joints minus rank six',7-6==1,1)
check('Encoder rotation converted to RPM',close((math.pi/2)/.1*60/(2*math.pi),150),150)
check('Sample period and scalar throughput',close(1/1000,.001) and 3*1000==3000,[.001,3000])
check('Margin norm',close(math.hypot(3,4),5),5)
check('One-sided margin',close(1/math.hypot(3,4),.2),.2)
check('Two-sided margin',close(2/math.hypot(3,4),.4),.4)
check('Norm objective',close(.5*(3**2+4**2),12.5),12.5)
check('Signed distance',close((2-1)/math.sqrt(2),1/math.sqrt(2)),1/math.sqrt(2))
check('Hard-margin feasibility',[a*b for a,b in zip([1,1,-1],[1.2,.4,-1.5])]==[1.2,.4,1.5])
check('Balanced stratified counts',int(.8*300)==240 and int(.2*300)==60,[240,60])
check('Training-statistic standardization',close((4-3)/.5,2),2)
check('RBF similarity',close(math.exp(-.5*2),math.exp(-1)),math.exp(-1))
check('Balanced API weights',np.all(compute_class_weight('balanced',classes=np.array([0,1]),y=np.array([0]*240+[1]*240))==1),[1,1])
X=np.array([[-1,-1,-1],[1,1,1]],float);svm=SVC(gamma='scale').fit(X,[0,1]);check('Installed scale-gamma rule',close(svm._gamma,1/3),svm._gamma)
check('Precision',close(54/57,18/19),54/57)
check('Recall',close(54/60,.9),.9)
check('Accuracy',close((54+57)/120,.925),.925)
check('Harmonic F1',close(2*.8*.5/(.8+.5),8/13),8/13)
check('Illustration parameter count',4*3+3+3+1==19,19)
h=np.maximum(np.array([[2,1],[-1,1]])@np.array([1,-2])+np.array([1,0]),0)
check('Toy hidden activations',np.array_equal(h,[1,0]),h.tolist());check('Toy forward output',close(np.array([3,-2])@h+.5,3.5),3.5)
check('Angle-output MSE',close((.1**2+.2**2)/2,.025),.025)
check('Plain gradient update',close(.5-.1*(-2),.7),.7)
check('Toy derivative/update/updated loss',close(2*(.5*2),2)and close(.5-.1*2,.3)and close(.5*(.3*2)**2,.18),[2,.3,.18])
check('Actual metre FK',np.allclose(fk(math.pi/6,math.pi/3),[math.sqrt(3)/2,1.5]),fk(math.pi/6,math.pi/3).tolist())
check('Metre target positive branch',np.allclose(fk(0,math.pi/2),[1,1]),[1,1])
check('Literal millimetre target is inside reach',math.hypot(.0015,.0015)<2,math.hypot(.0015,.0015))
check('Intended metre target is outside reach',math.hypot(1.5,1.5)>2,math.hypot(1.5,1.5))
manual=fk(math.radians(27.9),math.radians(90.1));check('Manual rounded pose is metres',np.allclose(manual,[.4143,1.3509],atol=5e-5),manual.tolist())
check('Joint-uniform radial fraction',close((math.pi-2*math.pi/3)/math.pi,1/3),1/3)
check('Training and test row counts',40000-4000==36000,[36000,4000])
width=[2,256,256,128,2];params=sum((a+1)*b for a,b in zip(width,width[1:]));check('Full network parameter count',params==99714,params)
default=MLPRegressor().get_params();check('Installed default solver',default['solver']=='adam',default['solver']);check('Installed validation early stopping',default['early_stopping']is False,False)
check('Installed no-improvement default',default['n_iter_no_change']==10,10)
check('Minibatch updates',10*(36000//200)==1800,1800)
check('Literal millimetre residual conversion',close((math.hypot(.03,.04)+0)/2/10,.0025),.0025)
check('Intended metre residual conversion',close((math.hypot(.03,.04)+0)/2*100,2.5),2.5)
check('Ideal upper-left metre point',np.allclose(fk(math.pi/2,math.pi/2),[-1,1]),[-1,1])
check('Historical angle degrees',round(math.degrees(1.6773),2)==96.10,math.degrees(1.6773))
historical=fk(1.6773,1.5809);err=float(np.linalg.norm(historical-[-1,1]));check('Historical metre endpoint',np.allclose(historical,[-1.09951,.87799],atol=5e-6),historical.tolist());check('Historical metre endpoint error cm',round(err*100,2)==15.74,err*100)
check('Literal mm historical residual cm',round(math.hypot(-1.09951+1,.87799-1)/10,5)==.01574,math.hypot(-.09951,-.12201)/10)
check('Singular endpoint sine',abs(math.sin(0))<1e-12 and abs(math.sin(math.pi))<1e-12)
check('Folded origin',np.linalg.norm(fk(.789,math.pi))<1e-12)
# Differentiate the source FK independently and compare against finite differences.
rng=random.Random(5401);varied=0
for _ in range(1000):
 a=rng.uniform(-math.pi,math.pi);b=rng.uniform(0,math.pi);r=fk(a,b)
 J=np.array([[-math.sin(a)-math.sin(a+b),-math.sin(a+b)],[math.cos(a)+math.cos(a+b),math.cos(a+b)]])
 assert np.allclose((fk(a+1e-6,b)-fk(a-1e-6,b))/2e-6,J[:,0],atol=1e-8);varied+=1
 assert np.allclose((fk(a,b+1e-6)-fk(a,b-1e-6))/2e-6,J[:,1],atol=1e-8);varied+=1
 assert close(float(np.linalg.det(J)),math.sin(b));varied+=1
 assert close(float(np.linalg.norm(r)),2*math.cos(b/2));varied+=1
 assert np.linalg.norm(fk(a+2*math.pi,b)-r)<1e-12;varied+=1
apis=[]
for cls in [SVC,MLPRegressor,StandardScaler]:
 p=Path(inspect.getfile(cls));apis.append(dict(className=cls.__name__,installedSource=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
report=dict(completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewerId='robotics-contracts-reviewer-L54',sourceFirst=True,authorContentUsed=False,checks=checks,explicitChecks=len(checks),variedCases=1000,variedAssertions=varied,installedSklearn=sklearn.__version__,apiImplementationEvidence=apis,officialDocumentation=[{'url':'https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html','observedVersion':'1.9.1','supportedClaims':'Scale gamma formula; class-weight formula; C regularization. Runtime claims independently pinned to installed1.8.0.'},{'url':'https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html','observedVersion':'1.9.1','supportedClaims':'Default Adam; max_iter epoch cap; training tolerance/no-improvement and separate validation early stopping.'},{'url':'https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html','observedVersion':'1.9.1','supportedClaims':'Training centering/scaling and outlier sensitivity, not data cleaning.'}],unitFinding='Seven blind-packet questions use millimetres inconsistently with source metre links, coordinates or centimetre conversion. No offered literal valid set is substituted with an intended key.',runtime='Installed default interpreter only. No downloads, dependency changes, restricted environments, live APIs or hardware. Complete original source-model execution is a separate independently transcribed report; historical outputs remain historical.')
out=R/'audits/W11-L54-contracts-independent-checks.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(len(checks),varied)
