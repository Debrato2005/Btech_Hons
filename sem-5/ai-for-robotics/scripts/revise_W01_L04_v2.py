"""Repair exactly 37 reviewed L04 items, preserve 94 approved hashes, never self-approve."""
import json,pathlib,hashlib,copy,datetime,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash,schema_errors,validate_bank
P=ROOT/'data/question-batches/W01-L04.json';raw=P.read_bytes();b=json.loads(raw);before=copy.deepcopy(b);qs={q['id']:q for q in b['questions']}
reviews=json.loads((ROOT/'data/reviews/W01-L04-v1-independent.json').read_text());good={r['questionId']:r for r in reviews if r['decision']=='verified'};bad={r['questionId']:r for r in reviews if r['decision']=='flagged'}
assert len(good)==94 and len(bad)==37
assert all(qs[k]['version']==1 for k in qs),'Refuse to reapply after revisions.'
assert all(question_hash(qs[r['questionId']])==r['questionSha256'] for r in reviews)
assert hashlib.sha256(raw).hexdigest()=='aaf536abf4b31cff534f4efed66a49f84b6c108102959279117e7236934f8e3d'
archive=ROOT/'data/question-batches/archive/W01-L04-v1.json'
if archive.exists():assert archive.read_bytes()==raw
else:archive.write_bytes(raw)
AUTHOR='define_robotics_data_contracts:L04-v2-revision-author';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def q(k):return qs['W01-L04-'+k]
def options(k,items):
 x=q(k);assert x['id'] in bad
 for oid,text,why in items:
  next(o for o in x['options'] if o['id']==oid)['text']=text
  x['solution']['optionExplanations'][oid]=('Correct. ' if oid in x['correctOptionIds'] else 'Incorrect. ')+why
 x['solution']['misconceptions']=[x['solution']['optionExplanations'][o['id']].removeprefix('Incorrect. ') for o in x['options'] if o['id'] not in x['correctOptionIds']]
for k in bad:
 x=qs[k];x['version']=2;x['status']='draft';x['reviewIds']=[];x['revisionAuthors']=list(dict.fromkeys(x.get('revisionAuthors',[])+[AUTHOR]));x['revisionHistory']=x.get('revisionHistory',[])+[{'version':2,'authorId':AUTHOR,'revisedAt':now,'priorQuestionSha256':bad[k]['questionSha256'],'reason':'Address the frozen v1 independent quality finding; new independent review required.'}]
for k,r in bad.items():
 if not r['checks']['difficulty']:qs[k]['difficulty']='medium'
options('P0127-Q01',[
 ('o2','Dynamic systems, computer science and control theory','The named third foundation is domain ontology, not control theory, even though control is relevant to robotics.'),
 ('o3','Dynamic systems, numerical analysis and domain ontology','The named middle foundation is computer science rather than the narrower numerical-analysis substitution.'),
 ('o4','Probability theory, computer science and domain ontology','The first named foundation is dynamic systems. Probability is useful in modeling but is not the first item in this stated trio.')])
options('P0151-Q01',[
 ('o2','The Jetson compute module beneath the heat sink','The slide distinguishes the compute module from the reference carrier board whose label explicitly mentions I/O ports.'),
 ('o3','The heat-sink and fan assembly above the module','That assembly is the cooling hardware above the module, not the lower board identified by the I/O label.'),
 ('o4','A separate external I/O expansion board outside the developer kit','The arrow points to the carrier board within the pictured kit, not to an additional external board.')])
options('P0152-Q02',[
 ('o2','Configure boot and install the IDE → run the course programs → set up the environment and required packages','This attempts the course programs before preparing their environment and dependencies; the slide places program execution last.'),
 ('o3','Set up the target environment and packages → configure the target for initial boot and install its IDE → run programs','This reverses the source sequence of making the target usable and then preparing its Python environment.'),
 ('o4','Configure boot and install the IDE → create an empty environment → run programs before installing their required packages','The slide calls for an environment with required packages before program execution, not dependency installation afterward.')])
options('P0153-Q01',[
 ('o2','SD Card Image and NVIDIA SDK Manager; NVIDIA SDK Manager is preferred','These are the two named methods, but the source explicitly attaches its simplicity preference to SD Card Image.'),
 ('o3','SD Card Image and an APT package update; SD Card Image is preferred','The second named initial-flashing method is NVIDIA SDK Manager, not an APT package update.'),
 ('o4','NVIDIA SDK Manager and an APT package update; NVIDIA SDK Manager is preferred','This omits the source\'s SD Card Image method and reverses which named method receives the simplicity preference.')])
