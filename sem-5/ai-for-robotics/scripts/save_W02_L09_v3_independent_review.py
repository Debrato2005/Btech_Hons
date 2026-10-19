#!/usr/bin/env python3
"""Re-review the one wording-only L09 v3 repair, explicitly not blind."""
import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import CHECK_KEYS,question_hash
load=lambda p:json.loads((R/p).read_text())
qs={q['id']:q for q in load('data/question-batches/W02-L09.json')['questions']}
qid='W02-L09-P0315-Q05';q=qs[qid]
assert question_hash(q)=='d5a7bfee989bfb62168b29c47d082c20c6ff8095b867dbfd5720bdb1f4681271'
accepted={**load('audits/W02-L09-independent-summary.json')['approvedCurrentHashes'],**load('audits/W02-L09-v2-independent-summary.json')['approvedCurrentHashes']}
assert len(accepted)==104 and all(question_hash(qs[k])==v for k,v in accepted.items())
assert q['assumptions']==['Differentiable map; δq is small; δx denotes the corresponding output increment.']
assert q['correctOptionIds']==['o1']
old=next(r for r in load('data/reviews/W02-L09-v2-independent.json') if r['questionId']==qid)
r=copy.deepcopy(old)
r.update({'id':f'REV-{qid}-v3-interface-rereview','questionVersion':3,'questionSha256':question_hash(q),'decision':'verified','reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'solvedBeforeAnswerSeen':False,'priorReviewerExposure':True,'priorAuthorExposure':False,'reviewType':'independent-revision-rereview-not-blind','checks':{k:True for k in CHECK_KEYS},'findings':[],'reasoning':'The wording-only v3 repair now clearly states a differentiable map, a small configuration increment δq, and its corresponding output increment δx. The p315 chain-rule Jacobian is an exact instantaneous rate map; differentiability gives δx=J(q)δq+o(||δq||), so option o1 correctly states a local first-order approximation for finite increments. This is an independent revision re-review with prior knowledge of the v1/v2 answers, not a fresh blind solve. The equation, four options, explanations and medium difficulty remain valid; all 104 previously accepted hashes are unchanged. Actual p315 source pixels were re-inspected during the preceding v2 review and the unchanged preview hash is bound below.','revisionPacketPath':'audits/blind-W02-L09-Q05-v3.json','revisionPacketSha256':hashlib.sha256((R/'audits/blind-W02-L09-Q05-v3.json').read_bytes()).hexdigest()})
assert r['reviewerId'] not in {q['authorId'],*q.get('revisionAuthors',[])}
p=R/'data/reviews/W02-L09-v3-independent.json';assert not p.exists();p.write_text(json.dumps([r],ensure_ascii=False,indent=2)+'\n')
s={'reviewed':1,'verified':1,'flagged':0,'answerAgreement':1,'preservedPriorApprovals':104,'priorApprovedHashesUnchanged':True,'totalCurrentL09Approved':105,'approvedCurrentHashes':{qid:question_hash(q)},'reviewType':r['reviewType'],'reviewPath':str(p.relative_to(R))}
(R/'audits/W02-L09-v3-independent-summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
