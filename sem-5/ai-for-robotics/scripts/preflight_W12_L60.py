#!/usr/bin/env python3
"""First-draft structure and exact-source bounds preflight; no canonical write."""
from pathlib import Path
import json,re,sys,copy,hashlib,datetime
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import validate_bank
B='W12-L60'
def rd(p):return json.loads((R/p).read_text())
b=rd(f'data/question-batches/{B}.json');ins=rd(f'data/inspection-batches/{B}.json');obs=rd('audits/L60-page-observations.json');checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('45 physical pages',sorted(s['physicalPage']for s in ins['slides'])==list(range(1909,1954)))
ck('Observed footers strings',all(isinstance(s['printedSlideNumber'],str)for s in ins['slides']))
ck('Actual completed inspection metadata',all(s['visualInspection']['status']=='complete'and s['visualInspection']['method']=='rendered_page'for s in ins['slides']))
ck('Six specific exclusions',sum(s['disposition']=='excluded'for s in ins['slides'])==6)
ck('Every concept drafted',all(c['questionIds']for c in b['concepts']))
ck('No printed code/equation claimed',all(c['kind']=='statement'for q in b['questions']for c in q['citations']))
for q in b['questions']:
 ck(q['id']+' per-option rationales',set(q['solution']['optionExplanations'])=={o['id']for o in q['options']})
 ck(q['id']+' distinct alternatives',len({o['text']for o in q['options']})==len(q['options']))
 ck(q['id']+' complete mathematical metadata',all(set(f['variables'])==set(f['units'])and f['assumptions']for f in q['solution']['formulas']))
 ck(q['id']+' citation/source bounds',all(1909<=c['physicalPage']<=1953 and c['sourceSha256']=='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'and c['locator'].startswith('Printed slide ')for c in q['citations']))
 ck(q['id']+' shuffle-safe wording',not re.search(r'\ball of the above\b|\bnone of the above\b|\bfirst two options\b|\boption [ABCD]\b',json.dumps(q),re.I))
 if q['type']in['numerical','algorithm_trace']:ck(q['id']+' numerical premises/steps',q['solution']['steps']and q['solution']['formulas']and q['assumptions']and any(c['role']=='premise'for c in q['citations'])or q.get('conflictResolution')and q['solution']['steps']and q['solution']['formulas'])
 if any(c['role']=='conflict'for c in q['citations']):ck(q['id']+' qualified source binding',q.get('conflictResolution',{}).get('questionVersion')==q['version'])
bank=rd('data/bank.json')
for key,values in [('questions',b['questions']),('concepts',b['concepts']),('slides',ins['slides'])]:
 ids={v['id']for v in values};bank[key]=[v for v in bank[key]if v['id']not in ids]+copy.deepcopy(values)
r=validate_bank(bank,R,check_files=False)
out={'role':'Author preflight, not independent review','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'localChecks':checks,'validation':r}
(R/f'audits/{B}-preflight.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('LOCAL',len(checks));print(json.dumps(r,ensure_ascii=False)[:6000]);assert r['valid']
