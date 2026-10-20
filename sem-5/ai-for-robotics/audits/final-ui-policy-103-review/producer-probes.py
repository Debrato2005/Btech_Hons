"""Independent producer probes. Synthetic fixture mutations never alter course data."""
import copy,datetime,hashlib,importlib.util,json,pathlib
R=pathlib.Path(__file__).resolve().parents[2];D=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('reviewer_fixture',R/'tests/test_assignment_reuse.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
results=[]
def rebind(t):
 t.write(t.original_path,t.original);t.mapping['originalRecordSha256']=t.sha(t.original_path)
 h=m.validator.question_hash(t.target);t.target_review['questionSha256']=h;t.mapping['reusedQuestions'][0]['questionSha256']=h
 t.mapping['duplicateQuestionSha256']=m.validator.question_hash(t.duplicate)
 t.review['mappingReviews'][0]['reusedQuestionHashes']={t.target['id']:h}
 t.write(t.batch_path,t.batch);t.review['mappingSha256']=t.sha(t.batch_path);t.save_review()
def malformed_hash(t):
 h='not-a-sha256';t.bank['sources'][0]['sha256']=h;t.bank['slides'][0]['sourceSha256']=h
 for q in (t.target,t.duplicate):
  for c in q['citations']:c['sourceSha256']=h
 t.target_review['sourceVersions']={t.original['sourceId']:h};t.original['sourceSha256']=h;t.mapping['sourceSha256']=h
def one_option(t):t.target['options']=[o for o in t.target['options'] if o['id'] in t.target['correctOptionIds']]
for name,mutate,expected in [
 ('unchanged control',lambda t:None,True),('source hash malformed but consistently rebound',malformed_hash,False),('one literal option but coherently reviewed',one_option,False),
 ('duplicate independent literal IDs',lambda t:t.target_review.update(independentAnswerOptionIds=t.target_review['independentAnswerOptionIds']*2),False),
 ('unsupported selection mode with new question hash',lambda t:t.target.update(selectionMode='unsupported'),False),
 ('padded reviewer self approval with current mapping/review bytes',lambda t:t.review.update(reviewerId=' '+t.batch['authorId']+' '),False),
 ('current mapping author declared as revision author',lambda t:t.batch.update(revisionAuthors=[t.review['reviewerId']]),False),
 ('removed concept duplicate edge',lambda t:t.bank['concepts'][-1].update(questionIds=[]),False),
 ('removed duplicate concept edge with new duplicate hash',lambda t:t.duplicate.update(conceptIds=[]),False),
 ('source role not assignments',lambda t:t.bank['sources'][0].update(role='lectures'),False),
 ('source physical page boolean',lambda t:t.bank['slides'][0].update(physicalPage=True),False),
 ]:
 t=m.AssignmentReuseTests();t.setUp()
 try:
  mutate(t);rebind(t);v=t.build();allowed=bool(v['links']);results.append({'case':name,'expectedAllowed':expected,'actualAllowed':allowed,'passed':allowed==expected,'diagnostics':v['diagnostics']})
 finally:t.doCleanups()
out={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'codeHashes':{p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in ('scripts/assemble_bank.py','scripts/validate.py')},'mode':'Independent reviewer mutations of explicit synthetic author fixture; no browser or canonical bank writes.','results':results,'passed':sum(x['passed'] for x in results),'failed':sum(not x['passed'] for x in results)}
(D/'producer-probes.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
