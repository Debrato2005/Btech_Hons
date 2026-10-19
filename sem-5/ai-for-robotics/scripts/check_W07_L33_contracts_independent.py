"""Independent L33 source transcription and mathematical checks, before keys.
Reuse only installed runtime and original image assets, never author check scripts/results.
"""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/l33-review-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/l33-review-cache')
os.environ.setdefault('MPLBACKEND','Agg')
import datetime,hashlib,json,inspect,importlib.metadata as metadata
import numpy as np, cv2 as cv
import matplotlib.pyplot as plt
from machinevisiontoolbox import Image
from machinevisiontoolbox.ImagePointFeatures import BaseFeature2D
from machinevisiontoolbox.ImageBlobs import Blobs
from machinevisiontoolbox.ImageLineFeatures import HoughFeature
ROOT=Path(__file__).resolve().parents[1]
ASSETS=Path('/tmp/robotics-l33-venv/lib/python3.12/site-packages/mvtbdata/images')
OUT=ROOT/'audits/W07-L33-contracts-independent-checks.json'
result={'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':'Before L33 author keys, solutions or checks','versions':{n:metadata.version(n) for n in ['machinevision-toolbox-python','opencv-python','numpy']},'assertions':[],'sourceAssets':{},'installedSourceEvidence':[],'observed':{}}
def save():
 result['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
def check(label,ok):
 assert bool(ok),label
 result['assertions'].append(label)
def arr(im):return im.array if isinstance(im,Image) else np.asarray(im)
def load(name,**kw):
 p=ASSETS/name;result['sourceAssets'][name]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};return Image.Read(str(p),**kw)
