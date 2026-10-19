"""Independent source-pixel mathematical reconstruction, no authored keys/scripts used."""
import math,random,json,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1];checks=[]
def ok(name,condition):
 assert condition,name
 checks.append(name)
def near(a,b):return math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-11)
def decode(s,lo=1,hi=16):return lo+(hi-lo)*int(s,2)/(2**len(s)-1)
def cross(a,b,k):return a[:k]+b[k:],b[:k]+a[k:]
def spread(r,q):return (2*r)**(1/(q+1)) if r<=.5 else (1/(2*(1-r)))**(1/(q+1))
def cdf(a,q):return .5*a**(q+1) if a<=1 else 1-.5*a**(-q-1)
def children(a,b,beta):return ((a+b-beta*abs(b-a))/2,(a+b+beta*abs(b-a))/2)
def mutation(r,q):return (2*r)**(1/(q+1))-1 if r<.5 else 1-(2*(1-r))**(1/(q+1))
ok('binary22',int('10110',2)==22)
ok('endpoints',decode('000000')==1 and decode('111111')==16)
ok('resolution',near(15/63,.23809523809523808) and 15/(2**7-1)>.1 and 15/(2**8-1)<=.1)
ok('hamming',sum(a!=b for a,b in zip('01111','10000'))==5)
ok('gray adjacency',all(( (n^(n>>1)) ^ ((n+1)^((n+1)>>1)) ).bit_count()==1 for n in range(255)))
ok('roulette expectation',near(7/10,.7) and 10*7/10==7)
ok('invalid raw roulette',-1/sum([-1,2,3])<0)
ok('rank probability',3/sum([1,2,3])==.5)
ok('tournament',max([2,9,4])==9)
ok('crossover expectation',5*.8==4)
ok('pair1',cross('100101','111010',2)==('101010','110101'))
ok('pair2',cross('011010','101100',3)==('011100','101010'))
ok('pair3',cross('111010','101100',2)==('111100','101010'))
ok('two cuts','110011'[:2]+'001100'[2:4]+'110011'[4:]=='111111')
ok('multi cuts','11110000'[:2]+'00001111'[2:4]+'11110000'[4:6]+'00001111'[6:]=='11000011')
ok('mask',''.join(a if m=='1' else b for a,b,m in zip('101010','010101','110010'))=='100111')
ok('mutation <=',''.join(str(1-int(x)) if r<=.1 else x for x,r in zip('1010',[.05,.2,.1,.9]))=='0000')
ok('mutation guideline',.1/20==.005 and 1/20==.05)
initial=['100101','011010','010110','111010','101100','001101'];new=['101010','110101','011100','111010','111100','101010']
initialrows=[dict(string=s,D=int(s,2),x=decode(s),fitness=math.sqrt(decode(s))) for s in initial]
newrows=[dict(string=s,D=int(s,2),x=decode(s),fitness=math.sqrt(decode(s))) for s in new]
ok('initial exact decoding',int(initial[0],2)==37 and round(decode(initial[0]),2)==9.81 and round(math.sqrt(decode(initial[0])),2)==3.13)
f=[3.13,2.68,2.50,3.85,3.39,2.02];g=[3.32,3.69,2.77,3.85,3.91,3.32]
ok('initial rounded entries',[round(t['fitness'],2) for t in initialrows]==f)
ok('initial displayed denominator',near(sum(f),17.57) and round(sum(f)/6,2)==2.93 and max(f)==3.85)
ok('selection probability',near(f[0]/sum(f),.17814456459874787))
ok('expected flips',near(36*.03,1.08))
p1=36*.03*.97**35;p0=.97**36
ok('binomial exact one',round(p1,5)==.37191 and round(p0,5)==.33403 and round(1-p0,5)==.66597)
ok('specific mutation','101010'[0]+'1'+'101010'[2:]=='111010')
ok('new rounded entries',[round(t['fitness'],2) for t in newrows]==g)
ok('new displayed stats',near(sum(g),20.86) and round(sum(g)/6,2)==3.48 and max(g)==3.91)
ok('new unrounded stats',round(sum(t['fitness'] for t in newrows),2)==20.85)
ok('not optimum',max(t['fitness'] for t in newrows)<math.sqrt(decode('111111'))==4)
lin=[.5*(2+6),1.5*2-.5*6,-.5*2+1.5*6]
ok('linear best2',sorted(lin,key=lambda x:-(x-5)**2,reverse=True)[:2]==[4,8])
ok('linear feasibility',[x for x in lin if 1<=x<=7]==[4])
def blend(g):return ((1-g)*2+g*6,(1-g)*6+g*2)
ok('printed vs shifted blend',blend((1+2*.5)*.25)==(4,4) and blend((1+2*.5)*.25-.5)==(2,6))
ok('BLX interval',(2-.5*4,6+.5*4)==(0,8))
ok('spread ratio',abs(3-5)/abs(2-6)==.5)
ok('SBX inverse contracting',spread(.125,1)==.5)
ok('SBX inverse expanding',spread(.875,1)==2 and children(2,6,2)==(0,8))
ok('SBX equal parents',children(5,5,2)==(5,5))
ok('random mutation',near(10+(.8-.5)*4,11.2) and .5*4==2)
ok('polynomial mutation',(10+mutation(.125,1)*4,10+mutation(.875,1)*4)==(8,12))
ok('mutation bound failure',9+.5*4>10)
ok('micro cost',5*3==15 and 50*3==150)
ok('parameter slots',4*10==40 and 10**4==10000 and 100*40/10000==.4)
F={(0,0):5,(1,0):4,(0,1):4,(1,1):10};state=(0,0)
for i in (0,1):
 cand=list(state);cand[i]=1;cand=tuple(cand)
 if F[cand]>F[state]:state=cand
