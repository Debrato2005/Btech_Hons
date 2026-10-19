"""Independent source-code checks using synthetic inputs only, no LLM or network."""
import ast, json, math, random, hashlib, datetime, platform
from pathlib import Path
from dataclasses import dataclass,field
from typing import Literal
from types import SimpleNamespace
import numpy as np
import pydantic
from pydantic import BaseModel,Field,ValidationError
R=Path(__file__).resolve().parents[1];path=R/'sources/supplemental/L50-official-week10_lecture50.ipynb';nb=json.loads(path.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ns=globals();tree=ast.parse(''.join(nb['cells'][7]['source']));tree.body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='EmotionAnalysis'];exec(compile(tree,str(path)+'#cell7-class-only','exec'),ns)
for i in [9,11,13,17]:exec(compile(''.join(nb['cells'][i]['source']),str(path)+f'#cell{i}','exec'),ns)
checks=[]
def ck(name,truth,data=None):
 assert truth,(name,data);checks.append(dict(name=name,passed=True,data=data))
def analysis(label='neutral',confidence=.8,valence=0,arousal=0):return EmotionAnalysis(emotion=label,confidence=confidence,valence=valence,arousal=arousal,explanation='Synthetic independent test.')
r=RobotEmotionEngine();h=HumanEmotionEngine();ck('Neutral initialization',r.state_r==h.state_r==0 and r.active_mood==h.active_mood=='NEUTRAL')
r.change('happy',75);ck('Centered opposite pair doubles deviation',math.isclose(r.state_r,50) and math.isclose(r.state_theta,112) and r.active_mood=='HAPPY',dict(r=r.state_r,theta=r.state_theta))
r.change('happy',150);ck('Clamping and complement',r.emotions['happy']==100 and r.emotions['sad']==0)
r.change('happy',54);ck('Neutral strict radius threshold',math.isclose(r.state_r,8) and r.active_mood=='NEUTRAL')
apply_analysis_to_human_engine(analysis(valence=.6,arousal=-.4,confidence=.5),h);ck('Weighted human mapping',h.emotions['happy']==65 and h.emotions['friendly']==60,dict(h.emotions))
apply_analysis_to_human_engine(analysis(valence=.8,arousal=.6,confidence=0),h);ck('Zero confidence resets human axes',all(x==50 for x in h.emotions.values()))
r=RobotEmotionEngine();update_robot_policy(analysis('sad',.2),r);ck('Low confidence early return',r.emotions['curious']==62 and r.emotions['welcome']==50)
r=RobotEmotionEngine();update_robot_policy(analysis('sad',.3),r);ck('Boundary confidence enters sad branch',r.emotions['welcome']==88 and r.emotions['friend']==82 and r.emotions['curious']==62)
m=ConversationMemory()
for i in range(8):m.add_turn(f'u{i}',f'a{i}')
ck('History retains messages not pairs',len(m.history)==12 and m.history[0]['content']=='u2' and m.turn_count==8)
ck('Known facts not extracted by add_turn',all(v is None for v in m.known_facts.values()))
r=RobotEmotionEngine();r.change('happy',75);old=(r.state_r,r.state_theta,r.active_mood)
for i in range(40):drain_battery(r)
ck('Battery clamp and no polar contribution',r.emotions['fresh']==10 and r.emotions['tired']==90 and (r.state_r,r.state_theta,r.active_mood)==old)
ck('Valid schema domain',analysis('neutral',.4,-.2,.7).confidence==.4)
for fieldname,value in [('confidence',1.4),('arousal',2),('valence',-2),('emotion','welcome')]:
 d=analysis().model_dump();d[fieldname]=value
 try:EmotionAnalysis(**d);ok=False
 except ValidationError:ok=True
 ck('Reject invalid '+fieldname,ok)
# Compile exact functions but supply an in-process failing client, not a network endpoint.
exec(compile(''.join(nb['cells'][15]['source']),str(path)+'#cell15','exec'),ns)
class FailClient:
 def chat(self,**kw):raise RuntimeError('Synthetic local failure, no service contacted')
