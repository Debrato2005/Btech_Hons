#!/usr/bin/env python3
"""Independent source-derived L23 computations. Does not import/read author content."""
import json,math,random,datetime
from pathlib import Path
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def exact(name,expr):
 assert s.simplify(expr)==0,(name,expr);checks.append(name)
def near(name,a,b,tol=1e-10):
 assert abs(a-b)<tol,(name,a,b);checks.append(name)
x,q,t,m,b,bh,v,k,fp,E0=s.symbols('x q t m b bh v k fp E0', real=True)
exact('Cubic tangent',s.diff(q*x**3,x)-3*q*x*x)
exact('Cubic doubled displacement',q*(2*x)**3-8*q*x**3)
exact('Tangent doubled displacement',3*q*(2*x)**2-4*(3*q*x*x))
exact('Cubic exact cancellation',(m*fp+b*v+q*x**3-b*v-q*x**3)/m-fp)
exact('Coulomb exact cancellation',(m*fp+b*s.sign(v)+k*x-b*s.sign(v)-k*x)/m-fp)
exact('Coulomb mismatch acceleration',(m*fp+bh*s.sign(v)+k*x-b*s.sign(v)-k*x)/m-fp-(bh-b)*s.sign(v)/m)
exact('Mismatch error forcing',-((bh-b)*s.sign(v)/m)-(b-bh)*s.sign(v)/m)
near('Normalized physical stiffness',18/2,9)
near('Critical velocity gain',2*math.sqrt(18/2),6)
near('Cubic command',2*3+.5*(-2)+4*.5**3,5.5)
near('Coulomb command',2*3+.4*(-1)+1*.5,6.1)
near('Negative-velocity physical friction',-.4*(-1),.4)
exact('Critical polynomial factor',s.Symbol('z')**2+8*s.Symbol('z')+16-(s.Symbol('z')+4)**2)
I,l,theta,omega,c,g=s.symbols('I l theta omega c g',real=True)
beta=v*omega+c*s.sign(omega)+m*g*l*s.cos(theta)
exact('Pendulum exact cancellation',(I*fp+beta-beta)/I-fp)
near('Horizontal holding torque',1*9.81*1*math.cos(0),9.81)
near('Vertical holding torque',1*9.81*1*math.cos(math.pi/2),0)
near('Position error',math.pi/2-math.pi/6,math.pi/3)
near('Velocity error',0-.5,-.5)
Einit=11*math.pi/18;torque=16*Einit+9.81*math.cos(-math.pi/9)
near('Initial radians',math.radians(110),Einit)
near('Initial torque',torque,39.936179445473715,1e-8)
Et=E0*(1+4*t)*s.exp(-4*t)
exact('Repeated-root homogeneous ODE',s.diff(Et,t,2)+8*s.diff(Et,t)+16*Et)
exact('Initial error',Et.subs(t,0)-E0)
exact('Zero initial error derivative',s.diff(Et,t).subs(t,0))
speed=-s.diff(Et,t)
exact('Speed formula',speed-16*E0*t*s.exp(-4*t))
exact('Peak time stationary',s.diff(speed,t).subs(t,s.Rational(1,4)))
exact('Peak speed value',speed.subs(t,s.Rational(1,4))-4*E0/s.E)
near('Initial endpoint x',math.cos(math.radians(-20)),.9396926207859084)
near('Initial endpoint y',math.sin(math.radians(-20)),-.3420201433256687)
exact('Trajectory derivative',s.diff(t*t,t)-2*t)
exact('Trajectory acceleration',s.diff(t*t,t,2)-2)
M=s.Matrix([[2,1],[1,3]]);f=s.Matrix([1,-2]);be=s.Matrix([s.Rational(1,2),1])
result=M*f+be
exact('MIMO full command component 1',result[0]-s.Rational(1,2))
exact('MIMO full command component 2',result[1]+4)
assert M.det()==5 and M[0,0]>0;checks.append('Example mass matrix positive definite')
exact('MIMO cancellation component 1',(M.inv()*(result-be)-f)[0])
exact('MIMO cancellation component 2',(M.inv()*(result-be)-f)[1])
near('Joint 1 critical damping',2*math.sqrt(9),6)
near('Joint 2 critical damping',2*math.sqrt(25),10)
# Reconstruct only explicitly supplied assumptions, not unprinted source initialization.
from scipy.integrate import solve_ivp
import numpy as np
def ode(_,state):
 th,om=state;ep=math.pi/2-th;ev=-om
 u=16*ep+8*ev+.6*om+.4*np.sign(om)+9.81*math.cos(th)
 return [om,u-.6*om-.4*np.sign(om)-9.81*math.cos(th)]
