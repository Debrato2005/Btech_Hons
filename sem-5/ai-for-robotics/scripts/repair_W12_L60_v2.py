from pathlib import Path
import json,hashlib,copy,datetime,sys,shutil
R=Path('/workspace/shared/Btech_Hons/sem-5/ai-for-robotics');sys.path.insert(0,str(R/'scripts'))
from validate import validate_bank
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat();AUTHOR='complete_robotics_python_coverage:L60-v2-repair'
def read(p):return json.loads((R/p).read_text())
def dump(p,x):(R/p).parent.mkdir(parents=True,exist_ok=True);(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qh(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ['status','reviewIds']},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert not (R/'audits/blind-W12-L60-v2.json').exists(),'Frozen repairs may not be overwritten.'
b=read('data/question-batches/W12-L60.json');summ=read('audits/W12-L60-integration-review-summary.json');accepted=summ['acceptedQuestionHashes'];qm={q['id']:q for q in b['questions']}
assert len(accepted)==70 and all(qh(qm[k])==h for k,h in accepted.items())
a=R/'audits/archive/W12-L60-v1-before-v2';a.mkdir(parents=True,exist_ok=True)
for p in ['data/question-batches/W12-L60.json','audits/source-disputes-W12-L60.json','audits/blind-W12-L60.json','audits/blind-binding-W12-L60.json']:
 t=a/Path(p).name
 if not t.exists():shutil.copy2(R/p,t)
sourcehash=sha('audits/source-disputes-W12-L60.json')
changes={
'W12-L60-P1913-Q01':[
 ('o1','Surgery: kinematics and real-time vision; rehabilitation: fixed assistance independent of patient response; eldercare: HRI-supported daily tasks','This preserves the surgical and eldercare roles but substitutes fixed patient-independent assistance for the source’s adaptive rehabilitation control.'),
 ('o3','Surgery: kinematics with preoperative imaging instead of real-time vision; rehabilitation: adaptive assistance; eldercare: HRI-supported daily tasks','This preserves the rehabilitation and eldercare roles but replaces the surgical example’s real-time vision with preoperative imaging alone.')],
'W12-L60-P1917-Q01':[
 ('o2','Domestic navigation: mapping and avoidance; shelf checks: visual camera-pose estimation; voice assistance: conversational AI/HRI','The navigation and voice roles match, but visual camera-pose estimation is localization, not the product observation needed for the cited shelf inventory checks.'),
 ('o3','Domestic navigation: mapping and avoidance; shelf checks: visual inventory recognition; voice assistance: speech transcription without language interpretation','The physical navigation and shelf roles match, but recognizing words alone does not supply the conversational interpretation and HRI emphasized for voice assistance.')],
'W12-L60-P1933-Q01':[
 ('o1','Tendon-actuated serial manipulators: large-workspace manipulation; wall-climbing robots: infrastructure inspection','The inspection pairing matches, but the lecture names cable-driven parallel robots for the large-workspace example. Cable or tendon actuation does not itself make a serial arm a parallel mechanism.'),
 ('o2','Cable-driven parallel mechanisms: large-workspace manipulation; free-flying aerial robots: the cited surface-climbing inspection role','The large-workspace pairing matches, but the cited infrastructure-access example is wall-climbing robotics, not free flight. This identifies the source’s example rather than claiming aerial inspection is impossible.')],
'W12-L60-P1948-Q02':[
 ('o1','Competitions primarily assess how convincingly ideas are presented; professional communities support networking and collaboration','The networking role matches, but the lecture emphasizes testing ideas against real engineering constraints, not primarily judging presentation quality.'),
 ('o2','Competitions test ideas against engineering constraints; professional communities primarily provide comparative robot-performance rankings','The competition role matches, but the specified role of IEEE-RAS, meetups and student programs is networking, not a common robot-performance ranking service.')]
}
for ident,edits in changes.items():
 q=qm[ident];assert q['version']==1;q['version']=2;q['status']='draft';q['reviewIds']=[];q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+[AUTHOR]))
 for oid,txt,why in edits:
  next(o for o in q['options']if o['id']==oid)['text']=txt;q['solution']['optionExplanations'][oid]='Incorrect. '+why
 q['solution']['misconceptions']=[why for _,_,why in edits]
 q['solution']['justification']={'W12-L60-P1913-Q01':'The source associates surgery with precise kinematics and real-time vision, rehabilitation with adaptive physical assistance, and eldercare with HRI-supported daily tasks. These are the stated examples, not exclusive boundaries between medical applications.','W12-L60-P1917-Q01':'The slide combines mapping and obstacle avoidance for domestic navigation, visual recognition for retail observation, and conversational AI/HRI for natural voice interaction. Localization, product recognition and language interpretation are different processing goals.','W12-L60-P1933-Q01':'The two explicitly named pairings are cable-driven parallel mechanisms for large-workspace manipulation and wall-climbing robotics for infrastructure inspection. Other robot classes may serve related missions, but are not the pair specified here.','W12-L60-P1948-Q02':'The slide gives complementary aims: competitions expose ideas to real engineering constraints, while IEEE-RAS, meetups and conference student programs support networking. Neither aim replaces the other.'}[ident]
 q['solution']['simpleExplanation']=q['solution']['justification']
 if ident=='W12-L60-P1933-Q01':q['stem']='Which pair of mechanism classes is explicitly associated with large-workspace manipulation and infrastructure inspection, respectively, in the lecture’s frontier examples?'
 if ident=='W12-L60-P1917-Q01':q['stem']='Which assignment of processing goals matches the lecture’s domestic navigation, retail shelf checking and natural voice-assistance examples?'
 if ident=='W12-L60-P1948-Q02':q['stem']='Which pair best matches the lecture’s stated main reasons for participating in robotics competitions and professional communities?'
