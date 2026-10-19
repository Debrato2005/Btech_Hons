#!/usr/bin/env python3
"""Author calculations, not independent review. No question or bank writes."""
import json,hashlib,math,io,contextlib,os,sys,platform
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from scipy.special import ndtr
from scipy.optimize import brentq
R=Path(__file__).resolve().parents[1];records=[]
def ck(name,condition,detail=None):
 assert bool(condition),name
 records.append({'name':name,'passed':True,'detail':detail})
# Exact scalar descent and every numerical choice.
w,b=F(3),F(1);states=[]
for j in range(6):
 p=2*w+b;e=p-10;states.append([str(w),str(b),str(p),str(e),str(e*e/2)])
 if j<5:w,b=w-F(1,10)*e*2,b-F(1,10)*e
ck('Five exact simultaneous updates',(w,b,2*w+b)==(F('4.1625'),F('1.58125'),F('9.90625')),states)
ck('Fifth stored pre-update frame is four updates',states[4][:3]==['33/8','25/16','157/16'])
ck('One-update and limiting distractors',states[1][:3]==['18/5','13/10','17/2'] and 2*F('4.2')+F('1.6')==10)
ck('Four activation derivatives and reciprocal distractor',F(1,4)**4==F(1,256) and 1/F(1,4)==4)
ck('Specified half loss versus ordinary MSE',F(7-10)**2==9 and F(7-10)**2/2==F('4.5'))
ck('Gradient sign and missing-half distractors',((-2)*3,3)==(-6,3) and (2*(-2)*3,2*3)==(-12,6))
x=np.array([1.,-2.,1.]);w=-2*x
ck('Mixed-sign component and score increase',(w+x)[1]<w[1] and np.dot(w+x,x)-np.dot(w,x)==6 and np.linalg.norm(w+x)<np.linalg.norm(w))
ck('Antiparallel negative-dot endpoint',float(np.dot(-x,x))<0 and abs(math.degrees(math.acos(float(F(-6,6))))-180)<1e-6)
for eta,contract in [(0,False),(.1,True),(.3,True),(.4,False),(.5,False)]:
 ck(f'Residual-contraction interval eta={eta}',(abs(1-5*eta)<1)==contract)
ck('Activation-only bound counterexample',(F(1,4)*8)**2==4 and 4>F(1,4)**2)
f=lambda t:ndtr(t)+t*np.exp(-t*t/2)/np.sqrt(2*np.pi)
r=brentq(f,-1.,-.5);minimum=r*ndtr(r)
ck('Exact GELU minimum rather than rounded endpoint',abs(minimum+0.1699712074799037)<1e-12 and round(minimum,2)==-.17,{'x':r,'value':minimum})
# Exact rational two-layer ReLU example, including all incorrect algorithm variants.
def network(W,b,v,c):
 x=(F(1),F(-1));z=[sum(W[i][j]*x[j] for j in range(2))+b[i]for i in range(2)];h=[max(F(0),a)for a in z];p=sum(v[i]*h[i]for i in range(2))+c
 return z,h,p
W=[[F(1),F(0)],[F(0),F(1)]];b=[F(1),F(0)];v=[F(1),F(-1)];c=F(0);eta=F(1,10);x=[F(1),F(-1)]
z,h,p=network(W,b,v,c);e=p-1;dv=[e*a for a in h];dc=e;dh=[e*v[i]*int(z[i]>0)for i in range(2)]
ck('MLP forward and loss',(z,h,p,e*e/2)==([F(2),F(-1)],[F(2),F(0)],F(2),F(1,2)))
ck('MLP exact gradients',dh==[F(1),F(0)] and dv==[F(2),F(0)] and dc==1)
new_states={}
for label,g,scale in [('correct',dh,F(1)),('ordinary_squared',[2*a for a in dh],F(2)),('mixed_new_output_weights',[e*(v[i]-eta*dv[i])*int(z[i]>0)for i in range(2)],F(1)),('ascent',[-a for a in dh],F(-1))]:
 Wn=[[W[i][j]-eta*g[i]*x[j]for j in range(2)]for i in range(2)];bn=[b[i]-eta*g[i]for i in range(2)];vn=[v[i]-eta*scale*dv[i]for i in range(2)];cn=c-eta*scale*dc;zn,hn,pn=network(Wn,bn,vn,cn)
 new_states[label]={'prediction':str(pn),'gradientFirstRow':[str(g[0]),str(-g[0])],'newW1':[[str(a)for a in row]for row in Wn],'newb1':list(map(str,bn)),'newW2':list(map(str,vn)),'newb2':str(cn)}
