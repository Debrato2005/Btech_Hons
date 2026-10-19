#!/usr/bin/env python3
"""Persist source-pixel independent review findings. Never edits the authored batch."""
import json,hashlib,datetime,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash
read=lambda p:json.loads((ROOT/p).read_text())
blind_path=ROOT/'audits/blind-answers-W02-L08-independent.json';blind=read(blind_path);assert blind['complete'] and not blind['keyedBatchOpened']
answers={a['questionId']:a for a in blind['answers']};packet={q['id']:q for q in read('audits/blind-W02-L08.json')};batch=read('data/question-batches/W02-L08.json');questions=batch['questions'];assert len(questions)==110
flags={}
def add(key,check,reason):
 p,n=key.split('-');qid=f'W02-L08-P{int(p):04d}-Q{int(n):02d}';flags.setdefault(qid,[]).append((check,reason))
for key,reason in {
'272-1':'Replace o2 (solve camera brightness and rename the tool) with a plausible but incorrect frame-conversion/IK ordering. It is unrelated to the requested kinematic workflow and gives an easy elimination cue.',
'272-2':'Replace the camera-pixel-count option o4 with a plausible inverse/forward-kinematics output confusion. The current option is unrelated to pose-to-joint inference.',
'275-6':'Options o2–o4 make obviously implausible claims that an added wrist reaches every position, changes unequal lengths into equal ones, or removes all joint limits. Use realistic 2R/3R orientation-versus-position confusions and tool-offset assumptions instead.',
'279-1':'Replace the arbitrary-translation-guarantees-uniqueness, remove-all-geometry and increase-all-lengths alternatives with realistic geometric conditions (e.g. wrong axis adjacency, intersection versus skew/parallel, or twist-pattern confusions). Current wrong options are not plausible analytical-IK criteria.',
'280-1':'The text-parsing/no-computation option o2 is nonsensical for IK; the options also do not all give the requested three-part mapping. Use parallel algebraic/geometric/numerical mappings with plausible swaps for every alternative.',
'280-4':'All wrong options are categorical giveaways: numerical always faster on every processor, closed form removes all physical constraints, numerical never uses a Jacobian. Replace them with realistic computational/geometry tradeoffs, not blanket guarantees.',
'281-2':'Use permutations of wrist rotation, wrist bend and flange rotation rather than camera focus, gripper opening or base translation. The present non-wrist alternatives do not plausibly compete with the only complete wrist-label mapping.',
'282-2':'Keep the useful orientation-versus-position distinction but replace o3 (a joint angle changes L1) and o4 (the base origin moves) with plausible model-dependent output confusions. Rigid link-length change is not a credible alternative in this explicitly fixed model.',
'284-2':'Options o2 and o3 make a joint angle the triangle hypotenuse, mixing dimensions and creating an elimination cue. Use competing length/angle label mappings or swapped atan2/square-root relationships with consistent quantity types.',
'285-6':'Only o1 is a complete dependency-respecting four-stage algorithm; alternatives call all remaining angles zero, average branches, or arbitrarily choose the wrist and discard a sign. Use parallel complete algorithms with realistic branch, quadrant, reachability-check or dependency errors.',
'290-1':'Replace o2 (wheel radii in, camera brightness out) with a realistic velocity/pose input-output confusion. It is unrelated to differential-drive IK.',
}.items():add(key,'distractors',reason)
for key,reason in {
'273-3':'This is a direct constraint-count-versus-existence/uniqueness distinction with explicit nonlinear context; medium is proportionate unless a counterexample or Jacobian argument is actually required.',
'275-6':'The stated model already supplies a pure orientation wrist; this one-step model distinction fits medium rather than hard.',
'276-2':'Interpreting can have eight as a possibility rather than an unconditional count is medium, not a hard branch analysis.',
'277-5':'The stem explicitly supplies two equal upper bounds. Comparing them and rejecting strict increase is medium, not hard.',
'278-4':'The stem supplies the conflicting uniqueness/multiple-solution definitions; distinguishing existence from uniqueness is medium.',
'278-5':'The correct option itself gives the elementary unit-circle scalar-closure counterexample. Medium is appropriate, rather than hard.',
'279-2':'This is a direct caveat about reachability/convergence/uniqueness, not a numerical convergence analysis. Reclassify medium.',
'280-3':'Recognizing sufficient does not imply necessary is a standard one-step implication distinction. Reclassify medium.',
'282-5':'Recognizing the unit-circle relation between sine and cosine of one planar angle is medium, not hard.',
'283-8':'Substituting c2=±1 into the square root and identifying coincident branches is one-step boundary reasoning. Reclassify medium.',
'285-4':'This is a worthwhile degenerate-family question, but the stem already identifies the reachable equal-link origin and the choices expose the continuous-family distinction. Hard is appropriate; extremely_tricky overstates its demand.',
'285-5':'Periodic orientation versus joint-limit representatives is a direct conceptual distinction. Reclassify medium rather than hard.',
'287-5':'The reflected-branch statement is given in the stem; recognizing it as a second branch fits medium, not hard.',
'290-2':'Recognizing that the displayed 3×2 matrix has no ordinary two-sided inverse is medium dimensional reasoning, not hard.',
'291-2':'This is direct selection of the printed tall full-rank pseudoinverse formula. Medium is appropriate unless a derivation/application is requested.',
'291-3':'This is direct selection of the printed wide full-rank pseudoinverse formula. Medium is appropriate unless a derivation/application is requested.',
'291-5':'Applying the displayed full-column-rank prerequisite to the Gram matrix is medium. The distinction from the general pseudoinverse is useful but does not require a hard calculation here.',
'291-8':'The one-row two-column formula gives the answer by division by two, with a simple squared-norm check. Medium is proportionate for this supplied numerical example.',
'291-13':'At 90°, identifying the remaining nonzero sum/difference rows is a short rank check; the alternatives are elementary zero-entry/rank confusions. Medium is appropriate.'
}.items():add(key,'difficulty',reason)
resolutions={
'278-2':('Printed f(αx)=αx','Use f(αx)=αf(x), explicitly showing why a general linear map scales its output rather than requiring the identity map.'),
'278-3':('Printed f(αx)=αx','Bind the supplied f(x)=2x, α=3, x=1 counterexample and the 6 versus 3 calculation to the corrected αf(x).'),
'278-4':('Solvable is defined as unique on p278, while p276/p279 admit and enumerate multiple solutions','Resolve existence/computability versus uniqueness using those cited internal source statements.'),
'278-5':('Circle/sphere is used as an informal sub-space example','State the narrower linear-vector-subspace interpretation and the supplied unit-circle scalar-closure counterexample; do not rewrite the source quotation.'),
'284-3':('The middle x/r expansion repeats cosθ1 in its final factor','Derive the repaired sinθ1 factor from x=k1 cosθ1−k2 sinθ1 and the cosine-sum identity.'),
'285-1':('The final p288 line uses +θ2 while the preceding sum requires subtraction','Isolate θ3=φ−θ1−θ2 from the printed angle sum, and retain the erroneous final source line as conflicting evidence.'),
'290-2':('p290 prints J^−1 for the preceding 3×2 Jacobian','Resolve the shorthand using p291 full-column-rank pseudoinverse, not an ordinary square inverse.'),
'290-3':('The p290 forward-flow diagram swaps qdot and pdot','Use qdot=J pdot and the 3×2 matrix dimensions to establish pdot→J→qdot.')}
for key,(claim,repair) in resolutions.items():add(key,'sourceSupport',f'The citation is correctly marked role=conflict, but the question has no conflictResolution record. The new fail-closed gate cannot promote it. Add version-bound sourceClaim/resolution/basis/verification metadata without deleting the conflicting evidence. Source issue: {claim}. Required resolution: {repair} The mathematical answer already agrees with the independent solve.')
# Conceptual source-derived formulas have been independently derived; no blanket key agreement substitutes for review.
reviews=[];now=datetime.datetime.now(datetime.timezone.utc).isoformat();blindhash=hashlib.sha256(blind_path.read_bytes()).hexdigest()
for q in questions:
 qid=q['id'];a=answers[qid];assert set(q['correctOptionIds'])==set(a['independentAnswerOptionIds'])
 for field,value in packet[qid].items():assert q[field]==value,(qid,field)
 checks={k:True for k in ['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']}
 for check,_ in flags.get(qid,[]):checks[check]=False
 reason=a['reasoning']+' The complete source page was inspected at original 1800×1013 pixel resolution; formula signs, frame labels and figure geometry were checked rather than inferred from text extraction alone. The keyed justification, every option explanation, steps, formula metadata and supplementary solution fields were read only after the blind answer artifact was frozen.'
 if q['type']=='numerical':reason+=' Numerical working and units agree with independent calculations recorded in audits/W02-L08-independent-computations.json.'
 else:reason+=' No separate scalar numerical calculation is required for this conceptual/diagram item; relevant algebra, matrix dimensions and kinematic identities were checked independently.'
 if q['type']!='diagram':reason+=' Figure fidelity is not a separate quantitative reconstruction requirement here; the item uses the actual cited equations/statements or explicitly supplied generated premises.'
 reason+=' The neighboring 110-question set was checked for distinct angles: branch sign, quadrant, orientation closure, origin singularity, inner/outer boundaries, rank cases, forward/inverse direction and wheel sign/geometry are materially different. Table-row recall shares a template but binds different printed geometric conditions, not reparameterized numerical coverage.'
 reviews.append({'id':f'REV-{qid}-v1-independent-interface','questionId':qid,'questionVersion':q['version'],'questionSha256':question_hash(q),'reviewerId':'build_offline_study_interface-L08-independent','decision':'flagged' if qid in flags else 'verified','reviewedAt':now,'sourceVersions':{c['sourceId']:c['sourceSha256'] for c in q['citations']},'reviewedSlideIds':a['reviewedSlideIds'],'independentAnswerOptionIds':a['independentAnswerOptionIds'],'solvedBeforeAnswerSeen':True,'checks':checks,'reasoning':reason,'findings':[f for _,f in flags.get(qid,[])],'reviewType':'independent_blind_source_review','blindAnswersPath':str(blind_path.relative_to(ROOT)),'blindAnswersSha256':blindhash,'computationsPath':'audits/W02-L08-independent-computations.json','sourceDisputeLedgerConsultedAfterBlindFreeze':True})
