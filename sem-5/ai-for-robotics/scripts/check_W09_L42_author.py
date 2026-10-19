"""Author-added executable reconstruction of L42 mathematics and pseudocode parts.
The slide has language-neutral pseudocode, not runnable Python. All extra conventions
are stated here; this is not independent verification or a full deployed planner.
"""
from pathlib import Path
import math,json,random,platform,hashlib,datetime,itertools
from fractions import Fraction as F
import sympy as sp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
OBS={(1,1),(1,2),(2,2),(2,4),(3,2),(4,3)};S=(0,0);G=(5,5)
P=[[(0,3),(4,5)],[(2,1),(5,3)],[(0,2),(3,4)],[(3,0),(5,4)],[(1,3),(4,4)],[(2,0),(5,2)]]
def decode(w,hfirst=True):
 path=[S]
 for dest in [*w,G]:
  for j in ([1,0] if hfirst else [0,1]):
   while path[-1][j]!=dest[j]:
    a=list(path[-1]);a[j]+=1 if a[j]<dest[j] else -1;path.append(tuple(a))
 return path

def evaluate(w,alpha=10,beta=1):
 path=decode(w);ds=[(b[0]-a[0],b[1]-a[1]) for a,b in zip(path,path[1:])]
 L=len(ds);hits=[a for a in path[1:] if a in OBS];turns=sum(a!=b for a,b in zip(ds,ds[1:]));cost=L+alpha*len(hits)+beta*turns
 return dict(path=path,L=L,obstacles=hits,Nobs=len(hits),Nturn=turns,cost=cost,fitness=1/(1+cost))
def potential(a,b):
 return -4*math.sin(a)-6*math.cos(a)-4*math.sin(b)-2*math.cos(b)
def fitdeg(a,b):return -potential(math.radians(a),math.radians(b))-7
checks=[]
def ck(name,ok,value):
 assert ok,(name,value)
 checks.append(dict(name=name,passed=True,result=value))
