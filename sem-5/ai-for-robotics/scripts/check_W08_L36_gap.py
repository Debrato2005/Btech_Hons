#!/usr/bin/env python3
"""Exact author checks for L36 gap content. Not independent review or source code execution."""
import json,heapq,random,math
from pathlib import Path
from fractions import Fraction as F
R=Path(__file__).resolve().parents[1];checks=[]
def ck(name,ok,detail):
 assert ok,name;checks.append(dict(name=name,passed=True,detail=detail,independent=False))
black=[[6,7,8],[4,6],[1,2],[],[4,5,6],[1,4,5],[4],[4,8]]
ck('Actual occupancy-image transcription',sum(map(len,black))==16 and 64-sum(map(len,black))==48,'Eight rows: occupied counts3,2,2,0,3,3,1,2;16 occupied and48 free.')
ck('Grid storage and distractors',20/F(1,2)*10/F(1,2)==800 and 20/F(1,4)*10/F(1,4)==3200,'0.5 m:40×20=800 cells;0.25 m:80×40=3200 cells;fourfold, not twofold or eightfold.')
ck('Objective comparison',8<10 and 9<12,'Length chooses P; energy chooses Q under the stipulated feasible-route values.')
ck('Footprint corridor comparison',F(10,10)>F(8,10),'1.0 m width exceeds0.8 m clearance; grid refinement does not change these physical dimensions.')
G={'A':{'B':3,'C':1},'B':{'D':5,'E':1},'C':{'B':7,'D':2},'D':{'E':7},'E':{}}
def allpaths(G,u,goal,path=(),cost=0,prob=F(1)):
 path=path+(u,)
 if u==goal:return [(path,cost,prob)]
 out=[]
 for v,w in G[u].items():
  assert v not in path,'This path enumerator requires the supplied DAG.'
  out+=allpaths(G,v,goal,path,cost+w,prob/F(len(G[u])))
 return out
paths=allpaths(G,'A','E');pm={''.join(p):(cost,prob) for p,cost,prob in paths}
ck('Directed map edges',sum(map(len,G.values()))==7 and 'B' in G['C'] and 'C' not in G['B'],'Seven arrows;C→B7 with no reverseB→C.')
ck('All five directed routes enumerated',pm=={'ABDE':(15,F(1,4)),'ABE':(4,F(1,4)),'ACBDE':(20,F(1,8)),'ACBE':(9,F(1,8)),'ACDE':(10,F(1,4))},str(pm))
ck('DAG every walk reaches E within four moves',len(paths)==5 and max(len(p)-1 for p,c,pr in paths)==4 and sum(pr for p,c,pr in paths)==1,'Acyclic outgoing graph;E is its only terminal vertex.')
ck('Directed minimum cost and every offered foil',min(c for p,c,pr in paths)==4 and [pm[x][0] for x in ['ABE','ACDE','ACBE','ABDE']]==[4,10,9,15],'All four numerical route options use valid arrows and correct sums.')
u='A';route='A';cost=0
while u!='E':
 v,w=min(G[u].items(),key=lambda z:z[1]);cost+=w;u=v;route+=u
ck('Greedy immediate-edge counterexample',route=='ACDE' and cost==10,'Immediate costs1,2,7 total10 versus optimum4.')
ck('Uniform local choice differs from uniform complete routes',pm['ABE'][1]==F(1,4) and pm['ACBDE'][1]==F(1,8),'Shortest-route probability1/4;not1/2,1/5 or1/8.')
card=[(-1,0),(1,0),(0,-1),(0,1)];eight=card+[(-1,-1),(-1,1),(1,-1),(1,1)]
ck('Interior graph connectivity',len(set(card))==4 and len(set(eight))==8,'Four cardinal neighbors plus four diagonal neighbors, not the center.')
d=1+1.5*math.sqrt(2)
ck('Scaled cardinal and diagonal distance',round(d,3)==3.121 and round(2*d,3)==6.243 and 2*.5+3*.5==2.5 and 2*.5+3*1==4,'Correct3.121 m;equal-step foil2.5;Manhattan-diagonal foil4;missing-scale foil6.243.')
free={(0,0),(1,1)};legal_diag=(0,1) in free and (1,0) in free
ck('Explicit no-corner-cutting example',not legal_diag and all((dx,dy) not in free for dx,dy in [(0,1),(1,0)]),'No cardinal or permitted diagonal route in supplied2×2 grid.')
def search(G,start,goal,heuristic=None,fifo=False):
 h=heuristic or {v:0 for v in G};g={start:0};parent={};closed=[];front=[(h[start],start)];queue=[start];seen={start}
 while queue if fifo else front:
  if fifo:u=queue.pop(0)
  else:
   f,u=heapq.heappop(front)
   if u in closed or f!=g[u]+h[u]:continue
  if u==goal:
   path=[u]
   while u in parent:u=parent[u];path.append(u)
   return g[goal],list(reversed(path)),closed
  closed.append(u)
  for v,w in sorted(G[u].items()):
   ng=g[u]+w
   if fifo:
    if v not in seen:seen.add(v);g[v]=ng;parent[v]=u;queue.append(v)
   elif v not in closed and ng<g.get(v,float('inf')):
    g[v]=ng;parent[v]=u;heapq.heappush(front,(ng+h[v],v))
 return None,[],closed
