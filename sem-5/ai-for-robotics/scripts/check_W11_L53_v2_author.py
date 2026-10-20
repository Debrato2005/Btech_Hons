"""Author-only deterministic checks for L53 changed items and added models."""
from pathlib import Path
import json,math,random,datetime,hashlib,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash
checks=[]
def ck(name,value):
 assert value,name
 checks.append(name)
ck('Angled wire force',math.isclose(.5*3*.2*math.sin(math.pi/6),.15))
ck('Back EMF',.1*100==10)
ck('Shunt line current',(24-20)/2+24/120==2.2)
ck('Tachometer error',100-1.6/.02==20)
ck('Calibration distractor',100-1.6/.04==60)
ck('One-pair synchronous speed',60*50==3000)
ck('Four-pole synchronous speed',120*50/4==1500)
ck('Slip',(1500-1440)/1500==.04)
ck('Full-step angle',360/144==2.5)
ck('Full-step displacement and duration',50*360/200==90 and 50/500==.1)
ck('Full-step speed',60*500/200==150)
ck('Two-error speed foil',500*200==100000)
ck('Duty copper loss',(6**2*2*2+2**2*2*6)/8==24)
ck('Incorrect equal segment weighting',(6**2*2+2**2*2)/2==40)
ck('Incorrect square of average current',((6*2+2*6)/8)**2*2==18)
ck('Separate flux scaling comparisons',24/.05==2*(24/.1) and .2/.05==2*(.2/.1))
# Bridge diode direction graph, all transistors open. Supply is a declared absorbing return.
edges={('G','L'),('G','R'),('L','V'),('R','V'),('V','G'),('L','R')}
path=['G','L','R','V','G'];ck('Bridge continuation path follows every directed edge',all((a,b) in edges for a,b in zip(path,path[1:])))
ck('Both-upper-only path cannot feed positive motor current',('V','L') not in edges)
ck('Both-lower-only path cannot accept positive motor current',('R','G') not in edges)
ck('Diode clamps give negative motor voltage',0-24==-24)
ck('Motor returns 48 W at switching instant',(0-24)*2==-48)
# Explicit nearest-alignment trace. Phase axes and opposite poles reduce modulo 180 degrees.
axes={'A':0,'B':45,'C':90,'D':135}
def shift(theta,phase):
 candidates=[]
 for a in [axes[phase],axes[phase]+180]:
  for k in range(-20,21):candidates.append(a-(theta+60*k))
 m=min(abs(z) for z in candidates);nearest={round(z,9) for z in candidates if abs(abs(z)-m)<1e-8};assert len(nearest)==1
 return nearest.pop()
theta=0;trace=[]
for phase in ['B','C','D','A','D','C','B','A']:
 delta=shift(theta,phase);theta+=delta;trace.append({'phase':phase,'delta':delta,'theta':theta})
ck('Forward four-phase trace',[z['theta'] for z in trace[:4]]==[-15,-30,-45,-60])
ck('Reversed four-phase trace',[z['theta'] for z in trace[4:]]==[-45,-30,-15,0])
ck('Marked-tooth travel',sum(abs(z['delta']) for z in trace)==120)
# Explicit integrated candidate table.
wm=10*20;tm=1.6/(.8*10);current=tm/.1;duty=2/8
ck('Required motor state',wm==200 and math.isclose(tm,.2) and math.isclose(current,2))
rows={}
for name,r,peak,lim in [('A',2,3,2.5),('B',3,3,4),('C',2,1.5,2.5),('D',2,3,1.5)]:
 voltage=.1*wm+current*r;loss=duty*current**2*r;rows[name]={'voltage':voltage,'current':current,'meanCopperLoss':loss,'voltagePass':voltage<=24,'peakPass':current<=peak,'thermalPass':loss<=lim}
ck('Only candidate A passes',[n for n,z in rows.items() if z['voltagePass'] and z['peakPass'] and z['thermalPass']]==['A'])
ck('B fails only voltage',not rows['B']['voltagePass'] and rows['B']['peakPass'] and rows['B']['thermalPass'])
ck('C fails only peak',rows['C']['voltagePass'] and not rows['C']['peakPass'] and rows['C']['thermalPass'])
ck('D fails only mean heating',rows['D']['voltagePass'] and rows['D']['peakPass'] and not rows['D']['thermalPass'])
rng=random.Random(532);varied=0
for _ in range(1000):
 V=rng.uniform(1,100);I=rng.uniform(.001,10);assert (-V)*I<0;varied+=1
 f=rng.uniform(1,200);p=rng.randint(1,10);ns=60*f/p;sl=rng.uniform(0,.2);nr=(1-sl)*ns;assert math.isclose((ns-nr)/ns,sl,abs_tol=1e-14);varied+=1
 ns=rng.choice([12,24,72,144,180,200]);fc=rng.uniform(.1,1000);count=rng.randint(1,1000);speed=60*fc/ns;t=count/fc;assert math.isclose(speed*t*6,count*360/ns);varied+=1
 i1=rng.uniform(0,10);i2=rng.uniform(0,10);w=rng.random();Rr=rng.uniform(.1,10);average=Rr*(w*i1*i1+(1-w)*i2*i2);squaremean=Rr*(w*i1+(1-w)*i2)**2;assert average+1e-10>=squaremean;varied+=1
 initial=60*rng.randint(-10,10);th=initial
 for phase in ['B','C','D','A','D','C','B','A']:th+=shift(th,phase)
 assert th==initial;varied+=1
b=json.loads((R/'data/question-batches/W11-L53.json').read_text());old=json.loads((R/'data/history/W11-L53/W11-L53-v1.json').read_text());summary=json.loads((R/'audits/W11-L53-contracts-review-summary.json').read_text());oldq={q['id']:q for q in old['questions']};qq={q['id']:q for q in b['questions']}
ck('All 62 accepted whole objects and hashes preserved',len(summary['acceptedQuestionHashes'])==62 and all(qq[i]==oldq[i] and question_hash(qq[i])==h for i,h in summary['acceptedQuestionHashes'].items()))
ck('Exactly the 29 flagged original objects changed',{q['id'] for q in b['questions'] if q['id'] in oldq and q!=oldq[q['id']]}==set(summary['flaggedFindings']))
ck('Two new gap drafts and no self-approval',len(b['questions'])==93 and all(q['status']=='draft' for q in b['questions'] if q['id'] not in oldq or q['id'] in summary['flaggedFindings']))
ck('Original source-claim qualifications preserved',all('conflictResolution' not in q or q['conflictResolution']['sourceClaim']==qq[q['id']]['conflictResolution']['sourceClaim'] for q in old['questions']))
r={'batchId':'W11-L53','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Author-only deterministic ideal models, declared candidate ratings and nearest-tooth geometry. No hardware, dependency installation, external notebook or browser execution.','independentReview':False,'namedChecks':len(checks),'checks':checks,'variedChecks':varied,'variedTrials':1000,'bridgePath':path,'phaseTrace':trace,'candidateResults':rows,'acceptedPreserved':62,'newIndependentReviewRequired':True}
(R/'audits/W11-L53-v2-author-checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'named':len(checks),'varied':varied,'candidate':rows,'phaseTrace':trace}))
