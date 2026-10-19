"""L51 author calculations. No robot, battery or external device is operated."""
from pathlib import Path
import json,math,random,datetime
R=Path(__file__).resolve().parents[1];a=[]
def check(name,v,e):
 assert math.isclose(v,e,rel_tol=1e-10,abs_tol=1e-12),(name,v,e);a.append({'name':name,'actual':v,'expected':e,'passed':True})
check('Drive plus compute plus sensor power',2*5+10+5,25)
check('Nominal watt-hour energy',2.5*11.1,27.75)
check('Ideal runtime minutes',27.75/25*60,66.6)
check('80 percent usable energy runtime',.8*27.75/25*60,53.28)
check('35 W upgraded load runtime',27.75/35*60,47.57142857142857)
check('3C rating arithmetic',3*2.5,7.5)
check('Nominal battery current at 25 W',25/11.1,2.2522522522522523)
check('Energy-density ideal mass',27.75/200,.13875)
check('Torque proportionality example',.12*2,.24)
check('Current-doubling copper loss factor',2**2,4)
check('Fixed geometry inertia reduction torque ratio',.2/.4,.5)
check('Duty average-voltage ideal model',.75*12,9)
check('Loaded motor speed ideal model',(9-2*.5)/.02,400)
check('Compute-only 8 ms maximum rate',1/.008,125)
check('100 Hz step remaining after inference',1000/100-8,2)
check('Serial total 2+8+1 ms rate',1000/(2+8+1),90.9090909090909)
check('500 Hz IMU samples per 100 Hz period',500/100,5)
check('Encoder 1 kHz sample interval ms',1000/1000,1)
check('Camera 30 fps frame interval ms',1000/30,33.333333333333336)
check('LiDAR 20 Hz scan interval ms',1000/20,50)
check('100 UART 8N1 bytes at 115000 bits/s ms',100*10/115000*1000,8.695652173913043)
check('Uncompressed RGB stream Mbps',640*480*3*30*8/1e6,221.184)
check('Raw RGB frame bits',640*480*3*8,7372800)
check('0.088 degree in radians',.088*math.pi/180,.00153588974175501)
check('Uniform half-width standard deviation',(.088*math.pi/180)/math.sqrt(3),.000886746355845041)
check('12-bit full-turn encoder resolution degrees',360/4096,.087890625)
check('Independent inverse-variance fusion mean',(1/4+3/1)/(1/4+1),2.6)
check('Independent inverse-variance fusion variance',1/(1/4+1),.8)
rng=random.Random(51);varied=0
for _ in range(1000):
 V=rng.uniform(5,50);Q=rng.uniform(.1,10);P=rng.uniform(1,100);t=V*Q/P
 assert math.isclose(P*t,V*Q);varied+=1
 r1=rng.uniform(.01,10);r2=rng.uniform(.01,10);v=1/(1/r1+1/r2);assert v<min(r1,r2);varied+=1
 m1=rng.uniform(-10,10);m2=rng.uniform(-10,10);w=r2/(r1+r2);mean=w*m1+(1-w)*m2;assert math.isclose(mean,(m1/r1+m2/r2)/(1/r1+1/r2),rel_tol=1e-10,abs_tol=1e-10);varied+=1
out={'authorId':'build_offline_study_interface:L51-author','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Author-supplied arithmetic/model checks only, not independent verification. No physical hardware, battery, model inference or network benchmark executed.','namedChecks':len(a),'variedChecks':varied,'checks':a,'sourceCodePresent':False}
(R/'audits/W11-L51-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'named':len(a),'varied':varied}))
