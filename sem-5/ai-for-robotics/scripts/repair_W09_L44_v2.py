"""One-time L44 quality repairs and bounded coverage additions; not a review."""
from pathlib import Path
import copy, json, hashlib, datetime, sys
R=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(R/'scripts'))
from validate import question_hash, schema_errors
from authoring_helpers import formula
p=R/'data/question-batches/W09-L44.json'; before=json.loads(p.read_text()); b=copy.deepcopy(before)
qs={int(q['id'][-3:]):q for q in b['questions']}
reviews=json.loads((R/'data/reviews/W09-L44-v1-independent.json').read_text())
changed=[int(r['questionId'][-3:]) for r in reviews if r['decision']=='flagged']
accepted={r['questionId']:r['questionSha256'] for r in reviews if r['decision']=='verified'}
assert len(changed)==21 and len(accepted)==68 and all(qs[n]['version']==1 for n in changed)
archive=R/'audits/batch-history/W09-L44-pre-v2.json'; assert not archive.exists(); archive.write_text(p.read_text())
AUTHOR='build_robotics_study_app:L44-v2-author'
def opt(n,i,text,why):
 q=qs[n]; next(o for o in q['options'] if o['id']==f'o{i}')['text']=text; q['solution']['optionExplanations'][f'o{i}']=why
def replace(n,options,exps,stem=None,why=None):
 for i,(s,e) in enumerate(zip(options,exps),1): opt(n,i,s,e)
 if stem: qs[n]['stem']=stem
 if why: qs[n]['solution']['justification']=qs[n]['solution']['simpleExplanation']=why
def cite(n,page,desc,kind='statement',role='premise'):
 q=qs[n]; c=next((c for c in q['citations'] if c['physicalPage']==page),None)
 if c is None: c=copy.deepcopy(q['citations'][0]);q['citations'].append(c)
 c.update(slideId=f'lectures-p{page}',physicalPage=page,kind=kind,role=role,locator=f'Lecture L44, physical PDF page {page}, printed footer {page-1369}: {desc}',evidenceText=(R/f'sources/text/lectures/page-{page}.txt').read_text().strip())
 for co in b['concepts']:
  if co['id'] in q['conceptIds'] and c['slideId'] not in co['slideIds']: co['slideIds'].append(c['slideId'])
