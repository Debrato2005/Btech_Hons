"""Versioned L41 author repairs. Never an independent review; reruns are rejected."""
from pathlib import Path
import copy, datetime, hashlib, json, math, sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from validate import question_hash, schema_errors
from authoring_helpers import formula
AUTHOR='build_offline_study_interface:L41-v2-reviser'
SHA='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=R/'data/question-batches/W09-L41.json';before=json.loads(p.read_text());b=copy.deepcopy(before)
qs={int(q['id'][-3:]):q for q in b['questions']}
reviews=json.loads((R/'data/reviews/W09-L41-v1-independent.json').read_text())
changed=sorted(int(r['questionId'][-3:]) for r in reviews if r['decision']=='flagged')
accepted={r['questionId']:r['questionSha256'] for r in reviews if r['decision']=='verified'}
assert len(changed)==26 and len(accepted)==49
assert all(qs[n]['version']==1 for n in changed),'Do not rerun a frozen revision.'
archive=R/'audits/batch-history/W09-L41-pre-v2.json'
archive.parent.mkdir(exist_ok=True)
if archive.exists():
 assert archive.read_bytes()==p.read_bytes(),'History differs from live batch; refuse replay.'
else:archive.write_text(p.read_text())
source_issues=R/'audits/W09-L41-source-issues.json';source_issues_hash=hashlib.sha256(source_issues.read_bytes()).hexdigest()
assert len(json.loads(source_issues.read_text())['issues'])==24

def opt(n,i,text,why):
 q=qs[n];next(o for o in q['options'] if o['id']==f'o{i}')['text']=text;q['solution']['optionExplanations'][f'o{i}']=why

def replace(n,options,explanations,stem=None,why=None):
 q=qs[n]
 if stem:q['stem']=stem
 for i,(text,e) in enumerate(zip(options,explanations),1):opt(n,i,text,e)
 if why:q['solution']['justification']=q['solution']['simpleExplanation']=why

def locate(n,mapping):
 for c in qs[n]['citations']:
  p=c['physicalPage'];desc,kind,role=mapping[p]
  c.update(locator=f'Lecture L41, physical PDF page {p}, printed footer {p-1262}: {desc}',kind=kind,role=role)

