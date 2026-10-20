import json,pathlib
p=pathlib.Path('audits/assignment-coverage/manual-observations.json')
d={'completedWeeks':[1,2,3,4,5,6],'viewedPages':list(range(1,29)),'restrictions':['No Git, canonical bank, accepted-question or source writes.','Never use /tmp/robotics-l35-venv or L48 incident temporary environment.','No new dependency/model/checkpoint/audio/NLTK retrieval or denied original L49 notebook route.','Browser execution denied by socket permission; no retry/install/alternate route. Layout unverified.','ROS 2 Humble QoS docs route denied; no retries/mirrors/browser bypass.','Default installed Python/Node and local source inspection permitted.'],'items':{}}
rows='''1|1|Asimov priority|A|Human-harm prohibition outranks self-preservation; course fiction, not a real safety standard.|L01:26
1|2|Offline calibration|D|Offline development does not remove model-to-robot calibration.|L01:44,L01:45,L01:46,L01:47
1|3|ML DL RL comparison|B|Preserve course distinction without making overlapping categories disjoint.|L02:10,L02:16,L02:18
1|4|Markov state sufficiency|B|Memoryless action selection does not establish Markov environment dynamics; supply a sufficient-state conditional-independence premise.|L02:28
1|5|State-space input|B|u(t) is control input in xdot=Ax+Bu.|L03:18
1|6|Gradient evaluation|B|Partials (6x+2y,2x+2y) at (1,2) give (10,6).|L03:9
1|7|Probabilistic uncertainty|C|Represent sensor noise rather than eliminate uncertainty.|L04:12
1|8|Fidelity and resolution|C|A point abstraction is coarse; fidelity is relative to intended observables, not automatically low for every task.|L04:18
1|9|ROS modularity|B|Independent navigation/speech modules and integration illustrate modularity.|L05:9
1|10|TF versus URDF|A|TF stores frame relationships; URDF describes structure.|L05:33
2|1|Proper rotation constraints|D|Orthogonal and det+1; det0 contradicts invertibility.|L06:10
2|2|Homogeneous transform|C|3D column-vector bottom row (0,0,0,1).|L06:18
2|3|Serial-joint DOFs|D|4R+2P gives6 independent joint coordinates, not necessarily task rank6.|L07:7
2|4|2R forward kinematics|D|Relative joint angles0,90deg give (2,2)m.|L07:17
2|5|Special-geometry IK count|D|<=8 is a lecture-specific geometry claim; two zero a values alone must not be generalized to every 6DOF architecture.|L08:9
2|6|IK cosine versus angle|D|Prompt says 3-link and asks theta2; work only computes 2R cos(theta2)=.25. Actual 2R angle is +/-acos(.25); third-link geometry is unspecified.|L08:15
2|7|Jacobian rank|B|Nonzero dependent rows give rank1 and det0.|L09:24
2|8|Singularity taxonomy|B|Interior versus workspace-boundary singularities.|L09:24
2|9|Frame-dependent torque|1.5|Missing symbols and force frame. .3*5=1.5Nm only under the matching local lever-arm convention; base-frame torque depends on orientation.|L10:12
2|10|Static force balance|B|Highlight B conflicts with printed Answer D. Neglecting gravity/inertial link forces is intended; free fall is not static balance.|L10:14
3|1|Parallel-axis inertia|B|Translated parallel axes: I_Azz=I_Czz+m(xc²+yc²).|L11:17
3|2|Cylinder axial inertia|A|Figure rotation is longitudinal through center: .5mR², not transverse.|L11:20
3|3|Angular momentum|B|I_C omega is COM angular momentum in a consistent frame.|L12:9
3|4|Resultant-force norm|C|4(3,0,4)=(12,0,16)N and norm20N; net force, not an additional gravity load.|L12:7
3|5|Gravity recursion boundary|C|Y0 points up; physical gravity -gY0 represented by fictitious base acceleration +gY0.|L13:5
3|6|Unloaded tool boundary|B|f3=n3=0 denotes no external wrench, not static equilibrium.|L13:5
3|7|V versus G dynamics|B|V depends on rates/configuration; G on configuration for fixed gravity.|L14:19
3|8|Rigid-link kinetic energy|B|Translation of COM plus rotation about COM; consistent velocity/inertia frames.|L14:8
3|9|2R mass matrix from geometry|A|Point masses at elbow/tip. Derive all four entries from kinetic energy; option C is nonsymmetric.|L15:6
3|10|Mixed-rate pair dimension|B|n forces and n(n-1)/2 unordered pairs: B is n by n(n-1)/2.|L15:8
4|1|Quintic endpoint constraints|D|Six independent position/velocity/acceleration endpoint constraints justify quintic; a lone polynomial is internally smooth regardless of degree.|L16:21
4|2|Cubic rest-to-rest|B|Four endpoint position/velocity constraints; acceleration matching not general.|L16:11
4|3|Parabolic-blend continuity|B|Ordinary LSPB has continuous velocity but acceleration jumps from nonzero blend acceleration to zero cruise; printed acceleration-continuity claim false.|L17:6
4|4|Angle-axis branch choice|B|Minimum travel intended; difference of arbitrary rotation vectors is not universally the SO(3) geodesic metric. Constrain axis/branch.|L17:8
4|5|Repeatability versus accuracy|C|Spread around taught pose versus error from specified target.|L18:11
4|6|2R reachable annulus|C|Unrestricted joints: abs(5-4)=1 through5+4=9; joint limits and obstacles qualify reach.|L18:29
4|7|Redundant collision avoidance|B|Regular reachable 6D tasks with7 joints permit self-motion, subject to limits and singularities.|L19:3
4|8|Compliance positioning error|C|Encoder-based rigid FK misses link deflection despite accurate joint sensing.|L19:12
4|9|SCARA compliance|C|Source design: rigid vertical, compliant horizontal.|L20:4
4|10|SCARA singular angles|C|sin(theta2)=0 gives0 or180deg modulo360. Explanation only writes theta2=0 while calling both folded/extended: omitted branch, correct highlighted option.|L20:14
5|1|Critical damping|C|m1,b6,k9: discriminant0, repeated pole-3.|L21:11
5|2|PD gain calculation|D|kp=16-1=15; bclosed=2sqrt(4*16)=16; kv=16-1=15.|L21:19
5|3|Back EMF law|B|Use e_back=ke*omega, distinguish from terminal voltage including R/L drops; source reuses v.|L22:6
5|4|Resonance separation heuristic|B|Source rule omega_res>=2omega_n, not a universal stability guarantee.|L22:11
5|5|Nonlinear cancellation|B|Matching-model input cancels nonlinear effects; feedback still needed.|L23:8
5|6|Spring-force ratio|4|Linear20N, cubic80N at2m: ratio4. k1,k2 have different units.|L23:5
5|7|Independent-joint PID decomposition|C|Source alpha=I,beta=0; preserve the decomposition meanings.|L24:15
5|8|Error damping ratio|1|omega_n=sqrt9=3; zeta=6/(2*3)=1.|L24:10
5|9|Joint-space error quantities|B|Source contrasts joint position/rate/acceleration with Cartesian errors.|L25:4
5|10|Jacobian transpose force mapping|C|tau=J^T F follows power duality with compatible frames.|L25:11
6|1|kNN similarity|B|Local similarity is metric/scaling dependent.|L26:15
6|2|Classification/regression|B|Class label versus continuous numerical target.|L26:14
6|3|Supervised/unsupervised|C|Labeled versus unlabeled data.|L27:11
6|4|Regression plane versus hyperplane|B|Plane in R3 is also hyperplane: B/C overlap unless most-specific dimension is requested.|L27:6
6|5|Estimator fit|C|fit(X,y) trains from labeled pairs; source/API claim, not fresh estimator execution.|L28:28
6|6|ndarray versus DataFrame dtype|B|One ndarray dtype does not require all Python objects to have one type; qualify object and structured dtypes.|L28:24
6|7|Regression leaf mean|18.0|90/5=18 under squared-error mean prediction; not universal across all criteria.|L29:8
6|8|Decision-tree diagram trace|14|x1=12 goes right at<=10; x2=3 left at<=5; (10+14+18)/3=14. Diagram and continuation both required.|L29:8
6|9|RL policy|B|State-to-action mapping/distribution, distinct from rewards/values.|L30:11
6|10|Q-learning update|4.8|4+.1*(3+.9*10-4)=4.8, assuming supplied nonterminal next-state Q.|L30:18'''
conflicts={(1,4),(2,6),(2,9),(2,10),(4,3),(6,4)}
qualified={(1,8),(2,5),(4,1),(4,4),(4,10),(5,3),(6,6)}
nums={(1,6),(2,3),(2,4),(2,6),(2,7),(2,9),(3,4),(3,9),(3,10),(4,6),(4,10),(5,1),(5,2),(5,6),(5,8),(6,7),(6,8),(6,10)}
figs={(3,2),(3,5),(3,6),(3,9),(6,8)}
for line in rows.splitlines():
 w,q,f,k,n,refs=line.split('|');w,q=int(w),int(q)
 d['items'][f'ASSIGN-W{w:02}-Q{q:02}']={'conceptFamily':f,'observedHighlightedKey':k,'independentSourceKeyAuditStatus':'conflicting_or_underspecified_quarantine' if (w,q) in conflicts else 'conditionally_consistent_needs_qualification' if (w,q) in qualified else 'consistent_under_stated_or_explicit_standard_model','independentReasoning':n,'authoringRequirement':'Explicit assignment citations and independent question review required. Preserve source claim separately; resolve ambiguity before acceptance. Avoid duplicate-only recall coverage.','requiredAngles':['concept','numerical_or_symbolic_working' if (w,q) in nums else 'assumption_or_misconception']+(['actual_diagram_trace'] if (w,q) in figs else []),'lectureReferences':[[x.split(':')[0],int(x.split(':')[1])] for x in refs.split(',')],'originalGeneratedCoverageApproved':False}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
