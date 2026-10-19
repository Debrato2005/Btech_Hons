"""Deterministic author-only L53 arithmetic and ideal-model checks; stdlib only."""
from pathlib import Path
import math,random,json,datetime,sys,hashlib
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import schema_errors
checks=[]
def c(name,a,b):
 assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(name,a,b)
 checks.append({'name':name,'actual':a,'expected':b,'passed':True})
c('Inclined wire force',.5*3*.2*math.sin(math.pi/6),.15)
c('Faraday 100-turn ramp',-100*(.003-.001)/.020,-10)
c('Geometric torque constant',20*.4*.1*.05,.04)
c('Geometric torque',20*.4*.1*.05*2,.08)
c('Back EMF',.1*100,10)
c('Armature current',(24-.1*100)/2,7)
c('Electromagnetic torque',.1*(24-.1*100)/2,.7)
c('Stall torque',.1*24/2,1.2)
c('Ideal free speed',24/.1,240)
c('Initial current slope',12/.020,600)
c('Electrical time constant',.020/2,.01)
c('Current at one time constant',6*(1-math.exp(-1)),3.792723352971346)
c('Converted mechanical power',.1*7*100,70)
c('Copper loss',7**2*2,98)
c('Power balance',24*7,70+98)
c('Power-maximizing speed',1.2/(2*.005),120)
c('Maximum mechanical power',120*(1.2-.005*120),72)
c('Series torque ratio',(3/2)**2,2.25)
c('Shunt line current',24/120+(24-20)/2,2.2)
c('Gear output speed',100/10,10)
c('Gear output torque',10*.2,2)
c('PWM duty',30/50,.6)
c('PWM average voltage',24*30/50,14.4)
c('Tach speed error',100-1.6/.02,20)
c('One-pair 50 Hz rpm',60*50,3000)
c('Four-pole 50 Hz rpm',120*50/4,1500)
c('Induction slip',(1500-1440)/1500,.04)
for n,d in zip([12,24,72,144,180,200],[30,15,5,2.5,2,1.8]):c(f'{n} step angle',360/n,d)
c('Stepper move degrees',50*360/200,90)
c('Stepper pulse duration',50/500,.1)
c('Stepper rpm',60*500/200,150)
c('VR nearest-tooth difference',abs(360/6-360/8),15)
c('Full-duty load intersection',(1.2-.2)/(.005+.005),100)
c('Full-duty torque',.2+.005*100,.7)
c('Half-duty load intersection',(.6-.2)/(.005+.005),40)
c('Half-duty torque',.2+.005*40,.4)
c('Disturbed acceleration',(.8-.6)/.02,10)
c('Microstep increment',360/(200*8),.225)
c('Duty-weighted mean copper loss',2*(2*6**2+6*2**2)/8,24)
c('Squared-mean-current distractor',2*((2*6+6*2)/8)**2,18)
c('Unweighted loss distractor',(72+8)/2,40)
# Independent implementation paths for the author's added models, not independent-person review.
rng=random.Random(53);varied=0
for _ in range(1000):
 V=rng.uniform(1,60);Rr=rng.uniform(.1,10);k=rng.uniform(.01,.3);omega=rng.uniform(0,V/k);I=(V-k*omega)/Rr
 assert math.isclose(V*I,I*I*Rr+k*I*omega,rel_tol=1e-9,abs_tol=1e-8);varied+=1
 load0=rng.uniform(0,k*V/Rr*.8);slope=rng.uniform(.001,.05);w=(k*V/Rr-load0)/(k*k/Rr+slope)
 assert w>0 and math.isclose(k*(V-k*w)/Rr,load0+slope*w,rel_tol=1e-9);varied+=1
 assert k*(V-k*(w*.99))/Rr-(load0+slope*w*.99)>0 and k*(V-k*(w*1.01))/Rr-(load0+slope*w*1.01)<0;varied+=1
 ns=rng.choice([12,24,72,144,180,200]);micro=rng.choice([1,2,4,8,16]);rate=rng.uniform(1,5000);rpm=rate*60/(ns*micro)
 assert math.isclose(rpm/60*360,rate*(360/ns/micro),rel_tol=1e-10);varied+=1
 flux=rng.uniform(.001,.1);ia=rng.uniform(.1,10);factor=rng.uniform(.2,2)
 assert math.isclose((flux*factor)*(ia*factor)/(flux*ia),factor**2,rel_tol=1e-10);varied+=1
# Enumerate bridge switch states for the actual source labels.
valid=[];short=[]
for mask in range(16):
 sw={i+1 for i in range(4) if mask>>i&1}
 if {1,3}<=sw or {2,4}<=sw:short.append(sorted(sw))
 elif sw in ({1,4},{2,3}):valid.append(sorted(sw))
assert valid==[[2,3],[1,4]]
b=json.loads((R/'data/question-batches/W11-L53.json').read_text());ins=json.loads((R/'data/inspection-batches/W11-L53.json').read_text());errors=[]
for key,items in [('question',b['questions']),('concept',b['concepts']),('slide',ins['slides'])]:
 schema=json.loads((R/f'data/schema.{key}.json').read_text())
 for x in items:errors += [x['id']+': '+e for e in schema_errors(x,schema)]
for q in b['questions']:
 assert set(q['solution']['optionExplanations'])=={o['id'] for o in q['options']}
 assert len(set(o['text'] for o in q['options']))==4
 if q['type'] in ('numerical','derivation'):assert q['solution']['steps'] and q['solution']['formulas'],q['id']
 for f in q['solution']['formulas']:assert f['variables'] and f['units'] and f['assumptions'],q['id']
assert not errors,errors
out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorId':b['authorId'],'independentReview':False,'sourceCodePresent':False,'hardwareExecuted':False,'environment':'Existing default Python standard library only; no package install, download or motor operation.','namedChecks':len(checks),'checks':checks,'variedChecks':varied,'variedAllPassed':True,'bridgeValidDrivePairs':valid,'bridgeShootThroughStates':short,'schemaErrors':errors,'scope':'Added exercise models and conservative graph interpretation checked by author; distinct independent review and coverage challenge remain required.'}
(R/'audits/W11-L53-author-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(len(checks),'named;',varied,'varied; schemas clean')
