#!/usr/bin/env python3
"""L30 author proposal after actual full-page inspection. Never self-verify."""
import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from authoring_helpers import DraftBatch,formula,SHA
from validate import schema_errors,question_hash
AUTHOR='build_offline_study_interface:L30-author';BATCH='W06-L30'
b=DraftBatch(BATCH,6,'L30','Reinforcement Learning',887,AUTHOR)
INSPECTED_AT='2026-10-19T19:22:20+00:00'
NOTES={
887:('Lecture 30 title Reinforcement Learning.','Title only.'),
888:('Objectives: foundations, loop components, policies/values and Q-learning application.','Objectives roadmap only.'),
889:('Contents: introduction, exploration, models, Q-learning, Gymnasium and code.','Contents roadmap only.'),
890:('Recap contrasts labeled supervised mapping and unlabeled unsupervised regularities; RL uses interaction and evaluative feedback rather than correct-action labels. Third branch is a pedagogical taxonomy, not an exhaustive universal classification.',None),
891:('Teacher-versus-critic table: prescribed labeled guidance versus evaluation, often scarce/delayed feedback and learned intermediate values. Feedback need not always be delayed or sparse; later dense rewards are compatible.',None),
892:('Trial-and-error example and complete loop diagram: actions travel agent to environment; observations, next state s_(t+1) and reward r_(t+1) return. Dog/treat is analogy, not a required formal action-label dataset.',None),
893:('Agent is learner/decision-maker; environment is outside the modeled agent. Mobile robot/maze example. Boundary is a modeling choice.',None),
894:('Action a_t belongs to action set A; four maze directions are discrete, steering angle can be continuous. Arrows lead from agent to environment.',None),
895:('Return arrow carries observations/state information and numerical reward. State is complete situation description; observation can be partial, as next page explicitly names o_t separately.',None),
896:('Loop uses o_t of s_t to choose a_t, yielding s_(t+1), new observation and r_(t+1). Episode/trial runs from start to terminal in the pedagogical episodic setting. Later continuing task is practically truncated.',None),
897:('Deterministic policy pi:S→A; stochastic pi(a|s) action distribution. Sarsa on-policy and Q-learning off-policy. Regardless of exploration strategy is too broad without sufficient data coverage/convergence conditions.',None),
898:('Finite undiscounted return sums T rewards from r_(t+1). Infinite discounted return uses powers gamma^(i−1), with 0≤gamma<1. Gamma=0 is immediate-only; closer to one retains distant weights. Bounded rewards plus discount give convergence; time limit is not the only reason for discounting.',None),
899:('Optimal value max over policies; Q*(s,a) fixes first action then optimal continuation; V*(s)=max_a Q*(s,a). Expected return, not guaranteed realization; optimal actions can tie.',None),
900:('Bellman derivation splits first reward from discounted tail; next-state transition distribution P(s_next|s,a). Expectations should be conditioned on current state/action and optimal continuation, omitted in compact notation.',None),
901:('State/action Bellman forms and bracket labels inspected. Q*=expected immediate reward plus gamma-weighted expectation of max next Q; V* maximizes current action. Greedy optimal policy needs actual Q*, not arbitrary current estimates.',None),
902:('Exploration gathers information; exploitation follows best current estimate. Source calls exploitation highest immediate reward, but Q values encode cumulative return. Excessive exploit can miss better actions; excessive explore sacrifices use of learned behavior, not a universal theorem of failure.',None),
903:('Model-free examples Q-learning/Sarsa versus fully known model dynamic programming with value/policy iteration. Model-based does not generally require perfect prior knowledge or eliminate all exploration; learned models exist. Model-free does not mean no learned Q model.',None),
904:('Q update with eta learning rate, gamma discount, sampled reward plus max estimated next value minus old estimate. Last Q omits hat typographically. Future value remains estimated, not wholly observed; convergence claim needs finite/tabular and sampling/step-size assumptions.',None),
905:('Full pseudocode initializes Q outside episodes, initializes s per episode, epsilon-greedy chooses a, observes r and s_next, updates Q, assigns s=s_next and repeats until terminal. Side box gives exploration-branch epsilon and exploitation-branch 1−epsilon. Random exploration can also select greedy action; terminal bootstrap convention omitted.',None),
906:('Diagram receives current gripper location and target 3D location; Q-learning reaches target, then separate gripper closing is shown. Reachability and grasping success are not guaranteed; subsequent FetchReach code is not a grasping task.',None),
907:('Gymnasium standard environment API: make, reset, step, render; environments and wrappers support comparable experiments. It is not itself the MuJoCo physics engine or a complete RL training algorithm.',None),
908:('MuJoCo models dynamics/contact/gravity for simulation before hardware. Four illustrations: pick/place, navigation, humanoid, object manipulation. Sim-to-real support is not a guarantee of safe or successful transfer.',None),
909:('Notebook shell command !pip install gymnasium-robotics mujoco matplotlib -q. FetchReachDense-v4: 7-DOF robot, 4-component continuous input, dense reward minus Euclidean goal error. Reward is nonpositive, not strictly negative at zero distance. The environment blocks the gripper channel; do not infer grasping.',None),
910:('Imports gymnasium as gym, gymnasium_robotics, numpy as np and pyplot; gym.register_envs(gymnasium_robotics), env=gym.make("FetchReachDense-v4"). Dense means per-step distance reward. Registration does not instantiate every robot model; current compatibility helper may be no-op after import.',None),
911:('NX=NY=NZ=8; BIN_SIZE=0.04; N_ACTIONS=6. Float32 ACTION_MAP rows [+x,−x,+y,−y,+z,−z], fourth component zero. Unit normalized commands are not guaranteed one metre or exactly one bin of achieved motion. Underlying API remains continuous while agent chooses six vectors.',None),
912:('Q=zeros((NX,NY,NZ,N_ACTIONS)); alpha=.1,gamma=.95,epsilon=.5. get_state: err=desired_goal−achieved_goal; tuple(clip(((err+.16)/BIN_SIZE).astype(int),0,7)). Code bins relative error, not absolute position, and has clipping/state aliasing. Training rewards=[],5000 episodes, obs,_=reset(),s,total=get_state(obs),0. Q persists across resets.',None),
913:('Up to 50 iterations; randint(N_ACTIONS) if rand()<epsilon else argmax(Q[s]); step(ACTION_MAP[a]) returns obs,r,terminated,truncated,info. The else includes equality. Source says terminated means won; generic termination can include failure, and FetchReach is continuing, not success-terminated.',None),
914:('s_next=get_state(obs); Q[s][a]+=alpha*(r+gamma*max(Q[s_next])−Q[s][a]); s,total=s_next,total+r; break if terminated or truncated. Update is before stopping and unconditionally bootstraps. Correct for continuing-task time-limit truncation, not arbitrary true terminal state with nonzero next estimate.',None),
915:('Append episodic undiscounted total; epsilon=max(.05,epsilon*.998); every (ep+1)%500==0 print last100 mean and epsilon. Output: 500 −7.06 .184;1000 −6.86 .068;1500 −7.41 .050;2000 −6.77;2500 −6.14;3000 −5.98;3500 −5.24;4000 −4.90;4500 −3.87;5000 −3.37, all latter epsilon .050. Trend is not monotonic.',None),
916:('smoothed=convolve(rewards,ones(50)/50,mode="valid"); figsize(10,4), plot(smoothed), axis labels, title, grid,show. Source graph rises roughly −9 to −3/−4 with oscillations and final dip, not convergence to zero. Plot x is window index 0..4950, not explicitly aligned final episode. Performance curve does not prove optimality.',None),
917:('Suggested grid12 and smaller bins,20000+episodes,deep RL and fourth-channel gripper action. Hard-coded clip upper7/offset.16 must be reviewed when changing grid. Larger table/sample burden; deep networks avoid explicit tabulation but do not eliminate all dimensionality problems. FetchReach ignores gripper channel, so action-only change cannot create grasping.',None),
918:('Summary repeats interaction/reward, greedy action from Q*, model-free/off-policy Q-learning and example. No new premise; qualifications retained.',None),
919:('Alpaydin textbook reference.','Bibliography only; unprovided book contents are not claimed inspected.'),
920:('Thank-you closing.','Closing only.')}
ISSUES=[
(890,'RL is called the third branch.','A pedagogical comparison, not a universal exhaustive taxonomy.'),
(891,'Critic feedback is described as scarce and delayed.','This is common, not necessary; the lecture later uses dense per-step rewards.'),
(897,'Off-policy learning works regardless of exploration strategy.','Its target can differ from the behavior policy, but learning guarantees still need adequate state-action coverage and other assumptions.'),
(898,'Discounting is motivated by a hard time limit.','Discounted infinite-horizon return is well defined for bounded rewards and 0≤gamma<1; a hard cutoff is not required.'),
(899,'Optimal wording may suggest guaranteed return.','Values optimize expected cumulative return; individual stochastic outcomes can differ and actions can tie.'),
(902,'Exploitation chooses highest immediate reward.','Q-based exploitation chooses greatest estimated cumulative return, which need not maximize immediate reward.'),
(903,'Model-based learning requires perfect prior knowledge and no exploration.','The slide contrasts known-model planning with model-free learning; model-based methods can instead learn models and need exploration.'),
(904,'Target is labeled actually happened and convergence is attributed only to decaying learning rate.','The reward and transition are sampled but next Q is estimated. Classical guarantees require finite/tabular assumptions, sufficient visits and suitable step sizes; fixed alpha in the example does not establish that theorem.'),
(905,'Terminal update convention is unstated.','A genuine terminal successor has no continuing return; an external time-limit truncation of a continuing task is different.'),
(906,'Any arbitrary target and subsequent grasping are suggested.','Targets must be reachable under task constraints. FetchReach trains reaching, not object grasping.'),
(909,'Dense reward is called always negative and fourth action is described as gripper control.','Negative distance is zero at exact coincidence. FetchReach blocks the fourth gripper command; its inclusion in the API does not make it effective.'),
(910,'register_envs is described as loading all robot models.','In tested Gymnasium 1.4.0 it is a compatibility no-op; importing gymnasium_robotics registers environments, and make constructs the selected environment.'),
(911,'The action example implies a unit command is a physical displacement.','Actions are normalized controls; achieved movement is governed by the simulator and is not guaranteed one metre or one discretization bin.'),
(912,'State is described as current position.','The code bins desired minus achieved goal, clips tails and omits other observation components; this compressed relative state can alias different physical conditions.'),
(913,'terminated means won.','Termination indicates a task-defined terminal state, not necessarily success. FetchReach is continuing and its default time limit truncates after 50 steps.'),
(914,'Unconditional bootstrap precedes both termination and truncation.','Appropriate for continuing FetchReach truncation; not a generic true-terminal update with a nonzero next-state estimate.'),
(915,'One printed stochastic training trace may look guaranteed or monotonic.','No seed is supplied, and even the displayed checkpoints worsen between episodes 1000 and 1500.'),
(916,'Plot caption/prose implies convergence near zero.','The displayed curve fluctuates around negative totals and does not prove convergence, zero error or optimality.'),
(917,'Larger grid, deep RL and gripper extension are suggested as simple changes.','Update hard-coded bounds/offsets together with shape, account for sample/storage costs, and use an actual grasp-capable task rather than changing an ignored FetchReach channel.')]

