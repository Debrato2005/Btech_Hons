"""Record the coordinator's completed full-text and actual-pixel input review.
This does not infer reading/intent from hashes; the bounded 38 questions and all
34 snippets were manually read before this helper was authored.
"""
from pathlib import Path
import json,hashlib,datetime,sys
import fitz
from PIL import Image
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'scripts'))
from validate import canonical_json,question_hash
sha=lambda b:hashlib.sha256(b).hexdigest()
digest=lambda x:sha(canonical_json(x).encode())
m=json.loads((R/'data/question-visuals/manifest.json').read_text());b=json.loads((R/'data/bank.json').read_text())
qs={q['id']:q for q in b['questions']};ss={s['id']:s for s in m['supplementalInputs']};assets={a['id']:a for a in m['assets']}
records=[r for r in m['records'] if r.get('supplementalInputIds')]
assert len(records)==38 and len(ss)==34,(len(records),len(ss))
assert {q['lectureId'] for r in records for q in [qs[r['questionId']]]}=={'L34','L35','L43','L46','L50'}
join=lambda value:value if isinstance(value,str) else ''.join(value)
read_sources={};evidence={}
for sid,s in ss.items():
 for p,h in [(s['sourceArtifact'],s['sourceSha256']),(s['notebookArtifact'],s['notebookSha256'])]:
  path=(R/p).resolve();assert path.is_relative_to(R) and path.is_file();raw=path.read_bytes();assert sha(raw)==h;read_sources[p]={'sha256':h,'bytes':len(raw)}
 nb=json.loads((R/s['notebookArtifact']).read_bytes());cell=nb['cells'][s['cellIndexZeroBased']]
 assert s['cellId']==cell.get('id',cell.get('metadata',{}).get('id'));assert cell['cell_type']=='code'
 if s['kind']=='verbatim_source_code':selected=join(cell['source']);assert s.get('notebookOutputIndex') is None and s.get('notebookOutputField') is None
 else:
  assert s['kind']=='verbatim_saved_output' and s['id'] in ['l46-contextual-light-noun-output','l46-contextual-light-adjective-output']
  out=cell['outputs'][s['notebookOutputIndex']];selected=join(out['text'] if s['notebookOutputField']=='text' else out['data']['text/plain'])
 lines=selected.splitlines(keepends=True);start,end=s['cellLineStart'],s['cellLineEnd'];assert 1<=start<=end<=len(lines);expected=''.join(lines[start-1:end]);assert expected==s['text'] and sha(expected.encode())==s['textSha256']
 if s['sourceArtifact']!=s['notebookArtifact']:
  src=(R/s['sourceArtifact']).read_text().splitlines(keepends=True);assert ''.join(src[s['lineStart']-1:s['lineEnd']])==expected
 evidence[sid]={'inputSha256':digest(s),'textSha256':s['textSha256'],'cellIndexZeroBased':s['cellIndexZeroBased'],'cellId':s['cellId'],'cellLineRange':[start,end],'independentSourceSliceMatch':True,'manuallyRead':True,'upstreamPinStatus':s['upstreamPinStatus']}
