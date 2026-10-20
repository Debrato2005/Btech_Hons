"""Reviewer-owned narrow exact-hash policy check; does not modify policy or bank."""
import copy,datetime,hashlib,json,pathlib,subprocess,sys
R=pathlib.Path(__file__).resolve().parents[2];D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'scripts'));import learning_resources as LR
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
policy=load(R/'data/learning-resource-policy.json');assert policy['version']=='1.0.3','Await coordinator-authored new policy, do not reuse old review.'
oldreviews=load(R/'data/learning-resource-policy-reviews.json');prior=next(r for r in oldreviews if r['resourceVersion']=='1.0.2' and r['decision']=='verified');checks=[]
def add(name,detail):checks.append({'name':name,'passed':True,'detail':detail})
assert set(policy['codeHashes'])==set(prior['codeHashes']);assert LR.code_errors(policy,R)==[]
changed=[n for n in policy['codeHashes'] if policy['codeHashes'][n]!=prior['codeHashes'][n]];assert set(changed)=={'app/app.js','app/learning-resources.js'};assert sha(R/'app/app.js')==load(D/'ui-delta-review.json')['codeHashes']['app/app.js']
add('complete current code inventory exact',{'codeFiles':len(policy['codeHashes']),'changedPaths':changed})
source=(R/'app/learning-resources.js').read_text();assert source.count("const VERSION='1.0.3';")==1
reverted=source.replace("const VERSION='1.0.3';","const VERSION='1.0.2';");assert hashlib.sha256(reverted.encode()).hexdigest()==prior['codeHashes']['app/learning-resources.js'];add('projection delta only version constant','Strict version gate preserved; no predicate or projection logic was changed.')
binding=load(R/'audits/blind-binding-learning-resources-policy-v3.json');records={x['id']:x for rows in load(R/'data/learning-tools-course.json')['learningTools'].values()for x in rows};assert len(binding['resourceBindings'])==18
for b in binding['resourceBindings']:assert LR.question_hash(records[b['id']])==b['sha256']
add('all 18 directly approved tool objects unchanged','Prior computation approvals retained without inventing new blind-answer reviews.')
assert not LR.policy_approval(policy,[r for r in oldreviews if r['resourceVersion']!='1.0.3']);add('old policy approvals cannot activate new policy','Python current exact version/content gate rejects all old reviews.')
r={'id':'synthetic-policy-review-probe-only','resourceId':policy['id'],'resourceVersion':policy['version'],'resourceSha256':LR.digest(policy),'reviewerId':'independent-test-fixture-not-real-approval','decision':'verified','checks':dict.fromkeys(LR.POLICY_CHECKS,True)}
assert LR.policy_approval(policy,[r]);add('distinct full exact-hash review is accepted in memory','Synthetic control only; no approval or bank was written by this checker.')
for who in [policy['authorId'],' ',*policy.get('revisionAuthors',[])]:
 bad={**r,'reviewerId':who};assert not LR.policy_approval(policy,[bad])
add('author/revision-author/blank identity rejected','Independent reviewer identity remains required.')
for check in LR.POLICY_CHECKS:
 bad=copy.deepcopy(r);bad['checks'][check]=False;assert not LR.policy_approval(policy,[bad])
assert not LR.policy_approval(policy,[r,{**r,'decision':'flagged'}]);add('failed check and exact-hash dispute reject','All mandatory policy checks and current dispute blocking preserved.')
bad=copy.deepcopy(policy);bad['codeHashes']['app/app.js']='f'*64;assert any('app/app.js' in e for e in LR.code_errors(bad,R));add('on-disk implementation mutation rejected','Changing only a policy hash does not approve altered code.')
program="""const R=require('./app/learning-resources.js');let s='';process.stdin.on('data',c=>s+=c).on('end',()=>{const p=JSON.parse(s),x={policy:p.policy,policySha256:p.sha,policyEligible:true,runtimePolicySha256:R.sha256(R.stableJSON(p.policy)),policyReviews:[p.review]},b={learningResourceIntegrity:x};const valid=R.policyAllowed(b);x.policyReviews=p.old;const oldRejected=!R.policyAllowed(b);x.policyReviews=[p.review];x.policy.version='1.0.2';x.runtimePolicySha256=R.sha256(R.stableJSON(x.policy));const versionRejected=!R.policyAllowed(b);console.log(JSON.stringify({version:R.VERSION,valid,oldRejected,versionRejected}));});"""
z=json.loads(subprocess.run(['node','-e',program],cwd=R,input=json.dumps({'policy':policy,'sha':LR.digest(policy),'review':r,'old':[x for x in oldreviews if x['resourceVersion']!='1.0.3']}),text=True,capture_output=True,check=True).stdout);assert z=={'version':'1.0.3','valid':True,'oldRejected':True,'versionRejected':True};add('JavaScript candidate and stale-version gate parity',z)
out={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'policyPath':'data/learning-resource-policy.json','policyFileSha256':sha(R/'data/learning-resource-policy.json'),'policyCanonicalSha256':LR.digest(policy),'policyVersion':policy['version'],'priorPolicyReviewId':prior['id'],'codeHashes':policy['codeHashes'],'checks':checks,'passed':len(checks),'failed':0,'browserQA':False,'boundary':'Narrow nonblind version/application integration review, preserving unchanged exact projection and math evidence; no actual browser run.'};(D/'policy-candidate-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
