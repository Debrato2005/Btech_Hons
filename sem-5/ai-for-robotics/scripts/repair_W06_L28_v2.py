#!/usr/bin/env python3
"""Repair 42 L28 quality flags and five bounded angles; preserve all 27 accepted hashes."""
import copy,datetime,hashlib,json,sys,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from authoring_helpers import SHA
from validate import question_hash,schema_errors
P=R/'data/question-batches/W06-L28.json';A=R/'audits/batch-history/W06-L28-v1-before-repairs.json';A.parent.mkdir(exist_ok=True)
if not A.exists():A.write_bytes(P.read_bytes())
old=json.loads(A.read_text());data=copy.deepcopy(old);qs={q['id']:q for q in data['questions']}
summary=json.loads((R/'audits/W06-L28-v1-independent-summary.json').read_text());flagged={f['questionId'] for f in summary['findings']}
review=json.loads((R/'data/reviews/W06-L28-v1-independent.json').read_text());rows=review.get('reviews',[]) if isinstance(review,dict) else review
approved={r['questionId']:r['questionSha256'] for r in rows if r['decision']=='verified'}
AUTHOR='build_offline_study_interface:L28-v2-revision-author'
assert len(flagged)==42 and len(approved)==27
for item in json.loads(P.read_text())['questions']:
 if item['id'] in approved:assert question_hash(item)==approved[item['id']]
 else:assert item['version']==1 or (item['version']==2 and AUTHOR in item.get('revisionAuthors',[])),item['id']
for id in flagged:
 item=qs[id];item.update(version=2,status='draft',reviewIds=[]);item['revisionAuthors']=list(dict.fromkeys(item.get('revisionAuthors',[])+[AUTHOR]))
def q(n):return qs[f'W06-L28-Q{n:03d}']
def opt(n,oid,text,why):
 item=q(n);next(o for o in item['options'] if o['id']==oid)['text']=text;item['solution']['optionExplanations'][oid]=why

def why(n,text):q(n)['solution']['justification']=q(n)['solution']['simpleExplanation']=text

def citation(page,kind,locator,role='premise',region=None):
 return {'slideId':f'lectures-p{page:04d}','sourceId':'lectures','sourceSha256':SHA,'physicalPage':page,'kind':kind,'locator':f'Lecture 28, physical PDF page {page}, actual printed footer {page-821}: '+locator,'evidenceText':(R/f'sources/text/lectures/page-{page:04d}.txt').read_text().strip(),'role':role,'region':region}