ck('Start already equals goal',search({'S':{}},'S','S')==(0,['S'],[]),'Goal test precedes successor expansion.')
ck('Exhausted finite graph reports represented failure',search({'S':{'A':1},'A':{'S':1},'G':{}},'S','G')[0] is None,'Reachable S,A exhausted;G absent from that reachable component.')
ck('Frontier duplicate avoidance',list(dict.fromkeys(['E','F']+['E','G']))==['E','F','G'],'Retain one E scheduled entry, append newG;already exploredB omitted.')
neg={'S':{'G':2,'A':3},'A':{'G':-2},'G':{}}
ck('Negative-edge UCS counterexample',search(neg,'S','G')[:2]==(2,['S','G']) and 3-2==1,'Goal popped at2 beforeA3;actual alternative1. Graph is directed and acyclic.')
roads=[('A','B',5),('A','C',2),('B','D',6),('B','E',3),('C','F',4),('D','E',2),('E','F',1),('D','G',6),('F','G',3)]
RG={v:{} for v in 'ABCDEFG'}
for u,v,w in roads:RG[u][v]=w;RG[v][u]=w
h=dict(zip('ABCDEFG',[7,6,5,4,3,2,0]));true={v:search(RG,v,'G')[0] for v in RG}
ck('Exact cost-to-go vector',list(true.values())==[9,7,7,6,4,3,0],str(true))
ck('Heuristic vector is admissible and not exact except goal',all(h[v]<true[v] for v in 'ABCDEF') and h['G']==true['G']==0,'Printed values are lower estimates;source graph itself permits exact comparison.')
ck('Printed heuristic consistency across all directed edge uses',all(h[u]<=w+h[v] for u in RG for v,w in RG[u].items()),'18 directional inequalities checked; author analysis, not a definition printed on the slide.')
ck('Cost-to-go foils',list(h.values())==[7,6,5,4,3,2,0] and [search(RG,'A',v)[0] for v in RG]==[0,5,2,9,7,6,9],'Foils distinguish heuristic from exact remaining costs and from exact cost-to-come.')
ck('Valid but suboptimal remaining-route foil',[5+6+6,6+6,4+3,6,2+6,3,0]==[17,12,7,6,8,3,0],'Longer routes throughD create the last vector foil.')
proposed={'E':5,'A':8,'B':7,'F':3}
ck('Only modified E is inadmissible',[v for v in proposed if proposed[v]>true[v]]==['E'],'5>4;8≤9;7=7;3=3.')
ck('Initial A-star priority',0+h['A']==7,'g(A)=0,f(A)=7;false pairs(7,14),(0,0),(7,0).')
bfs=search(RG,'A','G',fifo=True);ucs=search(RG,'A','G');astar=search(RG,'A','G',h)
ck('Source BFS trace reproduced',bfs==(17,['A','B','D','G'],['A','B','C','D','E','F']),str(bfs))
ck('Source UCS trace reproduced',ucs==(9,['A','C','F','G'],['A','C','B','F','E','D']),str(ucs))
ck('Source A-star trace reproduced',astar==(9,['A','C','F','G'],['A','C','F']),str(astar))
ck('Expansion metric not elapsed-time guarantee',len(astar[2])==3 and len(ucs[2])==6 and search(RG,'A','G',{v:0 for v in RG})==ucs,'Three versus six expansions;h=0 gives identical UCS behavior with this implementation.')
# Check implementation against all-pairs dynamic programming on500 fresh finite nonnegative directed graphs.
rng=random.Random(3608)
for case in range(500):
 n=rng.randrange(2,9);nodes=list(range(n));graph={u:{} for u in nodes};D=[[0 if u==v else math.inf for v in nodes] for u in nodes]
 for u in nodes:
  for v in nodes:
   if u!=v and rng.random()<.35:graph[u][v]=rng.randrange(0,12);D[u][v]=graph[u][v]
 for k in nodes:
  for i in nodes:
   for j in nodes:D[i][j]=min(D[i][j],D[i][k]+D[k][j])
 ans=search(graph,0,n-1)[0];truth=D[0][n-1]
 assert (ans is None and math.isinf(truth)) or ans==truth
ck('500 generated nonnegative-graph checks',True,'Seed3608;2–8 vertices,weights0–11;UCS cost/failure agrees with Floyd–Warshall. No source runtime or independent-review claim.')
report=dict(batchId='W08-L36-COVERAGE-GAP',role='author-checks-not-independent-review',checks=checks,sourceCodePresent=False,generatedAlgorithmImplementations=True,randomCases=500,gridBlackColumns=black,directedPaths={k:{'cost':v[0],'probability':str(v[1])} for k,v in pm.items()},roadCostToGo=true,sourceTraces=dict(BFS=bfs,UCS=ucs,Astar=astar))
(R/'audits/W08-L36-gap-author-computations.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(len(checks),'author-check groups passed;500 random graph cases')
