"""Author computations for L22. Added executable context is explicit, not printed source."""
from pathlib import Path
import json,math,hashlib
import numpy as np
import scipy
from scipy.integrate import solve_ivp
R=Path(__file__).resolve().parents[1]
checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
# The following state and ODE are transcribed from actual source page 685.
I_m=0.01;b_m=0.1;tau_m=2.0
def joint_ode(t,state,I_m,b_m,I,b,eta,tau_m):
 theta_dot=state[0]
 I_eff=I+(eta**2)*I_m
 b_eff=b+(eta**2)*b_m
 theta_ddot=(eta*tau_m-b_eff*theta_dot)/I_eff
 return [theta_ddot]
# Explicit added context: imports above, a 0–5 s interval, rest, 501 output points.
# The source does not print these definitions or plotting commands.
t_span=(0.0,5.0);theta_dot_0=[0.0];t_eval=np.linspace(0.0,5.0,501)
sol=solve_ivp(joint_ode,t_span,theta_dot_0,t_eval=t_eval,args=(I_m,b_m,0.0,0.0,1.0,tau_m))
theta_dot_m=sol.y[0];theta_ddot_m=np.gradient(theta_dot_m,sol.t);theta_dot_m_ss=tau_m/b_m
analytic=20*(1-np.exp(-10*t_eval))
check('no-load one-state solve succeeds',sol.success and sol.y.shape==(1,501))
check('default solver agrees with analytic rise within 0.03 rad/s',np.max(np.abs(theta_dot_m-analytic))<0.03)
check('steady no-load speed',theta_dot_m_ss==20)
check('initial analytic acceleration',joint_ode(0,[0],.01,.1,0,0,1,2)==[200])
check('time constant',math.isclose(.01/.1,.1))
check('analytic endpoint gradient 190.325',math.isclose(float(np.gradient(analytic,t_eval)[0]),190.32516392808096))
check('right-hand Lorentz cross product',np.array_equal(2*np.cross([3,0,0],[0,4,0]),[0,0,24]))
check('parallel cross product zero',np.array_equal(np.cross([1,2,3],[-2,-4,-6]),[0,0,0]))
check('power-consistent SI motor torque and back EMF',math.isclose(.4*3,1.2) and .4*10==4 and math.isclose(1.2*10,4*3))
check('armature current derivative',(12-2*1-.1*20)/.5==16)
check('gear ideal port power',20*2==(20/10)*(2*10))
check('inertia range',2+30**2*.01==11 and 6+30**2*.01==15)
check('inertia absolute span',(15-11)==(6-2)==4)
check('inertia relative ratio reduces',15/11<6/2)
check('critical example gains',(8/2)**2==16 and 2*(8/2)==8)
check('partition force',math.isclose(-7*(-.1)-15*.2,-2.3))
check('partition acceleration',math.isclose((-2.3)-(-.1)-.2,-2.4))
check('shaft natural frequency',math.sqrt(400/1)==20)
check('shaft gains',10**2==100 and 2*10==20)
me=.23*4.347;wn=math.sqrt(3600/me);freq=wn/(2*math.pi)
check('link effective mass',math.isclose(me,.99981))
check('link frequency corrected',60<wn<60.01 and 9.55<freq<9.551 and round(freq,2)==9.55)
# Loaded sweep: same source constants and equations, added time definitions above.
rows=[]
for eta in [1,5,20,50]:
 J=1+eta**2*.01;B=.05+eta**2*.1
 sl=solve_ivp(joint_ode,t_span,theta_dot_0,t_eval=t_eval,args=(.01,.1,1,.05,eta,2))
 load=sl.y[0];motor=load*eta
 motor_ss=eta**2*2/B;T=J/B;exact=motor_ss*(1-np.exp(-t_eval/T))
 check(f'loaded sweep eta {eta} analytic match',sl.success and np.max(np.abs(motor-exact))<.03)
 rows.append({'eta':eta,'J':J,'B':B,'motorSteadySpeed':motor_ss,'loadSteadySpeed':motor_ss/eta,'timeConstant':T,'motorAt5sAnalytic':float(exact[-1])})
