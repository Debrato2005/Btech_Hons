"""Independent bounded source-subpart challenge. Writes audits only, not acceptance records."""
import datetime,hashlib,json,pathlib,sys,collections
R=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'));from validate import question_hash
D=R/'audits/assignment-coverage';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
notes={
1:[
'Human-harm priority over self-protection is assessed; fictional law hierarchy is not a deployment safety standard.',
'Offline CAD programming and real-cell calibration/alignment are retained, rather than treating offline motion as automatically accurate.',
'Reward-based learning and deep-network representation overlap within ML; revised neutral scenario no longer gives the conclusion away.',
'Current-state policy and environment Markov transition assumption are distinguished; these are not equivalent assertions.',
'State-space input symbol u is identified in the supplied model.',
'Both gradient components are calculated, including the cross term and the continuation page.',
'Probabilistic observation model retains sensor-noise motivation rather than implying certainty.',
'Task-relative fidelity is bounded separately from resolution and representation detail.',
'Modular message-connected robot components are assessed without requiring a particular live ROS environment.',
'Changing camera-to-base transform role is distinguished from static robot-description structure.'
],
2:[
'Proper rotation orthogonality, inverse-transpose and determinant-one conditions are retained across alternatives.',
'Homogeneous-transform last row is assessed as a representation constraint.',
'Four revolute plus two prismatic coordinates counted with independence qualification, separate from instantaneous rank.',
'Planar 2R forward-position formula includes both x and y components and angle accumulation.',
'Inverse-kinematic solution-count claim is restricted to stated geometry, not universal for every 6-DOF robot.',
'Malformed original linkage/angle statement is preserved; explicit 2R model assesses positive and negative angle branches.',
'Rank-one 2×2 Jacobian is interpreted through null vector and attainable output direction, rather than scalar rank alone.',
'Boundary and interior singularity classes are retained.',
'Explicit lever arm and force remove ambiguous figure labels; cross-product torque sign and units are assessed.',
'Static force balance excludes gravity/inertia only under explicit assumptions; conflicting printed highlight and answer line are preserved.'
],
3:[
'Parallel-axis displacement perpendicular to z is used; axial displacement does not contribute to Izz.',
'Solid-cylinder axial inertia is distinguished from transverse inertia and thin-shell alternatives; source figure axis retained.',
'Angular-momentum relation to inertia and angular velocity is assessed.',
'Net inertial-force magnitude includes both nonzero acceleration components.',
'Fictitious base acceleration for gravity uses the specified physical-down coordinate convention.',
'Terminal zero external force/moment does not imply zero internal dynamics; page10 prompt/page11 figure provenance repaired.',
'Rate-dependent velocity term is separated from configuration-dependent gravity at the same joint configuration.',
'Total kinetic energy includes translation and rotation, not only one component.',
'Full symmetric 2R point-mass inertia matrix entries are assessed against the geometry; candidate matrices are not labeled as derivation.',
'Four outputs versus six unordered mixed-rate products determines the rectangular coefficient matrix, distinct from squared-rate terms.'
],
4:[
'Six independent endpoint position/velocity/acceleration constraints require minimum quintic degree.',
'Cubic candidate is checked against both endpoint position and velocity, not just final position.',
'Explicit LSPB piecewise velocity distinguishes continuous velocity from acceleration jumps; source false blanket continuity claim remains disputed.',
'Rotation-parameter distance is bounded to the same fixed axis modulo a full turn, avoiding arbitrary-vector distance overclaim.',
'Tight repeated clustering with a systematic target offset distinguishes high repeatability from poor accuracy.',
'Two-link inner and outer reach limits form an annulus, so an inner-hole target is unreachable. Numeric reuse is not a new concept.',
'Local rank-nullity of a regular 6×7 Jacobian is already assessed identically by W11-L54-P1719-Q02. Preserve assignment provenance by reuse or a distinct reasoning repair.',
'Payload-induced elastic link bending is distinguished from encoder angle error; compliance modeling or compensation addresses the missing effect.',
'SCARA lateral compliance and vertical stiffness insertion rationale duplicates W04-L18-Q031 and W04-L20-P0609-Q02. This is duplicate coverage, not missing knowledge.',
'Planar 2R Jacobian singularities use sin(theta2)=0 at both straight and folded configurations.'
],
5:[
'Critical damping is derived from the characteristic discriminant and repeated pole, not a bare coefficient label.',
'PD design uses total effective stiffness/damping before subtracting plant coefficients; continuation page included.',
'Back-EMF proportionality and opposing effect remain distinct from the full loaded terminal-voltage balance.',
'Resonance/bandwidth ratio is a design guideline, not proof of stability.',
'Nonlinear cancellation uses the explicitly normalized x-double-dot+x-cubed=u model and sign.',
'Contact-force ratio retains numerator/denominator direction and dimensions.',
'Computed-torque alpha/beta selection is bound to the supplied torque mapping convention, not inferred from source without a definition.',
'Critical-damping time response includes initial conditions and repeated-root linear factor; distinct from Q1 damping classification.',
'Tracking errors include position, velocity and acceleration as the course formulation, not every implementation requirement.',
'Jacobian transpose force-to-joint-torque mapping is evaluated numerically and grounded in virtual power.'
],
6:[
'kNN similarity depends on metric and feature scaling, rather than raw numeric proximity alone.',
'Numeric class codes are separated from continuous regression targets.',
'Supervised labeled data is distinguished from unsupervised data.',
'A plane is also a hyperplane in 3D; the original overlapping terminology is explicitly qualified.',
'fit(X,y) training role is distinguished from prediction, scoring and parameter access.',
'Array dtype descriptor, object-array exception and per-column DataFrame types are distinguished.',
'Squared-error regression-leaf mean is evaluated, not a median or arbitrary training value.',
'Figure has root x1<=10 -> mean(3,5,7)=5; else x2<=5 -> mean(10,14,18)=14; else mean(30,40)=35. Current item tests only (12,3), the root-false/second-true path. Root equality/short-circuit, reached second equality and rightmost leaf are not directly assessed.',
'Policy state-to-action role is assessed.',
'Q-learning update includes alpha, gamma, reward and maximum next-Q; terminal no-bootstrap comparison also assessed.'
],
7:[
'Pinhole projection compares depths with explicit camera/world-frame assumption and consistent focal-length units.',
'Depth scaling and fixed-depth parallel-line exception both assessed; avoids universal parallel-convergence claim.',
'uint8 wrapping and float-promoted addition are both assessed.',
'Asymmetric full kernel is used for both correlation and true flipped convolution; all entries retained.',
'Circularity uses pixel area units consistently; square candidate is not asserted to be uniquely determined.',
'All eigenvalue table rows are classified as flat, edge or corner, not only the highlighted corner row.',
'All training-cycle stages are retained in order.',
'Both additive-bias and threshold-sign interpretations are calculated; printed source inconsistency retained.',
'Kernel size and full spatial/channel output shape are both assessed.',
'Course YOLO comparison distinguishes anchor-free boxes from predefined box priors without live product claims.'
],
8:[
'Weighted undirected source graph is fully transcribed. UCS cheaper frontier update and pop-time goal termination are exercised; unused post-goal branches do not create a separate assessment obligation.',
'Heuristic cost-to-go role and zero-heuristic reduction to UCS are assessed with tie/optimality conditions.',
'All three frontier records are compared for A*, UCS and greedy selection; table columns are not reduced to only the highlighted choice.',
'Explicit repeatable H-to-L-to-H loop explains Bug0 failure without claiming all concave obstacles always trap it.',
'Slow target-network purpose is distinguished from exploration, replay and convergence guarantees.',
'Nonterminal target and TD error plus terminal no-bootstrap target are assessed; original stray Answer C remains source artifact.',
'GNSS waypoint feedback tracking is distinguished from preprocessing only.',
'Common receiver clock bias is converted through speed of light after satellite-clock correction.',
'Both weighted numerator and normalized denominator are explicit; source denominator typo and lecture-reference mismatch are preserved.',
'Crisp controller output is distinguished from fuzzy memberships without asserting every crisp set is singleton.'
],
9:[
'All three real-coded children are calculated and ranked under two explicit fitness functions, correcting source coordinate-versus-fitness assumption.',
'Endpoint-inclusive integer code and six-bit representation are both assessed; real variable and encoded integer are distinguished.',
'Full blocked-cell grid, path decoder, move length, entered collisions, turns and fitness all assessed.',
'Changed vertical-first decoder is executed on the same grid: unchanged length but changed collisions and turns; genuine alternate branch, not cosmetic numeric change.',
'Recurrent retained state is distinguished from explicitly supplied history windows; no universal architecture exclusion.',
'Input-hidden weights, all weights and all weights-plus-biases are all assessed; source only asked first count.',
'Prediction updates both mean and covariance under independent additive Gaussian noise, including source continuation.',
'Full conditional Markov expression is interpreted without throwing away history in the state belief.',
'Augmented state, full covariance and oriented robot-map covariance block sizes all assessed.',
'Full robot covariance propagation, lateral heading coupling and unchanged map covariance are assessed. Predicted augmented mean and zero cross block are explained, not separately selected; moving-robot/static-map mean behavior is already tested by W09-L45-Q030 and static-map behavior by W09-L45-Q008.'
],
10:[
'Supplied mechanical suffix stripping and lexicon/POS lemma procedure are distinguished without claiming named NLTK outputs.',
'Displayed vocabulary order and explicitly alphabetical order are both assessed, preserving original unspecified-order ambiguity.',
'All three query-key dot products, square-root scaling and normalized softmax weights are retained with final-only rounding.',
'All X/Q/K/V shapes plus attention and output shapes are assessed; source WV width typo is not propagated.',
'Both stride-two and stride-one valid convolution lengths are assessed, correcting the no-padding stride-one source overclaim.',
'All three conditional factors form the chain-rule probability; no independence or extra EOS event assumed.',
'All four AIML role-table rows are matched; custom set_it label remains source-specific rather than standard syntax assertion.',
'Serial ASR-to-LLM-to-TTS data dependency and error propagation are assessed without assuming automatic recovery.',
'Fixed pretrained backbone with trained head is distinguished from fine-tuning the backbone.',
'History-conditioned response is isolated by changing only retrieved context; no claim of true internal emotion inference.'
],
11:[
'All simultaneous loads, battery Wh conversion and ideal runtime are assessed with usable-energy/loss qualifications.',
'Both air compressibility and seal friction are retained as precision-control challenges.',
'ADC display endpoint is separated from the top quantization interval, under explicit reference and quantizer model.',
'Encoder cycles and one-count/four-count decoder conventions are both assessed, avoiding ambiguous PPR conversion.',
'Gear reduction and stipulated torque-transfer efficiency are evaluated; stall versus no-load speed distinction retained without physical stall-efficiency promise.',
'Torque surplus below a stable crossing is conditional on specified decreasing motor curve, constant load and positive inertia.',
'Negative gradient update exercises optimizer sign and learning-rate magnitude, distinguishing backpropagation from update policy.',
'Class, raw score and signed geometric distance are all assessed; erroneous source score-as-distance claim is corrected transparently.',
'Training-fit standardization and reuse on new data include nonconstant-feature qualification and no automatic test-unit-variance claim.',
'All position/rate/acceleration/intercept torque terms and absolute error are evaluated; coefficients carry units.'
],
12:[
'Face-region crop is separated from model estimation and from validated inference about inner feelings.',
'Concurrent maximum duration and serial comparison saving are both assessed with simultaneous-start/no-contention assumptions.',
'Course-specific stereo plus active-IR description is retained, not newly verified product information.',
'Perpendicular displacement norm, round trip, 12 repeats, speed fraction, unit conversion and total time are all assessed; physical acceleration limitations explicit.',
'Existing-map localization versus joint map-and-pose estimation is assessed with course-specific AMCL inputs.',
'Modularity, sensor integration and navigation role are retained without hard-real-time guarantee.',
'Planar LiDAR coverage versus valid low-obstacle depth contribution is assessed with common-frame calibration and bounded setup.',
'Wheel-rate sum and difference give zero translation plus nonzero yaw; signs and no-slip model explicit.',
'Near-miss logging/review principle is assessed as course engineering practice, not a named statutory compliance claim.',
'Physical yielding is distinguished from software stop logic; energy take-up is not necessarily dissipation or collision-safety proof.'
]}
assert set(notes)==set(range(1,13)) and all(len(v)==10 for v in notes.values())
ledger=load(D/'coverage-ledger.json');assert sha(R/ledger['sourcePath'])==ledger['sourceSha256']
allq={q['id']:q for p in (R/'data/question-batches').glob('*.json') for q in load(p).get('questions',[])}
reviews=[]
for p in (R/'data/reviews').glob('*.json'):
 x=load(p)
 if isinstance(x,list): reviews += [(str(p.relative_to(R)),r) for r in x]
 elif isinstance(x,dict) and 'questionId' in x: reviews.append((str(p.relative_to(R)),x))
