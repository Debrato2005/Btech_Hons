"""One-time source-bound L46 repair; author checks do not confer review status."""
from pathlib import Path
import copy,json,hashlib,datetime,sys,math,string
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors
from authoring_helpers import formula
p=R/'data/question-batches/W10-L46.json';before=json.loads(p.read_text());b=copy.deepcopy(before);qs={q['id'].split('-P')[1]:q for q in b['questions']}
s=json.loads((R/'audits/W10-L46-contracts-review-summary.json').read_text());changed=[x.split('-P')[1] for x in s['flaggedFindings']];accepted=s['acceptedQuestionHashes'];assert len(changed)==35 and len(accepted)==55 and all(qs[n]['version']==1 for n in changed)
archive=R/'audits/batch-history/W10-L46-pre-v2.json';assert not archive.exists();archive.write_text(p.read_text());AUTHOR='build_robotics_study_app:L46-v2-author';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def opt(n,i,t,e):
 q=qs[n];next(o for o in q['options'] if o['id']==f'o{i}')['text']=t;q['solution']['optionExplanations'][f'o{i}']=e
def replace(n,opts,exps,stem=None,why=None):
 for i,(t,e) in enumerate(zip(opts,exps),1):opt(n,i,t,e)
 if stem:qs[n]['stem']=stem
 if why:qs[n]['solution']['justification']=qs[n]['solution']['simpleExplanation']=why
def cite(n,page,desc,kind='statement',role='premise'):
 q=qs[n];c=next((c for c in q['citations'] if c['physicalPage']==page),None)
 if c is None:c=copy.deepcopy(q['citations'][0]);q['citations'].append(c)
 c.update(slideId=f'lectures-p{page}',physicalPage=page,kind=kind,role=role,locator=f'Lecture L46, physical PDF page {page}, printed footer {page-1439}: {desc}',evidenceText=(R/f'sources/text/lectures/page-{page}.txt').read_text().strip())
 for co in b['concepts']:
  if co['id'] in q['conceptIds'] and c['slideId'] not in co['slideIds']:co['slideIds'].append(c['slideId'])
