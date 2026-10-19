"""Independent L46 repair/gap derivations. No corpus or model requests."""
from pathlib import Path
import json, math, hashlib, datetime, string, random, sys, io, contextlib, inspect
from collections import Counter
R=Path(__file__).resolve().parents[1]
out=R/'audits/W10-L46-v2-contracts-independent-checks.json'; assert not out.exists()
checks=[]
def check(name, condition, result=None):
 assert condition,(name,result)
 checks.append({'name':name,'passed':True,'result':result})
def cos(a,b):return sum(x*y for x,y in zip(a,b))/math.sqrt(sum(x*x for x in a)*sum(y*y for y in b))
text='Do NOT pick up the boxes near the boxes!'
tokens=text.lower().translate(str.maketrans('','',string.punctuation)).split()
filtered=[t for t in tokens if t not in {'do','the','up'}];lemmas=['box' if t=='boxes' else t for t in filtered]
check('Unfiltered POS path has nine ordered occurrences',len(tokens)==9,tokens)
check('Declared stop set retains negation and repeated boxes',filtered==['not','pick','boxes','near','boxes'],filtered)
check('Declared lemma map and five nested input rows',lemmas==['not','pick','box','near','box'] and [[x]for x in lemmas]==[['not'],['pick'],['box'],['near'],['box']],lemmas)
check('Length-normalized pick TF',2/4==.5,2/4)
check('Unique-term denominator alternative',2/3!=.5,2/3)
check('One count instead of two alternative',1/4==.25,1/4)
commands=['pick red ball near chair','pick blue box','grab red box']
check('Red document frequency is two',sum('red'in s.split()for s in commands)==2,2)
check('One document ten occurrences means df one',sum('red'in s for s in [['red']*10,[],[],[],[]])==1,1)
check('Ubiquitous IDF is zero',math.log(5/5)==0,0)
check('Toy cosine is 8/9',math.isclose(cos([1,2,2],[2,1,2]),8/9),cos([1,2,2],[2,1,2]))
check('Repaired exhaustive four-weight normalization',math.isclose(.57/sum([.57,.35,.15,.07]),.5),.57/sum([.57,.35,.15,.07]))
check('VLM omitted mass is .01',math.isclose(1-sum([.78,.15,.04,.02]),.01),1-sum([.78,.15,.04,.02]))
# New integrated corpus exercise: derive from counts, not keyed values.
vocab=['red','box','ball'];docs=['red red red box','red ball','red box','box box box box box box box box box ball'];q='red ball'
counts=[[s.split().count(t)for t in vocab]for s in docs]
df=[sum(row[j]>0 for row in counts)for j in range(3)];idf=[math.log(4/n)for n in df]
def vec(s):
 c=Counter(s.split());return [c[t]/sum(c.values())*w for t,w in zip(vocab,idf)]
vectors=[vec(s)for s in docs];query=vec(q);scores=[cos(v,query)for v in vectors];ranking=sorted(range(4),key=lambda i:-scores[i]);binary=[[int(n>0)*w for n,w in zip(row,idf)]for row in counts];binaryscores=[cos(v,query)for v in binary]
check('Integrated corpus df',df==[3,3,2],df)
check('Repeated document term counts',counts==[[3,1,0],[1,0,1],[1,1,0],[0,9,1]],counts)
check('Query is not a fifth fitting document',idf==[math.log(4/3),math.log(4/3),math.log(2)],idf)
check('Integrated ranking',ranking==[1,0,2,3],scores)
check('High TF outweighs rare term here',vectors[0][0]>vectors[3][2],{'red_d1':vectors[0][0],'ball_d4':vectors[3][2]})
check('Binary-count mistake creates d1=d3',math.isclose(binaryscores[0],binaryscores[2]),binaryscores)
dots=[sum(x*y for x,y in zip(row,query))for row in vectors]
check('Raw weighted dot product instead of cosine yields d2>d1>d4>d3',sorted(range(4),key=lambda i:-dots[i])==[1,0,3,2],dots)
check('Ignoring IDF does not create that alternative',sorted(range(4),key=lambda i:-cos(counts[i],[1,0,1]))==[1,0,2,3],[cos(row,[1,0,1])for row in counts])
# Read the approved official notebook, and execute only dependency-independent local cells.
nbp=R/'sources/supplemental/L46-official-week10_lecture46.ipynb';nb=json.loads(nbp.read_text());nh=hashlib.sha256(nbp.read_bytes()).hexdigest();assert nh=='d32019733e3d14c0b21c9bf5276ecceb8fa4b0a11757bb0b4ffef4b2fe2504c3'
executions=[]
for n in [15,17,19]:
 src=''.join(nb['cells'][n]['source']);assert not any(x in src for x in ['download','requests.','!pip','urllib'])
 ns={'lemmatized_tokens':lemmas}if n==15 else {};buf=io.StringIO()
 with contextlib.redirect_stdout(buf):exec(compile(src,f'official-L46-cell-{n}','exec'),ns)
 executions.append({'cell':n,'sourceSha256':hashlib.sha256(src.encode()).hexdigest(),'output':buf.getvalue(),'inputQualification':'Explicitly supplied new exercise lemmas, not fresh WordNet execution.'if n==15 else'Unmodified standalone source cell with its own printed commands.'})
 if n==15:
  check('Original nested-encoder cell handles duplicate box rows',ns['one_hot_vectors'].shape==(5,4),ns['one_hot_vectors'].tolist())
  check('Duplicate box encodings equal',ns['one_hot_vectors'][2].tolist()==ns['one_hot_vectors'][4].tolist(),ns['encoder'].get_feature_names_out().tolist())
 if n==17:
  check('Original count-table columns',ns['df'].columns.tolist()==['ball','blue','box','chair','grab','near','pick','red'],ns['df'].columns.tolist())
  check('Original count-table values',ns['X'].toarray().tolist()==[[1,0,0,1,0,1,1,1],[0,1,1,0,0,0,1,0],[0,0,1,0,1,0,0,1]],ns['X'].toarray().tolist())
 if n==19:check('Original default TF-IDF rows normalized',all(math.isclose(sum(x*x for x in row),1)for row in ns['X'].toarray()),ns['X'].toarray().tolist())
