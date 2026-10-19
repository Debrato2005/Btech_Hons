#!/usr/bin/env python3
"""Versioned L27 author repairs; preserves accepted objects and never self-approves."""
import json,copy,hashlib,os
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];B='W06-L27';A='L27-author-20261019'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
if (R/f'audits/{B}-v2-review-manifest.json').exists():raise SystemExit('Frozen L27 v2: do not regenerate over reviewed content.')
archive=f'data/question-batches/archive/{B}-v1.json'
if not (R/archive).exists():write(archive,read(f'data/question-batches/{B}.json'))
old=read(archive);b=copy.deepcopy(old);qm={q['id']:q for q in b['questions']};review=read(f'data/reviews/{B}-v1-independent.json');flag={r['questionId']:r for r in review if r['decision']=='flagged'};accepted=[q for q in old['questions'] if q['id'] not in flag]
assert len(flag)==31 and len(accepted)==40
for q in old['questions']:assert next(r for r in review if r['questionId']==q['id'])['questionSha256']==sha(q)
for i,rv in flag.items():
 q=qm[i];assert q['version']==1;q.update(version=2,status='draft',reviewIds=[]);q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+[A]))
 if 'conflictResolution' in q:q['conflictResolution']['questionVersion']=2
 if any(t.startswith('difficulty:') for t in rv['findings']):q['difficulty']='easy'
changed=set()
def edit(short,opts,why,stem=None,**kw):
 q=qm[B+'-'+short];assert q['id'] in flag
 if stem:q['stem']=stem
 assert len(opts)==len(why)==4
 for o in q['options']:o['text']=opts[int(o['id'][1:])-1]
 just=' '.join(why[int(i[1:])-1] for i in q['correctOptionIds'])
 q['solution'].update(justification=just,simpleExplanation=just,optionExplanations={f'o{i+1}':('Correct. ' if f'o{i+1}' in q['correctOptionIds'] else 'Incorrect. ')+x for i,x in enumerate(why)},misconceptions=[why[i] for i in range(4) if f'o{i+1}' not in q['correctOptionIds']])
 for k,v in kw.items():
  if k in ('formulas','steps'):q['solution'][k]=v
  else:q[k]=v
 changed.add(q['id']);return q

def persist():
 replacements={q['stem']:qm[q['id']]['stem'] for q in old['questions'] if q['id'] in flag}
 for c in b['concepts']:c['examinationAngles']=[replacements.get(t,t) for t in c.get('examinationAngles',[])]
 for q in accepted:assert q==qm[q['id']]
 assert b['sourceIssues']==old['sourceIssues'] and len(b['sourceIssues'])==7
 write(f'data/question-batches/{B}.json',b)
 (R/f'audits/handoffs/{B}-v2-progress.md').write_text(f'# L27 v2 repair checkpoint\n\n{len(changed)} content repairs persisted; all 31 flags versioned and six requested difficulty labels lowered. All 40 accepted objects and seven source annotations remain unchanged. Rebuild only this owned draft from archived v1 with scripts/repair_W06_L27_v2.py until its freeze guard exists. Independent re-review is required; no self-approval, canonical or Git writes.\n')
 print('Checkpoint:',len(changed),'content repairs;',len(b['questions']),'questions')

edit('P0802-Q02',[
 'Torque is a continuous numerical target; a zone identifier denotes group membership rather than a measured magnitude',
 'Both are regression outputs because torque values and zone identifiers can both be stored as numbers',
 'Torque is a classification output because the training set contains only four distinct measured target values',
 'Zone identification is continuous estimation because temperature and Wi-Fi inputs are continuous'],[
 'The output meaning distinguishes continuous estimation from assigning a group; numerical storage alone is not decisive.',
 'An integer cluster ID names a group and does not acquire a continuous physical meaning merely by being numerical.',
 'A finite training set does not restrict the underlying torque target to a finite list of classes.',
 'Continuous inputs can be grouped into discrete clusters; input type alone does not determine output semantics.'])
edit('P0803-Q04',[
 'Some feature rows may be paired with torque labels measured for different rows',
 'All original feature-target pairs are preserved because the two arrays retain the same number of rows',
 'The operation is equivalent to applying the same permutation to both X_lifting and y_torque',
 'The fit can recover the original pairs from row order because it automatically sorts both arrays by torque'],[
 'Supervised targets must remain aligned with their corresponding feature rows; separate shuffling can break that association.',
 'Equal array lengths do not establish row-wise correspondence.',
 'Only a synchronized permutation preserves the original pairs; the stated operation changes X alone.',
 'The printed fit pairs inputs and targets by row position; it does not infer an unknown permutation by sorting.'])