rows=[evaluate(p) for p in P]
ck('All six route lengths',[x['L'] for x in rows]==[10]*6,[x['L'] for x in rows])
ck('All original collision lists',[x['obstacles'] for x in rows]==[[],[(1,1),(2,2),(4,3)],[(2,4)],[(3,2)],[(2,4)],[(2,2),(3,2)]],[x['obstacles'] for x in rows])
ck('All original turn counts',[x['Nturn'] for x in rows]==[1,4,3,3,5,3],[x['Nturn'] for x in rows])
ck('All original costs',[x['cost'] for x in rows]==[11,44,23,23,25,33],[x['cost'] for x in rows])
ck('P2 printed denominator error',F(1,45)!=F(1,12) and round(1/45,4)==.0222,{'correct':'1/45','printed':'1/12'})
fr=[F(1,1+x['cost']) for x in rows];rd=[F(str(round(float(f),4))) for f in fr]
ck('Rounded total .2568',sum(rd)==F('.2568'),str(sum(rd)))
ck('Exact initial mean',round(float(sum(fr)/6),4)==.0428,float(sum(fr)/6))
pr=[f/sum(rd) for f in rd];cum=list(itertools.accumulate(pr));draws=[.15,.35,.5,.6,.72,.9];pool=[next(i+1 for i,x in enumerate(cum) if r<float(x)) for r in draws]
ck('Roulette six draws',pool==[1,2,3,4,4,6],pool)
ck('Only P4 repeated',pool.count(1)==1 and pool.count(4)==2,{'P1':pool.count(1),'P4':pool.count(4)})
ck('P1 selection probability',round(float(pr[0]),4)==.3244,float(pr[0]))
children=[]
for i,j in [(0,2),(3,5),(1,3)]:children.extend([[P[i][0],P[j][1]],[P[j][0],P[i][1]]])
ck('All crossover children',children==[[(0,3),(3,4)],[(0,2),(4,5)],[(3,0),(5,2)],[(2,0),(5,4)],[(2,1),(5,4)],[(3,0),(5,3)]],children)
unmutated=evaluate(children[0]);children[0]=[(0,3),(3,5)];new=[evaluate(c) for c in children]
ck('All mutated-generation costs',[x['cost'] for x in new]==[11,11,23,33,44,33],[x['cost'] for x in new])
ck('Mutation changes collision and turns',unmutated['Nobs']==1 and unmutated['Nturn']==3 and new[0]['Nobs']==0 and new[0]['Nturn']==1,{'before':unmutated,'after':new[0]})
ck('Genotype differs but route same',children[0]!=children[1] and new[0]['path']==new[1]['path']==rows[0]['path'],new[0]['path'])
nf=[F(1,1+x['cost']) for x in new];mean6=sum(nf)/6;mean7=(sum(nf)+F(1,24))/7
ck('True six-child mean',round(float(mean6),4)==.0482,float(mean6))
ck('Printed mean counts comparison row',round(float(mean7),4)==.0473,float(mean7))
ck('Crossover C2 already best',new[1]['fitness']==rows[0]['fitness'],new[1]['fitness'])
ck('C5 uniquely worst current child',sum(x['cost']==44 for x in new)==1 and rows[1]['cost']==44,44)
free=[(r,c) for r in range(6) for c in range(6) if (r,c) not in OBS]
allrows=[(w,evaluate(w)) for w in itertools.product(free,repeat=2)]
ck('Exhaustive declared two-waypoint space',len(allrows)==900,900)
best=min(x['cost'] for w,x in allrows)
ck('Bounded exact grid optimum',best==11 and all(x['L']>=10 and x['Nturn']>=1 for w,x in allrows),{'minimumCost':best,'proof':'Every four-neighbor S-to-G path needs at least10 moves and at least1 direction change; nonnegative penalties. P1 attains11.'})
# Soft-penalty counterexample uses arbitrary admissible path costs, not an assertion about the finite source pool.
ck('Finite collision penalty counterexample',10+10+0<30+0+1,{'collidingCost':20,'collisionFreeCost':31})
a,b=sp.symbols('a b',real=True);pi=-4*sp.sin(a)-6*sp.cos(a)-4*sp.sin(b)-2*sp.cos(b)
grad=[sp.diff(pi,z) for z in [a,b]]
ck('Correct actual gradients',sp.simplify(grad[0]-(-4*sp.cos(a)+6*sp.sin(a)))==0 and sp.simplify(grad[1]-(-4*sp.cos(b)+2*sp.sin(b)))==0,[str(x) for x in grad])
a0=math.atan2(4,6);b0=math.atan2(4,2);emin=-math.sqrt(52)-math.sqrt(20)
ck('Equilibrium angles',abs(a0-.5880026035475675)<1e-14 and abs(b0-1.1071487177940904)<1e-14,{'radians':[a0,b0],'degrees':[math.degrees(a0),math.degrees(b0)]})
ck('Energy at exact equilibrium',abs(potential(a0,b0)-emin)<1e-12,emin)
ck('Positive Hessian at equilibrium',abs(4*math.sin(a0)+6*math.cos(a0)-math.sqrt(52))<1e-12 and abs(4*math.sin(b0)+2*math.cos(b0)-math.sqrt(20))<1e-12,[math.sqrt(52),math.sqrt(20)])
ck('Radian typo .558',abs(math.radians(33.7)-.588)<.001 and abs(a0-.558)>.02,a0)
ck('Angle grid sixteen inclusive values',[6*i for i in range(16)]==list(range(0,91,6)),list(range(0,91,6)))
ck('Eight bits total',2**8==16**2==256,256)
angles=[(0,0),(12,6),(6,30),(12,48),(36,60),(84,48),(84,78),(42,72)];fits=[fitdeg(*x) for x in angles]
ck('All table recomputations',[round(x,2) for x in fits]==[1,2.11,3.12,4.01,4.67,1.92,1.93,4.56],fits)
ck('Most material table typo',round(fits[4],2)==4.67 and not math.isclose(fits[4],4.60,abs_tol=.005),fits[4])
ck('Landscape false maximum',-potential(a0,b0)>8 and -potential(0,0)==8,{'atOrigin':8,'maximum':-emin})
ck('Fitness can be negative within bounds',abs(fitdeg(90,0)+1)<1e-12,fitdeg(90,0))
dgrid=[(fitdeg(i,j),i,j) for i in range(0,91,6) for j in range(0,91,6)];discrete=max(dgrid)
ck('Discrete optimum differs from continuous',discrete[1:]==(36,66) and discrete[0]<-emin-7,{'fitness':discrete[0],'angles':discrete[1:],'chromosome':'0110 1011'})
ck('Constant shifts preserve order but alter roulette ratios',fits[4]>fits[0] and not math.isclose(fits[4]/fits[0],(fits[4]+7)/(fits[0]+7)),{'shiftedRatio':fits[4]/fits[0],'unshiftedRatio':(fits[4]+7)/(fits[0]+7)})
ck('Added cost exercise',12+10+2==24 and F(1,25)==F(1,1+24),{'cost':24,'fitness':'1/25'})
ck('Expected six-draw copies',F('0.3244')*6==F('1.9464'),1.9464)
ck('Independent gene mutation',1-F('0.9')**2==F('0.19'),.19)
ck('Fixed-size elite capacity',6-1==5,5)
ck('Evaluation budget units',50*100*2/1000==10,{'milliseconds':10000,'seconds':10})
ck('Nearest-level quantization bound',max(min(abs(v-6*d) for d in range(16)) for v in np.linspace(0,90,901))<=3,3)
ck('Full two-angle decoding',(int('0110',2)*6,int('1011',2)*6)==(36,66),[36,66])
# Model-consistent random cross-checks against independent closed-form segment lengths and bounds.
rng=random.Random(421019);comparisons=0
for k in range(1000):
 w=[rng.choice(free),rng.choice(free)];x=evaluate(w);pts=[S,*w,G]
 assert x['L']==sum(abs(v[0]-u[0])+abs(v[1]-u[1]) for u,v in zip(pts,pts[1:]));comparisons+=1
 assert x['path'][0]==S and x['path'][-1]==G and all(abs(v[0]-u[0])+abs(v[1]-u[1])==1 for u,v in zip(x['path'],x['path'][1:]));comparisons+=1
 aa,bb=rng.random()*math.pi/2,rng.random()*math.pi/2
 assert potential(aa,bb)>=emin-1e-12 and -1-1e-12<=-potential(aa,bb)-7<=-emin-7+1e-12;comparisons+=1
 d=rng.randrange(16);assert 0<=6*d<=90 and int(format(d,'04b'),2)==d;comparisons+=1
