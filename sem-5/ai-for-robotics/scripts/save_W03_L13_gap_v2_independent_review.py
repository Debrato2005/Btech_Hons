#!/usr/bin/env python3
"""Persist honest revision rereview of L13 final gap repair."""
import datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import CHECK_KEYS,question_hash
load=lambda p:json.loads((R/p).read_text());qid='W03-L13-GAP-Q002'
q=next(q for q in load('data/question-batches/W03-L13-GAP.json')['questions'] if q['id']==qid)
p=load('audits/blind-W03-L13-GAP-v2.json')[0]
for k in ['stem','version','selectionMode','difficulty','options','assumptions']:assert p[k]==q[k]
assert q['version']==2 and q['correctOptionIds']==['o1']
allqs={x['id']:x for f in ['data/question-batches/W03-L13.json','data/question-batches/W03-L13-GAP.json'] for x in load(f)['questions']}
accepted={**load('audits/W03-L13-independent-summary.json')['approvedCurrentHashes'],**load('audits/W03-L13-v2-independent-summary.json')['approvedCurrentHashes']};assert len(accepted)==47
assert all(question_hash(allqs[k])==h for k,h in accepted.items())
now=datetime.datetime.now(datetime.timezone.utc).isoformat();reviewer='build_offline_study_interface-L13-independent'
assert reviewer not in {q['authorId'],*q.get('revisionAuthors',[])}
r={'id':'REV-W03-L13-GAP-Q002-v2-interface-rereview','questionId':qid,'questionVersion':2,'questionSha256':question_hash(q),'reviewerId':reviewer,'decision':'verified','reviewedAt':now,'sourceVersions':{c['sourceId']:c['sourceSha256'] for c in q['citations']},'reviewedSlideIds':[c['slideId'] for c in q['citations']],'sourceInspectionEvidence':[{'physicalPage':c['physicalPage'],'inspectorIds':[reviewer],'previewSha256':hashlib.sha256((R/f"sources/previews/lectures/page-{c['physicalPage']:04d}.webp").read_bytes()).hexdigest()} for c in q['citations']],'independentAnswerOptionIds':['o1'],'solvedBeforeAnswerSeen':False,'priorReviewerExposure':True,'priorAuthorExposure':False,'reviewType':'independent revision re-review, not blind','checks':{k:True for k in CHECK_KEYS},'reasoning':'The source distinguishes large closed-form symbolic expressions (p424) from linkwise outward/inward evaluation (p425). The v2 alternatives now test requiring symbolic expansion first, incorrectly decoupling links, and neglecting velocity-product terms. These are plausible and distinct misconceptions. Updated explanations and misconception strings correctly reject each without option-order dependence. The correct key remains o1. No assumption, equation, source or difficulty change was needed. All 47 other accepted hashes are unchanged. Actual p424/p425 pixels were reopened at 17:29 during this review sequence. Prior v1 keys were already known, so this is explicitly not blind.','findings':[],'priorReviewPath':'data/reviews/W03-L13-v2-and-gap-independent.json','sourcePacketPath':'audits/blind-W03-L13-GAP-v2.json','sourcePacketSha256':hashlib.sha256((R/'audits/blind-W03-L13-GAP-v2.json').read_bytes()).hexdigest()}
p=R/'data/reviews/W03-L13-GAP-v2-independent.json';assert not p.exists();p.write_text(json.dumps([r],ensure_ascii=False,indent=2)+'\n')
s={'reviewedAt':now,'reviewed':1,'verified':1,'flagged':0,'answerAgreement':1,'preservedPriorApprovals':47,'priorApprovedHashesUnchanged':True,'approvedCurrentHashes':{qid:question_hash(q)},'actionableFlags':{},'coverageGapClosed':'The final expression-complexity gap now has a verified item with plausible distractors.','reviewPath':str(p.relative_to(R))}
(R/'audits/W03-L13-GAP-v2-independent-summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');print(s)
