"""Checks for explicitly added L47 repair exercises, not pretrained-model outputs or review."""
import numpy as np,json,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1];checks=[]
def ck(name,actual,expected):
 assert np.allclose(actual,expected,rtol=1e-10,atol=1e-10), (name,actual,expected)
 checks.append({'name':name,'actual':np.asarray(actual).tolist(),'expected':np.asarray(expected).tolist(),'passed':True})
def sm(z):
 a=np.exp(z-np.max(z,axis=-1,keepdims=True));return a/a.sum(axis=-1,keepdims=True)
def ln(x,eps=0):return (x-x.mean(axis=-1,keepdims=True))/np.sqrt(x.var(axis=-1,keepdims=True)+eps)
X=np.eye(2);L=np.log(3.);WO=np.array([[1,2],[-1,1.]])
matrices=[(np.array([[1.],[1.]]),np.array([[0.],[L]]),np.array([[2.],[4.]])),(np.array([[2.],[1.]]),np.array([[L],[0.]]),np.array([[1.],[3.]]))];hs=[];weights=[]
for idx,(wq,wk,wv) in enumerate(matrices,1):
 Q=X@wq;K=X@wk;V=X@wv;S=Q@K.T;S[np.triu_indices(2,1)]=-np.inf;P=sm(S);H=P@V;hs.append(H);weights.append(P)
ck('G01 head1 weights',weights[0],[[1,0],[.25,.75]])
ck('G01 head2 weights',weights[1],[[1,0],[.75,.25]])
ck('G01 concatenated heads',np.concatenate(hs,axis=-1),[[2,1],[3.5,1.5]])
ck('G01 final output',np.concatenate(hs,axis=-1)@WO,[[1,5],[2,8.5]])
ck('G01 no-mask distractor',np.concatenate([sm((X@a)@(X@k).T)@(X@v) for a,k,v in matrices],axis=-1)@WO,[[2.3,8.2],[2,8.5]])
ck('G01 uniform distractor',np.array([[2,1],[3,2.]])@WO,[[1,5],[1,8]])
x=np.array([1.,3.]);A=np.diag([1.,2.]);W1=np.array([[1,-1],[1,1.]]);b1=np.array([1.,0]);W2=np.diag([2.,1.]);b2=np.array([0.,1.])
def ffn(z):return np.maximum(z@W1+b1,0)@W2+b2
z=ln(x);a=z@A;o=x+a;u=ln(o);f=ffn(u);h=o+f
ck('G02 first norm',z,[-1,1]);ck('G02 attention branch',a,[-1,2]);ck('G02 intermediate residual',o,[0,5]);ck('G02 second norm',u,[-1,1]);ck('G02 FFN affine hidden',u@W1+b1,[1,2]);ck('G02 FFN output',f,[2,3]);ck('G02 final pre-norm',h,[2,8]);ck('G02 post-norm comparison',ln(ln(x+x@A)+ffn(ln(x+x@A))),[-1,1]);ck('G02 omitted second norm',o+ffn(o),[12,11]);ck('FFN parameter count',W1.size+b1.size+W2.size+b2.size,12)
E=np.array([[0,1],[np.log(2),0],[np.log(3),1.]]);pos=np.array([[.1,0],[0,.2],[.3,-.1]])
ck('G03 initial composite',E[[1,0]]+pos[:2],[[np.log(2)+.1,0],[0,1.2]])
p=sm(np.array([1.,0])@E.T);ck('G03 head probability',p,[1/6,2/6,3/6]);kept=p[[1,2]];kept/=sum(kept);ck('G03 retained distribution ID order B,C',kept,[.4,.6]);chosen=[1,2][np.searchsorted(np.cumsum(kept),.30,side='right')];ck('G03 sample draw',chosen,1);ck('G03 updated input row',E[chosen]+pos[2],[np.log(2)+.3,-.1])
ck('G04 cross score shape',np.zeros((3,2))@np.zeros((5,2)).T,np.zeros((3,5)))
ck('G04 causal eligible target-input mask',np.tril(np.ones((3,3))),[[1,0,0],[1,1,0],[1,1,1]])
ck('Q033 true affine result',np.array([-1.,1])*[2,3]+[1,-1],[-1,2]);ck('Q033 omitted first scaled component',[0+1,3-1],[1,2]);ck('Q034 positive stabilizer constant input',ln(np.array([2.,2.]),1e-5),[0,0]);ck('Q034 small nonzero variance is defined',np.isfinite(ln(np.array([1.,1.+1e-8]),0)).all(),True)
rng=np.random.default_rng(4702);varied=0
for _ in range(1000):
 n=int(rng.integers(2,8));d=int(rng.integers(2,7));dk=int(rng.integers(1,5));dv=int(rng.integers(1,5));x=rng.normal(size=(n,d));Q=x@rng.normal(size=(d,dk));K=x@rng.normal(size=(d,dk));V=x@rng.normal(size=(d,dv));S=Q@K.T/np.sqrt(dk);S[np.triu_indices(n,1)]=-np.inf;P=sm(S);H=P@V
 assert np.allclose(P.sum(axis=1),1);varied+=1
 assert np.all(P[np.triu_indices(n,1)]==0);varied+=1
 assert np.allclose(H,np.array([sm((Q[i:i+1]@K[:i+1].T)/np.sqrt(dk))@V[:i+1] for i in range(n)]).reshape(n,dv));varied+=1
 xp=x+rng.normal(size=(n,1));assert np.allclose(ln(x,1e-5),ln(xp,1e-5));varied+=1
res={'authorId':'build_offline_study_interface:L47-revision-author','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Added small deterministic Transformer exercises and repaired rationales, not original source code or a pretrained GPT output. Author checks are not independent verification.','numpyVersion':np.__version__,'namedChecks':len(checks),'variedChecks':varied,'checks':checks}
(R/'audits/W10-L47-v2-author-checks.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(len(checks),varied,'passed')
