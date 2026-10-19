#!/usr/bin/env python3
"""Independent L09 calculations from equations, not from author check code."""
import datetime,json,math,platform
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];rng=np.random.default_rng(902631);results=[]
def record(name,n):results.append({'group':name,'cases':n,'passed':True})
def skew(w):x,y,z=w;return np.array([[0,-z,y],[z,0,-x],[-y,x,0]],float)
def rot(w,t=1.):
 a=np.linalg.norm(w)*t
 if abs(a)<1e-20:return np.eye(3)
 k=skew(w/np.linalg.norm(w));return np.eye(3)+math.sin(a)*k+(1-math.cos(a))*(k@k)
def eq(a,b,tol=1e-9):np.testing.assert_allclose(a,b,rtol=tol,atol=tol)
Rz=rot(np.array([0,0,math.pi/2]));Rx=rot(np.array([math.pi/2,0,0]));Rzm=Rz.T
# Actual explicit questions, not generated expected-answer data.
eq(np.linalg.norm([3,4,0]),5);eq(Rz@[2,0,0],[0,2,0]);eq(np.array([1,0,0])+Rz@[2,0,0],[1,2,0]);eq(2*3*math.sin(math.pi/6),3);eq(np.cross([0,0,2],[3,0,0]),[0,6,0]);eq(np.array([1,0,0])+Rz@[1,0,0]+np.cross([0,0,2],Rz@[2,0,0]),[-3,1,0]);eq(Rx@[0,0,2]+np.array([0,0,3]),[0,-2,3]);pv=np.array([1,2,0])+np.cross([0,0,2],[3,0,0]);eq(pv,[1,8,0]);eq(Rzm@pv,[8,-1,0]);eq(Rzm@pv+[0,0,4],[8,-1,4]);eq(Rz@[0,1,0],[-1,0,0]);eq(np.array([[4,1],[3,2]])@[.5,-1],[1,-.5]);eq(np.array([1.,2.])+np.linalg.solve(np.diag([2.,1.]),[.4,-.2])*.1,[1.02,1.98]);eq(np.array([[1,2],[0,1]]).T@[3,4],[3,10]);record('Fourteen direct numerical quantities',14)
# Transport theorem using finite differences of independent world position model.
for _ in range(1000):
 w,p,u,q,v,rvec=rng.normal(size=(6,3));R=rot(rvec);h=1e-6
 def world(t):return p+u*t+rot(w,t)@R@(q+v*t)
 actual=(world(h)-world(-h))/(2*h);expected=u+R@v+np.cross(w,R@q);eq(actual,expected,2e-8)
 # Re-expression is not observer change; zero maps to zero.
 eq(R@np.zeros(3),np.zeros(3));eq(R.T@R,np.eye(3))
record('Transport derivative and basis identities',1000)
# Independent link-position differentiation with revolute/prismatic relative motion.
for _ in range(500):
 w,v,P,rvec=rng.normal(size=(4,3));R=rot(rvec);rate=float(rng.normal());z=np.array([0.,0.,1.]);h=1e-6
 for prism in [False,True]:
  # In parent coordinates, a prismatic origin offset changes along R^T z.
  def world(t):return v*t+rot(w,t)@(P+(R.T@z)*rate*t*prism)
  numerical_child=R@(world(h)-world(-h))/(2*h)
  expected=R@(v+np.cross(w,P))+(rate*z if prism else 0)
  eq(numerical_child,expected,2e-8)
 # Independent composition of orientation derivatives for joint angular rate.
 def orient(t):return rot(w,t)@R.T@rot(z*rate,t)
 d=(orient(h)-orient(-h))/(2*h);Omega=d@orient(0).T
 world_w=np.array([Omega[2,1],Omega[0,2],Omega[1,0]])
 eq(R@world_w,R@w+rate*z,2e-8)
record('Revolute/prismatic origin and angular recurrences',1500)
for _ in range(500):
 q,qd=rng.normal(size=(2,2));h=1e-6
 def f(q):return np.array([q[0]**2+q[1],q[0]*q[1]])
 J=np.array([[2*q[0],1],[q[1],q[0]]]);eq((f(q+h*qd)-f(q-h*qd))/(2*h),J@qd,2e-8)
 dq=rng.normal(size=2)*.01;remainder=f(q+dq)-f(q)-J@dq;eq(remainder,[dq[0]**2,dq[0]*dq[1]])
record('Polynomial chain rule and exact second-order remainder',1000)
for _ in range(500):
 R=rot(rng.normal(size=3));D=np.block([[R,np.zeros((3,3))],[np.zeros((3,3)),R]])
 J=rng.normal(size=(6,3))@rng.normal(size=(3,7));eq(np.linalg.matrix_rank(D@J),np.linalg.matrix_rank(J));qdot=rng.normal(size=7);f=rng.normal(size=6);eq((J.T@f)@qdot,f@(J@qdot));eq((D@J)@qdot,D@(J@qdot))
record('Rank invariance, output basis mapping and virtual power',1500)
J=np.diag([1.,0.]);eq(J@[2,7],[2,0]);assert not np.any(J[1]);assert np.linalg.matrix_rank(np.array([[1,1,0],[0,0,1]]))==2;eq(np.array([1,1])@[1,-1],0);eq(np.linalg.matrix_rank(np.eye(3)),3)
for eps in [1.,.1,.001,1e-8]:eq(np.linalg.solve(np.diag([1.,eps]),[0,1]),[0,1/eps])
record('Singular compatible/incompatible targets, redundancy and joint-limit counterexample',8)
for theta in [.1,.01,.001,1e-4]:
 rho=1.5;arc=rho*theta;chord=2*rho*math.sin(theta/2);assert chord<arc;assert abs(chord/arc-1)<=theta**2/24+1e-15
record('Finite chord versus arc and derivative-limit bound',4)
out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentOfAuthorChecks':True,'seed':902631,'python':platform.python_version(),'numpy':np.__version__,'groups':results,'caseCount':sum(x['cases'] for x in results),'allPassed':True,'scope':'Checks establish the stated mathematics under explicit conventions, not physical robot safety or broad product claims.'};(ROOT/'audits/W02-L09-independent-computations.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
