#!/usr/bin/env python3
"""Author checks, not an independent review. Run in the isolated MVTB environment."""
import os
os.environ.setdefault('MPLBACKEND','Agg');os.environ.setdefault('MPLCONFIGDIR','/tmp/robotics-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/robotics-cache')
from pathlib import Path
import json,hashlib,importlib.metadata as md,math,inspect
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
from machinevisiontoolbox import Image
from machinevisiontoolbox.base import plot_chromaticity_diagram
from spatialmath.base import plot_point,plot_ellipse
R=Path(__file__).resolve().parents[1];checks=[];runs={};assets={}
def check(name,ok,detail=None):
 assert bool(ok),(name,detail)
 checks.append({'name':name,'passed':True,'detail':detail})
def read(name,**kw):
 im=Image.Read(name,**kw);p=Path(im.name);assets[name]={'officialPackage':'mvtb-data','pathWithinPackage':'images/'+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'shape':list(im.shape)};return im
# Explicit added context: imports above, package-provided image paths, noninteractive plotting.
castle=read('castle.png',dtype='float');t=.7;t=castle.otsu();cmask=castle>=t
adaptive=castle.threshold_adaptive(h=15)
check('Otsu assignment overrides manual threshold',abs(float(t)-.6039)<.001,float(t))
check('Adaptive h15 equals OpenCV mean-minus-C block31',np.array_equal(adaptive.to_int(),cv.adaptiveThreshold(castle.to_int(),255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,31,0)))
runs['castle']={'otsu':float(t),'slideOtsu':.6039,'qualification':'Version-specific numerical reproduction; do not assert bit-identical slide value. h=15 is 31 pixels, not caption15.'}
# Actual source input, not a synthetic substitute.
targets=read('yellowtargets.png',dtype='float',gamma='sRGB')
ab=targets.colorspace('L*a*b*').plane('a*:b*')
bplane=ab.plane('b*:')
targets_labels,targets_centroids,resid=ab.kmeans_color(k=2,seed=0)
mask=(1-targets_labels.astype(np.uint8))*255
labels,N=mask.labels_binary();blobs=mask.blobs()
check('Two chromatic classes',len(np.unique(targets_labels.A))==2)
check('Four connected foreground targets plus background',N==5 and len(blobs)==4,int(N))
check('Top target connected label1',int(labels.A[218,366])==1)
check('Source blob3 area',np.isclose(blobs[3].area,5609.5))
check('Source blob3 centroid',np.allclose(blobs[3].centroid,[365.7040,218.2074],atol=1e-4))
check('Source blob3 aspect and umin',np.isclose(blobs[3].aspect,.7489,atol=1e-4) and blobs[3].umin==331)
check('Raster count and contour area are different conventions',int(np.count_nonzero(labels.A==1))!=blobs[3].area)
# Preserve literal incomplete code failure before adding the missing moment names.
ns={'np':np,'blobs':blobs}
try:exec('m00=blobs[3].moments.m00\nu20=blobs[3].moments.mu20\nJ3=np.array([[u20,u11],[u11,u02]])',ns)
except NameError as e:literal_error=str(e)
else:raise AssertionError('Literal missing-name excerpt unexpectedly executed')
check('Literal source excerpt lacks u11',"u11" in literal_error,literal_error)
m00=blobs[3].moments.m00;u20=blobs[3].moments.mu20
# Added definitions, explicitly absent from the displayed excerpt:
u11=blobs[3].moments.mu11;u02=blobs[3].moments.mu02
J3=np.array([[u20,u11],[u11,u02]])
(uc3,vc3)=blobs[3].centroid
hu=blobs.humoments();r,th=blobs[0].polar();similarity,offset=blobs.polarmatch(1)
check('Blob perimeter coordinate shape',blobs[3].perimeter.shape==(2,303),list(blobs[3].perimeter.shape))
check('Self polar match near1',np.isclose(similarity[1],1),float(similarity[1]))
eig=np.linalg.eigvalsh(J3)
check('Equivalent ellipse aspect from eigenvalues',np.isclose(math.sqrt(eig[0]/eig[1]),blobs[3].aspect))
source_angles=np.deg2rad([-84.7,4.3,4.9,-87.6]);actual_angles=np.array(blobs.orientation)
angle_diff=(actual_angles-source_angles+np.pi/2)%np.pi-np.pi/2
check('Orientation agrees modulo pi within rounded slide precision',np.max(np.abs(angle_diff))<np.deg2rad(.06),np.rad2deg(angle_diff).tolist())
runs['targets']={'clusterCentroids':targets_centroids.tolist(),'residual':float(resid),'labelCountIncludingBackground':int(N),'foregroundInstances':len(blobs),'areas':np.asarray(blobs.area).tolist(),'centroids':[list(x.centroid) for x in blobs],'aspect':np.asarray(blobs.aspect).tolist(),'orientationDegrees':np.rad2deg(actual_angles).tolist(),'topTargetRasterCount':int(np.count_nonzero(labels.A==1)),'literalCodeError':literal_error,'perimeterShape':list(blobs[3].perimeter.shape),'perimeterLength':float(blobs[3].perimeter_length),'circularity':np.asarray(blobs.circularity).tolist(),'polarSimilarity':list(map(float,similarity)),'polarOrientationOffsets':offset.tolist(),'qualification':'Eigenvector signs differ by pi from printed angles; same unoriented axes. u11/u02 definitions were explicitly added after reproducing NameError.'}
# Execute source display methods as well as computations; save a compact reproducible montage.
fig,ax=plt.subplots(2,3,figsize=(15,8))
for a,arr,title in zip(ax.flat,[castle.A,cmask.A,adaptive.A,targets.A,labels.A,bplane.A],['Castle original','Otsu comparison','Adaptive h=15 (31×31)','Actual yellow targets','Connected labels including 0','Lab b* plane']):
 a.imshow(arr,cmap='gray' if np.asarray(arr).ndim==2 and 'labels' not in title else 'viridis');a.set_title(title);a.axis('off')
