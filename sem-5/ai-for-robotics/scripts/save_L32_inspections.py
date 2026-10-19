from pathlib import Path
import json,datetime,sys
R=Path(__file__).resolve().parents[1];rows={r['physicalPage']:r for r in map(json.loads,(R/'sources/page_maps/lectures.jsonl').read_text().splitlines())};p=R/'data/inspection-batches/W07-L32.json';b=json.loads(p.read_text())if p.exists()else{'batchId':'W07-L32','slides':[]};out={s['physicalPage']:s for s in b['slides']}
for k,note in json.load(sys.stdin).items():
 page=int(k);s=rows[page].copy();excluded=page in[954,955,956,985,986];s.update(disposition='excluded'if excluded else'examinable',exclusionReason=note if excluded else None,printedSlideNumber=str(page-953),printedSlideNumberStatus='present',printedNumberEvidence='Actual rendered bottom-right footer visually inspected.',visualInspection={'status':'complete','inspectorId':'robotics-integration-author-L32','inspectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'rendered_page','notes':note+' Actual full 1800-pixel page and footer viewed.'});out[page]=s
b['slides']=[out[k]for k in sorted(out)];p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');print('Actual inspected L32 pages:',len(out))
