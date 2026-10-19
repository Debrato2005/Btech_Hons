#!/usr/bin/env python3
"""Repair three independent-review findings without changing accepted items."""
from pathlib import Path
import copy,json
from validate import question_hash
R=Path(__file__).resolve().parents[1]
p=R/'data/question-batches/W02-L07.json'; b=json.loads(p.read_text())
ids={'W02-L07-Q040','W02-L07-Q043','W02-L07-Q047'}
original=copy.deepcopy(b)
assert all(q['version']==1 for q in b['questions'] if q['id'] in ids)
h=R/'audits/batch-history/W02-L07-v1-before-repair.json'
assert not h.exists(); h.write_text(json.dumps(original,indent=2,ensure_ascii=False)+'\n')
for q in b['questions']:
 if q['id'] not in ids:continue
 q.update(version=2,status='draft',reviewIds=[])
 if q['id'].endswith('Q040'):
  old=q['solution']['optionExplanations']['choice-3'];new='This is the negative of row 2, column 2, not the required row 2, column 3 entry.'
  q['solution']['optionExplanations']['choice-3']=new
  q['solution']['misconceptions']=[new if x==old else x for x in q['solution']['misconceptions']]
 elif q['id'].endswith('Q043'):
  q['stem']='In the differential-drive slide, how do the text definitions of r and 2d relate to the sketch?'
  q['citations'][0]['evidenceText']='The text defines wheel radius r and wheel separation 2d. The sketch shows one d segment between the axle midpoint and one wheel, plus heading φ and position (x,y). It does not label r or the full 2d distance.'
  q['citations'][0]['locator']='Lecture 7, physical PDF page 262, printed slide 20: geometry definitions at left and differential-drive sketch at upper right'
  t='The text defines r as wheel radius and 2d as wheel separation; the sketch labels only one half-separation d.'
  q['solution']['justification']=t;q['solution']['simpleExplanation']=t
 else:
  for o in q['options']:
   if o['id']=='choice-1':o['text']='It is clockwise when v_r<0, counterclockwise when v_r>0, and at rest when both wheel speeds are zero'
  t='Substituting v_l=−v_r gives v=0 and ω=v_r/d: the sign sets rotation direction, while v_r=0 gives rest.'
  q['solution']['justification']=t;q['solution']['simpleExplanation']=t
  q['solution']['optionExplanations']['choice-1']='This includes both rotation directions and the zero-speed exception.'
  q['solution']['steps'].append('If v_r=v_l=0, both the center speed and yaw rate are zero.')
  q['conflictResolution']['basis']=t
before={q['id']:question_hash(q) for q in original['questions']}
assert all(question_hash(q)==before[q['id']] for q in b['questions'] if q['id'] not in ids)
p.write_text(json.dumps(b,indent=2,ensure_ascii=False)+'\n')
packet=[{k:q[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')} for q in b['questions'] if q['id'] in ids]
(R/'audits/blind-W02-L07-v2.json').write_text(json.dumps(packet,indent=2,ensure_ascii=False)+'\n')
print('Revised 3 questions; 58 accepted question hashes unchanged.')
