#!/usr/bin/env python3
"""Integrate only actually viewed L24 page pixels; retain all unseen pages as pending."""
import json,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];A='L24-author-20261019';P=R/'data/inspection-batches/W05-L24.json'
if (R/'audits/W05-L24-review-manifest.json').exists():
 raise SystemExit('L24 is frozen; use a versioned repair rather than reinitializing inspected metadata.')
notes=json.loads((R/'audits/L24-visual-observations.json').read_text());base=json.loads((R/'data/bank.json').read_text());prior=json.loads(P.read_text()) if P.exists() else {}
known={x['physicalPage']:x for x in prior.get('slides',[])};slides=[]
for p in range(727,751):
 s=copy.deepcopy(known.get(p) or next(s for s in base['slides'] if s['sourceId']=='lectures' and s['physicalPage']==p))
 s.update(week=5,lectureId='L24',lectureTitle='The Control Problem for Manipulators',lectureRelativePage=p-726)
 if str(p) in notes:
  n=notes[str(p)];s.update(title=n['title'],printedSlideNumber=n['printed'],printedSlideNumberStatus='present' if n['printed'] is not None else 'absent',disposition='excluded' if n.get('excluded') else 'examinable',exclusionReason=n.get('excluded'),incrementalChangesChecked=True)
  s['visualInspection']=dict(status='complete',inspectorId=A,inspectedAt=n['inspectedAt'],method='rendered_page',notes=n['notes'])
 slides.append(s)
P.write_text(json.dumps(dict(batchId='W05-L24',authorId=A,sourceSha256=slides[0]['sourceSha256'],slides=slides,sourceIssues=prior.get('sourceIssues',[]),summary=dict(visuallyInspectedPages=len(notes),questions=prior.get('summary',{}).get('questions',0),concepts=prior.get('summary',{}).get('concepts',0),draftOnly=True,authorComplete=False)),ensure_ascii=False,indent=2)+'\n')
print('SAVED',len(notes),'actual inspections')
