"""One bounded figure/branch-coverage addition; preserve all accepted W06 objects."""
import assignment_second_half_common as common
common.AUTHOR='finish_assignment_authoring:W06-tree-boundary-author'
from assignment_second_half_common import *
from validate import validate_bank,question_hash
import sys
from fractions import Fraction as R
B='ASSIGN-W06-tree-boundaries';path=f'data/question-batches/{B}.json';assert not(ROOT/path).exists()
bank=json.loads((ROOT/'data/bank.json').read_text());bq={q['id']:q for q in bank['questions']};oldbatch=json.loads((ROOT/'data/question-batches/ASSIGN-W06.json').read_text());before={q['id']:qhash(q)for q in oldbatch['questions']};orig='audits/assignment-originals/ASSIGN-W06-Q08.json';originalsha=sha(orig)
q=Q(6,11,8,'Regression-tree equality and early termination','Use the source tree: if x₁≤10, stop at leaf [3,5,7]; otherwise test x₂≤5, whose true leaf is [10,14,18] and false leaf is [30,40]. Each leaf predicts its unweighted target mean. Evaluate samples A=(10,100), B=(12,5) and C=(12,6), in that order. Which option gives both the predictions (A,B,C) and whether the x₂ test is reached for each sample?', ['Predictions (5,14,35); x₂ test reached (no,yes,yes).','Predictions (35,14,35); x₂ test reached (yes,yes,yes).','Predictions (5,35,35); x₂ test reached (no,yes,yes).','Predictions (15,42,70); x₂ test reached (no,yes,yes).'],['A satisfies root equality and stops at the first leaf; B reaches and satisfies the second equality; C reaches the second false branch. The leaf means are 5,14,35.','This sends A past the root despite 10≤10, whether by changing ≤ to < or by testing x₂ unconditionally.','This sends B to the second false branch despite 5≤5.','The branch decisions are correct, but the predictions use leaf sums instead of means.'],[C(26,'Week 6 item 8, complete regression-tree figure in the lower half of the page','Root x1≤10: true→[3,5,7]; false→test x2≤5, true→[10,14,18], false→[30,40].','figure'),C(27,'Week 6 item 8 continuation, worked route and leaf-mean rule at the top of the page','The source follows reached tests in order and predicts the mean of target values in the selected leaf.','derivation')],'A tree follows only the branch actually reached. Equality belongs to the true side of each displayed ≤ test, and prediction uses the selected leaf’s mean rather than its sum.',assumptions=['The tree is transcribed from the printed figure; evaluate each sample independently; features and targets are dimensionless toy quantities; no missing-value or pruning rule is introduced.'],steps=['A: 10≤10 is true, so stop at [3,5,7]; the x₂ test is not reached, regardless of A’s second coordinate. Prediction=(3+5+7)/3=5.','B: 12≤10 is false, then 5≤5 is true; prediction=(10+14+18)/3=14.','C: 12≤10 is false, then 6≤5 is false; prediction=(30+40)/2=35.','Assemble predictions (5,14,35) and reached-test flags (no,yes,yes).'],formulas=[F('ŷ_leaf=(1/n)Σᵢyᵢ',{'ŷ_leaf':('prediction of the selected leaf','dimensionless target units'),'n':('number of training targets in that leaf','count'),'yᵢ':('training target in the selected leaf','dimensionless target units'),'i':('within-leaf target index','count')},['Unweighted squared-error regression leaf; use only values in the reached leaf.'])],qtype='diagram',difficulty='medium',angles=['root_equality','root_true_short_circuit','second_test_equality','rightmost_branch','all_leaf_means'])
q['cognitiveSkill']='application';q['originalRecordSha256']=originalsha;q['relatedQuestionIds']=['ASSIGN-W06-Q008'];q['difficultyRationale']='Trace three distinct branches/boundaries, track which tests are reached and average the correct leaf targets; not a numerical rescaling of the existing interior-path example.'
concept=copy.deepcopy(next(c for c in bank['concepts']if c['id']=='ASSIGN-W06-C008'));concept['questionIds']=sorted(set(concept['questionIds'])|{q['id']});concept['examinationAngles']=sorted(set(concept.get('examinationAngles',[]))|set(q['testedAssignmentAngles']));concept['coverageNotes']='One additional boundary/branch item closes the independently identified tree gap. Existing interior-path question and all accepted content are unchanged; the new item is pending independent review.'
checks=[]
def ck(n,v):assert v,n;checks.append(n)
leaves=[[3,5,7],[10,14,18],[30,40]];means=[R(sum(z),len(z))for z in leaves]
def run(x1,x2):
 trace=['x1≤10']
 if x1<=10:return means[0],False,trace
 trace.append('x2≤5')
 return (means[1]if x2<=5 else means[2]),True,trace
