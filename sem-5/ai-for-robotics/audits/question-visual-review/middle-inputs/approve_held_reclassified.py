"""One-off review of eleven read, previously held records, now inspected empty."""
from pathlib import Path
import json,sys,hashlib,datetime
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,canonical_json
from question_visuals import source_ref_valid
D=Path(__file__).resolve().parent
ids=['W06-L29-Q011','W06-L29-Q015','W06-L30-Q003','W07-L31-P0926-Q02','W07-L31-P0932-Q01','W07-L31-P0934-Q01','W07-L31-P0935-Q01','W07-L31-P0936-Q01','W07-L31-P0939-Q01','W07-L31-P0939-Q02','W07-L31-P0947-Q05']
b=json.loads((R/'data/bank.json').read_text());m=json.loads((R/'data/question-visuals/manifest.json').read_text());qs={q['id']:q for q in b['questions']};records={r['questionId']:r for r in m['records']};sources={s['id']:s for s in b['sources']};slides={s['id']:s for s in b['slides']}
tri={r['questionId']:r for p in D.glob('L*-input-triage.json') for r in json.loads(p.read_text())['questions']}
reviews=[];snapshot=[];now=datetime.datetime.now(datetime.timezone.utc).isoformat()
existing=[r for p in (R/'data/question-visuals/reviews').glob('*.json') for r in (json.loads(p.read_text()) if isinstance(json.loads(p.read_text()),list) else [])]
for qid in ids:
 q=qs[qid];r=records[qid];t=tri[qid]
 assert t['decision']=='self_contained' and q['status']=='verified'
 assert question_hash(q)==r['questionSha256']==t['questionSha256'] and r['questionVersion']==q['version']
 assert r['dependencyStatus']=='self_contained' and r['assetIds']==[] and r['requiredInputs']==[]
 assert all(source_ref_valid(ref,sources,slides) for ref in r['sourceRefs'])
 assert not any(v['questionId']==qid and v['reviewerId']=='independent-input-reviewer-middle-L27-L35' for v in existing)
 digest=hashlib.sha256(canonical_json(r).encode()).hexdigest();snapshot.append(r)
 reviews.append({'id':f"QVR-{qid}-v{r['version']}-middle-reclassified-1",'visualId':r['id'],'visualVersion':r['version'],'visualSha256':digest,'reviewerId':'independent-input-reviewer-middle-L27-L35','decision':'verified','questionId':qid,'questionVersion':q['version'],'questionSha256':t['questionSha256'],'sourceVersions':{s['sourceId']:s['sourceSha256'] for s in r['sourceRefs']},'assetHashes':{},'assetMetadataHashes':{},'reviewedAssetIds':[],'displayRole':'question_input','checks':{'inventoryCompleteness':True,'requiredInputFidelity':True,'legibility':True,'noAnswerLeak':True,'sourceLinkage':True},'reviewedAt':now,'reasoning':t['reason'],'scope':'This previously held record has now been explicitly inspected after producer reclassification. Its unchanged question was fully read earlier and remains bound to the initial question snapshot. Current source refs are valid and its required-input/asset arrays are empty. No positive image is approved: pixel fidelity, legibility and image answer-leak checks are nonapplicable. This is a first independent approval, not an automatic stale-approval refresh.','evidencePath':'audits/question-visual-review/middle-inputs/reclassified-records-1.json','findings':[]})
out=R/'data/question-visuals/reviews/L27-L35-middle-reclassified-1.json';evidence=D/'reclassified-records-1.json';assert not out.exists() and not evidence.exists();evidence.write_text(json.dumps({'reviewedAt':now,'records':snapshot},indent=2)+'\n');out.write_text(json.dumps(reviews,indent=2)+'\n');print('First approvals for newly inspected empty records:',len(reviews))
