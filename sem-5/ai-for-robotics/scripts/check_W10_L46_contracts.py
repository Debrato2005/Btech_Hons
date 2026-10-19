"""Independent source-first L46 checks. Never downloads NLTK resources."""
from pathlib import Path
import json,math,string,io,contextlib,hashlib,inspect,datetime
import numpy as np
import sklearn,nltk,pandas
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
ROOT=Path(__file__).resolve().parents[1]
nbpath=ROOT/'sources/supplemental/L46-official-week10_lecture46.ipynb'
nb=json.loads(nbpath.read_text());checks=[];runs=[]
def check(label,condition,evidence=None):
 assert bool(condition),label
 checks.append({'label':label,'passed':True,'evidence':evidence})
# Execute only self-contained original official notebook cells: no download, model or corpus calls.
for i in [17,19]:
 code=''.join(nb['cells'][i]['source']);env={};buf=io.StringIO()
 with contextlib.redirect_stdout(buf):exec(compile(code,f'official-notebook-cell-{i}','exec'),env)
 runs.append({'cellIndex':i,'sourceSha256':hashlib.sha256(code.encode()).hexdigest(),'execution':'unmodified source cell','stdout':buf.getvalue(),'columns':env['df'].columns.tolist(),'values':env['df'].values.tolist()})
commands=['pick red ball near chair','pick blue box','grab red box']
vocab=['ball','blue','box','chair','grab','near','pick','red'];counts=np.array([[1,0,0,1,0,1,1,1],[0,1,1,0,0,0,1,0],[0,0,1,0,1,0,0,1]])
cv=CountVectorizer();c=cv.fit_transform(commands).toarray()
check('BoW vocabulary alphabetical',cv.get_feature_names_out().tolist()==vocab,vocab)
check('BoW full three-row matrix',np.array_equal(c,counts),c.tolist())
check('New repeated-pick vector',cv.transform(['pick pick red box']).toarray().tolist()==[[0,0,1,0,0,0,2,1]])
check('Permutation loses order',np.array_equal(cv.transform(['pick red ball']).toarray(),cv.transform(['ball red pick']).toarray()))
# Input explicitly transcribed from the printed five-word list. This does NOT assert upstream corpus-dependent preprocessing executed.
words=['pick','red','ball','near','chair'];env={'lemmatized_tokens':words};code=''.join(nb['cells'][15]['source']);buf=io.StringIO()
with contextlib.redirect_stdout(buf):exec(compile(code,'official-notebook-cell-15-with-explicit-slide-input','exec'),env)
ohe=env['encoder'];one=env['one_hot_vectors'] if 'one_hot_vectors' in env else env['df'].values
runs.append({'cellIndex':15,'sourceSha256':hashlib.sha256(code.encode()).hexdigest(),'execution':'original cell with explicitly supplied PDF input; upstream NLTK pipeline unavailable','inputTokens':words,'columns':env['df'].columns.tolist(),'values':env['df'].values.tolist()})
check('One-hot red is row one feature four',env['df'].values[1].tolist()==[0,0,0,0,1])
try:ohe.transform([['blue']]);unknown=False
except ValueError as e:unknown=True;unknownMsg=str(e)
check('Default unseen-category error',unknown,unknownMsg)
text='Pick up the red ball near the chair!'.lower().translate(str.maketrans('','',string.punctuation))
check('Exact lowercase punctuation translation',text=='pick up the red ball near the chair',text)
check('Porter stemming without corpora',nltk.stem.PorterStemmer().stem('studies')=='studi')
check('WordNet default part-of-speech is noun',inspect.signature(nltk.stem.WordNetLemmatizer.lemmatize).parameters['pos'].default=='n')
try:exec("from nltk.stem import PorterStemmer, WordNetLemmatizer\nnltk.download('wordnet')",{});missing=False
except NameError as e:missing=True;nameMsg=str(e)
check('Fresh snippet fails before any download due missing nltk binding',missing,nameMsg)
resources=[]
for r in ['corpora/stopwords','corpora/wordnet','tokenizers/punkt_tab/english','taggers/averaged_perceptron_tagger_eng','chunkers/maxent_ne_chunker_tab','corpora/words']:
 try:nltk.data.find(r);resources.append({'path':r,'available':True})
 except LookupError:resources.append({'path':r,'available':False,'result':'local LookupError; no download attempted'})
