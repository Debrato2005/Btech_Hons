"""Freeze only authorized project changes for bounded GitHub connector writes.
Does not create a commit or move any remote ref. Run after validation and build.
"""
import json,subprocess,sys,hashlib,base64
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];prefix=P.relative_to(R).as_posix()+'/'
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
def git(*a):return subprocess.check_output(['git','-C',str(R),*a]).decode()
base=git('rev-parse','HEAD').strip();tree=git('rev-parse','HEAD^{tree}').strip()
files=set(git('diff','--name-only','HEAD','--',prefix).splitlines())|set(git('ls-files','--others','--exclude-standard','--',prefix).splitlines())
entries=[];blobs=[];batch=[];batches=[];size=0
for name in sorted(files):
 assert name.startswith(prefix);p=R/name
 if not p.exists():raise RuntimeError('Deletion requires explicit review: '+name)
 data=p.read_bytes();entry={'path':name,'mode':'100644','type':'blob'}
 try:content=data.decode('utf8');encoding='utf-8'
 except UnicodeDecodeError:content=base64.b64encode(data).decode('ascii');encoding='base64'
 if len(data)>100_000 or encoding=='base64':
  path=out/f'blob-{len(blobs)}.txt';path.write_text(content);blobs.append({'path':name,'local':str(path),'encoding':encoding,'chars':len(content),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()});entry['blobIndex']=len(blobs)-1
 else:entry['content']=content
 cost=len(json.dumps(entry,ensure_ascii=False).encode())
 if batch and size+cost>350_000:batches.append(batch);batch=[];size=0
 batch.append(entry);size+=cost
if batch:batches.append(batch)
for i,b in enumerate(batches):(out/f'tree-{i}.json').write_text(json.dumps(b,ensure_ascii=False))
(out/'blobs.json').write_text(json.dumps(blobs));(out/'meta.json').write_text(json.dumps({'baseCommit':base,'baseTree':tree,'files':len(files),'blobs':len(blobs),'trees':len(batches)}));print((out/'meta.json').read_text())