opt('1445-Q02',3,'Accept only the exact trained command string, because paraphrases cannot express the same intended action.','Exact-template matching can miss related requests that use different wording.')
opt('1445-Q02',4,'Treat commands as equivalent whenever their object nouns match, without checking the requested action or context.','The same object can be involved in different actions; noun agreement alone is insufficient.')
replace('1446-Q02',[
 'No; they are conceptual stages that some models perform together internally.',
 'Yes; a numerical representation must always be exported by a separately trained module before language understanding can begin.',
 'Yes; end-to-end training may tune numerical encodings but cannot learn their interaction with language understanding.',
 'No; joint implementation means numerical encoding and understanding are the same concept, so their different responsibilities disappear.'
],[
 'The text permits joint internal processing while retaining the conceptual roles.',
 'The source does not impose a separately trained, externally exported representation boundary.',
 'Jointly learned interaction is consistent with the described internal combination.',
 'Combining software stages does not erase their different conceptual responsibilities.'
])
opt('1447-Q02',3,'A vocabulary counts every repeated token occurrence separately; a corpus is only the set of distinct types.','Repeated occurrences belong to the texts; the vocabulary is a distinct-type inventory.')
opt('1447-Q02',4,'A vocabulary is the list of document identifiers; a corpus is the list of feature-column names.','Document identifiers and feature-column names are metadata, not the stated text-collection and token-type distinction.')
opt('1449-Q04',4,'It inherits the grammatical tag returned by any earlier pos_tag call, even when that tag is not passed to lemmatize.','The isolated method call does not automatically receive an earlier tagger result; pos must be passed explicitly.')
api=R/'audits/W10-L46-v2-supplemental-evidence.json'
wn=Path('/tmp/robotics-l46-deps/nltk/stem/wordnet.py').read_text();assert 'def lemmatize(self, word: str, pos: str = "n")' in wn
notebook=R/'sources/supplemental/L46-official-week10_lecture46.ipynb';nb=json.loads(notebook.read_text());cell=''.join(nb['cells'][17]['source']);assert 'X.toarray()' in cell and 'columns=vectorizer.get_feature_names_out()' in cell
api.write_text(json.dumps({'checkedAt':now,'wordnet':{'url':'https://www.nltk.org/api/nltk.stem.wordnet.html','installedVersion':'3.10.3','signature':'lemmatize(self, word: str, pos: str = "n")','localSourceSha256':hashlib.sha256(wn.encode()).hexdigest(),'scope':'Signature inspected as text; no corpus-dependent execution or download.'},'countDataFrame':{'url':'https://github.com/robotics-lab-iitr/nptel-ai-robotics/blob/main/week10/week10_lecture46.ipynb','localPath':str(notebook.relative_to(R)),'sha256':hashlib.sha256(notebook.read_bytes()).hexdigest(),'cell':17,'source':cell}},indent=2)+'\n')
evidenceHash=hashlib.sha256(api.read_bytes()).hexdigest()
qs['1449-Q04']['primaryEvidence']=[{'url':'https://www.nltk.org/api/nltk.stem.wordnet.html','version':'Installed NLTK 3.10.3 signature inspected; no corpus execution.','locator':'WordNetLemmatizer.lemmatize default pos="n".','savedEvidencePath':str(api.relative_to(R)),'savedEvidenceSha256':evidenceHash,'section':'wordnet','relationToLecture':'Supplemental API premise for the call displayed on p1449.'}]
qs['1449-Q04']['assumptions'].append('Supplemental premise: the inspected NLTK 3.10.3 signature defaults pos to n; no automatic sentence tagging is performed by this isolated call.')
replace('1450-Q01',[
 'The lemma study is a recognizable lexical base, while the stem studi need not be a word.',
 'The example demonstrates a smaller resulting vocabulary for lemmatization across any corpus.',
 'The example measures lower runtime and memory use for lemmatization than for stemming.',
 'The example establishes higher downstream command-classification accuracy for lemmatization.'
],[
 'Only the lexical-base comparison is directly shown.',
 'A single word-form example does not measure a corpus-wide vocabulary-size outcome.',
 'The slide does not benchmark runtime or memory in this comparison.',
 'No downstream task-accuracy experiment is supplied.'
])
for pg,desc in [(1452,'One-hot identity and bag-of-words counts/limitations.'),(1455,'TF-IDF term-frequency definition.'),(1456,'Corpus document-frequency and IDF weighting.'),(1458,'Learned dense embeddings and cosine comparison.')]:cite('1451-Q01',pg,desc)
cite('1451-Q02',1452,'Bag-of-words loses word order and semantic context.');cite('1451-Q02',1466,'Context, pronoun and reference difficulties.')
opt('1454-Q04',2,'The fitted CountVectorizer automatically lemmatizes and merges grab with pick, but the printed table temporarily splits their shared column.','The source uses ordinary token-count columns; it does not declare a synonym-merging or lemmatizing analyzer.')
cite('1454-Q05',1462,'Complete-code hyperlink provides the official notebook whose zero-based cell 17 constructs the table.','statement')
qs['1454-Q05']['primaryEvidence']=[{'url':'https://github.com/robotics-lab-iitr/nptel-ai-robotics/blob/main/week10/week10_lecture46.ipynb','localPath':str(notebook.relative_to(R)),'sha256':hashlib.sha256(notebook.read_bytes()).hexdigest(),'locator':'Zero-based cell 17: pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out()).','savedEvidencePath':str(api.relative_to(R)),'savedEvidenceSha256':evidenceHash,'section':'countDataFrame','relationToLecture':'Exact notebook detail omitted from the shortened p1454 excerpt; linked by p1462.'}]
opt('1455-Q01',2,'2/3','This wrongly divides the two occurrences by the three distinct token types instead of four token occurrences.')
qs['1455-Q01']['solution']['formulas']=[formula('TF(t,d)=c(t,d)/L_d',{'t':'term','d':'document','c(t,d)':'number of occurrences of t in d','L_d':'total token occurrences in d','TF(t,d)':'length-normalized term frequency'},{'c,L_d':'counts','TF':'dimensionless'},['L_d > 0; use all supplied tokens without additional filtering.'])]
for n in ['1456-Q01','1456-Q02','1456-Q03']:
 qs[n]['solution']['formulas']=[formula('df(t)=Σ_d 1[c(t,d)>0]; IDF(t)=ln(N/df(t))',{'t':'term','d':'document','c(t,d)':'occurrences in document d','df(t)':'number of corpus documents containing t','N':'corpus document count','IDF(t)':'unsmoothed inverse document frequency'},{'c,df,N':'counts','IDF':'dimensionless'},['Natural logarithm; N > 0; the finite formula requires 1 ≤ df(t) ≤ N; df=0 is deliberately outside its domain.'])]
