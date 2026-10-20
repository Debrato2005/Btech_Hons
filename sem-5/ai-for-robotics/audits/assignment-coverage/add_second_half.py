import json,pathlib
p=pathlib.Path('audits/assignment-coverage/manual-observations.json');d=json.loads(p.read_text())
rows='''7|1|Pinhole depth-dependent separation|5|Assuming world coordinates equal camera coordinates, fX/Z gives10mm and5mm, separation5mm. Unspecified camera extrinsics must be stated, not silently assumed.|L31:22
7|2|Perspective depth scaling|B|Equal-size objects farther from camera appear smaller; parallel lines parallel to the image plane need not have a finite vanishing point.|L31:28,L31:29,L31:30
7|3|uint8 modular addition|24|Array uint8 addition (230+50) modulo256 is24. Bind actual dtype and operation; no floating promotion or saturating-image API substitution.|L32:11
7|4|Correlation versus flipped-kernel convolution|A|I=[[1,2,3],[4,5,6],[7,8,9]], K=[[1,2,0],[0,-1,1],[2,0,-2]]. Direct sum2; 180deg-flipped kernel sum28.|L32:20,L32:21,L32:22
7|5|Circularity and shape inference|B|4*pi*100/40²=pi/4. Ideal square matches, but circularity alone does not identify an arbitrary object uniquely; retain closest-given-choice scope.|L33:19
7|6|Structure-tensor corner eigenvalues|C|P(.01,.02) flat, Q(.01,5) edge, R(4.5,5.2) both large/corner on common scale.|L33:28
7|7|Neural-network training sequence|B|Forward, loss, backward gradients, gradient update. No new training-runtime claim.|L34:21
7|8|Neuron bias convention and step output|0|Source says bias b=1 but works with w0=-b, giving net-3. Additive-bias convention gives-1. Both output0 but convention must be explicit and internal arithmetic not silently changed.|L34:10
7|9|Convolution kernel-size inversion|C|24=28-K+1 givesK5;16 filters give24x24x16 output, with unit dilation.|L35:9
7|10|YOLOv8 anchor-free architecture|B|Source comparison is anchor-free versus earlier anchor-based heads; do not turn this into a fresh model/runtime claim.|L35:24
8|1|Weighted-graph UCS trace|A|Undirected graph AB5,AC2,BD6,BE3,CF4,DE2,DG6,EF1,FG3: shortest A-C-F-E costs7, versus A-B-E8 and A-B-D-E13. G is not the goal.|
8|2|A-star heuristic role|C|h estimates remaining cost; optimality needs additional cost/heuristic/search conditions.|L36:32
8|3|A-star frontier priority|B|fA=6,fB=5.4,fC=5.8; select B assuming candidates are current valid frontier entries.|
8|4|Bug0 incompleteness|C|Memoryless leave-when-visible rule may cycle at nonconvex obstacles; need an actual loop trace to test more than recall.|L37:15,L37:16
8|5|DQN target-network purpose|B|Slow/frozen target reduces moving-target instability; does not guarantee convergence or remove exploration.|L38:17,L38:18
8|6|DQN Bellman target|5.5|Nonterminal target1+.9*max(3,5)=5.5. Source also prints stray Answer C although this is a numeric-answer item.|L38:18
8|7|GNSS waypoint feedback|B|Compare live position and target waypoint to close tracking loop, distinct from coordinate conversion/path preparation.|L39:30
8|8|GNSS clock-bias term|B|Receiver/satellite timing discrepancy yields range bias c*delta_t. Treat residual receiver clock bias consistently after satellite corrections.|L39:9
8|9|Singleton fuzzy weighted average|32|(.7*20+.3*60)/(.7+.3)=32%. Printed denominator lacks plus; numeric answer32 and stray Answer C coexist. Reference says Lecture39 Fuzzy though Fuzzy is mapped L40.|L39:21
8|10|Crisp versus fuzzy output|C|Source describes a single definite value; crisp sets generally need not be singletons. Keep scope to crisp output value.|L40:7
9|1|Real-coded crossover and fitness selection|D|Children4,0,8 follow formulas. Selecting4,8 requires a fitness such as maximize x; maximization alone does not rank candidate coordinates.|L41:24
9|2|Binary encoding linear map|B|Integer code D=(11-1)*(2^6-1)/(16-1)=42. Distinguish encoded integer from decoded real value11.|L41:11
9|3|Waypoint grid decoding and fitness|D|Image waypoints (x,y)=(0,1),(2,4); horizontal-first path length10 hits5 blocked cells and turns4 times: C64, F1/65.|L42:16,L42:17,L42:18,L42:19,L42:20,L42:21
9|4|Decoder order collision effect|C|Changing horizontal/vertical order changes intermediate cells and collisions while Manhattan length remains fixed.|L42:13,L42:14,L42:15,L42:16,L42:17,L42:18,L42:19,L42:20,L42:21
9|5|Temporal sensor architecture choice|C|RNN/LSTM is the source sequence-model choice; do not claim a CNN/MLP with a fixed history can never use past data.|L43:13
9|6|Dense input-hidden weight count|B|6*16=96, excluding biases and hidden-output weights.|L43:16
9|7|Gaussian linear prediction|B|F=G=I: mean(4,3), covariance diag(.75,.56), assuming independent zero-mean additive noise.|L44:20,L44:21
9|8|State-transition Markov conditional independence|B|Full history conditional reduces to previous state and current action, not the previous observation alone.|L44:15
9|9|EKF-SLAM augmented dimension|A|3 robot coordinates+2*6 landmarks=15; state15x1, covariance15x15.|L45:12
9|10|EKF-SLAM mean and coupled covariance propagation|B|At theta0 and distance2, F_robot=[[1,0,0],[0,1,2],[0,0,1]]. Robot covariance [[.05,0,0],[0,.09,.02],[0,.02,.0125]], landmark unchanged, cross block zero.|L45:12,L45:13,L45:14,L45:15,L45:16
10|1|Stemming versus lemmatization|B|The supplied illustrative outputs runn/run fit mechanical suffix stripping versus lexical base form; not a claim that a named stemmer outputs runn.|L46:9
10|2|One-hot vocabulary ordering|A|Prompt vocabulary is unordered. Highlight A follows alphabetical order introduced only in explanation, whereas displayed order would put near fifth with no matching option.|L46:14
10|3|Scaled dot-product attention|A|Dot products7,4,1 divided bysqrt2, then stable softmax approximately(.8817,.1057,.0127); rounded option A closest, not exactly normalized after coarse rounding.|L47:10,L47:11
10|4|Attention projection dimensions|A|X12x64,Q/K12x16,V12x20. Continuation incorrectly writes value factor64x16 while retaining12x20; use original WV64x20 premise.|L47:9,L47:10,L47:11,L47:12,L47:13,L47:14,L47:15,L47:16,L47:17,L47:18,L47:19
10|5|1D valid convolution stride|A|floor((100-2)/2)+1=50. Explanation falsely says stride1 gives input length; without padding stride1 gives99.|L48:18
10|6|Autoregressive chain probability|C|.5*.4*.2=.04 for the supplied sequence conditional on X; no independence assumption among tokens.|L48:23
10|7|AIML source-specific tag matching|A|P-category3,Q-pattern4,R-template1,S-set_it2. Preserve set_it as source-specific/custom syntax, not a universal standard AIML tag or fresh runtime assertion.|L49:14
10|8|ASR error propagation|B|Wrong transcription can cascade to LLM output; not guaranteed correction by TTS.|L49:17
10|9|Frozen feature extraction|C|Frozen pretrained backbone plus trained classifier, distinct from unfreezing backbone fine-tuning.|L50:15
10|10|Memory-dependent dialogue context|A|Same new sentence may yield different context-aware replies due to stored user history; estimated emotion is not ground truth.|L50:23
11|1|Battery energy-budget runtime|D|12V*2.5Ah=30Wh;20W total gives1.5h=90min ideal constant-load/full-usable-energy estimate, not measured runtime.|
11|2|Pneumatic control limits|B|Air compressibility and seal friction impair precise control; source claim, no hardware test.|L51:7
11|3|ADC maximum code and missing reference|D|Arduino alone does not specify resolution/reference;5V requires explicit10bit5V model. Code1023 identifies upper bin, not an exact unique voltage.|
11|4|Encoder count rotations|3|1800/600=3 only when interrupt counts use the same PPR convention; x2/x4 quadrature changes counts/revolution.|
11|5|Geared stall torque model|4.25|.25*20*.85=4.25Nm in the stipulated effective torque-transfer model. At zero speed power efficiency is not defined; do not treat this as a measured stall rating.|
11|6|Torque-speed equilibrium stability|B|Below the illustrated stable intersection motor torque exceeds load torque; arbitrary load curves can differ.|L53:27
11|7|Gradient-descent weight update|D|w_new=w_old-eta*dLoss/dw; distinguish backprop gradient computation from optimization update.|L54:19
11|8|SVM score versus signed geometric distance|A|f(3.2)=.5 gives Normal; geometric signed distance .5/abs(2.5)=.2 mm/s. None of the four literal pairs is correct.|
11|9|Training feature standardization|B|Default centering/scaling on training data yields zero mean/unit variance only for nonconstant features; constant columns stay zero variance, test data not guaranteed unit variance.|L55:16
11|10|Inverse-dynamics prediction and absolute error|B|2*.5+.5*2+1.5*3+.8=7.3Nm; abs(8-7.3)=.7Nm. Supplied toy predictor, not trained-model evidence.|
12|1|Face crop region of interest|B|Crop isolates region used by expression estimator; expression estimate does not establish internal emotional state.|L56:10
12|2|Concurrent availability latency|C|Both start together, no contention/fusion delay: max80,120=120ms. Given synthetic timing, not measured hardware.|
12|3|D415 sensing combination|B|Assignment attributes stereo plus active IR to the named sensor; keep version/model source claim separate from fresh specification verification.|L57:15
12|4|Repeated straight-line travel and ideal time|A|24*sqrt(.3²+.2²)=8.653323m; speed .6*8.2=4.92m/s; time1.758805s. Supplied ideal speed, not validated KR5 operating envelope.|
12|5|AMCL versus SLAM|B|Existing-map pose localization versus joint map/pose estimation; source course comparison.|L58:12,L58:22
12|6|ROS2 navigation motivation|A|Source lists modularity/sensor integration/real-time navigation; no unconditional hard-real-time guarantee.|L58:4
12|7|LiDAR RGB-D complementary geometry|B|In the described setup 360deg planar laser plus RGB-D can reveal low/off-plane obstacles; not every LiDAR is planar or360deg.|L59:8
12|8|Differential-drive opposing wheel rates|B|v=.1*(5-5)/2=0; yaw=.1*(5-(-5))/.5=2rad/s under positive-forward wheel conventions.|L59:7
12|9|Near-miss review|A|Course safety principle is log/review near misses. Do not claim a specific legal/standards obligation without primary standard evidence.|L60:20,L60:21
12|10|Mechanical compliance and impact energy|B|Compliance can store/absorb mechanical energy independently of software limits; it need not dissipate energy or ensure a safe collision by itself.|L60:16'''
conflicts={(7,1),(7,8),(9,1),(10,2),(11,3),(11,8)}
qualified={(7,2),(7,5),(8,6),(8,9),(8,10),(9,2),(9,5),(10,1),(10,4),(10,5),(10,7),(11,4),(11,5),(11,6),(11,9),(12,3),(12,6),(12,7),(12,9),(12,10)}
nums={(7,1),(7,3),(7,4),(7,5),(7,6),(7,8),(7,9),(8,1),(8,3),(8,6),(8,9),(9,1),(9,2),(9,3),(9,4),(9,6),(9,7),(9,9),(9,10),(10,2),(10,3),(10,4),(10,5),(10,6),(11,1),(11,3),(11,4),(11,5),(11,8),(11,10),(12,2),(12,4),(12,8)}
figs={(7,4),(7,6),(8,1),(9,3),(9,4),(9,7),(9,10),(10,7)}
for line in rows.splitlines():
 w,q,f,k,n,refs=line.split('|');w,q=int(w),int(q)
 d['items'][f'ASSIGN-W{w:02}-Q{q:02}']={'conceptFamily':f,'observedHighlightedKey':k,'independentSourceKeyAuditStatus':'conflicting_or_underspecified_quarantine' if (w,q) in conflicts else 'conditionally_consistent_needs_qualification' if (w,q) in qualified else 'consistent_under_stated_or_explicit_standard_model','independentReasoning':n,'authoringRequirement':'Explicit assignment citations and independent question review required. Preserve source claim separately; resolve ambiguity before acceptance. Avoid duplicate-only recall coverage.','requiredAngles':['concept','numerical_or_symbolic_working' if (w,q) in nums else 'assumption_or_misconception']+(['actual_diagram_or_table_trace'] if (w,q) in figs else []),'lectureReferences':[[x.split(':')[0],int(x.split(':')[1])] for x in refs.split(',') if x],'originalGeneratedCoverageApproved':False}
