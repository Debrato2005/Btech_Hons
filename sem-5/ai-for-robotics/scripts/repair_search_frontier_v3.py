#!/usr/bin/env python3
"""Remove an incidental conflicted-source dependency from one hypothetical scenario."""
from pathlib import Path
import copy, json, hashlib
from validate import question_hash
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'data/question-batches/search-foundations.json'
batch=json.loads(path.read_text());qid='W08-L37-P1135-Q04'
q=next(q for q in batch['questions'] if q['id']==qid)
assert q['version']==2,'Do not overwrite a later revision.'
original=copy.deepcopy(q);other={x['id']:question_hash(x) for x in batch['questions'] if x['id']!=qid}
history=ROOT/'audits/batch-history/search-P1135-Q04-v2-before-hypothetical-repair.json'
if history.exists():assert json.loads(history.read_text())==original
else:history.write_text(json.dumps(original,ensure_ascii=False,indent=2)+'\n')
q.update(version=3,status='draft',reviewIds=[],
 stem='Consider a hypothetical static grid diagram that labels final g and h values for every reachable free cell but omits the search history. Why is selecting the globally smallest labeled f over all cells NOT a valid replacement for an A* trace?',
 assumptions=['Use the graph-search frontier convention demonstrated on physical pages 1121–1122.',
              'The all-cell cost diagram is a hypothetical teaching scenario, not a claim about a specific source figure. The question tests current frontier eligibility, not any numerical label.'])
q['citations']=[c for c in q['citations'] if c['physicalPage'] in (1121,1122)]
assert len(q['citations'])==2
for c in q['citations']:
 c['role']='premise'
 c['locator']=('Physical page 1121, printed slide 34: initialize frontier with A, then discover B and C while A becomes explored' if c['physicalPage']==1121 else 'Physical page 1122, printed slide 35: expand C then F, with changing frontier and explored lists')
q['notes']='Hypothetical application of the source-supported current-frontier principle. No question premise depends on physical page 1135; its inconsistent start-cost annotation remains unresolved elsewhere.'
q['solution']['justification']='A* minimizes f among its current frontier entries, not among every location in a hypothetical final cost diagram. The source trace separately records discovery, expansion and the changing open set.'
q['solution']['simpleExplanation']='A final cost map tells you numbers, not which states have been discovered and are waiting right now. A* chooses from that current waiting list.'
assert all(question_hash(x)==other[x['id']] for x in batch['questions'] if x['id']!=qid)
path.write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
packet=[{k:q[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}]
(ROOT/'audits/blind-search-frontier-v3.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
report={'questionId':qid,'oldVersion':2,'newVersion':3,'oldSha256':question_hash(original),'newSha256':question_hash(q),'otherQuestionHashesUnchanged':len(other),'sourcePagesReinspected':[1121,1122],'removedCitationPhysicalPage':1135,'sourceConflictRemainsUnresolved':True,'reviewStatus':'independent_review_required','blindPacketPath':'audits/blind-search-frontier-v3.json'}
(ROOT/'audits/search-frontier-v3-revision-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,indent=2))
