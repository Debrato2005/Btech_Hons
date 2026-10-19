"""Freeze L33 source-first independent review. Do not rerun after author repairs."""
from pathlib import Path
import json, hashlib, datetime, sys, copy
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash, schema_errors, validate_bank
read=lambda p:json.loads((ROOT/p).read_text());sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
ap='audits/blind-answers-W07-L33-v1-contracts-reviewer.json';e=read(ap)
assert sha(ap)=='0f1e1eccecc489ab416e6da563449fb26c86618384663e24b83c4d6ac56acb2d'
reveal=read('audits/W07-L33-contracts-keyed-reveal.json');b=read(reveal['snapshotPath']);m=read(e['manifestPath']);hm={v['questionId']:v for v in m['questions']}
assert e['frozenAt']<reveal['revealedAt'] and not e['priorVersionExposure']
assert sha(ap)==reveal['answersSha256']
assert sha(e['blindPacketPath'])==e['blindPacketSha256']==m['blindPacketSha256']
assert sha(reveal['snapshotPath'])==sha('data/question-batches/W07-L33.json')==reveal['snapshotSha256']
c=read(e['independentCheckPath']);assert sha(e['independentCheckPath'])==e['independentCheckSha256']
assert c['assertionCount']==41 and c['randomTrials']==1000 and c['checksPerTrial']==3
assert c['completedAt']<e['frozenAt']
qs={q['id']:q for q in b['questions']};obs={o['physicalPage']:o for o in e['sourceObservations']}
assert set(obs)==set(range(987,1021))
for o in obs.values():assert sha(o['previewPath'])==o['previewSha256'] and o['inspectedAt']<e['frozenAt']
flags=read('audits/W07-L33-contracts-quality-findings.json')['findings']
checks9=['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']
reviews=[]
for a in e['independentAnswers']:
 q=qs[a['questionId']];assert question_hash(q)==a['questionSha256']==hm[q['id']]['questionSha256'];assert q['version']==a['questionVersion']==hm[q['id']]['questionVersion']
 assert sorted(q['correctOptionIds'])==sorted(a['independentAnswerOptionIds']);assert e['reviewerId'] not in {q['authorId'],*q.get('revisionAuthors',[])}
 pages=sorted({v['physicalPage'] for v in q['citations']});checks={k:True for k in checks9}
 for f in flags.get(q['id'],[]):checks[f['criterion']]=False
 reason=a['reasoning']+' All 34 actual source pages and text were inspected before these 77 independent responses were frozen. All five original-image examples were independently transcribed and executed in toolbox 2.4.1, with 41 explicit assertions and 1000 three-check trials. Author answers, solutions, generator, calculations and coverage ledger were read only after the blind freeze. The intended key agrees; agreement alone does not establish citation, distractor, difficulty or coverage quality. Every formula record, option rationale, numerical working and source qualification was examined. '+('This exact version is blocked by the findings below.' if q['id'] in flags else 'All nine item-level criteria pass for this version. The separate seven-angle bounded coverage challenge remains open.')
 reviews.append(dict(id=q['id']+f'-v{q["version"]}-contracts-independent-quality',questionId=q['id'],questionVersion=q['version'],questionSha256=question_hash(q),reviewerId=e['reviewerId'],decision='flagged' if q['id'] in flags else 'verified',reviewedAt=now,sourceVersions=e['sourceVersions'],reviewedSlideIds=[f'lectures-p{p:04}' for p in pages],independentAnswerOptionIds=a['independentAnswerOptionIds'],solvedBeforeAnswerSeen=True,checks=checks,reasoning=reason,findings=[f['finding'] for f in flags.get(q['id'],[])],blindAnswersPath=ap,blindAnswersSha256=sha(ap),independentSolvedAt=e['frozenAt'],priorAuthorExposure=False,sourceAnswerExposure=e['exposureDisclosure'],computationsPath=e['independentCheckPath'],externalEvidence=e['externalEvidence'],sourceInspectionEvidence=[dict(inspectorId=e['reviewerId'],**{k:obs[p][k] for k in ['physicalPage','previewPath','previewSha256','dimensions','inspectedAt']}) for p in pages]))
