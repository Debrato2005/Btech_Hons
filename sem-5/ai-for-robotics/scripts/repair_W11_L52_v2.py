#!/usr/bin/env python3
"""Repair exactly 15 flagged objects and add six bounded gaps; preserve all 117 accepted objects."""
from pathlib import Path
import json,copy,hashlib,random,datetime
R=Path(__file__).resolve().parents[1];B='W11-L52';A='L52-v2-repair-author-20261019';SHA='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ['status','reviewIds']},ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
assert not (R/f'audits/{B}-v2-repair-manifest.json').exists(),'Frozen: use new versioned repair'
orig=read('audits/archive/W11-L52-v1-before-v2/W11-L52.json');b=copy.deepcopy(orig);Q={q['id']:q for q in b['questions']};origQ={q['id']:q for q in orig['questions']};reviews=read('data/reviews/W11-L52-v1-independent.json');accepted={x['questionId']:x['questionSha256']for x in reviews if x['decision']=='verified'};flagged={x['questionId']for x in reviews if x['decision']=='flagged'}
assert len(accepted)==117 and len(flagged)==15
for qid,h in accepted.items():assert qhash(Q[qid])==h
current={q['id']:q for q in read(f'data/question-batches/{B}.json')['questions']}
for qid,h in accepted.items():assert qhash(current[qid])==h;Q[qid].clear();Q[qid].update(copy.deepcopy(current[qid]))
issues=read(f'audits/source-disputes-{B}.json');issueshash=hashlib.sha256((R/f'audits/source-disputes-{B}.json').read_bytes()).hexdigest();assert issueshash=='85bfd0a4cc6a75a034b83aef29089372677a772369778df9a3a4da0a29bc3f23'
changed=[];notes={}
def q(s):return Q[B+'-'+s]
def revise(s,note):
 z=q(s);assert z['id']in flagged;z['version']=2;z['status']='draft';z['reviewIds']=[];z['revisionAuthors']=list(dict.fromkeys(z.get('revisionAuthors',[])+[A]));
 if z.get('conflictResolution'):z['conflictResolution']['questionVersion']=2
 changed.append(z);notes[z['id']]=note;return z
def op(z,oid,text,why):
 next(o for o in z['options']if o['id']==oid)['text']=text;z['solution']['optionExplanations'][oid]=('Correct. 'if oid in z['correctOptionIds']else'Incorrect. ')+why

