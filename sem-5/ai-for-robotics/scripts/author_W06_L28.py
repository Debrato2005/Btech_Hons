#!/usr/bin/env python3
"""L28 author proposal after actual full-page inspection. Never self-verify."""
import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from authoring_helpers import DraftBatch,formula,SHA
from validate import schema_errors,question_hash
AUTHOR='build_offline_study_interface:L28-author';BATCH='W06-L28'
b=DraftBatch(BATCH,6,'L28','Libraries and tools for ML implementation in Python',822,AUTHOR)
INSPECTED_AT='2026-10-19T19:08:35+00:00'
NOTES={
822:('Lecture 28 title and attribution.','Title only.'),
823:('Objectives cover libraries, arrays, sparse matrices, plots, pandas and estimator API.','Objectives roadmap; substantive content is covered on later pages.'),
824:('Contents list the same library sections.','Contents roadmap only.'),
825:('Python is motivated by ecosystem depth, interactive experimentation, general-purpose use and community, not raw execution speed. Named companies are illustrative examples, not verified current adoption claims.',None),
826:('Six-row table links NumPy to numerical arrays/linear algebra; SciPy to scientific algorithms, optimization and sparse data; matplotlib to visualization; pandas to wrangling; scikit-learn to models/evaluation/pipelines; IPython/Jupyter to interactive exploration/reports.',None),
827:('Heading says install libraries not pre-installed in Colab, but all seven lines are import statements: numpy as np, scipy as sp, matplotlib, matplotlib.pyplot as plt, pandas as pd, IPython, sklearn. Imports do not install missing packages; runtime availability is not established.',None),
828:('Notebooks interleave code, text and images and support interactive, multilingual exploration. Colab cloud hosting and possible accelerator access are described; resource availability is not guaranteed.',None),
829:('Browser cell sends code through server to kernel; results return to browser. Kernel keeps variables between cells; restart clears live state. Notebook JSON may retain code, text and stored outputs, which are distinct from live variables.',None),
830:('NumPy ndarray supports multidimensional numerical arrays, mathematics, linear algebra, Fourier transforms and random sampling. One dtype per ndarray is not a claim that an object array contains only one Python object class. The claimed universal explicit conversion of all ML input to dense NumPy is too broad.',None),
831:('Code creates [[1,2,3],[4,5,6]]; output shape (2,3), dtype int64, ndim 2, size 6 and strides (24,8) bytes. Exact integer width/strides depend on dtype/platform and layout.',None),
832:('Constructors: zeros((3,4)), ones((2,5)), eye(4), full((3,3),7.0), empty((100,4)). Empty allocates without initializing numeric contents; no random distribution or zero guarantee.',None),
833:('Code: arange(0,10,0.5), linspace(0,2*pi,500), default_rng(seed=42), standard_normal((100,4)), integers(0,100,size=(6,4)). Arange comment says float-safe, which is not a general precision guarantee. Seed and draw history both matter.',None),
834:('Fresh default_rng(seed=42) produces 6 by 4 integer X. Code selects X[0], X[:,2], X[1:4,0:2], X[[0,2,5],:], masks X[:,0]>50 and filters X[mask]. Strict comparison excludes the row whose first entry is 50.',None),
835:('All printed results inspected: X rows [8,77,65,43], [43,85,8,69], [20,9,52,97], [73,76,71,78], [51,12,83,45], [50,37,18,92]. Mask [False,False,False,True,True,False]; filtered rows have leading entries 73 and 51. Repeated code results are linked rather than padded.',None),
836:('SciPy scientific algorithms include advanced linear algebra, optimization, signal processing, mathematical functions and statistical distributions. Sparse matrices represent zero-heavy data; benefits depend on matrix structure and operations.',None),
837:('np.eye(4) is converted with sparse.csr_matrix(eye). Output has four diagonal 1.0 entries. CSR also stores column indices and row pointers; only nonzero and universal memory/speed claims require qualification, especially for explicit zeros and small matrices.',None),
838:('COO arrays are four 1.0 values with row/column indices [0,1,2,3], giving a 4 by 4 identity. Literal print("COO representation:\\n{}",eye_coo) does not format braces, unlike the displayed output. Constructor triples and output coordinates inspected.',None),
839:('Figure is the overall container; Axes is a plotting region; Artists include lines, text, ticks and patches. Figure and Axes are themselves Artist subclasses, so these are not disjoint object types.',None),
840:('Function table: plot, scatter, subplots, xlabel/ylabel, xlim/ylim. Limits set visible ranges rather than deleting observations.',None),
841:('Function table: legend, show, text, semilogy, hist, colorbar. Legend identifies series; colorbar maps numeric values to colors. Semilogy uses logarithmic y, not x.',None),
842:('Literal notebook magic %matplotlib inline; imports pyplot and NumPy; x=linspace(-10,10,100), y=sin(x), plot(x,y,marker="x"). Plot shows oscillatory sine with marked samples. Comment says 100 steps, but there are 100 samples and 99 adjacent intervals. Notebook magic is not standalone Python syntax.',None),
843:('make_classification(n_samples=200,n_features=2,n_redundant=0,random_state=0); scatter(X_cls[:,0],X_cls[:,1],c=y_cls,cmap="bwr",edgecolors="k",linewidths=0.5,alpha=0.8). Labels, title, class colorbar, tight_layout and show. Graph has blue class 0, red class 1, black edges and some overlap; color is supplied labels, not learned predictions.',None),
844:('pandas DataFrame is a labeled table with column-specific types; CSV, SQL and Excel ingestion, cleaning and exploratory analysis are emphasized.',None),
845:('NumPy-versus-pandas table contrasts a single ndarray dtype with column-specific types and numerical modeling with data wrangling. Roles overlap; object/structured ndarray caveats remain.',None),
846:('People dataset: John/New York/24, Anna/Paris/13, Peter/Berlin/53, Linda/London/33. DataFrame output, head(2), tail(2) and Age>30 filter all inspected. Filtering retains row labels 2 and 3.',None),
847:('Table covers display, head, tail, dtypes, info, scalar-column versus list-column selection and iloc. Printed capital Data_pandas differs from defined data_pandas. display/info normally return None while displaying/printing; object does not mean only string.',None),
848:('scikit-learn is open-source and built on NumPy/SciPy, with common estimator interfaces. Exactly one changed line for every algorithm swap is an overstatement when capabilities, preprocessing or data assumptions differ.',None),
849:('Estimator objects store configuration and fitted information; workflow categories listed are supervised, unsupervised, preprocessing and meta-estimators. Not every estimator implements every method.',None),
850:('API table: fit returns self; predict returns labels/values; classifier predict_proba returns per-class probabilities; score uses default metric; transform changes representation; fit_transform fits and transforms. Shapes (n,) and (n,K) refer to ordinary single-output classification, not every estimator.',None),
851:('Iris imports train_test_split, StandardScaler, KNeighborsClassifier and load_iris. load_iris(return_X_y=True) separates feature/target arrays; train_test_split(X,y,test_size=0.2) separates train/test. Four measured features and three target classes. No random_state or stratify argument is supplied.',None),
852:('Scaler fits/transforms training data and transforms test/new samples only; KNN fits scaled train data, predicts [[5.1,3.5,1.4,0.2]], then scores scaled test data. Printed category [0], accuracy 93.33333333333333%. Accuracy is one unseeded split result, not a deterministic guarantee. Standardization is not general imputation or data cleaning.',None),
853:('Summary repeats ecosystem, arrays, sparse data, plots, pandas and estimator API. Universal-array and exactly-one-line claims retain earlier qualifications. No new premise.',None),
854:('Two textbook references and the scikit-learn website.','Bibliography only; unprovided textbook content is not assumed inspected.'),
855:('Thank-you closing.','Closing only.')}
ISSUES=[
(827,'Imports are labeled installation and Colab package absence is asserted.','The shown statements import already available packages; availability and installation are separate runtime questions.'),
(828,'Free GPU/TPU access is presented without availability limits.','Treat as a hosted-notebook capability subject to service/runtime availability, not a guaranteed allocation.'),
(830,'All ML data must be explicitly converted to a NumPy array; elements all same type.','An ndarray has one dtype, including possible object/structured dtypes; accepted inputs depend on the estimator and can include sparse, list-like or DataFrame inputs.'),
(833,'arange is described as float-safe and prose informally calls results lists.','It returns an ndarray; noninteger steps can have precision/length pitfalls. The half-unit example itself is exact.'),
(837,'CSR stores only nonzero entries and is unconditionally memory-saving/fast.','CSR includes indices and row pointers, can store explicit zero values and has operation/density-dependent costs.'),
(838,'Displayed COO print output omits braces present in the literal comma-argument print.','Literal Python prints the braces; adding .format or an f-string would be an explicit correction, not the original code.'),
(842,'linspace(-10,10,100) is described as 100 steps; notebook magic appears in code.','There are 100 sample values and 99 adjacent intervals. The magic requires an IPython notebook environment, unlike ordinary Python source.'),
(845,'NumPy and pandas dtype/workflow contrast can be read as exclusive.','One dtype is not one Python object class for object arrays, and numerical/wrangling workflow roles overlap.'),
(847,'display and info are said to return the shown table/summary; object=string; Data_pandas capitalization.','Ordinary display and info return None, object can contain non-string Python objects, and the printed uppercase identifier is undefined in the shown lowercase context.'),
(848,'Every estimator replacement requires exactly one changed line.','Common methods simplify compatible replacements; preprocessing, capabilities and input requirements still need checking.'),
(850,'Prediction shapes and all listed methods appear universal.','Use the single-output classification context and supported estimator methods; score metric is estimator-specific.'),
(851,'StandardScaler average 0/spread 1 statement omits scope.','Training nonconstant features have the fitted moments; transformed test data need not, and constant features cannot be made unit variance.'),
(852,'An unseeded split displays one precise accuracy; scaling is called cleaning.','No unique score follows from code without a fixed split; standardization does not imply imputation, outlier removal or universal cleaning.'),
(853,'Universal array and exactly-one-line claims repeat.','Preserve the earlier input/API qualifications instead of treating summary repetition as new evidence.')]

