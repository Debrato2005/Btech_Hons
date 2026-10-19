#!/usr/bin/env python3
"""Prefreeze author quality refinement; no independent approval."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1];B='W11-L54';p=R/f'data/question-batches/{B}.json'
assert not (R/f'audits/{B}-review-manifest.json').exists(),'Frozen'
x=json.loads(p.read_text());Q={q['id'].removeprefix(B+'-'):q for q in x['questions']}
def wrong(k,start,text,reason):
 q=Q[k];o=next(o for o in q['options']if o['text'].startswith(start));assert o['id']not in q['correctOptionIds'];o['text']=text;q['solution']['optionExplanations'][o['id']]='Incorrect. '+reason
wrong('P1725-Q04','Removing any row','Refitting the scaler leaves every transformed coordinate unchanged because its output mean is always zero','A zero-mean constraint does not keep the fitted mean, variance or each transformed value identical after row removal.')
wrong('P1728-Q03','stratify sets','stratify fixes the pseudorandom assignment; random_state preserves class proportions','The two roles are reversed.')
wrong('P1736-Q03','random_state=42 forces','The estimator seed also fixes the earlier split, so only the sensor noise needs to be seeded','The split occurs before the estimator consumes its own random_state; that seed does not control the earlier split.')
wrong('P1738-Q04','The model contains','The estimator must complete exactly300 epochs even if its no-improvement criterion triggers earlier','The maximum is a cap, not a mandatory number of completed epochs.')
wrong('P1741-Q05','A smaller learning','A very small learning rate guarantees faster convergence because each update is more accurate','Small steps can require many more updates; smaller does not guarantee faster progress.')
wrong('P1735-Q02','The values prove','The small difference proves that the displayed elbow angle is absolute rather than relative','That alternative changes the second-link orientation substantially; a small rounding-scale difference does not establish it.')
q=Q['P1734-Q03'];q['stem']='A trained model returns angles for the requested point(1.5,1.5)m of the unit-link arm. What must be recognized before commanding the robot?'
o=next(o for o in q['options']if o['id']in q['correctOptionIds']);o['text']='The target is outside the2m radial reach because its base distance is√4.5≈2.12m';q['solution']['optionExplanations'][o['id']]='Correct. Reachability depends on radial distance, not separate coordinate bounds; a numeric prediction cannot extend the links.'
wrong('P1734-Q03','The target is reachable','The target is reachable because each coordinate separately has magnitude below2m','Separate coordinate bounds are necessary but not sufficient for the disk-shaped workspace.')
# Source facts needed to solve a stand-alone item must be present, not hidden in a citation.
Q['P1723-Q02']['stem']='Three synchronized channels are each sampled at1kHz, producing one feature vector per sampling instant. What are the vector interval and total scalar readings per second per joint?'
Q['P1728-Q02']['stem']='The balanced600-row source dataset has300 examples per class and a stratified20% test split. How many examples of each class occur in train and test?'
Q['P1729-Q04']['stem']='For SVC(gamma="scale") with three transformed input features and overall training-matrix variance1, what gamma does the cited API use?'
Q['P1732-Q01']['stem']='The pictured generic network has four input nodes, three hidden nodes and one output node. With fully connected adjacent layers and one bias per non-input node, how many parameters are there?'
Q['P1737-Q02']['stem']='For40000 paired samples, X contains two Cartesian columns and Y contains two angle columns. With test_size=0.1, what are the shapes of X_tr, Y_tr, X_te and Y_te?'
Q['P1738-Q01']['stem']='For the fully connected architecture2→256→256→128→2, with one bias per non-input neuron, how many trainable weights plus biases are there?'
Q['P1738-Q01']['difficulty']='medium'
Q['P1741-Q01']['stem']='For the source planar two-revolute-joint arm, det(J)=L1·L2·sin(θ2). At which endpoint elbow configurations is this Jacobian singular?'
# Replace weak alternatives with common, technically identifiable confusions.
wrong('P1720-Q01','Both joint types','Revolute: angle, angular velocity, force; prismatic: position, linear velocity, torque','The coordinates and rates fit, but the generalized effort is torque for rotation and force for translation.')
wrong('P1720-Q03','Changing acceleration units','One integration of the acceleration channels directly yields absolute position without initial conditions','One integration yields velocity up to an initial velocity; position requires another integration and initial state information.')
wrong('P1721-Q01','Both tools','Vacuum cup: contact pressure measured only by a fingertip load cell; welding torch: torch position alone','Suction pressure is a pneumatic measurement, not merely fingertip force; position alone omits the listed welding-process channels.')
wrong('P1721-Q02','More fingers','A sum of all contact forces preserves every contact location and local force distribution','Aggregation loses spatial distribution even when the total load is preserved.')
wrong('P1721-Q02','An adaptive finger','Joint encoder angles alone uniquely determine each contact force for every object stiffness','The same geometry can have different forces because of stiffness, deformation and actuation.')
wrong('P1721-Q03','Millimetres and','A displacement resolution can be reported as force resolution without specifying sensor stiffness or calibration','A displacement-to-force conversion requires a physical calibration; length resolution alone is insufficient.')
wrong('P1721-Q03','Tremor filtering','Tremor filtering establishes the sensor’s static force resolution regardless of its noise and calibration','A filter can change noise characteristics, but does not by itself define calibrated force resolution.')
wrong('P1722-Q02','It makes an ADC','It can recover the missing distinction by duplicating existing channels as additional input features','Deterministic duplicates add no information about a distinction absent from the original observations.')
wrong('P1724-Q01','SVR cannot','SVR is required because current, speed and temperature are continuous inputs','Classification versus regression is determined by the target type, not by whether features are continuous.')
wrong('P1724-Q02','The outer plot','The dashed line nearest the positive-class points is the zero-score decision boundary','In the canonical margin picture the central separator has score zero; the dashed planes have nonzero margin scores.')
wrong('P1727-Q02','Every generated','The seed fixes only the draw count, so the generated values are unchanged by altering the seed','The seed initializes the pseudorandom sequence and can change the generated values, not merely the number of draws.')
wrong('P1727-Q02','The classifier','The seed also guarantees the same learned score after changing the sampled class distributions','Reusing a seed does not make different data-generating distributions equivalent.')
wrong('P1727-Q03','Replacement of','Per-sample normalization of each row to unit Euclidean norm','StandardScaler fits per-feature means and scales; row-wise unit-norm normalization is a different transform.')
wrong('P1729-Q06','The RBF kernel','The automatic gamma value is multiplied by C, so the RBF similarity directly becomes narrower','C controls the soft-margin penalty; it does not multiply gamma in the kernel definition.')
wrong('P1732-Q02','Replacing the need','Predicting joint angles because displaying a graph implicitly initializes and fits its weights','An architecture display is not a fitted supervised estimator and performs no target-based training.')
wrong('P1733-Q01','Calculate loss','Forward prediction → backpropagate a target-independent gradient → calculate loss → update parameters','The loss and target determine the gradient; backpropagation cannot use a target-independent substitute for that loss derivative.')
wrong('P1733-Q01','Update parameters','Forward prediction → calculate loss → update parameters → backpropagate using only the already-updated weights','A standard gradient step uses derivatives at the current parameters before updating them.')
wrong('P1734-Q04','A positive elbow','Restricting the elbow branch also makes ordinary squared shoulder-angle error periodic','Elbow-branch selection does not change the numerical shoulder loss into a circular distance.')
wrong('P1735-Q01','The trained MLP','The manual pose demonstrates the trained MLP’s mean error over the held-out dataset','One manually controlled configuration is not a held-out statistical evaluation of learned predictions.')
wrong('P1739-Q01','It retrains','It measures exactly the same loss as averaging squared angle errors, so the units are interchangeable','The nonlinear kinematic map and Euclidean position norm differ from angle-space squared loss.')
wrong('P1739-Q01','It converts','It evaluates accuracy by comparing only the predicted elbow angle against the target y coordinate','That comparison mixes an angle with a position and omits the full two-link geometry.')
wrong('P1739-Q05','Radians become','Only link lengths affect that mapping; changing the joint configuration leaves it identical','The Jacobian contains trigonometric functions of the configuration as well as link lengths.')
wrong('P1740-Q01','The outer brackets','The outer brackets are the two-output target dimension rather than the sample dimension','Prediction input is organized by samples then features; output width is determined by the fitted targets.')
wrong('P1740-Q05','The two predicted','The printed angles describe the ideal drawing in degrees rather than radians','The source labels them radians and separately converts them to degrees; changing units cannot reconcile the distinct predictions.')
# Readable quantities and punctuation without changing source evidence, URLs or code files.
def prose(s):
 tokens={}
 def keep(m):
  k='ZZTOKEN'+chr(65+len(tokens)//26)+chr(65+len(tokens)%26)+'ZZ';tokens[k]=m.group();return k
 s=re.sub(r'\b(?:[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+|L1|L2|F1|ReLU|SVC|SVR|MLPRegressor|StandardScaler|2R|2D|3D|1e-3)\b',keep,s)
 s=re.sub(r'(?<=[A-Za-z])(?=\d)',' ',s);s=re.sub(r'(?<=\d)(?=[A-Za-zµΩ])',' ',s)
 s=re.sub(r'([,;])(?=\S)',r'\1 ',s)
 s=re.sub(r'(?<=\d)(?=°C)',' ',s)
 s=re.sub(r'(?<=[A-Za-z])(?=[πθ√])',' ',s)
 s=re.sub(r'(?<=[A-Za-z])\(', ' (',s)
 s=re.sub(r'\)(?=m\b)',') m',s)
 s=s.replace('and−','and −').replace('and+','and +').replace('errors+','errors +').replace('near−','near −').replace('sinθ','sin θ')
 for a,b in [('1 ms;3000','1 ms; 3000'),('m.','m.'),('case.','case.')]:s=s.replace(a,b)
 for k,v in tokens.items():s=s.replace(k,v)
 return s
for q in Q.values():
 for k in ['stem','subtopic']:q[k]=prose(q[k])
 q['assumptions']=[prose(s)for s in q['assumptions']]
 for o in q['options']:o['text']=prose(o['text'])
 so=q['solution'];so['steps']=[prose(s)for s in so['steps']];so['optionExplanations']={k:prose(v)for k,v in so['optionExplanations'].items()}
 so['justification']=' '.join(so['optionExplanations'][k].removeprefix('Correct. ')for k in q['correctOptionIds']);so['simpleExplanation']=so['justification'];so['misconceptions']=[v.removeprefix('Incorrect. ')for k,v in so['optionExplanations'].items()if k not in q['correctOptionIds']]
 for f in so['formulas']:
  f['variables']={k:prose(v)for k,v in f['variables'].items()};f['assumptions']=[prose(s)for s in f['assumptions']]
 for c in q['citations']:c['locator']=prose(c['locator'])
 if q.get('conflictResolution'):
  for k in ['sourceClaim','basis','method','scope']:q['conflictResolution'][k]=prose(q['conflictResolution'][k])
p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');print('Refined',len(Q),'drafts')
