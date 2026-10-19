"""Independent NumPy/SciPy checks. No torch, audio decoding, model creation or pretrained execution."""
import json,math,hashlib,ast,datetime,pathlib
import numpy as np
from scipy.signal.windows import hamming,hann
from scipy.special import softmax
P=pathlib.Path(__file__).resolve().parents[1];checks=[]
def ok(name,condition,detail):
 assert bool(condition),(name,detail)
 checks.append({'name':name,'passed':True,'detail':detail})
def frames(n,l,h):
 if min(n,l,h)<=0 or n<l:raise ValueError('Requires n>=l>0 and h>0')
 return (n-l)//h+1
def conv(x,w,p=0,s=1,d=1):
 if s<=0 or d<=0 or p<0:raise ValueError('invalid stride/dilation/padding')
 xp=np.pad(x,(p,p));extent=d*(len(w)-1)+1
 if extent>len(xp):raise ValueError('no full placement')
 return np.array([np.dot(xp[t:t+extent:d],w) for t in range(0,len(xp)-extent+1,s)])
ok('sample/code counts',16000*.025==400 and 2**8==256 and 16000/2==8000,'400 samples;256 codes;8000Hz boundary')
ok('Nyquist phase boundary',np.allclose(np.sin(np.pi*np.arange(100)),0,atol=1e-12),'sin(pi n) numerically zero; exact symbolic identity for integer n')
ok('Nyquist cosine contrast',np.allclose(np.cos(np.pi*np.arange(8)),(-1.)**np.arange(8)),'phase matters at equality')
ok('complete frames',frames(16000,400,160)==98,'starts0..15520; next15680 would exceed length')
ok('frame boundary',frames(400,400,160)==1 and frames(560,400,160)==2,'equal/exact-hop boundary')
for args in [(399,400,160),(16000,400,0)]:
 try:frames(*args);raise AssertionError('domain not enforced')
 except ValueError:pass
