"""Independent byte/slice comparison only. Does not execute notebooks or approve snippet intent."""
from pathlib import Path
import datetime,hashlib,json,re
R=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;m=json.loads((R/'data/question-visuals/manifest.json').read_text());artifacts={};rows=[]
def cut(s,start,end):return ''.join(re.findall(r'[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+$',s)[start-1:end])
def joined(v):return v if isinstance(v,str) else ''.join(v)
for s in m['supplementalInputs']:
 for path,key in [(s['sourceArtifact'],'sourceSha256'),(s['notebookArtifact'],'notebookSha256')]:
  b=(R/path).read_bytes();h=hashlib.sha256(b).hexdigest();assert h==s[key],(s['id'],path);artifacts[path]={'sha256':h,'rawText':b.decode('utf8')}
 nb=json.loads(artifacts[s['notebookArtifact']]['rawText']);cell=nb['cells'][s['cellIndexZeroBased']];assert s['cellId']==(cell['id'] if 'id' in cell else cell.get('metadata',{}).get('id'))
 if s['kind']=='verbatim_source_code':field=cell['source']
 else:
  o=cell['outputs'][s['notebookOutputIndex']];field=o['text'] if s['notebookOutputField']=='text' else o['data']['text/plain']
 text=cut(joined(field),s['cellLineStart'],s['cellLineEnd']);assert text==s['text'];assert hashlib.sha256(text.encode()).hexdigest()==s['textSha256']
 if s['sourceArtifact']!=s['notebookArtifact']:assert cut(artifacts[s['sourceArtifact']]['rawText'],s['lineStart'],s['lineEnd'])==text
 rows.append({'id':s['id'],'kind':s['kind'],'textSha256':s['textSha256'],'sourceArtifact':s['sourceArtifact'],'sourceSha256':s['sourceSha256'],'notebookArtifact':s['notebookArtifact'],'notebookSha256':s['notebookSha256'],'passed':True})
(D/'actual-supplemental-source-fixture.json').write_text(json.dumps({'purpose':'Actual metadata and raw source bytes only; no question or intent approval.','inputs':m['supplementalInputs'],'artifacts':artifacts},ensure_ascii=False,indent=2)+'\n')
out={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'Independent read-only UTF8 SHA/cell/physical-line extraction. No source execution or intent approval.','manifestSha256':hashlib.sha256((R/'data/question-visuals/manifest.json').read_bytes()).hexdigest(),'sourceArtifacts':{k:v['sha256'] for k,v in artifacts.items()},'results':rows,'passed':len(rows),'failed':0};(D/'actual-source-parity.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
