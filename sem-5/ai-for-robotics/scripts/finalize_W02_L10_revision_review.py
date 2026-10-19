"""Freeze independent L10 v2/GAP reviews using immutable reviewer snapshots."""
from pathlib import Path
import json,hashlib,datetime,sys,copy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash,schema_errors,validate_bank
R='define_robotics_data_contracts:L10-independent-reviewer'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads((ROOT/p).read_text())
write=lambda p,x:(ROOT/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
original=read('data/reviews/W02-L10-v1-independent.json')
obs={o['physicalPage']:o for o in read('audits/blind-answers-W02-L10-v1.json')['pageObservations']}
for o in obs.values():assert sha(ROOT/o['previewPath'])==o['previewSha256']
base=read('audits/review-snapshots/W02-L10-20261019T1700.json')
gap=read('audits/review-snapshots/W02-L10-GAP-20261019T1700.json')
assert sha(ROOT/'audits/review-snapshots/W02-L10-20261019T1700.json')=='09be9c3ade49b744f5e0a34f4cd8253cc6d4912268fe68912d20550453436ca5'
assert sha(ROOT/'audits/review-snapshots/W02-L10-GAP-20261019T1700.json')=='8720311b7fb65155eef1f805c226693030b1cb27c8fa896b8321ba1cd4fc2308'
qb={q['id']:q for q in base['questions']}
accepted=[r for r in original if r['decision']=='verified']
assert len(accepted)==44 and all(question_hash(qb[r['questionId']])==r['questionSha256'] for r in accepted)
outputs=[]
for kind,batch,answerpath,outhash,outpath in [
 ('revision',base,'audits/independent-answers-W02-L10-v2.json','e760b364f2992e7663d704a99d2ddb133ba28f9ac2c47e8d9857310158b4b891','data/reviews/W02-L10-v2-independent.json'),
 ('gap',gap,'audits/blind-answers-W02-L10-GAP-v1.json','e760661c0ae4e7d110f1414935dbc49e2f0088f765ff49d8a186f68fb6a660c0','data/reviews/W02-L10-GAP-v1-independent.json')]:
 ap=ROOT/answerpath;assert sha(ap)==outhash
 evidence=read(answerpath);answers={a['questionId']:a for a in evidence['answers']};reviews=[]
 for q in batch['questions']:
  if q['id'] not in answers:continue
  a=answers[q['id']];assert set(q['correctOptionIds'])==set(a['independentAnswerOptionIds']);assert q['version']==a['questionVersion'];assert R not in {q['authorId'],*q.get('revisionAuthors',[])}
  pages=sorted({c['physicalPage'] for c in q['citations']});checks={k:True for k in ['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']};findings=[]
  if q['id']=='W02-L10-GAP-Q002':
   checks['explanation']=False
   findings=['The o4 rationale says (2,-3) results from treating the y coefficient as 1 instead of sqrt(3)/2. That alone gives q1dot=2 and, retaining the actual x row, q2dot=-4, not -3. The offered (2,-3) is instead the solution for theta1=0 degrees, theta2=90 degrees and the same (1,2) command, using J=[[-1,-1],[1,0]]. Replace the rationale and matching misconception with this precise geometry error, or change the distractor to the actual one-coefficient-error result and review the new version. The correct key (4/sqrt(3),-1-2sqrt(3)) is independently confirmed.']
  disclosure=('I previously saw this question\'s version1 answer and explanation, so solvedBeforeAnswerSeen is false. I independently re-derived the current answer from the source and saved it before opening the version2 key or revised solution. ' if kind=='revision' else 'I had prior exposure to the lecture and earlier57 questions, but these three new author keys and solutions were unseen until all three independent answers had been frozen. ')
  reasoning=a['reasoning']+' '+disclosure+'After the answer freeze I checked every option rationale, formula variable/basis/unit assumption, cited source and difficulty label. '+('The remaining explanation defect prevents approval.' if findings else 'The current answer set and full solution pass; the repaired defect is resolved. This item-level judgment is not a full-course coverage claim.')
  reviews.append({'id':q['id']+f"-v{q['version']}-independent-review",'questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q),'reviewerId':R,'decision':'flagged' if findings else 'verified','reviewedAt':now,'sourceVersions':evidence['sourceVersions'],'reviewedSlideIds':[f'lectures-p{p:04d}' for p in pages],'independentAnswerOptionIds':a['independentAnswerOptionIds'],'solvedBeforeAnswerSeen':kind=='gap','checks':checks,'reasoning':reasoning,'findings':findings,'independentSolvedAt':a['solvedAt'],'independentAnswerEvidencePath':answerpath,'independentAnswerEvidenceSha256':outhash,'priorAuthorVersionExposure':kind=='revision','currentVersionSolvedBeforeKeyReveal':True,'sourceInspectionEvidence':[{'physicalPage':p,'inspectorId':R,'previewPath':obs[p]['previewPath'],'previewSha256':obs[p]['previewSha256']} for p in pages]})
 assert len(reviews)==len(answers)
 schema=read('data/schema.review.json');errors=[e for r in reviews for e in schema_errors(r,schema)];assert not errors,errors
 write(outpath,reviews);outputs.append((outpath,reviews))
reviews=accepted+[r for _,rs in outputs for r in rs]
qs=copy.deepcopy(base['questions']+gap['questions']);cs=copy.deepcopy(base['concepts']+gap['concepts']);rb={r['questionId']:r for r in reviews}
for q in qs:q['status']=rb[q['id']]['decision'];q['reviewIds']=[rb[q['id']]['id']]
verified={q['id'] for q in qs if q['status']=='verified'}
for c in cs:c['status']='verified' if any(qid in verified for qid in c['questionIds']) else 'drafted'
manifest=read('sources/manifest.json');slides=[json.loads(s) for sid in ['lectures','assignments'] for s in (ROOT/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()];updates={s['id']:s for s in read('data/inspection-batches/W02-L10.json')['slides']};slides=[copy.deepcopy(updates.get(s['id'],s)) for s in slides]
for s in slides:
 if s['id'] in updates:s['conceptIds']=[c['id'] for c in cs if s['id'] in c['slideIds']]
tmp={'schemaVersion':'1.0.0','bankVersion':'L10-v2-GAP-v1-independent-isolated','title':'L10 revision review validation','complete':False,'sources':manifest['sources'],'assets':manifest['assets'],'slides':slides,'questions':qs,'concepts':cs,'reviews':reviews,'learningTools':{k:[] for k in ['formulaSheet','confusionPairs','traps','algorithmVisualizations','numericalFamilies']}}
v=validate_bank(tmp,ROOT,check_files=True)
summary={'reviewerId':R,'completedAt':now,'revisionReviews':13,'revisionVerified':13,'gapReviews':3,'gapVerified':2,'gapFlagged':1,'keyedAnswerDisagreements':0,'unchangedPreviouslyVerifiedHashes':44,'currentL10VerifiedTotal':59,'currentL10QuestionsTotal':60,'reviewFiles':[{'path':p,'sha256':sha(ROOT/p)} for p,_ in outputs],'revealEvidence':'audits/W02-L10-v2-GAP-author-reveal.json','exposure':'13 revision items disclose prior v1 keyed exposure; three new GAP solves were frozen before first exposure to their keys. No self-authored items were reviewed.','coverageFindings':[{'id':'L10-COVERAGE-01','status':'closed','questionId':'W02-L10-GAP-Q001'},{'id':'L10-COVERAGE-02','status':'open_pending_explanation_repair','questionId':'W02-L10-GAP-Q002'},{'id':'L10-COVERAGE-03','status':'closed','questionId':'W02-L10-GAP-Q003'}],'flaggedQuestionIds':['W02-L10-GAP-Q002'],'validation':v,'mutations':'Only independent review/audit/script/handoff files; no author batch, source, canonical bank or Git edits.'}
write('audits/W02-L10-v2-GAP-review-summary.json',summary)
handoff='''# L10 revision and gap review frozen\n\nAll 13 v2 repairs verified; two of three new GAP items verified. GAP Q002 has the correct key but an inaccurate o4 explanation. Changing only its y coefficient gives (2,-4), not (2,-3); the latter instead uses theta1=0 degrees, theta2=90 degrees. Exact finding is in data/reviews/W02-L10-GAP-v1-independent.json.\n\nAll 44 earlier approved hashes remain unchanged. Total current reviewed slice: 59 verified of 60 questions. Original source caveats remain preserved. Two of the three coverage findings are closed; inverse-command coverage is pending the explanation repair.\n\nReview files: data/reviews/W02-L10-v2-independent.json and data/reviews/W02-L10-GAP-v1-independent.json. Summary: audits/W02-L10-v2-GAP-review-summary.json. Answer freeze and reveal provenance are separate immutable files. The 13 revision reviews disclose previous v1 key exposure and do not claim first-time blindness; new GAP solves were frozen before keyed access.\n\nReviewer snapshots in audits/review-snapshots preserve exactly reviewed content if author repairs the flagged item. No bank, question, source or Git edits. Next assignment is fresh L14 authoring.\n'''
(ROOT/'docs/handoffs/L10-v2-GAP-review.md').write_text(handoff)
print(json.dumps(summary,ensure_ascii=False,indent=2));assert v['valid'],v
