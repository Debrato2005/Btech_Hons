#!/usr/bin/env python3
"""Author-added executable math checks. No literal source code or independent review."""
from pathlib import Path
import json,math,datetime,random,platform,hashlib
from fractions import Fraction as F
import sympy as sp
import numpy as np
from scipy.integrate import quad
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];checks=[]
def ck(name,test,result):
 assert bool(test),(name,result)
 checks.append({'name':name,'passed':True,'result':result})
def decode(bits,lo=1,hi=16):return F(lo)+F(hi-lo)*int(bits,2)/(2**len(bits)-1)
def cross(a,b,k):return a[:k]+b[k:],b[:k]+a[k:]
def twocross(a,b,k,j):return a[:k]+b[k:j]+a[j:]
def uniform(a,b,m):return ''.join(x if v=='1' else y for x,y,v in zip(a,b,m))
def sbx_alpha(r,q):return ((2*r) if r<=.5 else 1/(2*(1-r)))**(1/(q+1))
def sbx(a,b,r,q):
 al=sbx_alpha(r,q);return ((a+b-al*abs(b-a))/2,(a+b+al*abs(b-a))/2)
def poly(r,q):return (2*r)**(1/(q+1))-1 if r<.5 else 1-(2*(1-r))**(1/(q+1))
x=sp.symbols('x');ck('Stationary non-extremum',sp.diff(x**3,x).subs(x,0)==0 and (-.1)**3<0<(.1)**3,'x³ at0 has derivative0 but crosses0 monotonically')
ck('Boundary optimum',math.sqrt(16)==4 and all(math.sqrt(v)<4 for v in range(1,16)),{'x':16,'f':4})
ck('Unsigned10110',int('10110',2)==22,22)
ck('Endpoint mapping',decode('000000')==1 and decode('111111')==16,[1,16])
ck('Six-bit spacing',decode('000001')-decode('000000')==F(15,63),str(F(15,63)))
ck('Resolution bit count',F(15,127)>F(1,10) and F(15,255)<=F(1,10),8)
ck('Hamming cliff',sum(a!=b for a,b in zip('01111','10000'))==5 and int('10000',2)-int('01111',2)==1,{'distance':5,'integerDifference':1})
gray=lambda n:n^(n>>1)
ck('Gray adjacency all six-bit consecutive integers',all((gray(n)^gray(n+1)).bit_count()==1 for n in range(63)),63)
ck('Gray converse counterexample',(gray(0)^gray(3)).bit_count()==1,{'values':[0,3],'codes':[format(gray(0),'03b'),format(gray(3),'03b')]})
gen=0;events=[]
while gen<1:
 events+=['evaluate','select','cross','mutate'];gen+=1
