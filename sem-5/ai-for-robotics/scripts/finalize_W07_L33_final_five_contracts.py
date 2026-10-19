"""Freeze final L33 repair reviews; do not rerun over changed content."""
from pathlib import Path
import json,datetime,hashlib,copy,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors,validate_bank
read=lambda p:json.loads((R/p).read_text());sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(p,v):
 f=R/p;assert not f.exists();f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();ap='audits/blind-answers-W07-L33-final-five-contracts-reviewer.json';e=read(ap);r=read('audits/W07-L33-final-five-contracts-keyed-reveal.json');b=read(r['snapshotPath']);m=read(e['manifestPath']);qs={q['id']:q for q in b['questions']};prior=read('audits/W07-L33-v2-contracts-review-summary.json');obs={o['physicalPage']:o for o in e['sourceObservations']}
assert sha(ap)==r['answersSha256']=='2e678ad744b5b3c351ffff626a879ba43e3b98939604c8df8b0bb15ea1f831c0';assert e['frozenAt']<r['revealedAt'];assert sha(e['blindPacketPath'])==m['packetSha256']==e['blindPacketSha256'];assert sha(e['manifestPath'])==e['manifestSha256'];assert sha(r['snapshotPath'])==sha(r['batchPath'])==r['batchSha256'];assert sha(e['independentCheckPath'])==e['independentCheckSha256'];assert len(obs)==8
for o in obs.values():assert sha(o['previewPath'])==o['previewSha256'] and o['inspectedAt']<e['frozenAt']
for qid,h in prior['acceptedQuestionHashes'].items():assert question_hash(qs[qid])==h
assert len(prior['acceptedQuestionHashes'])==78
previous={}
for p in ['data/reviews/W07-L33-v1-independent-contracts.json','data/reviews/W07-L33-v2-independent-contracts.json']:
 for v in read(p):
  if v['decision']=='verified':previous[v['questionId']]=v
assert len(previous)==78
checks9=['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication'];reviews=[]
notes={'W07-L33-Q005':'The two-by-two same-domain mechanism alternatives remove the old hidden-parts/white-balance giveaway and match the actual car and ball panels.','W07-L33-Q007':'Parallel segmentation-versus-recognition and robustness-versus-nominal-accuracy alternatives require both distinctions. The invisible-target guarantee has been removed.','W07-L33-Q050':'All four alternatives are concrete common image representations. The rendered extended boundaries uniquely distinguish the source figure from histogram, dense appearance and point descriptors.','W07-L33-Q074':'The explicit conflictResolution now names the broad scale claims and the page1015 qualification, and page1001 is a premise rather than an unresolved component-count conflict. The scenario remains a genuine constrained synthesis.','W07-L33-Q078':'Removing the supplied score values restores an actual histogram calculation. Fresh exact fractions and within-plus-between variance checks uniquely select threshold1; the medium classification is now defensible.'}
for a in e['independentAnswers']:
 q=qs[a['questionId']];assert q['version']==a['questionVersion'];assert question_hash(q)==a['questionSha256']==m['questionHashes'][q['id']];assert q['correctOptionIds']==a['independentAnswerOptionIds'];assert e['reviewerId'] not in {q['authorId'],*q.get('revisionAuthors',[])};pages=sorted({c['physicalPage'] for c in q['citations']})
 reviews.append(dict(id=q['id']+f'-v{q["version"]}-contracts-final-repair',questionId=q['id'],questionVersion=q['version'],questionSha256=question_hash(q),reviewerId=e['reviewerId'],decision='verified',reviewedAt=now,sourceVersions=e['sourceVersions'],reviewedSlideIds=[f'lectures-p{p:04}' for p in pages],independentAnswerOptionIds=a['independentAnswerOptionIds'],solvedBeforeAnswerSeen=False,checks={k:True for k in checks9},reasoning=a['reasoning']+' '+notes[q['id']]+' All nine quality checks were applied to the exact revised object and all option explanations. Prior-version keys and solutions were seen, so this is explicitly nonblind; current responses and fresh calculations preceded current keyed access.',findings=[],blindAnswersPath=ap,blindAnswersSha256=sha(ap),independentSolvedAt=e['frozenAt'],priorAuthorExposure=True,sourceAnswerExposure=e['exposureDisclosure'],computationsPath=e['independentCheckPath'],sourceInspectionEvidence=[dict(inspectorId=e['reviewerId'],**{k:obs[p][k] for k in ['physicalPage','previewPath','previewSha256','dimensions','inspectedAt']}) for p in pages]))
