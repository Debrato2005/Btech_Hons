#!/usr/bin/env python3
"""Freeze prior-exposed revision answers and fresh L14 gap answers."""
import datetime,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];load=lambda p:json.loads((R/p).read_text())
prior={a['questionId']:a for a in load('audits/blind-answers-W03-L14-independent.json')['answers']}
packets=[('audits/blind-W03-L14-v2.json','93409a212a445025d9fe07755ebe5202072e0a062c0cb27b3d7676db26bcedd0'),('audits/blind-W03-L14-GAP.json','f487c33bdb9022a38595b4d2fce2c6dff043b26d41b6e4c4a445b38213a34298')];answers=[]
for p,h in packets:
 assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 for q in load(p):
  fresh='-GAP-' in q['id']
  if fresh:
   key=['o1'];reason=('The p432 formula gives initial K=0.5*2*3²=9 J. Final K=0, so net work done on the translating body is ΔK=−9 J; the positive mechanical energy removed is 9 J. The motion and potential assumptions rule out additional stored mechanical energy in this example.' if q['id'].endswith('001') else 'The p431 slide explicitly calls this a foundation for model-based control and AI-driven dynamics learning. It supplies structured motion equations, not a claim that parameters, nonconservative/contact terms, model assumptions or validation disappear. Using that model and assessing its fit is the bounded application among these choices; no specific AI performance guarantee is inferred.')
  else:key=prior[q['id']]['independentAnswerOptionIds'];reason=prior[q['id']]['reasoning']+' Revised visible premise and alternatives rechecked; prior keyed review exposure means this is not a fresh blind solve.'
  answers.append({'questionId':q['id'],'questionVersion':q['version'],'independentAnswerOptionIds':key,'reasoning':reason,'reviewedSlideIds':[c['slideId'] for c in q['citations']],'solvedBeforeAnswerSeen':fresh,'priorReviewerExposure':not fresh,'reviewType':'fresh source-first blind review' if fresh else 'independent revision re-review, not blind'})
out={'reviewerId':'build_offline_study_interface-L14-independent','frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete':True,'keyedRevisionBatchOpened':False,'sourcePackets':[{'path':p,'sha256':h} for p,h in packets],'sourcePagesReinspected':[431,432,434,441,443,446],'sourceInspectionMethod':'Read actual full-size page images, including the two new gap source slides. All pages 428–449 were previously fully inspected before initial keys. New gap answers frozen before keyed gap access.','answers':answers}
p=R/'audits/blind-answers-W03-L14-v2-independent.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Frozen',len(answers),'answers',out['frozenAt'])
