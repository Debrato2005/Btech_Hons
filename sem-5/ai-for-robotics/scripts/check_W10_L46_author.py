#!/usr/bin/env python3
"""Author checks only. Never downloads resources or changes security settings."""
from pathlib import Path
import sys,json,hashlib,inspect,math,io,contextlib,string
from fractions import Fraction as F
import numpy as np, sklearn, scipy
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer,TfidfTransformer
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,'/tmp/robotics-l46-deps')
import nltk
from nltk.stem import PorterStemmer,WordNetLemmatizer
from nltk.tokenize import word_tokenize
checks=[]
def ck(name,condition,details=None):
 assert bool(condition),name
 checks.append({'name':name,'passed':True,'details':details})
cmd=['pick red ball near chair','pick blue box','grab red box'];words=[[w]for w in cmd[0].split()]
e=OneHotEncoder(sparse_output=False);O=e.fit_transform(words)
ck('one-hot exact matrix',np.array_equal(O,[[0,0,0,1,0],[0,0,0,0,1],[1,0,0,0,0],[0,0,1,0,0],[0,1,0,0,0]]),O.tolist())
ck('one-hot names and dimensions',e.get_feature_names_out().tolist()==['x0_ball','x0_chair','x0_near','x0_pick','x0_red']and O.shape==(5,5))
ck('one-hot duplicate row does not add feature',e.transform([['red'],['red']]).shape==(2,5)and np.array_equal(e.transform([['red']])[0],O[1]))
try:e.transform([['blue']]);unknown=False
except ValueError:unknown=True
ck('default unseen category raises ValueError',unknown)
c=CountVectorizer();C=c.fit_transform(cmd);v=c.get_feature_names_out().tolist();M=C.toarray()
expected=[[1,0,0,1,0,1,1,1],[0,1,1,0,0,0,1,0],[0,0,1,0,1,0,0,1]]
ck('BoW full matrix and alphabetic vocabulary',np.array_equal(M,expected)and v==['ball','blue','box','chair','grab','near','pick','red'],{'matrix':M.tolist(),'vocabulary':v})
ck('BoW repeat and order variants',np.array_equal(c.transform(['box red grab','grab red box']).toarray()[0],M[2])and c.transform(['pick pick red box']).toarray()[0].tolist()==[0,0,1,0,0,0,2,1])
ck('BoW transform keeps learned features',c.transform(['pick green box']).shape==(1,8)and c.transform(['pick green box']).sum()==2)
t=TfidfVectorizer();T=t.fit_transform(cmd).toarray();df=(M>0).sum(axis=0);idf=np.log(4/(1+df))+1;raw=M*idf;norm=np.linalg.norm(raw,axis=1,keepdims=True)
ck('TF-IDF exact independent reconstruction',np.allclose(T,raw/norm,atol=1e-14),{'idf':idf.tolist(),'matrix':T.tolist(),'df':df.tolist()})
ck('TF-IDF printed two-decimal table',np.array_equal(T.round(2),[[.49,0,0,.49,0,.49,.37,.37],[0,.68,.52,0,0,0,.52,0],[0,0,.52,0,.68,0,0,.52]]))
ck('TF-IDF L2 norms not probability row sums',np.allclose(np.linalg.norm(T,axis=1),1)and not np.allclose(T.sum(axis=1),1),T.sum(axis=1).tolist())
printed=M/M.sum(axis=1,keepdims=True)*np.log(3/df)
ck('printed formula differs from default code',not np.allclose(printed,T),{'printedUnsmoothedNaturalLog':printed.tolist(),'redFirst':math.log(1.5)/5,'ballFirst':math.log(3)/5})
ck('ubiquitous unsmoothed IDF zero, default IDF one',math.log(3/3)==0 and math.log((3+1)/(3+1))+1==1)
ck('default smooth_idf=False still adds one',np.allclose(TfidfTransformer(smooth_idf=False,norm=None).fit_transform(C).toarray(),M*(np.log(3/df)+1)))
A=np.array([1.,2.,2.]);B=np.array([2.,1.,2.]);cos=lambda a,b:float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)))
ck('cosine toy dot and norms',np.dot(A,B)==8 and np.linalg.norm(A)==3 and np.linalg.norm(B)==3 and math.isclose(cos(A,B),8/9),{'cosine':cos(A,B),'degrees':math.degrees(math.acos(cos(A,B)))})
ck('cosine orthogonal/opposite/positive-scale',cos(np.array([1.,0]),np.array([0.,1]))==0 and cos(A,-A)==-1 and math.isclose(cos(A,5*B),cos(A,B)))
ck('zero vector outside formula domain',np.linalg.norm(np.zeros(3))==0)
rng=np.random.default_rng(46)
for _ in range(1000):
 a,b=rng.normal(size=(2,5));s=float(rng.uniform(.1,10));assert math.isclose(cos(s*a,b),cos(a,b),abs_tol=1e-12);assert -1-1e-12<=cos(a,b)<=1+1e-12