replace(5,[
 'Satellite signals can be blocked or degraded, so other information is needed for reliable localization.',
 'The receiver may retain its last outdoor fix; treating that stale fix as a current position removes the indoor localization problem.',
 'A correctly surveyed indoor map guarantees usable satellite reception, so only map calibration needs attention.',
 'A higher requested GPS update frequency guarantees recovery of the obstructed satellite measurements.'
],[
 'The source identifies blocked satellite signals as the indoor and urban-canyon limitation.',
 'A retained old fix is not a new observation of the moving robot.',
 'Map accuracy does not restore a blocked radio path.',
 'Requesting more frequent output does not itself make unavailable signals observable.'
])
opt(13,3,'Infer the ranging principle from the 5.5 Hz spin rate alone, because scan rotation uniquely distinguishes time-of-flight from triangulation.','Rotation rate describes scanning, not a unique distance-measurement principle.')
opt(13,4,'Treat the roughly 12 m example range and 360 samples as guarantees for every device in the product family.','The slide gives an unspecified example, not a family-wide specification.')
opt(15,2,'A heading change of 30°, by using the rate value as the accumulated angle.','This omits multiplication by the two-second duration.')
qs[15]['solution']['formulas']=[formula('Δθ = ∫ω(t)dt = ωΔt for constant ω',{'Δθ':'heading change','ω':'angular rate','Δt':'elapsed time'},{'Δθ':'degrees','ω':'degrees per second','Δt':'seconds'},['Constant unbiased rate; an initial heading is required for the absolute final heading.'])]
replace(19,[
 'Both are global localization, because possessing a map is the defining condition in both cases.',
 'Both are position tracking, because either task can use repeated measurements after motion starts.',
 'Global localization, compared with position tracking.',
 'Position tracking, compared with global localization.'
],[
 'Map availability alone does not distinguish the two source definitions; initial pose knowledge does.',
 'Repeated measurements do not turn an initially unknown pose into a known initial-pose premise.',
 'The source distinguishes the tasks by the amount of initial pose knowledge.',
 'This reverses the stated definitions.'
])
opt(23,1,'Yes; with a fixed future control, present velocity cannot change the next-position distribution.','A fixed control does not remove the explicitly stated dependence on present velocity.')
opt(23,2,'No; adding the present control alone always makes position sufficient, even when velocity remains unknown.','Present control does not necessarily determine current velocity or its effect on the future.')
opt(23,4,'Yes; declaring a first-order transition makes position sufficient without checking omitted velocity information.','A Markov assumption must be justified for the chosen state; merely declaring it does not establish sufficiency.')
opt(28,1,'The stated normalized update automatically returns the predicted prior unchanged.','Ignoring the observation and retaining the prior is an additional recovery policy, not the result of normalizing zero weights.')
replace(33,[
 'Use positive-definite covariance for the ordinary inverse/determinant density; handle singular Gaussian support separately.',
 'Use a pseudoinverse in the exponent but retain the ordinary zero determinant in the full-dimensional normalizer.',
 'Add εI with ε > 0 and describe the resulting full-dimensional density as exactly the same singular distribution.',
 'Use a pseudoinverse and pseudodeterminant, then interpret the resulting support density as an ordinary density over the entire original space.'
],[
 'A singular covariance has no ordinary inverse and zero determinant, so the printed formula needs the stated qualification.',
 'The zero determinant still makes the ordinary normalization undefined.',
 'Positive regularization changes the covariance and distribution, even if useful as an approximation.',
 'A density on lower-dimensional support is not a full-dimensional density with the same reference measure.'
])
replace(38,[
 'Yes; changing a known F_t requires nonlinear linearization even if the state equation remains linear.',
 'No; matrices chosen as arbitrary nonlinear functions of the current unknown state preserve the exact linear-Gaussian recursion.',
 'Yes; known time-varying matrices permit only steady-state gain, so the displayed time-indexed gain cannot be recomputed.',
 'No; known time-varying linear matrices can be used with the corresponding time-indexed model and noise covariances.'
],[
 'Known variation with time does not by itself make the state dependence nonlinear.',
 'State-dependent matrices can make the transition nonlinear and break exact Gaussian closure.',
 'The recursion can recompute the gain; a constant steady-state gain is a separate special case.',
 'Linearity is required here; time invariance is a narrower special case.'
])
opt(45,3,'The gain weights the measurement in direct proportion to its variance, so a noisier measurement would pull the posterior more strongly.','The scalar gain P/(P+R) decreases when measurement variance R increases; more precise, not noisier, measurements receive greater weight.')
replace(50,[
 'Use F_vᵀ V F_v because transposing the Jacobian always converts noise coordinates into state coordinates.',
 'Use F_x V F_xᵀ because the state Jacobian also maps any native process-noise coordinates correctly.',
 'Direct addition is forbidden even when the noise already lies in state coordinates and F_v is the identity.',
 'Noise may have different coordinates or dimension from the state, so F_v maps its covariance into state space.'
],[
 'The required mapping is F_v from noise to state; the reversed product is generally dimensionally invalid.',
 'F_x differentiates with respect to state, not noise, and cannot generally substitute for F_v.',
 'For additive state-space noise with identity mapping, the covariance term reduces to V.',
 'A linearized noise perturbation F_v v has covariance F_v V F_vᵀ.'
])
qs[51]['solution']['optionExplanations']['o2']='For Y = X², 4.25 is E[Y] = E[X²], the transformed mean and original X second moment; it is not the first-order EKF mean.'
opt(53,4,'The new world-to-robot coordinate transform, rather than the new robot-to-world pose.','The shown composition maps the new robot frame into the world frame; reversing that direction requires inversion.')
qs[55]['difficulty']='easy';qs[55]['difficultyRationale']='Direct differentiation of the fully supplied elementary motion function.'
opt(56,1,'The two columns are x and y state derivatives, while heading is omitted because odometry already contains an angle.','F_v differentiates with respect to two noise inputs, not selected state coordinates.')
opt(56,4,'It is the transpose of the derivative of the three pose outputs with respect to the two noise inputs.','The standard output-by-input derivative already has shape 3×2; its transpose has shape 2×3.')
cite(57,1393,'Prediction box: covariance propagation P̄ = F_x P F_xᵀ + F_v V F_vᵀ.','equation')
qs[57]['solution']['formulas'][-1]=formula('P̄ = F_x P F_xᵀ + F_v V F_vᵀ',{'P':'previous pose covariance','P̄':'predicted pose covariance','F_x':'state-to-state motion derivative','F_v':'noise-to-state motion derivative','V':'native odometry-noise covariance'},{'pose entries':'metres and radians','P,P̄':'products of pose-component units','V':'products of distance and angle noise units','F_x,F_v':'corresponding derivative units'},['Zero-mean process noise independent of previous pose error; Jacobians evaluated at the specified mean and zero noise.'])
opt(58,2,'As midpoint integration, because the use of θ in the displacement implicitly means θ + Δθ/2.','The source explicitly uses the old heading; a midpoint approximation would evaluate a different direction.')
opt(64,1,'The initial 3×3 standard-deviation matrix, with diagonal entries still 0.05, 0.05 and deg2rad(0.5).','Elementwise squaring produces variances on the diagonal, not the original standard deviations.')
opt(74,3,'Replace only r in the denominators by a small ε and call the result the exact derivative at coincidence.','Regularization is a chosen approximation; it does not supply the missing unique direction or exact derivative at zero range.')
opt(78,2,'It accepts the keyword silently, with no deprecation warning, and treats it as the preferred current spelling.','The independently checked pinned implementation emits a deprecation warning recommending plot.')
opt(78,3,'It warns but ignores animate=True, leaving the plotting option false rather than mapping the legacy value.','In the checked compatibility path the legacy value is accepted for plotting; it is not simply discarded.')
opt(80,1,'The close corrected trajectory shows that the measurement model dominates every update regardless of its assumed noise.','Fusion weights depend on the model and covariance, not just the appearance of one trajectory overlay.')
opt(80,3,'The examples show that a smaller estimated covariance guarantees smaller actual error even with incorrect landmark association.','Covariance is a model-based uncertainty estimate; incorrect association can create an overconfident but wrong estimate.')
opt(80,4,'The landmark-corrected run guarantees every covariance entry decreases after every prediction and correction step.','Prediction can add uncertainty, and the source illustration does not establish monotonic behavior of every matrix entry.')
replace(89,[
 'RandomPath supplies controls; vehicle .step simulates odometry; .f predicts the mean; .Fx and .Fv support covariance prediction; EKF maintains the estimate.',
 'RandomPath supplies controls; vehicle .step directly returns the posterior covariance; .f returns noisy odometry; .Fx and .Fv draw the uncertainty ellipse.',
 'RandomPath estimates the mean; vehicle .step supplies controls; .f constructs the posterior covariance; EKF selects random waypoints.',
 'RandomPath supplies controls; vehicle .step simulates odometry; .f predicts the covariance; .Fx and .Fv supply the predicted mean without a motion function.'
],[
 'The slide separates control generation, simulated odometry, nonlinear mean propagation, Jacobian covariance propagation and estimation.',
 'The odometry, mean, derivative and plotting roles have been interchanged.',
 'RandomPath is a driver, not the posterior estimator; the listed method roles are also interchanged.',
 'The nonlinear function predicts the mean, while its derivatives propagate covariance.'
],stem='Which mapping correctly combines the driver, vehicle methods and estimator in the source differential-drive example?',why='The driver chooses controls, .step advances simulation and yields odometry, .f propagates the estimated mean, and .Fx/.Fv supply the covariance Jacobians; EKF combines the specified models.')
cite(89,1397,'Driver paragraph and bottom method-role bullets: .step, .f, .Fx and .Fv.','statement')
def add(n,page,title,stem,options,key,exps,why,kind='statement',typ='conceptual',forms=None):
 q=copy.deepcopy(qs[23]);q.update(id=f'W09-L44-Q{n:03d}',version=1,status='draft',authorId=AUTHOR,stem=stem,type=typ,difficulty='easy',cognitiveSkill='conceptual',subtopic=title,tags=[f'gap-{n}'],conceptIds=[f'W09-L44-C-gap-{n}'],assumptions=[],correctOptionIds=[f'o{key}'],reviewIds=[])
 q['options']=[{'id':f'o{i+1}','text':s} for i,s in enumerate(options)]
 q['solution']=dict(justification=why,optionExplanations={f'o{i+1}':s for i,s in enumerate(exps)},steps=[],formulas=forms or [],simpleExplanation=why,memoryAid=None,misconceptions=[],examTraps=[],prerequisiteConceptIds=[])
 q['citations']=[copy.deepcopy(qs[23]['citations'][0])];q['citations'][0]['physicalPage']=page
 q.pop('authorCheckEvidence',None);qs[n]=q;b['questions'].append(q)
 b['concepts'].append(dict(id=q['conceptIds'][0],title=title,description=why,slideIds=[],questionIds=[q['id']],status='drafted',topic=q['topic'],subtopic=title,prerequisiteConceptIds=[],examinationAngles=[typ]))
 cite(n,page,title,kind);return q