for n in [9,18,21,31,36,45,49,55,62]:q(n)['difficulty']='easy'
# Q039 is extended to a multi-claim figure diagnostic rather than a direct styling lookup.
q(39)['difficulty']='medium'
opt(1,'o3','Python is preferred mainly because its scientific packages remove the need to consider algorithm choice and data preparation.','The ecosystem provides tools, but choosing algorithms and preparing data remain part of the workflow.')
opt(1,'o4','Python is preferred mainly because source code must be fully recompiled before each exploratory experiment, enforcing a fixed workflow.','The lecture emphasizes interactive iteration, not mandatory recompilation or a fixed exploratory sequence.')
# Parallel role permutations, with the same three tools in every option.
opt(3,'o1','NumPy supplies notebooks, matplotlib supplies arrays, and IPython/Jupyter supplies plots.','This cycles all three primary responsibilities into the wrong roles.')
opt(3,'o2','NumPy supplies arrays, matplotlib supplies notebooks, and IPython/Jupyter supplies the plotting library.','The array role is correct, but the plotting and interactive-environment roles are swapped.')
# Extend an existing flagged notebook question to test both missing document/kernel angles.
q(6).update(stem='Select every statement that correctly distinguishes notebook execution, supported languages and the saved notebook document in the lecture.',selectionMode='multi',correctOptionIds=['o1','o2','o4'],subtopic='Notebook execution, language support and saved state',difficulty='medium',type='conceptual',cognitiveSkill='conceptual')
opt(6,'o1','Jupyter can support multiple programming languages through suitable kernels, although this course uses Python.','The source explicitly distinguishes general language support from its chosen course language.')
opt(6,'o2','A saved .ipynb JSON file can contain code and displayed output without preserving the live kernel’s variable bindings.','The document and the running kernel are distinct forms of state.')
opt(6,'o3','Opening a saved output cell restores the live variables that produced it, even after the kernel has been restarted.','Saved display data do not execute the earlier code or recreate cleared variable bindings.')
opt(6,'o4','The browser submits cell code through the server to a kernel, and the returned result is displayed in the notebook.','This is the execution path in the source.')
why(6,'The source separates three layers: a notebook interface can use suitable kernels for multiple languages; a server sends submitted code to its selected kernel; and the .ipynb JSON document stores code and outputs rather than preserving a live session. A kernel restart clears variables even when prior output remains visible.')
q(6)['citations']=[citation(828,'statement','Bullet stating support for many languages while the course uses Python.'),citation(829,'statement','How-to-interact bullets; one-kernel/restart paragraph; final .ipynb JSON output-storage bullet.')]
q(7)['citations']=[citation(829,'statement','Kernel restart clears variables; cells may be rerun in any order while live state is preserved.')]
q(7)['assumptions'].append('The x assignments are an explicitly added execution trace, not code printed on this source page.')
opt(9,'o2','Yes; sparse input acceptance applies only after the user creates a dense copy with the same numerical values.','The stem explicitly says the API accepts the sparse input; mandatory prior densification does not follow.')
opt(9,'o3','Yes; converting to dense is always a safe memory optimization for zero-heavy matrices.','Densification can substantially increase storage for zero-heavy data.')
opt(9,'o4','No; accepting one sparse format guarantees acceptance of every sparse format without checking the API.','Supported formats and conversion behavior remain API-specific.')
opt(14,'o3','eye(4) has four diagonal ones, while ones((2, 5)) has only two diagonal ones and zeros elsewhere.','The identity description is correct, but ones fills all ten entries, not just a diagonal.')
opt(18,'o3','The normal array has shape (4, 100), and the integer array has shape (4, 6), because size lists columns before rows.','The requested shapes are used in their written axis order, not reversed.')
# Extend scientific-library question with a task-dependent sparse construction/operation comparison.
q(24).update(stem='A SciPy workflow needs optimization/statistical routines, then builds a sparse feature matrix from row-column-value triples and performs repeated row-oriented arithmetic. Which representation plan best matches the lecture, without claiming a universal speed winner?',subtopic='Scientific algorithms and sparse format stages',difficulty='medium',type='scenario',cognitiveSkill='application')
opt(24,'o1','Use SciPy for the scientific routines, CSR as the coordinate-triple construction format, and COO as the preferred row-oriented arithmetic format.','This reverses the lecture’s coordinate-construction versus compressed-row-operation comparison.')
opt(24,'o2','Use SciPy for the scientific routines, COO for convenient coordinate-triple construction, and consider CSR for repeated row-oriented arithmetic.','This matches the roles while leaving actual performance dependent on the task.')
opt(24,'o3','Use SciPy for the routines, convert triples to a dense ndarray first, and require that dense form before any sparse matrix can be constructed.','COO can be constructed directly from coordinate triples; a dense intermediate is not required.')
opt(24,'o4','Use SciPy for the routines and keep COO for every stage because coordinate storage is guaranteed to minimize time and memory for all operations.','The format comparison is task-dependent; no universal time/memory guarantee follows.')
why(24,'SciPy provides the scientific routines and sparse representations. COO directly records data with row/column coordinates and is convenient for construction. CSR organizes compressed rows and can suit repeated arithmetic or row-oriented access. Conversion and measured workload costs matter; neither format is universally fastest or smallest.')
q(24)['citations']=[citation(836,'statement','SciPy scientific routines and sparse-matrix discussion.'),citation(837,'statement','CSR compressed-row arithmetic and storage discussion.','conflict'),citation(838,'statement','COO construction from Row, Column and Number and convenient construction/addition discussion.')]
q(24)['conflictResolution']={'status':'explicit-qualification-awaiting-independent-review','sourceId':'lectures','sourceSha256':SHA,'physicalPages':[837],'sourceClaim':'CSR is called incredibly fast and significantly memory-saving without workload/density qualifications.','basis':q(24)['solution']['justification'],'method':'Retain the pedagogical format comparison while explicitly rejecting universal time or memory dominance.'}
opt(29,'o2','An Axes contains the entire Figure, while each subplot is a separate Figure nested inside that Axes.','This reverses the container hierarchy: a Figure can contain multiple Axes.')
opt(29,'o3','The Figure and Axes describe plot layout, but lines and text are not Artists until the image is saved.','Lines and text are in-memory Artist objects before saving; saving is not what creates that role.')
opt(29,'o4','A Figure is the overall container, but its x-axis and y-axis are the two Axes returned by any two-subplot layout.','An Axes is a plotting region with axes, not one axis direction; two subplots are two plotting regions.')
opt(30,'o2','plt.scatter for the connected loss curve and plt.plot for the unconnected feature cloud.','These primary choices reverse the stated line-versus-point roles unless extra styling changes are made.')
opt(30,'o3','plt.hist for the loss curve and plt.scatter for the feature points.','The scatter role is correct, but a histogram bins loss values rather than connecting them by epoch.')
# Make the comparison explicitly about the primary defaults, not possible configurable alternatives.
q(30)['stem']='Using the primary roles in the lecture’s function table rather than adding custom styling, you want a connected loss-versus-epoch curve and unconnected points for two measured features. Which calls match those needs?'
opt(31,'o1','The figure has two side-by-side plotting regions, and applying the x-limit permanently deletes input values outside [0,10].','The layout is correct, but limits change the view rather than deleting source data.')
opt(31,'o2','The figure has two vertically stacked plotting regions, and the x-limit changes only the visible x-range.','The view interpretation is correct, but subplots(1,2) means one row and two columns.')
opt(31,'o4','The figure has two vertically stacked plotting regions, and applying the x-limit permanently deletes input values outside [0,10].','Both the row/column interpretation and deletion claim are incorrect.')
opt(33,'o3','plt.scatter with the observation index on the horizontal axis.','This shows individual residuals in observation order rather than interval frequencies.')
opt(33,'o4','plt.boxplot of the residuals.','A box plot summarizes quartiles and potential outliers rather than displaying counts in value intervals.')
opt(34,'o2','A legend for both plots, interpreting each distinct numerical color shade as a separate named series.','Named-series legends and a continuous numerical color scale serve different purposes.')
opt(34,'o3','A colorbar for both plots, treating the model-name labels as positions on a continuous numerical scale.','The named model curves are categorical series rather than a continuous mapped numerical variable.')
# Extend the flagged sine item into a real source-code/figure agreement question.
q(35).update(stem='The source plots x=np.linspace(−10,10,100), y=np.sin(x) with marker="x". Using radians and sin(10)≈−0.544, which description agrees with both the code and the displayed curve?',type='diagram',cognitiveSkill='application',difficulty='medium',subtopic='Sine code, endpoint signs and plotted markers')
opt(35,'o1','The left endpoint is approximately −0.544 and the right endpoint +0.544, with x-shaped markers at all sampled points.','This reverses the sine endpoint signs; sin(−10)=−sin(10).')
opt(35,'o2','Both endpoints are approximately +0.544, with x-shaped markers at all sampled points.','Sine is odd, not even, so the endpoints have opposite signs.')
opt(35,'o3','The left endpoint is approximately +0.544 and the right endpoint −0.544; values lie within [−1,1], and x-shaped markers denote the sampled points.','This matches the odd sine function, its amplitude bound and the actual marked curve.')
opt(35,'o4','The endpoint signs are +0.544 then −0.544, but x-shaped markers are placed only at zero crossings.','marker="x" marks sampled data points, not only zeros.')
why(35,'The endpoints of linspace are −10 and 10 radians. Since sine is odd, sin(−10)=−sin(10)≈+0.544, while the right endpoint is approximately −0.544. Sine remains within [−1,1]. The displayed curve agrees and has x-shaped markers at the 100 sampled points, not just zero crossings.')
q(35)['solution']['steps']=['Use the supplied sin(10)≈−0.544.','Odd symmetry gives sin(−10)≈+0.544.','Compare the opposite endpoint signs and bounded oscillation with the actual figure; marker="x" styles each sampled point.']
q(35)['assumptions']=['The NumPy sine arguments are radians; the supplied numerical sine value is sufficient for the endpoint comparison.']
q(35)['citations']=[citation(842,'code','Lines 6, 8 and 11: linspace, sine calculation and marker argument.'),citation(842,'figure','Upper-right sine curve: left/right endpoints, vertical range near −1 to +1, and x-shaped sample markers.',region={'x':.625,'y':.14,'width':.335,'height':.43})]
opt(38,'o2','X_cls[:,0] supplies vertical coordinates; c=y_cls supplies colors from labels.','The colors are correct, but the second scatter positional argument is X_cls[:,1], not column 0.')
opt(38,'o3','X_cls[:,1] supplies vertical coordinates; c=X_cls[:,0] supplies colors from the first feature.','The coordinate is correct, but the displayed code colors by y_cls, not a feature column.')
# Extend the styling item to an active overlap diagnostic without inventing classifier accuracy.
q(39).update(stem='Inspect the actual two-class scatter plot and its code using c=y_cls, cmap="bwr", edgecolors="k" and alpha=0.8. Select every supported statement.',selectionMode='multi',correctOptionIds=['o1','o3'],type='diagram',cognitiveSkill='application',subtopic='Scatter styling, overlap and limits of inference')
opt(39,'o1','Red and blue points occupy some overlapping spatial regions; this plot of supplied labels alone does not establish a trained classifier’s accuracy.','The visible overlap is a data diagnostic, not a measured prediction result.')
opt(39,'o2','Visible overlap proves that every possible classifier must make exactly the same number of errors as the overlapping colored points.','No classifier, decision boundary or exact test-error count is supplied by this plot.')
opt(39,'o3','The colorbar maps class 0 to blue and class 1 to red; the points have black outlines and partial opacity.','This matches the actual endpoint colors and the k/alpha styling arguments.')
opt(39,'o4','The colorbar maps class 0 to red and class 1 to blue; black outlines and partial opacity leave that reversed endpoint mapping unchanged.','The styling clause is correct, but the actual colorbar endpoints are blue at 0 and red at 1.')
why(39,'The actual plot places blue class-0 and red class-1 samples in two feature coordinates, with some spatial overlap. The code supplies these labels directly through c=y_cls, black edges through edgecolors="k", and opacity 0.8. This is a visualization of labeled data, not a trained classifier or an accuracy measurement.')
q(39)['citations']=[citation(843,'code','scatter arguments X_cls columns, c=y_cls, bwr, black edges, linewidths and alpha.'),citation(843,'figure','Upper-right scatter cloud and class colorbar: blue-0/red-1 endpoints, black outlines and mixed red/blue regions near the center.',region={'x':.615,'y':.055,'width':.37,'height':.555})]
opt(40,'o1','xlim/ylim, text, show.','The note and display calls fit, but limits set viewing ranges rather than axis descriptions.')
opt(40,'o3','xlabel/ylabel, title, show.','The axis descriptions and display fit, but a title is not a note placed at data coordinates.')
opt(40,'o4','xlabel/ylabel, legend, show.','A legend identifies labeled series; it is not the coordinate-placed note requested.')
opt(41,'o3','A DataFrame stores column dtypes, but its row labels must always be consecutive integers and cannot be chosen explicitly.','DataFrames support labeled indexes, not only an immutable consecutive integer index.')
opt(47,'o1','r is the displayed table as an HTML string, while s is the printed summary as a text string.','Visible representations do not imply those return values; both ordinary calls return None.')
opt(47,'o2','r is None, but s is a DataFrame listing the summary’s non-null counts and dtypes.','info prints its summary and returns None, not a summary DataFrame.')
opt(49,'o4','Only whether both constructors accept the same random_state keyword; matching that keyword is enough for interchangeability.','One shared parameter does not establish input, method, preprocessing or evaluation compatibility.')
opt(50,'o1','An algorithm’s configuration only; calling fit must return a separate model while leaving the original estimator unchanged.','The usual source contract fits the estimator and returns self, so learned state belongs to the object.')
opt(50,'o2','Only the learned model values; the configuration used to construct the estimator is not part of the object.','The source describes configuration together with learned information.')
opt(50,'o3','A fully trained model immediately after construction, with fit used only to calculate its score.','Construction configures the estimator; fit learns from data, while score evaluates.')
opt(51,'o1','StandardScaler is an unsupervised clustering estimator; KNeighborsClassifier is a preprocessing estimator.','Scaling is preprocessing rather than clustering, and KNN here is supervised classification.')
opt(51,'o2','StandardScaler is a supervised label predictor; KNeighborsClassifier is an unsupervised clustering estimator.','Neither role matches the Iris workflow.')
opt(55,'o1','transform refits state from X and returns transformed data; fit_transform reuses previously learned state without fitting.','This reverses the fitting versus reuse distinction.')
opt(55,'o4','transform applies learned state and returns only self; fit_transform fits state but returns only self without transformed data.','Both operations return the transformed representation under the stated transformer contract, not just self.')
opt(60,'o4','Fitting on the test features is harmless whenever their target labels are hidden, because preprocessing cannot leak information.','Held-out feature statistics can leak through preprocessing even without test labels.')
opt(66,'o1','Prepare the table with pandas, fit scaling on all data before splitting, train/evaluate the classifier on the resulting partitions, and plot diagnostics with matplotlib.','Most tool roles fit, but learning scaling from all data leaks held-out information before the split.')
opt(66,'o2','Prepare the table with pandas, fit one scaler on training data and another on held-out data, train/evaluate the classifier across those separately scaled sets, and plot diagnostics with matplotlib.','Separate fitted scalers create inconsistent feature coordinate systems and use held-out statistics.')
opt(66,'o3','Prepare the table with pandas, fit scaling on training data, fit the classifier on transformed training data but evaluate it on unscaled held-out inputs, and plot diagnostics with matplotlib.','The classifier is evaluated in a different representation from the one used for training.')
opt(67,'o1','Numerical optimization, scientific integration, statistical distributions and sparse-matrix formats as the listed primary NumPy role.','These are the more advanced SciPy roles emphasized in the lecture’s distinction, not its listed NumPy capability group.')
opt(67,'o2','Labeled table joins, missing-record wrangling, CSV ingestion and column-index alignment as its primary role.','These are the pandas-oriented tasks in the lecture’s role comparison.')
opt(67,'o4','Classifier fitting, cross-validation, probability prediction and estimator pipelines as its primary role.','These are scikit-learn workflow roles rather than the source’s NumPy capability list.')
opt(69,'o2','Supervised learning, unsupervised learning, preprocessing and dataset-loading utilities.','Dataset loading is a utility role, not the fourth estimator category named in the source; meta-estimators are omitted.')
opt(69,'o3','Supervised learning, unsupervised learning, metric functions and meta-estimators.','Metric functions are not the listed preprocessing category.')
opt(69,'o4','Supervised learning, train/test split utilities, preprocessing and meta-estimators.','Splitting utilities do not replace the named unsupervised-learning category.')
# Correct citation kinds and locators only on flagged objects. Accepted objects remain untouched.
TABLES={826:'Library table: named Library, Main Role and Typical Use columns.',840:'Function table rows plot, scatter, subplots, xlabel/ylabel and xlim/ylim.',841:'Function table rows legend, show, text, semilogy, hist and colorbar.',845:'NumPy versus pandas comparison table: structure, dtype and workflow columns.',847:'pandas function table: display/head/tail/dtypes/info, bracket selection and iloc rows.',850:'Estimator API table: fit, predict, predict_proba, score, transform and fit_transform rows.'}
for id in flagged:
 item=qs[id]
 for c in item['citations']:
  p=c['physicalPage']
  if p in TABLES:c['kind']='table';c['locator']=f'Lecture 28, physical PDF page {p}, actual printed footer {p-821}: '+TABLES[p]+' Relevant operation: '+item['subtopic']+'.'
  if item['id']=='W06-L28-Q059' and p==851:
   c['kind']='statement';c['role']='conflict';c['locator']='Lecture 28, physical PDF page 851, actual printed footer 30: right-hand StandardScaler bullet claiming average zero and spread one.'
  if item['id']=='W06-L28-Q059' and p==852:
   c['kind']='code';c['role']='premise';c['locator']='Lecture 28, physical PDF page 852, actual printed footer 31: fit_transform on X_train and transform on X_test/new_sample.'
 item['solution']['misconceptions']=[item['solution']['optionExplanations'][o['id']] for o in item['options'] if o['id'] not in item['correctOptionIds']]