ck('all leaf means exact',means==[5,14,35])
answers=[run(*v)for v in [(10,100),(12,5),(12,6)]];ck('three predictions and reachability',[(a,b)for a,b,_ in answers]==[(5,False),(14,True),(35,True)])
ck('source original interior example unchanged',run(12,3)[:2]==(14,True))
ck('root strictness mutation detected',(35,True)!=run(10,100)[:2])
ck('second strictness mutation detected',(35,True)!=run(12,5)[:2])
ck('leaf sum mutation detected',[sum(z)for z in leaves]==[15,42,70] and [sum(z)for z in leaves]!=means)
count=0
for x1 in range(-20,31):
 for x2 in range(-20,31):
  pred,reached,trace=run(x1,x2)
  assert reached==(x1>10);count+=1
  assert len(trace)==(1 if x1<=10 else 2);count+=1
  expected=5 if x1<=10 else 14 if x2<=5 else 35
  assert pred==expected;count+=1
  if x1<=10:assert all(run(x1,alt)[0]==5 and not run(x1,alt)[1]for alt in [-1000,5,1000]);count+=1
ck('all preexisting batch object hashes preserved',{z['id']:qhash(z)for z in json.loads((ROOT/'data/question-batches/ASSIGN-W06.json').read_text())['questions']}==before)
ck('immutable source record preserved',sha(orig)==originalsha)
ck('new stable ID absent from bank',q['id']not in bq)
ck('canonical hash function agrees',qhash(q)==question_hash(q))
baseline=validate_bank(copy.deepcopy(bank),ROOT,check_files=False);bank['questions'].append(copy.deepcopy(q));bank['concepts']=[c for c in bank['concepts']if c['id']!=concept['id']]+[copy.deepcopy(concept)]
rep=validate_bank(bank,ROOT,check_files=False);allowed={'Learning extractor activation does not match independent approval/code hashes.','Extractor code hash mismatch: app/app.js'};assert set(rep['errors'])<=set(baseline['errors'])<=allowed,rep['errors'];rep['questionDeltaValid']=not(set(rep['errors'])-set(baseline['errors']));rep['baselineErrors']=baseline['errors']
dump(path,{'schemaVersion':'1.0.0','batchId':B,'authorId':AUTHOR,'questions':[q],'concepts':[concept],'coverageNote':'One distinct multi-case branch/boundary task adds missing root equality, reached-second equality and rightmost leaf averaging without repeating the existing interior-route example.'})
dump(f'audits/{B}-author-checks.json',{'role':'Author stdlib-only checks, not independent review','checkedAt':NOW(),'pythonExecutable':sys.executable,'checks':checks,'gridCases':51*51,'variedAssertions':count,'questionHashes':{q['id']:qhash(q)},'preservedQuestionHashes':before,'originalRecordSha256':originalsha})
dump(f'audits/{B}-preflight.json',rep)
pp=f'audits/blind-{B}.json';z={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','cognitiveSkill','week','lectureId','topic','subtopic','assumptions','options')};z['citations']=[{k:copy.deepcopy(v)for k,v in c.items()if k!='evidenceText'}for c in q['citations']]
dump(pp,{'batchId':B,'instructions':'Solve the added branch/boundary question using the actual diagram and continuation before revealing the generated author key. Original printed source keys are visible; disclose source-key exposure. Challenge whether all identified missing diagram angles are tested without cosmetic duplication.','questions':[z]});dump(f'audits/blind-binding-{B}.json',{'packetSha256':sha(pp),'questions':[{'id':q['id'],'version':q['version'],'sha256':qhash(q)}]})
views=[(26,'3','Actual lower-page diagram inspected: root x1≤10 true leaf [3,5,7]; false branch reaches x2≤5, true leaf [10,14,18], false [30,40]. All arrows, True/False labels and target lists checked.'),(27,'4','Actual item8 continuation inspected: original sample (12,3), two reached decisions and unweighted mean rule; printed answer visible. New question uses equalities and rightmost leaf absent from original sample.')]
dump(f'audits/assignment-coverage/{B}-source-view-log.json',{'authorId':AUTHOR,'viewedAt':NOW(),'sourceAnswerExposure':True,'fullyBlind':False,'pages':[{'physicalPage':p,'printedFooter':footer,'previewSha256':sha(f'sources/previews/assignments/page-{p:04}.webp'),'observations':note}for p,footer,note in views]})
dump(f'audits/{B}-freeze.json',{'frozenAt':NOW(),'packet':pp,'packetSha256':sha(pp),'binding':f'audits/blind-binding-{B}.json','newQuestionCount':1,'questionHashes':{q['id']:qhash(q)},'preservedQuestionHashes':before,'originalRecordsUnchanged':True,'globalPolicyPending':not rep['valid'],'globalValidationErrors':rep['errors'],'questionDeltaValid':rep['questionDeltaValid'],'independentReviewComplete':False})
print('FROZEN',B,sha(pp),len(checks),'check groups',count,'varied assertions')