opt(1,4,'Yes; its improvement in cost compensates for the mandatory load violation.','A mandatory constraint is not a soft penalty that can be traded against a lower cost.')
replace(2,[
 'Decision variable: m; fixed parameter: L; objective: E(L); functional constraint: σ(L) ≤ σ_max.',
 'Decision variable: L; fixed parameter: m; objective: σ(L); functional constraint: a bound on E(L).',
 'Decision variable: m; fixed parameter: L; objective: σ(L); functional constraint: a bound on E(L).',
 'Decision variable: L; fixed parameter: m; objective: E(L); functional constraint: σ(L) ≤ σ_max.'
],[
 'The scenario varies length and fixes payload, not the reverse; the objective and constraint roles here are otherwise correct.',
 'This swaps the stated energy objective with the stress constraint.',
 'This reverses both the variable/parameter pair and the objective/constraint pair.',
 'These four roles follow exactly what may change, what stays fixed, what is minimized, and what must be satisfied.'
])
for c in qs[2]['citations']:c['role']='premise'
replace(6,[
 'Objective linear, constraint linear: a linear problem.',
 'Objective nonlinear, constraint linear: a nonlinear problem.',
 'Objective nonlinear, constraint nonlinear: a nonlinear problem.',
 'Objective linear, constraint nonlinear: a nonlinear problem.'
],[
 'The x² term makes the constraint nonlinear, although the objective is linear.',
 'The objective 3x + 2y has only first powers; the nonlinear term is instead in the constraint.',
 'Only the constraint contains a nonlinear term.',
 'The x² constraint term prevents classification as a linear problem.'
])
opt(7,2,'It has functional constraints, but no bound constraints, because the interval restricts x.','The lecture distinguishes simple variable bounds from performance-related functional constraints; this interval is a bound.')
replace(9,[
 'Use objective values without derivatives; independent candidate evaluations may be distributed when the implementation and resources support it.',
 'Estimate derivatives at every candidate; independent candidate evaluations may be distributed when the implementation and resources support it.',
 'Use objective values without derivatives; each candidate evaluation must wait for the preceding candidate’s fitness even within one population.',
 'Estimate derivatives at every candidate; each candidate evaluation must wait for the preceding candidate’s fitness even within one population.'
],[
 'The described GA uses evaluated quality rather than required gradients, and independent population evaluations provide a qualified parallelization opportunity.',
 'Parallel evaluation is possible, but derivative estimation is not a requirement of the described GA.',
 'Derivative-free evaluation fits, but the declared independent evaluations need not be serialized within the population.',
 'Neither compulsory derivatives nor compulsory within-population serialization follows from the described method.'
],stem='An objective can be evaluated despite jumps, and candidate fitness evaluations within a population are independent. Which qualified pair of motivations supports using the described GA?',why='Derivative-free fitness selection can handle the stated lack of derivatives. Independent population evaluations can be distributed by a suitable implementation, but parallel speedup depends on resources and overhead; the source’s broad comparison is not a claim that every other optimizer is serial.')
qs[9]['assumptions']=['Added scenario: the objective is evaluable at all tested candidates and their fitness evaluations are independent. No guaranteed speedup or global convergence is assumed.']
locate(9,{1268:('Discontinuity and Search Robustness bullets in Traditional versus Evolutionary Search.','statement','premise'),1270:('Definition of a population-based probabilistic iterative search.','statement','premise')})
qs[9]['conflictResolution']={'status':'explicit-qualification-awaiting-independent-review','sourceId':'lectures','sourceSha256':SHA,'physicalPages':[1268],'sourceClaim':'The Search Robustness bullet broadly states that most traditional methods are not suitable for parallel computing or many problem types.','basis':qs[9]['solution']['justification'],'method':'Use the explicitly independent evaluation scenario and implementation-dependent parallelization; do not infer a universal comparison or speedup guarantee.'}
primary={'accessedAt':now,'source':'MathWorks R2026b documentation','url':'https://www.mathworks.com/help/gads/parallel-population-solvers.html','locator':'Enabling Parallel Computing and Limitations','paraphrase':'Population solvers can distribute objective and constraint evaluations. For ga, parallel evaluation must be enabled and vectorized evaluation disabled. Occasional serial evaluations and parallel overhead remain relevant.','role':'Supplementary qualification of the lecture motivation, not additional course coverage.'}
pe=R/'audits/W09-L41-v2-primary-evidence.json';pe.write_text(json.dumps(primary,ensure_ascii=False,indent=2)+'\n')
qs[9].setdefault('primaryEvidence',[]).append({'url':primary['url'],'accessedAt':now,'locator':primary['locator'],'savedEvidencePath':str(pe.relative_to(R)),'savedEvidenceSha256':hashlib.sha256(pe.read_bytes()).hexdigest(),'relationToLecture':primary['role']})
opt(17,4,'11.','This shifts the entire binary value right by one place, dropping the trailing zero: 10110 becomes 1011 = 11. Reducing only the leftmost weight from 16 to 8 would instead give 14.')
opt(18,3,'D = 0 maps to x_min; D = 2^l − 1 maps to x_max − (x_max − x_min)/2^l.','This upper endpoint would result from incorrectly dividing by 2^l instead of the stated 2^l − 1.')
replace(20,[
 'The numerical difference is 1 and the Hamming distance is 1.',
 'The numerical difference is 1 and the Hamming distance is 5.',
 'The numerical difference is 5 and the Hamming distance is 1.',
 'The numerical difference is 16 and the Hamming distance is 5.'
],[
 'Decoded adjacency is being mistaken for one-bit adjacency; all five positions differ.',
 'The decoded values are 15 and 16, while every bit position changes.',
 'This interchanges the numerical difference with the count of changed positions.',
 'Sixteen is the new decoded value, not its difference from fifteen.'
])
replace(21,[
 'The reachable listed values are 1, 3, and 7; a one-bit change need not be a numerical unit step.',
 'The reachable listed values are 1, 2, and 4; a one-bit change follows ordinary binary place weights.',
 'The reachable listed values are 1, 2, and 3; one-bit neighbors are the three closest integers.',
 'The only reachable listed value is 1; every one-bit change must reach the next integer.'
],[
 'Each of 001, 010, and 100 differs from 000 at one position, yet the given decoded values are not all adjacent to zero.',
 'This applies ordinary binary place weights instead of the supplied reflected Gray mapping.',
 'Hamming neighborhoods do not in general coincide with the numerically nearest integers.',
 'The adjacency property does not exclude the other one-bit neighbors 010 and 100.'
],stem='For an added three-bit reflected Gray-code lookup, 000, 001, 010, and 100 decode to 0, 1, 3, and 7 respectively. Starting at 000, which decoded values can be reached by flipping exactly one bit, and what does this show?',why='The one-bit adjacency of consecutive Gray values is not a converse guarantee for every possible bit flip. The provided lookup supplies a concrete counterexample.')
qs[21]['assumptions']=['The lookup is an explicitly added reflected Gray-code example; use the supplied mapping rather than unsigned binary decoding.']
for c in qs[21]['citations']:c['role']='premise'
qs[21]['difficulty']='easy';qs[21]['solution']['steps']=['Flip each of the three positions in 000 to obtain 100, 010, and 001.','Read their provided decoded values: 7, 3, and 1.']
replace(22,[
 'Mutation → selection of parents → crossover.',
 'Crossover → selection of parents → mutation.',
 'Selection of parents → mutation → crossover.',
 'Selection of parents → crossover → mutation.'
],[
 'The source places parent selection before variation and mutation after crossover.',
 'The selected mating pool is formed before crossover.',
 'The source places mutation after crossover, not before it.',
 'This is the displayed order after fitness evaluation.'
])
replace(26,[
 'The signed fitness total is zero, so the normalization denominator vanishes.',
 'The probabilities sum to 4, so a further division by population size is needed.',
 'The third candidate’s probability exceeds 1 because its score is greater than 1.',
 'The first candidate receives a negative probability because its score is negative.'
],[
 'The actual signed total is −1 + 2 + 3 = 4, not zero.',
 'The normalized values sum to 1, not the unnormalized total 4; no population-size division fixes a negative entry.',
 'The third probability is 3/4, so it does not exceed 1; raw scores need not lie in the unit interval.',
 'The first probability is −1/4, which violates nonnegativity even though the three values sum to 1.'
])
replace(28,[
 'Ranks stay unchanged, but probabilities change because transformed raw magnitudes become the weights.',
 'Ranks and their selection probabilities stay unchanged because the ordering is preserved.',
 'Ranks stay unchanged, but probabilities change according to the new gaps between adjacent fitnesses.',
 'Ranks stay unchanged, but probabilities change according to the transformed population variance.'
],[
 'That describes a switch to raw-magnitude weighting, not the stated rank-based rule.',
 'With the same rank-to-probability rule, preserving distinct-value order preserves its inputs and outputs.',
 'The stated rank rule does not weight adjacent raw-fitness gaps.',
 'The stated rank rule does not normalize by raw-fitness variance.'
])
opt(31,2,'1 pair.','This is the expected number that do not cross, 5 × (1 − 0.8), rather than the expected number that cross.')
locate(40,{1273:('Affine endpoint-inclusive decoding equation for binary coding.','equation','premise'),1280:('Example bounds [1, 16], fitness √x, and six-bit string length.','statement','premise'),1281:('Highlighted 100101 positional expansion and mapped x/fitness calculation.','equation','premise')})
qs[41]['difficulty']='easy';qs[41]['difficultyRationale']='Direct summation of six supplied numbers followed by one probability normalization.'
locate(44,{1279:('Mutation bullet defining the random per-bit flip test.','statement','premise'),1280:('GA parameters: population size 6, six bits per individual, and mutation probability 0.03.','statement','premise'),1283:('Step 4 mutation paragraph below the three crossover pairs, interpreting 36 × 0.03.','statement','conflict')})
qs[44]['conflictResolution'].update(sourceId='lectures',sourceSha256=SHA,physicalPages=[1283])
replace(49,[
 'A: excessive exploitation, risking premature convergence; B: excessive exploration, risking slow convergence.',
 'A: excessive exploration, risking slow convergence; B: excessive exploitation, risking premature convergence.',
 'A: excessive exploitation, risking premature convergence; B: excessive exploitation, risking premature convergence.',
 'A: excessive exploration, risking slow convergence; B: excessive exploration, risking slow convergence.'
],[
 'Strong reinforcement of similar candidates can lose diversity, while repeatedly seeking new regions without refinement can make progress slow.',
 'This reverses the two described search behaviors.',
 'The diagnosis of A fits, but B prioritizes new regions rather than refinement of the current best.',
 'The diagnosis of B fits, but A reinforces similar current candidates rather than broad exploration.'
],stem='Run A strongly selects the current best and becomes nearly uniform. Run B continually samples new regions but does little refinement of promising solutions. Which pair of tendencies matches the source’s exploration/exploitation comparison?',why='The two extremes have different risks: overexploitation can cause premature convergence and loss of diversity, while excessive exploration can cause stagnation or slow convergence. These are tendencies, not guarantees for every run.')
qs[49]['difficulty']='easy';qs[49]['difficultyRationale']='Direct classification of two explicitly described search behaviors.'
qs[49]['assumptions']=['Added contrasting runs; interpret the source comparison as tendencies rather than deterministic convergence guarantees.']
locate(49,{1285:('Two-column comparison, including both “too much” warnings and refinement versus new-region aims.','figure','premise')})
replace(52,[
 'All three are feasible because the linear operator automatically clips its extrapolated children to [1, 7].',
 'The bounds must still be checked: 0 and 8 violate [1, 7] despite both parents being feasible.',
 'Only the midpoint needs checking; feasible interpolation establishes feasibility of both extrapolated children.',
 'The three children are feasible collectively because their average 4 lies within [1, 7].'
],[
 'No clipping operation was specified; the generated values are explicitly 0 and 8.',
 'Each child must satisfy the interval independently, and extrapolation can leave it.',
 'Convex interpolation and extrapolation have different bound-preservation properties.',
 'Feasibility is required for each candidate, not merely for the average of the children.'
])
qs[61]['stem']='Let P1 = P2 = 5. Explicitly use the corrected multiplicative child formula C_± = (P1 + P2 ± α|P2 − P1|)/2 with finite α, rather than reading the raised distance in the slide as an exponent. What follows for the separation ratio and child values?'
qs[61]['assumptions']=['Equal scalar parents, finite nonnegative sampled spread, and the explicitly corrected multiplicative formula; no bound clipping is needed.']
why='The source’s spread ratio is undefined at coincident parents. Under the explicitly corrected multiplicative child formula, zero parent separation gives both children equal to 5. This is a separate limiting branch, not a value assigned to 0/0.'
qs[61]['solution']['justification']=qs[61]['solution']['simpleExplanation']=why
qs[61]['solution']['steps']=['|P2 − P1| = 0.','For finite α, α|P2 − P1| = 0, so each corrected child is (5 + 5)/2 = 5.','The child-to-parent separation ratio is therefore 0/0 and is undefined.']
qs[61]['solution']['formulas']=[formula('C_± = (P1 + P2 ± α|P2 − P1|)/2; ratio = |C_+ − C_−|/|P2 − P1|',{'P1, P2':'scalar parent design values','C_−, C_+':'lower and upper child values under the corrected multiplicative formula','α':'finite nonnegative sampled spread parameter','ratio':'observed child-to-parent separation ratio, defined only for distinct parents'},{'P1, P2, C_−, C_+':'common design-variable units','α, ratio':'dimensionless'},['The ratio is undefined for equal parents; evaluate children using the separate finite-spread limiting formula.'])]
qs[61]['conflictResolution']=copy.deepcopy(qs[59]['conflictResolution']);qs[61]['conflictResolution']['basis']=why
locate(61,{1287:('Separation-ratio denominator and bottom child formula with visually superscripted parent distance.','equation','conflict')})
replace(67,[
 '10 c versus 100 c; count both a parent and a child evaluation for every member in this generation.',
 '4 c versus 49 c; omit one elite member from evaluation in each population.',
 '5 c versus 50 c; total cost to a target quality also depends on generations, restarts, and achieved quality.',
 '5 c versus 50 c; the smaller population must therefore reach the same target quality ten times sooner.'
],[
 'This doubles the declared one-evaluation-per-member workload by inserting an extra parent/child evaluation.',
 'The premise evaluates every member once; it does not exempt an elite or reuse its cached score.',
 'Multiplying the equal cost c by population size gives the per-generation values, but not the full optimization budget.',
 'This assumes identical progress and generation requirements without evidence.'
])
opt(68,1,'Mutation probability p_m → crossover probability p_c → population size N → generation limit G_max.','This interchanges the first two stages of the displayed schedule.')
locate(69,{1290:('Four-row one-parameter-at-a-time stage table and nine intervals per parameter.','table','premise'),1291:('Ten candidate values, 10 + 10 + 10 + 10 evaluation slots, and 10000 Cartesian combinations.','statement','premise')})
replace(70,[
 '40 distinct tuples; 40 objective evaluations without caching, and 40 with caching.',
 '37 distinct tuples; 37 objective evaluations without caching, and 37 with caching.',
 '40 distinct tuples; 40 objective evaluations without caching, and 37 with caching.',
 '37 distinct tuples; 40 objective evaluations without caching, and 37 with caching.'
],[
 'Three slots revisit earlier tuples and do not add new distinct points.',
 'Without caching, all 40 scheduled slots are evaluated, including the three repeats.',
 'Caching reduces repeated evaluation work, but the same three repeats also reduce the distinct-tuple count.',
 'There are 40 − 3 = 37 distinct tuples; an uncached run evaluates 40 slots, while a perfect cache evaluates each distinct tuple once.'
],stem='Consider an added deterministic parameter study with 40 scheduled evaluation slots. Exactly three slots repeat an already tested parameter tuple; all other slots are new. How many distinct tuples and objective evaluations occur without caching versus with a perfect result cache?',why='Evaluation slots, distinct parameter tuples, and actual objective calls are different counts. In this declared example there are 37 distinct tuples, 40 uncached calls, and 37 perfectly cached calls.')
qs[70]['assumptions']=['Added count example: exactly three repeated slots, no other duplicates, deterministic objective, and a cache keyed by the complete parameter tuple.']
qs[70]['type']='numerical';qs[70]['cognitiveSkill']='numerical';qs[70]['difficulty']='easy'
qs[70]['solution']['steps']=['Distinct tuples = 40 − 3 = 37.','An uncached study executes every slot: 40 calls.','A perfect cache executes once per distinct tuple: 37 calls.']
qs[70]['solution']['formulas']=[formula('U = S − D; C_uncached = S; C_cached = U',{'U':'number of distinct tuples','S':'number of scheduled evaluation slots','D':'number of slots repeating an earlier tuple','C_uncached':'objective-call count without caching','C_cached':'objective-call count with a perfect cache'},{'U, S, D, C_uncached, C_cached':'dimensionless counts'},['Deterministic objective; perfect full-tuple cache; every slot is either new or a repeat.'])]
qs[71]['difficulty']='easy';qs[71]['difficultyRationale']='Two direct comparisons in a supplied four-entry score table.'
opt(74,3,'Fixed coefficient → static; scheduled growth → adaptive; feasibility-feedback adjustment → dynamic.','The fixed coefficient is correctly called static, but scheduled change is dynamic and feedback-based adjustment is adaptive.')
opt(75,4,'Minimize route length and test only each segment’s midpoint as a substitute for checking the complete segment.','A clear midpoint does not exclude an obstacle elsewhere on the continuous segment; sampled-point clearance alone is not a general collision certificate.')