# Identify only the relevant table rows, not an entire generic table locator.
ROW_LOCATORS={
(2,826):'Library table rows pandas, SciPy and scikit-learn; Main Role and Typical Use columns.',
(3,826):'Library table rows NumPy, matplotlib and IPython/Jupyter; numerical arrays, plots and interactive exploration roles.',
(30,840):'Function table rows plot and scatter: connected line versus point display.',
(31,840):'Function table rows subplots and xlim/ylim: Figure/Axes layout and viewing limits.',
(32,841):'Function table row semilogy: logarithmic vertical scale.',
(33,841):'Function table row hist: value-frequency distribution.',
(34,841):'Function table rows legend and colorbar: named series versus numerical color scale.',
(40,840):'Function table row xlabel/ylabel: axis descriptions.',
(40,841):'Function table rows text and show: coordinate-placed note and display.',
(41,845):'NumPy/pandas table rows on homogeneous array dtype versus column-specific table types and typical workflow roles.',
(43,847):'pandas function table rows head(n) and tail(n).',
(45,847):'pandas function table rows scalar-column bracket selection and list-of-columns selection.',
(46,847):'pandas function table row iloc[1,2], including printed uppercase Data_pandas identifier.',
(47,847):'pandas function table rows display(data_pandas) and data_pandas.info(), distinguishing visible output from return values.',
(48,847):'pandas function table row data_pandas.dtypes and object-dtype explanation.',
(51,850):'Estimator API table rows fit, predict and transform, in conjunction with the Iris preprocessing/classification code.',
(52,850):'Estimator API table row fit(X,y), Returns column self.',
(53,850):'Estimator API table rows predict(X) and predict_proba(X), single-output-classification return shapes.',
(54,850):'Estimator API table row score(X,y), default-metric interpretation.',
(55,850):'Estimator API table rows transform(X) and fit_transform(X).',
(65,850):'Estimator API table rows predict_proba, score, transform and fit_transform: capabilities and return contracts.',
(66,826):'Library table rows pandas, scikit-learn and matplotlib: preparation, modeling and plotting responsibilities.',
(66,850):'Estimator API table rows fit, transform and score: training state, representation reuse and evaluation.',
(68,847):'pandas function table row data_pandas.info(): column/non-null/dtype/memory summary.'}
for (n,p),loc in ROW_LOCATORS.items():
 for c in q(n)['citations']:
  if c['physicalPage']==p:c['locator']=f'Lecture 28, physical PDF page {p}, actual printed footer {p-821}: '+loc
