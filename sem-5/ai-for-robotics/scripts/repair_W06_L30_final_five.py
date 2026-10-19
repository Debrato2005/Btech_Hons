#!/usr/bin/env python3
"""Five targeted author repairs after independent v2 review. No self-approval."""
import copy,json,hashlib,datetime,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors
AUTHOR='build_offline_study_interface:L30-author';path=R/'data/question-batches/W06-L30.json'
archive=R/'audits/batch-history/W06-L30-before-final-five-repairs.json'
if not archive.exists():archive.write_bytes(path.read_bytes())
b=json.loads(archive.read_text());original=copy.deepcopy(b);changed={17,52,70,74,75};qs={int(q['id'][-3:]):q for q in b['questions']}
accepted={q['id']:question_hash(q) for n,q in qs.items() if n not in changed};assert len(accepted)==71
for n in changed:
 q=qs[n];q['version']+=1;q['status']='draft';q['reviewIds']=[]
 q['revisionAuthors']=list(dict.fromkeys(q.get('revisionAuthors',[])+[AUTHOR]))
def option(n,oid,text,reason):
 q=qs[n];next(o for o in q['options'] if o['id']==oid)['text']=text;q['solution']['optionExplanations'][oid]=reason
q=qs[17];oldConflict=q.pop('conflictResolution')
c=q['citations'][0];c.update(kind='statement',role='explicit',locator='Lecture 30, physical PDF page 899, printed footer 13: first bullet defines an optimal policy using highest possible expected cumulative reward; the final Q* definition also explicitly says expected cumulative reward.',evidenceText='The optimal-policy definition explicitly says “highest possible expected cumulative reward”. The Q* definition likewise says “the expected cumulative reward” of taking an action and then obeying the optimal policy.')
option(52,'o4','At the external 50-step limit, the Q-learning target must discard its successor-value term because any stopped rollout is a true terminal task state.','A time-limit truncation of this continuing task does not itself remove the successor return; true terminal and truncated transitions require different bootstrap treatment.')
# The added alternative uses the already captured primary time-limit evidence.
timeEvidence=next(e for e in qs[8].get('externalEvidence',[]) if e.get('section')=='timeLimits')
q=qs[52]
if not any(e.get('section')=='timeLimits' for e in q['externalEvidence']):q['externalEvidence'].append(copy.deepcopy(timeEvidence))
c=next(c for c in qs[70]['citations'] if c['physicalPage']==909)
c.update(kind='statement',locator='Lecture 30, physical PDF page 909, printed footer 23: FetchReachDense-v4 task-description bullets and the Action space section, a = [dx, dy, dz, gripper_open_close], each in [−1,1]. The separate installation command is not the evidence for this claim.',evidenceText='FetchReachDense-v4 uses a Fetch arm and the stated task is to move the gripper to a randomly placed target position in 3D space. The Action space section displays a = [dx, dy, dz, gripper_open_close], each in [−1,1]. Whether the fourth component is effective is separately qualified using the linked implementation evidence.')
c=next(c for c in qs[74]['citations'] if c['physicalPage']==909)
c.update(kind='equation',locator='Lecture 30, physical PDF page 909, printed footer 23: bottom Reward bullet, r = −distance(end_effector, target) per step. Nonpositivity follows from nonnegative Euclidean distance; this is not the pip-installation block.',evidenceText='Reward: r = −distance(end_effector, target) per step. The adjacent prose calls it always negative; the question uses the qualified nonpositive premise, including zero at exact goal coincidence.')
option(75,'o2','make constructs the instance; reset returns only the initial observation; step(action) returns observation, reward, terminated, truncated and info; render displays the task; reward-history plotting is separate.','The source uses the current reset signature returning observation and info, not an observation-only legacy signature. The other described roles do not fix that signature error.')
option(75,'o3','make constructs the instance; reset returns observation and info; step(action) advances the task; each render call then performs one additional physics step before displaying it; reward-history plotting is separate.','The rendering call displays the current task according to its rendering mode; it is not an extra environment step or action transition.')
option(75,'o4','make constructs the instance; reset returns observation and info; step(action) advances the task; render plots the training loop’s saved reward history, so a separate Matplotlib history plot is unnecessary.','Environment rendering displays the task rather than the training loop’s separate reward-history list. Plotting that list with Matplotlib is a different analysis operation.')
for n in changed:
 q=qs[n];q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']]
 assert q['correctOptionIds']==next(x for x in original['questions'] if x['id']==q['id'])['correctOptionIds']
