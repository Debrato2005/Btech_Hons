#!/usr/bin/env python3
"""Integrate only actually viewed L34 page pixels; retain all unseen pages as pending."""
import json,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];A='L34-author-20261019';P=R/'data/inspection-batches/W07-L34.json'
if (R/'audits/W07-L34-review-manifest.json').exists():
 raise SystemExit('L34 is frozen; use a versioned repair rather than reinitializing inspected metadata.')
notes=json.loads((R/'audits/L34-visual-observations.json').read_text());base=json.loads((R/'data/bank.json').read_text());prior=json.loads(P.read_text()) if P.exists() else {}
known={x['physicalPage']:x for x in prior.get('slides',[])};slides=[]
for p in range(1021,1060):
 s=copy.deepcopy(known.get(p) or next(s for s in base['slides'] if s['sourceId']=='lectures' and s['physicalPage']==p))
 s.update(week=7,lectureId='L34',lectureTitle='Fundamentals of Neural Networks',lectureRelativePage=p-1020)
 if str(p) in notes:
  n=notes[str(p)];s.update(title=n['title'],printedSlideNumber=str(n['printed']) if n['printed'] is not None else None,printedSlideNumberStatus='present' if n['printed'] is not None else 'absent',disposition='excluded' if n.get('excluded') else 'examinable',exclusionReason=n.get('excluded'),incrementalChangesChecked=True)
  s['visualInspection']=dict(status='complete',inspectorId=A,inspectedAt=n['inspectedAt'],method='rendered_page',notes=n['notes'])
 slides.append(s)
P.write_text(json.dumps(dict(batchId='W07-L34',authorId=A,sourceSha256=slides[0]['sourceSha256'],slides=slides,sourceIssues=prior.get('sourceIssues',[]),summary=dict(visuallyInspectedPages=len(notes),questions=prior.get('summary',{}).get('questions',0),concepts=prior.get('summary',{}).get('concepts',0),draftOnly=True,authorComplete=False)),ensure_ascii=False,indent=2)+'\n')
print('SAVED',len(notes),'actual inspections')
