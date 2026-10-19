#!/usr/bin/env python3
"""Reconstruct authored L02 draft batch and answer-hidden review packet.
This is explicit authored content, not an automated slide-to-question template.
No course question becomes verified here.
"""
from pathlib import Path
import copy,json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash, schema_errors,load_json
AUTHOR='define_robotics_data_contracts:L02-author'
STAMP='2026-10-19T12:56:00Z'
SHA=json.load(open(ROOT/'sources/manifest.json'))['sources'][0]['sha256']
SLIDES={s['physicalPage']:s for s in (json.loads(l) for l in (ROOT/'sources/page_maps/lectures.jsonl').read_text().splitlines()) if 50<=s['physicalPage']<=94}
CONCEPTS=[];QUESTIONS=[];BY_KEY={};PAGE_NOTES={}

def concepts(page,topic,items,notes):
 PAGE_NOTES[page]=notes
 for key,title,description in items:
  c={'id':f'W01-L02-C-{key}','title':title,'description':description,'slideIds':[f'lectures-p{page:04}'],'questionIds':[],'status':'identified','topic':topic,'subtopic':title,'prerequisiteConceptIds':[],'coverageNotes':'Identified from full-page visual inspection and extracted text. Independent question and coverage reviews are pending.'}
  CONCEPTS.append(c);BY_KEY[key]=c

def C(page,topic,text,notes):
 items=[]
 for line in text.strip().split('\n'):
  key,title,desc=line.split('|',2);items.append((key,title,desc))
 concepts(page,topic,items,notes)

