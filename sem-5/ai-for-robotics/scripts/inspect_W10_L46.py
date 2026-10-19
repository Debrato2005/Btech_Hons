#!/usr/bin/env python3
"""Persist only actual L46 rendered-page observations supplied in the local ledger."""
import json,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];B='W10-L46';A='L46-author-20261019'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
notes=read('audits/L46-page-observations.json');bpath=R/f'data/question-batches/{B}.json';b=read(f'data/question-batches/{B}.json')if bpath.exists()else{'schemaVersion':'1.0.0','batchId':B,'authorId':A,'questions':[],'concepts':[],'coverageNote':'Work in progress, authoring and actual inspection incomplete.'}
existing={s['id']:s for s in read(f'data/inspection-batches/{B}.json')['slides']}if (R/f'data/inspection-batches/{B}.json').exists()else{}
base={s['physicalPage']:copy.deepcopy(s)for s in read('data/bank.json')['slides']if s['sourceId']=='lectures'and 1440<=s['physicalPage']<=1475}
cm={c['id']:c for c in b['concepts']}
for p,ob in notes.items():
 p=int(p);s=existing.get(f'lectures-p{p}',base[p]);s.update(printedSlideNumber=ob['footer'],printedSlideNumberStatus='present'if ob['footer']is not None else'absent',disposition=ob['disposition'],exclusionReason=ob.get('exclusionReason'),incrementalChangesChecked=ob.get('incrementalChangesChecked',False),repeatsSlideIds=ob.get('repeatsSlideIds',[]),visualInspection=dict(status='complete',inspectorId=A,inspectedAt=ob['inspectedAt'],method='rendered_page',notes=ob['notes']))
 s['printedNumberEvidence']='Actual bottom-right rendered footer viewed; footer recorded separately from physical page.'
 for tag,c in ob.get('concepts',{}).items():
  cid=f'{B}-C-{tag}'
  if cid not in cm:cm[cid]=dict(id=cid,title=c['title'],description=c['description'],slideIds=[],questionIds=[],status='identified',topic='Natural Language Processing',subtopic=c['title'],prerequisiteConceptIds=[],examinationAngles=[])
  cc=cm[cid];cc['slideIds']=sorted(set(cc['slideIds']+[s['id']]));cc['examinationAngles']=list(dict.fromkeys(cc['examinationAngles']+c['angles']));s['conceptIds']=sorted(set(s.get('conceptIds',[])+[cid]))
 existing[s['id']]=s
b['concepts']=list(cm.values());write(f'data/question-batches/{B}.json',b);write(f'data/inspection-batches/{B}.json',{'batchId':B,'slides':sorted(existing.values(),key=lambda s:s['physicalPage'])})
print('Actual inspections',len(existing),'concept families',len(cm),'questions',len(b['questions']))
