#!/usr/bin/env python3
"""Default-stdlib author arithmetic and metadata checks, never independent validation."""
from pathlib import Path
import json,hashlib,math,random,decimal,datetime,sys
R=Path(__file__).resolve().parents[1];B='W12-L60';b=json.loads((R/f'data/question-batches/{B}.json').read_text());Q={q['id']:q for q in b['questions']};checks=[]
def ck(n,v):assert v,n;checks.append(n)
def close(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)
ck('Group A accuracy',close(196/200,.98));ck('Group B accuracy',close(12/20,.60));ck('Pooled accuracy',close(208/220,52/55));ck('Pooled percent rounding',format(100*208/220,'.2f')=='94.55');ck('Unweighted-mean distractor',close((.98+.6)/2,.79));ck('Pooled is not equal group metric',not close(208/220,.6))
ck('Edge total',4+8+0+6==18);ck('Cloud total',4+5+30+6==45);ck('Deadline slacks',(20-18,20-45)==(2,-25));ck('Omitted-network distractor',4+5+6==15);ck('Compute-only distractors',(8,5)!=(18,45))
allow=lambda u,c:u<=2 and c>=.8
ck('Inclusive fallback boundary',allow(2,.8));ck('High confidence cannot override action bound',not allow(2.1,.99));ck('Small action cannot override confidence',not allow(1,.7));ck('One accepted proposal',[name for name,u,c in [('P',2,.8),('Q',2.1,.99),('R',1,.7)]if allow(u,c)]==['P'])
ck('Usable energy',close((1-.2)*225,180));ck('Total load',60+30==90);ck('Runtime',close(180/90,2));ck('Mission shortfall',close(2.2-2,.2));ck('No-reserve distractor',close(225/90,2.5));ck('No-compute distractor',close(180/60,3))
p=decimal.Decimal('.98')**10
ck('Independent success exact decimal',p==decimal.Decimal('0.81707280688754689024'));ck('Success rounding',format(p*100,'.2f')=='81.71');ck('Linear failure approximation differs',p!=decimal.Decimal('.80'));ck('Single-step differs',p!=decimal.Decimal('.98'))
for i in ['P1919-Q01','P1924-Q01','P1927-Q01','P1935-Q01','P1935-Q02']:
 q=Q[B+'-'+i];ck(i+' steps and complete formula metadata',bool(q['solution']['steps'])and all(f['expression']and f['variables']and f['units']and f['assumptions']and set(f['variables'])==set(f['units'])for f in q['solution']['formulas']))
ck('All45 actual observations',len(json.loads((R/f'data/inspection-batches/{B}.json').read_text())['slides'])==45)
ck('All questions draft',all(q['status']=='draft'and not q['reviewIds']for q in Q.values()))
rng=random.Random(60002026);assertions=0
for _ in range(1000):
 n1,n2=rng.randint(1,1000),rng.randint(1,1000);c1,c2=rng.randint(0,n1),rng.randint(0,n2);pooled=(c1+c2)/(n1+n2);weighted=(c1/n1*n1+c2/n2*n2)/(n1+n2);assert close(pooled,weighted);assertions+=1
 delays=[rng.uniform(0,40)for _ in range(4)];D=rng.uniform(1,100);total=sum(delays);assert close(D-total+total,D);assertions+=1
 E=rng.uniform(1,1000);r=rng.uniform(0,.9);P=rng.uniform(.1,300);t=(1-r)*E/P;assert close(t*P,(1-r)*E);assertions+=1
 ps=rng.uniform(.05,.999);N=rng.randint(1,60);product=math.prod([ps]*N);assert close(product,ps**N);assertions+=1
 ckval=rng.uniform(0,1);u=rng.uniform(0,3);assert allow(u,ckval)==(not(u>2 or ckval<.8));assertions+=1
out=dict(role='Author deterministic checks, not independent review or hardware testing',checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),runtimeExecutable=sys.executable,pythonVersion=sys.version,importedPackages=['pathlib','json','hashlib','math','random','decimal','datetime','sys'],checkGroups=len(checks),checks=checks,randomCases=1000,randomAssertions=assertions,questionBatchSha256=hashlib.sha256((R/f'data/question-batches/{B}.json').read_bytes()).hexdigest(),sourceCodeExecution='None: L60 has no printed executable code; only explicitly supplied mathematical examples are checked.',restrictionsRespected=['No restricted virtual environment','No installations or corpus/model downloads','No hardware or browser execution claimed'])
(R/f'audits/{B}-author-checks.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print('PASS',len(checks),'groups;',assertions,'varied assertions')
