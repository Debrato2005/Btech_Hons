# HISTORICAL PREPARATION SNAPSHOT ONLY. Do not execute. The current script is scripts/freeze_ASSIGN_recovered.py. Frozen reviewed data must not be regenerated.
"""Freeze new W11/W12 drafts with accurate neutral source locators; no bank writes."""
from assignment_second_half_common import *
from validate import validate_bank, question_hash
import sys,re
w=int(sys.argv[1]);assert w in (11,12);B=f'ASSIGN-W{w:02}'
packetpath=f'audits/blind-{B}.json';assert not(ROOT/packetpath).exists(),'Frozen; do not regenerate'
b=json.loads((ROOT/f'data/question-batches/{B}.json').read_text());qs=b['questions'];ins=json.loads((ROOT/f'data/inspection-batches/{B}-author.json').read_text());checks=[]
def ck(n,v):assert v,n;checks.append(n)
for q in qs:
 ck(q['id']+' draft',q['status']=='draft' and q['reviewIds']==[])
 ck(q['id']+' original hash',q['originalRecordSha256']==sha(q['originalRecordPath']))
 ck(q['id']+' distinct options',len({o['text']for o in q['options']})==len(q['options']))
 ck(q['id']+' exhaustive rationales',set(q['solution']['optionExplanations'])=={o['id']for o in q['options']})
 ck(q['id']+' source hash',all(c['sourceSha256']==SOURCE for c in q['citations']))
 ck(q['id']+' canonical hash agrees',qhash(q)==question_hash(q))
 if q['type']=='numerical':ck(q['id']+' full numerical work',bool(q['solution']['steps'])and bool(q['solution']['formulas']))
 for f in q['solution']['formulas']:ck(q['id']+' formula complete '+f['expression'],bool(f['expression'])and bool(f['variables'])and set(f['variables'])==set(f['units'])and bool(f['assumptions']))
 ck(q['id']+' no relative choices',not re.search(r'(?i)all of the above|none of the above|first two options',q['stem']+' '.join(o['text']for o in q['options'])))
checksart=json.loads((ROOT/f'audits/{B}-author-checks.json').read_text());ck('checks match exact questions',checksart['questionHashes']=={q['id']:qhash(q)for q in qs})
bank=json.loads((ROOT/'data/bank.json').read_text())
for key,rows in [('questions',qs),('concepts',b['concepts'])]:
 ids={z['id']for z in rows};bank[key]=[z for z in bank[key]if z['id']not in ids]+copy.deepcopy(rows)
sm={s['id']:s for s in bank['slides']}
for s in ins['slides']:
 old=sm[s['id']];new=copy.deepcopy(s);new['conceptIds']=sorted(set(old['conceptIds'])|set(new['conceptIds']));sm[s['id']]=new
bank['slides']=list(sm.values());result=validate_bank(bank,ROOT,check_files=False)
dump(f'audits/{B}-preflight.json',{'role':'Author structural checks only','checkedAt':NOW(),'checks':checks,'validation':result});assert result['valid'],result['errors']
packet=[]
for q in qs:
 z={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','cognitiveSkill','week','lectureId','topic','subtopic','assumptions','options')}
 z['citations']=[{k:copy.deepcopy(v)for k,v in c.items()if k!='evidenceText'}for c in q['citations']]
 # These are exact, neutral page-region descriptions authored without answer values.
 # Unlike the old generic freezer, never pretend every page has choices/worked text.
 packet.append(z)
dump(packetpath,{'batchId':B,'instructions':'Solve each adaptation using actual source pages before opening keyed batches, immutable originals or author checks. Author evidenceText, key and solutions are hidden. Original printed source keys are visible; disclose that exposure. No self-approval.','questions':packet})
dump(f'audits/blind-binding-{B}.json',{'packetSha256':sha(packetpath),'questions':[{'id':q['id'],'version':q['version'],'sha256':qhash(q)}for q in qs]})
dump(f'audits/{B}-freeze.json',{'frozenAt':NOW(),'questionCount':len(qs),'conceptCount':len(b['concepts']),'actualPages':[s['physicalPage']for s in ins['slides']],'packetSha256':sha(packetpath),'bindingSha256':sha(f'audits/blind-binding-{B}.json'),'authorChecksSha256':sha(f'audits/{B}-author-checks.json'),'sourceViewLog':f'audits/assignment-coverage/W{w:02}-recovered-source-view-log.json','sourceAnswerExposure':True,'allDraft':True,'independentReviewComplete':False})
print('FROZEN',B,sha(packetpath),'preflight',len(checks),'groups')
