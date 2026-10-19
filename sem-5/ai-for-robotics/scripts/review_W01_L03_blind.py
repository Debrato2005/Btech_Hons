"""Independent blind solution record; reads only the frozen answer-hidden packet."""
import json,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
packet=ROOT/'audits/blind-W01-L03.json'
assert hashlib.sha256(packet.read_bytes()).hexdigest()=='17ce41a5302d8147e4f8f7dde89d999d5d9e3620bebf9db43fc89e45b2658c91'
qs=json.loads(packet.read_text())
reasoning='''The red position arrow begins at the fixed xy origin and ends at the tip P. The two components are position, not joint coordinates or a normalized direction.
Componentwise arithmetic gives 2(1,-2)+(3,4)=(2,-4)+(3,4)=(5,0).
The dot product is 2*3*cos(60 degrees)=6*(1/2)=3.
Nonzero magnitudes permit division by their product; zero dot product requires cos(theta)=0, hence 90 degrees among the options.
p^T p=3^2+4^2=25 square metres; taking the square root yields norm 5 metres.
Transpose exchanges row/column indices and dimensions: (A^T)_32=A_23=7 and the shape is 3 by 2.
Right multiplication requires an identity with three rows and three columns, preserving A's three columns.
Only [[2,3],[3,5]] is square with equal mirrored off-diagonal entries. The skew example has opposite entries; the rectangular example cannot be symmetric.
The final bullet explicitly links matrices to rigid-link mass distribution, inertia tensors, and dynamic forces. The alternative topics are not the displayed association.
S=-S^T requires a square matrix, S_ii=-S_ii so real diagonal entries vanish, and opposite off-diagonal entries. Equality rather than opposition is not necessary.
The shown cross-product matrix is [[0,-2,0],[2,0,0],[0,0,0]]. Multiplication by (3,0,0) gives (0,6,0), agreeing with positive z cross positive x giving positive y.
Inner dimensions 3 match in AB, giving 2 by 4. BA would require 4=2 and is undefined.
Associativity changes parentheses without changing operand order. Swapping transformation factors is not generally valid.
The formula has denominator det(A), so det(A)=0 prevents division and an ordinary inverse. Transpose and multiplication by identity remain defined.
The second nonzero row is twice the first, leaving one independent row: rank1. The determinant is 1*4-2*2=0, hence no inverse.
Rank loss is the meaningful singularity condition. It is not a statement that every matrix becomes symmetric or that changing labels causes a singularity.
A(1,0)=(2,0)=2(1,0), so lambda=2 for that eigenvector.
A0=0=lambda0 for any lambda. Excluding zero prevents the equation from being vacuous and retains a genuine direction.
For nonzero x, (lambda I-A)x=0 must have nontrivial nullspace, equivalent to determinant zero for square A.
For the stated continuous-time LTI system, all eigenvalues must have strictly negative real parts. -2 and -1 plus/minus3i satisfy this; zero and imaginary-axis roots do not give asymptotic stability.
Partial derivatives are 6x+2y and 2x+2y; at (1,2), they are 10 and6. The gradient is a vector, not the function value11.
The text says attracted to goal and repelled by obstacles; the potential contours distinguish the green goal and red obstacle.
Differentiate each entry: [[2t,cos(t)],[0,2]], giving [[0,1],[0,2]] at zero with radian arguments.
R=I leaves S unchanged. With z angular velocity2, the xy block is [[0,-2],[2,0]]. The opposite signs would reverse the angular direction.
A PMF requires nonnegative entries summing to1. Only .1+.2+.3+.4=1 satisfies both conditions.
A count has countably many possible integer values. The explicitly ideal, undigitized distance is real-valued and continuous; physical motion alone does not make every variable continuous.
The image has four available states labeled .25 each, and the prompt declares their exhaustive distribution. Two distinct mutually exclusive selections sum to .50, not their product.
Bayes gives .8*.2/.4=.4. The product .16 is the joint probability before normalizing by evidence.
P(B)>0 is needed for the displayed ratio. Independence or equal marginal probabilities is not required.
The posterior conditions the unknown state on observed sensor data: P(x|z). P(z|x) is the likelihood and P(x) is the prior.
For fixed o with positive evidence, P(o) is constant across candidate i. Maximizing posterior therefore maximizes likelihood times prior, P(o|i)P(i).
A random variable is the mapping from outcomes to real numbers. The sample space and a single realized value are not themselves that function.
The probability-weighted sum is 10*.3+(-2)*.7=3-1.4=1.6.
The continuous expectation integrates x times density over its domain. The integral of density alone is normalization, not generally the mean.
The density integrates to1. E(X)=integral_0^1 2x^2 dx=2/3.
The elementary binomial count requires independent Bernoulli trials with common success probability and fixed n. The proposed NLP trials match that model; arbitrary dependence or varying p does not.
Exactly two successes have three possible positions for the failure: C(3,2)*.8^2*.2=3*.64*.2=.384.
At x=mu the exponent is zero, so the Gaussian density equals its normalizing coefficient 1/(sigma sqrt(2pi)).
The peak coefficient is inversely proportional to positive sigma. Doubling sigma halves the density peak and does not move mu.
The source explicitly uses v~N(0,V) for process noise and w~N(0,W) for measurement noise. These symbols are source conventions, not mandatory universal letters.
MLE compares .6 versus .5 and chooses1. MAP compares .6*.2=.12 versus .5*.8=.40 and chooses2.
Multiplication by the same positive prior and division by common evidence preserve likelihood ordering; the unique maximizer is unchanged.
Evidence is the common denominator P(s), the marginal probability of the observed data, not a conditional posterior or prior.
The displayed sequential update makes the posterior from z1 the next prior. This is the slide's static-belief description, not a full moving-state prediction model.
The lecture contrasts sensor-only MLE with MAP using measurements plus map-derived prior information. Additional data is not an unconditional zero-error guarantee.
H=-2*(.5*log2(.5))=1 bit.
The certain distribution has entropy -1*log2(1)-0log2(0)=0 by the declared limit. The balanced binary distribution has1 bit.
The final bullet identifies entropy as class impurity for selecting informative features. It is not torque or an unconditional certificate of model correctness.
B multiplies u in the state equation and maps inputs to the state derivative. C maps state to the displayed output.
Ax=(2,-2-6)=(2,-8); Bu=(0,4); their sum is (2,-4).
[1,0](position,velocity)^T selects position alone.
x1_dot=q_dot=x2 and x2_dot=q_ddot=u-3x2-2x1. The signs follow by moving damping and stiffness terms to the right.
The lecture's nodes are docking stations, and edges model traversable passages. A directed edge does not assert reverse access.
A nonempty path returning to its starting node is the specified cycle. A-B-C-A returns toA; the other choices do not traverse a returning path.
Under the explicitly scoped rooted directed convention, cycles are prohibited. A root, connections, and more than one node are compatible.
The total path cost is the sum4+1+3+1=9.
The green edges are Dock1-Dock3 cost2, Dock3-Dock5 cost3, and Dock5-Dock6 cost1. Their sum is6.
The legend explicitly identifies the red dashed Dock1-Dock4 segment as a blocked passage. Apparent Euclidean shortness does not make it usable.
The lecture states FIFO, exploration by edge-depth, and minimum edge count rather than arbitrary weighted cost.
Ignoring edge weights, BFS prefers the two-edge route despite cost100. Its guarantee does not compare the sums100 and3.
S-A-C-F-G has five vertices but four traversed edges.
FIFO with sorted neighbors and visited-on-enqueue gives S,A,B,C,D,E,F,H,G. D is enqueued byA and not duplicated when exploringB; F is enqueued byC and not duplicated atD.
DFS backtracks when the present branch has no unvisited continuation; another branch may still contain a goal.
The highlighted first-found DFS route has no minimum-edge guarantee. LIFO determines exploration order, not equal edge weights.
Recursive sorted DFS enters S,A,C,F; atF the unvisited alphabetical choiceD precedesG, then D-B-E-H-G. The path therefore has S,A,C,F,D,B,E,H,G.
The highlighted DFS route has nine vertices and eight edges; the highlighted BFS route has five vertices and four edges. This is a comparison of these figures, not a universal factor2.
The page associates internal nodes with tests, branches with test outcomes, and leaves with final decisions/classifications. It is discussing a classification decision tree, despite the broad search-tree title.
A random forest combines multiple decision trees. A single deeper branch is not an ensemble, and a FIFO search queue is unrelated.
The weighted child entropy is .25*0+.75*.8=.6 bit. Information gain is1-.6=.4 bit.
The stated criterion chooses the largest reduction in uncertainty, so .35 bit beats .15 bit at the same parent.
The figure sends Glass=yes directly to Fragile/Low Force. Glass=no and Thickness=thin also reaches Low Force; non-glass thick reaches High Force; no measurements specify no route.
The explicit tests and outcomes provide a traceable reason for the decision. Interpretability does not guarantee real-world safety for every object.
The leading term is100n forA and n^2 forB; positive constants do not change their respective linear and quadratic growth classes.
At10, A=2000 and B=101, soB is smaller there. As n grows without bound, the quadratic n^2 term eventually exceeds linear growth.
A<B requires n^2-100n-999>0. At109, A=11900 and B=11882, so not yet; at110, A=12000 and B=12101. The positive root lies between109 and110, making110 the first positive integer.
For fixed conventional log base>1 and sufficiently large n, logarithmic growth is slower than linear, which is slower than quadratic.
Worst-case counts the most demanding input at a size; average-case averages over a specified input distribution. They need not coincide and are not exact hardware runtimes.
The safe supported distinction is heuristic-guided A* versus ordinary BFS without a goal-location heuristic. Neither an always-better Big-O class nor a ban on temporarily moving away follows.
Guaranteeing a valid solution when one exists is completeness. It says nothing by itself about minimum cost, constant time, or zero storage.
Resolution completeness is the slide's guarantee contingent on sufficiently fine discretization, not every coarse grid capturing every continuous solution.
Probabilistic completeness is convergence of success probability toward1 with unbounded computation, not certainty in each finite run and not path optimality.
The slide denies an absolute-shortest-path guarantee in a finite number of steps for its GA discussion. The scoped question does not assert every GA is probabilistically complete.
The summary connects probability/statistics to uncertainty in perception and decision-making. The other mappings swap unrelated roles.
The unit-square side lengths become2 and3, so the area becomes6 and the area scale is6, not the sum5.
The inverse of a nonzero diagonal matrix reciprocates corresponding entries: diag(1/2,1/4). Multiplying gives identity.
Zero diagonal is necessary but insufficient. For instance [[0,1],[2,0]] has zero diagonal but lacks opposite off-diagonal entries.
The summary explicitly names SVD in linear algebra and chain rule in calculus. It supplies category membership only, not enough here to derive SVD algorithms.'''.splitlines()
assert len(reasoning)==len(qs),(len(reasoning),len(qs))
notes={
98:'Printed4. Red arrow p starts at xy origin and ends P; visible x_tip/y_tip column, 3-link serial arm; norm contains both square roots.',
99:'Printed5. Side-by-side 3x3 A and transpose exchange indices; identity diagonal1 and symmetric A=A^T; inertia application.',
100:'Printed6. S upper xy entry -Omega_z and lower +Omega_z; zero diagonal; Omega cross P=SP; multiplication dimension/associativity statements.',
101:'Printed7. Adjugate divided by determinant; rank defined through independent rows/columns; Jacobian rank-loss condition; determinant notation limited to square case.',
102:'Printed8. Ax=lambda x explicitly x nonzero, characteristic determinant, negative real parts for stated stability claim.',
103:'Printed9. Gradient vector transposed; green goal at about(6,6), red obstacle around(-2,-2), high nested obstacle contours and inset. No question infers metric navigation path.',
104:'Printed10. Elementwise derivative notation; displayed R_dot=S(omega)R order, not RS.',
105:'Printed11. Four green available cells labeled0.25 around blue robot; red blocked cells, black walls and explicit legend. Axiom line mixes CDF inequality and PMF sum, not copied uncritically.',
106:'Printed12. Bayes numerator likelihood*prior, denominator evidence; localization P(x|z); speech posterior P(i|o).',
107:'Printed13. X:Omega to real; discrete weighted sum and continuous integral x*f_X; PMF/PDF distinction.',
108:'Printed14. Binomial coefficient and common p, independent Bernoulli trials; Gaussian normalizer/exponent; process v~N(0,V), measurement w~N(0,W).',
109:'Printed15. MLE data-only versus MAP prior; source typesets argmax chain as if estimator equals posterior probability, a notational issue to avoid.',
110:'Printed16. Posterior becomes next prior; wall-distance range sensor example. More-data accuracy claim is unqualified and not generalized in review.',
111:'Printed17. H=-sum p log2 p; decision-tree impurity. Source broad claim lower entropy means better model is not a universal quality guarantee.',
112:'Printed18. x_dot=Ax+Bu and y=Cx with no direct feedthrough; position/velocity state and reduction to first-order vector.',
113:'Printed19. G=(V,E), directed/undirected edges, path/cycle, rooted directed tree convention and summed path weights.',
114:'Printed20. Dock1 start blue ring, Dock6 magenta goal; green2+3+1 route via3/5; red dashed1-4 blocked; blue edges1-2 cost4,2-4 cost5,4-6 cost2,2-3 cost1.',
115:'Printed21. Graph edges SA,SB,AC,AD,BD,BE,CF,DF,EH,FG,HG; green path SACFG. No arrowheads; BFS FIFO and edge count explicit.',
116:'Printed22. Same graph, red DFS path SACFDBEHG; blue alternative AD,SB,FG. Text says first-found not optimal; broad speed comparison not generalized.',
117:'Printed23. Internal tests/branches outcomes/leaves decisions, classification focus; random forest many trees. Search-tree title does not imply every graph-search tree has attribute tests.',
118:'Printed24. Glass=yes ->Fragile->Low Force; no->Thickness; thick->High Force, thin->Low Force. Information gain weighted child entropies.',
119:'Printed25. Exact formulas100n+1000 and n^2+1. Leading terms and asymptotic rather than fixed-machine comparison.',
120:'Printed26. Lists O(n),O(log n),O(n^2); heuristic example overclaims reduced Big-O/never away. Question safely distinguishes heuristic use only.',
121:'Printed27. Completeness, resolution, probabilistic definitions; general A*/GA guarantees need assumptions. Scoped questions avoid universal optimality.',
122:'Printed28. Six summary categories. SVD and chain rule appear only in summary here; no detailed derivation is present on this slide.'}
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
answers=[]
for i,(q,r) in enumerate(zip(qs,reasoning),1):
 ans=['o1','o2','o4'] if i==10 else ['o1','o3'] if i==71 else ['o1']
 answers.append({'questionId':q['id'],'questionVersion':q['version'],'independentAnswerOptionIds':ans,'reasoning':r,'uncertainPoints':[],'sourceObservations':[notes[c['physicalPage']] for c in q['citations']],'solvedBeforeAnswerSeen':True})
x={'schemaVersion':'1.0.0','batchId':'W01-L03','reviewerId':'define_robotics_data_contracts:L03-independent-reviewer','recordedAt':now,'status':'answers_persisted_before_author_reveal','blindPacketPath':'audits/blind-W01-L03.json','blindPacketSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'frozenAuthorBatchExpectedSha256':'5318423c6fc8981c71f1f9db385b052e4115049e79a92c0269112eec329675ba','exposureStatement':'Read the frozen question/options/citations packet and actual source pages only. No author answer IDs, solutions, rationales, or full batch opened before this record. Course pages expose definitions and worked diagrams; numerical and traversal answers independently derived.','sourceVersions':{'lectures':'2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'},'sourceVisualObservations':[{'physicalPage':p,'slideId':f'lectures-p{p:04d}','previewPath':f'sources/previews/lectures/page-{p:04d}.webp','dimensions':[1800,1013],'method':'rendered_page','notes':n} for p,n in notes.items()],'answers':answers}
p=ROOT/'audits/blind-answers-W01-L03-v1.json';p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');print('Persisted',len(answers),'answers:',p.relative_to(ROOT),'sha256',hashlib.sha256(p.read_bytes()).hexdigest())
