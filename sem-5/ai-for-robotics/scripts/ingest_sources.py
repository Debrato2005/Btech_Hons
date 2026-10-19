#!/usr/bin/env python3
"""Reproducibly inventory user-supplied PDFs without equating extraction with review.

Retrieve fresh references using connected Drive metadata + fetch(download_raw_file=True,
include_base64=False); pass returned URLs with --lecture-url/--assignment-url. Do not
commit temporary download URLs. Or put the exact source files in sources/raw/.
"""
import argparse, concurrent.futures, datetime, hashlib, json, re, urllib.request
from pathlib import Path
import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'sources'
SPECS = [
 dict(id='lectures', filename='AI_for_Robotics_All_Lectures.pdf', role='lectures', providerFileId='11o0RzXIrDTIbb0FNe1Tl_-cgV4aKVl2m', modifiedTime='2026-10-03T11:34:16.231Z', expectedBytes=64251087),
 dict(id='assignments', filename='AI_for_Robotics_All_Assignment_Solutions.pdf', role='assignment_solutions', providerFileId='16Ybyme8t18KxPRKQYAinJYsidLQyxoDQ', modifiedTime='2026-10-19T12:01:31.514Z', expectedBytes=3507381),
]
WEEK_TITLES=['Introduction of Robotics and Artificial Intelligence','Manipulator Kinematics and Static Forces in Manipulators','Manipulator Dynamics','Trajectory Generation & Manipulator-mechanism Design','Linear and Non-linear Control of Manipulators','Picking Up and Putting Objects Using Reinforcement Learning','Recognizing Objects','Putting Things Away','AI-based navigation','AI Based speech recognition and robot emotion','Robot hardware and Integration of Robotics and AI','Robot demonstration']

def dump(path, obj):
 path.parent.mkdir(parents=True, exist_ok=True)
 path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def printed_number(page, source):
 # Extract only an actual footer glyph, never substitute the physical page.
 footer=page.get_text(clip=fitz.Rect(page.rect.width*.72,page.rect.height*.91,page.rect.width,page.rect.height)).strip()
 if source=='lectures':
  nums=re.findall(r'^\s*(\d+)\s*$',footer,re.M)
 else:
  nums=re.findall(r'\b(\d+)\s*\|\s*P\s*a\s*g\s*e',footer,re.I)
 return (nums[-1],'present') if nums else (None,'unchecked')

