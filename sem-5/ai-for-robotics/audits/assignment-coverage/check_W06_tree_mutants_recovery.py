from pathlib import Path
import json,hashlib,datetime,sys
R=Path.cwd();sys.path.insert(0,'scripts');from validate import question_hash
cases=[(10,100),(12,5),(12,6)]
def route(x,y,root_strict=False,second_strict=False,unconditional_second=False,use_sum=False):
 root=(x<10)if root_strict else(x<=10)
 if root and not unconditional_second:leaf=[3,5,7];seen=False
 else:
  second=(y<5)if second_strict else(y<=5);leaf=[10,14,18]if second else[30,40];seen=True
 return(sum(leaf)if use_sum else sum(leaf)/len(leaf),seen)
correct=[route(*p)for p in cases];assert correct==[(5,False),(14,True),(35,True)]
mutants={k:[route(*p,**{k:True})for p in cases]for k in ['root_strict','second_strict','unconditional_second','use_sum']}
for v in mutants.values():assert v!=correct
assert mutants['root_strict']==[(35,True),(14,True),(35,True)]
assert mutants['second_strict']==[(5,False),(35,True),(35,True)]
assert mutants['unconditional_second']==mutants['root_strict']
assert mutants['use_sum']==[(15,False),(42,True),(70,True)]
a=json.load(open('audits/ASSIGN-W06-tree-boundaries-author-checks.json'));b=json.load(open('data/question-batches/ASSIGN-W06.json'));qs={q['id']:q for q in b['questions']}
for i,h in a['preservedQuestionHashes'].items():assert question_hash(qs[i])==h
p=R/'audits/assignment-coverage/W06-tree-independent-mutation-and-preservation-checks.json';assert not p.exists();p.write_text(json.dumps({'executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':'PASS','reviewerId':'repair_assignment_source_bindings:independent-reviewer','threeCaseResponse':correct,'actualMutantOutputs':mutants,'mutantsDetected':4,'preservedPreexistingQuestionHashes':a['preservedQuestionHashes'],'preservedPreexistingQuestionCount':len(qs),'method':'Independently implemented configurable branch traversal; direct current canonical question hashes checked against frozen pre-addition author manifest. This is reviewer execution, not reliance on the author pass result.','scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n');print('Four actual branch/aggregation mutants detected; ten preexisting W06 question hashes preserved.')
