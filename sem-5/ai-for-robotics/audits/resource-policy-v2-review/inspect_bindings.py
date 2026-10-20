import json,hashlib,pathlib,sys,datetime
R=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'));import validate
D=R/'audits/resource-policy-v2-review'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=load(R/'audits/blind-binding-learning-resources-policy-v2.json');p=load(R/'data/learning-resource-policy.json');actual=load(R/'data/learning-tools-course.json')['learningTools'];old=load(R/'audits/resource-history/v1-before-policy-repairs/data/learning-tools-course.json')['learningTools'];oldmap={r['id']:r for rs in old.values() for r in rs};records=[r for rs in actual.values() for r in rs];out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'priorExposure':'Prior v1 arithmetic, source pages and implementations were independently reviewed. This is a nonblind revision review, not a new blind answer claim.','packetSha256':sha(R/b['packetPath']),'policyHash':validate.canonical_json(p),'files':[],'payloads':[]}
assert out['packetSha256']==b['packetSha256'];out['policyHash']=hashlib.sha256(out['policyHash'].encode()).hexdigest();assert out['policyHash']==b['policy']['sha256']
for f in b['codeFiles']+b['additionalReviewFiles']:
 h=sha(R/f['path']);assert h==f['sha256'],f['path'];out['files'].append({'path':f['path'],'sha256':h,'unchangedSinceFreeze':True})
for r in records:
 bind=next(i for i in b['resourceBindings'] if i['id']==r['id']);assert validate.question_hash(r)==bind['sha256'];assert r['version']==2
 o=oldmap[r['id']];fields=[k for k in set(r)|set(o) if r.get(k)!=o.get(k)];assert set(fields)<=set(['version','implementationFiles','status','reviewIds']),(r['id'],fields)
 out['payloads'].append({'id':r['id'],'version':r['version'],'sha256':bind['sha256'],'changedFields':fields,'computationalPayloadExactlyPreserved':True})
(D/'binding-and-payload-checks.json').write_text(json.dumps(out,indent=2)+'\n');print('Exact files',len(out['files']),'payloads',len(out['payloads']),'policy',out['policyHash'])
