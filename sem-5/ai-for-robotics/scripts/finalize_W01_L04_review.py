"""Finalize a resumed review without reattributing the original reviewer's blind work.
Only reviewer-owned outputs are written. No author, bank, source, or Git writes.
"""
import pathlib,json,hashlib,datetime,sys,copy,collections
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash,schema_errors,validate_bank
R='define_robotics_data_contracts:L04-continuation-reviewer'
oldp=ROOT/'audits/blind-answers-W01-L04-v1.json';newp=ROOT/'audits/blind-answers-W01-L04-v1-continuation.json';bp=ROOT/'data/question-batches/W01-L04.json'
expected={oldp:'50b0106805308529ca51b0a49f2f475a57917bb6fbbb7bc7a631dbe4e346fa5e',newp:'bd6dbdcc92d437dada082436a58442da6673b5f1cc8098b61172f0638967d571',bp:'aaf536abf4b31cff534f4efed66a49f84b6c108102959279117e7236934f8e3d'}
for p,h in expected.items():assert hashlib.sha256(p.read_bytes()).hexdigest()==h,(p,'frozen hash changed')
old=json.loads(oldp.read_text());new=json.loads(newp.read_text());batch=json.loads(bp.read_text());questions=batch['questions'];manifest=json.loads((ROOT/'audits/W01-L04-frozen-question-hashes.json').read_text());packet=json.loads((ROOT/'audits/blind-W01-L04.json').read_text());answers={a['questionId']:a for a in old['answers']+new['answers']};byid={q['id']:q for q in questions}
assert len(old['answers'])==83 and len(new['answers'])==48 and len(answers)==131
for q in packet:
 for k,v in q.items():assert byid[q['id']][k]==v,(q['id'],k)
for q in questions:assert question_hash(q)==manifest[q['id']]==answers[q['id']]['questionSha256']
allobs=old['pageObservations']+new['pageObservations'];obs={p:[o for o in allobs if o['physicalPage']==p] for p in range(125,171)}
assert all(obs.values())
for o in allobs:assert hashlib.sha256((ROOT/o['previewPath']).read_bytes()).hexdigest()==o['previewSha256']
flags={}
def flag(k,check,message):
 qid='W01-L04-'+k;assert qid in byid
 flags.setdefault(qid,{'checks':{},'findings':[]});flags[qid]['checks'][check]=False;flags[qid]['findings'].append(message)
