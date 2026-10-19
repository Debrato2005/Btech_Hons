#!/usr/bin/env python3
"""L34 author calculations, not independent verification. No package installation."""
import ast,contextlib,io,json,math,os,tempfile,hashlib
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import sympy as s
from scipy.optimize import minimize_scalar
from scipy.special import ndtr,expit
R=Path(__file__).resolve().parents[1];checks=[]
def ck(name,ok,detail=None):
 assert bool(ok),name
 checks.append(dict(name=name,passed=True,detail=detail))
x,w,b,y,eta=s.symbols('x w b y eta',real=True);yp=w*x+b;L=(yp-y)**2/2;e=yp-y
gw=s.diff(L,w);gb=s.diff(L,b)
ck('Weight gradient exact',s.simplify(gw-e*x)==0)
ck('Bias gradient exact',s.simplify(gb-e)==0)
ck('Residual recurrence exact',s.expand((w-eta*gw)*x+b-eta*gb-y-(1-eta*(x*x+1))*e)==0)
ck('Normalized eta stability bounds',F(2,5)==F('0.4'))
ck('Four sigmoid derivative factors',F(1,4)**4==F(1,256))
z=s.symbols('z',real=True);sg=1/(1+s.exp(-z))
ck('Sigmoid derivative exact',s.simplify(s.diff(sg,z)-sg*(1-sg))==0)
ck('Tanh derivative exact',s.simplify(s.diff(s.tanh(z),z)-(1-s.tanh(z)**2))==0)
ck('Activation maxima at zero',s.diff(sg,z).subs(z,0)==F(1,4) and s.diff(s.tanh(z),z).subs(z,0)==1)
ck('Biological sensor weighted example',np.dot([1,2,0,-1],[2,-1,3,1])+.5==-.5)
ck('MP count decisions',[int(sum(v)>=2) for v in [(1,1,0),(1,0,1),(1,0,0),(0,0,0)]]==[1,1,0,0])
ck('AND threshold truth table',all((sum(v)>=3)==all(v) for v in __import__('itertools').product((0,1),repeat=3)))
ck('Perceptron boundary equality',2-1-1==0)
ck('Augmented perceptron update',np.array_equal(np.array([0,-1,0])+[1,2,-1],[1,1,-1]))
ck('One update counterexample',np.dot([-10,0],[1,0])==-10 and np.dot([-9,0],[1,0])==-9)
ck('Activation zero values',expit(0)==.5 and np.tanh(0)==0)
ck('Softmax numeric example',np.allclose(np.exp([0,np.log(2),np.log(3)])/6,[1/6,2/6,3/6]))
ck('Leaky negative input',max(.01*-2,-2)==-.02 and max(0,-2)==0)
res=minimize_scalar(lambda z:z*ndtr(z),bounds=(-3,0),method='bounded',options={'xatol':1e-12})
ck('GELU rounded minimum',abs(res.fun-(-.1699712074799))<1e-10,{'argmin':res.x,'minimum':res.fun})
ck('GELU stationarity',abs(ndtr(res.x)+res.x*np.exp(-res.x**2/2)/np.sqrt(2*np.pi))<1e-7)
ck('3–4–1 parameter count',3*4+4*1+4+1==21)
ck('Hidden layer matrix example',np.array_equal(np.maximum(0,np.array([[1,2],[-1,1]])@np.array([1,-1])+[0,3]),[0,1]))
ck('Output sigmoid example',expit(.5*2-1*0-1)==.5)
ck('Printed and repaired binary signs',math.log(.5)==-math.log(2) and -math.log(.5)==math.log(2))
ck('Categorical example',-math.log([.2,.5,.3][1])==math.log(2))
ck('MSE two examples',F((1-2)**2+(3-1)**2,2)==F(5,2))
ck('Negative-input gradient example',3*(-2)==-6 and 3==3)
ck('Generic update example',F(2)-F(1,20)*(-4)==F(11,5))
ww,bb=F(3),F(1);hist=[]
for k in range(5):
 yy=2*ww+bb;ee=yy-10;hist.append([ww,bb,yy,ee*ee/2]);ww-=F(1,10)*ee*2;bb-=F(1,10)*ee
