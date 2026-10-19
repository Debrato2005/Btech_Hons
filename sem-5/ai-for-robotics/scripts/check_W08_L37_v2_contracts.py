"""Independent source-derived calculations, before keyed review. Not a supplied notebook."""
from pathlib import Path
import math,random,json,datetime,hashlib,heapq
R=Path(__file__).resolve().parents[1];out=R/'audits/W08-L37-v2-contracts-independent-checks.json';assert not out.exists()
checks=[]
def check(label,actual,expected):
 assert actual==expected,(label,actual,expected);checks.append({'label':label,'actual':actual,'expected':expected})
def delta(a,b):return abs((a-b+180)%360-180)
def cost(w,e):return sum(a*b for a,b in zip(w,e))
check('Q047 explicitly nonblind independent full weighted sums',[cost((5,2,2),(10,20,30)),cost((5,2,2),(20,0,0))],[150,100])
check('Q047 omission-of-previous distractor',cost((5,2,0),(10,20,30)),90)
check('Q047 unweighted alternative',[sum((10,20,30)),sum((20,0,0))],[60,20])
check('Q039 circular separation',delta(175,-175),10)
check('Q074 full Cartesian product',20**6,64000000)
check('Q074 five-coordinate distractor',20**5,3200000)
check('Q016 closest-goal Bug1 candidate',min([('A',3,8),('B',4,2)],key=lambda x:x[1])[0],'A')
check('Q022 fixed-line/strict-progress candidates',[i for i,on_line,d in [('off',False,3),('far',True,9),('equal',True,8),('near',True,7)] if on_line and d<8],['near'])
check('Q055 opposite wheel speeds yield zero translation',(1+(-1))/2,0)
check('Q055 opposite wheel speeds yield nonzero heading rate',(1-(-1))/2,1)
# Source A* geometry reconstructed independently, using integer tenths to avoid rounding artifacts.
blocked={(0,0),(0,1),(0,2),(1,2),(2,2),(3,2)}
def dijkstra(obstacles):
 start=(4,4);d={start:0};todo=[(0,start)]
 while todo:
  dist,u=heapq.heappop(todo)
  if dist!=d[u]:continue
  for dr in [-1,0,1]:
   for dc in [-1,0,1]:
    if not(dr or dc):continue
    v=(u[0]+dr,u[1]+dc)
    if not all(0<=k<5 for k in v) or v in obstacles:continue
    if dr and dc and ((u[0]+dr,u[1]) in obstacles or (u[0],u[1]+dc) in obstacles):continue
    z=dist+(14 if dr and dc else 10)
    if z<d.get(v,10**9):d[v]=z;heapq.heappush(todo,(z,v))
 return d
d=dijkstra(blocked);check('p1133 rounded-diagonal shortest g(goal)',d[(2,0)],54);check('p1133 actual start g',d[(4,4)],0);check('p1136 obstacle-update detour g(goal)',dijkstra(blocked|{(3,1)})[(2,0)],60)
check('p1134 octile ignores obstacles',14*2+10*2,48)
r=random.Random(3702);cases=1000
for _ in range(cases):
 w=[r.randint(1,20) for _ in range(3)];es=[[r.randint(0,180) for _ in range(3)] for _ in range(5)];s=r.randint(1,50)
 a=sorted(range(5),key=lambda i:cost(w,es[i]));b=sorted(range(5),key=lambda i:cost([s*x for x in w],es[i]));assert a==b
 theta,phi=r.uniform(-1080,1080),r.uniform(-1080,1080);assert 0<=delta(theta,phi)<=180;assert math.isclose(delta(theta,phi),delta(phi,theta),abs_tol=1e-9)
 m,n=r.randint(1,20),r.randint(0,8);assert m**(n+1)==m*m**n
 # Quadratic attraction + two differentiable synthetic repulsions: verify gradient linearity.
 x=r.uniform(-4,4);eps=1e-6
 fs=[lambda z:(z-3)**2/2,lambda z:2*(z+1)**2,lambda z:.5*(z-2)**2]
 total=lambda z:sum(f(z) for f in fs)
 numerical=-(total(x+eps)-total(x-eps))/(2*eps);analytic=-(x-3)-4*(x+1)-(x-2)
 assert math.isclose(numerical,analytic,rel_tol=1e-6,abs_tol=1e-6)
result={'reviewerId':'robotics-contracts-reviewer-L37-v2','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exactAssertions':len(checks),'variedCases':cases,'variedAssertions':cases*5,'checks':checks,'sourceRuntimeStatus':'No executable code or notebook is printed or linked in the38 inspected L37 pages. This is a reviewer-authored implementation of the shown arithmetic, grid graph and conceptual invariants, not a claim to execute source code.','Q047Exposure':'The binding manifest disclosed the keyed costs before solving; all computations are independent but Q047 is explicitly nonblind.'}
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
