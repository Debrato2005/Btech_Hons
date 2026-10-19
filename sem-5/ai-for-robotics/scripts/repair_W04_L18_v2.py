#!/usr/bin/env python3
"""Apply exactly the frozen L18 quality repairs; never independently approve them."""
import copy,datetime,hashlib,json,math,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors
from authoring_helpers import formula,SHA
AUTHOR='build_offline_study_interface:L18-revision-author';BATCH='W04-L18'
path=R/f'data/question-batches/{BATCH}.json';archive=R/f'audits/batch-history/{BATCH}-v1-before-repairs.json'
if not archive.exists():archive.write_bytes(path.read_bytes())
original=json.loads(archive.read_text());batch=copy.deepcopy(original)
qs={q['id']:q for q in batch['questions']};review=json.loads((R/'audits/W04-L18-contracts-review-summary.json').read_text())
flags=set(review['flaggedQuestionIds']);accepted={q['id']:question_hash(q) for q in original['questions'] if q['id'] not in flags};log=[]
def q(n):return qs[f'{BATCH}-Q{n:03d}']
def opt(n,oid,text,reason):
 row=q(n);next(o for o in row['options'] if o['id']==oid)['text']=text;row['solution']['optionExplanations'][oid]=reason
for n in [8,11,18,51,57,70,71,77]:q(n)['difficulty']='easy'
opt(5,'o3','Its mobility is always the sum of individual joint freedoms, without subtracting independent loop-closure constraints.','Summing unconstrained joint freedoms can overcount independent motion when a loop imposes constraints.')
opt(5,'o4','Its mobility is always exactly the number of actuators, even when passive joints or dependent drives are present.','Actuation count and independent configuration dimension need not coincide; passive coordinates and constraint dependencies must be considered.')
opt(33,'o3','It becomes the length of one link, L₁=L₂.','The minimum radius is the difference of the two link lengths, not either individual length; the folded vectors cancel.')
opt(51,'o1','The number of independent joint configuration coordinates necessarily decreases by the same amount.','A rank drop in the task-velocity map does not necessarily reduce the dimension of the mechanism’s joint-coordinate configuration space.')
opt(51,'o2','Every instantaneous task-velocity direction necessarily becomes unavailable.','Rank can decrease without becoming zero; some task-velocity directions can remain achievable.')
opt(51,'o4','Every nearby task position becomes globally unreachable by any finite joint motion.','Local instantaneous rank loss is not a proof that every nearby position is globally unreachable by finite motion.')
opt(55,'o1','Exactly one task direction is lost, regardless of the magnitude of the rank deficit.','w=0 establishes a rank deficit but does not restrict it to exactly one; the deficit can be larger.')
opt(55,'o2','The task rows remain independent; dependent redundant columns alone make this row-Gram determinant zero.','A redundant full-row-rank Jacobian can have dependent columns while JJᵀ remains nonsingular. Here w=0 requires row dependence.')
opt(64,'o1','r²=41+20cosθ₂.','This omits the factor of two in the cross term 2l₁l₂cosθ₂.')
opt(64,'o3','r²=41−40cosθ₂.','This reverses the sign of the cross term for the stated relative-angle forward map; the straight configuration should have the largest radius.')
q(66)['solution']['steps']=['Use the continuous ideal annulus 1≤r≤9.','The target (1,0) has radius 1; (0,9) has radius 9; (3,4) has radius 5.','The target (0.6,0.6) has radius √(0.6²+0.6²)=√0.72≈0.849.','Only (0.6,0.6) lies below the inner radius 1, so it is outside the workspace.']
opt(76,'o1','√(41+40cos(π/200)), slightly less than 9.','An inclusive grid with 200 points has 199 intervals, not 200; its nearest half-step to zero is π/199.')
opt(76,'o4','√(41+40cos(2π/199)), slightly less than 9.','2π/199 is the full grid spacing. For an even symmetric inclusive grid, the nearest samples are only half that distance from zero.')
opt(82,'o1','Axial tool symmetry makes roll irrelevant and therefore guarantees every required tool-axis direction at every reachable position.','Free axial roll does not remove constraints on the tool-axis direction, and positional reach alone does not guarantee that direction.')
opt(82,'o2','Once a position is reachable, the pictured three positioning joints can independently set any required tool-axis direction at that position.','The positioning joints couple the reachable position and orientation; they are not an additional independent orienting wrist.')
opt(82,'o3','Removing the axial-roll requirement reduces every general spatial pose task to three coordinates, so an orienting wrist can never be needed.','A general position-plus-tool-axis-direction task still has five coordinates: three position and two direction coordinates. An added wrist may be needed.')
# Replace the answer-revealing determinant prompt with actual fixed-frame differentiation.
row=q(83);row['difficulty']='medium'
row['stem']='For the fixed-frame planar 2R map x=l₁cosθ₁+l₂cos(θ₁+θ₂), y=l₁sinθ₁+l₂sin(θ₁+θ₂), define s₁=sinθ₁, c₁=cosθ₁, s₁₂=sin(θ₁+θ₂), c₁₂=cos(θ₁+θ₂). With positive link lengths and θ₂∈[−π,π], which complete Jacobian, determinant and singularity statement is correct? Rows correspond to (x,y), columns to (θ₁,θ₂).'
opt(83,'o1','J=[[-l₁s₁−l₂s₁₂, +l₂s₁₂], [l₁c₁+l₂c₁₂, −l₂c₁₂]]; det J=−l₁l₂sinθ₂; singular at θ₂=0,±π.','This negates the entire θ₂ column. Differentiating cos(θ₁+θ₂) gives −sin(θ₁+θ₂), while differentiating sin gives +cos; the stated positive θ₂ convention has the opposite signs from this option.')
opt(83,'o2','J=[[-l₁sinθ₁, −l₂sinθ₂], [l₁cosθ₁, l₂cosθ₂]]; det J=l₁l₂sin(θ₂−θ₁); singular when θ₂−θ₁ is an integer multiple of π.','This treats θ₂ as the second link’s absolute fixed-frame angle. The stated forward map instead uses θ₁+θ₂ for the second link and θ₂ as the relative elbow angle.')
opt(83,'o3','J=[[-l₁s₁−l₂s₁₂, −l₂s₁₂], [l₁c₁+l₂c₁₂, l₂c₁₂]]; det J=l₁l₂sinθ₂; singular at θ₂=0,±π.','All four entries follow from the stated partial derivatives. The l₂² determinant terms cancel, leaving l₁l₂sinθ₂ and the straight/folded singularities.')
opt(83,'o4','J=[[-l₁s₁, −l₂s₁₂], [l₁c₁, l₂c₁₂]]; det J=l₁l₂sinθ₂; singular at θ₂=0,±π.','The determinant happens to match, but the θ₁ column incorrectly omits the second link’s contribution. θ₁ rotates both link vectors, so a matching determinant alone does not make the full Jacobian correct.')
row['solution']['justification']='The fixed-frame Jacobian is [[−l₁s₁−l₂s₁₂,−l₂s₁₂],[l₁c₁+l₂c₁₂,l₂c₁₂]]. Its determinant is l₁l₂(s₁₂c₁−s₁c₁₂)=l₁l₂sinθ₂. Positive lengths therefore give rank loss at θ₂=0 and θ₂=±π in the stated interval. Those are the straight and folded radial boundaries; the selected task is planar position, not a six-coordinate pose.'
row['solution']['simpleExplanation']='Differentiate every occurrence of each joint angle. The base angle affects both links. Expanding the full 2×2 determinant cancels the l₂² terms, so only the relative elbow sine determines rank loss.'
row['solution']['steps']=['Compute ∂x/∂θ₁=−l₁s₁−l₂s₁₂ and ∂x/∂θ₂=−l₂s₁₂.','Compute ∂y/∂θ₁=l₁c₁+l₂c₁₂ and ∂y/∂θ₂=l₂c₁₂.','Expand det J=(−l₁s₁−l₂s₁₂)l₂c₁₂−(−l₂s₁₂)(l₁c₁+l₂c₁₂).','The −l₂²s₁₂c₁₂ and +l₂²s₁₂c₁₂ terms cancel, leaving l₁l₂(s₁₂c₁−s₁c₁₂)=l₁l₂sin[(θ₁+θ₂)−θ₁].','Thus det J=l₁l₂sinθ₂. For positive lengths, the zeros in [−π,π] are θ₂=−π,0,π.','These correspond to the folded radius |l₁−l₂| and the straight radius l₁+l₂. Even for equal positive links at the folded origin, the nonzero second column leaves rank one rather than zero.']
row['solution']['formulas'].append(formula('J=∂(x,y)/∂(θ₁,θ₂)=[[-l₁s₁−l₂s₁₂,−l₂s₁₂],[l₁c₁+l₂c₁₂,l₂c₁₂]]',{'J':'fixed-base-frame planar position Jacobian with x,y rows and θ₁,θ₂ columns','x,y':'endpoint coordinates in the fixed planar base frame','l₁,l₂':'positive link lengths','θ₁':'base angle of link 1','θ₂':'elbow angle of link 2 relative to link 1','s₁,c₁':'sinθ₁ and cosθ₁','s₁₂,c₁₂':'sin(θ₁+θ₂) and cos(θ₁+θ₂)'},{'x,y,l₁,l₂':'same length unit','θ₁,θ₂':'radians','J':'length per radian','s₁,c₁,s₁₂,c₁₂':'dimensionless'},['Ideal planar 2R chain; task is endpoint position only; derivatives use radians.']))
for row in batch['questions']:
 if row['id'] in flags:
  row['version']=2;row['status']='draft';row['reviewIds']=[];row['revisionAuthors']=list(dict.fromkeys(row.get('revisionAuthors',[])+[AUTHOR]))
  row['solution']['misconceptions']=[row['solution']['optionExplanations'][o['id']] for o in row['options'] if o['id'] not in row['correctOptionIds']]
  log.append({'questionId':row['id'],'fromVersion':1,'toVersion':2,'changes':next(f['findings'] for f in review['findings'] if f['questionId']==row['id']),'oldHash':question_hash(next(a for a in original['questions'] if a['id']==row['id'])),'newHash':question_hash(row)})