ck('MLP every algorithmic distractor',[new_states[k]['prediction']for k in new_states]==['63/50','16/25','327/250','143/50'],new_states)
# Complete deterministic perceptron trace and stop tests.
pts=[(np.array([1,0,0]),0),(np.array([1,0,1]),1),(np.array([1,1,0]),1),(np.array([1,1,1]),1)];w=np.zeros(3,dtype=int);trace=[];ends=[];updates=0
for epoch in range(1,10):
 for x,t in pts:
  s=int(w@x);pred=int(s>=0);old=w.copy();delta=(t-pred)*x;w+=delta;updates+=int(pred!=t)
  trace.append({'pass':epoch,'input':x.tolist(),'label':t,'oldScore':s,'oldWeights':old.tolist(),'updatedWeights':w.tolist(),'mistake':bool(pred!=t)})
 preds=[int(w@x>=0)for x,t in pts];correct=all(pred==t for pred,(_,t)in zip(preds,pts));ends.append({'pass':epoch,'weights':w.tolist(),'updates':updates,'allCorrect':correct})
 if correct:break
ck('Perceptron both branches, no-ops and all-example termination',ends==[{'pass':1,'weights':[0,0,1],'updates':2,'allCorrect':False},{'pass':2,'weights':[0,1,1],'updates':4,'allCorrect':False},{'pass':3,'weights':[-1,1,1],'updates':5,'allCorrect':True}],{'visits':trace,'passEnds':ends})
ck('Perceptron finite strict separability premise',all((np.dot([-.5,1,1],x)>0)==bool(t) for x,t in pts))
# Correct, wrong-class-branch, wrong-sign and sum-versus-mean BCE choices.
ps=[.8,.25,.6];ys=[1,0,1];losses=[-math.log(p if t else 1-p)for p,t in zip(ps,ys)];correct=[losses[1],sum(losses)/3];wrong_branch=[-math.log(ps[1]),-sum(math.log(p)for p in ps)/3]
ck('BCE negative-label and batch options',[round(a,5)for a in correct]==[.28768,.34055] and [round(a,5)for a in wrong_branch]==[1.38629,.70675] and round(sum(losses),5)==1.02165,{'losses':losses,'correct':correct,'wrongBranch':wrong_branch,'wrongSign':[-a for a in correct],'unaveragedSum':sum(losses)})
# Varied independent implementation checks of the authored derivations.
rng=np.random.default_rng(3419);maxdiff=0;checked=0
for case in range(200):
 x=rng.normal(size=2);W=rng.normal(size=(2,2));b=rng.normal(size=2);v=rng.normal(size=2);c=float(rng.normal());target=float(rng.normal());z=W@x+b
 if min(abs(z))<.02:b+=np.where(z>=0,.1,-.1);z=W@x+b
 h=np.maximum(0,z);e=float(v@h+c-target);d=e*v*(z>0);g=np.r_[np.outer(d,x).ravel(),d,e*h,e];theta=np.r_[W.ravel(),b,v,c]
 def obj(t):return .5*(float(t[6:8]@np.maximum(0,t[:4].reshape(2,2)@x+t[4:6])+t[8])-target)**2
 for j in range(9):
  step=1e-6;lo=theta.copy();hi=theta.copy();lo[j]-=step;hi[j]+=step;fd=(obj(hi)-obj(lo))/(2*step);diff=abs(fd-g[j]);maxdiff=max(maxdiff,diff);assert np.isclose(fd,g[j],rtol=1e-5,atol=2e-7),(case,j,fd,g[j]);checked+=1