options('P0153-Q02',[
 ('o2','AMD64 .deb package; select the created virtual-environment interpreter','The interpreter choice matches, but the slide specifies ARM64 rather than AMD64 for this device.'),
 ('o3','ARM64 .deb package; select the unrelated system interpreter instead of the created environment','The package matches, but the slide instructs selection of the created virtual-environment interpreter.'),
 ('o4','ARM64 .rpm package; select the created virtual-environment interpreter','The architecture and interpreter are plausible, but the displayed editor package is .deb, not .rpm.')])
options('P0154-Q01',[
 ('o2','Isolating source-code folders while forcing all projects to use one global package set','Folder organization alone is not the stated benefit; project-specific package and interpreter contexts reduce shared-dependency conflicts.'),
 ('o3','Permanently freezing every installed package version without recording or managing dependencies','The source promises isolation and flexibility, not automatic permanent version locking.'),
 ('o4','Synchronizing package upgrades automatically across every project interpreter','Automatic cross-project synchronization would undermine the separate project-specific dependencies highlighted on the slide.')])
options('P0155-Q02',[
 ('o2','It builds on roboticstoolbox and machinevisiontoolbox, which have no numerical or plotting dependencies','The source explicitly names NumPy, SciPy and Matplotlib as supporting dependencies of the toolboxes.'),
 ('o3','It builds on NumPy/SciPy/Matplotlib, which are stated to require roboticstoolbox and machinevisiontoolbox','This reverses the stated dependency direction: the robotics and vision toolboxes depend on the numerical/plotting packages.'),
 ('o4','It builds on roboticstoolbox alone; machinevisiontoolbox is excluded from the stated relationship','The source explicitly includes both roboticstoolbox and machinevisiontoolbox.')])
options('P0159-Q01',[
 ('o2','Phase portraits require time on the horizontal axis; time-history plots relate state variables without a time axis','This reverses the state-space versus time-history distinction. A phase portrait need not use time as an axis.'),
 ('o3','Phase portraits display frequency-response gain and phase; time-history plots display only state-space equilibria','This assigns frequency-response plotting to phase portraits and restricts time histories to a different state-space task; neither matches the slide.')])
options('P0159-Q02',[
 ('o2','3D paths: plt.imshow; matrices: ax.plot3D; animation: FuncAnimation','The animation association matches, but image/matrix display and 3D spatial plotting are interchanged.'),
 ('o3','3D paths: ax.plot3D; matrices: FuncAnimation; animation: plt.imshow','The 3D association matches, but the animation update mechanism and matrix-image display call are interchanged.'),
 ('o4','3D paths: FuncAnimation; matrices: plt.imshow; animation: ax.plot3D','Matrix display matches, but the slide names ax.plot3D for spatial paths and FuncAnimation for frame animation. Animating an artist is not the same role as drawing its 3D data.')])
options('P0159-Q03',[
 ('o2','bode_plot, sns.heatmap and plt.imshow are all attributed to matplotlib.pyplot','The slide explicitly credits python-control for bode_plot, and the sns alias distinguishes the Seaborn-style heatmap from plt.imshow.'),
 ('o3','bode_plot is attributed to Matplotlib; sns.heatmap to Seaborn; plt.imshow to Matplotlib','Only the bode_plot attribution is wrong: the slide names python-control for it.'),
 ('o4','bode_plot is attributed to python-control; sns.heatmap to Matplotlib; plt.imshow to Seaborn','The bode_plot attribution is right, but the heatmap/imshow library roles are reversed.')])
options('P0160-Q01',[
 ('o2','Read CSV → interpret timestamp seconds as milliseconds → set the converted time as index','The source explicitly passes unit="s". Treating those values as milliseconds changes their time scale.'),
 ('o3','Read CSV → sort by joint position → use row numbers as the time index','Joint position order and row numbers do not preserve the source\'s measured timestamp intervals or establish the displayed datetime index.'),
 ('o4','Read CSV → set the raw numeric timestamp as index → apply a time-duration window without datetime conversion','The source first converts the timestamp values to datetime and then sets that time column as the index; it does not omit conversion.')])
options('P0160-Q06',[
 ('o2','Compute sliding statistics; change time sampling; aggregate groups; combine related tables','This swaps resample and rolling. Resample addresses time sampling, while rolling calculates moving-window statistics.'),
 ('o3','Change time sampling; aggregate groups; compute sliding statistics; combine related tables','This swaps rolling and groupby: one uses windows, the other groups records by a key.'),
 ('o4','Change time sampling; compute sliding statistics; combine related tables; aggregate groups','This reverses groupby and merge/join. Groupby aggregates within groups; merge/join combines tables by related keys or indexes.')])