# A narrow new source-specific terminology item closes the remaining gap without changing an accepted object.
q=copy.deepcopy(qs[14]);q.update(id='W09-L41-Q076',version=1,status='draft',authorId=AUTHOR,stem='In the lecture’s 1990s–2000s history row, what does VIGA stand for?',selectionMode='single',type='definition',difficulty='easy',cognitiveSkill='recall',subtopic='VIGA terminology',tags=['viga-expansion'],conceptIds=['W09-L41-C-viga-expansion'],assumptions=['Recall the exact lecture terminology; no unprinted VIGA implementation is inferred.'],correctOptionIds=['o2'],reviewIds=[],difficultyRationale='Direct recall of a source-specific acronym expansion.')
for k in ('conflictResolution','primaryEvidence','revisionAuthors'):q.pop(k,None)
q['options']=[{'id':'o1','text':'Visualized Incremental Genetic Algorithms.'},{'id':'o2','text':'Visualized Interactive Genetic Algorithms.'},{'id':'o3','text':'Variable-length Interactive Genetic Algorithms.'},{'id':'o4','text':'Visualized Island Genetic Algorithms.'}]
q['citations']=[{'slideId':'lectures-p1271','sourceId':'lectures','sourceSha256':SHA,'physicalPage':1271,'kind':'table','locator':'Lecture L41, physical PDF page 1271, printed footer 9: 1990s–2000s row in History and Evolution of GA.','evidenceText':'1990s–2000s: Visualized Interactive Genetic Algorithms (VIGA).','role':'explicit','region':None}]
q['solution']={'justification':'The named history row expands VIGA as Visualized Interactive Genetic Algorithms.','optionExplanations':{'o1':'The printed word is Interactive, not Incremental.','o2':'This reproduces the exact expansion in the source row.','o3':'The printed first word is Visualized, not Variable-length.','o4':'The printed word is Interactive, not Island.'},'steps':[],'formulas':[],'simpleExplanation':'VIGA is the source’s abbreviation for Visualized Interactive Genetic Algorithms.','memoryAid':None,'misconceptions':[],'examTraps':[],'prerequisiteConceptIds':[]}
b['questions'].append(q);qs[76]=q
b['concepts'].append({'id':'W09-L41-C-viga-expansion','title':'VIGA terminology','description':q['solution']['justification'],'slideIds':['lectures-p1271'],'questionIds':[q['id']],'status':'drafted','topic':q['topic'],'subtopic':'VIGA terminology','prerequisiteConceptIds':[],'examinationAngles':['definition']})
for n in changed:
 q=qs[n];q['version']=2;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append(AUTHOR)
