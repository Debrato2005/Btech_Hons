"""Source-derived numerical checks, not independent answer verification."""
from pathlib import Path
import sys,json,hashlib
sys.path.append('/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages')
import numpy as np
R=Path(__file__).resolve().parents[1];checks=[]
def ck(name,condition):
 assert condition,name
 checks.append(name)
def softmax(x):
 e=np.exp(x-np.max(x,axis=-1,keepdims=True));return e/e.sum(axis=-1,keepdims=True)
def attention(q,k,v):
 s=q@k.T/np.sqrt(q.shape[1]);s[np.triu_indices(len(q),1)]=-np.inf
 return softmax(s)@v,softmax(s)
def ln(x,eps=0):
 return (x-x.mean(axis=-1,keepdims=True))/np.sqrt(x.var(axis=-1,keepdims=True)+eps)
ck('Simplified weighted sum',np.allclose(np.array([.25,.75])@np.array([[2,0],[0,4]]),[.5,3]))
ck('Query projection',np.allclose(np.array([1,2])@np.array([[1,0,1],[0,1,-1]]),[1,2,-1]))
ck('One scaled dot product',np.dot([2,0,0,0],[3,0,0,0])/np.sqrt(4)==3)
ck('Softmax of logarithms',np.allclose(softmax(np.array([0,np.log(3)])),[.25,.75]))
ck('Softmax value sum',np.allclose(softmax(np.array([0,np.log(3)]))@np.array([[2,0],[0,4]]),[.5,3]))
ck('Four head width',4*16==64)
ck('Projection weight count',2*3*8*4+(2*4)*8==256)
ck('Residual sum',np.allclose(np.array([1,2])+[.5,-1]+np.array([2,0]),[3.5,1]))
ffn=np.maximum(np.array([1,-2])+[0,1],0)@np.array([[2,1],[3,4]])+[1,-1]
ck('Two-layer FFN',np.allclose(ffn,[3,0]))
ck('FFN parameter count',4*10+10+10*4+4==94)
ck('LayerNorm mean population variance',np.allclose(ln(np.array([1.,3.])),[-1,1]))
ck('LayerNorm affine coordinates',np.allclose(np.array([-1,1])*[2,3]+[1,-1],[-1,2]))
ck('LayerNorm constant epsilon',np.allclose(ln(np.array([2.,2.]),1e-5),[0,0]))
t3=np.array([2,4])+[1,-1];ck('Pre-norm residual state additions',np.allclose(t3,[3,3])and np.allclose(t3+[.5,2],[3.5,5]))
ck('Parallel projected dimensions',(np.zeros((6,12))@np.zeros((12,3))).shape==(6,3)and(np.zeros((6,12))@np.zeros((12,5))).shape==(6,5))
ck('Inclusive causal pairs',sum(range(1,6))==15)
head,weights=attention(np.eye(2),np.eye(2),np.array([[2.,0],[0,4.]]))
ck('Full masked attention row',np.allclose(head[1],[.6604769013466862,2.6790461973066275]))
ck('First row identity value',np.allclose(head[0],[2,0])and weights[0,1]==0)
ck('Dense score table quadruples',(200**2)/(100**2)==4)
E=np.array([[1,2],[3,4],[5,6]]);W=np.array([[0,1,0],[1,0,0]])
ck('One-hot embedding lookup',np.array_equal(W@E,[[3,4],[1,2]]))
ck('Position addition',np.allclose(W@E+[[.1,.2],[.3,.4]],[[3.1,4.2],[1.3,2.4]]))
E=np.array([[0,1],[np.log(2),0],[np.log(3),1]])
ck('Tied language head',np.allclose(softmax(np.array([1,0])@E.T),np.array([1,2,3])/6))
ck('Top-k renormalization',np.allclose(np.array([.5,.3])/.8,[.625,.375]))
def nucleus(x,p):
 order=np.argsort(-np.array(x));mass=0;keep=[]
 for i in order:
  keep.append(int(i));mass+=x[i]
  if mass>=p:break
 return keep
ck('Inclusive nucleus boundary',nucleus([.5,.3,.15,.05],.8)==[0,1])
ck('Adaptive nucleus lengths',len(nucleus([.85,.1,.05],.8))==1 and len(nucleus([.4,.35,.25],.8))==3)
ck('Ninety percent fraction',90/100==.9)
rng=np.random.default_rng(47)
for trial in range(1000):
 n=int(rng.integers(2,12));dk=int(rng.integers(1,9));dv=int(rng.integers(1,9))
 q=rng.normal(size=(n,dk));k=rng.normal(size=(n,dk));v=rng.normal(size=(n,dv))
 h,a=attention(q,k,v)
 assert np.allclose(a.sum(axis=1),1) and np.all(a>=0) and np.allclose(np.triu(a,1),0)
 assert np.allclose(h[0],v[0])
 i=int(rng.integers(1,n));hh,_=attention(q[:i],k[:i],v[:i]);assert np.allclose(h[:i],hh)
 v2=v.copy();v2[i:]+=rng.normal(size=v2[i:].shape)*10;h2,_=attention(q,k,v2);assert np.allclose(h[:i],h2[:i])
 x=rng.normal(size=(3,8));z=ln(x);assert np.allclose(z.mean(axis=1),0)and np.allclose(z.var(axis=1),1)
 p=rng.uniform(.01,1);prob=rng.dirichlet(np.ones(n));keep=nucleus(prob,p);mass=sum(prob[j]for j in keep)
 assert mass>=p-1e-12 and (len(keep)==1 or mass-prob[keep[-1]]<p+1e-12)
ck('One thousand randomized causal-prefix, normalization and nucleus groups',True)
out={'authorChecksOnly':True,'independentReviewRequired':True,'sourceProgramPresent':False,'scope':'Explicit source-derived formula reconstructions, not execution of a lecture program.','checks':checks,'checkCount':len(checks),'variedGroups':1000,'sourceSha256':'2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c','numpyVersion':np.__version__}
(R/'audits/W10-L47-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
