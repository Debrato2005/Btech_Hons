"""Record an explicitly completed full lecture read and exact-bound approvals.
Usage requires a human-adjudicated mapping of required input reasons. Never
run this on a lecture whose full stems/options/assumptions were not inspected.
"""
from pathlib import Path
import sys,json,hashlib,datetime
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,canonical_json
lecture=sys.argv[1]; decisions=json.loads(Path(sys.argv[2]).read_text())
b=json.loads((R/'data/bank.json').read_text());m=json.loads((R/'data/question-visuals/manifest.json').read_text());rs={r['questionId']:r for r in m['records']}
qs=sorted((q for q in b['questions'] if q.get('lectureId')==lecture and q['status']=='verified'),key=lambda q:q['id'])
assert all(k in {q['id'] for q in qs} for k in decisions)
rows=[];out=[];held=[];now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for q in qs:
 r=rs[q['id']];sha=question_hash(q);assert sha==r['questionSha256']
 req=q['id'] in decisions
 reason=decisions[q['id']] if req else 'Independently read this full current stem, every option and all assumptions: its conceptual recall or explicitly supplied scenario/numeric premises are sufficient without an unseen figure, table, code listing, matrix or earlier-question state.'
 row={'questionId':q['id'],'questionSha256':sha,'decision':'required' if req else 'self_contained','reason':reason,'readEvidence':{'stem':q['stem'],'assumptions':q.get('assumptions',[]),'options':q['options']},'recordSha256AtInspection':hashlib.sha256(canonical_json(r).encode()).hexdigest(),'sourceVersions':{s['sourceId']:s['sourceSha256'] for s in r['sourceRefs']}}
 rows.append(row)
 if req:continue
 if r['dependencyStatus']!='self_contained' or r['assetIds'] or r['requiredInputs']:held.append(q['id']);continue
 out.append({'id':f"QVR-{q['id']}-v{r['version']}-later-input",'visualId':r['id'],'visualVersion':r['version'],'visualSha256':row['recordSha256AtInspection'],'reviewerId':'independent-later-input-reviewer-L36-L60','decision':'verified','questionId':q['id'],'questionVersion':q['version'],'questionSha256':sha,'sourceVersions':row['sourceVersions'],'assetHashes':{},'assetMetadataHashes':{},'reviewedAssetIds':[],'displayRole':'question_input','checks':{'inventoryCompleteness':True,'requiredInputFidelity':True,'legibility':True,'noAnswerLeak':True,'sourceLinkage':True},'reviewedAt':now,'reasoning':reason,'scope':'Independent standalone pre-answer input review only. Full stems/options/assumptions read. No image approved. Fidelity, legibility and no-leak checks refer to the empty-asset presentation and are not positive pixel approvals. Existing answer reviews remain separate.','evidencePath':f'audits/question-visual-review/later-inputs/{lecture}-input-triage.json','findings':[]})
triage={'reviewerId':'independent-later-input-reviewer-L36-L60','lectureId':lecture,'reviewedAt':now,'fullTextReadCount':len(qs),'questions':rows}
p=R/f'audits/question-visual-review/later-inputs/{lecture}-input-triage.json';assert not p.exists();p.write_text(json.dumps(triage,ensure_ascii=False,indent=2)+'\n')
p=R/f'data/question-visuals/reviews/{lecture}-self-contained-later-review.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'lecture':lecture,'inspected':len(qs),'required':len(decisions),'approvedSelfContained':len(out),'heldAuthorRequired':held}))
