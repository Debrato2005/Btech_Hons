#!/usr/bin/env python3
"""Remove five option-format clues, retaining original keys and review history."""
from pathlib import Path
import copy,json
from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W01-L02.json';b=json.loads(p.read_text());old=copy.deepcopy(b)
fixes={
35:{2:('Forward prediction → optimizer weight update → loss evaluation → backpropagation gradients','This applies the optimizer before calculating the loss and its current gradients.'),3:('Loss evaluation → backpropagation gradients → forward prediction → optimizer weight update','The loss for the current example needs the forward prediction before differentiation.'),4:('Forward prediction → backpropagation gradients → optimizer weight update → loss evaluation','This places the loss after the gradients and update, instead of defining the error that is differentiated.')},
71:{4:('Domain randomization; meta-learning','Varying simulation conditions matches randomization, but the second method explicitly aligns domains rather than learning how to adapt across tasks.')},
84:{2:('Intent prediction; safe physical interaction; explainability','This swaps contact-force safety monitoring and prediction of a human’s next action.'),3:('Safe physical interaction; explainability; intent prediction','The second operation predicts an action; the third explains a past robot decision.'),4:('Gesture recognition; intent prediction; speech recognition','Force monitoring is not hand/body gesture recognition, and explaining a decision is not merely transcribing speech.')},
89:{2:('Because ethics mainly ranks accuracy after training, with design changes deferred until the benchmark audit','The slide makes ethics a design concern from the outset, not chiefly a post-training accuracy ranking.'),3:('Because privacy protection is the central design task, while fairness and physical reliability belong outside ethical review','The slide includes fairness, safety, reliability and autonomy as well as privacy.'),4:('Because a balanced training set supplies the main ethical safeguard, leaving runtime safety and human oversight to later deployment choices','The source connects data bias with physical safety and human autonomy; balancing data does not replace those design responsibilities.')},
100:{2:('Meta-learning and imitation are listed as formal safety-verification methods, while uncertainty quantification is listed as a demonstration-reduction method','This exchanges the roles of the trustworthy-AI and data-efficiency panels.'),3:('The 5–50 demonstration range supplies a general data-efficiency threshold, while formal verification is proposed for systems that exceed that range','The survey range is not a universal threshold, and the slide does not condition safety methods on exceeding it.'),4:('Trustworthiness is framed mainly as preserving task accuracy after transfer, while data efficiency is framed mainly as reducing hardware power','This conflates transfer performance, trustworthy design and the separate low-power edge-computing direction.')}
}
h=R/'audits/batch-history/W01-L02-v2-before-format-repair.json';assert not h.exists();h.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
for q in b['questions']:
 n=int(q['id'].split('-')[-1])
 if n not in fixes:continue
 assert q['version']==2;q.update(version=3,status='draft',reviewIds=[])
 q['revisionAuthors']=list(dict.fromkeys(q.get('revisionAuthors',[])+['robotics-integration-revision-author']))
 for opt in q['options']:
  k=int(opt['id'].split('-o')[-1])
  if k in fixes[n]:opt['text'],q['solution']['optionExplanations'][opt['id']]=fixes[n][k]
before={q['id']:question_hash(q) for q in old['questions']};assert all(question_hash(q)==before[q['id']] for q in b['questions'] if int(q['id'].split('-')[-1]) not in fixes)
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in b['questions']:
 if int(q['id'].split('-')[-1]) not in fixes:continue
 item={k:q[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 item['citations']=[{k:v for k,v in c.items() if k!='evidenceText'} for c in item['citations']]
 packet.append(item)
(R/'audits/blind-W01-L02-v3.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
print('Revised 5 questions; all 100 accepted hashes unchanged.')
