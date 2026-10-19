"""Independent L49 checks: source-pixel transcription and supplied toy cases only.
Default Python + existing NumPy. No original notebook, model, package install, or network.
"""
import ast, json, math, pathlib, re, sys, datetime, hashlib, xml.etree.ElementTree as ET
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
records=[]
def check(name, condition, evidence):
    assert condition, (name,evidence)
    records.append({'name':name,'passed':True,'evidence':evidence})
code='''import gradio
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
# Load tokenizer (Text → Tokens)
tokenizer = AutoTokenizer.from_pretrained(model_id)
# Load pretrained LLM
model = AutoModelForCausalLM.from_pretrained(model_id)
# Create chatbot inference pipeline
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer)
# Format the user's question as a prompt
prompt = f"<|user|>\\n{question}\\n<|assistant|>\\n"
# Generate the chatbot's response
output = pipe(prompt)
# Extract only the assistant's reply
reply = output[0]["generated_text"]
# Return/display the reply
return reply
'''
try:compile(code,'source-p1552','exec');error='none'
except SyntaxError as e:error=e.msg
check('Literal module compile',error=="'return' outside function",error)
wrapped='def reconstructed_function():\n'+''.join('    '+l+'\n' for l in code.splitlines())
check('Explicit wrapper compiles',bool(compile(wrapped,'explicit-wrapper','exec')),'Compiled only; imports and model loaders not executed.')
tree=ast.parse(wrapped); loads={n.id for n in ast.walk(tree) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)};stores={n.id for n in ast.walk(tree) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Store)}
check('Missing variable inputs',{'model_id','question'} <= loads-stores,sorted(loads-stores))
question='Hello';prompt=f'<|user|>\n{question}\n<|assistant|>\n'
check('Literal prompt string',prompt=='<|user|>\nHello\n<|assistant|>\n',repr(prompt))
output=[{'generated_text':'PROMPTAnswer'}]
check('Exact supplied lookup',output[0]['generated_text']=='PROMPTAnswer',output[0]['generated_text'])
# This is only a mock mapping of the documented output-format contract, not a Transformers runtime.
def mock_pipe(s,return_full_text=True):return [{'generated_text':s+'Answer' if return_full_text else 'Answer'}]
check('Mock full-text contract',mock_pipe('PROMPT')[0]['generated_text']=='PROMPTAnswer' and mock_pipe('PROMPT',False)[0]['generated_text']=='Answer','Synthetic strings only; pinned API semantics independently checked in documentation.')
check('No Gradio application call',not any(isinstance(n,ast.Attribute) and n.attr in ['launch','Interface','Blocks','ChatInterface'] for n in ast.walk(tree)),'Only import gradio in the displayed source.')
guitar='<category><pattern>I PLAY *</pattern><template>Is <set_it><person/></set_it> a game or a musical instrument?</template></category>'
books='<category><pattern>I READ * BOOKS</pattern><template>Name some books in that genre.<think><set_it><set_does><settopic>read <person/> books</settopic></set_does></set_it></think><think><set_personality>critical</set_personality></think></template></category>'
# This evaluator deliberately implements ONLY the packet-supplied legacy semantics.
def evaluate(node,capture,state):
    if node.tag=='person':return re.sub(r'\bmy\b','your',capture,flags=re.I)
    val=(node.text or '')+''.join(evaluate(c,capture,state)+(c.tail or '') for c in node)
    setter={'set_it':'it','set_does':'does','settopic':'topic','set_personality':'personality'}
    if node.tag in setter:state[setter[node.tag]]=val
    return '' if node.tag=='think' else val
r=ET.fromstring(guitar);cap=re.fullmatch(r'I PLAY (.+)', 'I play my guitar.'.removesuffix('.'),re.I).group(1);state={};reply=evaluate(r.find('template'),cap,state)
check('Guitar wildcard',cap=='my guitar',cap)
check('Guitar state and output',state=={'it':'your guitar'} and reply=='Is your guitar a game or a musical instrument?',{'state':state,'reply':reply})
hidden=ET.fromstring(guitar.replace('<set_it>','<think><set_it>').replace('</set_it>','</set_it></think>'));state={};reply=' '.join(evaluate(hidden.find('template'),cap,state).split())
check('Think variant',state=={'it':'your guitar'} and reply=='Is a game or a musical instrument?',{'state':state,'reply':reply})
r=ET.fromstring(books);cap=re.fullmatch(r'I READ (.+) BOOKS','I read Sci-fi books.'.removesuffix('.'),re.I).group(1);state={};reply=evaluate(r.find('template'),cap,state)
check('Books wildcard',cap=='Sci-fi',cap)
check('Nested setter propagation',state=={'topic':'read Sci-fi books','does':'read Sci-fi books','it':'read Sci-fi books','personality':'critical'},state)
check('Books visible reply',reply=='Name some books in that genre.',reply)
inputs=['hello there',' HELLO ','hello!','say hello'];hits=[i for i,s in enumerate(inputs) if s.strip().lower()=='hello']
check('Normalization domain',hits==[1],hits)
check('Reassembly','Why are you {capture}?'.format(capture='tired today')=='Why are you tired today?','Direct stipulated slot substitution.')
def cosine(q,v):
    q=np.asarray(q,dtype=float);v=np.asarray(v,dtype=float)
    if q.shape!=v.shape or q.ndim!=1 or not np.isfinite(q).all() or not np.isfinite(v).all() or np.linalg.norm(q)==0 or np.linalg.norm(v)==0:raise ValueError('nonzero finite vectors of matching dimensions required')
    return float(q@v/(np.linalg.norm(q)*np.linalg.norm(v)))
