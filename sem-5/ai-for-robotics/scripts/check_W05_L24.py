#!/usr/bin/env python3
"""Author calculations only. Does not establish independent source review."""
import sympy as s,random,math
records=[]
def ck(name,condition,result):
 assert bool(condition),name
 records.append(dict(id='L24-CHECK-'+str(len(records)+1).zfill(2),check=name,result=result,status='passed',independentReview=False))
M=s.Matrix([[2,1],[1,3]]);a=s.Matrix([1,0]);ck('Coupled inertia torque',M*a==s.Matrix([2,1]),[2,1])
ck('Partitioned torque',2*3+1+4+s.Rational(1,2)==s.Rational(23,2),'11.5 N m')
ck('Error sign and gain',s.Rational(4,5)-1==-s.Rational(1,5) and 25*(-s.Rational(1,5))==-5,'E=-0.2, virtual correction=-5')
z=s.symbols('z');ck('Critical roots',s.factor(z*z+6*z+9)==(z+3)**2,'Repeated root -3')
ck('Servo sum',1+8*(-s.Rational(1,5))+16*s.Rational(1,10)==1,'1 rad/s^2')
ck('Sampling reciprocal',1/s.Integer(500)==s.Rational(2,1000),'2 ms')
ck('Feedforward sum',5+20*s.Rational(1,10)+3*(-s.Rational(1,5))==s.Rational(32,5),'6.4 N m')
mm,ad,h,tff,kp,kv,e,ed,edd=s.symbols('m ad h tff kp kv e ed edd')
# actual plant expressed using desired-minus-actual error
plant=mm*(ad-edd)+h-(tff+kp*e+kv*ed)
rhs=mm*ad+h-tff
ck('Feedforward residual exact algebra',s.expand(plant-(rhs-(mm*edd+kp*e+kv*ed)))==0,'M Edd+Kv Ed+Kp E=M ad+h-tau_ff')
ck('Frozen-inertia poles',s.simplify(((-1+s.sqrt(3)*s.I)**2+2*(-1+s.sqrt(3)*s.I)+4))==0,'-1 +/- i sqrt(3)')
ck('Dual-rate schedule',10/1==10 and 1/s.Rational(10,1000)==100,'10 feedback updates per 100-Hz model period')
M=s.Matrix([[2,1],[1,2]]);K=s.diag(2,4);d=s.Matrix([3,0]);ess=K.inv()*M.inv()*d
ck('Disturbance equilibrium and order',ess==s.Matrix([1,-s.Rational(1,4)]) and M.inv()*K.inv()*d==s.Matrix([1,-s.Rational(1,2)]),'Correct (1,-1/4); reversed order (1,-1/2)')
ck('Uncertainty scalar',(s.Rational(1,2))*((3-2)*4+1+2-1)==3,'3 rad/s^2')
ck('PID torque',20*s.Rational(1,10)+3*(-s.Rational(1,5))+4*s.Rational(1,2)==s.Rational(17,5),'3.4 N m')
ck('Integral error accumulation',5*s.Rational(1,5)*3==3,'z=0.6 rad s; torque=3 N m')
ck('Gravity PD balance',(5-3)/s.Integer(20)==s.Rational(1,10),'0.10 rad')
ck('Gravity integral balance',(5-3)/s.Integer(4)==s.Rational(1,2),'0.5 rad s')
x,u,m,b,k=s.symbols('x u m b k',real=True,nonzero=True);v=m*u*u/2+k*x*x/2;acc=(-b*u-k*x)/m
vd=s.simplify(s.diff(v,x)*u+s.diff(v,u)*acc)
ck('Linear energy chain rule',vd==-b*u*u,'v_dot=-b u^2')
ck('Linear numerical energy/rate',v.subs({m:2,k:8,x:s.Rational(1,2),u:-1})==2 and vd.subs({b:3,u:-1})==-3,'2 J, -3 W')
ck('Linear turning-point acceleration',acc.subs({m:2,b:3,k:8,x:s.Rational(1,2),u:0})==-2,'At x=.5,u=0 acceleration=-2 not equilibrium')
ck('Undamped energy',s.simplify(vd.subs(b,0))==0,'b=0 conserves energy')
ck('Zero-stiffness loss of positive definiteness',v.subs({k:0,u:0,x:1})==0,'Nonzero position with zero velocity has zero candidate')
xx=s.symbols('xx',real=True); vv=xx**2/2
ck('Nonlinear scalar strict derivative',s.diff(vv,xx)*(-xx**3)==-xx**4,'Strictly negative away from zero')
potential=s.integrate(xx+xx**3,(xx,0,x))
ck('Polynomial nonlinear potential',potential==x*x/2+x**4/4,'x^2/2+x^4/4')
Bn=2*u+u**3;Kn=x+x**3;vn=u*u/2+potential;vdn=s.simplify(s.diff(vn,x)*u+s.diff(vn,u)*(-Bn-Kn))
ck('Nonlinear energy derivative',s.expand(vdn+u*Bn)==0,'-2u^2-u^4')
ck('Nonlinear energy numerical',vn.subs({x:1,u:-2})==s.Rational(11,4) and vdn.subs(u,-2)==-24,'v=2.75, vdot=-24')
ck('Negative displacement restoring acceleration',(-Bn-Kn).subs({x:-1,u:0})==2,'+2 normalized acceleration')
ck('Strict polynomial signs',s.expand(u*u**3)==u**4 and s.expand(x*Kn)==x*x+x**4,'Damping u^4 and restoring x^2+x^4 positive away from 0')
# Reproduce general matrix mismatch identity using exact random integer matrices.
rng=random.Random(240727)
for i in range(100):
 n=3;U=s.Matrix(n,n,[rng.randint(-2,2) for _ in range(n*n)]);W=s.Matrix(n,n,[rng.randint(-2,2) for _ in range(n*n)])
 M=U.T*U+s.eye(n);Mh=W.T*W+s.eye(n);Kv=s.diag(2,3,4);Kp=s.diag(5,6,7)
 def rv():return s.Matrix([rng.randint(-3,3) for _ in range(n)])
 ad=rv();E=rv();Ed=rv();hv=rv();hh=rv();cmd=ad+Kv*Ed+Kp*E;tau=Mh*cmd+hh;actual=M.inv()*(tau-hv);Ed2=ad-actual
 assert Ed2+Kv*Ed+Kp*E==Mh.inv()*((M-Mh)*actual+hv-hh)
 # actual-state exact feedforward residual and sign for added resisting disturbance
 disturbance=rv();actual2=cmd-M.inv()*disturbance
 assert ad-actual2+Kv*Ed+Kp*E==M.inv()*disturbance
ck('100 exact 3x3 mismatch and disturbance identities',True,'100 seeded SPD actual/estimated inertia cases; both exact algebraic identities pass')
for q in [s.Rational(j,10) for j in range(-50,51) if j]:
 assert q*(q+q**3)>0 and q*(2*q+q**3)>0 and (q*q/2+q**4/4)>0
ck('Polynomial sign and negative-limit checks',True,'100 nonzero rational state/velocity samples, with symbolic positive-power decompositions above')
print('L24 author checks:',len(records),'records passed; no independent verification claimed')