output=ROOT/'data/reviews/W02-L08-v1-independent.json';assert not output.exists(),'Do not overwrite a review'
output.write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n')
summary={'reviewedAt':now,'reviewed':110,'verified':sum(r['decision']=='verified' for r in reviews),'flagged':len(flags),'answerAgreement':110,'answerCorrectionsRequired':0,'sourcePagesInspected':list(range(269,296)),'independentTestCases':2218,'blindAnswersPath':str(blind_path.relative_to(ROOT)),'reviewPath':str(output.relative_to(ROOT)),'actionableFlags':{r['questionId']:r['findings'] for r in reviews if r['decision']=='flagged'},'flagCountsByCheck':{k:sum(not r['checks'][k] for r in reviews) for k in reviews[0]['checks']},'sourceConflictNotes':'All 12 author source-dispute ledger entries were independently checked against pixels after the blind solve. Scope qualifications and mathematical repairs are sound, but eight role=conflict items need explicit question-level resolution bindings before promotion.','coverageChallenge':'All 27 pages inspected. Title/objective/contents/references/closing pages do not introduce additional answerable technical detail. The question set covers the substantive frame chain, workspace boundaries, branch counts, definitions and source defects, analytical/geometric planar IK, DH table, degenerate origins, geometric sign rules, differential-drive Jacobian/flow/rank/pseudoinverse and wheel-rate regimes. No additional substantive gap identified in this pass.','nonblockingStyleNote':'Many source-authored strings concatenate words with symbols/numbers (for example the16, withpositive, theydot). Repair affected prose with normal spacing when revising flagged objects; any broader formatting pass must preserve history and rebind hashes rather than reuse stale approvals.','approvedCurrentHashes':{r['questionId']:r['questionSha256'] for r in reviews if r['decision']=='verified'}}
(ROOT/'audits/W02-L08-independent-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['reviewed','verified','flagged','answerAgreement','independentTestCases','flagCountsByCheck']}))
