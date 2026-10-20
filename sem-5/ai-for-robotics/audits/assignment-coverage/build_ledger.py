#!/usr/bin/env python3
"""Non-mutating assignment coverage reconciliation. Manual observations are review evidence, not authored bank questions."""
import json,re,hashlib,datetime,pathlib,collections
R=pathlib.Path(__file__).resolve().parents[2]
OUT=R/'audits/assignment-coverage';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
BOUNDS=[(1,4),(5,7),(8,14),(15,18),(19,23),(24,28),(29,33),(34,38),(39,44),(45,49),(50,55),(56,59)]
source=R/'sources/raw/AI_for_Robotics_All_Assignment_Solutions.pdf'
manual=json.loads((OUT/'manual-observations.json').read_text())
bank=json.loads((R/'data/bank.json').read_text()); slides={s['id']:s for s in bank['slides']}
reviewed=set(manual['viewedPages'])
items=[]
for w,(a,b) in enumerate(BOUNDS,1):
 if w not in manual['completedWeeks']:continue
 text='';ranges=[]
 for p in range(a,b+1):
  t=(R/f'sources/text/assignments/page-{p:04}.txt').read_text()
  t=re.sub(r'(?m)^\s*\d+\s*\|\s*P a g e.*$','',t)
  t=re.sub(r'\*+\s*END\s*\*+','',t)
  ranges.append((len(text),len(text)+len(t),p));text+=t+'\n'
 starts=list(re.finditer(r'(?m)^\s*(?:Q\.\s*\d+|Que\b|(?:[1-9]|10)\.(?!\d)|10(?=\s+[A-Z]))',text))
 assert len(starts)==10,(w,len(starts))
 for i,m in enumerate(starts,1):
  end=starts[i].start() if i<len(starts) else len(text)
  raw=text[m.start():end].strip();pages=[p for x,y,p in ranges if max(x,m.start())<min(y,end) and text[x:y].strip()]
  # Number in the left cell can be extracted on a separate line after the prompt begins.
  cleaned=re.sub(r'^(?:Q\.\s*\d+|(?:[1-9]|10)\.(?!\d)|10(?=\s+[A-Z]))\s*','',raw)
  if cleaned.startswith('Que'):
   cleaned=re.sub(r'^Que\s*','',cleaned);cleaned=re.sub(r'(?m)^\s*'+str(i)+r'\s+','',cleaned,count=1)
  answer=re.search(r'(?i)(?:Answer|Explanation):\s*\(?([A-D]\b|[-+]?\d+(?:\.\d+)?)',cleaned)
  cut=re.search(r'(?im)^\s*(?:Answer\b|Explanation:|First calculate the SVM)',cleaned)
  body=cleaned[:cut.start()] if cut else cleaned
  opts=list(re.finditer(r'(?m)^\s*\(?([A-D])\)\s*',body))
  prompt=body[:opts[0].start()].strip() if opts else body.strip()
  options=[{'sourceLabel':z.group(1),'text':body[z.end():opts[j+1].start() if j+1<len(opts) else len(body)].strip()} for j,z in enumerate(opts)]
  key=f'ASSIGN-W{w:02}-Q{i:02}'
  obs=manual['items'][key]
  citation_ids=[f'assignments-p{p:04}' for p in pages]
  linked=[q for q in bank['questions'] if any(c.get('sourceId')=='assignments' and c.get('physicalPage') in pages for c in q.get('citations',[]))]
  concepts=[c['id'] for c in bank['concepts'] if any(s in citation_ids for s in c.get('slideIds',[]))]
  lecture_refs=[]
  for lid,pn in obs.get('lectureReferences',[]):
   matches=[s for s in bank['slides'] if s.get('lectureId')==lid and str(s.get('printedSlideNumber'))==str(pn)]
   lecture_refs.append({'lectureId':lid,'printedSlideNumber':str(pn),'candidatePhysicalPages':[s['physicalPage'] for s in matches],'basis':'Assignment printed reference; map resolution only, not a fresh lecture-source adjudication.'})
  item={'id':key,'week':w,'sourceId':'assignments','sourceSha256':sha(source),'physicalPages':pages,'printedItemNumber':str(i),'printedPageNumbers':[slides[s].get('printedSlideNumber') for s in citation_ids], 'originalPrompt':prompt,'originalOptions':options,'originalPrintedKey':answer.group(1) if answer else obs['observedHighlightedKey'],'printedKeyEvidence':'answer_line' if answer else 'visually_observed_highlight','originalSourceText':raw,'transcriptionStatus':'Text-layer locator checked against actual page pixels; Unicode layout can differ. Figure/matrix transcriptions supplied separately where needed. Source PDF remains authoritative.', 'sourcePreviewPaths':[f'sources/previews/assignments/page-{p:04}.webp' for p in pages], 'visualInspection':{'reviewerId':'robotics-contracts-assignment-coverage-reviewer','method':'actual_rendered_page','complete':all(p in reviewed for p in pages),'answersVisible':True,'blind':False}, 'coverageStatus':'missing_assignment_cited_questions','currentAssignmentCitedQuestionIds':[q['id'] for q in linked],'currentAssignmentConceptIds':concepts,'currentAssignmentReviewIds':[v['id'] for v in bank['reviews'] if v.get('questionId') in {q['id'] for q in linked}], 'lectureCrossLinks':lecture_refs,**obs}
  if not options:
   item['originalPrompt']=re.sub(r'\s*\n\s*'+re.escape(str(obs['observedHighlightedKey']))+r'\s*$','',item['originalPrompt'])
  if key=='ASSIGN-W03-Q09':
   item['originalPrompt']='For the manipulator shown below, the mass matrix, M(Theta) is given by'
   item['originalOptions']=[{'sourceLabel':k,'text':str(v),'notationDefinitions':obs['visuallyTranscribedMatrixOptions']['symbols']} for k,v in obs['visuallyTranscribedMatrixOptions'].items() if k!='symbols']
  for fld in ['visuallyTranscribedGaussianOptions','visuallyTranscribedEKFOptions']:
   if fld in obs:item['originalOptions']=[{'sourceLabel':k,'text':json.dumps(v,ensure_ascii=False)} for k,v in obs[fld].items()]
  item['originalPrompt']=re.sub(r'^10\s+','',item['originalPrompt'])
  items.append(item)
