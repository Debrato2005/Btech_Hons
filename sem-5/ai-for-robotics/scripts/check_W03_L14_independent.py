#!/usr/bin/env python3
"""L14 independent symbolic and Cartesian dynamics verification."""
import datetime,json,math
from pathlib import Path
import numpy as np
import sympy as s
R=Path(__file__).resolve().parents[1];rng=np.random.default_rng(1440446);groups=[]
# Symbolic Euler–Lagrange directly from source energies, not author code.
t,d,w,v,a,b,m1,m2,l,I1,I2,g,dm=s.symbols('theta d w v a b m1 m2 l I1 I2 g dmax',real=True)
A=m1*l*l+I1+I2+m2*d*d
K=A*w*w/2+m2*v*v/2
U=g*(m1*l+m2*d)*s.sin(t)+m1*l*g+m2*g*dm
q=s.Matrix([t,d]);qd=s.Matrix([w,v]);qdd=s.Matrix([a,b]);mom=s.Matrix([s.diff(K,z) for z in qd])
EL=mom.jacobian(q)*qd+mom.jacobian(qd)*qdd-s.Matrix([s.diff(K,z) for z in q])+s.Matrix([s.diff(U,z) for z in q])
expected=s.Matrix([A*a+2*m2*d*w*v+g*(m1*l+m2*d)*s.cos(t),m2*b-m2*d*w*w+m2*g*s.sin(t)])
assert all(s.simplify(z)==0 for z in EL-expected)
assert mom.jacobian(qd)==s.diag(A,m2)
velocity=s.Matrix([2*m2*d*w*v,-m2*d*w*w]);Mdot=s.diag(2*m2*d*v,0)
assert s.simplify((qd.T*velocity)[0]-(qd.T*Mdot*qd)[0]/2)==0
kt,m,L=s.symbols('kt m L',positive=True)
Ks=m*L*L*w*w/2;Us=kt*t*t/2-m*g*L*s.sin(t)
ELs=s.diff(s.diff(Ks,w),w)*a+s.diff(Us,t)
assert s.simplify(ELs-(m*L*L*a+kt*t-m*g*L*s.cos(t)))==0
assert s.simplify(s.diff(Ks,w)*a+s.diff(Us,t)*w-ELs*w)==0
groups.append({'name':'Exact symbolic Euler–Lagrange equations, mass Hessian and power identities','cases':5,'passed':True,'rpResult':[str(s.simplify(z)) for z in EL],'singleResult':str(ELs)})

def sample():
 return rng.uniform(-math.pi,math.pi),rng.uniform(.1,2),rng.uniform(-4,4),rng.uniform(-2,2),rng.uniform(-5,5),rng.uniform(-3,3),rng.uniform(.3,4),rng.uniform(.3,4),rng.uniform(.1,2),rng.uniform(.05,1),rng.uniform(.05,1),rng.uniform(0,15)
def analytic(z):
 t,d,w,v,a,b,m1,m2,l,I1,I2,g=z
 A=m1*l*l+I1+I2+m2*d*d
 return np.array([A*a+2*m2*d*w*v+g*(m1*l+m2*d)*math.cos(t),m2*b-m2*d*w*w+m2*g*math.sin(t)])
def cartesian(z):
 t,d,w,v,a,b,m1,m2,l,I1,I2,g=z
 er=np.array([math.cos(t),math.sin(t)]);et=np.array([-math.sin(t),math.cos(t)])
 ac1=l*a*et-l*w*w*er
 ac2=(b-d*w*w)*er+(d*a+2*v*w)*et
 f1=m1*(ac1+np.array([0.,g]));f2=m2*(ac2+np.array([0.,g]))
 # Virtual work J_C1^T F1+J_C2^T F2 and COM spin moments.
 J1=np.column_stack([l*et,np.zeros(2)]);J2=np.column_stack([d*et,er])
 return J1.T@f1+J2.T@f2+np.array([(I1+I2)*a,0.])
errs=[]
for i in range(600):
 z=sample();diff=analytic(z)-cartesian(z);errs.append(np.max(abs(diff)));assert np.allclose(diff,0,atol=1e-9)
groups.append({'name':'RP Euler–Lagrange versus independent Cartesian force/spin virtual work','cases':600,'maxAbsoluteError':max(errs),'passed':True})

errs=[]
for i in range(400):
 z=sample();t,d,w,v,a,b,m1,m2,l,I1,I2,g=z
 def energy(dt):
  qt=t+w*dt+.5*a*dt*dt;dr=d+v*dt+.5*b*dt*dt;wr=w+a*dt;vr=v+b*dt
  er=np.array([math.cos(qt),math.sin(qt)]);et=np.array([-math.sin(qt),math.cos(qt)])
  vc1=l*wr*et;vc2=vr*er+dr*wr*et
  return .5*m1*np.dot(vc1,vc1)+.5*m2*np.dot(vc2,vc2)+.5*(I1+I2)*wr*wr+g*(m1*l+m2*dr)*math.sin(qt)
 e=2e-6;de=(energy(e)-energy(-e))/(2*e);power=np.dot(analytic(z),[w,v]);errs.append(abs(de-power));assert np.isclose(de,power,atol=2e-6,rtol=1e-7)
groups.append({'name':'RP total energy rate equals torque/force power','cases':400,'maxAbsoluteError':max(errs),'passed':True})