options('P0160-Q07',[
 ('o2','describe() replaces each position with its mean; to_csv writes only the displayed summary rather than the DataFrame','describe returns a summary without making that claimed replacement, and the final call is df.to_csv, not summary.to_csv.')])
options('P0161-Q04',[
 ('o2','TypeError from passing two positional arguments to the call','The first failure is resolving the undefined function name. No callable is found whose argument binding could raise this TypeError.'),
 ('o3','AttributeError from looking up a missing object attribute','The call uses a bare global identifier, not a dotted attribute lookup such as object.method.'),
 ('o4','UnboundLocalError from reading a function-local variable before its assignment','The failed name is looked up at top level in the stated fresh namespace, not as a local variable inside a function with a later assignment.')])
options('P0164-Q01',[
 ('o2','Their move method signatures bind and store the constructor arguments','Ordinary move methods are not initialization hooks. The inherited Robot.__init__ stores name and speed.'),
 ('o4','Their first move call creates missing name and speed attributes automatically','The instances receive these attributes during construction through the parent initializer, before move is called.')])
options('P0165-Q01',[
 ('o2','NumPy stores/updates arrays; Matplotlib computes Euclidean distance; SciPy plots the path','The source assigns the Euclidean call to scipy.spatial.distance and plot/scatter calls to Matplotlib; these final two roles are swapped.'),
 ('o3','SciPy constructs the motion arrays; NumPy calls euclidean; Matplotlib plots the path','The array constructors use the np alias, whereas euclidean is imported from SciPy. The first two roles are swapped.'),
 ('o4','Matplotlib stores/updates motion arrays; SciPy computes Euclidean distance; NumPy plots the path','The SciPy role matches, but NumPy supplies the arrays and Matplotlib supplies the plotting calls, not the reverse.')])
options('P0166-Q07',[
 ('o2','It succeeds by automatically promoting the existing integer pose array to floating dtype in place','The in-place operation keeps the existing integer output buffer; it does not replace it with the promoted result used by ordinary pose=pose+m.'),
 ('o3','It succeeds by truncating each floating result to an integer under the default casting rule','The tested default same_kind output-casting rule rejects this float-to-integer write; it does not silently truncate.'),
 ('o4','The first row [1.0,1.0] succeeds, and the error occurs only when a later row contains 0.5','The rule uses the floating dtype of the result, not whether this particular row happens to have integral-valued entries. The first update already fails.')])
q('P0166-Q07')['solution']['justification']='The initial pose has integer dtype, while the motions array has floating dtype because it contains 0.5 elsewhere. Even its first row [1.0,1.0] produces a floating result. In-place addition attempts to write that result into the existing integer buffer and the tested same_kind casting rule rejects it.'
q('P0166-Q07')['solution']['simpleExplanation']='In-place addition must fit the existing integer array. Floating dtype is enough to trigger rejection here, even when the first motion values are whole numbers.'
q('P0166-Q07')['solution']['optionExplanations']['o1']='Correct. '+q('P0166-Q07')['solution']['justification']
q('P0166-Q07')['assumptions'][1]='Use the tested NumPy 2.3.5 runtime with ordinary default array dtype inference and the ufunc same_kind output-casting rule.'
q('P0166-Q07')['solution']['steps']=['Initial pose=np.array([0,0]) has integer dtype.','The motions constructor includes 0.5, so every row, including [1.0,1.0], has floating dtype.','The first in-place addition produces floating output but targets the existing integer buffer.','The default same_kind rule rejects that cast. Out-of-place pose=pose+m instead creates a new promoted array.']
options('P0168-Q01',[
 ('o2','NumPy, SciPy, Matplotlib and SymPy','The summary\'s four-library core names Pandas in this position. SymPy appears elsewhere for mathematical modeling, but not in this listed quartet.'),
 ('o3','NumPy, SciPy, Pandas and Seaborn','The named quartet includes Matplotlib rather than Seaborn.'),
 ('o4','NumPy, Matplotlib, Pandas and Numba','The named quartet includes SciPy rather than Numba; Numba is separately associated with JIT acceleration.')])
options('P0168-Q02',[
 ('o3','NumPy; Ray; Numba; CuPy/JAX','Only the first association matches. The row assigns JIT to Numba, GPU arrays to CuPy/JAX, and parallelism to Ray. This tests source mappings, not every capability a library might have.')])
