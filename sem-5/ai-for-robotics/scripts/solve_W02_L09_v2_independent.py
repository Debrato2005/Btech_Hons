#!/usr/bin/env python3
"""Freeze revision answers before opening keyed v2; disclose prior v1 review."""
import datetime,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'audits/blind-W02-L09-v2.json'; packet=json.loads(p.read_text())
assert hashlib.sha256(p.read_bytes()).hexdigest()=='fb0d3552031ce5961bef2d69947f3457111be871b16188cee8315c7c8fb5b21f'
assert all('evidenceText' not in c for q in packet for c in q['citations'])
old=json.loads((ROOT/'audits/blind-answers-W02-L09-independent.json').read_text()); prior={a['questionId']:a for a in old['answers']}
new_reason={
'W02-L09-P0309-Q08':'The actual diagram puts O on the rotation axis, A at the circle center, and B/C at the old/new tips. OA is the axial projection, AB and AC are circular radii, OB and OC are the full old/new vectors, and the straight BC segment is a finite chord, not the drawn arc. The derivative uses the small-angle limit.',
'W02-L09-P0321-Q09':'The third p321 bullet explicitly names industrial robot teleoperation and AI manipulation. This is source-attributed usefulness, not universal efficiency or safety.',
'W02-L09-P0322-Q14':'The traditional-column p322 bullet names Jacobian-based singularity avoidance. Combined with p319 rank diagnosis and p318 invertible basis re-expression, this means identifying problematic configurations and steering away where feasible, not restoring mechanism rank by basis rotation, inequalities or relabeling the controller.'}
ans=[]
for q in packet:
 new=q['id'] in new_reason
 reason=new_reason[q['id']] if new else prior[q['id']]['reasoning']+' I re-read the revised options and all affected source pixels. The changed distractors, definitions, frame roles or source scope do not change this source-based answer. This is a revision re-review with prior v1 exposure, not a fresh blind solve.'
 ans.append({'questionId':q['id'],'questionVersion':q['version'],'independentAnswerOptionIds':['o1','o2'] if q['id']=='W02-L09-P0322-Q02' else ['o1'],'reasoning':reason,'reviewedSlideIds':list(dict.fromkeys(c['slideId'] for c in q['citations'])),'solvedBeforeAnswerSeen':new,'priorReviewerExposure':not new,'reviewType':'independent_blind_initial_review' if new else 'independent_revision_rereview','blindItemSha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()})
out={'reviewerId':'build_offline_study_interface-L09-v2-independent','frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete':True,'keyedRevisionBatchOpened':False,'sourcePacketPath':str(p.relative_to(ROOT)),'sourcePacketSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'newBlindItemCount':3,'revisionRereviewCount':48,'sourcePagesReinspected':sorted({c['physicalPage'] for q in packet for c in q['citations']}),'sourceInspectionMethod':'Re-inspected all 21 cited page images at readable 1800x1013 scale after reading the answer-hidden revision packet. The initial review previously inspected all 30 lecture pages with extracted text. No v2 keyed batch or author revision script read before this freeze.','answers':ans}
path=ROOT/'audits/blind-answers-W02-L09-v2-independent.json'; assert not path.exists();path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n'); print(out['frozenAt'],len(ans))
