#!/usr/bin/env python3
"""Source-first independent checks, written without reading author L32 keys/checks."""
import json,hashlib,inspect,datetime,importlib.metadata as md,warnings
from pathlib import Path
import numpy as np
import cv2
from scipy.signal import convolve2d,correlate2d
from machinevisiontoolbox import Image,Kernel
R=Path(__file__).resolve().parents[1];checks=[];evidence={}
def ck(name,condition,detail):
 assert bool(condition),(name,detail)
 checks.append({'name':name,'passed':True,'result':detail})
def arr(x):return np.asarray(x).tolist()
with warnings.catch_warnings():
 warnings.simplefilter('ignore',DeprecationWarning)
 flowers=Image.Read('flowers9.png');A=flowers.image
 ck('Source flowers dimensions',A.shape==(640,426,3),list(A.shape))
 ck('Source pixel RGB and coordinate order',np.array_equal(A[400,100,:],[253,23,1]) and np.array_equal(flowers[100,400],[253,23,1]),arr(A[400,100,:]))
 ck('Literal NumPy crop has empty columns',A[250:400,450:600,:].shape==(150,0,3),list(A[250:400,450:600,:].shape))
 try:flowers[450:600,250:400,:]
 except ValueError as ex:evidence['literalImageCropError']=str(ex)
 else:raise AssertionError('Expected installed Image construction to reject empty crop')
 ck('Corrected crop APIs agree',np.array_equal(A[450:600,250:400,:],flowers[250:400,450:600,:].image),list(flowers[250:400,450:600,:].shape))
 F=flowers.to('float')
 ck('Image.to float alias and original preserved',F.dtype==np.float32 and flowers.dtype==np.uint8 and F is not flowers,{'newDtype':str(F.dtype),'originalDtype':str(flowers.dtype),'range':[float(F.image.min()),float(F.image.max())]})
 ck('Image.to normalization',np.allclose(F.image,A.astype(np.float32)/255),float(F.image[400,100,0]))
 seen=[]
 def fn(x):seen.append(x.shape);return x+100
 I=Image(np.array([[96,200]],dtype=np.uint8));O=I.apply(fn)
 ck('apply default receives one whole array',seen==[(1,2)] and np.array_equal(O.image,[[196,44]]),{'callbackShapes':seen,'output':arr(O.image)})
 ck('astype is not normalization',np.float32(np.uint8(255))==255.0,255.0)
 ck('uint8 retained addition wraps',int((np.array([200],dtype=np.uint8)+100)[0])==44,44)
 threshold=np.array([99,100,101])>=100
 ck('Inclusive threshold and bool storage',threshold.dtype==bool and threshold.tolist()==[False,True,True],threshold.tolist())
 ck('Negative and addition arithmetic',255-96==159 and 96+100==196,{'negative':159,'added':196})
 stretch=255*(118-91)/(138-91);gamma=255*(118/255)**7.5
 ck('Source stretch mismatch recomputed',abs(stretch-146.48936170212767)<1e-12,stretch)
 ck('Source gamma recomputed',round(gamma,3)==0.788,gamma)
 H=np.array([[0,1,0,1,0],[0,1,0,1,0],[0,1,1,1,0],[0,1,0,1,0],[0,1,0,1,0]],dtype=float)*255
 ck('Binary H count',int(np.count_nonzero(H))==11,11)
 small=np.array([[4,0,1],[1,0,0],[1,2,0]])
 ck('Source integer window sum and mean',small.sum()==9 and small.mean()==1,{'sum':int(small.sum()),'mean':float(small.mean())})
 box=np.ones((3,3))/9;B=correlate2d(H,box,mode='valid')
 ck('Two H box outputs',np.allclose(B[0,:2],[1020/9,1785/9]),arr(B[0,:2]))
 binomial=np.array([[1,2,1],[2,4,2],[1,2,1]])/16
 G=correlate2d(H,binomial,mode='valid')
 ck('Two H binomial outputs',np.allclose(G[0,:2],[143.4375,159.375]),arr(G[0,:2]))
 ck('Binomial normalization and center',binomial.sum()==1 and binomial[1,1]==.25,{'sum':float(binomial.sum()),'center':float(binomial[1,1])})
 v,u=np.mgrid[-1:2,-1:2];sigma=.85;gauss=np.exp(-(u*u+v*v)/(2*sigma*sigma))/(2*np.pi*sigma*sigma);GN=gauss/gauss.sum()
 ck('Continuous Gaussian center',np.isclose(gauss[1,1],.2202836582586787),{'continuousCenter':float(gauss[1,1]),'finiteSum':float(gauss.sum()),'normalizedFiniteCenter':float(GN[1,1])})
 ck('Binomial differs from sampled Gaussian',not np.allclose(GN,binomial),arr(GN))
 ck('Both Mona Lisa kernels have 31 support',Kernel.Box(h=15).K.shape==Kernel.Gauss(sigma=5,h=15).K.shape==(31,31),[31,31])
 ck('Both smoothing kernels normalized',np.isclose(Kernel.Box(h=15).K.sum(),1) and np.isclose(Kernel.Gauss(sigma=5,h=15).K.sum(),1),{'box':float(Kernel.Box(h=15).K.sum()),'gauss':float(Kernel.Gauss(sigma=5,h=15).K.sum())})
 castle=Image.Read('castle.png',mono=True,dtype='float');profile=castle.image[360,560:600];difference=np.diff(profile)
 ck('Castle profile lengths',len(profile)==40 and len(difference)==39,{'profile':len(profile),'difference':len(difference),'positivePeak':float(difference.max()),'negativePeak':float(difference.min())})
 ck('Backward and central differences',80-20==60 and (7-3)/2==2,{'backward':60,'central':2})
 ck('Central correlation kernel',np.dot([3,100,7],[-.5,0,.5])==2,2)
 sobel=np.array([[1,0,-1],[2,0,-2],[1,0,-1]])/8
 ramp=np.tile(np.arange(11,dtype=float),(9,1))
 ck('Source Sobel convention gives positive horizontal ramp',np.allclose(convolve2d(ramp,sobel,mode='valid'),1),1)
 ck('Correlation sign is opposite',np.allclose(correlate2d(ramp,sobel,mode='valid'),-1),-1)
 ck('Transposed Sobel on horizontal ramp gives zero',np.allclose(convolve2d(ramp,sobel.T,mode='valid'),0),0)
 ck('Installed Kernel and convolve agree on sign',np.allclose(Image(ramp).convolve(Kernel.Sobel(),mode='valid').image,1),1)
 ck('Valid 9 by 11 shape',convolve2d(ramp,sobel,mode='valid').shape==(7,9),[7,9])
 ck('Zero-padded top-left H mean',np.isclose(convolve2d(H,box,mode='same',boundary='fill')[0,0],510/9),510/9)
 ck('Constant positive zero border darkens',convolve2d(np.ones((5,5))*9,box,mode='same')[0,0]==4,4)
 first=np.array([[10,11,10],[9,10,11],[10,9,10]]);second=np.array([[10,0,2],[9,10,9],[11,9,99]])
 ck('Source median windows',np.median(first)==10 and np.median(second)==9,{'first':10,'second':9,'secondMean':float(second.mean())})
 ck('Median ignores listing direction',np.median(first.ravel(order='C'))==np.median(first.ravel(order='F')),10)
 ck('Median additivity counterexample',np.median([0,0,1])+np.median([0,1,0])==0 and np.median(np.array([0,0,1])+[0,1,0])==1,{'sumOfMedians':0,'medianOfSum':1})
 ck('Rank indexes',9//2==4 and 25//2==12,[4,12])
 med=Image(second.astype(np.uint8)).rank(rank=4,h=1).image[1,1]
 ck('Literal rank wrapper middle output',med==9,int(med))
 hist=np.array([1,2,1,0]);cdf=np.cumsum(hist)/sum(hist)
 ck('Inclusive CDF',np.allclose(cdf,[.25,.75,1,1]),arr(cdf))
 ck('CDF plot mapping rounding',round(255*.32)==82,82)
 tiny=Image(np.array([[0,1],[1,2]],dtype=np.uint8));equalized=tiny.normhist().image
 ck('normhist is not necessarily raw CDF mapping',np.array_equal(equalized,[[0,170],[170,255]]),{'opencv':arr(equalized),'rawCDFNearest':[[64,191],[191,255]]})
 # Vary values, not source facts. Assert algebraic invariants with independent scipy references.
 rng=np.random.default_rng(32019)
 for _ in range(1000):
  a=rng.normal(size=(9,11));k=rng.normal(size=(3,3));c=float(rng.normal());sym=(k+np.flip(k))/2
  assert np.allclose(convolve2d(a,k,'valid'),correlate2d(a,np.flip(k),'valid'))
  assert np.allclose(convolve2d(a,sym,'valid'),correlate2d(a,sym,'valid'))
  assert np.allclose(correlate2d(np.full((7,7),c),box,'valid'),c)
  vals=rng.integers(0,256,size=25);assert np.median(vals)==np.sort(vals)[12]
 ck('1000 varied trials, four invariants each',True,{'trials':1000,'comparisons':4000})
 # Save reproducible primary installed-code evidence and actual asset hashes, without full code copy.
 for fn in [Image.__getitem__,Image.to,Image.apply,Image.normhist,Image.convolve,Image.rank,Kernel.Sobel]:
  f=Path(inspect.getsourcefile(fn));lines,start=inspect.getsourcelines(fn)
  evidence[fn.__qualname__]={'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'line':start,'sourceExcerptSha256':hashlib.sha256(''.join(lines).encode()).hexdigest()}
 import mvtbdata
 root=Path(mvtbdata.__file__).parent
 assets={}
 for name in ['flowers9.png','castle.png','street.png','monalisa.png','pollen_image.tif','ckt_board_saltpep.tif']:
  paths=list(root.rglob(name));assets[name]=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
 out={'reviewerId':'build_offline_study_interface:L32-independent-reviewer','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'answerKeysRead':False,'versions':{n:md.version(n) for n in ['machinevision-toolbox-python','mvtb-data','numpy','opencv-python','scipy']},'namedAssertions':len(checks),'checks':checks,'primaryInstalledCodeEvidence':evidence,'assets':assets,'scope':'Source pixel transcription and declared mathematical inputs. Missing pollen and circuit images are not silently substituted. No author L32 code/checks read.','primaryDocumentation':['https://petercorke.github.io/machinevision-toolbox-python/stubs/machinevisiontoolbox.Image.to.html','https://petercorke.github.io/machinevision-toolbox-python/stubs/machinevisiontoolbox.Image.apply.html','https://petercorke.github.io/machinevision-toolbox-python/_modules/machinevisiontoolbox/Kernel.html']}
 (R/'audits/W07-L32-independent-computations.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'assertions':len(checks),'trials':1000,'comparisons':4000}))