q=qm[B+'-P0803-Q05'];q['solution']['optionExplanations']['o2']='Incorrect. This is a factor-ten mass-entry error: using 0.5 kg instead of 5 kg gives 0.5×9.8×1=4.9 N·m. Omitting the factor 5 would instead give 9.8 N·m.';q['solution']['misconceptions']=[v for k,v in q['solution']['optionExplanations'].items() if k not in q['correctOptionIds']];changed.add(q['id'])
edit('P0804-Q01',[
 'Construct LinearRegression → fit(X_lifting, y_torque) → predict(new_box)',
 'Construct LinearRegression → predict(new_box) → fit(X_lifting, y_torque)',
 'Construct LinearRegression → fit(X_lifting, y_torque) → predict(X_lifting) and report the first training prediction for new_box',
 'Construct LinearRegression → fit(X_lifting[:, ::-1], y_torque) → predict(new_box) without reversing the new row'],[
 'The source creates the estimator, fits aligned labeled examples, then predicts the new feature row.',
 'A newly constructed estimator has not learned its coefficients before the fit call.',
 'A prediction for a training row is not the prediction for the supplied new mass and extension.',
 'This trains with extension then mass, but queries with mass then extension; feature order is inconsistent.'],assumptions=['A fresh unfitted estimator is used; X_lifting and new_box use the printed feature order mass then extension.'])
q=qm[B+'-P0804-Q01'];q['citations'][0].update(kind='code',locator='Printed slide 6: LinearRegression construction, fit(X_lifting, y_torque), and predict(new_box)[0] calls')
edit('P0804-Q02',[
 'One plane giving a scalar height above each two-feature input location',
 'One straight line containing all input-output triples in three dimensions',
 'Two separate straight-line predictions, with no single output defined for a pair of inputs',
 'A generally curved surface whose slope in one input automatically varies with the other'],[
 'An affine scalar function of two inputs has the form b₀+b₁x₁+b₂x₂, whose graph is a plane.',
 'The two independent inputs span a two-dimensional domain, so their complete affine graph is not generally a line.',
 'The model combines both input contributions into one output, rather than returning two separate one-feature predictions.',
 'An affine model has constant partial slopes; input-dependent slopes require an interaction or other nonlinear term.'])
edit('P0804-Q05',[
 'The product contains a mass-distance interaction absent from b₀+b₁m+b₂r',
 'The free intercept supplies the interaction because it shifts the plane for each input pair',
 'The slope b₁ in a raw-feature affine fit is recomputed as 9.8r at every prediction point',
 'The separate terms b₁m and b₂r are multiplied together when the fitted model predicts'],[
 'In the product, changing r changes the mass slope; an affine plane has one constant mass slope and one constant extension slope.',
 'A fitted intercept is one constant, not a different correction at every input pair.',
 'The fitted coefficient b₁ remains fixed during prediction; it is not recomputed from the new extension.',
 'The affine model adds its terms; multiplying them would define a different model.'])
edit('P0805-Q02',[
 'Red circles: training examples; yellow star: new test prediction; translucent sheet: fitted plane',
 'Red circles: fitted predictions for training rows; yellow star: a measured training target; translucent sheet: residual magnitudes',
 'Red circles: held-out test examples; yellow star: training-data centroid; translucent sheet: fitted plane',
 'Red circles: training examples; yellow star: largest training residual; translucent sheet: boundary of a prediction interval'],[
 'The legend labels Training Data and New Test Point, and the title identifies the plane of best fit.',
 'The circles are labeled training data, while the sheet shows the model surface rather than residual magnitudes.',
 'The legend calls the circles training data and the star the new test point, not a centroid.',
 'The star is the new test point and the sheet is the fitted plane; no residual or interval-boundary legend is supplied.'])
edit('P0806-Q01',[
 'Low error on genuinely unseen examples representative of the deployment task',
 'Low error on the same examples used repeatedly to fit and select the final model',
 'Low error on an unseen test set collected only in an easier operating regime than deployment',
 'Low error on held-out rows that duplicate measurements already present in the fitting set'],[
 'Unseen and relevant evaluation data support generalization beyond the fitted examples.',
 'Reuse for fitting and selection does not supply independent evidence of unseen-case performance.',
 'Good results in an easier regime need not estimate performance in the intended deployment regime.',
 'Duplicating fitting measurements in the held-out set leaks known examples into the apparent test.'])
