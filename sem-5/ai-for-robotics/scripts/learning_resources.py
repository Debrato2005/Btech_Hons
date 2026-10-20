"""Fail-closed linkage for learning resources; never changes question objects.

Canonical hashes are those of validate.question_hash. Runtime hashes use the
explicit JavaScript stableJSON representation and are NOT substituted for them.
"""
from pathlib import Path
import copy, hashlib, importlib.util, json, subprocess

# The validator is also supported when loaded with spec_from_file_location.
# Resolve its canonical helpers by sibling path, not the caller's cwd/sys.path.
_validator_spec = importlib.util.spec_from_file_location(
 'robotics_learning_resource_canonical_validator', Path(__file__).with_name('validate.py'))
_validator = importlib.util.module_from_spec(_validator_spec)
_validator_spec.loader.exec_module(_validator)
question_hash, canonical_json = _validator.question_hash, _validator.canonical_json
POLICY_CHECKS=('exactProjection','contextPreservation','sourceAndReviewBinding','failClosedMutationTests','runtimeTests')
TOOL_CHECKS=('sourceSupport','assumptions','answerOrTrace','calculations','runtimeTests','explanation','sourceLinkage')
def digest(value): return hashlib.sha256(canonical_json(value).encode()).hexdigest()
def read(path,default=None): return json.loads(path.read_text()) if path.exists() else default
def nonblank(value): return isinstance(value,str) and bool(value.strip())
def independent_reviewer(value,record):
 return nonblank(value) and value.strip() not in {a.strip() for a in [record.get('authorId'),*record.get('revisionAuthors',[])] if nonblank(a)}
def unique_ids(values):
 return isinstance(values,list) and bool(values) and all(nonblank(x) for x in values) and len(set(values))==len(values)
def literal_answer_valid(question,answer):
 options=question.get('options')
 if not isinstance(options,list) or len(options)<2 or any(not isinstance(o,dict) or not nonblank(o.get('id')) for o in options): return False
 ids=[o['id'] for o in options]
 return unique_ids(ids) and unique_ids(answer) and set(answer)<=set(ids) and (len(answer)==1 if question.get('selectionMode')=='single' else question.get('selectionMode')=='multi')
def source_ref_allowed(ref,sources,slides):
 if not isinstance(ref,dict): return False
 source=sources.get(ref.get('sourceId'),{});slide=slides.get(ref.get('slideId'),{});page=ref.get('physicalPage');count=source.get('pageCount');h=ref.get('sourceSha256')
 return (source.get('retrievalStatus')=='ready' and isinstance(h,str) and len(h)==64 and all(c in '0123456789abcdef' for c in h)
  and source.get('sha256')==h and slide.get('sourceSha256')==h and slide.get('sourceId')==ref.get('sourceId')
  and type(page) is int and type(count) is int and 1<=page<=count and type(slide.get('physicalPage')) is int and slide.get('physicalPage')==page
  and slide.get('visualInspection',{}).get('status')=='complete' and slide.get('disposition') in ('examinable','repeated','excluded'))
def policy_approval(policy,reviews):
 h=digest(policy);rs=[r for r in reviews if r.get('resourceId')==policy.get('id') and r.get('resourceVersion')==policy.get('version') and r.get('resourceSha256')==h]
 return not any(r.get('decision') in ('flagged','rejected') for r in rs) and any(r.get('decision')=='verified' and independent_reviewer(r.get('reviewerId'),policy) and all(r.get('checks',{}).get(k) is True for k in POLICY_CHECKS) for r in rs)
def code_errors(policy,root):
 errors=[]
 for name,h in policy.get('codeHashes',{}).items():
  p=(root/name).resolve()
  if not p.is_relative_to(root.resolve()) or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:errors.append('Extractor code hash mismatch: '+name)
 if not policy.get('codeHashes'):errors.append('Missing extractor code hashes.')
 return errors
