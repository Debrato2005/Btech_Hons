"""Independent source-derived checks; never imports author objects or checks."""
from fractions import Fraction as F
import json, math, random, hashlib
from pathlib import Path
from datetime import datetime, timezone
checks=[]
def ck(name, value):
 assert value,name
 checks.append(name)
def tri(x,a,b,c):
 return max(0., min((x-a)/(b-a),(c-x)/(c-b)))
def wa(w,z):
 if sum(w)<=0: raise ValueError('zero support')
 return sum(a*b for a,b in zip(w,z))/sum(w)
ck('literal thermostat boundary', not(23.9>=24) and 24>=24)
ck('trapezoid right flank', (10-8)/(10-6)==.5)
ck('triangle symmetric pair', tri(2,0,5,10)==tri(8,0,5,10)==.4)
ck('Gaussian sigma offset', math.isclose(math.exp(-.5),.6065306597126334))
ck('min AND/max OR', min(.27,.65)==.27 and max(.27,.65)==.65)
ck('clipping and maximum not product or sum', min(.4,.7)==.4 and max(.4,.6)==.6)
ck('cooling 4 by 3', 4*3==12)
ck('80F equal overlap', tri(80,65,75,85)==tri(80,75,85,95)==.5)
ck('Hot 78 conflict', tri(78,75,85,95)==.3 and tri(78,75,85,95)!=.27)
ck('Humid 70 conflict', math.isclose(tri(70,40,60,90),2/3) and tri(70,40,60,90)!=.65)
rows=[["F","F","M"],["F","M","M"],["M","S","S"],["S","O","O"]]
tg=[0,.27,.7,0];hg=[0,.65,0]
fires=[(i*3+j+1,min(tg[i],hg[j]),rows[i][j]) for i in range(4) for j in range(3) if min(tg[i],hg[j])>0]
ck('all twelve cooling rules trace',fires==[(5,.27,'M'),(8,.65,'S')])
weighted=wa([.65,.27],[20,50]);ck('weighted cooling',math.isclose(weighted,28.804347826086953))
# Exact integration of maximum of two clipped triangles. Independently derived switches:
# slow rises to .65 at13, leaves cap30.5, falls to medium .27 at41.9;
# medium leaves cap71.9, falls to0 at80. Its earlier rise remains below Slow.
segments=[(F(0),F(13),F(1,20),F(0)),(F(13),F(61,2),F(0),F(65,100)),(F(61,2),F(419,10),F(-1,30),F(5,3)),(F(419,10),F(719,10),F(0),F(27,100)),(F(719,10),F(80),F(-1,30),F(8,3))]
area=sum(a*(r*r-l*l)/2+b*(r-l) for l,r,a,b in segments)
moment=sum(a*(r**3-l**3)/3+b*(r*r-l*l)/2 for l,r,a,b in segments)
centroid=moment/area
ck('exact centroid',round(float(centroid),4)==33.6981)
# Independent numerical midpoint sum for continuous clipped max envelope.
n=200000;dx=80/n
s=m=0.
for i in range(n):
 x=(i+.5)*dx;y=max(min(.65,tri(x,0,20,50)),min(.27,tri(x,20,50,80)))
 s+=y*dx;m+=x*y*dx
ck('dense numerical centroid agrees with exact piecewise integration',abs(m/s-float(centroid))<1e-7)
ck('singleton and area centroid differ',abs(weighted-float(centroid))>4)
ck('common weight scaling',math.isclose(wa([.325,.135],[20,50]),weighted))
try: wa([0,0],[20,50]);ck('zero support rejected',False)
except ValueError: ck('zero support rejected',True)
ck('repeated consequent max cap',max(.3,.6)==.6)
ck('robot rule count',5*4==20)
robot=[['VS','S','M','M'],['VS','S','M','F'],['S','M','F','VF'],['VS','S','M','F'],['VS','VS','S','M']]
ck('Level row',robot[2]==['S','M','F','VF'])
ck('positive and negative equality but extreme asymmetry',robot[1]==robot[3] and robot[0]!=robot[4])
ck('terrain half overlap',tri(30,20,40,60)==max(0,min(1,(40-30)/20))==.5)
caps={}
for row,sw in [(1,.95),(0,.05)]:
 for col,tw in [(2,.5),(3,.5)]:
  label=robot[row][col];caps[label]=max(caps.get(label,0),min(sw,tw))
ck('four-rule robot trace',caps=={'M':.5,'F':.5})
ck('robot weighted speed',wa([caps['M'],caps['F']],[10,15])==12.5)
ck('rounding convention half-up',math.floor(12.5+.5)==13)
ck('source trend need not strictly change at each adjacent label',robot[0][2]==robot[0][3])
rng=random.Random(401241)
for _ in range(1000):
 a,b=sorted([rng.uniform(-100,100),rng.uniform(-100,100)]);w=[rng.random()+1e-6,rng.random()+1e-6];v=wa(w,[a,b]);c=10**rng.uniform(-4,4)
 assert a<=v<=b and math.isclose(v,wa([z*c for z in w],[a,b]),rel_tol=1e-9,abs_tol=1e-9)
 x=rng.uniform(-10,20);y=tri(x,0,5,10);assert 0<=y<=1
 alpha,beta=rng.random(),rng.random();v=rng.random();assert math.isclose(max(min(alpha,v),min(beta,v)),min(max(alpha,beta),v))
 # Relabeling grades does not make membership a probability distribution.
 z=rng.uniform(.001,1);assert min(z,z)==max(z,z)==z
ck('4000 varied weighted/triangle/cap/idempotence checks',True)
out={'reviewerId':'independent-reviewer-robotics-batches-v2','completedAt':datetime.now(timezone.utc).isoformat(),'checks':checks,'checkGroups':len(checks),'variedCases':4000,'weightedCooling':weighted,'centroid':{'exactFraction':str(centroid),'value':float(centroid),'area':str(area),'moment':str(moment),'segments':[list(map(str,s)) for s in segments],'numericalCrosscheck':m/s},'robotSpeed':12.5,'sourceProgramExecuted':False,'sourceProgramLimitation':'Slides show plotted outputs and name tools, but supply no original implementation. This executes an independently specified reconstruction only.','authorArtifactsRead':False}
Path('audits/W08-L40-v2-independent-computations.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
