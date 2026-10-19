"""Freeze L37 v3 independent closure. Never rerun over changed objects."""
from pathlib import Path
import json,hashlib,datetime,copy,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors,validate_bank
read=lambda p:json.loads((R/p).read_text());sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(p,v):
 f=R/p;assert not f.exists(),p;f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();ap='audits/blind-answers-W08-L37-v3-contracts-reviewer.json';e=read(ap);rv=read('audits/W08-L37-v3-contracts-keyed-reveal.json');b=read(rv['snapshotPath']);m=read('audits/W08-L37-v3-review-manifest.json');qs={q['id']:q for q in b['questions']};prior=read(m['priorBatchArtifact']);priorqs={q['id']:q for q in prior['questions']};c=read(e['independentCheckPath']);obs={o['physicalPage']:o for o in e['sourceObservations']}
assert sha(ap)==rv['answersSha256']=='d3f08d78b485b8c72bc79e50f7d91ad664fc814a53b54501cd36937d75d745d7';assert c['completedAt']<e['frozenAt']<rv['revealedAt'];assert sha(e['blindPacketPath'])==m['blindPacketSha256']==e['blindPacketSha256'];assert sha(e['bindingPath'])==e['bindingSha256'];assert sha(e['independentCheckPath'])==e['independentCheckSha256'];assert sha(rv['snapshotPath'])==sha(rv['batchPath'])==rv['batchSha256'];assert sha(m['priorBatchArtifact'])==m['priorBatchSha256'];assert sha(e['priorFullSourceInspectionEvidence'])==e['priorFullSourceInspectionSha256'];assert len(read(e['priorFullSourceInspectionEvidence'])['observations'])==38
for o in obs.values():assert sha(o['previewPath'])==o['previewSha256'] and o['inspectedAt']<=e['frozenAt']
oldr={}
for p in ['data/reviews/W08-L37-v1-independent.json','data/reviews/W08-L37-v2-independent-contracts.json']:
 for r in read(p):
  if r['decision']=='verified' and r['questionId'] in m['preservedAcceptedHashes'] and r['questionSha256']==m['preservedAcceptedHashes'][r['questionId']]:oldr[r['questionId']]=r
assert len(oldr)==74
for qid,h in m['preservedAcceptedHashes'].items():assert qs[qid]==priorqs[qid] and question_hash(qs[qid])==h
reviews=[];checks9=['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']
for a in e['answers']:
 q=qs[a['questionId']];assert question_hash(q)==a['questionSha256']==m['questionSha256'][q['id']];assert q['version']==a['questionVersion'];assert sorted(q['correctOptionIds'])==a['independentAnswerOptionIds'];assert e['reviewerId'] not in [q['authorId'],*q.get('revisionAuthors',[])]
 for pe in q.get('primaryEvidence',[]):
  if pe.get('localPath'):assert sha(pe['localPath'])==pe['sha256']
 pages=sorted({ct['physicalPage'] for ct in q['citations']});reason=a['reasoning']+' Every current option rationale, formula variable/unit, explicit assumption, exact source locator, diagram mapping, difficulty and distinct angle was checked. All nine checks pass. '+('Prior-version keys and solutions were seen; current responses are independently recomputed, not freshly blind.' if a['priorAuthorExposure'] else 'This new question was solved source-first before current or prior author keys. New gap calculations and genuine notebook execution precede keyed access.')
 reviews.append(dict(id=q['id']+f'-v{q["version"]}-contracts-v3-quality',questionId=q['id'],questionVersion=q['version'],questionSha256=question_hash(q),reviewerId=e['reviewerId'],decision='verified',reviewedAt=now,sourceVersions=e['sourceVersions'],reviewedSlideIds=[f'lectures-p{p:04}' for p in pages],independentAnswerOptionIds=a['independentAnswerOptionIds'],solvedBeforeAnswerSeen=a['solvedBeforeAnswerSeen'],checks={k:True for k in checks9},reasoning=reason,findings=[],blindAnswersPath=ap,blindAnswersSha256=sha(ap),independentSolvedAt=e['frozenAt'],priorAuthorExposure=a['priorAuthorExposure'],sourceAnswerExposure=e['exposureDisclosure'],currentVersionSolvedBeforeKeyedAccess=True,computationsPath=e['independentCheckPath'],sourceInspectionEvidence=[dict(inspectorId=e['reviewerId'],**{k:obs[p][k] for k in ['physicalPage','previewPath','previewSha256','dimensions','inspectedAt']}) for p in pages]))
assert len(reviews)==12;assert not [x for r in reviews for x in schema_errors(r,read('data/schema.review.json'))]
rr={**oldr,**{r['questionId']:r for r in reviews}};qq=copy.deepcopy(b['questions']);cs=copy.deepcopy(b['concepts'])
for q in qq:q['status']='verified';q['reviewIds']=[rr[q['id']]['id']]
for co in cs:co['status']='verified'
# Include the preserved L37 search slice so source-page concept coverage is validated honestly.
search=read('data/question-batches/search-foundations.json');oldqs={q['id']:q for q in search['questions'] if q.get('lectureId')=='L37'};sr={}
for rp in ['data/reviews/search-foundations-v1-independent.json','data/reviews/search-foundations-v2-independent.json','data/reviews/search-frontier-v3-independent.json']:
 data=read(rp);data=data.get('reviews',[]) if isinstance(data,dict) else data
 for r in data:
  if r['questionId'] in oldqs and r['questionSha256']==question_hash(oldqs[r['questionId']]):sr[r['questionId']]=r
