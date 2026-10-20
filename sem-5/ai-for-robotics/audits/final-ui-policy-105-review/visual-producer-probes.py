"""Reviewer-owned visual gate fixtures, never course visual/source approvals."""
import base64,copy,datetime,hashlib,importlib.util,json,pathlib,struct,tempfile,zlib
R=pathlib.Path(__file__).resolve().parents[2];D=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('independent_visual_gate',R/'scripts/question_visuals.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
def png():
 def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0\xff\xff\xff'))+chunk(b'IEND',b'')
class Fixture:
 def __init__(self,root,required=True):
  self.root=root;self.bank=json.loads((R/'tests/fixtures/synthetic_bank.json').read_text());self.q=self.bank['questions'][0];self.answer=self.bank['reviews'][0];self.blob=png();self.path=root/'assets/question-visuals/software-only.png';self.path.parent.mkdir(parents=True);self.path.write_bytes(self.blob)
  self.ref={k:self.q['citations'][0][k] for k in ('sourceId','sourceSha256','slideId','physicalPage')}
  self.asset={'id':'software-only-png','path':'assets/question-visuals/software-only.png','mimeType':'image/png','sha256':hashlib.sha256(self.blob).hexdigest(),'width':1,'height':1,**self.ref,'cropRectangle':[0,0,1,1],'renderDpi':72,'alt':'Software-only white pixel; not a course source crop.'}
  self.record={'id':'software-only-visual','version':1,'authorId':'software-classification-author','questionId':self.q['id'],'questionVersion':self.q['version'],'questionSha256':M.question_hash(self.q),'dependencyStatus':'required' if required else 'self_contained','reason':'Explicit software-only fixture for gate checks, not factual visual approval.','assetIds':[self.asset['id']] if required else [],'requiredInputs':['Software fixture'] if required else [],'sourceRefs':[self.ref]}
  self.review={'id':'software-only-visual-review','visualId':self.record['id'],'visualVersion':1,'visualSha256':M.digest(self.record),'reviewerId':'software-independent-reviewer','decision':'verified','questionId':self.q['id'],'questionVersion':self.q['version'],'questionSha256':M.question_hash(self.q),'sourceVersions':{self.ref['sourceId']:self.ref['sourceSha256']},'assetHashes':{self.asset['id']:self.asset['sha256']} if required else {},'assetMetadataHashes':{self.asset['id']:M.digest(self.asset)} if required else {},'reviewedAssetIds':self.record['assetIds'][:],'displayRole':'question_input','checks':{k:True for k in M.VISUAL_CHECKS},'reviewedAt':'2026-10-20T00:00:00Z'}
  self.inputs={'manifest':{'schemaVersion':'1.0.0','authorId':'software-manifest-author','sourceVersions':self.review['sourceVersions'].copy()},'records':[self.record],'assets':[self.asset] if required else [],'reviews':[self.review]}
 def rebind(self):
  h=M.question_hash(self.q);self.answer['questionSha256']=h;self.record['questionSha256']=h;self.review['questionSha256']=h;self.review['visualSha256']=M.digest(self.record);self.review['assetHashes']={a['id']:a['sha256'] for a in self.inputs['assets']};self.review['assetMetadataHashes']={a['id']:M.digest(a) for a in self.inputs['assets']}
 def prepare(self):return M.prepare_question_visuals(self.bank,self.root,self.inputs,check_files=True)
results=[]
def check(name,mutation=lambda f:None,expected=False,rebind=False,required=True):
 with tempfile.TemporaryDirectory() as p:
  f=Fixture(pathlib.Path(p),required);mutation(f)
  if rebind:f.rebind()
  try:
   result=f.prepare();allowed=f.q['id'] in result['bindings'];results.append({'case':name,'passed':allowed==expected,'expectedAllowed':expected,'actualAllowed':allowed,'diagnostics':result['diagnostics']})
  except Exception as e:results.append({'case':name,'passed':False,'error':str(e)})
check('required PNG valid control',expected=True);check('self-contained valid control',expected=True,required=False)
for name,mutate in [
 ('answer review is not visual approval',lambda f:f.inputs.update(reviews=[])),('missing classification',lambda f:f.inputs.update(records=[])),('duplicate classification',lambda f:f.inputs['records'].append(copy.deepcopy(f.record))),('duplicate review IDs',lambda f:f.inputs['reviews'].append(copy.deepcopy(f.review))),
 ('revoked review',lambda f:f.review.update(decision='flagged')),('missing no-answer-leak check',lambda f:f.review['checks'].update(noAnswerLeak=False)),('missing exact asset metadata approval',lambda f:f.review.update(assetMetadataHashes={})),('wrong display role',lambda f:f.review.update(displayRole='solution')),('stale source pixels',lambda f:f.path.write_bytes(f.blob+b'changed')),('missing pixel file',lambda f:f.path.unlink()),('answer revoked',lambda f:f.answer.update(decision='flagged')),('source no longer inspected',lambda f:f.bank['slides'][0]['visualInspection'].update(status='pending')),
 ('self-contained claims assets',lambda f:f.record.update(dependencyStatus='self_contained')),('missing required inputs',lambda f:f.record.update(requiredInputs=[])),('missing required assets',lambda f:f.record.update(assetIds=[]))]:check(name,mutate)
for name,mutate in [
 ('classification author padded self-approval',lambda f:f.review.update(reviewerId=' '+f.record['authorId']+' ')),('manifest author self-approval',lambda f:f.review.update(reviewerId=f.inputs['manifest']['authorId'])),('revision author self-approval',lambda f:f.record.update(revisionAuthors=[f.review['reviewerId']])),
 ('negative crop coordinate',lambda f:f.asset.update(cropRectangle=[-1,0,1,1])),('boolean crop coordinate',lambda f:f.asset.update(cropRectangle=[False,0,1,1])),('dimension differs from actual PNG',lambda f:f.asset.update(width=2)),('unsupported image MIME',lambda f:f.asset.update(mimeType='image/svg+xml')),('path traversal',lambda f:f.asset.update(path='../software.png')),('missing asset alt',lambda f:f.asset.update(alt=' ')),('one literal option question',lambda f:f.q.update(options=[o for o in f.q['options'] if o['id'] in f.q['correctOptionIds']])),('duplicate independent answer IDs',lambda f:f.answer.update(independentAnswerOptionIds=f.answer['independentAnswerOptionIds']*2))]:check(name,mutate,rebind=True)
def corrupt_crc(f):
 b=bytearray(f.blob);b[-1]^=1;f.path.write_bytes(b);f.asset['sha256']=hashlib.sha256(b).hexdigest()
check('coherently rebound pixel hash still rejects broken PNG CRC',corrupt_crc,rebind=True)
with tempfile.TemporaryDirectory() as p:
 f=Fixture(pathlib.Path(p));sidecar=f.prepare();f.bank['questionVisuals']=sidecar;f.bank['assets']+=M.projected_visual_assets(sidecar);embedded={f.asset['id']:{**f.asset,'kind':'diagram','data':base64.b64encode(f.blob).decode()}};(D/'software-visual-fixture.json').write_text(json.dumps({'purpose':'SOFTWARE ONLY, NOT COURSE APPROVAL','bank':f.bank,'embeddedAssets':embedded},indent=2)+'\n')
out={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'Independent synthetic producer mutations; no course data or review changes.','producerSha256':hashlib.sha256((R/'scripts/question_visuals.py').read_bytes()).hexdigest(),'results':results,'passed':sum(r['passed'] for r in results),'failed':sum(not r['passed'] for r in results)};(D/'visual-producer-probes.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
