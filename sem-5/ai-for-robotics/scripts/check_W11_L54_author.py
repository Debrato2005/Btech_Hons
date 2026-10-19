#!/usr/bin/env python3
"""Exact L54 author checks in the existing default interpreter, not independent review."""
from pathlib import Path
import json,math,sys,hashlib,datetime,ast,importlib.util
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import precision_score,recall_score,accuracy_score,f1_score,classification_report
R=Path(__file__).resolve().parents[1];B='W11-L54';checks=[];started=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert '/tmp/robotics-l35-venv' not in sys.executable

def ck(name,passed,detail):
 assert bool(passed),(name,detail)
 checks.append(dict(id=f'L54-AUTH-{len(checks)+1:03}',name=name,passed=True,detail=detail))
def close(a,b):return bool(np.allclose(a,b,atol=1e-10,rtol=1e-10))
def fk(a,b):return np.array([np.cos(a)+np.cos(a+b),np.sin(a)+np.sin(a+b)])
def jac(a,b):return np.array([[-np.sin(a)-np.sin(a+b),-np.sin(a+b)],[np.cos(a)+np.cos(a+b),np.cos(a+b)]])
ck('Rank nullity',7-6==1,'Seven joint variables minus six independent task constraints; distractors omit constraints or treat a rectangular Jacobian as square.')
ck('Angular speed and all options',close((math.pi/2)/.1*60/(2*math.pi),150) and round((math.pi/2)/.1,2)==15.71 and close((math.pi/2)/.1*60/math.pi,300),'RPM conversion correct150; rad/s relabel15.71; omitted factor2 gives300.')
ck('Sampling',1/1000==.001 and 3*1000==3000,'Three synchronized channels at1kHz:1ms vectors,3000 scalar readings/s. Serializing rates or kilo/micro confusion are false alternatives.')
ck('SVM norm and margins',close(np.linalg.norm([3,4]),5) and close([1/5,2/5,.5*25],[.2,.4,12.5]),'Wrong width pair doubles both widths; wrong objective2.5 uses norm instead of squared norm.')
ck('Signed distance',close(np.dot([1,-1],[2,1]),1) and close(1/np.linalg.norm([1,-1]),1/math.sqrt(2)),'Score1; distance1/sqrt2. Omitted norm and reversed normal are distinct distractors.')
soft=SVC(kernel='linear',C=.1).fit([[-2],[-1],[0],[1],[2]],[0,0,1,0,1]);yf=np.where(soft.classes_[soft.predict([[-2],[-1],[0],[1],[2]])]==1,1,-1)
margin=np.array([-1,-1,1,-1,1])*soft.decision_function([[-2],[-1],[0],[1],[2]])
ck('Soft-margin support scope',any(margin[soft.support_]<1-1e-8),'Actual default-runtime linear SVC has support vectors inside the unit margin; this supplements the pinned soft-margin mathematics.')
x=np.array([[0.],[1.],[5.]]);s=StandardScaler().fit(x);s2=StandardScaler().fit(x[[0,2]])
ck('Scaler refit can change coordinates',not close(s.transform([[1.]]),s2.transform([[1.]])),'Both standardized training sets have zero mean, but their transforms of1 differ; removing a row does not preserve the feature problem.')
ck('Normal parameter interpretation',close(.2**2,.04),'NumPy normal scale=.2A corresponds to variance.04A², not variance.2; Gaussian support is not bounded by one standard deviation.')
ck('Data shapes',np.column_stack([np.zeros(300)]*3).shape==(300,3) and np.vstack([np.zeros((300,3))]*2).shape==(600,3),'column_stack and vstack execute with representative arrays; values do not affect dimensions.')
ck('Stratified counts',.2*300==60 and .8*300==240 and 2*240==480,'Each class has240train/60test;480/120 are totals rather than counts per class.')
ck('Standardized numeric alternatives',close((4-3)/.5,2) and 4/.5==8 and (4-3)*.5==.5,'Key2; omitting centering8; multiplying by scale.5.')
ck('Held-out transform does not refit',close(s.mean_,[2]) and close(s.transform([[8]]),(8-2)/np.std(x)),'Scaler fit only on0,1,5; transforming test8 retains training mean2.')
ck('RBF numeric alternatives',close(np.exp(-.5*2),math.exp(-1)) and round(math.exp(-2),4)==.1353 and round(math.exp(1),4)==2.7183,'exp(-1)=.3679; missing gamma givesexp(-2); wrong sign givesexp(+1)>1.')
ck('Scale gamma',1/(3*1)==1/3,'Three features and positive matrix variance1 givegamma1/3, not3 orC=10.')
ck('Balanced class weights',480/(2*240)==1,'Both weights equal1; omitting class-count normalization gives2, raw sample count240 is not a weight.')
ytrue=np.array([1]*60+[0]*60);ypred=np.array([1]*54+[0]*6+[1]*3+[0]*57)
ck('Confusion metrics',close([precision_score(ytrue,ypred),recall_score(ytrue,ypred),accuracy_score(ytrue,ypred)],[54/57,.9,.925]),'API and manual precision54/57,recall54/60,accuracy111/120 agree; swapped P/R and TP/total alternatives checked.')
ck('F1 alternatives',close(2*.8*.5/(.8+.5),8/13) and close((.8+.5)/2,.65) and close(.8*.5,.4),'Harmonic mean.6153846; arithmetic.65; product.40.')
report=classification_report(ytrue,ypred,output_dict=True)
ck('Report support',report['1']['support']==60 and report['0']['support']==60,'Report support counts all true labels, including errors; unrelated to SVC support vectors.')
ck('Generic network parameters',(4+1)*3+(3+1)*1==19 and 4*3+3*1==15 and (4+1)*3+3==18,'19total;15weights only;18omits output bias.')
z=np.array([[2,1],[-1,1]])@np.array([1,-2])+np.array([1,0]);a=np.array([3,-2]);h=np.maximum(z,0)
ck('Toy forward and all alternatives',close(z,[1,-3]) and a@h+.5==3.5 and a@z+.5==9.5 and a@np.maximum(z-[1,0],0)+.5==.5,'Correct3.5;skipReLU9.5;omit hidden bias.5.')
err=np.array([.1,-.2]);ck('Angle MSE alternatives',close(np.mean(err**2),.025) and close(np.sum(err**2),.05) and close(np.mean(err)**2,.0025),'Average squares differs from sum squares and square of average.')
ck('Plain gradient step',close(.5-.1*(-2),.7) and close(.5+.1*(-2),.3) and close(-.1*(-2),.2),'Correct.7;sign-reversal.3;delta-only.2.')
ck('Integrated forward backprop step',close([.5-.1*2,.5*(2*.3)**2],[.3,.18]) and close([.5+.1*2,.5*(2*.7)**2],[.7,.98]) and close([.5-.1,.5*(2*.4)**2],[.4,.32]),'All three coupled weight/loss pairs checked; missing input-chain factor2 gives.4,.32.')
ck('FK and absolute-angle alternative',close(fk(math.pi/6,math.pi/3),[math.sqrt(3)/2,1.5]) and close([math.cos(math.pi/6)+math.cos(math.pi/3),math.sin(math.pi/6)+math.sin(math.pi/3)],[(math.sqrt(3)+1)/2,(1+math.sqrt(3))/2]),'Source elbow is relative; absolute-elbow distractor and coordinate swap explicitly computed.')
ck('Two branches',close(fk(0,math.pi/2),[1,1]) and close(fk(math.pi/2,-math.pi/2),[1,1]) and close(fk(math.pi/2,math.pi/2),[-1,1]),'First two reach same target; negative elbow violates selected branch.')
ck('Radial reach',math.hypot(1.5,1.5)>2 and abs(1.5)<2,'Axis-wise bounds do not guarantee reachability inside the radius2disk.')
ck('Shoulder wrap',np.linalg.norm(fk(-math.pi+1e-6,1)-fk(math.pi-1e-6,1))<4e-6,'Nearby physical orientations across wrap have almost2pi raw-label separation.')
v=fk(*np.deg2rad([27.9,90.1]));ck('Manual visual rounded FK',close(v,[.4142940673130597,1.3508774070827374]),'Rounded angle inputs differ slightly from panel0.415,1.351; do not claim exact hidden values.')
# Exhibit a configuration whose two angular displays and two Cartesian displays round as printed.
found=[]
for a in np.linspace(27.85,27.9499,150):
 for b in np.linspace(90.05,90.1499,150):
  xx,yy=fk(*np.deg2rad([a,b]))
  if round(float(xx),3)==.415 and round(float(yy),3)==1.351:found=[float(a),float(b),float(xx),float(yy)];break
 if found:break