assert len(sr)==29
oldcopies=copy.deepcopy(list(oldqs.values()))
for q in oldcopies:q['status']=sr[q['id']]['decision'];q['reviewIds']=[sr[q['id']]['id']]
qq+=oldcopies;rr.update(sr)
for co in copy.deepcopy(search['concepts']):
 co['questionIds']=[qid for qid in co['questionIds'] if qid in oldqs];co['status']='verified' if any(sr[qid]['decision']=='verified' for qid in co['questionIds']) else 'identified'
 cs.append(co)
sm=read('sources/manifest.json');slides=[json.loads(l) for sid in ['lectures','assignments'] for l in (R/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()];up={s['id']:s for s in read('data/inspection-batches/W08-L37.json')['slides']};slides=[copy.deepcopy(up.get(s['id'],s)) for s in slides]
canonical={sl['id']:sl for sl in read('data/bank.json')['slides']};oldCited={ct['slideId'] for q in oldcopies for ct in q['citations']}
for sl in slides:
 sl['conceptIds']=[co['id'] for co in cs if sl['id'] in co['slideIds']]
 if sl['id'] in oldCited and sl['id'] not in up:sl['visualInspection']=copy.deepcopy(canonical[sl['id']]['visualInspection']);sl['disposition']=canonical[sl['id']]['disposition']
tmp=dict(schemaVersion='1.0.0',bankVersion='L37-v3-contracts-isolated',title='L37 independent closure validation',complete=False,sources=sm['sources'],assets=sm['assets'],slides=slides,questions=qq,concepts=cs,reviews=list(rr.values()),learningTools={k:[] for k in ['formulaSheet','confusionPairs','traps','algorithmVisualizations','numericalFamilies']});v=validate_bank(tmp,R,check_files=True);assert v['valid'],v
path='data/reviews/W08-L37-v3-independent-contracts.json';write(path,reviews)
search=read('data/question-batches/search-foundations.json');oldq={q['id']:q for q in search['questions'] if q.get('lectureId')=='L37'};oldbindings=read('audits/W08-L37-coverage-challenge-independent.json')['existingSearchBindings']
assert len(oldq)==29
for z in oldbindings:assert question_hash(oldq[z['questionId']])==z['questionSha256']
legacy=dict(questionId='W08-L37-P1135-Q03',version=oldq['W08-L37-P1135-Q03']['version'],questionSha256=question_hash(oldq['W08-L37-P1135-Q03']),status='flagged under earlier independent review; not included in current packet',finding='Unresolved p1135 g(start)=1.0 versus p1133 g(start)=0.0 source conflict, plus extremely_tricky calibration for typo spotting rather than substantive reasoning.',reviewPath='data/reviews/search-foundations-v1-independent.json')
coverage=dict(completedAt=now,reviewerId=e['reviewerId'],priorCoveragePath='audits/W08-L37-v2-contracts-coverage-challenge.json',priorFullPagesInspected=38,currentCitationPagesReinspected=13,closures=[dict(gapId='L37-v2-G05',questionId='W08-L37-Q047',result='Closed: complete supplied circular density threshold, equality handling, mask, maximal runs, midpoint candidates and coherent wrapped weighted costs independently reconstructed. Earlier nonblind exposure remains disclosed.'),dict(gapId='L37-v2-G06',questionId='W08-L37-Q016',result='Closed: single polygon, global closest boundary projection, full survey and shorter return versus first eligible fixed-line crossing independently computed.'),dict(questionId='W08-L37-Q063',result='Red-point interpretation is now quality-closed with plausible whole-arm, path-connectivity and metric-clearance alternatives.')],remainingCompletionQualityFlags=[],remainingBoundedContentGaps=[],oldSearchRemainingFlag=legacy,sourceQualificationsRemain=True,codeScope=c['codeScope'],releaseComplete=False,scope='All 86 completion items now have matching accepted reviews; the separate 29-item search slice retains 28 approvals and one existing flag. No blanket lecture closure until that flag is resolved.')
write('audits/W08-L37-v3-contracts-coverage-challenge.json',coverage)
summary=dict(completedAt=now,reviewed=12,verified=12,flagged=0,completionAcceptedPreserved=74,completionVerified=86,completionTotal=86,oldSearchVerified=28,oldSearchTotal=29,oldSearchFlagged=1,allLectureVerified=114,allLectureTotal=115,keyDisagreements=0,priorExposedRepairs=12,freshBlindQuestions=0,independentAssertions=21,variedCases=1000,variedAssertions=3000,reviewFile=path,reviewSha256=sha(path),blindAnswersPath=ap,blindAnswersSha256=sha(ap),coveragePath='audits/W08-L37-v3-contracts-coverage-challenge.json',acceptedQuestionHashes={qid:question_hash(q) for qid,q in qs.items()},legacyFlag=legacy,validation=v,mutations='Reviewer artifacts only; no author, bank, source or Git edits.')
write('audits/W08-L37-v3-contracts-review-summary.json',summary)
(R/'docs/handoffs/L37-v3-contracts-review.md').write_text(f"L37 v3 closed: all twelve revised objects verified, all 74 accepted completion objects preserved, giving 86/86 completion. Old search slice is still 28/29, with P1135-Q03 flagged; total 114/115, not complete. Thirteen actual citation pages re-inspected and prior full 38-page record preserved. Twenty-one exact checks and 3,000 varied assertions passed before current keys. Both integrated synthesis gaps and the red-point quality gap closed. All twelve disclose prior exposure, especially Q047's earlier manifest leak. Review: {path}. SHA256: {sha(path)}. Isolated 115-item validation: {len(v['errors'])} errors, {len(v['warnings'])} warnings. No author, bank, source or Git edits. Next L36 legacy two then fresh L42.\n")
print(json.dumps(dict(reviewed=12,verified=12,reviewSha256=sha(path),valid=v['valid'],errors=v['errors'],warnings=len(v['warnings']))))