options('P0168-Q03',[
 ('o2','A physics engine that integrates all robot dynamics inside rclpy itself','The source gives physics environments to PyBullet/MuJoCo and assigns rclpy the interface bridge role, not the physics-engine role.'),
 ('o3','A ROS visualization interface used only to display recorded sensor streams','The named role is connecting Python simulation and physical-robot interfaces, not merely displaying recorded data.'),
 ('o4','A reinforcement-learning trainer that updates policy weights from simulation rollouts','The summary separates RL training tools from the rclpy bridge; rclpy is not assigned the policy-training role.')])
options('P0168-Q05',[
 ('o3','Fit parameters only to simulated trajectories and omit comparison with physical measurements','The final row explicitly includes validation against physical measurements. Matching only the simulator to itself cannot establish the required reality agreement.')])
options('P0158-Q07',[
 ('o2','FFTW transform routines','The linear-algebra box explicitly names LAPACK wrappers, not a Fourier-transform implementation.'),
 ('o3','ODEPACK time-integration routines','The named foundation is LAPACK linear algebra, not a time-integration implementation.'),
 ('o4','BLAS operations alone, with no higher-level solver or factorization wrappers','The source specifically identifies LAPACK wrappers for advanced linear algebra, not only basic linear-algebra operations.')])
options('P0159-Q04',[
 ('o3','An ordered 3D end-effector trajectory drawn as connected spatial points','The slide assigns this to the 2D/3D Robot Paths box, not the Heatmaps/Matrices examples.'),
 ('o4','Frequency-response gain and phase curves drawn against frequency','The slide associates frequency-response plots with Bode/Nyquist, not the heatmap/matrix example list.')])
options('P0159-Q05',[
 ('o2','FuncAnimation with a complete figure redraw for every frame','FuncAnimation matches, but the source explicitly pairs it with blitting rather than stating a complete redraw for every frame.'),
 ('o3','Repeated plt.plot calls without an animation update function','The source names FuncAnimation with blitting, not merely repeatedly creating line plots.'),
 ('o4','A single static plt.imshow call with no frame updates','The static matrix-image operation does not supply the source\'s animation-and-blitting pairing.')])
options('P0160-Q08',[
 ('o4','rolling()','The table assigns rolling to sliding-window statistics. Its named time-rate alignment operation is resample, not rolling.')])
options('P0168-Q06',[
 ('o2','Integrating a differential-equation state trajectory and advancing simulation time','The summary assigns differential-equation dynamics simulation to integration, while its optimize row names PID tuning and system identification.'),
 ('o3','Filtering encoder measurements and estimating their frequency spectra','These are signal-processing tasks rather than the additional optimize applications named in the summary.'),
 ('o4','Finding spatial neighbors and constructing convex hulls','Those are spatial-calculation tasks, not the additional optimize applications named in the summary.')])
# Repair the actual arithmetic explanation, preserving the correct answer and all options.
x=q('P0160-Q04');why='These values are approximately 1/0.02, 1/0.04 and 1/0.06: reciprocals of position increments, with units 1/m before any mistaken labeling. They omit the required elapsed-time scaling. The inverse of the correct velocities would instead be [1,0.5,0.333...] s/m.'
x['solution']['optionExplanations']['o4']='Incorrect. '+why
x['solution']['misconceptions']=[x['solution']['optionExplanations'][o['id']].removeprefix('Incorrect. ') for o in x['options'] if o['id'] not in x['correctOptionIds']]
# Make revised numeric wording human-readable without touching approved content.
for k in ['P0162-Q07','P0162-Q08']:
 x=q(k);x['stem']=x['stem'].replace('to0.5','to 0.5').replace('to1.0','to 1.0')