# Update the four expanded concepts in place; no invented extra unique-concept claim.
for n in [6,24,35,39]:
 item=q(n)
 for c in data['concepts']:
  if c['id'] in item['conceptIds']:
   c['title']=c['subtopic']=item['subtopic'];c['description']=item['solution']['justification'];c['slideIds']=list(dict.fromkeys(x['slideId'] for x in item['citations']));c['examinationAngles']=list(dict.fromkeys(c['examinationAngles']+[item['type'],'bounded gap synthesis']))
for id,h in approved.items():assert question_hash(qs[id])==h,id
assert data['sourceIssues']==old['sourceIssues'] and len(data['sourceIssues'])==14
# Preserve the original frozen artifacts and publish current revision metadata separately.
ins_path=R/'data/inspection-batches/W06-L28.json';ins=json.loads(ins_path.read_text())
for s in ins['slides']:s['conceptIds']=[c['id'] for c in data['concepts'] if s['id'] in c['slideIds']]
for typ,entries in [('question',data['questions']),('concept',data['concepts']),('slide',ins['slides'])]:
 errors=[e for item in entries for e in schema_errors(item,json.loads((R/f'data/schema.{typ}.json').read_text()))];assert not errors,(typ,errors)
P.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');ins_path.write_text(json.dumps(ins,ensure_ascii=False,indent=2)+'\n')
packet=[];revisions=[item for item in data['questions'] if item['id'] in flagged]
for item in revisions:
 a={k:copy.deepcopy(item[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in a['citations']:c.pop('evidenceText',None)
 packet.append(a)
packetpath=R/'audits/blind-W06-L28-v2.json';packetpath.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
manifest={'batchId':'W06-L28','revisionAuthor':AUTHOR,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revisedQuestionCount':len(revisions),'preservedApprovedCount':len(approved),'preservedApprovedHashes':approved,'sourceIssuesPreserved':True,'sourceIssueCount':14,'blindPacketPath':str(packetpath.relative_to(R)),'blindPacketSha256':hashlib.sha256(packetpath.read_bytes()).hexdigest(),'revisions':[{'questionId':item['id'],'questionVersion':item['version'],'questionSha256':question_hash(item)} for item in revisions],'coverageRepair':{'Q006':'Multiple kernel languages and saved JSON versus live session, retaining execution path.','Q024':'COO construction versus task-dependent CSR operations, retaining scientific-routine scope.','Q035':'Sine code-to-figure agreement: endpoint signs, amplitude and markers.','Q039':'Actual class overlap and no classifier/accuracy inference, retaining styling.'},'independentReviewRequired':True}
manifest['artifactSha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [P,packetpath,ins_path,A,Path(__file__)]}
(R/'audits/W06-L28-v2-repair-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
coverage=json.loads((R/'audits/W06-L28-author-coverage-ledger.json').read_text())
for row in coverage['pages']:
 sid=row['slideId'];row['conceptIds']=[c['id'] for c in data['concepts'] if sid in c['slideIds']];row['questionIds']=[item['id'] for item in data['questions'] if any(c['slideId']==sid for c in item['citations'])]
coverage['status']='Version 2 author proposal after independent review: 27 accepted exact hashes preserved; 42 revisions and five bounded angles require independent re-review.'
coverage['boundedGapQuestionIds']=['W06-L28-Q006','W06-L28-Q024','W06-L28-Q035','W06-L28-Q039']
(R/'audits/W06-L28-author-coverage-ledger-v2.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:manifest[k] for k in ['revisedQuestionCount','preservedApprovedCount','blindPacketSha256','coverageRepair']}))
