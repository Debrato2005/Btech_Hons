#!/usr/bin/env python3
"""Version 17 flagged items, close 3 bounded gaps, preserve 70 accepted objects exactly."""
from pathlib import Path
import json,copy,hashlib,datetime
R=Path(__file__).resolve().parents[1];B='W11-L54';A='L54-v2-repair-author-20261020';SHA='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ('status','reviewIds')},ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
assert not (R/f'audits/{B}-v2-repair-manifest.json').exists(),'Frozen. Make a new versioned repair, never overwrite.'
orig=read(f'audits/archive/{B}-v1-before-v2/{B}.json');b=copy.deepcopy(orig);Q={q['id']:q for q in b['questions']};origQ={q['id']:q for q in orig['questions']};current={q['id']:q for q in read(f'data/question-batches/{B}.json')['questions']}
accepted=read(f'audits/{B}-later-duplicate-review-summary.json')['acceptedQuestionHashes'];flagged=set(Q)-set(accepted);assert len(accepted)==70 and len(flagged)==17
for qid,h in accepted.items():
 assert qhash(current[qid])==qhash(Q[qid])==h
 Q[qid].clear();Q[qid].update(copy.deepcopy(current[qid]))
issuehash=sha(f'audits/source-disputes-{B}.json');assert issuehash==sha(f'audits/archive/{B}-v1-before-v2/source-disputes-{B}.json')
changed=[];notes={}
def q(s):return Q[B+'-'+s]
def revise(s,note):
 z=q(s);assert z['id']in flagged;z['version']=2;z['status']='draft';z['reviewIds']=[];z['revisionAuthors']=list(dict.fromkeys(z.get('revisionAuthors',[])+[A]));changed.append(z);notes[z['id']]=note;return z
def op(z,oid,text,why):
 next(o for o in z['options']if o['id']==oid)['text']=text;z['solution']['optionExplanations'][oid]=('Correct. 'if oid in z['correctOptionIds']else'Incorrect. ')+why
def why(z,text):z['solution']['justification']=text;z['solution']['simpleExplanation']=text

def cite(p,k,loc,evidence,role='premise'):
 return dict(slideId=f'lectures-p{p}',sourceId='lectures',sourceSha256=SHA,physicalPage=p,kind=k,locator=f'Printed slide {p-1714}: {loc}',evidenceText=evidence,role=role,region=None)