check('eta-five effective terms',rows[1]['J']==1.25 and rows[1]['B']==2.55)
check('eta-five motor asymptote',math.isclose(rows[1]['motorSteadySpeed'],19.607843137254903))
check('eta-one finite window not steady',6.98<rows[0]['motorAt5sAnalytic']<7.0<rows[0]['motorSteadySpeed'])
check('optimal acceleration at eta ten',math.sqrt(1/.01)==10 and 10*2/(1+100*.01)==10)
check('eta five and twenty equal initial acceleration',5*2/(1+25*.01)==20*2/(1+400*.01)==8)
# Final source snippet resets all four physical parameters.
I_m=.01;b_m=.05;I=2.;b=.2;tau_m=3.
eta_values=np.array([1,2,5,10,20,30,50])
I_eff_arr=I+(eta_values**2)*I_m
b_eff_arr=b+(eta_values**2)*b_m
check('full inertia table',np.allclose(I_eff_arr,[2.01,2.04,2.25,3,6,11,27],rtol=0,atol=1e-12))
check('full damping table',np.allclose(b_eff_arr,[.25,.4,1.45,5.2,20.2,45.2,125.2],rtol=0,atol=1e-12))
check('inertia threshold',next(int(e) for e in eta_values if e*e*I_m>I)==20)
check('damping threshold',math.sqrt(b/b_m)==2)
# Independently varied algebra checks; still author checks, not independent review.
rng=np.random.default_rng(2201)
for _ in range(1000):
 I,Im,b,bm,eta,tau=rng.uniform(.01,20,6)
 om,acc=rng.normal(size=2);J=I+eta*eta*Im;B=b+eta*eta*bm
 load_torque=J*acc+B*om
 motor_balance=Im*(eta*acc)+bm*(eta*om)+(I*acc+b*om)/eta
 assert math.isclose(load_torque,eta*motor_balance,rel_tol=1e-10,abs_tol=1e-10)
 alpha=rng.uniform(.01,40);rho=alpha/J
 dd,ed,e=rng.normal(size=3);kv,kp=rng.uniform(.01,10,2)
 actual=rho*(dd+kv*ed+kp*e);errdd=dd-actual
 assert math.isclose(errdd+rho*kv*ed+rho*kp*e,(1-rho)*dd,rel_tol=1e-10,abs_tol=1e-10)
check('1000 varied gear and inertia-mismatch algebra cases',True)
output=['Reconstruction adds imports, t_span=(0,5), theta_dot_0=[0], t_eval=linspace(0,5,501); these are not printed source definitions.','Default solve_ivp is used; no plot generation or hardware experiment is claimed.',f'No-load analytic steady speed: {theta_dot_m_ss:.6f} rad/s',f'Numerical first gradient: {theta_ddot_m[0]:.6f} rad/s²',f'Analytic initial acceleration: 200 rad/s²',f'Link resonance: {wn:.9f} rad/s = {freq:.9f} Hz','Loaded sweep (eta J B motor_ss time_constant motor_at_5s):']
for row in rows:output.append(' '.join(f'{row[k]:.9f}' for k in ('eta','J','B','motorSteadySpeed','timeConstant','motorAt5sAnalytic')))
output+=['Final effective-parameter table:','eta I_eff b_eff']+[f'{e:3d} {j:.4f} {d:.4f}' for e,j,d in zip(eta_values,I_eff_arr,b_eff_arr)]
(R/'audits/W05-L22-reproduced-output.txt').write_text('\n'.join(output)+'\n')
report={'role':'author computations, not independent answer review','checksPassed':len(checks),'checks':checks,'randomCases':1000,'sourcePages':[673,674,675,676,677,679,680,681,682,683,685,686,687,688,689,690],'numpyVersion':np.__version__,'scipyVersion':scipy.__version__,'addedContext':['Imports for NumPy and solve_ivp.','t_span=(0,5), initial state [0], t_eval=np.linspace(0,5,501).'],'outputPath':'audits/W05-L22-reproduced-output.txt','sourceCodeScope':'The pictured code is not standalone because imports and integration setup are missing; reconstruction is labeled and no exact original sampling or plotting claim is made.','loadedSweep':rows}
(R/'audits/W05-L22-author-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(len(checks),'author checks passed and 1000 varied algebra cases.')
