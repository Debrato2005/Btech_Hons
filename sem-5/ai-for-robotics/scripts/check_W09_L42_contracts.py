"""Independent reconstruction from inspected source pixels, before author keys.
The slide contains language-neutral pseudocode, not an executable supplied program.
This implements its arithmetic and a declared fixed-size, re-evaluated elite loop.
"""
from pathlib import Path
import math,json,hashlib,datetime,random,itertools
from fractions import Fraction as F
R=Path(__file__).resolve().parents[1]
Obs={(1,1),(1,2),(2,2),(2,4),(3,2),(4,3)}
def decode(w):
 p=[(0,0)]
 for r,c in [*w,(5,5)]:
  rr,cc=p[-1]
  while cc!=c:cc+=1 if cc<c else -1;p.append((rr,cc))
  while rr!=r:rr+=1 if rr<r else -1;p.append((rr,cc))
 return p
def evaluate(w):
 p=decode(w);d=[(b[0]-a[0],b[1]-a[1]) for a,b in zip(p,p[1:])]
 hits=[v for v in p[1:] if v in Obs];t=sum(a!=b for a,b in zip(d,d[1:]));l=len(d);c=l+10*len(hits)+t
 return dict(path=p,length=l,hits=hits,turns=t,cost=c,fitness=F(1,1+c))
P=[[(0,3),(4,5)],[(2,1),(5,3)],[(0,2),(3,4)],[(3,0),(5,4)],[(1,3),(4,4)],[(2,0),(5,2)]]
checks=[]
def check(label,expr):
 assert expr,label;checks.append(label)
e=[evaluate(p) for p in P]
for i,(hits,t,c) in enumerate([([],1,11),([(1,1),(2,2),(4,3)],4,44),([(2,4)],3,23),([(3,2)],3,23),([(2,4)],5,25),([(2,2),(3,2)],3,33)]):
 check(f'P{i+1} full trace',e[i]['length']==10 and e[i]['hits']==hits and e[i]['turns']==t and e[i]['cost']==c)
rounded=[F(s) for s in ['.0833','.0222','.0417','.0417','.0385','.0294']]
check('Rounded fitness sum',sum(rounded)==F('.2568'))
check('P1 roulette',round(float(rounded[0]/sum(rounded)),4)==.3244)
bounds=[.3244,.4109,.5733,.7357,.8856,1];draws=[.15,.35,.50,.60,.72,.90]
pool=[next(i+1 for i,b in enumerate(bounds) if u<b) for u in draws]
check('Six roulette draws',pool==[1,2,3,4,4,6])
C=[]
for i,j in [(0,2),(3,5),(1,3)]:C.extend([[P[i][0],P[j][1]],[P[j][0],P[i][1]]])
check('All six crossovers',C==[[(0,3),(3,4)],[(0,2),(4,5)],[(3,0),(5,2)],[(2,0),(5,4)],[(2,1),(5,4)],[(3,0),(5,3)]])
unmut=evaluate(C[0]);C[0]=[(0,3),(3,5)];ce=[evaluate(c) for c in C]
check('Mutation doubles fitness',ce[0]['fitness']==2*unmut['fitness'])
check('Six child costs', [v['cost'] for v in ce]==[11,11,23,33,44,33])
check('Same phenotype distinct genotype',C[0]!=C[1] and ce[0]['path']==ce[1]['path'])
means=[sum(v['fitness'] for v in ee)/6 for ee in [e,ce]]
check('Mean fitness corrected',round(float(means[1]),4)==.0482 and means[1]>means[0])
check('Seven comparison rows do not yield displayed 0.0473',round(float((sum(v['fitness'] for v in ce)+unmut['fitness'])/7),4)==.0473)
free=[(r,c) for r in range(6) for c in range(6) if (r,c) not in Obs]
allcosts=[evaluate(w)['cost'] for w in itertools.product(free,repeat=2)]
check('All 900 free-waypoint chromosomes respect 11 lower bound',len(allcosts)==900 and min(allcosts)==11)
def energy(a,b):return -4*math.sin(a)-6*math.cos(a)-4*math.sin(b)-2*math.cos(b)
def fitness_deg(a,b):return -energy(math.radians(a),math.radians(b))-7
angles=math.atan2(4,6),math.atan2(4,2)
check('Stationary angles and corrected radians',abs(angles[0]-.5880026035)<1e-10 and abs(math.degrees(angles[1])-63.43494882)<1e-8)
check('Global continuous lower bound',abs(energy(*angles)+math.sqrt(52)+math.sqrt(20))<1e-12)
check('Positive diagonal Hessian',all(x>0 for x in [4*math.sin(angles[0])+6*math.cos(angles[0]),4*math.sin(angles[1])+2*math.cos(angles[1])]))
grid=[(energy(math.radians(a),math.radians(b)),a,b) for a in range(0,91,6) for b in range(0,91,6)]
check('All 256 binary angle configurations',min(grid)[1:]==(36,66))
check('Negative shifted score counterexample',abs(fitness_deg(90,0)+1)<1e-12)
check('Table Q058 rounding',round(fitness_deg(36,60),2)==4.67)
check('Four other fitness corrections',[round(fitness_deg(*x),2) for x in [(12,6),(6,30),(84,48),(42,72)]]==[2.11,3.12,1.92,4.56])
check('Timing',50*100*2/1000==10)
check('Expected copies',6*F('.3244')==F('1.9464'))
check('Independent mutation',1-F('.9')**2==F('.19'))
# Re-evaluated fixed-size elite loop uses reviewer-declared repair/randomness, not source outputs.
rng=random.Random(421029);pop=P[:];best=[]
for gen in range(20):
 scored=[evaluate(w) for w in pop];elite=pop[min(range(6),key=lambda i:scored[i]['cost'])];best.append(evaluate(elite)['cost']);weights=[float(v['fitness']) for v in scored];new=[elite]
 while len(new)<6:
  a,b=rng.choices(pop,weights,k=2);child=[a[0],b[1]]
  for j in range(2):
   if rng.random()<.1:child[j]=(rng.randrange(6),rng.randrange(6))
   if child[j] in Obs:child[j]=min(free,key=lambda z:(abs(z[0]-child[j][0])+abs(z[1]-child[j][1]),z))
  new.append(child)
 pop=new