def add_gap(number,pages,key,title,stem,options,correct,why,explanations,typ,difficulty):
 qid=f'{BATCH}-Q{number:03d}';cid=f'{BATCH}-C-{key}'
 citations=[{'slideId':f'lectures-p{p:04d}','sourceId':'lectures','sourceSha256':SHA,'physicalPage':p,'kind':'statement','locator':f'Lecture 18, physical PDF page {p}, printed slide {p-543}: '+title,'evidenceText':(R/f'sources/text/lectures/page-{p:04d}.txt').read_text().strip(),'role':'premise' if typ=='scenario' else 'explicit','region':None} for p in pages]
 row={'id':qid,'version':1,'status':'draft','authorId':AUTHOR,'stem':stem,'selectionMode':'single','type':typ,'difficulty':difficulty,'cognitiveSkill':'application' if typ=='scenario' else 'recall','week':4,'lectureId':'L18','topic':'Mechanism Design I','subtopic':title,'tags':[key,'independent-coverage-gap'],'conceptIds':[cid],'assumptions':[],'options':[{'id':f'o{i+1}','text':txt} for i,txt in enumerate(options)],'correctOptionIds':[f'o{correct+1}'],'citations':citations,'solution':{'justification':why,'optionExplanations':{f'o{i+1}':v for i,v in enumerate(explanations)},'steps':[],'formulas':[],'simpleExplanation':why,'memoryAid':None,'misconceptions':[v for i,v in enumerate(explanations) if i!=correct],'examTraps':[],'prerequisiteConceptIds':[]},'origin':'generated','reviewIds':[]}
 batch['questions'].append(row);batch['concepts'].append({'id':cid,'title':title,'description':why,'slideIds':[f'lectures-p{p:04d}' for p in pages],'questionIds':[qid],'status':'drafted','topic':'Mechanism Design I','subtopic':title,'prerequisiteConceptIds':[],'examinationAngles':[typ]});return row