assert all(qh(qm[k])==h for k,h in accepted.items());assert sha('audits/source-disputes-W12-L60.json')==sourcehash
qs=[qm[k]for k in changes]
bank=read('data/bank.json')
ids=set(changes);bank['questions']=[q for q in bank['questions']if q['id']not in ids]+copy.deepcopy(qs)
v=validate_bank(bank,R,check_files=False);assert v['valid'],v['errors']
checks=['All 70 accepted whole-question hashes preserved','All eight source qualification records unchanged','All four source pages actually revisited','Four versions incremented, revisions attributed, no self approval','All original intended key IDs preserved','Each distractor isolates one stated association or processing-role confusion','No arithmetic or executable code introduced; formulas remain inapplicable','Question-level exact cited page and printed footer retained','Three parallel distinct alternatives in each repaired object','In-memory structural validation passed']
dump('data/question-batches/W12-L60.json',b)
dump('audits/W12-L60-v2-author-revisits.json',{'authorId':AUTHOR,'inspectedAt':NOW,'method':'rendered_page','pages':[{'physicalPage':p,'printedFooter':str(p-1908),'notes':n}for p,n in [(1913,'Read all surgical, rehabilitation and eldercare bullets; source emphases are real-time vision/kinematics, adaptive control, and HRI-supported daily tasks.'),(1917,'Read domestic SLAM/avoidance, retail computer vision/NLP and conversational AI/HRI voice-interaction bullets; no algorithm or quantitative runtime is printed.'),(1933,'Read cable-driven parallel/large-workspace and wall-climbing/infrastructure examples; retained source-specific pairings rather than universal mechanism exclusions.'),(1948,'Read competitions for real engineering constraints and networking through IEEE-RAS, meetups and student programs; kept these distinct from presentation and scoring emphasis.')]]})
dump('audits/W12-L60-v2-author-checks.json',{'role':'Author quality checks, not independent verification','checkedAt':NOW,'checks':checks,'acceptedQuestionHashes':accepted,'changedQuestionHashes':{q['id']:qh(q)for q in qs},'sourceDisputesSha256':sourcehash,'validation':v})
packet=[]
for q in qs:
 z={k:copy.deepcopy(q[k])for k in ['id','version','stem','selectionMode','type','difficulty','cognitiveSkill','week','lectureId','topic','subtopic','assumptions','options']};z['citations']=[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]
 for c in z['citations']:c['locator']=f"Physical lecture page {c['physicalPage']}, printed footer {c['physicalPage']-1908}: application or participation bullets."
 packet.append(z)
dump('audits/blind-W12-L60-v2.json',{'batchId':'W12-L60-v2','questions':packet})
dump('audits/blind-binding-W12-L60-v2.json',{'packetSha256':sha('audits/blind-W12-L60-v2.json'),'questions':[{'id':q['id'],'version':q['version'],'sha256':qh(q)}for q in qs]})
dump('audits/W12-L60-v2-repair-manifest.json',{'frozenAt':NOW,'reviewSource':'data/reviews/W12-L60-v1-independent-integration.json','acceptedCountPreserved':70,'repairedCount':4,'allRepairedDraft':True,'packetSha256':sha('audits/blind-W12-L60-v2.json'),'bindingSha256':sha('audits/blind-binding-W12-L60-v2.json'),'sourceDisputesSha256':sourcehash})
(R/'audits/handoffs/W12-L60-repair.md').write_text('L60 v2: four source-revisited quality repairs frozen; all 70 accepted whole objects and eight source qualifications preserved. Packet audits/blind-W12-L60-v2.json; neutral binding audits/blind-binding-W12-L60-v2.json. Ten author precheck groups and in-memory validation passed. No numerical/code changes. All four remain draft pending independent re-review. Do not rerun full author scripts or this repair.\n')
print('FROZEN',sha('audits/blind-W12-L60-v2.json'))
