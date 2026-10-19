"""Independent L33 v2 re-solves. No revised author keys/checks are inputs."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/l33-review-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/l33-review-cache')
import json,datetime,hashlib,inspect,importlib.metadata as meta
from fractions import Fraction as F
import numpy as np,cv2 as cv
from machinevisiontoolbox import Image
from machinevisiontoolbox.ImagePointFeatures import BaseFeature2D
from machinevisiontoolbox.ImageBlobs import Blobs
R=Path(__file__).resolve().parents[1];out=R/'audits/W07-L33-v2-contracts-independent-checks.json'
r=dict(startedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase='Current answers, solutions and author v2 checks unopened; prior v1 exposure disclosed',versions={n:meta.version(n) for n in ['machinevision-toolbox-python','opencv-python','numpy']},checks=[],observed={},installedSourceEvidence=[])
def check(n,b):assert bool(b),n;r['checks'].append(n)
xy=np.array([[0.,0.],[1.,0.],[2.,1.],[3.,1.]])
m=[np.sum(xy[:,0]**p*xy[:,1]**q) for p,q in [(0,0),(1,0),(0,1),(2,0),(1,1),(0,2)]]
check('Q034 all six raw moments',np.array_equal(m,[4,6,2,14,5,2]))
center=xy.mean(0);J=(xy-center).T@(xy-center);val,vec=np.linalg.eigh(J);theta=float(np.degrees(np.arctan2(vec[1,-1],vec[0,-1]))%180);axes=2*np.sqrt(val/4)
check('Q034 centroid',np.allclose(center,[1.5,.5]));check('Q034 full scatter',np.array_equal(J,[[5,2],[2,1]]))
check('Q034 eigenvalues',np.allclose(val,[3-2*np.sqrt(2),3+2*np.sqrt(2)]));check('Q034 semiaxes',np.allclose(axes,[np.sqrt(2)-1,np.sqrt(2)+1]));check('Q034 major angle',np.isclose(theta,22.5))
r['observed']['Q034']={'rawMoments00_10_01_20_11_02':m,'centroid':center.tolist(),'scatter':J.tolist(),'eigenvalues':val.tolist(),'semiaxesSmallLarge':axes.tolist(),'angleDegreesModulo180':theta}
counts=[1,1,2,4];scores=[];within=[];mu=F(sum(i*c for i,c in enumerate(counts)),sum(counts));total=sum(F(c,8)*(i-mu)**2 for i,c in enumerate(counts))
for t in range(3):
 n0=sum(counts[:t+1]);n1=8-n0;m0=F(sum(i*counts[i] for i in range(t+1)),n0);m1=F(sum(i*counts[i] for i in range(t+1,4)),n1)
 sb=F(n0*n1,64)*(m0-m1)**2;sw=sum(F(counts[i],8)*(i-(m0 if i<=t else m1))**2 for i in range(4));scores.append(sb);within.append(sw);check(f'Q078 total variance split{t}',sb+sw==total)
check('Q078 exact between class values',scores==[F(289,448),F(169,192),F(49,64)]);check('Q078 maximizing split',scores.index(max(scores))==1);r['observed']['Q078']={'between':[str(z) for z in scores],'within':[str(z) for z in within],'totalVariance':str(total),'optimalThreshold':1}
A=np.array([[2,1,0],[0,1,1],[1,0,1]],float);c=np.array([7,4,3]);p=np.linalg.solve(A,c)
check('Q079 coupled solve',np.allclose(p,[2,3,1]));check('Q079 normalization',np.allclose(p/p.sum(),[1/3,1/2,1/6]));check('Q079 multiplication distractor',np.array_equal(A@c,[18,7,10]));r['observed']['Q079']={'coefficients':p.tolist(),'chromaticity':(p/p.sum()).tolist(),'wrongForwardProduct':(A@c).tolist()}
pts=np.array([[2,0],[4,2],[6,4],[0,5]],float);n=np.array([-1,1])/np.sqrt(2);rho=-np.sqrt(2);dot=pts@n
check('Q081 exact oblique support',np.array_equal(np.isclose(dot,rho),[True,True,True,False]));check('Q081 signed normal',np.isclose(np.degrees(np.arctan2(n[1],n[0])),135));check('Q081 strict boundary',sum(np.isclose(dot,rho))>2 and not 2>2);r['observed']['Q081']={'normal':n.tolist(),'rho':rho,'pointDots':dot.tolist(),'votes':int(sum(np.isclose(dot,rho)))}
g=np.array([[2,0],[0,2],[1,1]],float);w=np.array([.25,.25,.5]);H=np.einsum('i,ij,ik->jk',w,g,g);C=float(np.linalg.det(H)-.04*np.trace(H)**2);gmean=w@g;wrong=np.outer(gmean,gmean)
check('Q082 full weighted products',np.array_equal(H,[[1.5,.5],[.5,1.5]]));check('Q082 correct strength',np.isclose(C,1.64));check('Q082 product of means wrong option',np.isclose(np.linalg.det(wrong)-.04*np.trace(wrong)**2,-.16));check('Q082 omitted cross terms wrong option',np.isclose(np.prod(H.diagonal())-.04*np.trace(H)**2,1.89));check('Q082 trace not squared wrong option',np.isclose(np.linalg.det(H)-.04*np.trace(H),1.88));r['observed']['Q082']={'matrix':H.tolist(),'score':C,'meanGradientOuter':wrong.tolist()}
check('Q072 inclusive two-stage filter',np.array_equal(np.flatnonzero((np.array([10,6,5,4])>=5)&(np.array([6,4,5,8])>=5)),[0,2]))
# Fresh installed-library/source probes, not author expected values.
for f in [Image.Harris,Image.threshold_adaptive,Image.labels_binary,BaseFeature2D.filter,Blobs.polarmatch]:
 file=Path(inspect.getfile(f));src=inspect.getsource(f);r['installedSourceEvidence'].append({'symbol':f.__qualname__,'filePath':str(file),'fileSha256':hashlib.sha256(file.read_bytes()).hexdigest(),'firstLine':inspect.getsourcelines(f)[1],'symbolSha256':hashlib.sha256(src.encode()).hexdigest()})
check('Q083 inspected Harris cap documentation','maximum number of features' in inspect.getsource(Image.Harris))
asset=Path('/tmp/robotics-l33-venv/lib/python3.12/site-packages/mvtbdata/images/building2-1.png');im=Image.Read(str(asset),mono=True);small=Image(np.zeros((64,64),dtype=np.uint8));
try:
 blank=small.Harris(nfeat=500);blank_result={'returnedCount':len(blank)}
except IndexError as exc:
 blank_result={'exception':type(exc).__name__,'message':str(exc),'qualification':'This installed empty-descriptor edge case is not a guarantee that every blank input returns an empty feature object.'}
few=np.zeros((64,64),dtype=np.uint8);few[20:40,20:40]=255;smallh=Image(few).Harris(nfeat=500);h7=im.Harris(nfeat=7);h500=im.Harris(nfeat=500)
check('Q083 feature cap actual image',len(h7)<=7 and len(h500)<=500);check('Q083 sparse corners return fewer',len(smallh)<500);r['observed']['Q083']={'assetPath':str(asset),'assetSha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'cap7Count':len(h7),'cap500Count':len(h500),'sparseSquareCount':len(smallh),'blankImageObservation':blank_result}
mask=np.zeros((30,30),np.uint8);mask[[5,10,15],10]=255;h=Image(mask).Hough();check('Q075 strict threshold fresh control',len(h.lines(2))>0 and len(h.lines(3))==0)
x=np.array([[255,0],[0,255]],np.uint8);_,n4=Image(x).labels_binary(connectivity=4);_,n8=Image(x).labels_binary(connectivity=8);check('Q028 exact connectivity',n4-1==2 and n8-1==1)
rng=np.random.default_rng(333302)
for _ in range(1000):
 pts=rng.normal(size=(10,2));ww=rng.random(10);ww/=ww.sum();mean=ww@pts;H=np.einsum('i,ij,ik->jk',ww,pts,pts);cov=np.einsum('i,ij,ik->jk',ww,pts-mean,pts-mean)
 assert np.allclose(H-cov,np.outer(mean,mean));assert min(np.linalg.eigvalsh(H))>=-1e-12
 M=rng.normal(size=(3,3));M=M.T@M+np.eye(3);pp=rng.uniform(.1,5,3);cc=M@pp;back=np.linalg.solve(M,cc);assert np.allclose(back,pp) and np.allclose(back/back.sum(),pp/pp.sum())
r['variedCases']=1000;r['checksPerVariedCase']=3;r['assertionCount']=len(r['checks']);r['completedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();r['scriptSha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False,indent=2))