edit('P0806-Q02',[
 'Different operating conditions can change the input-target relationship, making an unseen test set unrepresentative of deployment',
 'Matching the number of test rows to the number of training rows makes any operating regime representative',
 'Matching the measurement units is sufficient even if sensor calibration or operating conditions change',
 'Matching each feature’s mean is sufficient even if its range and relationship to the target change'],[
 'Similarity concerns relevant data-generating conditions, not merely whether examples are new.',
 'Sample count does not ensure similarity of operating conditions.',
 'Identical units do not guarantee the same calibration or input-target relationship.',
 'Matching means alone does not preserve the whole distribution or the relation being predicted.'])
edit('P0807-Q02',[
 'Add relevant informative features or use appropriate model capacity to represent the missing relationship',
 'Collect more samples of the same incomplete features while leaving the missing information unmeasured',
 'Repeat the already converged optimization longer without changing inputs or model family',
 'Change only the train-test split while keeping the same incomplete inputs and fitted model family'],[
 'The stated limitation is missing information or representational capacity, so a targeted feature or model change addresses it.',
 'More samples can improve estimation, but do not directly supply the explicitly missing input information.',
 'After convergence, extra repetitions do not add missing features or enlarge the model family.',
 'A different evaluation split can change the estimate of performance but does not itself repair the missing representation.'],assumptions=['Optimization has converged for the current model; the question stipulates insufficient informative features as the cause, not merely infers it from error rates.'])
edit('P0807-Q03',[
 'Many features relative to samples: overfitting risk; excessively strong regularization: underfitting risk',
 'Many features relative to samples: underfitting risk; excessively strong regularization: overfitting risk',
 'Insufficient informative features: overfitting risk; highly flexible models relative to available data: underfitting risk',
 'Insufficient informative features: underfitting risk; excessively strong regularization: overfitting risk'],[
 'The table links flexibility relative to limited information with overfitting and excessive constraint with underfitting.',
 'This reverses both associations listed in the source.',
 'Missing features limit fitting the signal, while excessive flexibility can fit sample-specific details; these associations are reversed.',
 'The first association matches the source, but strong regularization is listed as an underfitting cause.'])
edit('P0807-Q04',[
 'Treat it as a possible risk in an iterative training setup, using held-out performance to judge when further fitting hurts generalization',
 'Choose the stopping point at the lowest training error, using continued training improvement as sufficient evidence of generalization',
 'Transfer the best epoch count from one model and dataset to another without rechecking held-out performance',
 'Diagnose overfitting from a high iteration count alone, even when both training and held-out errors are still improving'],[
 'Iteration effects depend on the model and data; held-out behavior tests whether further fitting is becoming harmful.',
 'Training error can continue decreasing while held-out performance worsens.',
 'A useful stopping point depends on the particular model, data and optimization setup.',
 'The count alone does not establish overfitting; simultaneous improvement supplies different evidence.'])
edit('P0808-Q03',[
 'Feature count, regularization strength, dataset size, evaluation strategy',
 'Feature count, regularization strength, optimizer learning rate, mini-batch size',
 'Dataset size, evaluation strategy, initialization method, optimizer momentum',
 'Feature count, dataset size, optimizer learning rate, parameter initialization'],[
 'These are the four design and evaluation choices explicitly listed on this slide.',
 'Learning rate and mini-batch size are plausible training choices, but replace the listed dataset size and evaluation strategy.',
 'Initialization and momentum are not in this slide’s four-item list.',
 'This substitutes learning rate and initialization for the listed regularization and evaluation choices.'],stem='Which four-item list reproduces the model-design choices explicitly enumerated on the trade-off slide?')
persist()
edit('P0811-Q04',[
 'A fixed point of the assignment/update loop, without certifying the globally lowest within-cluster squared error',
 'The globally lowest within-cluster squared error among all partitions into k clusters',
 'The same final partition would be obtained from every possible initial set of centers',
 'The assignments are stationary, but another mean update must still strictly decrease the objective'],[
 'Under the stated fixed-data, no-tie and nonempty-cluster assumptions, another identical loop returns the same centers and assignments; global optimality is not proved.',
 'A stable outcome of this local iteration does not compare its objective with every possible partition.',
 'Different initializations can lead to different fixed points; this one stopping test does not establish independence from initialization.',
 'At this fixed point the mean update leaves the centers unchanged, so it cannot force a strict objective decrease.'])
q=qm[B+'-P0811-Q04'];q['citations'][0].update(kind='figure',role='premise',locator='Printed slide 13: left-side K-means assignment/mean-update flowchart and unchanged-center stopping condition')
edit('P0811-Q06',[
 'Current cluster centers, with colors corresponding to the circular samples’ memberships',
 'The initial center positions before any assignment or mean-update step',
 'New observations withheld from fitting and then assigned to the colored groups',
 'One boundary sample per cluster chosen as the most distant observation from its center'],[
 'The image is labeled Recompute Centers (3), and the triangular markers identify the current centers.',
 'The illustrated stage is a recomputed-center stage, not the initial positions before clustering.',
 'The triangular markers denote centers, not a separate held-out prediction set.',
 'A mean center need not be a sample, and the figure does not mark farthest observations.'])