def render_batch(job):
 source, filename, indices, scale, quality, force=job
 d=fitz.open(filename);out=SOURCES/'previews'/source;out.mkdir(parents=True,exist_ok=True)
 n=0;total=0
 for i in indices:
  target=out/f'page-{i+1:04d}.webp'
  if force or not target.exists():
   pix=d[i].get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
   Image.frombytes('RGB',[pix.width,pix.height],pix.samples).save(target,'WEBP',quality=quality,method=5)
  n+=1;total+=target.stat().st_size
 return dict(source=source,count=n,bytes=total)

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--lecture-url');ap.add_argument('--assignment-url');ap.add_argument('--render',action='store_true')
 ap.add_argument('--render-scale',type=float,default=2.5);ap.add_argument('--webp-quality',type=int,default=88)
 ap.add_argument('--workers',type=int,default=4);ap.add_argument('--retrieved-at',default='2026-10-19T12:42:08Z')
 args=ap.parse_args()
 for spec,url in zip(SPECS,[args.lecture_url,args.assignment_url]):
  path=SOURCES/'raw'/spec['filename'];path.parent.mkdir(parents=True,exist_ok=True)
  if url:
   tmp=path.with_suffix('.part');urllib.request.urlretrieve(url,tmp)
   if tmp.read_bytes()[:5]!=b'%PDF-':raise ValueError('Download is not a PDF')
   tmp.replace(path)
  if not path.exists():raise FileNotFoundError(f'{path}: retrieve via connected Drive first')
 metadata=[];assets=[];maps={};lectures=[];assignment_starts=[];jobs=[]
 preview_versions_path=SOURCES/'preview_source_versions.json'
 preview_versions=json.loads(preview_versions_path.read_text()) if preview_versions_path.exists() else {}
 for spec in SPECS:
  sid=spec['id'];path=SOURCES/'raw'/spec['filename'];sha=digest(path);doc=fitz.open(path)
  rec={k:spec[k] for k in ['id','filename','role','providerFileId']}
  rec.update(url=f"https://drive.google.com/file/d/{spec['providerFileId']}/view",retrievalStatus='ready',sha256=sha,pageCount=len(doc),version=f"sha256:{sha}",localPath=str(path.relative_to(ROOT)),assetId=f'{sid}-pdf',fileSizeBytes=path.stat().st_size,providerModifiedTime=spec['modifiedTime'],providerVersion=None,retrievedAt=args.retrieved_at)
  metadata.append(rec)
  assets.append(dict(id=f'{sid}-pdf',kind='source_pdf',path=rec['localPath'],mimeType='application/pdf',sha256=sha,alt=f"Complete original {spec['filename']}: {len(doc)} pages",sourceId=sid))
  pages=[]
  textout=SOURCES/'text'/sid;textout.mkdir(parents=True,exist_ok=True)
  for i,page in enumerate(doc):
   text=page.get_text(sort=True);textpath=textout/f'page-{i+1:04d}.txt';textpath.write_text(text)
   lines=[x.strip() for x in text.splitlines() if x.strip()]
   match=re.search(r'Lecture\s+(?:Number\s+)?(\d+)',text[:220],re.I) if sid=='lectures' else None
   if match:
    seq=len(lectures)+1
    lectures.append(dict(id=f'L{seq:02d}',sequence=seq,printedLectureNumber=int(match.group(1)),title=lines[2] if len(lines)>2 else '',startPage=i+1,endPage=None,week=(seq-1)//5+1,boundaryStatus='text_detected_pending_visual_confirmation',titleSlideId=f'lectures-p{i+1:04d}'))
   if sid=='assignments':
    match2=re.search(r'WEEK\s+(\d+)\s*:\s*ASSIGNMENT\s+(\d+)',text,re.I)
    if match2:assignment_starts.append(dict(week=int(match2.group(1)),assignmentNumber=int(match2.group(2)),startPage=i+1,endPage=None,boundaryStatus='text_detected_pending_visual_confirmation'))
   printed,status=printed_number(page,sid)
   title=lines[0] if lines else ''
   pages.append(dict(id=f'{sid}-p{i+1:04d}',sourceId=sid,sourceSha256=sha,physicalPage=i+1,combinedLecturePage=i+1 if sid=='lectures' else None,week=None,lectureId=None,lectureTitle=None,lectureRelativePage=None,printedSlideNumber=printed,printedSlideNumberStatus=status,title=title,text='',disposition='unreviewed',exclusionReason=None,repeatsSlideIds=[],incrementalChangesChecked=False,conceptIds=[],assetId=None,visualInspection=dict(status='pending',inspectorId=None,inspectedAt=None,method=None,notes='Text extracted; page not yet visually inspected for content.'),localTextPath=str(textpath.relative_to(ROOT)),textSha256=hashlib.sha256(text.encode()).hexdigest(),textCharacterCount=len(text),widthPoints=page.rect.width,heightPoints=page.rect.height,previewPath=f'sources/previews/{sid}/page-{i+1:04d}.webp',printedNumberEvidence='Extracted from actual bottom-right footer region; not inferred from physical page.' if printed else 'No recognized footer number extracted; visual check pending.'))
  maps[sid]=pages
  for start in range(0,len(doc),25):jobs.append((sid,str(path),range(start,min(start+25,len(doc))),args.render_scale,args.webp_quality,preview_versions.get(sid)!=sha))
  print(f'{sid}: {len(doc)} pages, SHA256 {sha}',flush=True)
 for i,lec in enumerate(lectures):
  lec['endPage']=lectures[i+1]['startPage']-1 if i+1<len(lectures) else len(maps['lectures'])
  for p in maps['lectures'][lec['startPage']-1:lec['endPage']]:
   p.update(week=lec['week'],lectureId=lec['id'],lectureTitle=lec['title'],lectureRelativePage=p['physicalPage']-lec['startPage']+1,printedLectureNumber=lec['printedLectureNumber'],weekMappingEvidence=f'Course outline, lectures PDF physical page {lec["week"]+2}; chronological lecture-title grouping matches outline topics. Visual confirmation tracked in lecture_map.json.')
 assignment_boundary_path=SOURCES/'assignment_boundary_inspections.json'
 assignment_boundary_records=json.loads(assignment_boundary_path.read_text()) if assignment_boundary_path.exists() else []
 assignment_sha=next(record['sha256'] for record in metadata if record['id']=='assignments')
 for item in assignment_starts:
  if any(review['sourceSha256']==assignment_sha and review['physicalPage']==item['startPage'] and review['week']==item['week'] for review in assignment_boundary_records):item['boundaryStatus']='header_visually_confirmed'
 for i,item in enumerate(assignment_starts):
  item['endPage']=assignment_starts[i+1]['startPage']-1 if i+1<len(assignment_starts) else len(maps['assignments'])
  for p in maps['assignments'][item['startPage']-1:item['endPage']]:p.update(week=item['week'],assignmentNumber=item['assignmentNumber'],assignmentRelativePage=p['physicalPage']-item['startPage']+1)
 # Merge only source-version-bound, explicit human/model visual inspection records.
 inspections_path=SOURCES/'visual_inspections.json'
 inspections=json.loads(inspections_path.read_text()) if inspections_path.exists() else []
 rows_by_id={r['id']:r for rows in maps.values() for r in rows}
 for review in inspections:
  row=rows_by_id.get(review['slideId'])
  if row is None or review['sourceSha256']!=row['sourceSha256']:continue
  for key,value in review.items():
   if key not in ('slideId','sourceSha256'):row[key]=value
 # Completed page inspections from authored batches are evidence, not question verification.
 # Preserve each inspector's identity/notes; never convert extraction or a draft into a view.
 for batch_path in sorted((ROOT/'data'/'inspection-batches').glob('*.json')):
  batch=json.loads(batch_path.read_text())
  for inspection in batch.get('slides',[]):
   row=rows_by_id.get(inspection.get('id'))
   visual=inspection.get('visualInspection',{})
   bound_hash=inspection.get('sourceSha256',batch.get('sourceSha256'))
   if row is None or bound_hash!=row['sourceSha256'] or visual.get('status')!='complete':continue
   if not visual.get('inspectorId') or not visual.get('inspectedAt') or visual.get('method') not in ('rendered_page','pdf_viewer'):continue
   history=row.setdefault('visualInspectionHistory',[])
   if row['visualInspection']['status']=='complete' and row['visualInspection'] not in history:history.append(dict(row['visualInspection']))
   history.append(dict(visual,evidenceFile=str(batch_path.relative_to(ROOT))))
   row['visualInspection']=dict(visual)
   for field in ('printedSlideNumber','printedSlideNumberStatus'):
    if field in inspection:row[field]=inspection[field]
   # Concepts/questions are merged by the builder; the inventory retains only evidence.
   if inspection.get('disposition')=='excluded' and inspection.get('exclusionReason'):
    row['disposition']='excluded';row['exclusionReason']=inspection['exclusionReason']
 # Independent audit observations are additive evidence, with their original identity.
 for audit_path in [ROOT/'audits'/'page_observations.jsonl', ROOT/'audits'/'learning-tools-page-observations.jsonl']:
  if not audit_path.exists():continue
  for line in audit_path.read_text().splitlines():
   if not line.strip():continue
   observation=json.loads(line);page_id=f"{observation['source']}-p{observation['physicalPage']:04d}"
   row=rows_by_id.get(page_id)
   if row is None or row['sourceSha256']!=observation['sourceSha256']:continue
   history=row.setdefault('visualInspectionHistory',[])
   if row['visualInspection']['status']=='complete' and row['visualInspection'] not in history:history.append(dict(row['visualInspection']))
   row['visualInspection']=dict(status='complete',inspectorId=observation['inspectorId'],inspectedAt=observation['inspectedAt'],method=observation['method'],notes=observation.get('notes',''))
   row['printedSlideNumber']=observation['printedSlideNumber'];row['printedSlideNumberStatus']=observation['printedSlideNumberStatus']
   row['observedConceptDescriptions']=observation.get('observedConcepts',[])
   row['coverageChallenge']=observation.get('coverageChallenge','pending_question_mapping')
 for lec in lectures:
  if rows_by_id[lec['titleSlideId']]['visualInspection']['status']=='complete':lec['boundaryStatus']='title_visually_confirmed'
 weeks=[dict(week=w,title=WEEK_TITLES[w-1],outlinePhysicalPage=w+2,lectureIds=[x['id']for x in lectures if x['week']==w],lectureStartPage=min(x['startPage']for x in lectures if x['week']==w),lectureEndPage=max(x['endPage']for x in lectures if x['week']==w),assignmentRange=next((x for x in assignment_starts if x['week']==w),None),mappingStatus='outline_and_titles_visually_confirmed' if rows_by_id[f'lectures-p{w+2:04d}']['visualInspection']['status']=='complete' and all(x['boundaryStatus']=='title_visually_confirmed' for x in lectures if x['week']==w) else 'outline_and_title_sequence_pending_visual_confirmation')for w in range(1,13)]
 dump(SOURCES/'manifest.json',dict(schemaVersion='1.0.0',retrievedAt=args.retrieved_at,folderUrl='https://drive.google.com/drive/folders/1kJJLyX3HjmCX652v4jy_RyM7gS04mpx_',folderInventoryCount=2,lecturePageCount=len(maps['lectures']),assignmentPageCount=len(maps['assignments']),corpusPageCount=sum(map(len,maps.values())),expectedCountInterpretation='1,953 is the combined lecture PDF page count, not total corpus. Total is 2,012 including 59 assignment pages.',sources=metadata,assets=assets))
 dump(SOURCES/'lecture_map.json',lectures);dump(SOURCES/'week_map.json',weeks);dump(SOURCES/'assignment_map.json',assignment_starts)
 for sid,pages in maps.items():
  target=SOURCES/'page_maps'/f'{sid}.jsonl';target.parent.mkdir(parents=True,exist_ok=True)
  target.write_text(''.join(json.dumps(p,ensure_ascii=False)+'\n'for p in pages))
 # Only a separate explicit visual log may confer visual-inspection status.
 dump(SOURCES/'inventory_summary.json',dict(totalPages=sum(map(len,maps.values())),lectureCount=len(lectures),weekCount=len(weeks),assignmentCount=len(assignment_starts),allPagesTextExtracted=True,visualInspectionNotImplied=True,visuallyInspectedPages=sum(p['visualInspection']['status']=='complete' for pages in maps.values() for p in pages),unrecognizedPrintedNumbers={sid:sum(p['printedSlideNumber'] is None for p in pages)for sid,pages in maps.items()},sourceNumberingIssues=[dict(id='fuzzy-title-number-45',sourceId='lectures',physicalPage=1231,sequenceLectureId='L40',printedLectureNumber=45,explanation='Fuzzy Logic Control appears as the 40th lecture in the week-8 topic sequence but its title says Lecture Number 45. The subsequent week-9 Mapping/SLAM lecture also says 45 (physical page 1405). Never silently correct printed numbering.'),dict(id='duplicate-printed-slide-9',sourceId='lectures',physicalPage=1380,lectureId='L44',lectureRelativePage=11,printedSlideNumber='9',explanation='Visually confirmed printed9 at physical1380 while lecture-relative position is11. Do not conflate printed pagination with position.')]))
 if args.render:
  results=[]
  with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex:
   for result in ex.map(render_batch,jobs):results.append(result);print('rendered',result,flush=True)
  preview_versions={record['id']:record['sha256'] for record in metadata}
  dump(preview_versions_path,preview_versions)
  dump(SOURCES/'preview_manifest.json',dict(format='image/webp',scale=args.render_scale,quality=args.webp_quality,faithfulPageRender=True,renderedPageCount=sum(x['count']for x in results),totalBytes=sum(x['bytes']for x in results),visualInspectionNotImplied=True))
 # Optional standalone page-preview assets: inclusion in the bank is a builder choice.
 preview_assets=[]
 for sid,pages in maps.items():
  for row in pages:
   if preview_versions.get(sid)!=row['sourceSha256']:continue
   preview=ROOT/row['previewPath']
   if not preview.exists():continue
   with Image.open(preview) as im:width,height=im.size
   preview_assets.append(dict(id=f"{row['id']}-preview",kind='source_page',path=row['previewPath'],mimeType='image/webp',sha256=digest(preview),alt=f"Exact rendered page {row['physicalPage']} from {sid}; original printed number {row['printedSlideNumber'] or 'absent/unchecked'}",sourceId=sid,physicalPage=row['physicalPage'],width=width,height=height))
 dump(SOURCES/'preview_assets.json',preview_assets)
 dump(SOURCES/'preview_availability.json',dict(currentSourcePageCount=sum(len(rows) for rows in maps.values()),currentSourceVersionPreviewCount=len(preview_assets),allPagesHaveCurrentPreview=len(preview_assets)==sum(len(rows) for rows in maps.values()),sourceVersions={record['id']:record['sha256'] for record in metadata}))
if __name__=='__main__':main()
