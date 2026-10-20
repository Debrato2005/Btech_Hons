"""Reviewer mutations of explicit synthetic author fixture, not course data."""
import datetime,hashlib,importlib.util,json,pathlib,sys
R=pathlib.Path(__file__).resolve().parents[2];D=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reviewer_fixture',R/'tests/test_assignment_reuse.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=[]
def rebind(t):
 h=m.validator.question_hash(t.target);t.target_review['questionSha256']=h;t.mapping['reusedQuestions'][0]['questionSha256']=h;t.review['mappingReviews'][0]['reusedQuestionHashes']={t.target['id']:h};t.write(t.batch_path,t.batch);t.review['mappingSha256']=t.sha(t.batch_path);t.save_review()
for name,mutate,expected in [
 ('valid control',lambda t:None,True),
 ('duplicate independent answer IDs',lambda t:t.target_review.update(independentAnswerOptionIds=t.target_review['independentAnswerOptionIds']*2),False),
 ('unsupported selectionMode',lambda t:t.target.update(selectionMode='unsupported'),False),
 ('missing selectionMode',lambda t:t.target.pop('selectionMode'),False),
 ('mapping reviewer is whitespace-padded author',lambda t:t.review.update(reviewerId=' '+t.batch['authorId']+' '),False),
 ('source role is not assignment_solutions',lambda t:t.bank['sources'][0].update(role='lectures'),False),
 ]:
 t=m.AssignmentReuseTests();t.setUp()
 try:
  mutate(t);rebind(t);r=t.build();allowed=bool(r['links']);out.append({'case':name,'expectedAllowed':expected,'actualAllowed':allowed,'passed':allowed==expected,'diagnostics':r['diagnostics']})
 finally:t.doCleanups()
a={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'pre-freeze authoring, not final acceptance','assemblerSha256':hashlib.sha256((R/'scripts/assemble_bank.py').read_bytes()).hexdigest(),'fixtureSha256':hashlib.sha256((R/'tests/test_assignment_reuse.py').read_bytes()).hexdigest(),'probes':out};p=D/'pre-freeze-reuse-probes.json';assert not p.exists();p.write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a,indent=2))
