"""Independent deterministic/synthetic checks. No notebook, model, audio or network."""
import json, math, re, sys, datetime, xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
checks=[]
def check(name, condition, detail):
 assert condition, name
 checks.append({'name':name,'passed':True,'detail':detail})
text='I am sorry'; patterns=[('sorry',r'.*sorry.*'),('I am',r'I am (.*)')]
check('Explicit file-order first match',next(n for n,p in patterns if re.fullmatch(p,text,re.I))=='sorry','Both match; first listed wins in the stipulated toy rule, not an original ELIZA universal policy.')
capture=re.fullmatch(r'I am (.*)','I am tired today').group(1)
check('Reassembly capture substitution',f'Why are you {capture}?'=='Why are you tired today?','No additional pronoun substitutions supplied.')
check('Prefix plus parallel branches',math.isclose(.6+max(.8,1.5),2.1) and math.isclose(.6+.8,1.4),'Both outputs: 2.1 s; speech:1.4 s.')
check('Conditional stage chain',math.isclose(.9*.8*.95,.684),'0.684; conditional chain does not need additional independence.')
filter_tokens=lambda s:[x for x in s.lower().split() if x in {'clean','room'}]
check('Negation loss',filter_tokens('clean the room')==filter_tokens('do not clean the room'),'Both become clean room; sorting or threshold changes cannot recover discarded polarity.')
root=ET.fromstring('<aiml><category><pattern>HELLO</pattern><template><unsupported>Hi</unsupported></template></category></aiml>')
check('Well-formed XML versus implementation support',root.find('.//unsupported') is not None,'Standard XML parser accepts a custom tag; this does not prove AIML interpreter support. No AIML engine executed.')
a=np.array([0.,0.]);b=np.array([10.,0.]);queries=np.array([[.1,0.],[.2,0.]])
check('Nearby query example with same nearest answer',all(np.linalg.norm(q-a)<np.linalg.norm(q-b) for q in queries),'Synthetic Euclidean embeddings establish possibility, not a guarantee for all paraphrases.')
q1=np.array([4.999,0]);q2=np.array([5.001,0]);
check('Nearby queries can cross a ranking boundary',np.linalg.norm(q1-a)<np.linalg.norm(q1-b) and np.linalg.norm(q2-a)>np.linalg.norm(q2-b),'Arbitrarily close queries need not preserve nearest answer.')
check('Discrete code representation',float(7).is_integer() and 7.0 in [float(i) for i in range(16)],'Decimal rendering of a finite code index does not make the representation continuous.')
check('Full duplex with response interruption',all([True,True,True]) and not all([True,False,True]),'Concurrent input, responsive cancellation and continued interaction jointly witness stated behavior; concurrency alone does not prove interruption handling.')
rng=np.random.default_rng(49)
for _ in range(1000):
 p,a,b=rng.uniform(0,10,3);both=p+max(a,b); assert both>=p+a and both>=p+b and both<=p+a+b
check('Randomized parallel-latency bounds',True,'1000 varied positive timing cases.')
for _ in range(1000):
 a,b,c=rng.random(3);joint=a*b*c;assert 0<=joint<=min(a,b,c)
check('Randomized conditional-chain bounds',True,'1000 varied probability triples; product semantics only, not a learned-system success experiment.')
out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'interpreter':sys.executable,'numpy':np.__version__,'groupsPassed':len(checks),'variedCasesPassed':2000,'checks':checks,'runtimeBoundary':'Default existing Python/NumPy and standard library only. Synthetic examples and supplied numerical premises. No original notebook, pretrained/model/codec inference, audio, download, installation or incident virtual environment.'}
Path('audits/W10-L49-v2-independent-computations.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
