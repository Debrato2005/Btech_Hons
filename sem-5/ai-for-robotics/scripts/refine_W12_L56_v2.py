#!/usr/bin/env python3
"""Pre-freeze identifier-safe proofreading of the nine changed drafts only."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[1];B='W12-L56';assert not(R/f'audits/{B}-v2-repair-manifest.json').exists()
b=json.loads((R/f'data/question-batches/{B}.json').read_text());n=json.loads((R/f'audits/{B}-v2-author-repair-notes.json').read_text())
def fix(x):
 if isinstance(x,str):
  x=re.sub(r'\b([abo]) ([1-4])\b',r'\1\2',x).replace('L56-v 2-repair','L56-v2-repair')
  for a,z in {'C:20':'C: 20','B:20':'B: 20','A20/s':'A 20/s','payload:640':'payload: 640','transport:30':'transport: 30','transport:20':'transport: 20','capacity:1':'capacity: 1'}.items():x=x.replace(a,z)
  return x
 if isinstance(x,list):return[fix(v)for v in x]
 if isinstance(x,dict):return{k:fix(v)for k,v in x.items()}
 return x
for q in b['questions']:
 if q['id']not in n['changedQuestionIds']:continue
 clean=fix(q);q.clear();q.update(clean)
 if q['id']==B+'-P1798-Q03':q['solution']['formulas'][0]['units']={'age':'s','t_now':'s','t_obs':'s','confidence':'dimensionless','τ':'dimensionless','A_max':'s','valid':'Boolean'}
 assert set(q['solution']['optionExplanations'])=={o['id']for o in q['options']}
 for f in q['solution']['formulas']:assert set(f['variables'])==set(f['units'])
for q in b['questions']:
 if q['id']in n['acceptedQuestionHashes']:
  h=hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest();assert h==n['acceptedQuestionHashes'][q['id']]
(R/f'data/question-batches/{B}.json').write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n');print('Identifier-safe proof complete;59 accepted unchanged')
# Complete the explicit arithmetic relations used in the integrated resource solution.
b=json.loads((R/f'data/question-batches/{B}.json').read_text())
q=next(q for q in b['questions']if q['id']==B+'-P1798-Q05');f=q['solution']['formulas'][0]
f['expression']='b = W H (b_RGB+b_D); R = f b + R_audio; μ=1/t_i; g=max(0,f−μ); A_bound=1/f+t_i+t_p; A_n=(n+1)t_i+t_p−n/f'
f['variables'].update(g='FIFO backlog growth rate when every arriving pair is retained',A_n='age of FIFO result n at publication',n='zero-based pair index for the aligned FIFO example')
f['units'].update(g='pairs/s',A_n='s',n='count')
f['assumptions'].append('The FIFO A_n expression uses capture n/f, first service at time0 and sustained arrivals f≥μ, so service is continuously backlogged after the first pair.')
f['assumptions']=[x.replace('time0','time 0')for x in f['assumptions']]
q=next(q for q in b['questions']if q['id']==B+'-P1789-Q04');q['solution']['formulas'][0]['units']['n_heard']='chunks'
(R/f'data/question-batches/{B}.json').write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
