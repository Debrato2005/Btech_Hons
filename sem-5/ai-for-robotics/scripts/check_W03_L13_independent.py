#!/usr/bin/env python3
"""Independent L13 dynamics checks, not imported from the author implementation.

Compare vector Newton–Euler recursion with Cartesian point-mass virtual work,
Jacobian mass matrices, finite-difference potential/energy, and source examples.
"""
import datetime,json,math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
rng=np.random.default_rng(1310423)
groups=[]
def rz(t):
 c,s=math.cos(t),math.sin(t)
 return np.array([[c,-s,0.],[s,c,0.],[0.,0.,1.]])
def pos(q,l):
 p1=l[0]*np.array([math.cos(q[0]),math.sin(q[0]),0.])
 p2=p1+l[1]*np.array([math.cos(sum(q)),math.sin(sum(q)),0.])
 return p1,p2
def jac(q,l):
 t1=l[0]*np.array([-math.sin(q[0]),math.cos(q[0]),0.])
 t2=l[1]*np.array([-math.sin(sum(q)),math.cos(sum(q)),0.])
 return np.column_stack([t1,np.zeros(3)]),np.column_stack([t1+t2,t2])
def cartesian(q,v,a,l,m,g):
 p1,p2=pos(q,l);d=p2-p1
 ac1=np.cross([0,0,a[0]],p1)-v[0]**2*p1
 ac2=ac1+np.cross([0,0,sum(a)],d)-sum(v)**2*d
 j1,j2=jac(q,l)
 f1=m[0]*(ac1+[0,g,0]);f2=m[1]*(ac2+[0,g,0])
 return j1.T@f1+j2.T@f2,ac1,ac2

def recursive(q,v,a,l,m,g,boundary=0.):
 ac1=rz(-q[0])@np.array([0.,g,0.])+np.cross([0,0,a[0]],[l[0],0,0])+np.cross([0,0,v[0]],np.cross([0,0,v[0]],[l[0],0,0]))
 a2=rz(-q[1])@ac1
 ac2=a2+np.cross([0,0,sum(a)],[l[1],0,0])+np.cross([0,0,sum(v)],np.cross([0,0,sum(v)],[l[1],0,0]))
 f2=m[1]*ac2;n2=np.cross([l[1],0,0],f2)+[0,0,boundary]
 f1=m[0]*ac1+rz(q[1])@f2
 n1=rz(q[1])@n2+np.cross([l[0],0,0],m[0]*ac1)+np.cross([l[0],0,0],rz(q[1])@f2)
 return np.array([n1[2],n2[2]]),ac1,a2,ac2,f1,f2

def closed(q,v,a,l,m,g):
 c,s=math.cos(q[1]),math.sin(q[1]);k=m[1]*l[0]*l[1]
 mm=np.array([[(m[0]+m[1])*l[0]**2+m[1]*l[1]**2+2*k*c,m[1]*l[1]**2+k*c],[m[1]*l[1]**2+k*c,m[1]*l[1]**2]])
 h=k*s*np.array([-v[1]**2-2*v[0]*v[1],v[0]**2])
 G=np.array([(m[0]+m[1])*l[0]*g*math.cos(q[0])+m[1]*l[1]*g*math.cos(sum(q)),m[1]*l[1]*g*math.cos(sum(q))])
 return mm@a+h+G,mm,h,G

def sample():
 return rng.uniform(-math.pi,math.pi,2),rng.uniform(-4,4,2),rng.uniform(-5,5,2),rng.uniform(.2,2.5,2),rng.uniform(.3,5,2),rng.uniform(0,15)

errs=[]
for i in range(600):
 q,v,a,l,m,g=sample();tr,*_=recursive(q,v,a,l,m,g);tc,ac1,ac2=cartesian(q,v,a,l,m,g);tf,*_=closed(q,v,a,l,m,g)
 errs.append(max(np.max(abs(tr-tc)),np.max(abs(tr-tf))))
 assert np.allclose(tr,tc,atol=1e-9) and np.allclose(tr,tf,atol=1e-9)
groups.append({'name':'Vector recursion versus Cartesian virtual work and closed torque equations','cases':600,'maxAbsoluteError':max(errs),'passed':True})

errs=[]
for i in range(600):
 q,v,a,l,m,g=sample();_,M,h,G=closed(q,v,a,l,m,g);j1,j2=jac(q,l)
 independent=m[0]*j1.T@j1+m[1]*j2.T@j2
 determinant=m[1]*l[0]**2*l[1]**2*(m[0]+m[1]*math.sin(q[1])**2)
 errs.append(np.max(abs(M-independent)))
 assert np.allclose(M,independent,atol=1e-10)
 assert np.isclose(np.linalg.det(M),determinant,atol=1e-9)
 assert np.linalg.eigvalsh(M).min()>0
 assert np.allclose(M,M.T)
groups.append({'name':'Mass matrix from Cartesian Jacobians, determinant and positive definiteness','cases':600,'maxAbsoluteError':max(errs),'passed':True})

errs=[]
for i in range(400):
 q,v,a,l,m,g=sample();_,_,_,G=closed(q,v,a,l,m,g)
 def potential(q):
  p1,p2=pos(q,l);return g*(m[0]*p1[1]+m[1]*p2[1])
 e=1e-5;grad=np.array([(potential(q+e*np.eye(2)[j])-potential(q-e*np.eye(2)[j]))/(2*e) for j in range(2)])
 errs.append(np.max(abs(G-grad)));assert np.allclose(G,grad,atol=1e-7,rtol=1e-8)
