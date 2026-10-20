#!/usr/bin/env python3
"""Default-environment author checks of supplied examples; NOT independent review or hardware/API execution."""
from pathlib import Path
import json,sys,datetime,hashlib,math,random
from fractions import Fraction as F
R=Path(__file__).resolve().parents[1];B='W12-L56';start=datetime.datetime.now(datetime.timezone.utc).isoformat()
b=json.loads((R/f'data/question-batches/{B}.json').read_text());Q={q['id'].split(B+'-')[1]:q for q in b['questions']};checks=[]
def ck(name,cond,detail):
 assert cond,name
 checks.append(dict(id=f'L56-AUTHOR-{len(checks)+1:02}',name=name,detail=detail,passed=True))
def option(qid,fragment,correct):
 q=Q[qid];o=[o for o in q['options']if fragment in o['text']];assert len(o)==1,(qid,fragment)
 ck(qid+' option '+fragment,(o[0]['id']in q['correctOptionIds'])==correct,'Checked against saved instantiated option and answer binding, not displayed option position.')
def soft(z):
 m=max(z);e=[math.exp(v-m)for v in z];return[v/sum(e)for v in e]
p=soft([math.log(4),math.log(2),0]);ck('P1785-Q02 normalized exponents',all(abs(a-float(v))<1e-12 for a,v in zip(p,[F(4,7),F(2,7),F(1,7)])),'Happy4/7,neutral2/7,sad1/7; stable exponent subtraction.')
ck('P1785-Q02 raw-logit distractor',abs(math.log(4)/(math.log(4)+math.log(2))-2/3)<1e-12,'Dividing logits gives2/3, distinct from4/7.')
option('P1785-Q02','4/7',True);option('P1785-Q02','2/3',False);option('P1785-Q02','2/7',False)
ck('P1785-Q03 threshold and majority alternative',max([.6,.3,.1])<.7 and .6>.3+.1,'Argmax and majority do not meet supplied threshold; inclusive equality tested separately.')
ck('Threshold equality',F(70,100)>=F(7,10),'Supplied policy passes equality, not a source default.')
Rbyte=F(24000*16,8);N=F(24000*20,1000);chunk=Rbyte*F(20,1000)
ck('P1790-Q01 PCM dimensional conversion',Rbyte==48000 and N==480 and chunk==960,'16bits/sample=2bytes/sample;mono24000sample/s;20ms=0.020s.')
ck('P1790-Q01 both distractors',24000*16==384000 and F(384000*20,1000)==7680 and N!=chunk,'Bits mislabeled bytes versus sample count mislabeled bytes.')
option('P1790-Q01','48000 bytes/s and 960',True)
ck('P1790-Q02 underflow',max(0,200-120)==80,'80ms;0incorrectly assumes infinite buffering;200ignores initialbuffer.')
ck('P1790-Q03 queued audio',5*20==100,'100ms persists under supplied no-clear/no-overlap conditions;20countsone;0assumesclear.')
option('P1790-Q02','80 ms',True);option('P1790-Q03','100 ms',True)
def emit(events,threshold=F(3,4)):
 out=[];last=None
 for lab,score in events:
  if score>=threshold and lab!=last:out.append(lab);last=lab
 return out
