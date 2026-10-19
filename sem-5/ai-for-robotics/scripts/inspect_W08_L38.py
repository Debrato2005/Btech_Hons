"""Persist only actual rendered-page inspections for L38."""
from pathlib import Path
import json,copy,hashlib,datetime
R=Path(__file__).resolve().parents[1]
NOTES={
1165:'Title page: Introduction to Deep Reinforcement Learning. Printed footer 1.',
1166:'Objectives roadmap: neural approximation, DQN networks, exploration, navigation case and training challenges. Printed footer 2.',
1167:'RL/deep-learning Venn diagram and sequential decision definition inspected. Tabular RL is the contrast, not all classical RL; finite-output DQN does not automatically handle continuous actions.',
1168:'Full agent/action/environment/next-state-reward loop and tabular Q-learning equation inspected. Deterministic policy notation is one case; terminal bootstrap handling is unstated.',
1169:'Large state/action tables and lack of direct parameter sharing inspected. Tabular limitations concern representation and sample demands, not categorical inability to handle changing environments.',
1170:'Actual 3×3 grid and three-row four-action Q table inspected. Nine positions and four actions give 36 entries; Down is greedy in each displayed row. Dynamic-obstacle claims require state/Markov and sample-demand qualifications.',
1171:'Fetch illustration, 8³=512 state bins and six actions giving 3,072 entries inspected. Position encoding omits other physical information. Deep approximation is motivated, not the only possible non-tabular method.',
1172:'Q-table-to-neural-approximator figure inspected. Text describes scalar state-action input while figure uses state-only input with three action outputs; these are different valid architectures, not identical input contracts.',
1173:'Actual network has three inputs, two hidden layers of four and four outputs. Feature prose lists four scalars, so the schematic is not a literal match. Fully connected architecture gives 44 weights, plus 12 biases if explicitly assumed.',
1174:'Corridor diagram and Q table inspected: distances 4.8, 0.6 and 0.2 m favor Forward, Turn and Stop respectively. Q values are not probabilities. No weights are supplied to compute the exact unseen 3.14 m output.',
1175:'MLP/vector, CNN/image and RNN/history examples inspected. These are suitable examples, not exclusive architectures or guarantees of observability.',
1176:'Policy, value and model function list inspected. P(s′|s,a) is a transition model; reward prediction requires a separate or joint reward model. Theta convention includes trainable parameters, typically biases as well as weights.'}
NOTES.update({
1177:'Four-family table inspected: direct policy, action value, dynamics and combined actor/critic. REINFORCE, SARSA/DQN, Dyna-Q/MCTS and A2C/PPO are examples; not every named algorithm is inherently deep or learns a model.',
1178:'Value-based description and SARSA on-policy versus DQN off-policy inspected. V(s) is not itself an action-indexed value; model/lookahead is needed to compare actions from state values alone.',
1179:'Full RL plus DNN → Q-vector → exploration-policy diagram inspected. The Q-network scores actions; epsilon-greedy/Boltzmann selects actions.',
1180:'Atari image/CNN/action-output diagram inspected. Five illustrated actions are schematic, not a validated Breakout action set. Greedy selection is exploitation, not the entire exploration policy.',
1181:'Main network acting and training-prediction roles inspected. Theta is optimized through the chosen-action loss; identical architecture does not mean identical weights at every step.',
1182:'Target-network equation y=r+gamma max Q(s′,a′;phi), hard copying and beta-retention soft update inspected. Terminal handling and update schedule require explicit assumptions. Frozen targets mitigate, not guarantee avoidance of, instability.',
1183:'Two-action example inspected: main Left2.1/Right4.3, greedy Right, reward+1. Fixed target parameters have a different role from action selection.',
1184:'Next-state target values Left3/Right5, gamma0.9 and target5.5 inspected. Main prediction4.3 implies TD error1.2. Exact neural-output change needs network gradient/optimizer context.',
1185:'Epsilon-greedy and Boltzmann softmax equation inspected. Uniform random actions may include the greedy action; positive temperature and tie conventions must be stated. Q-to-probability transformation is distinct from raw Q.',
1186:'Static, predictable dynamic and unpredictable dynamic table inspected. Categories depend on the modeled motion during the episode, not merely whether the object is a person or furniture.',
1187:'Mobile wheel speeds0.42/0.51m/s, arm torques1.8/−0.6N·m and drone vector inspected. Drone units are unspecified. Continuous actuators do not turn a finite-output DQN into a continuous-action optimizer.',
1188:'Bibliographic case-study introduction only. Exact publisher title differs slightly; online publication2024 and issue2025 are compatible. No assessed author/year trivia.',
1189:'Modified DQN with top-view RGB/CNN, inflated-robot reward and CLIK path tracking inspected. Separate planning and control roles; intended safe behavior is not a universal safety proof.',
1190:'Actual concourse/home maps and legends inspected. Black static and pink dynamic obstacles; concourse12m/40cells and home9m/30cells both imply0.3m cells. Reset randomization does not mean walls move during an episode.',
1191:'Actual square5×5 buffer with red center0, eight yellow1 cells and sixteen green2 cells inspected. Radius150mm is physical robot geometry, not the5×5 buffer radius. PrintedP2−50 is not universal across the next table.',
1192:'All six reward rows and both environment columns inspected. P3 is−2/−4 and P2 is−50/−2 for concourse/home; other four rows match. Aggregation and simultaneous-event priority are not specified.',
1193:'Reported results text only, no tracking plots on this slide. Same model,16+16 versus8+8 and300mm minimum gap are reported simulation observations, not universal guarantees. Small tracking error alone cannot prove obstacle clearance.',
1194:'Sample inefficiency, data-feedback instability and sparse/misaligned reward challenges inspected. Millions is an illustrative tendency, not a theorem; density alone does not imply reward hacking.',
1195:'Summary repeats deep approximation, main/target networks, exploration and inflated-reward navigation. Link to prior concepts rather than duplicate recall.',
1196:'Closing thank-you slide; printed footer32.'})
EX={1188:'Bibliographic case-study introduction only; substantive method assessed on following pages.',1165:'Title only.',1166:'Objectives roadmap only.',1196:'Closing page only.'}
def save():
 maps={s['physicalPage']:s for s in map(json.loads,(R/'sources/page_maps/lectures.jsonl').read_text().splitlines())}; slides=[]
 batch=R/'data/question-batches/W08-L38.json'; concepts=json.loads(batch.read_text())['concepts'] if batch.exists() else []
 for p,n in sorted(NOTES.items()):
  s=copy.deepcopy(maps[p]);s.update(disposition='excluded' if p in EX else 'examinable',exclusionReason=EX.get(p),conceptIds=[c['id'] for c in concepts if s['id'] in c['slideIds']],printedSlideNumber=str(p-1164),printedSlideNumberStatus='present',printedNumberEvidence='Actual rendered footer inspected, separately from physical PDF index.')
  s['visualInspection']={'status':'complete','inspectorId':'build_offline_study_interface:L38-author','inspectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'rendered_page','notes':n+' Actual 1800×1013 page pixels viewed alongside extracted text.','previewSha256':hashlib.sha256((R/s['previewPath']).read_bytes()).hexdigest(),'dimensions':[1800,1013]};slides.append(s)
 (R/'data/inspection-batches/W08-L38.json').write_text(json.dumps({'batchId':'W08-L38','slides':slides},ensure_ascii=False,indent=2)+'\n')
 (R/'audits/W08-L38-page-observations.json').write_text(json.dumps({'sourceId':'lectures','notes':NOTES,'inspectionComplete':len(NOTES)==32,'authoringComplete':False,'independentReviewComplete':False},ensure_ascii=False,indent=2)+'\n')
 print('Persisted',len(slides),'actual inspections.')
if __name__=='__main__':save()
