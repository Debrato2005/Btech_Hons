"""Exact candidate identity and approved-baseline delta check; no canonical writes."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,difflib
R=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads((R/p).read_text())
spec=importlib.util.spec_from_file_location('reviewer_validator',R/'scripts/validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
p=read('data/learning-resource-policy.json');manifest=read('audits/final-delivery-audit/policy-1.0.3-expanded-candidate.json');old=read('data/learning-resource-policy-reviews.json')[2];checks=[]
def ck(name,condition,detail=None):
 checks.append({'name':name,'passed':bool(condition),'details':detail});assert condition,name
ck('exact current manifest policy/file identity',p['version']=='1.0.3' and sha(v.canonical_json(p).encode())==manifest['policySha256'] and sha((R/manifest['policyPath']).read_bytes())==manifest['policyFileSha256'])
ck('all policy-bound files match exact frozen bytes',p['codeHashes']==manifest['codeHashes'] and all(sha((R/f).read_bytes())==h for f,h in p['codeHashes'].items()),p['codeHashes'])
changed=[f for f,h in p['codeHashes'].items() if old['codeHashes'].get(f)!=h]
ck('only five expected approved implementation files changed',set(changed)=={'app/app.js','app/core.js','app/learning-resources.js','scripts/assemble_bank.py','scripts/validate.py'},changed)
s=(R/'app/learning-resources.js').read_text();a=s.index('// A bounded study-order heuristic');b=s.index('function base(',a);s=s[:a]+s[b:];s=s.replace("const VERSION='1.0.3'","const VERSION='1.0.2'").replace(',assignmentPriority});', '});')
ck('existing JS question/context/tool gates byte-identical after removing declared new function/version/export',sha(s.encode())==old['codeHashes']['app/learning-resources.js'])
s=(R/'app/core.js').read_text();a=s.index('  function rankRevisionQuestions');b=s.index('  function selectQuestions',a);s=s[:a]+s[b:];s=s.replace('revisionScore,rankRevisionQuestions,','revisionScore,')
ck('existing core behavior byte-identical after removing new ranking function/export',sha(s.encode())==old['codeHashes']['app/core.js'])
s=(R/'scripts/validate.py').read_text().replace('_COVERAGE_LINKS = None\n','');a=s.index('def coverage_links_module():');b=s.index('def canonical_json(',a);s=s[:a]+s[b:];s='\n'.join(l for l in s.split('\n') if 'errors.extend(coverage_links_module().assignment_reuse_errors' not in l and not any("'"+k+"':" in l for k in ('conceptsWithReviewedAssignmentReuse','assignmentItemsWithReviewedReuse','additionalUniqueQuestionsFromReuse')))
ck('existing validator byte-identical except declared loader/gate/count additions',sha(s.encode())==old['codeHashes']['scripts/validate.py'])
baseline=Path('/workspace/shared/robotics-verification-logs/assemble_bank-approved-575e2c9.py').read_text();ck('parent-provided assembler approved baseline exact',sha(baseline.encode())==old['codeHashes']['scripts/assemble_bank.py'])
s=(R/'scripts/assemble_bank.py').read_text();a=s.index('\n_REUSE_VALIDATOR=None');b=s.index('def main():',a);s=s[:a]+s[b:];s=s.replace(',importlib.util','');s=s.replace(" bank['assignmentReuse']=build_assignment_reuse(bank,ROOT)\n",'');s='\n'.join(l for l in s.split('\n') if not any(l.startswith(" counts['"+k+"']") for k in ('assignmentItemsWithReviewedReuse','conceptsWithReviewedAssignmentReuse','additionalUniqueQuestionsFromReuse')))
ck('existing assembly path byte-identical except declared helper/import/sidecar/count additions',s==baseline)
objects=read('data/learning-tools-course.json');objects=objects.get('learningTools',objects);flat=[x for values in objects.values() for x in values];bindings=read('audits/blind-binding-learning-resources-policy-v3.json')['resourceBindings'];byid={x['id']:x for x in flat}
ck('all 18 previously approved computational objects exact',len(bindings)==18 and all(v.question_hash(byid[b['id']])==b['sha256'] and byid[b['id']]['version']==b['version'] for b in bindings))
ck('entire author tool payload file exact',sha((R/'data/learning-tools-course.json').read_bytes())==manifest['learningToolPayloadSha256']=='f38a953f52c80a0c921a95840d23495d751101ab82ee977b0b205852c30c76b8')
ck('policy authors explicitly distinct from independent reviewer',not {'verify_remaining_assignment_answers:independent-ui-policy-reviewer'}.intersection({p['authorId'],*p.get('revisionAuthors',[])}))
for name,oldpath,newpath in [('app-expanded',R/'audits/final-delivery-audit/app-before-assignment-priority.js',R/'app/app.js'),('assembler-expanded',Path('/workspace/shared/robotics-verification-logs/assemble_bank-approved-575e2c9.py'),R/'scripts/assemble_bank.py')]:
 (D/(name+'.patch')).write_text(''.join(difflib.unified_diff(oldpath.read_text().splitlines(True),newpath.read_text().splitlines(True),fromfile=str(oldpath),tofile=str(newpath))))
out={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'policySha256':sha(v.canonical_json(p).encode()),'policyFileSha256':sha((R/'data/learning-resource-policy.json').read_bytes()),'checks':checks,'passed':len(checks),'failed':0,'browserQA':False};(D/'binding-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