check('Declared elite implementation retains size and evaluated optimum',len(pop)==6 and all(v==11 for v in best) and min(evaluate(w)['cost'] for w in pop)==11)
# Finite-difference, bounds, and decoder invariants across varied inputs.
for i in range(1000):
 a,b=[rng.random()*math.pi/2 for _ in range(2)];h=1e-6
 g=[-4*math.cos(a)+6*math.sin(a),-4*math.cos(b)+2*math.sin(b)]
 assert abs((energy(a+h,b)-energy(a-h,b))/(2*h)-g[0])<1e-8
 assert abs((energy(a,b+h)-energy(a,b-h))/(2*h)-g[1])<1e-8
 assert energy(a,b)>=energy(*angles)-1e-12
 w=[rng.choice(free),rng.choice(free)];v=evaluate(w);p=v['path']
 assert v['length']==sum(abs(y[0]-x[0])+abs(y[1]-x[1]) for x,y in zip([(0,0),*w],[*w,(5,5)]))
 assert p[0]==(0,0) and p[-1]==(5,5) and all(abs(y[0]-x[0])+abs(y[1]-x[1])==1 for x,y in zip(p,p[1:]))
out=dict(completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),codeScope=__doc__,explicitChecks=checks,explicitCount=len(checks),enumeratedFreeWaypointChromosomes=900,enumeratedAnglePairs=256,variedCases=1000,variedAssertions=5000,initial=e,children=ce,means=means,pendulumAnglesRadians=angles,pendulumMinimum=energy(*angles),binaryMinimum=min(grid),sourceClaimDifferences=['P2 fraction 1/12 should be 1/45','P1 appears once in actual mating pool','Mean six-child fitness is 0.0482; printed 0.0473 includes the comparison row','Mutation not necessary for a best child because C2 already best','C5 ties old P2, not another new child; both parents already infeasible','Displayed gradient is negative of actual energy gradient; stationary roots survive','0.558 rad is a typo for 0.588','-Pi=8 at zero is not the maximum','Shift F=-Pi-7 permits negative weights','Multiple binary-population fitness entries have arithmetic/rounding errors'],scriptSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
f=R/'audits/W09-L42-contracts-independent-checks.json';assert not f.exists();f.write_text(json.dumps(out,indent=2,default=lambda x:str(x))+'\n');print(json.dumps({k:out[k] for k in ['explicitCount','variedCases','means','pendulumMinimum','binaryMinimum']},default=str))
