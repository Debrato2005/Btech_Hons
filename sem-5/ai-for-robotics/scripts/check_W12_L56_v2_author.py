#!/usr/bin/env python3
"""Exact supplied-state/scheduling/graph checks in default Python stdlib only."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,random,itertools,datetime,sys
R=Path(__file__).resolve().parents[1];B='W12-L56';b=json.loads((R/f'data/question-batches/{B}.json').read_text());n=json.loads((R/f'audits/{B}-v2-author-repair-notes.json').read_text());Q={q['id']:q for q in b['questions']};checks=[]
def ck(s,v):assert v,s;checks.append(s)
def trace(clear=True,filter_old=True,truncate=True,queued=2,late=1,new=2,played=1):
 heard=['a'+str(i+1)for i in range(played)];queue=['a'+str(played+i+1)for i in range(queued)];extent=(played+queued)*20;cancelled={'R1'}
 if clear:queue=[]
 if truncate:extent=played*20
 for i in range(late):
  label='a'+str(played+queued+i+1)
  if not filter_old:queue.append(label)
 context=['earlier','R1','U2'];queue+=['b'+str(i+1)for i in range(new)]
 if queue:heard.append(queue.pop(0))
 return heard,queue,extent,context,cancelled
ck('Correct interruption state',trace()==(['a1','b1'],['b2'],20,['earlier','R1','U2'],{'R1'}))
ck('Omitted queue-clear distractor',trace(clear=False)[:3]==(['a1','a2'],['a3','b1','b2'],20))
ck('Omitted response-filter distractor',trace(filter_old=False)[:3]==(['a1','a4'],['b1','b2'],20))
ck('Omitted truncation distractor',trace(truncate=False)[:3]==(['a1','b1'],['b2'],60))
ck('Preserved intended interruption key',Q[B+'-P1789-Q04']['correctOptionIds']==['o2'])
payload=640*480*(3+2);audio=48000;cap=40000000
ck('Image-pair payload',payload==1536000);ck('A transport fails',30*payload+audio==46128000>cap);ck('B/C transport fits',20*payload+audio==30768000<cap)
service=F(80,1000);post=F(20,1000);f=20;period=F(1,f)
ck('Worker service capacity',1/service==F(25,2));ck('FIFO backlog rate',F(f)-1/service==F(15,2));ck('Latest-only bound',period+service+post==F(150,1000))
# Periodic deterministic schedules; equality arrivals are visible at a service start.
def ages_fifo(f,t,p,count):
 arrivals=[F(k,f)for k in range(count)];start=F(0);ages=[]
 for arrival in arrivals:
  start=max(start,arrival);end=start+t;ages.append(end+p-arrival);start=end
 return ages
def ages_latest(f,t,p,count):
 start=F(0);ages=[];used=[]
 for _ in range(count):
  index=int(start*f);capture=F(index,f)
  if used and index<=used[-1]:index=used[-1]+1;capture=F(index,f);start=max(start,capture)
  used.append(index);ages.append(start+t+p-capture);start+=t
 return ages,used
fifo=ages_fifo(20,service,post,20);latest,used=ages_latest(20,service,post,500)
ck('FIFO first three ages',fifo[:3]==[F(1,10),F(13,100),F(16,100)]);ck('FIFO violates freshness',fifo[2]>F(15,100));ck('Latest actual max within bound',max(latest)<=F(15,100));ck('Latest drops unprocessed arrivals',used[2]==3 and len(set(used))==500)
ck('Sustained candidate selection',Q[B+'-P1798-Q05']['correctOptionIds']==['o2'])
# Boolean required-input policy is supplied, not inferred from arrow existence.
def graph(depth=True,color=True,detector=True,emotion=True,dialogue=True,audio_in=True):
 face=depth and color and detector;annotation=face;emotion_out=emotion and color and face;text=dialogue and audio_in
 return dict(face=face,annotation=annotation,emotion=emotion_out,speech_text=text,response_text=text)
D=graph(depth=False);E=graph(emotion=False)
ck('D depth loss propagation',D==dict(face=False,annotation=False,emotion=False,speech_text=True,response_text=True));ck('E preserves annotation',E==dict(face=True,annotation=True,emotion=False,speech_text=True,response_text=True));ck('Diagnostic annotation distinction',not D['annotation']and E['annotation']);ck('Graph new key',Q[B+'-P1795-Q09']['correctOptionIds']==['o1'])
ages={F('9.50'):F(10)-F('9.50'),F('9.90'):F(10)-F('9.90'),F('9.75'):F(10)-F('9.75')};ck('Labeled freshness ages',list(ages.values())==[F('.50'),F('.10'),F('.25')]);ck('Unique eligible observation',[t for t,s in[(F('9.50'),F('.95')),(F('9.90'),F('.70')),(F('9.75'),F('.80'))]if F(10)-t<=F('.30')and s>=F('.75')]==[F('9.75')])
ck('Lower-row exact source order','Speech (beside Realtime) → Language → Speech (beside Robot)'in next(o['text']for o in Q[B+'-P1794-Q01']['options']if o['id']=='o3'))
ck('Camera citation triangulation',{c['physicalPage']for c in Q[B+'-P1779-Q03']['citations']}=={1779,1781,1782})
rng=random.Random(56022026);count=0
for _ in range(1000):
 f=rng.randint(2,50);t=F(rng.randint(10,150),1000);p=F(rng.randint(0,40),1000);aa,used=ages_latest(f,t,p,50);assert max(aa)<=F(1,f)+t+p;count+=1;assert len(used)==len(set(used));count+=1
 played=rng.randint(0,10);new=rng.randint(1,5);r=trace(queued=rng.randint(0,10),late=rng.randint(0,5),new=new,played=played);assert r[2]==played*20 and r[0][-1]=='b1';count+=1;assert r[1]==['b'+str(i)for i in range(2,new+1)]and 'U2'in r[3];count+=1
 args=[bool(rng.getrandbits(1))for _ in range(6)];g=graph(*args);assert (not g['face'])or(args[0]and args[1]and args[2]);count+=1;assert g['speech_text']==g['response_text']==(args[4]and args[5]);count+=1
for i in n['changedQuestionIds']:
 q=Q[i];ck(i+' complete rationales',set(q['solution']['optionExplanations'])=={o['id']for o in q['options']});ck(i+' formula variable/unit binding',all(set(f['variables'])==set(f['units'])and f['assumptions']for f in q['solution']['formulas']))
for i,h in n['acceptedQuestionHashes'].items():
 got=hashlib.sha256(json.dumps({k:v for k,v in Q[i].items()if k not in('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest();assert got==h
ck('59 accepted content hashes preserved',len(n['acceptedQuestionHashes'])==59)
ck('7 qualifications byte-identical',hashlib.sha256((R/f'audits/source-disputes-{B}.json').read_bytes()).hexdigest()==n['sourceQualificationsUnchangedSha256'])
out=dict(role='Author checks, not independent verification',checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),command='python scripts/check_W12_L56_v2_author.py',runtime=sys.executable,packages='Python standard library only: pathlib, fractions, json, hashlib, random, itertools, datetime, sys',checkGroups=len(checks),checks=checks,randomCases=1000,randomAssertions=count,questionBatchSha256=hashlib.sha256((R/f'data/question-batches/{B}.json').read_bytes()).hexdigest(),scope='Supplied state, scheduling and graph models; no ROS, DeepFace, model, audio, API or hardware run.')
(R/f'audits/{B}-v2-author-checks.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print('PASS',len(checks),'groups and',count,'varied assertions')
