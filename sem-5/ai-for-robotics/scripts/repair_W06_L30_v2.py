#!/usr/bin/env python3
"""Versioned L30 author repairs. Preserve accepted objects and never self-approve."""
import json,copy,hashlib,datetime,sys,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors
from authoring_helpers import DraftBatch,formula,SHA
BATCH='W06-L30';AUTHOR='build_offline_study_interface:L30-author'
path=R/f'data/question-batches/{BATCH}.json';archive=R/'audits/batch-history/W06-L30-v1-before-repairs.json'
if not archive.exists():archive.write_bytes(path.read_bytes())
data=json.loads(archive.read_text());original=copy.deepcopy(data)
summary=json.loads((R/'audits/W06-L30-contracts-review-summary.json').read_text());flagged=set(summary['flaggedQuestionIds']);accepted={q['id']:question_hash(q) for q in data['questions'] if q['id'] not in flagged}
for item in data['questions']:
 if item['id'] in flagged:item.update(version=2,status='draft',reviewIds=[],revisionAuthors=[AUTHOR])
qs={int(q['id'][-3:]):q for q in data['questions']}
def q(n):return qs[n]
def option(n,oid,text,reason):
 next(x for x in q(n)['options'] if x['id']==oid)['text']=text;q(n)['solution']['optionExplanations'][oid]=reason

def why(n,text):
 q(n)['solution']['justification']=text;q(n)['solution']['simpleExplanation']=text
 if q(n).get('conflictResolution'):q(n)['conflictResolution']['basis']=text

def cite(n,p,kind='code',locator='Displayed source code relevant to the qualified statement.'):
 if any(c['physicalPage']==p for c in q(n)['citations']):return
 q(n)['citations'].append({'slideId':f'lectures-p{p:04d}','sourceId':'lectures','sourceSha256':SHA,'physicalPage':p,'kind':kind,'locator':f'Lecture30, physical page{p}, printed footer{p-886}: '+locator,'evidenceText':(R/f'sources/text/lectures/page-{p:04d}.txt').read_text().strip(),'role':'premise','region':None})
 for c in data['concepts']:
  if c['id'] in q(n)['conceptIds'] and f'lectures-p{p:04d}' not in c['slideIds']:c['slideIds'].append(f'lectures-p{p:04d}')

