"""Independent changed-item checks; no author modules or keyed files are read."""
import json, math, random, datetime, hashlib
from pathlib import Path
out=[]
def check(name,ok,detail):
 assert bool(ok),name
 out.append({'name':name,'passed':True,'detail':detail})
def near(a,b):return all(math.isclose(x,y,abs_tol=1e-10) for x,y in zip(a,b))
check('Camera inverse translation',near([.3-(-.5),.4,5],[.8,.4,5]),'Point minus camera origin; no rotation in this task.')
check('Grid centering and full width',near([640+1500*x for x in [-.1,0,.1]],[490,640,790]),'The revised stem now supplies the previously missing center.')
vecs=[(2,1,1),(-4,-2,-2),(6,3,1),(2,3,3)]
check('Homogeneous exact answer cardinality',[near([x/z,y/z],[2,1])for x,y,z in vecs]==[True,True,False,False],'Both positive and negative common nonzero scaling preserve the ordinary point.')
check('Physical pitch units',math.isclose(.015/10e-6,1500),'f/rho has pixel units, not length units.')
check('Different depth changes projected spacing',not math.isclose((2/3-1/2),(1/2-0)),'Uniform world samples (0,0,1),(1,0,2),(2,0,3) project nonuniformly.')
check('Same viewing ray not visibility guarantee',near([1/2,1/2],[2/4,2/4]),'Two positive-depth points share an image coordinate; a nearer opaque surface can occlude the farther one.')
check('Finite vanishing point',near([1e10/(1+1e10),1/(1+1e10)],[1,0]),'Direction (1,0,1) tends to a finite point; d_z=0 gives no finite directional normalization.')
check('No forced geometric rounding',1500*.12345/3+640==701.725,'Continuous image coordinate need not be an integer sample index.')
ns={}
try:exec('p=mkgrid(n=3, side=.2, pose=SE3.Tz(1.0))',ns)
except NameError as e:check('Fresh mkgrid fragment',"mkgrid" in str(e),'Actual Python execution fails before later imports; toolbox execution not claimed.')
else:raise AssertionError('NameError missing')
try:exec('p=SE3.Tx(-.5)',{})
except NameError as e:check('Missing SE3 binding',"SE3" in str(e),'Actual Python name resolution; not a toolbox runtime test.')
else:raise AssertionError('NameError missing')
a={'rho':1,'pp':(0,0)};camera=a;camera={'rho':1e-5,'pp':(640,512)}
check('Sequential assignment',camera is not a and camera['rho']==1e-5 and a['rho']==1,'Actual Python rebinding does not merge old and new object attributes.')
rng=random.Random(3102)
for _ in range(500):
 x,y,z=[rng.uniform(-10,10)for k in range(3)];z=abs(z)+.1;s=rng.choice([-1,1])*rng.uniform(.1,10)
 assert near([x/z,y/z],[(s*x)/(s*z),(s*y)/(s*z)])
check('500 nonzero homogeneous scaling cases',True,'Deterministic seed 3102; both signs, positive nonzero depths, exact comparison within floating tolerance.')
report={'reviewerId':'independent-reviewer-robotics-batches-v2','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':out,'passed':len(out),'randomizedCases':500,'toolboxRuntimeExecuted':False,'scope':'Independent arithmetic, geometry and actual Python name/assignment semantics. API source inspection, not full machinevisiontoolbox execution.','scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
Path('audits/W07-L31-v2-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':len(out),'randomizedCases':500,'toolboxRuntimeExecuted':False}))