edit('P0812-Q01',[
 'Temperature in °C and Wi-Fi strength in percent; no labeled target; three requested groups',
 'Temperature in °C and Wi-Fi strength in percent; labeled room names; three supervised classes',
 'Temperature in °C and Wi-Fi strength in percent; no labeled target; two groups because there are two features',
 'Temperature in °C and Wi-Fi strength in percent; a continuous room-score target; three fitted output values'],[
 'The printed task supplies two sensor features and requests three unlabeled groups.',
 'Known room-name targets are not supplied; the example performs unsupervised grouping.',
 'The requested cluster count is three, independent of the two feature columns.',
 'The example has no continuous target array and returns group membership, not three scalar regression outputs.'])
edit('P0812-Q02',[
 'A feature cluster can contain spatially separated locations whose temperature and Wi-Fi readings are similar',
 'A feature cluster must be spatially connected because Euclidean distances are used between its sensor readings',
 'A change of cluster label along a route establishes that the robot crossed a physical room boundary',
 'Two adjoining rooms must receive different cluster labels even when their sensor readings overlap'],[
 'The supplied features describe sensor similarity, not physical connectivity; no spatial coordinates or room labels establish a room partition.',
 'Distance in temperature/Wi-Fi feature space is not geographic distance or a connectivity test.',
 'A sensor change can occur within a room, so a label change alone does not establish a wall or doorway crossing.',
 'Distinct rooms can have similar readings and be grouped together without spatial or room-label evidence.'],stem='Which conclusion respects what temperature/Wi-Fi clustering can establish about physical rooms?')
edit('P0813-Q03',[
 '100 observations, each with temperature and Wi-Fi feature values',
 'Two observations, each measured on 100 sensor-feature channels',
 '100 observations, with the first column storing means and the second storing standard deviations',
 '100 observations divided between two zone populations, with one population per column'],[
 'The requested shape creates 100 rows and two feature columns in the printed temperature/Wi-Fi order.',
 'This reverses the observation and feature axes.',
 'Means and standard deviations are inputs to the generator, not the meanings of the output columns.',
 'Each zone call generates one population; the two columns are its sensor features, not two separate zones.'])
q=qm[B+'-P0813-Q05'];q['citations'][0].update(kind='code',role='conflict',locator='Printed slide 15: np.random.normal location and scale arrays plus the standard-deviation annotation');q['citations'][1].update(kind='figure',role='explicit',locator='Printed slide 17: upper sensor cluster in the scatter plot; purple observation markers above the 100% horizontal Wi-Fi gridline',evidenceText='Visual observation: the upper cluster contains purple circular samples above the y-axis gridline labeled 100 on Wi-Fi Strength (%). The red centroid is near 90%, and the magenta new-reading star is near 85%.');changed.add(q['id'])
edit('P0815-Q02',[
 'Small circles: exploration data; red X marks: centroids; magenta star: new reading',
 'Small circles: exploration data; red X marks: initial centers; magenta star: the mean of all sensor readings',
 'Small circles: held-out test readings; red X marks: fitted centroids; magenta star: one of the original training samples',
 'Small circles: exploration data; red X marks: new readings; magenta star: the centroid of the upper group'],[
 'These match the three entries in the source plot’s legend.',
 'The X marks are labeled Zone Centers (Centroids), not initial centers; the star is labeled New Reading, not an overall mean.',
 'The circles are exploration data used for the displayed grouping, and the star is the separately supplied new reading.',
 'The X marks are centroids; the magenta star is the new point near the upper centroid, not the centroid itself.'])
edit('P0816-Q02',[
 'It may indicate a problem requiring investigation, but an anomaly alone does not identify its cause',
 'It identifies mechanical failure rather than changed operating conditions because the detector used torque data',
 'It identifies a sensor fault rather than a mechanical fault because the monitor did not use failure labels',
 'It identifies harmless distribution shift rather than failure whenever the flagged pattern was absent from training'],[
 'Unusual torque patterns motivate investigation; causal diagnosis needs context beyond the anomaly flag.',
 'Torque can vary for several reasons, including changed loading or operating conditions; the feature type does not isolate a cause.',
 'Unsupervised detection does not distinguish sensor faults from mechanical faults merely by lacking labels.',
 'Novelty does not establish that a change is harmless; both faults and nonfault changes can be unfamiliar.'])