assert not [err for rr in reviews for err in schema_errors(rr,read('data/schema.review.json'))]
allreviews=list(previous.values())+reviews;rr={x['questionId']:x for x in allreviews};qq=copy.deepcopy(b['questions']);cs=copy.deepcopy(b['concepts'])
for q in qq:q['status']='verified';q['reviewIds']=[rr[q['id']]['id']]
for co in cs:co['status']='verified'
sm=read('sources/manifest.json');slides=[json.loads(l) for sid in ['lectures','assignments'] for l in (R/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()];updates={v['id']:v for v in read('data/inspection-batches/W07-L33.json')['slides']};slides=[copy.deepcopy(updates.get(v['id'],v)) for v in slides]
for sl in slides:
 if sl['id'] in updates:sl['conceptIds']=[co['id'] for co in cs if sl['id'] in co['slideIds']]
tmp=dict(schemaVersion='1.0.0',bankVersion='L33-final-five-contracts-isolated',title='L33 final repair independent validation',complete=False,sources=sm['sources'],assets=sm['assets'],slides=slides,questions=qq,concepts=cs,reviews=allreviews,learningTools={k:[] for k in ['formulaSheet','confusionPairs','traps','algorithmVisualizations','numericalFamilies']});v=validate_bank(tmp,R,check_files=True);assert v['valid'],v
path='data/reviews/W07-L33-final-five-independent-contracts.json';write(path,reviews)
coverage=copy.deepcopy(read('audits/W07-L33-v2-contracts-coverage-challenge.json'));coverage['completedAt']=now;coverage['status']='All seven previously bounded gaps have verified remedies; all83current objects are independently verified with source qualifications preserved';coverage['itemLevelVerified']=83;coverage['itemLevelFlagged']=0;coverage['freshTargetedReinspections']=8;coverage['releaseComplete']=False;coverage['releaseScope']='This closes the bounded L33 review, not the complete course or offline-product release.'
for gap in coverage['gaps']:
 if gap['gapId'].endswith('G01'):gap.update(status='bounded-remedy-verified',questionVersion=qs['W07-L33-Q078']['version'],questionSha256=question_hash(qs['W07-L33-Q078']),reason=notes['W07-L33-Q078'])
write('audits/W07-L33-final-five-contracts-coverage-challenge.json',coverage)
summary=dict(batchId='W07-L33-final-five',completedAt=now,reviewerId=e['reviewerId'],reviewed=5,verified=5,flagged=0,lectureVerified=83,lectureTotal=83,acceptedPreserved=78,keyDisagreements=0,priorExposureDisclosure=e['exposureDisclosure'],actualPagesReinspected=8,priorFullSourcePages=34,freshIndependentAssertions=8,reviewFile=path,reviewSha256=sha(path),blindAnswersPath=ap,blindAnswersSha256=sha(ap),acceptedQuestionHashes={qid:question_hash(qs[qid]) for qid in sorted(qs)},coverageChallengePath='audits/W07-L33-final-five-contracts-coverage-challenge.json',boundedGapsClosed=7,validation=v,runtimeWarnings='Matplotlib default cache was read-only and the library used a temporary directory; Fontconfig emitted cache warnings and the old .A image property emitted a deprecation warning. All eight non-plotting checks completed successfully. No failed write was retried or runtime result suppressed.',mutations='Reviewer artifacts only; no author, bank, source or Git changes',nextQueue='Fresh independent L35v2 repair review, then L37v2')
write('audits/W07-L33-final-five-contracts-review-summary.json',summary)
(R/'docs/handoffs/L33-final-five-contracts-review.md').write_text(f'''# L33 final five repairs closed

All five revisions passed all nine quality checks. The 78 accepted hashes remain exact, giving 83 of 83 current questions verified. The final Otsu computation gap is now genuinely tested because the options no longer supply the variance scores. All seven previously bounded coverage remedies are verified; source qualifications remain explicit. This is not a whole-course release claim.

Review: {path}
SHA256: {sha(path)}
Frozen current responses: {ap}
SHA256: {sha(ap)}
Summary and all 83 accepted hashes: audits/W07-L33-final-five-contracts-review-summary.json

Prior-version answer exposure is disclosed for all five items. Eight actual cited pages were freshly inspected. Eight independent assertions recomputed exact Otsu statistics and executed synthetic touching/separated connected-component controls in the existing toolbox runtime before current keyed access. Original source-image runs remain in earlier frozen evidence and were not misrepresented as freshly rerun. Isolated validation: zero errors, {len(v['warnings'])} expected nonblind-review warnings.

No author, bank, source or Git changes. Do not rerun frozen scripts. Next queue: L35 v2, then L37 v2.
''')
print(json.dumps({k:summary[k] for k in ['verified','flagged','lectureVerified','reviewSha256','boundedGapsClosed']},indent=2));print('validation',len(v['errors']),len(v['warnings']))