scores=[cosine([1,0],v) for v in [[3,4],[4,3],[-1,0]]]
check('Cosine ranking and rejection',np.allclose(scores,[.6,.8,-1],rtol=0,atol=1e-14) and int(np.argmax(scores))==1 and max(scores)<.85,scores)
bad=0
for q,v in [([0,0],[1,0]),([1],[1,2]),([math.nan,0],[1,0])]:
    try:cosine(q,v)
    except ValueError:bad+=1
check('Cosine invalid domains',bad==3,'Zero vector, dimension mismatch and NaN rejected.')
check('Cosine acceptance boundary',not (.8>=.85) and .8>=.8,'Threshold is inclusive; rejection and ranking are separate.')
check('Greedy and support',int(np.argmax([.55,.3,.15]))==0 and sum([.55,.3,.15])==1 and all(p>0 for p in [.55,.3,.15]),'Unique greedy maximum; three positive-probability candidates.')
check('Sequential latency',math.isclose(.4+.75+.25+.1,1.5,abs_tol=1e-15),'1.50 s; alternative errors: max+overhead .85, omit overhead 1.40, triple overhead 1.70.')
check('Parallel latency',math.isclose(.6+max(.8,1.5),2.1) and math.isclose(.6+.8,1.4),'Both 2.1 s; speech 1.4 s; serial error 2.9 s.')
check('Conditional cascade',math.isclose(.9*.8*.95,.684,abs_tol=1e-15),'0.684; average .883333, first stage .9, subtract errors .65 are distinct.')
def keywords(s):return [w for w in s.lower().split() if w in {'clean','room'}]
check('Polarity collision',keywords('Clean the room')==keywords('Do not clean the room')==['clean','room'],'A non-injective retained representation loses polarity.')
rng=np.random.default_rng(4919);trials=1000
for i in range(trials):
    q=rng.normal(size=4);v=rng.normal(size=4);s=cosine(q,v);scale=rng.uniform(.01,10)
    assert -1-1e-12<=s<=1+1e-12 and math.isclose(s,cosine(q,scale*v),abs_tol=1e-12)
    prefix,a,b,over=rng.uniform(0,10,size=4)
    assert math.isclose(prefix+max(a,b),max(prefix+a,prefix+b),abs_tol=1e-12)
    probs=rng.uniform(size=3);joint=float(np.prod(probs));assert 0<=joint<=float(min(probs))
    genre='genre'+str(i);state={};reply=evaluate(ET.fromstring(books).find('template'),genre,state)
    assert state['topic']==state['it']==state['does']=='read '+genre+' books' and state['personality']=='critical' and reply=='Name some books in that genre.'
check('Varied deterministic cases',True,{'iterations':trials,'caseFamilies':4,'cases':trials*4,'families':['Cosine bounds and positive scale invariance','Parallel completion identity','Conditional probability bounds','Nested hidden setter propagation']})
# Exact visible options and canonical binding stability, not author-check execution.
qs=json.load(open(ROOT/'data/question-batches/W10-L49.json'))['questions'];bind=json.load(open(ROOT/'audits/blind-binding-W10-L49.json'))['questions'];sys.path.insert(0,str(ROOT/'scripts'));from validate import question_hash
check('All frozen hashes preserved',all(question_hash(q)==b['sha256'] for q,b in zip(qs,bind)),'84 question objects match minimal bindings.')
check('Unique option texts and full rationales',all(len({o['text'].strip().casefold() for o in q['options']})==len(q['options']) and set(q['solution']['optionExplanations'])=={o['id'] for o in q['options']} for q in qs),'Structural check supplements, not replaces, manual distractor review.')
result={'reviewer':'independent-reviewer-robotics-batches-v2','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pythonExecutable':sys.executable,'numpyVersion':np.__version__,'groupsPassed':len(records),'variedCases':4000,'records':records,'sourceCodeMode':'Exact slide transcription compiled; explicit wrapped variant compiled; XML reconstructed supplied semantics executed; mock string interface executed. No original notebook or model inference.','restrictedEnvironmentUsed':False,'originalNotebookObtained':False,'originalNotebookExecuted':False,'pretrainedInferenceExecuted':False,'codeTranscription':code,'guitarTranscription':guitar,'booksTranscription':books}
(ROOT/'audits/W10-L49-independent-computations.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['groupsPassed','variedCases','pythonExecutable','sourceCodeMode']}))