d['completedWeeks']=list(range(1,13));d['viewedPages']=list(range(1,60))
d['items']['ASSIGN-W07-Q04']['visuallyTranscribedMatrices']={'I':[[1,2,3],[4,5,6],[7,8,9]],'K':[[1,2,0],[0,-1,1],[2,0,-2]],'KFlipped':[[-2,0,2],[1,-1,0],[0,2,1]]}
d['items']['ASSIGN-W08-Q01']['visuallyTranscribedEdges']=[['A','B',5],['A','C',2],['B','D',6],['B','E',3],['C','F',4],['D','E',2],['D','G',6],['E','F',1],['F','G',3]]
d['items']['ASSIGN-W09-Q03']['visuallyTranscribedGrid']={'coordinateConvention':'x=column from left, y=row from top; equivalent row-column transpose yields same stated path counts if consistent.','start':[0,0],'waypoints':[[0,1],[2,4]],'goal':[5,5],'obstacles':[[1,1],[2,1],[2,2],[4,2],[2,3],[3,4]],'decodeRule':'horizontal then vertical per waypoint segment','fitness':'1/(1+L+10*Nobs+Nturn)'}
d['items']['ASSIGN-W09-Q07']['visuallyTranscribedGaussianOptions']={'A':{'mean':[4,3],'covariance':[[.5,0],[0,.4]]},'B':{'mean':[4,3],'covariance':[[.75,0],[0,.56]]},'C':{'mean':[2,2],'covariance':[[.75,0],[0,.56]]},'D':{'mean':[4,3],'covariance':[[.25,0],[0,.16]]}}
d['items']['ASSIGN-W09-Q10']['visuallyTranscribedEKFOptions']={'A':{'mean':[4,1,0,5,4],'robotCovariance':[[.05,0,0],[0,.05,.01],[0,.01,.0125]],'mapCovariance':[[.09,0],[0,.09]]},'B':{'mean':[4,1,0,5,4],'robotCovariance':[[.05,0,0],[0,.09,.02],[0,.02,.0125]],'mapCovariance':[[.09,0],[0,.09]]},'C':{'mean':[2,3,0,5,4],'robotCovariance':[[.05,0,0],[0,.05,.01],[0,.01,.0125]],'mapCovariance':[[.09,0],[0,.09]]},'D':{'mean':[4,1,0,7,4],'robotCovariance':[[.05,0,0],[0,.06,.01],[0,.01,.0125]],'mapCovariance':[[.1,0],[0,.1]]}}
d['items']['ASSIGN-W10-Q07']['visuallyTranscribedMatchingTable']={'P':'<category>','Q':'<pattern>','R':'<template>','S':'<set_it>','1':'Is the piano your favorite instrument?','2':'Hiddenly stores your piano as conversational context','3':'Complete conversational rule with trigger and response','4':'I ENJOY PLAYING *'}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