rows=[]
for orig in ledger['items']:
 w=orig['week'];n=int(orig['printedItemNumber']);qid=f'ASSIGN-W{w:02d}-Q{n:03d}';q=allq[qid];op=R/q['originalRecordPath'];o=load(op)
 assert q['assignmentSourceItemId']==orig['id']==o['id'];assert sha(op)==q['originalRecordSha256'];assert o['sourceSha256']==ledger['sourceSha256'];assert o['physicalPages']==orig['physicalPages']
 h=question_hash(q);status='core_source_parts_assessed'; reuse=[];missing=[]
 if (w,n)==(6,8):
  status='partial_figure_branch_coverage';missing=['root equality x1=10 and short-circuit of x2','reached second equality x2=5','rightmost-leaf route and mean 35']
 if (w,n)==(4,7):status='duplicate_reuse_resolution_pending';reuse=['W11-L54-P1719-Q02']
 if (w,n)==(4,9):status='duplicate_reuse_resolution_pending';reuse=['W04-L18-Q031','W04-L20-P0609-Q02']
 if (w,n)==(9,10):status='core_plus_existing_bank_reuse';reuse=['W09-L45-Q030','W09-L45-Q008']
 matching=[{'path':p,'reviewId':r.get('id'),'decision':r.get('decision')} for p,r in reviews if r.get('questionId')==qid and r.get('questionSha256')==h]
 reuseobjects=[{'questionId':k,'questionSha256':question_hash(allq[k]),'matchingVerifiedReviewIds':[r.get('id') for p,r in reviews if r.get('questionId')==k and r.get('questionSha256')==question_hash(allq[k]) and r.get('decision')=='verified']} for k in reuse]
 rows.append(dict(originalSourceItemId=orig['id'],week=w,printedItemNumber=n,physicalPages=orig['physicalPages'],originalRecordPath=str(op.relative_to(R)),originalRecordSha256=sha(op),questionId=qid,questionSha256=h,questionVersion=q['version'],sourcePartAssessment=notes[w][n-1],completenessDisposition=status,missingAssessedAngles=missing,reusedQuestionEvidence=reuseobjects,currentHashMatchingReviewEvidence=matching,completenessIsNotAnswerApproval=True,sourceConflictDisposition='Original source, printed key and qualified adaptation remain separate; this challenge does not overwrite them.'))