def prepare_integrity(bank,root):
 """Called by assembly only after the current question review gate."""
 root=Path(root);policy=read(root/'data/learning-resource-policy.json',{});reviews=read(root/'data/learning-resource-policy-reviews.json',[])
 qlist=[q for q in bank['questions'] if q.get('status')=='verified'];tool_records=[r for rs in bank['learningTools'].values() for r in rs if r.get('status')=='verified'];payload={'questions':qlist,'policy':policy,'tools':tool_records}
 program="const R=require(process.argv[1]);let s='';process.stdin.setEncoding('utf8');process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const p=JSON.parse(s);console.log(JSON.stringify({policy:R.sha256(R.stableJSON(p.policy)),questions:Object.fromEntries(p.questions.map(q=>[q.id,R.runtimeQuestionDigest(q)])),tools:Object.fromEntries(p.tools.map(q=>[q.id,R.runtimeQuestionDigest(q)]))}));});"
 result=subprocess.run(['node','-e',program,str(root/'app/learning-resources.js')],input=json.dumps(payload,ensure_ascii=False),text=True,capture_output=True,check=True)
 runtime=json.loads(result.stdout);errors=code_errors(policy,root)
 return {'formatVersion':1,'toolReviews':read(root/'data/learning-tool-reviews.json',[]),'toolBindings':{r['id']:{'version':r['version'],'sha256':question_hash(r),'runtimeSha256':runtime['tools'][r['id']]} for r in tool_records},'policy':policy,'policySha256':digest(policy),'runtimePolicySha256':runtime['policy'],'policyReviews':reviews,'policyEligible':bool(policy and not errors and policy_approval(policy,reviews)),'policyDiagnostics':errors or ([] if policy_approval(policy,reviews) else ['Extractor policy awaits independent exact-hash review.']),'bindings':{q['id']:{'questionVersion':q['version'],'questionSha256':question_hash(q),'runtimeSha256':runtime['questions'][q['id']]} for q in qlist}}
def integrity_errors(bank,root):
 x=bank.get('learningResourceIntegrity');errors=[]
 if x is None:
  if any(r.get('status')=='verified' for records in bank.get('learningTools',{}).values() for r in records):errors.append('Verified learning tools require exact-hash integrity metadata.')
  return errors
 policy=x.get('policy',{});code=code_errors(policy,Path(root));expected=bool(policy and not code and policy_approval(policy,x.get('policyReviews',[])))
 if x.get('policySha256')!=digest(policy):errors.append('Learning extractor policy content hash mismatch.')
 if x.get('policyEligible') is not expected:errors.append('Learning extractor activation does not match independent approval/code hashes.')
 if x.get('policyEligible'):errors.extend(code)
 qmap={q['id']:q for q in bank['questions']}
 for qid,binding in x.get('bindings',{}).items():
  q=qmap.get(qid)
  if not q or q.get('status')!='verified' or binding.get('questionVersion')!=q['version'] or binding.get('questionSha256')!=question_hash(q):errors.append('Stale learning-resource question binding: '+qid)
 for records in bank['learningTools'].values():
  for record in records:
   if record.get('status')=='verified':
    reasons,_=tool_reasons(record,bank,root,x.get('toolReviews',[]));errors.extend(record['id']+': '+r for r in reasons)
 return errors


