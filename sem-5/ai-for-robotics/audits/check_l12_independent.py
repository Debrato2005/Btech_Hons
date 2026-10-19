"""Independent reviewer computations, not author checks. No question writes."""
import json,math,pathlib,datetime
import numpy as np
RZ=np.array([[0,-1,0],[1,0,0],[0,0,1]],float);cross=np.cross;arr=lambda a:np.array(a,float)
checks=[]
def check(name,actual,expected):
 assert np.allclose(actual,expected,atol=1e-10,rtol=1e-10),(name,actual,expected)
 checks.append({'name':name,'actual':np.asarray(actual).tolist(),'expected':np.asarray(expected).tolist(),'passed':True})
check('Q006_force',3*arr([2,-1,0]),[6,-3,0])
I=np.diag([2,3,4]);w=arr([1,2,3]);alpha=arr([.5,-1,2]);check('Q010_H',I@w,[2,6,12]);check('Q010_gyro',cross(w,I@w),[6,-6,2]);check('Q010_moment',I@alpha+cross(w,I@w),[7,-9,10])
check('Q009_zero',cross([0,0,0],I@arr([0,0,0])),[0,0,0]);check('Q009_principal',cross([0,2,0],I@arr([0,2,0])),[0,0,0]);check('Q009_isotropic',cross(w,3*w),[0,0,0]);assert np.linalg.norm(cross(w,I@w))>0
check('Q013_angular_velocity',arr([1,0,2])+3*arr([0,0,1]),[1,0,5]);check('Q014_angular_acceleration',cross([1,0,0],[0,0,2])+arr([0,0,3]),[0,-2,3])
check('Q017_COM_acceleration',arr([1,0,0])+cross([0,0,3],[.5,0,0])+cross([0,0,2],cross([0,0,2],[.5,0,0])),[-1,1.5,0]);check('Q019_prismatic_extra',2*cross([1,0,0],[0,0,2])+arr([0,0,3]),[0,-4,3])
F=arr([0,2,0]);N=arr([0,0,1]);fc=arr([0,3,0]);nc=arr([0,0,2]);r=arr([.5,0,0]);p=arr([1,0,0]);check('Q026_force',F+fc,[0,5,0]);check('Q026_moment',N+nc+cross(r,F)+cross(p,fc),[0,0,7]);check('Q026_subtract_child_with_arms_retained',N-nc+cross(r,F)-cross(p,fc),[0,0,-3])
check('Q027_rotated_moment',arr([0,0,1])+RZ@arr([0,0,3])+cross(r,[0,1,0])+cross(p,RZ@arr([2,0,0])),[0,0,6.5]);check('Q027_inverse_rotation_distractor',arr([0,0,1])+RZ.T@arr([0,0,3])+cross(r,[0,1,0])+cross(p,RZ.T@arr([2,0,0])),[0,0,2.5]);check('Q029_projections',[np.dot([3,4,-2],[0,0,1]),np.dot([5,-1,6],[0,0,1])],[-2,6]);check('Q030_loop_targets',[i+1 for i in range(6)],[1,2,3,4,5,6]);check('Q032_gravity_sign',-arr([0,0,-9.81]),[0,0,9.81]);check('Q035_holding_torque',cross([.5,0,0],-2*arr([0,-9.81,0])),[0,0,9.81]);check('Q040_control',2+.5*(100*.02+10*(-.1)),2.5)
# Nonidentical discrete point-mass distributions with identical mass,COM,inertia.
a=[(1/6,arr(v)) for v in [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]]]
b=[(.5,arr([0,0,0]))]+[(m/2,math.sqrt(2)*v) for m,v in a]
def moments(dist):
 return np.array([sum(m for m,_ in dist),*sum((m*v for m,v in dist),np.zeros(3)),*sum((m*(np.dot(v,v)*np.eye(3)-np.outer(v,v)) for m,v in dist),np.zeros((3,3))).ravel()])
check('Q003_nonunique_mass_distribution',moments(a),moments(b))
# Independent balance identity and coordinate covariance across nonidentity rotations.
rng=np.random.default_rng(120319);cases=0;maxres=0
for _ in range(1000):
 Q,_=np.linalg.qr(rng.normal(size=(3,3)));Q[:,0]*=np.linalg.det(Q)
 F,N,fc,nc,r,p=rng.normal(size=(6,3)); f=F+Q@fc;n=N+Q@nc+cross(r,F)+cross(p,Q@fc)
 recoveredN=n-Q@nc-cross(r,f)-cross(p-r,Q@fc)
 assert np.allclose(recoveredN,N,atol=1e-10)
 assert np.allclose(Q@cross(fc,nc),cross(Q@fc,Q@nc),atol=1e-10)
 maxres=max(maxres,float(np.linalg.norm(recoveredN-N)));cases+=1
# Rigid moving point derivation checked by finite differences, including relative slide Coriolis2.
# Rz(t)r(t) with r(t)=(1+t,0,0); at t=0, rddot=(-1,2,0).
h=1e-4
def point(t):return np.array([(1+t)*math.cos(t),(1+t)*math.sin(t),0])
afd=(point(h)-2*point(0)+point(-h))/h**2
assert np.allclose(afd,[-1,2,0],atol=3e-8)
report={'reviewerId':'independent-reviewer-robotics-batches-v2','runAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exactExampleChecks':checks,'randomNonidentityBalanceAndRotationCases':cases,'randomSeed':120319,'maximumMomentBalanceResidual':maxres,'movingPointFiniteDifference':{'h':h,'result':afd.tolist(),'expected':[-1,2,0],'passed':True},'allPassed':True,'scope':'Fixed authored examples plus mathematical identities; no claim of runtime app or numerical-family generator validation. Q026 computation diagnoses the incomplete o3 rationale.'}
pathlib.Path('audits/W03-L12-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n');print(len(checks),'example/boundary checks;',cases,'nonidentity cases; derivative check passed')