for case in range(500):
 x,w,b,target=rng.normal(size=4);eta=float(rng.uniform(.001,.2));e=w*x+b-target;wn=w-eta*e*x;bn=b-eta*e;en=wn*x+bn-target
 assert np.isclose(en,(1-eta*(x*x+1))*e,atol=1e-12)
 assert np.isclose(en*en/2,(1-eta*(x*x+1))**2*e*e/2,atol=1e-12)
for case in range(200):
 W1,W2=rng.normal(size=(2,2)),rng.normal(size=(2,2));x,b1,b2=rng.normal(size=(3,2));assert np.allclose(W2@(W1@x+b1)+b2,(W2@W1)@x+W2@b1+b2)
ck('Varied full-network finite differences and recurrence checks',True,{'twoLayerCases':200,'finiteDifferenceAssertions':checked,'maxAbsoluteDifference':maxdiff,'residualCases':500,'residualAssertions':1000,'affineCompositionCases':200})
# Execute exact original notebook core cells, with explicit non-installing runtime setup.
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML,display
nbpath=R/'sources/supplemental/L34-official-notebook.ipynb';nb=json.loads(nbpath.read_text());env={'np':np,'plt':plt,'FuncAnimation':FuncAnimation,'HTML':HTML,'display':display};out=io.StringIO();work=R/'audits/code-output/W07-L34-v2-notebook';work.mkdir(parents=True,exist_ok=True);cwd=Path.cwd()
try:
 os.chdir(work)
 with contextlib.redirect_stdout(out):
  for j in [4,6,8,10,12,13]:exec(compile(''.join(nb['cells'][j]['source']),f'official-notebook-cell-{j}','exec'),env)
finally:os.chdir(cwd)
(work/'stdout.txt').write_text(out.getvalue())
ck('Exact notebook final values',np.allclose([env['w'],env['b'],2*env['w']+env['b']],[4.1625,1.58125,9.90625]))
ck('Exact notebook stored pre-update histories',np.allclose(env['w_history'],[3,3.6,3.9,4.05,4.125])and np.allclose(env['loss_history'],[4.5,1.125,.28125,.0703125,.017578125]))
for i in range(5):
 artists=env['animate'](i);xx,yy=env['loss_line'].get_data();assert len(xx)==len(yy)==i+1 and xx[-1]==i+1 and artists[2]is env['epoch_text']
ck('All five animation prefix lengths and reused text artist',True)
try:compile(''.join(nb['cells'][2]['source']),'setup-cell-as-plain-python','exec')
except SyntaxError:ck('Unadapted setup fails ordinary Python parsing',True)
else:raise AssertionError('Expected IPython syntax failure')
for seed in [0,19,2026]:
 np.random.seed(seed);np.random.random(9);probe={};exec(''.join(nb['cells'][4]['source']),probe);assert(probe['w'],probe['b'])==(3.,1.)
ck('Literal initialization independent of random state',True)
plt.close('all')
report={'authorId':'L34-repair-author-20261019','independentReview':False,'passed':True,'assertionGroups':len(records),'records':records,'randomCases':900,'randomAssertions':3000,'runtimeVersions':{'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__},'notebook':{'path':str(nbpath.relative_to(R)),'sha256':hashlib.sha256(nbpath.read_bytes()).hexdigest(),'executedOriginalCells':[4,6,8,10,12,13],'notExecuted':'Cell 2 install/magic setup. Imports and Agg backend supplied explicitly; no package installation performed.','outputsDirectory':str(work.relative_to(R))}}
(R/'audits/W07-L34-v2-author-computations.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'passed':True,'groups':len(records),'randomCases':900,'randomAssertions':3000}))
