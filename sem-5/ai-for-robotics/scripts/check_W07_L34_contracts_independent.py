#!/usr/bin/env python3
"""Source-only independent L34 notebook and mathematics checks. Does not load questions/keys."""
import os,sys,json,hashlib,datetime,contextlib,io,math,tempfile
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/l34-contracts-mpl');os.environ.setdefault('MPLBACKEND','Agg')
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML,display
from scipy.special import expit,ndtr,softmax
from scipy.optimize import brentq
R=Path(__file__).resolve().parents[1]; checks=[]
def check(name,value):
 assert bool(value),name
 checks.append({'name':name,'passed':True})
nbpath=R/'sources/supplemental/L34-official-notebook.ipynb';nb=json.loads(nbpath.read_text());out=io.StringIO()
ns={'np':np,'plt':plt,'HTML':HTML,'display':display,'FuncAnimation':FuncAnimation}
old=os.getcwd();tmp=tempfile.mkdtemp(prefix='l34-contracts-notebook-')
try:
 os.chdir(tmp)
 with contextlib.redirect_stdout(out):
  for i in [4,6,8,10,12,13]:exec(compile(''.join(nb['cells'][i]['source']),f'original-notebook-cell-{i}','exec'),ns)
finally:os.chdir(old)
check('five original notebook loop updates',ns['epoch']==5)
check('five pre-update history records',len(ns['loss_history'])==len(ns['w_history'])==len(ns['b_history'])==5)
check('pre-update weights',[round(x,10) for x in ns['w_history']]==[3,3.6,3.9,4.05,4.125])
check('pre-update biases',np.allclose(ns['b_history'],[1,1.3,1.45,1.525,1.5625]))
check('stored half-squared losses',np.allclose(ns['loss_history'],[4.5,1.125,.28125,.0703125,.017578125]))
check('post-five-update parameters',np.allclose([ns['w'],ns['b']],[4.1625,1.58125]))
check('final prediction',np.isclose(ns['w']*2+ns['b'],9.90625))
check('stale loop y_pred is fifth pre-update value',np.isclose(ns['y_pred'],9.8125))
check('history vs final parameter distinction',ns['w_history'][-1]!=ns['w'])
assets=[]
for i in range(5):
 ns['animate'](i);check(f'frame {i} matching lengths',len(ns['loss_line'].get_xdata())==len(ns['loss_line'].get_ydata())==i+1)
 if i in (0,4):
  path=R/f'audits/W07-L34-contracts-frame-{i}.png';ns['fig'].savefig(path,dpi=100);assets.append({'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
check('final stored frame endpoint above graph limit',np.isclose(ns['line'].get_ydata()[1],18.0625) and ns['ax1'].get_ylim()[1]==15)
check('epoch text callback bound',ns['epoch_text'].get_text()=='Epoch: 5/5\nLoss: 0.0176')
check('original animation GIF saved',(Path(tmp)/'gradient_descent_animation.gif').stat().st_size>0)
# Independently derived numerical questions and identities.
check('sensor weighted sum',np.isclose(np.dot([1,2,0,-1],[2,-1,3,1])+.5,-.5))
check('inclusive MP threshold equality',int(sum([1,1,0])>=2)==1)
check('perceptron bias-inclusive update',np.array_equal(np.array([0,-1,0])+[1,2,-1],[1,1,-1]))
check('one positive update need not correct',np.dot(np.array([-10,0])+[1,0],[1,0])==-9)
check('zero-input activation outputs',expit(0)==.5 and np.tanh(0)==0 and int(0>=0)==1)
check('softmax log-count example',np.allclose(softmax([0,np.log(2),np.log(3)]),[1/6,2/6,3/6]))
check('activation derivative maxima',expit(0)*(1-expit(0))==.25 and 1-np.tanh(0)**2==1)
check('four maximum sigmoid factors',.25**4==1/256)
check('negative relu slopes and values',max(0,-2)==0 and max(.01*-2,-2)==-.02)
root=brentq(lambda z:ndtr(z)+z*np.exp(-z*z/2)/np.sqrt(2*np.pi),-2,0);gmin=root*ndtr(root)
check('GELU rounded minimum',-.171<gmin<-.169 and not np.isclose(gmin,-.17,rtol=0,atol=1e-5))
check('3-4-1 MLP parameter count',3*4+4+4+1==21)
check('two-unit affine ReLU',np.array_equal(np.maximum(0,np.array([[1,2],[-1,1]])@[1,-1]+[0,3]),[0,1]))
check('sigmoid output example',expit(np.dot([.5,-1],[2,0])-1)==.5)
check('printed and repaired CE sign',np.log(.5)<0 and np.isclose(-np.log(.5),np.log(2)))
check('categorical CE target second class',np.isclose(-np.log([.2,.5,.3][1]),np.log(2)))
check('regression MSE',np.mean((np.array([1,3])-np.array([2,1]))**2)==2.5)
check('gradient example negative input',[3*-2,3]==[-6,3])
check('descent negative gradient',2-.05*(-4)==2.2)
check('braking initial gradients',[(-3)*2,-3]==[-6,-3])
check('first simultaneous update',np.allclose(np.array([3,1])-.1*np.array([-6,-3]),[3.6,1.3]))
check('residual contraction range',all(abs(1-5*t)<1 for t in [.0001,.1,.2,.3,.3999]) and abs(1-5*.4)==1)
check('CNN valid kernel widths',28-24+1==5 and 12-8+1==5 and 24//2==12 and 8//2==4)
# Independent finite differences and exact algebra across varied supplied examples.
rng=np.random.default_rng(3401);maxerr=0.
for _ in range(1000):
 x,w,b,y=rng.normal(size=4);eta=rng.uniform(.001,.1);e=w*x+b-y
 w1=w-eta*e*x;b1=b-eta*e
 assert np.isclose(w1*x+b1-y,e*(1-eta*(x*x+1)))
 eps=1e-6
 loss=lambda ww,bb:.5*(ww*x+bb-y)**2
 fd=np.array([(loss(w+eps,b)-loss(w-eps,b))/(2*eps),(loss(w,b+eps)-loss(w,b-eps))/(2*eps)])
 err=float(np.max(np.abs(fd-[e*x,e])));maxerr=max(maxerr,err);assert err<1e-7
 z=rng.normal(size=4);shift=rng.normal();assert np.allclose(softmax(z),softmax(z+shift))
 assert np.isclose(softmax(z[:2])[0],expit(z[0]-z[1]))
check('1000 residual identities and finite-difference gradients',True)
check('1000 common-logit shifts and binary softmax equivalences',True)
result={'reviewerId':'robotics-contracts-independent-reviewer','computedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceNotebookPath':str(nbpath.relative_to(R)),'sourceNotebookSha256':hashlib.sha256(nbpath.read_bytes()).hexdigest(),'execution':'Original source notebook code cells 4,6,8,10,12,13 executed verbatim in an isolated temporary working directory. Cell2 package-install/IPython magic setup omitted; installed imports supplied, Agg selected. No author question keys or check outputs loaded. Original animation saved successfully.','versions':{'python':sys.version.split()[0],'numpy':np.__version__,'matplotlib':matplotlib.__version__},'checks':checks,'assertionCount':len(checks),'variedCases':1000,'maximumFiniteDifferenceError':maxerr,'geluMinimum':{'input':float(root),'output':float(gmin)},'notebook':{'wHistory':ns['w_history'],'bHistory':ns['b_history'],'lossHistory':ns['loss_history'],'finalWeight':ns['w'],'finalBias':ns['b'],'finalPrediction':ns['w']*2+ns['b'],'stdout':out.getvalue()},'assets':assets,'sourceCaveats':['The PDF labels the target braking torque while its graph and linked notebook label motor speed.','Loss is half-squared error, not unscaled one-example MSE.','Explicit initialization is fixed despite random initialization comments and seed.','Five animation frames contain pre-update states, excluding the final post-update state.','The later line extends above fixed y-axis15; clipping is not model saturation.']}
p=R/'audits/W07-L34-contracts-independent-checks.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['assertionCount','variedCases','maximumFiniteDifferenceError','geluMinimum']}));print('saved',p)