def add(p,key,title,stem,opts,why,**kw):
 correct=list(kw.pop('correct',(0,)));k=len(b.questions)%4;opts=opts[k:]+opts[:k];correct=[(i-k)%4 for i in correct]
 conflict_pages=kw.pop('conflict_pages',None);code=kw.pop('code',False)
 q=b.add(p,key,title,stem,[o[0] for o in opts],correct,why,[o[1] for o in opts],**kw);q['options'].sort(key=lambda o:o['id'])
 for c in q['citations']:
  c['locator']=f"Lecture 28, physical PDF page {c['physicalPage']}, actual printed footer {c['physicalPage']-821}: {title}"
  c['evidenceText']='Actual pixel inspection note: '+NOTES[c['physicalPage']][0]+'\n'+c['evidenceText']
  if code:c['kind']='code'
 if q.get('conflictResolution'):
  pages=conflict_pages or ([p] if isinstance(p,int) else p);q['conflictResolution'].update(sourceId='lectures',sourceSha256=SHA,physicalPages=pages)
  for c in q['citations']:c['role']='conflict' if c['physicalPage'] in pages else 'premise'
 return q

def save(frozen=False):
 b.save();path=R/f'data/question-batches/{BATCH}.json';data=json.loads(path.read_text());data['sourceIssues']=[{'physicalPage':p,'description':d,'qualification':q,'status':'preserved with explicit scope; not globally resolved'} for p,d,q in ISSUES];path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 maps={s['physicalPage']:s for s in map(json.loads,(R/'sources/page_maps/lectures.jsonl').read_text().splitlines())};slides=[]
 for p,(note,excluded) in NOTES.items():
  s=copy.deepcopy(maps[p]);s['disposition']='excluded' if excluded else 'examinable';s['exclusionReason']=excluded;s['conceptIds']=[c['id'] for c in b.concepts.values() if s['id'] in c['slideIds']]
  s['printedSlideNumber']=str(p-821);s['printedSlideNumberStatus']='present';s['printedNumberEvidence']='Actual bottom-right footer inspected; physical PDF page is retained separately.'
  s['visualInspection']={'status':'complete','inspectorId':AUTHOR,'inspectedAt':INSPECTED_AT,'method':'rendered_page','notes':note+' Actual readable 1800×1013 source pixels inspected alongside extracted text.','previewSha256':hashlib.sha256((R/s['previewPath']).read_bytes()).hexdigest(),'dimensions':[1800,1013]};slides.append(s)
 for typ,rows in [('question',b.questions),('concept',list(b.concepts.values())),('slide',slides)]:
  errors=[e for row in rows for e in schema_errors(row,json.loads((R/f'data/schema.{typ}.json').read_text()))];assert not errors,(typ,errors)
 (R/f'data/inspection-batches/{BATCH}.json').write_text(json.dumps({'batchId':BATCH,'slides':slides},ensure_ascii=False,indent=2)+'\n')
 (R/f'audits/{BATCH}-source-issues.json').write_text(json.dumps({'sourceId':'lectures','sourceSha256':SHA,'issues':data['sourceIssues'],'officialDocumentationChecked':[{'url':u,'purpose':v} for u,v in [('https://numpy.org/doc/stable/reference/generated/numpy.arange.html','Floating-step precision warning.'),('https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.info.html','Printed summary versus returned None.'),('https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html','Fitted training mean/variance and zero-variance behavior.'),('https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html','CSR representation and explicit-zero qualification.')]],'documentationNote':'Documentation checked on 2026-10-19. Executed versions are separately recorded; online stable versions may differ. External documentation clarifies software behavior, not course coverage.'},ensure_ascii=False,indent=2)+'\n')
 (R/f'audits/{BATCH}-author-progress.json').write_text(json.dumps({'frozen':frozen,'questionCount':len(b.questions),'conceptCount':len(b.concepts),'inspectedPages':list(NOTES),'next':'Independent source-based answer and coverage review required.' if frozen else 'Continue distinct source-grounded drafting.'},indent=2)+'\n')
 print('Saved',len(b.questions),'drafts;',len(slides),'actual page inspections; frozen=',frozen)
save()
add(825,'ecosystem','Why Python is useful for ML',
 'Which explanation best matches the lecture’s reason for using Python in machine learning?',[
 ('A rich scientific-library ecosystem and interactive experimentation reduce development effort.','This is the stated ecosystem and workflow advantage.'),
 ('Interpreted Python loops intrinsically execute faster than compiled numerical kernels.','The lecture explicitly distinguishes ecosystem value from raw speed.'),
 ('Python replaces numerical libraries with built-in syntax for every learning algorithm.','The cited advantage depends heavily on libraries, not removal of them.'),
 ('Python is useful only for training and cannot participate in deployment or data processing.','Its general-purpose scope supports broader applications.')],
 'The lecture emphasizes library depth, community and interactive workflows rather than claiming that ordinary Python execution is always fastest.',difficulty='easy')
add(826,'library-match','Choosing libraries by primary purpose',
 'A workflow needs tabular CSV cleaning, zero-heavy matrix operations and model fitting. Which ordered tool assignment best matches the lecture?',[
 ('pandas, SciPy sparse, scikit-learn.','These match wrangling, sparse representation and learning.'),
 ('NumPy, matplotlib, IPython.','NumPy can hold data, but matplotlib and IPython are not the listed sparse and fitting libraries.'),
 ('scikit-learn, pandas, matplotlib.','This swaps modeling with wrangling and assigns fitting to a plotting library.'),
 ('SciPy sparse, scikit-learn, pandas.','This assigns the three main responsibilities to the wrong primary tools.')],
 'The table distinguishes data wrangling, sparse scientific computation and learning/evaluation; these responsibilities can cooperate in one pipeline.',typ='match',difficulty='easy')
add(826,'interactive-versus-plot','Interactive environment versus plotting library',
 'Which pairing correctly distinguishes the lecture’s numerical array library, plotting library and interactive notebook environment?',[
 ('NumPy supplies arrays, matplotlib supplies plots, and IPython/Jupyter supplies interactive execution and reports.','These are the three stated roles.'),
 ('matplotlib supplies arrays, IPython supplies plots, and NumPy supplies notebooks.','This cyclically swaps the core responsibilities.'),
 ('Jupyter supplies trained estimators, scikit-learn supplies notebook kernels, and SciPy supplies only plots.','The named estimator, environment and scientific-computation roles are confused.'),
 ('pandas replaces the notebook kernel, while NumPy and matplotlib are alternative notebook file formats.','These are libraries, not notebook file formats or kernel replacements.')],
 'Libraries for data and visualization run within an interactive environment; the environment is not itself the numerical array or plotting API.',typ='match',difficulty='easy')
add(827,'imports-installation','Imports do not install packages',
 'The slide shows import numpy as np and import sklearn under an installation heading. In a fresh environment where sklearn is absent, what does the second statement normally do?',[
 ('It raises an import error; installation must be performed separately.','Import resolves an available module rather than installing it.'),
 ('It downloads and installs scikit-learn before continuing.','Import does not invoke a package installer.'),
 ('It installs scikit-learn only if NumPy was imported first.','Dependency import order does not supply an absent package.'),
 ('It creates an empty sklearn namespace that can train models later.','An unavailable module cannot be replaced by an empty namespace through this statement.')],
 'The literal statements are imports. The slide heading and its assertion about Colab package availability must not be treated as proof of installation or of a current runtime’s contents.',typ='scenario',difficulty='easy',code=True,conflict='Page 827 labels import statements as installation and asserts that the listed packages are not pre-installed in Colab.')
add(828,'notebook-medium','Notebook document and hosted execution',
 'What is a defensible description of the notebook workflow presented in the lecture?',[
 ('It combines executable cells, explanatory text and visual output; hosted accelerators depend on runtime availability.','This retains the notebook benefit without promising resources.'),
 ('It is only a static report, so code cannot be rerun after text is written.','Cells are executable and can be rerun.'),
 ('A saved notebook guarantees a continuously running GPU kernel whenever reopened.','A document does not guarantee persistent state or hardware allocation.'),
 ('Using a browser means every numerical operation must execute in the browser’s JavaScript engine.','The execution architecture sends code to a kernel, which may run elsewhere.')],
 'Notebook documents mix narrative and execution. The source’s hosted GPU/TPU statement describes a possible capability, not a guaranteed allocation or persistence promise.',difficulty='easy',conflict='The source describes free Colab GPU/TPU access without stating resource availability or runtime limits.')
add(829,'execution-path','Notebook execution path',
 'Which sequence best describes the execution path shown for a notebook code cell?',[
 ('Browser cell → server → kernel execution → returned result → browser display.','This follows the stated architecture.'),
 ('Browser cell → saved JSON output → compiler executes the old output → kernel.','Stored output is not an instruction for executing the new code.'),
 ('Browser cell → matplotlib renderer → pandas database → kernel.','Plotting and tabular libraries are not mandatory transport stages.'),
 ('Browser cell → kernel restart → loss of variables before every line.','Normal cell execution does not restart the kernel each time.')],
 'The browser presents and submits code, while the kernel executes it and maintains state across ordinary cell runs.',typ='match',difficulty='easy')
