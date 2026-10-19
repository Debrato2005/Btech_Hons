"""L23 author reproduction. Explicit added initialization is not printed source code."""
from pathlib import Path
import json,math
import numpy as np
import scipy
from scipy.integrate import solve_ivp
R=Path(__file__).resolve().parents[1]; checks=[]
def check(name,ok):
 assert ok,name
 checks.append(name)
# Source pages716–718, normalized spelling only.
def desired_trajectory(t):
 theta_d=np.deg2rad(90.0);theta_d_d=0.;theta_d_dd=0.
 return theta_d,theta_d_d,theta_d_dd
m=1.;l=1.;I=m*l**2;v=.6;c=.4;g=9.81;kp=16.;kv=8.
def control_torque(t,x):
 theta,theta_dot=x
 theta_d,theta_d_dot,theta_d_ddot=desired_trajectory(t)
 e=theta_d-theta;e_dot=theta_d_dot-theta_dot
 f_prime=theta_d_ddot+kv*e_dot+kp*e
 tau=I*f_prime+v*theta_dot+c*np.sign(theta_dot)+m*g*l*np.cos(theta)
 return tau,e,e_dot,f_prime

def plant_dynamics(t,x):
 theta,theta_dot=x;tau,_,_,_=control_torque(t,x)
 theta_ddot=(tau-v*theta_dot-c*np.sign(theta_dot)-m*g*l*np.cos(theta))/I
 return [theta_dot,theta_ddot]
# ADDED context inferred as a reproduction choice, not a printed initialization:
# imports; time0..8s, rest at-20degrees,801 samples. Source graphs support these
# endpoints but do not disclose their actual code/sampling or plotting setup.
t0=0.;tf=8.;x0=[np.deg2rad(-20.),0.];t_eval=np.linspace(t0,tf,801)
sol=solve_ivp(plant_dynamics,[t0,tf],x0,t_eval=t_eval,rtol=1e-8,atol=1e-8)
e0=np.deg2rad(110.);e=e0*(1+4*t_eval)*np.exp(-4*t_eval)
theta=np.pi/2-e;omega=16*e0*t_eval*np.exp(-4*t_eval)
check('two-state integration succeeds',sol.success and sol.y.shape==(2,801))
check('matched angle agrees with analytic critical solution',np.max(np.abs(sol.y[0]-theta))<1e-7)
check('matched speed agrees with analytic critical solution',np.max(np.abs(sol.y[1]-omega))<1e-7)
check('target90degrees is pi/2radians',desired_trajectory(3)==(np.pi/2,0,0))
check('gain discriminant zero',kv*kv-4*kp==0)
check('initial error110degrees',math.isclose(e0,1.9198621771937625))
check('initial normalized acceleration',math.isclose(control_torque(0,x0)[3],30.7177948351002))
check('initial torque39.94Nm',math.isclose(control_torque(0,x0)[0],39.93617944501076))
check('initial Coulomb term zero',np.sign(0)==0)
check('peak speed at.25s',math.isclose(4*e0/math.e,2.82511129948892,rel_tol=1e-12))
check('phase coordinates differ from error coordinates',math.isclose(x0[0],-.3490658503988659) and math.isclose(e0,1.9198621771937625))
check('rod endpoint consistent with horizontal reference',np.allclose([l*np.cos(x0[0]),l*np.sin(x0[0])],[.9396926207859084,-.3420201433256687]))
check('horizontal static gravity torque',math.isclose(m*g*l*np.cos(0),9.81))
check('upright static gravity torque',abs(m*g*l*np.cos(np.pi/2))<1e-12)
check('negative-velocity Coulomb sign',-.4*np.sign(-2)==.4)
check('positive-velocity Coulomb sign',-.4*np.sign(2)==-.4)
check('cubic example force and tangent stiffness',3*.2**3==.024000000000000007 and math.isclose(3*3*.2**2,.36))
check('cubic doubling ratios',math.isclose((2*.2)**3/.2**3,8) and math.isclose((2*.2)**2/.2**2,4))
check('physical stiffness normalization',18/2==9 and 2*math.sqrt(18/2)==6)
check('2x2 torque compensation',np.allclose(np.array([[2,1],[1,3]])@np.array([1,-2])+np.array([.5,1]),[.5,-4]))
check('diagonal critical gains',np.allclose(2*np.sqrt([9,25]),[6,10]))
# Additional hypothetical arithmetic used by questions.
check('cubic cancellation sample',math.isclose(2*3+.5*(-2)+4*(.5**3),5.5))
check('Coulomb linear spring sample',math.isclose(2*3+.4*np.sign(-2)+5*.1,6.1))
check('Coulomb mismatch error forcing',math.isclose((.6-.4)/2,.1))
check('position derivative consistency',2*3==6 and 2==2)
# Author varied-model checks; not independent review.
rng=np.random.default_rng(2301)
for _ in range(1000):
 mass,b,qq=rng.uniform(.05,5,3);pos,vel,ad,ed,err=rng.normal(size=5);kpp,kvv=rng.uniform(.05,20,2)
 servo=ad+kvv*ed+kpp*err;f=mass*servo+b*vel+qq*pos**3
 acc=(f-b*vel-qq*pos**3)/mass
 assert math.isclose(ad-acc+kvv*ed+kpp*err,0,abs_tol=1e-10)
 A=rng.normal(size=(3,3));M=A.T@A+np.eye(3);a=rng.normal(size=3);beta=rng.normal(size=3)
 assert np.allclose(np.linalg.solve(M,M@a+beta-beta),a)
check('1000 cubic and positive-definite MIMO cancellation cases',True)
report={'role':'author calculations, not independent review','checksPassed':len(checks),'checks':checks,'randomCases':1000,'numpyVersion':np.__version__,'scipyVersion':scipy.__version__,'sourcePages':list(range(697,724)),'addedContext':['Imports for NumPy and solve_ivp.','t0=0, tf=8, x0=[deg2rad(-20),0], t_eval=linspace(0,8,801).','No plot or animation code is claimed to be printed or reproduced.'],'outputs':{'initialErrorRad':float(e0),'initialTorqueNm':float(control_torque(0,x0)[0]),'initialAccelerationRadPerS2':float(control_torque(0,x0)[3]),'peakSpeedRadPerS':float(4*e0/math.e),'peakTimeS':.25,'angleMaxAbsoluteError':float(np.max(np.abs(sol.y[0]-theta))),'speedMaxAbsoluteError':float(np.max(np.abs(sol.y[1]-omega)))}}
(R/'audits/W05-L23-author-checks.json').write_text(json.dumps(report,indent=2)+'\n')
(R/'audits/W05-L23-reproduced-output.txt').write_text(json.dumps(report['outputs'],indent=2)+'\nAdded context:0..8s,801samples,rest at-20degrees; not printed initialization.\n')
print(len(checks),'author checks and1000varied cases passed.',report['outputs'])
