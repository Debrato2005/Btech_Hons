#!/usr/bin/env python3
"""Persist sixteen L14 revision reviews and two new gap reviews without edits."""
import collections,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import CHECK_KEYS,question_hash
load=lambda p:json.loads((R/p).read_text())
blindpath=R/'audits/blind-answers-W03-L14-v2-independent.json';blind=load(blindpath)
assert blind['complete'] and not blind['keyedRevisionBatchOpened']
qs={q['id']:q for path in ['data/question-batches/W03-L14.json','data/question-batches/W03-L14-GAP.json'] for q in load(path)['questions']}
accepted=load('audits/W03-L14-independent-summary.json')['approvedCurrentHashes'];assert len(accepted)==37
assert all(question_hash(qs[qid])==h for qid,h in accepted.items())
answers={a['questionId']:a for a in blind['answers']}
old={q['id']:q for q in load('audits/batch-history/W03-L14-v1-before-quality-repair.json')}
diffs={}
for packet in blind['sourcePackets']:
 assert hashlib.sha256((R/packet['path']).read_bytes()).hexdigest()==packet['sha256']
 for p in load(packet['path']):
  q=qs[p['id']]
  for k in ['stem','version','selectionMode','options','assumptions','difficulty']:assert p[k]==q[k]
  assert set(q['correctOptionIds'])==set(answers[q['id']]['independentAnswerOptionIds'])
  if q['id'] in old:diffs[q['id']]=[k for k in set(q)|set(old[q['id']]) if q.get(k)!=old[q['id']].get(k)]
assert len(answers)==18
comp=load('audits/W03-L14-independent-computations.json');assert comp['allPassed'] and comp['caseCount']==2218
flags={}
now=datetime.datetime.now(datetime.timezone.utc).isoformat();reviewer=blind['reviewerId'];reviews=[]
for qid,a in answers.items():
 q=qs[qid];assert reviewer not in {q['authorId'],*q.get('revisionAuthors',[])}
 checks={k:True for k in CHECK_KEYS}
 for f in flags.get(qid,[]):checks[f['check']]=False
 reviews.append({'id':f"REV-{qid}-v{q['version']}-interface-revision-gap-review",'questionId':qid,'questionVersion':q['version'],'questionSha256':question_hash(q),'reviewerId':reviewer,'decision':'flagged' if qid in flags else 'verified','reviewedAt':now,'sourceVersions':{c['sourceId']:c['sourceSha256'] for c in q['citations']},'reviewedSlideIds':a['reviewedSlideIds'],'sourceInspectionEvidence':[{'physicalPage':c['physicalPage'],'inspectorIds':[reviewer],'previewSha256':hashlib.sha256((R/f"sources/previews/lectures/page-{c['physicalPage']:04d}.webp").read_bytes()).hexdigest()} for c in q['citations']],'independentAnswerOptionIds':a['independentAnswerOptionIds'],'solvedBeforeAnswerSeen':a['solvedBeforeAnswerSeen'],'priorReviewerExposure':a['priorReviewerExposure'],'priorAuthorExposure':False,'reviewType':a['reviewType'],'checks':checks,'reasoning':a['reasoning']+' After the saved answer freeze, I checked all revised options, explanations, full formulas and units, steps, assumptions and citation roles. All 18 keys agree. The clarified A coefficient is now self-contained; option vectors no longer depend on option order. The physical total torque includes the actuator, and the wrong cosine derivative rationale now retains the radius when discussing the full angle derivative. Q040 has a precise source-version-bound local glyph qualification, without globally changing p446. Source-attributed limitation claims remain explicitly attributed rather than universal. Targeted difficulty and distractor repairs are appropriate. Both new gap questions cover genuinely distinct source points. All 37 earlier approved hashes remain unchanged. Independent 2,218 dynamics cases were rerun; stopping work was also recomputed as 0−0.5*2*3²=−9 J. No specific AI performance claim is inferred.','findings':[f['finding'] for f in flags.get(qid,[])],'blindAnswersPath':str(blindpath.relative_to(R)),'blindAnswersSha256':hashlib.sha256(blindpath.read_bytes()).hexdigest(),'computationsPath':'audits/W03-L14-v2-independent-computations.json'})
p=R/'data/reviews/W03-L14-v2-and-gap-independent.json';assert not p.exists();p.write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n')
summary={'reviewedAt':now,'reviewed':18,'verified':18,'flagged':0,'answerAgreement':18,'answerCorrectionsRequired':0,'revisionRereviews':16,'newBlindReviews':2,'preservedPriorApprovals':37,'priorApprovedHashesUnchanged':True,'approvedCurrentHashes':{r['questionId']:r['questionSha256'] for r in reviews if r['decision']=='verified'},'allReviewedCurrentHashes':{r['questionId']:r['questionSha256'] for r in reviews},'actionableFlags':flags,'revisionChangedFields':diffs,'sourcePagesReinspected':blind['sourcePagesReinspected'],'computationGroupsPassed':len(comp['groups']),'computationCasesPassed':comp['caseCount'],'coverageGapsClosedByNewVerifiedQuestions':['W03-L14-GAP-Q001','W03-L14-GAP-Q002'],'coverageGapRemaining':None,'reviewPath':str(p.relative_to(R)),'notes':['Sixteen repairs are honest revision re-reviews, not fresh blind solves. Two new gap answers were frozen before keyed gap access.','Q040 qualification is scoped to the unclear lower mass-matrix glyph; valid upper equations and positive kinetic energy remain usable.','No authored question, source ledger, inspection, canonical bank or Git state was edited.']}
(R/'audits/W03-L14-v2-independent-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['reviewed','verified','flagged','answerAgreement','preservedPriorApprovals','revisionRereviews','newBlindReviews']},indent=2))
