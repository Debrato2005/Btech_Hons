#!/usr/bin/env python3
"""Author-side exact checks and labeled reconstructions; not independent review."""
import ast,json,math,random,re,hashlib,copy,textwrap,xml.etree.ElementTree as ET
from fractions import Fraction as F
from pathlib import Path
R=Path(__file__).resolve().parents[1];B='W10-L49'
def read(p):return json.loads((R/p).read_text())
checks=[]
def ck(name,condition,detail=None):
 assert condition,name
 checks.append({'name':name,'passed':True,'detail':detail})
code=read('sources/supplemental/L49-slide-code-transcriptions.json')['codeByPhysicalPage']
# XML shape is verifiable even though these legacy tags are not claimed to run in a modern interpreter.
roots={p:ET.fromstring(code[p])for p in ['1549','1550']}
ck('Both exact AIML-shaped excerpts parse as XML',all(r.tag=='category'for r in roots.values()))
ck('Guitar pattern and visible setter nesting',roots['1549'].findtext('pattern')=='I PLAY *'and roots['1549'].find('template/set_it/person')is not None and roots['1549'].find('template/think')is None)
ck('Book pattern and both hidden blocks',roots['1550'].findtext('pattern')=='I READ * BOOKS'and len(roots['1550'].findall('template/think'))==2)
ck('All nested book setters are present',roots['1550'].find('template/think/set_it/set_does/settopic/person')is not None and roots['1550'].find('template/think/set_personality').text=='critical')

def capture(pattern,user):
 # Explicit supplied convention: trim terminal period, case-insensitive matching, retain capture spelling.
 text=user.strip().removesuffix('.')
 pat='^'+re.escape(pattern).replace(r'\*','(.+)')+'$'
 m=re.fullmatch(pat,text,re.I)
 return m.group(1)if m else None

def eval_template(root,cap):
 state={}
 def evaluate(node):
  if node.tag=='person':return re.sub(r'\bmy\b','your',cap,flags=re.I)
  s=(node.text or '')+''.join(evaluate(ch)+(ch.tail or '')for ch in node)
  key={'set_it':'it','set_does':'does','settopic':'topic','set_personality':'personality'}.get(node.tag)
  if key:state[key]=' '.join(s.split())
  return ''if node.tag=='think'else s
 visible=' '.join(evaluate(root.find('template')).split())
 return visible,state
