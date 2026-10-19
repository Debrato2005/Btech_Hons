#!/usr/bin/env python3
"""Repair only two flagged distractor sets. Preserve 98 accepted objects exactly."""
import json,copy,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];B='W04-L19'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
if (R/f'audits/{B}-v3-review-manifest.json').exists():raise SystemExit('L19 v3 is frozen; do not rerun over reviewed content.')
old=read(f'data/question-batches/{B}.json');b=copy.deepcopy(old);ids={f'{B}-P0598-Q04',f'{B}-P0602-Q02'}
rv=read(f'data/reviews/{B}-v2-independent-contracts.json');assert {r['questionId'] for r in rv if r['decision']=='flagged'}==ids
assert len(old['questions'])==100
archive=f'data/question-batches/archive/{B}-v2.json'
if (R/archive).exists():assert read(archive)==old
else:write(archive,old)
changed=[]
for q in b['questions']:
 if q['id'] not in ids:continue
 assert q['version']==2;q.update(version=3,status='draft',reviewIds=[]);q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+['L19-author-20261019']))
 if 'P0598' in q['id']:
  q['stem']='Which capability is explicitly attributed to active center-of-mass shifting on the lecture’s locomotion slide?'
  values={'o1':'Climbing obstacles several times the wheel diameter','o2':'Reducing traction differences between wheels during level-ground travel','o3':'Increasing ground clearance through active suspension extension','o4':'Reducing the turning radius through coordinated wheel steering'}
  why={'o1':'The slide specifically links active COM shifting in some advanced robots to climbing obstacles several times their wheel diameter. This is a source-attributed capability, not a guarantee for arbitrary obstacles.','o2':'Redistributing load can affect individual wheel traction, but equalizing level-ground traction is not the particular capability attributed to COM shifting on this slide.','o3':'Suspension extension is a plausible clearance mechanism, but it is not the COM-shifting obstacle-climbing capability named here.','o4':'Coordinated steering can affect turning geometry, but that is a steering mechanism rather than the slide’s stated COM-shifting capability.'}
 else:
  q['stem']='Which division of base and arm motion is emphasized on the lecture’s mobile-manipulation slide?'
  values={'o1':'The base provides gross relocation while the arm performs fine manipulation','o2':'The base supplies fine tool-position corrections while the arm makes larger movements within its reach','o3':'The base stays parked throughout the task while the arm performs both gross and fine movements','o4':'The arm maintains a fixed pose while base motion provides both gross and fine positioning'}
  why={'o1':'The source emphasizes complementary roles: gross chassis motion and fine manipulation by the arm.','o2':'This is a possible alternative allocation within a local workspace, but it reverses the gross-base/fine-arm division emphasized by the source.','o3':'A parked-base task can be feasible, but it does not use the mobile chassis for the gross motion emphasized here.','o4':'Moving the base with a fixed arm can position the tool in some tasks, but it omits the arm’s emphasized fine-manipulation role.'}
 for o in q['options']:o['text']=values[o['id']]
 q['solution'].update(justification=why['o1'],simpleExplanation=why['o1'],optionExplanations={k:('Correct. ' if k=='o1' else 'Incorrect. ')+v for k,v in why.items()},misconceptions=[why[k] for k in ('o2','o3','o4')]);changed.append(q)
for c in b['concepts']:
 for q in changed:
  prior=next(x for x in old['questions'] if x['id']==q['id']);c['examinationAngles']=[q['stem'] if x==prior['stem'] else x for x in c.get('examinationAngles',[])]
accepted=[q for q in old['questions'] if q['id'] not in ids];assert len(accepted)==98
for q in accepted:assert q==next(x for x in b['questions'] if x['id']==q['id'])
reviews=read(f'data/reviews/{B}-v1-independent-contracts.json')+rv
for q in accepted:assert any(r['questionId']==q['id'] and r['decision']=='verified' and r['questionSha256']==sha(q) for r in reviews)
assert all(q['correctOptionIds']==next(x for x in old['questions'] if x['id']==q['id'])['correctOptionIds'] for q in changed)
write(f'data/question-batches/{B}.json',b)
blind=[{**{k:q[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions')},'citations':[{k:v for k,v in x.items() if k!='evidenceText'} for x in q['citations']]} for q in changed];write(f'audits/blind-{B}-v3.json',blind)
h=hashlib.sha256((R/f'audits/blind-{B}-v3.json').read_bytes()).hexdigest()
write(f'audits/{B}-v3-review-manifest.json',dict(batchId=B,blindPacket=f'audits/blind-{B}-v3.json',blindPacketSha256=h,questionSha256={q['id']:sha(q) for q in changed},preservedAcceptedCount=98,preservedAcceptedHashes={q['id']:sha(q) for q in accepted},independentReviewPending=True))
write(f'audits/{B}-v3-author-checks.json',dict(changedCount=2,preservedCount=98,acceptedObjectsUnchanged=True,acceptedReviewHashesMatch=True,keysUnchanged=True,sourceIssuesUnchanged=b['sourceIssues']==old['sourceIssues'],actualSourcePagesReinspected=[598,602],sourcePrintedFooters=['21','25'],numericCheck='Not applicable: two conceptual source-attribution distractor repairs only.',independentReview=False))
(R/f'audits/handoffs/{B}-v3.md').write_text(f'# L19 v3 frozen\nTwo revised source-attribution distractor sets; all98 accepted objects and review-bound hashes unchanged. All100 questions remain present. Source pages598/602 actually revisited, footers21/25. No numerical changes and no self-approval.\nPacket audits/blind-{B}-v3.json\nSHA256 {h}\nManifest audits/{B}-v3-review-manifest.json\nArchive {archive}\nScript scripts/repair_W04_L19_v3.py\nChecks audits/{B}-v3-author-checks.json\nIndependent re-review required; prior-v2 exposure must be disclosed. No canonical/Git writes.\n')
print(h)