assert len(reviews)==77 and len(flags)==29
assert not [err for r in reviews for err in schema_errors(r,read('data/schema.review.json'))]
out='data/reviews/W07-L33-v1-independent-contracts.json';write(out,reviews)
rb={r['questionId']:r for r in reviews};qq=copy.deepcopy(b['questions']);cs=copy.deepcopy(b['concepts'])
for q in qq:q['status']=rb[q['id']]['decision'];q['reviewIds']=[rb[q['id']]['id']]
verified={q['id'] for q in qq if q['status']=='verified'}
for co in cs:co['status']='verified' if any(qid in verified for qid in co['questionIds']) else 'drafted'
sm=read('sources/manifest.json');slides=[json.loads(l) for sid in ['lectures','assignments'] for l in (ROOT/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()]
updates={v['id']:v for v in read('data/inspection-batches/W07-L33.json')['slides']};slides=[copy.deepcopy(updates.get(v['id'],v)) for v in slides]
for sl in slides:
 if sl['id'] in updates:sl['conceptIds']=[co['id'] for co in cs if sl['id'] in co['slideIds']]
tmp={'schemaVersion':'1.0.0','bankVersion':'L33-contracts-isolated','title':'L33 independent review validation','complete':False,'sources':sm['sources'],'assets':sm['assets'],'slides':slides,'questions':qq,'concepts':cs,'reviews':reviews,'learningTools':{k:[] for k in ['formulaSheet','confusionPairs','traps','algorithmVisualizations','numericalFamilies']}}
v=validate_bank(tmp,ROOT,check_files=True)
gaps=[
 {'id':'L33-G01','physicalPages':[995],'angle':'Numerical Otsu threshold selection','finding':'Q009 identifies the criterion but never evaluates weighted within-class or between-class variance for competing histogram splits.','boundedRemedy':'Supply a small explicit histogram and class-membership boundary convention; compare at least two candidate thresholds with weighted means/variances. This is an added worked example of the slide criterion, not a claimed original source dataset.'},
 {'id':'L33-G02','physicalPages':[997],'angle':'Nonidentity primary-mixture and chromaticity chain','finding':'Q014, Q015 and Q016 separately scale sensitivities, select a symbolic inverse and normalize an already supplied RGB vector. No item performs the coupled matrix solve and normalization.','boundedRemedy':'Give an invertible nonidentity 3-by-3 response matrix and an explicit stimulus/response vector. Solve Ap=c and normalize the resulting coefficients, with units, linearity and nonzero-sum assumptions.'},
 {'id':'L33-G03','physicalPages':[1001],'angle':'Named alternatives for complex segmentation scenes','finding':'The source explicitly names MSER and graph-based algorithms, but no question or substantive concept record tests even this bounded distinction.','boundedRemedy':'Add a narrowly source-attributed identification/application item covering the two named alternatives, without inventing mechanics, guarantees or thresholds absent from the slides.'},
 {'id':'L33-G04','physicalPages':[1002,1003],'angle':'Pixels to raw moments to equivalent ellipse','finding':'Q030-Q034 begin with supplied moments or eigenvalues; no item computes raw moments from an actual declared small binary region and follows through to its central matrix and axis geometry.','boundedRemedy':'A revised Q034 can close this gap: supply finite foreground coordinates and weights, compute raw moments and centroid, then the central matrix, eigenaxis and semiaxes. Declare the image frame, nonzero area and axis modulo pi. Avoid relabeling the existing short eigenproblem as hard.'},
 {'id':'L33-G05','physicalPages':[1011,1012],'angle':'Oblique Hough geometry with vote-boundary application','finding':'Q056 uses only theta=0; Q058 counts support and Q075 separately states the strict threshold. No item derives a non-axis-aligned normal angle and signed rho and applies the vote boundary.','boundedRemedy':'Supply an oblique point set with explicit theta domain and image frame, derive its candidate parameters, count support and apply the stated strict threshold. Keep ideal geometry separate from quantized OpenCV bins.'},
 {'id':'L33-G06','physicalPages':[1014],'angle':'Windowed image gradients to Harris response','finding':'Q062 names product averaging, while Q064 starts with a diagonal matrix. The computation distinguishing the average of gradient products from products of averaged gradients is absent.','boundedRemedy':'Provide a few noncollinear gradient samples and normalized nonnegative weights; form the full matrix including off-diagonal terms, evaluate C and interpret the result. Contrast the actual wrong product-of-averages computation in a plausible distractor.'},
 {'id':'L33-G07','physicalPages':[1017],'angle':'Harris nfeat code semantics','finding':'The source call requests Harris(nfeat=500), but the current bank only tests SIFT filtering and plot markers. Maximum requested feature count is not the same as a guarantee of 500 available corners or semantic classes.','boundedRemedy':'Add a bounded code question distinguishing the nfeat cap from detected count, scale and class count, citing the actual code and exact primary/versioned API evidence where needed.'}
]
excluded={987:'Title only',988:'Objectives only',989:'Contents only',1019:'References only',1020:'Thanks only'}
pageledger=[]
for p,o in sorted(obs.items()):
 qids=[q['id'] for q in b['questions'] if any(c['physicalPage']==p for c in q['citations'])]
 pageledger.append(dict(physicalPage=p,sourceSha256=e['sourceVersions']['lectures'],inspectorId=e['reviewerId'],previewPath=o['previewPath'],previewSha256=o['previewSha256'],observed=o['observations'],disposition='excluded-nontechnical' if p in excluded else 'repeated-technical-summary' if p==1018 else 'substantive',exclusionReason=excluded.get(p),questionIds=qids,conceptIds=[co['id'] for co in cs if f'lectures-p{p:04}' in co['slideIds']],openGapIds=[g['id'] for g in gaps if p in g['physicalPages']]))
assert all(v['questionIds'] for v in pageledger if v['physicalPage'] not in excluded)
coverage=dict(batchId='W07-L33',reviewerId=e['reviewerId'],completedAt=now,status='Bounded independent omission challenge completed; seven substantive angles remain open',releaseComplete=False,actualPagesInspected=34,originalSubstantivePages=28,repeatedTechnicalSummaryPages=1,nontechnicalExclusions=5,substantivePagesWithCitations=29,conceptRecords=77,warning='One concept record per question and citation coverage on every technical page do not establish concept/angle completeness.',pages=pageledger,gaps=gaps,itemLevelVerified=48,itemLevelFlagged=29,difficultyCounts=dict(Counter(q['difficulty'] for q in b['questions'])),selectionModes=dict(Counter(q['selectionMode'] for q in b['questions'])),questionFormats=dict(Counter(q['type'] for q in b['questions'])),formatFinding='There is one multiple-select Hu item and several diagram/matching questions. The pool is heavily easy recall (61/77), and its sole hard label is not justified by current depth; the bounded synthesis gaps provide meaningful harder angles without paraphrase inflation.',answerPresentation='Stable option IDs exhibit a stored cycle. No new user-facing clue is alleged: the parent has implemented answer-independent default presentation permutations. This reviewer did not repeat browser QA.',reviewFile=out,sourceIssuesRemainQualified=True)
write('audits/W07-L33-contracts-coverage-challenge.json',coverage)
a=read('audits/W07-L33-author-checks.json');o=c['observed'];ar=a['sourceRuns']
comparisons={'sameFiveSourceAssetHashes':all(a['assets'][name]['sha256']==rec['sha256'] for name,rec in c['sourceAssets'].items()),'otsuThreshold':o['castle']['otsuThreshold']==ar['castle']['otsu'],'targetChromaticCentroids':o['targets']['chromaticCentroids']==ar['targets']['clusterCentroids'],'topBlobArea':o['targets']['blob3']['area']==ar['targets']['areas'][3],'topRasterPixelCount':o['targets']['topRasterPixelCount']==ar['targets']['topTargetRasterCount'],'polarSimilarities':o['targets']['polarSimilarity']==ar['targets']['polarSimilarity'],'fivePointHoughLines':o['fivePoints']['threshold2Lines']==ar['houghFivePoints']['linesThreshold2'],'churchSegments':o['church']['segments']==ar['church']['segments'],'SiftFilteredCount':o['building']['siftFilteredCount']==ar['keypoints']['siftFilteredCount']}
assert all(comparisons.values())
su=dict(batchId='W07-L33',completedAt=now,reviewerId=e['reviewerId'],reviewed=77,verified=48,flagged=29,keyDisagreements=0,actualPagesInspected=34,sourcePages=list(range(987,1021)),priorVersionExposure=False,independentAssertions=41,randomTrials=1000,checksPerTrial=3,sourceExamplesIndependentlyExecuted=['castle.png','yellowtargets.png','5points.png','church.png','building2-1.png'],runtimeVersions=c['versions'],reviewFile=out,reviewSha256=sha(out),blindAnswersPath=ap,blindAnswersSha256=sha(ap),validation=v,flaggedQuestionIds=list(flags),findings=[dict(questionId=qid,criteria=[z['criterion'] for z in fs],findings=[z['finding'] for z in fs]) for qid,fs in flags.items()],coverageChallengePath='audits/W07-L33-contracts-coverage-challenge.json',coverageGaps=gaps,authorComparisonAfterBlindFreeze=comparisons,sourceQualifications=read('audits/W07-L33-source-issues.json'),qualificationSummary=['Adaptive h=15 is a 31-by-31 mean-minus-C neighborhood, not the printed full-width label or generic mu-minus-k-sigma model.','Contour blob area 5609.5 and raster count 5762 are different conventions; blob orientation is equivalent to the printed value modulo pi.','Five points with h.lines(2) produce two candidates; the minimum-three-votes comment is consistent with strict OpenCV threshold, not an error.','Literal Canny defaults to L1; the independent L1 and L2 edge counts differ.','percentstrength uses a fraction of maximum response, not half the count.','Faster R-CNN boxes do not by themselves constitute masks; the additional branch distinction is preserved.','Historical all-primary mercury attribution is excluded rather than silently accepted.'],mutations='Reviewer evidence, check/finalizer scripts, snapshot, review and handoff only. No author objects, canonical bank, source files or Git edits.',nextQueue=['L30 final five repair review','L34 fresh source-first review'])
write('audits/W07-L33-contracts-review-summary.json',su)
(ROOT/'docs/handoffs/L33-v1-contracts-review.md').write_text(f'''# L33 independent review frozen

48 of 77 objects verified, 29 flagged, zero intended-key disagreements. All 34 actual pages 987–1020 were personally inspected before answers and computations were frozen. Fresh L33 review with no prior author-key exposure. All nine quality checks were applied to each exact version.

Five original source-image examples independently executed in toolbox 2.4.1 and OpenCV 5.0.0.93. Forty-one explicit assertions and 1000 three-check trials passed. The independent runtime agrees with the author run after keyed reveal, but remains separately transcribed and evidenced. Code-caption, API-default, contour/raster and orientation qualifications remain explicit; no source issue was globally resolved.

Review: {out}
Review SHA256: {sha(out)}
Blind answers: {ap}
Blind answer SHA256: {sha(ap)}
Summary: audits/W07-L33-contracts-review-summary.json
Coverage challenge: audits/W07-L33-contracts-coverage-challenge.json

The 29 flags concern credible distractors, item-level exact evidence for external/API corrections, missing cross-page premises, one repeated family-mapping item and difficulty calibration. No key or executed numerical result is rejected. Preserve all 48 accepted hashes while making versioned repairs; a second independent reviewer must assess revisions. All 29 substantive/summary pages have citations, but seven bounded angles remain: numerical Otsu selection, full primary-matrix/chromaticity chain, named MSER/graph alternatives, pixels-to-moments-to-ellipse synthesis, oblique Hough geometry with threshold, gradient-products-to-Harris response, and Harris nfeat semantics.

Do not rerun this finalizer after author changes or alter frozen answers. No author, bank, source or Git edits. Next queue: first L30 final five repairs (packet audits/blind-W06-L30-final-five.json, SHA256 f81e4e20a2ce71c084a04ab64b29f2502f33ac6ca434f60a00bf1e4662cd5a39), then fresh L34. Disclose prior L30 v1 exposure. L34 keys must remain unopened until its source-based answers are frozen.
''')
print(json.dumps({'verified':48,'flagged':29,'reviewSha256':sha(out),'validation':v,'comparisons':comparisons},indent=2));assert v['valid'],v