def cite(p,k,loc,role='explicit',evidence=None):return dict(slideId=f'lectures-p{p}',sourceId='lectures',sourceSha256=SHA,physicalPage=p,kind=k,locator=f'Printed slide {p-1619}: {loc}',evidenceText=evidence if evidence is not None else (R/f'sources/text/lectures/page-{p}.txt').read_text().strip(),role=role,region=None)
z=revise('P1627-Q01','Replace mechanical-housing distractor with a real wiper-short wiring misconception; state fixed supply and high-impedance reading.')
z['stem']='With a fixed supply across a potentiometer’s track and a high-impedance ADC, which connection gives a position-dependent divider voltage?'
op(z,'o1','Read the wiper after permanently shorting it to the grounded track endpoint','The short clamps the wiper to ground instead of allowing its unloaded divider voltage to vary.')
op(z,'o2','Read between the two fixed track endpoints','Their voltage remains the fixed supply, independent of the wiper position.')
op(z,'o3','Read the unshorted wiper relative to the grounded track endpoint','The moving contact taps a position-dependent fraction of the fixed track voltage.')
z['assumptions']+=['Ideal fixed supply, negligible ADC loading, and a functioning resistive track; no wiper-to-endpoint short in the intended connection.']
z=revise('P1632-Q03','Correct code-block citation kind; retain the separate accuracy statement qualification.')
z['citations'][0]['kind']='code';z['citations'][0]['locator']='Printed slide 13: volatile long count declaration and noInterrupts()/interrupts() surrounding the count/PPR snapshot'
z['citations'].append(cite(1632,'statement','Right-hand Code Explanation bullet: interrupt ensures accurate counting','conflict'))
z=revise('P1659-Q01','Replace generic duplicate stem with the specific IMU transducer/quantity/unit mapping.')
z['stem']='Which IMU transducer-to-measured-quantity and unit mapping is correct, distinguishing raw signals from inferred pose?'
z=revise('P1660-Q02','Specify board-pin versus bus-address comparison; split table and code citation regions.')
z['stem']='For the shown Arduino Mega IMU connection, how do SDA/SCL pin numbers 20 and 21 differ from MPU_ADDR 0x68?'
z['citations'][0]['locator']='Printed slide 41: pin table rows SDA→20 and SCL→21'
z['citations'].append(cite(1660,'code','Lower code block: #define MPU_ADDR 0x68'))
z=revise('P1662-Q01','Replace I2C-implies-position distractor with a precision-versus-calibration misconception.')
op(z,'o3','A demonstrated absolute tilt accuracy equal to the smallest displayed decimal increment','Displayed resolution is not a calibration or accuracy measurement against a known angle reference.')
z=revise('P1667-Q04','Restrict the slide locator to the actual predicate and print branches; ST status meanings remain external primary evidence.')
z['citations'][0]['locator']='Printed slide 48: if (measure.RangeStatus != 4) numeric-print branch and else Out of range branch'
z=revise('P1672-Q02','Replace generic duplicate stem with the stereo-depth/event-camera output distinction.')
z['stem']='How do the lecture’s stereo camera and event camera differ in the information they derive or report?'
z=revise('P1673-Q02','Replace ADC category error with a plausible spatial-versus-temporal color sampling misconception.')
op(z,'o3','It exposes every photodiode sequentially through full-frame red, green and blue filters in each capture','The stated color-filter array spatially places different spectral filters over pixel sites; it is not a required temporal full-frame filter wheel.')
z=revise('P1674-Q01','Replace hardware-validation shortcut with concrete enhancement-versus-defect tradeoffs.')
z['stem']='For robotic defect inspection, denoising makes an image look smoother and contrast enhancement makes edges stronger. Which evaluation approach is justified?'
op(z,'o1','Choose the strongest smoothing because removing more fine texture necessarily preserves every thin crack','Fine defect features can resemble the detail that smoothing removes; visual smoothness alone cannot establish defect recall.')
op(z,'o2','Choose the greatest global contrast because its strongest edges must correspond to true defects','Global contrast can also emphasize texture or artifacts, so it does not identify which edges are defects.')
op(z,'o3','Evaluate defect decisions against suitable references, because improved appearance need not improve task accuracy','Image enhancement and successful quality-control decisions are related but distinct objectives.')
z['citations'][0]['role']='premise';z['assumptions']+=['The smoothing and contrast choices are supplied inspection scenarios; the lecture lists enhancement and industrial inspection but no measured improvement guarantee.']
z=revise('P1675-Q01','Replace depth-category distractor with classless object proposal confusion.')
op(z,'o2','Only unlabeled candidate rectangles, without assigning an object category','Region proposals can localize candidates, but the shown detection output also assigns object labels and confidence scores.')
z=revise('P1676-Q01','Use archived configuration metadata with exact inclusive count; replace object-count distractor with background-index misconception. No restricted runtime used.')
z['stem']='The source labels its Open Images example “approximately 600 classes”. In the preserved Ultralytics 8.4.182 dataset YAML, what does the complete names mapping indexed 0–600 mean?'
op(z,'o1','It contains 600 category names because the largest zero-based index equals the entry count','For consecutive indices including both 0 and 600, the count is 600−0+1=601.')
op(z,'o2','It contains 601 category names; the indices are vocabulary entries rather than per-frame object counts','The archived mapping includes both endpoints and names index 0 Accordion; it lists categories, not detected instances.')
op(z,'o3','It contains 600 object categories plus an unnamed background entry at index 0','Index 0 is explicitly named Accordion in the preserved mapping, so it is not an unnamed background slot.')
z['assumptions']=['Read the preserved metadata file linked in primaryEvidence; no claim is made about an uninspected checkpoint or fresh model inference.']
z['conflictResolution']['method']='Count the preserved dataset YAML entries in the permitted default Python, without importing Ultralytics, downloading weights, using a webcam or returning to the restricted runtime.'
for e in z.get('primaryEvidence',[]):e['version']='Preserved dataset YAML from Ultralytics 8.4.182; metadata-only default-Python recount; original guide accessed 2026-10-19'
z['solution']['formulas']=[dict(expression='N=b−a+1',variables={'N':'Number of entries in a consecutive inclusive index range','a':'Smallest included index','b':'Largest included index'},units={'N':'entries','a,b':'dimensionless integer indices'},assumptions=['Every integer from a through b is present exactly once; endpoints included; here a=0 and b=600.'])]
z['solution']['steps']=['Inspect the preserved mapping: both index 0 and index 600 exist.','Count the consecutive keys: 600−0+1=601.','Check index 0 is Accordion rather than an unnamed background entry.']
z=revise('P1677-Q04','Assign interval counter/write-loop evidence to p1677 and writer fps evidence only to p1676.')
z['citations'][0]['locator']='Printed slide 58: current_time/prev_time interval FPS calculation and out.write(annotated) loop'
z=revise('P1679-Q01','Replace RGB-depth category error with a calibration/coordinate-frame misconception.')
op(z,'o3','RGB gives appearance; depth pixels already give metric X and Y from their row and column indices without camera intrinsics','Image indices are pixel coordinates, not metric lateral coordinates; calibrated geometry is needed to reconstruct 3D points.')
z=revise('P1680-Q01','Remove answer-giving negation and use parallel false-color depth/confidence/semantic interpretations.')
z['stem']='In the lower-left RealSense Viewer panel labeled Colorized Depth Image, what does its blue-to-warm palette represent?'
op(z,'o1','A confidence-score scale for how reliably each pixel was matched','Confidence is a distinct possible visualization; this panel is explicitly identified as the depth map, not a confidence map.')
op(z,'o2','A display mapping of depth values, separate from the RGB appearance panel','The labeled depth view encodes scene geometry with a palette rather than recording the objects’ visible surface color.')
op(z,'o3','A semantic-class palette assigning a separate color to each recognized object category','No class-segmentation legend is shown; the panel is identified as colorized depth, not semantic labels.')
z=revise('P1682-Q02','Replace generic duplicate stem with the three force/torque transducer mechanisms.')
z['stem']='Which mapping correctly matches strain-gauge, piezoelectric and capacitive force/torque sensors to their transduction mechanisms?'
z['citations'][0]['locator']='Printed slide 63: Strain Gauge F/T, Piezoelectric F/T and Capacitive F/T mechanism bullets'
# Rebuild only changed solutions from their exact per-option rationales.
for z in changed:
 sol=z['solution'];sol['justification']=' '.join(sol['optionExplanations'][o['id']].removeprefix('Correct. ')for o in z['options']if o['id']in z['correctOptionIds']);sol['simpleExplanation']=sol['justification'];sol['misconceptions']=[sol['optionExplanations'][o['id']].removeprefix('Incorrect. ')for o in z['options']if o['id']not in z['correctOptionIds']]
 assert z['correctOptionIds']==origQ[z['id']]['correctOptionIds']
