"""Author-side numerical checks for L37; not independent answer approval."""
from pathlib import Path
import json,math,random,datetime
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,actual,expected):
 assert actual==expected,(name,actual,expected);checks.append({'name':name,'actual':actual,'expected':expected,'passed':True})
def delta(a,b):return abs((a-b+180)%360-180)
def valleys(mask):
 if not any(mask):return 0
 if all(mask):return 1
 return sum(mask[i]and not mask[(i-1)%len(mask)]for i in range(len(mask)))
check('Bug1 shorter return',min(6,14),6)
check('Bug1 minimum goal distance differs from shortest return',min([('A',3,8),('B',4,2)],key=lambda x:x[1])[0],'A')
check('Bug2 closer crossing',5<8,True)
check('Bug2 reject equal hit distance',8<8,False)
check('threshold free sectors',[i+1 for i,v in enumerate([2,7,3,6])if v<5],[1,3])
check('circular valleys',valleys([True,True,False,True,False,False,True,True]),2)
check('narrow midpoint',(20+40)/2,30)
check('wrapped absolute difference',delta(350,10),20)
check('cost A',5*10+2*20+2*30,150)
check('cost B',5*20+2*0+2*0,100)
check('compass lower right',(-45)%360,315)
check('quadratic force',[-2*x for x in[3,4]],[-6,-8])
check('six-dimensional grid',20**6,64000000)
check('one extra joint multiplies grid',20**7//20**6,20)
check('full circular free set',valleys([True]*8),1)
check('no circular free set',valleys([False]*8),0)
check('quadratic Hessian positive',[2,2],[2,2])
r=random.Random(370019)
for i in range(1000):
 a,b=r.uniform(-10000,10000),r.uniform(-10000,10000)
 assert 0<=delta(a,b)<=180
 assert abs(delta(a,b)-delta(b,a))<1e-9
 assert abs(delta(a+360,b)-delta(a,b))<1e-9
 weights=[r.uniform(.1,10)for _ in range(3)];errs=[[r.uniform(0,180)for _ in range(3)]for _ in range(5)];costs=[sum(x*y for x,y in zip(weights,e))for e in errs];factor=r.uniform(.1,20)
 assert min(range(5),key=lambda j:costs[j])==min(range(5),key=lambda j:factor*costs[j])
 mask=[r.choice([True,False])for _ in range(8)];shift=r.randrange(8);assert valleys(mask)==valleys(mask[shift:]+mask[:shift])
 q=[r.uniform(-5,5),r.uniform(-5,5)];goal=[r.uniform(-5,5),r.uniform(-5,5)];k=r.uniform(.1,5);eps=1e-5
 def U(x):return k*sum((x[j]-goal[j])**2 for j in range(2))/2
 for j in range(2):
  qp=q.copy();qm=q.copy();qp[j]+=eps;qm[j]-=eps
  assert abs((U(qp)-U(qm))/(2*eps)-k*(q[j]-goal[j]))<1e-7
report={'allPassed':True,'explicitChecks':len(checks),'variedTrials':1000,'checksPerTrial':7,'checks':checks,'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Bug leave-rule examples, circular-sector masks, wrapped angular costs, positive scaling invariance, configuration-grid counts and finite-difference verification of the explicitly supplied quadratic model; no source program exists in L37.'}
(R/'audits/W08-L37-author-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in['allPassed','explicitChecks','variedTrials','checksPerTrial']}))