for n in changed+[76]:
 q=qs[n];q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']]
 # Keep concept descriptions in sync for the substantively extended angles.
 if n in (9,21,49,70):
  for c in b['concepts']:
   if c['id'] in q['conceptIds']:c['description']=q['solution']['justification'];c['examinationAngles']=list(dict.fromkeys(c['examinationAngles']+[q['type']]))
for q in b['questions']:
 if q['id'] in accepted:
  assert question_hash(q)==accepted[q['id']],q['id']
  assert q==next(o for o in before['questions'] if o['id']==q['id'])
assert hashlib.sha256(source_issues.read_bytes()).hexdigest()==source_issues_hash
assert all(qs[n]['correctOptionIds']==before['questions'][n-1]['correctOptionIds'] for n in changed)
assert all(len({o['text'] for o in q['options']})==4 for q in b['questions'])
# New or changed numeric examples checked as author evidence, not independent review.
checks={'binary_rationale':int('10110',2)==22 and (int('10110',2)>>1)==11 and 8+4+2==14,'gray_lookup':all((n^(n>>1))==g for n,g in [(0,0),(1,1),(3,2),(7,4)]),'cache_counts':40-3==37,'equal_parent_sbx':all((10-a*0)/2==5 and (10+a*0)/2==5 for a in [0,0.1,1,2,100]),'endpoint_bad_denominator':math.isclose(1+15*63/64,16-15/64),'accepted_hashes':len(accepted)==49,'old_keys_unchanged':True,'all_24_source_qualifications_preserved':True}
assert all(checks.values())
schema=json.loads((R/'data/schema.question.json').read_text())
errors={q['id']:schema_errors(q,schema) for q in b['questions'] if schema_errors(q,schema)}
assert not errors,errors
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for n in changed+[76]:
 q=qs[n];x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
