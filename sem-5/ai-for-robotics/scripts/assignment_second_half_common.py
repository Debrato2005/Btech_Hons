"""Author-owned assignment batch support. Never rewrites frozen packets or originals."""
from pathlib import Path
import json, hashlib, copy, datetime, random
ROOT=Path(__file__).resolve().parents[1]
AUTHOR='complete_robotics_python_coverage:assignments-W07-W12-author'
SOURCE='b0450429866ac8017d7971932acf8812adf41df9dff4eb10bc8c87015b41c1b5'
HANDOFF='audits/assignment-coverage/author-handoff-weeks-07-12-v2.json'
H= json.loads((ROOT/HANDOFF).read_text())
ITEMS={q['id']:q for q in H['items']}
PRESERVATION_OVERRIDES={}
NOW=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(path,data):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ('status','reviewIds')},ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def F(expr,defs,assumptions=()):
 return {'expression':expr,'variables':{k:v[0] for k,v in defs.items()},'units':{k:v[1] for k,v in defs.items()},'assumptions':list(assumptions)}
def C(page,locator,evidence,kind='statement',role='premise'):
 return dict(slideId=f'assignments-p{page:04}',sourceId='assignments',sourceSha256=SOURCE,physicalPage=page,kind=kind,locator=f'Assignment physical page {page}: {locator}',evidenceText=evidence,role=role,region=None)
def preserve(week,relations):
 for item in [i for i in ITEMS.values() if i['week']==week]:
  record=copy.deepcopy(item)
  if item['id'] in PRESERVATION_OVERRIDES:
   record['authorTranscriptionCorrections']=[{'field':k,'frozenHandoffValue':copy.deepcopy(item.get(k)),'pixelCheckedValue':copy.deepcopy(v),'reason':'Author actual-page inspection resolves extraction or key-transcription artifact; source PDF and frozen handoff remain unchanged.','authorId':AUTHOR,'inspectedAt':PRESERVATION_OVERRIDES[item['id']].get('_inspectedAt')}for k,v in PRESERVATION_OVERRIDES[item['id']].items()if not k.startswith('_')]
   record.update({k:copy.deepcopy(v)for k,v in PRESERVATION_OVERRIDES[item['id']].items()if not k.startswith('_')})
  record.update(recordPurpose='Immutable original prompt, source-labelled options, visible key, source text and original audit. Not an approved question.',sourceHandoffPath=HANDOFF,sourceHandoffSha256=sha(HANDOFF),originalSourceItemId=item['id'],relatedQuestionIds=relations[item['id']],literalOriginalDisposition='quarantined_original' if item['independentSourceKeyAuditStatus']=='conflicting_or_underspecified_quarantine' else 'source_record_only_not_in_question_pool')
  p=f"audits/assignment-originals/{item['id']}.json"
  if (ROOT/p).exists():
   assert json.loads((ROOT/p).read_text())==record, f'Immutable original changed: {p}'
  else:dump(p,record)
def Q(week,num,item,title,stem,choices,rationales,citations,why,*,assumptions=(),steps=(),formulas=(),difficulty='easy',qtype='conceptual',key=1,conflict=None,angles=('concept','assumption_or_misconception')):
 qid=f'ASSIGN-W{week:02}-Q{num:03}';iid=f'ASSIGN-W{week:02}-Q{item:02}'
 opts=[{'id':f'o{i+1}','text':t} for i,t in enumerate(choices)]
 random.Random(qid).shuffle(opts)
 q=dict(id=qid,version=1,status='draft',authorId=AUTHOR,stem=stem,selectionMode='single',type=qtype,difficulty=difficulty,cognitiveSkill='numerical' if qtype=='numerical' else 'algorithm' if qtype=='algorithm_trace' else 'synthesis' if qtype=='synthesis' else 'conceptual',week=week,lectureId=None,topic=f'Assignment Week {week}',subtopic=title,tags=['assignment',f'week-{week}'],conceptIds=[f'ASSIGN-W{week:02}-C{item:03}'],assumptions=list(assumptions),options=opts,correctOptionIds=[f'o{key}'],citations=citations,solution=dict(justification=why,optionExplanations={f'o{i+1}':r for i,r in enumerate(rationales)},steps=list(steps),formulas=list(formulas),simpleExplanation=why,memoryAid=None,misconceptions=[r for i,r in enumerate(rationales) if i+1!=key],examTraps=[],prerequisiteConceptIds=[]),origin='assignment_adapted',reviewIds=[],assignmentSourceItemId=iid,originalRecordPath=f'audits/assignment-originals/{iid}.json',originalRecordSha256=None,difficultyRationale='Requires combining multiple operations or assumptions.' if difficulty=='medium' else 'A direct distinction or short calculation under stated assumptions.',testedAssignmentAngles=list(angles))
 if len(opts)<4:q['optionCountRationale']='Three technically plausible, distinct alternatives cover the targeted misconception without adding filler.'
 if conflict:q['conflictResolution']={**conflict,'status':'qualification_pending_independent_review','questionVersion':1,'sourceId':'assignments','sourceSha256':SOURCE,'physicalPage':citations[0]['physicalPage'],'sourceClaim':conflict['issue'],'basis':conflict['resolution']}
 return q