add(90,1382,'Position-density surface and contour projection','The position-uncertainty figure has horizontal axes x (m) and y (m), a probability-density axis, and contours projected below the surface. Which interpretation is supported?',[
 'The surface height is robot heading, so the plot directly displays a three-coordinate pose sample.',
 'The surface represents density over two position coordinates; the lower contours project equal-density levels rather than negative probabilities.',
 'The negative vertical position of the projected contours means some possible positions have negative probability.',
 'The height at each plotted point is the probability of that exact continuous position, so the surface values must sum to one without an area factor.'
],2,[
 'The vertical axis is labeled probability density, not heading.',
 'The source explicitly labels position uncertainty and a 2D Gaussian; the lower drawing plane is a display projection.',
 'A projection below the surface changes its visual placement, not the nonnegative density values.',
 'A continuous density assigns probability through integration over an area, not by reading a point height as a point probability.'
],'The illustrated Gaussian describes uncertainty in x and y; a full planar-pose belief would also address heading. The contour display does not make probability negative.',kind='figure',typ='diagram')
add(91,1384,'Measurement conditional independence versus transition','Let H_t denote past states, controls and measurements in the lecture’s model. Which pair preserves both conditional-independence assumptions?',[
 'p(x_t | H_t) = p(x_t | x_(t−1)); p(z_t | H_t,x_t) = p(z_t | x_t), dropping the current control from motion.',
 'p(x_t | H_t) = p(x_t | x_(t−1),u_t); p(z_t | H_t,x_t) = p(z_t), dropping dependence on the current state.',
 'p(x_t | H_t) = p(x_t | x_(t−1),u_t); p(z_t | H_t,x_t) = p(z_t | x_t).',
 'p(x_t | H_t) = p(x_t | x_(t−1),u_t); p(z_t | H_t,x_t) = p(z_t | x_(t−1)), using only the previous state for sensing.'
],3,[
 'The controlled transition retains the current input u_t.',
 'Conditional independence from history given x_t does not imply unconditional independence from x_t.',
 'Motion is conditioned on the previous state and current control; sensing is conditioned on the current state.',
 'The displayed measurement relation uses x_t, not x_(t−1).'
],'A sufficient current state screens the present measurement from history; the transition instead uses the previous state together with the current control.',kind='equation')
for n in changed:
 q=qs[n];q.update(version=2,status='draft',reviewIds=[]);q.setdefault('revisionAuthors',[]).append(AUTHOR)
