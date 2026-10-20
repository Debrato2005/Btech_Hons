"""Validate and freeze a supplied completed second-half week; no canonical writes."""
from assignment_second_half_common import *
import sys,re
from validate import validate_bank
w=int(sys.argv[1]);B=f'ASSIGN-W{w:02}'
assert 7<=w<=12
assert not (ROOT/f'audits/blind-{B}.json').exists(),'Already frozen'
b=json.loads((ROOT/f'data/question-batches/{B}.json').read_text());ins=json.loads((ROOT/f'data/inspection-batches/{B}-author.json').read_text());qs=b['questions'];checks=[]
def ck(n,v):assert v,n;checks.append(n)
for q in qs:
 ck(q['id']+' draft',q['status']=='draft' and not q['reviewIds'])
 ck(q['id']+' original hash',q['originalRecordSha256']==sha(q['originalRecordPath']))
 ck(q['id']+' option rationales',set(q['solution']['optionExplanations'])=={o['id']for o in q['options']})
 ck(q['id']+' distinct options',len({o['text']for o in q['options']})==len(q['options']))
 ck(q['id']+' source-item link',q['assignmentSourceItemId']in ITEMS)
 ck(q['id']+' no option-relative answer',not re.search(r'(?i)all of the above|none of the above|first two options',q['stem']+' '+q['solution']['justification']))
 ck(q['id']+' formula definitions',all(f['expression'] and f['variables'] and set(f['variables'])==set(f['units']) and f['assumptions']for f in q['solution']['formulas']))
 if q['type']=='numerical':ck(q['id']+' numerical working',bool(q['solution']['steps'])and bool(q['solution']['formulas']))
 if any(c['role']=='conflict' for c in q['citations']):ck(q['id']+' conflict binding',q.get('conflictResolution',{}).get('questionVersion')==q['version'])
bank=json.loads((ROOT/'data/bank.json').read_text())
for key,values in [('questions',qs),('concepts',b['concepts'])]:
 ids={v['id']for v in values};bank[key]=[x for x in bank[key]if x['id']not in ids]+copy.deepcopy(values)
# Preserve all prior assignment concepts on shared page metadata in validation memory.
sm={s['id']:s for s in bank['slides']}
for s in ins['slides']:
 old=sm[s['id']];new=copy.deepcopy(s);new['conceptIds']=sorted(set(old['conceptIds'])|set(s['conceptIds']));sm[s['id']]=new
bank['slides']=list(sm.values());result=validate_bank(bank,ROOT,check_files=False)
dump(f'audits/{B}-preflight.json',dict(role='Author structural checks, not independent review',checkedAt=NOW(),localChecks=checks,validation=result))
print('preflight',len(checks),'valid',result['valid']);print(result['errors'][:20]);assert result['valid']
checks_art=json.loads((ROOT/f'audits/{B}-author-checks.json').read_text());ck('numeric checks bind current questions',checks_art['questionHashes']=={q['id']:qhash(q) for q in qs})
packet=[]
for q in qs:
 z={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','cognitiveSkill','week','lectureId','topic','subtopic','assumptions','options')}
 z['citations']=[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]
 # Locators are neutral item/region identifiers, not author conclusions.
 for c in z['citations']:c['locator']=f"Assignment physical page {c['physicalPage']}, Week {w}, printed item {int(q['assignmentSourceItemId'].split('-Q')[1])}: relevant prompt, choices and worked explanation."
 if q.get('externalSources'):z['externalSources']=[{k:v for k,v in e.items()if k in ('title','url','version')}for e in q['externalSources']]
 packet.append(z)
dump(f'audits/blind-{B}.json',dict(batchId=B,instructions='Solve these author adaptations from actual sources before opening keyed batches, originals audit or author checks. Source keys are visible; disclose that exposure. No author-written evidenceText or answer explanations are included.',questions=packet))
dump(f'audits/blind-binding-{B}.json',dict(packetSha256=sha(f'audits/blind-{B}.json'),questions=[dict(id=q['id'],version=q['version'],sha256=qhash(q))for q in qs]))
dump(f'audits/{B}-freeze.json',dict(frozenAt=NOW(),questionCount=len(qs),conceptCount=len(b['concepts']),actualPages=[s['physicalPage']for s in ins['slides']],packetSha256=sha(f'audits/blind-{B}.json'),bindingSha256=sha(f'audits/blind-binding-{B}.json'),authorChecksSha256=sha(f'audits/{B}-author-checks.json'),allDraft=True))
print('FROZEN',B,sha(f'audits/blind-{B}.json'))