for f in [Image.threshold_adaptive,Image.labels_binary,Image.kmeans_color,BaseFeature2D.filter,Blobs.polarmatch,HoughFeature.lines,HoughFeature.lines_p]:
 path=Path(inspect.getfile(f));result['installedSourceEvidence'].append({'symbol':f.__qualname__,'path':str(path),'fileSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'firstLine':inspect.getsourcelines(f)[1],'sourceSha256':hashlib.sha256(inspect.getsource(f).encode()).hexdigest()})
# Independent arithmetic and algebra, from supplied problems and source equations.
check('Adaptive numerical threshold',120-.5*20==110 and 115>=110)
check('Impulse receptor response',np.allclose(2*np.array([.2,.5,.1]),[.4,1,.2]))
A=np.array([[1.,.2,.1],[.1,1.,.3],[.2,.1,1.]]);c=np.array([.4,1.,.2]);p=np.linalg.solve(A,c)
check('Primary mixing inverse reconstructs receptor vector',np.allclose(A@p,c))
check('Chromaticity and positive common-scale invariance',np.allclose(np.array([2,3,5])/10,np.array([4,6,10])/20))
check('Normalized chromaticity sums to one',np.isclose(np.sum(np.array([2,3,5])/10),1))
check('Two-class uint8 inversion',np.array_equal((1-np.array([0,1],dtype=np.uint8))*255,[255,0]))
check('Centroid quotient',np.allclose([10/4,6/4],[2.5,1.5]))
J=np.array([[30-100/4,17-60/4],[17-60/4,14-36/4]])
check('Raw to central second moments',np.allclose(J,[[5,2],[2,5]]))
w,V=np.linalg.eigh(J);major=V[:,-1]
check('Eigenvalues and major direction',np.allclose(w,[3,7]) and np.isclose(abs(major@np.array([1,1])/np.sqrt(2)),1))
check('Equivalent ellipse semiaxes',np.allclose(2*np.sqrt(w/4),np.sqrt([3,7])))
check('Ellipse example axes and ratio',np.allclose(2*np.sqrt(np.array([100,25])/25),[4,2]))
check('Zero first central moment identity',10-(10/4)*4==0)
check('Chain length',np.isclose(sum([1,1,np.sqrt(2),1]),3+np.sqrt(2)))
check('Circle circularity',np.isclose(4*np.pi*(np.pi*4**2)/(2*np.pi*4)**2,1))
check('Square circularity',np.isclose(4*np.pi*7**2/(4*7)**2,np.pi/4))
check('Circularity under threefold scale',np.isclose(4*np.pi*(9*8)/(3*12)**2,4*np.pi*8/12**2))
check('Gradient magnitude and angle',np.hypot(3,4)==5 and np.isclose(np.degrees(np.arctan2(4,3)),53.13010235415598))
check('Hysteresis connected chain',all(x>=5 for x in [12,8,6]) and 12>=10 and not 8>=10)
pts=np.array([[9,9],[39,9],[24,24],[9,39],[39,39]])
check('Ideal Hough support',sum(pts[:,1]==39)==2 and sum(pts.sum(axis=1)==48)==3)
check('Vertical polar line',np.isclose(6*np.cos(0)+44*np.sin(0),6))
check('Harris numerical strength',np.isclose(np.linalg.det(np.diag([4,4]))-.04*np.trace(np.diag([4,4]))**2,13.44))
check('SIFT neighbor and descriptor counts',8+9+9==26 and 4*4*8==128)
strength=np.array([10,6,5,4]);scale=np.array([6,4,5,8]);mask=(strength>=.5*strength.max())&(scale>=5)
check('Inclusive strength and scale filter',np.array_equal(np.where(mask)[0],[0,2]))
rng=np.random.default_rng(330033)
for _ in range(1000):
 xy=rng.normal(size=(17,2));weights=rng.uniform(.1,2,17);shift=rng.normal(size=2);mass=weights.sum();mean=np.average(xy,axis=0,weights=weights);center=xy-mean
 checkval=np.sum(center*weights[:,None],axis=0)
 assert np.allclose(checkval,0,atol=1e-12)
 cov=(center*weights[:,None]).T@center;translated=xy+shift-np.average(xy+shift,axis=0,weights=weights)
 assert np.allclose(cov,(translated*weights[:,None]).T@translated)
 sc=rng.uniform(.2,8);assert np.allclose(sc*weights/(sc*weights).sum(),weights/mass)
result['randomTrials']=1000;result['checksPerTrial']=3;save()
# Original source image 1, source threshold script with no expected author outputs.
castle=load('castle.png',dtype='float');t=castle.otsu();manual=castle>=.7;otsu=castle>=t;adaptive=castle.threshold_adaptive(h=15)
expected=cv.adaptiveThreshold(castle.array_as('uint8'),255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,31,0)
check('Adaptive half-width31 and mean-minus-C implementation',np.array_equal(arr(adaptive),arr(adaptive).dtype.type(1)*expected) or np.array_equal(arr(adaptive),expected/255))
result['observed']['castle']={'shape':list(castle.shape),'otsuThreshold':float(t),'manualForeground':int(np.count_nonzero(arr(manual))),'otsuForeground':int(np.count_nonzero(arr(otsu))),'adaptiveForeground':int(np.count_nonzero(arr(adaptive)))}
fig,axes=plt.subplots(1,4,figsize=(16,4))
for ax,im,title in zip(axes,[castle,manual,otsu,adaptive],['Original','Manual 0.7',f'Otsu {t:.6f}','Adaptive half-width15']):ax.imshow(arr(im),cmap='gray');ax.set_title(title);ax.axis('off')
fig.tight_layout();fig.savefig(ROOT/'audits/W07-L33-contracts-independent-castle.png',dpi=130);plt.close(fig);save()
# Original source image 2, chromatic classes, connected instances, moments and perimeters.
targets=load('yellowtargets.png',dtype='float',gamma='sRGB');ab=targets.colorspace('L*a*b*').plane('a*:b*');cl,centers,residual=ab.kmeans_color(k=2,seed=0)
yellow=int(np.argmax(centers[1,:]));check('Two chromatic classes',len(np.unique(arr(cl)))==2)
source_mask=(1-cl.astype(np.uint8))*255
check('Source assumes yellow label0 in this version',yellow==0)
lab,N=source_mask.labels_binary();blobs=source_mask.blobs()
check('Four foreground targets and background count',len(blobs)==4 and N==5)
check('Top connected label and blob index differ',int(arr(lab)[218,366])==1 and np.argmin(np.array(blobs.centroid)[:,1])==3)
small=Image(np.array([[255,0],[0,255]],dtype=np.uint8));_,n4=small.labels_binary(connectivity=4);_,n8=small.labels_binary(connectivity=8)
check('Four versus eight connectivity',n4-1==2 and n8-1==1)
b3=blobs[3];mm=b3.moments;m00=mm.m00;u20=mm.mu20
try:eval('np.array([[u20,u11],[u11,u02]])',{'np':np,'u20':u20,'m00':m00})
except NameError as ex:check('Fresh source excerpt missing u11',"u11" in str(ex))
else:raise AssertionError('Undefined moment should not be inferred')
J3=np.array([[mm.mu20,mm.mu11],[mm.mu11,mm.mu02]]);vals=np.linalg.eigvalsh(J3);axes_len=2*np.sqrt(vals/m00)
check('Blob semiaxis aspect agrees with moment matrix',np.isclose(axes_len[0]/axes_len[1],b3.aspect))
check('Contour area equals contour m00 not raster count',np.isclose(float(b3.area),m00) and not np.isclose(np.count_nonzero(arr(lab)==1),m00))
sim,offset=blobs.polarmatch(1);check('Polar match self similarity',np.isclose(sim[1],1))
rr,_=b3.polar();check('Radius normalization sum',np.isclose((rr/rr.sum()).sum(),1))
result['observed']['targets']={'shape':list(targets.shape),'chromaticCentroids':centers.tolist(),'yellowClass':yellow,'residual':float(residual),'labelsIncludingBackground':int(N),'blobCount':len(blobs),'topRasterPixelCount':int(np.count_nonzero(arr(lab)==1)),'blob3':{'area':float(b3.area),'centroid':np.array(b3.centroid).tolist(),'aspect':float(b3.aspect),'orientationRadians':float(b3.orientation),'J':J3.tolist(),'semiaxesSmallLarge':axes_len.tolist(),'perimeterShape':list(b3.perimeter.shape),'perimeterLength':float(b3.perimeter_length)},'polarSimilarity':np.asarray(sim).tolist(),'polarOffset':np.asarray(offset).tolist(),'huShape':list(np.asarray(blobs.humoments()).shape)}
fig,aa=plt.subplots(1,3,figsize=(14,4));aa[0].imshow(arr(targets));aa[1].imshow(arr(cl));aa[2].imshow(arr(lab));
for ax,title in zip(aa,['Original','Two chromatic classes','Connected labels']):ax.set_title(title);ax.axis('off')
fig.tight_layout();fig.savefig(ROOT/'audits/W07-L33-contracts-independent-targets.png',dpi=130);plt.close(fig);save()
# Original image 3, standard Hough; explicit support-count test for strict threshold.
five=load('5points.png',mono=True);h=five.Hough();l1=h.lines(1);l2=h.lines(2);l3=h.lines(3)
tiny=np.zeros((30,30),dtype=np.uint8);tiny[[5,10,15],10]=255
ht=Image(tiny).Hough();strict2=ht.lines(2);strict3=ht.lines(3)
check('Standard Hough strict support threshold',len(strict2)>0 and len(strict3)==0)
result['observed']['fivePoints']={'shape':list(five.shape),'nonzeroCount':int(np.count_nonzero(arr(five))),'threshold1Lines':l1.tolist(),'threshold2Lines':l2.tolist(),'threshold3Lines':l3.tolist(),'strictControl2Count':len(strict2),'strictControl3Count':len(strict3)};save()
# Original image 4, church pipeline including L1 versus explicit L2.
church=load('church.png',mono=True);img=church.to_int();smooth=cv.GaussianBlur(img,(5,5),1.4);edge=cv.Canny(smooth,50,100);e1=cv.Canny(smooth,50,100,L2gradient=False);e2=cv.Canny(smooth,50,100,L2gradient=True)
check('Default Canny matches explicit L1 flag',np.array_equal(edge,e1));check('L2 flag changes actual church result',not np.array_equal(edge,e2))
lines=Image(edge).Hough().lines_p(100,minlinelength=200,maxlinegap=5,seed=0)
check('Probabilistic Hough segment shape',lines.ndim==2 and lines.shape[1]==4)
result['observed']['church']={'shape':list(church.shape),'defaultEdgeCount':int(np.count_nonzero(edge)),'L2EdgeCount':int(np.count_nonzero(e2)),'houghSegmentCount':len(lines),'segments':lines.tolist()}
fig,aa=plt.subplots(1,3,figsize=(14,4));aa[0].imshow(img,cmap='gray');aa[1].imshow(edge,cmap='gray');aa[2].imshow(img,cmap='gray')
for line in lines:aa[2].plot([line[0],line[2]],[line[1],line[3]])
for ax,title in zip(aa,['Church original','Canny default','Probabilistic line segments']):ax.set_title(title);ax.axis('off')
fig.tight_layout();fig.savefig(ROOT/'audits/W07-L33-contracts-independent-church.png',dpi=130);plt.close(fig);save()
# Original image 5, source Harris and SIFT calls.
building=load('building2-1.png',mono=True);harris=building.Harris(nfeat=500);sift=building.SIFT();filtered=sift.filter(percentstrength=50,minscale=5)
s=np.asarray(sift.strength);sc=np.asarray(sift.scale);expected_mask=(s>=.5*s.max())&(sc>=5)
check('Harris cap is not class count',len(harris)<=500)
check('SIFT filter means fraction of maximum not count percentile',len(filtered)==int(expected_mask.sum()))
check('SIFT descriptors length',np.asarray(filtered.descriptor).shape[-1]==128)
result['observed']['building']={'shape':list(building.shape),'harrisCount':len(harris),'siftUnfilteredCount':len(sift),'siftFilteredCount':len(filtered),'maximumStrength':float(s.max()),'descriptorShape':list(np.asarray(filtered.descriptor).shape),'filteredMinScale':float(np.min(filtered.scale))}
fig,aa=plt.subplots(1,3,figsize=(14,4))
for ax in aa:ax.imshow(arr(building),cmap='gray');ax.axis('off')
aa[1].scatter(np.asarray(harris.u),np.asarray(harris.v),s=4,c='yellow',marker='+')
aa[2].scatter(np.asarray(filtered.u),np.asarray(filtered.v),s=np.asarray(filtered.scale)*2,facecolors='none',edgecolors='yellow',linewidths=.5)
for ax,title in zip(aa,['Building original','Harris locations','Filtered SIFT scales']):ax.set_title(title)
fig.tight_layout();fig.savefig(ROOT/'audits/W07-L33-contracts-independent-building.png',dpi=130);plt.close(fig)
result['assertionCount']=len(result['assertions']);result['completedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();result['scriptSha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();save();print(json.dumps(result,indent=2))
