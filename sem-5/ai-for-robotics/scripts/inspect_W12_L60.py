#!/usr/bin/env python3
"""Persist only actual page observations; extraction is never inspection."""
from pathlib import Path
import json,copy
R=Path(__file__).resolve().parents[1];B='W12-L60'
assert not(R/f'audits/{B}-review-manifest.json').exists(),'Frozen inspection batch'
obs=json.loads((R/'audits/L60-page-observations.json').read_text());bank=json.loads((R/'data/bank.json').read_text());base={s['physicalPage']:s for s in bank['slides']if s['sourceId']=='lectures'};slides=[]
for n,o in sorted(obs.items(),key=lambda x:int(x[0])):
 p=int(n);s=copy.deepcopy(base[p]);s.update(printedSlideNumber=str(o['footer']),printedSlideNumberStatus='present',disposition=o.get('disposition','examinable'),exclusionReason=o.get('exclusionReason'),repeatsSlideIds=o.get('repeatsSlideIds',[]),incrementalChangesChecked=bool(o.get('repeatsSlideIds')),conceptIds=[B+'-C-'+c for c in o.get('concepts',[])],visualInspection=dict(status='complete',inspectorId='L60-author-20261020',inspectedAt=o['inspectedAt'],method='rendered_page',notes=o['notes']))
 slides.append(s)
(R/f'data/inspection-batches/{B}.json').write_text(json.dumps({'schemaVersion':'1.0.0','batchId':B,'inspectorId':'L60-author-20261020','slides':slides},indent=2,ensure_ascii=False)+'\n');print('Persisted actual pages',len(slides))
