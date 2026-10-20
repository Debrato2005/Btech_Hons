import json,pathlib,sys,copy,subprocess,hashlib,datetime
R=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'));import learning_resources as LR
out=[]
def make():
 b=json.loads(subprocess.check_output(['node','-e',"console.log(JSON.stringify(require('./tests/fixtures/learning-resource-bank.js').fixture()))"],cwd=R,text=True));q=b['questions'][0]
 r={'id':'synthetic-review-probe','version':1,'status':'verified','authorId':'tool-author','generatorKind':'q-learning-update','generatorVersion':'1.0.0','questionIds':[q['id']],'sourceRefs':copy.deepcopy(q['citations']),'implementationFiles':[{'path':'app/course-numerical.js','sha256':hashlib.sha256((R/'app/course-numerical.js').read_bytes()).hexdigest()}]}
 rv={'id':'synthetic-in-memory-review','toolId':r['id'],'toolVersion':1,'reviewerId':'other-tool-reviewer','decision':'verified','sourceVersions':{'S':'a'*64},'reviewedSlideIds':['S1'],'checks':dict.fromkeys(LR.TOOL_CHECKS,True)}
 refresh(b,r,rv);return b,r,rv
def refresh(b,r,rv):
 q=b['questions'][0];h=LR.question_hash(q);b['reviews'][0]['questionSha256']=h;r['questionBindings']=[{'questionId':q['id'],'questionVersion':q['version'],'questionSha256':h}];rv['toolSha256']=LR.question_hash(r)
def check(name,mutate,expectedReject=True):
 b,r,rv=make();mutate(b,r,rv);refresh(b,r,rv);reasons,_=LR.tool_reasons(r,b,R,[rv]);out.append({'name':name,'expectedReject':expectedReject,'actualRejected':bool(reasons),'passed':bool(reasons)==expectedReject,'reasons':reasons})
check('valid baseline',lambda b,r,v:None,False)
for key,ans in [([],[]),(['missing'],['missing']),(['o1','o1'],['o1']),(['o1'],['o1','o1'])]:check('literal '+str((key,ans)),lambda b,r,v:(b['questions'][0].update(correctOptionIds=key),b['reviews'][0].update(independentAnswerOptionIds=ans)))
for who in [' ',None,4,' author ']:check('question reviewer '+str(who),lambda b,r,v:b['reviews'][0].update(reviewerId=who))
check('revision author whitespace',lambda b,r,v:b['questions'][0].update(revisionAuthors=[' reviewer ']))
check('conditional intended not literal',lambda b,r,v:b['reviews'][0].update(independentAnswerOptionIds=[],conditionalIntendedOptionIds=['o1']))
for page in [0,-1,1.5,True,None,'1',4]:check('page '+str(page),lambda b,r,v:(b['questions'][0]['citations'][0].update(physicalPage=page),b['slides'][0].update(physicalPage=page)))
for status in ['mystery','unreviewed','unresolved','']:check('disposition '+status,lambda b,r,v:b['slides'][0].update(disposition=status))
for count in [0,True,1.5,None,'3']:check('pageCount '+str(count),lambda b,r,v:b['sources'][0].update(pageCount=count))
# This is a real on-disk, hash-matching implementation, omitted from the policy's code inventory.
check('implementation omitted from approved policy',lambda b,r,v:b['learningResourceIntegrity']['policy'].update(codeHashes={}),True)
check('implementation conflicts with approved policy',lambda b,r,v:b['learningResourceIntegrity']['policy'].update(codeHashes={'app/course-numerical.js':'0'*64}),True)
D=R/'audits/resource-policy-v2-review';(D/'python-mutation-checks.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'Synthetic fixtures in memory; no approvals persisted. Default Python/Node only.','checks':out},indent=2)+'\n');print(json.dumps({'checks':len(out),'failed':[x for x in out if not x['passed']]},indent=2))
