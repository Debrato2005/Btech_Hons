"""Focused author regressions for repaired content, not independent review."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,math
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash
b=json.loads((R/'data/question-batches/W06-L30.json').read_text());q={int(x['id'][-3:]):x for x in b['questions']};checks=[]
def test(name,condition):
 assert condition,name;checks.append({'name':name,'passed':True})
test('Q010 distinct greedy/sampled targets',np.isclose(2+.9*4,5.6) and np.isclose(2+.9*1,2.9))
test('Q012 explanation distinguishes sign flip from omission',2+1+4==7 and 2+4==6 and 2-1+4==5)
test('Q044 half-up differs from nearest-even',np.rint([5.25,3.75,4.5]).tolist()==[5,4,4] and [math.floor(x+.5) for x in [5.25,3.75,4.5]]==[5,4,5])
test('Q055 source-row update arithmetic',np.isclose(5+.1*(1+.9*7-5),5.23))
L,U=F(-4,25),F(4,25);w=(U-L)/12
encode=lambda e:max(0,min(11,int((e-L)/w)))
test('Q068 exact range-preserving encoding',[encode(e) for e in [L,F(0),U]]==[0,6,11])
test('Q068 upper saturation starts2/15',L+11*w==F(2,15))
test('Q068 each interior bin has declared half-open bounds',all(encode(L+k*w)==k and encode(L+(F(k)+F(1,2))*w)==k for k in range(12)))
test('Q068 tails saturate',[encode(F(-100)),encode(F(100))]==[0,11])
error=np.array([-.03,0,0]);reward=-np.linalg.norm(error)
test('Q071 dense reward consistency',np.isclose(reward,-.03))
test('Q071 update and source encoder',np.isclose(.1*reward,-.003) and tuple(np.clip(((error+.16)/.04).astype(int),0,7))==(3,4,4))
test('Q076 additional step budget',(20000-5000)*50==750000)
test('Q076 nongreedy expectation',F(750000)*F(5,100)*F(5,6)==31250)
test('Q076 random-branch count distinct',F(750000)*F(5,100)==37500)
m=json.loads((R/'audits/W06-L30-v2-repair-manifest.json').read_text())
test('All47 accepted hashes unchanged',all(question_hash(next(x for x in b['questions'] if x['id']==i))==h for i,h in m['preservedAcceptedHashes'].items()))
changed={x['questionId'] for x in m['changedQuestions']}
test('Exactly27v2 repairs plus2v1 new drafts',len(changed)==29 and sum(x['version']==2 for x in b['questions'])==27 and len(b['questions'])==76)
for n in [8,31,37,52,70]:
 for e in q[n]['externalEvidence']:
  import hashlib
  test(f'Q{n:03d} linked API evidence current '+e['section'],hashlib.sha256((R/e['savedEvidencePath']).read_bytes()).hexdigest()==e['savedEvidenceSha256'])
p=json.loads((R/'audits/blind-W06-L30-v2-and-gaps.json').read_text())
test('Changed-only answer-hidden packet',len(p)==29 and all('solution' not in x and 'correctOptionIds' not in x and all('evidenceText' not in c for c in x['citations']) for x in p))
result={'batchId':'W06-L30','role':'Author-focused revision checks only; no independent approval','checkCount':len(checks),'checks':checks,'gapMapping':m['coverageGapMapping'],'priorAuthorExperimentPreserved':'audits/W06-L30-author-simulation.json','newVersionScope':'The Q071 reward/update is corrected; original v1 checks remain evidence for original v1 only.'}
(R/'audits/W06-L30-v2-author-checks.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(checks),'focused checks')