for n in ['1458-Q02','1469-Q03']:qs[n]['difficulty']='easy';qs[n]['difficultyRationale']='Direct substitution into a fully supplied formula with a short arithmetic calculation.'
opt('1458-Q05',3,'GloVe first computes document-level TF-IDF and takes each normalized document row as the word embedding, without fitting a word co-occurrence model.','This confuses document feature vectors with the learned word vectors and co-occurrence objective in the cited original paper.')
opt('1458-Q05',4,'GloVe fits global co-occurrence statistics, so cosine comparison of its learned vectors is invalid after training.','The training objective and a valid post-training comparison measure need not be identical.')
opt('1460-Q04',2,'The filtered five-token sequence preserves the original POS input positions because stopwords have no position in the sentence.','The original sequence has eight tokens, including up and two the occurrences; deleting them changes positions.')
opt('1460-Q04',4,'Pass only the unique sorted filtered words, because POS tagging uses the vocabulary rather than the ordered token occurrences.','The shown tagger receives an ordered sentence token list, not a unique sorted type list.')
opt('1461-Q02',3,'It is a proper-noun label that confirms light is the name of the box.','The displayed NN is a common-noun tag, not the NNP proper-noun category or proof of an object name.')
opt('1461-Q02',4,'It is an adjective-sense confidence score, so its presence confirms the lightweight interpretation.','The displayed output is a grammatical category label, not a confidence score or word-sense decision.')
opt('1461-Q03',2,'Yes; an adjective tag records which one of the two supplied adjectival senses is intended.','The stipulated senses share their grammatical category, so that tag cannot distinguish them.')
opt('1461-Q03',3,'No; the adjective tag is useful only for recognizing the object’s physical location, not its grammatical role.','The tag does indicate grammatical role; its limitation is incomplete sense resolution, not absence of linguistic information.')
qs['1461-Q03']['optionCountRationale']='Three distinct alternatives test sense labeling, grammatical-role information and the correct limitation.'
opt('1462-Q03',2,'The reported category proves the annotation scheme defines every indoor laboratory as a geopolitical entity.','One reported model label does not establish the annotation ontology or universal correctness.')
opt('1462-Q03',3,'The GPE label includes a calibrated confidence high enough to establish the intended navigation destination.','The displayed categorical output supplies neither a calibrated confidence nor a grounded metric destination.')
opt('1462-Q03',4,'Because the speaker used Lab3 as a destination, every valid entity recognizer must output exactly the same GPE label.','Different annotation schemes and models can represent such mentions differently; task use does not mandate this label.')
replace('1464-Q03',[
 'Clarify whether light means low mass or illuminated; after the user says low mass, select B, check feasibility, and use the updated observation after execution.',
 'Repeat ASR on the unchanged audio until the English word light disappears; select A because illumination is directly visible.',
 'Accept a VLM description naming B as sufficient proof that the pick action has already executed; omit action and state checks.',
 'Select B after clarification, but treat the predicted next visual state as the actual observation even if feedback shows that the grasp failed.'
],[
 'The linguistic ambiguity needs clarification; grounding then selects B, and action generation is distinct from execution and observed feedback.',
 'ASR and translation are stipulated correct; repeating transcription does not resolve the remaining sense ambiguity.',
 'A language description of the image is not a physical action or evidence that it happened.',
 'A predicted outcome is not a substitute for the observed post-action state, especially after failure.'
],stem='In an added multilingual robot case, ASR and translation are stipulated correct and yield “pick up the light box.” Box A is illuminated and heavy; B is unlit and lightweight; both are visible. Which sequence resolves the remaining ambiguity and correctly distinguishes VLM description, VLA action and feedback?',why='Correct transcription and translation do not settle every word sense. Clarification identifies low mass, the supplied scene grounds that request to B, and a validated action must be distinguished from a description and its observed result.')
qs['1464-Q03'].update(type='scenario',difficulty='medium',cognitiveSkill='synthesis',assumptions=['All scene facts and successful ASR/translation are supplied, not inferred model outputs.','The user clarifies that light means low mass; physical feasibility must be checked before execution.'])
for pg,desc in [(1445,'Lightweight versus illuminated word-sense ambiguity.'),(1465,'Speech recognition, language understanding, planning and execution pipeline.'),(1470,'Clarification, hallucination and instruction interpretation limits.'),(1471,'Image-plus-text model produces language descriptions.'),(1472,'Action prediction head, execution and updated embodied visual state.')]:cite('1464-Q03',pg,desc)
replace('1465-Q02',[
 'NLP extraction/understanding, then robot planning.',
 'Robot planning of a fixed motion first, then NLP only to assign a label to that finished plan.',
 'Speech synthesis of the transcript, followed directly by execution without interpreting its requested action.',
 'Map grounding alone, with the requested action and object relation left unresolved until after motion.'
],[
 'The diagram puts understanding before planning and execution.',
 'Planning the requested task requires interpretation, rather than merely labeling an already fixed plan.',
 'Repeating the text as audio does not supply its interpretation or a plan.',
 'Grounding a place is not sufficient to resolve the requested action and relation.'
])
replace('1465-Q03',[
 'Scene grounding or target selection failed after correct speech and intent processing.',
 'ASR substituted blue for red in the audio transcript.',
 'The intent parser interpreted pick up as put down.',
 'A correct red-ball target was selected, but the motor controller missed its planned trajectory.'
],[
 'The stipulated target ID already points to the blue ball, so the error occurs before otherwise accurate execution.',
 'The supplied transcript is correct and contains red.',
 'The supplied intent is explicitly pick(red ball), not put down.',
 'The executed trajectory reaches the selected blue-ball target accurately; the wrong target was chosen earlier.'
],stem='ASR correctly outputs “pick up the red ball,” the intent parser outputs pick(red ball), and the controller accurately reaches the selected target. Logs show that target ID refers to the blue ball. Which stage is directly implicated?',why='The evidence isolates an incorrect mapping from the understood object description to a scene object, not an ASR, action-intent or trajectory-tracking error.')
replace('1466-Q01',[
 'In “move the robot toward the shelf because it is cluttered,” resolving it requires relating the later description to the earlier candidates.',
 'In “pick the red box,” choosing a noun from two senses is fully solved by keeping the last token only.',
 'In “move left, then stop,” the later stop always cancels the earlier instruction rather than following it.',
 'In “put the cup on the tray beside the chair,” the nearest noun rule always determines which object is beside the chair.'
],[
 'This is the source’s context-dependent reference example.',
 'Keeping a single last token does not retain the action and descriptive context.',
 'The explicit then expresses a sequence, not a general cancellation rule.',
 'Attachment and relation interpretation require more than an unconditional nearest-noun rule.'
])
opt('1467-Q02',4,'The illustrated boldest link must carry more than 0.5 of the normalized attention mass.','A qualitative ranking or bold stroke supplies no calibrated absolute threshold or denominator.')
opt('1468-Q01',4,'move: action; robot: reference destination; shelf: the moved object with property cluttered.','The source moves the robot toward the shelf; this alternative swaps the object and reference roles.')
replace('1468-Q02',[
 'Attention relates context-dependent token information; training-data and parameter growth describe model scale.',
 'Increasing the number of training examples changes only the attention mechanism, while adding attention leaves the architecture unchanged.',
 'Model width is the attention weight assigned to each token, so a wider model means every contextual link has a higher probability.',
 'Parameter count directly specifies the current sentence’s token-to-token attention matrix, independently of the input.'
],[
 'Contextual interaction is a mechanism; data and parameter growth describe scale.',
 'More training data is a scaling change; introducing attention is an architectural/mechanistic change.',
 'Hidden width and input-dependent attention weights are different quantities.',
 'A parameter count is not the input-specific attention matrix or its entries.'
])
opt('1469-Q01',4,'At inference, append the correct future reference token after each prediction, even though no reference answer was supplied.','Using known reference tokens describes teacher-forced conditioning, not ordinary free autoregressive generation.')
opt('1469-Q04',3,'The candidate token w; the probability that all previously observed context would occur given it.','This reverses the direction of conditioning to a context-given-token likelihood.')
opt('1469-Q04',4,'The available context; a marginal probability p(w) that deliberately ignores which context was supplied.','A conditional distribution p(w|context) retains dependence on the specified context, unlike a marginal p(w).')
# Keep the reversed-conditional alternative distinct from the newly revised o3.
opt('1469-Q04',2,'The available context and next token jointly; their joint probability p(w,context) without normalization by the context probability.','The displayed expression is conditional, not the unnormalized joint probability.')
replace('1470-Q01',[
 'Ask “Do you mean the ball left of the tray or the ball right of it?” when those positions distinguish the two candidates.',
 'Ask “Is the target red?” when both candidates are already known to be red.',
 'Ask “Should I pick up a ball?” when the requested action and object class are already clear.',
 'Ask “Is it the round object?” when both candidates have the same round shape.'
],[
 'The supplied left/right distinction can identify the intended candidate.',
 'Confirming a shared color leaves both candidates possible.',
 'Repeating the agreed action and class does not distinguish the two targets.',
 'A shared shape does not resolve the target ambiguity.'
],stem='Two visually identical red balls lie left and right of a tray, and either fits “pick up the red ball.” Which clarification can distinguish the intended target using the supplied scene?')
replace('1470-Q03',[
 'Check the proposed action against the intended task and observed physical constraints before execution.',
 'Check only that the response parses as valid JSON, because syntax validity establishes the intended object and feasible path.',
 'Ask the same language model for a more confident explanation without comparing it with scene or task evidence.',
 'Check only that the object noun appears in the command, without verifying its scene identity or the requested spatial relation.'
],[
 'Grounding and physical/task checks address incorrect content and interpretation rather than just fluent output.',
 'Well-formed syntax does not establish meaning, grounding or feasibility.',
 'A second unsupported explanation is not independent grounding evidence.',
 'Matching a noun alone can still select the wrong instance or relation.'
])
opt('1471-Q01',2,'Encode the image and answer from image features alone, using the question only to format the finished answer.','The depicted model conditions its answer on image and question together, not just output formatting.')
opt('1471-Q01',3,'Encode only the text and use the raw image merely as a lookup label, without visual representations entering the language model.','The source explicitly maps visual tokens from the vision encoder into the language model.')
opt('1471-Q01',4,'Send predicted language tokens into the vision backbone to generate an image, rather than mapping input-image tokens into language processing.','This reverses the illustrated input-image encoding direction.')
opt('1471-Q02',3,'Mug has the largest shown value; renormalizing the four shown entries to sum to one proves omitted outcomes have zero probability.','Renormalizing a displayed subset changes the stipulated full distribution and discards its residual mass; the ellipsis leaves 0.01 unshown.')
opt('1472-Q02',4,'Use the predicted next scene as if it were a new camera observation, without checking the executed action’s outcome.','Prediction and observed post-action state are distinct; the figure depicts embodied execution and a visual-state update.')
replace('1472-Q03',[
 'It describes a representation choice used in many designs, not a requirement that every VLA use discrete action tokens.',
 'It states that every VLA must use a categorical action-token head and rules out continuous action decoders.',
 'It means each distinct token must correspond to a distinct physically achievable motion even when actuator limits are considered.',
 'It guarantees that increasing token resolution by itself increases actual actuator accuracy by the same factor.'
],[
 'The source says often, so its scope is a common design choice rather than a universal architecture rule.',
 'Often does not mean every design or exclude other output parameterizations.',
 'Representation labels do not by themselves establish feasibility under physical constraints.',
 'Representation resolution and actual control accuracy depend on different limits and uncertainties.'
])
def add(key,title,stem,opts,correct,exps,why,pages,typ='algorithm_trace',difficulty='medium',forms=None,assumptions=None):
 q=copy.deepcopy(qs['1446-Q02']);q.update(id=f'W10-L46-P{key}',version=1,status='draft',authorId=AUTHOR,stem=stem,type=typ,difficulty=difficulty,cognitiveSkill='synthesis',subtopic=title,tags=[key],conceptIds=[f'W10-L46-C-gap-{key}'],assumptions=assumptions or [],correctOptionIds=[f'o{correct}'],reviewIds=[])
 q['options']=[dict(id=f'o{i+1}',text=x) for i,x in enumerate(opts)];q['solution']=dict(justification=why,optionExplanations={f'o{i+1}':x for i,x in enumerate(exps)},steps=[],formulas=forms or [],simpleExplanation=why,memoryAid=None,misconceptions=[],examTraps=[],prerequisiteConceptIds=[]);q['citations']=[copy.deepcopy(qs['1446-Q02']['citations'][0])];qs[key]=q;b['questions'].append(q)
 b['concepts'].append(dict(id=q['conceptIds'][0],title=title,description=why,slideIds=[],questionIds=[q['id']],status='drafted',topic=q['topic'],subtopic=title,prerequisiteConceptIds=[],examinationAngles=[typ]))
 for pg,desc,kind in pages:cite(key,pg,desc,kind)
 q['citations']=[c for c in q['citations'] if c['physicalPage'] in [x[0] for x in pages]];return q
