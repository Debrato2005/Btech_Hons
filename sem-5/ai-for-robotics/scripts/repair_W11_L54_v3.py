#!/usr/bin/env python3
"""Exact one-item source transcription repair; no mglearn import or execution."""
from pathlib import Path
import json,hashlib,copy,datetime,ast
R=Path(__file__).resolve().parents[1];B='W11-L54';ID=B+'-P1732-Q02';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def rd(p):return json.loads((R/p).read_text())
def wr(p,o):(R/p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qh(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert not(R/f'audits/{B}-v3-repair-manifest.json').exists()
b=rd(f'data/question-batches/{B}.json');accepted=rd(f'audits/{B}-v2-integration-review-summary.json')['acceptedQuestionHashes'];assert len(accepted)==88
for q in b['questions']:
 if q['id']in accepted:assert qh(q)==accepted[q['id']]
q=next(q for q in b['questions']if q['id']==ID);assert q['version']==2;old=copy.deepcopy(q)
a=R/f'audits/archive/{B}-v2-before-v3';a.mkdir(parents=True,exist_ok=False);(a/'question.json').write_text(json.dumps(old,indent=2,ensure_ascii=False)+'\n')
def fix(x):
 if isinstance(x,str):return x.replace('mglearn.plot_single_hidden_layer_graph','mglearn.plots.plot_single_hidden_layer_graph')
 if isinstance(x,list):return[fix(v)for v in x]
 if isinstance(x,dict):return{k:fix(v)for k,v in x.items()}
 return x
new=fix(q);new.update(version=3,status='draft',reviewIds=[],revisionAuthors=list(dict.fromkeys(q.get('revisionAuthors',[])+['L54-v3-source-transcription-author-20261020'])))
new['citations'][0]['evidenceText']='display(mglearn.plots.plot_single_hidden_layer_graph())\nfrom sklearn.neural_network import MLPRegressor'
new['citations'][0]['locator']='Printed slide 18: upper-right display snippet, separately from the upper-left estimator import'
q.clear();q.update(new)
assert 'mglearn.plot_single_hidden_layer_graph'not in json.dumps(q)
node=ast.parse('display(mglearn.plots.plot_single_hidden_layer_graph())').body[0].value.args[0].func
assert ast.unparse(node)=='mglearn.plots.plot_single_hidden_layer_graph'
assert q['correctOptionIds']==old['correctOptionIds']and q['options']==old['options']and q['solution']==old['solution']
for i,h in accepted.items():assert qh(next(x for x in b['questions']if x['id']==i))==h
wr(f'data/question-batches/{B}.json',b)
blind={k:q[k]for k in['id','version','stem','selectionMode','type','difficulty','options','assumptions']};blind['citations']=[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]
wr(f'audits/blind-{B}-v3.json',[blind]);ph=sha(f'audits/blind-{B}-v3.json')
wr(f'audits/blind-binding-{B}-v3.json',{'packetSha256':ph,'questions':[{'id':ID,'version':3,'sha256':qh(q)}]})
wr(f'audits/{B}-v3-author-checks.json',{'checkedAt':now,'role':'Author checks, not independent review','checks':['Actual rendered page1732 revisited; footer18 read','Exact upper-right module path transcribed','All item strings checked for obsolete path','Syntax tree inspected without imports or execution','All88 accepted content hashes unchanged','Key/options/solution unchanged','Version increment and revision contributor recorded','Blind packet excludes answers, solution and evidenceText'],'sourcePage':1732,'sourceSha256':q['citations'][0]['sourceSha256'],'runtime':'Default Python standard library; mglearn was not imported or executed'})
wr(f'audits/{B}-v3-repair-manifest.json',{'frozenAt':now,'packetSha256':ph,'packet':f'audits/blind-{B}-v3.json','binding':f'audits/blind-binding-{B}-v3.json','bindingSha256':sha(f'audits/blind-binding-{B}-v3.json'),'acceptedQuestionHashes':accepted,'questionSha256':{ID:qh(q)},'sourceQualificationsSha256':sha(f'audits/source-disputes-{B}.json'),'authorRevisit':1732,'independentReviewRequired':True,'priorVersion':str(a.relative_to(R))})
(R/f'audits/handoffs/{B}-repair.md').write_text(f'L54 v3 frozen: one exact source-transcription repair, all88 accepted hashes unchanged. Packet audits/blind-{B}-v3.json SHA256 {ph}. Minimal binding audits/blind-binding-{B}-v3.json. Source actual1732/footer18 revisited. Eight author checks passed; no mglearn import or execution. Independent review still required. Prior versions archived. No canonical/Git or restricted runtime use. Continue L60, then L56.\n')
print('PACKET',ph);print('BINDING',sha(f'audits/blind-binding-{B}-v3.json'))
