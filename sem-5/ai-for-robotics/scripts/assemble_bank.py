#!/usr/bin/env python3
"""Assemble honest partial snapshots; never infer review or inspection completion."""
from pathlib import Path
import argparse,json,datetime,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--version');a=ap.parse_args()
 manifest=read(ROOT/'sources/manifest.json');slides=[]
 for p in sorted((ROOT/'sources/page_maps').glob('*.jsonl')):
  slides.extend(json.loads(l) for l in p.read_text().splitlines() if l.strip())
 byslide={s['id']:s for s in slides}
 for s in slides:
  t=ROOT/s.get('localTextPath','MISSING')
  if t.is_file():s['text']=t.read_text(encoding='utf-8')
 for p in sorted((ROOT/'data/inspection-batches').glob('*.json')):
  payload=read(p);records=payload if isinstance(payload,list) else payload.get('slides',payload.get('inspections',[]))
  for rec in records:
   sid=rec.get('id',rec.get('slideId'))
   if sid not in byslide:raise ValueError(f'Unknown slide in {p}: {sid}')
   if rec.get('sourceSha256') != byslide[sid]['sourceSha256']:raise ValueError(f'Stale inspection {sid}')
   for k,v in rec.items():
    if k not in ('id','slideId','sourceSha256','conceptIds'):byslide[sid][k]=v
 for p in sorted((ROOT/'audits').glob('*page-observations.jsonl')):
  for line in p.read_text().splitlines():
   if not line.strip():continue
   rec=json.loads(line);sid=rec.get('slideId')
   if sid not in byslide or rec.get('sourceSha256')!=byslide[sid]['sourceSha256']:continue
   slide=byslide[sid]
   if slide['visualInspection']['status']!='complete':
    slide['visualInspection']={'status':'complete','inspectorId':rec['inspectorId'],'inspectedAt':rec['inspectedAt'],'method':rec['method'],'notes':rec.get('notes','')}
   for k in ('disposition','exclusionReason','printedSlideNumber','printedSlideNumberStatus'):
    if k in rec:slide[k]=rec[k]
 questions=[];concepts=[];reviews=[]
 for p in sorted((ROOT/'data/question-batches').glob('*.json')):
  b=read(p);questions.extend(b.get('questions',[]));concepts.extend(b.get('concepts',[]))
 for p in sorted(list((ROOT/'audits/review-batches').glob('*.json'))+list((ROOT/'data/reviews').glob('*.json'))):
  b=read(p);reviews.extend(b if isinstance(b,list) else b.get('reviews',[]))
 for name,records in [('questions',questions),('concepts',concepts),('reviews',reviews)]:
  ids=[x['id'] for x in records]
  if len(ids)!=len(set(ids)):raise ValueError(f'Duplicate {name} IDs')
 for s in slides:s['conceptIds']=[]
 for c in concepts:
  for sid in c['slideIds']:
   byslide[sid]['conceptIds'].append(c['id'])
   if byslide[sid]['disposition']=='unreviewed' and byslide[sid]['visualInspection']['status']=='complete':byslide[sid]['disposition']='examinable'
 # Authors save visual inspection before complete concept records; snapshots must
 # not imply finished examinable coverage merely because pixels were viewed.
 for slide in slides:
  if slide['disposition']=='examinable' and not slide['conceptIds']:
   slide['disposition']='unreviewed';slide['conceptLedgerPending']=True
 from review_gate import apply_review_gate
 quarantined=apply_review_gate(questions,reviews,slides,manifest['sources'])
 qmap={q['id']:q for q in questions}
 for c in concepts:
  if any(qmap[qid]['status']=='verified' for qid in c['questionIds']):c['status']='verified'
  elif c['status']=='verified':c['status']='drafted' if c['questionIds'] else 'identified'
 dump(ROOT/'audits/assembly-gate.json',{'quarantined':quarantined,'note':'Metadata eligibility gate only; not a substitute for independent source review or full validation.'})
 tools={k:[] for k in ('formulaSheet','confusionPairs','traps','algorithmVisualizations','numericalFamilies')}
 for p in sorted((ROOT/'data').glob('learning-tools*.json')):
  d=read(p);d=d.get('learningTools',d)
  for k in tools:tools[k].extend(d.get(k,[]))
 bank={'schemaVersion':'1.0.0','bankVersion':a.version or datetime.datetime.now(datetime.timezone.utc).strftime('0.1.%Y%m%dT%H%M%SZ'),'title':'Semester 5 · AI for Robotics','complete':False,'sources':manifest['sources'],'slides':slides,'concepts':concepts,'questions':questions,'reviews':reviews,'assets':manifest['assets'],'learningTools':tools,'notes':['Work in progress: unreviewed pages and draft questions are not complete or validated coverage.','Only independent source-bound verified questions enter normal study and exams.']}
 challenge=ROOT/'audits/coverage_challenge.json'
 if challenge.exists():bank['coverageChallenge']=read(challenge)
 dump(ROOT/'data/bank.json',bank)
 counts={'sourcePages':len(slides),'visuallyInspectedPages':sum(s['visualInspection']['status']=='complete' for s in slides),'excludedPages':sum(s['disposition']=='excluded' for s in slides),'conceptRecords':len(concepts),'draftQuestions':sum(q['status']=='draft' for q in questions),'verifiedQuestions':sum(q['status']=='verified' for q in questions),'flaggedQuestions':sum(q['status']=='flagged' for q in questions),'reviews':len(reviews)}
 dump(ROOT/'data/progress-summary.json',{'bankVersion':bank['bankVersion'],'complete':False,'counts':counts})
 print(json.dumps(counts))
if __name__=='__main__':main()
