"""Independent reviewer arithmetic and identities; does not import author checks or modify questions."""
import json, random, math, pathlib
import sympy as s
from datetime import datetime, timezone
out=[]
def check(name, ok, detail):
 out.append({'name':name,'passed':bool(ok),'detail':detail})
R=s.Rational
check('coupled_inertial_torque',s.Matrix([[2,1],[1,3]])*s.Matrix([1,0])==s.Matrix([2,1]),'M*(1,0)=(2,1) N m')
check('partitioned_scalar',2*3+1+4+R(1,2)==R(23,2),'11.5 N m')
check('error_and_feedback',R(8,10)-1==R(-1,5) and 25*R(-1,5)==-5,'E=-.2; KpE=-5')
z=s.symbols('z');check('critical_roots',s.expand((z+3)**2)==z*z+6*z+9,'s=-3 repeated')
check('virtual_acceleration',1+16*R(1,10)+8*R(-2,10)==1,'1 rad/s^2')
check('sample_period',R(1,500)*1000==2,'2 ms')
check('feedforward_torque',5+20*R(1,10)+3*R(-2,10)==R(64,10),'6.4 N m')
check('frozen_inertia_roots',s.simplify(4*(-1+s.I*s.sqrt(3))**2+8*(-1+s.I*s.sqrt(3))+16)==0,'-1 +/- i sqrt(3)')
check('dual_rate',10/1==10 and R(1,10)*1000==100,'10 updates, 100 Hz')
M=s.Matrix([[2,1],[1,2]]);K=s.diag(2,4);d=s.Matrix([3,0]);E=K.inv()*M.inv()*d
check('steady_order',E==s.Matrix([1,R(-1,4)]),'Kp^-1 M^-1 d=(1,-.25)')
check('reversed_order_distractor',M.inv()*K.inv()*d==s.Matrix([1,R(-1,2)]),'Wrong order gives (1,-.5), distinct')
check('diagonal_only_distractor',s.diag(R(1,2),R(1,4))*s.diag(R(1,2),R(1,2))*d==s.Matrix([R(3,4),0]),'Ignoring inertia coupling gives (.75,0)')
check('uncertainty_scalar',((3-2)*4+1+2-1)/2==3,'Estimated inverse, not actual inverse')
check('pid_torque',20*R(1,10)+3*R(-2,10)+4*R(1,2)==R(34,10),'3.4 N m')
check('integral_torque',R(1,5)*3*5==3,'3 N m')
check('pd_gravity',(5-3)/20==.1,'0.1 rad')
check('pid_gravity',(5-3)/4==.5,'0.5 rad s')
x,u,m,b,k=s.symbols('x u m b k',positive=True)
v=m*u*u/2+k*x*x/2;f=s.Matrix([u,(-b*u-k*x)/m]);vd=s.Matrix([s.diff(v,x),s.diff(v,u)]).dot(f)
check('linear_energy_identity',s.simplify(vd+b*u*u)==0,'grad(v).f=-b*u^2')
check('linear_energy_numbers',v.subs({m:2,k:8,x:R(1,2),u:-1})==2 and vd.subs({b:3,u:-1})==-3,'2 J,-3 W')
check('linear_wrong_rationale_counterexample',(-b*u*x).subs({b:3,u:-1,x:R(1,2)})==R(3,2),'Author o4 rationale yields +1.5, not option -1.5; flag explanation/calculation')
check('undamped_boundary',vd.subs(b,0)==0,'Conserved nonzero energy does not converge')
check('zero_stiffness_boundary',v.subs({k:0,u:0})==0,'Candidate zero for every x when u=0')
X,U,L=s.symbols('X U L',real=True);pot=s.integrate(L+L**3,(L,0,X));nv=U*U/2+pot;nf=s.Matrix([U,-(2*U+U**3)-(X+X**3)]);nvd=s.simplify(s.Matrix([s.diff(nv,X),s.diff(nv,U)]).dot(nf))
check('nonlinear_potential',s.expand(pot-X**2/2-X**4/4)==0,'Integral x+x^3 -> x^2/2+x^4/4')
check('nonlinear_energy_identity',s.simplify(nvd+U*(2*U+U**3))==0,'-u b(u)')
check('nonlinear_numbers',nv.subs({X:1,U:-2})==R(11,4) and nvd.subs({U:-2})==-24,'2.75,-24')
check('nonlinear_turning_accel',nf[1].subs({X:-1,U:0})==2,'+2')
check('nonlinear_option_3_explanation',2+(1+1)!=R(7,2) and 2+(1+1)/2!=R(7,2),'Using k(1) or half k(1) gives4 or3, not option3.5; explain actual missing quartic divisor')
check('scalar_cubic_lyapunov',s.diff(X**2/2,X)*(-X**3)==-X**4,'Strict negative away from origin')
check('nonproper_sublevel',s.simplify((X*X+1)/(1+X*X))==1,'v(x,y)=(x^2+y^2)/(1+x^2) is positive definite but has unbounded level y=1; positivity alone does not make sublevels compact')
# Independent, varied exact 2x2 SPD instances: torque cancellation, feedforward residual,
# resisting-disturbance order, estimated-model residual. No author random seeds/scripts.
rng=random.Random(202610191855)
for i in range(500):
 A=s.Matrix(2,2,[rng.randint(-4,4) for _ in range(4)]);B=s.Matrix(2,2,[rng.randint(-4,4) for _ in range(4)])
 M=A.T*A+s.eye(2);H=B.T*B+s.eye(2);K=s.diag(rng.randint(1,9),rng.randint(1,9));D=s.diag(rng.randint(1,9),rng.randint(1,9))
 vec=lambda:s.Matrix([rng.randint(-5,5),rng.randint(-5,5)])
 e,ed,ad,h,hh,ff,dist=vec(),vec(),vec(),vec(),vec(),vec(),vec();virtual=ad+D*ed+K*e
 assert M.inv()*(M*virtual+h-h)==virtual
 actual=M.inv()*(ff+K*e+D*ed-h); eacc=ad-actual
 assert M*eacc+D*ed+K*e==M*ad+h-ff
 actual=M.inv()*(H*virtual+hh-h)
 assert ad-actual+D*ed+K*e==H.inv()*((M-H)*actual+h-hh)
 ss=K.inv()*M.inv()*dist; assert K*ss==M.inv()*dist
check('500_varied_exact_matrix_cases',True,'SPD matrices, coupled/noncommuting gains, arbitrary signed vectors; all four identities pass')
# Positive/negative arguments, zero velocity, restoring/damping signs and invariant-set implications.
for i in range(500):
 xx=R(rng.randint(-100,100),10);uu=R(rng.randint(-100,100),10)
 assert nv.subs({X:xx,U:uu})>=0
 assert nvd.subs({U:uu})<=0
 assert bool(nvd.subs({U:uu})==0)==bool(uu==0)
 if xx!=0 and uu==0: assert nf[1].subs({X:xx,U:uu})!=0
check('500_signed_nonlinear_cases',True,'Nonlinear energy and dissipation signs, including zero states and negative arguments')
report={'reviewerId':'independent-reviewer-robotics-batches-v2','checkedAt':datetime.now(timezone.utc).isoformat(),'scope':'Independently derived fixed questions and varied domain identities; no generators claimed','checks':out,'passed':sum(q['passed'] for q in out),'failed':sum(not q['passed'] for q in out),'authorScriptsReadOrRun':False}
p=pathlib.Path('audits/W05-L24-independent-computations.json');assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print(report['passed'],'passed',report['failed'],'failed')
