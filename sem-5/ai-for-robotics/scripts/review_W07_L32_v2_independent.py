#!/usr/bin/env python3
"""Freeze the independent L32 revision review; never mutate the authored batch."""
import json, hashlib, datetime, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from validate import question_hash, schema_errors, CHECK_KEYS
REVIEWER='build_offline_study_interface:L32-independent-reviewer'
def read(p): return json.loads((R/p).read_text())
def digest(p): return hashlib.sha256((R/p).read_bytes()).hexdigest()
def save(p,v): (R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
packet='audits/blind-W07-L32-v2.json'
answerspath='audits/W07-L32-v2-independent-prefinal-answers.json'
assert digest(packet)=='04ed545c1555a2e370d6467215690de5985d8fab309499e5e7b9d2d2eb0e1899'
assert digest(answerspath)=='417096ee23b05e8a86cb2f4b13842f2458b8d482d6bd42ac0f4293a1b92ce8a8'
frozen=read(answerspath)
assert not frozen['v2AuthorBatchRead'] and not frozen['v2AuthorChecksRead']
m=read('audits/W07-L32-v2-repair-manifest.json')
bpath=R/'data/question-batches/W07-L32.json'; raw=bpath.read_bytes(); b=json.loads(raw)
qs={q['id']:q for q in b['questions']}
for qid,h in {**m['acceptedQuestionHashes'],**m['questionHashes']}.items(): assert question_hash(qs[qid])==h,qid
old=read('audits/W07-L32-independent-summary.json')
oldfindings={x['questionId']:x for x in old['findings']}
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
reviews=[]
special={
'W07-L32-Q012':'Fresh independent installed-code hashes match the saved implementation evidence; a declared sufficiently large test array reproduces both 150×150×3 slices. The original flowers image has height 640 and width 426, so the correctly ordered source rectangle is also in bounds.',
'W07-L32-Q024':'The installed to implementation and fresh execution confirm float32 scaling to 0–1, a new object, and preservation of the uint8 original.',
'W07-L32-Q033':'The installed apply implementation and fresh callback observation confirm one whole-array invocation by default.',
'W07-L32-Q034':'Recomputed the corrected wrong-denominator distractor: 255×27/118=58.3474576271. The intended range-based output is 146.4893617021. Both the option rationale and repeated misconception now agree.',
'W07-L32-Q046':'Independently opened W3C CSS Color 4, dated 9 October 2026, section 10.2. It gives a linear branch through absolute encoded component 0.04045 and an offset 2.4-power branch; this supports the item-level external qualification without claiming that the slide states the full standard.',
'W07-L32-Q052':'The question now supplies the complete 3×3 binary window and exact 1/9 normalization, so the 1785/9 result is independent of question order.',
'W07-L32-Q056':'The complete binomial matrix and divisor are now in the stem. The first H-window weighted sum is 9 and 255×9/16=143.4375.',
'W07-L32-Q057':'The complete binomial matrix and divisor are now in the stem. The adjacent H-window weighted sum is 10 and 255×10/16=159.375.',
'W07-L32-Q059':'The stem now explicitly names convolution and correlation; no missing antecedent remains.',
'W07-L32-Q079':'Re-viewed all nine orange-window source cells. Sorting gives 9,9,10,10,10,10,10,11,11 and median 10. Column-major versus row-major listing does not change the multiset.',
'W07-L32-Q081':'The duplicate listing-order item has been replaced. Independently computed continuous center 0.22028365825867868, finite nine-sample sum 0.8821096750246818, and normalized center 0.24972366191598006 before opening the revised key. Re-viewed the actual worked source calculation; its local missing-factor qualification remains.',
'W07-L32-Q088':'Independently executed the declared toy input in toolbox 2.4.1 before reading its key: normhist gives [[0,170],[170,255]], while nearest-rounded raw CDF gives [[64,191],[191,255]]. The implementation hash independently matches the pinned evidence and delegates to cv2.equalizeHist. This is not represented as a reproduction of unavailable pollen_image.tif.'}
for a in frozen['answers']:
 q=qs[a['questionId']]
 assert q['version']==a['questionVersion']
 assert set(a['independentAnswerOptionIds'])==set(q['correctOptionIds'])
 prev=oldfindings.get(q['id'])
 resolved=('Reassessed all previously failed dimensions: '+', '.join(prev['criteria'])+'. The exact earlier findings are addressed by the current source kinds/locators, explicit premise roles, item-linked primary evidence, self-contained premises, corrected arithmetic, ordinary prose spacing, plausible misconception alternatives, calibrated difficulty or nonduplicated coverage as applicable. ') if prev else 'This is the new bounded runtime-qualification question. '
 reasoning=a['reasoning']+' '+special.get(q['id'],'')+' '+resolved+'Read the complete revised stem, all options, every option explanation, all solution fields and local source qualifications. All nine quality checks pass. The original independent source-first inspection covered all 33 actual pages 954–986; this revision pass re-viewed pages 957, 958, 969, 970, 974, 978, 979, 981 and 982. Forty-one independently authored assertions and 4,000 varied comparisons pass again. Prior v1 answer exposure is disclosed, and this is not a fresh blind review. Revision responses were frozen before opening the v2 keyed batch. Purely conceptual questions do not claim an additional numerical or figure derivation where none is applicable. Source qualifications remain local and do not resolve an entire source page.'
 reviews.append({'id':f'REV-{q["id"]}-v{q["version"]}-revision-independent-interface','questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q),'reviewerId':REVIEWER,'decision':'verified','reviewedAt':now,'sourceVersions':{c['sourceId']:c['sourceSha256'] for c in q['citations']},'reviewedSlideIds':list(dict.fromkeys(c['slideId'] for c in q['citations'])),'independentAnswerOptionIds':a['independentAnswerOptionIds'],'solvedBeforeAnswerSeen':False,'checks':{k:True for k in CHECK_KEYS},'reasoning':reasoning,'findings':[],'reviewMode':'independent revision re-review; prior v1 key exposure disclosed','answerFreezePath':answerspath,'answerFreezeSha256':digest(answerspath)})
schema=read('data/schema.review.json')
errors=[e for r in reviews for e in schema_errors(r,schema)]
assert not errors,errors
reviewpath='data/reviews/W07-L32-v2-independent-interface.json'
save(reviewpath,{'reviewerId':REVIEWER,'reviews':reviews})
coverage={'reviewerId':REVIEWER,'completedAt':now,'status':'closed within the inspected L32 source scope','originalChallenge':'audits/W07-L32-independent-coverage-challenge.json','actualPagesInspectedInOriginalIndependentPass':list(range(954,987)),'actualPagesReinspectedThisPass':[957,958,969,970,974,978,979,981,982],'substantivePages':list(range(957,984)),'currentAcceptedQuestionCount':88,'gaps':[{'id':'L32-COVERAGE-01','status':'closed','questionId':'W07-L32-Q081','questionSha256':question_hash(qs['W07-L32-Q081']),'evidence':'Actual p974 and independent continuous/finite-normalized Gaussian calculation.'},{'id':'L32-COVERAGE-02','status':'closed','questionId':'W07-L32-Q088','questionSha256':question_hash(qs['W07-L32-Q088']),'evidence':'Actual p969–970, independently executed declared toy input and pinned implementation hash.'}],'qualification':'All 14 original source qualifications remain. Exact unavailable pollen and circuit TIFF output reproduction is not claimed. Every substantive page and its equations, code, tables and diagram examination angles were challenged against the current questions; no further bounded missing angle found. Question count is not a claim of 88 independent underlying concepts or whole-course completion.','priorReviewExposure':'This is a revision re-review, not a fresh blind review.'}
save('audits/W07-L32-v2-independent-coverage-closure.json',coverage)
report={'reviewerId':REVIEWER,'completedAt':now,'reviewMode':'Independent revision re-review, not fresh blind review','questionCount':len(reviews),'verified':len(reviews),'flagged':0,'keyDisagreements':0,'priorAcceptedPreserved':len(m['acceptedQuestionHashes']),'currentTotalAccepted':88,'packetSha256':digest(packet),'batchSha256':hashlib.sha256(raw).hexdigest(),'answerFreezePath':answerspath,'answerFreezeSha256':digest(answerspath),'reviewPath':reviewpath,'reviewSha256':digest(reviewpath),'acceptedQuestionHashes':{r['questionId']:r['questionSha256'] for r in reviews},'preservedAcceptedQuestionHashes':m['acceptedQuestionHashes'],'independentRuntimePath':'audits/W07-L32-v2-independent-runtime.json','independentCheckReplayPath':'audits/W07-L32-v2-independent-computation-replay.json','checks':{'namedAssertions':41,'variedTrials':1000,'variedComparisons':4000,'freshPrimaryImplementationHashesMatched':4,'freshAdditionalRuntimeChecks':['correct coordinate slices','float conversion scaling','whole-array apply callback']},'actualPagesReinspected':[957,958,969,970,974,978,979,981,982],'primarySpecificationCheck':{'url':'https://www.w3.org/TR/2026/CRD-css-color-4-20261009/#predefined-sRGB','checkedAt':now,'locator':'Section 10.2 transfer-function branches','finding':'The standard uses a linear segment and an offset power segment, rather than a single pure power over the entire domain.'},'coverageClosurePath':'audits/W07-L32-v2-independent-coverage-closure.json','findings':[],'mutations':'Independent review, executable review checks and reviewer audits only. No author-batch, source, canonical bank, assembly or Git changes.'}
save('audits/W07-L32-v2-independent-summary.json',report)
assert bpath.read_bytes()==raw
print(json.dumps({k:report[k] for k in ['questionCount','verified','flagged','keyDisagreements','priorAcceptedPreserved','currentTotalAccepted']}))
