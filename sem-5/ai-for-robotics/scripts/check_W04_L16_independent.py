"""Reviewer-derived checks from actual L16 source pixels, before keyed access."""
import datetime, hashlib, json, os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/robotics-l16-review-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/robotics-l16-review-cache")
from pathlib import Path
import numpy as np
import sympy as s
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name, condition):
    assert bool(condition), name
    checks.append(name)
t,T=s.symbols('t T', positive=True)
q0,qf,v0,vf=s.symbols('q0 qf v0 vf', real=True)
a0,a1,a2,a3=s.symbols('a0:4')
q=a0+a1*t+a2*t**2+a3*t**3
sol=s.solve([q.subs(t,0)-q0,q.subs(t,T)-qf,s.diff(q,t).subs(t,0)-v0,s.diff(q,t).subs(t,T)-vf],[a0,a1,a2,a3])
check('General a0',sol[a0]==q0);check('General a1',sol[a1]==v0)
check('General a2',s.simplify(sol[a2]-(3*(qf-q0)-(2*v0+vf)*T)/T**2)==0)
check('General a3',s.simplify(sol[a3]-(-2*(qf-q0)+(v0+vf)*T)/T**3)==0)
check('Residual determinant',s.Matrix([[T**2,T**3],[2*T,3*T**2]]).det()==T**4)
D=s.symbols('D',real=True)
rest=s.expand(q.subs(sol).subs({qf:q0+D,v0:0,vf:0}))
check('Rest polynomial',s.simplify(rest-(q0+D*(3*(t/T)**2-2*(t/T)**3)))==0)
check('Rest midpoint position',s.simplify(rest.subs(t,T/2)-q0-D/2)==0)
check('Rest midpoint rate',s.simplify(s.diff(rest,t).subs(t,T/2)-3*D/(2*T))==0)
check('Initial acceleration',s.simplify(s.diff(rest,t,2).subs(t,0)-6*D/T**2)==0)
check('Final acceleration',s.simplify(s.diff(rest,t,2).subs(t,T)+6*D/T**2)==0)
check('Interior jerk',s.simplify(s.diff(rest,t,3)+12*D/T**3)==0)
coeff=s.symbols('b0:6');quintic=sum(c*t**i for i,c in enumerate(coeff))
conditions=[s.diff(quintic,t,k).subs(t,u)-value for k,u,value in [(0,0,q0),(0,T,q0+D),(1,0,0),(1,T,0),(2,0,0),(2,T,0)]]
qs=s.solve(conditions,coeff);quint=s.expand(quintic.subs(qs))
check('Quintic normalized profile',s.simplify(quint-(q0+D*(10*(t/T)**3-15*(t/T)**4+6*(t/T)**5)))==0)
for k in [1,2]:
 for end in [0,T]:check(f'Quintic derivative{k} at{end}',s.diff(quint,t,k).subs(t,end)==0)
