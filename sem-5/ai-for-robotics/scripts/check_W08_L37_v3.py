#!/usr/bin/env python3
"""Author-only checks for revised L37 toy examples, not robot or learning execution."""
import json,math,random
from fractions import Fraction as F
from pathlib import Path
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,condition):assert condition,name;checks.append(name)
# Exact boundary geometry, including the first goal-line crossing B.
points=[(2,0),(2,-2),(6,-2),(6,0),(6,1),(10,1),(10,4),(2,4),(2,0)];goal=(12,0)
def dist2(p,q):return sum((F(a)-F(b))**2 for a,b in zip(p,q))
lengths=[abs(b[0]-a[0])+abs(b[1]-a[1])for a,b in zip(points,points[1:])];cum=[0]
for d in lengths:cum.append(cum[-1]+d)
check('Bug polygon perimeter and event arclengths',sum(lengths)==28 and cum[3]==8 and cum[5]==13)
minima=[]
for a,b in zip(points,points[1:]):
 v=[F(b[i]-a[i])for i in range(2)];t=sum(F(goal[i]-a[i])*v[i]for i in range(2))/sum(x*x for x in v);t=max(F(0),min(F(1),t));p=tuple(F(a[i])+t*v[i]for i in range(2));minima.append((dist2(p,goal),p))
check('Bug unique closest boundary location',min(d for d,p in minima)==5 and {p for d,p in minima if d==5}=={(F(10),F(1))})
check('Bug hit and crossing goal distances',dist2(points[0],goal)==100 and dist2(points[3],goal)==36)
def inside(p):
 x,y=p;return(2<x<6 and -2<y<4)or(6<=x<10 and 1<y<4)
check('Bug outgoing line blocked at hit and free at B',inside((F(201,100),F(0)))and not inside((F(601,100),F(0))))
check('Bug selected leave directions locally free',not inside((F(1001,100),F(199,200))))
check('Bug1 complete survey plus shortest return',28+min(13,28-13)==41)
check('Bug2 first eligible crossing and boundary travel',cum[3]==8 and math.sqrt(dist2(points[3],goal))<math.sqrt(dist2(points[0],goal)))
check('Bug distractor totals',28+8==36 and 13!=41 and 28+15==43)
angles=list(range(0,360,30));densities=[1,1,5,1,2,1,2,7,6,5,2,1]
def runs(free):
 n=len(free)
 if all(free):return[list(range(n))]
 result=[]
 for i in range(n):
  if free[i]and not free[(i-1)%n]:
   r=[];j=i
   while free[j]:r.append(j);j=(j+1)%n
   result.append(r)
 return result
def wrap(a,b):return abs((a-b+180)%360-180)
def mid(r):return(angles[r[0]]+30*(len(r)-1)/2)%360
def cost(a):return 5*wrap(a,20)+2*wrap(a,150)+2*wrap(a,150)
free=[h<5 and a!=90 for a,h in zip(angles,densities)];rr=[r for r in runs(free)if len(r)>=3];candidate=[mid(r)for r in rr];costs={x:cost(x)for x in candidate}
check('VFH threshold equality and mask', [a for a,f in zip(angles,free)if f]==[0,30,120,150,180,300,330])
check('VFH circular valleys',[[angles[i]for i in r]for r in rr]==[[120,150,180],[300,330,0,30]])
check('VFH center candidates and exact weighted costs',costs=={150.0:650.0,345.0:835.0})
check('VFH shared reference consistency',wrap(345,150)==165 and wrap(150,150)==0 and wrap(345,20)==35 and wrap(150,20)==130)
check('VFH selected feasible heading',min(candidate,key=lambda a:(cost(a),a))==150)
wrongmask=runs([h<5 for h in densities]);check('VFH omitted-mask distractor',[[angles[i]for i in r]for r in wrongmask]==[[90,120,150,180],[300,330,0,30]]and cost(135)==635)
wrong_equal=runs([h<=5 and a!=90 for a,h in zip(angles,densities)]);check('VFH inclusive-free distractor',[[angles[i]for i in r]for r in wrong_equal]==[[120,150,180],[270,300,330,0,30,60]])
check('VFH goal-only distractor',5*wrap(345,20)==175 and 5*wrap(150,20)==650)
# Independent circular metric and positive-scale geometry invariants.
rng=random.Random(3703)
for _ in range(1000):
 a,b,c=[rng.randrange(-2000,2001)for _ in range(3)]
 alternative=math.degrees(math.acos(max(-1,min(1,math.cos(math.radians(a-b))))))
 assert abs(wrap(a,b)-alternative)<1e-6
 assert wrap(a,c)<=wrap(a,b)+wrap(b,c)
 assert wrap(a+360*rng.randint(-9,9),b)==wrap(a,b)
checks.append('1000 angle cases and 3000 independent assertions')
widths=[2*r*math.sin(math.radians(20)/2)for r in [2,4]]
check('Gap chord widths and robot clearance',abs(widths[0]-.6945927106677213)<1e-12 and abs(widths[1]-1.3891854213354426)<1e-12 and widths[0]<.6+2*.1<widths[1])
check('Gap radius and full-angle distractors',all(r*math.sin(math.radians(10))<.8 for r in [2,4])and all(2*r*math.sin(math.radians(20))>.8 for r in [2,4]))
check('Gap omitted-margin distractor',all(w>.6 for w in widths))
check('Threshold code boundary',[h>=5 for h in [4.9,5.0,5.1]]==[False,True,True])
data={'authorId':'L37-repair-author-20261019','independentVerification':False,'passed':True,'checkGroups':len(checks),'checks':checks,'variedCases':1000,'variedAssertions':3000,'bug':{'boundaryPoints':points,'segmentLengths':lengths,'cumulativeLengths':cum,'goal':goal,'closestPoint':[10,1],'closestSquaredGoalDistance':5,'Bug1BoundaryDistance':41,'Bug2LeavePoint':[6,0],'Bug2BoundaryDistance':8},'vfh':{'angles':angles,'densities':densities,'free':free,'valleys':[[angles[i]for i in r]for r in rr],'candidates':candidate,'costs':costs,'selected':150},'chordWidths':widths,'noSourceCodeExecutionClaim':'All exercises are author-supplied deterministic examples derived from slide rules; no robot, learning or original notebook execution is claimed.'}
(R/'audits/W08-L37-v3-author-computations.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(len(checks),'groups and 1000 cases passed')
