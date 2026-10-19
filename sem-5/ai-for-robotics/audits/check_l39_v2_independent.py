"""Independent review checks, not an author generation script. Does not mutate questions."""
import contextlib,io,json,math,random,hashlib,runpy,tempfile,heapq,datetime,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
nbp=ROOT/'sources/supplemental/L39-official-notebook.ipynb'
nb=json.loads(nbp.read_text()); code=''.join(nb['cells'][0]['source'])
assert len(nb['cells'])==1 and nb['cells'][0]['cell_type']=='code'
checks=[]
def check(name,result,detail=None):
 assert result,(name,detail)
 checks.append({'name':name,'passed':True,'detail':detail})
with tempfile.TemporaryDirectory(prefix='l39-independent-') as td:
 p=pathlib.Path(td)/'original_cell.py';p.write_text(code)
 capture=io.StringIO();random.seed(392019)
 with contextlib.redirect_stdout(capture): ns=runpy.run_path(str(p),run_name='__main__')
stdout=capture.getvalue()
check('Complete original official code cell executed unchanged, including main pipeline and three random fixes',stdout.count('run ')>=3 and 'Step 7 - Waypoint Tracking:' in stdout)
nodes=ns['NODES'];adj=ns['ADJACENCY'];d=ns['euclidean'];astar=ns['astar']
check('twelve nodes nineteen undirected edges thirty-eight adjacency entries',len(nodes)==12 and len(ns['EDGE_DEFS'])==19 and sum(map(len,adj.values()))==38)
check('every rounded edge reciprocal',all((u,w) in adj[v] for u in adj for v,w in adj[u]))
check('N2 N7 length',round(math.hypot(220,155)/100,2)==2.69 and dict(adj['N2'])['N7']==2.69)
check('bounds',{**ns['MAP_BOUNDS']}=={'x_min':50.,'x_max':750.,'y_min':45.,'y_max':480.})
check('cosmetic tuple exact source input400,200',ns['to_fake_latlon'](400,200)==(28.6199,77.215))
check('nearest node independent distances',ns['map_match']((150,420))=='N9')
# Equal-distance candidate order tested by temporarily substituting the function globals, restored afterwards.
fn=ns['map_match'];old=fn.__globals__['NODES'];fn.__globals__['NODES']={'A':(-1,0),'B':(1,0)}
try:check('strict less-than tie keeps first',fn((0,0))=='A')
finally:fn.__globals__['NODES']=old
route=['N9','N10','N11','N12','N8','N4']
check('highlighted source route reproduced',astar('N9','N4',verbose=False)==route)
graph=sum(dict(adj[a])[b] for a,b in zip(route,route[1:]));raw=sum(d(a,b) for a,b in zip(route,route[1:]));wps=ns['build_waypoints'](route)
check('graph versus raw cumulative distinction',math.isclose(graph,9.07) and round(raw,2)==9.08 and abs(raw-9.0830789)<1e-7,{'graph':graph,'raw':raw,'waypoints':[vars(w) for w in wps]})
check('waypoint displayed values',[w.cumulative_km for w in wps]==[0,1.9,3.91,5.73,7.33,9.08])
check('sixty percent target',ns['current_waypoint'](wps,0.6*9.08).node_id=='N12')
check('equality tolerance retains reached threshold',ns['current_waypoint'](wps,3.91).node_id=='N11')
check('beyond end returns last',ns['current_waypoint'](wps,100).node_id=='N4')
check('zero length singleton route',[w.cumulative_km for w in ns['build_waypoints'](['N4'])]==[0] and astar('N4','N4',False)==['N4'])
# Standard independent Dijkstra implementation with no source heuristic.
def shortest(a,b):
 best={a:0.}; heap=[(0.,a)]
 while heap:
  cost,u=heapq.heappop(heap)
  if cost!=best[u]:continue
  if u==b:return cost
  for v,w in adj[u]:
   nc=cost+w
   if nc<best.get(v,math.inf):best[v]=nc;heapq.heappush(heap,(nc,v))
 return math.inf
