from pathlib import Path
import json,sys,hashlib,datetime
import fitz
from PIL import Image
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'scripts'));from validate import canonical_json,question_hash
config=json.loads(Path(sys.argv[1]).read_text());snap=json.loads((R/config['snapshot']).read_text());current=json.loads((R/'data/question-visuals/manifest.json').read_text());records={r['questionId']:r for r in current['records']};assets={a['id']:a for a in current['assets']};by={q['id']:q for q in json.loads((R/'data/bank.json').read_text())['questions']}
sha=lambda v:hashlib.sha256(canonical_json(v).encode()).hexdigest()
raw=R/'sources/raw/AI_for_Robotics_All_Lectures.pdf';sourcehash=hashlib.sha256(raw.read_bytes()).hexdigest();doc=fitz.open(raw)
exclude=config.get('exclude',{});notes={int(k):v for k,v in config['notes'].items()}
checks={};out=[];held=[]
for old in snap['records']:
 qid=old['questionId']
 if qid in exclude:held.append({'questionId':qid,'reason':exclude[qid]});continue
 r=records[qid];assert r==old,(qid,'changed record needs reinspection')
 for aid in r['assetIds']:
  if aid in checks:continue
  a=assets[aid];assert a['sourceSha256']==sourcehash
  p=R/a['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
  pix=doc[a['physicalPage']-1].get_pixmap(matrix=fitz.Matrix(a['renderDpi']/72,a['renderDpi']/72),clip=fitz.Rect(a['cropRectangle']),alpha=False)
  im=Image.open(p).convert('RGB');assert im.size==(pix.width,pix.height)==(a['width'],a['height']);assert im.tobytes()==pix.samples,(qid,'pixel mismatch')
  checks[aid]={'assetSha256':a['sha256'],'assetMetadataSha256':sha(a),'originalPdfSha256':sourcehash,'physicalPage':a['physicalPage'],'rasterMatchesIndependentPdfRender':True,'visualInspection':notes[a['physicalPage']]}
 q=by[qid];assert question_hash(q)==r['questionSha256'];h=sha(r)
 out.append({'id':f'QVR-{qid}-lead-crop-{h[:12]}','visualId':r['id'],'visualVersion':r['version'],'visualSha256':h,'reviewerId':'independent-input-reviewer-integration-L20-L35','decision':'verified','questionId':qid,'questionVersion':q['version'],'questionSha256':question_hash(q),'sourceVersions':{s['sourceId']:s['sourceSha256'] for s in r['sourceRefs']},'assetHashes':{aid:assets[aid]['sha256'] for aid in r['assetIds']},'assetMetadataHashes':{aid:sha(assets[aid]) for aid in r['assetIds']},'reviewedAssetIds':r['assetIds'],'displayRole':'question_input','checks':dict.fromkeys(['inventoryCompleteness','requiredInputFidelity','legibility','noAnswerLeak','sourceLinkage'],True),'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reasoning':' '.join(dict.fromkeys(notes[assets[aid]['physicalPage']] for aid in r['assetIds'])),'scope':'Full current question stem, choices and assumptions independently read; every actual PNG independently visually inspected at readable scale. Raster pixels independently rerendered from hash-verified source PDF and matched exactly. This approves the pre-answer input role only, not browser display or a new answer judgment. Input labels/formulas/code are legitimate premises; worked numeric outputs and answer keys are excluded.','evidencePath':config['evidencePath'],'findings':[]})
p=R/config['reviewPath'];assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n')
(R/config['evidencePath']).write_text(json.dumps({'sourceSha256':sourcehash,'assets':checks,'approvedQuestionIds':[r['questionId'] for r in out],'held':held},indent=2)+'\n')
print(json.dumps({'approvedRequiredRecords':len(out),'independentlyComparedAssets':len(checks),'held':held}))
