import json,pathlib,hashlib,datetime,importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[3]; OUT=ROOT/'audits/question-visual-review/early-inputs'
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def qhash(q):return digest({k:v for k,v in q.items() if k not in ('status','reviewIds')})
m=json.load(open(ROOT/'data/question-visuals/manifest.json'));rs={r['questionId']:r for r in m['records']};qs={q['id']:q for p in (ROOT/'data/question-batches').glob('*.json') for q in json.load(open(p))['questions']}
batches=[json.load(open(p))|{'batchFile':str(p.relative_to(ROOT))} for p in sorted(OUT.glob('L??-*.json'))]; read={r['questionId']:r for b in batches for r in b['records']}; flags={i for b in batches for i in b['excludedForMissingDependencyIds']}; reviews={r['questionId']:r for p in (ROOT/'data/question-visuals/reviews').glob('L??-self-contained-early-review.json') for r in json.load(open(p))}; current={i for i,r in rs.items() if qs[i]['lectureId'] in [f'L{n:02}' for n in range(1,20)] and r['dependencyStatus']=='self_contained'}
groups=[]
def group(ids,reason,pages):
 for i in ids.split():groups.append({'questionId':i,'missingDependency':reason,'suggestedPremisePhysicalPages':pages})
group('W01-L03-P0119-Q02 W01-L03-P0119-Q03','Algorithm comparison lacks T_A=100n+1000 and T_B=n^2+1; those appear only in the preceding question.',[119])
group('W01-L04-P0157-Q03','Whole-snippet execution in a fresh namespace requires preceding import/R definitions; shown block call alone cannot distinguish intended exception from undefined-name failures.',[157])
group('W01-L04-P0157-Q06','Original quaternion q values are absent; required q=[0.1,-0.5,1.2,0.8].',[157])
group('W01-L04-P0161-Q05','Function-return question omits the compute_distance body; physical constant-speed assumption does not define the actual program.',[161])
group('W01-L04-P0163-Q01','Robot/robot1 class-versus-instance identification requires declarations, not name capitalization alone.',[163])
group('W01-L04-P0164-Q01','Inherited constructor explanation requires the omitted class inheritance and base initializer declarations.',[164])
group('W01-L04-P0166-Q02','Numeric Euclidean distance requires path endpoint and goal values from preceding code.',[165,166])
group('W01-L05-Q-024','Callback trigger requires actual create_subscription registration; callback method name does not distinguish timer from subscription.',[])
group('W02-L07-Q026','Numerical modified-DH transform omits the printed factor order Rx(alpha) Dx(a) Rz(theta) Dz(d).',[256])
group('W02-L07-Q035 W02-L07-Q039','Specific source-arm transform requires omitted geometry/frame assignment or printed RPR factors, beyond given joint/length symbols.',[])
group('W02-L08-P0287-Q03','Triangle beta/psi angle definitions are absent, so numeric angles lack a specified geometric meaning.',[287])
group('W02-L08-P0289-Q07','Source-specific numeric generalized-velocity vector requires omitted output row order.',[289])
group('W02-L08-P0291-Q11','Pseudoinverse computation requires the omitted differential-drive Jacobian and coordinate order.',[291])
group('W02-L10-GAP-Q002 W02-L10-Q006 W02-L10-Q009 W02-L10-Q010 W02-L10-Q011 W02-L10-Q015 W02-L10-Q018 W02-L10-Q020 W02-L10-Q021 W02-L10-Q022 W02-L10-Q023 W02-L10-Q036 W02-L10-Q037 W02-L10-Q041','Source planar-arm/frame construction is absent; lengths and joint angles do not determine mechanism arrangement, axes, or source-specific transforms.',[329])
group('W03-L11-P0365-Q04 W03-L11-P0365-Q05 W03-L11-P0366-Q02 W03-L11-P0370-Q01','Ordered cuboid tensor components require omitted width/length/height assignment to x/y/z and signed corner geometry.',[365,366,370])
group('W03-L11-P0376-Q01','Identify-the-missing-term comparison requires both source acceleration equations, neither supplied.',[359,376])
group('W03-L12-Q040','Numerical task-space controller output requires the omitted controller law, not merely numerical gains, errors, gravity, and Jacobian.',[])
group('W03-L13-Q006 W03-L13-Q007 W03-L13-Q010 W03-L13-Q011 W03-L13-Q014 W03-L13-Q026 W03-L13-Q034 W03-L13-Q046','Source two-point-mass arm geometry, frame conventions, or endpoint-mass model is absent from this standalone instance.',[407,408])
group('W03-L13-Q020','Cross-term sign needs the omitted surrounding negative l2 coefficient in the acceleration expression.',[])
group('W03-L14-Q035','Potential-energy zero requires its arbitrary additive reference. The complete model does not imply the stated U constant. p444 top total U includes m1*l1*g + m2*g*d2max.',[443,444])
group('W03-L15-Q032','Numeric expanded Vx requires tool-axis map J and Jdot. Use p463 matrices, not p465 expanded Vx answer.',[463])
group('W04-L16-P0496-Q02 W04-L16-P0496-Q04 W04-L16-P0496-Q05 W04-L16-P0496-Q06','Unnamed cubic example omits its 10-degree to 70-degree rest-to-rest five-second boundary data.',[496])
group('W04-L16-P0499-Q05','Limiting behavior of source A/B computation requires the omitted actual matrix/vector construction code.',[499])
group('W04-L16-P0501-Q02','Maximum versus minimum velocity at zero acceleration requires the omitted positive profile direction.',[501])
group('W04-L17-Q055','Why acceleration arrays stay zero requires actual source assignments, specifically np.zeros_like code.',[534])
group('W04-L18-Q063 W04-L18-Q064','Source 2R endpoint/radial calculation omits fixed-frame and relative-angle/FK convention.',[])
group('W04-L18-Q076','Inclusive 200-point grid maximum reach requires omitted linspace interval bounds.',[])
assert {g['questionId'] for g in groups}==flags
for g in groups:
 i=g['questionId'];r=rs[i];g.update(lectureId=qs[i]['lectureId'],questionSha256=qhash(qs[i]),originalVisualSha256=read[i]['visualSha256'],currentVisualSha256=digest(r),currentDependencyStatus=r['dependencyStatus'],currentAssetIds=r['assetIds'],assetReviewScope='No asset approval; independent positive crop review is required.')