add(829,'cell-state','Execution order and kernel state',
 'In one notebook kernel, cell A executes x = 2, cell B executes x = x + 3, and cell B is then rerun once. Before any restart, what is x, and what happens if B is run immediately after a kernel restart without A?',[
 ('x is 8; after restart, B raises NameError because x is undefined.','The second execution uses the existing value 5, but restart removes it.'),
 ('x is 5; after restart, B restores x from its saved output.','Rerunning B updates live state, and saved output does not recreate variables.'),
 ('x is 8; after restart, B starts x automatically at zero.','The notebook kernel does not initialize undefined names to zero.'),
 ('x is 5; after restart, B still sees the previous live x.','Both claims incorrectly make cell execution or restart stateless/persistent in the wrong way.')],
 'Cell execution is stateful: 2 → 5 → 8. Restart clears variables, even if the notebook file retains previously displayed results.',typ='scenario',difficulty='medium',code=True,steps=['Execute A: x = 2.','Execute B twice: x = 5, then x = 8.','Restart clears the binding; evaluating x on the right side of B raises NameError.'])
add(830,'array-dtype','One ndarray dtype and object arrays',
 'Which statement correctly qualifies the lecture’s claim that a NumPy array has elements of the same type?',[
 ('An ndarray has one dtype, but object dtype can hold references to Python objects of different classes.','The storage dtype is uniform without requiring identical referenced object classes.'),
 ('Every ndarray must contain only integers, so floats require a DataFrame.','NumPy supports many numerical and nonnumerical dtypes.'),
 ('Every ndarray cell has an independently declared dtype exactly like a DataFrame column.','An ordinary ndarray has one dtype descriptor, unlike independent DataFrame column dtypes.'),
 ('An object array removes the ndarray’s dtype attribute entirely.','The dtype remains object; it is not absent.')],
 'The precise invariant is one ndarray dtype. Object and structured dtypes prevent the simplified statement from being read as an absolute ban on heterogeneous referenced values.',difficulty='medium',conflict='The slide says all elements have the same type without distinguishing ndarray dtype from Python object classes.')
add([830,836,853],'input-representation','Array foundations do not require universal dense conversion',
 'A learning API explicitly accepts a SciPy sparse input matrix. Must the user first convert that input to a dense NumPy ndarray solely because the lecture calls ndarray universal?',[
 ('No; accepted representations depend on the API, and unnecessary densification can lose sparse-memory benefits.','The stated sparse-capable API already accepts the representation.'),
 ('Yes; importing NumPy forces every other container to become dense before fitting.','Importing a library does not impose that conversion.'),
 ('Yes; sparse matrices cannot represent numerical feature values.','Sparse matrices represent numerical data while exploiting structure.'),
 ('No; this means the estimator cannot use any NumPy or SciPy computations internally.','Accepted external representation and internal implementation are separate questions.')],
 'NumPy is foundational, but the explicit premise that an API accepts sparse input defeats the claimed mandatory user-side dense conversion. The source’s universal wording is qualified, not silently repeated.',typ='scenario',difficulty='medium',conflict='Pages 830 and 853 imply that all ML input must be explicitly converted to a NumPy ndarray.',conflict_pages=[830,853])
add(831,'array-metadata','Array shape, dimensions and size',
 'For a = np.array([[1, 2, 3], [4, 5, 6]]), what are a.shape, a.ndim and a.size?',[
 ('(2, 3), 2, 6.','There are two axes, two rows, three columns and six scalar elements.'),
 ('(3, 2), 2, 6.','This transposes the row and column counts.'),
 ('(2, 3), 6, 2.','ndim counts axes and size counts elements, not the reverse.'),
 ('(6,), 1, 6.','The nested input creates a matrix rather than a flattened vector.')],
 'Shape lists the lengths of the two axes. ndim is the number of axes, and size is their product.',difficulty='easy',code=True)
add(831,'array-strides','Byte strides and an address offset',
 'Assume the displayed matrix is C-contiguous with int64 elements and strides (24, 8) bytes. What is the byte offset of a[1, 2] from a[0, 0]?',[
 ('40 bytes.','One row stride plus two column strides gives 24 + 16.'),
 ('24 bytes.','This moves one row but ignores the two-column displacement.'),
 ('32 bytes.','This adds only one column stride to the row stride.'),
 ('6 bytes.','Element count is not a byte offset and ignores the 8-byte dtype.')],
 'For zero-based indices, offset = 1 × 24 + 2 × 8 = 40 bytes. The given layout and dtype are explicit; these strides are not asserted for every platform or array view.',typ='numerical',difficulty='easy',code=True,steps=['Use row index 1 and column index 2.','Offset = 1 × 24 + 2 × 8 = 40 bytes.'],formulas=[formula('offset = i s_row + j s_col',{'offset':'byte displacement from the first element','i':'zero-based row index','j':'zero-based column index','s_row':'row stride','s_col':'column stride'},{'offset,s_row,s_col':'bytes','i,j':'dimensionless'},['The given array has strides (24, 8) bytes.'])])
add(831,'dtype-layout','Interpreting the printed stride values',
 'The source prints dtype int64 and strides (24, 8) for a 2 × 3 matrix. Which interpretation is correct?',[
 ('Moving one column advances 8 bytes; moving one row advances 24 bytes in the shown layout.','A row contains three 8-byte elements in this C-contiguous example.'),
 ('The first stride counts rows and the second counts columns, so the array has 24 rows and 8 columns.','Strides are byte increments, not shape dimensions.'),
 ('Every 2 × 3 NumPy array must have these strides even after dtype or layout changes.','Different item sizes and layouts can change strides.'),
 ('The first stride is the total allocation size and the second is the number of dimensions.','Neither interpretation matches the stride definition.')],
 'The displayed strides describe a specific memory layout. The same shape does not force a universal dtype, item size or stride tuple.',difficulty='easy',code=True)
add(832,'constructors','Matching constant-array constructors',
 'Which pair creates a 3 × 4 zero array and a 3 × 3 array filled with 7.0?',[
 ('np.zeros((3, 4)) and np.full((3, 3), 7.0).','Both constructors directly express the required shapes and values.'),
 ('np.ones((3, 4)) and np.eye(3).','These produce ones and an identity matrix, not the requested values.'),
 ('np.zeros((4, 3)) and np.full((3, 3), 7.0).','The filled array is correct, but the zero-array shape is reversed.'),
 ('np.empty((3, 4)) and np.full((3, 3), 7.0).','empty does not guarantee initialized zeros.')],
 'zeros initializes every entry to zero; full initializes every entry to the supplied fill value. Shape order is rows then columns in this two-dimensional case.',typ='match',difficulty='easy',code=True)
add(832,'identity','Identity versus all-ones matrix',
 'Which statement about np.eye(4) and np.ones((2, 5)) matches the constructors shown?',[
 ('eye(4) has four diagonal ones and zeros elsewhere; ones((2, 5)) has ten entries equal to one.','This distinguishes identity structure from uniform filling.'),
 ('eye(4) is a length-four vector; ones((2, 5)) is a 5 × 2 matrix.','Both the identity rank and the shape order are wrong.'),
 ('eye(4) has sixteen ones; ones((2, 5)) has ones only on its diagonal.','This swaps identity and uniform-array behavior.'),
 ('Both constructors create the same shape because their arguments total four and seven.','Tuple entries specify dimensions, not totals used to choose a shared shape.')],
 'An identity matrix is square with unit diagonal, while ones fills all positions of the requested shape.',difficulty='easy',code=True)
add(832,'empty','Uninitialized allocation',
 'You allocate work = np.empty((100, 4)) for later computation. Which action is safe before using every entry as a feature value?',[
 ('Write the intended values into every entry that will be read.','Numeric empty allocation does not initialize meaningful contents.'),
 ('Treat every entry as zero because the array shape was specified.','Shape allocation does not imply zero initialization.'),
 ('Treat the contents as independent standard-normal random samples.','empty is not a random-number generator.'),
 ('Assume every entry is nonzero because the constructor is named empty.','Uninitialized values can include zeros and are not predictable data.')],
 'np.empty reserves an array without initializing numeric entries. It is appropriate when subsequent computation overwrites values before reading them.',typ='scenario',difficulty='easy',code=True)
add(833,'arange','Half-open arange example',
 'What does np.arange(0, 10, 0.5) produce in the lecture example?',[
 ('An ndarray with 20 values, from 0.0 through 9.5.','The half-unit increments exclude the stop value 10.'),
 ('An ndarray with 21 values, from 0.0 through 10.0.','This incorrectly includes the stop endpoint.'),
 ('A Python range object with 10 integer values.','NumPy returns an ndarray and accepts this half-unit step.'),
 ('An ndarray with 500 values, including both endpoints.','That describes neither the supplied step nor the number of samples.')],
 'The sequence is 0, 0.5, …, 9.5. This exactly representable half-unit example does not make arbitrary floating steps immune to rounding issues.',difficulty='easy',code=True,conflict='The source comment calls arange float-safe, which is not a general precision or endpoint guarantee.')
add(833,'linspace','Endpoint-inclusive linspace spacing',
 'With default endpoint behavior, np.linspace(0, 2*np.pi, 500) has what adjacent spacing?',[
 ('2π / 499.','Five hundred samples spanning both endpoints create 499 intervals.'),
 ('2π / 500.','This divides by the sample count rather than the interval count.'),
 ('500 / (2π).','This is the reciprocal of an approximate spacing, not the spacing itself.'),
 ('2π.','That is the full interval width, not the distance between adjacent samples.')],
 'linspace specifies the number of samples. Including both endpoints means spacing = (2π − 0) / (500 − 1).',typ='numerical',difficulty='easy',code=True,steps=['Count intervals: 500 − 1 = 499.','Divide the endpoint span 2π by 499.'],formulas=[formula('Δx = (b − a)/(N − 1)',{'Δx':'spacing between neighboring sample values','a':'first endpoint','b':'last endpoint','N':'number of endpoint-inclusive samples'},{'Δx,a,b':'radians in this example','N':'dimensionless'},['N > 1 and endpoint=True.'])])
