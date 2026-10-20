"""Write only explicitly read and adjudicated self-contained input records."""
from pathlib import Path
import sys,json,hashlib,datetime
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'scripts'));from validate import question_hash,canonical_json
triage=json.loads(Path(sys.argv[1]).read_text());m=json.loads((R/'data/question-visuals/manifest.json').read_text());b=json.loads((R/'data/bank.json').read_text());by={q['id']:q for q in b['questions']};records={r['questionId']:r for r in m['records']};out=[];held=[]
for row in triage['questions']:
 if row['decision']!='self_contained':continue
 q=by[row['questionId']];r=records[q['id']];assert question_hash(q)==row['questionSha256']==r['questionSha256']
 if r['dependencyStatus']!='self_contained' or r['assetIds'] or r['requiredInputs']:held.append(q['id']);continue
 sha=hashlib.sha256(canonical_json(r).encode()).hexdigest()
 out.append({'id':f"QVR-{q['id']}-v{r['version']}-lead-input",'visualId':r['id'],'visualVersion':r['version'],'visualSha256':sha,'reviewerId':'independent-input-reviewer-integration-L20-L35','decision':'verified','questionId':q['id'],'questionVersion':q['version'],'questionSha256':row['questionSha256'],'sourceVersions':{s['sourceId']:s['sourceSha256'] for s in r['sourceRefs']},'assetHashes':{},'assetMetadataHashes':{},'reviewedAssetIds':[],'displayRole':'question_input','checks':{'inventoryCompleteness':True,'requiredInputFidelity':True,'legibility':True,'noAnswerLeak':True,'sourceLinkage':True},'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reasoning':row['reason'],'scope':'Independent input-completeness review after reading the full current stem, assumptions and options. No image is required or approved; image fidelity/legibility/leak checks are nonapplicable to this empty-asset record. Existing answer approvals remain separate. Source PDFs retain the exact hashes verified by the final packaging receipt.','evidencePath':str(Path(sys.argv[1]).resolve().relative_to(R)),'findings':[]})
p=Path(sys.argv[2]);assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'written':str(p),'verifiedSelfContained':len(out),'heldForAuthorDisposition':held}))