edit('P0816-Q03',[
 'Replace similar original colors by a smaller palette of representative colors, accepting possible reconstruction error',
 'Store a cluster ID in addition to every unchanged full-precision pixel color, treating the extra labels as the compression',
 'Retain one distinct palette entry for every original color, using clustering only to reorder those entries',
 'Replace each color by its cluster center while requiring every original color to remain exactly recoverable'],[
 'Color grouping can reduce the palette and representation cost, usually with a trade-off in exact color reconstruction.',
 'Adding labels without removing or reducing the original color representation adds information rather than implementing the stated palette reduction.',
 'Reordering an unchanged set of distinct colors does not implement representation with fewer representative colors.',
 'If different original colors share one representative, their exact original values are not generally recoverable from that representative alone.'],assumptions=['Interpret the slide’s color-grouping mechanism as palette reduction; net file size also depends on palette and index encoding overhead.'])
edit('P0817-Q02',[
 '{left, right, forward} is the action set; left is the selected action',
 '{left, right, forward} is the action set; left is the new observed state rather than a selected move',
 '{left, right, forward} is one selected action; left is the entire action set',
 '{left, right, forward} is the state space; left is a policy mapping observations to decisions'],[
 'An action is one chosen element of the available set, as the concrete example distinguishes.',
 'Here left names the controller’s selected move, not an observation of the resulting environment state.',
 'This reverses a set of alternatives and its selected element.',
 'Available moves define an action set, while a policy is a decision rule rather than the single chosen move.'])
edit('P0817-Q04',[
 'No; a simulator can provide action-dependent state transitions and reward feedback, fulfilling the functional environment role',
 'Yes; simulator feedback cannot serve as reinforcement feedback until a physical robot repeats the same actions',
 'No; a fixed log of one route provides the same interactive responses for any alternative action the agent chooses',
 'Yes; an environment must contain the policy that chooses the agent’s action, rather than respond to that action'],[
 'The relevant interface is interaction and feedback; physical hardware is one implementation, not a necessary condition in this supplied simulator example.',
 'Simulated transitions and rewards can implement the interaction loop without first executing it on hardware.',
 'A fixed log contains recorded outcomes, not necessarily counterfactual responses to different chosen actions; offline learning is a separate setup.',
 'The policy belongs to the agent’s decision process; the environment responds with transitions and feedback.'],assumptions=['The supplied simulator responds to the agent’s selected actions and provides observations and reward feedback; no claim is made that it perfectly represents hardware.'])
edit('P0817-Q06',[
 'Feedback evaluates action consequences through rewards or penalties without necessarily specifying the correct action',
 'Feedback supplies correct-action labels paired with states so the agent can fit an action-prediction target',
 'Feedback is only sensor-reconstruction error, without evaluating consequences of the selected action',
 'Feedback is only membership in a group of similar sensor observations, without evaluating action outcomes'],[
 'This is the lecture’s critic-style distinction: outcome evaluation rather than a teacher’s correct-answer target.',
 'Correct-action labels describe teacher-style supervision, the contrasting setup.',
 'Reconstructing observations can train a representation but is not the stated reward-based evaluation of action consequences.',
 'Grouping observations describes the clustering example, not the critic’s reward or penalty for outcomes.'])
edit('P0818-Q03',[
 'Choice A is exploration; choice B is exploitation',
 'Choice A is exploitation; choice B is exploration',
 'Both choices are exploration',
 'Both choices are exploitation'],[
 'Choice A seeks information about an uncertain alternative; choice B uses the currently best-known estimate to obtain reward.',
 'This reverses the information-seeking and best-known-choice roles.',
 'Choice B is selected to use current knowledge, not primarily to resolve uncertainty.',
 'Choice A deliberately tests an uncertain alternative for information rather than only maximizing the current estimate.'],stem='Choice A tries a less-known route primarily to learn its outcome. Choice B chooses the route with the highest current estimated reward primarily to obtain that reward. How are the choices classified?')
edit('P0819-Q01',[
 'Use learning to model sensor patterns that resist hand-crafted rules, but align the learned target and evaluation with the required robotics task',
 'Keep the unrelated target because high accuracy on a complex sensor prediction is sufficient evidence of robotics-task success',
 'Keep the target and use a more flexible model, treating improved prediction accuracy as the remedy for task misalignment',
 'Evaluate only reconstruction of all sensor values, treating that metric as a substitute for the required task outcome'],[
 'The summary motivates learning for difficult sensor patterns while warning that sophisticated learning can still solve the wrong problem.',
 'Prediction accuracy is not enough when the predicted quantity does not address the intended task.',
 'Greater flexibility cannot make an unrelated objective relevant without changing the problem formulation.',
 'Reconstruction can be a useful intermediate objective, but must not replace evaluation of an unrelated required task without justification.'],stem='A robot’s complex sensor patterns are difficult to describe with hand-crafted rules. A team learns to predict a quantity accurately, but that quantity is unrelated to the required robotics task. Which response combines the summary’s motivation for learning with its warning?',assumptions=['The scenario stipulates that the predicted quantity is unrelated to the required task; it does not claim that learning is always necessary or always better than hand-crafted rules.'])
