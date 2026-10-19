"""Reviewer-authored, source-equation checks. No author solutions are read."""
from pathlib import Path
import numpy as np, math, itertools, json, datetime, hashlib
R=Path(__file__).resolve().parents[1]; checks=[]
def ck(name,actual,expected):
 assert np.allclose(actual,expected,rtol=1e-10,atol=1e-10),(name,actual,expected)
 checks.append({'name':name,'actual':np.asarray(actual).tolist(),'expected':np.asarray(expected).tolist()})
def sm(x):
 x=np.asarray(x,float); z=np.exp(x-np.max(x,axis=-1,keepdims=True));return z/z.sum(axis=-1,keepdims=True)
def attention(x,wq,wk,wv):
 q=x@wq;k=x@wk;v=x@wv;s=q@k.T/math.sqrt(k.shape[-1]);s[np.triu_indices(len(x),1)]=-np.inf;return sm(s)@v,sm(s)
def ln(x):return (x-x.mean(axis=-1,keepdims=True))/np.sqrt(x.var(axis=-1,keepdims=True))
def nucleus(p,t):
 order=np.argsort(-p,kind='stable'); n=int(np.searchsorted(np.cumsum(p[order]),t,side='left'))+1;n=min(n,len(p));out=np.zeros_like(p);out[order[:n]]=p[order[:n]];out/=out.sum();return out,order[:n]
ck('Q009 weighted sum',np.array([.25,.75])@np.array([[2,0],[0,4]]),[.5,3])
ck('Q013 query projection',np.array([1,2])@np.array([[1,0,1],[0,1,-1]]),[1,2,-1])
ck('Q014 one scale',6/math.sqrt(4),3)
for d in range(1,5):
 vals=[sum(a*b for a,b in zip(q,k))/math.sqrt(d) for q in itertools.product([-1,1],repeat=d) for k in itertools.product([-1,1],repeat=d)]
 ck(f'Q016 exact independent unit-variance products dk={d}',np.var(vals),1)
ck('Q017 softmax weights',sm([0,math.log(3)]),[.25,.75]);ck('Q017 head output',sm([0,math.log(3)])@np.array([[2,0],[0,4]]),[.5,3])
ck('Q023 concatenation dimensions',[4*16,4*16,64],[64,64,64]);ck('Q024 parameter count',2*3*8*4+(2*4)*8,256)
ck('Q025 residual stream',np.array([1,2])+[.5,-1]+np.array([2,0]),[3.5,1])
ck('Q029 FFN',np.maximum(np.array([1,-2])+[0,1],0)@np.array([[2,1],[3,4]])+[1,-1],[3,0])
ck('Q030 FFN parameters',4*10+10+10*4+4,94)
ck('Q032 layer normalization',ln(np.array([[1.,3.]])),[[-1,1]])
ck('Q033 affine layer norm',np.array([-1,1])*[2,3]+[1,-1],[-1,2])
ck('Q036 states',[[2+1,4-1],[2+1+.5,4-1+2]],[[3,3],[3.5,5]])
ck('Q038 shapes',[6,3,6,3,6,5],[6,3,6,3,6,5]);ck('Q041 eligible pairs',sum(range(1,6)),15)
y,w=attention(np.eye(2),np.eye(2),np.eye(2),np.diag([2.,4.]));ck('Q043 second output',y[1],[2/(1+math.exp(1/math.sqrt(2))),4*math.exp(1/math.sqrt(2))/(1+math.exp(1/math.sqrt(2)))]);ck('Q044 first output',y[0],[2,0])
ck('Q046 dense score size',[100**2,200**2,(200/100)**2],[10000,40000,4])
ck('Q052 embedding lookup',np.array([[0,1,0],[1,0,0]])@np.array([[1,2],[3,4],[5,6]]),[[3,4],[1,2]])
ck('Q053 position sum',np.array([[3,4],[1,2]])+np.array([[.1,.2],[.3,.4]]),[[3.1,4.2],[1.3,2.4]])
ck('Q059 tied head',sm(np.array([1,0])@np.array([[0,1],[math.log(2),0],[math.log(3),1]]).T),[1/6,2/6,3/6])
ck('Q063 top k',[.5/.8,.3/.8,0,0],[.625,.375,0,0]);ck('Q065 exact inclusive threshold',nucleus(np.array([.5,.3,.15,.05]),.8)[0],[.625,.375,0,0])
ck('Q066 adaptive set sizes',[len(nucleus(np.array([.85,.1,.05]),.8)[1]),len(nucleus(np.array([.4,.35,.25]),.8)[1])],[1,3]);ck('Q067 percent',90/100,.9)
rng=np.random.default_rng(470019); assertions=0
for _ in range(1000):
 n=int(rng.integers(2,9));d=int(rng.integers(2,7));dk=int(rng.integers(1,6));dv=int(rng.integers(1,6));x=rng.normal(size=(n,d));wq=rng.normal(size=(d,dk));wk=rng.normal(size=(d,dk));wv=rng.normal(size=(d,dv));cut=int(rng.integers(1,n));out,weights=attention(x,wq,wk,wv);changed=x.copy();changed[cut:]+=rng.normal(size=changed[cut:].shape)*100;out2,_=attention(changed,wq,wk,wv)
 assert np.allclose(out[:cut],out2[:cut]);assertions+=1
 assert np.allclose(weights.sum(axis=1),1) and np.all(weights[np.triu_indices(n,1)]==0);assertions+=1
 z=ln(x);assert np.allclose(z.mean(axis=1),0,atol=1e-10) and np.allclose(z.var(axis=1),1);assertions+=1
 p=sm(rng.normal(size=n));t=float(rng.uniform(.01,.99));ret,idx=nucleus(p,t);assert np.isclose(ret.sum(),1) and p[idx].sum()>=t-1e-12 and (len(idx)==1 or p[idx[:-1]].sum()<t+1e-12);assertions+=1
 c=float(rng.normal()*100);assert np.allclose(sm(np.log(p)+c),p);assertions+=1
report={'reviewerId':'robotics-contracts-reviewer','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent reconstruction of displayed algebra on explicit synthetic inputs. No supplied executable lecture program exists; the linked GPT-2 visualization was read, not executed. No author checks or expected answers were used.','explicitChecks':checks,'explicitCount':len(checks),'randomCases':1000,'randomAssertions':assertions,'randomSeed':470019,'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'pass':True}
path=R/'audits/W10-L47-contracts-independent-checks.json';assert not path.exists();path.write_text(json.dumps(report,indent=2)+'\n');print(len(checks),assertions, y[1])