for end in [0,T]:check(f'Quintic endpoint jerk{end}',s.simplify(s.diff(quint,t,3).subs(t,end)-60*D/T**3)==0)
# Derive shared via velocity from the two independently substituted cubic segments.
v=s.symbols('v')
qgeneral=q.subs(sol)
left=s.simplify(s.diff(qgeneral,t,2).subs({q0:0,qf:1,v0:0,vf:v,T:1,t:1}))
right=s.simplify(s.diff(qgeneral,t,2).subs({q0:1,qf:2,v0:v,vf:0,T:1,t:0}))
check('Via left acceleration',left==4*v-6);check('Via right acceleration',right==6-4*v)
check('Via acceleration continuity rate',s.solve(left-right,v)==[s.Rational(3,2)])
check('Two rest segment acceleration jump',left.subs(v,0)==-6 and right.subs(v,0)==6)
check('Nonzero-rate example',s.expand(qgeneral.subs({q0:1,qf:5,v0:1,vf:0,T:2}))==1+t+2*t**2-s.Rational(3,4)*t**3)
check('Minimum duration',max(s.Rational(3,2)*60/20,s.sqrt(s.Rational(6*60,15)))==s.sqrt(24))
# Independent literal transcription of physical499-500 numerical lines and plot commands.
theta_0=10;theta_f=70;theta_dot_0=0;theta_dot_f=0;tf=5
c0=theta_0;c1=theta_dot_0
A=np.array([[tf**2,tf**3],[2*tf,3*tf**2]])
B=np.array([theta_f-c0-c1*tf,theta_dot_f-c1])
c2,c3=np.linalg.solve(A,B)
time=np.linspace(0,tf,100)
theta=c0+c1*time+c2*time**2+c3*time**3
velocity=c1+2*c2*time+3*c3*time**2
acceleration=2*c2+6*c3*time
check('Code matrix',np.array_equal(A,[[25,125],[10,75]]));check('Code RHS',np.array_equal(B,[60,0]))
check('Code coefficients',np.allclose([c2,c3],[7.2,-.96]))
check('Code shape',all(z.shape==(100,) for z in [time,theta,velocity,acceleration]))
check('Inclusive endpoints',time[0]==0 and time[-1]==5)
check('Missing midpoint',not np.any(time==2.5))
check('Spacing',np.allclose(np.diff(time),5/99))
check('Adjacent peak times',np.allclose(time[49:51],[245/99,250/99]))
check('Sampled peak formula',np.isclose(max(velocity),18*(1-1/99**2),atol=1e-12))
check('Exact sampled peak formula',s.Rational(18)-s.Rational(288,100)*(s.Rational(5,198))**2==18*(1-s.Rational(1,99**2)))
check('Endpoint rates',np.allclose(velocity[[0,-1]],[0,0]))
check('Endpoint positions',np.allclose(theta[[0,-1]],[10,70]))
check('Endpoint accelerations',np.allclose(acceleration[[0,-1]],[14.4,-14.4]))
check('One second position',np.isclose(c0+c1+c2+c3,16.24))
try:np.linalg.solve(np.zeros((2,2)),[60,0]); singular=False
except np.linalg.LinAlgError:singular=True
check('Zero duration raises',singular)
fig=plt.figure(figsize=(10,6))
for k,(values,title,label) in enumerate([(theta,r'Joint Trajectory $\theta(t)$',r'$\theta(t)$'),(velocity,r'Joint Velocity $\dot{\theta}(t)$',r'$\dot{\theta}(t)$'),(acceleration,r'Joint Acceleration $\ddot{\theta}(t)$',r'$\ddot{\theta}(t)$')],1):
 plt.subplot(3,1,k);plt.plot(time,values);plt.title(title);plt.ylabel(label)
plt.xlabel('Time (s)');plt.tight_layout()
check('Three axes',len(fig.axes)==3);check('Physical figure size',np.array_equal(fig.get_size_inches(),[10,6]))
check('Top plot positions',np.array_equal(fig.axes[0].lines[0].get_ydata(),theta))
check('Middle plot rates',np.array_equal(fig.axes[1].lines[0].get_ydata(),velocity))
check('Bottom plot acceleration',np.array_equal(fig.axes[2].lines[0].get_ydata(),acceleration));plt.close(fig)
rng=np.random.default_rng(16161019);maxres=0
for _ in range(500):
 Q0,Qf,V0,Vf=rng.uniform(-10,10,4);duration=rng.uniform(.5,10)
 mat=np.array([[duration**2,duration**3],[2*duration,3*duration**2]])
 cc=np.linalg.solve(mat,[Qf-Q0-V0*duration,Vf-V0]);formula=np.array([(3*(Qf-Q0)-(2*V0+Vf)*duration)/duration**2,(-2*(Qf-Q0)+(V0+Vf)*duration)/duration**3])
 residuals=[*list(cc-formula),Q0+V0*duration+cc[0]*duration**2+cc[1]*duration**3-Qf,V0+2*cc[0]*duration+3*cc[1]*duration**2-Vf]
 maxres=max(maxres,max(abs(x) for x in residuals));assert max(abs(x) for x in residuals)<1e-9
out={'reviewerId':'define_robotics_data_contracts:L16-independent-reviewer','authorKeysSeen':False,'runAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourcePages':[487,488,489,490,491,492,493,497,498,499,500,501],'method':'Independent symbolic boundary solve, literal source-pixel numerical/plot transcription, and500 random nonzero-endpoint-rate coefficient cases. No author scripts imported.','exactAndCodeAssertionCount':len(checks),'assertions':checks,'randomCases':500,'maxRandomResidual':maxres,'samplePeak':float(max(velocity)),'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT/'audits/W04-L16-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='assertions'},indent=2))