q=qm[B+'-P0819-Q01'];q['citations'][0].update(role='premise',locator='Printed slide 21: first bullet on complex sensor data and hand-crafted rules, together with the final warning about solving the wrong problem')
edit('P0819-Q02',[
 'Known target outputs can motivate a supervised setup',
 'Unlabeled sensor structure can motivate an unsupervised setup',
 'Action-dependent rewards can motivate a reinforcement setup',
 'Continuous sensor inputs make their unlabeled clustering a supervised regression task'],[
 'Supervised learning uses known target values, as in the torque example.',
 'Unsupervised learning can seek structure without target labels, as in the sensor grouping example.',
 'Reinforcement learning uses consequences of actions and reward feedback.',
 'Continuous inputs do not create labeled targets; grouping unlabeled observations remains an unsupervised task.'])
persist()
# The existing single-seed and cluster-count questions are accepted, so add the distinct two-generator angle separately.
q=copy.deepcopy(qm[B+'-P0813-Q04']);q.update(id=B+'-P0813-Q06',version=1,status='draft',reviewIds=[],difficulty='easy',stem='The code uses np.random.seed(42) before creating sensor data and KMeans(n_clusters=3, random_state=42) when fitting. Which distinction correctly identifies the two randomness controls?',conceptIds=[B+'-P0813-C01',B+'-P0814-C01'],assumptions=['Compare repeated runs with the same library versions, algorithm settings, input data and operation order. No universal cluster-number identity across implementations is asserted.'])
q.pop('revisionAuthors',None);q.pop('conflictResolution',None)
opts=[
 'The NumPy seed controls estimator-center initialization; KMeans random_state controls the earlier Gaussian sensor draws',
 'The NumPy seed controls synthetic sensor draws; the estimator’s random_state controls its own initialization randomness',
 'The NumPy seed controls both stages; the estimator’s random_state only chooses which final group is called cluster 0',
 'Both integers refer to one shared mutable generator, so additional NumPy draws necessarily advance estimator initialization despite its fixed integer random_state']
why=[
 'This reverses the two roles: the Gaussian draws occur through NumPy before the estimator is fitted.',
 'The printed settings separately control data-generation randomness and estimator initialization, supporting reproducibility under the fixed-setup assumption.',
 'The estimator’s integer random_state is not merely a label-renaming parameter and is not replaced by the earlier global seed.',
 'An explicit integer estimator random_state establishes its own reproducible random state; it is not the same mutable global generator advanced by unrelated NumPy calls.']
for o in q['options']:o['text']=opts[int(o['id'][1:])-1]
q['correctOptionIds']=['o2'];q['solution'].update(justification=why[1],simpleExplanation=why[1],optionExplanations={f'o{i+1}':('Correct. ' if i==1 else 'Incorrect. ')+w for i,w in enumerate(why)},misconceptions=[w for i,w in enumerate(why) if i!=1],steps=['Identify np.random.seed(42) before the three np.random.normal calls.','Identify random_state=42 as an argument of the separate KMeans estimator.','Keep data generation, estimator initialization and arbitrary final cluster names conceptually distinct.'],formulas=[])
q['citations']=[copy.deepcopy(qm[B+'-P0813-Q04']['citations'][0]),copy.deepcopy(qm[B+'-P0814-Q03']['citations'][0])]
q['citations'][0].update(kind='code',role='premise',locator='Printed slide 15: np.random.seed(42), followed by three np.random.normal calls',evidenceText='Visual code transcription: np.random.seed(42); zone_A=np.random.normal([10,20],[2,5],(100,2)); zone_B=np.random.normal([22,90],[2,5],(100,2)); zone_C=np.random.normal([25,40],[2,5],(100,2)).')
q['citations'][1].update(kind='code',role='premise',locator='Printed slide 16: KMeans(n_clusters=3, random_state=42), followed by fit(X_sensors)',evidenceText='Visual code transcription: X_sensors=np.vstack([zone_A,zone_B,zone_C]); clustering_model=KMeans(n_clusters=3, random_state=42); clustering_model.fit(X_sensors).')
b['questions'].append(q);qm[q['id']]=q
for c in b['concepts']:
 if c['id'] in q['conceptIds']:c['questionIds'].append(q['id']);c['examinationAngles'].append(q['stem'])
