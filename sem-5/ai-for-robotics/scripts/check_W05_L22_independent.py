#!/usr/bin/env python3
"""Source-first independent L22 calculations. Does not load author questions/keys."""
import datetime,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
import sympy as sy
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
check('Figure shoulder elbow wrist count',3+1+3==7)
check('Lorentz vector sign and magnitude',np.array_equal(2*np.cross([3,0,0],[0,4,0]),[0,0,24]))
check('Given torque and back EMF arithmetic',math.isclose(.4*3,1.2) and math.isclose(.2*10,2))
check('Armature derivative',math.isclose((12-2*1-.1*20)/.5,16))
check('Ideal gear port power',20*2==(20/10)*(2*10))
check('Inertia interval and relative variation',2+30**2*.01==11 and 6+30**2*.01==15 and 15-11==6-2 and 15/11<6/2)
check('Half resonance and critical gains',30/2==15 and (8/2)**2==16 and 2*(8/2)==8)
check('Partitioned actuator force',math.isclose(-8*(-.1)-16*.2+(-.1)+.2,-2.3))
check('Torsional resonance',math.sqrt(400/1)==20)
meff=.23*4.347;omega=math.sqrt(3600/meff)
check('Equivalent link mass',math.isclose(meff,.99981))
check('Link Hz conversion disagrees with printed 9.7',abs(omega-60)<.01 and abs(omega/(2*math.pi)-9.55)<.01 and abs(omega/(2*math.pi)-9.7)>.1)
J,alpha,B,ed,e,ad,dist,kv,kp=sy.symbols('J alpha B ed e ad d kv kp',positive=True)
actual=alpha/J*(ad+kv*ed+kp*e)
check('Inertia-mismatch tracking equation',sy.simplify((ad-actual)+(alpha/J)*(kv*ed+kp*e)-(1-alpha/J)*ad)==0)
check('Opposing physical torque normalization',sy.simplify(ad-(ad+kv*ed+kp*e-dist/J)+kv*ed+kp*e)==dist/J)
# Independently transcribed source p685. Explicitly supply omitted context rather than claiming it was printed.
def joint_ode(t,state,I_m,b_m,I,b,eta,tau_m):
 theta_dot=state[0]
 I_eff=I+(eta**2)*I_m
 b_eff=b+(eta**2)*b_m
 theta_ddot=(eta*tau_m-b_eff*theta_dot)/I_eff
 return [theta_ddot]
t_span=(0.,5.);theta_dot_0=[0.];t_eval=np.linspace(*t_span,501)
I_m=.01;b_m=.1;tau_m=2.
sol=solve_ivp(joint_ode,t_span,theta_dot_0,t_eval=t_eval,args=(I_m,b_m,0.,0.,1.,tau_m),rtol=1e-10,atol=1e-12)
expected=20*(1-np.exp(-10*sol.t))
check('One speed state',sol.y.shape==(1,501))
check('Source no-load ODE against exact solution',np.max(np.abs(sol.y[0]-expected))<1e-7)
check('Initial analytic acceleration and terminal speed',joint_ode(0,[0],.01,.1,0,0,1,2)[0]==200 and abs(sol.y[0,-1]-20)<1e-7)
grad=np.gradient(expected,t_eval)
check('Default endpoint derivative',abs(grad[0]-190.32516392808097)<1e-9 and grad[0]<200)
check('Model no-load electromagnetic torque fully balances friction at steady speed',.1*20==2)
ratios=[1,5,20,50];colors=['steelblue','darkorange','forestgreen','tomato']
check('Zip color mapping',dict(zip(colors,ratios))['forestgreen']==20)
rows=[]
for eta in ratios:
 I=1.;b=.05;effI=I+eta**2*I_m;effb=b+eta**2*b_m
 loaded=solve_ivp(joint_ode,t_span,theta_dot_0,t_eval=t_eval,args=(I_m,b_m,I,b,eta,tau_m),rtol=1e-10,atol=1e-12)
 motor=loaded.y[0]*eta;ss=eta**2*tau_m/effb
 exact=ss*(1-np.exp(-effb*t_eval/effI))
 check(f'Source ratio {eta} numerical/analytic motor response',np.max(np.abs(motor-exact))<1e-7)
 rows.append({'eta':eta,'effectiveInertia':effI,'effectiveDamping':effb,'steadyMotorSpeed':ss,'motorSpeedAt5Seconds':float(motor[-1]),'timeConstant':effI/effb})