q=add('1449-Q05','Complete preprocessing and unfiltered POS paths','Apply the five stages to “Do NOT pick up the boxes near the boxes!”: lowercase, delete punctuation, split on spaces, remove only {do,the,up}, then map boxes→box and leave other tokens unchanged. One-hot input uses one one-word row per surviving token. A separate POS path only lowercases, deletes punctuation and splits the original string. Which trace is correct?',[
 'Lemmas [not,pick,box,near,box]; encoder input [[not],[pick],[box],[near],[box]]; the separate POS path retains all 9 token occurrences.',
 'Lemmas [pick,box,near,box]; encoder input has 4 one-word rows; not is removed automatically even though absent from the declared stop set.',
 'Lemmas [box,near,not,pick]; encoder input has 4 rows because repeated box tokens must be deduplicated before any encoding.',
 'Lemmas [not,pick,box,near,box]; encoder input is one row with 5 separate features; the separate POS path receives only these same 5 tokens.'
],1,[
 'Only declared stopwords are removed, the negation and repeated object remain, and separate unfiltered POS preprocessing retains function words.',
 'The supplied stop set does not contain not; deleting it changes the declared algorithm and can change meaning.',
 'The sequence preserves occurrence order and repeated tokens; fitting a vocabulary is not permission to deduplicate the input sequence.',
 'The source encoder has one categorical feature per word row, and the distinct POS path does not receive the filtered list.'
],'The supplied tables make every stage deterministic without downloading NLTK resources. The ordered lemma sequence is not the same object as a unique vocabulary or the separate POS input.',[(1446,'Five conceptual preprocessing stages.','statement'),(1449,'Ordered preprocessing code and intermediate outputs.','code'),(1453,'Nested one-word rows in OneHotEncoder input.','code'),(1460,'Separate unfiltered POS token path.','code')],assumptions=['These stopword and lemma rules are supplied exercise premises, not a claim about a fresh WordNet or POS execution.','Punctuation is deleted before space splitting; no empty tokens result.'])
q['solution']['steps']=['Lowercase: do not pick up the boxes near the boxes!','Delete punctuation: do not pick up the boxes near the boxes','Tokens: [do,not,pick,up,the,boxes,near,the,boxes]','Filter: [not,pick,boxes,near,boxes]','Lemmatize: [not,pick,box,near,box]; construct five one-word encoder rows.']
a=math.log(4/3);z=math.log(2);vecs=[[3*a/4,a/4,0],[a/2,0,z/2],[a/2,a/2,0],[0,9*a/10,z/10]];query=[a/2,0,z/2]
cos=lambda x,y:sum(v*w for v,w in zip(x,y))/math.sqrt(sum(v*v for v in x)*sum(v*v for v in y))
scores=[cos(v,query) for v in vecs];assert scores[1]>scores[0]>scores[2]>scores[3] and 3*a/4>z/10
forms=[formula('TF(t,d)=c(t,d)/L_d; df(t)=Σ_d 1[c(t,d)>0]; IDF(t)=ln(N/df(t)); w(t,d)=TF(t,d)IDF(t); cos(w,q)=(w·q)/(||w||₂||q||₂)',{'t':'term in fixed vocabulary [red,box,ball]','d':'one supplied document','c,L_d':'term count and total token count in d','df,N':'document frequency and training-corpus document count','w,q':'document and query TF-IDF vectors using training-corpus IDF'},{'counts':'token/document counts','weights and cosine':'dimensionless'},['No smoothing, additive constant, binary TF or sublinear TF; natural logarithm; query is not added to the four-document corpus.','No separate L2 normalization is needed before cosine; cosine itself divides by both norms.','Cosine is undefined for a zero vector; all supplied vectors are nonzero.'])]
q=add('1458-Q07','Integrated corpus weighting and cosine ranking','Use vocabulary [red,box,ball] and corpus d1="red red red box", d2="red ball", d3="red box", d4="box box box box box box box box box ball". Query q="red ball" is not added to the corpus. Use TF=count/document length, IDF=ln(4/df), no smoothing, and cosine similarity. Which descending document ranking and weight comparison are correct?',[
 'd2 > d1 > d4 > d3; w(red,d1) > w(ball,d4).',
 'd2 > d1 = d3 > d4; w(red,d1) > w(ball,d4).',
 'd2 > d1 > d3 > d4; w(red,d1) > w(ball,d4).',
 'd2 > d1 > d3 > d4; w(red,d1) < w(ball,d4) because ball is rarer.'
],3,[
 'The d4/d3 order here results from using raw dot products rather than cosine; the required normalization reverses that pair.',
 'Ignoring repeated red occurrences produces an equal-direction d1/d3 comparison, but the declared TF retains those occurrences.',
 'df=(3,3,2), cosine scores are approximately (0.363662,1,0.271057,0.238852), and the compared weights are 0.215762 and 0.069315.',
 'IDF rarity alone does not order TF-IDF weights across documents; the larger red term frequency outweighs the ball rarity in this comparison.'
],'Document frequency counts documents, TF keeps within-document multiplicity, and cosine compares direction after length normalization. A rarer term need not have the greater final weight.',[(1454,'Shared document vocabulary and count matrix.','code'),(1455,'Length-normalized term frequency.','equation'),(1456,'Document frequency and unsmoothed IDF.','equation'),(1458,'Cosine similarity equation.','equation')],typ='numerical',difficulty='hard',forms=forms,assumptions=['All documents, counts and conventions are added exercise premises; no pretrained embedding coordinates are inferred.'])
q['solution']['steps']=['df(red)=3, df(box)=3, df(ball)=2; let a=ln(4/3), b=ln 2.','w1=(3a/4,a/4,0), w2=q=(a/2,0,b/2), w3=(a/2,a/2,0), w4=(0,9a/10,b/10).',f'Cosines for d1 through d4: {scores}.','3a/4≈0.215762 exceeds b/10≈0.069315 despite ball having higher IDF.']
check={'checkedAt':now,'independentReview':False,'checks':{'wordnetSignatureTextOnly':True,'notebookCell17TextRead':True,'df':[3,3,2],'vectors':vecs,'query':query,'cosines':scores,'ranking':[2,1,3,4],'rawDotRanking':[2,1,4,3],'weightComparison':[3*a/4,z/10],'orderedLemmas':['not','pick','box','near','box'],'posInputLength':9},'noCorpusDownload':True,'noCorpusDependentExecution':True}
(R/'audits/W10-L46-v2-author-checks.json').write_text(json.dumps(check,indent=2)+'\n')
new=['1449-Q05','1458-Q07']
for n in changed:
 q=qs[n];q.update(version=2,status='draft',reviewIds=[]);q.setdefault('revisionAuthors',[]).append(AUTHOR)
 if 'conflictResolution' in q:q['conflictResolution']['questionVersion']=2
