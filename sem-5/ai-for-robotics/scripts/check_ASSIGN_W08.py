from assignment_second_half_common import *
from fractions import Fraction as F
import heapq,random,sys
checks=[]
def ck(n,v):assert v,n;checks.append(n)
edges=[('A','B',5),('A','C',2),('B','D',6),('B','E',3),('C','F',4),('D','E',2),('D','G',6),('E','F',1),('F','G',3)]
g={x:[]for x in 'ABCDEFG'}
for a,b,c in edges:g[a].append((b,c));g[b].append((a,c))
pq=[(0,'A',['A'])];best={'A':0};trace=[]
while pq:
 d,u,path=heapq.heappop(pq)
 if d!=best[u]:continue
 trace.append((u,d))
 if u=='E':break
 for v,c in g[u]:
  if d+c<best.get(v,10**8):best[v]=d+c;heapq.heappush(pq,(d+c,v,path+[v]))
ck('UCS exact removal trace',trace==[('A',0),('C',2),('B',5),('F',6),('E',7)])
ck('UCS returned path and cost',path==['A','C','F','E'] and d==7)
ck('distractor route costs',[5+3,5+6+2,2+4+3+6+2]==[8,13,17])
vals={'A':(F(4),F(2)),'B':(F(3),F('2.4')),'C':(F(1),F('4.8'))}
ck('Astar/UCS/greedy triple',(min(vals,key=lambda n:sum(vals[n])),min(vals,key=lambda n:vals[n][0]),min(vals,key=lambda n:vals[n][1]))==('B','C','A'))
ck('target and residual',(F(1)+F('.9')*5,F(1)+F('.9')*5-F('4.3'))==(F('5.5'),F('1.2')))
ck('online-value distractor',F(1)+F('.9')*F('4.3')==F('4.87'))
ck('terminal masking',F(1)+F('.9')*(1-1)*5==1)
ck('clock conversion',3*10**8*F(2,10**6)==600)
ck('singleton output',(F('.7')*20+F('.3')*60)/(F('.7')+F('.3'))==32)
ck('swapped singleton distractor',F('.3')*20+F('.7')*60==48)
ck('Bug0 recurrence',['H','L','H','L','H']==['H'if i%2==0 else'L'for i in range(5)])
rng=random.Random(808);cnt=0
for _ in range(1000):
 a=F(rng.randint(1,100),100);b=F(rng.randint(1,100),100);x=rng.randint(0,100);y=rng.randint(0,100)
 z=(a*x+b*y)/(a+b);assert min(x,y)<=z<=max(x,y);cnt+=1
 k=rng.randint(1,30);assert (k*a*x+k*b*y)/(k*a+k*b)==z;cnt+=1
 r=F(rng.randint(-100,100),10);gamma=F(rng.randint(0,100),100);v=F(rng.randint(-100,100),10)
 assert r+gamma*(1-1)*v==r;cnt+=1
 assert r+0*v==r;cnt+=1
out=dict(role='Author checks, not independent review',checkedAt=NOW(),pythonExecutable=sys.executable,checks=checks,variedCases=1000,variedAssertions=cnt,questionHashes={q['id']:qhash(q)for q in json.loads((ROOT/'data/question-batches/ASSIGN-W08.json').read_text())['questions']})
dump('audits/ASSIGN-W08-author-checks.json',out);print(len(checks),'groups',cnt,'varied assertions')