def add(p,key,title,stem,opts,why,**kw):
 correct=list(kw.pop('correct',(0,)));k=len(b.questions)%4;opts=opts[k:]+opts[:k];correct=[(i-k)%4 for i in correct]
 conflict_pages=kw.pop('conflict_pages',None);code=kw.pop('code',False)
 kw.setdefault('difficulty','easy')
 q=b.add(p,key,title,stem,[o[0] for o in opts],correct,why,[o[1] for o in opts],**kw);q['options'].sort(key=lambda o:o['id'])
 for c in q['citations']:
  c['locator']=f"Lecture 30, physical PDF page {c['physicalPage']}, actual printed footer {c['physicalPage']-886}: {title}"
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
  s['printedSlideNumber']=str(p-886);s['printedSlideNumberStatus']='present';s['printedNumberEvidence']='Actual bottom-right footer inspected; physical PDF page retained separately.'
  s['visualInspection']={'status':'complete','inspectorId':AUTHOR,'inspectedAt':INSPECTED_AT,'method':'rendered_page','notes':note+' Actual readable 1800×1013 source pixels inspected alongside text.','previewSha256':hashlib.sha256((R/s['previewPath']).read_bytes()).hexdigest(),'dimensions':[1800,1013]};slides.append(s)
 for typ,rows in [('question',b.questions),('concept',list(b.concepts.values())),('slide',slides)]:
  errors=[e for row in rows for e in schema_errors(row,json.loads((R/f'data/schema.{typ}.json').read_text()))];assert not errors,(typ,errors)
 (R/f'data/inspection-batches/{BATCH}.json').write_text(json.dumps({'batchId':BATCH,'slides':slides},ensure_ascii=False,indent=2)+'\n')
 (R/f'audits/{BATCH}-source-issues.json').write_text(json.dumps({'sourceId':'lectures','sourceSha256':SHA,'issues':data['sourceIssues'],'officialDocumentationChecked':[{'url':u,'purpose':v} for u,v in [('https://robotics.farama.org/envs/fetch/reach/','Negative distance reward, continuing task, ignored gripper and default 50-step truncation.'),('https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/','True termination versus time-limit truncation and bootstrapping.'),('https://gymnasium.farama.org/api/registry/','Registration and environment construction.'),('https://www.gatsby.ucl.ac.uk/~dayan/papers/cjch.pdf','Classical tabular Q-learning convergence assumptions.')]],'documentationNote':'Primary documentation checked on 2026-10-19. External clarification is not lecture coverage. Actual installed source and runtime tests are separately captured.','runtimeQualification':'The literal unpinned installation initially selected MuJoCo 3.16.0 and environment construction failed. An explicitly added MuJoCo 3.3.7 pin in an isolated temporary environment made the source loop executable; see initial-runtime-attempt and author-simulation artifacts.'},ensure_ascii=False,indent=2)+'\n')
 (R/f'audits/{BATCH}-author-progress.json').write_text(json.dumps({'frozen':frozen,'questionCount':len(b.questions),'conceptCount':len(b.concepts),'inspectedPages':list(NOTES),'next':'Independent source-based answer and coverage review required.' if frozen else 'Continue source-grounded drafting.'},indent=2)+'\n')
 print('Saved',len(b.questions),'drafts;',len(slides),'actual page inspections; frozen=',frozen)

RET=formula('G_t = Σ_(i=1)^T γ^(i−1) r_(t+i)',{'G_t':'discounted return from decision time t','t':'current discrete time','T':'number of included future rewards','i':'reward-offset summation index','γ':'dimensionless discount factor','r_(t+i)':'reward received i transitions after t'},{'G_t,r_(t+i)':'reward units','t,T,i,γ':'dimensionless'},['Finite horizon T; 0≤γ≤1. For the infinite discounted case use T→∞ with bounded rewards and γ<1.'])
TD=formula('Q_new(s,a) = Q_old(s,a) + α [r + γ max_b Q_old(s_next,b) − Q_old(s,a)]',{'Q_new(s,a)':'updated state-action value estimate','Q_old(s,a)':'estimate before this update','s':'current encoded state','a':'action taken','α':'learning rate','r':'observed immediate reward','γ':'discount factor','s_next':'encoded successor state','b':'candidate next action','Q_old(s_next,b)':'pre-update successor action-value estimate'},{'Q_new,Q_old,r':'reward units','α,γ':'dimensionless','s,s_next,a,b':'state/action labels'},['Nonterminal successor, or continuing task with external time-limit truncation; true terminal continuation is zero.'])
save()
add(890,'feedback-paradigms','Learning signals across three paradigms','Which comparison matches the lecture’s introduction?',[
 ('Supervised learning uses labeled targets, unsupervised learning seeks regularities, and reinforcement learning uses evaluative interaction.','These are the three contrasting learning signals.'),
 ('Reinforcement learning requires a teacher’s correct action label after every move.','That substitutes supervised instruction for evaluative feedback.'),
 ('Unsupervised learning is defined by rewards received after chosen actions.','This describes the reinforcement interaction rather than the stated unsupervised setting.'),
 ('Supervised learning cannot use numerical target values because only RL uses numbers.','Regression can have numerical supervised targets; reward and target roles differ.')],
 'The comparison concerns the source of learning guidance, not a claim that these are the only possible learning categories.',conflict='Third branch is pedagogical wording, not an exhaustive universal taxonomy.')
add([891,909],'teacher-critic','Teacher versus critic and dense feedback','Which statement preserves both the teacher–critic contrast and the later dense-reward example?',[
 ('A critic evaluates outcomes rather than prescribing correct actions, and its reward can still arrive at every step.','Dense evaluation is compatible with a critic.'),
 ('A critic must remain silent until an entire episode ends.','Delayed feedback is possible, not a necessary definition.'),
 ('A teacher and critic differ only in whether their signals are integers.','Signal role, not integer dtype, defines the contrast.'),
 ('Dense reward supplies the unique correct next action as a supervised label.','A reward evaluates a transition and need not prescribe a unique action.')],
 'The source’s frequent scarcity/delay description is not universal: the FetchReach dense reward evaluates distance at each step.',difficulty='medium',conflict='Page 891 presents critic feedback as scarce/delayed; page 909 uses dense per-step reward.',conflict_pages=[891])
add(892,'loop-arrows','Agent–environment diagram','In the lecture’s interaction diagram, which directional assignment is correct?',[
 ('Actions go from agent to environment; observations and reward return from environment to agent.','This follows the arrow directions.'),
 ('Rewards are the agent’s commands to the environment, while actions return as feedback.','It swaps commands and evaluations.'),
 ('The environment selects the agent’s policy parameter as a labeled action every step.','The diagram does not replace decision-making with teacher labels.'),
 ('Observations go only from agent to environment and never inform subsequent action choice.','The feedback arrow informs the agent’s decisions.')],
 'The agent acts, the environment changes, and feedback informs the next decision.',typ='diagram')
add(893,'agent-boundary','Agent and environment boundary','For the lecture’s mobile robot navigating a maze, which modeling assignment is coherent?',[
 ('The decision-making controller is the agent; the modeled maze dynamics and feedback are part of its environment.','It identifies learner and external interaction system.'),
 ('The maze is the agent solely because it provides reward.','Providing feedback does not make the maze the learner.'),
 ('A motor command is the entire environment, while every wall is an action.','It confuses actions with physical surroundings.'),
 ('The reward number must be a separate learning agent in every RL model.','Reward is a feedback signal, not necessarily another agent.')],
 'The agent is the decision-maker; the environment is what it interacts with outside the chosen modeling boundary.',typ='scenario')
add(894,'action-space','Discrete and continuous action sets','Which pairing correctly illustrates the action-space contrast on the slide?',[
 ('Choosing north/south/east/west is discrete; selecting a steering angle from an interval is continuous.','The former has finitely listed choices, the latter a continuous range.'),
 ('Choosing four directions is continuous because motion occurs through physical space.','Physical motion does not make a finite command set continuous.'),
 ('A steering angle is discrete whenever written as a decimal in software.','Numerical representation does not change the modeled continuous action space.'),
 ('Actions must always be scalar, so neither directions nor steering commands are valid.','Actions can be categorical, scalar or vector-valued.')],
 'The modeled action set, not the physical continuity of the robot’s trajectory, determines the distinction.',typ='match')
add([895,896],'state-observation','State is not always fully observed','Which distinction is important when the loop uses observation o_t of state s_t?',[
 ('The state describes the modeled situation, while the agent’s observation may expose only part of it.','This allows partially observed interaction.'),
 ('o_t must equal the scalar reward r_t by definition.','Observation and reward play different roles.'),
 ('Every observation necessarily reveals all hidden variables needed to predict transitions.','Partial observation is possible.'),
 ('States are actions chosen by the agent, while observations are its policy probabilities.','This swaps different loop components.')],
 'A complete modeled state and the information actually sensed by the agent need not coincide.')
add(896,'time-index','Transition timing','Starting from observation o_t of state s_t, which sequence matches the slide’s time indices?',[
 ('Choose a_t, transition to s_(t+1), then receive o_(t+1) and r_(t+1).','The new feedback follows the current action.'),
 ('Receive r_(t+1), then use it to choose a_t before that transition occurs.','This reverses the causal timing of the shown interaction.'),
 ('Choose s_(t+1) as the action and receive a_t as reward.','States, actions and rewards are different objects.'),
 ('Choose a_(t+1) from o_t and always keep s_t unchanged.','This changes indices and rules out environment evolution without justification.')],
 'The chosen action at time t produces the successor state and its associated next reward/observation.',typ='match')
add([896,913],'episode-versus-truncation','Episode boundary and continuing tasks','A continuing task is collected in 50-step segments by an external time limit. Which interpretation is correct?',[
 ('The recorded segment can end without the underlying task entering a terminal state.','External truncation need not be an MDP terminal event.'),
 ('Every 50-step boundary proves that the robot reached its goal.','A time limit is not a success certificate.'),
 ('Continuing tasks cannot be reset for training because they have no natural terminal state.','Training can collect truncated segments and reset.'),
 ('The environment’s reward must become zero at a time limit.','Ending data collection does not impose zero task reward.')],
 'The lecture’s start-to-terminal episode definition fits episodic tasks; its FetchReach example instead uses a continuing task with time-limit truncation.',difficulty='medium',conflict='The episodic description and terminated-means-won wording cannot be applied unqualified to continuing FetchReach.',conflict_pages=[913])
add(897,'policy-types','Deterministic and stochastic policies','Which statement correctly distinguishes the two policy forms?',[
 ('A deterministic policy maps a state to one action; a stochastic policy assigns action probabilities conditioned on state.','This matches π:S→A versus π(a|s).'),
 ('A deterministic policy returns reward, while a stochastic policy returns the next state.','Policy output concerns actions, not environment reward or transition.'),
 ('A stochastic policy requires every action to have equal probability in every state.','Uniform choice is only one possible distribution.'),
 ('A deterministic policy must select the same action in every state.','It can choose different actions at different states.')],
 'Determinism means one specified action per given state, not one action for the entire task.')
