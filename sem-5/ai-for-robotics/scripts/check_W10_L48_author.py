"""Author mathematical checks only: no model/audio download and no ASR inference."""
from pathlib import Path
import json, math, hashlib, datetime, sys, ast
import numpy as np
import scipy
from scipy.signal.windows import hamming
R=Path(__file__).resolve().parents[1]; checks=[]
def check(name, actual, expected, atol=1e-10):
 assert np.allclose(actual,expected,atol=atol), (name,actual,expected)
 checks.append({'name':name,'actual':np.asarray(actual).tolist(),'expected':np.asarray(expected).tolist(),'passed':True})
check('Sample counts for 25 ms and 10 ms at 16 kHz',[.025*16000,.01*16000],[400,160])
check('Full unpadded frames in one second',1+(16000-400)//160,98)
check('Nyquist and bit-depth levels',[16000/2,2**8,2**16],[8000,256,65536])
n=np.arange(160); check('9 kHz aliases to negative 7 kHz sine at 16 kHz',np.sin(2*np.pi*9000*n/16000),-np.sin(2*np.pi*7000*n/16000))
check('Boundary sine vanishes at exact Nyquist',np.sin(np.pi*n),np.zeros(160))
check('Boundary cosine alternates at exact Nyquist',np.cos(np.pi*n),(-1.)**n)
check('Periodic four-point Hamming',hamming(4,sym=False),[.08,.54,1,.54]);check('Symmetric four-point Hamming',hamming(4,sym=True),[.08,.77,.77,.08]);check('Hamming zero-index endpoint',hamming(8,sym=False)[0],.08)
check('Pointwise window operation',np.array([2,4,6,8])*hamming(4,sym=False),[.16,2.16,6,4.32])
check('Four-point DFT real',[*np.fft.fft([1,0,-1,0]).real],[0,2,0,2]);check('Four-point DFT general',np.abs(np.fft.fft([1,2,3,4])-np.array([10,-2+2j,-2,-2-2j])),np.zeros(4))
check('DFT bin spacing',16000/400,40)
check('Mel at 700 Hz',1127*np.log(2),781.1778724910583)
check('Two toy Mel channel energies',np.array([[1,.5,0],[0,.5,1]])@np.array([1,4,9]),[3,11])
check('Toy log energies',np.log([3,11]),[1.0986122886681098,2.3978952727983707])
q=np.array([[1.,0.]]);k=np.eye(2);v=np.array([[2.,0.],[0.,4.]])
scores=q@k.T/np.sqrt(2);a=np.exp(scores)/np.exp(scores).sum(axis=-1,keepdims=True)
check('Cross-attention weights',a,[[.6697615493266569,.3302384506733431]])
check('Cross-attention output',a@v,[[1.3395230986533138,1.3209538026933724]])
check('Zero query averages values',np.ones((1,2))/2@v,[[1,2]])
check('Conditional sequence probability',.5*.4*.25,.05);check('Log chain equivalence',sum(np.log([.5,.4,.25])),np.log(.05))
check('Greedy versus global counterexample',[.6*.51,.4*.99],[.306,.396])
check('Acoustic-only length normalization lambda .2',[-8/4+.2*-3,-5/2+.2*-1],[-2.6,-2.7])
check('Acoustic-only length normalization lambda .5',[-8/4+.5*-3,-5/2+.5*-1],[-3.5,-3])
check('Mono squeeze shape',np.zeros((1,160)).squeeze().shape,[160]);check('Stereo squeeze shape',np.zeros((2,160)).squeeze().shape,[2,160])
check('Declared stereo mean downmix',np.array([[1.,3.],[3.,5.]]).mean(axis=0),[2,4])
check('DFT magnitude and squared magnitude',[abs(3+4j),abs(3+4j)**2],[5,25])
check('Width-one shared kernel',np.array([2,-1,3])*2,[4,-2,6])
check('Multiple channel sum',2*4+3*(-1),5)
check('Stride two output count',(8+2-3)//2+1,4)
check('Integrated framing and attention shape',[4,((1+(16000-400)//160)+2-3)//2+1],[4,49])
# Cross-check direct DFT and inverse Mel over varied inputs, without calling a pretrained model.
rng=np.random.default_rng(48); varied=0
for _ in range(500):
 N=int(rng.integers(2,33));x=rng.normal(size=N);idx=np.arange(N)
 direct=np.exp(-2j*np.pi*np.outer(idx,idx)/N)@x
 assert np.allclose(direct,np.fft.fft(x),atol=1e-10);varied+=1
 f=float(rng.uniform(0,8000));m=1127*np.log1p(f/700);assert np.isclose(700*np.expm1(m/1127),f);varied+=1
 L=int(rng.integers(2,100));assert np.allclose(.54-.46*np.cos(2*np.pi*np.arange(L)/L),hamming(L,sym=False));varied+=1
source='''from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
import torchaudio
model_name = "openai/whisper-small"
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name)
audio, sampling_rate = torchaudio.load("/content/sample_audio.mp3")
if sampling_rate != 16000:
    resampler = torchaudio.transforms.Resample(sampling_rate, 16000)
    audio = resampler(audio)
inputs = processor(audio.squeeze().numpy(), sampling_rate=16000, return_tensors="pt")
with torch.no_grad():
    predicted_ids = model.generate(inputs["input_features"])
transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
'''
ast.parse(source);(R/'audits/W10-L48-literal-slide-code.py.txt').write_text(source)
nb=json.loads((R/'sources/supplemental/L48-official-week10_lecture48.ipynb').read_text());code=[''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code'];assert any('sample.flac' in c for c in code);assert any('print("Transcription:", transcription)' in c for c in code)
result={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Author checks, not independent verification. Added numerical inputs are explicitly labeled. Literal snippet parsed only; no external ASR weights or audio were retrieved or executed.','versions':{'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__},'checks':checks,'namedChecks':len(checks),'variedChecks':varied,'literalCodeParsed':True,'literalCodeExecuted':False,'pretrainedModelExecuted':False,'notebookReadOnly':True,'notebookDifferences':['Official notebook retrieves a public FLAC rather than the slide MP3 path.','Official notebook adds a labeled print of transcription; slide assignment alone does not print.'],'dependencyBlockerPath':'audits/W10-L48-source-retrieval.json'}
(R/'audits/W10-L48-author-checks-dsp.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'namedChecks':len(checks),'variedChecks':varied,'pretrainedModelExecuted':False}))
