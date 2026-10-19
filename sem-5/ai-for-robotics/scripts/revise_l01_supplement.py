from pathlib import Path
import json,copy
R=Path(__file__).resolve().parents[1]; p=R/'data/question-batches/W01-L01-supplement.json'; b=json.loads(p.read_text())
if any(q['version']!=1 for q in b['questions']):raise SystemExit('Already revised; do not overwrite later versions.')
(R/'audits/question-history/W01-L01-supplement-v1.json').write_text(json.dumps(b,ensure_ascii=False,indent=2))
r=json.loads((R/'data/reviews/W01-L01-supplement-v1-independent.json').read_text()); flags={x['questionId'] for x in r['reviews'] if x['decision']=='flagged'}
for q in b['questions']:
 if q['id'] not in flags:continue
 q['version']=2;q['status']='draft';q['reviewIds']=[]
 for c in q['citations']:
  if c['physicalPage']==16:
   c['locator']='Lecture1, physical PDF page16, printed slide16; center-lower Unimate sketch and its motion arrows.'
   c['evidenceText']='Unimate sketch labels: Rotary motion above the base-axis curved arrow; Radial motion beside the arm-axis double arrow; Vertical motion beside the side-axis curved arrow; Wrist bend; Wrist yaw; Wrist swivel. Caption: Sketch of a Unimate robot (Critchlow,1985).'
  if c['physicalPage']==21:
   c['locator']='Lecture1, physical PDF page21, printed slide21; PUMA560 sketch on left and parallel-platform sketch in center-right.'
   c['evidenceText']='Left: PUMA560 Serial Robot; Waist, Shoulder, Forearm, Three rotations at Wrist. Right: Top Platform, Spherical Joint, Prismatic Joint, U Joint, Extensible Leg, Fixed Base, Actuator Motion. Paired actuator-motion arrows run along the extensible legs; spherical joints connect legs at the top platform; U joints are marked at the base.'
 opts={x['id']:x for x in q['options']};ex=q['solution']['optionExplanations']
 if q['id'].endswith('P0021-Q05'):
  for oid,t,why in [('o2','Rotation around the extensible leg’s own long axis','The double arrow is axial translation, not rotation about that axis.'),('o3','Transverse motion perpendicular to the leg axis','The arrows align with the leg rather than pointing transversely.'),('o4','Rotation of the entire top platform about its normal','The highlighted arrow labels one leg actuator, not a prescribed whole-platform rotation.')]:opts[oid]['text']=t;ex[oid]=why
 if q['id'].endswith('P0027-Q03'):
  q['stem']='An unchanged rigid object is described in two reference frames; which statement correctly distinguishes the object from its coordinate description?'
  for oid,t,why in [('o2','Different coordinate values necessarily mean the object physically moved','A change of reference frame can change components without any physical motion.'),('o3','Keeping the object fixed guarantees identical position coordinates in all frames','Fixed physical position does not make components identical across translated or rotated frames.'),('o4','Changing the reference frame can change position components but never orientation components','Orientation descriptions also depend on the reference frame.')]:opts[oid]['text']=t;ex[oid]=why
 if q['id'].endswith('P0039-Q02'):
  for oid,t,why in [('o2','Some stepper-equipped manipulators need torque commands, while most other manipulators directly accept trajectories without effort calculation','This reverses the particular distinction stated in the introductory slide.'),('o3','For force/torque-driven manipulators, inverse kinematics alone supplies the required actuator effort','Inverse kinematics gives joint configurations; the slide requires an effort-computing algorithm involving dynamics and control.'),('o4','For force/torque-driven manipulators, computing nominal dynamics alone fully solves trajectory tracking','The source explicitly says dynamics is central but does not by itself constitute the control solution.')]:opts[oid]['text']=t;ex[oid]=why
 q['solution']['misconceptions']=[ex[x['id']] for x in q['options'] if x['id'] not in q['correctOptionIds']]
p.write_text(json.dumps(b,ensure_ascii=False,indent=2))
(R/'audits/blind-W01-L01-supplement-v2.json').write_text(json.dumps([{k:q[k] for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']} for q in b['questions'] if q['id'] in flags],ensure_ascii=False,indent=2))
print('Revised',len(flags),'items;11 approved question objects unchanged.')