for k,reason in {
'P0132-Q02':'The reason directly restates the purpose of relevance-based simplification; the assertion-reason format does not itself make this hard.',
'P0138-Q03':'This is the direct continuous-model versus discrete-numerical-evaluation distinction, with no discretization derivation or error analysis.',
'P0142-Q01':'Applying the separate definitions of detail and fidelity to one miscalibrated sensor scenario is medium-level discrimination, not a multistage hard problem.',
'P0144-Q02':'This directly applies the source\'s own slope-flip example to verification versus validation, without a novel inference chain.',
'P0157-Q07':'Shape compatibility versus arbitrary addition/matrix multiplication is a basic conceptual distinction; no actual broadcasting shapes must be resolved.',
'P0160-Q02':'The stem already isolates the bare newline and absence of continuation. Recognizing the resulting parse error is medium-level code reading.',
'P0162-Q07':'Two strict comparisons at 0.5 are a short boundary trace, not a hard algorithm problem.',
'P0162-Q08':'Two strict comparisons at 1.0 are a short boundary trace, not a hard algorithm problem.',
'P0163-Q05':'Distinguishing print from an implicit None return is a standard medium-level Python misconception, not a hard trace.',
'P0166-Q03':'Summing four explicitly supplied 2D segment norms is a routine multistep numerical exercise; medium is appropriate.'
}.items():flag(k,'difficulty',reason+' Change hard to medium, or genuinely redesign the reasoning task and obtain new review; do not retain the inflated label.')
# Reject demonstrably off-topic filler, not merely easy but plausible misconceptions.
for k,reason,repair in [
('P0127-Q01','Bookkeeping, typography and accounting are conspicuously unrelated filler in the theoretical-foundation choices.','Use nearby robotics/mathematical/computational foundation confusions rather than unrelated professions.'),
('P0151-Q01','A remote cloud server and Python virtual environment cannot plausibly be the pictured I/O hardware.','Use same-level kit components such as module, carrier, interface/controller or power board, with unambiguous image references.'),
('P0152-Q02','The distractor that removes all interpreters before running ROS and the plot-before-install sequence are artificial failures rather than realistic setup-order confusions.','Use plausible boot, environment, dependency, interpreter-selection and execution ordering mistakes.'),
('P0153-Q01','All three distractor pairs are package tools, editors or data workflows rather than plausible initial-flashing alternatives.','Use credible boot-media/flashing methods and reversed source-preference choices.'),
('P0153-Q02','Selecting a browser as the Python interpreter and requiring no interpreter are conspicuously implausible.','Keep alternatives at the relevant architecture/package-format and system-versus-venv interpreter level.'),
('P0154-Q01','Creating a physical GPU and automatically repairing syntax are unrelated to virtual-environment isolation.','Use realistic dependency/version, interpreter-sharing, global-package and activation-scope misconceptions.'),
('P0155-Q02','Equating a Python dependency package with the Jetson carrier board is off-topic hardware filler.','Use plausible Python toolbox/dependency relationships, with every alternative remaining software-related.'),
('P0159-Q01','The alternative saying phase portraits are CSV tables and line plots hardware drivers is not a plausible visualization misconception.','Use state-axis versus time-axis, trajectory versus phase-flow and equilibrium/stability interpretation mistakes.'),
('P0159-Q02','Every wrong mapping uses visibly nonplotting operations such as venv, apt, pi, read_csv or groupby.','Use real plotting/animation APIs in incorrectly matched roles, not unrelated operations.'),
('P0159-Q03','Bode plots reading CSV and FuncAnimation performing a matrix inverse are off-topic filler.','Use plausible function-ownership confusions across Matplotlib, Seaborn and python-control.'),
('P0160-Q01','The path-plot/np.eye/name-the-table option is unrelated to constructing a datetime-indexed table.','Use plausible date-unit, conversion-order, index and timestamp-retention mistakes.'),
('P0160-Q06','The wrong four-function mappings mainly use image rendering, ODEs, installation or virtual-environment creation instead of competing tabular-data operations.','Permute the actual resample/rolling/groupby/merge roles or use credible window-versus-group/time-alignment errors.'),
('P0160-Q07','The otherwise relevant mutating-summary misconception is bundled with the implausible claim that to_csv trains a controller.','Replace that clause with a credible export/return-value/in-place misunderstanding.'),
('P0161-Q04','The distractors rely on Python guessing a function name, invalidating ordinary named parameters, or silently adding arguments.','Offer plausible NameError versus TypeError versus a valid but unintended call/return behavior, with the namespace still explicit.'),
('P0164-Q01','Randomly choosing constructor values is not a plausible explanation of the shown inheritance.','Use realistic initializer lookup, missing-constructor TypeError or explicit parent-initializer misconceptions.'),
('P0165-Q01','Booting Jetson or creating venv through numerical/plotting functions is conspicuously unrelated.','Use incorrect but plausible assignments among numerical arrays, Euclidean distance and plotting roles.'),
('P0166-Q07','Converting path into a Pandas DataFrame or computing distance cannot plausibly result from this in-place addition.','Replace o3/o4 with meaningful floating-promotion, truncation, value-dependent casting or aliasing alternatives. Retain the exact tested casting rule and subtle first-row dtype issue.'),
('P0168-Q01','All wrong core-stack sets visibly mix libraries with editors, operating systems or a package manager.','Use plausible four-library stacks so source recall, not category spotting, distinguishes the answer.'),
('P0168-Q02','The Pandas/Matplotlib/venv/editor option is unrelated to the named acceleration mechanisms.','Use plausible permutations or competing acceleration-library associations.'),
('P0168-Q03','Calling rclpy an image format or venv creation command is unrelated filler.','Use credible ROS client-library, middleware, simulator and hardware-driver role confusions.'),
('P0168-Q05','Changing a code editor and file extension is unrelated to reducing physical simulation mismatch.','Replace that option with a plausible but insufficient model calibration, validation or randomization strategy.'),
('P0158-Q07','CSV parsing, a JavaScript plotting backend and a Jetson bootloader are all implausible competing linear-algebra foundations.','Use plausible numerical backends or linear-algebra implementation confusions.'),
('P0159-Q04','Both rejected choices are unrelated boot-image preparation and class definition; selecting the two visualization choices requires no substantive discrimination.','Use plausible but incorrect visualization purposes or graph/matrix interpretation confusions.'),
('P0159-Q05','apt with sqrt and np.linalg with venv are nonsensical alternatives to an animation technique.','Use real animation/rendering techniques and meaningful blitting versus full-redraw/update confusions.'),
('P0160-Q08','np.eye is an unrelated identity-matrix constructor in this time-alignment question.','Replace it with a credible Pandas alignment/interpolation/window operation while retaining a uniquely supported named source operation.'),
('P0168-Q06','Every incorrect option is unrelated editor themes, hardware construction or font/image formatting.','Use plausible numerical control/modeling tasks with clear optimize-versus-integrate/signal/linalg distinctions.')
]:flag(k,'distractors',reason+' '+repair)
flag('P0160-Q04','explanation','The o4 rationale says [50,25,16.667] inverts the needed relationship. The inverse of the correct velocities [1,2,3] is [1,0.5,0.333], not those values. The displayed distractor is approximately the reciprocals of the position increments [0.02,0.04,0.06], omitting elapsed-time scaling. Explain that actual error mechanism and its units, or change the distractor consistently. Also update the repeated misconception entry. The keyed [1,2,3] m/s remains correct.')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();reviews=[]
for q in questions:
 a=answers[q['id']];assert set(a['independentAnswerOptionIds'])==set(q['correctOptionIds'])
 pageids=sorted({c['physicalPage'] for c in q['citations']});assert all(p in obs for p in pageids)
 checks={k:True for k in ['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']};f=flags.get(q['id'],{'checks':{},'findings':[]});checks.update(f['checks'])
 inherited=a['reviewerId']!=R
 reasoning=(('The blind answer and derivation below were persisted by '+a['reviewerId']+' before author reveal; the continuation reviewer did not re-solve or reattribute that original work. ') if inherited else 'I independently solved this question before author reveal and persisted the derivation in the separate continuation evidence. ')+a['reasoning']+' After all 131 blind answers were frozen, I audited this full author solution, every option rationale, numerical steps and available formula metadata against the attributed visual observations and execution evidence. The answer set matches. '+('The listed quality finding prevents verification.' if f['findings'] else 'The source scope and assumptions support the answer; no material answer, solution, distractor, difficulty or duplication defect was found.')
 reviews.append({'id':q['id']+'-v1-independent-review','questionId':q['id'],'questionVersion':1,'questionSha256':question_hash(q),'reviewerId':R,'independentSolverId':a['reviewerId'],'independentSolvedAt':a['solvedAt'],'independentAnswerEvidencePath':str((oldp if inherited else newp).relative_to(ROOT)),'independentAnswerEvidenceSha256':expected[oldp if inherited else newp],'sourceInspectionEvidence':[{'physicalPage':p,'inspectorIds':sorted({o['inspectorId'] for o in obs[p]}),'previewSha256':obs[p][0]['previewSha256']} for p in pageids],'decision':'flagged' if f['findings'] else 'verified','reviewedAt':now,'sourceVersions':new['sourceVersions'],'reviewedSlideIds':[f'lectures-p{p:04d}' for p in pageids],'independentAnswerOptionIds':a['independentAnswerOptionIds'],'solvedBeforeAnswerSeen':True,'checks':checks,'reasoning':reasoning,'findings':f['findings']})
