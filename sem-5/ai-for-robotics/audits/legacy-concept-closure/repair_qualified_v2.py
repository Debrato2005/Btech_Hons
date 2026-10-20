"""Only the three independently flagged v1 questions are revised."""
import copy,datetime,hashlib,json,pathlib,sys
R=pathlib.Path(__file__).resolve().parents[2];D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,canonical_json,schema_errors
v1=json.loads((D/'qualified-drafts-v1.json').read_text());n1=json.loads((D/'neutral-packet-v1.json').read_text());review=json.loads((D/'independent-review-v1.json').read_text());qm={q['id']:q for q in v1['questions']};nm={q['id']:q for q in n1['questions']};rm={r['questionId']:r for r in review};now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(x):return hashlib.sha256(canonical_json(x).encode()).hexdigest()
def fsha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
repairs={
 'W01-L02-Q-106':'Remove answer-bearing purpose clauses from the stem; retain the actual PCA-versus-clustering distinction.',
 'W01-L02-Q-107':'Replace the two implausible distractors with software-version and bundled-dataset count confusions.',
 'W01-L05-Q-081':'Supply the bounded official indexed historical dates before answer selection, with no direct-read or current-release claim.'}
out=[];neutral=[]
for qid,reason in repairs.items():
 assert rm[qid]['decision']=='flagged';q=copy.deepcopy(qm[qid]);q['version']=2
 if qid.endswith('106'):
  q['stem']='A robotics team applies PCA and then K-means to an unlabeled feature matrix. Which interpretation correctly qualifies the PCA entry in the slide’s Clustering box?'
 if qid.endswith('107'):
  for o in q['options']:
   if o['id']=='o2':o['text']='Fixing the Habitat-Sim software version is sufficient to reproduce the table’s scan count, without identifying the loaded scene dataset.'
   if o['id']=='o4':o['text']='The table’s 100K figure specifies the scene-scan collection bundled with Habitat-Sim, so installing the simulator establishes that dataset size.'
  q['solution']['optionExplanations']['o2']='A software-version identifier does not identify the loaded scene dataset or its version. Reproducing a scene count requires those data-specific facts; the available evidence does not validate the table’s count.'
  q['solution']['optionExplanations']['o4']='This assumes that the simulator installation includes a fixed scan collection. Supported scene datasets are distinct from the simulation software; the table supplies no verified bundle or version-specific inventory.'
 if qid.endswith('081'):
  q['stem']='Read the printed ROS timeline together with these historical distribution entries from official indexed evidence: Ardent, 2017-12-08; Bouncy, 2018-07-02; Crystal, 2018-12-14. Select every supported interpretation.'
 q['revisionAuthors']=[q['authorId']]
 q['revisionHistory']=[{'version':2,'authorId':q['authorId'],'priorQuestionSha256':question_hash(qm[qid]),'reason':reason,'revisedAt':now,'reviewId':rm[qid]['id']}]
 schema=json.loads((R/'data/schema.bank.json').read_text());assert not schema_errors(q,schema['$defs']['question'],root=schema)
 n=copy.deepcopy(nm[qid])
 for k in ['id','version','stem','selectionMode','assumptions','options','citations']:n[k]=copy.deepcopy(q[k])
 out.append(q);neutral.append(n)
wr('qualified-drafts-v2.json',{'schemaVersion':'1.0.0','batchId':'W01-L02-L05-QUALIFIED-GAPS-v2-repairs','createdAt':now,'status':'frozen_awaiting_independent_review','questions':out,'reviews':[],'repairScope':repairs,'preservedApprovedQuestions':[{'id':q['id'],'version':q['version'],'questionSha256':question_hash(q),'wholeObjectSha256':sha(q)} for q in v1['questions'] if rm[q['id']]['decision']=='verified']})
wr('neutral-packet-v2.json',{'batchId':'W01-L02-L05-QUALIFIED-GAPS-v2-repairs','createdAt':now,'questionKeysIncluded':False,'questions':neutral,'restrictions':n1['restrictions'],'reviewInstructions':'Three revised questions only. Freeze independent option-ID responses before opening qualified-drafts-v2.json or repair_qualified_v2.py. Prior review exposure is disclosed. All prior Anubis denials remain stopped.'})
wr('freeze-manifest-v2.json',{'createdAt':now,'priorNeutralFileSha256':fsha(D/'neutral-packet-v1.json'),'priorDraftFileSha256':fsha(D/'qualified-drafts-v1.json'),'independentReviewV1Sha256':fsha(D/'independent-review-v1.json'),'draftFileSha256':fsha(D/'qualified-drafts-v2.json'),'neutralFileSha256':fsha(D/'neutral-packet-v2.json'),'questionBindings':[{'id':q['id'],'version':q['version'],'questionSha256':question_hash(q),'wholeObjectSha256':sha(q),'neutralObjectSha256':sha(n)} for q,n in zip(out,neutral)],'preservedApprovedQuestionBindings':[{'id':q['id'],'version':q['version'],'questionSha256':question_hash(q),'wholeObjectSha256':sha(q)} for q in v1['questions'] if rm[q['id']]['decision']=='verified'],'canonicalWritesInThisStep':False})
print(json.dumps({'neutralPacketSha256':fsha(D/'neutral-packet-v2.json'),'questions':list(repairs),'approvedWholeObjectsPreserved':3,'v1NeutralUnchanged':fsha(D/'neutral-packet-v1.json')=='8cf5edc49c8fa7cfcd1a651329f4e751d0cc6669cf15f98088d2282f44e8b167'},indent=2))