cap=capture(roots['1549'].findtext('pattern'),'I play my guitar.')
ck('Guitar wildcard excludes fixed prefix and punctuation',cap=='my guitar')
out,state=eval_template(roots['1549'],cap)
ck('Guitar visible return and stored predicate',out=='Is your guitar a game or a musical instrument?'and state=={'it':'your guitar'},{'visible':out,'state':state})
modified=copy.deepcopy(roots['1549']);temp=modified.find('template');setter=temp.find('set_it');tail=setter.tail;setter.tail=None;temp.remove(setter);think=ET.Element('think');think.append(setter);think.tail=tail;temp.append(think)
out,state=eval_template(modified,cap)
ck('Explicit think-wrapped variant suppresses only visible setter return',out=='Is a game or a musical instrument?'and state=={'it':'your guitar'},{'visible':out,'state':state})
cap=capture(roots['1550'].findtext('pattern'),'I read Sci-fi books.')
ck('Book wildcard excludes fixed prefix and suffix',cap=='Sci-fi')
out,state=eval_template(roots['1550'],cap)
ck('Nested setters propagate one value and second hidden block sets personality',state=={'topic':'read Sci-fi books','does':'read Sci-fi books','it':'read Sci-fi books','personality':'critical'},state)
ck('Book visible output contains neither hidden state string',out=='Name some books in that genre.',out)
ck('Unmatched category is not falsely evaluated',capture('I PLAY *','We play my guitar.')is None and capture('I READ * BOOKS','I read books about robots.')is None)
ck('Only exact supplied greeting normalization is used',[s.strip().lower()=='hello'for s in [' HELLO ','hello!','say hello','hello there']]==[True,False,False,False])
ck('Supplied decomposition substitution', 'Why are you {capture}?'.format(capture='tired today')=='Why are you tired today?')
# No imports, network, models or original notebook execution are attempted.
try:compile(code['1552'],'p1552-as-printed','exec');syntax=None
except SyntaxError as e:syntax=e
ck('As-printed module fails at return outside function',syntax is not None and 'return' in str(syntax)and 'outside function' in str(syntax),str(syntax))
wrapped='def reconstructed(model_id, question):\n'+textwrap.indent(code['1552'],'    ')
ck('Explicit whole-excerpt function wrapper compiles',compile(wrapped,'p1552-wrapper-only','exec')is not None)
# Analyzing the wrapper does not execute its imports or model-loading calls.
tree=ast.parse(wrapped);names={n.id for n in ast.walk(tree)if isinstance(n,ast.Name)and isinstance(n.ctx,ast.Load)}
assigns={n.id for n in ast.walk(tree)if isinstance(n,ast.Name)and isinstance(n.ctx,ast.Store)}
ck('Omitted model_id and question distinguished from assigned variables',{'model_id','question'}<=names and not {'model_id','question'}&assigns and {'tokenizer','model','pipe','output','reply'}<=assigns)
ck('No Gradio construction or launch appears',not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and (n.func.attr=='launch'or isinstance(n.func.value,ast.Name)and n.func.value.id=='gradio')for n in ast.walk(tree)))
question='Hello';prompt=f'<|user|>\n{question}\n<|assistant|>\n'
ck('Exact f-string characters',prompt=='<|user|>\nHello\n<|assistant|>\n',repr(prompt))
output=[{'generated_text':'PROMPTAnswer'}]
ck('Indexing does not strip prompt',output[0]['generated_text']=='PROMPTAnswer')
# Reconstruct only the last four assignment/return lines using a supplied fake pipeline.
helper='def helper(question, pipe):\n    prompt = f"<|user|>\\n{question}\\n<|assistant|>\\n"\n    output = pipe(prompt)\n    reply = output[0]["generated_text"]\n    return reply\n'
ns={};exec(compile(helper,'explicit-stub-helper','exec'),ns)
seen=[]
def stub(p):seen.append(p);return [{'generated_text':p+'Hi'}]
ck('Explicit stub helper reproduces full-string extraction',ns['helper']('Hello',stub)==prompt+'Hi'and seen==[prompt])
def flag_stub(p,return_full_text=True):return [{'generated_text':(p if return_full_text else '')+'Hi'}]
ck('Explicit new-text stub variant separates return scope',flag_stub(prompt,False)[0]['generated_text']=='Hi'and flag_stub(prompt)[0]['generated_text']==prompt+'Hi')
# Exact numbers and every arithmetic-based distractor.
q=(F(1),F(0));vs=[(F(3),F(4)),(F(4),F(3)),(F(-1),F(0))]
s=[sum(a*b for a,b in zip(q,v))/F(math.isqrt(int(sum(a*a for a in v))))for v in vs]
ck('Cosine example scores and rejection threshold',s==[F(3,5),F(4,5),F(-1)]and max(s)<F(85,100),[float(v)for v in s])
ck('Coordinate-confusion distractor picks a instead of b',[v[1]for v in vs].index(max(v[1]for v in vs))==0 and s.index(max(s))==1)
probs=[F(55,100),F(30,100),F(15,100)]
ck('Complete toy token distribution and unique greedy choice',sum(probs)==1 and probs.index(max(probs))==0 and all(p>0 for p in probs))
ck('Nonuniform and threshold-set distractors differ from greedy',len(set(probs))>1 and [i for i,p in enumerate(probs)if p>F(1,4)]==[0,1])
t=[F(4,10),F(75,100),F(25,100)];o=F(1,10)
ck('Sequential latency and all numerical distractors',[sum(t)+o,max(t)+o,sum(t),sum(t)+3*o]==[F(15,10),F(85,100),F(14,10),F(17,10)])
prefix,voice,action=F(6,10),F(8,10),F(15,10)
ck('Parallel completion and speech time',(prefix+max(voice,action),prefix+voice)==(F(21,10),F(14,10)))
ck('Parallel serial and omitted-prefix distractors',prefix+voice+action==F(29,10)and (max(voice,action),voice)==(F(15,10),F(8,10)))
factors=[F(9,10),F(8,10),F(95,100)]
ck('Conditional success chain',math.prod(factors)==F(684,1000))
ck('Conditional chain distractor arithmetic',sum(factors)/3==F(53,60)and factors[0]==F(9,10)and 1-sum(1-x for x in factors)==F(65,100))
filtered=lambda s:[w for w in re.findall(r'\w+',s.lower())if w in {'clean','room'}]
ck('Negation counterexample collapses opposite requests',filtered('Clean the room')==filtered('Do not clean the room')==['clean','room'])
# Randomized internal consistency checks cover formulas, not factual model performance.
rng=random.Random(49);assertions=0
for k in range(1000):
 a,b,c=[F(rng.randrange(1,101),100)for _ in range(3)]
 assert a+max(b,c)<=a+b+c;assertions+=1
 assert math.prod([a,b,c])<=min(a,b,c);assertions+=1
 word=f'object{k}';r,s=eval_template(roots['1549'],'my '+word)
 assert s['it']=='your '+word and r=='Is your '+word+' a game or a musical instrument?';assertions+=1
ck('Randomized formula and reconstructed-template consistency',assertions==3000,{'cases':1000,'assertions':assertions,'seed':49})
b=read(f'data/question-batches/{B}.json')
ck('All numerical questions have complete formula and steps',all(q['solution']['formulas']and q['solution']['steps']for q in b['questions']if q['type']=='numerical'))
report={'batchId':B,'role':'author-side checks only, not independent verification','passedGroups':len(checks),'checks':checks,'randomCases':1000,'randomAssertions':3000,'actualSourceCodePages':[1549,1550,1552],'xmlParsing':'Two exact source fragments parsed; semantics checked only by explicitly supplied reconstruction, not a standard AIML interpreter.','pythonExecution':'Exact excerpt compilation and explicit stub/helper variants only. No Transformers, Gradio, torch, model weights or original notebook execution.','primaryAPIVersion':'Transformers 4.57.1 documentation, not installed','officialNotebookRetrieval':'denied twice; absent artifact; no further route','inheritedNLTKCorpusSecurityBlocker':'Preserved; no override or bypass','transcriptionSha256':hashlib.sha256((R/'sources/supplemental/L49-slide-code-transcriptions.json').read_bytes()).hexdigest()}
(R/f'audits/{B}-author-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Passed',len(checks),'check groups and',assertions,'random assertions')