ck('Varied invariants',comparisons==4000,{'trials':1000,'comparisons':comparisons})
fig,ax=plt.subplots(1,3,figsize=(13,4))
for aa,(title,x) in zip(ax[:2],[('P2: three obstacle visits',rows[1]),('C1-prime: no obstacle visits',new[0])]):
 for r,c in OBS:aa.scatter(c,r,s=220,c='#e6a0a0',marker='s')
 rr,cc=zip(*x['path']);aa.plot(cc,rr,'o-',color='#234f98',lw=2);aa.set(xlim=(-.5,5.5),ylim=(5.5,-.5),xticks=range(6),yticks=range(6),xlabel='Column',ylabel='Row',title=title);aa.grid(alpha=.2);aa.set_aspect('equal')
t=np.linspace(0,90,181);xx,yy=np.meshgrid(t,t);zz=4*np.sin(np.radians(xx))+6*np.cos(np.radians(xx))+4*np.sin(np.radians(yy))+2*np.cos(np.radians(yy))-7
cs=ax[2].contourf(xx,yy,zz,levels=20);ax[2].plot(math.degrees(a0),math.degrees(b0),'w*',ms=12,label='Continuous optimum');ax[2].plot(36,66,'rx',ms=9,label='4-bit optimum');ax[2].set(xlabel='theta1 (degrees)',ylabel='theta2 (degrees)',title='Reconstructed F = -Pi - 7');ax[2].legend(fontsize=7);fig.colorbar(cs,ax=ax[2]);fig.tight_layout();out=R/'audits/W09-L42-reconstruction.png';fig.savefig(out,dpi=150);plt.close(fig)
report={'authorId':'build_offline_study_interface:L42-author','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentReview':False,'sourceCodePresent':'Language-neutral pseudocode only; no literal runnable code.','scope':'Author-added reconstruction of inspected grid traces and pendulum mathematics, plus declared completion conventions. Not independent review or physical safety validation.','conventions':{'coordinates':'zero-based row,column','decoding':'horizontal then vertical per segment','turns':'changes between consecutive unit moves, merging across waypoint boundaries','violations':'occupied entered-cell visits; all source paths have no repeated occupied visits','gen1':'six children; mutated C1 replaces unmutated C1','pendulum':'consistent force/length units; trig receives radians after degree conversion','extraSearch':'900 ordered free-cell waypoint pairs, repeats and endpoints allowed;256 binary angle pairs'},'namedChecks':len(checks),'checks':checks,'initialRows':rows,'newRows':new,'unmutatedComparison':unmutated,'roulette':{'roundedWeights':[str(x) for x in rd],'probabilities':[float(x) for x in pr],'draws':draws,'pool':pool},'means':{'initial':float(sum(fr)/6),'sixChildren':float(mean6),'sevenDisplayedRows':float(mean7)},'pendulumTable':{'anglesDegrees':angles,'computedFitness':fits,'printedFitness':[1,2.10,3.11,4.01,4.60,1.91,1.93,4.55]},'discreteOptimum':discrete,'randomTrials':1000,'randomComparisons':comparisons,'versions':{'python':platform.python_version(),'numpy':np.__version__,'sympy':sp.__version__},'figure':{'path':str(out.relative_to(R)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}}
(R/'audits/W09-L42-author-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'namedChecks':len(checks),'randomComparisons':comparisons,'allPass':True}))
