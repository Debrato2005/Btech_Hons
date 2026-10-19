"""Author-side invariant checks, not independent approval of L04 v2."""
import pathlib,json,hashlib,datetime,sys
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash
b=json.loads((ROOT/'data/question-batches/W01-L04.json').read_text());old=json.loads((ROOT/'data/question-batches/archive/W01-L04-v1.json').read_text());rs=json.loads((ROOT/'data/reviews/W01-L04-v1-independent.json').read_text());packet=json.loads((ROOT/'audits/blind-W01-L04-v2-revisions.json').read_text());summary=json.loads((ROOT/'audits/W01-L04-v2-revision-summary.json').read_text());qs={q['id']:q for q in b['questions']};oq={q['id']:q for q in old['questions']};good={r['questionId'] for r in rs if r['decision']=='verified'};bad={r['questionId'] for r in rs if r['decision']=='flagged'}
checks=[]
def ck(n,v):checks.append({'name':n,'pass':bool(v)});assert v,n
ck('Exactly 37 flagged IDs revised',set(k for k in qs if question_hash(qs[k])!=question_hash(oq[k]))==bad and len(bad)==37)
ck('All 94 approved correctness hashes unchanged',len(good)==94 and all(question_hash(qs[k])==question_hash(oq[k]) for k in good))
ck('37 v2 draft questions and revision attribution',all(qs[k]['version']==2 and qs[k]['status']=='draft' and summary['revisionAuthorId'] in qs[k]['revisionAuthors'] and not qs[k]['reviewIds'] for k in bad))
ck('All 131 original keyed answer sets unchanged',all(qs[k]['correctOptionIds']==oq[k]['correctOptionIds'] for k in qs))
ck('Every option has a unique text and an explanation',all(len({o['text'] for o in q['options']})==len(q['options']) and set(q['solution']['optionExplanations'])=={o['id'] for o in q['options']} for q in b['questions']))
ck('New blind packet has exactly the 37 revised IDs',len(packet['questions'])==37 and {q['id'] for q in packet['questions']}==bad)
for q in packet['questions']:
 ck(q['id']+' hidden answer content',not any(k in q for k in ['correctOptionIds','solution','revisionHistory']) and all('evidenceText' not in c for c in q['citations']))
 ck(q['id']+' exact full-question hash',q['questionSha256']==question_hash(qs[q['id']]))
ck('P0160 Q04 velocities',np.allclose(np.array([.02,.04,.06])/.02,[1,2,3]))
ck('P0160 Q04 actual distractor mechanism',np.allclose(1/np.array([.02,.04,.06]),[50,25,16.666666666666668]))
ck('P0160 Q04 inverse velocities are different',np.allclose(1/np.array([1.,2.,3.]),[1,.5,1/3]))
pose=np.array([0,0]);motions=np.array([[1,1],[1,.5],[1,.5],[1,1]])
ck('P0166 Q07 first motion dtype is float despite integral values',np.issubdtype(motions[0].dtype,np.floating) and np.array_equal(motions[0],[1,1]))
try:pose+=motions[0]
except Exception as e:ck('P0166 Q07 first update raises output-casting error',type(e).__name__=='UFuncTypeError');error=str(e)
else:raise AssertionError('Expected in-place cast error')
ck('Original v1 blind evidence untouched',hashlib.sha256((ROOT/'audits/blind-answers-W01-L04-v1.json').read_bytes()).hexdigest()=='50b0106805308529ca51b0a49f2f475a57917bb6fbbb7bc7a631dbe4e346fa5e')
report={'authorId':summary['revisionAuthorId'],'independentVerification':False,'executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'numpyVersion':np.__version__,'pythonVersion':sys.version,'checks':checks,'total':len(checks),'passed':sum(x['pass'] for x in checks),'castingErrorMessage':error,'authorBatchSha256':hashlib.sha256((ROOT/'data/question-batches/W01-L04.json').read_bytes()).hexdigest(),'blindPacketSha256':hashlib.sha256((ROOT/'audits/blind-W01-L04-v2-revisions.json').read_bytes()).hexdigest(),'revisionSourceVisualChecks':[]}
for page,note in {127:'The exact foundational trio is dynamic systems, computer science and domain ontology.',151:'The lower in-kit board has the explicit Carrier board with I/O ports arrow, distinguished from compute module below cooling assembly; no separate external expansion board is labeled.',152:'The three preparation bullets order initial boot/IDE, then virtual environment with required packages, then run programs.',153:'Two named methods are SD Card Image and NVIDIA SDK Manager, with SD preferred; editor ARM64 .deb and created environment interpreter selection explicitly shown.',154:'Isolation, separate interpreter context, project-specific packages and dependency-conflict avoidance are explicit benefits, not shared automatic upgrades or permanent version freezing.'}.items():
 p=f'sources/previews/lectures/page-{page:04d}.webp';report['revisionSourceVisualChecks'].append({'physicalPage':page,'previewPath':p,'previewSha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),'inspectorId':summary['revisionAuthorId'],'method':'rendered_page','observations':note,'inspectedAt':'2026-10-19T16:24:28+00:00'})
(ROOT/'audits/W01-L04-v2-author-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'total':report['total'],'passed':report['passed'],'independentVerification':False}))
