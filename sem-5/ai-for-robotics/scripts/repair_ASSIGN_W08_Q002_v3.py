"""Remove one definition cue; preserve all nine accepted W08 objects."""
from assignment_second_half_common import *
from validate import validate_bank
B='ASSIGN-W08';p=f'data/question-batches/{B}.json';mp=f'audits/assignment-coverage/{B}-v3-repair-manifest.json';assert not(ROOT/mp).exists()
old=json.loads((ROOT/p).read_text());b=copy.deepcopy(old);qq={q['id']:q for q in b['questions']};summary=json.loads((ROOT/'audits/assignment-coverage/ASSIGN-W08-v2-recovery-independent-review-summary.json').read_text());accepted=summary['currentAcceptedHashes'];assert len(accepted)==9
history=ROOT/'data/history/ASSIGN-W08';assert not(history/'v2.json').exists();(history/'v2.json').write_bytes((ROOT/p).read_bytes())
for src,dst in [('audits/blind-ASSIGN-W08-v2.json','blind-v2.json'),('audits/blind-binding-ASSIGN-W08-v2.json','blind-binding-v2.json')]:assert not(history/dst).exists();(history/dst).write_bytes((ROOT/src).read_bytes())
q=qq[B+'-Q002'];before=copy.deepcopy(q);q.update(version=3,status='draft',reviewIds=[],revisionAuthors=list(dict.fromkeys(q.get('revisionAuthors',[])+['finish_assignment_authoring:W08-Q002-v3-repair'])))
q['stem']='A* uses priority f(n)=g(n)+h(n), where g(n) is accumulated path cost from the start. What does h(n) represent, and what priority results if h(n)=0 for every node, using the same frontier and tie rules?'
for qid,hsh in accepted.items():assert qq[qid]==next(z for z in old['questions']if z['id']==qid) and qhash(qq[qid])==hsh
check=copy.deepcopy(q)
for field in ['version','stem','revisionAuthors']:check[field]=before[field]
assert check==before,'Unexpected extra edit'
for z in b['questions']:assert sha(z['originalRecordPath'])==z['originalRecordSha256']
bank=json.loads((ROOT/'data/bank.json').read_text());base=validate_bank(copy.deepcopy(bank),ROOT,check_files=False);ids=set(qq);oldbank={q['id']:q for q in bank['questions']}
bank['questions']=[z for z in bank['questions']if z['id']not in ids]+[copy.deepcopy(oldbank[z['id']])if z['id']in accepted and z['id']in oldbank and qhash(oldbank[z['id']])==qhash(z)else copy.deepcopy(z)for z in b['questions']]
ci={c['id']for c in b['concepts']};bank['concepts']=[c for c in bank['concepts']if c['id']not in ci]+copy.deepcopy(b['concepts'])
v=validate_bank(bank,ROOT,check_files=False);allowed={'Learning extractor activation does not match independent approval/code hashes.','Extractor code hash mismatch: app/app.js'};assert set(v['errors'])<=set(base['errors'])<=allowed,v['errors'];v['questionDeltaValid']=not(set(v['errors'])-set(base['errors']));v['baselineErrors']=base['errors'];dump('audits/assignment-coverage/ASSIGN-W08-v3-author-validation.json',v)
dump(p,b)
z={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','cognitiveSkill','week','lectureId','topic','subtopic','assumptions','options')};z['citations']=[{k:copy.deepcopy(v)for k,v in c.items()if k!='evidenceText'}for c in q['citations']]
pp='audits/blind-ASSIGN-W08-v3.json';dump(pp,{'batchId':B,'instructions':'One stem-only revision. Inspect exact actual-source regions and assess the tested distinction before keyed reveal. The independent reviewer saw earlier-version keys; disclose that exposure.','questions':[z]})
dump('audits/blind-binding-ASSIGN-W08-v3.json',{'packetSha256':sha(pp),'questions':[{'id':q['id'],'version':q['version'],'sha256':qhash(q)}]})
dump(mp,{'batchId':B,'revisionAuthorId':'finish_assignment_authoring:W08-Q002-v3-repair','frozenAt':NOW(),'packet':pp,'packetSha256':sha(pp),'questionHashes':{q['id']:qhash(q)},'acceptedQuestionHashes':accepted,'acceptedPreserved':9,'onlyStemAndVersionMetadataChanged':True,'optionsKeysCitationsSolutionsUnchanged':True,'originalRecordsUnchanged':True,'questionDeltaValid':v['questionDeltaValid'],'globalPolicyPending':not v['valid'],'globalValidationErrors':v['errors'],'independentReviewComplete':False})
dump('audits/ASSIGN-W08-v3-author-checks.json',{'role':'Narrow author preservation checks, not independent review','checkedAt':NOW(),'checks':['Exactly one stem plus version/revision metadata changed.','All nine accepted object values and hashes preserved.','All immutable source hashes preserved.','Options, keys, exact source locators and solutions unchanged.','No additional in-memory validation errors beyond allowed current app-policy baseline.'],'questionHashes':{q['id']:qhash(q)},'newNumericalComputationClaimed':False})
print('FROZEN',pp,sha(pp))