add(897,'on-off-policy','On-policy versus off-policy','How does the slide classify Sarsa and Q-learning?',[
 ('Sarsa is on-policy; Q-learning is off-policy because its greedy target can differ from its exploratory behavior.','The target/behavior distinction explains the classification.'),
 ('Sarsa is off-policy; Q-learning must evaluate exactly the action distribution it executes.','This reverses the stated distinction.'),
 ('Both are model-based because a table is a known transition model.','A value table is not the transition/reward model.'),
 ('Q-learning is off-policy only when it never explores any action.','It can learn a greedy target while executing exploratory actions.')],
 'Q-learning uses a maximum in its bootstrap target rather than requiring the next action sampled by its behavior policy.',difficulty='medium')
add(897,'coverage-off-policy','Off-policy does not remove data requirements','An off-policy learner never visits action b at state s. What follows about the slide’s “regardless of exploration strategy” claim?',[
 ('Off-policy target flexibility does not guarantee learning the unknown value of that unvisited pair.','The required information may never be sampled.'),
 ('The maximum operator automatically reveals the exact return of every unvisited action.','Taking a maximum over estimates does not supply missing data.'),
 ('Off-policy learning makes all actions equally valuable after one observation.','Neither off-policy learning nor one sample implies equal values.'),
 ('The learner becomes on-policy simply because one action is missing from its data.','Coverage deficiency does not redefine target versus behavior policy.')],
 'Off-policy identifies whose policy is being learned; adequate state-action sampling and other conditions remain necessary for classical guarantees.',typ='scenario',difficulty='medium',conflict='The source says off-policy learning operates regardless of exploration strategy without coverage qualifications.')
add(898,'finite-return','Finite undiscounted return','For the explicitly supplied next three rewards [2, −1, 4], what is the finite undiscounted return?',[
 ('5.','The sum is 2 − 1 + 4.'),('7.','This drops the negative reward.'),('4.','This keeps only the final reward.'),('5/3.','This is the average, not the cumulative sum.')],
 'The finite undiscounted expression sums every included future reward without averaging or discounting.',typ='numerical',steps=['Sum the three rewards: 2 + (−1) + 4 = 5.'],formulas=[RET],assumptions=['These reward values are an added arithmetic example; T=3 and γ=1.'])
add(898,'discounted-return','Discount powers start at zero','Using rewards [2, −1, 4] and γ = 0.5, what is the three-step discounted return?',[
 ('2.5.','2 + 0.5(−1) + 0.25(4) = 2.5.'),('1.25.','This incorrectly discounts the immediate reward once as well.'),('5.','This omits all discounting.'),('3.5.','This applies one factor of 0.5 to both later rewards instead of successive powers.')],
 'The first reward has weight γ^0 = 1; later rewards have successively smaller powers.',typ='numerical',difficulty='medium',steps=['Use weights 1, 0.5 and 0.25.','Return = 2 − 0.5 + 1 = 2.5.'],formulas=[RET],assumptions=['Added three-reward example; no rewards beyond these are included.'])
add(898,'discount-extremes','Meaning of the discount factor','Which interpretation follows from the lecture’s infinite-horizon return?',[
 ('γ = 0 retains only the next reward; values closer to 1 give distant rewards relatively more weight.','This follows from the powers γ^(i−1).'),
 ('γ = 0 weights all future rewards equally.','Only the first term survives when γ=0.'),
 ('Increasing γ makes a fixed distant positive reward less influential.','Its weight increases for a fixed positive horizon exponent.'),
 ('γ is the probability of choosing a random exploratory action.','That is ε in the shown epsilon-greedy scheme.')],
 'Discounting and exploration are different mechanisms: γ weights future reward while ε controls the behavior policy.')
add(898,'infinite-return','Bounded infinite reward series','In an added deterministic example, reward 2 arrives at every future step and γ = 0.9. What is the infinite discounted return?',[
 ('20.','The geometric sum is 2/(1−0.9).'),('18.','This discounts the first reward unnecessarily.'),('2.','This ignores every later reward.'),('Unbounded, because every infinite sum of positive rewards diverges.','Geometrically decreasing weights yield a finite sum here.')],
 'An infinite number of rewards can have a finite discounted sum; no hard time cutoff is needed for this bounded example.',typ='numerical',difficulty='medium',steps=['G = 2(1 + 0.9 + 0.9² + …).','The ratio is below 1, so G = 2/(1−0.9) = 20.'],formulas=[formula('G = c/(1−γ)',{'G':'infinite discounted return','c':'constant reward per transition','γ':'discount factor'},{'G,c':'reward units','γ':'dimensionless'},['0≤γ<1; deterministic constant reward c.'])],conflict='The source ties discounting to a hard time limit; the infinite bounded series does not require one.')
add(899,'state-action-values','Optimal state value and action value','Which definition matches Q*(s,a) and its relationship to V*(s)?',[
 ('Q* fixes the first action a and then follows an optimal continuation; V*(s) is the maximum over first actions.','This is the stated state/action value relationship.'),
 ('Q*(s,a) is only the immediate reward from a, with no future return.','It includes optimal future continuation.'),
 ('V*(s) averages all Q*(s,a) equally regardless of policy.','Optimal value takes a maximum, not a uniform average.'),
 ('Q* depends on action a only when γ equals zero, so actions can otherwise be omitted.','The first action generally affects reward and successor state for any discount.')],
 'The first action is constrained in Q*, whereas V* also optimizes that first choice.',difficulty='medium')
add(899,'optimal-expectation','Optimality is in expectation','A policy has the greatest expected return, but one noisy episode gives a poor reward. Which conclusion is justified?',[
 ('A poor realization alone does not refute optimality in expected return.','Stochastic outcomes can vary under an optimal policy.'),
 ('An optimal policy must maximize every possible realized trajectory simultaneously.','Expected optimality is not a pathwise guarantee.'),
 ('Optimal policies cannot exist when any transition is stochastic.','The expectation explicitly accommodates stochasticity.'),
 ('The episode proves all actions have equal Q values.','One outcome cannot establish equality of expected values.')],
 'The expectation in the source is essential; it does not promise the same or best realized outcome on every trial.',typ='scenario',difficulty='medium',conflict='Unqualified maximum-return wording must retain the expectation present in the equations.')
add(900,'bellman-decomposition','First reward plus discounted tail','Which decomposition gives the Bellman structure of an infinite discounted return?',[
 ('Separate r_(t+1), then multiply the return beginning at t+1 by γ.','Factoring one γ from every later term leaves the same tail structure.'),
 ('Separate r_(t+1), then add an undiscounted tail regardless of γ.','This drops one discount factor from every later term.'),
 ('Multiply the immediate reward by γ and leave all later rewards unweighted.','This reverses the correct pattern of weights.'),
 ('Replace all future rewards with the number of available actions.','Action count is not a return tail.')],
 'The discounted sum is recursively r_(t+1) + γ G_(t+1); conditioning and optimal continuation yield the Bellman equations.',typ='derivation',difficulty='medium',steps=['Write G_t = r_(t+1) + γ r_(t+2) + γ² r_(t+3) + ….','Factor γ from the terms after the first: G_t = r_(t+1) + γ G_(t+1).'],formulas=[RET])
add(900,'transition-probability','Transition model in Bellman expectations','What does P(s_next | s,a) represent in the lecture’s equation?',[
 ('The probability of successor state s_next given current state s and chosen action a.','It describes environment dynamics conditioned on the decision.'),
 ('The policy’s probability of action a given state s.','That is π(a|s), a different distribution.'),
 ('The learning rate for updating the current Q estimate.','The learning rate is η or α, not a state-transition distribution.'),
 ('The probability that the immediate reward equals the current Q estimate.','This is not what the conditional variables denote.')],
 'The transition model weights next-state values in an expected continuation return.')
add(901,'bellman-number','Expected Bellman backup','In an added one-action backup, expected immediate reward is 1, γ = 0.9, and successor values are 8 and 4 with probabilities 0.25 and 0.75. What is Q*(s,a) under these given continuation values?',[
 ('5.5.','1 + 0.9(0.25×8 + 0.75×4) = 5.5.'),('6.0.','This uses the correct expected continuation 5 but omits its discount.'),('8.2.','This takes only the best successor value 8 instead of averaging transition outcomes.'),('4.5.','This omits the immediate reward 1.')],
 'Environment outcomes are probability-weighted; the agent does not choose which random successor occurs.',typ='numerical',difficulty='medium',steps=['Expected successor value = 0.25×8 + 0.75×4 = 5.','Backup = 1 + 0.9×5 = 5.5.'],formulas=[formula('Q*(s,a) = R(s,a) + γ Σ_x P(x|s,a) V*(x)',{'Q*(s,a)':'optimal value after first action a at s','R(s,a)':'expected immediate reward','γ':'discount factor','x':'successor-state summation variable','P(x|s,a)':'transition probability','V*(x)':'optimal continuation state value','s':'current state','a':'current action'},{'Q*,R,V*':'reward units','γ,P':'dimensionless','s,a,x':'state/action labels'},['The supplied successor values are the continuation values used in this backup.'])])
add(901,'max-inside-expectation','Next action may depend on observed successor','Two successor states occur with equal probability. Their next-action Q pairs are (10,0) and (0,10). What is the expected optimal next value when the next action can depend on the observed successor?',[
 ('10.','Each successor permits its own best action worth 10.'),('5.','This forces one fixed action before the successor is observed.'),('20.','This adds both maxima without probability weights.'),('0.','This selects the worse action in each successor.')],
 'The Bellman action maximum is inside the next-state expectation because the later decision can use the later state.',typ='numerical',difficulty='medium',steps=['At the first successor max(10,0)=10.','At the second successor max(0,10)=10.','Expected maximum = 0.5×10 + 0.5×10 = 10.'],assumptions=['Added two-successor example; successor state is observed before the next action.'])
add([899,901],'greedy-ties','Greedy policy and tied values','At a state, true optimal Q values for actions A, B and C are 5, 5 and 2. Which actions may an optimal greedy policy select?',[
 ('A or B.','Both attain the maximum value 5.'),('Only A, because the mathematical maximum must be unique.','A maximum value can be attained by multiple actions.'),('C, because optimal policies minimize positive Q values.','The objective here maximizes return.'),('Every action equally, because any tie makes all actions optimal.','The tie at 5 does not promote C with value 2.')],
 'Argmax can be a set. A particular implementation may choose one tied maximizer, but uniqueness is not implied.',typ='scenario')
add(902,'exploit-cumulative','Exploitation uses estimated return','Suppose estimated cumulative Q values are Q(A)=8 and Q(B)=3, but A’s immediate reward is lower. Which choice is Q-greedy exploitation?',[
 ('A, because it maximizes the estimated cumulative return.','Q-based exploitation compares Q values, not only immediate rewards.'),
 ('B, solely because its immediate reward is larger.','This is the source’s overly myopic wording, not Q-greedy choice under the stated values.'),
 ('Uniform random choice, because unequal Q values require exploration.','Exploration is a separate choice, not forced by unequal values.'),
 ('Neither action, because negative short-term outcomes invalidate Q estimates.','Delayed benefits can make an action valuable despite lower immediate reward.')],
 'Q values summarize discounted cumulative reward; exploitation of them need not be myopic.',typ='scenario',difficulty='medium',conflict='Page 902 calls exploitation selection of highest immediate reward rather than greatest estimated cumulative value.')