all_assignment_q=[q for q in bank['questions'] if any(c.get('sourceId')=='assignments' for c in q.get('citations',[]))]
batches=[]
for p in (R/'data/question-batches').glob('*.json'):
 d=json.loads(p.read_text());qs=d.get('questions',[]) if isinstance(d,dict) else d
 for q in qs:
  if isinstance(q,dict) and any(c.get('sourceId')=='assignments' for c in q.get('citations',[])):batches.append({'path':str(p.relative_to(R)),'questionId':q['id']})
page_ledger=[]
for s in bank['slides']:
 if s.get('sourceId')!='assignments':continue
 p=s['physicalPage']; page_ledger.append({'physicalPage':p,'week':s.get('week'),'printedPageNumber':s.get('printedSlideNumber'),'sourceSha256':s['sourceSha256'],'previewSha256':sha(R/s['previewPath']),'priorVisualInspection':s.get('visualInspection'),'freshVisualInspectionComplete':p in reviewed,'bankDisposition':s.get('disposition'),'bankConceptIds':s.get('conceptIds',[]),'sourceItemIds':[x['id'] for x in items if p in x['physicalPages']],'directQuestionIds':[q['id'] for q in all_assignment_q if any(c.get('physicalPage')==p and c.get('sourceId')=='assignments' for c in q.get('citations',[]))],'gapDisposition':'open: author explicit assignment-derived or assignment-linked coverage, resolve conflicts, then independent review'})
ledger={'auditVersion':'1.0.0','auditedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewerId':'robotics-contracts-assignment-coverage-reviewer','sourcePath':str(source.relative_to(R)),'sourceSha256':sha(source),'sourcePageCount':59,'bankSnapshotSha256':sha(R/'data/bank.json'),'bankQuestionCount':len(bank['questions']),'bankAssignmentCitedQuestionCount':len(all_assignment_q),'batchAssignmentCitedQuestions':batches,'completedWeeks':manual['completedWeeks'],'freshViewedPages':sorted(reviewed),'scopeComplete':len(reviewed)==59 and len(items)==120,'assignmentCoverageComplete':False,'reviewBoundary':'Source keys were visible; this is a nonblind independent source-key/coverage challenge, not acceptance of generated questions. Existing accepted lecture questions and their reviews were not changed. Lecture candidate overlap is not assignment citation coverage.','restrictions':manual['restrictions'],'pages':page_ledger,'items':items,'existingDisputeLedger':'audits/assignment_disputes.json'}
write(OUT/'coverage-ledger.json',ledger)
for first,last in [(1,6),(7,12)]:
 subset=[i for i in items if first<=i['week']<=last]
 if subset and not (OUT/f'author-handoff-weeks-{first:02}-{last:02}-v2.json').exists():write(OUT/f'author-handoff-weeks-{first:02}-{last:02}-v2.json',{k:v for k,v in ledger.items() if k not in ('items','pages')}|{'items':subset,'pages':[p for p in page_ledger if first<=p['week']<=last]})
print(json.dumps({'items':len(items),'viewed':len(reviewed),'assignmentQuestions':len(all_assignment_q),'batchAssignmentQuestions':len(batches),'ledgerSha256':sha(OUT/'coverage-ledger.json')}))
