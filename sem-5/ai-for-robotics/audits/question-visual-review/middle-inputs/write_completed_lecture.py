"""Emit reviews only for a lecture whose complete text has been independently read.

The manual decision files are authored after reading all stems/options/assumptions.
Question hashes are pinned to the initial reading snapshot, not refreshed on change.
No source, question, manifest or asset producer data is edited here.
"""
from pathlib import Path
import sys,json,hashlib,datetime
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,canonical_json
from question_visuals import source_ref_valid
D=Path(__file__).resolve().parent
lecture=sys.argv[1];manual=json.loads((D/f'{lecture}-manual-decisions.json').read_text())
assert manual['readAllStemsOptionsAndAssumptions'] is True
snapshot=json.loads((D/'question-read-snapshot.json').read_text())
rows=[x for x in snapshot['questions'] if x['question']['lectureId']==lecture]
assert len(rows)==manual['expectedQuestionCount']
b=json.loads((R/'data/bank.json').read_text());m=json.loads((R/'data/question-visuals/manifest.json').read_text())
qs={q['id']:q for q in b['questions']};rs={r['questionId']:r for r in m['records']};sources={s['id']:s for s in b['sources']};slides={s['id']:s for s in b['slides']}
assert set(manual['required']) <= {x['questionId'] for x in rows}
assert set(manual.get('specificSelfContainedReasons',{})) <= {x['questionId'] for x in rows}
now=datetime.datetime.now(datetime.timezone.utc).isoformat();triage=[];reviews=[];held=[]
for x in rows:
 qid=x['questionId'];q=qs[qid];r=rs[qid];assert q['status']=='verified' and question_hash(q)==x['questionSha256']==r['questionSha256'],f'Stale question {qid}'
 required=qid in manual['required'];reason=manual['required'].get(qid) if required else manual.get('specificSelfContainedReasons',{}).get(qid,manual['selfContainedReason'])
 row={'questionId':qid,'questionVersion':q['version'],'questionSha256':x['questionSha256'],'decision':'required' if required else 'self_contained','reason':reason,'currentVisualId':r['id'],'currentVisualVersion':r['version'],'currentVisualSha256':hashlib.sha256(canonical_json(r).encode()).hexdigest(),'currentDependencyStatus':r['dependencyStatus']};triage.append(row)
 if required:continue
 if r['dependencyStatus']!='self_contained' or r['assetIds'] or r['requiredInputs']:
  held.append(qid);continue
 assert r['questionVersion']==q['version']
 assert r['sourceRefs'] and all(source_ref_valid(ref,sources,slides) for ref in r['sourceRefs'])
 assert {(ref['sourceId'],ref['sourceSha256']) for ref in r['sourceRefs']} <= {(ref['sourceId'],ref['sourceSha256']) for ref in q['citations']}
 for ref in r['sourceRefs']:assert m['sourceVersions'][ref['sourceId']]==ref['sourceSha256']
 reviews.append({'id':f"QVR-{qid}-v{r['version']}-middle-input",'visualId':r['id'],'visualVersion':r['version'],'visualSha256':row['currentVisualSha256'],'reviewerId':'independent-input-reviewer-middle-L27-L35','decision':'verified','questionId':qid,'questionVersion':q['version'],'questionSha256':x['questionSha256'],'sourceVersions':{s['sourceId']:s['sourceSha256'] for s in r['sourceRefs']},'assetHashes':{},'assetMetadataHashes':{},'reviewedAssetIds':[],'displayRole':'question_input','checks':{'inventoryCompleteness':True,'requiredInputFidelity':True,'legibility':True,'noAnswerLeak':True,'sourceLinkage':True},'reviewedAt':now,'reasoning':reason,'scope':'Independent standalone-input completeness review of the full current stem, every option and every assumption. This exact manifest record contains no required inputs and no assets; image fidelity, image legibility and image answer-leak checks are nonapplicable. This does not approve any positive visual asset or replace answer verification. Question hash is pinned to the original reading snapshot; source refs were checked against the current source and slide ledger.','evidencePath':f'audits/question-visual-review/middle-inputs/{lecture}-input-triage.json','findings':[]})
triage_path=D/f'{lecture}-input-triage.json';review_path=R/f'data/question-visuals/reviews/{lecture}-middle-self-contained.json'
assert not triage_path.exists() and not review_path.exists(),'Never auto-refresh an existing review.'
triage_path.write_text(json.dumps({'reviewerId':'review_middle_question_inputs','reviewedAt':now,'lectureId':lecture,'questionsRead':len(rows),'questions':triage,'heldSelfContainedManifestConflicts':held},indent=2)+'\n')
review_path.write_text(json.dumps(reviews,indent=2)+'\n')
print(json.dumps({'lecture':lecture,'read':len(rows),'required':sum(r['decision']=='required' for r in triage),'selfContainedApprovals':len(reviews),'held':held}))