add(902,'exploration-tradeoff','Exploration and exploitation tradeoff','Why might a learner deliberately choose an action that is not currently estimated best?',[
 ('To gather information that can reveal a better long-term choice.','Exploration can improve uncertain estimates.'),
 ('Because exploration guarantees that the very next reward will exceed exploitation’s reward.','Exploration can incur an immediate cost.'),
 ('Because the current Q table cannot be used until every possible trajectory is known.','Learning can alternate estimation, exploration and exploitation.'),
 ('Because selecting a non-greedy action removes all need for future learning.','One exploratory decision does not settle the task.')],
 'Exploration trades some current performance for information; too little can preserve a mistaken preference.')
add(903,'model-free-based','Known-model planning versus model-free learning','Which pairing matches the lecture’s algorithm comparison?',[
 ('Known-model value/policy iteration plans with dynamics; Q-learning and Sarsa can learn values from sampled interaction without an explicit transition model.','This is the bounded contrast intended by the slide.'),
 ('Q-learning requires a complete transition-probability table before any update.','Its sampled update does not require that explicit model.'),
 ('A Q table is itself a complete dynamics model specifying every successor probability.','Values and dynamics are different objects.'),
 ('Model-based learning can never learn its model from data.','The source’s perfect-prior-knowledge wording is not a universal definition.')],
 'The known-model dynamic-programming example should not be generalized to every model-based method.',difficulty='medium',conflict='Page 903 presents perfect prior model knowledge and absence of exploration as universal model-based requirements.')
add(904,'td-parts','Target, error and update','Which expression is the temporal-difference error in the lecture’s nonterminal Q-learning update?',[
 ('r + γ max_b Q(s_next,b) − Q(s,a).','It is target minus the old estimate.'),
 ('α Q(s,a) + r.','This omits discounted continuation and does not subtract the old estimate.'),
 ('Q(s,a) − γ max_b Q(s_next,b) − r.','This is the negative of the stated error.'),
 ('max_b Q(s_next,b) alone.','This is only the undiscounted continuation component.')],
 'The update adds α times target-minus-estimate; reward and successor are sampled, while the future Q term remains estimated.',difficulty='medium',formulas=[TD],conflict='The source labels the target as what actually happened although its future Q component remains estimated.')
add(904,'td-numerical','One Q-learning update','For an added nonterminal example, old Q=2, α=0.1, reward=1, γ=0.9 and maximum next Q=4. What is the updated Q?',[
 ('2.26.','Target 4.6, error 2.6 and correction 0.26 give 2.26.'),('4.6.','This replaces Q by the target as if α were 1.'),('2.46.','This adds α times the target but forgets to subtract old Q in the error.'),('1.74.','This reverses the sign of target minus old estimate.')],
 'A learning rate of 0.1 moves the old estimate one tenth of the way toward the target.',typ='numerical',difficulty='medium',steps=['Target = 1 + 0.9×4 = 4.6.','TD error = 4.6−2 = 2.6.','New Q = 2 + 0.1×2.6 = 2.26.'],formulas=[TD])
add([904,912],'convergence-conditions','A learning-rate statement is not a convergence proof','The example uses fixed α=0.1. Which conclusion is justified?',[
 ('The shown run alone does not establish classical tabular Q-learning convergence; coverage and suitable step-size assumptions must be checked.','A demonstration and theorem have different evidence requirements.'),
 ('Any positive fixed α proves exact convergence in every stochastic environment.','Persistent noise and missing conditions defeat this universal assertion.'),
 ('A decreasing learning rate alone guarantees convergence even for never-visited actions.','No step-size schedule can replace missing state-action information.'),
 ('Off-policy status makes finite state/action and sampling assumptions irrelevant to every convergence theorem.','Off-policy classification does not erase theorem hypotheses.')],
 'Classical guarantees involve finite/tabular conditions, sufficient visits and suitable learning-rate sequences; the fixed-alpha source demonstration is not itself such a proof.',difficulty='medium',conflict='Page 904 attributes convergence too simply to decaying learning rate; page 912 uses a fixed value.',conflict_pages=[904])
add(905,'pseudocode-persistence','Q table and episode initialization','Which placement matches the lecture’s Q-learning pseudocode?',[
 ('Initialize Q before the episode loop; initialize the starting state at the beginning of each episode.','This preserves learned values across episodes.'),
 ('Reset the entire Q table after every action.','That discards almost all accumulated learning.'),
 ('Initialize the starting state once and never reset between episodes.','Episodes need their own starting conditions.'),
 ('Update Q only before observing the reward and successor state.','The sampled target requires the observed transition.')],
 'Per-episode state reset is distinct from global value-table initialization.',typ='algorithm-trace')
add(905,'epsilon-branches','Exploration branch probability versus action probability','With six actions, one uniquely greedy action and ε=0.5, the random branch samples all six uniformly. What is the total probability of selecting the greedy action?',[
 ('7/12.','It can be selected by exploitation (1/2) or random exploration (1/12).'),('1/2.','This forgets that exploration can choose the greedy action too.'),('1/12.','This counts only the exploratory route.'),('1/6.','This treats the complete behavior policy as uniform.')],
 'ε is the probability of entering the random branch, not the probability of choosing a non-greedy action.',typ='numerical',difficulty='medium',steps=['Exploitation selects the unique greedy action with probability 1−ε=1/2.','Exploration selects it with probability ε/6=1/12.','Total = 1/2+1/12=7/12.'],formulas=[formula('P(a_g|s) = 1−ε + ε/m',{'P(a_g|s)':'behavior probability of the unique greedy action at state s','a_g':'unique greedy action','s':'current state','ε':'probability of uniform exploratory branch','m':'number of available actions'},{'P,ε,m':'dimensionless','s,a_g':'state/action labels'},['Unique greedy action; exploration samples all m actions uniformly.'])])
save()
add(906,'reach-grasp-sequence','Reaching is not the whole grasping task','In the application diagram, the controller receives current gripper location and target location. Which qualification is necessary?',[
 ('Reaching a feasible target and successfully grasping an object are distinct stages; arbitrary unreachable targets are not guaranteed.','This preserves the diagram’s sequence without promising impossible reach or grasp.'),
 ('Any numerical 3D target is reachable because Q-learning can ignore robot joint limits.','Learning does not remove mechanical or task constraints.'),
 ('Matching gripper and target positions alone proves a stable object grasp.','Contact, closure and object mechanics require additional conditions.'),
 ('The target position is always the reward scalar itself rather than an input to the task.','A goal location and numerical reward are different quantities.')],
 'The slide draws reaching followed by closing the gripper. That schematic does not prove every target is feasible or that the later FetchReach task includes grasping.',typ='diagram',difficulty='medium',conflict='The slide says any arbitrary target and depicts a grasp stage; feasibility and the later reaching-only task require explicit limits.')
add(907,'gym-api','Gymnasium’s responsibility','Which description correctly separates the tools used in the application?',[
 ('Gymnasium provides a standard environment interaction API; the learning loop still implements the agent’s algorithm.','Environment access does not itself train the Q table.'),
 ('Calling gym.make automatically completes Q-learning training before returning.','make constructs the environment, not a trained agent.'),
 ('Gymnasium replaces all physics with a supervised table of correct actions.','The environment can use physics simulation and evaluative rewards.'),
 ('render updates the Q table while step only draws a picture.','step advances interaction; rendering is for visualization.')],
 'Standard methods such as reset and step support experiments, while the supplied code implements learning.')
add(908,'physics-role','MuJoCo and simulation scope','What role does MuJoCo serve in the lecture’s robotics example?',[
 ('It simulates physical dynamics and interactions such as contact, supporting testing before hardware deployment.','This is the physics-engine role.'),
 ('It replaces exploration with exact correct-action labels for every target.','A physics engine does not provide a supervised optimal-action oracle.'),
 ('It guarantees that a policy trained in simulation is safe on every real robot.','Simulation-to-real transfer still requires validation.'),
 ('It is only the plotting library used to draw the reward curve.','matplotlib draws the curve; MuJoCo simulates the environment.')],
 'The source’s manipulation, navigation and humanoid examples illustrate simulation scope, not guaranteed real-world transfer.',typ='scenario')
add(909,'dof-action-dimension','Robot joints versus action coordinates','The example has a seven-degree-of-freedom robot and a four-component action vector. Why is this not a contradiction?',[
 ('The policy issues task-space position increments plus a gripper channel, not one independent command for every arm joint.','Robot joint count and high-level action dimension can differ.'),
 ('Seven joint degrees of freedom require every policy action to have exactly seven entries.','Control interfaces can expose lower-dimensional task-space commands.'),
 ('The four-component input proves that the robot physically has only four joints.','Input representation does not determine the mechanical joint count.'),
 ('The extra three joints must be removed from the simulator before each step.','No such removal follows from the interface.')],
 'The source uses [dx,dy,dz,gripper] as a high-level interface to the robot; the FetchReach gripper channel is blocked.',difficulty='medium')
add(909,'dense-reward-number','Negative Euclidean goal distance','In an added geometry example, desired minus achieved goal is (0.03,0.04,0) metres. What is the dense reward r = −‖error‖₂?',[
 ('−0.05.','The Euclidean norm is √(0.03²+0.04²)=0.05.'),('−0.07.','This uses the sum of absolute coordinate errors instead of Euclidean norm.'),('−0.0025.','This is negative squared distance, without the square root.'),('+0.05.','This reverses the reward sign.')],
 'Closer is better because a smaller nonnegative distance produces a larger, less negative reward.',typ='numerical',steps=['Squared distance = 0.0009 + 0.0016 = 0.0025 m².','Distance = 0.05 m.','Under the stated numerical reward convention, reward = −0.05.'],formulas=[formula('r = −‖g−p‖₂',{'r':'dense numerical reward defined as negative distance','g':'desired Cartesian goal vector','p':'achieved Cartesian goal vector','‖·‖₂':'Euclidean norm'},{'g,p':'metres','r':'reward units numerically equal to negative distance in metres'},['Source reward convention; no extra shaping coefficient.'])])
add(909,'reward-zero','Nonpositive is not strictly negative','Under r = −‖desired_goal−achieved_goal‖₂, which statement is correct?',[
 ('Reward is zero at exact coincidence and negative for nonzero distance.','The norm is nonnegative and vanishes only at zero error.'),
 ('Reward is strictly negative even when the two positions are identical.','The norm of the zero vector is zero.'),
 ('Reward is positive whenever the gripper is closer than one metre.','The sign is negative for every positive distance.'),
 ('Reward equals the sum of signed coordinate errors, so cancellation can make it zero away from the goal.','The Euclidean norm does not allow signed-coordinate cancellation.')],
 'The source’s “always negative” wording should be read as nonpositive for the displayed negative-distance function.',conflict='Page 909 calls the dense reward always negative, although exact coincidence gives zero.')
add(910,'registration-construction','Import, registration and environment construction','In the shown setup, which operation constructs the selected FetchReachDense-v4 environment?',[
 ('gym.make("FetchReachDense-v4").','make instantiates the named registered environment.'),
 ('import numpy as np.','This imports numerical array support rather than the robot task.'),
 ('gym.register_envs(gymnasium_robotics) necessarily loads every robot model into a live simulator.','This overstates registration; in the tested version the helper is a no-op.'),
 ('import matplotlib.pyplot as plt.','This supplies plotting functions, not the environment instance.')],
 'Registration makes identifiers available; construction creates the selected environment. The installed-source check records that import registers tasks and the compatibility register_envs helper is a no-op in Gymnasium 1.4.0.',code=True,conflict='Page 910 describes register_envs as loading all robot models rather than distinguishing registration from construction.')
