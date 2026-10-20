"""Assemble, validate and test with actual exits; persist a hash-bound receipt."""
from pathlib import Path
import json,subprocess,sys,hashlib,datetime,re
R=Path(__file__).resolve().parents[1];tag=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=R/'audits';logs=Path('/workspace/shared/robotics-verification-logs')/('robotics-milestone-'+tag);logs.mkdir(parents=True)
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def input_manifest():
 paths=set()
 for folder in ['data/question-batches','data/reviews','data/inspection-batches']:
  paths.update((R/folder).glob('*.json'))
 for folder in ['app','scripts','tests']:
  paths.update(p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.log'])
 paths.update((R/'data').glob('schema.*.json'))
 paths.update((R/'data').glob('learning-*.json'))
 return {str(p.relative_to(R)):hashfile(p) for p in sorted(paths)}
inputs=input_manifest()
receipt={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputManifest':inputs,'processResults':{},'complete':False,'limitations':['Integrity validation does not certify scientific correctness or complete-course coverage.','Actual downloaded-file offline browser QA remains blocked.']}
steps=[('assembly',['python3','scripts/assemble_bank.py']),('validator',['python3','scripts/validate.py','--report','audits/integrity-latest.json']),('build',['python3','scripts/build.py']),('pythonTests',['python3','-m','unittest','discover','-s','tests','-p','test_*.py']),('nodeTests',['node','--test','app/core.test.js','app/algorithm-selector.test.js','tests/test_learning_tools.js','tests/test_learning_resources.js'])]
for name,cmd in steps:
 log=logs/(name+'.log')
 with log.open('w') as f:r=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 receipt['processResults'][name+'ExitCode']=r.returncode
 if name=='assembly' and r.returncode==0:
  receipt['bankSha256']=hashfile(R/'data/bank.json');receipt.update(json.loads((R/'data/progress-summary.json').read_text()));receipt['counts']['questions']=sum(receipt['counts'][k] for k in ['verifiedQuestions','draftQuestions','flaggedQuestions'])
 if name=='validator' and (R/'audits/integrity-latest.json').exists():
  v=json.loads((R/'audits/integrity-latest.json').read_text());receipt['validator']={'valid':v['valid'],'errors':v['errors'],'reportSha256':hashfile(R/'audits/integrity-latest.json')}
 if r.returncode or (name=='validator' and not receipt['validator']['valid']):break
 if name=='build':
  br=json.loads((R/'dist/ai-for-robotics-mcq.build-report.json').read_text());receipt['artifact']={k:br[k] for k in ['output','bytes','sha256','bankVersion']}
 if name=='pythonTests':
  m=re.search(r'Ran (\d+) tests',log.read_text());receipt['pythonTestsPassed']=int(m.group(1)) if m else None
 if name=='nodeTests':
  m=re.search(r'(?:#|ℹ) pass (\d+)',log.read_text());receipt['nodeTestsPassed']=int(m.group(1)) if m else None
 if receipt.get('bankSha256') and hashfile(R/'data/bank.json')!=receipt['bankSha256']:raise RuntimeError('Bank mutated during milestone verification')
final_inputs=input_manifest()
receipt['inputManifestChangedDuringRun']=sorted(p for p in set(inputs)|set(final_inputs) if inputs.get(p)!=final_inputs.get(p))
path=out/('validated-milestone-'+tag+'.json');path.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='inputManifest'},indent=2));print('receipt',path)
assert len(receipt['processResults'])==len(steps) and all(x==0 for x in receipt['processResults'].values()) and receipt['validator']['valid'] and not receipt['inputManifestChangedDuringRun']