add(833,'random-bounds','Normal distribution versus bounded integers',
 'Which interpretation of standard_normal((100, 4)) and integers(0, 100, size=(6, 4)) is correct?',[
 ('The normal array has shape (100, 4) and is not bounded to [−1, 1]; the integer array draws from 0 through 99.','A standard normal has unbounded support and integers uses an exclusive upper bound by default.'),
 ('Every normal entry lies in [−1, 1], and integer values include 100.','Both proposed bounds are wrong.'),
 ('The normal sample mean must be exactly zero, and the integer sample mean must be exactly 50.','Distribution parameters do not force exact finite-sample means.'),
 ('Both calls return one-dimensional arrays because randomness ignores the requested size.','The size tuples determine the output shapes.')],
 'The normal distribution has mean zero and variance one, but finite samples vary. The default integer interval is [0, 100), so 100 is excluded.',difficulty='medium',code=True)
add([833,834],'rng-history','Seed and random draw history',
 'Page 833 draws 400 normal values before its integer array. Page 834 starts a fresh generator with seed 42 and immediately draws integers. Must the two integer arrays match?',[
 ('No; the earlier normal draws advance the generator state before the first integer array.','The seed alone does not erase different draw histories.'),
 ('Yes; specifying seed 42 fixes every later array regardless of earlier calls.','A seeded generator produces a sequence whose position changes with draws.'),
 ('Yes; normal draws use no random generator state.','They consume random state in generating their samples.'),
 ('No; seeded random generation can never reproduce the same sequence even with identical calls.','Identical generator configuration and draw sequence can be reproducible within the stated software context.')],
 'Reproducibility requires matching generator configuration, seed and call history. The fresh seed on page 834 explains why its printed matrix need not equal the later integer array on page 833.',typ='scenario',difficulty='medium',code=True)
MATRIX='X = [[8, 77, 65, 43], [43, 85, 8, 69], [20, 9, 52, 97], [73, 76, 71, 78], [51, 12, 83, 45], [50, 37, 18, 92]] is a NumPy array.'
add([834,835],'row-column','Single-row and single-column indexing',
 MATRIX+' What is X[:, 2]?',[
 ('[65, 8, 52, 71, 83, 18].','Column index 2 is the third column across all six rows.'),
 ('[20, 9, 52, 97].','This is row index 2, not column index 2.'),
 ('[77, 85, 9, 76, 12, 37].','This is column index 1, reflecting one-based confusion.'),
 ('[[65], [8], [52], [71], [83], [18]].','The values match, but this is a two-dimensional column rather than the one-dimensional result of scalar column indexing.')],
 'The colon selects all rows and scalar index 2 selects the third column, yielding shape (6,).',difficulty='easy',code=True)
add([834,835],'slicing','Exclusive slice stops',
 MATRIX+' What is X[1:4, 0:2]?',[
 ('[[43, 85], [20, 9], [73, 76]], with shape (3, 2).','Rows 1, 2, 3 and columns 0, 1 are included.'),
 ('[[43, 85, 8], [20, 9, 52], [73, 76, 71], [51, 12, 83]], with shape (4, 3).','This incorrectly includes both stop indices.'),
 ('[[8, 77], [43, 85], [20, 9]], with shape (3, 2).','This starts from row 0 instead of row 1.'),
 ('[[85, 8], [9, 52], [76, 71]], with shape (3, 2).','This starts from column 1 instead of column 0.')],
 'NumPy slicing includes the start and excludes the stop on each axis. The selected row count is 4 − 1 = 3 and column count is 2 − 0 = 2.',difficulty='medium',code=True,steps=['Rows: 1, 2, 3.','Columns: 0, 1.','Collect the six selected entries into a 3 × 2 array.'])
add([834,835],'advanced-rows','Selecting noncontiguous rows',
 MATRIX+' Which expression selects exactly rows with zero-based indices 0, 2 and 5, retaining all columns?',[
 ('X[[0, 2, 5], :].','A list of row indices selects the three specified rows.'),
 ('X[0:5, :].','This selects rows 0 through 4, not just the requested three.'),
 ('X[:, [0, 2, 5]].','This selects columns and also requests a nonexistent column index 5.'),
 ('X[0, 2, 5].','This supplies three scalar axes to a two-dimensional array.')],
 'The list of row indices performs noncontiguous row selection, and the colon keeps all four columns. The resulting shape is (3, 4).',difficulty='easy',code=True)
add([834,835],'boolean-filter','Strict boolean filtering',
 MATRIX+' After mask = X[:, 0] > 50, which rows appear in X[mask]?',[
 ('[73, 76, 71, 78] and [51, 12, 83, 45].','Only first-column values 73 and 51 exceed 50.'),
 ('[73, 76, 71, 78], [51, 12, 83, 45] and [50, 37, 18, 92].','This replaces strict > with ≥ and incorrectly includes 50.'),
 ('[8, 77, 65, 43], [43, 85, 8, 69] and [20, 9, 52, 97].','These are the rows below the threshold rather than above it.'),
 ('[65, 8, 52, 71, 83, 18].','This is a column selection, not a row filter.')],
 'The mask is [False, False, False, True, True, False]. Boolean row indexing keeps two entire rows and preserves their order.',difficulty='easy',code=True)
save()
add(836,'scipy-scope','Scientific algorithms and sparse data',
 'A pipeline needs numerical optimization, statistical distributions and operations on a zero-heavy feature matrix. Which library and subpackage most directly match the lecture?',[
 ('SciPy, including scipy.sparse for the matrix representation.','These scientific-computing and sparse capabilities are listed.'),
 ('matplotlib, including pyplot as the sparse storage format.','pyplot is a plotting interface, not a sparse matrix format.'),
 ('IPython, including notebook outputs as optimization routines.','An interactive environment can call routines but does not replace the scientific library.'),
 ('pandas alone, because its DataFrame is the CSR format named in the source.','DataFrame and CSR are distinct structures; the listed CSR example is in SciPy.')],
 'SciPy extends the numerical ecosystem with algorithms and specialized representations. Sparse storage is useful for suitable zero-heavy matrices, rather than a universal replacement for dense arrays.',typ='scenario',difficulty='easy')
add(837,'csr-identity','Dense identity to CSR',
 'For eye = np.eye(4) followed by sparse_matrix = sparse.csr_matrix(eye), which entries are printed as stored values in the source?',[
 ('(0, 0), (1, 1), (2, 2), (3, 3), each with value 1.0.','The four diagonal ones are the only nonzero values in this conversion.'),
 ('All sixteen coordinates, each with value 1.0.','That would describe an all-ones matrix, not an identity.'),
 ('(0, 1), (1, 2), (2, 3), (3, 0), each with value 1.0.','Those positions shift the identity’s diagonal.'),
 ('Only (0, 0), with value 4.0.','The trace is four, but conversion does not combine distinct diagonal coordinates.')],
 'The conversion preserves the identity’s entries and shape. Its four stored values occur on the main diagonal.',difficulty='easy',code=True)
add(837,'sparse-cost','Qualifying sparse memory and speed claims',
 'Which statement correctly qualifies the lecture’s broad memory and speed claims for CSR?',[
 ('CSR stores values plus indexing metadata; its advantage depends on sparsity, size and the requested operation.','Sparse formats have representation overhead and operation-specific strengths.'),
 ('CSR requires only the value array, so indices and row boundaries take no storage.','Column indices and row pointers are part of CSR.'),
 ('CSR is always smaller and faster, even for tiny fully dense matrices.','Overhead and density can eliminate the advantage.'),
 ('CSR cannot represent any zero-valued stored entry under any construction.','Explicit stored zeros are possible even though the identity conversion omits zeros.')],
 'Sparse storage avoids many implicit zeros but is not free of metadata or universal performance tradeoffs. The source’s identity is a concrete example, not proof of a speed ranking for every matrix.',difficulty='medium',conflict='The source says only nonzero entries are stored and describes unconditional major memory/speed benefits.')
add(838,'coo-constructor','Coordinate sparse construction',
 'Given data = [1.0, 1.0, 1.0, 1.0], row_indices = [0, 1, 2, 3] and col_indices = [0, 1, 2, 3], what does sparse.coo_matrix((data, (row_indices, col_indices))) represent?',[
 ('A 4 × 4 identity matrix with the values paired to the listed row/column coordinates.','Each value is attached to one diagonal coordinate, and the maximum index is 3.'),
 ('A 3 × 3 identity matrix because the largest index is 3.','Zero-based index 3 requires four positions.'),
 ('A 4 × 4 all-ones matrix because data contains only ones.','Only four listed coordinates receive those values.'),
 ('A 4 × 1 matrix because data has four entries.','The row and column indices jointly determine the two-dimensional shape.')],
 'COO construction pairs each data entry with a row and column index. The given triples populate the diagonal from index 0 through 3.',difficulty='easy',code=True)
add(838,'coo-print','Literal formatting mismatch',
 'The source literally writes print("COO representation:\\n{}", eye_coo). What happens to {} under ordinary Python print semantics?',[
 ('The braces are printed literally before the second argument’s representation.','Comma-separated print arguments do not invoke string formatting.'),
 ('The braces are replaced by eye_coo because print always applies .format.','print does not automatically call format on the first argument.'),
 ('The braces make the statement a SyntaxError before print is called.','Braces inside a quoted string are valid characters.'),
 ('The braces cause eye_coo to become an empty dictionary.','String contents do not reassign the matrix or create a dictionary here.')],
 'The displayed output omits the literal braces, so it does not exactly follow this print statement. Explicit .format(eye_coo) or an f-string would be a correction, not the original source code.',difficulty='easy',code=True,conflict='The source code uses a comma print argument after a string containing {}, but the displayed output does not show the braces.')