C(53,'Foundations of AI','''ai-definition|McCarthy definition and attribution|AI is defined as the science and engineering of making intelligent machines; the slide attributes the term to John McCarthy in 1956.
thinking-humanly|Thinking humanly|Cognitive modeling simulates human thought processes; ACT-R is the example.
acting-humanly|Acting humanly|The Turing-test approach seeks behavior indistinguishable from humans; chatbots and conversational agents are examples.
thinking-rationally|Thinking rationally|The laws-of-thought approach emphasizes logic-based correct inference, expert systems and theorem provers.
acting-rationally|Acting rationally|The rational-agent approach maximizes expected goal achievement; autonomous robots and game AI are examples.''','Inspected the four colored boxes and their correct positions. Extracted text order interleaves headings, but visual labels clearly distinguish thinking/acting and humanly/rationally. Footer printed 4.')
C(54,'AI-enabled robots','''adaptive-robot|AI robot versus fully pre-coded behavior|AI robot software can make decisions, learn and adapt using sensor data, examples and interaction rather than programming every behavior in advance.''','Read every bullet including both examples and interaction as learning sources; no substantive figure; footer 5.')
C(55,'History of AI','''history-turing|1950 Turing milestone|The history slide associates 1950 with Alan Turing proposing a machine-intelligence test.
history-dartmouth|1956 Dartmouth milestone|The slide associates 1956 with the Dartmouth Conference and John McCarthy coining AI.
history-expert|1980s expert systems|The timeline associates the 1980s with rule-based expert systems in industry.
history-deepblue|1997 Deep Blue|IBM Deep Blue defeated chess world champion Kasparov in the 1997 milestone.
history-deeplearning|2006 deep learning revival|The slide associates Hinton and deep belief networks with a 2006 neural-network revival.
history-alexnet|2012 AlexNet|The timeline associates AlexNet with a CNN ImageNet victory and growth in deep learning in 2012.
history-llm|LLM and foundation-model timeline caveat|The slide places ChatGPT/LLMs under 2022 and multimodal vision-language-action foundation models under 2024; its GPT-4/Gemini era wording must not be treated as their exact launch dates.''','Read all eight colored timeline rows; flagged imprecise 2022 GPT-4/Gemini era association. Footers and row continuation visible.')
C(56,'AI capability categories','''narrow-ai|Narrow AI|Narrow AI excels at a specific task such as chess, voice assistance or robot control; the slide places We are HERE under it.
general-ai|General AI|General AI is described as human-level reasoning across all cognitive tasks.
super-ai|Super AI|Super AI is described as surpassing human intelligence in every domain.''','Inspected three boxes and connecting line. No printed footer slide number visible; do not assign 7 as an observed printed number.')
C(57,'Turing test','''turing-procedure|Text-based Turing-test procedure|A human judge converses by text with a human and machine; passing means the judge cannot reliably tell them apart.
turing-origin|Turing-test origin|Alan Turing proposed the test in 1950 in Computing Machinery and Intelligence.
turing-components|Turing-test component capabilities|The slide lists natural language processing, knowledge representation, automated reasoning and machine learning.
turing-captcha|Inverse Turing test|The slide describes CAPTCHA as an inverse Turing test.
turing-status|Unrestricted-test statement is source-specific|The slide states no machine has fully passed an unrestricted Turing test; preserve it as a source-time claim rather than a current universal claim.''','Read all five main bullets and four component sub-bullets. Distinguished unrestricted-test assertion from definition; footer 8.')
C(58,'Branches of AI','''branch-ml|Machine learning branch|Learns patterns from data rather than explicitly programming each rule.
branch-vision|Computer vision branch|Interprets and understands images and video.
branch-nlp|Natural language processing branch|Understands and generates human language.
branch-embodied|Robotics and embodied AI|Physical agents perceive and act in the world.
branch-expert|Expert systems|Encode domain expertise through rules and inference engines.
branch-knowledge|Knowledge representation|Stores, organizes and reasons over structured knowledge.
branch-multiagent|Multi-agent systems|Networks of interacting agents produce collective behavior.
branch-evolutionary|Evolutionary algorithms|Optimize solutions by simulating natural selection.
branch-planning|Planning and reasoning|Produce goal-directed sequences of decisions and actions.''','Inspected all nine boxes around central AI node and connecting lines. Lines denote branches, not a temporal pipeline.')
C(59,'Machine learning','''ml-data|Learning from data and generalization|ML software learns models from data and predicts on previously unknown data.
ml-limit|Data limitation|The slide emphasizes that limited datasets constrain learned models; quantity alone is not a guarantee of quality.''','Read five bullets and Learn from Data icon; quantity limitation interpreted alongside summary quality statement.')
C(60,'Machine learning','''mitchell-etp|Experience-task-performance definition|Mitchell defines learning as improved task T performance measured by P with experience E.
programming-vs-ml|Programming versus learning|Traditional programming maps rules plus data to output; the supervised-learning illustration maps data plus outputs to learned rules.
brake-rule|Strict-threshold brake rule|The code illustration brakes only when speed > 50 AND obstacle_dist < 2; equality does not satisfy either strict condition.
ml-three-types|Three learning paradigms|Supervised, unsupervised and reinforcement learning are listed as the main types.''','Inspected two comparison boxes, Mitchell quote, code inequality signs, AND, and lower type list. The Data+Output illustration is not a claim that all ML has labels.')
C(61,'Supervised learning','''regression|Continuous supervised regression|Regression learns from labeled (x,y) pairs to predict a continuous real-valued output such as angle, control signal or image depth.
regression-algorithms|Regression algorithms|Listed families are linear regression, decision trees, random forests, SVMs, k-nearest neighbors and neural/deep networks.
regression-plot|Regression plot interpretation|Scatter plot shows continuous X and Y observations around an increasing fitted line, rather than class regions; illustrative output is 2.37 m/s.''','Read regression box, output unit m/s, list and scatter figure. Axes X/Y have no physical unit labels, so do not invent exact numerical data from dots.')
C(62,'Supervised learning','''classification|Discrete supervised classification|Classification predicts a discrete class from labeled examples, including object, gesture and obstacle/free-space labels.
classification-algorithms|Classification algorithms|Logistic regression, decision trees, random forests, SVMs, k-nearest neighbors and XGBoost are listed.
classification-plots|Binary and multiclass decision regions|The first figure has two classes separated by a boundary; the second has four labeled classes and multiple regions.''','Inspected two scatter diagrams: Class1 red crosses, Class2 triangles; second additionally Class3 circles and Class4 squares. Some title text is clipped at left but content is readable.')
C(63,'Unsupervised learning','''unsupervised|Unlabeled structure discovery|Unsupervised learning finds hidden structure without ground-truth training labels.
clustering-methods|Clustering methods and applications|K-means partitions into K groups, DBSCAN is density-based, and hierarchical clustering is listed; robotics examples are terrain segmentation and pedestrian grouping.
clustering-figure|Clustering figure groups|The original unlabelled point set is shown grouped into three clusters containing two, three and four points.
pca-placement|PCA grouping caveat|PCA appears in the slide Clustering box, but this placement must not be taught as proof that PCA itself is a clustering algorithm.''','Viewed original and clustered point sets, counted 2 orange/3 green/4 blue points. PCA appears as a bullet under Clustering; record classification ambiguity rather than silently teach it.')
C(64,'Unsupervised learning','''generative|Generative models|Generate new samples, including synthetic training data and world-model simulations.
dimensionality|Dimensionality reduction|Compress data into fewer dimensions for sensor compression and planning feature extraction.
anomaly|Anomaly detection|Find unusual outliers using examples such as Isolation Forest, one-class SVM and autoencoder reconstruction error; applications include fault detection.''','Inspected all three boxes and algorithm list. Unexpected obstacle classification is given as an anomaly example, not a definition of supervised classification.')
C(65,'Reinforcement learning','''rl-interaction|Reward-driven interaction|An agent acts on the environment and receives state/reward feedback, seeking cumulative rather than merely immediate reward.
rl-state-action|State and action roles|State describes the environment observation; action is a motor command, joint velocity or gripper command selected by the agent.
rl-reward-policy|Reward and policy roles|Reward is scalar feedback; policy π(a|s) is a state-conditioned action-selection strategy, with π* optimal.
rl-values|State value versus action value|V(s) denotes expected cumulative reward from a state; Q(s,a) concerns taking an action in that state.
rl-exploration|Exploration-exploitation tradeoff|Epsilon-greedy is named as balancing new actions and known good actions.
rl-algorithms|RL algorithm families|Q-learning, deep Q networks and policy-gradient methods are listed.''','Read arrow directions agent→environment action and environment→agent state/reward. Formula/value boxes and final algorithm line inspected; reward timing uses slide r_t convention.')
C(66,'ML applications in robotics','''ml-detection|Detection and recognition|YOLO/Faster-RCNN classify and localize objects in robot camera feeds.
ml-grasp|Learned grasping|Grasp success is learned from data; sim-to-real transfer supports robot hands.
ml-locomotion|Learned locomotion|RL-trained gaits for ANYmal/Spot are examples; performance superiority is source-context dependent.
ml-imitation|Imitation from demonstrations|Behavioral cloning and inverse RL learn using human demonstrations.
ml-fault|Robotic fault detection|ML detects sensor failures or unusual robot behavior.
ml-hri|ML for HRI|Gesture, speech and intent recognition enable natural communication.
ml-semantic-map|Semantic mapping|Combine geometric SLAM with labels such as chair/table/door from neural networks.
ml-path-predict|Trajectory prediction|Social-force or attention models predict pedestrians and other agents.''','Inspected eight application boxes including bottom semantic-map/path rows close to footer. No supporting performance experiment for outperformance claim.')
C(67,'Deep learning','''dl-unstructured|Deep learning for raw unstructured data|The slide motivates neural deep models for images, audio and chat messages, contrasting them with traditional tabular ML.
dl-families|Deep model families|Neural networks, CNNs, RNNs and Transformers are listed; the simplified comparison is not a theorem that statistical ML cannot process derived image features.''','Read all bullets. Treat does-not-perform-well statement as motivation, not a universal impossibility claim.')
C(68,'Neural networks','''neuron|Weighted neuron equation|A neuron computes a = σ(Σ w_i x_i + b); w are weights, b bias and σ activation.
relu-sigmoid|ReLU and sigmoid|ReLU is max(0,x); sigmoid is 1/(1+e^(−x)) with smooth output between zero and one.
network-diagram|Network diagram structure|The drawing shows 3 input nodes, two hidden layers of 4 nodes each, and 3 output nodes, with adjacent-layer full connectivity.
training-roles|Forward, backpropagation and optimizer roles|Forward passes predict; loss measures error; backpropagation computes gradients; Adam/SGD update weights.
network-scale|Network scale caveat|The slide highlights brain inspiration and billions of parameters, which describes large modern systems rather than a requirement for every neural network.''','Inspected neuron formula, all nodes/edges (3-4-4-3), activation signs and training box. No arrow labels or biases shown on network drawing; parameter-count questions must state bias convention.')
C(69,'Neural architectures','''fnn|Feed-forward networks|FNNs have no recurrent loops and are contrasted with sequence-memory architectures.
rnn-lstm|RNN context and LSTM|RNN memory affects future outputs; translation and speech are examples; LSTM addresses long-term-memory limitations.
cnn|CNN local structure|CNNs exploit image spatial structure using local connectivity and parameter sharing; examples are object classification/video analysis.
transformer|Transformer attention|Transformers calculate attention and are prominent in sequence models, LLMs and robot learning; blanket all/replaced claims are treated as simplifications.''','Read left architecture list and right Transformer box. CNN local patches do not by themselves establish every layer shrinks image dimensions; avoid that overgeneralization.')
C(70,'Robotic perception','''robot-pipeline|Sense-process-perceive-decide-act|Sense uses sensors; process filters/extracts features; perceive detects/maps; decide plans/selects; act issues motor commands and feedback.
perception-modalities|Perception modalities|Computer vision, point clouds and sensor fusion are named as perception components.''','Inspected ordered five boxes with numbers 01–05 and connector sequence. Read each stage payload; motor feedback appears under Act.')
C(71,'Computer vision','''vision-pipeline|Vision pipeline stages|Image acquisition → preprocessing → feature extraction → object detection → scene understanding, with listed examples for each stage.
segmentation|Semantic, instance and panoptic segmentation|Semantic labels pixels by class; instance separates individual objects; panoptic combines both, aiding avoidance and grasp zones.
pose6d|6-DoF object pose|Estimate 3D position plus orientation using examples PoseCNN/PVNet/FoundPose for grasping and assembly.
depth|Depth estimation methods|Stereo, structured light, ToF and monocular methods support 3D reconstruction; RealSense and MiDaS are examples.
visual-slam|Visual SLAM|Camera-based simultaneous localization/mapping, including ORB-SLAM3 and Kimera, supports unknown-environment navigation.''','Viewed complete top pipeline and four lower boxes. Table memberships verified visually despite extraction order; no numeric depth relation is supplied.')
C(72,'3D perception','''point-cloud|Unordered point cloud structure|LiDAR point clouds are unordered (x,y,z) point sets without the regular grid of images.
pointnet|PointNet permutation invariance|PointNet (2017) processes points independently then aggregates with a symmetric operation such as max-pooling, preserving invariance to point order.''','Read all bullets, x/y/z tuple, PointNet year, symmetric max-pool and permutation-invariance statement. No figure on this page.')
C(73,'Sensor fusion','''sensor-camera|Camera strengths and limits|Dense color/texture, weak direct depth cues and sensitivity to lighting.
sensor-lidar|LiDAR strengths and limits|Accurate 3D geometry, sparse/no texture and high expense in the slide comparison.
sensor-radar|Radar strengths and limits|Rain/fog operation and velocity measurement, with lower resolution in the comparison.
sensor-imu|IMU strengths and limits|High-rate inertial acceleration, small/cheap hardware, and drift over time; slide labels 6-DoF.
sensor-gps|GPS/GNSS strengths and limits|Global localization, indoor denial and lower update rate in the slide comparison.
sensor-sonar|Sonar strengths and limits|Cheap proximity sensing and underwater use, with low resolution; slide labels 1D.
fusion-early|Early sensor fusion|Concatenate raw data; rich information but computationally costly.
fusion-mid|Intermediate sensor fusion|Combine intermediate features to balance richness and efficiency.
fusion-late|Late sensor fusion|Combine final predictions; modular but loses cross-modal context.''','Read all six modality boxes and three fusion boxes, including edge labels 2D/3D/6-DoF/Abs/1D. Distinguish slide-summary labels from universal sensor specifications.')
C(74,'Language for robots','''asr|Speech recognition|ASR uses acoustic/language models; Whisper/wav2vec2/DeepSpeech and online streaming with VAD are examples.
nlu|Language understanding and grounding|Intent classification, slot filling, percept grounding and context-based ambiguity resolution; BERT/RoBERTa/GPT are examples.
task-grounding|Language-to-action grounding|Maps language to robot actions; Code-as-Policies generates Python and Inner Monologue uses an LLM loop. SayScan spelling differs from SayCan elsewhere.
dialogue|Dialogue management|Tracks conversation state, asks clarifying questions, reports task progress and retains multi-turn memory.''','Inspected all four boxes and contextual introductory sentence. Explicitly observed SayScan spelling in Task Grounding; avoid treating typographic variant as a separate algorithm.')
C(75,'Search','''search-purpose|Search and applications|Search examines alternative possibilities for action/path selection; examples include chess, networking, resource allocation and scheduling. Not every search algorithm guarantees optimality.''','Read all bullets and most optimal wording. Cross-reference next slide showing nonoptimal greedy/DFS rather than repeat the broad statement unqualified.')
C(76,'Search algorithms','''bfs|BFS properties|Breadth-first search is complete for finite branching and optimal for unit costs; slide memory O(b^d), useful for shallow goals.
dfs|DFS properties|Depth-first search uses low memory, is not generally optimal and may fail in infinite spaces; slide writes O(bd).
ucs|Uniform-cost search|Expands least accumulated path cost and handles unequal nonnegative step costs; associated with Dijkstra.
ids|Iterative deepening|Combines depth-first memory efficiency with breadth-first unit-cost optimality when depth is unknown.
greedy|Greedy best-first priority|Expands smallest heuristic estimate h(n), without a general optimality guarantee.
astar|A-star priority and assumptions|Uses f(n)=g(n)+h(n); admissibility supports optimality under suitable search/reopening conventions.
rrt|RRT sampling|Rapidly-exploring Random Trees sample states and build a tree for high-DoF configuration spaces; source places RRT under informed search despite no heuristic requirement stated.
dstar|D-star Lite replanning|Efficient replanning when maps/environment change; used for autonomous navigation.''','Inspected both columns and all eight algorithm rows; formulas O(b^d), O(bd), f=g+h read. Flagged assumptions absent for completeness/optimality and RRT column categorization.')
C(77,'Markov decision processes','''mdp-markov|Markov property|Given current state and action, the next-state model does not require the full earlier history.
mdp-components|MDP state/action/transition/reward|S contains states, A actions, T(s′|s,a) next-state probabilities and R(s,a,s′) immediate task reward; transitions may be deterministic or stochastic.
mdp-discount|Discount factor|γ lies in [0,1] in the slide; near zero emphasizes immediate rewards and near one gives future rewards greater weight.
mdp-objective|Expected discounted return|The optimal policy maximizes expected sum Σ γ^k r_k; finite-horizon conventions must be stated for numeric examples.''','Inspected six labeled boxes and top Markov statement. Reward/transition/policy conditionals and γ bounds read; no horizon/convergence assumption given at γ=1.')
C(78,'Planning hierarchy','''global-planning|Global planning|Map/start/goal input yields collision-free waypoint route; A-star/Dijkstra/PRM/RRT-star examples; path length, static obstacles and smoothness matter.
local-planning|Local planning|Global path/local costmap input yields velocity commands reacting to nearby dynamic obstacles; DWA/TEB/MPPI/MPC examples; collision and speed limits matter.
task-planning|Task planning|World-state/goal input yields symbolic pick/place/open/navigate sequences; STRIPS/PDDL/MCTS/LLM-planner examples; feasibility/recovery matter.''','Read three full columns, inputs, outputs, methods and considerations. PDDL is listed alongside algorithms but is a language in p83; preserve that distinction.')
C(79,'Knowledge representation','''propositional|Propositional logic|True/false facts with AND/OR/NOT/implication; limited expressiveness, theorem-proving foundation.
fol|First-order logic|Variables, predicates and quantifiers express relationships; the slide example Robot(x) ∧ Near(x,obj) → CanGrasp(x,obj) is a stipulated logical rule, not a physical sufficiency claim.
semantic-network|Semantic networks|Concept nodes and relation edges; predecessors of modern knowledge graphs with WordNet/ConceptNet examples.
ontology|Ontologies and OWL|Formal concept/property taxonomy supports reasoning about types, capabilities and affordances.
probabilistic-knowledge|Probabilistic graphical models|Bayesian networks/Markov random fields represent uncertain knowledge and support fusion, SLAM and activity recognition.
llm-knowledge|Implicit LLM knowledge|Transformer weights encode learned implicit knowledge; task-planning examples include SayCan and Code-as-Policies.''','Inspected all six panels including ∀/∃ and exact implication. Flag overly simplified CanGrasp rule: any inference question explicitly assumes it, never claims safe real graspability.')
C(80,'Embodied AI','''embodied-cycle|Intelligence in physical systems|AI in robotics brings perception, planning and action into physical systems.''','Single substantive bullet reviewed; links prior embodied-AI and pipeline concepts but retained as an explicit source statement.')
C(81,'SLAM','''slam-coupling|SLAM coupled estimation|Localization asks where the robot is; mapping asks what its environment looks like; SLAM computes them together.
slam-algorithms|SLAM method examples|EKF-SLAM, ORB-SLAM and graph SLAM are listed.
slam-grid|SLAM occupancy illustration|The illustration shows a marked robot cell amid free/occupied-looking grid cells; it has no legend, coordinates, distances or trajectory, so exact navigation metrics cannot be inferred.''','Inspected grid, red marked cell, dark cells, all explanatory labels. No legend or axes: do not invent occupancy coding or metric scale from colors.')
C(82,'Robot learning paradigms','''bc|Behavioral cloning|Supervised observation-to-action learning from expert demonstrations; vulnerable to distribution shift and compounding errors.
irl|Inverse reinforcement learning|Infers a reward function from demonstrations; Max Entropy IRL/GAIL and preference-based T-REX are named.
rlhf|Human-feedback pipeline|Human rankings/comparisons train a reward model; policy is fine-tuned against it, with PPO as the slide example.
sim-to-real|Simulation transfer|Train in simulation, deploy on real robots; simulation is cheap/parallelizable/safer, but distribution mismatch must be handled.
randomization-adaptation|Randomization versus adaptation|Domain randomization varies textures/physics; domain adaptation aligns simulation and real distributions.
meta-learning|Meta-learning|Learning-to-learn enables few-shot adaptation; MAML is gradient-based and RL-squared models adaptation as a sequence.
world-model|World models|Learn latent environment dynamics; Dreamer plans in latent space and MBPO is model-based policy optimization.''','Read all six boxes, including 5–10-demo source example. Named RLHF deployments and blanket sample-efficiency/generalization claims need source-specific wording, not universal guarantees.')
C(83,'Decision-making architectures','''sense-plan-act|Closed-loop decision cycle|Sense-plan-act runs as continuous feedback, not a one-time open-loop sequence.
strips|Classical task planning|STRIPS actions have preconditions/effects; search finds a plan; PDDL is a language used for task representation.
behavior-tree|Behavior trees|Hierarchical modular control with sequence/fallback/parallel/decorator node examples.
fsm|Finite-state machines|Explicit states/transitions are simple and interpretable for defined tasks but can suffer combinatorial state explosion.
llm-planning|LLM-based planning|Decomposes goals into subtasks/skill calls and handles open-vocabulary instructions.
mpc|Model predictive control|Optimizes an action sequence over a receding horizon using a dynamics model, replanning each step under constraints.
reactive-policy|Reactive learned policies|End-to-end policies map sensing to actions without an explicit online planning stage; PPO/SAC examples; contact-rich suitability is contextual.''','Inspected cycle and six architecture panels. Distinguish model-based receding-horizon MPC from reactive RL and symbolic preconditions/effects.')
C(84,'Manipulation','''manipulation-perception|Manipulation perception|Detect/segment the object, estimate 6-DoF pose, use point-cloud normals and handle occlusion.
grasp-planning|Grasp planning|Sample grasp candidates and assess quality such as force closure; GraspNet/Contact-GraspNet support unknown-object grasping.
manipulation-motion|Manipulation motion planning|Inverse kinematics to pre-grasp pose, collision-free arm trajectories and real-time replanning.
manipulation-control|Manipulation control|Force/impedance control, contact-rich/deformable-object handling and Cartesian feedback.''','Read four numbered pipeline columns and connector order. Typo Occlusoin interpreted as printed occlusion handling; no numerical force-closure criterion supplied.')
C(85,'Autonomous vehicles','''autonomy-levels|SAE level labels on the slide|L0 no automation, L1 driver assist, L2 partial, L3 conditional, L4 high and L5 full automation; detailed responsibility conditions are not given here.
av-sensing|AV sensing and redundancy|Camera/LiDAR/radar/GPS/IMU, HD-map priors and sensor redundancy for safety.
av-perception|AV perception|3D detection CenterPoint/BEVFusion; tracking SORT/DeepSORT/ByteTrack; map segmentation/free space.
av-prediction|AV prediction|Forecast agent trajectories and occupancy flow; Social-LSTM/TNT/MTR examples.
av-planning|AV planning|Route/behavior/motion planning with comfort and safety constraints.
av-control|AV control|MPC trajectory following; Stanley/PurePursuit lateral, PID/ACC longitudinal control.
av-safety|AV safety|Formal verification, shadow mode and human monitoring/takeover are listed as safeguards.''','Read six autonomy boxes and six component panels; only labels, not official full SAE definitions, are on this source page.')
C(86,'Human-robot interaction','''hri-speech|HRI speech and language|Voice/dialogue via ASR Whisper/wav2vec and NLU BERT/GPT.
hri-gesture|Gesture recognition|Hand/body pose and action classification using MediaPipe/OpenPose support nonverbal communication.
hri-emotion|Emotion and expression|FACS facial-action units, AffectNet/EmotionNet and robot expressive displays are examples.
hri-safe|Safe physical HRI|Force/torque sensing, impedance control, collision detection/stopping and cobot safety considerations.
hri-intent|Intent prediction|Predict human next actions using social-force/attention models to support proactive assistance.
hri-explain|Explainability and trust|Explain why the robot acted using examples attention maps/LIME/SHAP and voice narration; explanations support trust.''','Inspected all six panel lists. Emotion-recognition labels are course examples, not a claim reliable mental-state inference is guaranteed.')
C(87,'Application domains','''surgical|Surgical robotics examples|da Vinci is described as surgeon-controlled with tremor filtering; AI examples include tissue recognition, guidance, suturing with IL/force feedback and tumor identification.
rehabilitation|Rehabilitation robotics|Adaptive exoskeletons, RL-personalized gait, EEG intent detection and upper-limb assistance are listed.
service|Service robotics|Hotel delivery Savioke Relay/Keenon, restaurant BellaBot/Servi and airport PEPPER/SANBOT combine voice/navigation/HRI.
domestic|Domestic robotics|Roomba coverage planning, elderly-assistance PARO/Care-O-bot, Moley cooking and ambient assisted living.
agriculture|Agricultural robotics|CV precision spraying, Agrobot/Soft Robotics fruit picking, autonomous tractors and aerial-image yield estimation.
inspection|Inspection robotics|Bridge/pipeline/wind-turbine inspection, drone/CNN crack-corrosion detection, underwater SeaRobotics/Blue Robotics and radiation-tolerant nuclear robotics.''','Read six dense application panels and all names; no medical efficacy or deployment guarantees are inferred from examples.')
C(88,'Responsible AI','''ethics-design|Ethics designed from the start|Robot decisions affect physical safety, fairness and privacy, making ethics an upfront engineering requirement.
bias|Algorithmic bias|Training-data biases may yield demographic disparities or grasp models biased toward common objects.
privacy|Privacy design|Vision can collect sensitive information; on-device inference reduces cloud exposure and federated learning is a named privacy-oriented training approach, not an absolute privacy guarantee.
fail-safe|Fail-safe design|Robot failures can physically harm people; failure should lead to an appropriate safe state.
xai|Explainable AI|People need to understand actions; black-box deployment raises concerns in sensitive domains.
autonomy|Human autonomy|Robots should augment high-stakes human decision-making and retain human-in-the-loop critical actions.''','Inspected introductory warning and all five panels. Read always-default-safe wording as design requirement, not a claim one universal safe configuration exists.')
C(89,'Technology stack','''stack-order|High-to-low abstraction stack|Applications → AI algorithms → middleware → sensing/actuation → computing hardware.
stack-mapping|Stack examples|Applications include surgery/construction/agriculture/defense; AI includes DL/RL/planning/NLP; middleware ROS2/DDS/protocols; sensors/actuators LiDAR/camera/IMU/motors/grippers; hardware CPU/GPU/FPGA/neuromorphic chips.''','Read five aligned stack layers and high/low abstraction labels. The slide groups sensors/actuators separately from computing hardware for this abstraction diagram.')
C(90,'Datasets and benchmarks','''dataset-imagenet|ImageNet table row|Table lists classification, 1.2M images/1000 classes, and pretraining robot visual backbones.
dataset-coco|COCO table row|Table lists detection/segmentation, 330K images/80 categories and environment object detection.
dataset-kitti|KITTI table row|Table lists AV perception/SLAM road sequences for 3D detection, depth and SLAM evaluation.
dataset-nuscenes|nuScenes table row|Table lists 1000 multi-sensor scenes and camera/LiDAR/radar fusion.
dataset-openx|Open X-Embodiment table row|Table lists 1M+ robot trajectories for cross-embodiment manipulation learning.
dataset-rlbench|RLBench table row|Table lists manipulation RL and 100 simulation tasks for policy learning.
dataset-habitat|HabitatSim row caveat|Table labels HabitatSim as embodied navigation with 100K photoreal scans; simulator/dataset distinction and count need independent clarification before teaching this as a general factual count.
dataset-bdd|BDD100K table row|Table lists 100K annotated driving videos with diverse weather/time/conditions.
dataset-scannet|ScanNet table row|Table lists 1513 RGB-D scans for 3D scene understanding, detection and semantic segmentation.
dataset-mpii|MPII table row|Table lists 25K images for pose estimation and human activity recognition.''','Read every row and all four columns at 1800px. Numeric sizes are source-table values, not current dataset-release claims. HabitatSim count/type remains a source dispute.')
C(91,'Future directions','''foundation-trend|Foundation models for robots|The slide identifies multimodal LLMs and physical-world embodied AI as trends.
collaboration-trend|Human-robot collaboration|Co-worker robots use social intelligence, intent prediction and legible motion.
edge-trend|Neuromorphic and edge AI|Ultra-low-power computing is motivated by energy-constrained aerial/wearable robots.
trust-trend|Safe trustworthy AI|Formal verification, conformal prediction and uncertainty quantification make safety a first-class constraint.
data-efficient|Data-efficient learning|The slide highlights 5–50 demonstrations and meta/model-based/imitation/transfer methods as illustrative directions, not guarantees.''','Inspected six trend panels. Few-demo quantities are contextual illustrations; no measured experiment is cited here.')
C(92,'Cross-concept quick reference','''quick-supervised|Supervised perception mapping|CNN/ResNet/Transformer → detection/pose; YOLO/PoseCNN/FoundPose examples.
quick-rl|RL application mapping|PPO/SAC/TD3 → locomotion/manipulation/navigation; ANYmal/Spot/OpenAI Hand examples.
quick-cv|CV technique mapping|Segmentation/optical flow → perception/avoidance; SegFormer/RAFT/MaskRCNN examples.
quick-lidar|LiDAR technique mapping|PointNet/CenterPoint → 3D mapping/detection; PointPillars/VoxelNet examples.
quick-slam|SLAM technique mapping|Factor graphs/g2o → localization/mapping; ORB-SLAM3/Cartographer examples.
quick-motion|Motion-planning mapping|A-star/RRT-star/MPC → paths/arm trajectories; MoveIt2/OMPL/Nav2 examples.
quick-deep-il|Deep-RL and imitation mapping|Table lists GAIL/BC/RLHF, demonstrations, and RT-2/OpenVLA/π0, with distinctions among methods needing care.
quick-foundation|Foundation-model mapping|VLM/LLM/diffusion → language-conditioned manipulation; PaLM-E/RT-2/CLIP examples.
quick-multi|Multi-agent mapping|QMIX/MAPPO relate to swarm/multi-agent coordination; AlphaStar/OpenAI Five are table examples, not physical robot systems.
quick-knowledge|Knowledge-graph mapping|Ontologies/scene graphs → semantic understanding/task planning; KnowRob and printed SayScan example.''','Read every cell of ten-row table. Noted SayScan spelling, broad category overlaps, and nonphysical multi-agent examples. No assumption that each named system is itself a robot.')
C(93,'Lecture synthesis','''summary-diversity|AI is multidisciplinary|ML/DL/CV/NLP/planning/robotics work together rather than representing one algorithm.
summary-data|Data quality and quantity|Both data quality and quantity matter for learned systems.
summary-uncertainty|Uncertainty handling|The summary names Kalman/Bayes/RL for uncertainty handling rather than asserting deterministic certainty.
summary-endtoend|End-to-end learning|Deep RL and imitation can learn sensor-to-motor behavior.
summary-grounded|Language-grounded action|VLMs/LLMs motivate robot generalization through grounded language.
summary-safety|Safety as engineering requirement|Robustness, alignment and ethics are not optional requirements.
summary-quote|Closing quotation is not a theorem|The Minsky-attributed emotion/intelligence quotation is commentary, not a proven necessity of emotion for intelligence.''','Inspected all seven summary rows and closing attributed quote. Perception-first row maps existing pipeline concepts; quotation excluded from factual theorem-style questions.')

