"""Independent exact arithmetic and graph checks for frozen L03 questions."""
from fractions import Fraction as F
from math import comb,log2,sqrt,isclose,cos,pi
from collections import defaultdict,deque
import json,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name,actual,expected):
 ok=isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-12) if isinstance(actual,float) else actual==expected
 assert ok,(name,actual,expected)
 checks.append({'name':name,'actual':str(actual),'expected':str(expected),'passed':True})
check('98-Q02 componentwise vector arithmetic',tuple(2*a+b for a,b in zip((1,-2),(3,4))),(5,0))
check('98-Q03 degree dot product',2*3*cos(pi/3),3)
check('98-Q04 orthogonal dot product',2*3*cos(pi/2),0)
check('98-Q05 squared norm',3**2+4**2,25)
check('98-Q05 norm',sqrt(25),5)
S=((0,-2,0),(2,0,0),(0,0,0));P=(3,0,0)
check('100-Q02 skew matrix product',tuple(sum(a*b for a,b in zip(row,P)) for row in S),(0,6,0))
check('100-Q01 skew antisymmetry',all(S[i][j]==-S[j][i] for i in range(3) for j in range(3)),True)
check('101-Q02 determinant',1*4-2*2,0)
check('101-Q02 row dependence',tuple(2*a for a in (1,2)),(2,4))
check('102-Q01 eigen equation',(2*1,3*0),(2,0))
check('103-Q01 gradient at1,2',(6*1+2*2,2*1+2*2),(10,6))
check('104-Q01 derivative at0',((0,1),(0,2)),((2*0,cos(0)),(0,2)))
check('105-Q01 normalization',sum([F(1,10),F(2,10),F(3,10),F(4,10)]),F(1))
check('105-Q01 missing probability mass',sum([F(2,10)]*4),F(4,5))
check('105-Q03 two disjoint state probabilities',F(1,4)+F(1,4),F(1,2))
check('106-Q01 Bayes',F(8,10)*F(2,10)/F(4,10),F(2,5))
check('107-Q02 expectation',10*F(3,10)-2*F(7,10),F(8,5))
check('107-Q04 density normalization',F(2,2)*(1**2-0**2),F(1))
check('107-Q04 polynomial integral mean',F(2,3)*(1**3-0**3),F(2,3))
check('108-Q02 binomial',comb(3,2)*F(4,5)**2*F(1,5),F(48,125))
check('108-Q02 exactly versus at least two',F(48,125)+F(4,5)**3,F(112,125))
check('108-Q04 peak ratio',1/(2*sqrt(2*pi))/(1/sqrt(2*pi)),.5)
check('109-Q01 MLE selection',max([(F(6,10),1),(F(5,10),2)])[1],1)
check('109-Q01 MAP selection',max([(F(6,10)*F(2,10),1),(F(5,10)*F(8,10),2)])[1],2)
check('111-Q01 fair entropy',-sum(p*log2(p) for p in [.5,.5]),1)
check('111-Q02 certain entropy',-sum(p*log2(p) for p in [1,0] if p),0)
A=((0,1),(-2,-3));x=(1,2);B=(0,1);u=4
check('112-Q02 state derivative',tuple(sum(a*b for a,b in zip(row,x))+B[i]*u for i,row in enumerate(A)),(2,-4))
check('112-Q03 output selection',1*3+0*9,3)
check('113-Q04 path sum',sum([4,1,3,1]),9)
check('114-Q01 green route cost',sum([2,3,1]),6)
check('114-Q01 upper route distractor',sum([4,5,2]),11)
check('114-Q01 via Dock2 distractor',sum([4,1,3,1]),9)
edges='SA SB AC AD BD BE CF DF EH FG HG'.split();adj=defaultdict(list)
for a,b in edges:adj[a].append(b);adj[b].append(a)
queue=deque('S');seen={'S'};order=[]
while queue:
 n=queue.popleft();order.append(n)
 if n=='G':break
 for child in sorted(adj[n]):
  if child not in seen:seen.add(child);queue.append(child)
check('115-Q04 BFS dequeue sequence',','.join(order),'S,A,B,C,D,E,F,H,G')
seen=set()
def dfs(n,path):
 seen.add(n);path=path+[n]
 if n=='G':return path
 for child in sorted(adj[n]):
  if child not in seen:
   found=dfs(child,path)
   if found:return found
check('116-Q03 DFS first path',','.join(dfs('S',[])),'S,A,C,F,D,B,E,H,G')
check('116-Q04 DFS versus BFS edges',(len('SACFDBEHG')-1,len('SACFG')-1),(8,4))
check('118-Q01 weighted gain',1-(F(1,4)*0+F(3,4)*F(8,10)),F(2,5))
def force(glass,thick):return 'low' if glass or not thick else 'high'
check('118-Q03 all four defined branches',[force(g,t) for g,t in [(True,True),(True,False),(False,True),(False,False)]],['low','low','high','low'])
check('119-Q02 operation counts',(100*10+1000,10**2+1),(2000,101))
check('119-Q03 first crossover',next(n for n in range(1,1001) if 100*n+1000<n*n+1),110)
check('119-Q03 boundary109',(100*109+1000,109**2+1),(11900,11882))
check('119-Q03 boundary110',(100*110+1000,110**2+1),(12000,12101))
check('101-Q04 area scale',2*3,6)
check('101-Q05 diagonal inverse',(2*F(1,2),4*F(1,4)),(1,1))
M=((0,1),(2,0))
check('100-Q05 zero diagonal insufficient',all(M[i][j]==-M[j][i] for i in range(2) for j in range(2)),False)
x={'schemaVersion':'1.0.0','batchId':'W01-L03','reviewerId':'define_robotics_data_contracts:L03-independent-reviewer','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Fixed authored question calculations and deterministic graph traces; not a numerical generator certification. Boundary/domain restrictions independently reviewed in the blind reasoning and full solution audit.','checks':checks}
p=ROOT/'audits/independent-checks-W01-L03.json';p.write_text(json.dumps(x,indent=2)+'\n');print(len(checks),'independent checks passed')