E=[('neutral',F(8,10)),('neutral',F(9,10)),('sad',F(6,10)),('sad',F(85,100)),('sad',F(9,10))]
ck('P1793-Q02 exact policy trace',emit(E)==['neutral','sad'],'Rejected event does not modify state; repeated accepted label suppressed.')
ck('P1793-Q02 no-dedup distractor',[l for l,s in E if s>=F(3,4)]==['neutral','neutral','sad','sad'],'This plausible wrong output applies only the threshold.')
ck('P1793-Q02 equality and rejection state',emit([('sad',F(7,10)),('sad',F(3,4)),('neutral',F(3,4)),('neutral',F(9,10))])==['sad','neutral'],'Exact rational scores avoid floating point boundary ambiguity.')
T=max(70,110)+10+180+40
ck('P1794-Q02 parallel and wrong paths',T==340 and 70+110+10+180+40==410 and max(70,110)+10+180==300,'Criticalpath340ms;serial410ms;omitplayback300ms.')
option('P1794-Q02','340 ms',True)
Bp=640*480*(3+2);capacity=40000000;audio=48000;f=(capacity-audio)//Bp
ck('P1798-Q01 payload and maximum whole rate',Bp==1536000 and f==26 and f*Bp+audio==39984000 and (f+1)*Bp+audio>capacity,'26fits;27exceeds. Values explicitly supplied; no USB benchmark claimed.')
ck('P1798-Q01 distractor payloads',30*Bp+audio==46128000 and (capacity-audio)//(640*480*3)==43,'30fps exceeds40MB/s;43fps is RGB-only capacity with audio retained.')
option('P1798-Q01','26 frames/s',True)
mu=1/F(80,1000);backlog=30-mu
ck('P1798-Q02 service/backlog units',mu==F(25,2)and backlog==F(35,2),'12.5frames/s capacity and17.5frames/s average accumulation; arrival30Hzdoesnotraise capacity;80msisnot80Hz.')
option('P1798-Q02','12.5 frames/s',True)
def valid(now,obs,score):return score>=F(3,4)and 0<=now-obs<=F(3,10)
a=[valid(F(10),F(t),F(s))for t,s in [('9.75','.80'),('9.50','.95'),('9.90','.70')]]
ck('P1798-Q03 combined freshness/confidence',a==[True,False,False],'Ages0.25,0.50,0.10seconds; secondstale,thirdlowconfidence.')
ck('P1794-Q04 coupled stale affect and valid intent',F('5')-F('4.4')==F('.6')and not valid(F(5),F('4.4'),F('.9')),'Discard stalevisualcontext; directions remain valid; rejecting sad does not prove neutral.')
ck('Freshness boundaries',valid(F(10),F('9.7'),F('.75'))and not valid(F(10),F('10.01'),F('.9')),'Inclusive maxage/score;futuretimestamps invalid under supplied policy.')
# Exact edges manually transcribed from actual page1795; checks validate internal graph-reading consistency.
nodes={'/camera_node','/face_detection_node','/emotion_node','/tara_node','/visualization_node'}
pub={'/camera_node':['/camera/depth/image_rect_raw','/camera/color/image_raw'],'/face_detection_node':['/human_face','/human_face/annotated'],'/emotion_node':['/human_emotion'],'/tara_node':['/chatgpt_response','/speech_text']}
sub={'/camera/depth/image_rect_raw':['/face_detection_node'],'/camera/color/image_raw':['/face_detection_node','/emotion_node'],'/human_face':['/emotion_node'],'/human_face/annotated':['/visualization_node'],'/human_emotion':['/tara_node','/visualization_node'],'/chatgpt_response':['/visualization_node'],'/speech_text':['/visualization_node']}
ck('P1795-Q01/Q08 graph entities',len(nodes)==5 and len(sub)==7,'Five nodeovals, seven distinct topicnames; namespacecontainers notnodes; sixfunctionalroles onp1781cannotbeconvertedtoextraoval.')
ck('P1795-Q02 direct color recipients',set(sub['/camera/color/image_raw'])=={'/face_detection_node','/emotion_node'},'Two independently drawncolor edges.')
ck('P1795-Q03 detector outputs',set(pub['/face_detection_node'])=={'/human_face','/human_face/annotated'}and sub['/human_face']==['/emotion_node']and sub['/human_face/annotated']==['/visualization_node'],'Face/inference versus annotated/display paths.')
q=Q['P1795-Q04'];selected={o['text']for o in q['options']if o['id']in q['correctOptionIds']}
ck('P1795-Q04 all subscribers match key',selected==set(sub['/human_emotion']),'Includes curvedlower visualizationedge, notjusttara.')
ck('P1795-Q05 text outputs',set(pub['/tara_node'])=={'/chatgpt_response','/speech_text'},'Bothlead tovisualization.')
rng=random.Random(5601)
for _ in range(1000):
 z=[rng.uniform(-40,40)for j in range(7)];shift=rng.uniform(-100,100);a=soft(z);a2=soft([v+shift for v in z]);assert abs(sum(a)-1)<1e-12;assert max(abs(u-v)for u,v in zip(a,a2))<1e-12
 g,bf=rng.randrange(1000),rng.randrange(1000);assert max(0,g-bf)>=0 and max(0,g-bf)<=g
 rv,ra=rng.randrange(1000),rng.randrange(1000);serial=rv+ra;parallel=max(rv,ra);assert parallel<=serial and parallel>=rv and parallel>=ra
ck('Random invariants',True,'1000seeded cases,4000assertions:Softmaxsum/shift,finitebufferbound,parallelcriticalpathbound.')
report=dict(role='Author-side supplied-example checks, not independent verification',batchId=B,startedAt=start,completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),command='python scripts/check_W12_L56_author.py',interpreter=sys.executable,pythonVersion=sys.version,importedPackages='Python standard library only; no OpenCV, DeepFace, ROS2, OpenAI client, restricted venv, model or hardware',executionScope='Explicitly supplied numerical/state examples and manually transcribed graph consistency. No executable source program is printed. No live API, camera, microphone, humanoid or original notebook execution.',checkGroups=len(checks),checks=checks,randomCases=1000,randomAssertions=4000,graph=dict(nodes=sorted(nodes),publishers=pub,subscribers=sub),questionBatchSha256=hashlib.sha256((R/f'data/question-batches/{B}.json').read_bytes()).hexdigest())
(R/f'audits/{B}-author-checks.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print('Passed',len(checks),'groups;1000randomcases/4000assertions')
