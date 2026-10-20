"""Only for explicitly inspected, frozen question/PNG batches; never auto-approves unseen pixels."""
from pathlib import Path
import json,sys,hashlib,datetime
import fitz
from PIL import Image
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'scripts'));from validate import canonical_json,question_hash
c=json.loads(Path(sys.argv[1]).read_text());s=json.loads((R/c['snapshot']).read_text());m=json.loads((R/'data/question-visuals/manifest.json').read_text());rs={r['questionId']:r for r in m['records']};old={r['questionId']:r for r in s['records']};aa={a['id']:a for a in m['assets']};oa={a['id']:a for a in s['assets']};qs={q['id']:q for q in json.loads((R/'data/bank.json').read_text())['questions']}
sha=lambda x:hashlib.sha256(canonical_json(x).encode()).hexdigest();raw=R/'sources/raw/AI_for_Robotics_All_Lectures.pdf';sourcehash=hashlib.sha256(raw.read_bytes()).hexdigest();doc=fitz.open(raw);checked={};reviews=[]
for qid,reason in c['approved'].items():
 r=rs[qid];assert r==old[qid],(qid,'changed record needs reinspection');assert r['dependencyStatus']=='required' and r['assetIds'];assert not r.get('supplementalInputIds'),(qid,'supplemental review separately owned')
 q=qs[qid];assert question_hash(q)==r['questionSha256']
 for aid in r['assetIds']:
  a=aa[aid];assert a==oa[aid],(aid,'metadata changed');assert a['sourceSha256']==sourcehash
  if aid in checked:continue
  note=c['assetNotes'][a['path']];p=R/a['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'];pix=doc[a['physicalPage']-1].get_pixmap(matrix=fitz.Matrix(a['renderDpi']/72,a['renderDpi']/72),clip=fitz.Rect(a['cropRectangle']),alpha=False);im=Image.open(p).convert('RGB');assert im.size==(pix.width,pix.height)==(a['width'],a['height']);assert im.tobytes()==pix.samples,(aid,'independent pixels mismatch');checked[aid]={'assetSha256':a['sha256'],'assetMetadataSha256':sha(a),'sourceSha256':sourcehash,'physicalPage':a['physicalPage'],'cropRectangle':a['cropRectangle'],'renderDpi':a['renderDpi'],'rasterMatchesIndependentOriginalPdfRender':True,'visualInspection':note}
 h=sha(r);reviews.append({'id':f'QVR-{qid}-later-pixels-{h[:12]}','visualId':r['id'],'visualVersion':r['version'],'visualSha256':h,'reviewerId':'independent-later-input-reviewer-L36-L60','decision':'verified','questionId':qid,'questionVersion':q['version'],'questionSha256':question_hash(q),'sourceVersions':{x['sourceId']:x['sourceSha256'] for x in r['sourceRefs']},'assetHashes':{a:aa[a]['sha256'] for a in r['assetIds']},'assetMetadataHashes':{a:sha(aa[a]) for a in r['assetIds']},'reviewedAssetIds':r['assetIds'],'displayRole':'question_input','checks':dict.fromkeys(['inventoryCompleteness','requiredInputFidelity','legibility','noAnswerLeak','sourceLinkage'],True),'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reasoning':reason,'scope':'Full current stem/options/assumptions and every actual PNG read independently. Each PNG independently rerendered from hash-verified original PDF and pixel-compared exactly. This approves question-input presentation only, not answers, supplemental snippets or browser rendering. Source outputs are permitted only when the question explicitly asks to read/compare those outputs; not as replacement premises for a computation.','evidencePath':c['evidencePath'],'findings':[]})
for path,value in [(c['reviewPath'],reviews),(c['evidencePath'],{'sourceSha256':sourcehash,'assets':checked,'approvedQuestionIds':list(c['approved']),'held':c.get('held',{})})]:
 p=R/path;assert not p.exists();p.write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps({'approvedRequiredRecords':len(reviews),'independentlyComparedAssets':len(checked),'held':c.get('held',{})}))