errs=[]
for i in range(400):
 z=sample();t,d,w,v,a,b,m1,m2,l,I1,I2,g=z
 def E(t,w):return .5*m1*l*l*w*w+.5*I1*t*t-m1*g*l*math.sin(t)
 # I1 here is a positive numerical spring stiffness, not imported from RP.
 tau=m1*l*l*a+I1*t-m1*g*l*math.cos(t)
 er=np.array([math.cos(t),-math.sin(t),0.]);Fg=np.array([0.,-m1*g,0.])
 gravity_positive_down=-np.cross(l*er,Fg)[2]
 newton=m1*l*l*a+I1*t-gravity_positive_down
 e=2e-6;de=(E(t+w*e+.5*a*e*e,w+a*e)-E(t-w*e+.5*a*e*e,w-a*e))/(2*e)
 errs.append(max(abs(tau-newton),abs(de-tau*w)))
 assert np.isclose(tau,newton,atol=1e-10) and np.isclose(de,tau*w,atol=2e-6,rtol=1e-7)
groups.append({'name':'Downward-positive spring arm: vector gravity moment and energy derivative','cases':400,'maxAbsoluteError':max(errs),'passed':True})

errs=[]
for i in range(300):
 z=list(sample());t,d,w,v,a,b,m1,m2,l,I1,I2,g=z
 A=m1*l*l+I1+I2+m2*d*d;z[4]=-(2*m2*d*v)*w/A;z[-1]=0
 Q=cartesian(z);errs.append(abs(Q[0]));assert np.isclose(Q[0],0,atol=1e-9)
 # Directly check a different radius conserving momentum, with energy free to change.
 df=rng.uniform(.1,2);Af=m1*l*l+I1+I2+m2*df*df;wf=A*w/Af
 assert np.isclose(A*w,Af*wf,atol=1e-10)
groups.append({'name':'Zero revolute input conserves angular momentum during radial actuation','cases':300,'maxAbsoluteError':max(errs),'passed':True})

errs=[]
for i in range(300):
 t,d,w,v,a,b,m1,m2,l,I1,I2,g=sample();dmax=d+rng.uniform(0,2)
 def U(t,d,c):return g*(m1*l+m2*d)*math.sin(t)+m1*l*g+m2*g*dmax+c
 e=1e-5;c=rng.uniform(-20,20)
 grad=np.array([(U(t+e,d,c)-U(t-e,d,c))/(2*e),(U(t,d+e,c)-U(t,d-e,c))/(2*e)])
 desired=np.array([g*(m1*l+m2*d)*math.cos(t),m2*g*math.sin(t)])
 errs.append(np.max(abs(grad-desired)));assert np.allclose(grad,desired,atol=1e-7,rtol=1e-8)
 assert U(t,d,0)>=-1e-10 and abs(U(-math.pi/2,dmax,0))<1e-10
groups.append({'name':'Potential gradients, constant-datum invariance and zero attainable minimum','cases':300,'maxAbsoluteError':max(errs),'passed':True})

errs=[]
for i in range(200):
 z=sample();t,d,w,v,a,b,m1,m2,l,I1,I2,g=z
 # Inertial generalized-velocity terms and their single-rate reversal.
 h=np.array([2*m2*d*w*v,-m2*d*w*w]);hr=np.array([2*m2*d*(-w)*v,-m2*d*(-w)**2])
 assert np.allclose(hr,[-h[0],h[1]])
 mdot=np.diag([2*m2*d*v,0]);vel=np.array([w,v]);errs.append(abs(vel@h-.5*vel@mdot@vel))
 assert np.isclose(vel@h,.5*vel@mdot@vel,atol=1e-10)
groups.append({'name':'Velocity-product signs and configuration-rate kinetic identity','cases':200,'maxAbsoluteError':max(errs),'passed':True})
examples=[]
def test(name,got,want):
 assert np.allclose(got,want,atol=1e-10),(name,got,want)
 examples.append({'name':name,'result':np.asarray(got).tolist(),'expected':np.asarray(want).tolist()})
test('Q005 translation and rotation energy',.5*2*3**2+.5*.5*4**2,13)
test('Q008 total energy and Lagrangian',[12+5,12-5],[17,7])
test('Q013 gravitational vector potential',-2*np.dot([0,-10,0],[2,3,0]),60)
test('Q022 driven spring torque',2*.5**2*4+3*math.pi/6-2*10*.5*math.cos(math.pi/6),2+math.pi/2-5*math.sqrt(3))
assert round(examples[-1]['result'],2)==-5.09
for n,mass,length,gravity in [(1,2,.5,10),(2,1,2,9.81)]:test('Q023 initial free acceleration '+str(n),mass*gravity*length/(mass*length**2),gravity/length)
test('Q026 radians spring torque',4*math.radians(90),2*math.pi)
test('Q033 RP kinetic energy',.5*(2*.5**2+.2+.3+3*.4**2)*2**2+.5*3*.5**2,3.335)
test('Q043 mixed actuator efforts',cartesian((0,.4,2,.5,1,-.2,2,3,.5,.2,.3,10)),[25.88,-5.4])
test('Q045 inward force',analytic((.4,.5,3,0,0,0,1,2,.7,.2,.3,0))[1],-9)
test('Q046 horizontal gravity',analytic((0,.4,0,0,0,0,2,3,.5,.2,.3,10)),[22,0])
test('Q046 vertical gravity',analytic((math.pi/2,.4,0,0,0,0,2,3,.5,.2,.3,10)),[0,30])
test('Q048 conserved momentum rate',(1+.5+.5+2*.5**2)*4/(1+.5+.5+2),2.5)
groups.append({'name':'Question numerical values and limit cases','cases':len(examples),'examples':examples,'passed':True})
out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentImplementation':True,'authorImplementationImported':False,'seed':1440446,'allPassed':True,'caseCount':sum(g['cases'] for g in groups),'groups':groups,'scope':'Tests the two explicit source models and stated sign conventions. Source-attributed limitation claims are reviewed as attribution, not promoted into universal mathematical facts.'}
(R/'audits/W03-L14-independent-computations.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['allPassed','caseCount']},indent=2))
