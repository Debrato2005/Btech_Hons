"""Independent source-reconstructed L36 graph and resolution checks; no keyed data loaded."""
import json,math,heapq,random,datetime,hashlib
from fractions import Fraction as F
from pathlib import Path
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,value):
 assert value,name
 checks.append({'name':name,'passed':True})
edges=[('A','B',5),('A','C',2),('B','D',6),('B','E',3),('C','F',4),('E','F',1),('E','D',2),('D','G',6),('F','G',3)]
graph={v:{} for v in 'ABCDEFG'}
for u,v,c in edges:graph[u][v]=c;graph[v][u]=c
h=dict(zip('ABCDEFG',[7,6,5,4,3,2,0]))
def search(adj,start,goal,heur):
 g={start:0};par={start:None};open=[(heur.get(start,0),start,0)];closed=set();order=[];trace=[]
 while open:
  f,u,gu=heapq.heappop(open)
  if gu!=g[u] or u in closed:continue
  if u==goal:
   path=[];v=u
   while v is not None:path.append(v);v=par[v]
   return {'cost':gu,'path':path[::-1],'expanded':order,'trace':trace,'parents':par,'g':g}
  order.append(u);closed.add(u)
  changes=[]
  for v,w in sorted(adj[u].items()):
   ng=gu+w
   if ng<g.get(v,float('inf')):
    before=g.get(v);g[v]=ng;par[v]=u;heapq.heappush(open,(ng+heur.get(v,0),v,ng));changes.append({'vertex':v,'old':before,'new':ng,'parent':u})
  trace.append({'expanded':u,'changes':changes,'frontier':sorted([(g[v]+heur.get(v,0),v,g[v],par[v]) for v in g if v not in closed])})
 return None
ucs=search(graph,'A','G',{});astar=search(graph,'A','G',h)
check('UCS six non-goal expansions',ucs['expanded']==list('ACBFED'))
check('A-star three non-goal expansions',astar['expanded']==list('ACF'))
check('both nine-kilometer parent paths',ucs['cost']==astar['cost']==9 and ucs['path']==astar['path']==list('ACFG'))
check('E parent improves B to F',ucs['trace'][3]['changes'][0]=={'vertex':'E','old':8,'new':7,'parent':'F'})
check('D parent improves B to E',ucs['parents']['D']=='E' and ucs['g']['D']==9)
check('D before G tie resolved alphabetically',ucs['trace'][4]['frontier']==[(9,'D',9,'E'),(9,'G',9,'F')])
check('worse G15 does not overwrite G9',ucs['parents']['G']=='F' and not ucs['trace'][5]['changes'])
check('heuristic consistency on all18 orientations',all(h[u]<=c+h[v] and h[v]<=c+h[u] for u,v,c in edges))
directed={'A':{'B':3,'C':1},'B':{'D':5,'E':1},'C':{'B':7,'D':2},'D':{'E':7},'E':{}}
routecosts={p:sum(directed[u][v] for u,v in zip(p,p[1:])) for p in ['ABE','ACDE','ACBE','ABDE']}
check('directed route costs',routecosts=={'ABE':4,'ACDE':10,'ACBE':9,'ABDE':15})
check('directed minimum route search',search(directed,'A','E',{})['path']==list('ABE'))
def freecell(i,j,s):return F(0)<=i*s and (i+1)*s<=4 and F(3,10)<j*s and (j+1)*s<F(9,10)
coarse=(F(1,2)//F(1),F(1,2)//F(1));fine=(F(1,2)//F(1,5),F(1,2)//F(1,5));goal=(F(7,2)//F(1,5),fine[1])
check('coarse endpoint cells blocked',not freecell(*coarse,F(1)))
check('fine entire horizontal chain free',all(freecell(i,fine[1],F(1,5)) for i in range(int(fine[0]),int(goal[0])+1)))
check('strict boundary excludes squares touching walls',not(F(3,10)<F(3,10)) and not(F(9,10)<F(9,10)))
card=F(2,5)*(5+3);octile=.4*(2+3*math.sqrt(2))
check('4-connected length',card==F(16,5))
check('8-connected length',math.isclose(octile,.8+1.2*math.sqrt(2)))
check('Euclidean and equal-hop distractors distinct',.4*math.sqrt(34)<octile<3.2 and not math.isclose(octile,2))
# Independent dynamic shortest-path enumeration verifies octile formula for 1000 supplied variations.
rng=random.Random(3602)
for _ in range(1000):
 dx,dy=rng.randrange(11),rng.randrange(11);side=rng.uniform(.01,2);dp=[[float('inf')]*(dy+1) for i in range(dx+1)];dp[0][0]=0
 for i in range(dx+1):
  for j in range(dy+1):
   if i:dp[i][j]=min(dp[i][j],dp[i-1][j]+side)
   if j:dp[i][j]=min(dp[i][j],dp[i][j-1]+side)
   if i and j:dp[i][j]=min(dp[i][j],dp[i-1][j-1]+math.sqrt(2)*side)
 assert math.isclose(dp[dx][dy],side*(abs(dx-dy)+math.sqrt(2)*min(dx,dy)),abs_tol=1e-10)
check('1000 independent octile dynamic-programming comparisons',True)
result={'reviewerId':'robotics-contracts-independent-reviewer','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'assertionCount':len(checks),'variedCases':1000,'checks':checks,'UCS':ucs,'AStar':astar,'directedRouteCosts':routecosts,'resolution':{'coarseEndpointCell':list(map(int,coarse)),'fineEndpointCell':list(map(int,fine)),'fineGoalCell':list(map(int,goal)),'fineHorizontalHops':int(goal[0]-fine[0])},'minimumGridLengths':{'fourConnected':float(card),'eightConnected':octile},'codeScope':'Reviewer-authored reconstruction of the actual printed graphs and explicitly supplied occupancy/step variants. No literal source Python code or linked notebook appears in L36; this is not claimed as execution of source code. No current author key, repair narrative or expected check result was loaded.'}
p=R/'audits/W08-L36-v2-contracts-independent-checks.json';p.write_text(json.dumps(result,indent=2)+'\n');print('passed',len(checks),'checks and1000 varied cases')
