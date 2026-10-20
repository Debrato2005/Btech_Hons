"""Independent deterministic checks, not ROS/Gazebo/vision/hardware reproduction."""
import math, random, json, datetime, pathlib
import numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
fixed=[]
def check(label, actual, expected):
 assert np.allclose(actual,expected,rtol=1e-11,atol=1e-11),(label,actual,expected)
 fixed.append({'label':label,'actual':np.asarray(actual).tolist(),'expected':np.asarray(expected).tolist(),'pass':True})
def wheels(v,w,r,L):
 if r<=0 or L<=0: raise ValueError('positive geometry required')
 return np.array([(v+L*w/2)/r,(v-L*w/2)/r])
def body(a,b,r,L):
 if r<=0 or L<=0: raise ValueError('positive geometry required')
 return np.array([r*(a+b)/2,r*(a-b)/L])
def arc(s,t,theta=0):
 # Independent midpoint-sinc representation, stable at zero turn.
 factor=1 if t==0 else math.sin(t/2)/(t/2)
 return np.array([s*factor*math.cos(theta+t/2),s*factor*math.sin(theta+t/2),t])
check('Q006 forward',body(6,2,.1,.5),[.4,.8])
check('Q007 zero translation',body(4,-4,.1,.5),[0,1.6])
check('Q008 inverse',wheels(.3,1,.1,.4),[5,1])
check('Q009 circular radius',.4/.8,.5)
check('Q017 decoded wheel travel',300/1200*2*math.pi*.1,.05*math.pi)
check('Q020 PID',.2*(4-3)+.1*(.2+(4-3)*.1)+.01*((4-3)-.5)/.1,.28)
Tmo=np.array([[0,-1,1],[1,0,2],[0,0,1.]])
Tob=np.array([[1,0,2],[0,1,0],[0,0,1.]])
check('Q024 homogeneous point',Tmo@Tob@np.array([1,0,1]),[1,5,1])
P,Rn=.04,.01; K=P/(P+Rn)
check('Q028 scalar update',[1+K*.3,(1-K)*P],[1.24,.008])
p=np.array([.5,.3,.2])*np.array([.2,.5,.5]);check('Q037 normalized weights',p/p.sum(),[2/7,3/7,2/7])
check('Q043 feasible route costs',[8+.5*6,10+.5*0],[11,10])
check('Q054 added pinhole',(np.array([420-320,240-240,500])/500)*(1500*.001),[.3,0,1.5])
check('Q061 playback',20*3.25,65)
check('Q062 exact arc',arc(.15,.2),[.75*math.sin(.2),.75*(1-math.cos(.2)),.2])
check('Q063 wheel scaling',wheels(.3*.8,1*.8,.1,.4),[4,.8])
check('Q064 corridor width',2*(.25+.1),.7)
check('zero arc limit',arc(.3,0,math.pi/2),[0,.3,0])
check('pure spin arc',arc(0,.5,.2),[0,0,.5])
check('Q020 wrong derivative option',.2+.03+.01*.5,.235)
check('Q037 likelihood-only distractor',np.array([.2,.5,.5])/1.2,[1/6,5/12,5/12])
rng=random.Random(591877); counts={k:0 for k in ['forward_inverse','arc_composition','encoder_conversion','scalar_posterior','particle_weights','pinhole_roundtrip','rate_limit_scaling','corridor_clearance']}
for _ in range(1000):
 r=rng.uniform(.01,.9);L=rng.uniform(.05,2);v=rng.uniform(-2,2);w=rng.uniform(-5,5)
 ws=wheels(v,w,r,L); assert np.allclose(body(*ws,r,L),[v,w],atol=1e-12);counts['forward_inverse']+=1
 s=rng.uniform(-3,3);t=rng.uniform(-5,5);theta=rng.uniform(-math.pi,math.pi)
 a=arc(s,t,theta);b=arc(s/2,t/2,theta);c=arc(s/2,t/2,theta+t/2);assert np.allclose(a,b+c,atol=1e-12);counts['arc_composition']+=1
 N=rng.randint(1,10000);n=rng.randint(-10000,10000);dist=2*math.pi*r*n/N;assert math.isclose(dist/(2*math.pi*r),n/N,abs_tol=1e-12);counts['encoder_conversion']+=1
 P=10**rng.uniform(-6,3);V=10**rng.uniform(-6,3);x=rng.uniform(-20,20);z=rng.uniform(-20,20);K=P/(P+V)
 assert np.allclose([x+K*(z-x),(1-K)*P],[(x/P+z/V)/(1/P+1/V),1/(1/P+1/V)],rtol=1e-7,atol=1e-10);counts['scalar_posterior']+=1
 prior=np.array([rng.random()+.001 for _ in range(5)]);prior/=prior.sum();lik=np.array([rng.random()+.001 for _ in range(5)]);post=prior*lik;post/=post.sum();assert math.isclose(post.sum(),1) and np.all(post>0);counts['particle_weights']+=1
 Z=rng.uniform(.05,15);fx=rng.uniform(50,2000);fy=rng.uniform(50,2000);cx=rng.uniform(100,700);cy=rng.uniform(100,700);u=rng.uniform(0,1000);vv=rng.uniform(0,1000);X=(u-cx)*Z/fx;Y=(vv-cy)*Z/fy;assert np.allclose([fx*X/Z+cx,fy*Y/Z+cy],[u,vv]);counts['pinhole_roundtrip']+=1
 limit=rng.uniform(.1,10);factor=min(1,limit/max(abs(ws)));scaled=wheels(factor*v,factor*w,r,L);assert max(abs(scaled))<=limit+1e-10;assert np.allclose(scaled,ws*factor);assert math.isclose((factor*v)*w,(factor*w)*v,abs_tol=1e-12);counts['rate_limit_scaling']+=1
 rad=rng.uniform(.01,2);margin=rng.uniform(0,1);width=rng.uniform(.01,6);clearance=width/2-rad;assert (clearance>=margin)==(width>=2*(rad+margin));counts['corridor_clearance']+=1