df=(c>0).sum(axis=0);idf=np.log(4/(df+1))+1;manual=c*idf;manual/=np.linalg.norm(manual,axis=1,keepdims=True)
tv=TfidfVectorizer();actual=tv.fit_transform(commands).toarray()
check('Default TF-IDF independently derived full matrix',np.allclose(actual,manual),manual.tolist())
check('First-row ball/red rounded weights',np.allclose(np.round(actual[0,[0,7]],2),[.49,.37]))
check('L2 squared sum one, not ordinary sum',np.allclose((actual**2).sum(axis=1),1) and not np.allclose(actual.sum(axis=1),1))
uns=TfidfVectorizer(smooth_idf=False);u=uns.fit_transform(commands).toarray();uidf=np.log(3/df)+1;mu=c*uidf;mu/=np.linalg.norm(mu,axis=1,keepdims=True)
check('Disabling smoothing still adds one and normalizes',np.allclose(u,mu))
check('Simple unsmoothed ball/red',np.allclose([math.log(3)/5,math.log(1.5)/5],[.21972245773362198,.08109302162163289]))
check('Repeated document term has one document frequency',sum('red' in x.split() for x in ['red '*10,'blue','chair'])==1)
check('All-document unsmoothed IDF zero',math.log(3/3)==0)
a=np.array([1,2,2]);b=np.array([2,1,2]);cos=float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)))
check('Cosine is eight ninths',np.isclose(cos,8/9),cos)
check('LLM displayed probabilities exceed one',np.isclose(sum([.57,.35,.15,.07]),1.14))
check('Explicitly renormalized weights yield half for up',np.isclose(.57/1.14,.5))
check('VLM omitted probability mass',np.isclose(1-sum([.78,.15,.04,.02]),.01))
x=.12;lo=-.5;hi=.5;n=10;width=(hi-lo)/n;idx=math.floor((x-lo)/width);mid=lo+(idx+.5)*width
check('Toy VLA index midpoint error',idx==6 and np.isclose(mid,.15) and np.isclose(abs(mid-x),.03),{'index':idx,'midpoint':mid,'absoluteError':abs(mid-x),'units':'m'})
rng=np.random.default_rng(460046)
for _ in range(1000):
 a=rng.normal(size=5);b=rng.normal(size=5);k=rng.uniform(.001,100);cos=a@b/(np.linalg.norm(a)*np.linalg.norm(b))
 assert np.isclose(cos,(k*a)@b/(np.linalg.norm(k*a)*np.linalg.norm(b)))
 w=rng.uniform(.001,10,size=7);p=w/w.sum();assert np.isclose(p.sum(),1);assert int(p.argmax())==int(w.argmax())
 x=rng.uniform(-.5,.5);i=math.floor((x+.5)/.1);m=-.5+(i+.5)*.1;assert 0<=i<10;assert abs(m-x)<=.05+1e-12
report={'reviewerId':'robotics-contracts-reviewer','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'keyedMaterialOpened':False,'versions':{'sklearn':sklearn.__version__,'nltk':nltk.__version__,'numpy':np.__version__,'pandas':pandas.__version__},'sourceNotebook':str(nbpath.relative_to(ROOT)),'sourceNotebookSha256':hashlib.sha256(nbpath.read_bytes()).hexdigest(),'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,'explicitChecks':len(checks),'variedCases':1000,'variedAssertions':5000,'sourceCellRuns':runs,'localResourceChecks':resources,'blockedCoverage':'No corpus-dependent NLTK pipeline/POS/NER fresh execution. Historical outputs read as historical source evidence only. No resource download attempted; no fake/mocked outputs.'}
p=ROOT/'audits/W10-L46-contracts-independent-checks.json';p.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'explicit +5000 varied assertions; corpus-dependent execution unavailable')
