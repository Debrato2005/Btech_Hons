#!/usr/bin/env python3
"""Author mathematical reconstructions, not independent review or literal source code."""
from pathlib import Path
import json,math,datetime,hashlib,importlib.metadata
import numpy as np
import sympy as sp
from scipy.integrate import trapezoid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]; checks=[]
def ck(name,test,result):
 assert bool(test),(name,result)
 checks.append({'name':name,'passed':True,'result':result})
def tri(x,a,b,c):
 x=np.asarray(x,float);y=np.zeros_like(x)
 if a<b:y=np.where((x>=a)&(x<=b),(x-a)/(b-a),y)
 if b<c:y=np.where((x>=b)&(x<=c),(c-x)/(c-b),y)
 return np.where(x==b,1,y)
def trap(x,a,b,c,d):
 x=np.asarray(x,float);y=np.where((x>=b)&(x<=c),1.,0.)
 if a<b:y=np.where((x>=a)&(x<b),(x-a)/(b-a),y)
 if c<d:y=np.where((x>c)&(x<=d),(d-x)/(d-c),y)
 return y
def avg(w,z):
 w=np.asarray(w,float);z=np.asarray(z,float)
 if not np.any(w>0):raise ValueError('No active singleton weight')
 return float(np.dot(w,z)/w.sum())
ck('Inclusive thermostat boundary',not(23.9>=24) and 24>=24,{'23.9':False,'24.0':True})
ck('Trapezoid falling ramp',trap(8,0,4,6,10)==.5,.5)
ck('Triangle two branches',np.allclose(tri([2,8],0,5,10),[.4,.4]),[.4,.4])
ck('Gaussian one width',abs(math.exp(-.5)-.6065306597126334)<1e-14,math.exp(-.5))
ck('Min/max example',min(.27,.65)==.27 and max(.27,.65)==.65,[.27,.65])
ck('Minimum clipping',min(.4,.7)==.4,.4)
ck('Maximum overlapping aggregation',max(.4,.6)==.6,.6)
try:avg([0,0],[20,50])
except ValueError:ck('Zero-weight output is explicitly undefined',True,'ValueError rather than invented output')
else:raise AssertionError('No-fire fallback test failed')
ck('Cooling antecedent grid',4*3==12,12)
ck('Warm/Hot at exact 80',tri(80,65,75,85)==.5 and tri(80,75,85,95)==.5,[.5,.5])
ck('Hot exact graph versus supplied grade',abs(float(tri(78,75,85,95))-.3)<1e-14 and .3!=.27,{'exactGraph':.3,'supplied':.27})
ck('Humid exact graph versus supplied grade',abs(float(tri(70,40,60,90))-2/3)<1e-14 and 2/3!=.65,{'exactGraph':2/3,'supplied':.65})
cooling={
'Very-hot':['Fast','Fast','Medium'],
'Hot':['Fast','Medium','Medium'],
'Warm':['Medium','Slow','Slow'],
'Cold':['Slow','Off','Off']}
humidity=['Very-humid','Humid','Dry']; tg={'Very-hot':0,'Hot':.27,'Warm':.7,'Cold':0};hg={'Very-humid':0,'Humid':.65,'Dry':0}
activations={o:0 for o in ['Off','Slow','Medium','Fast']}; fired=[]
for i,(t,rows) in enumerate(cooling.items()):
 for j,(h,o) in enumerate(zip(humidity,rows)):
  a=min(tg[t],hg[h]);activations[o]=max(activations[o],a)
  if a:fired.append({'rule':3*i+j+1,'strength':a,'output':o})
