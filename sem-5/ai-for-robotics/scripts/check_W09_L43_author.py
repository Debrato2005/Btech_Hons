"""Source-derived author checks, independent review still required."""
from pathlib import Path
import sys,runpy,contextlib,io,json,hashlib,random,collections
R=Path(__file__).resolve().parents[1]
sys.path.append('/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages')
with contextlib.redirect_stdout(io.StringIO()):m=runpy.run_path(str(R/'sources/supplemental/L43-official-code.py'))
checks=[]
def ck(name,test):assert test,name;checks.append(name)
ck('Source maze shape',m['ROWS']==4 and m['COLS']==5)
ck('Three source walls',m['WALLS']=={(0,1),(2,3),(3,0)})
ck('Sixteen non-goal free cells',m['X'].shape==(16,6) and len(m['y'])==16)
ck('Start feature row',m['np'].allclose(m['featurize'](0,0),[0,0,1,0,1,1]))
ck('Interior feature row',m['np'].allclose(m['featurize'](2,2),[.5,.4,0,0,0,1]))
ck('Far-end normalization excludes one',m['np'].allclose(m['featurize'](3,4)[:2],[.75,.8]))
ck('Action encoding and preference differ',m['ACTION_NAMES']==['UP','DOWN','LEFT','RIGHT'] and m['PREFERENCE']==[3,1,2,0])
ck('Teacher start down',m['best_direction'](0,0)==1)
ck('Teacher tie at1,1 picksright',m['best_direction'](1,1)==3)
ck('Teacher wall at2,3 forcesdown',m['best_direction'](2,2)==1)
ck('Class frequencies',collections.Counter(m['y'].tolist())=={3:11,1:5})
ck('Parameter count180',sum(p.numel()for p in m['model'].parameters())==180)
ck('Linear layer shapes',tuple(m['model'].net[0].weight.shape)==(16,6) and tuple(m['model'].net[2].weight.shape)==(4,16))
ck('Seeded current training accuracy',m['train_acc']==1.0)
ck('Source printed path reproduced',m['path']==[(0,0),(1,0),(1,1),(1,2),(1,3),(1,4),(2,4),(3,4)])
ck('Seven path edges',len(m['path'])-1==7)
ck('Manhattan lower bound attained',m['manhattan'](*m['START'])==7)
ck('Network outputs logits not required sum1',m['model'](m['X_t']).shape==(16,4) and not m['np'].allclose(m['model'](m['X_t']).detach().numpy().sum(1),1))
ck('Animation38framesnot38moves',m['TOTAL_FRAMES']==38 and m['DRIVE_FRAMES']==8)
ck('Printed other network count',4*10+10*3+3==73 and 73+10+3+1==87)
# Execute official local greedy helper on a reachable layout needing an initial detour.
g=m['best_direction'].__globals__;old={k:g[k]for k in ['ROWS','COLS','START','GOAL','WALLS']};g.update(ROWS=3,COLS=3,START=(0,0),GOAL=(0,2),WALLS={(0,1)})
ck('Greedy counterexample returnsNone',m['best_direction'](0,0)is None)
def bfs(start,goal,rows,cols,walls):
 seen={start};Q=collections.deque([(start,0)])
 while Q:
  x,d=Q.popleft()
  if x==goal:return d
  for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
   y=x[0]+dr,x[1]+dc
   if 0<=y[0]<rows and 0<=y[1]<cols and y not in walls and y not in seen:seen.add(y);Q.append((y,d+1))
 return None
ck('Counterexample reachable in4',bfs((0,0),(0,2),3,3,{(0,1)})==4)
g.update(old)
ck('Alloriginalteacherpathsreachgoal',all(bfs(c,m['GOAL'],4,5,m['WALLS'])==m['manhattan'](*c)for c in m['cells_for_training']))
# Correct masked action example at start: only DOWN is valid, even when RIGHT has greater score.
scores=[2,3,1,9];valid=[a for a,(dr,dc)in enumerate(m['ACTIONS'])if m['is_free'](dr,dc)];ck('Mask precedesargmax',max(valid,key=lambda a:scores[a])==1)
# Four-neighbor Manhattan parity means the non-worsening fallback cannot find a same-distance move.
rng=random.Random(43);trials=5000
for _ in range(trials):
 r,c,gr,gc=[rng.randrange(-30,31)for i in range(4)];dr,dc=rng.choice(m['ACTIONS']);delta=abs(r+dr-gr)+abs(c+dc-gc)-abs(r-gr)-abs(c-gc);assert delta in [-1,1]
ck('NoequalManhattanunitneighbors',True)
# A fixed-goal feature omits goal coordinates: changing GOAL alone leaves featurize unchanged.
a=m['featurize'](1,1).copy();g['GOAL']=(0,0);ck('Goalnotencodedinfeatures',m['np'].array_equal(a,m['featurize'](1,1)));g['GOAL']=old['GOAL']
out={'authorChecksOnly':True,'independentReviewRequired':True,'checks':checks,'checkCount':len(checks),'variedManhattanTrials':trials,'sourceCodeExecutedUnchangedBeforeTestScenarios':True,'testScenarioMutations':'Temporarily changed globals only for explicitly added counterexample; restored original settings.','sourceSha256':hashlib.sha256((R/'sources/supplemental/L43-official-code.py').read_bytes()).hexdigest(),'sourceProofLimits':'Successful exact training/maze reproduction is not proof for unseen mazes, altered goals, continuous robot dynamics or physical safety.'};(R/'audits/W09-L43-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