add(839,'figure-axes-artists','Plot object roles',
 'In matplotlib’s object organization, which description best matches the lecture?',[
 ('A Figure contains the overall visualization; Axes provide plotting regions; lines and text are examples of Artists.','This matches the container, plotting-region and drawable-object roles.'),
 ('An Axes is always one individual tick mark, and a Figure is always one plotted data point.','These confuse plotting containers with individual drawable elements.'),
 ('Artists are only image files saved to disk, not in-memory plot objects.','Artists are drawable objects used to construct the visualization.'),
 ('The x-axis and y-axis together are called the Figure, and all subplots share one mandatory Axes.','A Figure can contain multiple Axes; the object hierarchy is not that restriction.')],
 'The roles help organize a plot. They are not mutually exclusive Python type categories: Figure and Axes are also Artist subclasses.',difficulty='easy')
add(840,'plot-scatter','Choosing line and scatter displays',
 'You want a connected loss-versus-epoch curve and, separately, unconnected points for two measured features. Which primary calls match those needs?',[
 ('plt.plot for the loss curve and plt.scatter for the feature points.','The calls match an ordered curve and a scatter relationship.'),
 ('plt.hist for both, because both displays contain numerical values.','A histogram summarizes bins rather than either requested relationship.'),
 ('plt.colorbar for the loss curve and plt.legend for feature coordinates.','These annotate existing mappings or series, not plot the requested data.'),
 ('plt.xlabel for the loss values and plt.ylabel for the feature points.','These label axes without creating the data displays.')],
 'Plotting functions should match the diagnostic task: an ordered series often uses a line, while feature pairs are naturally displayed as scatter points.',typ='scenario',difficulty='easy')
add(840,'axes-limits','Labels, subplots and view limits',
 'A script calls plt.subplots(1, 2) and then sets an Axes x-limit to (0, 10). What is the correct interpretation?',[
 ('The figure has two side-by-side plotting regions; the limit changes the visible x-range without deleting source data.','Subplot layout and viewing limits concern the visualization.'),
 ('The figure contains two vertically stacked regions; all input rows outside the range are deleted.','Both the grid interpretation and data-deletion claim are wrong.'),
 ('The call returns a two-row DataFrame with values clipped to [0, 10].','subplots creates plot objects, not a DataFrame.'),
 ('The x-limit changes every plotted y-value to lie between 0 and 10.','An x viewing limit is not a transformation of y data.')],
 'One row and two columns gives side-by-side Axes. Limits set the displayed coordinate window; labels separately describe the axes.',typ='scenario',difficulty='medium')
add(841,'semilogy','Logarithmic y-axis',
 'Which plot call is appropriate when a loss curve should use a logarithmic vertical axis and a linear epoch axis?',[
 ('plt.semilogy.','The y-axis is logarithmic while x remains linear.'),
 ('plt.semilogx.','That makes the horizontal axis logarithmic instead.'),
 ('plt.hist.','This computes a distribution histogram rather than the requested axis scaling.'),
 ('plt.colorbar.','This adds a color-value reference rather than changing the curve’s y-axis scale.')],
 'The name semilogy identifies the logarithmic axis. This is useful for positive losses spanning orders of magnitude.',difficulty='easy')
add(841,'histogram','Frequency distribution diagnostic',
 'A researcher wants to inspect how often residual values fall in value intervals, rather than connect residuals in observation order. Which function best matches that task?',[
 ('plt.hist.','A histogram groups values into bins and displays their frequencies.'),
 ('plt.plot with the observation index on the horizontal axis.','That shows order-dependent variation rather than a binned frequency distribution.'),
 ('plt.text at the mean residual.','A single annotation does not show the distribution.'),
 ('plt.xlim using the minimum and maximum residual.','Changing view limits does not compute a histogram.')],
 'Histograms are distribution diagnostics. A line plot of ordered residuals answers a different question about their sequence.',typ='scenario',difficulty='easy')
add(841,'legend-colorbar','Legend and colorbar distinction',
 'Two model curves are labeled by model name, while a separate scatter plot uses color to encode a numerical measurement. Which annotation pairing is appropriate?',[
 ('A legend for the named curves and a colorbar for the numerical color mapping.','The annotations explain different visual encodings.'),
 ('A colorbar for model names and a legend automatically displaying every possible numerical color value.','This confuses series identities with a numeric color scale.'),
 ('Only axis limits, because labels and color mappings are inferred without explanation.','Limits do not identify curves or explain colors.'),
 ('Only plt.show, which automatically supplies both model names and physical color units.','Display does not invent missing labels or units.')],
 'A legend identifies labeled plot elements; a colorbar provides the mapping from color to a represented value.',typ='scenario',difficulty='easy')
add(842,'sine-plot','Reading the sine example',
 'The code sets x = np.linspace(-10, 10, 100), y = np.sin(x), then plt.plot(x, y, marker="x"). What does the plotted x-shaped symbol indicate?',[
 ('A marker at each of the 100 sampled (x, sin(x)) data points on the line.','The marker option controls the point symbol, not the function or x coordinates.'),
 ('A cross-product operation between x and y.','marker is a styling argument, not an algebraic operator.'),
 ('The horizontal axis is logarithmic.','A marker does not change axis scale.'),
 ('Only samples whose y-value equals x are drawn.','The marker string does not filter the data.')],
 'The code plots a connected sine curve sampled at 100 x values, with x-shaped point markers. np.sin uses radians; the displayed endpoint signs match sin(−10) > 0 and sin(10) < 0.',typ='diagram',difficulty='easy',code=True)
add(842,'sample-intervals','Samples, intervals and notebook magic',
 'Which pair of statements correctly interprets the source’s sine code?',[
 ('linspace(-10, 10, 100) creates 100 samples and 99 intervals; %matplotlib inline is IPython-specific syntax.','Both the sample count and environment qualification are correct.'),
 ('It creates 101 samples and 100 intervals; the magic is ordinary Python modulo assignment.','The count and syntax interpretation are incorrect.'),
 ('It creates 100 samples and 100 intervals; the magic installs matplotlib.','Endpoint-inclusive intervals are one fewer, and the magic selects notebook plotting behavior.'),
 ('It creates 99 samples and excludes 10; the magic is required in every standalone Python plotting script.','Both default endpoint behavior and the universal magic requirement are wrong.')],
 'The comment’s informal word steps must not change linspace semantics. A standalone script uses suitable backend/display code rather than copying the notebook magic as Python syntax.',difficulty='medium',code=True,conflict='The source comment calls 100 endpoint-inclusive samples 100 steps and includes notebook magic without a standalone-script qualification.')
add(843,'classification-generation','Synthetic scatter dataset dimensions',
 'In make_classification(n_samples=200, n_features=2, n_redundant=0, random_state=0), what do X_cls and y_cls represent in the shown two-class example?',[
 ('X_cls contains 200 rows with 2 features, while y_cls contains one class label for each row.','Features provide coordinates and the labels provide the supplied class colors.'),
 ('X_cls contains 2 rows with 200 features, while y_cls is a 2 × 2 probability matrix.','This reverses dimensions and invents predicted probabilities.'),
 ('X_cls contains only class IDs, while y_cls contains the two plotted coordinate columns.','This swaps features and targets.'),
 ('X_cls contains the trained model, while y_cls contains its test accuracy.','make_classification generates data rather than fitting an estimator.')],
 'The source generates a labeled synthetic dataset with shape (200, 2) and target shape (200,). A fixed random_state supports reproducibility in the stated generator/software context.',difficulty='easy',code=True)
add(843,'scatter-encoding','Scatter coordinates and supplied class colors',
 'In the displayed scatter call, which expression supplies the vertical coordinates and which supplies the colors?',[
 ('X_cls[:, 1] supplies vertical coordinates; c=y_cls supplies colors from the labels.','The second feature is y-position and c selects the color values.'),
 ('y_cls supplies vertical coordinates; X_cls[:, 1] supplies colors.','This swaps target labels with the second feature.'),
 ('edgecolors="k" supplies vertical coordinates; alpha=0.8 supplies class labels.','These arguments control edge color and opacity.'),
 ('cmap="bwr" trains a classifier and its predictions supply both coordinates.','A colormap does not fit a model or generate coordinates.')],
 'The points use two feature columns as coordinates and provided class labels as color values. The plot is not itself a classifier prediction.',typ='diagram',difficulty='easy',code=True)
add(843,'scatter-style','Reading colorbar and scatter styles',
 'For the source’s bwr colorbar spanning class values 0 to 1, edgecolors="k", linewidths=0.5 and alpha=0.8, which reading is correct?',[
 ('Class 0 maps to blue and class 1 to red; points have black edges and partial opacity.','This follows the shown endpoint colors and the style parameters.'),
 ('Class 0 maps to red and class 1 to blue; alpha is classification accuracy.','The color endpoints are reversed and alpha is opacity.'),
 ('Black edges mean a third learned class; linewidths sets the feature count.','Edge styling does not add labels or determine data dimensionality.'),
 ('Intermediate colorbar ticks prove that the dataset contains six additional classes.','The continuous colormap scale can show intermediate ticks even when labels are only 0 and 1.')],
 'The numerical colormap and point styling are visual encodings. Intermediate ticks do not create new target categories, and opacity is not a performance score.',typ='diagram',difficulty='medium',code=True)
