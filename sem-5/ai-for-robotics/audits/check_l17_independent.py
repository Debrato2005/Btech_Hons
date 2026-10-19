"""Independent checks derived from viewed source pixels and frozen blind packet, not author code."""
import numpy as np, math, json, pathlib, sys
from fractions import Fraction as F
P=pathlib.Path(__file__).resolve().parents[1];checks=[]
def check(name,actual,expected):
 ok=bool(np.allclose(actual,expected,rtol=1e-10,atol=1e-10)) if not isinstance(expected,(str,bool,F)) else actual==expected
 checks.append({'name':name,'passed':bool(ok),'actual':str(actual),'expected':str(expected)});assert ok,name
Rx=np.array([[1,0,0],[0,0,-1],[0,1,0]]);Ry=np.array([[0,0,1],[0,1,0],[-1,0,0]])
check('relative_rotation_90x_90y_angle',math.degrees(math.acos((np.trace(Rx.T@Ry)-1)/2)),120)
check('absolute_rotation_vector_difference_not_relative_angle',abs(90*math.sqrt(2)-120)>7,True)
check('same_axis_shortest_unwrap',190-170,20)
check('two_link_inner_hole',abs(2-1)>0,True)
J=np.diag([1,.01]);check('jacobian_inverse',np.linalg.solve(J,[0,1]),[0,100]);check('direction_exception',np.linalg.solve(J,[1,0]),[1,0]);check('rate_limit',.01*10,.1)
check('cubic_pose_rate_accel',[1+2*.5+3*.5**2+4*.5**3,2+6*.5+12*.5**2,6+24*.5],[3.25,8,18]);check('local_time',5.2-5,.2)
# Analytic polynomial expansion: v*(t-(t-c))=v*c, so derivative has no v.
xj,v,a,c=2.,3.,4.,.7;t=1.2;s=t-c;h=1e-5
literal=lambda z:xj+v*(z-(z-c))+.5*a*(z-c)**2
check('literal_blend_derivative',(literal(t+h)-literal(t-h))/(2*h),a*s)
check('corrected_blend',[2+3*.5+2*.5**2,3+4*.5],[4,5])
check('noncommon_progress_counterexample',[.5,.5**2],[.5,.25])
R=Rx.astype(float);p=np.array([2.,3.,4.]);T=np.block([[R,p[:,None]],[np.zeros((1,3)),np.ones((1,1))]])
check('homogeneous_map',(T@np.array([1.,2.,3.,1.]))[:3],R@np.array([1.,2.,3.])+p)
q=np.array([0,.01,.04]);vv=np.diff(q)/.1;check('backward_velocity_acceleration',[vv[-1],np.diff(vv)[0]/.1],[.3,2]);check('unwrap_rate',(181-179)/.1,20)
check('torque_load_inertia',(12-8)/2,2);check('grid_counts',[10**2,10**6,10**6/10**2],[100,1000000,10000])
# Fresh transcription of source values, not importing any author implementation.
tf,dt=4.,.2;t=np.arange(0,tf+dt,dt);start=np.array([.7,.2,0.]);end=np.array([.3,-.4,60.]);rates=(end-start)/tf;poses=start+t[:,None]*rates
check('time_samples_intervals',[len(t),len(t)-1,t[-1]],[21,20,4]);check('affine_rates',rates,[-.1,-.15,15]);check('midpoint',poses[10],[.5,-.1,30]);check('degrees_radians',math.radians(15),math.pi/12);check('length_speed',[np.linalg.norm(end[:2]-start[:2]),np.linalg.norm(rates[:2])],[math.sqrt(.52),math.sqrt(.0325)])
check('zero_crossing',F(1,5)/F(3,20),F(4,3))
check('row7',' '.join([f'{t[7]:.1f}',f'{poses[7,0]:.3f}',f'{poses[7,1]:.3f}',f'{poses[7,2]:.1f}']),'1.4 0.560 -0.010 21.0')
check('frequency',1/dt,5);check('ones_like_shape',np.ones_like(t).shape==t.shape,True);check('zero_arrays',np.count_nonzero(np.zeros_like(t)),0)
rows=[]
for k in range(21):
 exact=[F(k,5),F(7,10)-F(k,50),F(1,5)-F(3*k,100),F(3*k)]
 check(f'table_row_{k}',np.r_[t[k],poses[k]],[float(x) for x in exact]);rows.append([f'{float(exact[0]):.1f}',f'{float(exact[1]):.3f}',f'{float(exact[2]):.3f}',f'{float(exact[3]):.1f}','-0.100','-0.150','15.0','0.0','0.0','0.0'])
# Distinct affine cases, not claiming any persistent numerical generator exists.
rng=np.random.default_rng(170519)
for k in range(500):
 p0=rng.uniform(-20,20,3);pf=rng.uniform(-20,20,3);duration=rng.uniform(.01,100);u=rng.uniform(0,1);r=(pf-p0)/duration;x=p0+r*(u*duration)
 assert np.allclose(x,(1-u)*p0+u*pf);assert np.allclose(p0+r*duration,pf);assert np.isclose(np.linalg.norm(pf-p0)/duration,np.linalg.norm(r))
checks.append({'name':'500_varied_affine_endpoint_common_progress_speed_cases','passed':True})
report={'reviewerId':'independent-reviewer-robotics-batches-v2','pythonVersion':sys.version.split()[0],'numpyVersion':np.__version__,'checks':checks,'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'notes':['No author script imported or rerun.','Source table independently reproduced from fractional arithmetic for every row.','No robot execution, IK, dynamic feasibility or obstacle clearance test claimed.','No persisted question variant generator exists in this packet.']}
(P/'audits/W04-L17-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n');(P/'audits/W04-L17-independent-table.txt').write_text('\n'.join(' '.join(row) for row in rows)+'\n');print({'passed':report['passed'],'failed':report['failed'],'variedCases':500})