add(909,'notebook-shell','Notebook installation syntax','The slide contains !pip install gymnasium-robotics mujoco matplotlib -q. What execution-context qualification is needed?',[
 ('The leading ! is notebook/IPython shell syntax; it is not an ordinary Python statement in a .py file.','A standalone script needs an explicitly separate installation step.'),
 ('The command is an import statement that only checks whether the three modules already exist.','pip install is installation, not Python import.'),
 ('The -q flag freezes all packages at the versions used to create the slides.','Quiet output does not pin package versions.'),
 ('The command guarantees identical simulation results because all random seeds are set implicitly.','Installation neither fixes random seeds nor guarantees identical versions.')],
 'The source is notebook-oriented and unpinned. Our compatibility pin is explicitly added reproduction context, not silently attributed to this command.',code=True)
add(911,'action-map','Six discrete choices through a continuous interface','What action set does the six-row ACTION_MAP implement?',[
 ('Positive and negative commands along each Cartesian axis, with a zero fourth component.','The six rows are ±x, ±y and ±z with unchanged gripper channel.'),
 ('All combinations of simultaneous ±x, ±y and ±z commands.','Those diagonal combinations are not the six listed rows.'),
 ('One separate command for every joint of the seven-joint arm.','The rows represent task-space directions, not joint-specific commands.'),
 ('Only gripper opening and closing, with all three Cartesian components zero.','The listed rows have nonzero Cartesian entries and zero gripper entry.')],
 'The agent selects a finite subset of vectors accepted by a continuous four-dimensional environment action space.',code=True)
add(911,'normalized-command','Normalized command is not achieved distance','ACTION_MAP includes [1,0,0,0], and BIN_SIZE=0.04. What can be inferred from choosing that action?',[
 ('It issues the positive-x normalized command; achieved motion depends on simulator dynamics and need not be one metre or one bin.','Command normalization and state discretization have different roles.'),
 ('The achieved gripper x coordinate must increase by exactly one metre in one step.','The action value is not a guaranteed physical displacement in metres.'),
 ('The encoded x-state must increase by exactly one bin.','The encoding uses relative error, and realized motion/clipping need not yield that change.'),
 ('BIN_SIZE directly multiplies every action because it appears in ACTION_MAP.','BIN_SIZE is used by get_state, not in the shown action-map entries.')],
 'The environment interprets normalized controls; the bin size only participates in encoding the observed goal error.',difficulty='medium',code=True,conflict='The unit-action description may imply a guaranteed physical displacement, which the normalized interface does not establish.')
add([911,912],'q-shape-size','Table dimensions and storage','For NX=NY=NZ=8 and N_ACTIONS=6, how many state cells and Q values are allocated by np.zeros((NX,NY,NZ,N_ACTIONS))?',[
 ('512 states and 3,072 state-action values.','8³=512, then multiply by 6 actions.'),('24 states and 144 values.','This adds the three axis sizes instead of taking their Cartesian product.'),('512 states and 512 values.','This omits the action axis.'),('4,096 states and 24,576 values.','This mistakenly gives the state four axes of length 8.')],
 'The three grid axes index states; the last axis holds one value per discrete action.',typ='numerical',code=True,steps=['State count = 8×8×8 = 512.','Q entries = 512×6 = 3,072.'])
add(912,'q-memory','Raw Q-array memory','Assume the default Q array has float64 entries, 8 bytes each. What is its raw data storage for shape (8,8,8,6), excluding object metadata?',[
 ('24,576 bytes, or 24 KiB.','3,072 entries × 8 bytes = 24,576 bytes.'),('3,072 bytes.','This counts entries as if each occupied one byte.'),('12,288 bytes.','This assumes 4-byte entries rather than the stated float64.'),('196,608 bytes.','This multiplies by an extra factor of 8 after accounting for the entry size.')],
 'Array dtype determines bytes per entry. ACTION_MAP’s explicit float32 does not change the separately created Q array’s default float64 dtype.',typ='numerical',code=True,steps=['Entries = 8×8×8×6 = 3,072.','Raw bytes = 3,072×8 = 24,576; divide by 1,024 to obtain 24 KiB.'],assumptions=['The stated float64 layout excludes Python/NumPy object overhead.'])
add(912,'relative-error','What get_state encodes','The code begins err = obs["desired_goal"] − obs["achieved_goal"]. What quantity is discretized?',[
 ('The Cartesian goal-error vector, not the absolute gripper position.','Both goal and achieved position enter the difference.'),
 ('Only the desired goal’s absolute position, irrespective of the gripper.','The achieved goal is explicitly subtracted.'),
 ('Only the seven joint angles of the arm.','The code accesses the goal vectors, not joint-angle entries.'),
 ('The scalar immediate reward repeated in all three coordinates.','get_state uses three-dimensional goal error, not reward.')],
 'The source’s position wording is incomplete: it is a relative target-minus-achieved encoding.',code=True,conflict='Page 912 describes the binned quantity as current position, although the literal code bins goal error.')
add(912,'state-bin-computation','Calculating encoded goal error','Use get_state with offset 0.16, BIN_SIZE=0.04, integer conversion and clipping to [0,7]. Desired goal is (0.10,0.20,0.30) and achieved goal is (0.05,0.21,0.28), in metres. Which tuple results?',[
 ('(5,3,4).','Error (0.05,−0.01,0.02) gives scaled values (5.25,3.75,4.5), truncated to integers.'),
 ('(1,0,0).','This approximately bins the raw error while omitting the +0.16 offset.'),
 ('(5,4,5).','This rounds scaled values rather than using the shown integer truncation.'),
 ('(2,4,3).','This reverses the desired-minus-achieved difference.')],
 'The code shifts each error coordinate, scales by the bin size, converts toward zero, then clips. These positive scaled values yield (5,3,4).',typ='numerical',difficulty='medium',code=True,steps=['Error = desired−achieved = (0.05,−0.01,0.02).','(error+0.16)/0.04 = (5.25,3.75,4.5).','Integer conversion gives (5,3,4), already within [0,7].'],assumptions=['Treat the displayed decimal arithmetic ideally; the tested NumPy evaluation gives the same tuple.'])
add(912,'zero-error-bin','Zero goal error is the central bin','What tuple does the shown get_state assign when achieved_goal equals desired_goal exactly?',[
 ('(4,4,4).','Each coordinate becomes (0+0.16)/0.04=4.'),('(0,0,0).','This omits the positive offset before scaling.'),('(7,7,7).','Zero error is not clipped to the upper bound.'),('(3,3,3).','The exact quotient is 4, not 3.')],
 'A zero physical error does not mean a zero array index because the encoding includes an offset.',typ='numerical',code=True,steps=['Each error coordinate is 0.','Shift/scale gives 0.16/0.04=4; clipping leaves it unchanged.'])
add(912,'clipped-aliasing','Clipping and state aliasing','Which limitation follows from the get_state clipping operation?',[
 ('Different out-of-range errors can map to the same boundary index.','Clipping collapses all sufficiently extreme values at each end.'),
 ('Clipping reconstructs each exact continuous error from its index.','Information lost by binning/clipping cannot be recovered that way.'),
 ('The table automatically grows whenever the goal lies outside the grid range.','The allocated shape and clipping bounds remain fixed.'),
 ('Every distinct physical robot state must have a distinct encoded tuple.','Only coarse relative error is retained, so many states can share an index.')],
 'The finite encoding is a lossy abstraction; it trades detail for a manageable table.',code=True)
add(912,'state-sufficiency','A grid tuple is not automatically Markov','Two robot configurations have the same binned goal error but different velocities. Why might their future behavior differ under the same action?',[
 ('The encoder omits variables that can affect dynamics, so identical tuples need not be sufficient Markov states.','The omitted velocity/configuration can affect subsequent motion.'),
 ('A three-integer tuple is mathematically forbidden as a state representation.','Discrete states are valid; the issue is information sufficiency.'),
 ('Q-learning guarantees that omitted physical variables cannot influence transitions.','An algorithm does not remove physical dependence.'),
 ('Binning converts the environment to a deterministic system regardless of hidden variables.','Discretization does not guarantee determinism.')],
 'The code’s compressed state is an approximation. Markov sufficiency must be justified from the task, not inferred from having a Q table.',typ='scenario',difficulty='medium',code=True)
add(912,'reset-return','Reset return values and persistent learning','In obs, _ = env.reset(); s, total = get_state(obs), 0, what is reset at each episode while Q remains outside the loop?',[
 ('The environment/starting observation, encoded state and episode reward total are reset; the Q table retains earlier updates.','This matches the variable placement.'),
 ('The Q table and all learning parameters are recreated by this assignment.','The statement does not assign Q, alpha or gamma.'),
 ('Only the plotted figure is reset; the environment state is unchanged.','env.reset explicitly initializes the environment episode.'),
 ('The underscore stores the chosen next action, replacing the policy.','The second reset return is auxiliary information, not an action.')],
 'Environment reset and learner-memory reset are separate operations.',code=True)
add(913,'epsilon-code-trace','Tie-breaking and epsilon branch','Initially Q[s] contains six zeros. In the shown code, ε=0.5 and np.random.rand() returns 0.7. Which action index is selected?',[
 ('0, because the greedy branch uses np.argmax and returns the first maximal index.','0.7 is not less than 0.5, and all six entries tie.'),
 ('A uniformly random index, because every tie forces the random branch.','The branch is selected by the random comparison, not by a tie test.'),
 ('5, because argmax returns the final tied maximum.','NumPy argmax returns the first maximal index.'),
 ('0.7, because the random draw is used directly as the action index.','The draw only determines which branch is taken.')],
 'The action selection is not random tie-breaking on the greedy branch; zero initialization initially favors index 0 when that branch is used.',typ='algorithm-trace',difficulty='medium',code=True,steps=['Compare 0.7<0.5: false, so use argmax.','All entries are equal; np.argmax returns index 0.'])
add(913,'negative-greedy','Greedy choice among negative values','For Q[s]=[−2,−3,−1,−4,−5,−6], what index does the greedy branch np.argmax(Q[s]) return?',[
 ('2.','−1 is the largest value, at zero-based index 2.'),('5.','−6 is the minimum, not the maximum.'),('0.','Index 0 is chosen only if it maximizes the vector or wins a tie.'),('−1.','argmax returns an index, not the maximum value itself.')],
 'With negative rewards, less negative estimated return is preferable under maximization.',code=True)
add(913,'step-api','Five outputs of step','Which unpacking matches the modern Gymnasium step call shown in the lecture?',[
 ('obs, reward, terminated, truncated, info.','This is the five-value environment-step interface.'),
 ('action, Q, alpha, gamma, epsilon.','These are agent-side quantities, not step outputs.'),
 ('obs, reward, done only.','This omits the separate termination/truncation signals and info.'),
 ('reward, obs, truncated, terminated, action.','This swaps output order and replaces info with an action.')],
 'The observation and reward are followed by two distinct stopping indicators and auxiliary information.',code=True)
