#!/usr/bin/env python3
import json,sys,copy
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];OUT=R/'data/inspection-batches/W08-L36-COVERAGE-GAP.json';OBS=R/'audits/L36-completeness-observations.json'
def save(entries):
 bank=json.loads((R/'data/bank.json').read_text());base={s['physicalPage']:s for s in bank['slides'] if s.get('lectureId')=='L36'}
 old=json.loads(OUT.read_text()) if OUT.exists() else dict(batchId='W08-L36-COVERAGE-GAP',authorId='L36-gap-author-20261019',sourceSha256=base[1088]['sourceSha256'],slides=[],sourceIssues=[],summary={})
 sm={s['physicalPage']:s for s in old['slides']};notes=json.loads(OBS.read_text()) if OBS.exists() else {}
 for p,footer,disposition,note,reason in entries:
  s=copy.deepcopy(base[p]);s.update(printedSlideNumber=str(footer),printedSlideNumberStatus='present',disposition=disposition,exclusionReason=reason,visualInspection=dict(status='complete',inspectorId='L36-gap-author-20261019',inspectedAt=datetime.now(timezone.utc).isoformat(),method='rendered_page',notes=note))
  sm[p]=s;notes[str(p)]=dict(printedFooter=str(footer),actualPixelsViewed=True,notes=note,disposition=disposition,exclusionReason=reason)
 old['slides']=[sm[p] for p in sorted(sm)];old['summary']=dict(actualPagesInspected=len(sm),expectedPages=39,scope='Author completeness audit, not independent verification; all existing approved questions remain untouched.')
 OUT.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n');OBS.write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
 print('Actual L36 inspections saved:',len(sm))
if __name__=='__main__':save(json.load(sys.stdin))