EXCLUDED={50:'Lecture title, authorship and branding; no substantive technical concept.',51:'Learning-objective statement only; technical concepts are covered in subsequent pages.',52:'Agenda/outline only; listed headings are mapped to their substantive pages rather than generating outline trivia.',94:'Thank-you closing page with no technical content.'}
for p,n in EXCLUDED.items():PAGE_NOTES[p]=n+' Full rendered page and footer inspected.'
DISPUTES=[
 {'id':'L02-D01','pages':[55],'issue':'2022 timeline row mentions GPT-4/Gemini era without exact chronology.','treatment':'Test source milestones or chronology only; do not derive exact release dates from era wording.','status':'source_caveat'},
 {'id':'L02-D02','pages':[57],'issue':'No unrestricted Turing test pass is a time/criterion-dependent assertion.','treatment':'Source-specific framing only; not a current universal factual answer.','status':'source_caveat'},
 {'id':'L02-D03','pages':[63],'issue':'PCA is placed under Clustering despite being a dimensionality-reduction method.','treatment':'Keep concept identified/flagged; do not accept a general PCA-is-clustering question.','status':'unresolved'},
 {'id':'L02-D04','pages':[67,68,69],'issue':'Statistical ML/unstructured-data, billions-of-parameters and all-modern-LLMs/replaced-RNN statements are broad simplifications.','treatment':'Use qualified architectural distinctions, not universal impossibility or necessity claims.','status':'source_caveat'},
 {'id':'L02-D05','pages':[75,76],'issue':'Broad search optimality/completeness claims omit assumptions; RRT sits under heuristic search despite no required heuristic.','treatment':'State finite branching, cost and reopening conventions; do not teach plain RRT as requiring h.','status':'source_caveat'},
 {'id':'L02-D06','pages':[74,79,92],'issue':'SayScan versus SayCan spelling inconsistency.','treatment':'Avoid treating spelling variants as separate methods; retain exact source evidence.','status':'unresolved'},
 {'id':'L02-D07','pages':[79],'issue':'Near robot implies CanGrasp is an illustrative logical rule, not sufficient real-world grasp feasibility.','treatment':'Explicitly stipulate rule for logic questions; no physical inference.','status':'source_caveat'},
 {'id':'L02-D08','pages':[82],'issue':'RLHF deployments and few-demo/generalization claims are unqualified summaries.','treatment':'Test process distinctions rather than unsupported universal guarantees/deployment histories.','status':'source_caveat'},
 {'id':'L02-D09','pages':[90],'issue':'HabitatSim listed as dataset with 100K scans; type/count need clarification.','treatment':'Flag row, do not use as generally correct dataset-size answer. Other sizes explicitly source-table values.','status':'unresolved'},
 {'id':'L02-D10','pages':[92],'issue':'Quick-reference categories overlap and include game systems as multi-agent examples.','treatment':'Use source-table membership or shared concepts, not assertions that every named system is a physical robot.','status':'source_caveat'}]

