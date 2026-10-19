"""Author-only default-library checks for revised L51 exercises; no hardware execution."""
from pathlib import Path
import math,json,random,datetime
R=Path(__file__).resolve().parents[1];named=[];varied=0
def check(name,ok):
 assert ok,name
 named.append(name)
def close(a,b):return math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-12)
check('Q033 cloud range lower',2+6==8);check('Q033 cloud range upper',2+18==20);check('Q033 local deadline',8<=10<20)
check('Q040 full-load runtime',close(27.75/35*60,47.57142857142857));check('Q040 omitted-load distractor',close(27.75/20*60,83.25));check('Q040 doubled-total distractor',close(27.75/50*60,33.3))
check('Q054 remainder',close(1000/100-8,2));check('Q054 addition distractor',10+8==18)
check('Q056 bound conversion',close(.088*math.pi/180,.00153588974175501));check('Q059 signal criterion',100>2*40 and not 60>2*40)
m=(1/4+3)/(1/4+1);v=1/(1/4+1)
check('Q065 fused mean',close(m,2.6));check('Q065 fused variance',close(v,.8));check('Q065 reversed precision distractor',close((1+3/4)/(1+1/4),1.4))
check('Q066 bias retained',close((.4+.4)/2,.4));check('Q066 noise variance',close((.04+.04)/4,.02));check('Q066 variance differs from MSE',close(.4**2+.02,.18))
check('Q071 reach bound excludes A',1>.8);check('Q071 rank deficient',5<6)
check('Q077 aluminium torque',close(.2*2+.3,.7));check('Q077 steel torque',close(.4*2+.3,1.1));check('Q077 torque feasibility',.7<.8<1.1);check('Q077 command dimensions',1<=1<3)
E=.8*11.1*2.5;P=[10+5+1+c for c in [10,20,5,8]];times=[E/p*60 for p in P];cmd=100*10/1_000_000;camera=320*240*1*20*8;paths=[.002+x/1000+cmd for x in [6,3,9,5]];links=[100e6,100e6,100e6,10e6]
check('Q078 usable energy',close(E,22.2));check('Q078 full loads',P==[26,36,21,24]);check('Q078 UART framing',close(cmd,.001));check('Q078 camera payload',camera==12_288_000);check('Q078 runtimes',all(close(a,b) for a,b in zip(times,[51.23076923076923,37,63.42857142857143,55.5])));check('Q078 path times',all(close(a,b) for a,b in zip(paths,[.009,.006,.012,.008])));check('Q078 only A feasible',[i for i in range(4) if times[i]>=45 and paths[i]<=.010 and links[i]>=camera]==[0])
r=random.Random(5102)
for _ in range(1500):
 v1,v2=r.uniform(.01,10),r.uniform(.01,10);m1,m2=r.uniform(-5,5),r.uniform(-5,5);w1=v2/(v1+v2);w2=v1/(v1+v2);mf=w1*m1+w2*m2;vf=1/(1/v1+1/v2)
 assert close(mf,(m1/v1+m2/v2)/(1/v1+1/v2));varied+=1
 assert close(vf,w1*w1*v1+w2*w2*v2) and vf<min(v1,v2);varied+=1
 b=r.uniform(-5,5);assert close((b+b)/2,b) and (v1+v2)/4>0;varied+=1
 J,a,load=[r.uniform(.001,5) for i in range(3)];tau=J*a+load;assert close((tau-load)/J,a);varied+=1
 energy,power=r.uniform(.1,100),r.uniform(.1,100);assert close((energy/power)*power,energy);varied+=1
 deg=r.uniform(0,180);assert close((deg*math.pi/180)*180/math.pi,deg);varied+=1
out={'batchId':'W11-L51','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'namedChecks':len(named),'named':named,'variedChecks':varied,'variedTrials':1500,'seed':5102,'passed':True,'independentReview':False,'environment':'Existing default Python standard library only.','scope':'Declared added timing, power, torque, sampling, unit and scalar-estimation models; no physical hardware or network benchmark execution.'}
(R/'audits/W11-L51-v2-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['namedChecks','variedChecks','passed']}))
