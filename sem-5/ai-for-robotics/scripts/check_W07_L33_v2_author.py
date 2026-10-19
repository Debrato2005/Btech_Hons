from pathlib import Path
import sys,json,math,hashlib,datetime
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import question_hash
b=json.loads((R/'data/question-batches/W07-L33.json').read_text());m=json.loads((R/'audits/W07-L33-v2-repair-manifest.json').read_text());qs={q['id']:q for q in b['questions']};checks=[]
def check(name,cond):assert cond,name;checks.append(name)
check('48 accepted objects preserve exact hashes',all(question_hash(qs[k])==v for k,v in m['acceptedQuestionHashes'].items())and len(m['acceptedQuestionHashes'])==48)
x=np.array([[0,0],[1,0],[2,1],[3,1]],float);center=x.mean(0);J=(x-center).T@(x-center);lam,V=np.linalg.eigh(J)
check('centroid',np.allclose(center,[1.5,.5]));check('raw moments',np.allclose([sum(x[:,0]),sum(x[:,1]),sum(x[:,0]**2),sum(x[:,1]**2),sum(x[:,0]*x[:,1])],[6,2,14,2,5]));check('central matrix',np.allclose(J,[[5,2],[2,1]]));check('eigenvalues',np.allclose(lam,[3-2*np.sqrt(2),3+2*np.sqrt(2)]));check('semiaxes',np.allclose(np.sqrt(lam),[np.sqrt(2)-1,np.sqrt(2)+1]));check('major direction',math.isclose(math.degrees(math.atan2(V[1,1],V[0,1]))%180,22.5))
levels=np.arange(4);counts=np.array([1,1,2,4]);vals=[];within=[]
for t in range(3):
 mask=levels<=t;a=counts[mask].sum()/8;c=1-a;u=np.average(levels[mask],weights=counts[mask]);v=np.average(levels[~mask],weights=counts[~mask]);vals.append(a*c*(u-v)**2);within.append(a*np.average((levels[mask]-u)**2,weights=counts[mask])+c*np.average((levels[~mask]-v)**2,weights=counts[~mask]))
check('Otsu candidate comparisons',np.allclose(vals,[289/448,169/192,49/64]));check('Otsu weighted within',math.isclose(within[1],11/48));check('Otsu chosen threshold',np.argmax(vals)==1)
A=np.array([[2,1,0],[0,1,1],[1,0,1]],float);c=np.array([7,4,3]);p=np.linalg.solve(A,c);check('coupled primary solution',np.allclose(p,[2,3,1]));check('chromaticity',np.allclose(p/p.sum(),[1/3,1/2,1/6]));check('wrong multiply distractor',np.allclose(A@c,[18,7,10]))
points=np.array([[2,0],[4,2],[6,4],[0,5]]);rho=points@np.array([-1,1])/np.sqrt(2);check('signed Hough rho and support',sum(np.isclose(rho,-np.sqrt(2)))==3);check('strict threshold boundary',3>2 and not 3>3)
g=np.array([[2,0],[0,2],[1,1]],float);w=np.array([.25,.25,.5]);M=np.einsum('n,ni,nj->ij',w,g,g);score=np.linalg.det(M)-.04*np.trace(M)**2;check('Harris weighted products',np.allclose(M,[[1.5,.5],[.5,1.5]]));check('Harris score',math.isclose(score,1.64));mean=w@g;wrong=np.outer(mean,mean);check('Harris wrong-mean rationale',math.isclose(np.linalg.det(wrong)-.04*np.trace(wrong)**2,-.16));check('Harris cross-term rationale',math.isclose(1.5**2-.04*3**2,1.89));check('Harris trace rationale',math.isclose(2-.04*3,1.88))
from machinevisiontoolbox import Image
from machinevisiontoolbox.ImagePointFeatures import BaseFeature2D
import cv2,inspect
src=inspect.getsource(BaseFeature2D.filter);check('actual percentstrength formula','vmax * limits / 100'in src);check('actual inclusive minscale','v >= limits'in src)
img=np.zeros((9,9),dtype=np.uint8);img[1,1]=img[1,7]=img[7,1]=img[7,7]=255;_,N=Image(img).labels_binary();check('actual labels count background',N==5)
a=np.zeros((41,41),dtype=np.uint8);a[10:30,10:30]=130;check('actual adaptive 31-pixel mean',np.array_equal(Image(a).threshold_adaptive(h=15).A,cv2.adaptiveThreshold(a,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,31,0)))
# Vary data independently of the selected worked examples.
rng=np.random.default_rng(5332)
for _ in range(1000):
 z=rng.normal(size=(7,2));weights=rng.random(7);weights/=weights.sum();mu=weights@z;scatter=np.einsum('n,ni,nj->ij',weights,z-mu,z-mu);raw=np.einsum('n,ni,nj->ij',weights,z,z)-np.outer(mu,mu);assert np.allclose(scatter,raw)
 scale=rng.uniform(.1,10);rr=rng.uniform(.1,20,10);assert np.allclose(rr/rr.sum(),(scale*rr)/(scale*rr).sum())
 perturb=rng.normal(size=(3,3));assert np.allclose(A@np.linalg.solve(A,perturb),perturb)
out={'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'explicitChecks':len(checks),'checks':checks,'randomTrials':1000,'checksPerTrial':3,'status':'passed','scope':'Author calculations and actual pinned API execution only; independent review remains required.','questionHashes':m['questionHashes']};(R/'audits/W07-L33-v2-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in['questionHashes','checks']},indent=2))