ts=np.linspace(0,8,801);sol=solve_ivp(ode,[0,8],[-math.pi/9,0],t_eval=ts,rtol=1e-10,atol=1e-12)
assert sol.success
expected_error=Einit*(1+4*ts)*np.exp(-4*ts)
expected_velocity=16*Einit*ts*np.exp(-4*ts)
err=float(np.max(np.abs(sol.y[0]-(math.pi/2-expected_error))))
velerr=float(np.max(np.abs(sol.y[1]-expected_velocity)))
assert err<1e-9 and velerr<1e-9;checks.extend(['Independent ODE position versus analytic response','Independent ODE velocity versus analytic response'])
rng=random.Random(230019);maxres=0
for _ in range(500):
 mass=rng.uniform(.1,7);vv=rng.uniform(-6,6);xx=rng.uniform(-3,3);qq=rng.uniform(.2,5);bb=rng.uniform(.01,2);cmd=rng.uniform(-10,10)
 u=mass*cmd+bb*vv+qq*xx**3
 res=abs((u-bb*vv-qq*xx**3)/mass-cmd);assert res<1e-10;maxres=max(maxres,res)
 aa=rng.uniform(.1,7);dd=rng.uniform(.1,7);cross=rng.uniform(-.9,.9)*math.sqrt(aa*dd)
 mat=np.array([[aa,cross],[cross,dd]]);ff=np.array([rng.uniform(-5,5),rng.uniform(-5,5)]);beta_np=np.array([rng.uniform(-2,2),rng.uniform(-2,2)])
 recovered=np.linalg.solve(mat,mat@ff+beta_np-beta_np)
 res=float(np.max(np.abs(recovered-ff)));assert res<1e-10;maxres=max(maxres,res)
 mi=rng.uniform(.1,5);li=rng.uniform(.1,3);th=rng.uniform(-math.pi,math.pi);om=rng.uniform(-5,5);vis=rng.uniform(0,2);cou=rng.uniform(0,2)
 beta_p=vis*om+cou*np.sign(om)+mi*9.81*li*math.cos(th);iner=mi*li*li
 res=abs((iner*cmd+beta_p-beta_p)/iner-cmd);assert res<1e-10;maxres=max(maxres,res)
out={'reviewerId':'define_robotics_data_contracts:L23-independent-reviewer','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorKeysSeen':False,'exactAndNumericAssertions':len(checks),'assertions':checks,'randomTrials':500,'checksPerTrial':3,'maxResidual':maxres,'reconstructedSimulation':{'horizonSeconds':[0,8],'samples':801,'initialState':[-math.pi/9,0],'theseInitialConditionsAreExplicitQuestionAssumptionsNotPrintedSlideInitialization':True,'rtol':1e-10,'atol':1e-12,'maxPositionErrorAgainstAnalytic':err,'maxVelocityErrorAgainstAnalytic':velerr},'numericResults':{'initialErrorRad':Einit,'initialTorqueNm':torque,'peakTimeSeconds':.25,'peakSpeedRadPerSecond':4*Einit/math.e,'mimoCommand':[.5,-4]},'status':'passed'}
(ROOT/'audits/W05-L23-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
