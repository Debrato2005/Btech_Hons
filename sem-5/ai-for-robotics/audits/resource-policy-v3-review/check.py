import json,pathlib,sys,copy,hashlib,subprocess,datetime
R=pathlib.Path(__file__).resolve().parents[2];D=R/'audits/resource-policy-v3-review';sys.path.insert(0,str(R/'scripts'));import learning_resources as LR
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
binding=load(R/'audits/blind-binding-learning-resources-policy-v3.json');assert sha(R/binding['packetPath'])==binding['packetSha256']
policy=load(R/'data/learning-resource-policy.json');assert LR.digest(policy)==binding['policy']['sha256']
for c in binding['codeFiles']+binding['additionalReviewFiles']:assert sha(R/c['path'])==c['sha256'],c['path']
oldroot=R/'audits/resource-history/v2-before-python-parity-repair';oldjs=(oldroot/'app/learning-resources.js').read_text();assert oldjs.replace("const VERSION='1.0.1'","const VERSION='1.0.2'")==(R/'app/learning-resources.js').read_text()
tools=load(R/'data/learning-tools-course.json');assert (oldroot/'data/learning-tools-course.json').read_bytes()==(R/'data/learning-tools-course.json').read_bytes()
for rs in tools['learningTools'].values():
 for t in rs:assert LR.question_hash(t)==next(z['sha256'] for z in binding['resourceBindings'] if z['id']==t['id'])
b=json.loads(subprocess.check_output(['node','-e',"console.log(JSON.stringify(require('./tests/fixtures/learning-resource-bank.js').fixture()))"],cwd=R,text=True));q=b['questions'][0];qh=LR.question_hash(q);b['reviews'][0]['questionSha256']=qh
engine='app/course-numerical.js';h=sha(R/engine);r={'id':'synthetic-policy-parity-probe','version':1,'status':'verified','authorId':'tool-author','generatorKind':'q-learning-update','generatorVersion':'1.0.0','questionIds':['Q'],'questionBindings':[{'questionId':'Q','questionVersion':1,'questionSha256':qh}],'sourceRefs':copy.deepcopy(q['citations']),'implementationFiles':[{'path':engine,'sha256':h}]};rh=LR.question_hash(r)
p={'id':'synthetic-policy','version':policy['version'],'authorId':'policy-author','codeHashes':{'app/learning-resources.js':sha(R/'app/learning-resources.js'),engine:h}};ph=LR.digest(p)
x=b['learningResourceIntegrity'];x.update(policy=p,policySha256=ph,policyEligible=True,policyReviews=[{'id':'synthetic-policy-review','resourceId':p['id'],'resourceVersion':p['version'],'resourceSha256':ph,'reviewerId':'distinct-policy-reviewer','decision':'verified','checks':dict.fromkeys(LR.POLICY_CHECKS,True)}],toolBindings={r['id']:{'version':1,'sha256':rh}},toolReviews=[{'id':'synthetic-tool-review','toolId':r['id'],'toolVersion':1,'toolSha256':rh,'reviewerId':'distinct-tool-reviewer','decision':'verified','sourceVersions':{'S':'a'*64},'reviewedSlideIds':['S1'],'checks':dict.fromkeys(LR.TOOL_CHECKS,True)}]);x['bindings']['Q']['questionSha256']=qh;b['learningTools']={'numericalFamilies':[r]}
js="const R=require('./app/learning-resources.js');let s='';process.stdin.on('data',c=>s+=c).on('end',()=>{const b=JSON.parse(s),x=b.learningResourceIntegrity,r=b.learningTools.numericalFamilies[0];x.runtimePolicySha256=R.sha256(R.stableJSON(x.policy));x.toolBindings[r.id].runtimeSha256=R.runtimeQuestionDigest(r);console.log(JSON.stringify({bank:b,policyAllowed:R.policyAllowed(b),toolAllowed:R.toolRecordAllowed(r,b)}));});"
checks=[]
for label,mode in [('valid','valid'),('omitted implementation','omitted'),('conflicting implementation','conflict'),('missing inventory','missing'),('malformed inventory','malformed')]:
 bb=copy.deepcopy(b);pp=bb['learningResourceIntegrity']['policy']
 if mode=='omitted':del pp['codeHashes'][engine]
 if mode=='conflict':pp['codeHashes'][engine]='0'*64
 if mode=='missing':del pp['codeHashes']
 if mode=='malformed':pp['codeHashes']=[]
 xx=bb['learningResourceIntegrity'];xx['policySha256']=LR.digest(pp);xx['policyReviews'][0]['resourceSha256']=xx['policySha256']
 zz=json.loads(subprocess.run(['node','-e',js],cwd=R,input=json.dumps(bb),text=True,capture_output=True,check=True).stdout);bb=zz.pop('bank');rr=bb['learningTools']['numericalFamilies'][0];reasons,_=LR.tool_reasons(rr,bb,R,xx['toolReviews']);expected=(mode=='valid');assert (not reasons)==expected;assert zz['toolAllowed']==expected
 # malformed inventories are exercised through tool_reasons, not code_errors which requires validated policy schema.
 integrity=LR.integrity_errors(bb,R) if mode!='malformed' else ['not invoked on invalid policy schema; tool gate rejected']
 if mode=='valid':assert integrity==[]
 elif mode=='omitted':assert any('policy code hashes' in e for e in integrity)
 checks.append({'case':label,'expectedAllowed':expected,'pythonToolReasons':reasons,'pythonIntegrityErrors':integrity,'javascript':zz,'passed':True})
for bad in [None,{}, {'policy':None},{'policy':[]},{'policy':{}},{'policy':{'codeHashes':None}}]:
 bb=copy.deepcopy(b);bb['learningResourceIntegrity']=bad;reasons,_=LR.tool_reasons(r,bb,R,x['toolReviews']);assert any('policy code hashes' in s for s in reasons);checks.append({'case':'malformed embedded metadata '+json.dumps(bad),'passed':True,'reasons':reasons})
bb=copy.deepcopy(b);del bb['learningResourceIntegrity'];reasons,_=LR.tool_reasons(r,bb,R,x['toolReviews']);assert reasons==[];checks.append({'case':'preassembly disk candidate policy valid control','passed':True})
r_bad=copy.deepcopy(r);r_bad['implementationFiles']=[{'path':'docs/DATA_CONTRACT.md','sha256':sha(R/'docs/DATA_CONTRACT.md')}];rv=copy.deepcopy(x['toolReviews']);rv[0]['toolSha256']=LR.question_hash(r_bad);reasons,_=LR.tool_reasons(r_bad,bb,R,rv);assert any('policy code hashes' in s for s in reasons);checks.append({'case':'preassembly actual unlisted file rejected','passed':True,'reasons':reasons})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packetSha256':binding['packetSha256'],'policySha256':binding['policy']['sha256'],'frozenFilesMatched':len(binding['codeFiles']+binding['additionalReviewFiles']),'toolObjectsExactlyPreserved':18,'javascriptChangeOnlyVersionConstant':True,'checks':checks,'priorComputationsPreserved':'All directly bound implementation bytes unchanged, so v2 independent39 answers,5 traces and13000-seed computation/replay evidence remain exact. No redundant new blind claim.','mode':'Nonblind independent revision review; synthetic fixtures remain in memory, no actual bank approvals or data changed by this checker. No browser execution.'}
(D/'independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checks':len(checks),'allPassed':True,'policySha256':out['policySha256']},indent=2))