ck('Literal flow exits after mutation',gen==1 and events[-1]=='mutate',events+['stop'])
ck('Roulette example',7/(1+2+7)==.7 and 10*.7==7,{'p':.7,'expectedCopies':7})
ck('Negative roulette weight invalid',-1/(-1+2+3)<0,-.25)
ck('Zero-total roulette undefined',sum([0,0,0])==0,'No division; explicit fallback would be a separate policy')
ck('Rank probabilities',3/sum([1,2,3])==.5,.5)
ck('Elite protects max not mean',max([9,0,0])==max([9,8,7]) and np.mean([9,0,0])<np.mean([9,8,7]),{'before':[9,8,7],'after':[9,0,0]})
ck('Pair expectation',10/2*.8==4,4)
pairs=[('100101','111010',2),('011010','101100',3),('111010','101100',2)]
children=[child for a,b,k in pairs for child in cross(a,b,k)]
ck('All three source crossover traces',children==['101010','110101','011100','101010','111100','101010'],children)
ck('Cross-pair wrong-cut distractors',cross('011010','101100',1)==('001100','111010') and cross('111010','101100',4)==('111000','101110'),{'pair2Cut1':cross('011010','101100',1),'pair3Cut4':cross('111010','101100',4)})
ck('Two-point added trace',twocross('110011','001100',2,4)=='111111','111111')
a,b='11110000','00001111';z=a[:2]+b[2:4]+a[4:6]+b[6:]
ck('Multi-point added trace',z=='11000011',z)
ck('Uniform added mask',uniform('101010','010101','110010')=='100111','100111')
z=''.join(str(1-int(bit)) if r<=.1 else bit for bit,r in zip('1010',[.05,.2,.1,.9]))
ck('Inclusive mutation boundary',z=='0000',z)
ck('Mutation guideline',.1/20==.005 and 1/20==.05,[.005,.05])
ck('Source100101 decode and fitness',decode('100101')==F(206,21) and round(math.sqrt(float(decode('100101'))),2)==3.13,{'D':37,'x':str(decode('100101')),'f':math.sqrt(float(decode('100101')))})
old=['100101','011010','010110','111010','101100','001101'];ox=[decode(s) for s in old];of=[math.sqrt(float(v)) for v in ox];oround=[3.13,2.68,2.50,3.85,3.39,2.02]
ck('All six initial integer entries',[int(s,2) for s in old]==[37,26,22,58,44,13],[int(s,2) for s in old])
ck('Initial fitness entries',[round(v,2) for v in of]==oround,of)
ck('Initial rounded total and mean',sum(F(str(v)) for v in oround)==F('17.57') and round(sum(of)/6,2)==2.93,{'roundedTotal':17.57,'exactNumericTotal':sum(of),'mean':sum(of)/6})
ck('Conflicting denominator remains explicit',F('17.57')!=F('17.51') and abs(3.13/17.57-.17814456459874786)<1e-15,{'fromDisplayedEntries':3.13/17.57,'printedPreviousPage':3.13/17.51})
ck('Initial truncation qualification',ox[-1]==F(86,21) and round(float(ox[-1]),2)==4.10,{'exact':str(ox[-1]),'rounded':4.1,'source':4.09})
pool=[old[i] for i in [0,1,3,3,4,4]]
ck('Source mating-pool realization',pool==['100101','011010','111010','111010','101100','101100'],pool)
ck('Expected mutation count',36*.03==1.08,1.08)
p1=36*.03*.97**35;p0=.97**36
ck('Binomial exactly one',abs(p1-.37190708744855916)<1e-15,p1)
ck('Binomial distinctions',0<p0<p1<1-p0<1,{'zero':p0,'one':p1,'atLeastOne':1-p0})
ck('Binomial PMF normalizes',abs(sum(math.comb(36,k)*.03**k*.97**(36-k) for k in range(37))-1)<1e-13,1)
children[3]=''.join(str(1-int(v)) if j==1 else v for j,v in enumerate(children[3]))
ck('Fourth-child mutation',children[3]=='111010',children)
nx=[decode(s) for s in children];nf=[math.sqrt(float(v)) for v in nx];nr=[3.32,3.69,2.77,3.85,3.91,3.32]
ck('All new integer entries',[int(s,2) for s in children]==[42,53,28,58,60,42],[int(s,2) for s in children])
ck('New fitness rows',[round(v,2) for v in nf]==nr,nf)
ck('Rounded new fitness total',sum(F(str(v)) for v in nr)==F('20.86'),20.86)
ck('Unrounded new total differs',abs(sum(nf)-20.85053290745843)<1e-13 and round(sum(nf),2)==20.85,{'unroundedTotal':sum(nf),'roundedEntrySum':20.86})
ck('New mean and maximum',round(sum(nf)/6,2)==3.48 and round(max(nf),2)==3.91,{'mean':sum(nf)/6,'max':max(nf)})
ck('New x truncation qualification',nx[4]==F(107,7) and round(float(nx[4]),2)==15.29,{'exact':str(nx[4]),'rounded':15.29,'source':15.28})
ck('Exact optimum not reached',max(nf)<4 and decode('111111')==16,{'observedBest':max(nf),'globalBest':4})
lin=[.5*(2+6),1.5*2-.5*6,-.5*2+1.5*6];fit=lambda z:-(z-5)**2
ck('Linear crossover three candidates',lin==[4,0,8],lin)
ck('Linear best two',sorted(lin,key=fit,reverse=True)[:2]==[4,8],[4,8])
ck('Linear feasibility check',[1<=v<=7 for v in lin]==[True,False,False],[1<=v<=7 for v in lin])
def blend(a,b,al,r,shift):
 g=(1+2*al)*r-(al if shift else 0);return ((1-g)*a+g*b,(1-g)*b+g*a)
ck('BLX literal versus shifted',blend(2,6,.5,.25,False)==(4,4) and blend(2,6,.5,.25,True)==(2,6),{'printed':blend(2,6,.5,.25,False),'shifted':blend(2,6,.5,.25,True)})
ck('BLX symmetric support',blend(2,6,.5,0,True)==(0,8) and blend(2,6,.5,1,True)==(8,0),[0,8])
ck('SBX separation ratio',abs(3-5)/abs(2-6)==.5,.5)
a=sp.symbols('a',positive=True);q=sp.symbols('q',nonnegative=True)
cm=sp.integrate(sp.Rational(1,2)*(q+1)*a**q,(a,0,1));em=sp.integrate(sp.Rational(1,2)*(q+1)*a**(-q-2),(a,1,sp.oo))
ck('Symbolic SBX branch masses',sp.simplify(cm-sp.Rational(1,2))==0 and sp.simplify(em-sp.Rational(1,2))==0,{'contracting':str(cm),'expanding':str(em)})
ck('Printed SBX lower-zero integral diverges',sp.integrate(a**(-3),(a,0,2))==sp.oo,'Expanding density cannot be integrated from0')
ck('SBX contracting inverse',sbx_alpha(.125,1)==.5,.5)
ck('SBX expanding inverse and children',sbx_alpha(.875,1)==2 and sbx(2,6,.875,1)==(0,8),{'alpha':2,'children':[0,8]})
ck('SBX equal-parent limit',sbx(5,5,.875,1)==(5,5),[5,5])
ck('SBX concentration with index',abs(sbx_alpha(.875,100)-1)<abs(sbx_alpha(.875,1)-1),[sbx_alpha(.875,1),sbx_alpha(.875,100)])
ck('Random mutation and range',math.isclose(10+(.8-.5)*4,11.2) and .5*4==2,{'value':11.2,'maxAbsoluteOffset':2})
ck('Polynomial mutation both branches',poly(.125,1)==-.5 and poly(.875,1)==.5 and 10+4*poly(.125,1)==8 and 10+4*poly(.875,1)==12,[8,12])
ck('Polynomial mutation midpoint',poly(.5,1)==0,0)
ck('Mutation can violate bounds',9+.5*4==11 and not 0<=11<=10,11)
ck('Micro restart preserves one and replaces four',1+4==5,{'eliteCopies':1,'newRandomCandidates':4})
ck('Tuning budget',4*10==40 and 10**4==10000 and 100*40/10000==.4,{'slots':40,'grid':10000,'percent':.4})
score={(0,0):5,(1,0):4,(0,1):4,(1,1):10};point=(0,0)
for j in [0,1]:
 trial=list(point);trial[j]=1;trial=tuple(trial)
 if score[trial]>score[point]:point=trial