for q in b['questions']:
 if q['id'] in accepted:
  assert question_hash(q)==accepted[q['id']]
  assert q==next(x for x in original['questions'] if x['id']==q['id'])
schema=json.loads((R/'data/schema.question.json').read_text());errors=[e for q in b['questions'] for e in schema_errors(q,schema)];assert not errors,errors
path.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for n in sorted(changed):
 q=qs[n];r={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in r['citations']:c.pop('evidenceText',None)
 packet.append(r)
packetpath=R/'audits/blind-W06-L30-final-five.json';packetpath.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
# Keep the mistaken earlier allegation, but adjudicate it rather than asserting a nonexistent conflict.
issuespath=R/'audits/W06-L30-source-issues.json';issuesarchive=R/'audits/batch-history/W06-L30-source-issues-before-final-five.json'
if not issuesarchive.exists():issuesarchive.write_bytes(issuespath.read_bytes())
issues=json.loads(issuesarchive.read_text());oldIssue=next(x for x in issues['issues'] if x['physicalPage']==899)
oldIssue['priorAnnotation']=copy.deepcopy(oldIssue)
oldIssue.update(description='The source explicitly defines optimal policy and Q* in terms of expected cumulative reward.',qualification='A poor individual realization does not refute optimal expected return. This is an interpretation of the source, not a correction of an omitted expectation.',status='Earlier author conflict allegation withdrawn after independent review and renewed pixel inspection; no global source-resolution claim.')
issuespath.write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
adjudication={'questionId':qs[17]['id'],'previousVersion':2,'revisedVersion':3,'sourceId':'lectures','sourceSha256':qs[17]['citations'][0]['sourceSha256'],'physicalPage':899,'withdrawnConflictMetadata':oldConflict,'finding':'Both relevant source bullets already explicitly say expected. The old conflict label was an author annotation error; the learner-facing key and interpretation remain correct.','evidence':'Actual page 899 re-viewed at 1800×1013 during repair; independent v2 review flags the same issue.','authorId':AUTHOR,'recordedAt':now}
(R/'audits/W06-L30-Q017-source-adjudication.json').write_text(json.dumps(adjudication,ensure_ascii=False,indent=2)+'\n')
manifest={'frozenAt':now,'authorId':AUTHOR,'batchId':'W06-L30','changedCount':5,'totalQuestions':76,'preservedAcceptedCount':71,'preservedAcceptedHashes':accepted,'blindPacketPath':str(packetpath.relative_to(R)),'blindPacketSha256':hashlib.sha256(packetpath.read_bytes()).hexdigest(),'archivePath':str(archive.relative_to(R)),'questions':[{'id':qs[n]['id'],'version':qs[n]['version'],'questionSha256':question_hash(qs[n])} for n in sorted(changed)],'authorChecks':{'allQuestionSchemasPass':True,'acceptedObjectsIdentical':71,'changedKeysUnchanged':5,'sourcePagesReinspected':[899,909,917]},'independentReviewRequired':True,'note':'Four items advance v2→v3; the newer Q075 advances v1→v2. No self-approvals.'}
(R/'audits/W06-L30-final-five-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'changed':5,'preserved':71,'sha256':manifest['blindPacketSha256'],'versions':[(qs[n]['id'],qs[n]['version']) for n in sorted(changed)]}))