def evidence(n,url,scope,section):
 p=R/'audits/W06-L30-v2-api-evidence.json'
 q(n).setdefault('externalEvidence',[]).append({'url':url,'accessedAt':'2026-10-19T20:03:59+00:00','scope':scope,'savedEvidencePath':str(p.relative_to(R)),'savedEvidenceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'section':section,'relationToLecture':'External API qualification, not claimed printed-slide evidence.'})
# External/implementation evidence is captured before this script runs.
REACH='https://robotics.farama.org/envs/fetch/reach/'
LIMITS='https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/'
option(8,'o1','The external limit creates a natural terminal MDP state even when the continuing-task objective remains unchanged.','A collection wrapper does not by itself change the task’s transition/return definition.')
option(8,'o3','A fixed finite task horizon and an external collection limit require identical terminal treatment in every model.','A horizon that is part of the task differs from a collection cutoff on a continuing task.')
option(8,'o4','The final collected transition should be discarded because the underlying task has no terminal state.','A truncated transition can still supply reward and successor information for learning.')
why(8,'Under the explicitly stated continuing-task premise, a 50-step collection boundary can truncate a trajectory without a natural terminal state. As an external API qualification, FetchReachDense-v4 in Gymnasium1.4.0/Gymnasium-Robotics1.4.2 has this continuing-task behavior; see the linked implementation evidence, not the slide’s episodic wording.')
evidence(8,LIMITS,'Task termination versus external collection cutoff.','timeLimits');evidence(8,REACH,'FetchReachDense-v4 in the recorded package versions.','reachFlags')
q(10).update(stem='In a nonterminal transition the observed reward is 2 and γ=0.9. Estimated next-state values are Q(s_next,A)=4 and Q(s_next,B)=1, but exploration actually selects B next. What are the Q-learning and Sarsa bootstrap targets, respectively?',type='numerical',cognitiveSkill='numerical',difficulty='medium')
option(10,'o1','2.9 and 5.6.','This reverses sampled-action Sarsa and greedy-bootstrap Q-learning targets.')
option(10,'o2','5.6 and 5.6.','This uses the greedy maximum for Sarsa even though the selected next action is B.')
option(10,'o3','2 and 2.','This drops the nonterminal estimated continuation from both targets.')
option(10,'o4','5.6 and 2.9.','Q-learning uses max(4,1); Sarsa uses the selected action value1.')
why(10,'The reward2 is observed, but both continuation values are estimates. Q-learning targets 2+0.9×4=5.6 regardless of the exploratory next action; Sarsa targets 2+0.9×1=2.9 for the selected B. Neither complete bootstrapped target is an observed full return.')
q(10)['solution']['steps']=['The maximum next estimate is4, so the Q-learning target is2+0.9×4=5.6.','The selected next action is B with estimate1, so the Sarsa target is2+0.9×1=2.9.','Distinguish sampled immediate reward from estimated continuation.']
q(10)['assumptions']=['Added arithmetic transition; nonterminal successor; B is the explicitly sampled next behavior action.']
q(10)['solution']['formulas']=[formula('y_Q=r+γ max_b Q(s_next,b); y_S=r+γ Q(s_next,a_next)',{'y_Q':'Q-learning target','y_S':'Sarsa target','r':'observed immediate reward','γ':'discount factor','s_next':'successor state','b':'candidate successor action','a_next':'actual sampled next action','Q':'current estimated action-value function'},{'y_Q,y_S,r,Q':'reward units','γ':'dimensionless','s_next,b,a_next':'state/action labels'},['Nonterminal transition.'])]
cite(10,904,'equation','Q-learning maximum and target update.');cite(10,905,'code','Greedy-bootstrap pseudocode.');cite(10,913,'code','Exploratory next-action selection rule.');cite(10,914,'code','Implemented maximum successor estimate.')
option(12,'o3','7.','This changes the reward −1 to +1, giving2+1+4=7; merely omitting −1 would give6.')
option(17,'o3','The single poor episode establishes a lower expected return than a competitor whose only observed episode was better.','Two individual samples do not determine the policies’ expected values.')
option(17,'o4','Maximizing expected return also establishes that the policy minimizes outcome variance.','Expected-return and risk/variance objectives are distinct.')
option(23,'o1','A mixture proportional to8 and3, because Q-greedy means sampling in proportion to values.','That is a different stochastic action-selection rule, not a greedy maximum.')
option(23,'o2','Choose the action with the smaller Q value to minimize estimated accumulated cost, without changing the stated reward-maximization convention.','Cost minimization reverses the objective without the required sign/model transformation.')
cite(23,899,'equation','Q is expected cumulative return, not immediate reward alone.');cite(23,901,'equation','Greedy action selection by maximizing action value.')
q(25)['difficulty']='easy';q(26)['difficulty']='easy'
option(28,'o1','Finite tabulation and bounded rewards suffice even when some state-action pairs receive only finitely many visits.','Classical convergence also requires sufficient repeated sampling of the relevant pairs.')
option(28,'o3','Repeated visits and a fixed positive step size suffice for the classical exact-convergence result under persistent stochastic rewards.','A fixed positive step size generally retains stochastic fluctuations and does not satisfy the usual square-summability condition.')
option(28,'o4','A schedule with finite total step size suffices because its squared step sizes also have a finite sum.','The classical conditions require an infinite sum of step sizes as well as a finite sum of their squares.')
q(28)['assumptions']=['Discuss the classical finite-state/action discounted tabular theorem with bounded rewards, not an unrestricted function-approximation guarantee.']
why(28,'The classical tabular result requires suitable state/action coverage and learning rates such as Σα=∞ and Σα²<∞ along each updated pair, together with its finite discounted Markov-task assumptions. The fixed α=0.1 demonstration does not establish those hypotheses.')
q(28)['externalEvidence']=[{'url':'https://www.gatsby.ucl.ac.uk/~dayan/papers/cjch.pdf','scope':'Watkins and Dayan tabular Q-learning convergence conditions; not evidence that the example satisfies them.','accessedAt':'2026-10-19','relationToLecture':'Primary theoretical qualification of the slide claim.'}]
option(31,'o2','Closing the fingers after reaching always guarantees stable force closure, regardless of object shape or contacts.','A closure command does not by itself establish stable contact geometry or adequate forces.')
option(31,'o4','A reachable Cartesian goal by itself establishes a collision-free trajectory to that goal.','Endpoint reachability does not establish path feasibility or obstacle avoidance.')
cite(31,909,'statement','The later example is FetchReach, a reaching task.');evidence(31,REACH,'The reach objective is not an object-grasp objective.','reachAction')
why(34,'The source uses [dx,dy,dz,gripper] as a high-level task-space interface, rather than one independent policy coordinate for each arm joint. Action-interface dimension and mechanical degrees of freedom need not match.')
evidence(37,'https://gymnasium.farama.org/api/registry/','Gymnasium1.4.0 register_envs implementation and named-environment construction.','registration')
cite(40,912,'code','get_state uses desired-minus-achieved error and BIN_SIZE.');cite(42,911,'code','ACTION_MAP explicitly requests dtype=np.float32; this is separate from the Q allocation.')
option(44,'o4','(5,4,5).','This uses round-half-up on the ideal scaled values(5.25,3.75,4.5), rather than the shown integer conversion; NumPy nearest-even rounding would instead give(5,4,4).')
option(47,'o1','The tuple is sufficient whenever both configurations have equal instantaneous goal distance, even if velocity changes the next motion.','Equal distance does not guarantee identical conditional transition distributions.')
option(47,'o2','The tuple is sufficient if the robot is deterministic in its full physical state, even when the tuple omits velocity.','Determinism in the full state does not make a partial observation sufficient.')
option(47,'o4','The tuple is sufficient once the Q estimate has been averaged over previous visits, even when the hidden-state mixture depends on history.','A history-dependent hidden-state mixture can still violate the Markov property for the tuple.')
q(52)['stem']='For FetchReachDense-v4 in the explicitly checked Gymnasium1.4.0/Gymnasium-Robotics1.4.2 setup with its default50-step wrapper, which statement correctly qualifies the lecture’s termination wording?'
q(52)['assumptions']=['Use the dated, version-specific external API/implementation evidence linked in this item; do not treat the slide’s “won” gloss as the API definition.']
why(52,'The source’s “won” explanation is too narrow. The linked installed-code audit checks the continuing FetchReachDense-v4 task, its always-false task termination and the default50-step TimeLimit wrapper. The saved5000-segment author run corroborates that setup, with zero terminations and5000 truncations; it is not independent verification or a universal statement about every task.')
evidence(52,REACH,'Tested FetchReachDense-v4 task and default wrapper, not every Gymnasium environment.','reachFlags')
cite(53,912,'code','Numerical hyperparameters alpha0.1 and gamma0.95.')
q(55).update(stem='A transition leaves state S using action a and reaches distinct state T. Before the update Q[S,a]=5 and max_b Q[T,b]=7; r=1, α=0.1 and γ=0.9. Which bookkeeping and update are correct?',type='algorithm-trace',cognitiveSkill='application',difficulty='medium')
option(55,'o1','Assign s=T and update Q[T,a] to5.23 without retaining S.','The numerical target does not justify writing into the successor row.')
option(55,'o2','Update Q[S,a] to7.3 by replacing it directly with the bootstrap target, then set s=T.','7.3 is the target; alpha0.1 moves the old estimate only partway.')
option(55,'o3','Update Q[S,a] to5.23, then set s=T; assigning s=T earlier is also safe only if S was retained separately for the write.','This preserves the transition’s source state-action pair and applies the step size.')
option(55,'o4','Use max_b Q[S,b] instead of the supplied successor maximum because the write is to row S.','The update destination is S, but the continuation estimate comes from T.')
why(55,'The target is1+0.9×7=7.3, so Q[S,a] becomes5+0.1(7.3−5)=5.23. The write belongs to the old source pair; a saved old-state variable permits equivalent ordering, but forgetting S does not.')
q(55)['solution']['steps']=['Keep the old state S or an explicit saved copy.','Compute target1+0.9×7=7.3.','Update the source entry5+0.1×2.3=5.23.','Advance the current-state variable to T.'];q(55)['assumptions']=['Added nonterminal trace with distinct states S and T; the successor maximum is measured before this update.']
q(57)['difficulty']='easy'
option(62,'o1','Seeding NumPy alone fixes both exploration draws and every environment reset, without checking how the environment generates goals.','The environment has its own random-generator state.')
option(62,'o2','Seeding environment resets alone fixes the unseeded NumPy exploration draws as well.','Reset seeding does not automatically set the separate NumPy generator used by the policy.')
option(62,'o3','Using the same NumPy and environment seeds guarantees bit-identical results across arbitrary simulator and package versions.','Version and implementation differences can still affect trajectories.')
option(65,'o2','The last smoothed total is the final instantaneous distance with its sign reversed.','The statistic averages sums over segments; it is not one instantaneous distance.')
option(65,'o3','The curve is an independent greedy-policy evaluation because it was plotted after training.','Plot timing does not change that its data came from the exploratory training loop.')
option(65,'o4','A second run with different exploration and reset seeds must reproduce the same sequence of smoothed totals.','The curve does not establish seed-invariant trajectories or scores.')
cite(65,913,'code','Epsilon-greedy action rule.');cite(65,915,'code','Nonzero epsilon floor and accumulated training statistics.')
q(68).update(stem='The original encoder shifts goal error e by0.16m, uses width0.04m and clips to bins0…7. Design12 uniform bins preserving the nominal interval[−0.16,0.16)m, with clipping outside it. In ideal arithmetic, which width, clipping bounds and indices for e=(−0.16,0,0.16)m are correct?',type='numerical',cognitiveSkill='numerical',difficulty='medium')
option(68,'o1','Width0.04m; clip0…11; indices(0,4,8).','These settings expand the nominal range rather than preserve its0.32m width.')
option(68,'o2','Width0.32/12m; clip0…11; indices(0,6,11).','The total interval is divided into12; the upper endpoint is clipped into the last bin.')
option(68,'o3','Width0.32/12m; clip0…7; indices(0,6,7).','The old upper clip discards the four new indices.')
option(68,'o4','Width0.32/12m with offset0; clip0…11; indices(0,0,6).','This shifts the nominal interval and loses the intended centering.')
why(68,'Preserving the0.32m nominal span requires w=0.32/12m and the same0.16m offset. Ideal scaled coordinates are0,6,12; clipping to0…11 gives0,6,11. Bin0 absorbs the lower tail and bin11 the upper tail. Interior bin k spans[−0.16+kw,−0.16+(k+1)w); the upper bin begins at e=2/15m.')
q(68)['solution']['steps']=['Compute nominal width0.16−(−0.16)=0.32m.','Set w=0.32/12m and retain offset0.16m.','Calculate(e+0.16)/w=(0,6,12).','Convert exact nonnegative values to integers and clip to[0,11].'];q(68)['assumptions']=['This is an explicitly proposed12-bin extension, not unchanged source code. Treat boundary arithmetic exactly, avoiding floating-point representation ambiguity.']
q(68)['solution']['formulas']=[formula('w=(U−L)/N; j=clip(int((e−L)/w),0,N−1)',{'L':'nominal lower error boundary−0.16m','U':'nominal upper error boundary0.16m','N':'number of bins12','w':'bin width','e':'one coordinate of goal error','j':'clipped bin index','int':'conversion toward zero','clip':'saturation to the stated inclusive integer bounds'},{'L,U,w,e':'metres','N,j':'dimensionless'},['Ideal arithmetic; nominal interval[L,U); clipping absorbs the exterior tails.'])]
option(69,'o2','A network avoids storing all grid cells and therefore requires the same number of transition samples regardless of task complexity.','Parameter sharing does not establish task-independent sample demand.')
option(69,'o3','A network generalizes between sampled states, so reducing approximation bias must always reduce optimization instability.','Expressiveness, approximation error and training stability are distinct trade-offs.')
option(69,'o4','A finer table and a neural approximator have identical memory scaling because both receive the same state vector.','Representation storage depends on bin enumeration or network architecture, not input dimension alone.')
q(70)['stem']='In the explicitly checked FetchReachDense-v4 setup (Gymnasium-Robotics1.4.2), why is changing only ACTION_MAP’s fourth component insufficient to turn the reaching task into grasping?'
option(70,'o1','Once the action table contains opening and closing values, actuator availability and the task reward no longer matter.','The environment must apply those controls and reward the intended object interaction.')
option(70,'o2','A fourth-channel command is sufficient because an effective actuator alone guarantees that a reaching reward will teach stable grasping.','Even effective actuation would not supply the missing object/contact objective.')
evidence(70,REACH,'Tested blocked gripper and reach objective, distinguished from slide extension.','reachAction')
# Fix the genuine task-consistency error, not merely the arithmetic label.
q(71)['stem']='In an explicitly supplied FetchReachDense trace, current encoded state is(4,4,4), all Q values are zero, ε=0.5 and the random draw is0.7. The step returns goal error(−0.03,0,0)m and its consistent dense reward−0.03. What are the updated old entry and next encoded state?'
q(71)['assumptions']=['The successor error and reward form a coherent supplied observation, not a claim that+x always moves a fixed distance. Use α=0.1, γ=0.95 and the source encoder.']
option(71,'o1','Q[(4,4,4)][5]=−0.03, then s=(4,4,4).','This uses the wrong tie index, replaces the estimate with the target and fails to encode the successor.')
option(71,'o2','Q[(4,4,4)][0]=+0.003, then s=(5,4,4).','This reverses the reward sign and the error direction.')
option(71,'o3','Q[(4,4,4)][0]=−0.003, then s=(3,4,4).','The greedy tie selects0, the consistent dense reward is−0.03 and the old entry moves by alpha0.1.')
option(71,'o4','Q[(3,4,4)][0]=−0.003, then s=(3,4,4).','The arithmetic is right but the update is incorrectly written to the successor row.')
why(71,'The successor Euclidean distance is0.03m, so dense reward is−0.03. The greedy branch selects action0 from tied zeros. Encoding the successor gives(3,4,4), while the old pair is updated to0+0.1(−0.03+0.95×0−0)=−0.003 before advancing state.')
q(71)['solution']['steps']=['Distance=√((−0.03)²)=0.03m, so dense reward=−0.03.','0.7≥0.5 selects the greedy branch; tied zeros choose action index0.','int((−0.03+0.16)/0.04)=3; the other coordinates encode to4.','Update old Q[(4,4,4)][0] to−0.003, then set s=(3,4,4).'];cite(71,909,'equation','Dense reward is negative Euclidean goal distance.')
option(73,'o2','An epsilon-greedy behavior rule with ε>0 establishes that every relevant pair has already received enough samples for exact optimal values.','Positive exploration probability alone does not establish completed finite-sample accuracy or coverage.')
option(73,'o3','A unique maximum in the current row establishes that estimation uncertainty cannot change the action ranking.','A numerical gap in estimates is not a bound on their errors.')
option(73,'o4','A rising training return establishes that the current greedy policy is optimal under every initial state distribution.','Improvement on sampled training segments does not prove that universal optimum.')
option(74,'o1','Zero is a measured return for the untried action because initialization is equivalent to one neutral experience.','Initialization is a prior estimate, not an observed transition.')
option(74,'o2','Optimism guarantees that every state-action pair is visited sufficiently often, even when some states are never reached.','A preference among available actions does not ensure global state coverage.')
option(74,'o3','A negative update makes the sampled action permanently undesirable because later estimates cannot revise its ranking.','Later data and updates can change the estimate and relative ranking.')
# Readable spacing in every newly written prose field, with code identifiers preserved.
import re
for n in qs:
 item=qs[n]
 if item['id'] not in flagged:continue
 def spacing(s):
  s=re.sub(r'(?<=[A-Za-z])(?=\d)', ' ',s)
  # Do not split identifiers, paths, API names or symbolic indexed expressions: targeted prose values below only.
  return s
 # Explicitly normalize common running-prose joins without rewriting API identifiers.
 def prose(s):
  for old,new in [('Gymnasium1.4.0','Gymnasium 1.4.0'),('Gymnasium-Robotics1.4.2','Gymnasium-Robotics 1.4.2'),('default50','default 50'),('saved5000','saved 5000'),('and5000','and 5000'),('reward2','reward 2'),('estimate1','estimate 1'),('value1','value 1'),('is4','is 4'),('target is2','target is 2'),('is B with estimate1','is B with estimate 1'),('giving2','giving 2'),('give6','give 6'),('to5.23','to 5.23'),('to7.3','to 7.3'),('target1','target 1'),('entry5','entry 5'),('alpha0.1','alpha 0.1'),('gamma0.95','gamma 0.95'),('spans[','spans ['),('interval[','interval ['),('width0.','width 0.'),('Width0.','Width 0.'),('offset0','offset 0'),('clip0','clip 0'),('indices(','indices ('),('Design12','Design 12'),('into12','into 12'),('proposed12','proposed 12'),('span requires w','span requires w'),('the0.','the 0.'),('same0.','same 0.'),('bin0','bin 0'),('bin11','bin 11'),('bin k','bin k'),('state is(','state is ('),('draw is0','draw is 0'),('error(','error ('),('reward−','reward −'),('selects0','selects 0'),('action0','action 0'),('index0','index 0'),('to4','to 4'),('to0+','to 0+'),('distance is0','distance is 0'),('gives(','gives ('),('clip to[','clip to ['),('is1+','is 1+'),('becomes5+','becomes 5+'),('values(5','values (5'),('give(5','give (5')]:s=s.replace(old,new)
  s=re.sub(r'(?<=\d)m\b',' m',s)
  return s
 item['stem']=prose(item['stem']);item['assumptions']=[prose(x) for x in item['assumptions']]
 for o in item['options']:o['text']=prose(o['text'])
 for field in ['justification','simpleExplanation']:item['solution'][field]=prose(item['solution'][field])
 item['solution']['steps']=[prose(x) for x in item['solution']['steps']]
 item['solution']['optionExplanations']={k:prose(v) for k,v in item['solution']['optionExplanations'].items()}
 item['solution']['misconceptions']=[item['solution']['optionExplanations'][o['id']] for o in item['options'] if o['id'] not in item['correctOptionIds']]
q(10)['subtopic']='Observed reward, greedy bootstrap and sampled next action'
q(68)['subtopic']='Range-preserving twelve-bin encoder and saturation'
q(10)['assumptions'].append('For this explicitly defined comparison, Sarsa bootstraps from the actually selected next action, whereas Q-learning bootstraps from the maximum current successor estimate.')
# Two gaps are incorporated into Q010/Q068; the remaining two need coherent new items.
b=DraftBatch(BATCH,6,'L30','Reinforcement Learning',887,AUTHOR);b.questions=data['questions'];b.concepts={c['id']:c for c in data['concepts']}
new=b.add([907,910,912,913,916],'api-lifecycle-gap','Environment lifecycle versus visualization',
'A registered environment is constructed with a supported rendering mode. Which trace correctly distinguishes construction, reset, stepping, rendering and plotting a saved reward history?',
['make constructs the instance; reset returns initial observation and info; step(action) advances the task and returns transition outputs; render visualizes the current task; plotting reward history is separate analysis.',
'make constructs the instance; render(action) advances the task and returns reward/flags; step() only draws the current state; plotting history resets the environment.',
'make constructs the instance; reset returns only a scalar reward; step(action) returns only a new image; render computes the training update automatically.',
'make constructs the instance; reset and step have their usual transition roles, but plotting the saved reward history calls render and changes the environment state automatically.'],[0],
'The environment API separates initialization and interaction from display. The source training loop receives observation/info from reset and five outputs from step. Rendering the task is not the same operation as plotting accumulated rewards, and neither implies a Q update by itself.',
['This keeps the distinct lifecycle and visualization roles.','This swaps step and render and invents a reset side effect for plotting.','The return signatures and automatic learning claim do not match the shown interface.','A separate matplotlib history plot is not an environment render call and need not change task state.'],typ='scenario',difficulty='medium',assumptions=['The environment supports the explicitly configured rendering mode; exact render output type depends on that mode.'])
new['revisionAuthors']=[AUTHOR]
for c in new['citations']:c.update(kind='statement' if c['physicalPage']==907 else 'code',locator=f"Lecture 30, physical page {c['physicalPage']}, printed footer {c['physicalPage']-886}: API lifecycle calls or separate reward-history plotting.")
new=b.add([913,915,917],'training-budget-gap','Extra samples and residual exploration',
'Extend training from 5,000 to 20,000 segments, each exactly 50 steps. During every added step ε is already at its 0.05 floor, and uniform exploration chooses among six actions with one unique greedy action. What are the added step count and expected number of non-greedy action choices?',
['750,000 steps and 37,500 non-greedy choices.','750,000 steps and 31,250 non-greedy choices.','1,000,000 added steps and 41,666⅔ non-greedy choices.','15,000 steps and 625 non-greedy choices.'],[1],
'The extension adds 15,000×50=750,000 steps. Exploration is entered with probability 0.05, but one of its six uniform actions is still greedy, so the non-greedy probability is 0.05×5/6=1/24. The expectation is 31,250 non-greedy choices. More samples alone do not prove convergence, adequate state coverage or optimality.',
['37,500 is the expected number of exploration-branch selections, including those that happen to choose the greedy action.','Both the added step budget and the non-greedy probability are accounted for.','This uses the full 20,000-segment budget instead of only the added 15,000 segments.','This counts segments as if each contained only one decision.'],typ='numerical',difficulty='medium',assumptions=['Added segments all reach their external 50-step collection limit. The epsilon floor applies throughout the extension. There is one unique greedy action at each decision and exploration samples all six actions uniformly.'],steps=['Additional segments: 20,000−5,000=15,000.','Additional decisions: 15,000×50=750,000.','Non-greedy probability: ε×(6−1)/6=0.05×5/6=1/24.','Expected non-greedy choices: 750,000/24=31,250.'],formulas=[formula('N_steps=(E_new−E_old)H; E[N_non-greedy]=N_steps ε(K−1)/K',{'N_steps':'added action decisions','E_new,E_old':'new and previous segment counts','H':'steps per segment','ε':'exploration-branch probability','K':'number of available actions','E[N_non-greedy]':'expected count of selected actions that differ from the unique greedy action'},{'N_steps,E_new,E_old,H,K':'counts','ε':'dimensionless','E[N_non-greedy]':'expected count'},['Uniform exploration with one unique greedy action; constant epsilon over the added decisions.'])])
new['revisionAuthors']=[AUTHOR]
for c in new['citations']:c.update(kind='code',role='premise',locator=f"Lecture 30, physical page {c['physicalPage']}, printed footer {c['physicalPage']-886}: interaction loop, epsilon floor or proposed 20,000+ segment extension.")
# Final item-specific readability pass. Keep mathematical symbols and genuine code identifiers intact.
for item in b.questions:
 if item['id'] in accepted:continue
 def normalize(s):
  replacements={'by0.16':'by 0.16','width0.04':'width 0.04','bins0':'bins 0','bounds and indices':'bounds and indices','clip0':'clip 0','than8':'than 8','proportional to8':'proportional to 8','and3':'and 3','step size0':'step size 0','row S':'row S','is0':'is 0','as4':'as 4','coordinates are0':'coordinates are 0','gives0':'gives 0','and the0':'and the 0','bin11':'bin 11','of12':'of 12','number of bins12':'number of bins 12','boundary−0.16':'boundary −0.16','boundary0.16':'boundary 0.16','to−0.003':'to −0.003','to5.23':'to 5.23','is1+':'is 1 +','is2+':'is 2 +','its0.32':'its 0.32', ')m':') m', ')m,':') m,', 'mean?':'mean?','action index0':'action index 0','index0':'index 0','metres therefore':'metres therefore'}
  for a,z in replacements.items():s=s.replace(a,z)
  return s
 item['stem']=normalize(item['stem']);item['assumptions']=[normalize(x) for x in item['assumptions']]
 for o in item['options']:o['text']=normalize(o['text'])
 for key in ['justification','simpleExplanation']:item['solution'][key]=normalize(item['solution'][key])
 item['solution']['optionExplanations']={k:normalize(v) for k,v in item['solution']['optionExplanations'].items()};item['solution']['steps']=[normalize(x) for x in item['solution']['steps']]
 item['solution']['misconceptions']=[item['solution']['optionExplanations'][o['id']] for o in item['options'] if o['id'] not in item['correctOptionIds']]
 if item.get('conflictResolution'):item['conflictResolution']['basis']=item['solution']['justification']
 for cid in item['conceptIds']:
  b.concepts[cid].update(title=item['subtopic'],description=item['solution']['justification'])
# Update changed concept angles explicitly; accepted question objects remain byte-equivalent as JSON values.
for item in b.questions:
 if item['id'] not in accepted:
  for cid in item['conceptIds']:
   c=b.concepts[cid];c['examinationAngles']=list(dict.fromkeys(c['examinationAngles']+[item['type']]))
# Final visible-prose polish also covers nested formula definitions.
for item in b.questions:
 if item['id'] in accepted:continue
 def polish(value):
  if isinstance(value,str):
   value=value.replace('clipping to0','clipping to 0').replace('Bin0','Bin 0').replace('Calculate(e','Calculate (e').replace('is−0.03','is −0.03').replace('boundary−0.16m','boundary −0.16 m').replace('boundary0.16m','boundary 0.16 m').replace('bins12','bins 12').replace('interval[L','interval [L')
   return value
  if isinstance(value,list):return [polish(x) for x in value]
  if isinstance(value,dict):return {k:polish(v) for k,v in value.items()}
  return value
 item['stem']=polish(item['stem']);item['options']=polish(item['options']);item['solution']=polish(item['solution']);item['assumptions']=polish(item['assumptions'])
 if item.get('conflictResolution'):item['conflictResolution']['basis']=item['solution']['justification']
q(55)['solution']['formulas']=copy.deepcopy(q(71)['solution']['formulas'])
b.save();newdata=json.loads(path.read_text());newdata['sourceIssues']=original.get('sourceIssues',[]);newdata['revisionNote']='27 versioned author repairs plus two new drafts; four bounded coverage gaps addressed by Q010, Q068, Q075 and Q076. Independent review required.';path.write_text(json.dumps(newdata,ensure_ascii=False,indent=2)+'\n')
for item in b.questions:
 if item['id'] in accepted:
  assert question_hash(item)==accepted[item['id']],item['id']
  assert item==next(z for z in original['questions'] if z['id']==item['id'])
changed=[x for x in b.questions if x['id'] not in accepted];assert len(changed)==29
packet=[]
for item in changed:
 hidden={k:copy.deepcopy(item[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in hidden['citations']:c.pop('evidenceText',None)
 packet.append(hidden)
packetpath=R/'audits/blind-W06-L30-v2-and-gaps.json';packetpath.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
errors=[]
for typ,rows in [('question',b.questions),('concept',list(b.concepts.values()))]:
 schema=json.loads((R/f'data/schema.{typ}.json').read_text())
 for item in rows:errors.extend(schema_errors(item,schema))
assert not errors,errors
# Persist source-page concept links without rewriting inspection evidence.
ins=R/'data/inspection-batches/W06-L30.json';inspection=json.loads(ins.read_text())
for slide in inspection['slides']:slide['conceptIds']=[c['id'] for c in b.concepts.values() if slide['id'] in c['slideIds']]
ins.write_text(json.dumps(inspection,ensure_ascii=False,indent=2)+'\n')
manifest={'batchId':BATCH,'revisionAuthor':AUTHOR,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repairedQuestionCount':27,'newQuestionCount':2,'preservedAcceptedCount':47,'totalQuestionCount':len(b.questions),'priorBatchArchive':str(archive.relative_to(R)),'priorBatchSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'blindPacketPath':str(packetpath.relative_to(R)),'blindPacketSha256':hashlib.sha256(packetpath.read_bytes()).hexdigest(),'changedQuestions':[{'questionId':x['id'],'questionVersion':x['version'],'questionSha256':question_hash(x)} for x in changed],'preservedAcceptedHashes':accepted,'coverageGapMapping':{'api-lifecycle':'W06-L30-Q075','training-budget':'W06-L30-Q076','physical-grid':'W06-L30-Q068','bootstrap-target':'W06-L30-Q010'},'independentReviewStillRequired':True,'sourceIssuesPreserved':True}
(R/'audits/W06-L30-v2-repair-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('FROZEN',len(changed),'changed drafts;',len(accepted),'accepted unchanged;',manifest['blindPacketSha256'])