CM={c['id']:c for c in b['concepts']};new=[];gapmap={}
def add(p,tag,gap,loc,stem,choices,kind='diagram',ck='figure',difficulty='easy',ass=(),extra=(),conflict=None,formulas=(),steps=(),evidence=None):
 cid=B+'-C-'+tag;idx=1+sum(x['id'].startswith(f'{B}-P{p}-Q')for x in b['questions']);qid=f'{B}-P{p}-Q{idx:02}';seq=list(range(len(choices)));random.Random(qid).shuffle(seq);oid={i:f'o{j+1}'for j,i in enumerate(seq)}
 z=dict(id=qid,version=1,status='draft',authorId=A,stem=stem,selectionMode='single',type=kind,difficulty=difficulty,cognitiveSkill='synthesis'if kind=='synthesis'else'algorithm'if kind=='algorithm_trace'else'application'if kind=='scenario'else'conceptual',week=11,lectureId='L52',topic='Sensors used in Robots',subtopic=CM[cid]['title'],tags=['sensors','bounded-coverage-gap',tag],conceptIds=[cid],assumptions=list(ass),options=[dict(id=oid[i],text=choices[i][0])for i in seq],correctOptionIds=[oid[0]],citations=[cite(p,ck,loc,'premise'if kind=='synthesis'else'explicit',evidence)]+list(extra),solution=dict(justification=choices[0][1],optionExplanations={oid[i]:('Correct. 'if i==0 else'Incorrect. ')+choices[i][1]for i in seq},steps=list(steps),formulas=list(formulas),simpleExplanation=choices[0][1],memoryAid=None,misconceptions=[x[1]for x in choices[1:]],examTraps=[],prerequisiteConceptIds=[]),origin='generated',reviewIds=[])
 if len(choices)==3:z['optionCountRationale']='Three parallel, technically plausible alternatives avoid unrelated filler.'
 if conflict:
  z['conflictResolution']=dict(status='source_attributed_qualification_pending_independent_review',questionVersion=1,sourceId='lectures',sourceSha256=SHA,physicalPage=conflict['physicalPage'],sourceClaim=conflict['finding'],basis=conflict['handling'],method=conflict['method'],sourceIssueId=conflict['id'],scope='This question version only; source-attributed drawing, not every hardware revision.');z['primaryEvidence']=copy.deepcopy(conflict['primaryEvidence'])
  if not any(c['physicalPage']==conflict['physicalPage']for c in z['citations']):z['citations'].append(cite(conflict['physicalPage'],'statement','Humidity-element description, whose hardware revision is unspecified','conflict'))
  else:
   for c in z['citations']:
    if c['physicalPage']==conflict['physicalPage']:c['role']='conflict'
 b['questions'].append(z);Q[qid]=z;new.append(z);CM[cid]['questionIds'].append(qid);CM[cid]['examinationAngles'].append(gap+': '+loc);gapmap[gap]=qid