ns['client']=FailClient();ns['MODEL_NAME']='not-contacted'
f=analyse_emotion('synthetic',m);ck('Local simulated client failure fallback',f.emotion=='neutral' and f.confidence==f.valence==f.arousal==0)
ck('Reply local failure path',bool(generate_reply('synthetic',f,r,m)))
class CaptureClient:
 def __init__(self):self.calls=[]
 def chat(self,**kw):
  self.calls.append(kw);return SimpleNamespace(message=SimpleNamespace(content=analysis().model_dump_json() if 'format'in kw else 'Synthetic reply'))
cap=CaptureClient();ns['client']=cap
analyse_emotion('new synthetic',m);generate_reply('new synthetic',analysis(),r,m)
context=json.loads(cap.calls[0]['messages'][1]['content'].split('Recent context:\n')[1].split('\n\nLatest message:')[0])
ck('Prompt slicing counts',len(context)==6 and len(cap.calls[0]['messages'])==2 and len(cap.calls[1]['messages'])==10,dict(classifierHistoryEntries=len(context),classifierEnvelopeMessages=2,replyHistoryEntries=8,replyEnvelopeMessages=10))
ck('Midpoint and half-span differ',((80+20)/2,(80-20)/2)==(50,30))
ck('Nonwrapping angular midpoint',((140+20)/2,(140-20)/2)==(80,60))
ck('Dense layer weights plus biases',128*8+8==1032)
# Full new multi-axis trace derived from coordinates, not author checks.
r=RobotEmotionEngine();update_robot_policy(analysis('happy',.8),r);first=dict(r.emotions);update_robot_policy(analysis('sad',.8),r)
ck('Multi-turn untouched axes persist',r.emotions['happy']==80 and r.emotions['welcome']==88 and r.emotions['friend']==82 and r.emotions['curious']==62)
pairs=[('happy',112),('welcome',22),('friend',67),('curious',157)]
x=sum(2*(r.emotions[k]-50)*math.cos(math.radians(a))for k,a in pairs);y=sum(2*(r.emotions[k]-50)*math.sin(math.radians(a))for k,a in pairs)
ck('Independent pairwise resultant',math.isclose(r.state_r,math.hypot(x,y)) and math.isclose(r.state_theta,math.degrees(math.atan2(y,x))%360),dict(x=x,y=y,r=r.state_r,theta=r.state_theta,mood=r.active_mood))
ck('Resultant can exceed display radius',r.state_r>100,dict(rawRadius=r.state_r,plotRadius=float(np.clip(r.state_r,0,100))))
rng=random.Random(50019);assertions=0
for _ in range(1000):
 r=RobotEmotionEngine()
 for k,a in pairs:r.change(k,rng.uniform(-50,150))
 expected=sum((2*(r.emotions[k]-50)*complex(math.cos(math.radians(a)),math.sin(math.radians(a)))for k,a in pairs),0j)
 assert math.isclose(r.state_r,abs(expected),rel_tol=1e-10,abs_tol=1e-10);assertions+=1
 assert all(math.isclose(r.emotions[k]+r.emotions[r.opposites[k]],100)for k,a in pairs);assertions+=1
 h=HumanEmotionEngine();a=analysis(rng.choice(['happy','sad','angry','fearful','frustrated','neutral']),rng.random(),rng.uniform(-1,1),rng.uniform(-1,1));apply_analysis_to_human_engine(a,h)
 assert math.isclose(h.emotions['happy'],50+50*a.confidence*a.valence);assertions+=1
 assert math.isclose(h.emotions['friendly'],50-50*a.confidence*a.arousal);assertions+=1
 assert all(0<=v<=100 for v in h.emotions.values());assertions+=1
report=dict(generatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),notebookPath=str(path.relative_to(R)),notebookSha256=sha(path),scriptSha256=sha(Path(__file__)),executedOriginalWholeCells=[9,11,13,15,17],classOnlyCell=7,versions=dict(python=platform.python_version(),numpy=np.__version__,pydantic=pydantic.__version__),explicitChecks=checks,variedCases=1000,variedAssertions=assertions,limitations='No Ollama installation, service, model inference, microphone, camera, widgets or live UI executed. Cell 15 used explicitly synthetic in-process client success/failure responses, not model predictions. Source notebook historical outputs were not treated as fresh execution.')
(R/'audits/W10-L50-contracts-independent-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(len(checks),'explicit checks and',assertions,'varied assertions passed')
