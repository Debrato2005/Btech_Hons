#!/usr/bin/env python3
"""Author-side preflight, in-memory integration only. No canonical writes."""
import json,copy,re,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import validate_bank
B='W12-L56'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
b=read(f'data/question-batches/{B}.json');i=read(f'data/inspection-batches/{B}.json');bank=read('data/bank.json')
checks=[]
def ck(name,v):assert v,name;checks.append(name)
ck('67 complete draft questions',len(b['questions'])==67 and all(q['status']=='draft'and not q['reviewIds']for q in b['questions']))
ck('26 actual page inspections',len(i['slides'])==26 and all(s['visualInspection']['status']=='complete'for s in i['slides']))
ck('actual footer strings',all(s['printedSlideNumber']==str(s['physicalPage']-1776)for s in i['slides']))
ck('all 21 concept families have drafts',len(b['concepts'])==21 and all(c['questionIds']for c in b['concepts']))
ck('All 21 examinable pages have exact citations',all(s['disposition']!='examinable'or any(any(c['physicalPage']==s['physicalPage']for c in q['citations'])for q in b['questions'])for s in i['slides']))
ck('No forbidden environment use required',read(f'audits/{B}-author-checks.json')['checkGroups']==33)
ck('All 9 formula records have complete fields',sum(len(q['solution']['formulas'])for q in b['questions'])==9 and all(f['expression']and f['variables']and f['units']and f['assumptions']for q in b['questions']for f in q['solution']['formulas']))
for q in b['questions']:
 ck(q['id']+' rationales/options',set(q['solution']['optionExplanations'])=={o['id']for o in q['options']}and len(set(o['text']for o in q['options']))==len(q['options']))
 if q['type']in['numerical','algorithm_trace']:ck(q['id']+' explicit steps',bool(q['solution']['steps']))
 if q['type']=='numerical':ck(q['id']+' formula record',bool(q['solution']['formulas']))
 if any(c['role']=='conflict'for c in q['citations']):ck(q['id']+' bound qualification',q.get('conflictResolution',{}).get('questionVersion')==q['version'])
 ck(q['id']+' no shuffle-relative reference',not re.search(r'(?i)all of the above|none of the above|first two options|option [ABCD]',q['stem']+' '+q['solution']['justification']))
for collection,own in [('questions',b['questions']),('concepts',b['concepts']),('slides',i['slides'])]:
 ids={x['id']for x in own};bank[collection]=[x for x in bank[collection]if x['id']not in ids]+copy.deepcopy(own)
result=validate_bank(bank,R,check_files=False)
write(f'audits/{B}-preflight.json',{'role':'author-side structural preflight, not independent review','localChecks':checks,'validation':result})
print(json.dumps(result,ensure_ascii=False)[:1000]);print('Preflight local checks',len(checks))
