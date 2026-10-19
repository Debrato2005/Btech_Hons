#!/usr/bin/env python3
"""Freeze L13 revision rereview and fresh gap answers before keyed access."""
import datetime, hashlib, json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
load=lambda p:json.loads((R/p).read_text())
prior={a['questionId']:a for a in load('audits/blind-answers-W03-L13-independent.json')['answers']}
packets=[('audits/blind-W03-L13-v2.json','e318c34a91fad30110aa8dd207d523690b8a6fa66971ebfa0ae98fa58cdadf59'),('audits/blind-W03-L13-GAP.json','e4a6412fdd24dae0e3f496d380ada954aaf979e71ddde1b772726a2f997465ea')]
answers=[]
for p,h in packets:
 assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 for q in load(p):
  fresh='-GAP-' in q['id']
  if fresh:
   key=['o1']
   reason=('The p408 diagram shows frame0 fixed at the base, frame1 sharing the base with x1 along the first link, frame2 at the elbow with x2 along the second link, and frame3 at the tip with the same orientation as frame2. Origins and free-vector orientations must not be confused.' if q['id'].endswith('001') else 'The p424 remark concerns the length of fully expanded symbolic torque expressions. The p425 algorithm instead evaluates linkwise kinematics and local inertia terms outward, then loads inward; such numerical recursion does not require a fully expanded symbolic expression or remove velocity/acceleration dependence.')
  else:
   key=prior[q['id']]['independentAnswerOptionIds'];reason=prior[q['id']]['reasoning']+' Rechecked revised premise and difficulty against the previously inspected source; this is a revision re-review, not a fresh blind solve.'
  answers.append({'questionId':q['id'],'questionVersion':q['version'],'independentAnswerOptionIds':key,'reasoning':reason,'reviewedSlideIds':[c['slideId'] for c in q['citations']],'solvedBeforeAnswerSeen':fresh,'priorReviewerExposure':not fresh,'reviewType':'fresh source-first blind review' if fresh else 'independent revision re-review, not blind'})
out={'reviewerId':'build_offline_study_interface-L13-independent','frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete':True,'keyedRevisionBatchOpened':False,'sourcePackets':[{'path':p,'sha256':h} for p,h in packets],'sourcePagesReinspected':[408,421,422,424,425],'sourceInspectionMethod':'Reopened actual readable page pixels; all 24 L13 pages were also inspected during initial review. New gap answers were recorded before keyed gap access. Prior review exposure is explicitly recorded for the eight revisions.','answers':answers}
p=R/'audits/blind-answers-W03-L13-v2-independent.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Frozen',len(answers),'answers',out['frozenAt'])
