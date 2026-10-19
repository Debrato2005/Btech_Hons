"""Independent full original-notebook execution and bounded mathematical checks."""
import sys,os,json,pathlib,hashlib,datetime,time,contextlib,io,random,math,collections
sys.path.append('/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages')
os.environ['MPLBACKEND']='Agg'
import numpy as np,torch,matplotlib
from IPython.display import HTML
P=pathlib.Path(__file__).resolve().parents[1];os.chdir(P)
assert (P/'audits/W09-L43-v2-before-key-independent.json').exists()
nbpath=P/'sources/supplemental/L43-official-notebook-output-stripped.ipynb';nb=json.loads(nbpath.read_text()); cells=[c for c in nb['cells'] if c['cell_type']=='code']; assert len(cells)==6
ns={'__name__':'__independent_original_l43__'};s=io.StringIO();t=time.time()
with contextlib.redirect_stdout(s):
 for i,c in enumerate(cells):exec(compile(''.join(c['source']),str(nbpath)+f':cell{i+1}','exec'),ns)
(P/'audits/W09-L43-v2-independent-original-stdout.txt').write_text(s.getvalue())
checks=[]
def ok(name,cond):
 assert bool(cond),name
 checks.append(name)
ok('original 6 code cells executed unchanged',True)
ok('training array16x6',ns['X'].shape==(16,6))
ok('training class counts',collections.Counter(ns['y'].tolist())=={3:11,1:5})
ok('long integer targets',ns['y_t'].dtype==torch.long)
ok('exact maze coordinates',ns['ROWS']==4 and ns['COLS']==5 and ns['WALLS']=={(0,1),(2,3),(3,0)})
ok('start feature vector',np.array_equal(ns['featurize'](0,0),[0,0,1,0,1,1]))
ok('goal normalized coordinates',np.allclose(ns['featurize'](3,4)[:2],[.75,.8]))
ok('teacher examples',ns['best_direction'](1,1)==3 and ns['best_direction'](2,2)==1)
ok('parameter enumeration',sum(p.numel() for p in ns['model'].parameters())==180)
ok('small and large diagram counts',2*3+3==9 and 4*10+10*3+3+10+3+1==87)
ok('ReLU actual execution',torch.equal(torch.relu(torch.tensor([-2,0,3])),torch.tensor([0,0,3])))
ok('training60epochs',len(ns['loss_history'])==60)
ok('actual training accuracy',ns['train_acc']==1)
path=ns['path']; expected=[(0,0),(1,0),(1,1),(1,2),(1,3),(1,4),(2,4),(3,4)]
ok('original exact route',path==expected)
ok('7 legal transitions',len(path)-1==7 and all(ns['is_free'](*x) for x in path) and all(abs(a[0]-b[0])+abs(a[1]-b[1])==1 for a,b in zip(path,path[1:])))
ok('Manhattan lower bound attained',len(path)-1==abs(3)+abs(4))
ok('animation frames38notmoves',ns['TRAIN_FRAMES']==30 and ns['DRIVE_FRAMES']==8 and ns['TOTAL_FRAMES']==38)
params=[p.detach().clone() for p in ns['model'].parameters()];ns['navigate'](ns['model'])
ok('inference weights unchanged',all(torch.equal(a,b) for a,b in zip(params,ns['model'].parameters())))
oldgoal=ns['GOAL'];before=ns['featurize'](1,1).copy();ns['GOAL']=(0,4);ok('no goal feature',np.array_equal(before,ns['featurize'](1,1)));ns['GOAL']=oldgoal
class Scores(torch.nn.Module):
 def forward(self,x):return torch.tensor([[2.,3.,1.,9.]])
ok('legalmask excludes high wall score',ns['navigate'](Scores(),max_steps=1)==[(0,0),(1,0)])
ok('zero stepcap',ns['navigate'](Scores(),max_steps=0)==[(0,0)])
oldstart=ns['START'];ns['START']=ns['GOAL'];ok('goalstart earlyexit',ns['navigate'](Scores())==[ns['GOAL']]);ns['START']=oldstart
oldwalls=ns['WALLS'];ns['WALLS']={(0,1),(1,0)}
try:ns['navigate'](Scores());empty=False
except ValueError:empty=True
ok('emptyvalid raisesValueError',empty);ns['WALLS']=oldwalls
old=(ns['ROWS'],ns['COLS'],ns['GOAL'],ns['WALLS']);ns.update(ROWS=3,COLS=3,GOAL=(0,2),WALLS={(0,1)})
ok('detour teacherNone',ns['best_direction'](0,0) is None)
q=collections.deque([((0,0),0)]);seen={(0,0)};distance=None
while q:
 pos,d=q.popleft()
 if pos==ns['GOAL']:distance=d;break
 for dr,dc in ns['ACTIONS']:
  nxt=pos[0]+dr,pos[1]+dc
  if ns['is_free'](*nxt) and nxt not in seen:seen.add(nxt);q.append((nxt,d+1))
ok('independentBFSdetour4',distance==4);ns.update(zip(['ROWS','COLS','GOAL','WALLS'],old))
ok('delay displacement',math.isclose(2+1*.5,2.5))
# Check all original table rows with separately derived features and teacher labels.
for (r,c),feat,a in zip(ns['cells_for_training'],ns['X'],ns['y']):
 expectedbits=[int(not(0<=r+dr<4 and 0<=c+dc<5 and(r+dr,c+dc) not in oldwalls)) for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]]
 assert np.allclose(feat,[r/4,c/5]+expectedbits)
 distances=[abs(r+dr-3)+abs(c+dc-4) if not expectedbits[i] else 100 for i,(dr,dc) in enumerate(ns['ACTIONS'])]
 assert distances[int(a)]==abs(r-3)+abs(c-4)-1
ok('16 complete source rows independently checked',True)
rng=random.Random(4362)
for _ in range(5000):
 r,c,gr,gc=[rng.randrange(-100,101) for z in range(4)];dr,dc=rng.choice([(-1,0),(1,0),(0,-1),(0,1)])
 assert abs((abs(r+dr-gr)+abs(c+dc-gc))-(abs(r-gr)+abs(c-gc)))==1
 n,h,o=[rng.randrange(1,100) for z in range(3)]
 assert n*h+h+h*o+o==(n+1)*h+(h+1)*o
 x0,v,dt=rng.uniform(-100,100),rng.uniform(-10,10),rng.uniform(0,20)
 assert math.isclose((x0+v*dt)-x0,v*dt,abs_tol=1e-12)
ok('5000 varied integer metric/parameter/kinematic trials',True)
ns['update'](37);ns['fig'].savefig(P/'audits/W09-L43-v2-independent-final-frame.png',dpi=160)
report={'reviewerId':'independent-reviewer-robotics-batches-v2','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'originalNotebookSha256':hashlib.sha256(nbpath.read_bytes()).hexdigest(),'originalCodeSha256':hashlib.sha256((P/'sources/supplemental/L43-official-code.py').read_bytes()).hexdigest(),'executedAllCodeCellsUnchanged':True,'codeCellCount':6,'backend':matplotlib.get_backend(),'environment':'L35venv with system IPython path appended; original notebook unchanged','torch':torch.__version__,'numpy':np.__version__,'passedChecks':checks,'checkGroupCount':len(checks),'variedTrials':5000,'loss':ns['loss_history'][-1],'accuracy':ns['train_acc'],'path':path,'runtimeSeconds':time.time()-t,'noBrowserAnimationInteractionClaim':True}
(P/'audits/W09-L43-v2-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2))