add(913,'termination-semantics','Terminated does not mean won','Which statement correctly interprets termination flags for the lecture’s example?',[
 ('A true terminal state is task-defined and need not mean success; default FetchReach instead reaches its time-limit truncation without success termination.','This distinguishes general semantics from the tested continuing task.'),
 ('terminated is true whenever the reward is negative.','Reward sign does not define termination.'),
 ('truncated proves that the gripper successfully grasped an object.','The task is reaching and truncation is a collection limit, not grasp success.'),
 ('terminated and truncated are aliases that always carry identical values.','They represent distinct reasons for ending interaction.')],
 'The source’s “won” explanation is too narrow. Installed FetchReach code and 5,000 executed segments produced zero true terminations and 5,000 time-limit truncations.',difficulty='medium',code=True,conflict='Page 913 equates terminated with winning, but FetchReach is continuing and does not terminate on goal success.')
add(914,'first-negative-update','First update from a zero table','Using the source α=0.1 and γ=0.95, old Q(s,a)=0, reward=−0.1 and all next-state Q values zero, what is the updated Q(s,a)?',[
 ('−0.01.','0 + 0.1(−0.1+0−0)=−0.01.'),('−0.1.','This ignores the learning rate and replaces Q with the target.'),('0.01.','This reverses the reward sign.'),('−0.095.','This discounts the immediate reward rather than applying the shown update.')],
 'Only the chosen state-action entry is moved toward the negative target.',typ='numerical',code=True,steps=['Target = −0.1 + 0.95×0 = −0.1.','New Q = 0 + 0.1×(−0.1−0) = −0.01.'],formulas=[TD])
add(914,'negative-bootstrap-update','Update with a negative continuation estimate','With old Q=−0.01, reward=−0.05, maximum next Q=−0.02, α=0.1 and γ=0.95, what is new Q?',[
 ('−0.0159.','Target −0.069 minus old −0.01 gives error −0.059 and correction −0.0059.'),('−0.0169.','This adds 0.1 times the target without subtracting the old estimate.'),('−0.069.','This replaces the estimate by the target, equivalent to α=1.'),('−0.0041.','This reverses the TD-error sign.')],
 'Subtracting a negative old estimate matters: the error is −0.069−(−0.01)=−0.059.',typ='numerical',difficulty='medium',code=True,steps=['Target = −0.05 + 0.95×(−0.02) = −0.069.','Error = −0.069−(−0.01) = −0.059.','New Q = −0.01 + 0.1×(−0.059) = −0.0159.'],formulas=[TD])
add(914,'transition-order','State advancement after the update','Why does the code compute s_next, update Q[s][a], and only then assign s = s_next?',[
 ('The update must be written to the state-action pair that produced the transition before advancing the current-state variable.','The old s identifies the entry being learned from this transition.'),
 ('The assignment s=s_next must happen first so that the previous state is deliberately forgotten before updating.','That would target the wrong state entry unless the old state were saved separately.'),
 ('Every transition should update all state rows equally, so the order is irrelevant.','The shown sampled update changes only the selected entry.'),
 ('s_next is the reward and must overwrite the cumulative total.','The successor state and reward are distinct values.')],
 'State bookkeeping is part of the algorithm: update the source state-action entry, then move to the successor.',typ='algorithm-trace',difficulty='medium',code=True,steps=['Encode the returned observation as s_next.','Update the old Q[s][a] using reward and successor values.','Advance s to s_next for the next decision.'])
add(914,'terminal-bootstrap','True terminal update versus truncation','As an explicit adaptation to a genuinely terminal transition, old Q=2, α=0.5 and reward=1. A stored successor estimate happens to be 10 and γ=0.9. What should the update use for the terminal continuation?',[
 ('Zero continuation, giving new Q=1.5.','A true terminal state has no future task return.'),
 ('Continuation 10, giving new Q=6.0.','This wrongly bootstraps beyond a true terminal transition.'),
 ('Continuation 1, giving new Q=1.95.','The immediate reward is not an extra successor-value estimate.'),
 ('Skip the entire update and leave Q=2.','The terminal reward still provides a valid learning target.')],
 'For true termination, target is reward alone. For an external time-limit truncation of continuing FetchReach, bootstrapping remains appropriate. The source code does not distinguish these cases in its update.',typ='numerical',difficulty='medium',code=True,steps=['True terminal continuation = 0, so target=1.','New Q = 2 + 0.5(1−2) = 1.5.'],assumptions=['This explicitly added example is a true task terminal state, not the source task’s time-limit truncation.'],formulas=[formula('Q_new = Q_old + α(r−Q_old)',{'Q_new':'updated terminal-transition action-value estimate','Q_old':'previous estimate','α':'learning rate','r':'observed terminal reward'},{'Q_new,Q_old,r':'reward units','α':'dimensionless'},['True task termination; no future return.'])],conflict='The source update bootstraps unconditionally before checking both terminated and truncated.')
add([914,915],'logged-total','Undiscounted logged total versus learned return','The code uses total = total + r, while Q updates contain γ. What is stored in rewards after each episode?',[
 ('The undiscounted sum of rewards collected in that segment.','No powers of gamma appear in the total accumulation.'),
 ('The discounted Q target for the final transition only.','total accumulates every reward rather than only the last target.'),
 ('The maximum Q value in the final state.','The code appends total, not a table maximum.'),
 ('The mean Euclidean distance divided by the number of actions.','Neither averaging nor division by action count occurs.')],
 'The plotted training statistic and the discounted value estimate are related but not identical quantities.',difficulty='medium',code=True)
add(915,'epsilon-first-decay','One exploration-rate decay','Starting from ε=0.5, what value follows one completed episode’s update ε=max(0.05, ε×0.998)?',[
 ('0.499.','0.5×0.998=0.499, which exceeds the floor.'),('0.05.','The floor is a lower bound, not a value selected immediately.'),('0.998.','This confuses the multiplier with the updated epsilon.'),('0.501.','Decay decreases rather than increases epsilon.')],
 'The multiplicative schedule gradually reduces exploration until the floor becomes active.',typ='numerical',code=True,steps=['Multiply: 0.5×0.998=0.499.','Take max(0.05,0.499)=0.499.'])
add(915,'epsilon-floor','When the exploration floor first activates','For ε_n=max(0.05,0.5×0.998^n), with n completed episode updates, when is ε_n first exactly 0.05 due to the floor?',[
 ('At n=1,151.','Solve 0.998^n≤0.1 and take the first integer satisfying it.'),('At n=1,150.','The unfloored value is still slightly above 0.05 at this update.'),('At n=500.','The shown value is still approximately 0.184 then.'),('Never, because the multiplicative term is positive for all finite n.','A positive term can fall below the positive floor.')],
 'Taking logarithms gives n≥ln(0.1)/ln(0.998)≈1150.14, so the first integer update is 1,151.',typ='numerical',difficulty='medium',code=True,steps=['Require 0.5×0.998^n≤0.05, or 0.998^n≤0.1.','Because ln(0.998)<0, n≥ln(0.1)/ln(0.998)≈1150.14.','Round upward to the first integer: 1,151.'],formulas=[formula('n_floor = ceil(ln(ε_min/ε_0)/ln(d))',{'n_floor':'first completed update count at which the floor is active','ceil':'least integer not below the argument','ln':'natural logarithm','ε_min':'positive exploration floor','ε_0':'initial exploration probability','d':'multiplicative decay factor'},{'n_floor,ε_min,ε_0,d':'dimensionless'},['0<ε_min<ε_0 and 0<d<1; update is max(ε_min, previous ε times d).'])])
add(915,'logging-window','Logging cadence and averaging window','With ep starting at zero, what does if (ep+1)%500==0 followed by np.mean(rewards[-100:]) report?',[
 ('Every 500 completed episodes, the mean total reward of the latest 100 completed episodes.','The print cadence and averaging window are separate sizes.'),
 ('Every 100 episodes, the mean of the latest 500 rewards.','This swaps the cadence and window.'),
 ('At ep=0, the mean of all 5,000 future episodes.','The condition is false at ep=0 and future rewards are unavailable.'),
 ('Every 500 environment steps, the maximum immediate reward seen so far.','ep counts episodes, mean is not max, and rewards stores episode totals.')],
 'The first print happens when ep=499, after 500 episodes; the statistic uses the trailing 100 totals.',code=True)
add(915,'printed-trend','Reading the printed checkpoint table','The source prints average totals −6.86 at episode 1,000 and −7.41 at episode 1,500. What does this show?',[
 ('The displayed training statistic temporarily worsens; the sequence is not monotonically improving.','More negative return is worse under this maximization objective.'),
 ('The later value is necessarily better because its magnitude is larger.','For negative reward maximization, larger magnitude here is worse.'),
 ('The values prove that ε increased between those checkpoints.','The displayed schedule decreases to its floor.'),
 ('The table proves a coding error because learning curves cannot fluctuate.','Stochastic exploratory learning can fluctuate without establishing a bug.')],
 'An overall favorable trend can contain worse checkpoints. The printed run is not evidence of monotonic improvement.',typ='diagram',conflict='The printed trace can be overread as monotonic improvement, but the actual 1000-to-1500 interval worsens.')
add([912,913,915],'reproduction-seeds','Unseeded output is not an exact promise','The source omits fixed seeds for NumPy exploration and environment resets. What is a defensible expectation for another run?',[
 ('Exact reward checkpoints may differ even with the same nominal algorithm; reproducible comparison needs explicit seed/version context.','Random choices and environment sampling affect trajectories.'),
 ('All ten printed reward means must match because the loop has exactly 5,000 episodes.','A fixed loop length does not fix random transitions or actions.'),
 ('The epsilon checkpoints must become random solely because rewards are random.','The specified epsilon schedule depends on completed episode count, not reward.'),
 ('Different results prove that Q-learning is off-policy only in the original run.','Off-policy classification is not determined by score matching.')],
 'The deterministic epsilon schedule can reproduce while stochastic reward means differ. The author run records versions and explicitly does not claim an identical trace.',difficulty='medium',code=True,conflict='The source displays one unseeded trace; it is not a guaranteed output of every execution.',conflict_pages=[915])
add(916,'moving-average-length','Valid convolution length','There are 5,000 episode totals. How many values does np.convolve(rewards, np.ones(50)/50, mode="valid") return?',[
 ('4,951.','5,000−50+1 complete windows fit.'),('5,000.','This corresponds to length-preserving padding, not valid mode here.'),('4,950.','This omits the final complete window.'),('5,049.','This is the full convolution length, not valid.')],
 'Valid mode includes only positions where the entire 50-value kernel overlaps the data.',typ='numerical',code=True,steps=['Count full windows: N−W+1.','5,000−50+1=4,951.'],formulas=[formula('N_valid = N−W+1',{'N_valid':'number of complete moving-average windows','N':'number of episode totals','W':'moving-average window length'},{'N_valid,N,W':'counts'},['N≥W; one-dimensional valid convolution.'])])
