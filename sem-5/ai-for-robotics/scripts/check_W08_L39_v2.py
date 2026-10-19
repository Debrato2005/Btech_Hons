#!/usr/bin/env python3
"""Author-only L39 checks; execute unchanged official code without source writes."""
import json,math,hashlib,types,sys,io,contextlib,random,heapq
from pathlib import Path
from fractions import Fraction as F
R=Path(__file__).resolve().parents[1];nbp=R/'sources/supplemental/L39-official-notebook.ipynb';nb=json.loads(nbp.read_text());src='\n'.join(''.join(c['source'])for c in nb['cells']if c['cell_type']=='code');assert src==(R/'sources/supplemental/L39-official-code.py').read_text()
m=types.ModuleType('l39_v2_author_original');sys.modules[m.__name__]=m;exec(compile(src,str(nbp),'exec'),m.__dict__)
checks=[]
def ck(name,condition,detail=None):
 assert condition,name
 checks.append(dict(name=name,passed=True,detail=detail))
ck('Immutable official notebook hash',hashlib.sha256(nbp.read_bytes()).hexdigest()=='77577033081f535374682f37df140f08c3f86cb60ba26ae18df75e6e614ab852')
ck('Synthetic coordinate conversion',m.to_fake_latlon(400,200)==(28.6199,77.215))
ck('All signed and reordered display distractors',len({(28.6199,77.215),(28.6079,77.203),(77.215,28.6199),(28.6199,77.203)})==4)
fix=(150,420);selected=['N9','N10','N5','N1'];squares=[sum((a-b)**2 for a,b in zip(m.NODES[n],fix))for n in selected]
ck('Nearest-node exact distances',squares==[200,32400,24100,99700] and m.map_match(fix)=='N9',squares)
# Invoke the original map_match implementation with explicitly supplied variant dictionaries, restoring globals.
original_nodes=m.NODES
m.NODES={'A':(-1,0),'B':(1,0)};first=m.map_match((0,0));m.NODES={'B':(1,0),'A':(-1,0)};reverse=m.map_match((0,0));m.NODES=original_nodes
ck('Strict tie retains insertion-first candidate',first=='A'and reverse=='B')
# Geometric projection and each erroneous numerical procedure.
a=(F(0),F(0));b=(F(100),F(0));p=(F(50),F(2));ab=(b[0]-a[0],b[1]-a[1]);raw=sum((p[i]-a[i])*ab[i]for i in range(2));t=raw/sum(x*x for x in ab);proj=tuple(a[i]+t*ab[i]for i in range(2))
ck('Exact projection',t==F(1,2) and proj==(50,0) and sum((p[i]-proj[i])**2 for i in range(2))==4)
ck('Endpoint squared versus unsquared distractor',sum((p[i]-a[i])**2 for i in range(2))==2504 and round(math.sqrt(2504),2)==50.04)
ck('Unscaled-fraction and raw-clamp distractors',round(math.hypot(49.5,2),2)==49.54 and min(F(1),max(F(0),raw))==1)
# Original complete graph execution and independent shortest paths.
def dijkstra(s):
 d={s:0};queue=[(0,s)]
 while queue:
  cost,u=heapq.heappop(queue)
  if cost!=d[u]:continue
  for v,w in m.ADJACENCY[u]:
   c=cost+w
   if c<d.get(v,math.inf):d[v]=c;heapq.heappush(queue,(c,v))
 return d
pairs=0;bad=[]
for start in m.NODES:
 distances=dijkstra(start)
 for goal in m.NODES:
  route=m.astar(start,goal,False);cost=sum(dict(m.ADJACENCY[x])[y]for x,y in zip(route,route[1:]));pairs+=1
  if not math.isclose(cost,distances[goal],abs_tol=1e-10):bad.append((start,goal,cost,distances[goal]))