ck('1000 random cosine scale and range cases',True,{'cases':1000,'assertions':2000})
p=[F(57,100),F(35,100),F(15,100),F(7,100)];z=sum(p)
ck('p1469 invalid partial probabilities',z==F(57,50),{'sum':str(z),'excess':str(z-1)})
repaired=[x/z for x in p];ck('explicit exhaustive weight normalization',repaired==[F(1,2),F(35,114),F(5,38),F(7,114)]and sum(repaired)==1,[str(x)for x in repaired])
ck('p1471 omitted probability mass',1-sum([F(78,100),F(15,100),F(4,100),F(2,100)])==F(1,100))
ck('supplied action bins and midpoint error',math.floor((.12-(-.5))/.1)==6 and math.isclose((-.5+(6+.5)*.1),.15)and math.isclose(abs(.12-.15),.03))
text='Pick up the red ball near the chair!';lower=text.lower();clean=lower.translate(str.maketrans('','',string.punctuation))
ck('exact lower and punctuation operations',lower=='pick up the red ball near the chair!'and clean=='pick up the red ball near the chair')
# Explicit data-free variant, NOT the source default word_tokenize call.
tokens=word_tokenize(clean,preserve_line=True)
ck('single-line tokenizer variant',tokens==['pick','up','the','red','ball','near','the','chair'],{'variant':'preserve_line=True supplied; sentence tokenizer not invoked','tokens':tokens})
ck('token occurrences versus unique types',len(tokens)==8 and len(set(tokens))==7)
# Source-reported stopword membership is supplied, not a corpus-runtime claim.
filtered=[w for w in tokens if w not in {'up','the'}]
ck('supplied stopword membership preserves order',filtered==['pick','red','ball','near','chair'])
ck('Porter exact stems without resource dependency',[PorterStemmer().stem(w)for w in ['playing','played','plays','studies']]==['play','play','play','studi'])
ck('default WordNet lemma POS signature',inspect.signature(WordNetLemmatizer.lemmatize).parameters['pos'].default=='n')
ck('capitalization retained by source p1461 tokenization input',word_tokenize('Pick up the light box',preserve_line=True)[0]=='Pick')
nbp=R/'sources/supplemental/L46-official-week10_lecture46.ipynb';nb=json.loads(nbp.read_text());executed=[];g={'lemmatized_tokens':filtered}
for i in [15,17,19]:
 out=io.StringIO()
 with contextlib.redirect_stdout(out):exec(compile(''.join(nb['cells'][i]['source']),f'original-L46-cell-{i}','exec'),g)
 executed.append({'cell':i,'sourceSha256':hashlib.sha256(''.join(nb['cells'][i]['source']).encode()).hexdigest(),'stdout':out.getvalue(),'alterations':'None to cell; source-reported lemma list supplied for cell 15.'})
ck('original notebook cells 15 17 19 execute unchanged',len(executed)==3)
ck('notebook saved version is historical 3.9.1','3.9.1'in ''.join(nb['cells'][0]['outputs'][0]['text']))
ck('notebook p1461 variant differs from slide','This is a light box'in ''.join(nb['cells'][24]['source'])and'command2'not in ''.join(nb['cells'][24]['source']))
# Additional exact distractor and as-printed code checks before freeze.
trans=json.loads((R/'sources/supplemental/L46-slide-code-transcriptions.json').read_text())['codeByPhysicalPage']
for page,output,expected in [('1453','encoded',O),('1454','X',M),('1457','X',T)]:
 env={};exec(compile(trans[page],f'PDF-physical-{page}-as-printed','exec'),env)
 val=env[output];val=val.toarray()if hasattr(val,'toarray')else val
 ck('as-printed code executes '+page,np.allclose(val,expected))
for page,code in trans.items():compile(code,f'PDF-{page}-static-only','exec')
ck('all eight source code excerpts compile without semantic repair',len(trans)==8)
a=1+math.log(2);b=1+math.log(4/3)
ck('TF-IDF L1 distractor arithmetic',round(a/(3*a+2*b),5)==.22119 and round(b/(3*a+2*b),5)==.16822)
ck('printed TF-IDF alternative denominators',round(math.log(3)/8,5)==.13733 and round(math.log(1.5)/8,5)==.05068)
ck('normalization distractor arithmetic',F(57,100)/4==F(1425,10000)and 1-F(57,100)==F(43,100))
ck('action-bin distractor arithmetic',math.floor(.12/.1)==1 and math.isclose(-.5+1.5*.1,-.35)and math.isclose(abs(.12-(-.35)),.47)and math.isclose(abs(.12-.1),.02))
mods={}
for cls in [OneHotEncoder,CountVectorizer,TfidfVectorizer,TfidfTransformer,PorterStemmer,WordNetLemmatizer]:
 f=Path(inspect.getfile(cls));mods[cls.__name__]={'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
report={'role':'author checks, not independent review','runtime':{'python':sys.version,'sklearn':sklearn.__version__,'numpy':np.__version__,'scipy':scipy.__version__,'nltk':nltk.__version__},'checks':checks,'passedGroups':len(checks),'originalNotebookSha256':hashlib.sha256(nbp.read_bytes()).hexdigest(),'originalCellsExecuted':executed,'installedSourceFiles':mods,'blockedChecks':{'operation':'NLTK resource downloader','status':'blocked by library proxy/SSRF protection','resourceIndex':'https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/index.xml','notExecuted':['source default word_tokenize requiring punkt_tab','WordNet lemmatization','corpus stopword loading','POS tagging','NER chunking'],'policy':'No proxy-security override, alternate download, or downgrade was attempted. Saved official notebook outputs are provenance evidence, not fresh execution.'}}
(R/'audits/W10-L46-author-checks.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('Passed',len(checks),'author groups and 1000 random cases; corpus-dependent checks explicitly blocked.')
