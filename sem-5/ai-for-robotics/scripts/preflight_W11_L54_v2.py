#!/usr/bin/env python3
"""Changed-item author preflight and in-memory schema check; never canonical writes."""
from pathlib import Path
import json,sys,copy,re
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import validate_bank
B='W11-L54'
def read(p):return json.loads((R/p).read_text())
b=read(f'data/question-batches/{B}.json');ins=read(f'data/inspection-batches/{B}.json');notes=read(f'audits/{B}-v2-author-repair-notes.json');qs=[q for q in b['questions']if q['id']in notes['changedQuestionIds']];checks=[]
def ck(n,t):assert t,n;checks.append(n)
ck('19 changed drafts',len(qs)==19 and all(q['status']=='draft'and not q['reviewIds']for q in qs))
ck('17 revisions, two additions',sum(q['version']==2 for q in qs)==17 and sum(q['version']==1 for q in qs)==2)
for q in qs:
 ck(q['id']+' rationales',set(q['solution']['optionExplanations'])=={o['id']for o in q['options']})
 ck(q['id']+' distinct options',len({o['text']for o in q['options']})==len(q['options']))
 ck(q['id']+' formula metadata',all(f['expression']and f['variables']and f['units']and f['assumptions']for f in q['solution']['formulas']))
 ck(q['id']+' shuffle-safe prose',not re.search(r'(?i)all of the above|none of the above|first two options|option [ABCD]',q['stem']+' '+q['solution']['justification']))
 if q['type']in['numerical','synthesis']:ck(q['id']+' worked formula',bool(q['solution']['steps'])and bool(q['solution']['formulas']))
 if q['version']==2:ck(q['id']+' revision authors',bool(q.get('revisionAuthors')))
 if any(c['role']=='conflict'for c in q['citations']):ck(q['id']+' source conflict binding',q.get('conflictResolution',{}).get('questionVersion')==q['version'])
 ck(q['id']+' citation kinds',all(c['kind']in['statement','equation','table','figure','code','derivation','other']for c in q['citations']))
bank=read('data/bank.json')
# Retain existing canonical eligibility/review links for unchanged accepted objects in memory.
# This is not an approval of edits; only the 19 changed draft objects replace questions.
for key,values in [('questions',qs),('concepts',b['concepts']),('slides',ins['slides'])]:
 ids={v['id']for v in values};bank[key]=[v for v in bank[key]if v['id']not in ids]+copy.deepcopy(values)
result=validate_bank(bank,R,check_files=False)
(R/f'audits/{B}-v2-preflight.json').write_text(json.dumps({'role':'Author preflight, not independent review','localChecks':checks,'validation':result},ensure_ascii=False,indent=2)+'\n')
print('LOCAL CHECKS',len(checks));print(json.dumps(result,ensure_ascii=False)[:3500]);assert result['valid']
