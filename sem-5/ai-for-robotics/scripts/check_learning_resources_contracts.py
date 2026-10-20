#!/usr/bin/env python3
"""Independent source-first oracle. Does not import authored resource generators."""
import json,math,hashlib,copy
from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal,ROUND_HALF_UP
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def oracle(k,p):
 if k=='bayes-two-hypotheses':return p['prior']*p['likelihoodTrue']/(p['prior']*p['likelihoodTrue']+(1-p['prior'])*p['likelihoodFalse'])
 if k=='q-learning-update':return (1-p['alpha'])*p['oldQ']+p['alpha']*(p['reward']+(0 if p.get('terminal',False) else p['gamma']*p['maxNextQ']))
 if k=='rotated-vector-x':return p['vx']*math.cos(math.radians(p['angleDeg']))-p['vy']*math.sin(math.radians(p['angleDeg']))
 if k=='net-force-component':return p['m']*p['ax']
 if k=='series-stiffness':return 1/(1/p['k1']+1/p['k2'])
 if k=='coupled-inertia-torque':return p['a']*p['x']+p['b']*p['y']
 if k=='epsilon-greedy-probability':return 1-p['epsilon']+p['epsilon']/p['actions']
 if k=='pinhole-image-x':return p['fMM']*p['X']/p['Z']
 if k=='convolution-output-size':return (p['I']+2*p['P']-p['K'])//p['S']+1
 if k=='octile-grid-distance':return p['cell']*(max(p['dx'],p['dy'])-min(p['dx'],p['dy'])+math.sqrt(2)*min(p['dx'],p['dy']))
 if k=='lidar-roundtrip-range':return .15*p['timeNS']
 if k=='uniform-sample-count':return p['rate']*p['durationMS']/1000
 if k=='adc-uniform-bin-width':return p['reference']/2**p['bits']
 raise ValueError(k)
def search(r):
 adj={n:[] for n in r['graph']['nodes']}
 for e in r['graph']['edges']:adj[e['from']].append((e['to'],e['cost']));adj[e['to']].append((e['from'],e['cost']))
 conf=r['config'];a=conf['algorithm'];start=conf['start'];goal=conf['goal'];h=conf['heuristic'];front=[start];best={start:0};parent={};closed=[];trace=[]
 while front:
  if a in ('ucs','astar'):front.sort(key=lambda n:(best[n]+(h[n] if a=='astar' else 0),n))
  n=front.pop(0);goalHit=n==goal
  if not goalHit:
   closed.append(n)
   neigh=sorted(adj[n]);fresh=[]
   for nb,c in neigh:
    g=best[n]+c
    if (nb not in best) or (a in ('ucs','astar') and g<best[nb]):
     best[nb]=g;parent[nb]=n
     if nb in closed:closed.remove(nb)
     if nb not in front:fresh.append(nb)
   front=fresh+front if a=='dfs' else front+fresh
   if a in ('ucs','astar'):front.sort(key=lambda n:(best[n]+(h[n] if a=='astar' else 0),n))
  trace.append({'current':n,'goal':goalHit,'frontier':list(front),'g':{x:best[x] for x in front},'closed':list(closed)})
  if goalHit:break
 path=[goal]
 while path[-1]!=start:path.append(parent[path[-1]])
 return {'trace':trace,'path':path[::-1],'cost':best[goal],'successorExpansionCount':len(closed)}
if __name__=='__main__':
 out=ROOT/'audits/blind-answers-learning-resources-v1-contracts.json'
 if out.exists():raise SystemExit('Frozen independent answers exist; do not overwrite.')
 p=json.loads((ROOT/'audits/blind-learning-resources-v1.json').read_text());binding=json.loads((ROOT/'audits/blind-binding-learning-resources-v1.json').read_text())
 assert sha(binding['packetPath'])==binding['packetSha256']
 for c in binding['codeFiles']:assert sha(c['path'])==c['sha256'],c['path']
 responses=[];traces=[]
 for r in p['resources']:
  if 'examples' in r:
   for e in r['examples']:
    value=oracle(r['generatorKind'],e['parameters']);precision=e.get('precision',3)
    rounded=Decimal(str(value)).quantize(Decimal(1).scaleb(-precision),rounding=ROUND_HALF_UP)
    answer=[o['id'] for o in e['options'] if Decimal(o['text'].split()[0])==rounded]
    assert len(answer)==1,(e['exampleId'],value,answer)
    responses.append({'exampleId':e['exampleId'],'resourceId':r['id'],'parameters':e['parameters'],'independentValue':value,'rounded':str(rounded),'independentAnswerOptionIds':answer})
  elif 'graph' in r:traces.append({'resourceId':r['id'],**search(r)})
  else:
   c=r['qLearningConfig'];q=copy.deepcopy(c['initialQ']);ts=[]
   for t in c['transitions']:
    old=q[t['state']][t['action']];mx=max(q.get(t['nextState'],{}).get(x,0) for x in t['nextActions']);target=t['reward']+(0 if t['terminal'] else c['gamma']*mx);new=(1-c['alpha'])*old+c['alpha']*target;q[t['state']][t['action']]=new
    ts.append({'oldQ':old,'maxNextQ':mx,'target':target,'updatedQ':new,'table':copy.deepcopy(q)})
   traces.append({'resourceId':r['id'],'trace':ts})
 answer={'reviewerId':'robotics-contracts-independent-reviewer','frozenAt':datetime.now(timezone.utc).isoformat(),'packetSha256':sha(binding['packetPath']),'bindingSha256':sha('audits/blind-binding-learning-resources-v1.json'),'newExampleKeysOrAuthorCodeSeen':False,'priorExposure':'Previously reviewed several underlying lecture questions and sources; this is a separate resource review. New remapped numerical examples and configured traces were independently derived before opening generator code or author expected results. Handoff includes qualitative model descriptions, not expected numerical answers.','responses':responses,'algorithmTraces':traces,'runtime':'Default Python only; no browser or restricted environment used.'}
 out.write_text(json.dumps(answer,indent=2)+'\n');print('Frozen',len(responses),'responses',len(traces),'traces',hashlib.sha256(out.read_bytes()).hexdigest())
 for t in traces:print(t['resourceId'],t.get('path'),t.get('cost'),t.get('successorExpansionCount'),[x.get('updatedQ') for x in t['trace']] if 'path' not in t else [x['current'] for x in t['trace']])
