"""Repair five remaining independent-review flags; do not overwrite on rerun."""
from pathlib import Path
import json,copy,datetime,hashlib
from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W01-L05.json';b=json.loads(p.read_text());old=copy.deepcopy(b)
a=R/'audits/batch-history/W01-L05-before-final-quality-repairs.json'
if a.exists():assert json.loads(a.read_text())==old,'Already applied or subsequently changed.'
else:a.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
nums={2,31,45,74,80};qs={int(q['id'][-3:]):q for q in b['questions']}
for n in nums:
 q=qs[n];h=question_hash(q);q['version']+=1;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append('robotics-integration-L05-final-quality-revision');q.setdefault('revisionHistory',[]).append({'version':q['version'],'authorId':'robotics-integration-L05-final-quality-revision','priorQuestionSha256':h,'reason':'Five exact remaining independent-review findings; preserve all accepted objects and open source issues.','revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
def setq(n,stem,opts,key,why,exps):
 q=qs[n];q['stem']=stem
 for o in q['options']:o['text']=opts[int(o['id'][1:])-1]
 q['correctOptionIds']=[f'o{key}'];q['selectionMode']='single';q['solution']['justification']=why;q['solution']['simpleExplanation']=why;q['solution']['optionExplanations']={f'o{i+1}':e for i,e in enumerate(exps)};q['solution']['misconceptions']=[e for i,e in enumerate(exps) if i+1!=key]
setq(2,'Which interpretation matches the ecosystem and cross-platform cards as course feature descriptions, rather than a current inventory or universal compatibility certificate?',[
 'Ecosystem refers only to packages shipped inside the core installation; cross-platform means those packages need no platform-specific dependencies',
 'Ecosystem highlights reusable packages and users; cross-platform names Linux, macOS and Windows as ROS 2 hosts',
 'Ecosystem counts certify every package on every host; cross-platform guarantees identical drivers on those hosts',
 'Ecosystem means every package is maintained by the core ROS team; cross-platform means the same compiled executable runs unchanged on every host'],2,
 'The cards describe a reusable software/community ecosystem and named host operating systems; they do not certify every package, dependency, driver or binary combination.',[
 'An ecosystem extends beyond the core installation, and platform support does not remove platform-specific dependencies.',
 'This matches the two source feature categories without overstating their guarantee.',
 'Naming supported hosts is not certification of every package and driver combination.',
 'A community ecosystem does not imply one maintainer for every package or universal compiled-binary portability.'])
qs[2]['difficulty']='easy'
for c in qs[31]['citations']:
 if c['physicalPage']==194:c['kind']='statement';c['locator']='Lecture 5, physical PDF page 194: service prose, including the intended multiple-client arrangement; not the diagram on page 195'
qs[45]['difficulty']='easy'
setq(74,'In a hypothetical URDF link, a visible fin is centered at x=+0.15 m, while the existing collision box spans x=−0.10 to +0.10 m; which change models fin contacts at the correct location while retaining the existing body collision and visual geometry?',[
 'Keep the body collision box and add a fin collision shape with its link-frame center at x=+0.15 m',
 'Keep the body collision box and add the same fin collision shape with its link-frame center at x=−0.15 m',
 'Move the existing body collision box center to x=+0.15 m instead of retaining it and adding the fin',
 'Keep collision geometry unchanged and increase only the fin’s contribution to the inertial mass'],1,
 'Contacts use the configured collision shapes and their link-frame placements; adding the fin shape at +0.15 m represents it without moving the body or changing the visual model.',[
 'This satisfies the location, retained-body and unchanged-visual requirements.',
 'This places the added collision fin on the wrong side of the link frame.',
 'This moves the body’s contact representation rather than retaining it and adding the fin.',
 'Changing inertial mass changes dynamics, not the geometric shape used for contact.'])
qs[74]['difficulty']='easy';qs[74]['type']='scenario';qs[74]['cognitiveSkill']='application';qs[74]['assumptions']=['The dimensions are hypothetical and refer to one common link frame; other axes and fin dimensions are chosen correctly.','The task is model-geometry correction, not proof of numerical contact accuracy or physical validation.'];qs[74]['solution']['steps']=['Identify the fin’s required collision center as +0.15 m in the link frame.','Retain the existing body box and visual mesh.','Add a separate matching fin collision shape at the specified positive-x location.']
setq(80,'Which experiment most directly matches hardware-in-the-loop rather than an entirely simulated, entirely physical or playback-only setup?',[
 'A physical controller exchanges live signals with a Gazebo-simulated plant, and RViz displays the resulting data',
 'A simulated controller exchanges live signals with a Gazebo-simulated plant, and RViz displays the resulting data',
 'A physical controller operates a physical plant, and RViz displays the resulting data',
 'RViz displays recorded sensor messages while neither a controller nor a simulated plant is actively coupled'],1,
 'Hardware-in-the-loop couples real hardware with a simulated part of the active experiment; Gazebo supplies the simulated plant here and RViz remains a data-visualization tool.',[
 'This explicitly couples real controller hardware to an active simulated plant.',
 'This is a software-only simulation in the stated setup.',
 'This is the stated all-physical experiment, despite using software for visualization.',
 'Playback visualization alone does not form an active real-hardware/simulation loop.'])
qs[80]['difficulty']='easy';qs[80]['type']='scenario';qs[80]['cognitiveSkill']='application';qs[80]['assumptions']=['Classify only the components explicitly described in each option; no additional hardware or simulation is implied.']
unchanged=[q for q in b['questions'] if int(q['id'][-3:]) not in nums];oldmap={q['id']:q for q in old['questions']};assert all(question_hash(q)==question_hash(oldmap[q['id']]) for q in unchanged)
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for n in sorted(nums):
 q=qs[n];z={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in z['citations']:c.pop('evidenceText',None)
 packet.append(z)
f=R/'audits/blind-W01-L05-final-quality-repairs.json';f.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
manifest={'changedQuestions':5,'unchangedOriginalBatchHashes':75,'unchangedSeparateGapQuestions':3,'packet':str(f.relative_to(R)),'packetSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'questionHashes':{q['id']:question_hash(q) for q in b['questions']},'independentReview':'pending','sourceIssues':'All 16 original annotations, including four open issues, remain untouched.'}
(R/'audits/W01-L05-final-quality-repair-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(manifest['packetSha256'])