save()
add([840,841],'plot-annotation','Completing a diagnostic figure',
 'A figure already contains data. Which sequence correctly adds axis descriptions, a note at coordinates and then requests display?',[
 ('xlabel/ylabel, text, show.','The calls label axes, add an annotation and request display.'),
 ('xlim/ylim, hist, colorbar.','Limits, a new histogram and a color scale do not perform the three requested actions.'),
 ('legend, subplots, semilogy.','These identify series, create plot regions and choose a log-y plot instead.'),
 ('show, fit, predict.','The latter methods belong to estimator workflows, not figure annotation.')],
 'Plot annotations and display are separate operations. Whether show opens a window or yields inline output depends on the plotting environment.',typ='match',difficulty='easy')
add([844,845],'dataframe','DataFrame structure and workflow',
 'A table contains names, ages and timestamps and must be loaded, cleaned and explored before model fitting. Which description fits pandas?',[
 ('A DataFrame is a labeled table whose columns can have different dtypes, with tools for ingestion and wrangling.','This matches both the structure and stated workflow.'),
 ('A DataFrame requires every column to have one identical numerical dtype.','Different columns can carry different types.'),
 ('A DataFrame is a trained classifier that automatically predicts the name column.','It is a data structure, not a fitted estimator.'),
 ('A DataFrame accepts only CSV data and cannot participate in SQL or Excel workflows.','The source lists all three ingestion contexts.')],
 'pandas provides a labeled, column-oriented table suited to mixed tabular data. This does not forbid numerical computations in pandas or wrangling in NumPy.',typ='scenario',difficulty='easy')
PEOPLE="The DataFrame data_pandas has columns Name, Location, Age and rows 0: John, New York, 24; 1: Anna, Paris, 13; 2: Peter, Berlin, 53; 3: Linda, London, 33."
add(846,'dataframe-construction','Dictionary of equal-length columns',
 'The source supplies a dictionary with lists of four names, four locations and four ages, then calls pd.DataFrame(data). What shape results?',[
 ('(4, 3).','Four records become rows and three dictionary keys become columns.'),
 ('(3, 4).','This swaps records and named fields.'),
 ('(12,).','DataFrame construction does not flatten the table into one dimension.'),
 ('(4, 4).','The displayed row index is not an additional data column in shape.')],
 'The four people are observations and the three keys define columns. The displayed index is separate from the column count.',difficulty='easy',code=True)
add([846,847],'head-tail','Head and tail preserve row order',
 PEOPLE+' Which names appear in data_pandas.head(2) and data_pandas.tail(2)?',[
 ('head: John, Anna; tail: Peter, Linda.','The calls select the first and last two rows in existing order.'),
 ('head: Anna, John; tail: Linda, Peter.','Neither call reverses the selected row order.'),
 ('head: Anna, John; tail: Linda, Peter after sorting by age automatically.','head and tail do not sort automatically.'),
 ('head: Name, Location; tail: Location, Age.','These are column names, not rows selected by head or tail.')],
 'head and tail select rows from the beginning and end of the existing table. They do not sort, reverse or select columns.',difficulty='easy',code=True)
add(846,'pandas-filter','Boolean row selection retains index labels',
 PEOPLE+' What does data_pandas[data_pandas.Age > 30] contain?',[
 ('Peter and Linda with their original row labels 2 and 3.','Their ages are 53 and 33, and filtering does not automatically reset the index.'),
 ('Peter and Linda, necessarily relabeled 0 and 1 by the filter.','The selected values are correct but automatic index resetting is not.'),
 ('John and Anna with row labels 0 and 1.','Those ages are below 30.'),
 ('Only the Age column, containing [53, 33].','The outer DataFrame filter retains all columns for selected rows.')],
 'The boolean Series selects entire rows satisfying the condition. A separate operation would be needed to reset the displayed row labels.',difficulty='easy',code=True)
add(847,'series-dataframe','Single-column versus list-column selection',
 'Assume data_pandas has four rows and a uniquely named Age column. How do data_pandas["Age"] and data_pandas[["Age"]] differ?',[
 ('The former is a one-dimensional Series; the latter is a two-dimensional one-column DataFrame.','A scalar column label and a list of labels produce different container dimensionality.'),
 ('Both are always scalar integers because only one column is named.','Selecting a column retains its values across rows.'),
 ('The former is a DataFrame and the latter a Series.','This reverses the selection behavior.'),
 ('The latter duplicates Age into two columns because two bracket pairs are used.','The list contains one label, so it selects one column.')],
 'A list of column labels preserves DataFrame structure, even when the list has one entry. For four rows, the shapes are (4,) and (4, 1).',difficulty='medium',code=True)
add([846,847],'iloc','Position-based indexing and case sensitivity',
 PEOPLE+' The code consistently defines lowercase data_pandas. What is data_pandas.iloc[1, 2], and what if the source table’s uppercase Data_pandas is used with no such name defined?',[
 ('The lowercase expression returns 13; the uppercase expression raises NameError.','Position (1,2) is Anna’s Age, while Python names are case-sensitive.'),
 ('The lowercase expression returns Paris; the uppercase expression refers to the same variable.','Paris is column position 1, and the names differ.'),
 ('The lowercase expression returns 53; the uppercase expression returns 13.','This incorrectly shifts the row and assumes an undefined alias.'),
 ('Both expressions return the entire second row.','Two scalar positional indices select one cell, not a row.')],
 'iloc uses zero-based row and column positions. The capitalized identifier in the source table is a contextual typo, not a case-insensitive alternative.',difficulty='medium',code=True,conflict='The source table prints Data_pandas although the preceding code defines only data_pandas.',conflict_pages=[847])
add(847,'display-info','Visible output versus returned value',
 'With ordinary IPython display behavior and pandas defaults, what do r = display(data_pandas) and s = data_pandas.info() assign?',[
 ('Both r and s are None, although a table and an informational summary are displayed or printed.','Visible output and a function return value are distinct.'),
 ('r is the DataFrame and s is the summary string because those appear on screen.','Neither displayed content is automatically returned in this ordinary use.'),
 ('r is a new cleaned DataFrame and s is its fitted classifier.','These operations do not clean data or fit a model.'),
 ('r is the row count and s is the number of columns.','The displayed summaries do not change the return contract to dimensions.')],
 'The slide’s wording about returning a table or summary is informal. Ordinary display and info present information as a side effect while returning None.',difficulty='medium',code=True,conflict='The source describes display as returning a table and info as returning a summary, conflating visible output with return values.')
add(847,'dtype-inspection','Inspecting column types',
 'Which statement about data_pandas.dtypes and an object dtype is correct?',[
 ('dtypes reports each column’s dtype; object can hold Python objects and is not synonymous with string only.','This separates per-column inspection from a too-narrow object interpretation.'),
 ('dtypes returns one shared dtype that every column must use.','DataFrame columns can have different types.'),
 ('object proves that every value is a string and no missing or non-string objects are possible.','object is a general object-reference dtype, not a string-only guarantee.'),
 ('Reading dtypes automatically converts all columns into float64.','It inspects types rather than converting them.')],
 'The source’s object=string shorthand describes a common case, not the full type contract. Exact inferred string dtype can also depend on pandas version and construction options.',difficulty='medium',code=True,conflict='The source table abbreviates object dtype as object=string.')
add(848,'api-compatibility','Uniform API does not guarantee one-line swaps',
 'Two estimators both expose fit and predict. What must still be checked before swapping one for the other in a workflow?',[
 ('Input assumptions, preprocessing needs, supported methods and evaluation behavior.','Shared method names do not guarantee complete compatibility.'),
 ('Nothing; the same names guarantee identical predictions and probabilities.','Different algorithms and method capabilities can differ.'),
 ('Only the class name’s spelling; all hyperparameters have the same meanings.','Estimator hyperparameters and assumptions vary.'),
 ('Whether NumPy has been uninstalled so the new estimator can run independently.','Removing a dependency is unrelated to API compatibility.')],
 'The uniform estimator interface reduces code changes for compatible replacements, but the literal exactly-one-line claim is not universally valid.',typ='scenario',difficulty='medium',conflict='The source claims that replacing any algorithm requires changing exactly one line of code.')
add(849,'estimator-state','Configuration and fitted model information',
 'What does an estimator object represent in the lecture’s scikit-learn workflow?',[
 ('An algorithm’s configuration together with model information learned when it is fitted.','The object carries the algorithm and fitted state.'),
 ('Only a static picture of the dataset, with no callable training method.','Estimators provide learning-related methods.'),
 ('Only the raw feature file, which becomes a model when renamed.','Data files and fitted estimator objects are different.'),
 ('A notebook kernel that executes every library import on the computer.','An estimator is a model/preprocessing object, not the execution environment.')],
 'Estimator classes organize algorithm behavior and state. Fitting extracts model-specific information from training data and stores it in the estimator.',difficulty='easy')
add([849,850,851],'estimator-roles','Preprocessing versus prediction',
 'In the source’s Iris workflow, which role pairing is correct?',[
 ('StandardScaler is a preprocessing estimator; KNeighborsClassifier is a supervised learning estimator.','One learns scaling statistics and the other uses labeled training examples for classification.'),
 ('StandardScaler predicts species labels; KNeighborsClassifier only rescales columns.','This reverses the roles.'),
 ('load_iris is the classifier; train_test_split is the fitted preprocessing estimator.','Those functions load and partition data rather than perform the two fitted roles.'),
 ('Both objects are plotting Artists because they run in a notebook.','Execution environment does not make estimator objects part of the plotting hierarchy.')],
 'The estimator umbrella includes preprocessing as well as supervised and unsupervised learning and meta-estimators. Not every estimator has prediction as its purpose.',typ='match',difficulty='easy')
