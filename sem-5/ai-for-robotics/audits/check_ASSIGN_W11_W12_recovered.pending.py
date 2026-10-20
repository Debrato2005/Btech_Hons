# HISTORICAL PREPARATION SNAPSHOT ONLY. Do not execute. The current script is scripts/check_ASSIGN_W11_W12_recovered.py. Frozen reviewed data must not be regenerated.
"""Stdlib-only deterministic author checks; never independent review."""
from assignment_second_half_common import *
from fractions import Fraction as R
import math,sys,random
w=int(sys.argv[1]);assert w in (11,12);checks=[]
def ck(name,value):
 assert value,name
 checks.append(name)
rng=random.Random(110012+w);n=0
if w==11:
 ck('battery energy runtime exact',(12*R('2.5'),60*12*R('2.5')/20)==(30,90))
 ck('battery wrong unit/missing load distractors',(60*30/10,60*R('2.5')/20,30/20)==(180,R('7.5'),R('1.5')))
 lo=R(1023*5,1024);hi=R(5);ck('ADC exact top bin',lo==R('4.9951171875') and math.floor(1024*lo/5)==1023 and R(1023*5,1023)==5)
 ck('ADC adjacent-bin boundary',math.floor(1024*(lo-R(1,1000000))/5)==1022)
 ck('encoder independent mode counts',(R(1800,600),R(1800,2400))==(3,R('.75')))
 ck('gear torque exact and distractors',(R('.25')*20*R('.85'),R('.25')/20*R('.85'),round(float(R(5)/R('.85')),8))==(R('4.25'),R('.010625'),5.88235294))
 ck('positive torque surplus accelerates',(6-R('.2')*10-2)/R('.5')==4)
 ck('gradient-descent exact update',R('.4')-R('.02')*R(-3)==R('.46'))
 ck('gradient distractors',(R('.4')+R('.02')*(-3),R('.4')-(-3),R('.02')*(-3))==(R('.34'),R('3.4'),R('-.06')))
 score=R('2.5')*R('3.2')-R('7.5');ck('SVM score class boundary distance',(score,-R('-7.5')/R('2.5'),score/abs(R('2.5')))==(R('.5'),3,R('.2')))
 train=[-1.,0.,1.];mu=sum(train)/3;sd=math.sqrt(sum((x-mu)**2 for x in train)/3);z=[(x-mu)/sd for x in train];new=[(x-mu)/sd for x in [10.,11.,12.]]
 ck('standardization training moments',abs(sum(z)/3)<1e-12 and abs(sum(v*v for v in z)/3-1)<1e-12)
 ck('standardization new mean not forced',sum(new)/3>10)
 pred=2*R('.5')+R('.5')*2+R('1.5')*3+R('.8');ck('inverse dynamics prediction exact',pred==R('7.3') and abs(8-pred)==R('.7'))
 ck('torque predictor omissions',(pred-R('.8'),abs(8-(pred-R('.8'))),pred-1,abs(8-(pred-1)))==(R('6.5'),R('1.5'),R('6.3'),R('1.7')))
 for _ in range(1000):
  v=R(rng.randint(1,100));cap=R(rng.randint(1,100),10);power=R(rng.randint(1,100));assert v*cap/power*power==v*cap;n+=1
  k=rng.randrange(1024);ref=R(rng.randint(1,100),10);lower=k*ref/1024;middle=(2*k+1)*ref/2048;assert math.floor(1024*lower/ref)==k and math.floor(1024*middle/ref)==k;n+=1
  cycles=rng.randint(1,1000);mult=rng.choice([1,2,4]);cnt=rng.randint(0,10000);assert R(cnt,cycles*mult)*mult==R(cnt,cycles);n+=1
  a=R(rng.randint(1,100),10);x0=R(rng.randint(-100,100),10);x=R(rng.randint(-100,100),10);b=-a*x0;assert (a*x+b)/abs(a)==x-x0;n+=1
  old=R(rng.randint(-100,100),10);grad=R(rng.randint(-100,100),10);eta=R(rng.randint(1,100),1000);assert ((old-eta*grad)-old)*grad<=0;n+=1