# Appended explicit question authoring calls below.
def Q(key,concept_keys,stem,options,correct,reason,simple,*,difficulty='medium',kind='conceptual',skill='conceptual',steps=None,formulas=None,assumptions=None,memory=None,traps=None,extra_pages=None):
 qid='W01-L02-Q-'+key
 if any(q['id']==qid for q in QUESTIONS):raise ValueError('Duplicate question '+qid)
 correct=[correct] if isinstance(correct,int) else correct
 qopts=[{'id':qid+f'-o{i+1}','text':pair[0]} for i,pair in enumerate(options)]
 answer=[qopts[i]['id'] for i in correct]
 rationales={qopts[i]['id']:pair[1] for i,pair in enumerate(options)}
 random.Random(qid).shuffle(qopts)
 pages=sorted({int(s.rsplit('p',1)[1]) for k in concept_keys for s in BY_KEY[k]['slideIds']}|set(extra_pages or []))
 q={'id':qid,'version':1,'status':'draft','authorId':AUTHOR,'stem':stem,'selectionMode':'multi' if len(correct)>1 else 'single','type':kind,'difficulty':difficulty,'cognitiveSkill':skill,'week':1,'lectureId':'L02','topic':BY_KEY[concept_keys[0]]['topic'],'subtopic':BY_KEY[concept_keys[0]]['title'],'tags':['W01','L02',kind],'conceptIds':[BY_KEY[k]['id'] for k in concept_keys],'assumptions':assumptions or [],'options':qopts,'correctOptionIds':answer,'citations':[{'slideId':f'lectures-p{p:04}','sourceId':'lectures','sourceSha256':SHA,'physicalPage':p,'kind':'equation' if kind=='numerical' else 'table' if p in (90,92) else 'figure' if kind=='diagram' else 'statement','locator':f'Printed slide {SLIDES[p]["printedSlideNumber"] or "number absent"}; '+SLIDES[p]['title']+'; supporting panel(s): '+', '.join(BY_KEY[k]['title'] for k in concept_keys if f'lectures-p{p:04}' in BY_KEY[k]['slideIds']),'evidenceText':' '.join((ROOT/f'sources/text/lectures/page-{p:04}.txt').read_text().split()),'role':'premise' if kind=='numerical' else 'explicit','region':None} for p in pages],'solution':{'justification':reason,'optionExplanations':rationales,'steps':steps or [],'formulas':formulas or [],'simpleExplanation':simple,'memoryAid':memory,'misconceptions':traps or [],'examTraps':traps or [],'prerequisiteConceptIds':[]},'origin':'generated','reviewIds':[]}
 QUESTIONS.append(q)
 for k in concept_keys:BY_KEY[k]['questionIds'].append(qid);BY_KEY[k]['status']='drafted'
 return q