add(916,'moving-average-alignment','What plotted index zero represents','With plt.plot(smoothed) and the source’s 50-episode valid average, what does the first plotted x index represent?',[
 ('The average of episode totals 1 through 50, plotted at implicit index 0.','No explicit episode-end x coordinates are supplied.'),
 ('Only the reward from episode 1, because the first convolution value uses one observation.','Valid mode uses a full window.'),
 ('Exactly episode 50 on the x axis, because the axis label automatically shifts indices.','An axis label does not change numeric x coordinates.'),
 ('The average of episodes 0 through 5,000, because convolution uses all data at every point.','The kernel has only 50 entries.')],
 'The x label says Episode, but implicit indices are window indices. To place values at window-end episodes, explicit x coordinates would be needed.',difficulty='medium',code=True)
add(916,'curve-inference','What the displayed curve establishes','The source curve rises overall from roughly −9 toward −3 or −4, with fluctuations. Which conclusion is supported?',[
 ('The displayed smoothed training totals improve overall, but the graph alone does not prove zero error or optimal-policy convergence.','This is bounded to what the curve shows.'),
 ('The graph proves every action at every state has its exact optimal Q value.','A performance curve cannot establish full-table correctness.'),
 ('The final reward is zero because the title contains Q-learning.','The displayed values remain negative.'),
 ('A rising training curve guarantees successful grasping on physical hardware.','The task, metric and simulation do not support that conclusion.')],
 'The plotted statistic is smoothed training return under a still-exploratory behavior policy, not a mathematical convergence or real-world grasp certificate.',typ='diagram',difficulty='medium',conflict='The source’s near-zero/convergence interpretation is stronger than its visibly negative, fluctuating plot.')
add(917,'larger-grid-cost','Increasing all three grid axes','If each grid dimension changes from 8 to 12 and the six actions remain, how many Q entries are allocated and by what factor does this grow?',[
 ('10,368 entries, a factor of 3.375.','12³×6=10,368 and (12/8)³=3.375.'),('4,608 entries, a factor of 1.5.','This scales only one axis rather than all three.'),('6,912 entries, a factor of 2.25.','This accounts for only two scaled axes.'),('20,736 entries, a factor of 6.75.','This adds an unsupported doubling of the action dimension.')],
 'Tabular storage grows with the Cartesian product of all state-axis sizes and the action count.',typ='numerical',difficulty='medium',code=True,steps=['New state cells = 12³ = 1,728.','New Q entries = 1,728×6 = 10,368.','Growth = 10,368/3,072 = 3.375.'])
add([912,917],'hardcoded-bounds','Changing shape does not change the encoder','A user changes NX=NY=NZ from 8 to 12 but leaves get_state’s np.clip(...,0,7) unchanged. What happens?',[
 ('The larger table is allocated, but the encoder still never returns axis indices 8 through 11.','Hard-coded clipping limits remain 0 through 7.'),
 ('np.clip automatically reads Q.shape and changes its upper bound to 11.','The explicit literal bound does not consult Q.'),
 ('The encoder returns indices through 12 because NX is now 12.','The function’s shown clipping expression does not use NX.'),
 ('The code must immediately overflow because every old index is invalid in the larger table.','Old indices 0 through 7 remain valid in a size-12 axis.')],
 'Grid resolution changes require coordinated updates to table shape and encoder bounds; merely enlarging Q leaves added cells inaccessible.',typ='scenario',difficulty='medium',code=True,conflict='Page 917 suggests a larger grid without addressing the shown encoder’s hard-coded upper bound 7.',conflict_pages=[917])
add([912,917],'bin-size-range','Smaller bins and physical range','If the encoder retains eight bins per axis and offset 0.16 but BIN_SIZE is reduced from 0.04 to 0.02, what must be reconsidered?',[
 ('The representable error intervals and saturation thresholds change; finer bins do not automatically preserve the previous physical range.','Bin count, width, offset and clipping bounds jointly define the encoding.'),
 ('Only array dtype changes; every physical error maps to the same index as before.','Dividing by a different bin size changes indices.'),
 ('The robot’s physical workspace doubles because every bin is smaller.','An encoding parameter does not enlarge mechanical reach.'),
 ('The six action vectors are automatically halved by this assignment.','The shown ACTION_MAP is defined independently of BIN_SIZE.')],
 'Finer discretization is not a free resolution improvement: physical coverage, clipping and data needs must be considered together.',typ='scenario',difficulty='medium',code=True,conflict='The smaller-bin extension omits coordinated range/offset/bound adjustments.',conflict_pages=[917])
add(917,'deep-rl-scope','What replacing a table with a network changes','Which statement is a defensible version of the slide’s deep-RL extension?',[
 ('A network can approximate values without explicitly storing every grid cell, but sample demands, approximation error and stability still matter.','Function approximation changes representation, not every learning difficulty.'),
 ('A neural network eliminates the need for state inputs or reward feedback.','It still needs inputs and a learning signal.'),
 ('Replacing Q with a network guarantees convergence for every environment and hyperparameter choice.','No such universal guarantee follows.'),
 ('Deep RL must allocate a separate output neuron for every possible continuous state.','Function approximation is not literal state enumeration.')],
 'Avoiding explicit tabulation can improve representational scaling without eliminating all dimensionality and learning challenges.',difficulty='medium',conflict='The source suggests deep RL bypasses dimensionality problems without stating remaining approximation and learning limitations.')
add([906,909,917],'gripper-extension','Making a real grasping extension','Why is changing only ACTION_MAP’s fourth component insufficient to turn the shown FetchReach task into grasping?',[
 ('FetchReach ignores the gripper command and lacks a grasping objective; a suitable task, object interaction and effective gripper control are needed.','The environment/task must support the intended behavior.'),
 ('The fourth component must be 7 because the robot has seven degrees of freedom.','Joint count does not determine the normalized gripper command value.'),
 ('Any nonzero fourth component automatically changes the environment ID to a pick-and-place task.','Action values do not replace the registered task.'),
 ('A negative reaching reward already proves the object has been grasped.','Goal distance does not certify grasping.')],
 'The source’s proposed gripper extension is conceptual. The actual blocked-gripper reaching environment cannot acquire grasping through an action-array edit alone.',typ='scenario',difficulty='medium',code=True,conflict='Pages 909 and 917 imply an effective gripper action in FetchReach; its fourth channel is ignored.',conflict_pages=[909,917])
add([911,912,913,914],'end-to-end-trace','One complete encoded transition','In an explicitly supplied trace, current encoded state is (4,4,4), all Q values are zero, ε=0.5 and the random draw is 0.7. The selected step returns reward −0.1 and goal error (−0.03,0,0). What are the updated old entry and next encoded state?',[
 ('Q[(4,4,4)][0]=−0.01, then s=(3,4,4).','The greedy tie selects index 0; the old entry updates before the state advances.'),
 ('Q[(3,4,4)][0]=−0.01, then s=(3,4,4).','This writes the update to the successor entry rather than the old state-action pair.'),
 ('Q[(4,4,4)][5]=−0.1, then s=(4,4,4).','This uses the wrong tie index, ignores alpha and fails to encode the returned error.'),
 ('Q[(4,4,4)][0]=+0.01, then s=(5,4,4).','This reverses both the reward sign and the x-error direction.')],
 'Follow the code in order: choose with current values, step, encode the successor, update the old pair and advance state.',typ='algorithm-trace',difficulty='medium',code=True,steps=['0.7≥0.5 chooses argmax; tied zeros give action index 0, the +x command.','Next x index is int((−0.03+0.16)/0.04)=int(3.25)=3; y and z indices are 4.','Old entry becomes 0+0.1(−0.1+0.95×0−0)=−0.01.','Only after this update set s=(3,4,4).'],assumptions=['The returned reward and goal error are supplied observations for this trace, not a claim that +x always achieves a fixed displacement.'],formulas=[TD])
add([913,915],'persistent-exploration','Exploration does not vanish at the floor','After ε reaches 0.05, with one unique greedy action among six and uniform random exploration, what is the probability of choosing a non-greedy action on a decision?',[
 ('1/24, approximately 0.04167.','The random branch occurs with probability 0.05 and selects one of five non-greedy actions with probability 5/6.'),
 ('0, because the floor stops exploration entirely.','A positive epsilon retains random action selection.'),
 ('0.05 exactly.','The exploratory branch can also select the greedy action.'),
 ('5/6.','This ignores that the random branch is used only 5% of the time.')],
 'The floor creates persistent exploratory behavior, and branch probability differs from actual non-greedy probability.',typ='numerical',difficulty='medium',code=True,steps=['Random-branch probability is 0.05.','Conditional non-greedy probability is 5/6.','Multiply: 0.05×5/6=1/24≈0.04167.'])
add([901,912,913],'estimate-not-optimal','Greedy with an estimate versus greedy with Q*','Why does selecting argmax(Q[s]) from the current table not by itself prove the selected action is optimal?',[
 ('The current Q array is an estimate learned from limited data, whereas the optimal-policy result assumes true Q*.','The mathematical premise differs from an intermediate training table.'),
 ('argmax always selects the minimum when Q values are negative.','argmax still selects the largest number.'),
 ('A greedy policy cannot be defined on a finite action set.','Finite action sets make the maximum straightforward.'),
 ('Any action selected from an estimate is necessarily worse than every random action.','An estimate may be useful or accurate; absence of proof is not proof of inferiority.')],
 'Do not substitute an unverified current estimate for the true optimal value function in a theorem about greedy optimality.',difficulty='medium',code=True)
add([909,912,914],'optimistic-zero','Zero initialization with nonpositive reward','With nonpositive returns, why can an untried zero-initialized action appear preferable to an action already updated to a negative Q value?',[
 ('Zero can be optimistic relative to the learned negative estimate, so the untried action may win the greedy comparison.','Initialization affects action preferences before sufficient data arrive.'),
 ('Zero proves that the untried action will reach the goal with certainty.','An initial estimate is not observed performance.'),
 ('Negative rewards make the maximum operator prefer the most negative entry.','It prefers the greatest, not the smallest, entry.'),
 ('An action’s Q value cannot become negative when initialized at zero.','The source’s update with negative reward immediately gives negative values.')],
 'Initialization and learning interact with exploitation, but optimism alone does not establish optimality or sufficient exploration.',typ='scenario',difficulty='medium',code=True)
save()
# Author quality pass before the first freeze: parallel, instruction-relevant distractors.
def replace(tag,prefix,text,explanation):
 q=next(q for q in b.questions if tag in q['tags']);o=next(o for o in q['options'] if o['text'].startswith(prefix));o['text']=text;q['solution']['optionExplanations'][o['id']]=explanation