fig.tight_layout();fig.savefig(R/'audits/W07-L33-author-region-reproduction.png',dpi=140);plt.close('all')
mask.disp(block=None);blobs.plot_centroid(marker='+',color='blue');blobs.plot_box(color='red');plot_ellipse(4*J3/m00,centre=(uc3,vc3),inverted=True,color='green');blobs[3].plot_perimeter(color='orange');plt.savefig(R/'audits/W07-L33-author-blob-reproduction.png',dpi=120);plt.close('all')
plot_chromaticity_diagram(colorspace='a*b*');plot_point(targets_centroids,marker='*',text='{}');plt.close('all')
# Five-point Hough literal calls.
points5=read('5points.png',mono='True');h=points5.Hough();h.plot_accumulator();plt.colorbar();plt.close('all')
lines=h.lines(2);line=lines[0];points5.disp();h.plot_lines(np.array([line]));h.plot_lines(h.lines(1));plt.close('all')
check('Five point input really contains5 active pixels',np.count_nonzero(points5.A)==5)
# Independently declared fixture isolates threshold semantics in the same API.
two=np.zeros((21,21),np.uint8);two[4,3]=255;two[4,14]=255
three=two.copy();three[4,8]=255
l2=Image(two).Hough().lines(2);l3=Image(three).Hough().lines(2)
check('Hough threshold2 rejects exact two-vote line but accepts three',len(l2)==0 and len(l3)>0,{'twoPointLineCount':len(l2),'threePointLineCount':len(l3)})
runs['houghFivePoints']={'linesThreshold2':lines.tolist(),'linesThreshold1Count':len(h.lines(1)),'nonzeroCoordinates_uv':np.argwhere(points5.A>0)[:,::-1].tolist(),'qualification':'Installed wrapper passes minvotes directly to OpenCV; execution confirms strict greater-than threshold. Source minimum3 comment for lines(2) is consistent, not a defect.'}
church=read('church.png',mono=True);img=church.to_int();smooth=cv.GaussianBlur(img,(5,5),1.4);edges=cv.Canny(smooth,50,100)
edges_img=Image(edges);hchurch=edges_img.Hough();segments=hchurch.lines_p(100,minlinelength=200,maxlinegap=5,seed=0)
check('Church segments returned',len(segments)>0,len(segments))
check('Canny literal default matches explicit L1 choice',np.array_equal(edges,cv.Canny(smooth,50,100,L2gradient=False)))
church.disp();hchurch.plot_lines(segments);plt.savefig(R/'audits/W07-L33-author-church-reproduction.png',dpi=120);plt.close('all')
runs['church']={'edgePixelCount':int(np.count_nonzero(edges)),'lineSegmentCount':len(segments),'segments':segments.tolist(),'cannyL2gradient':False}
view=read('building2-1.png',mono=True);harris=view.Harris(nfeat=500);sift_all=view.SIFT();sift=sift_all.filter(percentstrength=50,minscale=5);first=sift[0]
check('Harris request at most500',0<len(harris)<=500,len(harris))
response=np.asarray(sift_all.strength);scales=np.asarray(sift_all.scale);expected=(response>=response.max()*.5)&(scales>=5)
check('SIFT filter uses maximum strength and inclusive scale',len(sift)==np.count_nonzero(expected))
check('SIFT descriptor length128',np.asarray(first.descriptor).shape[-1]==128,np.asarray(first.descriptor).shape)
view.disp(block=None,darken=True);sift.plot(filled=True,color='y',hand=True,alpha=.3);plt.savefig(R/'audits/W07-L33-author-sift-reproduction.png',dpi=120);plt.close('all')
runs['keypoints']={'harrisCount':len(harris),'siftAllCount':len(sift_all),'siftFilteredCount':len(sift),'maximumStrength':float(response.max()),'firstFiltered':str(first),'descriptorShape':list(np.asarray(first.descriptor).shape),'qualification':'Filtering is response-relative plus scale, not the top50% by count. Counts are version-specific.'}
# Exact declared mathematical fixtures, independent of external image pixel values.
check('Local threshold arithmetic',120-.5*20==110)
check('Chromaticity example',np.allclose(np.array([2,3,5])/10,[.2,.3,.5]))
check('Central moments arithmetic',np.allclose([30-100/4,14-36/4,17-60/4],[5,5,2]))
J=np.array([[5.,2.],[2.,5.]])
vals,vecs=np.linalg.eigh(J)
check('Moment eigenvalue derivation',np.allclose(vals,[3,7]) and np.isclose(abs(vecs[:,1]@np.array([1,1])/np.sqrt(2)),1))
check('Ellipse scalar example',np.allclose(2*np.sqrt(np.array([100,25])/25),[4,2]))
check('Circularity circle and square',np.isclose(4*np.pi*(np.pi*4)/(4*np.pi)**2,1) and np.isclose(4*np.pi*4/8**2,np.pi/4))
check('Gradient example',np.isclose(np.hypot(3,4),5) and np.isclose(np.rad2deg(np.arctan2(4,3)),53.13010235415598))
check('Harris example',np.isclose(16-.04*64,13.44))
check('SIFT dimensions',4*4*8==128)
check('Scale neighborhood',3*3*3-1==26)
check('Strength scale declared fixture',np.flatnonzero((np.array([10,6,5,4])>=5)&(np.array([6,4,5,8])>=5)).tolist()==[0,2])
rng=np.random.default_rng(33019);trials=1000
for _ in range(trials):
 points=rng.normal(size=(30,2));shift=rng.normal(size=2);mu=points.mean(0);J=(points-mu).T@(points-mu)
 shifted=points+shift;Js=(shifted-shifted.mean(0)).T@(shifted-shifted.mean(0))
 assert np.allclose(J,Js)
 factor=rng.uniform(.1,10);A=rng.uniform(.1,10);P=rng.uniform(1,20)
 assert np.isclose(4*np.pi*A/P**2,4*np.pi*(factor**2*A)/(factor*P)**2)
 rgb=rng.uniform(.01,10,3);assert np.allclose(rgb/rgb.sum(),factor*rgb/(factor*rgb).sum())
check('1000 varied translation/scale/normalization trials',True,'3000 invariant comparisons; fixed seed33019.')
result={'batchId':'W07-L33','role':'author reproducibility checks only; not independent verification','versions':{p:md.version(p) for p in ['machinevision-toolbox-python','mvtb-data','opencv-python','opencv-contrib-python','numpy','scipy','matplotlib']},'addedContext':['Official package assets from mvtb-data; their hashes are recorded.','Explicit Image, NumPy, cv2, matplotlib, plot_point and plot_ellipse imports.','Noninteractive Agg plotting.','u11 and u02 definitions added only after reproducing the literal missing-name error.','Synthetic checks are explicitly separate from actual source-image reproduction.'],'assets':assets,'checks':checks,'checkCount':len(checks),'variedTrials':trials,'variedComparisons':3000,'sourceRuns':runs,'independentReviewStillRequired':True}
(R/'audits/W07-L33-author-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS',len(checks),'checks;',trials,'varied trials; source images reproduced.')
