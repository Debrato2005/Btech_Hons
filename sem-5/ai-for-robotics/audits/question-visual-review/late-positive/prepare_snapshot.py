from pathlib import Path
import json,sys,hashlib,datetime
import fitz
from PIL import Image
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'scripts'));from validate import canonical_json,question_hash
out=R/'audits/question-visual-review/late-positive';m=json.loads((R/'data/question-visuals/manifest.json').read_text());b=json.loads((R/'data/bank.json').read_text());by={q['id']:q for q in b['questions']};assets={a['id']:a for a in m['assets']};rr=[r for r in m['records'] if by[r['questionId']].get('lectureId') in [f'L{x}' for x in range(36,49)] and r['dependencyStatus']=='required'];rr=[r for r in rr if len(sys.argv)<3 or r['questionId'] in sys.argv[2].split(',')];doc=fitz.open(R/'sources/raw/AI_for_Robotics_All_Lectures.pdf');sh=hashlib.sha256((R/'sources/raw/AI_for_Robotics_All_Lectures.pdf').read_bytes()).hexdigest();checks={};findings=[]
for r in rr:
 q=by[r['questionId']]
 if question_hash(q)!=r['questionSha256']:findings.append([r['questionId'],'stale question binding'])
 refs={(s['sourceId'],s['physicalPage']) for s in r['sourceRefs']}
 for aid in r['assetIds']:
  a=assets[aid]
  if (a['sourceId'],a['physicalPage']) not in refs:findings.append([r['questionId'],'asset not sourceRefs member',aid])
  if aid in checks:continue
  assert sh==a['sourceSha256'];assert hashlib.sha256((R/a['path']).read_bytes()).hexdigest()==a['sha256'];im=Image.open(R/a['path']).convert('RGB');pix=doc[a['physicalPage']-1].get_pixmap(matrix=fitz.Matrix(a['renderDpi']/72,a['renderDpi']/72),clip=fitz.Rect(a['cropRectangle']),alpha=False);assert im.size==(pix.width,pix.height)==(a['width'],a['height']);assert im.tobytes()==pix.samples
  checks[aid]={'originalPdfSha256':sh,'assetSha256':a['sha256'],'assetMetadataSha256':hashlib.sha256(canonical_json(a).encode()).hexdigest(),'exactIndependentRenderMatches':True,'dimensions':[pix.width,pix.height]}
snap={'snapshotAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':rr,'questions':[by[r['questionId']] for r in rr],'assets':[assets[a] for a in checks],'independentPixelComparisons':checks,'structuralFindings':findings};p=out/(sys.argv[1] if len(sys.argv)>1 else 'snapshot-initial.json');assert not p.exists();p.write_text(json.dumps(snap,indent=2)+'\n')
for l in range(36,49):
 rr1=[r for r in rr if by[r['questionId']]['lectureId']==f'L{l}'];print(f'L{l}: {len(rr1)} required, {sum(bool(r.get("supplementalInputIds")) for r in rr1)} mixed; '+', '.join(str(x) for x in sorted(set(assets[a]['physicalPage'] for r in rr1 for a in r['assetIds']))))
print('Checked assets',len(checks),'structural findings',findings)