ck('Coordinate-pass interaction counterexample',point==(0,0) and score[(1,1)]>score[point],{'returned':point,'missed':(1,1)})
ck('Penalty signs',10+3==13 and 10-3==7,[13,7])
viol=[max(0,3-2),max(0,1-0)];pen=5*sum(v*v for v in viol)
ck('Squared-violation penalty',viol==[1,1] and pen==10 and 3+pen==13,{'violations':viol,'penalty':pen,'penalizedObjective':3+pen})
# Author variation checks, not an independent verification stream.
rng=random.Random(41019);varied=0
for _ in range(1000):
 l=rng.randint(1,12);lo=rng.randint(-50,20);hi=lo+rng.randint(1,100);d=rng.randrange(2**l);bits=format(d,f'0{l}b');v=decode(bits,lo,hi)
 assert lo<=v<=hi and decode('0'*l,lo,hi)==lo and decode('1'*l,lo,hi)==hi;varied+=1
 r=rng.uniform(.0001,.9999);qq=rng.uniform(0,30);al=sbx_alpha(r,qq);cdf=.5*al**(qq+1) if al<=1 else 1-.5*al**(-qq-1)
 assert abs(cdf-r)<1e-11;varied+=1
 p1,p2=rng.uniform(-20,20),rng.uniform(-20,20);c1,c2=sbx(p1,p2,r,qq)
 assert math.isclose(c1+c2,p1+p2,abs_tol=1e-9) and math.isclose(abs(c1-c2),al*abs(p1-p2),rel_tol=1e-9,abs_tol=1e-9);varied+=1
 dp=poly(r,qq);assert -1<=dp<=1 and abs(poly(1-r,qq)+dp)<1e-11;varied+=1
 w=[rng.uniform(0,5) for j in range(5)];probs=[v/sum(w) for v in w];assert abs(sum(probs)-1)<1e-12 and min(probs)>=0;varied+=1
ck('Varied invariants',varied==5000,{'trials':1000,'comparisons':varied})
# Draw the source-derived probability law with corrected support; not an original slide.
fig,axes=plt.subplots(1,2,figsize=(11,4));aa=np.linspace(0,3,1201)
for qq in [1,5,20]:
 yy=np.where(aa<=1,.5*(qq+1)*aa**qq,.5*(qq+1)*np.maximum(aa,1)**(-qq-2));axes[0].plot(aa,yy,label=f'q={qq}')
axes[0].set(xlabel='Spread ratio alpha',ylabel='Density',title='SBX density on its valid supports');axes[0].axvline(1,color='gray',ls=':');axes[0].legend()
ks=np.arange(8);pv=[math.comb(36,int(k))*.03**int(k)*.97**(36-int(k)) for k in ks];axes[1].bar(ks,pv);axes[1].set(xlabel='Number of bit flips',ylabel='Probability',title='36 independent bits, p=0.03');axes[1].axvline(1.08,color='red',ls='--',label='Expected count 1.08');axes[1].legend();fig.tight_layout();out=R/'audits/W09-L41-distribution-reconstruction.png';fig.savefig(out,dpi=160);plt.close(fig)
report={'authorId':'build_offline_study_interface:L41-author','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentReview':False,'sourceCodePresent':False,'scope':'Author-added math reconstruction of inspected equations, tables, operator examples and explicitly added contexts; not source-code execution or independent review.','namedChecks':len(checks),'checks':checks,'oldPopulation':{'strings':old,'decodedIntegers':[int(s,2) for s in old],'exactX':[str(v) for v in ox],'fitness':of,'roundedFitness':oround},'newPopulation':{'strings':children,'decodedIntegers':[int(s,2) for s in children],'exactX':[str(v) for v in nx],'fitness':nf,'roundedFitness':nr},'randomTrials':1000,'randomComparisons':varied,'versions':{'python':platform.python_version(),'numpy':np.__version__,'sympy':sp.__version__},'figure':{'path':str(out.relative_to(R)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}}
(R/'audits/W09-L41-author-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'namedChecks':len(checks),'variedComparisons':varied,'allPass':True}))
