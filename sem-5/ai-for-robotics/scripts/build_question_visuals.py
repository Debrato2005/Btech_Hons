#!/usr/bin/env python3
"""Non-mutating question sidecar producer and exact-source PNG crop renderer.
Never writes bank questions, reviews, or answer/source content. Crop records contain
PDF-point rectangles, lossless renderer settings and both source/pixel SHA-256.
"""
import argparse,datetime,hashlib,json,sys
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash,canonical_json
AUTHOR='bind_required_question_figures'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p,d=None):return json.loads((ROOT/p).read_text()) if (ROOT/p).exists() else d
def write(p,v):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');tmp.replace(p)
def load_supplemental():
 proposal=read('audits/question-visuals/late-supplemental-proposal.json',{'inputs':{},'records':{}})
 snippets=[]
 for sid,entry in sorted(proposal['inputs'].items()):
  v=dict(id=sid,**entry)
  assert v['kind'] in ('verbatim_source_code','verbatim_saved_output'),sid
  assert v['language']==('text' if v['kind']=='verbatim_saved_output' else 'python'),sid
  assert v['notebookRepresentation'] in ('verbatim','output_stripped'),sid
  assert v['upstreamPinStatus'] in ('pinned','commit_only','local_only'),sid
  assert isinstance(v.get('authorId'),str) and v['authorId'].strip(),sid+' missing snippet author'
  if v['upstreamPinStatus']=='commit_only':assert v['upstreamCommit'] and v['upstreamGitBlobSha'] is None and '/blob/'+v['upstreamCommit']+'/' in v['sourceUrl'],sid
  if v['upstreamPinStatus']=='local_only':assert v['upstreamCommit'] is None and v['upstreamGitBlobSha'] is None,sid
  if v['upstreamPinStatus']=='pinned':assert v['upstreamCommit'] and v['upstreamGitBlobSha'],sid
  for pk,hk in [('sourceArtifact','sourceSha256'),('notebookArtifact','notebookSha256')]:
   path=(ROOT/v[pk]).resolve();assert path.is_relative_to(ROOT.resolve()),sid
   assert sha(path)==v[hk],sid+' artifact SHA mismatch'
  nb=read(v['notebookArtifact']);cell=nb['cells'][v['cellIndexZeroBased']]
  assert cell.get('id',cell.get('metadata',{}).get('id'))==v['cellId'],sid+' cell id mismatch'
  if v['notebookRepresentation']=='output_stripped':assert not any(c.get('outputs') for c in nb['cells']),sid
  if v['kind']=='verbatim_saved_output':
   out=cell['outputs'][v['notebookOutputIndex']]
   raw=out['text'] if v['notebookOutputField']=='text' else out['data']['text/plain']
  else:raw=cell['source']
  raw=''.join(raw) if isinstance(raw,list) else raw
  sliced=''.join(raw.splitlines(keepends=True)[v['cellLineStart']-1:v['cellLineEnd']])
  assert sliced==v['text'],sid+' notebook slice mismatch'
  if v['lineStart'] is not None:
   raw=(ROOT/v['sourceArtifact']).read_bytes().decode('utf-8')
   assert ''.join(raw.splitlines(keepends=True)[v['lineStart']-1:v['lineEnd']])==v['text'],sid+' source slice mismatch'
  else:assert v['sourceArtifact']==v['notebookArtifact'],sid
  assert hashlib.sha256(v['text'].encode('utf-8')).hexdigest()==v['textSha256'],sid
  snippets.append(v)
 return snippets,proposal['records']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');args=ap.parse_args()
 bank=read('data/bank.json');rawbank=sha(ROOT/'data/bank.json')
 previousRecords={r['questionId']:r for r in read('data/question-visuals/manifest.json',{}).get('records',[])}
 required={x.strip() for x in (ROOT/'audits/question-visuals/required-manual.txt').read_text().splitlines() if x.strip() and not x.startswith('#')}
 overrides=read('audits/question-visuals/decision-overrides.json',{})
 plans=read('data/question-visuals/crop-plan.json',{})
 refs=read('audits/question-visuals/source-overrides.json',{})
 supplements,supplementRecords=load_supplemental()
 for qid,sr in supplementRecords.items():
  ov=overrides.setdefault(qid,{})
  was_required=ov.get('dependencyStatus', 'required' if qid in required else 'self_contained')=='required'
  prior_inputs=ov.get('requiredInputs',[])
  ov.update(dependencyStatus='required',reason=sr['reason'],requiredInputs=list(dict.fromkeys(prior_inputs+['Exact separately bound notebook premise: '+key for key in sr['proposedInputKeys']])))
  # Pending notebook-only placeholders intentionally have no PDF substitute.
  # Existing required PDF defaults, however, must survive supplemental additions.
  if any(k.startswith('pending-supplemental-') for k in ov.get('cropKeys',[])) or ('cropKeys' not in ov and not was_required):ov['cropKeys']=[]
 sources={s['id']:s for s in bank['sources']};slides={s['id']:s for s in bank['slides']}
 sourceHashes={sid:sha(ROOT/source["localPath"]) for sid,source in sources.items()}
 previousAssets={a['path']:a for a in read('audits/question-visuals/render-cache.json',{}).get('assets',[])}
 previousAssets.update({a['path']:a for a in read('data/question-visuals/manifest.json',{}).get('assets',[])})
 docs={};assets=[];assetByPlan={}
 for key,p in sorted(plans.items()):
  sid=p['sourceId'];page=p['physicalPage'];source=sources[sid]
  assert source['sha256']==sourceHashes[sid],sid
  rect=p['cropRectangle'];assert len(rect)==4 and rect[2]>rect[0] and rect[3]>rect[1]
  dpi=p.get('renderDpi',144);assert dpi>=144
  if sid not in docs:docs[sid]=fitz.open(ROOT/source['localPath'])
  pg=docs[sid][page-1];assert fitz.Rect(rect) in pg.rect
  dest=ROOT/f'assets/question-visuals/{key}.png'
  prior=previousAssets.get(str(dest.relative_to(ROOT)),{})
  dirty=not dest.exists() or any(prior.get(k)!=v for k,v in {'sourceSha256':source['sha256'],'physicalPage':page,'cropRectangle':rect,'renderDpi':dpi}.items())
  if not dirty and prior.get('sha256')!=sha(dest):dirty=True
  if args.render or dirty:
   pix=pg.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),clip=fitz.Rect(rect),alpha=False)
   dest.parent.mkdir(parents=True,exist_ok=True);pix.save(dest)
  from PIL import Image
  with Image.open(dest) as im:w,h=im.size
  hsh=sha(dest);aid='qv-'+hsh[:24]
  asset=dict(id=aid,path=str(dest.relative_to(ROOT)),mimeType='image/png',sha256=hsh,width=w,height=h,sourceId=sid,sourceSha256=source['sha256'],physicalPage=page,slideId=f'{sid}-p{page:04}',cropRectangle=rect,renderDpi=dpi,alt=p['alt'])
  # Byte-identical assets share one id and one metadata record.
  if aid not in {a['id'] for a in assets}:assets.append(asset)
  assetByPlan[key]=aid
 records=[]
 for q in bank['questions']:
  qid=q['id'];isreq=qid in required;ov=overrides.get(qid,{})
  if 'dependencyStatus' in ov:isreq=ov['dependencyStatus']=='required'
  defaultrefs=[dict(sourceId=c['sourceId'],sourceSha256=c['sourceSha256'],physicalPage=c['physicalPage'],slideId=c['slideId']) for c in q['citations']]
  actualrefs=[]
  for ref in refs.get(qid,defaultrefs):
   if isinstance(ref,int):ref=dict(sourceId='lectures',physicalPage=ref)
   ref={**ref,'sourceSha256':sources[ref['sourceId']]['sha256'],'slideId':f'{ref["sourceId"]}-p{ref["physicalPage"]:04}'}
   if ref not in actualrefs:actualrefs.append(ref)
  keys=ov.get('cropKeys',[]) if isreq else []
  if isreq and 'cropKeys' not in ov:
   keys=[f'{x["sourceId"]}-p{x["physicalPage"]:04}' for x in actualrefs if f'{x["sourceId"]}-p{x["physicalPage"]:04}' in assetByPlan]
  unknown_keys=[k for k in keys if k not in assetByPlan]
  assert not unknown_keys,qid+' names missing required crop plans: '+', '.join(unknown_keys)
  reason=ov.get('reason')
  if not reason:
   if isreq:reason='The question refers to a particular source '+('code or output instance' if q['type'] in ('code','code_output','code-numerical','algorithm_trace') else 'diagram, table, model, or displayed instance')+' whose required labels, structure, or input values are not completely specified by the stem, options, and assumptions.'
   elif q.get('assumptions'):reason='The stem, options, and explicit assumptions supply the instance-specific givens needed to answer; the cited visual is evidence or illustration, not an additional input. Assumptions inspected: '+'; '.join(q['assumptions'])
   else:reason='This is a conceptual/recall item, or all instance-specific data needed to choose among the options is already stated. Its source citation is supporting evidence, not an unsupplied visual/code/table input.'
  record=dict(id='QV-'+qid,version=1,authorId=AUTHOR,questionId=qid,questionVersion=q['version'],questionSha256=question_hash(q),dependencyStatus='required' if isreq else 'self_contained',reason=reason,assetIds=list(dict.fromkeys(assetByPlan[k] for k in keys if k in assetByPlan)),requiredInputs=ov.get('requiredInputs',[q.get('subtopic') or q.get('topic') or 'Exact source stimulus'] if isreq else []),sourceRefs=actualrefs)
  if qid in supplementRecords:
   record['supplementalInputIds']=supplementRecords[qid]['proposedInputKeys']
   if any(x['kind']=='verbatim_saved_output' and x['id'] in record['supplementalInputIds'] for x in supplements):record['savedOutputUse']='explicit_output_reading'
  # A byte-identical crop can deduplicate across distinct source pages. Bind the
  # canonical asset's actual origin as an explicit premise ref for review.
  byid={a['id']:a for a in assets}
  for aid in record['assetIds']:
   a=byid[aid];aref={k:a[k] for k in ('sourceId','sourceSha256','physicalPage','slideId')}
   if aref not in record['sourceRefs']:record['sourceRefs'].append(aref)
  records.append(record)
 write('audits/question-visuals/render-cache.json',{'assets':assets})
 used_assets={aid for record in records for aid in record['assetIds']}
 unused_assets=[asset for asset in assets if asset['id'] not in used_assets]
 assets=[asset for asset in assets if asset['id'] in used_assets]
 write('audits/question-visuals/unreferenced-crops-not-packaged.json',{'reason':'Not bound as required input by any current question record. Original files retained; not embedded in delivery.','assets':unused_assets})
 manifest=dict(schemaVersion='1.0.0',authorId=AUTHOR,sourceVersions={s['id']:s['sha256'] for s in bank['sources']},records=records,assets=assets,supplementalInputs=supplements)
 write('data/question-visuals/manifest.json',manifest)
 write('audits/question-visuals/build-receipt.json',dict(builtAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),bankSha256=rawbank,questionCount=len(records),changedQuestionRecordIds=[r['questionId'] for r in records if previousRecords.get(r['questionId'])!=r],requiredQuestionCount=sum(r['dependencyStatus']=='required' for r in records),selfContainedCount=sum(r['dependencyStatus']=='self_contained' for r in records),assets=len(assets),unreferencedAssetsNotPackaged=len(unused_assets),assetBytes=sum((ROOT/a['path']).stat().st_size for a in assets),missingRequiredAssets=[r['questionId'] for r in records if r['dependencyStatus']=='required' and not r['assetIds'] and not r.get('supplementalInputIds')],supplementalInputCount=len(supplements),supplementalQuestionCount=len(supplementRecords),manifestSha256=sha(ROOT/'data/question-visuals/manifest.json'),authorReviewOnly=True))
 assert rawbank==sha(ROOT/'data/bank.json'),'Bank mutated unexpectedly'
 print(json.dumps({k:v for k,v in read('audits/question-visuals/build-receipt.json').items() if k!='missingRequiredAssets'},indent=2))
if __name__=='__main__':main()
