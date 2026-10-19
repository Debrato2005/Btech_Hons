#!/usr/bin/env python3
"""Independent L38 arithmetic checks, not author code or a course training run."""
from fractions import Fraction as F
import math,random,json,datetime,pathlib
R=random.Random(381019); checks=[]
def check(name,condition,result):
 assert condition,name
 checks.append({'name':name,'passed':True,'result':result})
def softmax(q,t):
 if t<=0 or not math.isfinite(t) or not q or any(not math.isfinite(x) for x in q):raise ValueError('finite values, nonempty actions, positive finite temperature required')
 z=[math.exp((v-max(q))/t) for v in q];return [v/sum(z) for v in z]
def epsilon(n,e,g=0):
 if not isinstance(n,int) or n<1 or not 0<=e<=1 or not 0<=g<n:raise ValueError('invalid finite action count/probability/greedy index')
 p=[e/n]*n;p[g]+=1-e;return p
check('Q003 TD update',F(2)+F(1,5)*(F(1)+F(9,10)*5-2)==F(27,10),'target5.5,error3.5,updated2.7')
check('Q005 storage',10**9*100*4==400*10**9,{'bytes':400000000000,'decimalGB':400})
row=[1.9,6,3,5.2];rank=sorted(enumerate(row),key=lambda x:x[1],reverse=True)
check('Q007 greedy margin',rank[0][0]==1 and math.isclose(rank[0][1]-rank[1][1],.8),'Down;0.8')
check('Q008 cardinality',16**3*6==24576 and (16**3*6)//(8**3*6)==8,{'entries':24576,'factor':8})
check('Q013 weights and biases',sum(a*b+b for a,b in zip([3,4,4],[4,4,4]))==56,{'weights':44,'biases':12})
check('Q015 three greedy rows',[max(range(3),key=lambda j:r[j]) for r in [[.91,.20,.35],[.1,.55,.8],[-.9,.7,.6]]]==[0,2,1],['Forward','Turn','Stop'])
phi=2;trace=[]
for step,theta in enumerate([3,5,8],1):
 if step%3==0:phi=theta
 trace.append(phi)
check('Q030 hard-copy trace',trace==[2,2,8],trace)
check('Q031 beta convention',F(9,10)*2+F(1,10)*10==F(14,5),'2.8')
for beta in [F(0),F(1),F(3,10)]:
 old=F(2);theta=F(10);new=beta*old+(1-beta)*theta
 check(f'Q032 beta endpoint/recurrence {beta}',new-theta==beta*(old-theta),str(new))
check('Q033 target and error',F(1)+F(9,10)*5==F(11,2) and F(11,2)-F(43,10)==F(6,5),'5.5;1.2')
check('Q034 terminal mask',1+F(9,10)*(1-1)*5==1,'terminal y=1')
check('Q035 scalar gradient',F(43,10)-F(1,10)*(F(43,10)-F(11,2))==F(221,50),'4.42')
check('Q037 epsilon probabilities',all(math.isclose(a,b) for a,b in zip(epsilon(4,.2),[.85,.05,.05,.05])),epsilon(4,.2))
check('Q039 finite softmax',all(math.isclose(a,b) for a,b in zip(softmax([0,math.log(2)],1),[1/3,2/3])),softmax([0,math.log(2)],1))
check('Q040 high temperature',max(abs(x-1/3) for x in softmax([1,2,4],1e10))<1e-9,softmax([1,2,4],1e10))
check('Q040 unique low temperature',softmax([1,2,4],.001)==[0,0,1],softmax([1,2,4],.001))
check('Q042 low-temperature tie',softmax([5,5,1],.001)==[.5,.5,0],softmax([5,5,1],.001))
check('Q047 equal cell sides',F(12,40)==F(9,30)==F(3,10),'0.3m;0.3m')
zones=[max(abs(x),abs(y)) for x in range(-2,3) for y in range(-2,3)]
check('Q051 geometric ring count',[zones.count(k) for k in range(3)]==[1,8,16],[zones.count(k) for k in range(3)])
check('Q052 zone/diameter',5*F(3,10)==F(3,2) and 2*F(150,1000)==F(3,10),'1.5m;0.3m')
c={'Rg':500,'P4':-1,'P0':-300,'P3':-2,'P1':-100,'P2':-50};h=dict(c,P3=-4,P2=-2)
check('Q054 changed rows',[k for k in c if c[k]!=h[k]]==['P3','P2'],['P3','P2'])
check('Q055 source column distinction',c['P2']==-50 and h['P2']==-2,{'concourse':-50,'home':-2})
check('Q056 disjoint sum',c['Rg']+10*c['P4']+2*c['P3']==486,486)
check('Q057 immediate tradeoff',c['P3']==2*c['P4']==-2 and h['P3']==-4 and 2*h['P4']==-2,{'concourse':[-2,-2],'home':[-4,-2]})
y=h['P2']+F(9,10)*5
check('Q058 correct environment target',y==F(5,2) and y-1==F(3,2),'2.5;1.5')
check('Q065 zone penalties',[c['P'+str(i)] for i in range(3)]==[-300,-100,-50],[-300,-100,-50])
invalid=[lambda:softmax([1,2],0),lambda:softmax([1,2],-1),lambda:softmax([],1),lambda:softmax([math.inf],1),lambda:epsilon(0,.5),lambda:epsilon(2,-.1),lambda:epsilon(2,1.1),lambda:epsilon(2,.5,2)]
for f in invalid:
 try:f()
 except ValueError:pass
 else:raise AssertionError('domain accepted')
check('Helper invalid-domain checks',True,8)
for _ in range(1000):
 b=R.random();a=R.uniform(-20,20);t=R.uniform(-20,20);n=b*a+(1-b)*t
 assert math.isclose(n-t,b*(a-t),abs_tol=1e-12)
check('1000 varied soft-update contractions',True,1000)
for _ in range(1000):
 n=R.randrange(1,31);e=R.random();g=R.randrange(n);p=epsilon(n,e,g)
 assert math.isclose(sum(p),1) and all(0<=x<=1 for x in p) and p[g]>=max(p)-1e-12
check('1000 varied epsilon distributions',True,1000)
for _ in range(1000):
 q=[R.uniform(-20,20) for _ in range(R.randrange(1,15))];t=R.uniform(.1,10);c=R.uniform(-100,100)
 a=softmax(q,t);b=softmax([x+c for x in q],t)
 assert math.isclose(sum(a),1) and all(x>=0 for x in a) and max(abs(x-y) for x,y in zip(a,b))<1e-12
check('1000 varied stable-softmax shifts',True,1000)
for _ in range(1000):
 old=R.uniform(-100,100);r=R.uniform(-10,10);v=R.uniform(-100,100);eta=R.random();gamma=R.random();target=r+gamma*v
 updated=old+eta*(target-old)
 assert math.isclose(updated,(1-eta)*old+eta*target,abs_tol=1e-11)
 assert min(old,target)-1e-10<=updated<=max(old,target)+1e-10
check('1000 varied TD/identity-gradient convex updates',True,1000)
out={'reviewerId':'independent-reviewer-robotics-batches-v2','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceCodePresentInLecture':False,'trainedCaseStudyModelExecuted':False,'scope':'Independent arithmetic and specified toy algorithms only; not the unavailable research training system. Frozen question objects are never modified.','checkGroups':len(checks),'variedTrials':4000,'checks':checks}
pathlib.Path('audits/W08-L38-independent-computations.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checkGroups':len(checks),'variedTrials':4000,'passed':True}))