ck('All twelve cooling rules transcribed',sum(map(len,cooling.values()))==12,cooling)
ck('Source active rule paths',fired==[{'rule':5,'strength':.27,'output':'Medium'},{'rule':8,'strength':.65,'output':'Slow'}],fired)
ck('No unintended active output',activations=={'Off':0,'Slow':.65,'Medium':.27,'Fast':0},activations)
weighted=avg([.65,.27],[20,50])
ck('Singleton weighted output',np.isclose(weighted,1325/46),weighted)
ck('Source singleton rounding',round(weighted)==29,29)
ck('Swapped-weight distractor',np.isclose(avg([.27,.65],[20,50]),41.19565217391305),avg([.27,.65],[20,50]))
ck('Positive common weight scaling',np.isclose(avg([.325,.135],[20,50]),weighted),weighted)
# Exact symbolic integration of the declared max envelope, separately checked against a dense numeric reconstruction.
z=sp.symbols('z');segments=[(0,13,z/20),(13,sp.Rational(61,2),sp.Rational(65,100)),(sp.Rational(61,2),sp.Rational(419,10),(50-z)/30),(sp.Rational(419,10),sp.Rational(719,10),sp.Rational(27,100)),(sp.Rational(719,10),80,(80-z)/30)]
area=sum(sp.integrate(f,(z,a,b)) for a,b,f in segments);moment=sum(sp.integrate(z*f,(z,a,b)) for a,b,f in segments);centroid=moment/area
ck('Exact clipped-area integral',area==sp.Rational(2403,80),str(area))
ck('Exact clipped first moment',moment==sp.Rational(2429293,2400),str(moment))
ck('Exact Mamdani centroid',centroid==sp.Rational(2429293,72090),float(centroid))
x=np.linspace(0,100,100001);slow=tri(x,0,20,50);medium=tri(x,20,50,80);union=np.maximum(np.minimum(.65,slow),np.minimum(.27,medium));numeric=trapezoid(x*union,x)/trapezoid(union,x)
ck('Cross-method numeric centroid',abs(numeric-float(centroid))<1e-9,numeric)
ck('Source Mamdani rounding',round(numeric)==34,34)
ck('Methods not falsely equated',abs(numeric-weighted)>4,{'singleton':weighted,'areaCentroid':numeric})
fig,ax=plt.subplots(figsize=(10,5));ax.plot(x,slow,label='Slow: triangle (0,20,50)',alpha=.5);ax.plot(x,medium,label='Medium: triangle (20,50,80)',alpha=.5);ax.fill_between(x,union,alpha=.3,label='max of clipped outputs');ax.plot(x,union,color='black',lw=2);ax.axvline(numeric,color='purple',label=f'Area centroid {numeric:.4f}%');ax.axvline(weighted,color='red',ls='--',label=f'Singleton average {weighted:.4f}%');ax.set(xlabel='Power coordinate (%)',ylabel='Membership',xlim=(0,85),ylim=(0,1.05),title='Declared source-geometry reconstruction, not source simulation code');ax.legend(fontsize=8);fig.tight_layout();out=R/'audits/W08-L40-centroid-reconstruction.png';fig.savefig(out,dpi=160);plt.close(fig)
# Explicit robot rule transcription, with no claim to know exact source simulator output shapes.
terr=['Very-Rough','Rough','Moderate','Smooth']
robot={
'Large-Positive':['Very-Slow','Slow','Medium','Medium'],
'Positive':['Very-Slow','Slow','Medium','Fast'],
'Level':['Slow','Medium','Fast','Very-Fast'],
'Negative':['Very-Slow','Slow','Medium','Fast'],
'Large-Negative':['Very-Slow','Very-Slow','Slow','Medium']}
ck('All twenty robot rules',sum(map(len,robot.values()))==20,robot)
ck('Moderate signed rows match',robot['Positive']==robot['Negative'],robot['Positive'])
ck('Extreme signed rows differ only as printed',robot['Large-Positive']!=robot['Large-Negative'] and robot['Large-Positive'][0]==robot['Large-Negative'][0] and robot['Large-Positive'][-1]==robot['Large-Negative'][-1],{'positive':robot['Large-Positive'],'negative':robot['Large-Negative']})
ck('Level row is complete',robot['Level']==['Slow','Medium','Fast','Very-Fast'],robot['Level'])
ck('Terrain index 30 overlap',tri(30,20,40,60)==.5 and trap(30,0,0,20,40)==.5,{'Moderate':.5,'Smooth':.5})
sg={'Positive':.95,'Large-Positive':.05,'Level':0,'Negative':0,'Large-Negative':0};rg={'Very-Rough':0,'Rough':0,'Moderate':.5,'Smooth':.5};outs={o:0 for o in ['Very-Slow','Slow','Medium','Fast','Very-Fast']}
for slope,row in robot.items():
 for terrain,o in zip(terr,row):outs[o]=max(outs[o],min(sg[slope],rg[terrain]))