def save_week(week,questions,notes):
 assert not (ROOT/f'audits/blind-ASSIGN-W{week:02}.json').exists(),'Frozen batch: use versioned repair, never rerun.'
 relations={i['id']:[q['id'] for q in questions if q['assignmentSourceItemId']==i['id']] for i in ITEMS.values() if i['week']==week}
 assert all(relations.values());preserve(week,relations)
 for q in questions:
  q['originalRecordSha256']=sha(q['originalRecordPath'])
  related=[z for z in relations[q['assignmentSourceItemId']] if z!=q['id']]
  if related:q['relatedQuestionIds']=related
 concepts=[]
 for iid,ids in relations.items():
  qs=[q for q in questions if q['id'] in ids];item=ITEMS[iid]
  concepts.append(dict(id=f'ASSIGN-W{week:02}-C{int(item["printedItemNumber"]):03}',title=qs[0]['subtopic'],description=qs[0]['solution']['justification'],slideIds=sorted(set(c['slideId'] for q in qs for c in q['citations'])),questionIds=ids,status='drafted',topic=f'Assignment Week {week}',subtopic=qs[0]['subtopic'],prerequisiteConceptIds=[],examinationAngles=sorted(set(a for q in qs for a in q['testedAssignmentAngles'])),coverageNotes='Original source item preserved separately. Adaptations require independent review; existing source-key audit is nonblind and does not approve generated content.'))
 dump(f'data/question-batches/ASSIGN-W{week:02}.json',dict(schemaVersion='1.0.0',batchId=f'ASSIGN-W{week:02}',authorId=AUTHOR,questions=questions,concepts=concepts,coverageNote='All ten original items represented; immutable originals remain outside the approved pool. Meaningful assumptions and calculation angles are explicitly stated.'))
 bank=json.loads((ROOT/'data/bank.json').read_text());slides={s['id']:s for s in bank['slides']};out=[]
 for p,footer,note in notes:
  s=copy.deepcopy(slides[f'assignments-p{p:04}']);s.update(week=week,lectureId=None,lectureTitle=None,printedSlideNumber=str(footer) if footer is not None else None,printedSlideNumberStatus='present' if footer is not None else 'absent',disposition='examinable',exclusionReason=None,conceptIds=[c['id'] for c in concepts if s['id'] in c['slideIds']],visualInspection=dict(status='complete',inspectorId=AUTHOR,inspectedAt=NOW(),method='rendered_page',notes=note+' Source answers were visible; this is author inspection, not blind independent review.'))
  out.append(s)
 dump(f'data/inspection-batches/ASSIGN-W{week:02}-author.json',dict(schemaVersion='1.0.0',batchId=f'ASSIGN-W{week:02}-author',inspectorId=AUTHOR,slides=out))
 dump(f'audits/assignment-coverage/W{week:02}-author-coverage.json',dict(authorId=AUTHOR,createdAt=NOW(),sourceSha256=SOURCE,originalHandoffSha256=sha(HANDOFF),items=[dict(sourceItemId=iid,originalDisposition=json.loads((ROOT/f'audits/assignment-originals/{iid}.json').read_text())['literalOriginalDisposition'],questionIds=ids,reviewStatus='draft_pending_independent_review') for iid,ids in relations.items()],pages=[dict(physicalPage=p,printedFooter=str(f) if f is not None else None,notes=n) for p,f,n in notes]))
 print(f'Week {week}: {len(questions)} drafts, {len(concepts)} original-item concepts, {len(notes)} actual pages saved.')