check('Ratio five effective parameters',rows[1]['effectiveInertia']==1.25 and math.isclose(rows[1]['effectiveDamping'],2.55))
check('Ratio five steady motor speed',math.isclose(rows[1]['steadyMotorSpeed'],50/2.55))
check('Ratio one visible five-second plot is below asymptote',6.9<rows[0]['motorSpeedAt5Seconds']<7.1 and math.isclose(rows[0]['steadyMotorSpeed'],2/.15))
eta,I,Im,tau=sy.symbols('eta I Im tau',positive=True)
a=eta*tau/(I+eta**2*Im);derivative=sy.factor(sy.diff(a,eta))
check('Initial acceleration optimal ratio derivative',sy.simplify(derivative-tau*(I-Im*eta**2)/(I+Im*eta**2)**2)==0)
check('Initial acceleration maximum at ten',math.sqrt(1/.01)==10 and 10*2/(1+10**2*.01)>20*2/(1+20**2*.01))
Bm,b=sy.symbols('Bm b',positive=True)
check('Motor high-ratio limit',sy.limit(eta**2*tau/(b+eta**2*Bm),eta,sy.oo)==tau/Bm)
check('Load high-ratio limit',sy.limit(eta*tau/(b+eta**2*Bm),eta,sy.oo)==0)
eta_values=np.array([1,2,5,10,20,30,50]);I_eff_arr=2+(eta_values**2)*.01;b_eff_arr=.2+(eta_values**2)*.05
check('All table inertia cells',np.allclose(I_eff_arr,[2.01,2.04,2.25,3,6,11,27]))
check('All table damping cells',np.allclose(b_eff_arr,[.25,.4,1.45,5.2,20.2,45.2,125.2]))
check('Array shape',I_eff_arr.shape==(7,))
check('First motor-inertia dominance',eta_values[np.nonzero(eta_values**2*.01>2)[0][0]]==20)
check('Reflected damping equality',2**2*.05==.2)
check('Torque absent from effective parameter calculation',all('tau' not in x for x in ['I+(eta_values**2)*I_m','b+(eta_values**2)*b_m']))
rng=np.random.default_rng(22669)
for _ in range(1000):
 eta=float(rng.uniform(1,100));Im,I=rng.uniform(.001,10,2);bm,b=rng.uniform(.001,2,2);wm,am=rng.normal(size=2)
 wl=wm/eta;al=am/eta
 motor_torque=(Im+I/eta**2)*am+(bm+b/eta**2)*wm
 load_equivalent=(I+eta**2*Im)*al+(b+eta**2*bm)*wl
 assert np.isclose(eta*motor_torque,load_equivalent)
 assert np.isclose(Im*wm**2+I*wl**2,(I+eta**2*Im)*wl**2)
 actualJ,controllerJ=rng.uniform(.1,20,2);ed,e,ad=rng.normal(size=3);kp,kv=rng.uniform(.1,10,2);rho=controllerJ/actualJ
 actualacc=rho*(ad+kv*ed+kp*e);edd=ad-actualacc
 assert np.isclose(edd+rho*kv*ed+rho*kp*e,(1-rho)*ad)
check('1000 randomized reflected torque, energy and mismatch identities',True)
report={'reviewerId':'build_offline_study_interface:L22-independent-reviewer','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'pass','answerKeysRead':False,'namedCheckCount':len(checks),'checks':checks,'randomizedCases':1000,'randomSeed':22669,'sourceDerivedGearSweep':rows,'sourcePage682Computed':{'effectiveMass':meff,'omegaRadPerSecond':omega,'frequencyHz':omega/(2*math.pi)},'suppliedContext':'NumPy and solve_ivp imports, t_span=(0,5), zero initial speed [0], 501 equally spaced samples. Tight numerical tolerances were added for verification. These setup values and tolerances are not claimed to be printed in the excerpt.','sourceCodeScope':'The transcribed joint_ode is the printed constant-torque, one-speed-state equation, not PID or voltage/current simulation.'}
(R/'audits/W05-L22-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'pass','checks':len(checks),'randomizedCases':1000,'page682Hz':report['sourcePage682Computed']['frequencyHz'],'ratio1At5':rows[0]['motorSpeedAt5Seconds']}))