schema=json.loads((ROOT/'data/schema.review.json').read_text());errors=[e for r in reviews for e in schema_errors(r,schema)];assert not errors,errors
out=ROOT/'data/reviews/W01-L04-v1-independent.json';out.write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n')
# Isolated in-memory integration using the author's already-linked inspection slice.
sources=json.loads((ROOT/'sources/manifest.json').read_text());slides=[json.loads(s) for sid in ['lectures','assignments'] for s in (ROOT/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()];updates={s['id']:s for s in json.loads((ROOT/'data/inspection-batches/W01-L04.json').read_text())['slides']};slides=[copy.deepcopy(updates.get(s['id'],s)) for s in slides]
qs=copy.deepcopy(questions);cs=copy.deepcopy(batch['concepts']);rby={r['questionId']:r for r in reviews}
for q in qs:q['status']=rby[q['id']]['decision'];q['reviewIds']=[rby[q['id']]['id']]
verified={q['id'] for q in qs if q['status']=='verified'}
for c in cs:
 if c['status']!='flagged':c['status']='verified' if any(i in verified for i in c['questionIds']) else 'drafted'
tmp={'schemaVersion':'1.0.0','bankVersion':'L04-v1-independent-isolated','title':'L04 independent temporary validation','complete':False,'sources':sources['sources'],'assets':sources['assets'],'slides':slides,'questions':qs,'concepts':cs,'reviews':reviews,'learningTools':{'formulaSheet':[],'confusionPairs':[],'traps':[],'algorithmVisualizations':[],'numericalFamilies':[]}}
v=validate_bank(tmp,ROOT,check_files=True)
# Save the result even when a validation assertion would fail, preserving recovery.
summary={'schemaVersion':'1.0.0','batchId':'W01-L04','reviewerId':R,'completedAt':now,'questionCount':131,'verified':sum(r['decision']=='verified' for r in reviews),'flagged':len(flags),'keyedAnswerDisagreements':0,'originalBlindSolverId':old['reviewerId'],'originalBlindAnswers':83,'continuationBlindSolverId':R,'continuationBlindAnswers':48,'originalBlindEvidencePath':str(oldp.relative_to(ROOT)),'originalBlindEvidenceSha256':expected[oldp],'continuationBlindEvidencePath':str(newp.relative_to(ROOT)),'continuationBlindEvidenceSha256':expected[newp],'originalEvidenceUnchanged':True,'authorRevealEvidencePath':'audits/W01-L04-author-reveal.json','reviewedAuthorBatchSha256':expected[bp],'reviewPath':str(out.relative_to(ROOT)),'reviewSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'allPagesWithAttributedVisualInspection':list(range(125,171)),'originalReviewerPages':list(range(125,161)),'continuationPersonallyInspectedPages':sorted(o['physicalPage'] for o in new['pageObservations']),'originalCodeChecks':19,'continuationCodeChecks':24,'flagCountsByCheck':dict(collections.Counter(k for f in flags.values() for k in f['checks'])),'flags':[{'questionId':k,**f} for k,f in flags.items()],'validation':v,'sourceUncertaintiesPreserved':batch['sourceIssues'],'coverageScope':'This is an item-level independent answer and quality review, not an exhaustive lecture/full-course coverage certificate. Source uncertainties and excluded broad claims remain open where stated.','coverageAdvisories':['The 41 concept records are broad section-level groupings, not an atomized full concept ledger; source-page linkage alone cannot establish every meaningful angle covered.','Eight ecosystem-category questions and six SciPy-module questions cover distinct categories but mostly recall. Add genuinely harder supported applications and error diagnosis rather than relabeling direct recall as hard.','The literal syntax, np.block nesting, command typos and function-name defects remain distinct from explicitly repaired examples. Do not silently rewrite the source.','P0160-Q05 is self-contained through its assumptions, which repeat the test times and positions; the study interface must show assumptions before answering.','Formula coordinate unit metadata in P0166-Q02 can be made more explicit in a future version; current common-scale assumption and coordinate-unit answers avoid an unspecified physical unit.','The eight-row summary contains unbounded 90%, 5–10-line, any-system, industry-standard and automatic-portability claims; these are not verified as general facts.'],'mutations':'Only reviewer-owned scripts/audits/reviews/handoff were written. Original 83-solve evidence remains byte-for-byte unchanged. No author batch, source, bank or Git edits.'}
(ROOT/'audits/W01-L04-review-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['questionCount','verified','flagged','keyedAnswerDisagreements','flagCountsByCheck','reviewSha256','validation']},indent=2));assert v['valid'],v