ok('coordinate trap',state==(0,0) and F[(1,1)]>F[state])
ok('penalty sign',(10+3,10-3)==(13,7))
P=5*(max(0,3-2)**2+max(0,1-0)**2)
ok('penalty application',P==10 and 3+0+P==13)
# Derive normalized density integrals from antiderivatives rather than copying a key.
ok('branch half masses',all(near(.5*(q+1)/(q+1),.5) for q in [0,1,2,20,100]))
rng=random.Random(4101263);varied=0
for _ in range(1000):
 q=rng.uniform(0,50);r=rng.uniform(.00001,.99999);a=spread(r,q)
 assert near(cdf(a,q),r);varied+=1
 x,y=sorted([rng.uniform(-100,100),rng.uniform(-100,100)]);c,d=children(x,y,a)
 assert near((c+d)/2,(x+y)/2) and near((d-c)/(y-x),a);varied+=1
 alpha=rng.uniform(0,2);gam=(1+2*alpha)*r-alpha;v=(1-gam)*x+gam*y
 assert x-alpha*(y-x)-1e-10<=v<=y+alpha*(y-x)+1e-10;varied+=1
 delta=mutation(r,q)
 assert -1<=delta<=1 and near(mutation(1-r,q),-delta);varied+=1
 l=rng.randrange(1,17);lo=rng.uniform(-20,0);hi=rng.uniform(1,20);code=rng.randrange(2**l);s=format(code,f'0{l}b')
 z=decode(s,lo,hi);assert lo-1e-10<=z<=hi+1e-10 and math.isclose((z-lo)*(2**l-1)/(hi-lo),code,rel_tol=1e-11,abs_tol=1e-8);varied+=1
out=dict(reviewer='independent-reviewer-robotics-batches-v2',executedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='Independently reconstructed formulas and deterministic traces from all source pixels; no original executable code is present in this lecture and no author script used.',groupsPassed=len(checks),checks=checks,variedCasesPassed=varied,seed=4101263,testDevelopmentNote='Initial varied check used exact float endpoint inequalities and failed on rounding at an affine endpoint; corrected to1e-10 domain tolerance and1e-8 inverse absolute tolerance. This changes no question value or key.',initialRows=initialrows,newRows=newrows,probExactlyOne=p1,probZero=p0,displayRoundingQualification='Source x=4.09 at D13 and15.28 at D60 differ from nearest-two-decimal exact affine values4.10 and15.29; displayed fitnesses still match exact-derived rounded values.',initialUnroundedSum=sum(t['fitness'] for t in initialrows),newUnroundedSum=sum(t['fitness'] for t in newrows))
(R/'audits/W09-L41-independent-computations.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['groupsPassed','variedCasesPassed','probExactlyOne','initialUnroundedSum','newUnroundedSum']}))
