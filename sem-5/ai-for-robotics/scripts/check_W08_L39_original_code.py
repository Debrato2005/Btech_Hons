from pathlib import Path
import json,hashlib,sys,types,math,heapq,contextlib,io,random
R=Path(__file__).resolve().parents[1]; f=R/'sources/supplemental/L39-official-notebook.ipynb';n=json.loads(f.read_text());src='\n'.join(''.join(c['source']) for c in n['cells'] if c['cell_type']=='code'); (R/'sources/supplemental/L39-official-code.py').write_text(src)
m=types.ModuleType('official_l39');sys.modules[m.__name__]=m;exec(compile(src,str(f),'exec'),m.__dict__)
def dijkstra(start):
 d={start:0};h=[(0,start)]
 while h:
  v,a=heapq.heappop(h)
  if v>d[a]:continue
  for b,w in m.ADJACENCY[a]:
   nd=v+w
   if nd<d.get(b,math.inf):d[b]=nd;heapq.heappush(h,(nd,b))
 return d
checks=[]
def check(name,v):
 assert v,name
 checks.append(name)
path=m.astar('N9','N4',False);wp=m.build_waypoints(path);dists={s:dijkstra(s) for s in m.NODES};bad=[];adm=[];cons=[]
for s in m.NODES:
 for g in m.NODES:
  p=m.astar(s,g,False);cost=sum(dict(m.ADJACENCY[a])[b] for a,b in zip(p,p[1:]));
  if abs(cost-dists[s][g])>1e-9:bad.append([s,g,cost,dists[s][g]])
  if m.heuristic(s,g)>dists[s][g]+1e-9:adm.append([s,g,m.heuristic(s,g),dists[s][g]])
  for t,w in m.ADJACENCY[s]:
   if m.heuristic(s,g)>w+m.heuristic(t,g)+1e-9:cons.append([s,t,g,m.heuristic(s,g),w+m.heuristic(t,g)])
check('12 nodes',len(m.NODES)==12);check('19 undirected edges',len(m.EDGE_DEFS)==19);check('38 adjacency entries',sum(map(len,m.ADJACENCY.values()))==38);check('symmetry',all(dict(m.ADJACENCY[b])[a]==w for a,es in m.ADJACENCY.items() for b,w in es));check('all 144 pairs match Dijkstra',not bad);check('heuristic not generally admissible on rounded graph',bool(adm));check('heuristic not consistent on rounded graph',bool(cons));check('N9 to N4 route',path==['N9','N10','N11','N12','N8','N4']);check('rounded graph 9.07',math.isclose(dists['N9']['N4'],9.07));check('raw waypoint total 9.08',wp[-1].cumulative_km==9.08);check('cumulative raw distances match screenshot',[x.cumulative_km for x in wp]==[0,1.9,3.91,5.73,7.33,9.08]);check('fake center origin',m.to_fake_latlon(300,300)==(28.6139,77.209));check('map bounds',m.MAP_BOUNDS==dict(x_min=50,x_max=750,y_min=45,y_max=480));check('node exact matches',all(m.map_match(xy)==s for s,xy in m.NODES.items()));check('current waypoint 60%',m.current_waypoint(wp,.6*wp[-1].cumulative_km).node_id=='N12');check('exact arrival retains equality waypoint',m.current_waypoint(wp,3.91).node_id=='N11');check('past end returns final',m.current_waypoint(wp,100).node_id=='N4');check('start equals goal',m.astar('N4','N4',False)==['N4']);check('single-node waypoints',m.build_waypoints(['N4'])[0].cumulative_km==0)
m.random.seed(39);sio=io.StringIO()
with contextlib.redirect_stdout(sio):m.run_pipeline('Airport',True)
for i in range(1000):
 xy=m.acquire_gnss_fix();assert 50<=xy[0]<=750 and 45<=xy[1]<=480
r={'status':'pass','notebookUrl':'https://github.com/robotics-lab-iitr/nptel-ai-robotics/blob/a70ba559deefa15abd9045756f3c76f0bada8abd/week08/week8_lecture39.ipynb','notebookSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'codeSha256':hashlib.sha256(src.encode()).hexdigest(),'execution':'Original complete code cell executed unchanged as an imported module; run_pipeline called with fixed random seed39; no browser or real satellite data used.','explicitChecks':checks,'allPairsDijkstraComparisons':144,'randomBoundsChecks':1000,'N9N4':{'path':path,'roundedGraphCost':dists['N9']['N4'],'unroundedPathCost':sum(m.euclidean(a,b) for a,b in zip(path,path[1:])),'waypoints':[vars(x) for x in wp]},'admissibilityViolations':adm,'consistencyViolations':cons,'AstarMismatchesAgainstDijkstra':bad,'pipelineStdout':sio.getvalue()}
(R/'audits/W08-L39-original-code-execution.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ('status','notebookSha256','N9N4','AstarMismatchesAgainstDijkstra')}));print('checks',len(checks),'admissibility violations',len(adm),'consistency',len(cons));print('example',adm[:2]);print(sio.getvalue())
