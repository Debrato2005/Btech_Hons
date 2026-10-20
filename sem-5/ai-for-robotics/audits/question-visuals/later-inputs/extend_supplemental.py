import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];path=R/'audits/question-visuals/late-supplemental-proposal.json';out=json.loads(path.read_text());bank={q['id']:q for q in json.loads((R/'data/bank.json').read_text())['questions']}
for v in out['inputs'].values():v.update(notebookRepresentation='output_stripped',upstreamPinStatus='pinned',language='python',extractionPath=f"cells[{v['cellIndexZeroBased']}].source")
def snippet(key,artifact,ci,start,end,url,output_index=None,output_field=None):
 nb=json.loads((R/artifact).read_text());c=nb['cells'][ci];source=c['source'] if output_index is None else (c['outputs'][output_index]['text'] if output_field=='text' else c['outputs'][output_index]['data'][output_field]);text=''.join(''.join(source).splitlines(keepends=True)[start-1:end]);sha=hashlib.sha256((R/artifact).read_bytes()).hexdigest()
 out['inputs'][key]={'kind':'verbatim_source_code' if output_index is None else 'verbatim_saved_output','language':'python' if output_index is None else 'text','sourceArtifact':artifact,'sourceSha256':sha,'lineStart':None,'lineEnd':None,'notebookArtifact':artifact,'notebookSha256':sha,'notebookRepresentation':'verbatim','upstreamPinStatus':'local_only','cellIndexZeroBased':ci,'cellId':c.get('id') or c.get('metadata',{}).get('id'),'cellLineStart':start,'cellLineEnd':end,'outputIndexZeroBased':output_index,'outputField':output_field,'extractionPath':f'cells[{ci}].source' if output_index is None else f'cells[{ci}].outputs[{output_index}].'+('text' if output_field=='text' else "data['text/plain']"),'sourceUrl':url,'upstreamCommit':None,'upstreamGitBlobSha':None,'text':text,'textSha256':hashlib.sha256(text.encode()).hexdigest(),'transformation':'None: exact frozen source substring; no execution, correction or result added.' if output_index is None else 'None: exact historically saved notebook output; not freshly executed and not a claim about current resources.'}
def record(q,keys):
 b=bank[q];out['records'][q]={'dependencyStatus':'required','proposedInputKeys':keys,'linkedLectureCitations':[{'sourceId':c['sourceId'],'physicalPage':c['physicalPage'],'sourceSha256':c['sourceSha256'],'locator':c['locator']} for c in b['citations']],'reason':'Exact source-notebook premise required by this question; PDF alone omits this code or historical saved output. Frozen source input is supplied without answer annotation or any claim of fresh execution.'}
a='sources/supplemental/L34-official-notebook.ipynb';u='https://raw.githubusercontent.com/robotics-lab-iitr/nptel-ai-robotics/main/week07/week07_lecture34.ipynb'
snippet('l34-setup-cell',a,2,1,22,u);snippet('l34-initial-values',a,4,1,8,u);snippet('l34-learning-loop',a,8,1,39,u)
for q in ['W07-L34-P1052-Q06','W07-L34-P1052-Q07']:record(q,['l34-initial-values','l34-learning-loop'])
record('W07-L34-P1052-Q11',['l34-setup-cell'])
a='audits/review-snapshots/W07-L35-official-notebook-contracts.ipynb';u='https://raw.githubusercontent.com/robotics-lab-iitr/nptel-ai-robotics/main/week07/week07_lecture35.ipynb'
for key,ci,end in [('l35-predict-cell',7,7),('l35-report-loop',11,25),('l35-display-cell',12,5)]:snippet(key,a,ci,1,end,u)
record('W07-L35-Q089',['l35-report-loop']);record('W07-L35-Q101',['l35-predict-cell','l35-report-loop','l35-display-cell'])
a='sources/supplemental/L46-official-week10_lecture46.ipynb';u='https://github.com/robotics-lab-iitr/nptel-ai-robotics/blob/main/week10/week10_lecture46.ipynb'
snippet('l46-count-dataframe',a,17,10,20,u);record('W10-L46-P1454-Q05',['l46-count-dataframe'])
snippet('l46-contextual-light-code',a,24,1,7,u)
snippet('l46-contextual-light-noun-output',a,24,1,1,u,0,'text')
snippet('l46-contextual-light-adjective-output',a,24,1,1,u,1,'text/plain')
record('W10-L46-P1461-Q04',['l46-contextual-light-code','l46-contextual-light-noun-output','l46-contextual-light-adjective-output'])
out['scope']='Exact pinned/frozen notebook premises for L34, L35, L43 and L46; frozen question content unchanged.'
path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('inputs',len(out['inputs']),'records',len(out['records']))