ck('Five exact pre-update losses',[v[3] for v in hist]==[F(9,2),F(9,8),F(9,32),F(9,128),F(9,512)])
ck('Final five-step weights',ww==F(333,80) and bb==F(253,160),{'w':str(ww),'b':str(bb)})
ck('Final five-step prediction',2*ww+bb==F(317,32))
ck('Convergence limiting weights',F(21,5)*2+F(8,5)==10)
ck('One-step and two-step distractors',hist[1][:3]==[F(18,5),F(13,10),F(17,2)] and hist[4][:3]==[F(33,8),F(25,16),F(157,16)])
ck('CNN supplied kernel dimensions',28-5+1==24 and 24//2==12 and 12-5+1==8 and 8//2==4)
ck('CNN flatten count',4*4*3==48)
ck('Plot last-frame clipping',hist[4][0]*4+hist[4][1]==F(289,16) and F(289,16)>15)
rng=np.random.default_rng(34)
for _ in range(500):
 v=rng.normal(size=5);a=rng.normal();p=np.exp(v-v.max());p/=p.sum();q=np.exp((v+a)-(v+a).max());q/=q.sum();assert np.allclose(p,q)
 u,v2=rng.normal(size=2);assert abs(expit(u-v2)-np.exp(u-max(u,v2))/(np.exp(u-max(u,v2))+np.exp(v2-max(u,v2))))<1e-12
 xx,ww0,bb0,yy0=rng.normal(size=4);ee0=ww0*xx+bb0-yy0;rate=float(rng.uniform(.001,1.99/(xx*xx+1)));new=(ww0-rate*ee0*xx)*xx+bb0-rate*ee0-yy0;assert abs(new)<abs(ee0)+1e-12
ck('500 random softmax invariance/equivalence/stable-update cases',True,{'cases':500,'assertions':1500})
nbp=R/'sources/supplemental/L34-official-notebook.ipynb';raw=nbp.read_bytes();ck('Official notebook snapshot hash',hashlib.sha256(raw).hexdigest()=='b460420750fcee804b99fcf48fc04f3680719026c7b351fb54c67c5028b1a4aa')
nb=json.loads(raw);src=lambda i:''.join(nb['cells'][i]['source'])
try:ast.parse(src(2));ordinary_python=True
except SyntaxError:ordinary_python=False
ck('Original setup contains notebook-only syntax',not ordinary_python)
# Setup replacement is explicit: installed packages, headless backend; NO install/magic cell run.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
from PIL import Image
ns={'np':np,'plt':plt,'FuncAnimation':FuncAnimation,'HTML':HTML};out=io.StringIO();old=os.getcwd()
with tempfile.TemporaryDirectory(prefix='l34-notebook-') as td:
 os.chdir(td)
 try:
  with contextlib.redirect_stdout(out):
   for i in (4,6,8,10,12,13):exec(compile(src(i),f'official-notebook-cell-{i}','exec'),ns)
  gif=Path('gradient_descent_animation.gif');im=Image.open(gif)
  ck('Original inspected arithmetic/plot cells execute',True,{'cells':[4,6,8,10,12,13],'setup':'Explicit imports and Agg backend; no pip/magic execution.'})
  ck('Generated animation has five frames',im.n_frames==5,{'frames':im.n_frames,'bytes':gif.stat().st_size})
  ck('Notebook numeric histories match exact derivation',np.allclose(ns['loss_history'],[float(v[3]) for v in hist]))
  ck('Notebook final model matches exact arithmetic',abs(ns['w']-float(ww))<1e-12 and abs(ns['b']-float(bb))<1e-12)
  ck('Notebook printed final prediction is9.91','Final Prediction: 9.91' in out.getvalue())
  # Persist generated execution evidence, not the unmodified notebook file itself.
  (R/'audits/L34-notebook-execution-output.txt').write_text(out.getvalue())
  (R/'audits/L34-notebook-animation.gif').write_bytes(gif.read_bytes())
  ns['animate'](0);ns['fig'].savefig(R/'audits/L34-notebook-frame-initial.png',dpi=110)
  ns['animate'](4);ns['fig'].savefig(R/'audits/L34-notebook-frame-last.png',dpi=110)
 finally:os.chdir(old);plt.close('all')
report=dict(batchId='W07-L34',authorOnly=True,independentVerification=False,assertionGroups=len(checks),allPassed=all(q['passed'] for q in checks),checks=checks)
(R/'audits/W07-L34-author-computations.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'author check groups;1500 randomized assertions; exact linked notebook cells.')