for n in changed+new:
 q=qs[n];q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']]
 for co in b['concepts']:
  if co['id'] in q['conceptIds']:co['examinationAngles']=list(dict.fromkeys(co['examinationAngles']+[q['type']]))
for q in b['questions']:
 if q['id'] in accepted:assert question_hash(q)==accepted[q['id']],q['id']
schema=json.loads((R/'data/schema.question.json').read_text());errors={q['id']:schema_errors(q,schema) for q in b['questions'] if schema_errors(q,schema)};assert not errors,errors
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');packet=[]
for n in changed+new:
 q=qs[n];x={k:copy.deepcopy(q[k]) for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
pf=R/'audits/blind-W10-L46-v2-and-gaps.json';pf.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
m=dict(frozenAt=now,author=AUTHOR,independentVerification=False,packet=str(pf.relative_to(R)),packetSha256=hashlib.sha256(pf.read_bytes()).hexdigest(),revisedCount=35,newQuestionCount=2,totalCount=92,preservedAcceptedQuestionHashes=accepted,questionHashes={qs[n]['id']:question_hash(qs[n]) for n in changed+new},gapDispositions={'G01':'P1449-Q05 full preprocessing, negation, repetition, nested rows and separate POS input','G02':'P1458-Q07 integrated corpus weighting/cosine/ranking and TF versus rarity','G03':'P1464-Q03 v2 integrated multilingual clarification, scene grounding, action and feedback'},sourceReinspection={'pages':[1446,1449,1453,1458,1462,1466,1471,1472],'method':'Actual rendered source pages viewed during repair.'},notes=['All 55 accepted question hashes preserved.','No downloaded corpus, pretrained model or fresh corpus-dependent outputs claimed.'])
(R/'audits/W10-L46-v2-repair-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:m[k] for k in ['packetSha256','revisedCount','newQuestionCount','totalCount']}))
