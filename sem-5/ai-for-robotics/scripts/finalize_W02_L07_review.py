"""Bind completed independent L07 review to the exact frozen question versions."""
import json,datetime,hashlib,copy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash,schema_errors,validate_bank
bp=ROOT/'audits/blind-answers-W02-L07-v1.json';blind=json.loads(bp.read_text());packet=json.loads((ROOT/'audits/blind-W02-L07.json').read_text());batchpath=ROOT/'data/question-batches/W02-L07.json';batch=json.loads(batchpath.read_text())
assert len(blind['answers'])==61 and len(blind['sourceVisualObservations'])==26
assert hashlib.sha256(bp.read_bytes()).hexdigest()=='0b329a8fdaba83f03fbe18da67a7fa5372619f03cf51a0fe2ca0443de6bf7f43'
assert hashlib.sha256(batchpath.read_bytes()).hexdigest()=='ac2ecaaf6e742dceec3f3d1a4248b4403ba967795fce28ac13e846bccdccdcbb'
answers={x['questionId']:x for x in blind['answers']};byid={q['id']:q for q in batch['questions']}
for x in packet:
 for k,v in x.items():assert byid[x['id']][k]==v,(x['id'],k)
notes={x['physicalPage']:x for x in blind['sourceVisualObservations']}
flags={
40:({'explanation':False},['The choice-3 rationale says sin(theta1) sin(theta3) belongs to a different product entry. In the derived RPR rotation, R22=−sin(theta1) sin(theta3), so the positive expression is the negative of that entry, not another entry as stated. Correct this rationale (and its repeated misconception text) without changing the correct −cos(theta1) answer.']),
43:({'figureFidelity':False,'explanation':False},['The justification says the figure labels radius r and two half-width segments d. The actual diagram shows one midpoint-to-wheel d segment; r and full separation 2d are defined in the accompanying text. Attribute the radius/full width to the text and only the shown half-width to the diagram. The keyed geometry answer is correct.']),
47:({'assumptions':False,'explanation':False},['The equality v_r=−v_l permits v_r=v_l=0, which gives rest rather than rotation. The keyed option says opposite speeds alone specify in-place rotation. Add an explicit nonzero-speed assumption or qualify this as zero center translation, with in-place rotation only for nonzero speeds; retain the clockwise condition v_r<0 and counterclockwise condition v_r>0.'])}
now=datetime.datetime.now(datetime.timezone.utc).isoformat();reviews=[]
calcids={24,25,26,33,34,35,36,39,40,41,42,44,45,46,47,50,51,52,53,54,55,56,57,58,59,60}
for n,q in enumerate(batch['questions'],1):
 a=answers[q['id']];assert set(a['independentAnswerOptionIds'])==set(q['correctOptionIds'])
 checks={k:True for k in ['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']}
 findings=[]
 if n in flags:change,findings=flags[n];checks.update(change)
 pages=sorted({c['physicalPage'] for c in q['citations']});assert all(p in notes for p in pages)
 calculation='The relevant matrix identities, arithmetic, coordinate order, units or zero/sign limits were independently derived and checked; symbolic/numeric details are saved in audits/independent-checks-W02-L07.json.' if n in calcids else 'No numerical evaluation or algorithm trace is requested; the named definitions, mechanism roles and option distinctions were checked directly against the inspected source.'
 reasoning=a['reasoning']+' After this independent answer was persisted, the full author solution, every option rationale, formula variables/units/assumptions and difficulty were read. '+calculation+' The source pixels, not extraction alone, support the cited interpretation. Difficulty is easy/medium rather than an inflated hard label; shared source pages are not counted as duplication when the tested angle differs.'
 if findings:reasoning+=' The answer set matches, but the listed explanation/assumption/figure issue prevents verification.'
 reviews.append({'id':q['id']+'-v1-independent-review','questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q),'reviewerId':blind['reviewerId'],'decision':'flagged' if findings else 'verified','reviewedAt':now,'sourceVersions':blind['sourceVersions'],'reviewedSlideIds':[f'lectures-p{p:04d}' for p in pages],'independentAnswerOptionIds':a['independentAnswerOptionIds'],'solvedBeforeAnswerSeen':True,'checks':checks,'reasoning':reasoning,'findings':findings})
schema=json.loads((ROOT/'data/schema.review.json').read_text());errors=[e for r in reviews for e in schema_errors(r,schema)];assert not errors,errors
out=ROOT/'data/reviews/W02-L07-v1-independent.json';out.write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n')
# Validate an isolated in-memory integration. No bank or author writes.
manifest=json.loads((ROOT/'sources/manifest.json').read_text());slides=[json.loads(line) for sid in ['lectures','assignments'] for line in (ROOT/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()];updates={x['id']:x for x in json.loads((ROOT/'data/inspection-batches/W02-L07.json').read_text())['slides']};slides=[updates.get(x['id'],x) for x in slides]
# Author inspection slice is a raw visual ledger; materialize reciprocal concept links
# and accountable page dispositions only in this temporary integration.
for slide in slides:
 if slide['id'] in updates:
  slide['conceptIds']=[c['id'] for c in batch['concepts'] if slide['id'] in c['slideIds']]
  if slide['conceptIds']:
   slide['disposition']='examinable';slide['exclusionReason']=None
  elif slide['physicalPage'] in [243,244,245,267,268]:
   slide['disposition']='excluded';slide['exclusionReason']='Title, objectives, outline, references or closing courtesy only; no independent technical proposition.'
questions=copy.deepcopy(batch['questions']);concepts=copy.deepcopy(batch['concepts']);rby={r['questionId']:r for r in reviews}
for q in questions:q['status']=rby[q['id']]['decision'];q['reviewIds']=[rby[q['id']]['id']]
verified={q['id'] for q in questions if q['status']=='verified'}
for c in concepts:
 if c['status']!='flagged':c['status']='verified' if any(i in verified for i in c['questionIds']) else 'drafted'
tmp={'schemaVersion':'1.0.0','bankVersion':'L07-v1-independent-isolated','title':'Independent L07 temporary integration','complete':False,'sources':manifest['sources'],'assets':manifest['assets'],'slides':slides,'questions':questions,'concepts':concepts,'reviews':reviews,'learningTools':{'formulaSheet':[],'confusionPairs':[],'traps':[],'algorithmVisualizations':[],'numericalFamilies':[]}}
validation=validate_bank(tmp,ROOT,check_files=True);assert validation['valid'],validation
checks=json.loads((ROOT/'audits/independent-checks-W02-L07.json').read_text())
summary={'schemaVersion':'1.0.0','batchId':'W02-L07','reviewerId':blind['reviewerId'],'completedAt':now,'questionCount':61,'verified':58,'flagged':3,'keyedAnswerDisagreements':0,'blindAnswerEvidencePath':str(bp.relative_to(ROOT)),'blindAnswerEvidenceSha256':hashlib.sha256(bp.read_bytes()).hexdigest(),'frozenBlindPacketSha256':hashlib.sha256((ROOT/'audits/blind-W02-L07.json').read_bytes()).hexdigest(),'reviewedAuthorBatchSha256':hashlib.sha256(batchpath.read_bytes()).hexdigest(),'reviewPath':str(out.relative_to(ROOT)),'reviewSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'pagesIndividuallyInspected':list(range(243,269)),'citedPagesIndividuallyInspected':sorted({c['physicalPage'] for q in batch['questions'] for c in q['citations']}),'independentCalculationChecks':len(checks['checks']),'flags':[{'questionId':f'W02-L07-Q{n:03d}','findings':items[1]} for n,items in flags.items()],'validation':validation,'sourceUncertainties':['Physical 256 expanded row3,column2 is inconsistent with the printed factors; sin(alpha_(i−1))cos(theta_i) follows from multiplication.','Physical 261 expanded row2,column3 prints −cos(theta3); multiplying factors gives −cos(theta1).','Physical 263 opposite-wheel clockwise label needs sign and zero-speed qualification.','Physical 256 prose frame-direction wording should not override the explicit column-vector mapping convention in the question formula metadata.','Physical 266 six-joint summary needs local independence, nonsingularity and task-scope qualifications.'],'coverageScope':'This certifies the individual listed questions only, with three flags. It is not an exhaustive lecture or full-course coverage certificate.','coverageAdvisories':['The objectives mention PUMA 560, but these 26 pages contain planar 3R and RPR worked models rather than a PUMA 560 worked derivation. Do not claim the objective is fulfilled from these pages.','The bank is all easy/medium. A later coverage challenge should consider genuinely harder composition, convention/error diagnosis and wheel-control scenarios rather than relabeling direct recall as hard.','The brief application/advantage bullets for differential drive, and the full kinematics derivative hierarchy, deserve explicit coverage review beyond mere page-to-question linkage.','Q055/Q056 scaling statements should be read as algebraic scale factors; zero-rate boundary values remain zero. This does not invalidate the general formulas.'],'validationNormalization':'The raw author inspection ledger retains unreviewed dispositions and empty conceptIds. The isolated test materialized reciprocal concept links and examinable/excluded dispositions in memory, as integration must do; no source or inspection file was changed.','mutations':'Only reviewer-owned audit/check/review/handoff files were written; no author batch, source, Git or bank edits.'}
(ROOT/'audits/W02-L07-review-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['questionCount','verified','flagged','keyedAnswerDisagreements','independentCalculationChecks','reviewSha256','validation']},indent=2))
