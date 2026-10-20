"""Independent exact frozen policy, baseline and content checks. No data writes."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,difflib
R=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;B=Path('/workspace/shared/robotics-verification-logs/policy-103-producer-baseline')
sha=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('reviewer_validator104',R/'scripts/validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
read=lambda p:json.loads((R/p).read_text());p=read('data/learning-resource-policy.json');m=read('audits/final-ui-policy-104-author/candidate-manifest.json');ledger=read('data/learning-resource-policy-reviews.json');old=next(r for r in ledger if r['id']=='recovery-independent-learning-resource-policy-v1.0.3');checks=[]
def ck(name,ok,detail=None):
 checks.append({'name':name,'passed':bool(ok),'details':detail});assert ok,name
ck('exact policy1.0.4 and final author manifest',p['version']=='1.0.4' and sha(v.canonical_json(p).encode())==m['policySha256'] and sha((R/'data/learning-resource-policy.json').read_bytes())==m['policyFileSha256'])
ck('all 13 bound implementation files exact',len(p['codeHashes'])==13 and p['codeHashes']==m['codeHashes'] and all(sha((R/f).read_bytes())==h for f,h in p['codeHashes'].items()),p['codeHashes'])
ck('previous independent policy ledger untouched',sha((R/'data/learning-resource-policy-reviews.json').read_bytes())=='f88448a5f1e260ad93b1144003dccf95b64ec2d7df2dc4fe753857ed1f1cf645')
changed={f for f,h in p['codeHashes'].items() if old['codeHashes'].get(f)!=h}
ck('only declared six changed and two added files',changed=={'app/app.js','app/core.js','app/learning-resources.js','scripts/build.py','scripts/assemble_bank.py','scripts/validate.py','scripts/question_visuals.py','data/schema.bank.json'},sorted(changed))
for f in ['app/app.js','app/core.js','app/learning-resources.js']:
 name=f.replace('/','-')+'.before-104';ck('reviewer baseline exact: '+f,sha((D/name).read_bytes())==old['codeHashes'][f])
for f in ['scripts/assemble_bank.py','scripts/validate.py','scripts/build.py']:
 ck('recovered producer baseline exact: '+f,sha((B/f).read_bytes())==old['codeHashes'][f])
 (D/(Path(f).name+'.patch')).write_text(''.join(difflib.unified_diff((B/f).read_text().splitlines(True),(R/f).read_text().splitlines(True),fromfile='approved-1.0.3/'+f,tofile='candidate-1.0.4/'+f)))
s=(R/'app/learning-resources.js').read_text();a=s.index('const VISUAL_CHECKS=');b=s.index('function context(',a);s=s[:a]+s[b:];s=s.replace("const VERSION='1.0.4'","const VERSION='1.0.3'")
s=s.replace("function sha256(text){return sha256Bytes(new TextEncoder().encode(text));}\nfunction sha256Bytes(bytes){\n if(!(bytes instanceof Uint8Array))throw Error('SHA-256 bytes require Uint8Array');\n const length=bytes.length", "function sha256(text){\n const bytes=new TextEncoder().encode(text),length=bytes.length")
s=s.replace('eligibleQuestionIds:eligible.questions.map(e=>e.question.id),','').replace('POLICY_CHECKS,VISUAL_CHECKS,visualEligibility,','POLICY_CHECKS,').replace('stableJSON,sha256,sha256Bytes,','stableJSON,sha256,')
ck('all old source, literal-answer, policy, tool and reuse gates byte-identical after declared additions',s==(D/'app-learning-resources.js.before-104').read_text())
s=(R/'app/core.js').read_text();oldcore=(D/'app-core.js.before-104').read_text();a=s.index('  function rankRevisionQuestions');b=s.index('  function selectQuestions',a);oa=oldcore.index('  function rankRevisionQuestions');ob=oldcore.index('  function selectQuestions',oa);s=s[:a]+oldcore[oa:ob]+s[b:];s=s.replace('rankRevisionQuestions,currentStudyProgress,studyFollowUps,','rankRevisionQuestions,')
ck('core old scoring, fingerprints, exams, backups and filters byte-identical outside declared recommendation helpers',s==oldcore)
bank=read('data/bank.json');baseline=read('audits/final-ui-policy-104-review/content-baseline.json');rows=[{'id':q['id'],'version':q['version'],'status':q['status'],'sha256':v.question_hash(q)} for q in bank['questions']]
ck('all5071 question IDs/statuses/versions and answer-content hashes unchanged',rows==baseline['questions'])
ck('entire approved computational tool payload remains exact',sha((R/'data/learning-tools-course.json').read_bytes())==baseline['toolPayloadFileSha256']=='f38a953f52c80a0c921a95840d23495d751101ab82ee977b0b205852c30c76b8')
objects=read('data/learning-tools-course.json');objects=objects.get('learningTools',objects);flat={x['id']:x for values in objects.values() for x in values};bindings=read('audits/blind-binding-learning-resources-policy-v3.json')['resourceBindings']
ck('all18 approved tool object hashes remain exact',len(bindings)==18 and all(v.question_hash(flat[b['id']])==b['sha256'] for b in bindings))
oldschema=json.loads((B/'data/schema.bank.json').read_text());schema=read('data/schema.bank.json');schema['properties'].pop('questionVisuals');added=set(schema['$defs'])-set(oldschema['$defs']);[schema['$defs'].pop(k) for k in added]
ck('schema preserves every previous definition, only visual sidecar definitions added',schema==oldschema,sorted(added))
ck('independent reviewer is not any policy author',not {'verify_remaining_assignment_answers:independent-ui-policy-reviewer'}.intersection({p['authorId'],*p.get('revisionAuthors',[])}))
out={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'policySha256':m['policySha256'],'policyFileSha256':m['policyFileSha256'],'checks':checks,'passed':len(checks),'failed':0,'browserQA':False};(D/'binding-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