# Signature inspection does not invoke WordNet corpus or download code.
sys.path.insert(0,'/tmp/robotics-l46-deps');import nltk
from nltk.stem import WordNetLemmatizer
sig=str(inspect.signature(WordNetLemmatizer.lemmatize));check('Installed noun POS default',inspect.signature(WordNetLemmatizer.lemmatize).parameters['pos'].default=='n',sig)
# Meaningful varied invariants of normalized frequency, IDF and cosine.
rng=random.Random(4602);varied=0
for _ in range(1000):
 c=[rng.randrange(1,20)for _ in range(5)];v=[rng.randrange(1,20)for _ in range(5)];a=rng.uniform(.1,10);b=rng.uniform(.1,10)
 assert math.isclose(sum(n/sum(c)for n in c),1);varied+=1
 assert math.isclose(cos(c,v),cos([a*x for x in c],[b*x for x in v]));varied+=1
 assert 0<cos(c,v)<=1+1e-12;varied+=1
 N=rng.randrange(2,100);d1=rng.randrange(1,N);d2=rng.randrange(d1+1,N+1)
 assert math.log(N/d1)>math.log(N/d2)>=0;varied+=1
 assert math.isclose((c[0]*a)/sum(n*a for n in c),c[0]/sum(c));varied+=1
r={'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewerId':'robotics-contracts-reviewer-L46','explicitChecks':len(checks),'checks':checks,'variedCases':1000,'variedAssertions':varied,'gapDerivation':{'counts':counts,'df':df,'idf':idf,'vectors':vectors,'query':query,'cosines':scores,'ranking':[f'd{i+1}'for i in ranking],'binaryCosines':binaryscores},'notebookPath':str(nbp.relative_to(R)),'notebookSha256':nh,'sourceCellExecutions':executions,'signatureInspection':{'nltkVersion':nltk.__version__,'signature':sig,'corpusCalled':False},'runtime':'Default interpreter and installed sklearn/pandas; source cells 17/19 unchanged, cell 15 supplied exercise lemmas. NLTK signature only. No corpus-dependent tokenizer, lemmatizer, POS, NER, model, download, or network execution. Historical source outputs remain historical. L48 incident temporary environment not used.','derivationCorrection':'Before any keyed access, an attempted hypothesis that omitting IDF creates the o1 ranking failed: it keeps d2>d1>d3>d4. The raw weighted dot product, without cosine normalization, independently produces d2>d1>d4>d3. No failed claim was silently carried into frozen answers.','primarySourceChecks':[{'url':'https://www.nltk.org/api/nltk.stem.wordnet.html','finding':'Official signature pos=n; grammatical class supplied, not automatically inferred.'},{'url':'https://nlp.stanford.edu/projects/glove/','finding':'Original training fits global word co-occurrence statistics; learned vectors may subsequently be compared with cosine.'}]}
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'explicit':len(checks),'variedAssertions':varied,'gapCosines':scores,'ranking':r['gapDerivation']['ranking']}))