add_gap(84,[548],'iterative-design-decisions','Iterative refinement of coupled design choices',
 'A first manipulator prototype reaches the required positions, but evaluation reveals excessive moving inertia and inadequate sensing for the required cycle and precision. Which response best follows the lecture’s iterative design process?',[
 'Freeze the joint arrangement because reachability was passed, and assume software tuning alone must meet every remaining requirement.',
 'Revisit the number and arrangement of joints together with actuation and sensing choices, then evaluate the revised task compromises.',
 'Replace only the actuator with a larger one, treating its added moving mass and the sensing limitation as irrelevant to the next evaluation.',
 'Improve only encoder resolution and accept the unchanged mechanism as meeting cycle-time requirements without another dynamics evaluation.'
 ],1,'Passing reachability does not complete a task-based design. The source explicitly describes iterative refinement of joint count, arrangement, actuation and sensing; the newly observed limitations justify reconsidering coupled choices rather than freezing them prematurely.',[
 'Reachability is one requirement. Hardware architecture can still need revision for dynamics, sensing or task performance.',
 'This revisits the high-level coupled choices listed on the source page and evaluates the effects of the revision.',
 'A larger actuator can itself affect moving inertia, while it does not by itself remedy inadequate sensing.',
 'Better sensing does not establish that the unchanged dynamics can meet the cycle-time requirement.'
 ],'scenario','medium')
