"""Freeze explicitly assessed revision checks; expects prior review and fresh sealed response evidence."""
import pathlib,json,hashlib,datetime,sys,copy,re
R=pathlib.Path(__file__).resolve().parents[2];D=R/'audits/assignment-coverage';sys.path.insert(0,str(R/'scripts'));from validate import question_hash
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def freeze(week,version,flags,binding_path=None):
 prefix=f'{week}-v{version}';sealpath=D/f'{prefix}-independent-prekey-seal.json';seal=load(sealpath);assert sha(R/seal['packetPath'])==seal['packetSha256'];answers={x['questionId']:x for x in seal['answers']};old={x['questionId']:x for x in load(R/f'data/reviews/ASSIGN-{week}-v1-independent.json')};raw=load(R/f'data/question-batches/ASSIGN-{week}.json');qs=raw if isinstance(raw,list)else raw['questions'];qmap={q['id']:q for q in qs};binding=load(R/(binding_path or f'audits/assignment-coverage/ASSIGN-{week}-v{version}-minimal-bindings.json'));bindings=binding['questionHashes'];assert set(bindings)==set(answers);reveal=load(D/f'{prefix}-independent-reveal.json');now=datetime.datetime.now(datetime.timezone.utc).isoformat();reviews=[]
 preserved={qid:r['questionSha256']for qid,r in old.items()if r['decision']=='verified' and qid not in answers}
 for qid,h in preserved.items():assert question_hash(qmap[qid])==h
 collisions=[]
 targets={qid:re.sub(r'\W+','',qmap[qid]['stem'].casefold())for qid in answers}
 for p in (R/'data/question-batches').glob('*.json'):
  d=load(p);other=d if isinstance(d,list)else d.get('questions',[])
  for x in other:
   for qid,t in targets.items():
    if x.get('id')!=qid and re.sub(r'\W+','',x.get('stem','').casefold())==t:collisions.append([qid,x['id']])
 assert not collisions,collisions
 for qid,a in answers.items():
  q=qmap[qid];assert question_hash(q)==bindings[qid];assert set(a['independentAnswerOptionIds'])==set(q['correctOptionIds']);assert sha(R/q['originalRecordPath'])==q['originalRecordSha256'];r=copy.deepcopy(old[qid]);r.update(id=f'REV-{qid}-v{q["version"]}-independent-revision',questionVersion=q['version'],questionSha256=question_hash(q),reviewedAt=now,decision='flagged'if qid in flags else'verified',solvedBeforeAnswerSeen=False,priorExposure=seal['priorExposure'],independentAnswerOptionIds=a['independentAnswerOptionIds'],reviewType='targeted_nonblind_assignment_revision',reasoning=a['reasoning']+' Full current key, option explanations, source locators/kinds, difficulty and qualifications checked after the response seal. Prior source/key exposure disclosed. No computational execution is claimed for purely conceptual or locator repairs.',blindAnswerRecord=str(sealpath.relative_to(R)),blindAnswerRecordSha256=sha(sealpath),firstCurrentKeyOpenedAt=reveal['firstCurrentKeyOpenedAt'],checks={k:True for k in r['checks']},findings=[])
  for check,finding in flags.get(qid,[]):r['checks'][check]=False;r['findings'].append(finding)
  fresh={(e['sourceId'],e['physicalPage']):e for e in seal['sourceInspectionEvidence']};used={(c['sourceId'],c['physicalPage'])for c in q['citations']};assert used<=set(fresh)
  r['sourceInspectionEvidence']=[fresh[k]for k in sorted(used)];r['reusedPriorLectureEvidence']=dict(priorReviewId=old[qid]['id'],priorReviewPath=f'data/reviews/ASSIGN-{week}-v1-independent.json',priorReviewSha256=sha(R/f'data/reviews/ASSIGN-{week}-v1-independent.json'),scope='Unchanged lecture premise evidence retained from original independent review; not represented as a new pixel inspection.');r['reviewedSlideIds']=sorted({f'{s}-p{p:04d}'for s,p in used}|{s for s in old[qid]['reviewedSlideIds']if s.startswith('lectures-')});r.pop('independentCheckEvidence',None);assert r['reviewerId']not in [q['authorId']]+q.get('revisionAuthors',[]);reviews.append(r)
 import jsonschema
 for r in reviews:jsonschema.validate(r,load(R/'data/schema.review.json'))
 out=R/f'data/reviews/ASSIGN-{week}-v{version}-independent.json';assert not out.exists();out.write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n');accepted={r['questionId']:r['questionSha256']for r in reviews if r['decision']=='verified'}
 summary=dict(frozenAt=now,reviewPath=str(out.relative_to(R)),reviewSha256=sha(out),revisionCount=len(reviews),verifiedCount=len(accepted),flaggedCount=len(reviews)-len(accepted),keysMatching=len(reviews),preservedAcceptedHashes=preserved,acceptedRevisionHashes=accepted,currentAcceptedHashes={**preserved,**accepted},currentAcceptedCount=len(preserved)+len(accepted),flaggedQuestions=[dict(questionId=r['questionId'],questionSha256=r['questionSha256'],findings=r['findings'])for r in reviews if r['decision']=='flagged'],sourceKeyExposure=True,solvedBeforeAnswerSeen=False,originalSourceRecordsPreserved=True,exactNormalizedStemCollisions=collisions)
 (D/f'{prefix}-independent-review-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':
 freeze('W01',2,{'ASSIGN-W01-Q003':[('distractors','The stem no longer states the answer relation, but the question-visible assumptions still say the source definitions do not imply mutually exclusive categories. Only o1 allows overlapping categories; the same answer-elimination cue remains outside the stem. Keep the neutral deep-policy scenario and remove the overlap/non-exclusive conclusion from pre-answer assumptions; retain that conclusion in the solution.')]})