def fk():return cite(1734,'equation','Displayed x and y forward-kinematics equations','x = L1 cos(θ1) + L2 cos(θ1+θ2); y = L1 sin(θ1) + L2 sin(θ1+θ2).')
def links():return cite(1731,'statement','Two-link example dimensions and input/output description','L1 = L2 = 1 m; input (x,y), output (θ1,θ2).')
def fit():return cite(1730,'code','Upper training/prediction block: fit on training arrays, predict on held-out features','svm.fit(X_tr, y_tr); y_pred = svm.predict(X_te).')
def report():return cite(1730,'code','classification_report call and target_names argument','classification_report(y_te, y_pred, target_names=["normal", "overload"])')
def f(expr,var,units,assume):return dict(expression=expr,variables=var,units=units,assumptions=assume)
FK=copy.deepcopy(q('P1734-Q01')['solution']['formulas'][0])
ERR=f('e_m=√((x_p−x_t)²+(y_p−y_t)²); e_cm=100 e_m',{'x_p,y_p':'Predicted Cartesian endpoint','x_t,y_t':'Target endpoint','e_m':'Single-sample Euclidean error in metres','e_cm':'Same error in centimetres'},{'x_p,y_p,x_t,y_t,e_m':'m','e_cm':'cm'},['All positions use the same fixed base frame; 1 m = 100 cm.'])
z=revise('P1720-Q02','Parallel nonexclusive sensor-to-application alternatives.')
z['stem']='Which three sensor-to-application pairings match the table’s listed examples? Treat these as examples, not exclusive sensor capabilities.'
op(z,'o1','Encoder angle → IK data; torque → fault detection; load-cell force → grasp control','These are the three associations listed in the source table.')
op(z,'o2','Encoder angle → fault detection; torque → grasp control; load-cell force → IK data','These are plausible signals for some broader systems, but this permutation does not reproduce the table’s stated examples.')
op(z,'o3','Encoder angle → grasp control; torque → IK data; load-cell force → fault detection','This permutation also differs from the particular application associations requested; the question does not prohibit those signals from helping other tasks.')
why(z,'The table pairs encoder angle with IK, torque with fault detection, and load-cell force with grasp control. The mapping is source-specific, not a claim of exclusivity.')
z=revise('P1721-Q01','Same-tool alternatives instead of cross-domain measurement swaps.')
z['stem']='Which pair reproduces the listed measurements for the vacuum gripper and welding torch, rather than proposing a different sensing scheme?'
op(z,'o1','Vacuum gripper: air-flow rate for seal inference; welding torch: current, voltage and wire-feed rate','Flow can help assess a vacuum seal, but the source specifically lists suction pressure for this gripper.')
op(z,'o2','Vacuum gripper: suction pressure; welding torch: current, voltage and wire-feed rate','This matches the two source rows, including the welding-process measurements.')
op(z,'o3','Vacuum gripper: suction pressure; welding torch: torch position and orientation','Pose sensing is useful, but it does not reproduce the listed electrical and feed-rate process channels.')
why(z,'The requested source pairing is suction pressure for the vacuum tool and current, voltage and feed rate for welding. Other useful sensing schemes are not ruled out.')
z=revise('P1728-Q03','Contextualize the generic colliding stem without changing the split concept or key.')
z['stem']='In the motor-fault train_test_split call, how do stratify=y and random_state=42 differ in their roles?'
z=revise('P1729-Q01','Bind the held-out fitting boundary to the actual fit/predict code.')
z['citations'].append(fit())
z=revise('P1729-Q07','Use a coherent dot-product-versus-RBF kernel misconception.')
op(z,'o2','The RBF kernel is the dot product of the standardized sensor vectors, so its input-space boundary must remain a plane','A plain dot product defines the linear kernel, not the RBF similarity; standardization does not turn an RBF into a linear kernel.')
z['citations'][0]['locator']='Printed slide 15: RBF kernel explanation and nonlinear-boundary bullet'
z['stem']='Why can the code’s RBF SVC have a nonlinear input-space boundary even though the introductory SVM picture shows a straight separator?'
z=revise('P1730-Q07','Use class-order/display-name alternatives.')
z['stem']='The source labels normal as 0 and overload as 1 and passes target_names=["normal", "overload"] to classification_report without labels=. Which report-row interpretation is correct?'
op(z,'o1','The overload row reports class 0 metrics because target_names is paired with classes in descending numeric order','With these labels the default report order is 0, then 1; it is not descending.')
op(z,'o2','Reversing target_names would still leave normal on class 0 because display names are sorted alphabetically','Reversing the supplied names would reverse the displayed names associated with the fixed label order; the API does not independently alphabetize them.')
op(z,'o3','The overload row reports class 1 precision, recall, F1 and true-label support','The second supplied name aligns with label 1; these are per-class metrics and support, not a relabeling or refitting operation.')
why(z,'The label order is 0 then 1, and target_names supplies matching display names in that order. Thus overload identifies class 1.')
z=revise('P1732-Q02','Distinguish generic architecture display from initialized or fitted estimator state.')
z['stem']='What does the displayed mglearn.plot_single_hidden_layer_graph() call establish, separate from importing MLPRegressor?'
op(z,'o1','It creates an unfitted MLPRegressor configured with the later 256, 256, 128 hidden widths','A generic diagram call is not construction of that estimator; the later model constructor supplies those widths.')
op(z,'o2','It visualizes the fitted connection weights of the later robot-arm regressor','No fitted robot-arm model is passed to this illustrative graph function, so the drawing is not evidence of fitted weights.')
op(z,'o3','It displays a generic architecture graph, without configuring or fitting the later robot-arm regressor','The graph illustrates network structure; estimator construction and model.fit are separate operations.')
why(z,'An illustrative graph is neither the later configured estimator nor its fitted weights. No training arrays or fitted regressor are supplied to this call.')
z=revise('P1734-Q01','Correct author-written endpoint units to metres and explicitly bind unit links.')
for o in z['options']:o['text']=o['text'].replace(' mm',' m')
z['assumptions']+=['L1=L2=1 m; all Cartesian coordinates are in metres.'];z['citations'].append(links())
z['solution']['steps']=['θ1+θ2 = π/2 rad.','x = cos(π/6)+cos(π/2) = √3/2 m.','y = sin(π/6)+sin(π/2) = 1.5 m.']
z=revise('P1734-Q02','Correct target units, supply link lengths, and check branch plus closure.')
z['stem']='For L1=L2=1 m, which supplied angle pair (θ1, θ2), in radians, reaches (1, 1) m and belongs to the lecture’s nonnegative-elbow branch?'
z['assumptions']+=['All Cartesian coordinates are metres; L1=L2=1 m.'];z['citations'].append(links());z['citations'].append(fk())
why(z,'The pair (0, π/2) gives link vectors (1, 0) m and (0, 1) m and lies within the selected elbow range.')
z['solution']['optionExplanations']['o2']='Correct. Its two link vectors sum to (1, 1) m, and θ2=π/2 lies in [0, π].'
z['solution']['steps']=['(0, π/2) gives (1, 1) m and θ2≥0.','(π/2, −π/2) also gives (1, 1) m, but violates θ2∈[0, π].','(π/2, π/2) gives (−1, 1) m, which is the wrong target.']
z=revise('P1734-Q03','Correct target units; label radial reach as a derivation from FK, not a printed formula.')
z['stem']='For a fixed-base arm with L1=L2=1 m, an IK regressor returns angles for target (1.5, 1.5) m. What must be recognized before accepting those angles as a solution?'
z['assumptions']=['Rigid planar links of length 1 m each; no translating base or extra axis; target is expressed in the base frame.']
op(z,'o3','Clipping each requested coordinate into [−2, 2] m is sufficient to make this target reachable','Coordinate-wise clipping leaves this point unchanged but does not enforce the circular radial bound.')
z['citations']=[fk(),links()];z['type']='numerical';z['cognitiveSkill']='application'
z['solution']['steps']=['From the two link vectors, triangle inequality gives r≤L1+L2=2 m.','The requested radius is √(1.5²+1.5²)=√4.5≈2.1213 m.','Since 2.1213>2, no returned joint angles can close this target under the stated geometry.']
z=revise('P1735-Q02','Correct rendered coordinates to metres and distinguish small rounding differences from unit errors.')
z['stem']='The panel shows 1 m links, angles 27.9° and 90.1°, and endpoint (0.415, 1.351) m. Treating the rounded angles as inputs gives approximately (0.4143, 1.3509) m by FK. How should this small difference be interpreted?'
z['assumptions']+=['The two coordinates and link lengths are in metres, as labeled on the panel; relative elbow angle and fixed base frame.'];z['citations'].append(fk())
z['solution']['formulas'][1]['expression']='θ_rad=θ_deg·π/180; θ_deg=θ_rad·180/π'
z['solution']['steps']=['Convert the displayed angles to radians using π/180.','Their sum is 118.0°; evaluate the two-link FK to get approximately (0.4143, 1.3509) m.','Compare with the separately rounded panel values. Differences are about 0.0007 m and 0.0001 m, not a thousandfold unit conversion.']
why(z,'Separately rounded angle and position labels need not agree exactly. These sub-millimetre-scale coordinate differences are consistent with display precision; all compared lengths here are metres.')
z['solution']['optionExplanations']['o3']='Correct. The displayed inputs and outputs are rounded independently, so the small coordinate differences do not establish a different angle convention or erroneous geometry.'
z=revise('P1737-Q01','Replace duplicate input/output recall with the complete branch-aware inverse-regression decision gap.')
z['stem']='For a fixed-base 2R arm with L1=L2=1 m, target (1, 1) m has reference angles q*=(0, π/2). Three supplied regressor outputs in radians are A=(π/2, −π/2), B=(π/6, π/2), and C=(0, π/3). First reject outputs outside θ1∈[−π, π], θ2∈[0, π]; among the rest choose the smallest Euclidean Cartesian error after FK. For comparison, angle MSE is ((θ1−θ1*)²+(θ2−θ2*)²)/2 without angle wrapping. Which assessment is correct?'
z['type']='synthesis';z['cognitiveSkill']='synthesis';z['difficulty']='medium';z['assumptions']=['All three angle outputs are supplied examples, not fresh model predictions or accuracy claims.','Rigid planar links; all Cartesian positions are metres in the same base frame; positive counterclockwise shoulder and relative elbow angles.','Only the stated joint ranges and position-error criterion are imposed; no additional obstacles or actuator constraints.','The reference and MSE use the stated angle representatives, with no wrap minimization.']
op(z,'o1','Choose A: its Cartesian error is zero, so it wins even though its elbow angle is negative','A reaches the target, but the explicit first-stage branch filter rejects its θ2=−π/2 before comparing position errors.')
op(z,'o2','Choose C: B and C have equal angle MSE, but their position errors are about 0.732 m and 0.518 m; A fails the branch filter','B and C each differ from q* in one angle by π/6, yet their FK errors differ; C has the smaller admissible task-space error.')
op(z,'o3','Treat B and C as tied: equal angle MSE forces equal Cartesian position error, while A fails the branch filter','FK is nonlinear and direction-dependent. Equal squared joint-angle error does not imply equal endpoint distance from this target.')
why(z,'A is rejected by the branch condition despite exact position closure. B and C both have angle MSE π²/72 rad², but their Cartesian errors are √3−1≈0.732 m and √(2−√3)≈0.518 m, so C wins.')
z['solution']['steps']=['The target radius √2 m is within the 2 m maximum reach, and q* closes it on the permitted branch.','A gives (1, 1) m but θ2=−π/2 is outside [0, π].','B gives ((√3−1)/2, (1+√3)/2) m and error √3−1≈0.73205 m.','C gives (1.5, √3/2) m and error √(2−√3)≈0.51764 m.','For B and C, one angle differs from q* by π/6 while the other is exact, so both angle MSEs equal π²/72 rad². Choose C by the stipulated Cartesian criterion.']
z['solution']['formulas']=[copy.deepcopy(FK),copy.deepcopy(ERR),f('MSE_q=((θ1−θ1*)²+(θ2−θ2*)²)/2',{'MSE_q':'Mean squared joint-angle error over the two outputs','θ1,θ2':'Predicted shoulder and relative elbow angles','θ1*,θ2*':'Reference shoulder and relative elbow angles'},{'MSE_q':'rad²','θ1,θ2,θ1*,θ2*':'rad'},['Two equally weighted joint outputs; angle representatives are not wrapped.']),f('r=√(x_t²+y_t²); r≤L1+L2',{'r':'Target distance from fixed base','x_t,y_t':'Target coordinates','L1,L2':'Positive link lengths'},{'r,x_t,y_t,L1,L2':'m'},['The radial inequality is a necessary geometric reach condition for the two rigid links.'])]
z['citations']=[links(),fk(),cite(1734,'statement','Specified shoulder/elbow sampling ranges','θ1∈[−π, π], θ2∈[0, π].'),cite(1733,'statement','Loss computation stage of training diagram','Mean squared error (MSE).'),cite(1737,'code','X and Y column_stack assignments','X=np.column_stack([x,y]); Y=np.column_stack([t1,t2]).'),cite(1739,'code','Predicted-angle FK and Euclidean error evaluation','pred=model.predict(X_te); err=np.sqrt((xp-X_te[:,0])**2+(yp-X_te[:,1])**2).')]
z['conceptIds']=['W11-L54-C-ik-data'];z['subtopic']='Branch-aware IK prediction and task-space assessment';z['tags']=['robot-arm-ml','ik-dataset','integrated-gap-L54-G02']
z=revise('P1738-Q01','Correct weights-only rationale and bind the two input/output dimensions.')
z['solution']['optionExplanations']['o3']='Incorrect. 99072 counts weights only; omitting 642 biases from the total gives this value. Adding those biases yields 99714.'
z['citations'][0]['locator']='Printed slide 24: hidden_layer_sizes=(256, 256, 128) in MLPRegressor constructor';z['citations'].append(links())
z=revise('P1739-Q03','Explicitly distinguish raw unit-inappropriate print output from physical millimetre residuals.')
z['stem']='Two supplied Cartesian residual vectors are (0.03, 0.04) mm and (0, 0) mm. Their raw numeric components are passed unchanged to the slide’s Euclidean-distance code, then to print(f"{err.mean()*100:.2f} cm"). What pair gives the literal printed output and the physically correct mean error in centimetres?'
z['assumptions']=['This is a deliberately unit-inappropriate supplied-input scenario; the source itself uses metre-valued Cartesian geometry.','The two residual vectors share the same base frame; arithmetic has no automatic unit metadata; exactly two samples are averaged.']
op(z,'o1','Literal print: 0.00 cm; physical mean: 0.0025 cm','The physical mean rounds to 0.00 cm at two decimal places, but the unmodified code is given raw millimetre numbers and does not automatically perform that conversion.')
op(z,'o2','Literal print: 2.50 cm; physical mean: 0.0025 cm','Raw distances 0.05 and 0 average to 0.025, then the unchanged multiplier prints 2.50 cm. Physically, 0.025 mm is 0.0025 cm.')
op(z,'o3','Literal print: 2.50 cm; physical mean: 2.50 cm','The printed label cannot change the physical input unit. The raw numeric multiplier is appropriate for metres, not these supplied millimetre residuals.')
why(z,'The literal code prints 2.50 cm, but that label is wrong for this deliberately mismatched input. The true mean is 0.025 mm = 0.0025 cm; the original metre-based source calculation is not being called erroneous.')
z['solution']['steps']=['Physical distances are √(0.03²+0.04²)=0.05 mm and 0 mm.','The physical mean is (0.05+0)/2=0.025 mm; divide by 10 to obtain 0.0025 cm.','The array stores only the numbers 0.05 and 0; its mean is 0.025.','The unchanged print expression multiplies that raw number by 100 and formats it as 2.50 cm, without knowing that the numbers represented millimetres.']
z['solution']['formulas']=[f('e_i=√(Δx_i²+Δy_i²); ē_mm=(e_1+e_2)/2; ē_cm=ē_mm/10; p=100·mean(e_raw)',{'e_i':'Physical norm of residual i','Δx_i,Δy_i':'Physical Cartesian residual components','ē_mm':'Physical mean expressed in millimetres','ē_cm':'Same physical mean expressed in centimetres','e_raw':'Unitless stored numeric values of the millimetre distances','p':'Numeric value formatted by the unmodified print call','i':'Sample index, 1 or 2'},{'e_i,Δx_i,Δy_i,ē_mm':'mm','ē_cm':'cm','e_raw,p,i':'dimensionless stored number/index'},['Exactly two samples; same base frame; 10 mm = 1 cm; no automatic unit conversion in the numeric array.'])]
z['citations']=[cite(1739,'code','Euclidean norm, mean, and literal *100 centimetre print','err=np.sqrt((xp-X_te[:,0])**2+(yp-X_te[:,1])**2); print(f"Mean position error: {err.mean()*100:.2f} cm")'),links()]
z=revise('P1740-Q02','Correct requested Cartesian units and state the 1 m link premise.')
z['stem']='For L1=L2=1 m and the source branch θ2∈[0, π], which angle pair (θ1, θ2), in radians, exactly reaches (−1, 1) m?'
z['assumptions']+=['Both links are 1 m long and all Cartesian coordinates are metres.'];z['citations']+=[links(),fk()]
z['solution']['steps']=['For (π/2, π/2), the first link contributes (0, 1) m and the second (−1, 0) m.','Their sum is (−1, 1) m, and the elbow lies in [0, π].','The alternatives reach (1, 1) m and (−2, 0) m, respectively.']
z=revise('P1740-Q04','Correct endpoint units and narrow the formula metadata to one historical prediction error.')
z['stem']='Using the historical rounded prediction θ1=1.6773 rad, θ2=1.5809 rad for L1=L2=1 m gives FK endpoint approximately (−1.09951, 0.87799) m. Relative to target (−1, 1) m, what is the single-sample Euclidean position error, rounded to 0.01 cm?'
z['citations']+=[fk(),links(),cite(1739,'code','Cartesian Euclidean norm used for predicted-angle validation','err=np.sqrt((xp-X_te[:,0])**2+(yp-X_te[:,1])**2).')]
z['solution']['formulas']=[copy.deepcopy(FK),copy.deepcopy(ERR)]
z['solution']['steps']=['Evaluate FK at the historical rounded angles to obtain approximately (−1.09950999, 0.87798903) m.','Subtract target (−1, 1) m: residual approximately (−0.09950999, −0.12201097) m.','The Euclidean norm is approximately 0.1574447 m; multiplying by 100 gives 15.74447 cm, rounded to 15.74 cm.']
why(z,'The component errors are approximately −9.95 cm and −12.20 cm; their Euclidean norm is 15.74 cm. This is one historical target, not the separate 9.82 cm test-set mean.')
z['solution']['optionExplanations']['o2']='Correct. Combining both metre-valued residual components by the Euclidean norm and converting to centimetres gives 15.74 cm.'
z=revise('P1741-Q01','Bind the retained Jacobian derivation to the actual FK equation premise.')
z['citations'].append(fk());z['solution']['steps'].insert(0,'Differentiate the two FK coordinates with respect to θ1 and θ2; the resulting 2×2 Jacobian determinant simplifies to L1 L2 sin(θ2).')
# The two genuinely new items close the remaining bounded synthesis/report gaps.
def new(s,base,stem,concept):
 z=copy.deepcopy(q(base));z['id']=B+'-'+s;z['version']=1;z['authorId']=A;z.pop('revisionAuthors',None);z['status']='draft';z['reviewIds']=[];z['stem']=stem;z['conceptIds']=[concept];z['type']='numerical';z['difficulty']='medium';z['cognitiveSkill']='synthesis';z['primaryEvidence']=[];z.pop('conflictResolution',None);z['solution']={'justification':'','optionExplanations':{},'steps':[],'formulas':[],'simpleExplanation':'','memoryAid':None,'misconceptions':[],'examTraps':[],'prerequisiteConceptIds':[]};b['questions'].append(z);Q[z['id']]=z;changed.append(z);return z
