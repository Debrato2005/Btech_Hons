from pathlib import Path
import json,hashlib,datetime,copy,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import question_hash,schema_errors,validate_bank
read=lambda p:json.loads((R/p).read_text());sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(p,x):
 f=R/p;assert not f.exists(),p;f.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
e=read('audits/blind-answers-W10-L50-residual-contracts.json');binding=read(e['bindingPath']);b=read('audits/review-snapshots/W10-L50-residual-contracts.json');qs={q['id']:q for q in b['questions']};old=read('audits/review-snapshots/W10-L50-v2-contracts.json');oldqs={q['id']:q for q in old['questions']};obs=read(e['sourceObservationsPath']);om={o['physicalPage']:o for o in obs['observations']};now=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert sha(e['packetPath'])==e['packetSha256'] and sha(e['bindingPath'])==e['bindingSha256']
assert len(binding['acceptedQuestionHashes'])==68
for k,h in binding['acceptedQuestionHashes'].items():assert question_hash(qs[k])==h and qs[k]==oldqs[k],k
current=read('data/question-batches/W10-L50.json');assert current==b
reviews=[];checkNames=['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication']
for a in e['answers']:
 q=qs[a['questionId']];assert q['version']==a['questionVersion'] and question_hash(q)==a['questionSha256'];assert e['reviewerId']not in[q['authorId'],*q.get('revisionAuthors',[])];assert q['correctOptionIds']==a['independentAnswerOptionIds']
 reviews.append({'id':q['id']+f'-v{q["version"]}-contracts-residual-closure','questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q),'reviewerId':e['reviewerId'],'decision':'verified','reviewedAt':now,'sourceVersions':{'lectures':binding['sourceVersion']},'reviewedSlideIds':sorted({c['slideId']for c in q['citations']}),'independentAnswerOptionIds':a['independentAnswerOptionIds'],'solvedBeforeAnswerSeen':False,'checks':dict.fromkeys(checkNames,True),'reasoning':a['reasoning']+' Current keyed solution, option rationales, figure/source locators, difficulty and nonduplication were then reviewed; all nine criteria pass.','findings':[],'blindAnswersPath':'audits/blind-answers-W10-L50-residual-contracts.json','blindAnswersSha256':sha('audits/blind-answers-W10-L50-residual-contracts.json'),'independentSolvedAt':e['frozenAt'],'priorAuthorExposure':a['priorAuthorExposure'],'currentVersionSolvedBeforeKeyedAccess':True,'sourceInspectionEvidence':[om[p]for p in sorted({c['physicalPage']for c in q['citations']})],'supplementalSourceEvidence':{'path':obs['notebookPath'],'sha256':obs['notebookSha256'],'cellsZeroBased':[9,19]},'computationsPath':e['computationsPath'],'computationsSha256':sha(e['computationsPath']),'runtimeQualification':'Only default installed Python, local source, unmodified deterministic definitions and inert plotting stub; no model, live inference, GUI or browser execution.'})
for r in reviews:assert not schema_errors(r,read('data/schema.review.json'))
prior=[]
for file in ['data/reviews/W10-L50-v1-independent-contracts.json','data/reviews/W10-L50-v2-independent-contracts.json']:
 for r in read(file):
  if r['decision']=='verified' and r['questionId']in binding['acceptedQuestionHashes'] and r['questionSha256']==binding['acceptedQuestionHashes'][r['questionId']]:prior.append(r)
assert len(prior)==68
allreviews=prior+reviews;rr={r['questionId']:r for r in allreviews};qq=copy.deepcopy(b['questions']);cs=copy.deepcopy(b['concepts'])
for q in qq:q['status']='verified';q['reviewIds']=[rr[q['id']]['id']]
for c in cs:c['status']='verified'
sm=read('sources/manifest.json');slides=[json.loads(l)for sid in ['lectures','assignments']for l in(R/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()];up={s['id']:s for s in read('data/inspection-batches/W10-L50.json')['slides']};slides=[copy.deepcopy(up.get(s['id'],s))for s in slides]
for s in slides:s['conceptIds']=[co['id']for co in cs if s['id']in co['slideIds']]
tmp={'schemaVersion':'1.0.0','bankVersion':'L50-residual-contracts-isolated','title':'L50 residual independent validation','complete':False,'sources':sm['sources'],'assets':sm['assets'],'slides':slides,'questions':qq,'concepts':cs,'reviews':allreviews,'learningTools':{k:[]for k in ['formulaSheet','confusionPairs','traps','algorithmVisualizations','numericalFamilies']}}
v=validate_bank(tmp,R,check_files=True);assert v['valid'],v
rp='data/reviews/W10-L50-residual-v3-independent-contracts.json';write(rp,reviews)
summary={'completedAt':now,'reviewerId':e['reviewerId'],'reviewed':3,'verified':3,'flagged':0,'keyDisagreements':0,'preservedAcceptedCount':68,'preservedAcceptedWholeObjects':True,'wholeLectureVerified':71,'wholeLectureQuestions':71,'reviewFile':rp,'reviewSha256':sha(rp),'packetPath':e['packetPath'],'packetSha256':e['packetSha256'],'blindAnswersSha256':sha('audits/blind-answers-W10-L50-residual-contracts.json'),'acceptedQuestionHashes':{**binding['acceptedQuestionHashes'],**{r['questionId']:r['questionSha256']for r in reviews}},'actualSourcePagesReinspected':sorted(om),'sourceNotebookSha256':obs['notebookSha256'],'boundedCoverageStatus':{'L50-G01':'Closed: integrated centered resultant with exact slide conflict and notebook cells9/19 locators.','L50-G02':'Previously closed: multi-turn state and memory behavior.','L50-G03':'Previously closed: full dense-head parameter counts.','L50-G04':'Closed: meaningful source-bounded dataset/supervision/alignment/domain-evaluation alternatives.'},'validation':v,'runtimeBoundary':'No browser or live inference. Deterministic source definitions and inert plotting stub only; prior exposure explicitly disclosed.','learningResources':'Separate policy remains flagged; L50 question approval does not approve formula extraction or tool activation.','next':'Await independently eligible repair packet or source-review assignment from lead. Do not duplicate lead L53/L52/L55 work.'};write('audits/W10-L50-residual-contracts-review-summary.json',summary)
handoff=f'''# L50 residual review closure

All three residual revisions pass all nine checks. The68 previously accepted whole objects and hashes are unchanged; L50 now has71/71 current independently verified questions, with all four bounded gaps closed. This does not certify overall course completion or the separate learning-resource policy.

Review: `{rp}`. SHA256 `{sha(rp)}`.
Packet: `{e['packetPath']}`. SHA256 `{e['packetSha256']}`.
Blind/current responses: `audits/blind-answers-W10-L50-residual-contracts.json`, SHA256 `{sha('audits/blind-answers-W10-L50-residual-contracts.json')}`. Prior keyed exposure is disclosed; these are independent revision reviews, not fresh-blind claims.
All nine cited source pages were reopened. Exact notebook cells9/19 were re-inspected and deterministic definitions executed with an inert plotting stub. No GUI, browser, model or live inference was run. Exact71-question accepted map and isolated clean validation: `audits/W10-L50-residual-contracts-review-summary.json`.

Learning resources: separate18-tool computational review is frozen, but its policy remains flagged and all tools inactive. Policy review SHA256 `4c1d62de9f870c080d710c5211c55cd819f974ac3d3aaaf276b76e254feec8d2`; tool review SHA256 `fd54941b9376b68b052c0742fce2d2006c84a9abdda4378fed5bce54a6ad5e8c`. See `docs/handoffs/learning-resources-contracts-review.md` and its exact finding packet.

Next: await an eligible repair/source-review assignment from lead. Do not duplicate lead L53/L52/L55 or whole-course reconciliation.

Restrictions: never use `/tmp/robotics-l35-venv` or the L48 incident temporary environment. All denied downloads stay stopped. No new dependency/model/checkpoint/audio/NLTK retrieval, denied original L49 notebook route, browser bypass or alternate restricted route. Actual browser QA remains blocked after the socket denial; do not retry/install/use another route. Default installed Python/Node, local source inspection and deterministic checks remain permitted. Historical outputs are not fresh executions. No Git, author or canonical bank edits. Do not self-review L13/L14/L04v2.
'''
(R/'docs/handoffs/L50-residual-contracts-review.md').write_text(handoff)
p=R/'docs/handoffs/learning-resources-contracts-review.md';t=p.read_text();t=t.replace('Next: review the three L50 residual v3 revisions from','L50 residual review is now closed: all three revisions verified, all68 earlier hashes preserved,71/71 current questions. Review SHA256 '+sha(rp)+'. Packet was');t=t.replace('Minimal bindings:', 'Minimal bindings:');t+='\nTool review SHA256: fd54941b9376b68b052c0742fce2d2006c84a9abdda4378fed5bce54a6ad5e8c. Policy review SHA256: 4c1d62de9f870c080d710c5211c55cd819f974ac3d3aaaf276b76e254feec8d2. Next: await eligible resource repair or source-review assignment.\n';p.write_text(t)
print(json.dumps({k:summary[k]for k in ['verified','flagged','wholeLectureVerified','reviewSha256']}))