x=q('P0163-Q05');next(o for o in x['options'] if o['id']=='o2')['text']='result stores 6.0 because the local distance exists'
x=q('P0166-Q03');x['solution']['justification']='The segment lengths are √2, √1.25, √1.25 and √2. Their sum is 2√2 + √5 ≈ 5.064 coordinate units.';x['solution']['simpleExplanation']=x['solution']['justification'];x['solution']['optionExplanations']['o1']='Correct. '+x['solution']['justification']
# Assert exactly the requested content changed, and every approved correctness hash is intact.
old={x['id']:x for x in before['questions']};changed={k for k in qs if question_hash(qs[k])!=question_hash(old[k])};assert changed==set(bad)
assert all(question_hash(qs[k])==r['questionSha256'] for k,r in good.items())
assert all(qs[k]['status']=='draft' and qs[k]['version']==2 and AUTHOR in qs[k]['revisionAuthors'] and not qs[k]['reviewIds'] for k in bad)
schema=json.loads((ROOT/'data/schema.question.json').read_text());errs=[e for x in b['questions'] for e in schema_errors(x,schema)];assert not errs,errs
b['revisionAuthors']=list(dict.fromkeys(b.get('revisionAuthors',[])+[AUTHOR]));b['revisionStatus']='37 v2 revisions await a distinct independent reviewer; 94 v1 approved correctness hashes are unchanged.'
# Keep original source issues/author checks for history; this metadata adds, not overwrites, revision checks.
b['revisionChecks']={'revision':2,'revisionAuthorId':AUTHOR,'revisedCount':37,'preservedApprovedCount':94,'independentlyVerified':False,'historicalReviewPath':'data/reviews/W01-L04-v1-independent.json'}
P.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
# Answer-free current-version question manifest and minimally exposed review packet.
packet={'schemaVersion':'1.0.0','batchId':'W01-L04','revision':2,'status':'frozen_revisions_ready_for_independent_review','revisionAuthorId':AUTHOR,'reviewInstruction':'A distinct reviewer must derive answers from source artifacts and save them before opening the author batch or revision summary. This packet deliberately omits keys, solutions and citation evidenceText. Record any prior exposure truthfully.','questions':[]}
for x in b['questions']:
 if x['id'] not in bad:continue
 z={k:copy.deepcopy(x[k]) for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions']}
 z['citations']=[{k:v for k,v in c.items() if k!='evidenceText'} for c in x['citations']];z['questionSha256']=question_hash(x);packet['questions'].append(z)
pp=ROOT/'audits/blind-W01-L04-v2-revisions.json';pp.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
assert len(packet['questions'])==37
assert all('evidenceText' not in c for x in packet['questions'] for c in x['citations'])
assert all('correctOptionIds' not in x and 'solution' not in x for x in packet['questions'])
manifestpath=ROOT/'audits/W01-L04-v2-revision-question-hashes.json';manifestpath.write_text(json.dumps({x['id']:question_hash(x) for x in b['questions'] if x['id'] in bad},indent=2)+'\n')
# Validate temporary merged slice, preserving only genuine existing v1 approvals.
sources=json.loads((ROOT/'sources/manifest.json').read_text());slides=[json.loads(line) for sid in ['lectures','assignments'] for line in (ROOT/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()];updates={x['id']:x for x in json.loads((ROOT/'data/inspection-batches/W01-L04.json').read_text())['slides']};slides=[updates.get(x['id'],x) for x in slides]
tq=copy.deepcopy(b['questions']);tc=copy.deepcopy(b['concepts'])
for x in tq:
 if x['id'] in good:x['status']='verified';x['reviewIds']=[good[x['id']]['id']]
for c in tc:
 if c['status']!='flagged':c['status']='verified' if any(k in good for k in c['questionIds']) else 'drafted'
tmp={'schemaVersion':'1.0.0','bankVersion':'L04-v2-revisions-isolated','title':'L04 revision temporary validation','complete':False,'sources':sources['sources'],'assets':sources['assets'],'slides':slides,'questions':tq,'concepts':tc,'reviews':reviews,'learningTools':{'formulaSheet':[],'confusionPairs':[],'traps':[],'algorithmVisualizations':[],'numericalFamilies':[]}}
v=validate_bank(tmp,ROOT,check_files=True)
summary={'schemaVersion':'1.0.0','batchId':'W01-L04','revision':2,'revisionAuthorId':AUTHOR,'revisedAt':now,'archivedV1Path':str(archive.relative_to(ROOT)),'archivedV1Sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'revisedCount':37,'preservedApprovedCount':94,'preservedApprovedHashes':{k:question_hash(qs[k]) for k in good},'revisedQuestionHashes':{k:question_hash(qs[k]) for k in bad},'changes':[{'questionId':k,'oldVersion':1,'newVersion':2,'oldSha256':question_hash(old[k]),'newSha256':question_hash(qs[k]),'changedFields':[f for f in qs[k] if qs[k][f]!=old[k].get(f)],'findingsAddressed':bad[k]['findings']} for k in sorted(bad)],'blindPacketPath':str(pp.relative_to(ROOT)),'blindPacketSha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'authorBatchSha256':hashlib.sha256(P.read_bytes()).hexdigest(),'validation':v,'independentVerification':False,'scope':'Only the 37 frozen flagged questions were revised; all 94 approved hashes remain unchanged. The v1 batch and its independent review are archived/preserved. Every revised question is draft with revision author attribution and awaits another reviewer. No bank, source or Git edits.'}
(ROOT/'audits/W01-L04-v2-revision-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['revisedCount','preservedApprovedCount','blindPacketSha256','authorBatchSha256','validation']},indent=2));assert v['valid'],v