assert len(rows)==120 and len({r['originalSourceItemId'] for r in rows})==120
pages=[]
for p in range(1,60):
 ip=R/f'sources/previews/assignments/page-{p:04d}.webp'
 pages.append(dict(physicalPage=p,imagePath=str(ip.relative_to(R)),imageSha256=sha(ip),personallyViewed=True,method='actual local rendered image via view_image',recordedAt=now,viewTiming='Viewed during this recovery session before this record; recordedAt is not an invented per-page view timestamp.',sourceAnswerExposure=p!=55,disposition='end-marker-only justified exclusion' if p==55 else 'substantive source item/continuation'))
summary=dict(totalOriginalItems=120,mappedCurrentItems=120,personallyInspectedPages=59,substantivePages=58,endOnlyPages=1,missingOriginalItems=0,dispositionCounts=dict(collections.Counter(r['completenessDisposition'] for r in rows)),newBoundedGapItems=['ASSIGN-W06-Q08'],knownDuplicateReuseItems=['ASSIGN-W04-Q07','ASSIGN-W04-Q09'],pendingGapAuthor='finish_assignment_authoring',coverageComplete=False,answerApprovalInferred=False)
out=dict(auditVersion='assignment-completeness-challenge-v2',reviewerId='independent-reviewer-robotics-recovery-v3',recordedAt=now,sourcePath=ledger['sourcePath'],sourceSha256=ledger['sourceSha256'],ledgerPath=str((D/'coverage-ledger.json').relative_to(R)),ledgerSha256=sha(D/'coverage-ledger.json'),scope='Bounded full-120-item source figure/formula/subpart completeness challenge, not a new blind key review or exhaustive course-wide semantic deduplication.',method='Personally inspect all59 actual page pixels, including58 substantive pages and55 end-only; compare every current assignment adaptation and rationale, investigate branches/tables/multipart requests, and reuse existing assessed reasoning instead of generating numeric variants.',priorExposure='Printed highlighted source keys and generated answers/solutions were visible during completeness comparison. No blind-answer claim is made; existing sealed independent answer records are untouched.',limitations=['Presence and current-hash review links do not imply all current questions are accepted. Integration must apply separate independent answer and quality reviews.','No browser, package, model, hardware, NLTK, ROS or external notebook execution occurred.','Not every distractor, unused graph edge or different numeric value requires a separate question; preserved original-item provenance is distinct from new assessed knowledge.','The two known W04 duplicate-reuse decisions are unresolved in this frozen snapshot; W06 branch addition is pending separate author/reviewer.'],supersedes={'path':'audits/assignment-coverage/full120-independent-completeness-challenge.json','sha256':sha(D/'full120-independent-completeness-challenge.json'),'reason':'Two reviewer note copy errors corrected before handoff: W04 Q005 is accuracy/repeatability, and Q008 is elastic-link compliance. Item mappings, source evidence, gap counts and conclusions unchanged.'},summary=summary,pages=pages,items=rows)
p=D/'full120-independent-completeness-challenge-v2.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');s=D/'full120-independent-completeness-summary.json';s.write_text(json.dumps({**summary,'artifactPath':str(p.relative_to(R)),'artifactSha256':sha(p),'recordedAt':now},indent=2)+'\n');print(json.dumps(summary,indent=2));print(sha(p))
