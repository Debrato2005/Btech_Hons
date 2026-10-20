"""Reviewer-owned synthetic text fixtures. Notebook text is never executed."""
from pathlib import Path
import base64,copy,datetime,hashlib,importlib.util,json,tempfile,re
R=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('reviewer105_visual',R/'scripts/question_visuals.py');V=importlib.util.module_from_spec(sp);sp.loader.exec_module(V)
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
base=json.loads((R/'audits/final-ui-policy-104-review/software-visual-fixture.json').read_text())
class Fixture:
 def __init__(self,root,output=False,code="x = 2\nprint(x)\n",extracted=False):
  self.root=root;self.bank=copy.deepcopy(base['bank']);self.bank['assets']=[];self.bank.pop('questionVisuals');self.q=self.bank['questions'][0]
  self.record=copy.deepcopy(base['bank']['questionVisuals']['records'][0]);self.record.update(assetIds=[],supplementalInputIds=['SOFTWARE_SNIPPET'],requiredInputs=['SOFTWARE ONLY code or saved output stimulus'])
  self.review=copy.deepcopy(base['bank']['questionVisuals']['reviews'][0]);self.review.update(assetHashes={},assetMetadataHashes={},reviewedAssetIds=[])
  self.name='sources/supplemental/SOFTWARE_ONLY.ipynb';self.notebook={'cells':[{'cell_type':'code','id':'stable-cell','metadata':{'id':'fallback-cell'},'source':code,'outputs':[{'output_type':'stream','text':'2\n'},{'output_type':'execute_result','data':{'text/plain':['tensor(2)\n']}}]}]}
  self.artifacts={};self.write(self.name,json.dumps(self.notebook,ensure_ascii=False));text='2\n' if output else code
  self.s={'id':'SOFTWARE_SNIPPET','authorId':'SOFTWARE_SNIPPET_AUTHOR','revisionAuthors':[],'kind':'verbatim_saved_output' if output else 'verbatim_source_code','language':'text' if output else 'python','sourceArtifact':self.name,'sourceSha256':self.artifacts[self.name]['sha256'],'notebookArtifact':self.name,'notebookSha256':self.artifacts[self.name]['sha256'],'lineStart':None,'lineEnd':None,'cellIndexZeroBased':0,'cellId':'stable-cell','cellLineStart':1,'cellLineEnd':len(re.findall(r'[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+$',text)),'text':text,'textSha256':sha(text),'notebookRepresentation':'verbatim','upstreamPinStatus':'local_only','upstreamCommit':None,'upstreamGitBlobSha':None,'sourceUrl':None,'transformation':'SOFTWARE ONLY exact text selection. Never executed.'}
  if extracted:
   name='audits/review-snapshots/SOFTWARE_ONLY.py';self.write(name,'# header\n'+code);self.s.update(sourceArtifact=name,sourceSha256=self.artifacts[name]['sha256'],lineStart=2,lineEnd=len(re.findall(r'[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+$',code))+1)
  if output:self.s.update(notebookOutputIndex=0,notebookOutputField='text');self.record['savedOutputUse']='explicit_output_reading';self.review['savedOutputUse']='explicit_output_reading';self.review['checks']['savedOutputIsQuestionStimulus']=True
  self.inputs={'manifest':copy.deepcopy(base['bank']['questionVisuals']['manifest']),'records':[self.record],'assets':[],'reviews':[self.review],'supplementalInputs':[self.s],'supplementalArtifacts':self.artifacts};self.rebind()
 def write(self,name,text):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(text.encode());self.artifacts[name]={'sha256':sha(text),'rawText':text}
 def rebind(self):
  self.review.update(visualSha256=V.digest(self.record),reviewedSupplementalInputIds=self.record['supplementalInputIds'][:],supplementalInputHashes={self.s['id']:V.digest(self.s)},supplementalSourceHashes={self.s[k]:self.s[h] for k,h in [('sourceArtifact','sourceSha256'),('notebookArtifact','notebookSha256')]})
 def prepare(self):return V.prepare_question_visuals(self.bank,self.root,self.inputs,check_files=True)
results=[];fixtures={}
def check(name,mutate=lambda f:None,expected=False,**kwargs):
 with tempfile.TemporaryDirectory(dir=D) as td:
  f=Fixture(Path(td),**kwargs);mutate(f);f.rebind()
  try:
   x=f.prepare();allowed=f.q['id'] in x['bindings'];results.append({'name':name,'passed':allowed==expected,'allowed':allowed,'diagnostics':x['diagnostics']})
   if expected and allowed:fixtures[name]={'bank':{**f.bank,'questionVisuals':x},'embeddedAssets':{}}
  except Exception as e:results.append({'name':name,'passed':not expected,'allowed':False,'rejectionMode':'producer exception, fail closed before any binding','error':str(e)})