ck('All 144 ordered pairs match separate Dijkstra',pairs==144 and not bad,dict(pairs=pairs,mismatches=bad))
route=m.astar('N9','N4',False);raw_edges=[m.euclidean(x,y)for x,y in zip(route,route[1:])];rounded_edges=[dict(m.ADJACENCY[x])[y]for x,y in zip(route,route[1:])];wp=m.build_waypoints(route);cum=[x.cumulative_km for x in wp]
ck('Highlighted path',route==['N9','N10','N11','N12','N8','N4'],route)
ck('Distinct source rounding stages',math.isclose(sum(rounded_edges),9.07)and round(sum(raw_edges),7)==9.0830789 and wp[-1].cumulative_km==9.08,dict(rawEdges=raw_edges,roundedEdges=rounded_edges,rawTotal=sum(raw_edges),roundedGraphTotal=sum(rounded_edges),waypointTotal=wp[-1].cumulative_km))
ck('Cumulative table matches source',[0,1.90,3.91,5.73,7.33,9.08]==cum,cum)
iterated=0
for v in raw_edges:iterated=round(iterated+v,2)
ck('Round-running-accumulator alternative differs',iterated==9.07)
ck('Adding cumulative entries double-counts',math.isclose(sum(cum),27.95)and sum(cum)!=sum(rounded_edges))
ck('Rounding heuristic counterexample',m.heuristic('N2','N3')>dict(m.ADJACENCY['N2'])['N3']and math.isclose(m.heuristic('N2','N3'),math.sqrt(40100)/100))
ck('Supplied sixty-percent calculation',F('.6')*F('9.08')==F('5.448')and m.current_waypoint(wp,5.448).node_id=='N12')
ck('Exact threshold and tolerance behavior',m.current_waypoint(wp,3.91).node_id=='N11'and m.current_waypoint(wp,3.91+0.5e-6).node_id=='N11'and m.current_waypoint(wp,3.91+2e-6).node_id=='N12')
ck('Time conversions and all distractors',60*F(4)/20==12 and 60*F(6)/60==6 and F(4)/20==F('.2')and F(6)/60==F('.1')and 60*F(20)/4==300 and 60*F(60)/6==600)
# Exact planar circle systems: derive a candidate from independent difference equations, then check circles.
def squared(q,c):return sum((F(q[j])-F(c[j]))**2 for j in range(2))
centersI=[(0,0),(2,0),(0,2)];centersII=[(-1,0),(0,0),(1,0)]
ck('Unique consistent noncollinear example',all(squared((1,1),c)==2 for c in centersI)and (centersI[1][0]-centersI[0][0])*(centersI[2][1]-centersI[0][1])-(centersI[1][1]-centersI[0][1])*(centersI[2][0]-centersI[0][0])!=0)
ck('Collinear exact mirror pair',all([squared(q,c)for c in centersII]==[2,1,2]for q in[(0,1),(0,-1)]))
ck('Inconsistent three-circle case',squared((1,0),centersI[0])==squared((1,0),centersI[1])==1 and squared((1,0),centersI[2])==5)
# Full official run_pipeline function, fixed seed makes the source's synthetic randomness reproducible.
m.random.seed(39);out=io.StringIO()
with contextlib.redirect_stdout(out):m.run_pipeline('Airport',True)
ck('Original end-to-end demonstration runs','Step 7' in out.getvalue(),{'stdout':out.getvalue()})
# Varied author tests are not new question counts or independent verification.
rng=random.Random(391222);cases=0;assertions=0
for _ in range(500):
 pts=[(rng.uniform(-10,10),rng.uniform(-10,10))for j in range(rng.randint(2,8))]
 direct=math.dist(pts[0],pts[-1]);broken=sum(math.dist(x,y)for x,y in zip(pts,pts[1:]));assert direct<=broken+1e-12;cases+=1;assertions+=1
for _ in range(500):
 a=(rng.uniform(-10,10),rng.uniform(-10,10));b=(rng.uniform(-10,10),rng.uniform(-10,10));p=(rng.uniform(-10,10),rng.uniform(-10,10));v=(b[0]-a[0],b[1]-a[1]);t=max(0,min(1,sum((p[j]-a[j])*v[j]for j in range(2))/sum(z*z for z in v)));proj=tuple(a[j]+t*v[j]for j in range(2));d=math.dist(p,proj)
 assert 0<=t<=1;assert d<=min(math.dist(p,a),math.dist(p,b))+1e-10;cases+=1;assertions+=2
ck('Varied triangle and segment checks',cases==1000 and assertions==1500,dict(cases=cases,assertions=assertions))
report=dict(precheckCorrections=['Initial author script had missing lexical spaces and an over-precise handwritten expected raw total; corrected syntax and compare the stated seven-decimal total. Official source code and numerical result were not changed.'],authorId='L39-repair-author-20261019',independentReview=False,passed=True,groups=len(checks),variedCases=cases,variedAssertions=assertions,allPairsDijkstraComparisons=pairs,notebookSha256=hashlib.sha256(nbp.read_bytes()).hexdigest(),codeSha256=hashlib.sha256(src.encode()).hexdigest(),execution='Complete original code cell compiled unchanged; run_pipeline called unchanged with fixed random seed. Separate supplied tie inputs temporarily replace NODES and restore it. No source file modifications.',checks=checks)
(R/'audits/W08-L39-v2-author-computations.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'groups',cases,'cases',assertions,'varied assertions',pairs,'graph pairs')