add(850,'fit-return','Fit returns the estimator',
 'For a scikit-learn estimator following the source’s API contract, what does fitted = model.fit(X, y) return?',[
 ('The fitted estimator itself.','The return is self, enabling subsequent estimator method calls.'),
 ('Only the predicted labels for X.','Predictions are obtained with predict, not the stated fit return.'),
 ('Only a floating-point accuracy score.','Evaluation is a separate score operation.'),
 ('A pair containing the train and test datasets.','Partitioning is performed by train_test_split, not fit.')],
 'fit learns from data and returns self. Training, prediction and evaluation are separate operations even when the object supports all three.',difficulty='easy',code=True)
add(850,'prediction-probability','Prediction versus class probability shapes',
 'For a fitted single-output classifier that supports predict_proba, consider 12 new samples and 3 classes. What shapes are expected from predict and predict_proba?',[
 ('(12,) and (12, 3).','There is one predicted class per sample and one probability per sample/class pair.'),
 ('(3,) and (3, 12).','This reverses the roles of samples and classes.'),
 ('(12, 3) and (12,).','This swaps labels with probability vectors.'),
 ('A scalar and (3,).','This discards predictions/probabilities for multiple samples.')],
 'The source’s shapes are interpreted in the explicitly stated single-output classification context. They are not a guarantee that every estimator supports probability prediction or those shapes.',difficulty='easy',code=True,assumptions=['Single-output classification; the fitted classifier supports predict_proba.'])
add(850,'score-metric','Default score is estimator-specific',
 'Which statement correctly interprets score(X_test, y_test) in the generic estimator API table?',[
 ('It returns the estimator’s default evaluation metric; its meaning must be checked for that estimator.','The method name alone does not define one universal metric.'),
 ('It always returns training-set classification accuracy, regardless of its inputs.','The supplied data and estimator-specific metric matter.'),
 ('It always returns a probability for each class.','That is the role of predict_proba for supporting classifiers.'),
 ('It always retrains the estimator on the test targets before evaluating.','Ordinary score evaluates a fitted model, not a new fit.')],
 'The table calls score a default evaluation metric. The later KNN classifier example uses accuracy, but this does not make every estimator’s score accuracy.',difficulty='easy')
add(850,'transform-fit-transform','Fitting a transformation versus applying it',
 'What is the key distinction between a fitted transformer’s transform(X) and fit_transform(X)?',[
 ('transform applies learned transformation state; fit_transform fits from the supplied data and transforms it.','This distinguishes application from fitting plus application.'),
 ('transform always predicts target labels, while fit_transform always returns only self.','These are representation-changing operations; the source lists transformed X as their output.'),
 ('transform chooses a train/test split, while fit_transform draws a scatter plot.','Those are unrelated loading/visualization operations.'),
 ('The two methods always have identical effects on fitted state for every new dataset.','Fitting again can replace learned state based on the new data.')],
 'The distinction is crucial for leakage-free preprocessing: fitting learns statistics, whereas transforming held-out data should reuse training-derived statistics.',difficulty='medium',code=True)
save()
add(851,'iris-load','Feature/target separation versus train/test separation',
 'What does load_iris(return_X_y=True) do before the separate train_test_split call?',[
 ('It returns the feature matrix X and target vector y; it does not itself create training and test partitions.','The return option separates predictors from targets, not train from test.'),
 ('It returns only the training features and automatically reserves 20% for testing.','The 20% fraction belongs to train_test_split.'),
 ('It returns a fitted Iris classifier and its accuracy.','The loader supplies data rather than a model.'),
 ('It turns the three species into three feature columns and removes measured features.','The four measurements remain features and species are target classes.')],
 'The two operations solve different problems: retrieving features and labels, then partitioning matched observations into train and test subsets.',difficulty='easy',code=True)
add(851,'iris-features','Iris measurements and target classes',
 'Which interpretation matches the Iris feature and target description in the source?',[
 ('Four measured features are sepal length, sepal width, petal length and petal width; the target identifies one of three species.','This distinguishes measured input columns from target categories.'),
 ('There are three features, one for each species, and four target classes named after measurements.','This swaps features and classes.'),
 ('The target is always the petal length, and species names are continuous predictors.','The shown example is species classification from measurements.'),
 ('Each row has only one feature because all four measurements use the same unit.','Shared units do not collapse distinct feature columns.')],
 'Feature count and class count measure different aspects of the dataset. The species named in the slide are setosa, versicolor and virginica.',difficulty='easy')
add(851,'split-sizes','Iris training and test sizes',
 'Given the built-in Iris dataset has 150 observations with four features, what shapes follow from the source’s test_size=0.2 split?',[
 ('X_train: (120, 4); X_test: (30, 4); y_train: (120,); y_test: (30,).','Twenty percent of 150 is 30, leaving 120; feature count stays four.'),
 ('X_train: (30, 4); X_test: (120, 4); y_train: (30,); y_test: (120,).','This assigns the 20% fraction to training instead of test.'),
 ('X_train: (150, 3); X_test: (150, 1); y_train: (3,); y_test: (1,).','The split partitions observations, not feature columns.'),
 ('X_train: (120, 3); X_test: (30, 3); y_train: (120, 4); y_test: (30, 4).','This confuses class count, feature count and target dimensionality.')],
 'A sample split preserves the four feature columns and paired labels. There are 30 test observations and 120 training observations.',typ='numerical',difficulty='easy',code=True,assumptions=['The built-in Iris data contains 150 observations; targets are single-output class labels.'],steps=['Test count = 0.2 × 150 = 30.','Training count = 150 − 30 = 120.','Keep four feature columns and one class label per row.'])
add([851,852],'scaler-moments','Scope of standardization guarantees',
 'For StandardScaler() fitted on training data with a nonconstant feature, select every correct statement.',[
 ('The transformed training feature has approximately zero mean and unit population variance, up to floating-point error.','The default fitted centering and scaling use training mean and population variance.'),
 ('Test observations are transformed using the training mean and scale.','The source uses transform rather than fitting on test data.'),
 ('The transformed test feature must also have exactly zero mean and unit variance.','Its distribution can differ from the training data.'),
 ('A constant training feature becomes a nonconstant unit-variance feature after scaling.','Centering a constant feature cannot create variation.')],
 'Standardization learns training statistics and reuses them. The usual zero-mean/unit-variance description applies to nonconstant training features, not automatically to test data or constant columns.',correct=[0,1],difficulty='medium',code=True,conflict='The source describes average zero and spread one without stating the training-data and nonconstant-feature scope.',conflict_pages=[851])
add(852,'leakage','Why test data uses transform only',
 'Why does the source call scaler.fit_transform(X_train) but scaler.transform(X_test)?',[
 ('The scale is learned from training data and reused on held-out data without learning test-set statistics.','This preserves the training-defined representation and avoids preprocessing leakage.'),
 ('Test data must be left entirely unscaled because any transformation is training.','Applying learned parameters is not the same as fitting them.'),
 ('The transformer automatically knows the correct test labels and can therefore fit without leakage.','Feature scaling does not justify learning from the held-out set.'),
 ('fit_transform on the test set is required to put both sets in the same coordinate system.','Separate fitting can create different centers/scales instead of the shared training coordinate system.')],
 'The fitted scaler defines the coordinate transformation used by the trained model. Test and new inputs must use that same mapping rather than independently relearn it.',typ='scenario',difficulty='medium',code=True)
add(852,'new-sample','Transforming a single new flower',
 'The fitted KNN model was trained on scaled four-feature samples. What is the correct way to prepare new_flower = [[5.1, 3.5, 1.4, 0.2]]?',[
 ('Apply the existing scaler.transform to the (1, 4) sample, then model.predict.','The new input uses the same feature count/order and fitted scaling.'),
 ('Fit a new scaler on this one sample, then predict with the original model.','That learns unrelated single-sample statistics and changes the representation.'),
 ('Drop the outer brackets so predict receives a guaranteed valid four-row, one-feature matrix.','A one-dimensional list is not the stated two-dimensional sample matrix.'),
 ('Pass its species label as an extra fifth feature before predicting.','The unknown target is not an input measurement and would change feature count.')],
 'Double brackets represent one observation with four features. The source transforms it with the training-fitted scaler and predicts one label.',typ='scenario',difficulty='medium',code=True)
add([851,852],'score-reproducibility','Unseeded split and displayed accuracy',
 'The source omits random_state in train_test_split and displays 93.33333333333333% accuracy. What may be concluded?',[
 ('The printed percentage is one split’s result; a new split need not reproduce it exactly.','No fixed split is specified by this code.'),
 ('Every execution must achieve precisely that percentage because Iris is built in.','A fixed dataset does not fix an unseeded shuffled partition.'),
 ('KNN’s default parameters guarantee that exactly two observations are wrong for any test set.','No such error-count guarantee follows from the estimator defaults.'),
 ('The shown percentage is the probability assigned to class 0 for the new flower.','It is the score on the test set, not the new sample’s probability.')],
 'The code separates prediction on one new sample from test accuracy. Controlled reproductions with explicitly added split seeds produce different scores; those seeds are author test context, not source code.',difficulty='medium',code=True,conflict='A precise test accuracy is displayed after an unseeded train_test_split, so the output is not a deterministic guarantee of the literal code.',conflict_pages=[852])
add(852,'accuracy-count','Interpreting the displayed percentage',
 'Assume the 30-sample test set and classifier accuracy displayed in the source, 93.33333333333333%. How many test samples were correctly classified?',[
 ('28 correct and 2 incorrect.','28/30 = 0.933333….'),
 ('29 correct and 1 incorrect.','29/30 is approximately 96.67%.'),
 ('27 correct and 3 incorrect.','27/30 is 90%.'),
 ('14 correct and 16 incorrect.','14/30 is approximately 46.67%, not 93.33%.')],
 'For ordinary unweighted single-output classification, accuracy is the number correct divided by the test count. The question interprets the shown result, not a promised score for every split.',typ='numerical',difficulty='easy',code=True,steps=['Convert the percentage to a fraction: 0.933333….','Correct count = 30 × 0.933333… = 28.','Incorrect count = 30 − 28 = 2.'],formulas=[formula('accuracy = N_correct / N_test',{'accuracy':'fraction of correctly classified test observations','N_correct':'number of correct predictions','N_test':'number of test observations'},{'accuracy':'dimensionless','N_correct,N_test':'counts'},['Ordinary unweighted single-output classification.'])])
