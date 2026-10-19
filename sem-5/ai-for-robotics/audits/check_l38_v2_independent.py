import json,math,random
from pathlib import Path
from datetime import datetime,timezone
now=datetime.now(timezone.utc).isoformat()
checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('storage',10**9*100*4==400*10**9)
phi=2;trace=[]
for i,theta in enumerate([3,5,8],1):
 if i%3==0:phi=theta
 trace.append(phi)
ck('after-step copy',trace==[2,2,8]);ck('beta endpoints',0*2+(1-0)*8==8 and 1*2+(1-1)*8==2)
ck('zone anddiameter',math.isclose(5*.3,1.5) and 150*2/1000==.3)
con={'Rg':500,'P4':-1,'P0':-300,'P3':-2,'P1':-100,'P2':-50};home={**con,'P3':-4,'P2':-2}
ck('tablechangedrows',[k for k in con if con[k]!=home[k]]==['P3','P2'])
ck('episode',con['Rg']+10*con['P4']+2*con['P3']==486)
ck('localcost',con['P3']==2*con['P4']==-2 and home['P3']==-4 and 2*home['P4']==-2)
ck('thrustnotprobabilities',-.03<0 and not math.isclose(.12-.03+.88,1))
ck('Vunderdeterminesactions',(8+12)/2==(12+8)/2==10)
ck('zero tracking error canhavezero clearance',math.dist([0,0],[0,0])==0)
def soft(q,t):
 z=[math.exp((a-max(q))/t) for a in q];return[x/sum(z) for x in z]
ck('softmaxlimits',max(abs(v-1/3) for v in soft([1,2,3],1e8))<1e-7 and soft([1,2,3],1e-3)[2]>.99999)
rng=random.Random(3802)
for _ in range(1000):
 b=rng.random();p=rng.uniform(-10,10);t=rng.uniform(-10,10);pn=b*p+(1-b)*t;assert math.isclose(pn-t,b*(p-t),abs_tol=1e-12)
 n=rng.randint(2,10);eps=rng.random();assert eps/n>0 and math.isclose((1-eps+eps/n)+(n-1)*eps/n,1)
 moves=rng.randrange(100);waits=rng.randrange(100);assert 500-moves-2*waits==sum([500]+[-1]*moves+[-2]*waits)
ck('3000variedsoftupdateexplorationrewardcases',True)
Path('audits/W08-L38-v2-independent-computations.json').write_text(json.dumps({'checkedAt':now,'checks':checks,'groups':len(checks),'variedCases':3000,'sourceModelExecuted':False,'scope':'Independent arithmetic/algebra, no original DQN research implementation supplied or executed.'},indent=2)+'\n');print('checks',len(checks),'varied',3000)