def write():
 slides=[]
 for p,orig in SLIDES.items():
  s=copy.deepcopy(orig);s['text']=(ROOT/f'sources/text/lectures/page-{p:04}.txt').read_text();s['conceptIds']=[c['id'] for c in CONCEPTS if s['id'] in c['slideIds']]
  s['visualInspection']={'status':'complete','inspectorId':AUTHOR,'inspectedAt':STAMP,'method':'rendered_page','notes':PAGE_NOTES[p]+' Evidence: sources/previews/lectures/page-'+f'{p:04}'+'.webp, 1800-pixel width.'}
  s['disposition']='excluded' if p in EXCLUDED else 'examinable';s['exclusionReason']=EXCLUDED.get(p)
  s['repeatsSlideIds']=[];s['incrementalChangesChecked']=False
  if p==56:s['printedSlideNumber']=None;s['printedSlideNumberStatus']='absent'
  slides.append(s)
 for key in ['pca-placement','dataset-habitat','summary-quote']:
  if not BY_KEY[key]['questionIds']:BY_KEY[key]['status']='flagged';BY_KEY[key]['coverageNotes']='Retained for explicit adjudication or justified exclusion, not verified coverage. See audits/source-disputes-W01-L02.json.'
 batch={'schemaVersion':'1.0.0','batchId':'W01-L02','authorId':AUTHOR,'sourceVersions':{'lectures':SHA},'physicalPageRange':[50,94],'status':'draft_partial_coverage','questions':QUESTIONS,'concepts':CONCEPTS,'reviews':[],'coverage':{'pagesVisuallyInspected':45,'pagesExcluded':len(EXCLUDED),'conceptsIdentified':len(CONCEPTS),'conceptsWithDraftQuestions':sum(bool(c['questionIds']) for c in CONCEPTS),'questionsDrafted':len(QUESTIONS),'questionsIndependentlyVerified':0,'uncoveredConceptIds':[c['id'] for c in CONCEPTS if not c['questionIds']],'meaningfulAngleReview':'pending independent coverage challenge'}}
 (ROOT/'data/question-batches/W01-L02.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/inspection-batches/W01-L02.json').write_text(json.dumps({'schemaVersion':'1.0.0','batchId':'W01-L02','slides':slides},ensure_ascii=False,indent=2)+'\n')
 packet={'schemaVersion':'1.0.0','batchId':'W01-L02','instructions':'Solve from cited source pages before reading author answers. This packet omits author solution and correctOptionIds. Persist reviewer answers/reasoning first. No question is verified by this packet.','sourceVersions':{'lectures':SHA},'questions':[{**{k:q[k] for k in ['id','version','stem','selectionMode','type','difficulty','cognitiveSkill','assumptions','options','citations']},'questionSha256':question_hash(q)} for q in QUESTIONS]}
 (ROOT/'audits/blind-W01-L02.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'audits/source-disputes-W01-L02.json').write_text(json.dumps({'sourceId':'lectures','sourceSha256':SHA,'issues':DISPUTES},ensure_ascii=False,indent=2)+'\n')
 schema=load_json(ROOT/'data/schema.bank.json')
 for q in QUESTIONS:
  e=schema_errors(q,{'$ref':'#/$defs/question'},root=schema)
  if e:raise ValueError(e)
 print(json.dumps(batch['coverage'],ensure_ascii=False))

if __name__=='__main__':
 exec((ROOT/'scripts/author_W01_L02_questions.py').read_text(),globals())
 exec((ROOT/'scripts/refine_W01_L02_distractors.py').read_text(),globals())
 write()