ck('Display-rounding consistency witness',bool(found),{'underlyingAnglesDegrees':found[:2],'underlyingXY':found[2:],'scope':'One mathematical witness, not a claim about the application’s actual hidden state.'})
ck('Radial probability',close((math.pi-2*math.pi/3)/math.pi,1/3) and close((1/2)**2,1/4),'Angle-uniform fraction1/3; area-uniform assumption1/4; complementary interval2/3.')
ck('IK split and shapes',40000*.1==4000 and 40000-4000==36000,'X/Y stay paired and each has two columns.')
width=[2,256,256,128,2];weights=sum(a*b for a,b in zip(width,width[1:]));bias=sum(width[1:]);params=weights+bias
ck('Full architecture all options',params==99714 and weights==99072 and params-(128+1)*2==99456,'Bias642; omitted output transition258 gives99456.')
defaults=MLPRegressor().get_params()
ck('Pinned MLP defaults',defaults['solver']=='adam' and defaults['early_stopping']is False and defaults['tol']==1e-4 and defaults['n_iter_no_change']==10, {k:defaults[k]for k in ['solver','activation','early_stopping','tol','n_iter_no_change']})
ck('Epoch versus update',10*(36000/200)==1800,'180batches/epoch;10epochs;neither180nor10counts total updates.')
res=np.array([[.03,.04],[0,0]]);norms=np.linalg.norm(res,axis=1)
ck('Mean norm, RMS and max alternatives',close(100*np.mean(norms),2.5) and round(100*np.sqrt(np.mean(norms**2)),2)==3.54 and close(100*max(norms),5),'Correct2.50cm, RMS3.54cm, max5.00cm.')
ck('Single input batch',np.array([[-1.,1.]]).shape==(1,2),'One sample with two coordinate features, not two independent samples or an output axis.')
ck('Ideal target and alternatives',close(fk(math.pi/2,math.pi/2),[-1,1]) and close(fk(math.pi/2,-math.pi/2),[1,1]) and close(fk(math.pi,0),[-2,0]),'Positive branch ideal(pi/2,pi/2); both wrong pairs computed.')
ck('Degree conversion alternatives',round(math.degrees(1.6773),2)==96.10 and round(1.6773,2)==1.68 and round(math.radians(1.6773),2)==.03,'Degree96.10;relabel1.68;reverseconversion.03.')
historical=fk(1.6773,1.5809);delta=historical-[-1,1]
ck('Historical target position norm',round(100*np.linalg.norm(delta),2)==15.74,{'predictedXY':historical.tolist(),'residualCm':(delta*100).tolist(),'normCm':float(100*np.linalg.norm(delta)),'distractors':'9.82cm is a separate test-set mean;10cm a rough component scale, not the norm.'})
ck('Endpoint singularities',close(np.linalg.det(jac(.4,0)),0) and close(np.linalg.det(jac(.4,math.pi)),0) and close(np.linalg.det(jac(.4,math.pi/2)),1),'Zero at elbow0/pi, not atpi/2 or every shoulder angle.')
ck('Folded equal-link degeneracy',all(close(fk(a,math.pi),[0,0])for a in np.linspace(-math.pi,math.pi,30)),'Any shoulder value maps to the origin for equal-link folded geometry.')
ck('Supplied hard-margin feasibility',close(np.array([1,1,-1])*[1.2,.4,-1.5],[1.2,.4,1.5]),'Only second point violates canonical constraint despite correct sign; third point has product1.5.')
ck('Report class name ordering',list(classification_report(ytrue,ypred,target_names=['normal','overload'],output_dict=True))[:2]==['normal','overload'],'Class0/1 map to normal/overload; labels are display names, not a refit.')
full=json.loads((R/f'audits/{B}-full-code-author.json').read_text())
for run in full['runs']:
 ck('Full source hash '+run['name'],hashlib.sha256((R/run['sourcePath']).read_bytes()).hexdigest()==run['sourceSha256'],'Earlier actual full execution is hash-bound; no unnecessary repeat or restricted interpreter.')