z=new('P1729-Q08','P1729-Q01','A supplied RBF decision-rule demonstration uses training means μ=(2 A, 1500 rpm, 40 °C) and scales σ=(0.5 A, 100 rpm, 5 °C). A new measurement is x=(2.5 A, 1400 rpm, 45 °C). Compute z_j=(x_j−μ_j)/σ_j, then K(z,v)=exp(−γ||z−v||²) with standardized support vectors v1=(1, −1, 1), v2=(0, 0, 0), γ=ln(2)/3, signed coefficients c1=2, c2=−1, and intercept b=−1.25. Score s=c1 K(z,v1)+c2 K(z,v2)+b; classify overload for s>0, otherwise normal. Which complete trace is correct?','W11-L54-C-svm-pipeline')
z['correctOptionIds']=['o1'];z['options']=[{'id':'o1','text':'z=(1, −1, 1); kernels (1, 0.5); score 0.25; overload'},{'id':'o2','text':'z=(2.5, 1400, 45); kernels approximately (0, 0); score −1.25; normal'},{'id':'o3','text':'z=(1, −1, 1); kernels (1, 0.5); score 1.25; overload'}]
z['solution']['optionExplanations']={'o1':'Correct. Standardization gives the first support vector exactly; the second squared distance is 3, and the signed score is 2−0.5−1.25=0.25.','o2':'Incorrect. This feeds raw, differently scaled measurements into a standardized support-vector space and omits the required centering/scaling.','o3':'Incorrect. This adds the second similarity with coefficient +1 instead of the supplied signed coefficient −1.'}
z['assumptions']=['All statistics, support vectors, coefficients, intercept and score convention are supplied for this hand-checkable exercise, not recovered parameters or output of the source-trained model.','The supplied fixed gamma deliberately replaces gamma="scale" for this exercise.',
'The supplied coefficients define this hand-checkable score; no claim is made that they solve the SVC training optimization problem.','Feature order is current, speed, temperature; statistics are training-only and fixed; all three positive scales are supplied.','Temperature differences use degrees Celsius; standardized coordinates, kernel values and scores are dimensionless.']
why(z,'After scaling all three channels, z=(1, −1, 1). Its squared distances are 0 and 3, giving kernels 1 and 1/2. Applying the signed coefficients and intercept yields score 0.25, hence overload under the supplied convention.')
z['solution']['steps']=['z=((2.5−2)/0.5, (1400−1500)/100, (45−40)/5)=(1, −1, 1).','||z−v1||²=0 and ||z−v2||²=1+1+1=3.','K1=exp(0)=1; K2=exp(−ln(2))=0.5.','s=2×1+(−1)×0.5−1.25=0.25>0, so classify overload.']
z['solution']['formulas']=[f('z_j=(x_j−μ_j)/σ_j; K_i=exp(−γΣ_j(z_j−v_ij)²); s=Σ_i c_i K_i+b',{'x_j':'Raw measurement in feature j','μ_j,σ_j':'Fixed training mean and positive standard deviation for feature j','z_j':'Standardized feature','v_ij':'Feature j of standardized support vector i','γ':'Positive RBF width parameter','K_i':'Similarity to support vector i','c_i':'Signed coefficient for support vector i','b':'Score intercept','s':'Decision score','i':'Support-vector index 1 or 2','j':'Feature index 1 through 3'},{'x_1,μ_1,σ_1':'A','x_2,μ_2,σ_2':'rpm','x_3,μ_3,σ_3':'°C (σ is a temperature difference)','z_j,v_ij,γ,K_i,c_i,b,s,i,j':'dimensionless'},['Three features in the stated order; two supplied support vectors; positive scales and gamma; fixed supplied score convention.'])]
z['citations']=[cite(1729,'code','Pipeline constructor: StandardScaler followed by RBF SVC','Pipeline([("sc", StandardScaler()), ("svc", SVC(kernel="rbf", C=10, gamma="scale", class_weight="balanced"))])'),fit()]
z['primaryEvidence']=[{'title':'StandardScaler feature transformation','url':'https://scikit-learn.org/1.8/modules/generated/sklearn.preprocessing.StandardScaler.html','version':'scikit-learn 1.8.0','locator':'Class description: training means/scales and z=(x-u)/s.','checkedAt':'2026-10-20'},{'title':'SVC kernel decision function','url':'https://scikit-learn.org/1.8/modules/svm.html','version':'scikit-learn 1.8.0','locator':'Mathematical formulation and RBF kernel sections; supplied example coefficients are not source-trained values.','checkedAt':'2026-10-20'}];notes[z['id']]='L54-G01: full scaled two-support-vector decision.'
z=new('P1730-Q08','P1730-Q07','For a supplied held-out report, normal has support 80 and recall 0.90, while overload has support 20 and recall 0.50. Macro recall gives each class equal weight; support-weighted recall uses true-label supports. What are (macro recall, support-weighted recall)?','W11-L54-C-fault-evaluation')
z['correctOptionIds']=['o3'];z['options']=[{'id':'o1','text':'(0.82, 0.70)'},{'id':'o2','text':'(0.70, 0.70)'},{'id':'o3','text':'(0.70, 0.82)'}]
z['solution']['optionExplanations']={'o1':'Incorrect. This reverses the unweighted and support-weighted aggregations.','o2':'Incorrect. It ignores the unequal supports when computing the second quantity.','o3':'Correct. The equal-class mean is 0.70; weighting normal four times as heavily gives 0.82.'}
z['assumptions']=['The supports and recalls are supplied for a new example, not values read from a printed table or fresh training output.','Both classes have positive support and the recall values are exact for this exercise; normal is label 0, overload label 1.']
why(z,'Macro recall is (0.90+0.50)/2=0.70. Support-weighted recall is (80×0.90+20×0.50)/100=0.82. A perfectly classified demonstration gives 1 for both and does not reveal this distinction; equal supports would also make these two means coincide.')
z['solution']['steps']=['Treat each class once for macro recall: (0.90+0.50)/2=0.70.','Count 72 correctly recalled normal and 10 correctly recalled overload samples.','Divide their total by total support: (72+10)/(80+20)=0.82.']
z['solution']['formulas']=[f('R_macro=(Σ_k R_k)/K; R_weighted=(Σ_k n_k R_k)/(Σ_k n_k)',{'R_macro':'Unweighted mean of class recalls','R_weighted':'Support-weighted mean of class recalls','R_k':'Recall of class k','n_k':'Number of true samples of class k','K':'Number of included classes','k':'Class index'},{'R_macro,R_weighted,R_k':'dimensionless','n_k':'samples','K,k':'dimensionless count/index'},['Positive total support; class recalls are defined; K=2 in this example.'])]
z['citations']=[report()];z['primaryEvidence']=[{'title':'classification_report averaging definitions','url':'https://scikit-learn.org/1.8/modules/generated/sklearn.metrics.classification_report.html','version':'scikit-learn 1.8.0','locator':'Returns section: macro is the unweighted per-label mean; weighted uses support.','checkedAt':'2026-10-20'}];notes[z['id']]='L54-G03: support-weighted versus equal-class recall, with feasible imbalanced counts.'
for suffix in ['P1738-Q01','P1740-Q04','P1730-Q08']:
 q(suffix)['difficulty']='easy'
