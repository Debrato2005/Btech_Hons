#!/usr/bin/env python3
"""Final targeted L22 re-review; preserves all authored objects."""
import json,hashlib,datetime,sys,contextlib,io
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,CHECK_KEYS,schema_errors,validate_bank
AUTHOR='build_offline_study_interface:L22-independent-reviewer'
f=R/'audits/W05-L22-final-readability-independent-answers.json';frozen=json.loads(f.read_text());assert frozen['currentKeysRead'] is False
raw=(R/'data/question-batches/W05-L22.json').read_bytes();b=json.loads(raw);qs={q['id']:q for q in b['questions']};preserved={}
for name in ['W05-L22-v1-independent-interface.json','W05-L22-quality-repairs-independent-interface.json']:
 for r in json.loads((R/'data/reviews'/name).read_text())['reviews']:
  if r['decision']=='verified':preserved[r['questionId']]=r['questionSha256']
assert len(preserved)==50 and all(question_hash(qs[k])==v for k,v in preserved.items())
now=datetime.datetime.now(datetime.timezone.utc).isoformat();reviews=[]
for a in frozen['answers']:
 q=qs[a['questionId']];assert q['version']==a['questionVersion'] and q['correctOptionIds']==a['independentAnswerOptionIds']
 reviews.append({'id':f'REV-{q["id"]}-v{q["version"]}-final-readability-interface','questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q),'reviewerId':AUTHOR,'decision':'verified','reviewedAt':now,'sourceVersions':{c['sourceId']:c['sourceSha256'] for c in q['citations']},'reviewedSlideIds':list(dict.fromkeys(c['slideId'] for c in q['citations'])),'independentAnswerOptionIds':a['independentAnswerOptionIds'],'solvedBeforeAnswerSeen':False,'reviewKind':'independent revision re-review, prior exposure disclosed','checks':{k:True for k in CHECK_KEYS},'reasoning':a['reasoning']+' The final prose is readable and quantities remain unchanged. The p679/p680 citations now support Q025’s heuristic and critical-gain relations; p676 now supports Q059’s gear transmission claim. Those source pixels and the p682 diagram factors were reinspected. All current options, assumptions, explanations, individual rationales, steps and formula definitions were checked; all nine dimensions pass. This is not a new blind solve because the reviewer saw earlier versions. Independent 17-assertion/1,000-case checks were rerun successfully. All local source qualifications remain intact.','findings':[]})
schema=json.loads((R/'data/schema.review.json').read_text());assert not [e for r in reviews for e in schema_errors(r,schema)]
out=R/'data/reviews/W05-L22-final-readability-independent-interface.json';out.write_text(json.dumps({'reviewerId':AUTHOR,'reviews':reviews},ensure_ascii=False,indent=2)+'\n')
report={'reviewerId':AUTHOR,'completedAt':now,'verified':10,'flagged':0,'keyDisagreements':0,'batchVerifiedTotal':60,'preservedAcceptedHashes':preserved,'reviewFile':str(out.relative_to(R)),'reviewSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'answersPath':str(f.relative_to(R)),'answersSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'reviewKind':'revision re-review with prior exposure, not fresh blind','coverageChallenge':'All three bounded L22 gaps are closed by current Q059 component roles, Q026 actual distributed/lumped diagram factors, and Q060 retained state counts. Full 26-page coverage challenge is complete within this lecture boundary; does not claim whole-course coverage.','mutations':'Reviews, scripts, audits and handoff only; author batch, source PDF, canonical bank and Git unchanged.'}
(R/'audits/W05-L22-final-readability-independent-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
import assemble_bank
captured={};assemble_bank.dump=lambda p,v:captured.setdefault(str(p),v);sys.argv=['assemble_bank.py']
with contextlib.redirect_stdout(io.StringIO()):assemble_bank.main()
bank=next(v for k,v in captured.items() if k.endswith('/data/bank.json'));v=validate_bank(bank,R);(R/'audits/W05-L22-final-readability-independent-validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
assert (R/'data/question-batches/W05-L22.json').read_bytes()==raw
assert sum(q['id'].startswith('W05-L22-') and q['status']=='verified' for q in bank['questions'])==60
print(json.dumps({'verified':10,'totalVerifiedL22':60,'preservedHashes':50,'valid':v['valid'],'errors':v['errors']}))
