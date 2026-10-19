"""Use existing installed torch read-only; never download model or audio."""
from pathlib import Path
import torch, numpy as np, json, datetime
R=Path(__file__).resolve().parents[1];torch.set_num_threads(1);out=[]
def check(name,a,b):
 a=np.asarray(a);b=np.asarray(b);assert np.allclose(a,b,atol=1e-10),(name,a,b);out.append({'name':name,'actual':a.tolist(),'expected':b.tolist(),'passed':True})
x=torch.tensor([[[1.,2.,3.,4.]]],dtype=torch.float64);w=torch.tensor([[[1.,0.,-1.]]],dtype=torch.float64)
check('Source-style cross-correlation, padding one',torch.nn.functional.conv1d(x,w,padding=1).numpy(),[[[-2,-2,-2,3]]])
check('Stride two',torch.nn.functional.conv1d(x,w,padding=1,stride=2).numpy(),[[[-2,-2]]])
check('Length preserving width one',torch.nn.functional.conv1d(x,torch.ones((1,1,1),dtype=torch.float64)).shape,[1,1,4])
check('Whisper-style two temporal convolution lengths',[torch.nn.functional.conv1d(torch.zeros((1,1,3000)),torch.ones((1,1,3)),padding=1).shape[-1],torch.nn.functional.conv1d(torch.zeros((1,1,3000)),torch.ones((1,1,3)),padding=1,stride=2).shape[-1]],[3000,1500])
y=torch.tensor([1.],requires_grad=True)
with torch.no_grad(): z=y*2
assert not z.requires_grad;out.append({'name':'no_grad disables result gradient tracking','passed':True})
m=torch.nn.Dropout();assert m.training
with torch.no_grad():assert m.training
out.append({'name':'no_grad does not set evaluation mode','passed':True})
check('Stereo squeeze shape',torch.zeros((2,160)).squeeze().shape,[2,160]);check('Mono squeeze shape',torch.zeros((1,160)).squeeze().shape,[160])
check('Hann and Hamming initial weights differ',[torch.hann_window(8)[0].item(),torch.hamming_window(8)[0].item()],[0,.08])
rng=np.random.default_rng(481);cases=0
for _ in range(500):
 C=int(rng.integers(1,5));T=int(rng.integers(5,30));K=int(rng.choice([1,3,5]));P=K//2;S=int(rng.integers(1,4));a=rng.normal(size=(C,T));b=rng.normal(size=(2,C,K));pad=np.pad(a,((0,0),(P,P)));N=(T+2*P-K)//S+1
 direct=np.array([[sum((pad[c,j*S:j*S+K]*b[o,c]).sum() for c in range(C)) for j in range(N)] for o in range(2)])
 actual=torch.nn.functional.conv1d(torch.from_numpy(a[None]),torch.from_numpy(b),padding=P,stride=S).numpy()[0]
 assert np.allclose(direct,actual,atol=1e-10);cases+=1
r={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Author-added tensor checks, not independent review or pretrained speech inference. Existing dependency environment used read-only.','versions':{'torch':torch.__version__,'numpy':np.__version__},'checks':out,'namedChecks':len(out),'variedChecks':cases,'pretrainedModelExecuted':False}
(R/'audits/W10-L48-author-checks-torch.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'namedChecks':len(out),'variedChecks':cases}))
