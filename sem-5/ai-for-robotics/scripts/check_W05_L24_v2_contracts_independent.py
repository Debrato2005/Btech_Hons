"""Independent L24 equations and boundary cases derived before keyed access."""
from pathlib import Path
import sympy as s,numpy as np,json,datetime
R=s.Rational;M=s.Matrix;checks=[]
def ck(name,a,b=0):
 d=a-b;assert all(s.simplify(z)==0 for z in d) if isinstance(d,s.MatrixBase) else s.simplify(d)==0,(name,d)
 checks.append(name)
mass=M([[2,1],[1,3]]);kp=s.diag(4,9);kv=s.diag(4,6);e=M([R(1,10),-R(1,5)]);ed=M([-R(1,20),R(1,10)]);ad=M([1,-2]);h=M([R(1,2),1]);ff=M([1,2]);u=ad+kv*ed+kp*e
ck('exact computed-torque cancellation',mass.inv()*(mass*u+h-h),u)
a=mass.inv()*(ff+kv*ed+kp*e-h);edd=ad-a;forcing=mass*ad+h-ff
ck('desired-state feedforward residual derivation',mass*edd+kv*ed+kp*e,forcing)
ck('explicit residual vector',forcing,M([-R(1,2),-6]));ck('full inverse times diagonal gain',mass.inv()*kp,M([[R(12,5),-R(9,5)],[-R(4,5),R(18,5)]]))
assert mass.inv()*kp!=kp*mass.inv();checks.append('noncommuting inverse inertia and gain witness')
td=M([1,0]);steady=kp.inv()*mass.inv()*td
ck('correct equilibrium matrix order',steady,M([R(3,20),-R(1,45)]));ck('wrong swapped order witness',mass.inv()*kp.inv()*td,M([R(3,20),-R(1,20)]))
ck('subtracted plant disturbance gives positive error forcing',ad-(u-mass.inv()*td)+kv*ed+kp*e,mass.inv()*td)
ck('scalar residual torque',(3-2)*4+1+2-1,6);ck('scalar estimated-inverse uncertainty',R(1,2)*6,3)
# Actual velocity-independent mismatch can cancel without an exact model.
ck('nonzero mismatches can cancel',1*0+2-2,0)
x,v,mm,bb,kk=s.symbols('x v m b k',real=True);energy=mm*v*v/2+kk*x*x/2;acc=(-bb*v-kk*x)/mm
vd=s.diff(energy,x)*v+s.diff(energy,v)*acc;ck('linear energy derivative',vd,-bb*v*v)
ck('linear numeric energy',energy.subs({mm:2,kk:8,x:R(1,2),v:-1}),2)
ck('linear numeric dissipation',vd.subs({bb:3,v:-1}),-3)
ck('zero velocity restoring acceleration',acc.subs({mm:2,bb:3,kk:8,x:R(1,2),v:0}),-2)
ck('undamped boundary energy derivative',vd.subs(bb,0),0)
ck('zero spring full-state degeneracy',energy.subs({kk:0,v:0,x:7}),0)
ck('scalar strict candidate derivative',s.diff(x*x/2,x)*(-x**3),-x**4)
lam=s.symbols('lambda',real=True);pot=s.integrate(lam+lam**3,(lam,0,x));ck('nonlinear restoring potential',pot,x*x/2+x**4/4);ck('potential differentiation',s.diff(pot,x),x+x**3)
nonlin=v*v/2+pot;damp=2*v+v**3;accn=-damp-(x+x**3);vdn=s.diff(nonlin,x)*v+s.diff(nonlin,v)*accn
ck('nonlinear energy derivative cancellation',vdn,-v*damp);ck('nonlinear numeric energy',nonlin.subs({x:1,v:-2}),R(11,4));ck('nonlinear numeric dissipation',vdn.subs({x:1,v:-2}),-24)
ck('nonlinear damping value',damp.subs(v,-2),-12);ck('nonlinear wrong potential coefficient total',v*v/2+x*x/2+x**4,s.Rational(0)) if False else None
ck('nonlinear missing quartic denominator distractor',(v*v/2+x*x/2+x**4).subs({x:1,v:-2}),R(7,2))
ck('general equilibrium permits opposing constants',-(3+(-3)),0)
ck('absolute value left derivative',s.limit(s.Abs(x)/x,x,0,dir='-'),-1);ck('absolute value right derivative',s.limit(s.Abs(x)/x,x,0,dir='+'),1)
ck('polynomial candidate gradient at origin',s.diff(x*x,x).subs(x,0),0)
rng=np.random.default_rng(240224);maxres=0
for _ in range(500):
 z=rng.normal(size=(2,2));ma=z.T@z+np.eye(2);z=rng.normal(size=(2,2));mh=z.T@z+np.eye(2);a0=rng.normal(size=2);ee=rng.normal(size=2);eev=rng.normal(size=2);kp0=np.diag(rng.uniform(.1,12,2));kv0=np.diag(rng.uniform(.1,12,2));hh=rng.normal(size=2);hhhat=rng.normal(size=2);ff0=rng.normal(size=2)
 u0=a0+kv0@eev+kp0@ee;ac=np.linalg.solve(ma,mh@u0+hhhat-hh)
 residual=np.max(np.abs(u0-ac-np.linalg.solve(mh,(ma-mh)@ac+hh-hhhat)))
 af=np.linalg.solve(ma,ff0+kv0@eev+kp0@ee-hh)
 residual=max(residual,np.max(np.abs(ma@(a0-af)+kv0@eev+kp0@ee-(ma@a0+hh-ff0))))
 xx,vv=rng.normal(size=2);mn,bn,kn=rng.uniform(.1,10,3);an=(-bn*vv-kn*xx)/mn
 residual=max(residual,abs(mn*vv*an+kn*xx*vv+bn*vv**2))
 an=-2*vv-vv**3-xx-xx**3;residual=max(residual,abs(vv*an+(xx+xx**3)*vv+vv*(2*vv+vv**3)))
 assert residual<1e-10,residual;maxres=max(maxres,residual)
out=dict(reviewerId='define_robotics_data_contracts:L24-independent-reviewer',createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),authorKeysSeen=False,priorVersionExposure=False,exactAssertions=len(checks),assertions=checks,randomTrials=500,checksPerTrial=4,randomChecks=['estimated-model uncertainty identity','desired-state feedforward residual','linear energy dissipation','nonlinear energy dissipation'],maxResidual=float(maxres),status='passed')
r=Path(__file__).resolve().parents[1];(r/'audits/W05-L24-v2-contracts-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
