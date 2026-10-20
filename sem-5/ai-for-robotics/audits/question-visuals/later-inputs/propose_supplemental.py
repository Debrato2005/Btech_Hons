import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3]
codepath='sources/supplemental/L43-official-code.py';notepath='sources/supplemental/L43-official-notebook-output-stripped.ipynb'
code=(R/codepath).read_text();lines=code.splitlines(keepends=True);nb=json.loads((R/notepath).read_text())
retrieval=json.loads((R/'sources/supplemental/L43-source-retrieval.json').read_text())
# Inclusive ranges in exact preserved notebook source cells and concatenated code artifact.
specs={
 'l43-maze-actions':(3,1,11,15,25),
 'l43-featurize':(5,4,13,62,71),
 'l43-manhattan':(5,1,2,59,60),
 'l43-teacher':(5,15,30,73,88),
 'l43-training-labels':(5,32,43,90,101),
 'l43-navnet':(7,1,11,110,120),
 'l43-training-epoch':(7,13,28,122,137),
 'l43-navigate':(9,1,15,144,158)
}
inputs={}
for key,(ci,cs,ce,ps,pe) in specs.items():
 cell=nb['cells'][ci];text=''.join(lines[ps-1:pe]);ct=''.join(''.join(cell['source']).splitlines(keepends=True)[cs-1:ce]);assert text.rstrip('\n')==ct.rstrip('\n'),(key,repr(text),repr(ct))
 inputs[key]={'kind':'verbatim_source_code','sourceArtifact':codepath,'sourceSha256':hashlib.sha256((R/codepath).read_bytes()).hexdigest(),'lineStart':ps,'lineEnd':pe,'notebookArtifact':notepath,'notebookSha256':hashlib.sha256((R/notepath).read_bytes()).hexdigest(),'cellIndexZeroBased':ci,'cellId':cell['id'],'cellLineStart':cs,'cellLineEnd':ce,'sourceUrl':retrieval['url'],'upstreamCommit':retrieval['commit'],'upstreamGitBlobSha':retrieval['gitBlobSha'],'text':text,'textSha256':hashlib.sha256(text.encode()).hexdigest(),'transformation':'None: exact source substring, no outputs, assertions, or worked examples added.'}
config=['l43-maze-actions'];features=config+['l43-featurize'];teacher=config+['l43-manhattan','l43-teacher']
keys={
 'Q020':features,'Q021':features,'Q022':features,'Q023':teacher,'Q024':teacher,'Q025':teacher,'Q026':teacher,
 'Q030':['l43-navnet'],'Q034':['l43-training-labels','l43-training-epoch'],'Q035':['l43-training-epoch'],
 'Q038':config+['l43-navigate'],'Q039':['l43-navigate'],'Q042':features
}
bank={q['id']:q for q in json.loads((R/'data/bank.json').read_text())['questions']};records={}
for suffix,ks in keys.items():
 qid='W09-L43-'+suffix;q=bank[qid]
 records[qid]={'dependencyStatus':'required','proposedInputKeys':ks,'linkedLectureCitations':[{'sourceId':c['sourceId'],'physicalPage':c['physicalPage'],'sourceSha256':c['sourceSha256'],'locator':c['locator']} for c in q['citations']],'reason':'The question refers to exact implementation details of the pinned official notebook. PDF pages provide context/link but not the required exact code; a distinct supplemental code input is needed, with no saved output or worked answer.'}
out={'schemaVersion':'proposal-1','status':'proposed-not-integrated-not-approved','scope':'L43 exact pinned notebook premises; frozen questions unchanged','inputs':inputs,'records':records}
path=R/'audits/question-visuals/late-supplemental-proposal.json';path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(path,len(inputs),len(records))