else:
 ck('parallel versus serial exact',(max(80,120),80+120,(80+120)-max(80,120))==(120,200,80))
 d=math.hypot(.3,.2);D=24*d;speed=.6*8.2;t=D/speed
 ck('ideal round trip computed values',math.isclose(D,8.653323061113575,abs_tol=1e-12) and math.isclose(t,1.7588055002263365,abs_tol=1e-12))
 ck('ideal round trip final rounding',(round(D,2),round(t,2))==(8.65,1.76))
 ck('outbound-only distractor',(round(D/2,2),round(t/2,2))==(4.33,.88))
 ck('component-sum distractor',(round(24*(.3+.2),2),round(24*(.3+.2)/speed,2))==(12.,2.44))
 ck('full-speed distractor',round(D/8.2,2)==1.06)
 r=R('.1');L=R('.5');right=R(5);left=R(-5);ck('differential drive exact',(r*(right+left)/2,r*(right-left)/L)==(0,2))
 ck('differential reversed sign and same-wheel distractors',(r*(left-right)/L,r*(right+right)/2,r*(right-right)/L)==(-2,R('.5'),0))
 for _ in range(1000):
  a=rng.randint(1,10000);b=rng.randint(1,10000);assert max(a,b)<=a+b and a+b-max(a,b)==min(a,b);n+=1
  x=rng.uniform(.01,10);y=rng.uniform(.01,10);rounds=rng.randint(1,100);vel=rng.uniform(.1,20);length=2*rounds*math.hypot(x,y);assert math.isclose(length/vel*vel,length,rel_tol=1e-12) and length<2*rounds*(x+y);n+=1
  rad=R(rng.randint(1,100),100);sep=R(rng.randint(1,100),10);rate=R(rng.randint(-100,100),10);assert rad*(rate-rate)/2==0 and rad*(rate-(-rate))/sep==2*rad*rate/sep;n+=1
  wr=R(rng.randint(-100,100),10);wl=R(rng.randint(-100,100),10);vf=rad*(wr+wl)/2;om=rad*(wr-wl)/sep;assert vf+om*sep/2==rad*wr and vf-om*sep/2==rad*wl;n+=1
b=json.loads((ROOT/f'data/question-batches/ASSIGN-W{w:02}.json').read_text())
for q in b['questions']:
 ck(q['id']+' option explanations exhaustive',set(q['solution']['optionExplanations'])=={o['id'] for o in q['options']})
 ck(q['id']+' immutable original',sha(q['originalRecordPath'])==q['originalRecordSha256'])
 if q.get('conflictResolution'):
  cr=q['conflictResolution'];ck(q['id']+' conflict points to conflict citation',any(c['physicalPage']==cr['physicalPage'] and c['role']=='conflict' for c in q['citations']))
ck('all ten original items represented',len({q['assignmentSourceItemId']for q in b['questions']})==10)
ins=json.loads((ROOT/f'data/inspection-batches/ASSIGN-W{w:02}-author.json').read_text());ck('exact actual page range',[s['physicalPage']for s in ins['slides']]==list(range(50,56)if w==11 else range(56,60)))
if w==11:ck('END-only page exclusion',ins['slides'][-1]['disposition']=='excluded' and not ins['slides'][-1]['conceptIds'])
dump(f'audits/ASSIGN-W{w:02}-author-checks.json',dict(role='Author stdlib-only deterministic checks, not independent review or browser/hardware execution',authorId='finish_assignment_authoring:W11-W12-author',checkedAt=NOW(),pythonExecutable=sys.executable,checks=checks,variedCases=1000,variedAssertions=n,restrictedRuntimeUsed=False,questionHashes={q['id']:qhash(q)for q in b['questions']}))
print('Week',w,len(checks),'check groups;',n,'varied assertions')
