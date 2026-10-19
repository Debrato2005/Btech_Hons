"""Independent v2 repair/gap computations, source-derived reconstruction only."""
from pathlib import Path
import math,json,hashlib,datetime,random
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,condition,value=None):assert condition,(name,value);checks.append(dict(name=name,value=value))
obs={(1,1),(1,2),(2,2),(2,4),(3,2),(4,3)}
def evaluate(w):
 p=[(0,0)];dirs=[]
 for target in [*w,(5,5)]:
  for j in [1,0]:
   while p[-1][j]!=target[j]:
    nxt=list(p[-1]);nxt[j]+=1 if target[j]>nxt[j]else-1;d=tuple(nxt[i]-p[-1][i]for i in range(2));dirs.append(d);p.append(tuple(nxt))
 hits=[x for x in p[1:]if x in obs];turns=sum(a!=b for a,b in zip(dirs,dirs[1:]));cost=len(dirs)+10*len(hits)+turns
 return dict(path=p,length=len(dirs),hits=hits,turns=turns,cost=cost,fitness=1/(1+cost))
P={1:[(0,3),(4,5)],2:[(2,1),(5,3)],3:[(0,2),(3,4)],4:[(3,0),(5,4)],6:[(2,0),(5,2)]};children=[]
for a,b in [(1,3),(4,6),(2,4)]:children.extend([[P[a][0],P[b][1]],[P[b][0],P[a][1]]])
old=evaluate(children[0]);children[0][1]=(3,5);values=[evaluate(c)for c in children];costs=[v['cost']for v in values];order=sorted(range(6),key=lambda i:(costs[i],i))[:5]
check('Q027 six evaluated children',costs==[11,11,23,33,44,33],values)
check('Q027 fixed-size elite selection',order==[0,1,2,3,5]and len(order)+1==6,dict(retained=['P1']+[f'C{i+1}'for i in order]))
check('Q027 evaluated best',max([evaluate(P[1])['fitness']]+[values[i]['fitness']for i in order])==1/12)
check('Q034 mutation improvement not unique attainability',old['cost']==23 and values[0]['cost']==values[1]['cost']==11)
check('Q035 parent comparisons',evaluate(P[2])['cost']==44 and evaluate(P[4])['cost']==23 and values[4]['cost']==44)
check('Q012',12+10*1+2==24 and 1/(1+24)==.04)
check('Q014',10+10<30+1)
def energy(a,b):return -4*math.sin(a)-6*math.cos(a)-4*math.sin(b)-2*math.cos(b)
def fdeg(a,b):return -energy(math.radians(a),math.radians(b))-7
angles=(math.atan2(2,3),math.atan2(2,1));hessian=(4*math.sin(angles[0])+6*math.cos(angles[0]),4*math.sin(angles[1])+2*math.cos(angles[1]))
check('Q047 roots',tuple(round(math.degrees(a),2)for a in angles)==(33.69,63.43),angles)
check('Q050 Hessian',all(math.isclose(a,b)for a,b in zip(hessian,[math.sqrt(52),math.sqrt(20)])),hessian)
check('Q057 negative shift',math.isclose(fdeg(90,0),-1))
check('Q058 actual formula evaluation',round(fdeg(36,60),2)==4.67,fdeg(36,60))
a=(6*int('0110',2),6*int('1011',2));b=(0,0);fa,fb=fdeg(*a),fdeg(*b);pa=(fa+2)/(fa+fb+4)
check('Q071 decoding',a==(36,66))
check('Q071 positive-weight roulette',round(pa,4)==.6899,dict(anglesA=a,fitnessA=fa,fitnessB=fb,weightA=fa+2,weightB=fb+2,probabilityA=pa,unshiftedProbabilityA=fa/(fa+fb)))
check('Q071 not exact continuous optimum',a!=tuple(math.degrees(x)for x in angles))
check('Q072 displayed not feasible',1.8>math.pi/2>1.0)
check('Q065 weight compensation',3*4+2*5==.03*400+2*5)
rng=random.Random(4202)
for _ in range(1000):
 x,y=rng.random()*math.pi/2,rng.random()*math.pi/2;h=1e-6
 assert abs((energy(x+h,y)-energy(x-h,y))/(2*h)-(-4*math.cos(x)+6*math.sin(x)))<1e-8
 assert abs((energy(x,y+h)-energy(x,y-h))/(2*h)-(-4*math.cos(y)+2*math.sin(y)))<1e-8
 u,v=sorted([rng.uniform(0,100),rng.uniform(0,100)])
 assert 1/(1+u)>=1/(1+v)>0
 # A common positive scaling preserves roulette probabilities; an additive shift usually does not.
 z,w=rng.uniform(8,20),rng.uniform(8,20);assert math.isclose(z/(z+w),(3*z)/(3*z+3*w))
 assert (z>w)==(z-7>w-7)
report=dict(completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),scriptSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope=__doc__,explicitChecks=checks,explicitCount=len(checks),variedCases=1000,variedAssertions=5000,restrictions='Default interpreter and standard library only. No package/model download or restricted L48 temporary environment used. No executable lecture program claimed; the printed GA pseudocode was reconstructed under explicit packet conventions.')
f=R/'audits/W09-L42-v2-contracts-independent-checks.json';assert not f.exists();f.write_text(json.dumps(report,indent=2)+'\n');print(len(checks),'checks and5000 assertions passed; Q071',pa)
