"""Freeze current L48 draft artifacts, without assembly or Git mutation."""
from pathlib import Path
import json,hashlib,datetime,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors
from authoring_helpers import SHA
B='W10-L48';bp=R/f'data/question-batches/{B}.json';b=json.loads(bp.read_text());packet=R/f'audits/blind-{B}.json';p=json.loads(packet.read_text());cov=json.loads((R/f'audits/{B}-author-coverage.json').read_text());check=json.loads((R/f'audits/{B}-author-checks.json').read_text())
assert len(p)==len(b['questions'])==77
for q,h in zip(b['questions'],p):
 assert q['id']==h['id'] and q['status']=='draft' and not q['reviewIds']
 assert not {'correctOptionIds','solution','conflictResolution','primaryEvidence'} & set(h)
 assert all('evidenceText' not in c for c in h['citations'])
 assert not schema_errors(q,json.loads((R/'data/schema.question.json').read_text()))
paths=[f'data/question-batches/{B}.json',f'data/inspection-batches/{B}.json',f'audits/blind-{B}.json',f'audits/{B}-author-coverage.json',f'audits/{B}-source-issues.json',f'audits/{B}-primary-evidence.json',f'audits/{B}-page-observations.json',f'audits/{B}-source-retrieval.json',f'audits/{B}-author-checks.json',f'audits/{B}-author-checks-dsp.json',f'audits/{B}-author-checks-torch.json',f'audits/{B}-literal-slide-code.py.txt','scripts/author_W10_L48.py','scripts/inspect_W10_L48.py','scripts/check_W10_L48_author.py','scripts/check_W10_L48_torch.py','sources/supplemental/L48-official-week10_lecture48.ipynb','sources/supplemental/L48-official-whisper-model.py','sources/supplemental/L48-official-whisper-audio.py','sources/supplemental/L48-official-whisper-tokenizer.py']
qh={q['id']:question_hash(q) for q in b['questions']}
m={'batchId':B,'authorId':b['authorId'],'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Frozen drafts awaiting distinct source-first independent review.','sourceId':'lectures','sourceSha256':SHA,'physicalPages':[1507,1536],'printedLectureNumber':48,'actualPagesInspected':30,'substantivePages':25,'questionCount':77,'conceptCount':77,'packet':str(packet.relative_to(R)),'packetSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'questionHashes':qh,'files':{x:hashlib.sha256((R/x).read_bytes()).hexdigest() for x in paths},'authorChecks':{'named':check['namedChecks'],'varied':check['variedChecks'],'independent':False},'pretrainedModelExecuted':False,'boundedGap':'Source notebook and reported transcription inspected, but pretrained ASR was not run after the dependency-install denial. No alternate route or retry was used.','coverageChallengePending':True,'preflight':['Actual pixels inspected for all pages; 5 nonsubstantive exclusions retained.','Each page has its own locator and evidence kind; calculations are marked premise, not printed output.','Distractors revised for same-domain misconceptions and normal prose spacing.','Complete formula definitions and source-version-bound local conflicts retained.','Every current substantive page is cited; summary reuses concepts rather than duplicate recall.','No author check is an independent verification.']}
(R/f'audits/{B}-frozen-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
minimal={k:m[k] for k in ['batchId','authorId','sourceId','sourceSha256','physicalPages','packet','packetSha256','questionHashes']};minimal['reviewInstructions']='Inspect actual pixels and freeze answers before opening keyed batch, checks, issue ledger or author script. Prior author analysis is not independent evidence.'
(R/f'audits/{B}-minimal-bindings.json').write_text(json.dumps(minimal,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:m[k] for k in ['questionCount','packet','packetSha256','authorChecks','pretrainedModelExecuted']}))