groups.append({'name':'Gravity compensation equals finite-difference potential gradient','cases':400,'maxAbsoluteError':max(errs),'passed':True})

errs=[]
for i in range(300):
 q,v,a,l,m,g=sample();tau,*_=closed(q,v,a,l,m,g)
 def energy(t):
  qt=q+v*t+.5*a*t*t;vt=v+a*t;j1,j2=jac(qt,l);p1,p2=pos(qt,l)
  return .5*m[0]*np.dot(j1@vt,j1@vt)+.5*m[1]*np.dot(j2@vt,j2@vt)+g*(m[0]*p1[1]+m[1]*p2[1])
 e=2e-6;derivative=(energy(e)-energy(-e))/(2*e);power=np.dot(tau,v)
 errs.append(abs(derivative-power));assert np.isclose(derivative,power,atol=2e-6,rtol=1e-7)
groups.append({'name':'Instantaneous actuator power equals total mechanical energy derivative','cases':300,'maxAbsoluteError':max(errs),'passed':True})

errs=[]
for i in range(300):
 q,v,a,l,m,g=sample();tau,*_=recursive(q,v,a,l,m,g);reverse,*_=recursive(q,-v,a,l,m,g)
 M=rng.uniform(-10,10);with_couple,*_=recursive(q,v,a,l,m,g,M)
 errs.append(max(np.max(abs(tau-reverse)),np.max(abs(with_couple-tau-M))))
 assert np.allclose(tau,reverse,atol=1e-9)
 assert np.allclose(with_couple-tau,[M,M],atol=1e-9)
groups.append({'name':'Simultaneous rate reversal and terminal-couple propagation','cases':300,'maxAbsoluteError':max(errs),'passed':True})

errs=[]
for i in range(300):
 q,v,a,l,m,g=sample();_,ac1,ac2=cartesian(q,v,a,l,m,0)
 e=1e-4;p0=pos(q,l);pp=pos(q+v*e+.5*a*e*e,l);pm=pos(q-v*e+.5*a*e*e,l)
 approx=[(pp[j]-2*p0[j]+pm[j])/(e*e) for j in range(2)]
 errs.append(max(np.max(abs(approx[0]-ac1)),np.max(abs(approx[1]-ac2))))
 assert np.allclose(approx[0],ac1,atol=2e-5,rtol=1e-5) and np.allclose(approx[1],ac2,atol=2e-5,rtol=1e-5)
groups.append({'name':'Physical point accelerations from finite-difference positions','cases':300,'maxAbsoluteError':max(errs),'passed':True})

# Exact reviewed examples and special cases. Each assertion group is one case.
examples=[]
def test(name,got,want):
 assert np.allclose(got,want,atol=1e-10), (name,got,want)
 examples.append({'name':name,'result':np.asarray(got).tolist(),'expected':np.asarray(want).tolist()})
test('Q003 one-point-mass torque',2*.5**2*3,1.5)
test('Q006 component rotation',rz(-math.pi/2)@[1,0,0],[0,-1,0])
test('Q009 augmented fixed-origin acceleration',rz(-math.pi/2)@[0,10,0],[10,0,0])
r=recursive([0,math.pi/2],[2,-1],[3,1],[1,.5],[1,2],10)
test('Q017 elbow acceleration',r[2],[13,4,0]);test('Q019 second COM acceleration',r[3],[12.5,6,0]);test('Q022 second force',r[5],[25,12,0]);test('Q024 elbow torque',r[0][1],6)
test('Q012 first force',2*np.array([-.5*2**2,.5*3+10,0]),[-4,23,0])
test('Q026 independent specified-force propagation',rz(math.pi/2)@[25,12,0]+np.array([-4,23,0]),[-16,48,0])
test('Q021 zero spin with translating elbow',recursive([.2,math.pi/2],[2,-2],[0,0],[1,.8],[2,3],0)[3],[0,4,0])
test('Q033 both torque numerical case',recursive([0,math.pi/2],[1,2],[3,4],[1,1],[1,1],10)[0],[25,8])
test('Q035 straight mass matrix',closed([0,0],[0,0],[0,0],[1,1],[1,1],0)[1],[[5,2],[2,1]])
test('Q037 horizontal holding torques',recursive([0,0],[0,0],[0,0],[1,1],[1,1],10)[0],[30,10])
r=recursive([math.pi/2,0],[0,0],[0,0],[1,1],[1,1],10)
test('Q038 vertical holding torques',r[0],[0,0]);assert np.linalg.norm(r[4])>0 and np.linalg.norm(r[5])>0
test('Q040 acceleration-free velocity coupling',recursive([0,math.pi/2],[2,0],[0,0],[1,1],[1,1],0)[0],[0,4])
test('Q045 zero sine velocity torque',closed([.4,0],[2,3],[0,0],[1,2],[3,4],0)[2],[0,0])
groups.append({'name':'Exact source-derived question examples and special cases','cases':len(examples),'passed':True,'examples':examples})
report={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentImplementation':True,'authorImplementationImported':False,'seed':1310423,'allPassed':True,'caseCount':sum(g['cases'] for g in groups),'groups':groups,'scope':'Validates the stated endpoint-point-mass 2R model, not general massive-rod dynamics. Positive-z terminal boundary sign is as specified in Q046. Source typography and question-quality review are separate.'}
(R/'audits/W03-L13-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['allPassed','caseCount']},indent=2))