add(1638,'ldr','L52-GAP-01','Labeled LDR cutaway: top photoconductive layer, electrodes, ceramic and clear coating','Which role assignment matches the LDR construction drawing?',[
 ('Photoconductive layer: light-dependent conduction; electrodes: electrical contacts; ceramic: support; clear coating: top cover','The drawing separates the light-responsive material and its electrical contacts from the supporting body and covering.'),
 ('Photoconductive layer: mechanical support; electrodes: top cover; ceramic: light-dependent conduction; clear coating: electrical contacts','These are real parts assigned to the wrong roles: the labeled photoconductive layer is the responsive region, not the ceramic base.'),
 ('Photoconductive layer: light-dependent conduction; electrodes: mechanical support; ceramic: electrical contacts; clear coating: top cover','The sensing and covering roles are right, but the electrodes and ceramic support have been interchanged.')],evidence='Diagram labels: Electrodes; Photoconductive material over top surface; Ceramic; Clear coating over entire top surface; Wire terminals; Cold weld contacts.')
add(1646,'reed','L52-GAP-02','Reed-switch cross-section labels: glass capsule, inert gas, contact material, bond and reed blades','Which interpretation follows the labeled reed-switch construction?',[
 ('The reed blades/contact region are enclosed by a glass capsule containing inert gas, with glass-to-metal bonds where metal passes through','The labels distinguish the conducting contact structure from its enclosing capsule, fill and seals; no particular gas chemistry is specified.'),
 ('The glass-to-metal bond is the internal contact that repeatedly opens, while the contact material seals the outside capsule','This swaps the fixed feedthrough seal with the internal switching-contact region.'),
 ('The inert gas fills an external chamber, while the glass capsule is one of the movable reed blades','The arrows place the gas within the capsule and identify the metal reed blades separately.')],evidence='Diagram labels: Glass Capsule; Inert Gas; Contact Material; Glass to Metal Bond; Reed Blade on both sides.')
