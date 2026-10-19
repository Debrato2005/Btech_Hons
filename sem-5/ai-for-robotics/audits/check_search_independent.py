"""Independent reviewer recomputation, transcribed from inspected source pixels."""
import json,heapq,math
from collections import deque
from pathlib import Path
R=Path(__file__).resolve().parents[1]
roads=[('A','B',5),('A','C',2),('B','D',6),('B','E',3),('C','F',4),('D','E',2),('E','F',1),('D','G',6),('F','G',3)]
G={v:{} for v in 'ABCDEFG'}
for a,b,w in roads:G[a][b]=w;G[b][a]=w
H=dict(zip('ABCDEFG',[7,6,5,4,3,2,0]))
def weighted(start,goal,h,reverse_tie=False):
 d={start:0};parent={};opened={start};closed=[];frontiers=[]
 while opened:
  node=min(opened,key=lambda n:(d[n]+h(n),-ord(n) if reverse_tie else ord(n)))
  opened.remove(node)
  if node==goal:
   path=[node]
   while path[-1] in parent:path.append(parent[path[-1]])
   return {'cost':d[node],'path':path[::-1],'expanded':closed,'frontiers':frontiers}
  closed.append(node)
  for nxt in sorted(G[node]):
   cand=d[node]+G[node][nxt]
   if cand<d.get(nxt,math.inf):d[nxt]=cand;parent[nxt]=node;opened.add(nxt)
  frontiers.append([[n,d[n],d[n]+h(n)] for n in sorted(opened,key=lambda n:(d[n]+h(n),n))])
queue=deque(['A']);discovered={'A'};parent={};expanded=[]
while queue:
 n=queue.popleft()
 if n=='G':break
 expanded.append(n)
 for v in sorted(G[n]):
  if v not in discovered:discovered.add(v);parent[v]=n;queue.append(v)
path=['G']
while path[-1] in parent:path.append(parent[path[-1]])
path.reverse()
bfs={'path':path,'cost':sum(G[a][b] for a,b in zip(path,path[1:])),'expanded':expanded}
ucs=weighted('A','G',lambda n:0);astar=weighted('A','G',H.get);tie=weighted('A','G',lambda n:0,True)
assert bfs['cost']==17 and bfs['expanded']==list('ABCDEF')
assert ucs['cost']==9 and ucs['expanded']==list('ACBFED')
assert astar['cost']==9 and astar['expanded']==list('ACF')
assert tie['cost']==9 and tie['expanded']==list('ACBFE')
assert all(H[a]<=w+H[b] for a in G for b,w in G[a].items())
walls={(0,0),(0,1),(0,2),(1,2),(2,2),(3,2)}
free={(r,c) for r in range(5) for c in range(5)}-walls
expected_g={(0,3):4.4,(0,4):4,(1,0):6.4,(1,1):6,(1,3):3.4,(1,4):3,(2,0):5.4,(2,1):5,(2,3):2.4,(2,4):2,(3,0):4.4,(3,1):4,(3,3):1.4,(3,4):1,(4,0):4,(4,1):3,(4,2):2,(4,3):1,(4,4):0}
expected_h={(0,3):3.8,(0,4):4.8,(1,0):1,(1,1):1.4,(1,3):3.4,(1,4):4.4,(2,0):0,(2,1):1,(2,3):3,(2,4):4,(3,0):1,(3,1):1.4,(3,3):3.4,(3,4):4.4,(4,0):2,(4,1):2.4,(4,2):2.8,(4,3):3.8,(4,4):4.8}
def grid_dist():
 d={(4,4):0};heap=[(0,(4,4))]
 while heap:
  val,(r,c)=heapq.heappop(heap)
  if val!=d[(r,c)]:continue
  for dr in [-1,0,1]:
   for dc in [-1,0,1]:
    if not(dr or dc):continue
    nxt=(r+dr,c+dc)
    if nxt not in free:continue
    if dr and dc and ((r+dr,c) not in free or (r,c+dc) not in free):continue
    cand=round(val+(1.4 if dr and dc else 1),10)
    if cand<d.get(nxt,math.inf):d[nxt]=cand;heapq.heappush(heap,(cand,nxt))
 return d
actual_g=grid_dist()
actual_h={p:round(1.4*min(abs(p[0]-2),p[1])+abs(abs(p[0]-2)-p[1]),10) for p in free}
assert actual_g==expected_g
assert actual_h==expected_h
out={'bfs':bfs,'ucs':ucs,'astar':astar,'ucsGoalFirstTie':tie,'roadHeuristicConsistent':True,'gridFreeCells':len(free),'all19SourceGValuesRecomputed':True,'all19SourceHValuesRecomputed':True,'startGConflict':{'p1133':0,'p1135':1,'independentMoveCost':0},'sourcePages':[1110,1119,1131,1132,1133,1134,1135],'limitations':'This recomputes fixed source examples, not arbitrary generated families.'}
(R/'audits/search-independent-computations.json').write_text(json.dumps(out,indent=2)+'\n')
print('Independent recomputation passed: BFS/UCS/A*, tie change, all19 g cells, all19 h cells.')