def tool_reasons(record,bank,root,reviews):
 if not isinstance(record,dict) or not isinstance(record.get('id'),str):return ['Malformed learning tool record.'],[]
 refs=record.get('sourceRefs',[]);links=record.get('questionBindings',[])
 if not isinstance(refs,list) or any(not isinstance(c,dict) or not all(k in c for k in ('sourceId','sourceSha256','slideId','physicalPage')) for c in refs):return ['Malformed source references.'],[]
 if not isinstance(links,list) or any(not isinstance(c,dict) or not all(k in c for k in ('questionId','questionVersion','questionSha256')) for c in links):return ['Malformed question bindings.'],[]
 if not isinstance(record.get('implementationFiles',[]),list) or any(not isinstance(c,dict) or not isinstance(c.get('path'),str) or not isinstance(c.get('sha256'),str) for c in record.get('implementationFiles',[])):return ['Malformed implementation bindings.'],[]
 qmap={q['id']:q for q in bank['questions']};sources={s['id']:s for s in bank['sources']};slides={s['id']:s for s in bank['slides']};reasons=[];h=question_hash(record)
 rs=[r for r in reviews if r.get('toolId')==record['id'] and r.get('toolVersion')==record.get('version') and r.get('toolSha256')==h]
 if any(r.get('decision') in ('flagged','rejected') for r in rs):reasons.append('Current independent tool dispute.')
 authors={record.get('authorId'),*record.get('revisionAuthors',[])};refs=record.get('sourceRefs',[])
 accepted=[r for r in rs if r.get('id') and r.get('decision')=='verified' and independent_reviewer(r.get('reviewerId'),record) and all(r.get('checks',{}).get(k) is True for k in TOOL_CHECKS) and all(r.get('sourceVersions',{}).get(c['sourceId'])==c['sourceSha256'] and c['slideId'] in r.get('reviewedSlideIds',[]) for c in refs) and all(sources.get(sid,{}).get('sha256')==h for sid,h in r.get('sourceVersions',{}).items())]
 if not accepted:reasons.append('No current complete independent tool approval.')
 if not refs:reasons.append('No source references.')
 for c in refs:
  source=sources.get(c['sourceId'],{});slide=slides.get(c['slideId'],{})
  if not source_ref_allowed(c,sources,slides):reasons.append('Source/page/inspection mismatch.')
  if c.get('role')=='conflict' and not record.get('conflictResolution'):reasons.append('Unqualified tool source conflict.')
 links=record.get('questionBindings',[])
 if not links:reasons.append('No hash-bound approved-question links.')
 if not unique_ids(record.get('questionIds')) or not unique_ids([x.get('questionId') for x in links]) or set(record['questionIds'])!={x.get('questionId') for x in links}:reasons.append('Question IDs and binding IDs differ.')
 for link in links:
  q=qmap.get(link.get('questionId'),{})
  if q.get('status')!='verified' or q.get('version')!=link.get('questionVersion') or question_hash(q)!=link.get('questionSha256'):reasons.append('Linked question is not currently approved at its bound hash.')
  if q.get('synthetic') or q.get('origin')=='synthetic':reasons.append('Synthetic question is not course evidence.')
  qrefs=q.get('citations',[])
  if not isinstance(qrefs,list) or any(not isinstance(c,dict) or not all(k in c for k in ('sourceId','sourceSha256','slideId','physicalPage')) for c in qrefs):
   reasons.append('Malformed linked-question citations.');continue
  if any(not source_ref_allowed(c,sources,slides) for c in qrefs):reasons.append('Linked question source/page/inspection mismatch.')
  if any(c.get('role')=='conflict' for c in qrefs) and not q.get('conflictResolution'):reasons.append('Unqualified linked-question source conflict.')
  if not literal_answer_valid(q,q.get('correctOptionIds')):reasons.append('Invalid linked-question literal answer key.')
  current=[r for r in bank.get('reviews',[]) if r.get('questionId')==q.get('id') and r.get('questionVersion')==q.get('version') and r.get('questionSha256')==question_hash(q) and all(r.get('sourceVersions',{}).get(c['sourceId'])==c['sourceSha256'] for c in qrefs) and all(sources.get(sid,{}).get('sha256')==h for sid,h in r.get('sourceVersions',{}).items())]
  accepted_question=any(r.get('decision')=='verified' and independent_reviewer(r.get('reviewerId'),q) and all(r.get('checks',{}).get(k) is True for k in _validator.CHECK_KEYS) and literal_answer_valid(q,r.get('independentAnswerOptionIds')) and literal_answer_valid(q,q.get('correctOptionIds')) and set(r['independentAnswerOptionIds'])==set(q['correctOptionIds']) and all(c['slideId'] in r.get('reviewedSlideIds',[]) for c in qrefs) for r in current)
  if not qrefs or not accepted_question or any(r.get('decision') in ('flagged','rejected') for r in current):reasons.append('Linked question lacks current complete independent approval.')
 if (record.get('generatorKind') or record.get('config') or record.get('qLearningConfig')) and not record.get('implementationFiles'):reasons.append('Executable tool requires hash-bound implementation files.')
 for impl in record.get('implementationFiles',[]):
  p=(Path(root)/impl['path']).resolve()
  if not p.is_relative_to(Path(root).resolve()) or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=impl['sha256']:reasons.append('Tool implementation hash changed.')
 return sorted(set(reasons)),accepted

def apply_tool_gate(bank,root):
 reviews=read(Path(root)/'data/learning-tool-reviews.json',[]);diagnostics=[]
 for records in bank['learningTools'].values():
  for record in records:
   reasons,accepted=tool_reasons(record,bank,root,reviews)
   record['reviewIds']=[r['id'] for r in accepted]
   record['status']='verified' if not reasons else 'draft'
   if reasons:diagnostics.append({'id':record['id'],'reasons':reasons})
 return diagnostics
