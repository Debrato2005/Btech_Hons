"""Small serialization helper for hand-authored, source-bound draft questions."""
from pathlib import Path
import copy,json
R=Path(__file__).resolve().parents[1]
SHA='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'
def formula(expression,variables,units,assumptions=None):return dict(expression=expression,variables=variables,units=units,assumptions=assumptions or [])
class DraftBatch:
 def __init__(self,batch,week,lecture,topic,first_page,author):
  self.batch=batch;self.week=week;self.lecture=lecture;self.topic=topic;self.first=first_page;self.author=author;self.questions=[];self.concepts={}
 def add(self,pages,key,title,stem,options,correct,why,explanations,typ='conceptual',difficulty='medium',assumptions=None,steps=None,formulas=None,conflict=None,memory=None,traps=None):
  if isinstance(pages,int):pages=[pages]
  if isinstance(correct,int):correct=[correct]
  assert len(options)==len(explanations)==4 and len(set(options))==4
  qid=f'{self.batch}-Q{len(self.questions)+1:03d}';cid=f'{self.batch}-C-{key}';ids=[f'o{i+1}' for i in range(4)]
  c=self.concepts.setdefault(cid,dict(id=cid,title=title,description=why,slideIds=[],questionIds=[],status='drafted',topic=self.topic,subtopic=title,prerequisiteConceptIds=[],examinationAngles=[]))
  c['questionIds'].append(qid)
  if typ not in c['examinationAngles']:c['examinationAngles'].append(typ)
  for p in pages:
   sid=f'lectures-p{p:04d}'
   if sid not in c['slideIds']:c['slideIds'].append(sid)
  opts=[{'id':ids[i],'text':v} for i,v in enumerate(options)];shift=len(self.questions)%4;opts=opts[shift:]+opts[:shift]
  citations=[dict(slideId=f'lectures-p{p:04d}',sourceId='lectures',sourceSha256=SHA,physicalPage=p,kind='figure' if typ=='diagram' else 'equation' if typ in ('numerical','derivation') else 'statement',locator=f'Lecture {int(self.lecture[1:])}, physical PDF page {p}, printed slide {p-self.first+1}: relevant text, equations and associated figures',evidenceText=(R/f'sources/text/lectures/page-{p:04d}.txt').read_text().strip(),role='conflict' if conflict else 'premise' if typ in ('numerical','derivation','scenario') else 'explicit',region=None) for p in pages]
  q=dict(id=qid,version=1,status='draft',authorId=self.author,stem=stem,selectionMode='multi' if len(correct)>1 else 'single',type=typ,difficulty=difficulty,cognitiveSkill='numerical' if typ=='numerical' else 'application' if typ in ('scenario','diagram') else 'recall' if typ in ('definition','match') else 'synthesis' if typ=='derivation' else 'conceptual',week=self.week,lectureId=self.lecture,topic=self.topic,subtopic=title,tags=[key],conceptIds=[cid],assumptions=assumptions or [],options=opts,correctOptionIds=[ids[i] for i in correct],citations=citations,solution=dict(justification=why,optionExplanations=dict(zip(ids,explanations)),steps=steps or [],formulas=formulas or [],simpleExplanation=why,memoryAid=memory,misconceptions=[explanations[i] for i in range(4) if i not in correct],examTraps=traps or [],prerequisiteConceptIds=[]),origin='generated',reviewIds=[])
  if conflict:q['conflictResolution']=dict(status='explicit-qualification-awaiting-independent-review',sourceClaim=conflict,basis=why,method='Retain the printed wording and evaluate the explicitly stated interpretation or qualification, not an unannounced correction.')
  self.questions.append(q);self.save();return q
 def save(self):
  b=dict(schemaVersion='1.0.0',batchId=self.batch,authorId=self.author,questions=self.questions,concepts=list(self.concepts.values()),coverageNote='Hand-authored drafts after actual source-page inspection; independent answer review and complete-coverage challenge remain required.')
  (R/f'data/question-batches/{self.batch}.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
  packet=[]
  for q in self.questions:
   a={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
   for c in a['citations']:c.pop('evidenceText',None)
   packet.append(a)
  (R/f'audits/blind-{self.batch}.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
