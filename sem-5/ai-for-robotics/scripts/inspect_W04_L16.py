#!/usr/bin/env python3
"""Persist actual L16 visual observations; text extraction alone never counts."""
import json,copy,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];AUTHOR='L16-author-20261019'
notes=json.loads((ROOT/'audits/L16-visual-observations.json').read_text())
base=json.loads((ROOT/'data/bank.json').read_text())
prior=ROOT/'data/inspection-batches/W04-L16.json'
records={x['physicalPage']:x for x in json.loads(prior.read_text())['slides']} if prior.exists() else {}
slides=[]
for p in range(473,505):
 s=copy.deepcopy(records.get(p) or next(x for x in base['slides'] if x['sourceId']=='lectures' and x['physicalPage']==p))
 s.update({'week':4,'lectureId':'L16','lectureTitle':'Joint-Space Schemes','lectureRelativePage':p-472})
 if str(p) in notes:
  n=notes[str(p)];s.update({'title':n['title'],'printedSlideNumber':n['printed'],'printedSlideNumberStatus':'present','text':(ROOT/f'sources/text/lectures/page-{p:04d}.txt').read_text(),'disposition':'excluded' if n.get('excluded') else 'examinable','exclusionReason':n.get('excluded'),'repeatsSlideIds':[],'incrementalChangesChecked':True})
  s['visualInspection']={'status':'complete','inspectorId':AUTHOR,'inspectedAt':n['inspectedAt'],'method':'rendered_page','notes':n['notes']}
 slides.append(s)
packet={'batchId':'W04-L16','authorId':AUTHOR,'sourceSha256':slides[0]['sourceSha256'],'slides':slides,'sourceIssues':[],'summary':{'visuallyInspectedPages':len(notes),'questions':0,'concepts':0,'draftOnly':True,'authorComplete':False}}
prior.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
print('SAVED',len(notes),'actual inspections')