add_gap(85,[558,560],'configuration-terminology','Articulated aliases and source-specific SCARA expansion',
 'Which combined terminology match reproduces the wording on the two lecture pages, rather than substituting another configuration or acronym expansion?',[
 'Articulated: jointed, elbow or anthropomorphic; SCARA: Selectively Compliant Articulated Robot Arm.',
 'Articulated: Cartesian, gantry or rectilinear; SCARA: Selectively Compliant Assembly Robot Arm.',
 'Articulated: spherical, polar or telescoping; SCARA: Selectively Compliant Assembly Robot Arm.',
 'Articulated: jointed, elbow or anthropomorphic; SCARA: Selectively Compliant Assembly Robot Arm.'
 ],3,'The articulated page explicitly gives jointed, elbow and anthropomorphic as aliases. The SCARA page spells the acronym Selectively Compliant Assembly Robot Arm. This item tests that exact source wording rather than claiming there is only one expansion used in all literature.',[
 'The articulated aliases match, but the source uses Assembly, not Articulated, in the SCARA expansion.',
 'Those aliases describe Cartesian/gantry structures, not the source’s human-arm-like articulated configuration.',
 'Those names refer to spherical/polar-style positioning rather than the articulated aliases on the cited page.',
 'Both the alias group and the source-specific acronym expansion match the actual pages.'
 ],'match','easy')
# Accepted objects and original source-dispute records are immutable in this repair.
assert all(question_hash(qs[k])==h for k,h in accepted.items())
assert batch['sourceIssues']==original['sourceIssues']
assert len(batch['questions'])==85 and len(flags)==16 and len(accepted)==67
schema=json.loads((R/'data/schema.question.json').read_text());errors=[e for row in batch['questions'] for e in schema_errors(row,schema)];assert not errors,errors
for row in batch['questions']:
 assert len({o['text'] for o in row['options']})==len(row['options'])
batch['coverageNote']='Original 34 pages visually inspected. Sixteen reviewer-flagged items repaired as v2; 67 accepted question hashes preserved. Two new source-inspected coverage questions are draft. All changed/new items require a different reviewer; source disputes are preserved.'
path.write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
# Refresh only concept membership for the two gap pages; retain original inspection evidence.
ip=R/f'data/inspection-batches/{BATCH}.json';ins=json.loads(ip.read_text())
for slide in ins['slides']:
 slide['conceptIds']=[c['id'] for c in batch['concepts'] if slide['id'] in c['slideIds']]
ip.write_text(json.dumps(ins,ensure_ascii=False,indent=2)+'\n')
selected=[row for row in batch['questions'] if row['id'] in flags or int(row['id'].split('-Q')[1])>=84]
packet=[]
for row in selected:
 a={k:copy.deepcopy(row[k]) for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
 for c in a['citations']:c.pop('evidenceText',None)
 packet.append(a)
pp=R/f'audits/blind-{BATCH}-v2-and-gaps.json';pp.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
manifest={'batchId':BATCH,'revisionAuthor':AUTHOR,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revisedCount':16,'newGapCount':2,'unchangedAcceptedCount':67,'preservedAcceptedQuestionHashes':accepted,'originalBatchArchive':str(archive.relative_to(R)),'originalBatchSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'blindPacketPath':str(pp.relative_to(R)),'blindPacketSha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'sourceVersions':{'lectures':SHA},'sourceDisputesPreserved':True,'independentReviewStillRequired':True,'questions':[{'questionId':row['id'],'questionVersion':row['version'],'questionSha256':question_hash(row)} for row in selected],'repairs':log,'coverageGapQuestions':{'L18-COVERAGE-01':'W04-L18-Q084','L18-COVERAGE-02':'W04-L18-Q085','L18-COVERAGE-03':'W04-L18-Q083 v2'}}
(R/f'audits/{BATCH}-v2-repair-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
coverage=json.loads((R/f'audits/{BATCH}-author-coverage-ledger.json').read_text())
for page in coverage['pages']:
 p=page['physicalPage'];page['conceptIds']=[c['id'] for c in batch['concepts'] if f'lectures-p{p:04d}' in c['slideIds']];page['questionIds']=[row['id'] for row in batch['questions'] if any(c['physicalPage']==p for c in row['citations'])]
coverage['status']='Author v2 coverage proposal after independent gap challenge; repaired and gap items still require independent review.'
(R/f'audits/{BATCH}-author-coverage-ledger-v2.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:manifest[k] for k in ['revisedCount','newGapCount','unchangedAcceptedCount','blindPacketSha256','independentReviewStillRequired']}))
