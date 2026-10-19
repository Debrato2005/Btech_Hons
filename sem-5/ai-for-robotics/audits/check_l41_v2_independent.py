"""Fresh reviewer arithmetic, not author script or absent lecture source code."""
import json,math,random,datetime,pathlib
checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
check('binary and shifted distractor',int('10110',2)==22 and int('1011',2)==11 and 8+4+2==14)
check('five Hamming flips',sum(a!=b for a,b in zip('01111','10000'))==5)
def graydecode(g):
 n=0
 while g:n^=g;g>>=1
 return n
check('Gray given lookup',[graydecode(i) for i in [0,1,2,4]]==[0,1,3,7])
check('negative probability',[-1/4,2/4,3/4]==[-.25,.5,.75])
check('expected crossed pairs',5*.8==4)
x=1+15*int('100101',2)/63
check('decoded phenotype and objective',round(x,2)==9.81 and round(math.sqrt(x),2)==3.13)
check('rounded normalization',math.isclose(sum([3.13,2.68,2.50,3.85,3.39,2.02]),17.57) and math.isclose(3.13/17.57,.17814456,abs_tol=1e-8))
check('mutation count and noncertainty',math.isclose(36*.03,1.08) and math.isclose(36*.03*.97**35,.37190708745,abs_tol=1e-10))
check('linear children',[.5*(2+6),1.5*2-.5*6,-.5*2+1.5*6]==[4,0,8])
check('scan and Cartesian budget',(4*10,10**4,100*40/10000)==(40,10000,.4))
check('repeated tuple counts',(40-3,40,40-3)==(37,40,37))
f={(0,0):5,(1,0):4,(0,1):4,(1,1):10};s=(0,0)
for i in [0,1]:
 t=list(s);t[i]=1;t=tuple(t)
 if f[t]>f[s]:s=t
check('greedy scan misses joint optimum',s==(0,0) and f[1,1]>f[s])
r=random.Random(4102)
for i in range(1000):
 l=r.randint(1,18);lo=r.uniform(-100,100);hi=lo+r.uniform(.01,100);m=2**l-1
 assert math.isclose(lo+(hi-lo)*m/m,hi,abs_tol=1e-10)
 p=r.uniform(-1000,1000);alpha=r.uniform(0,20)
 assert (p+p-alpha*abs(p-p))/2==p and (p+p+alpha*abs(p-p))/2==p
 vals=r.sample(range(-1000,1000),10);assert sorted(range(10),key=lambda j:vals[j])==sorted(range(10),key=lambda j:3*vals[j]+11)
check('1000 varied endpoint equal-parent rank cases',True)
out={'executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'groupsPassed':len(checks),'variedCasesPassed':1000,'checks':checks,'x':x,'sqrtX':math.sqrt(x),'executionKind':'reviewer mathematics reconstruction; no literal lecture program exists','failedAttempts':[]}
pathlib.Path('audits/W09-L41-v2-independent-computations.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