ok('frame invalid domains',True,'shorter-than-frame and zero hop explicitly rejected')
ok('periodic Hamming',np.allclose(hamming(4,sym=False),[.08,.54,1,.54]),hamming(4,sym=False).tolist())
ok('symmetric Hamming',np.allclose(hamming(4,sym=True),[.08,.77,.77,.08]),hamming(4,sym=True).tolist())
ok('Hann contrast',np.allclose(hann(4,sym=False),[0,.5,1,.5]),'Hann is not Hamming; first coefficient0 not.08')
x=np.arange(1,5);manual=np.array([sum(x[n]*np.exp(-2j*np.pi*k*n/4) for n in range(4)) for k in range(4)])
ok('DFT independent sum',np.allclose(manual,[10,-2+2j,-2,-2-2j]) and np.allclose(manual,np.fft.fft(x)),str(manual.tolist()))
ok('frequency bin',10*16000/400==400,'bin10 at400Hz')
ok('complex magnitude',abs(3+4j)==5 and abs(3+4j)**2==25,'magnitude5;square25')
ok('Mel700',np.isclose(1127*np.log(2),781.1768724910584,rtol=0,atol=1e-10),'natural-log result781.1768724910584; author step781.1779 is not correct four-decimal rounding')
f=np.linspace(0,8000,1001);m=1127*np.log1p(f/700)
ok('Mel inverse',np.allclose(700*np.expm1(m/1127),f),'1001 frequencies including0/8000')
energies=np.array([[1,.5,0],[0,.5,1]])@np.array([1,4,9])
ok('weighted energies',np.array_equal(energies,[3,11]),energies.tolist())
ok('Q026 bad rationale detected',np.mean([1,4,9])!=7,'An unweighted mean is14/3, not7. The [7,7] distractor explanation needs repair.')
log=np.log10(np.maximum(np.array([0,1e-12,1e-4,1.]),1e-10));log=np.maximum(log,log.max()-8);scaled=(log+4)/4
ok('frontend floor/range/scale',np.allclose(scaled,[-1,-1,0,1]),'Source-reconstructed scalar postprocessing only, not Whisper inference')
ok('width one',np.array_equal(conv(np.array([2,-1,3]),np.array([2])),[4,-2,6]),'scalar repeated product')
ok('padded crosscorrelation',np.array_equal(conv(x,np.array([1,0,-1]),1),[-2,-2,-2,3]),'unflipped weights')
ok('kernel reversal',np.array_equal(conv(x,np.array([-1,0,1]),1),[2,2,2,-3]),'weight reversal changes signs')
ok('Q038 bad rationale detected',not np.array_equal(conv(x,np.array([1,1,-1]),1),x),'Changing only center0to1 gives[-1,0,1,7]; identity requires[0,1,0].')
ok('stride length',len(conv(np.arange(8),np.ones(3),1,2))==4,'T8,K3,P1,S2 gives4')
ok('channel sum',2*4+3*(-1)==5,'8-3=5')
Q=np.zeros((3,4));K=np.zeros((7,4));V=np.zeros((7,5));A=softmax(Q@K.T/2,axis=-1)
ok('attention shapes',(Q@K.T).shape==(3,7) and(A@V).shape==(3,5),'3x7 scores;3x5 output')
A=softmax(np.array([[1.,0.]])/np.sqrt(2),axis=-1);O=A@np.array([[2.,0.],[0.,4.]])
ok('attention values',np.allclose(O,[[1.339523098653314,1.3209538026933723]]),{'weights':A.tolist(),'output':O.tolist()})
ok('attention rounding distinction',len({tuple(np.round(z,3)) for z in [[1,2],[1.462,1.076],[2,0],O[0].tolist()]})==4,'all four displayed alternatives distinct')
ok('greedy counterexample',.6>.4 and .6*.51<.4*.99,'greedyA;.306<.396')
ok('chain product',np.isclose(.5*.4*.25,.05),'specified complete candidate .05')
sa=-8/4+.2*(-3);sb=-5/2+.2*(-1)
ok('fusion ranking',np.isclose(sa,-2.6) and np.isclose(sb,-2.7) and sa>sb,'A selected; acoustic-only normalization')
ok('fusion lambda zero',-8/4+0*(-3)==-2,'only weighted external term removed')
ok('two convolution lengths',len(conv(np.zeros(3000),np.ones(3),1,1))==3000 and len(conv(np.zeros(3000),np.ones(3),1,2))==1500,'3000 then1500')
ok('NumPy singleton semantics',np.zeros((2,8)).squeeze().shape==(2,8) and np.zeros((1,8)).squeeze().shape==(8,),'NumPy analogue only; torch behavior separately checked from official source/docs, not newly executed')
ok('downmix arithmetic',np.array_equal(np.array([[1,3],[3,5]]).mean(0),[2,4]),'explicit equal-weight policy')
ok('combined dimensions',len(conv(np.zeros(frames(16000,400,160)),np.ones(3),1,2))==49,'98frames→49keys→4x49score matrix')
nb=json.load(open(P/'sources/supplemental/L48-official-week10_lecture48.ipynb'));cells=[''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code'];pycells=[c for c in cells if not c.lstrip().startswith('!')]
for c in pycells:ast.parse(c)
ok('original notebook syntax only',len(pycells)==6,'Six non-install code cells parsed, NOT executed; saved output is historical source evidence.')
ok('notebook print distinction',any('print("Transcription:", transcription)' in c for c in pycells),'Original notebook includes print omitted by slide excerpt')
rng=np.random.default_rng(481019);trials={'frame_enumeration':0,'conv_length_values':0,'attention_normalization_shape':0,'mel_inverse':0}
for _ in range(1000):
 l=int(rng.integers(1,200));n=int(rng.integers(l,l+5000));h=int(rng.integers(1,150));assert frames(n,l,h)==len(range(0,n-l+1,h));trials['frame_enumeration']+=1
 n=int(rng.integers(10,100));k=int(rng.integers(1,6));p=int(rng.integers(0,4));s=int(rng.integers(1,5));d=int(rng.integers(1,3));xx=rng.normal(size=n);ww=rng.normal(size=k);yy=conv(xx,ww,p,s,d);assert len(yy)==(n+2*p-d*(k-1)-1)//s+1;xp=np.pad(xx,(p,p));ref=np.array([sum(xp[t+d*j]*ww[j] for j in range(k)) for t in range(0,n+2*p-d*(k-1),s)]);assert np.allclose(yy,ref);trials['conv_length_values']+=1
 nq,na,dk,dv=[int(rng.integers(1,9)) for i in range(4)];q=rng.normal(size=(nq,dk));kk=rng.normal(size=(na,dk));v=rng.normal(size=(na,dv));a=softmax(q@kk.T/np.sqrt(dk),axis=-1);assert np.allclose(a.sum(-1),1) and(a@v).shape==(nq,dv);trials['attention_normalization_shape']+=1
 ff=float(rng.uniform(0,24000));mm=1127*np.log1p(ff/700);assert np.isclose(700*np.expm1(mm/1127),ff);trials['mel_inverse']+=1
ok('varied property trials',True,trials)
o={'reviewerId':'independent-reviewer-robotics-batches-v2','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runtime':'Default Python; existing NumPy '+np.__version__+' and SciPy only. No modified venv use.','groups':len(checks),'variedCases':sum(trials.values()),'checks':checks,'runtimeBoundary':'audits/W10-L48-independent-runtime-boundary.json','pretrainedInferenceExecuted':False,'torchExecutionThisReview':False,'notebookExecution':False,'syntaxIsNotExecution':True};(P/'audits/W10-L48-independent-computations.json').write_text(json.dumps(o,indent=2)+'\n');print(o['groups'],o['variedCases'],'passed')