for name,kwargs in [('code LF',{}),('code CRLF',{'code':'x=2\r\nprint(x)\r\n'}),('code without final newline',{'code':'x=2\nprint(x)'}),('extracted source exact line range',{'extracted':True}),('historical text output',{'output':True})]:check(name,expected=True,**kwargs)
for name,mutate in [
 ('wrong exact text despite coherent metadata review',lambda f:f.s.update(text='answer=99\n',textSha256=sha('answer=99\n'))),('wrong current local bytes',lambda f:(f.root/f.name).write_text('changed')),('changed embedded bytes',lambda f:f.artifacts[f.name].update(rawText=f.artifacts[f.name]['rawText']+' ')),('wrong cell index',lambda f:f.s.update(cellIndexZeroBased=1)),('boolean cell index',lambda f:f.s.update(cellIndexZeroBased=False)),('wrong top-level cell ID cannot fall back to metadata',lambda f:f.s.update(cellId='fallback-cell')),('wrong cell range',lambda f:f.s.update(cellLineEnd=99)),('boolean cell line',lambda f:f.s.update(cellLineStart=True)),('misleading notebook global lines',lambda f:f.s.update(lineStart=1,lineEnd=2)),('code selecting saved output',lambda f:f.s.update(notebookOutputIndex=0,notebookOutputField='text')),('wrong language',lambda f:f.s.update(language='javascript')),('path traversal',lambda f:f.s.update(sourceArtifact='sources/supplemental/../../bad.py')),('unsupported local root',lambda f:f.s.update(sourceArtifact='data/bank.json')),('incomplete upstream pinned identity',lambda f:f.s.update(upstreamPinStatus='pinned')),('unknown commit represented as local-only',lambda f:f.s.update(upstreamCommit='a'*40)),('missing transformation qualification',lambda f:f.s.update(transformation=' ')),('blank snippet author',lambda f:f.s.update(authorId=' ')),('null snippet revision authors',lambda f:f.s.update(revisionAuthors=None)),('empty-string snippet revision authors',lambda f:f.s.update(revisionAuthors='')),('snippet revision author self approval',lambda f:f.s.update(revisionAuthors=[f.review['reviewerId']])),('padded snippet author self approval',lambda f:f.review.update(reviewerId=' SOFTWARE_SNIPPET_AUTHOR ')),('missing independent output classification',lambda f:f.review['checks'].pop('noAnswerLeak')),('duplicate snippet IDs',lambda f:f.inputs['supplementalInputs'].append(copy.deepcopy(f.s)))]:check(name,mutate)
for name,mutate in [('historical missing record intent',lambda f:f.record.pop('savedOutputUse')),('historical missing review intent',lambda f:f.review.pop('savedOutputUse')),('historical false review intent check',lambda f:f.review['checks'].update(savedOutputIsQuestionStimulus=False)),('historical output-stripped notebook forbidden',lambda f:f.s.update(notebookRepresentation='output_stripped')),('historical wrong output index',lambda f:f.s.update(notebookOutputIndex=2)),('historical HTML output forbidden',lambda f:f.s.update(notebookOutputField='data.text/html'))]:check(name,mutate,output=True)
check('extracted source line mismatch',lambda f:f.s.update(lineStart=1),extracted=True)
def plain(f):
 f.s.update(notebookOutputIndex=1,notebookOutputField='data.text/plain',text='tensor(2)\n',textSha256=sha('tensor(2)\n'))
check('historical text/plain output',plain,expected=True,output=True)
def pin(f):f.s.update(upstreamPinStatus='commit_only',upstreamCommit='a'*40,sourceUrl='https://github.com/example/repo/blob/'+('a'*40)+'/fixture.ipynb')
check('commit-only qualification',pin,expected=True)
check('Unicode line separator within source literal',expected=True,code="x = 'a\u2028b'\nprint(x)\n")
(D/'software-supplemental-fixtures.json').write_text(json.dumps({'purpose':'SOFTWARE ONLY. Not course input approvals.','fixtures':fixtures},ensure_ascii=False,indent=2)+'\n')
out={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'Independent synthetic producer mutations; no notebook execution or browser.','producerHashes':{p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in ['scripts/question_supplemental.py','scripts/question_visuals.py']},'results':results,'passed':sum(r['passed'] for r in results),'failed':sum(not r['passed'] for r in results)};(D/'supplemental-producer-probes.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
