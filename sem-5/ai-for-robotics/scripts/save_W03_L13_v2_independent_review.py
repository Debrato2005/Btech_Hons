#!/usr/bin/env python3
"""Persist eight L13 revision reviews and two new gap reviews without edits."""
import collections,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import CHECK_KEYS,question_hash
load=lambda p:json.loads((R/p).read_text())
blindpath=R/'audits/blind-answers-W03-L13-v2-independent.json';blind=load(blindpath)
assert blind['complete'] and not blind['keyedRevisionBatchOpened']
qs={q['id']:q for path in ['data/question-batches/W03-L13.json','data/question-batches/W03-L13-GAP.json'] for q in load(path)['questions']}
accepted=load('audits/W03-L13-independent-summary.json')['approvedCurrentHashes'];assert len(accepted)==38
assert all(question_hash(qs[qid])==h for qid,h in accepted.items())
answers={a['questionId']:a for a in blind['answers']}
old={q['id']:q for q in load('audits/batch-history/W03-L13-v1-before-quality-repair.json')}
diffs={}
for packet in blind['sourcePackets']:
 assert hashlib.sha256((R/packet['path']).read_bytes()).hexdigest()==packet['sha256']
 for p in load(packet['path']):
  q=qs[p['id']]
  for k in ['stem','version','selectionMode','options','assumptions','difficulty']:assert p[k]==q[k]
  assert set(q['correctOptionIds'])==set(answers[q['id']]['independentAnswerOptionIds'])
  if q['id'] in old:diffs[q['id']]=[k for k in set(q)|set(old[q['id']]) if q.get(k)!=old[q['id']].get(k)]
assert len(answers)==10
comp=load('audits/W03-L13-independent-computations.json');assert comp['allPassed'] and comp['caseCount']==2516
flags={'W03-L13-GAP-Q002':[{'check':'distractors','finding':'Replace the three implausible alternatives with realistic misunderstandings of symbolic expansion versus recursive numerical evaluation, such as requiring pre-expanded joint expressions, omitting downstream loads, or confusing repeated numerical evaluation with one reusable symbolic result. Equal torques at all six joints, eliminating all velocity/acceleration dependence, and guaranteeing shorter six-DOF expansions do not plausibly compete with the correct algorithmic advantage. Keep the key and easy difficulty. Normalize minor number/prose joins when versioning; update every affected explanation and misconception without option-order references.'}]}
now=datetime.datetime.now(datetime.timezone.utc).isoformat();reviewer=blind['reviewerId'];reviews=[]
for qid,a in answers.items():
 q=qs[qid];assert reviewer not in {q['authorId'],*q.get('revisionAuthors',[])}
 checks={k:True for k in CHECK_KEYS}
 for f in flags.get(qid,[]):checks[f['check']]=False
 reviews.append({'id':f"REV-{qid}-v{q['version']}-interface-revision-gap-review",'questionId':qid,'questionVersion':q['version'],'questionSha256':question_hash(q),'reviewerId':reviewer,'decision':'flagged' if qid in flags else 'verified','reviewedAt':now,'sourceVersions':{c['sourceId']:c['sourceSha256'] for c in q['citations']},'reviewedSlideIds':a['reviewedSlideIds'],'sourceInspectionEvidence':[{'physicalPage':c['physicalPage'],'inspectorIds':[reviewer],'previewSha256':hashlib.sha256((R/f"sources/previews/lectures/page-{c['physicalPage']:04d}.webp").read_bytes()).hexdigest()} for c in q['citations']],'independentAnswerOptionIds':a['independentAnswerOptionIds'],'solvedBeforeAnswerSeen':a['solvedBeforeAnswerSeen'],'priorReviewerExposure':a['priorReviewerExposure'],'priorAuthorExposure':False,'reviewType':a['reviewType'],'checks':checks,'reasoning':a['reasoning']+' After recording answers I checked current keyed explanations, complete option sets, assumptions, formula metadata and citation roles. All ten keys agree. The seven difficulty changes match the actual number of reasoning steps. Q028 now preserves and locally qualifies the source transpose error, with source-version and page bindings; it does not globally correct p421. All 38 earlier approved hashes remain unchanged. The original 2,516 independent dynamics checks were rerun. The new frame-origin gap is directly supported by the diagram; the symbolic-complexity gap has a distinct purpose from the existing recursion-order item. Its separate distractor flag does not challenge its correct mathematical point.','findings':[f['finding'] for f in flags.get(qid,[])],'blindAnswersPath':str(blindpath.relative_to(R)),'blindAnswersSha256':hashlib.sha256(blindpath.read_bytes()).hexdigest(),'computationsPath':'audits/W03-L13-v2-independent-computations.json'})
p=R/'data/reviews/W03-L13-v2-and-gap-independent.json';assert not p.exists();p.write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n')
summary={'reviewedAt':now,'reviewed':10,'verified':9,'flagged':1,'answerAgreement':10,'answerCorrectionsRequired':0,'revisionRereviews':8,'newBlindReviews':2,'preservedPriorApprovals':38,'priorApprovedHashesUnchanged':True,'approvedCurrentHashes':{r['questionId']:r['questionSha256'] for r in reviews if r['decision']=='verified'},'allReviewedCurrentHashes':{r['questionId']:r['questionSha256'] for r in reviews},'actionableFlags':flags,'revisionChangedFields':diffs,'sourcePagesReinspected':blind['sourcePagesReinspected'],'computationGroupsPassed':len(comp['groups']),'computationCasesPassed':comp['caseCount'],'coverageGapsClosedByNewVerifiedQuestions':['W03-L13-GAP-Q001'],'coverageGapRemaining':'GAP-Q002 covers symbolic complexity versus recursive evaluation correctly but requires plausible distractors before approval.','reviewPath':str(p.relative_to(R)),'notes':['Eight repairs are honest revision re-reviews, not fresh blind solves. Two new gap answers were frozen before keyed gap access.','Q028 qualification is scoped to one local erroneous expanded transpose; valid neighboring recurrences remain usable.','No authored question, source ledger, inspection, canonical bank or Git state was edited.']}
(R/'audits/W03-L13-v2-independent-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['reviewed','verified','flagged','answerAgreement','preservedPriorApprovals','revisionRereviews','newBlindReviews']},indent=2))