pf=R/'audits/blind-W09-L41-v2-and-gap.json';pf.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
manifest={'frozenAt':now,'author':AUTHOR,'independentVerification':False,'packet':str(pf.relative_to(R)),'packetSha256':hashlib.sha256(pf.read_bytes()).hexdigest(),'revisedCount':26,'newGapCount':1,'totalCount':76,'questionHashes':{qs[n]['id']:question_hash(qs[n]) for n in changed+[76]},'preservedAcceptedQuestionHashes':accepted,'originalBatchHistory':str(archive.relative_to(R)),'sourceQualificationsPreserved':{'count':24,'path':str(source_issues.relative_to(R)),'sha256':source_issues_hash},'gapDispositions':{'qualified_parallel_computing':'Q009 v2, with independent-evaluation assumption and primary implementation documentation.','excessive_exploration':'Q049 v2, both extremes compared explicitly.','VIGA_expansion':'New Q076 v1, exact source terminology only.'},'sourceReinspection':{'at':now,'pages':[1268,1271,1285,1287],'method':'Actual 1800×1013 rendered pages viewed; original full-page inspection remains in the batch records.'},'authorChecks':checks,'notes':['No accepted object was modified.','All original 26 repaired keys were preserved; each revised version remains draft.','Q061 now announces and binds the multiplicative SBX correction locally.','All changed option explanations and misconception lists were synchronized.','Original primary-evidence file and all source qualifications remain byte-identical.']}
(R/'audits/W09-L41-v2-repair-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'packetSha256':manifest['packetSha256'],'revised':26,'new':1,'acceptedPreserved':49,'authorChecks':checks}))