add([851,852],'scaler-calculation','A declared numerical standardization extension',
 'As an explicit one-feature extension of the source’s StandardScaler workflow, fit on values [2, 4, 6] using population variance. What is the transformed value of a held-out observation 8?',[
 ('√6, approximately 2.449.','Training mean is 4 and population variance is 8/3, so (8−4)/√(8/3)=√6.'),
 ('2.0.','This uses sample standard deviation 2 instead of the stated population standard deviation.'),
 ('0.0.','This would result from incorrectly fitting a new scaler on the single held-out value.'),
 ('4.0.','This centers the value but omits division by the training scale.')],
 'The numerical values are an explicitly declared extension, not an Iris-source output. Reusing the training mean and standard deviation gives (8−4)/√(8/3)=√6.',typ='numerical',difficulty='medium',code=True,assumptions=['One feature, no missing values; default centering/scaling and population variance (ddof=0).','The values [2, 4, 6] and held-out 8 are added author context.'],steps=['Training mean μ = (2 + 4 + 6)/3 = 4.','Population variance σ² = ((2−4)² + (4−4)² + (6−4)²)/3 = 8/3.','Use the training scale: z = (8−4)/√(8/3) = √6 ≈ 2.449.'],formulas=[formula('μ = (1/N) Σ x_i; σ² = (1/N) Σ (x_i−μ)²; z = (x−μ)/σ',{'μ':'training mean of the feature','σ²':'training population variance','σ':'positive training standard deviation','N':'number of training observations','x_i':'training feature value for observation i','x':'new feature value','z':'standardized new value','i':'training-observation index'},{'μ,σ,x_i,x':'same feature unit','σ²':'squared feature unit','N,i,z':'dimensionless'},['Nonconstant feature; fit statistics only on training observations.'])])
add([849,850,852],'api-capabilities','Method availability and estimator roles',
 'Select every statement consistent with the lecture’s API and its Iris example.',[
 ('A preprocessing estimator can fit transformation state without being a species classifier.','StandardScaler illustrates fitting without predicting class labels.'),
 ('For the shown KNN classifier, score on the test set evaluates classification accuracy.','This is the metric used by the specific classifier example.'),
 ('Every estimator must support predict_proba merely because the method appears in the API table.','Probability prediction is capability-dependent.'),
 ('fit_transform necessarily returns the estimator itself rather than transformed data.','The table distinguishes fit returning self from fit_transform returning transformed X.')],
 'The API table collects common conventions, not an obligation that every estimator implement every operation. Distinguish fit’s return value, transformer output and classifier evaluation.',correct=[0,1],difficulty='medium')
add([826,844,850,852,853],'pipeline-synthesis','Putting the library workflow together',
 'A tabular classification task requires cleaning records, fitting training-only scaling, fitting a classifier, evaluating held-out data and plotting diagnostics. Which workflow is coherent?',[
 ('Use pandas for tabular preparation, fit preprocessing on training data, transform held-out inputs with it, fit/evaluate the classifier, and plot diagnostics with matplotlib.','This combines the library roles while maintaining the train/test boundary.'),
 ('First fit scaling on the whole dataset, then split it; this guarantees a more independent test estimate.','Fitting preprocessing before the split can leak held-out information.'),
 ('Replace target labels with matplotlib colors, then treat the scatter plot itself as the trained classifier.','A visual label encoding is not a fitted prediction model.'),
 ('Use a fresh scaler for every test sample so every input becomes zero before the original classifier sees it.','This destroys the common training-defined representation.')],
 'The source’s ecosystem is a cooperating workflow, not interchangeable tools with identical roles. Training-derived preprocessing, model fitting, evaluation and visualization serve distinct purposes.',typ='scenario',difficulty='medium')
add(830,'numpy-tools','Numerical capabilities beyond array storage',
 'Besides storing multidimensional arrays, which capability group is explicitly associated with NumPy in the lecture?',[
 ('Mathematical operations, linear algebra, Fourier transforms and random-number generation.','These are the numerical capabilities named in the source.'),
 ('Notebook-server routing, live kernel restart and browser authentication.','These are environment/infrastructure functions, not the listed NumPy role.'),
 ('SQL database administration, spreadsheet styling and slide publishing.','These are not the numerical array capabilities described.'),
 ('Only scalar integer addition; matrix and random operations require an unrelated language.','This contradicts the listed numerical operations.')],
 'NumPy supplies an array foundation together with mathematical, linear-algebra, Fourier and random-sampling tools; it is not just a file container.',difficulty='easy')
add(847,'info-summary','Choosing a structural DataFrame summary',
 'Which operation is suited to inspecting a DataFrame summary containing column names, non-null counts, dtypes and memory information?',[
 ('data_pandas.info().','This prints a concise structural summary.'),
 ('data_pandas.head(2).','This shows the first two rows, not the full structural summary.'),
 ('data_pandas.tail(2).','This shows the final two rows, not the full structural summary.'),
 ('data_pandas.dtypes alone.','This reports column dtypes but does not by itself supply all the requested information.')],
 'info is the structural inspection tool in the source table. Its printed summary is distinct from its return value, which is None.',difficulty='easy',code=True)
add(849,'estimator-categories','Estimator categories in the lecture',
 'Which list gives the four estimator workflow categories named on the source slide?',[
 ('Supervised learning, unsupervised learning, preprocessing and meta-estimators.','These are the four headings in the slide.'),
 ('Training rows, test rows, feature columns and target columns.','These categorize data partitions and roles, not estimator classes.'),
 ('Figures, Axes, lines and annotations.','These belong to plotting organization, not estimator taxonomy.'),
 ('NumPy arrays, pandas DataFrames, CSR matrices and COO matrices.','These are data representations, not the four estimator categories.')],
 'The lecture groups estimators by their function in the workflow, including preprocessing and meta-estimators as well as learning estimators.',difficulty='easy')
# Link repeated summary content to the relevant existing concepts, not duplicate recall items.
for n in [1,2,9,24,30,41,49,66]:
 q=b.questions[n-1]
 if any(c['physicalPage']==853 for c in q['citations']):continue
 q['citations'].append({'slideId':'lectures-p0853','sourceId':'lectures','sourceSha256':SHA,'physicalPage':853,'kind':'statement','locator':'Lecture 28, physical PDF page 853, actual printed footer 32: repeated library workflow summary','evidenceText':NOTES[853][0],'role':'premise','region':None})
 for cid in q['conceptIds']:b.concepts[cid]['slideIds'].append('lectures-p0853')
# Correct a duplicate distractor before freezing: retain a distinct tail-order misconception.
q=next(q for q in b.questions if 'head-tail' in q['tags'])
for o in q['options']:
 if o['text'].startswith('head: Anna, John; tail: Linda, Peter after'):
  o['text']='head: John, Anna; tail: Linda, Peter.'
  q['solution']['optionExplanations'][o['id']]='head is correct, but tail retains Peter then Linda rather than reversing the final rows.'
q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']]
save(frozen=True)
packet=R/f'audits/blind-{BATCH}.json';batchpath=R/f'data/question-batches/{BATCH}.json'
manifest={'batchId':BATCH,'authorId':AUTHOR,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'questionCount':len(b.questions),'conceptCount':len(b.concepts),'physicalPages':list(NOTES),'sourceVersions':{'lectures':SHA},'blindPacketPath':str(packet.relative_to(R)),'blindPacketSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'questionHashConvention':'scripts.validate.question_hash; excludes only status and reviewIds','questions':[{'questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q)} for q in b.questions],'independentReviewStillRequired':True}
coverage=[]
for p,(note,excluded) in NOTES.items():
 coverage.append({'physicalPage':p,'printedSlideNumber':str(p-821),'slideId':f'lectures-p{p:04d}','sourceSha256':SHA,'visualInspection':'complete','disposition':'excluded' if excluded else 'drafted-awaiting-independent-review','exclusionReason':excluded,'observedMeaningfulContent':note,'conceptIds':[c['id'] for c in b.concepts.values() if f'lectures-p{p:04d}' in c['slideIds']],'questionIds':[q['id'] for q in b.questions if any(c['physicalPage']==p for c in q['citations'])]})
assert all(row['exclusionReason'] or (row['conceptIds'] and row['questionIds']) for row in coverage)
(R/f'audits/{BATCH}-author-coverage-ledger.json').write_text(json.dumps({'batchId':BATCH,'status':'Author coverage proposal only; independent substantive challenge required.','pageCount':len(coverage),'exclusions':sum(bool(x['exclusionReason']) for x in coverage),'pages':coverage},ensure_ascii=False,indent=2)+'\n')
assert all('correctOptionIds' not in q and 'solution' not in q and all('evidenceText' not in c for c in q['citations']) for q in json.loads(packet.read_text()))
manifest['artifactSha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [batchpath,packet,R/f'data/inspection-batches/{BATCH}.json',R/f'audits/{BATCH}-author-coverage-ledger.json',R/f'audits/{BATCH}-source-issues.json',R/f'audits/{BATCH}-author-code-checks.json',Path(__file__),R/'scripts/check_W06_L28_author.py']}
(R/f'audits/{BATCH}-frozen-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('FROZEN_PACKET_SHA256',manifest['blindPacketSha256'])