for a in nodes:
 for b in nodes:
  path=astar(a,b,False);cost=sum(dict(adj[u])[v] for u,v in zip(path,path[1:]));assert math.isclose(cost,shortest(a,b),abs_tol=1e-10),(a,b,path,cost,shortest(a,b))
check('all144orderedpairs match independent Dijkstra on this fixed graph',True,{'cases':144,'scope':'Finite graph only, not a proof of heuristic admissibility.'})
check('rounded graph heuristic counterexample',d('N2','N3')>dict(adj['N2'])['N3'],{'heuristic':d('N2','N3'),'directEdge':dict(adj['N2'])['N3']})
check('time distance units',math.isclose(3e8*.070,21000000) and math.isclose(3e8*2e-6,600) and math.isclose(30/3e8,1e-7))
check('circle equations exact',(4**2+3**2,(4-4)**2+3**2,4**2+(3-3)**2)==(25,9,16))
check('projection distance and bounds',math.isclose(math.hypot(50,2),50.039984012787215) and 2<math.hypot(50,2))
check('A-star f ordering',2+5>5+1)
check('travel time conversion',math.isclose(4/20*60,12) and math.isclose(6/60*60,6))
check('PDOP stated simplified model',2*3.5==7)
rng=random.Random(392020)
for i in range(1000):
 fix=ns['acquire_gnss_fix']();assert 50<=fix[0]<=750 and 45<=fix[1]<=480
 a,b,c=[(rng.uniform(-100,100),rng.uniform(-100,100)) for _ in range(3)]
 dist=lambda p,q:math.hypot(p[0]-q[0],p[1]-q[1])
 assert dist(a,c)<=dist(a,b)+dist(b,c)+1e-10
 sigma=rng.uniform(0,20);pdop=rng.uniform(1,12);assert math.isclose(math.sqrt((sigma*pdop)**2),sigma*pdop)
 travel=rng.uniform(-2,12);wp=ns['current_waypoint'](wps,travel);expected=next((w for w in wps if w.cumulative_km>=travel-1e-6),wps[-1]);assert wp==expected
check('1000 each bounds triangle-inequality PDOP nonnegative arithmetic and threshold scans',True,{'trials':4000})
# New independently derived circle cases, exact substitution after linear elimination.
check('caseI unique',(1**2+1**2,(1-2)**2+1**2,1**2+(1-2)**2)==(2,2,2))
check('caseII two mirror solutions',all(((x+1)**2+y*y,x*x+y*y,(x-1)**2+y*y)==(2,1,2) for x,y in [(0,1),(0,-1)]))
check('caseIII inconsistent tangent circles',(1**2+0**2,(1-2)**2+0**2)==(1,1) and 1**2+(0-2)**2!=1)
out={'reviewerId':'independent-reviewer-robotics-batches-v2','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'officialNotebookSha256':hashlib.sha256(nbp.read_bytes()).hexdigest(),'exactCellSha256':hashlib.sha256(code.encode()).hexdigest(),'originalCellExecutedUnchanged':True,'officialCellStdout':stdout,'independentChecks':checks,'groups':len(checks),'variedTrials':4000,'orderedGraphComparisons':144,'sourceQualifications':['Original localization section comment says fixed-centre noise but actual function uniform-samples the whole rectangle.','Original current_waypoint docstring says not-yet-reached but equality comparison returns the reached threshold.','Random extra fixes are not guaranteed to have three different matched nodes.','Original function expects a nonempty waypoint list; empty input raises IndexError.'],'notClaimed':['No physical GNSS sensor was read.','No graphical HTML simulator/browser controller was executed.','No real closed-loop controller or actual geodetic conversion exists in this notebook.','Finite A-star matching does not prove universal admissibility.']}
f=ROOT/'audits/W08-L39-v2-independent-computations.json';f.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'groups':len(checks),'trials':4000,'pairs':144,'raw':raw,'path':str(f)}))