dht=next(i for i in issues if i['id']=='L52-ISSUE-dht-revision')
add(1655,'dht','L52-GAP-03','Working-principle bullets: internal ADC and single-wire serial data','According to the lecture’s DHT11 signal-chain description, where does conversion occur and how do readings leave the sensor?',[
 ('The sensor internally digitizes its sensed signal, then transmits digital data over the described single data wire','The slide places an ADC inside the sensor and separately names single-wire serial transmission; this is not the preceding raw analogRead pattern.'),
 ('The sensor sends its raw analog voltage to the Arduino ADC, which alone converts each temperature/humidity reading','This confuses the described digital DHT interface with a raw analog-output sensor read through the controller ADC.'),
 ('The sensor internally digitizes the signal, then requires separate I2C SDA and SCL lines for that described link','Internal digitization is right, but the slide explicitly describes a single-wire serial data link rather than the two I2C lines.')],kind='sequence',ck='statement',ass=['This question is source-attributed to the lecture’s ADC/interface chain; it does not identify the humidity-element technology of every DHT11 revision.'],conflict=dht)
add(1656,'dht-wiring','L52-GAP-04','Upper-left exploded humidity element: upper electrode, moisture-holding substrate, lower electrode and glass substrate','Read the humidity-element exploded drawing as printed, without generalizing it to every DHT11 revision. What is the order from top to bottom?',[
 ('Upper electrode → moisture-holding substrate → lower electrode → glass substrate','The responsive substrate is between the two electrodes, while the glass forms the supporting bottom layer in the drawing.'),
 ('Upper electrode → glass substrate → lower electrode → moisture-holding substrate','This places the named glass support between the electrodes and moves the moisture-holding layer below them.'),
 ('Upper electrode → lower electrode → moisture-holding substrate → glass substrate','This incorrectly puts both electrodes together above the moisture-holding layer instead of on opposite sides.')],ass=['Interpret only the actual labeled source drawing; the separate documentation-revision qualification is retained.'],conflict=dht,evidence='Exploded drawing labels from top: Upper Electrode, Moisture Holding Substrate, Lower Electrode, Glass Substrate.')
add(1682,'force-torque','L52-GAP-05','Capacitive F/T low-noise/soft-robotics/tactile-array bullets and opening compliant-control statement','Which pairing follows the lecture’s force/torque sensing applications without claiming that the sensor alone guarantees safe control?',[
 ('Low-noise capacitive sensing is listed for soft-robotics tactile arrays; measured forces and moments can provide feedback for compliant control','The slide connects capacitive sensing with distributed touch and the measured wrist wrench with contact-responsive control; actual performance still depends on implementation.'),
 ('Low-noise capacitive sensing is listed only for rapid impacts; measured forces and moments replace the need to define a contact-control law','The capacitive applications include tactile arrays, not just impacts, and measurement alone does not specify how the controller responds.'),
 ('Low-noise capacitive sensing is listed for tactile arrays; compliant control should ignore the measured wrench and enforce a fixed motion regardless of contact','The tactile association is right, but disregarding force/moment feedback defeats the described role of wrench sensing in compliance.')],kind='scenario',ck='statement',ass=['These are source-listed applications, not universal noise specifications or a safety certification.'])
