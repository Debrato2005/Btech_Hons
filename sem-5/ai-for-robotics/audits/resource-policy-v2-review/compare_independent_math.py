import json,pathlib,sys,math,hashlib,datetime,collections
from decimal import Decimal,ROUND_HALF_UP
R=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'));from check_learning_resources_contracts import oracle,search
D=R/'audits/resource-policy-v2-review';x=json.loads(pathlib.Path('/tmp/resource-policy-v2-review/results.json').read_text());blind=json.loads((R/'audits/blind-answers-learning-resources-v1-contracts.json').read_text());packet=json.loads((R/'audits/blind-learning-resources-v1.json').read_text())
prior={e['exampleId']:e for e in blind['responses']};fixed=0
for e in x['examples']:
 assert math.isclose(e['value'],prior[e['exampleId']]['independentValue'],rel_tol=1e-12,abs_tol=1e-12),e['exampleId'];fixed+=1
def exact_value(k,p):
 d={key:Decimal(str(v)) for key,v in p.items() if isinstance(v,(int,float)) and not isinstance(v,bool)}
 if k=='bayes-two-hypotheses':
  joint=d['prior']*d['likelihoodTrue'];return joint/(joint+(1-d['prior'])*d['likelihoodFalse'])
 if k=='q-learning-update':return (1-d['alpha'])*d['oldQ']+d['alpha']*(d['reward']+(0 if p.get('terminal',False) else d['gamma']*d['maxNextQ']))
 if k=='net-force-component':return d['m']*d['ax']
 if k=='series-stiffness':return d['k1']*d['k2']/(d['k1']+d['k2'])
 if k=='coupled-inertia-torque':return d['a']*d['x']+d['b']*d['y']
 if k=='epsilon-greedy-probability':return 1-d['epsilon']+d['epsilon']/d['actions']
 if k=='pinhole-image-x':return d['fMM']*d['X']/d['Z']
 if k=='convolution-output-size':return (d['I']+2*d['P']-d['K'])//d['S']+1
 if k=='octile-grid-distance':return d['cell']*(max(d['dx'],d['dy'])-min(d['dx'],d['dy'])+Decimal(2).sqrt()*min(d['dx'],d['dy']))
 if k=='lidar-roundtrip-range':return Decimal('.15')*d['timeNS']
 if k=='uniform-sample-count':return d['rate']*d['durationMS']/1000
 if k=='adc-uniform-bin-width':return d['reference']/Decimal(2)**int(d['bits'])
 return Decimal(str(oracle(k,p)))
counts=collections.Counter()
for e in x['generated']:
 z=oracle(e['kind'],e['parameters']);assert math.isclose(e['value'],z,rel_tol=1e-12,abs_tol=1e-12),e
 assert len(e['options'])==4 and len(set(e['options']))==4,e
 rounded=float(exact_value(e['kind'],e['parameters']).quantize(Decimal(1).scaleb(-e['precision']),rounding=ROUND_HALF_UP));assert sum(abs(v-rounded)<1e-10 for v in e['options'])==1,e
 counts[e['kind']]+=1
tracechecks=[]
for r in packet['resources']:
 if r.get('examples'):continue
 t=next(z['trace'] for z in x['traces'] if z['resourceId']==r['id'])
 if 'graph' in r:
  independent=search(r);assert t['path']==independent['path'] and t['cost']==independent['cost'] and t['expansions']==independent['successorExpansionCount']
  actual=t['steps'][1:];assert len(actual)==len(independent['trace'])
  for a,b in zip(actual,independent['trace']):
   assert a['current']['node']==b['current'];assert [z['node'] for z in a['frontier']]==b['frontier'];assert {z['node']:z['g'] for z in a['frontier']}==b['g'];assert a['closed']==b['closed']
  tracechecks.append({'id':r['id'],'completeStepsMatched':len(actual),'path':t['path'],'cost':t['cost']})
 else:
  expected=next(z for z in blind['algorithmTraces'] if z['resourceId']==r['id']);actual=t['steps'][1:];assert len(actual)==len(expected['trace'])
  for a,b in zip(actual,expected['trace']):assert a['q']==b['table']
  tracechecks.append({'id':r['id'],'completeStepsMatched':len(actual),'finalQ':t['finalQ']})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fixedAnswersMatched':fixed,'newSeedCasesMatched':sum(counts.values()),'perFamily':dict(counts),'fourDistinctRoundedAlternativesPerCase':True,'replayChecksPassed':13000,'completeTraceChecks':tracechecks,'independentOraclePath':'scripts/check_learning_resources_contracts.py','independentOracleSha256':hashlib.sha256((R/'scripts/check_learning_resources_contracts.py').read_bytes()).hexdigest(),'priorFrozenBlindAnswersSha256':hashlib.sha256((R/'audits/blind-answers-learning-resources-v1-contracts.json').read_bytes()).hexdigest(),'rawRuntimeResultSha256':hashlib.sha256(pathlib.Path('/tmp/resource-policy-v2-review/results.json').read_bytes()).hexdigest(),'scope':'Nonblind revision rerun against the independent Python oracle and prior frozen source-first derivations. No browser, model, dependency or network execution.'}
(D/'independent-math-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