replace('feedback-paradigms','Supervised learning cannot','Supervised and reinforcement learning both require the correct action label, but only RL delays that label.','RL reward evaluates behavior and need not reveal the correct action label.')
replace('teacher-critic','A teacher and critic differ only','A critic provides the correct action after execution, while a teacher provides that same action before execution.','Timing alone is not the distinction: the critic evaluates rather than prescribing the correct action.')
replace('agent-boundary','A motor command','The selected movement is the agent, while the controller’s learned decision rule is the environment.','A movement is an action; the controller and its policy belong to the decision-making agent.')
replace('agent-boundary','The reward number','The environment consists only of the reward rule and excludes the maze’s state transitions.','Both transitions and feedback form part of the modeled interaction system.')
replace('action-space','Actions must always','A steering angle becomes a discrete action set simply by normalizing it to [−1,1].','Normalization changes the numeric range, not a continuous set into finitely listed choices.')
replace('state-observation','States are actions','The observation is always a sufficient Markov state, even if velocity and hidden obstacles are omitted.','A partial observation need not contain all information needed to predict future outcomes.')
replace('time-index','Choose s_(t+1)','Choose a_t from o_t, then receive r_t for that new transition while retaining o_t as the successor observation.','The source labels the newly returned feedback r_(t+1) and o_(t+1).')
replace('time-index','Choose a_(t+1)','Receive o_(t+1), choose a_t using it, and only then let the environment produce s_(t+1).','This makes the successor observation available before its state-producing transition.')
replace('policy-types','A deterministic policy returns','A deterministic policy gives transition probabilities P(s_next|s,a), while a stochastic policy gives action probabilities.','The deterministic policy selects an action; transition probabilities describe the environment.')
replace('coverage-off-policy','Off-policy learning makes','Off-policy learning requires no estimate for an unvisited pair because its value is defined to equal the visited pair’s value.','Different actions can have different outcomes; off-policy status does not equate their values.')
replace('bellman-decomposition','Replace all future','Use only the largest individual future reward as the tail instead of the discounted cumulative return.','The objective accumulates rewards; a maximum single reward is a different criterion.')
replace('exploration-tradeoff','Because the current Q table','Because exploration means repeatedly selecting the current maximum Q value without testing alternatives.','That describes greedy exploitation, not the reason for a deliberately non-greedy choice.')
replace('exploration-tradeoff','Because selecting a non-greedy','Because an unvisited action’s zero initial estimate is already a measured guarantee of superior return.','Initialization is not an observation; exploration tests uncertainty rather than converting it into certainty.')
replace('gym-api','Gymnasium replaces','Gymnasium supplies the Q-learning update rule, while the user must implement reset and step for every provided environment.','The provided environments expose reset/step; the source code supplies the learning update.')
replace('gym-api','render updates','Gymnasium and MuJoCo are interchangeable names for the same layer, so either one alone supplies both the task API and this Q-learning loop.','The API, physics engine and agent learning code have distinct responsibilities.')
replace('physics-role','It replaces exploration','It is the optimizer that directly fits the Q table from the logged reward curve.','The Python update fits the table; MuJoCo supplies simulated dynamics.')
replace('physics-role','It is only','It provides only kinematic forward-position calculations, without contact or dynamic interaction.','The slide emphasizes physical dynamics and interactions beyond kinematics.')
replace('dof-action-dimension','The extra three joints','The action vector must contain four selected joint angles, so its Cartesian labels can be ignored.','The shown interface is explicitly task-space displacement commands plus gripper, not four joint angles.')
replace('registration-construction','import numpy','import gymnasium_robotics alone, without any gym.make call.','Import registers tasks but does not create this particular environment instance for the variable env.')
replace('registration-construction','import matplotlib','env.reset() creates and registers the named task even when env has never been assigned.','reset operates on an existing environment instance; it cannot use an undefined env variable.')
replace('notebook-shell','The command guarantees','The -q flag makes installation a dry run that leaves the environment unchanged.','The quiet flag suppresses output; it does not turn installation into a dry run.')
replace('state-sufficiency','A three-integer','Any averaging over repeated visits guarantees that omitted velocities become irrelevant to future transitions.','Averaging observed outcomes does not establish state sufficiency or remove hidden-state dependence.')
replace('reset-return','Only the plotted','The environment is reset, but total keeps the sum from all previous episodes.','The shown assignment explicitly sets total to zero each episode.')
replace('reset-return','The underscore','The underscore receives the reward of the first action, which must be added to total.','reset returns auxiliary information, not the reward of an action transition.')
replace('step-api','action, Q','obs, reward, done, info.','This is the older four-output convention, not the five-output API shown.')
replace('step-api','obs, reward, done only','obs, reward, terminated, truncated.','This omits the fifth auxiliary info value.')
replace('step-api','reward, obs','obs, reward, truncated, terminated, info.','This reverses the positions of the two distinct Boolean outputs.')
replace('termination-semantics','terminated is true','terminated includes the external 50-step collection limit, while truncated is reserved only for numerical simulation failures.','The default external limit sets truncated, not true task termination.')
replace('termination-semantics','truncated proves','truncated means the observation vector was shortened, not that the trajectory segment ended.','Truncation concerns the interaction boundary, not array length.')
replace('printed-trend','The values prove','The more negative later average means the average goal-distance total became smaller.','Negative-distance return becomes more negative when the accumulated distance becomes larger, not smaller.')
replace('reproduction-seeds','Different results prove','Fixing only the array shape and number of episodes reproduces the exact random exploration sequence.','The sequence also depends on random generator state; shape and count do not fix it.')
replace('deep-rl-scope','A neural network eliminates','A network removes the need to distinguish training return from an independent policy evaluation.','Function approximation does not erase the training/evaluation distinction.')
replace('gripper-extension','The fourth component must','Opening the gripper requires shrinking BIN_SIZE, while changing the task and action interface is unnecessary.','State-bin width does not unblock an ignored actuator channel or introduce a grasping objective.')
replace('gripper-extension','A negative reaching reward','Matching achieved_goal to desired_goal already certifies a stable grasp, even without an object-contact reward.','Position coincidence in a reaching task does not certify object contact or grasp stability.')
replace('estimate-not-optimal','A greedy policy cannot','Q[s] contains a transition-probability distribution, so its maximum identifies only the likeliest successor.','The array stores action-value estimates, not next-state probabilities.')
for q in b.questions:
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']]
 if q['type']=='algorithm-trace':
  q['cognitiveSkill']='algorithm'
  if not q['solution']['steps']:q['solution']['steps']=['Initialize the table before episode iteration.','Reset the state for the episode.','Select an action, observe the transition, update its old state-action entry, then advance state.']
 for c in q['citations']:
  p=c['physicalPage'];tag=q['tags'][0]
  suffix='Relevant stated definition and associated explanation.'
  if p==891:c['kind']='table';suffix='Teacher and Critic comparison columns: labeled guidance, evaluation and feedback timing.'
  elif p==897 and tag in ['on-off-policy','coverage-off-policy']:c['kind']='table';suffix='On-policy and Off-policy comparison boxes, including Sarsa, Q-learning and exploration wording.'
  elif p==903:c['kind']='table';suffix='Model-Free Learning and Model-based Learning comparison boxes, model knowledge and algorithm examples.'
  elif p in [898,899,900,901,904]:c['kind']='equation';suffix='Displayed return/value/Bellman/update equations and their adjacent definitions or qualifications.'
  elif p==905:c['kind']='code' if tag=='pseudocode-persistence' else 'equation';suffix='Left Q-learning pseudocode initialization/transition/update lines and right epsilon-greedy probability box.'
  elif p==915 and tag=='printed-trend':c['kind']='table';suffix='Printed training-output table, specifically episode 1000 and 1500 Avg values.'
  elif p==916 and tag=='curve-inference':c['kind']='figure';suffix='Displayed training curve: negative vertical scale, overall rise and local fluctuations.'
  elif 910<=p<=916:c['kind']='code';suffix='Literal Python block and accompanying output/explanation for '+q['subtopic']+'.'
  elif p in [892,906]:c['kind']='figure';suffix='Labeled interaction arrows and application workflow diagram.'
  elif p==909 and tag=='notebook-shell':c['kind']='code';suffix='Notebook !pip install command and package names.'
  c['locator']=f'Lecture 30, physical PDF page {p}, actual printed footer {p-886}: '+suffix
# The summary introduces no new premise; link the appropriate existing concepts.
for tag in ['feedback-paradigms','state-action-values','model-free-based','td-parts','reach-grasp-sequence']:
 q=next(q for q in b.questions if tag in q['tags'])
 q['citations'].append({'slideId':'lectures-p0918','sourceId':'lectures','sourceSha256':SHA,'physicalPage':918,'kind':'statement','locator':'Lecture 30, physical page 918, actual printed footer 32: repeated RL/Q-learning summary','evidenceText':NOTES[918][0],'role':'premise','region':None})
 for cid in q['conceptIds']:b.concepts[cid]['slideIds'].append('lectures-p0918')
# Include recurrence symbols explicitly in the derivation metadata.
q=next(q for q in b.questions if 'bellman-decomposition' in q['tags'])
q['solution']['formulas']=[formula('G_t = r_(t+1) + γ G_(t+1)',{'G_t':'infinite discounted return starting with reward after decision time t','r_(t+1)':'immediate next reward','γ':'discount factor','G_(t+1)':'return beginning with the following reward, with discount exponent reset to zero','t':'current discrete time index'},{'G_t,G_(t+1),r_(t+1)':'reward units','γ,t':'dimensionless'},['Bounded rewards and 0≤γ<1; the same recurrence also applies before a finite-horizon boundary.'])]
save(frozen=True)
packet=R/f'audits/blind-{BATCH}.json';batchpath=R/f'data/question-batches/{BATCH}.json'
manifest={'batchId':BATCH,'authorId':AUTHOR,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'questionCount':len(b.questions),'conceptCount':len(b.concepts),'physicalPages':list(NOTES),'sourceVersions':{'lectures':SHA},'blindPacketPath':str(packet.relative_to(R)),'blindPacketSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'questionHashConvention':'scripts.validate.question_hash; excludes only status and reviewIds','questions':[{'questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q)} for q in b.questions],'independentReviewStillRequired':True}
coverage=[]
for p,(note,excluded) in NOTES.items():
 coverage.append({'physicalPage':p,'printedSlideNumber':str(p-886),'slideId':f'lectures-p{p:04d}','sourceSha256':SHA,'visualInspection':'complete','disposition':'excluded' if excluded else 'drafted-awaiting-independent-review','exclusionReason':excluded,'observedMeaningfulContent':note,'conceptIds':[c['id'] for c in b.concepts.values() if f'lectures-p{p:04d}' in c['slideIds']],'questionIds':[q['id'] for q in b.questions if any(c['physicalPage']==p for c in q['citations'])]})
assert all(row['exclusionReason'] or (row['conceptIds'] and row['questionIds']) for row in coverage)
(R/f'audits/{BATCH}-author-coverage-ledger.json').write_text(json.dumps({'batchId':BATCH,'status':'Author coverage proposal only; independent substantive challenge required.','pageCount':len(coverage),'exclusions':sum(bool(x['exclusionReason']) for x in coverage),'pages':coverage},ensure_ascii=False,indent=2)+'\n')
assert all('correctOptionIds' not in q and 'solution' not in q and all('evidenceText' not in c for c in q['citations']) for q in json.loads(packet.read_text()))
files=[batchpath,packet,R/f'data/inspection-batches/{BATCH}.json',R/f'audits/{BATCH}-author-coverage-ledger.json',R/f'audits/{BATCH}-source-issues.json',R/f'audits/{BATCH}-author-checks.json',R/f'audits/{BATCH}-author-simulation.json',R/f'audits/{BATCH}-initial-runtime-attempt.json',R/f'audits/{BATCH}-author-reproduced-curve.png',R/f'audits/{BATCH}-author-simulation-arrays.npz',Path(__file__),R/'scripts/check_W06_L30_author.py',R/'scripts/reproduce_W06_L30_source.py']
manifest['artifactSha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(R/f'audits/{BATCH}-frozen-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('FROZEN_PACKET_SHA256',manifest['blindPacketSha256'])
