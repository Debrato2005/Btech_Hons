"""Independent source-based default-Python checks, before revised keys."""
from pathlib import Path
import math,json,datetime,random,hashlib
R=Path(__file__).resolve().parents[1];out=R/'audits/W11-L51-v2-contracts-independent-checks.json';assert not out.exists()
checks=[]
def check(name,actual,expected):
 if isinstance(expected,(int,float)):assert math.isclose(actual,expected,rel_tol=1e-10,abs_tol=1e-12),(name,actual,expected)
 else:assert actual==expected,(name,actual,expected)
 checks.append(dict(name=name,result=actual,expected=expected,passed=True))
check('cloud best ms',2+6,8);check('cloud worst ms',2+18,20);check('local meets 10ms',8<=10,True)
check('20W compute runtime min',27.75/(20+10+5)*60,47.57142857142857);check('compute-only wrong min',27.75/20*60,83.25)
check('period ms',1000/100,10);check('remaining ms',1000/100-8,2);check('bound radians',.088*math.pi/180,.0015358897417550101)
check('40Hz strict sampling threshold',2*40,80);check('100Hz meets threshold',100>80,True)
v1,v2=4,1;mean=(1/v1+3/v2)/(1/v1+1/v2);variance=1/(1/v1+1/v2)
check('inverse variance mean',mean,2.6);check('inverse variance variance',variance,.8);check('reversed precision mean',(1*v1+3*v2)/(v1+v2),1.4)
check('fixed bias after average',(.4+.4)/2,.4);check('independent noise average variance',(.04+.04)/4,.02)
check('aluminium required torque',.2*2+.3,.7);check('steel required torque',.4*2+.3,1.1)
check('nominal Wh',11.1*2.5,27.75);energy=11.1*2.5*.8;check('usable Wh',energy,22.2)
command=100*10/1e6*1000;check('serial 8N1 command ms',command,1)
camera=320*240*8*20/1e6;check('camera payload Mbps',camera,12.288)
candidates={};expected={'A':(51.23076923076923,9,True),'B':(37,6,False),'C':(63.42857142857143,12,False),'D':(55.5,8,False)}
for name,p,inf,link in [('A',10,6,100),('B',20,3,100),('C',5,9,100),('D',8,5,10)]:
 runtime=60*energy/(10+5+1+p);lat=2+inf+command;ok=runtime>=45 and lat<=10 and link>=camera;candidates[name]=dict(totalPowerW=16+p,runtimeMinutes=runtime,serialLatencyMs=lat,cameraMbps=link,feasible=ok)
 check(name+' runtime',runtime,expected[name][0]);check(name+' latency',lat,expected[name][1]);check(name+' feasible',ok,expected[name][2])
check('unique feasible candidate',[k for k,v in candidates.items()if v['feasible']],['A'])
r=random.Random(5102);n=0
for _ in range(1000):
 E=r.uniform(1,200);P=r.uniform(1,100);delta=r.uniform(.01,50);assert E/(P+delta)<E/P;n+=1
 a,b=r.uniform(.01,20),r.uniform(.01,20);mu1,mu2=r.uniform(-100,100),r.uniform(-100,100);mf=(mu1/a+mu2/b)/(1/a+1/b);vf=1/(1/a+1/b)
 assert min(mu1,mu2)-1e-10<=mf<=max(mu1,mu2)+1e-10;n+=1
 assert 0<vf<min(a,b);n+=1
 assert math.isclose(vf,a*b/(a+b),rel_tol=1e-12);n+=1
 bias=r.uniform(-5,5);noise=r.uniform(.001,3);errors=[bias+(x+y)/2 for x in [-noise,noise]for y in [-noise,noise]];m=sum(errors)/4;var=sum((x-m)**2 for x in errors)/4
 assert math.isclose(m,bias,abs_tol=1e-12)and math.isclose(var,noise**2/2,rel_tol=1e-10,abs_tol=1e-12);n+=1
report=dict(reviewerId='robotics-contracts-reviewer-L51',completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),explicitChecks=len(checks),checks=checks,variedCases=1000,variedAssertions=n,candidateResults=candidates,runtime='Default Python standard library only. No lecture program/notebook exists in this bounded lecture; these are independently written checks of declared educational equations, not hardware or model execution.',primarySources=[dict(url='https://www.bosch-semiconductors.com/products/ip-modules/can-protocols/can-fd/',finding='Official Bosch page distinguishes Classical CAN 1 Mbps and optional faster CAN FD data phase, also payload expansion.'),dict(url='https://www.nxp.com/docs/en/user-guide/UM10204.pdf',finding='Official revision 7.0 introduction lists 100/400 kbps, 1/3.4 Mbps and unidirectional 5 Mbps modes; device and electrical conditions still apply.'),dict(url='https://docs.ros.org/en/ros2_documentation/kilted/Concepts/Intermediate/About-Different-Middleware-Vendors.html',finding='Official search result describes RMW implementations for discovery/serialization/network transport; DDS is middleware, not Wi-Fi. Direct page returned a bot challenge, which was not bypassed.'),dict(url='https://support.maxongroup.com/hc/en-us/articles/360012252780-What-supply-voltage-is-required-by-a-controller',finding='Manufacturer explicitly links PWM-adjusted voltage to speed/load demands and describes decreasing speed with torque at fixed voltage.')])
out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(len(checks),n)
