"""Source-derived synthetic checks. No audio, model, dependency installation or incident venv."""
import math, json, sys, io, contextlib
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
checks=[]
def check(name,condition,result):
 assert condition,name
 checks.append({'name':name,'passed':True,'result':result})
m=1127*math.log(2)
check('Mel substitution and rounding',round(m,2)==781.18,{'exactFloat':m,'twoDecimals':round(m,2)})
e=np.array([[1,.5,0],[0,.5,1]])@np.array([1,4,9]);check('Weighted filter energies',e.tolist()==[3,11],e.tolist())
check('Wrong equal-energy alternative',sum([1,4,9])/2==7 and sum([1,4,9])/3!=7,{'totalDividedByFilterCount':7,'unweightedBinMean':14/3})
x=np.array([1,2,3,4]);z=np.correlate(np.pad(x,(1,1)),[1,0,-1],mode='valid');check('Unflipped padded kernel',z.tolist()==[-2,-2,-2,3],z.tolist())
identity=np.correlate(np.pad(x,(1,1)),[0,1,0],mode='valid');bad=np.correlate(np.pad(x,(1,1)),[1,1,-1],mode='valid');check('Identity requires zero neighbors',np.array_equal(identity,x) and bad.tolist()==[-1,0,1,7],{'identity':identity.tolist(),'centerOneCounterexample':bad.tolist()})
Q=np.arange(12).reshape(3,4);K=np.arange(28).reshape(7,4);V=np.arange(35).reshape(7,5);scores=Q@K.T;weights=np.exp(scores-scores.max(axis=1,keepdims=True));weights/=weights.sum(axis=1,keepdims=True);out=weights@V
check('Cross-attention dimensions',scores.shape==(3,7) and out.shape==(3,5),{'scores':list(scores.shape),'output':list(out.shape)})
check('Causal allowed positions include diagonal',np.tril(np.ones((4,4),dtype=int)).tolist()[2]==[1,1,1,0],np.tril(np.ones((4,4),dtype=int)).tolist())
check('Greedy token',max({'a':.5,'b':.3,'c':.2},key={'a':.5,'b':.3,'c':.2}.get)=='a','a')
check('Lambda zero preserves length normalization',math.isclose(math.log(.125)/3+0*math.log(.2),-math.log(2)),math.log(.125)/3)
check('Singleton-axis semantics illustrated in NumPy',np.squeeze(np.zeros((2,8))).shape==(2,8) and np.squeeze(np.zeros((1,8))).shape==(8,),{'stereo':[2,8],'mono':[8],'boundary':'NumPy shape demonstration, not execution of torch or torchaudio.'})
buf=io.StringIO();scope={}
with contextlib.redirect_stdout(buf):exec("transcription = 'example'",scope)
check('Assignment emits no output',buf.getvalue()=='' and scope['transcription']=='example',{'stdout':buf.getvalue(),'assignedValue':scope['transcription']})
N=8;v=np.arange(N);direct=np.array([sum(v[n]*np.exp(-2j*np.pi*k*n/N) for n in range(N)) for k in range(N)]);check('FFT computes the same DFT coefficients',np.allclose(direct,np.fft.fft(v)),float(np.max(np.abs(direct-np.fft.fft(v)))))
rng=np.random.default_rng(481023)
for _ in range(1000):
 f=float(rng.uniform(0,48000));mel=1127*math.log1p(f/700);back=700*math.expm1(mel/1127);assert math.isclose(f,back,rel_tol=2e-14,abs_tol=1e-11)
for _ in range(1000):
 n=int(rng.integers(3,50));v=rng.integers(-20,21,n);w=rng.integers(-5,6,3);p=np.pad(v,(1,1));direct=[sum(int(p[t+i])*int(w[i]) for i in range(3)) for t in range(n)];assert direct==np.correlate(p,w,'valid').tolist()
r={'reviewerId':'independent-reviewer-robotics-batches-v2','checkedAt':datetime.now(timezone.utc).isoformat(),'python':sys.executable,'numpyVersion':np.__version__,'groups':len(checks),'variedCases':2000,'checks':checks,'runtimeBoundary':'Fresh synthetic default-Python/NumPy calculations only. No installed incident packages, audio, model assets, torch runtime, pretrained inference or original notebook execution. Prior pinned primary configuration evidence reused as source evidence, not reretrieved.'}
Path('audits/W10-L48-v2-independent-computations.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