ck('Integrated robot aggregation',outs=={'Very-Slow':0,'Slow':0,'Medium':.5,'Fast':.5,'Very-Fast':0},outs)
robot_speed=avg([outs[o] for o in outs],[3,6,10,15,19]);ck('Integrated robot singleton speed',robot_speed==12.5,robot_speed)
ck('Wrong sum-aggregation distractor',np.isclose(avg([.6,.5],[10,15]),12.272727272727273),avg([.6,.5],[10,15]))
ck('Slope-weight-only distractor',np.isclose(avg([.95,.05],[10,15]),10.25),10.25)
ck('Repeated rule consequents allow plateaus',robot['Large-Positive'][2]==robot['Large-Positive'][3],'Medium for both Moderate and Smooth')
# Full grid tests only the declared membership/rule coverage, not physical stability or a hidden source implementation.
grid_count=0
for t in np.linspace(60,100,81):
 temp=[float(trap(t,90,95,100,100)),float(tri(t,75,85,95)),float(tri(t,65,75,85)),float(trap(t,60,60,65,70))]
 for h in np.linspace(40,100,121):
  hum=[float(trap(h,70,90,100,100)),float(tri(h,40,60,90)),float(trap(h,40,40,45,50))]
  assert max(min(a,c) for a in temp for c in hum)>0
  grid_count+=1
ck('Declared cooling input grid has a fired rule',grid_count==9801,{'points':grid_count,'scope':'Finite grid, not an all-continuous-input or safety proof'})
rng=np.random.default_rng(40019)
for _ in range(1000):
 a,beta,c=sorted(rng.uniform(-20,20,3));xs=rng.uniform(-25,25,10);mu=tri(xs,a,beta,c)
 assert np.all((mu>=0)&(mu<=1))
 w=rng.uniform(.001,1,5);v=rng.uniform(-50,50,5);o=avg(w,v);assert v.min()<=o<=v.max()
 scale=rng.uniform(.001,1);assert np.isclose(avg(scale*w,v),o)
 u,vv=rng.uniform(0,1,2);assert min(u,vv)<=u<=max(u,vv) and min(u,vv)<=vv<=max(u,vv)
ck('Varied mathematical invariants',True,{'trials':1000,'comparisons':4000})
report={'authorId':'build_offline_study_interface:L40-author','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentReview':False,'sourceCodePresent':False,'scope':'Author-added mathematical implementation from actual inspected source diagrams/rules and explicitly supplied test contexts. No source simulator code is available. No author check is independent verification.','namedChecks':len(checks),'checks':checks,'coolingRules':cooling,'robotRules':robot,'exactCentroid':{'area':str(area),'firstMoment':str(moment),'centroid':str(centroid),'decimal':float(centroid)},'finiteCoverageGridPoints':grid_count,'randomTrials':1000,'randomComparisons':4000,'versions':{n:importlib.metadata.version(n) for n in ['numpy','scipy','sympy','matplotlib']},'figure':{'path':str(out.relative_to(R)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},'sourceQualifications':['Exact plotted Hot/Humid interpolation differs from supplied grades.','Rounded singleton and area results are distinct, both reproducible under declared assumptions.','Robot output spikes versus Mamdani surface leave unprovided settings; singleton calculation is an explicit reconstruction.']}
(R/'audits/W08-L40-author-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'namedChecks':len(checks),'finiteGridPoints':grid_count,'variedComparisons':4000,'centroid':float(centroid)}))
