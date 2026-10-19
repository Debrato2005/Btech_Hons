#!/usr/bin/env python3
"""Integrate only actually viewed L19 page pixels; retain all unseen pages as pending."""
import json,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];A='L19-author-20261019';P=R/'data/inspection-batches/W04-L19.json'
notes=json.loads((R/'audits/L19-visual-observations.json').read_text());base=json.loads((R/'data/bank.json').read_text());prior=json.loads(P.read_text()) if P.exists() else {}
known={x['physicalPage']:x for x in prior.get('slides',[])};slides=[]
for p in range(578,606):
 s=copy.deepcopy(known.get(p) or next(s for s in base['slides'] if s['sourceId']=='lectures' and s['physicalPage']==p))
 s.update(week=4,lectureId='L19',lectureTitle='Manipulator–Mechanism Design-II',lectureRelativePage=p-577)
 if str(p) in notes:
  n=notes[str(p)];s.update(title=n['title'],printedSlideNumber=n['printed'],printedSlideNumberStatus='present',disposition='excluded' if n.get('excluded') else 'examinable',exclusionReason=n.get('excluded'),incrementalChangesChecked=True)
  s['visualInspection']=dict(status='complete',inspectorId=A,inspectedAt=n['inspectedAt'],method='rendered_page',notes=n['notes'])
 slides.append(s)
P.write_text(json.dumps(dict(batchId='W04-L19',authorId=A,sourceSha256=slides[0]['sourceSha256'],slides=slides,sourceIssues=prior.get('sourceIssues',[]),summary=dict(visuallyInspectedPages=len(notes),questions=prior.get('summary',{}).get('questions',0),concepts=prior.get('summary',{}).get('concepts',0),draftOnly=True,authorComplete=False)),ensure_ascii=False,indent=2)+'\n')
print('SAVED',len(notes),'actual inspections')
