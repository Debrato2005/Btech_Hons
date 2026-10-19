"""Independent closure checks; current author objects are not imported."""
from fractions import Fraction as F
from pathlib import Path
import datetime,json,hashlib
import numpy as np
from machinevisiontoolbox import Image
R=Path(__file__).resolve().parents[1];hist=[1,1,2,4];N=sum(hist);mu=sum(F(i*n,N) for i,n in enumerate(hist));scores=[];within=[];details=[]
for t in range(3):
 n0=sum(hist[:t+1]);n1=N-n0;w0=F(n0,N);w1=F(n1,N);m0=sum(F(i*hist[i],n0) for i in range(t+1));m1=sum(F(i*hist[i],n1) for i in range(t+1,4));v0=sum(F(hist[i],n0)*(i-m0)**2 for i in range(t+1));v1=sum(F(hist[i],n1)*(i-m1)**2 for i in range(t+1,4));scores.append(w0*w1*(m0-m1)**2);within.append(w0*v0+w1*v1);details.append(dict(t=t,w0=str(w0),w1=str(w1),mu0=str(m0),mu1=str(m1),between=str(scores[-1]),within=str(within[-1])))
assert scores==[F(289,448),F(169,192),F(49,64)];assert within==[F(13,28),F(11,48),F(11,32)];assert max(range(3),key=scores.__getitem__)==1;total=sum(F(hist[i],N)*(i-mu)**2 for i in range(4));assert all(a+b==total==F(71,64) for a,b in zip(scores,within))
a=np.zeros((12,18),dtype=np.uint8);a[3:8,2:7]=255;a[3:8,7:12]=255
labels,n=Image(a).labels_binary();assert n==2;assert len(np.unique(labels.A[a>0]))==1
b=np.zeros((12,18),dtype=np.uint8);b[3:8,2:7]=255;b[3:8,9:14]=255
labels2,n2=Image(b).labels_binary();assert n2==3;assert len(np.unique(labels2.A[b>0]))==2
out=R/'audits/W07-L33-final-five-contracts-checks.json';assert not out.exists();res=dict(completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),assertions=8,otsu=details,totalVariance=str(total),touchingLabelsIncludingBackground=n,separatedLabelsIncludingBackground=n2,scope='Fresh synthetic checks of the declared histogram and touching-region premise; not a rerun of the original slide images. Prior independent original-image and API evidence remains separately preserved.');out.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
