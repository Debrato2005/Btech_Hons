"""Independent L31 numerical oracle. Does not import author code or read author keys.
Toolbox calls are NOT executed: machinevisiontoolbox/spatialmath are unavailable.
"""
import json, math, hashlib, sys, platform, importlib.util
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

checks=[]
def check(name, condition, detail):
    checks.append({'name':name,'passed':bool(condition),'detail':detail})
    assert condition, name

def project(P, f=.015, pitch=(1.,1.), pp=(0.,0.), R=None, t=None):
    P=np.asarray(P,dtype=float)
    if P.ndim==1: P=P[:,None]
    R=np.eye(3) if R is None else np.asarray(R)
    t=np.zeros(3) if t is None else np.asarray(t)
    C=R.T@(P-t[:,None])
    with np.errstate(divide='ignore',invalid='ignore'):
        uv=C[:2]/C[2]*np.asarray([f/pitch[0],f/pitch[1]])[:,None]+np.asarray(pp)[:,None]
    return uv,C

def inside(uv,z,W=1280,H=1024):
    return (z>0)&np.isfinite(uv).all(axis=0)&(uv[0]>=0)&(uv[0]<W)&(uv[1]>=0)&(uv[1]<H)

check('weighted spectral response',np.isclose(np.sum(np.array([8,4])*[.25,.5]*[.5,1]),3),'Two equal-weight bands give 1+2=3 relative units.')
M=np.array([[1,0,0,1],[0,1,0,1],[0,0,1,1.]])
a=np.array([1,1,1,1.]);b=np.array([.5,.5,.5,1.5])
check('nonunique spectral reduction',np.allclose(M@a,M@b) and not np.allclose(a,b),'Two different nonnegative four-band spectra have identical three responses.')
check('response linearity',np.allclose(M@(2*a),2*(M@a)),'Doubling received spectrum doubles each fixed linear channel.')
check('reflectance zero and unit bounds',np.all(np.array([8,4])*[0,1]==[0,4]),'R=0 suppresses and R=1 preserves incident contribution in the simplified product.')
check('Bayer missing channels',4*3-4==8,'Four scalar samples leave eight of twelve channel entries to estimate.')
q=lambda v:int(np.clip(np.floor(8*v),0,7))
check('ADC supplied floor',q(.6)==4,'floor(4.8)=4, not nearest-integer 5.')
check('ADC clipping boundaries',[q(v)for v in [-1,0,.124999,.125,.999999,1,2]]==[0,0,0,1,7,7,7],'Explicit saturation, zero and bin transition; no unavailable source quantizer inferred.')
check('white balance gains',np.allclose(np.array([.5,.4,.25])*[2,2.5,4],1),'Channel reciprocals neutralize the stated patch.')
check('gamma value and endpoints',np.allclose(np.sqrt([0,.25,1]),[0,.5,1]),'Supplied square-root law only, not a complete sRGB transfer specification.')
C=np.array([[1,0,0,.1],[.2,.8,0,0],[0,0,2,0]])
check('affine color correction',np.allclose(C@[.4,.5,.2,1],[.5,.48,.4]),'Three row dot products, including first-row offset.')
f,do=50,200;di=1/(1/f-1/do)
check('thin lens exact example',np.isclose(di,200/3),'Positive real distances in mm.')
check('signed magnification',np.isclose(-di/do*30,-10),'Inverted image sign retained.')
check('far-object focal limit',abs(1/(1/50-1/1e12)-50)<1e-8,'Real image distance approaches f from above.')
check('focus boundary scope',np.isclose(1/50-1/50,0) and 1/(1/50-1/25)<0,'Object at f has no finite image; object inside f needs signed virtual-image convention.')
uv,_=project([.2,-.1,2],f=.02)
check('metric projection',np.allclose(uv[:,0],[.002,-.001]),'Positive front virtual plane convention.')
check('homogeneous normalization',np.allclose(np.array([.004,-.002])/2,[.002,-.001]),'The supplied m²/m components yield metres.')
vectors=np.array([[6,3,3],[2,1,1],[-4,-2,-2],[6,3,1],[2,3,3.]])
check('homogeneous answer cardinality',np.all(np.all(np.isclose(vectors[:, :2]/vectors[:,2,None],[2,1]),axis=1)==[True,True,True,False,False]),'Exactly o1 and o2 normalize to the original point; order-independent set.')
uv0,_=project([1,1,0],f=.02)
check('zero-depth boundary',not np.isfinite(uv0).all(),'A nonzero lateral point at Z=0 has no finite ordinary coordinate.')
_,pc=project([.3,.4,5],t=[-.5,0,0])
check('inverse translation',np.allclose(pc[:,0],[.8,.4,5]),'Subtract camera origin, not add it.')
R=np.array([[0,-1,0],[1,0,0],[0,0,1.]])
uv,pc=project([1,3,4],f=.02,pitch=(1e-5,2e-5),pp=(320,240),R=R,t=[1,2,0])
check('inverse rotation and translation',np.allclose(pc[:,0],[1,0,4]),'R transpose applied after subtracting t.')
check('composed projection and bounds',np.allclose(uv[:,0],[820,240]) and not inside(uv,pc[2],800,600)[0],'fx=2000, fy=1000; outside horizontal sensor bound.')
check('sensor physical size',np.allclose(np.array([1280,1024])*10e-6,[.0128,.01024]),'12.8 by 10.24 mm under the stipulated contiguous-pixel model.')
check('metric-to-pixel anisotropy',np.allclose(np.array([1,-.5])/[.01,.02]+[320,240],[420,215]),'Consistent millimetres and unequal pitches.')
check('intrinsic focal ratios',np.allclose(.015/np.array([1e-5,2e-5]),[1500,750]),'Convert all physical lengths to metres.')
check('nearest-index example',np.all(np.rint([100.4,200.6])==[100,201]),'No half-integer tie occurs; this does not impose rounding on general geometry.')
metric,_=project([.3,.4,5]);moved,_=project([.3,.4,5],t=[-.5,0,0]);pixel,_=project([.3,.4,5],pitch=(1e-5,1e-5),pp=(640,512))
check('source metric and conversion',np.allclose(metric[:,0],[.0009,.0012]) and np.allclose(metric[:,0]*1000,[.9,1.2]),'Printed parenthetical 1.5/2.0 mm is incorrect.')
check('source translated metric',np.allclose(moved[:,0],[.0024,.0012]),'Before pixel-camera reassignment.')
check('source pixel output',np.allclose(pixel[:,0],[730,632]),'1500-pixel focal length and 640/512 principal point.')
uvtest=np.array([[1279.5,1280,640,100],[1023.5,100,512,1024.]])
check('continuous bounds',np.array_equal(inside(uvtest,np.array([2,2,-2,2])),[True,False,False,False]),'Positive depth, half-open continuous bounds, no premature rounding.')
P=np.column_stack([[0,0,10],[10,10,10],[.3,.4,5]])
check('actual NumPy column_stack',P.shape==(3,3) and np.allclose(P[:,1],[10,10,10]),'Executed the displayed NumPy operation, not toolbox projection.')
p,pc=project(P,pitch=(1e-5,1e-5),pp=(640,512))
check('three-point output and mask',np.allclose(p,[[640,2140,730],[512,2012,632]]) and np.array_equal(inside(p,pc[2]),[True,False,True]),'Independent NumPy projection reproduces all displayed values.')
xs=np.array([-.1,0,.1]);G=np.array([[x,y,1]for x in xs for y in xs]).T
g,_=project(G,pitch=(1e-5,1e-5),pp=(640,512));gm,_=project(G,pitch=(1e-5,1e-5),pp=(640,512),t=[-.25,0,0])
check('centered grid coordinates',np.allclose(np.unique(g[0]),[490,640,790]),'Requires center X=0, which P0949-Q03 omits from its standalone stem.')
shifted=G+np.array([.1,0,0])[:,None];gs,_=project(shifted,pitch=(1e-5,1e-5),pp=(640,512))
check('missing grid center counterexample',np.allclose(np.unique(gs[0]),[640,790,940]),'Same side, depth and calibration but different allowed horizontal center changes answer.')
check('grid camera shift',np.allclose(gm-g,np.array([375,0])[:,None]),'Every point has equal fixed depth one metre.')
check('cube face parallax',np.allclose(np.round(375/np.array([.9,1.1]),2),[416.67,340.91]),'Independent two-decimal values remain distinct.')
s=np.array([0,1,10,1e8]);p1=np.vstack([s/(1+s),np.zeros_like(s)]);p2=np.vstack([s/(1+s),1/(1+s)])
check('coplanar parallel counterexample',np.allclose(p2[1],1-p2[0]) and np.allclose(p1[:,-1],[1,0]) and np.allclose(p2[:,-1],[1,0]),'Image lines y=0 and y=1-x are not parallel, although spatial lines are coplanar and parallel.')
check('finite vanishing pixel',np.allclose(.02*np.array([2,1])/4/1e-5+[640,512],[1640,1012]),'Finite projective point may lie beyond the 1280-pixel sensor width.')
check('image-parallel directions',np.allclose(np.cross([1,2,0],[2,4,0]),0),'dz=0 yields projected line directions proportional to (dx,dy), excluding degeneracy.')
ns={};exec('f=0.015;\nP=[0.3,0.4,5.0]\n',ns)
check('Python literal and semicolon execution',ns['f']==.015 and ns['P']==[.3,.4,5.],'Actual Python semantics, no camera mock.')
try:exec('SE3.Tx(-0.5)',{})
except NameError as e:missing=str(e)
check('undefined SE3 expression',"SE3" in missing,'Only isolated name lookup executed; not a claim that the full toolbox fragment ran.')
try:exec('P_grid = mkgrid(n=3, side=0.2, pose=SE3.Tz(1.0))',{})
except NameError as e:missing=str(e)
check('first grid statement fresh namespace',"mkgrid" in missing,'Actual initial statement fails before any lower import; unavailable toolbox is not installed.')
rng=np.random.default_rng(7312026)
for i in range(500):
    theta=rng.uniform(-np.pi,np.pi);R=np.array([[np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1]])
    t=rng.normal(size=3);Pc=np.r_[rng.normal(size=2),rng.uniform(.1,20)];Pw=R@Pc+t
    f=rng.uniform(.001,.2);w,h=rng.uniform(1e-6,1e-4,size=2);pp=rng.normal(size=2)*100
    uv,Cp=project(Pw,f,(w,h),pp,R,t)
    T=np.eye(4);T[:3,:3]=R;T[:3,3]=t;K=np.array([[f/w,0,pp[0]],[0,f/h,pp[1]],[0,0,1.]])
    z=K@np.eye(3,4)@np.linalg.inv(T)@np.r_[Pw,1]
    assert np.allclose(Cp[:,0],Pc) and np.allclose(uv[:,0],z[:2]/z[2])
    scale=rng.uniform(.1,10);v2,_=project(scale*Pc,f,(w,h),pp)
    assert np.allclose(uv,v2)
check('500 varied rigid-camera cases',True,'Independent direct R-transpose calculation agrees with 4x4 inverse/composed KQ transform; positive-depth ray scale invariance and unequal pitches checked. Seed 7312026.')
report={'reviewerId':'independent-reviewer-robotics-batches-v2','executedAt':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),'numpy':np.__version__,'checks':checks,'passed':len(checks),'failed':0,'randomCases':500,'seed':7312026,'limitations':{'machinevisiontoolbox':importlib.util.find_spec('machinevisiontoolbox') is not None,'spatialmath':importlib.util.find_spec('spatialmath') is not None,'toolboxRuntimeExecuted':False,'authorScriptsReadOrExecuted':False,'qualification':'Independent equations and NumPy statements executed. Camera/plot API behavior checked separately in official source, not called locally. No dependency installation attempted by reviewer.'}}
Path('audits/W07-L31-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'failed':0,'variedCases':500,'toolboxRuntimeExecuted':False}))
