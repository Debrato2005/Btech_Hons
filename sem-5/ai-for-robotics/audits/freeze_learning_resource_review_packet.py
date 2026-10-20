"""One-time author freeze; no question, bank, review or Git writes."""
from pathlib import Path
import json,hashlib,importlib.util,subprocess,datetime
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text())
def write(p,v): (R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('frozen_validator',R/'scripts/validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
packet='audits/blind-learning-resources-v1.json';bindings='audits/blind-binding-learning-resources-v1.json'
assert not (R/packet).exists() and not (R/bindings).exists()
paths=['app/learning-resources.js','app/learning-resource-ui.js','scripts/learning_resources.py','app/learning-tools.js','app/course-numerical.js','app/core.js','app/app.js','scripts/build.py','scripts/assemble_bank.py','scripts/validate.py','app/index.html']
policy=read('data/learning-resource-policy.json');policy['codeHashes']={p:sha(p) for p in paths};write('data/learning-resource-policy.json',policy)
b=read('data/learning-tools-course.json');records=[x for rows in b['learningTools'].values() for x in rows]
for t in records:
 for f in t['implementationFiles']:assert sha(f['path'])==f['sha256'],f
program="""const fs=require('fs'),E=require('./app/learning-tools.js'),b=require('./data/bank.json');b.learningTools=require('./data/learning-tools-course.json').learningTools;const r=E.registerBankNumericalFamilies(b,{includeDrafts:true});if(r.diagnostics.length)throw Error(JSON.stringify(r));console.log(JSON.stringify({numerical:b.learningTools.numericalFamilies.map(t=>({id:t.id,variants:[1,2,3].map(i=>E.generateVariant(t.id,{seed:'independent-review-'+i}))})),algorithms:b.learningTools.algorithmVisualizations.map(t=>({id:t.id,trace:t.config?E.searchTrace(t.graph,t.config):E.qLearningTrace(t.qLearningConfig)}))}));"""
outputs=json.loads(subprocess.run(['node','-e',program],cwd=R,capture_output=True,text=True,check=True).stdout)
full_variants={t['id']:t['variants'] for t in outputs['numerical']};full_traces={t['id']:t['trace'] for t in outputs['algorithms']}
cleanrefs=lambda refs:[{k:x for k,x in c.items() if k!='evidenceText'} for c in refs]
rows=[];answer_map={}
for t in records:
 row={k:t[k] for k in ('id','version','title','week','lectureId','questionIds','questionBindings','slideIds','assumptions','description') if k in t};row['sourceRefs']=cleanrefs(t['sourceRefs']);row['hasRetainedSourceQualifications']=bool(t.get('sourceQualifications'));row['hasConflictResolution']=bool(t.get('conflictResolution'));row['primaryEvidenceLocators']=[{k:x for k,x in p.items() if k in ('url','title','source','section','locator')} for p in t.get('primaryEvidence',[])]
 if 'generatorKind' in t:
  row.update({k:t[k] for k in ('generatorKind','generatorVersion','parameterDomains')});row['examples']=[];answer_map[t['id']]=[]
  for i,var in enumerate(full_variants[t['id']],1):
   option_map={o['id']:'o'+str(j+1) for j,o in enumerate(var['options'])}
   row['examples'].append({k:var[k] for k in ('seed','parameters','question','type','units','precision','rounding','assumptions')})
   row['examples'][-1].update({'exampleId':t['id']+'.example'+str(i),'options':[{'id':option_map[o['id']],'text':o['text']} for o in var['options']]})
   answer_map[t['id']].append({'exampleId':t['id']+'.example'+str(i),'blindToOriginalOptionIds':{x:k for k,x in option_map.items()},'correctBlindOptionIds':[option_map[x] for x in var['correctOptionIds']],'fullGeneratedVariant':var})
 else:
  for k in ('graph','config','qLearningConfig'):
   if k in t:row[k]=t[k]
  row['executionConventions']=full_traces[t['id']]['conventions']
  row['reviewTask']='Independently derive each frontier/current state and final path/cost, or each sequential Q table. State whether the source supports the configured convention and any added assumptions.'
 rows.append(row)
inspect=read('audits/learning-resource-completion-source-inspections.json')
p={'packetVersion':1,'authorId':b['authorId'],'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent review of exact-projection code/policy plus 18 new draft tools. Prior question approvals are evidence links, not approval of these transformed resources. Freeze independent example answers and traces before opening keyed author data or generator implementation.','policy':policy,'policyReviewInstructions':'Inspect exact context preservation and fail-closed code after freezing the examples. Runtime check status must distinguish Node/default-Python execution from blocked browser launch. Do not mark an unassessed check true.','sourcePreviewPattern':'sources/previews/lectures/page-NNNN.webp','resources':rows,'sourceInspectionAudit':'audits/learning-resource-completion-source-inspections.json','runtimeBoundary':'Default Python/Node only. Do not use /tmp/robotics-l35-venv, new dependencies/audio, checkpoints/model inference, downloads, NLTK corpora or denied L49 notebook retrieval. Browser launch failed before page checks with socket Operation not permitted; no alternate launch is authorized by this packet.'}
write(packet,p)
write(bindings,{'packetPath':packet,'packetSha256':sha(packet),'policy':{'id':policy['id'],'version':policy['version'],'sha256':hashlib.sha256(v.canonical_json(policy).encode()).hexdigest()},'resourceBindings':[{'id':t['id'],'version':t['version'],'sha256':v.question_hash(t)} for t in records],'codeFiles':[{'path':k,'sha256':h} for k,h in policy['codeHashes'].items()]})
write('audits/learning-resources-v1-author-example-results.json',{'scope':'Author-generated output, not independent approval. Open only after independent answers are frozen.','packetSha256':sha(packet),'numericalExamples':answer_map,'algorithmTraces':full_traces})
print(json.dumps({'packet':packet,'packetSha256':sha(packet),'bindings':bindings,'bindingsSha256':sha(bindings),'resources':len(records),'examples':sum(len(r.get('examples',[])) for r in rows),'policySha256':hashlib.sha256(v.canonical_json(policy).encode()).hexdigest()},indent=2))