assert set(flag)-changed=={i for i,r in flag.items() if len(r['findings'])==1 and r['findings'][0].startswith('difficulty:')}
for i in flag:assert qm[i]['correctOptionIds']==next(q for q in old['questions'] if q['id']==i)['correctOptionIds']
b['coverageNote']='All 23 actual pages remain inspected. Version 2 repairs 31 flagged questions, preserving 40 accepted objects and all seven source qualifications. New P0813-Q06 distinguishes data and estimator random seeds; expanded P0819-Q01 combines complex-sensor motivation with task alignment. All 32 changed/new objects await independent review.'
persist()

import sympy as s
import numpy as np
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.exceptions import NotFittedError
newchecks=[]
def check(name,truth,result):
 assert bool(truth),name
 newchecks.append(dict(id=f'L27-V2-AUTHOR-{len(newchecks)+1:02}',check=name,result=result,status='passed',independentReview=False))
check('803Q05 correct torque',s.Integer(5)*s.Rational(98,10)*1==49,'5 kg × 9.8 m/s² × 1 m = 49 N·m.')
check('803Q05 o2 factor-ten mass entry',s.Rational(5,10)*s.Rational(98,10)*1==s.Rational(49,10),'0.5 kg instead of 5 kg gives 4.9 N·m.')
check('803Q05 o3 omitted mass factor',s.Rational(98,10)*1==s.Rational(98,10),'Omitting factor 5 gives 9.8 N·m, not 4.9.')
check('803Q05 o4 half-metre arm',5*s.Rational(98,10)*s.Rational(1,2)==s.Rational(49,2),'Using r=0.5 m gives 24.5 N·m.')
X=np.array([[1,.5],[2,.5],[1,1],[5,1]]);y=np.array([4.9,9.8,9.8,49.]);new=np.array([[3.5,.8]])
fit=LinearRegression().fit(X,y);correct=float(fit.predict(new)[0]);swapped=float(LinearRegression().fit(X[:,::-1],y).predict(new)[0])
check('804Q01 printed lifecycle and result',abs(correct-31.04294117647059)<1e-10,{'prediction':correct})
try:LinearRegression().predict(new);unfit=False
except NotFittedError:unfit=True
check('804Q01 unfitted prediction rejected',unfit,'A fresh estimator cannot predict before fitting.')
check('804Q01 training prediction is not new-point prediction',abs(float(fit.predict(X)[0])-correct)>1,{'firstTrainingPrediction':float(fit.predict(X)[0]),'newPrediction':correct})
check('804Q01 inconsistent feature order changes prediction',abs(swapped-correct)>1,{'reversedTrainingColumnsUnchangedQuery':swapped})
perm=np.array([3,1,2,0]);synchronized=LinearRegression().fit(X[perm],y[perm]);misaligned=LinearRegression().fit(X[perm],y)
check('803Q04 synchronized permutation preserves prediction',np.allclose(synchronized.predict(new),fit.predict(new)),'Joint row permutation preserves input-target pairs and this OLS prediction.')
check('803Q04 independent permutation can break prediction',not np.allclose(misaligned.predict(new),fit.predict(new)),{'misalignedPrediction':float(misaligned.predict(new)[0])})
mm,rr=s.symbols('m r');f=s.Rational(98,10)*mm*rr;b0,b1,b2=s.symbols('b0 b1 b2');affine=b0+b1*mm+b2*rr
check('804Q05 interaction versus affine mixed derivative',s.diff(f,mm,rr)==s.Rational(98,10) and s.diff(affine,mm,rr)==0,'Product mixed derivative is 9.8; an affine raw-feature model has zero mixed derivative.')
def data(seed):
 np.random.seed(seed)
 return np.vstack([np.random.normal([10,20],[2,5],(100,2)),np.random.normal([22,90],[2,5],(100,2)),np.random.normal([25,40],[2,5],(100,2))])
