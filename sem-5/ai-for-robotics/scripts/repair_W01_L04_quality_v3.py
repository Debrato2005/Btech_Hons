"""One-time targeted source-based repairs after the independent coverage challenge."""
from pathlib import Path
import json, copy, datetime
from validate import question_hash
R=Path(__file__).resolve().parents[1]
p=R/'data/question-batches/W01-L04.json'; b=json.loads(p.read_text()); old=copy.deepcopy(b)
archive=R/'audits/batch-history/W01-L04-before-coverage-repairs.json'
assert not archive.exists(), 'Already applied; do not overwrite reviewed questions.'
archive.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
qmap={q['id'].removeprefix('W01-L04-'):q for q in b['questions']}
easy={'P0129-Q03','P0140-Q03','P0145-Q01','P0147-Q01','P0148-Q01','P0127-Q04','P0151-Q01','P0154-Q04',*[f'P0158-Q0{i}' for i in range(1,7)],'P0161-Q05','P0162-Q02','P0163-Q04','P0165-Q03','P0166-Q04'}
distractors={'P0129-Q03','P0140-Q03','P0145-Q01','P0147-Q01','P0148-Q01','P0151-Q02','P0154-Q03','P0167-Q01'}
gaps={'P0137-Q02','P0155-Q03'}
changed=easy|distractors|gaps
assert len(changed)==24
for k in changed:
 q=qmap[k]; prior=question_hash(q); q['version']+=1;q['status']='draft';q['reviewIds']=[]
 q.setdefault('revisionAuthors',[]).append('robotics-integration-L04-quality-revision-author')
 q.setdefault('revisionHistory',[]).append({'version':q['version'],'authorId':'robotics-integration-L04-quality-revision-author','priorQuestionSha256':prior,'reason':'Repair independently identified distractor/difficulty defects or extend an existing item to close a documented narrow source coverage gap.','revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 if k in easy:q['difficulty']='easy';q['cognitiveSkill']='recall'
def setq(k,stem,opts,why,exps,assumptions=None):
 q=qmap[k];q['stem']=stem
 for o in q['options']:o['text']=opts[int(o['id'][1:])-1]
 q['correctOptionIds']=['o1'];q['solution']['justification']=why;q['solution']['simpleExplanation']=why
 q['solution']['optionExplanations']={f'o{i+1}':s for i,s in enumerate(exps)}
 q['solution']['misconceptions']=exps[1:]
 if assumptions is not None:q['assumptions']=assumptions
setq('P0129-Q03','Which paired contrast is NOT among the three system-study comparisons listed on this slide?',[
 'Deterministic models versus stochastic models', 'An actual system versus a model of the system', 'Physical models versus mathematical models', 'Analytical solutions versus simulation'],
 'This slide lists actual/model, physical/mathematical, and analytical/simulation comparisons, not the deterministic/stochastic classification.',[
 'Correct: deterministic/stochastic is a meaningful model classification, but it is not one of this slide’s three comparisons.', 'This is the slide’s first comparison.', 'This is the slide’s second comparison.', 'This is the slide’s third comparison.'])
setq('P0140-Q03','In the Analyze phase, which pair correctly matches an uncertain model and an optimization objective to the techniques named by the lecture?',[
 'Probability and statistics for uncertainty; optimization techniques for the objective', 'Optimization techniques for uncertainty; probability and statistics for the objective', 'Syntax checking for uncertainty; plotting alone for the objective', 'A single nominal simulation for uncertainty; code compilation for the objective'],
 'The slide assigns probability and statistics to uncertainty, and optimization techniques to an optimization goal.',[
 'Correct: these are the two stated method-to-purpose matches.', 'This reverses the two assignments; optimizing a design is not the stated uncertainty analysis.', 'Syntax checking concerns code form; plotting can display results but does not itself select an optimum.', 'One nominal run does not characterize uncertainty; compilation does not optimize the model’s engineering objective.'])
setq('P0145-Q01','Which set contains only the three modelling and simulation limitations listed on the slide?',[
 'Omitted real-world effects; accumulated numerical errors; an environment simpler than reality',
 'Omitted real-world effects; accumulated numerical errors; an environment necessarily more complex than reality',
 'Omitted real-world effects; numerical errors confined to the initial time step; an environment simpler than reality',
 'All real-world effects retained by a mathematical model; accumulated numerical errors; an environment simpler than reality'],
 'The source names omitted effects, accumulated numerical error, and simplified environments.',[
 'Correct: all three are listed limitations.', 'The source warns that the environment is simpler, not necessarily more complex, than reality.', 'Numerical errors can accumulate over repeated calculations rather than being confined to initialization.', 'A mathematical representation can omit relevant effects; its use does not ensure complete physical detail.'])
setq('P0147-Q01','What role does the slide assign Python in extending a mathematical model into a computational model?',[
 'Evaluate model equations repeatedly while changing model parameters',
 'Obtain a closed-form symbolic solution before every model can be evaluated',
 'Store observed outputs instead of evaluating the model’s equations',
 'Infer all physical parameter values solely from the form of the equations'],
 'The slide describes repeated evaluation of model equations with different parameters, rather than automatic model or parameter discovery.',[
 'Correct: this is the computational extension described.', 'Numerical evaluation need not wait for a closed-form symbolic solution.', 'Observed outputs may support validation, but storing them is not the stated equation-evaluation role.', 'Equation form alone does not supply every numerical physical parameter.'])
setq('P0148-Q01','According to the numerical-computation slide, which approach supports a complex dynamic model without a practical closed-form solution?',[
 'Use vectors and matrices, approximate equation solutions, and repeated calculations over time',
 'Use vectors and matrices, but replace the whole time history with a steady-state solution',
 'Use repeated calculations, but require a closed-form symbolic solution at every update',
 'Use an approximate initial solution, but hold it fixed while studying changing dynamics'],
 'The source combines vector/matrix handling, approximate solutions, and repeated time calculations.',[
 'Correct: all three capabilities appear on the slide.', 'A steady-state result alone omits the evolving behaviour that a dynamic simulation is meant to study.', 'Requiring closed-form solutions contradicts the stated reason for numerical computation.', 'A fixed initial result does not provide repeated calculations of changing system behaviour.'])
setq('P0151-Q02','Which description correctly separates the roles of the Jetson developer kit and JetPack SDK as presented on the slide?',[
 'The kit supports edge-AI software development and testing; JetPack software supports sensor processing and robotics functions',
 'The kit is the sensor-processing software package; JetPack is the module mounted below the heat sink',
 'The kit provides the carrier board only; JetPack is the physical module that supplies computation',
 'The kit trains models only on a remote workstation; JetPack is the name of the board’s input/output ports'],
 'The source describes a hardware module/carrier-board kit and a JetPack software development kit for sensor and robotics processing.',[
 'Correct: this retains the hardware/software distinction stated on the slide.', 'This swaps the hardware kit and software SDK roles.', 'The pictured kit contains a module and carrier board; JetPack is not that physical module.', 'The stated application is edge-AI development, and JetPack is software rather than a port label.'],
 ['Answer from this lecture’s description; this is not a claim about the latest vendor product release.'])
setq('P0154-Q03','The virtual environment vrenv already exists and no environment is active. Which sequence installs rvc3python inside vrenv, then leaves it?',[
 'source vrenv/bin/activate; pip install rvc3python; deactivate',
 'pip install rvc3python; source vrenv/bin/activate; deactivate',
 'source vrenv/bin/activate; deactivate; pip install rvc3python',
 'source vrenv/bin/activate; pip uninstall rvc3python; deactivate'],
 'Activate the intended environment before installing the package, then deactivate after installation.',[
 'Correct: pip runs while vrenv is active.', 'The installation occurs before vrenv is activated.', 'The installation occurs after vrenv has been deactivated.', 'The middle command removes rather than installs the package.'],
 ['Use the slide’s shell syntax, with an existing vrenv and no initially active environment; pip refers to the active environment when one is activated.'])
setq('P0167-Q01','Which workflow best matches the slide’s proposed bridge from Python modelling to hands-on robotics?',[
 'Interpret simulated behaviour, debug and test the algorithm, then use those results to prepare the real-hardware transition',
 'Tune the controller on real hardware first, then use simulation mainly to draw the final report figures',
 'Select an AI package first, then replace debugging and behavioural tests with a check that the package imports',
 'Match one simulated trajectory, then use that match as the complete validation of the real robot'],
 'The source connects simulation analysis, logical debugging, algorithm testing before hardware deployment, and a prepared transition to real robots.',[
 'Correct: this follows the stated simulation-to-hardware preparation.', 'The source specifically proposes testing algorithms before real-hardware deployment, not using simulation only as a reporting step.', 'Import success is not a behavioural test or logical debugging.', 'One simulated match does not by itself validate real-hardware behaviour; the lecture elsewhere describes simulation limitations.'])
setq('P0137-Q02','Match these four examples to the slide’s advantages: changing test conditions; avoiding repeated prototypes; testing hazardous failures; running many experiments quickly.',[
 'Flexibility; cost efficiency; safety; speed',
 'Speed; safety; cost efficiency; flexibility',
 'Safety; flexibility; speed; cost efficiency',
 'Cost efficiency; speed; flexibility; safety'],
 'The four examples match flexibility, cost efficiency, safety, and speed in that order.',[
 'Correct: each example matches the corresponding stated advantage.', 'Changing conditions is flexibility, prototype avoidance saves cost, and hazardous testing concerns safety.', 'This assigns each example to a different advantage than the one stated.', 'Avoiding prototypes concerns cost, and running experiments quickly concerns speed.'],
 ['These are potential advantages stated by the lecture, not a guarantee that every simulation runs faster than every real experiment.'])
qmap['P0137-Q02']['difficulty']='easy';qmap['P0137-Q02']['cognitiveSkill']='recall'
setq('P0155-Q03','Which description preserves the introductory slide’s Python classification, editing/execution roles, and named file suffixes without treating the two formats as interchangeable?',[
 'Python is described as interpreted and high-level; an editor prepares code and an interpreter runs it; the slide names .py and .ipynb',
 'Python is described as interpreted and high-level; an editor alone executes the language without an interpreter; the slide names .py and .ipynb',
 'Python is described as a low-level machine language; an editor prepares code and an interpreter runs it; the slide names .py and .ipynb',
 'Python is described as interpreted and high-level; an editor prepares code and an interpreter runs it; the slide names .csv and .hdf5'],
 'The slide calls Python an interpreted high-level language, separately lists code editors and a Python interpreter, and names .py/.ipynb; its compact wording does not make scripts and notebooks identical.',[
 'Correct: this keeps the stated classification, separates editing from execution, and recalls the actual suffix pair.', 'An editor’s interface may launch an interpreter, but editing software alone does not replace the execution runtime.', 'The slide says high-level, not low-level machine language.', 'The slide names .py and .ipynb rather than those data-file suffixes.'],
 ['Use the source’s introductory classification; do not infer that implementations cannot use bytecode or compilation internally.', 'The source compresses scripts and notebooks into one line; .py and .ipynb are not asserted to share the same file format or execution path.'])
for c in b['concepts']:
 if c['id']=='W01-L04-P0137-C01':c['coverageNote']='Includes all four named benefits: flexibility, cost efficiency, safety, and speed; not a universal runtime guarantee.'
 if c['id']=='W01-L04-P0155-C01':c['coverageNote']='Includes high-level/interpreted classification, editing versus interpreter execution, paradigms/typing, package structure, and the named script/notebook suffixes with their distinction preserved.'
assert sum(question_hash(q)==question_hash(o) for q,o in zip(b['questions'],old['questions']))==107
assert b['sourceIssues']==old['sourceIssues']
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for k in sorted(changed):
 q=qmap[k];r={a:copy.deepcopy(q[a]) for a in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
 for c in r['citations']:c.pop('evidenceText',None)
 packet.append(r)
(R/'audits/blind-W01-L04-coverage-repairs.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
(R/'audits/W01-L04-coverage-repair-author-checks.json').write_text(json.dumps({'changedQuestions':24,'flaggedQuestionsRepaired':22,'existingItemsExtendedForCoverage':2,'unchangedHashes':107,'sourceIssuesPreserved':len(b['sourceIssues']),'visuallyRecheckedPhysicalPages':[129,137,140,141,145,147,148,151,154,155,167],'remainingIndependentReviewRequired':True},indent=2)+'\n')
print('24 targeted revisions frozen; 107 question hashes and all source issues preserved.')