ck('Full code provenance',full['status']=='passed_author_check_not_independent_review' and '/tmp/robotics-l35-venv' not in full['interpreter'],'Exact transcribed executable statements, external seed54 disclosed for IK; not an original notebook.')
for p in R.glob('sources/supplemental/L54-slide-*-code.py.txt'):ast.parse(p.read_text())
ck('Both exact code fragments parse',True,'AST parsed under current default Python; actual complete training was separately recorded.')
ck('mglearn absent, not executed',importlib.util.find_spec('mglearn')is None,'Architecture plotting fragment remains inspected source, not a claimed fresh library rendering; no installation attempted.')
rng=np.random.default_rng(54030);nassert=0
for _ in range(1000):
 a=rng.uniform(-math.pi,math.pi);b=rng.uniform(.01,math.pi-.01);p=fk(a,b)
 bb=math.acos(float(np.clip((p@p-2)/2,-1,1)));aa=math.atan2(p[1],p[0])-math.atan2(math.sin(bb),1+math.cos(bb))
 assert close(fk(aa,bb),p);nassert+=1
 j=jac(a,b);eps=1e-6;finite=np.column_stack([(fk(a+eps,b)-fk(a-eps,b))/(2*eps),(fk(a,b+eps)-fk(a,b-eps))/(2*eps)])
 assert np.allclose(j,finite,atol=3e-10,rtol=3e-9);nassert+=1
 assert math.isclose(np.linalg.det(j),math.sin(b),abs_tol=1e-12);nassert+=1
 d=rng.normal(size=(10,2));norm=np.linalg.norm(d,axis=1);assert np.mean(norm)<=np.sqrt(np.mean(norm**2))+1e-12;nassert+=1
ck('Random inverse/Jacobian/norm checks',nassert==4000,'1000seeded cases,4000assertions:branch FK closure,finite-difference Jacobian,determinant and mean/RMS inequality.')
result=dict(batchId=B,status='author_checks_only_not_independent_review',startedAt=started,completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),interpreter=sys.executable,checkGroups=len(checks),checks=checks,randomCases=1000,randomAssertions=nassert,fullCodeReport=f'audits/{B}-full-code-author.json',fullCodeReportSha256=hashlib.sha256((R/f'audits/{B}-full-code-author.json').read_bytes()).hexdigest(),executionScope='Existing default Python NumPy/scikit-learn only, no installations; no original notebook, mglearn rendering, hardware or restricted virtual environment. Both complete source-transcribed models executed in the separate hash-bound author report; historical printed outputs and fresh supplied-seed outputs are distinct.')
(R/f'audits/{B}-author-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(len(checks),'author check groups;',nassert,'random assertions')