D=data(42);Dsame=data(42);Dother=data(43);saved=D.copy()
check('813Q06 NumPy data-seed repeatability',np.array_equal(D,Dsame) and not np.array_equal(D,Dother),'Same seed and draw order reproduce all 300×2 entries; changing the data seed changes them.')
np.random.seed(1);np.random.normal(size=17);k1=KMeans(n_clusters=3,random_state=42).fit(D)
np.random.seed(987);np.random.normal(size=103);k2=KMeans(n_clusters=3,random_state=42).fit(D)
check('813Q06 integer estimator seed isolated from unrelated global draws',np.array_equal(k1.labels_,k2.labels_) and np.allclose(k1.cluster_centers_,k2.cluster_centers_),'Fixed input and integer random_state reproduce the fit despite different preceding global NumPy draws.')
k3=KMeans(n_clusters=3,random_state=43).fit(D)
check('813Q06 estimator fit does not regenerate source sensor array',np.array_equal(D,saved),'Changing estimator random_state leaves the supplied sensor array unchanged; final group IDs are not promised universal.')
check('813Q05 actual unbounded-Gaussian sample evidence',np.count_nonzero(D[:,1]>100)==2,{'samplesAbove100Percent':int(np.count_nonzero(D[:,1]>100)),'maximumWiFi':float(D[:,1].max())})
check('Source issue file remains frozen',hashlib.sha256((R/'audits/source-disputes-W06-L27.json').read_bytes()).hexdigest()=='5ce58c0a78bffd3b1df52d6b12acaa2bb47614f9825279970e45b2b62d51c9e1','All seven source annotations remain byte-identical.')
b['authorChecks']=old['authorChecks']+newchecks
persist()
env=read(f'data/inspection-batches/{B}.json');env['summary'].update(questions=len(b['questions']),concepts=len(b['concepts']));write(f'data/inspection-batches/{B}.json',env)
write(f'audits/{B}-v2-author-repair.json',dict(createdAt=datetime.now(timezone.utc).isoformat(),revisedCount=31,newQuestionCount=1,contentRepairs=28,difficultyOnlyRepairs=3,difficultyLabelsLowered=6,preservedAcceptedCount=40,acceptedObjectsUnchanged=True,acceptedReviewHashesPreserved=True,originalKeysUnchanged=True,sourceIssuesUnchanged=True,authorChecks=newchecks,environment={'numpy':np.__version__,'scikitLearn':sklearn.__version__},actualSourcePagesRevisited=[804,805,807,808,811,813,814,815,819],printedFooters=['6 (clipped)','7','9','10','13','15','16 (clipped)','17','21'],coverageRepairs={'distinct-data-and-estimator-seeds':'W06-L27-P0813-Q06','complex-sensor-rule-motivation':'W06-L27-P0819-Q01'},independentReview=False))
if os.environ.get('FREEZE_L27_V2')=='1':
 changedqs=[q for q in b['questions'] if q['id'] in flag or q['id']==B+'-P0813-Q06']
 assert len(changedqs)==32 and len(b['questions'])==72
 blind=[{**{k:q[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions')},'citations':[{k:v for k,v in ci.items() if k!='evidenceText'} for ci in q['citations']]} for q in changedqs]
 write(f'audits/blind-{B}-v2.json',blind);h=hashlib.sha256((R/f'audits/blind-{B}-v2.json').read_bytes()).hexdigest()
 write(f'audits/{B}-v2-review-manifest.json',dict(batchId=B,blindPacket=f'audits/blind-{B}-v2.json',blindPacketSha256=h,questionSha256={q['id']:sha(q) for q in changedqs},preservedAcceptedCount=40,preservedAcceptedHashes={q['id']:sha(q) for q in accepted},revisedCount=31,newQuestionIds=[B+'-P0813-Q06'],sourceIssuesSha256=hashlib.sha256((R/'audits/source-disputes-W06-L27.json').read_bytes()).hexdigest(),independentReviewPending=True))
 (R/f'audits/handoffs/{B}-v2.md').write_text(f'''# L27 v2 frozen for independent re-review\n\n31 flagged questions revised to v2, 40 accepted objects and hashes unchanged. Added P0813-Q06 to distinguish data generation and estimator initialization seeds; extended P0819-Q01 to combine complex-sensor motivation with task alignment. Total 72 questions and 18 concepts.\n\nPacket: audits/blind-{B}-v2.json\nSHA-256: {h}\nManifest: audits/{B}-v2-review-manifest.json\nArchive: {archive}\nScript: scripts/repair_W06_L27_v2.py\nChecks: audits/{B}-v2-author-repair.json\n\nAll original keys and seven source-issue records preserved. Six difficulty labels lowered. Corrected the 4.9 N·m distractor rationale with an explicit 0.5 kg mass-entry error; omitting factor 5 gives 9.8. Corrected p815 above-100%-Wi-Fi evidence to an actual figure citation. Sixteen new author checks pass, including all torque distractors, lifecycle errors, synchronized versus broken row alignment, mixed derivatives and independent random-generator roles under NumPy {np.__version__}/sklearn {sklearn.__version__}. These are author checks, not independent approval. All 23 prior actual inspections retained; nine pages revisited. Frozen-script guard prevents overwriting reviewed work. No canonical or Git writes.\n''')
 print('FROZEN',len(changedqs),h)
