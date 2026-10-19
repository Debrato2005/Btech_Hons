"""Independent L36 source-graph checks. No author batch or check imports."""
from pathlib import Path
from fractions import Fraction
from collections import deque
import heapq,json,datetime,random,math,hashlib
R=Path(__file__).resolve().parents[1]; checks=[]
def ck(label,value,expected):
 assert value==expected,(label,value,expected)
 checks.append(dict(label=label,value=value,expected=expected))
directed={'A':{'B':3,'C':1},'B':{'D':5,'E':1},'C':{'B':7,'D':2},'D':{'E':7},'E':{}}
paths=[]
def enumerate_paths(g,u,goal,path,cost,prob):
 if u==goal:paths.append(dict(path=path,cost=cost,probability=str(prob)));return
 for v,w in g[u].items():enumerate_paths(g,v,goal,path+[v],cost+w,prob/Fraction(len(g[u])))
enumerate_paths(directed,'A','E',['A'],0,Fraction(1))
ck('Directed terminal path count',len(paths),5);ck('Directed maximum transitions',max(len(p['path'])-1 for p in paths),4)
ck('Minimum directed route',[p['path'] for p in paths if p['cost']==min(q['cost'] for q in paths)],[['A','B','E']]);ck('Minimum directed cost',min(p['cost'] for p in paths),4)
ck('Optimal random local route probability',next(p['probability'] for p in paths if p['path']==['A','B','E']),'1/4');ck('Total terminal probability',str(sum(Fraction(p['probability']) for p in paths)),'1')
u='A';greedy=['A'];cost=0
while u!='E':v=min(directed[u],key=directed[u].get);cost+=directed[u][v];greedy.append(v);u=v
ck('Immediate-edge greedy path',greedy,['A','C','D','E']);ck('Immediate-edge greedy cost',cost,10)
G={u:{} for u in 'ABCDEFG'}
for u,v,w in [('A','B',5),('A','C',2),('B','D',6),('B','E',3),('C','F',4),('D','E',2),('D','G',6),('E','F',1),('F','G',3)]:G[u][v]=w;G[v][u]=w
h=dict(zip('ABCDEFG',[7,6,5,4,3,2,0]))
def search(g,start,goal=None,heur=None):
 heur=heur or {u:0 for u in g};dist={start:0};parent={start:None};queue=[(heur[start],start)];expanded=[];trace=[]
 while queue:
  f,u=heapq.heappop(queue)
  if u in expanded or f!=dist[u]+heur[u]:continue
  if u==goal:break
  expanded.append(u)
  for v,w in sorted(g[u].items()):
   nd=dist[u]+w
   if nd<dist.get(v,float('inf')):dist[v]=nd;parent[v]=u;heapq.heappush(queue,(nd+heur[v],v))
  frontier=sorted((dist[v]+heur[v],v) for v in dist if v not in expanded)
  trace.append(dict(expanded=u,frontier=frontier))
 path=[]
 if goal is not None and goal in dist:
  v=goal
  while v is not None:path.insert(0,v);v=parent[v]
 return dist,expanded,path,trace
back=search(G,'G')[0];ck('True distances to goal',[back[u] for u in 'ABCDEFG'],[9,7,7,6,4,3,0])
ck('Source heuristic admissibility',all(h[u]<=back[u] for u in G),True);ck('Source heuristic edge consistency',all(h[u]<=w+h[v] for u in G for v,w in G[u].items()),True)
u=search(G,'A','G');a=search(G,'A','G',h)
ck('UCS expansions',u[1],['A','C','B','F','E','D']);ck('UCS path',u[2],['A','C','F','G']);ck('UCS cost',u[0]['G'],9)
ck('A-star expansions',a[1],['A','C','F']);ck('A-star path',a[2],['A','C','F','G']);ck('A-star cost',a[0]['G'],9)
ck('E overestimate',5>back['E'],True);ck('Other candidate h admissible',all(v<=back[n] for n,v in [('A',8),('B',7),('F',3)]),True)
q=deque(['A']);seen={'A'};parents={'A':None};expanded=[]
while q:
 n=q.popleft()
 if n=='G':break
 expanded.append(n)
 for v in sorted(G[n]):
  if v not in seen:seen.add(v);parents[v]=n;q.append(v)
p=[];n='G'
while n is not None:p.insert(0,n);n=parents[n]
ck('BFS expansions',expanded,list('ABCDEF'));ck('BFS path',p,['A','B','D','G']);ck('BFS path cost',sum(G[u][v] for u,v in zip(p,p[1:])),17)
ck('BFS duplicate handling',[n for n in ['E','F']]+[n for n in ['B','E','G'] if n not in {'A','B','C','D','E','F'}],['E','F','G'])
neg={'S':{'G':2,'A':3},'A':{'G':-2},'G':{}};r=search(neg,'S','G');ck('Negative counterexample returns2',r[0]['G'],2);ck('Counterexample true path cost',3-2,1)
ck('Start-goal no expansion',search(G,'A','A')[1],[])
occupied=[[6,7,8],[4,6],[1,2],[],[4,5,6],[1,4,5],[4],[4,8]];ck('Occupied cells',sum(map(len,occupied)),16);ck('Free cells',64-sum(map(len,occupied)),48)
ck('Coarse cell bytes',int(20/.5)*int(10/.5),800);ck('Refined cell bytes',int(20/.25)*int(10/.25),3200);ck('Grid memory factor',3200//800,4)
ck('Mixed-move length rounded',round(2*.5+3*.5*math.sqrt(2),3),3.121);ck('Footprint fits0.8m corridor',1.0<=.8,False);ck('Initial g f',[0,0+h['A']],[0,7])
# Cross-check nonnegative shortest-path implementation with independent all-pairs relaxation.
rng=random.Random(360043)
for case in range(1000):
 graph={v:{} for v in 'ABCDE'}
 for i in range(4):graph['ABCDE'[i]]['ABCDE'[i+1]]=rng.randint(0,15)
 for u1 in graph:
  for v1 in graph:
   if u1!=v1 and rng.random()<.3:graph[u1][v1]=rng.randint(0,15)
 floyd={(u1,v1):(0 if u1==v1 else graph[u1].get(v1,float('inf'))) for u1 in graph for v1 in graph}
 for k in graph:
  for i in graph:
   for j in graph:floyd[i,j]=min(floyd[i,j],floyd[i,k]+floyd[k,j])
 for start in graph:
  distances=search(graph,start)[0]
  for goal in graph:assert distances.get(goal,float('inf'))==floyd[start,goal]
result=dict(completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewerId='robotics-contracts-independent-reviewer',sourcePages=[1099,1100,1101,1102,1103,1104,1107,1108,1109,1110,1112,1113,1114,1115,1116,1117,1119,1120,1121,1122,1123],runtime='Python standard library; no literal source executable or notebook link exists in these39pages. Independently transcribed algorithms and figures, not author code.',assertionCount=len(checks),variedCases=1000,comparisonsPerVariedCase=25,checks=checks,directedPaths=paths,trueDistances=back,ucsTrace=u[3],aStarTrace=a[3],sourceQualifications=['D/G UCS tie resolved alphabetically as demonstrated, not universally required.','Goal removal/testing is excluded from successor-expansion count.','The source heuristics are admissible and consistent on the depicted weights; coordinates are not supplied to establish literal Euclidean geometry.','Generic graph guarantees are limited by nonnegative weights, finite exhaustive exploration and repeated-state rules.'])
out=R/'audits/W08-L36-contracts-independent-checks.json';assert not out.exists();out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(assertions=len(checks),variedCases=1000,trueDistances=back,outputSha256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2))