# Synchronize only changed solution misconception summaries, not approved question content.
for z in changed:
 z['solution']['misconceptions']=[v.removeprefix('Incorrect. ') for k,v in z['solution']['optionExplanations'].items()if k not in z['correctOptionIds']]
 assert set(z['solution']['optionExplanations'])=={o['id']for o in z['options']}
 assert len({o['text']for o in z['options']})==len(z['options'])
 assert not any(' mm' in str(z[k])for k in ['stem','options'] )or z['id'].endswith('P1739-Q03')
 assert z['status']=='draft'and not z['reviewIds']
assert {z['id']for z in changed if z['version']==2}==flagged
assert len(changed)==19 and len(b['questions'])==89
for qid,h in accepted.items():assert Q[qid]==current[qid]and qhash(Q[qid])==h
for c in b['concepts']:
 c['questionIds']=[z['id']for z in b['questions']if c['id']in z['conceptIds']]
 if c['id']=='W11-L54-C-svm-pipeline':c.setdefault('examinationAngles',[]).append('Supplied three-channel scaling through signed two-support-vector RBF decision.')
 if c['id']=='W11-L54-C-ik-data':c.setdefault('examinationAngles',[]).append('Supplied branch filtering and Cartesian-error comparison versus equal angle MSE.')
 if c['id']=='W11-L54-C-fault-evaluation':c.setdefault('examinationAngles',[]).append('Macro versus support-weighted recall with unequal class supports.')
assert all(any(c['id']==cid for c in b['concepts'])for z in b['questions']for cid in z['conceptIds'])
b['coverageNote']='89 current questions: 70 accepted objects preserved exactly; 17 versioned repairs plus 2 new bounded-gap items await independent review. One replacement closes the integrated IK gap. Existing 30 actual source inspections and 12 qualifications are preserved.'
write(f'data/question-batches/{B}.json',b)
write(f'audits/{B}-v2-author-repair-notes.json',{'changedQuestionIds':[z['id']for z in changed],'acceptedQuestionHashes':accepted,'notes':notes,'sourceQualificationSha256':issuehash,'sourceQualificationsUnchanged':True,'authorTextUnitErrorsNotSourceConflicts':True,'actualRevisits':16,'uniqueInspectionCountUnchanged':30,'independentReviewPending':True})
print('SAVED',len(b['questions']),'questions;',len(changed),'changed packet items;',len(accepted),'accepted hashes preserved')