invalid=0
for r,L in [(0,.2),(-1,.2),(.1,0),(.1,-.2)]:
 for fun,args in [(wheels,(.3,.2,r,L)),(body,(1,2,r,L))]:
  try:fun(*args)
  except ValueError:invalid+=1
  else:raise AssertionError('bad geometry accepted')
# Fixed offered numerical alternatives remain distinct at printed precision.
option_sets={'Q006':[(.2,.8),(.8,.4),(.4,.8),(.4,-.8)],'Q008':[(5,1),(1,5),(3,3),(7,-1)],'Q017':[.05*math.pi,.025,.2*math.pi,.0125*math.pi],'Q020':[.28,.23,.27,.235],'Q024':[(1,5),(4,2),(-1,5),(3,3)],'Q028':[(1.24,.008),(1.06,.032),(1.15,.025),(1.3,0)],'Q037':[(2/7,3/7,2/7),(.5,.3,.2),(1/6,5/12,5/12),(.1,.15,.1)],'Q054':[(.2,0,1.5),(.3,0,1.5),(.3,0,1500),(0,0,1.5)],'Q062':[(.1490,-.01495,-.2),(.298,.0299,.2),(.15,0,.2),(.149,.01495,.2)]}
for label,opts in option_sets.items(): assert len({tuple(np.round(np.atleast_1d(o),5)) for o in opts})==len(opts),label
result={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewerId':'independent-reviewer-robotics-batches-v2','fixedAssertionCount':len(fixed),'fixedChecks':fixed,'variedCounts':counts,'variedTotal':sum(counts.values()),'invalidGeometryRejected':invalid,'fixedDistinctOptionSetsChecked':list(option_sets),'execution':'Default installed Python and NumPy only. Source-derived or explicitly added arithmetic; no author script or ROS/Gazebo/model/browser/video/hardware executed. These are not numerical-family generator validations.'}
(R/'audits/W12-L59-independent-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='fixedChecks'}))