add(1683,'sensor-selection','L52-GAP-06','Operating Environment, Interface & Computational Load, and Size, Weight & Power rows','A supplied outdoor robot must operate from −10 to 50 °C in dust and splashes. Its available controller interface is 3.3 V I2C, with no adapters. A fixed-orientation mount allows at most 30×20 mm and 20 g. All candidates already meet range, error, update-rate and power needs. Which candidate meets the remaining constraints?',[
 ('Qualified for the full environment; 3.3 V I2C; 28×18 mm; 18 g','It satisfies environmental qualification, the directly supported interface, both mount dimensions and mass.'),
 ('Qualified only for dry indoor operation from 0 to 50 °C; 3.3 V I2C; 25×18 mm; 15 g','The interface, dimensions and mass fit, but the operating environment does not include the required cold, dusty and splash-exposed conditions.'),
 ('Qualified for the full environment; 5 V UART only; 25×18 mm; 15 g','The environmental and mechanical conditions fit, but the stipulated controller offers only 3.3 V I2C and adapters are unavailable.'),
 ('Qualified for the full environment; 3.3 V I2C; 45×30 mm; 28 g','The environment and interface fit, but both physical size and mass exceed the stated limits.')],kind='synthesis',ck='statement',difficulty='medium',ass=['All candidate specifications and limits are supplied, not product specifications from the slide; environmental qualification includes the full temperature interval plus dust/splash suitability; fixed orientation; no adapter or mount redesign.'],steps=['Require the rated environment to cover all task conditions.','Require a directly compatible 3.3 V I2C interface.','Compare each width and height with 30 mm and 20 mm, respectively, and each mass with 20 g.','Only the 28×18 mm, 18 g, fully qualified I2C candidate passes every condition.'],formulas=[dict(expression='eligible=E AND I AND (w≤w_max) AND (h≤h_max) AND (m≤m_max)',variables={'eligible':'Boolean satisfaction of every remaining selection constraint','E':'Environmental rating covers the required temperature interval, dust and splashes','I':'Controller and sensor electrical/protocol interfaces are directly compatible','w,h':'Candidate width and height in the fixed mounting orientation','w_max,h_max':'Maximum allowed mount dimensions','m':'Candidate mass','m_max':'Maximum allowed mass'},units={'eligible,E,I':'Boolean','w,h,w_max,h_max':'mm','m,m_max':'g'},assumptions=['Fixed orientation; no adapter; all omitted measurement and power constraints already satisfied; all bounds inclusive.'])])
# A multiple-selection construction reading avoids an implausible third single-select alternative.
rz=Q[gapmap['L52-GAP-02']];rz['stem']='Select every statement that matches the labeled reed-switch construction drawing.';rz['selectionMode']='multi';rz.pop('optionCountRationale',None)
rz['options']=[dict(id='o1',text='The reed blades extend through the capsule ends and meet at an internal contact region.'),dict(id='o2',text='The inert gas is inside the glass capsule rather than being a separate external housing.'),dict(id='o3',text='The glass-to-metal bond label identifies the central opening and closing contact gap.'),dict(id='o4',text='The contact-material arrow points to the glass capsule wall rather than the internal reed/contact region.')]
rz['correctOptionIds']=['o1','o2'];rz['solution']['optionExplanations']={'o1':'Correct. The reed blades continue from the leads into the enclosed switching structure.','o2':'Correct. The gas label points to the space enclosed by the capsule; the diagram does not specify its chemical composition.','o3':'Incorrect. The bond is labeled at the capsule end where metal passes through glass, not at the central switching gap.','o4':'Incorrect. The contact-material label points to the internal metal region, not the enclosing glass wall.'}
rz['solution']['justification']='The drawing distinguishes internal reed/contact structure and enclosed inert gas from the glass capsule and its metal feedthrough bonds.';rz['solution']['simpleExplanation']=rz['solution']['justification'];rz['solution']['misconceptions']=[rz['solution']['optionExplanations'][i].removeprefix('Incorrect. ')for i in ['o3','o4']]
assert len(changed)==15 and len(new)==6 and len(b['questions'])==138
for qid,h in accepted.items():assert qhash(Q[qid])==h and Q[qid]==current[qid]
assert hashlib.sha256((R/f'audits/source-disputes-{B}.json').read_bytes()).hexdigest()==issueshash
b['coverageNote']='138 current objects: 117 accepted objects preserved exactly; 15 v2 repairs and six bounded gap drafts require independent review. Historical restricted-runtime checks remain excluded from validation.'
write(f'data/question-batches/{B}.json',b)
write(f'audits/{B}-v2-repair-work.json',dict(revisionAuthor=A,preparedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),priorReview='data/reviews/W11-L52-v1-independent.json',preservedAcceptedHashes=accepted,changedIds=[z['id']for z in changed],newGapIds=[z['id']for z in new],gapQuestionMap=gapmap,changeNotes=notes,sourceQualificationsSha256=issueshash,independentReviewPending=True))
print('Saved15repairs+6gaps;117acceptedobjectsunchanged')