stale=[i for i,r in reviews.items() if r['visualSha256']!=digest(rs[i]) or r['questionSha256']!=qhash(qs[i])]
coverage=[]
for n in range(1,20):
 l=f'L{n:02}';ids={i for i in read if qs[i]['lectureId']==l};coverage.append({'lectureId':l,'fullyReadCount':len(ids),'acceptedCount':len(ids&set(reviews)),'withheldCount':len(ids&flags),'currentSelfContainedCount':len(ids&current),'reviewFile':f'data/question-visuals/reviews/{l}-self-contained-early-review.json','fullyReadIds':sorted(ids),'acceptedIds':sorted(ids&set(reviews)),'withheldIds':sorted(ids&flags)})
result={'reviewerId':'review_early_question_inputs','scope':'Complete current stem, every option, and every assumption were read for the original 1449 self_contained L01-L19 records. Question-input completeness only; no answer-correctness re-review and no positive asset approval. Each batch snapshot records exact reviewed question/record hashes. No regex/type or old-answer-review blanket approval.','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceVersions':m['sourceVersions'],'sourceHashVerification':'Both local source PDF SHA-256 values independently recomputed and matched before receipt creation.','manifestSnapshotSha256':digest(m),'fullyReadCount':len(read),'negativeReceiptsCount':len(reviews),'missingDependencyCount':len(flags),'currentSelfContainedCount':len(current),'unreadCurrentSelfContainedIds':sorted(current-set(read)),'uncoveredCurrentSelfContainedIds':sorted(current-set(reviews)),'staleNegativeReceiptIds':sorted(stale),'pendingManifestReclassificationIds':sorted(flags&current),'inProgressBatchFiles':[b['batchFile'] for b in batches if b['readStatus']!='adjudicated'],'coverageByLecture':coverage,'missingDependencyFindings':sorted(groups,key=lambda g:g['questionId']),'followUp':'All 56 missing-dependency classifications were adopted by the visual author by this snapshot. Asset pixels, prerequisite completeness, clipping and answer leakage remain separately owned by verify_required_question_visuals. No stale approvals were refreshed.'}
(OUT/'coverage-final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('coverageByLecture','missingDependencyFindings')},indent=2))