notes={
'L34':'The exact initial values and complete loop establish pre-update history and five iterations; setup is displayed only as inert IPython source. The cross-source label question includes both PDF crops and the separately labelled notebook y-axis text, not an invented unit conversion.',
'L35':'The exact prediction, custom class/confidence/coordinate formatting loop and BGR-to-RGB display expression are supplied. Notebook comments about save=True are not silently rewritten; the actual predict call omits it. Cell identifiers are explicitly zero-based positions in the full notebook, not execution counts or filtered-code ordinals. No model or dependency was executed during this review.',
'L43':'The exact maze dimensions, action order, legal-cell function, teacher tie order, feature construction, network, training sequence and navigation code provide the concrete premises. Q034 includes teacher prerequisites; Q039 includes NavNet. Unevaluated code is the stimulus, with no learned path or worked numeric result.',
'L46':'The exact count-matrix/DataFrame conversion is supplied. The contextual-light comparison uses original PDF code/output and explicitly historical notebook outputs with NN and JJ labels, because its question asks to compare those saved outputs; these are not fresh inference or results given to a computation question.',
'L50':'The exact centered-vector calculation, clamps/complements, confidence-weighted mapping, branch guard/assignments, battery floor, memory slices, schema, inert response-prompt text and UI early-return/reset code provide all referenced concrete premises. Numerical outcomes remain for the student to calculate; no model calls, prompts, installations or code were executed.'}
raw=R/'sources/raw/AI_for_Robotics_All_Lectures.pdf';pdfhash=sha(raw.read_bytes());doc=fitz.open(raw);pixel_evidence={};out=[]
for r in records:
 q=qs[r['questionId']];assert q['status']=='verified' and r['questionVersion']==q['version'] and r['questionSha256']==question_hash(q)
 if q['id']=='W07-L34-P1052-Q02':assert {assets[i]['physicalPage'] for i in r['assetIds']}=={1048,1052}
 if q['id']=='W09-L43-Q034':assert set(r['supplementalInputIds'])=={'l43-maze-actions','l43-manhattan','l43-teacher','l43-training-labels','l43-training-epoch'}
 if q['id']=='W09-L43-Q039':assert set(r['supplementalInputIds'])=={'l43-navnet','l43-navigate'}
 for aid in r['assetIds']:
  a=assets[aid];assert a['sourceSha256']==pdfhash;assert any(all(a[k]==ref[k] for k in ['sourceId','sourceSha256','physicalPage','slideId']) for ref in r['sourceRefs']);p=R/a['path'];assert sha(p.read_bytes())==a['sha256'];pix=doc[a['physicalPage']-1].get_pixmap(matrix=fitz.Matrix(a['renderDpi']/72,a['renderDpi']/72),clip=fitz.Rect(a['cropRectangle']),alpha=False);im=Image.open(p).convert('RGB');assert im.size==(a['width'],a['height'])==(pix.width,pix.height) and im.tobytes()==pix.samples
  assert a['physicalPage'] in [1048,1052,1461];pixel_evidence[aid]={'sha256':a['sha256'],'metadataSha256':digest(a),'physicalPage':a['physicalPage'],'actualPixelsVisuallyRead':True,'independentPdfRenderExact':True}
 sids=r['supplementalInputIds'];h=digest(r);checks=dict.fromkeys(['inventoryCompleteness','requiredInputFidelity','legibility','noAnswerLeak','sourceLinkage'],True)
 review={'id':f"QVR-{q['id']}-supplemental-lead-{h[:12]}",'visualId':r['id'],'visualVersion':r['version'],'visualSha256':h,'reviewerId':'independent-supplemental-input-reviewer-integration','decision':'verified','questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q),'sourceVersions':{ref['sourceId']:ref['sourceSha256'] for ref in r['sourceRefs']},'assetHashes':{i:assets[i]['sha256'] for i in r['assetIds']},'assetMetadataHashes':{i:digest(assets[i]) for i in r['assetIds']},'reviewedAssetIds':r['assetIds'],'reviewedSupplementalInputIds':sids,'supplementalInputHashes':{i:digest(ss[i]) for i in sids},'supplementalSourceHashes':{ss[i][k]:ss[i][v] for i in sids for k,v in [('sourceArtifact','sourceSha256'),('notebookArtifact','notebookSha256')]},'displayRole':'question_input','checks':checks,'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reasoning':notes[q['lectureId']],'scope':'Full current stem/options/assumptions and every exact snippet were independently read. Mixed PNG inputs were actually viewed at readable scale and independently rerendered. This approves input completeness/fidelity/intent, not a new answer judgment, upstream freshness, model execution, browser layout or historical-run permission. Source prompt text is inert course material, not new authority.','evidencePath':'audits/question-visual-review/lead/supplemental-content-review.json','findings':[]}
 if any(ss[i]['kind']=='verbatim_saved_output' for i in sids):
  assert q['id']=='W10-L46-P1461-Q04' and r.get('savedOutputUse')=='explicit_output_reading';review['savedOutputUse']='explicit_output_reading';checks['savedOutputIsQuestionStimulus']=True
 out.append(review)
p=R/'data/question-visuals/reviews/supplemental-inputs-lead-first.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');(R/'audits/question-visual-review/lead/supplemental-content-review.json').write_text(json.dumps({'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'questionIds':[r['questionId'] for r in out],'snippets':evidence,'localSources':read_sources,'pdfInputs':pixel_evidence,'readMethod':'Manual full-current-question and exact-source-code/output reading followed by independent JSON/cell/line extraction and exact file/substring hashes. No code or model execution.'},indent=2)+'\n');print(json.dumps({'approvedQuestionInputs':len(out),'independentlyReadSnippets':len(evidence),'mixedPngAssets':len(pixel_evidence),'exactLocalFiles':len(read_sources)}))