for n in changed+[90,91]:
 q=qs[n];q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']]
 for co in b['concepts']:
  if co['id'] in q['conceptIds']:co['description']=q['solution']['justification'];co['examinationAngles']=list(dict.fromkeys(co['examinationAngles']+[q['type']]))
for q in b['questions']:
 if q['id'] in accepted: assert question_hash(q)==accepted[q['id']],q['id']
assert all(qs[n]['correctOptionIds']==before['questions'][n-1]['correctOptionIds'] for n in changed)
schema=json.loads((R/'data/schema.question.json').read_text());errors={q['id']:schema_errors(q,schema) for q in b['questions'] if schema_errors(q,schema)};assert not errors,errors
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for n in changed+[90,91]:
 q=qs[n];x={k:copy.deepcopy(q[k]) for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
pf=R/'audits/blind-W09-L44-v2-and-gaps.json';pf.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
m=dict(frozenAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),author=AUTHOR,independentVerification=False,packet=str(pf.relative_to(R)),packetSha256=hashlib.sha256(pf.read_bytes()).hexdigest(),revisedCount=21,newQuestionCount=2,totalCount=91,preservedAcceptedQuestionHashes=accepted,questionHashes={qs[n]['id']:question_hash(qs[n]) for n in changed+[90,91]},gapDispositions={'density figure':'Q090','measurement independence':'Q091','vehicle method roles':'Q089 v2'},sourceReinspection={'pages':[1382,1384,1393,1397],'method':'Actual full-resolution rendered source pages viewed during repair.'},notes=['All 68 accepted question hashes preserved.','All 21 revised answer keys unchanged.','No source notebook or additional model execution claimed.'])
(R/'audits/W09-L44-v2-repair-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:m[k] for k in ['packetSha256','revisedCount','newQuestionCount','totalCount']}))
