"""Execute unmodified pure engine cells, not Ollama installation or live model calls."""
import json,math,hashlib,random,datetime,ast
from pathlib import Path
from dataclasses import dataclass,field
from typing import Literal
from types import SimpleNamespace
import numpy as np
from pydantic import BaseModel,Field,ValidationError
R=Path(__file__).resolve().parents[1];p=R/'sources/supplemental/L50-official-week10_lecture50.ipynb';nb=json.loads(p.read_text());ns=globals();checks=[]
def ck(name,value):assert value,name;checks.append(name)
src7=''.join(nb['cells'][7]['source']);tree=ast.parse(src7);node=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='EmotionAnalysis');exec(compile(ast.Module(body=[node],type_ignores=[]),str(p)+':cell7:EmotionAnalysis','exec'),ns)
for i in [9,11,13,17]:exec(compile(''.join(nb['cells'][i]['source']),str(p)+f':cell{i}','exec'),ns)
r=RobotEmotionEngine();h=HumanEmotionEngine();ck('initial robot neutral and zero resultant',r.active_mood=='NEUTRAL'and r.state_r==0);ck('initial human neutral',h.active_mood=='NEUTRAL')
r.change('happy',75);ck('complement pair',r.emotions['sad']==25);ck('signed opposite vectors reinforce centered happy deviation',math.isclose(r.state_r,50)and math.isclose(r.state_theta,112)and r.active_mood=='HAPPY')
r.change('happy',150);ck('clip above100',r.emotions['happy']==100 and r.emotions['sad']==0);r.change('happy',-20);ck('clip below0',r.emotions['happy']==0 and r.emotions['sad']==100)
r=RobotEmotionEngine();r.change('happy',54);ck('r8 neutral',math.isclose(r.state_r,8)and r.active_mood=='NEUTRAL');r.change('happy',56);ck('r12 nonneutral',math.isclose(r.state_r,12)and r.active_mood=='HAPPY')
r=RobotEmotionEngine();s=r.state_r;drain_battery(r);ck('fresh tired update',r.emotions['fresh']==78 and r.emotions['tired']==22);ck('fresh tired absent from mood axes',r.state_r==s)
for _ in range(100):drain_battery(r)
ck('fresh floor10',r.emotions['fresh']==10 and r.emotions['tired']==90)
a=EmotionAnalysis(emotion='happy',confidence=.5,valence=.6,arousal=-.4,explanation='Synthetic test');apply_analysis_to_human_engine(a,h);ck('confidence attenuates human values',h.emotions=={'happy':65,'sad':35,'friendly':60,'distant':40})
a=EmotionAnalysis(emotion='sad',confidence=.2,valence=-1,arousal=1,explanation='Synthetic test');r=RobotEmotionEngine();update_robot_policy(a,r);ck('low confidence branch first',r.emotions['curious']==62 and r.emotions['welcome']==50)
a=EmotionAnalysis(emotion='sad',confidence=.8,valence=-1,arousal=1,explanation='Synthetic test');r=RobotEmotionEngine();update_robot_policy(a,r);ck('sad response is supportive not copied',r.emotions['welcome']==88 and r.emotions['friend']==82 and r.emotions['sad']==50)
m=ConversationMemory()
for i in range(8):m.add_turn(str(i),'r'+str(i))
ck('12 messages not12 paired turns',len(m.history)==12 and m.turn_count==8 and m.history[0]['content']=='2');ck('recent6 messages means3 complete pairs',len(m.history[-6:])==6);ck('generation8 messages means4 complete pairs',len(m.history[-8:])==8)
try:EmotionAnalysis(emotion='joy',confidence=1,valence=0,arousal=0,explanation='Synthetic');ok=False
except ValidationError:ok=True
ck('label validation',ok)
try:EmotionAnalysis(emotion='neutral',confidence=1.1,valence=0,arousal=0,explanation='Synthetic');ok=False
except ValidationError:ok=True
ck('confidence bounds',ok)
rng=random.Random(50000)
for _ in range(5000):
 v=rng.uniform(-1,1);a=rng.uniform(-1,1);c=rng.random();ana=EmotionAnalysis(emotion='neutral',confidence=c,valence=v,arousal=a,explanation='Synthetic');h=HumanEmotionEngine();apply_analysis_to_human_engine(ana,h)
 assert math.isclose(h.emotions['happy'],50+50*c*v)and math.isclose(h.emotions['friendly'],50-50*c*a)
 assert math.isclose(h.emotions['happy']+h.emotions['sad'],100)and math.isclose(h.emotions['friendly']+h.emotions['distant'],100)
 x=sum((h.emotions[e]-50)*math.cos(math.radians(t))for e,t in h.emotion_axis.items());y=sum((h.emotions[e]-50)*math.sin(math.radians(t))for e,t in h.emotion_axis.items());assert math.isclose(h.state_r,math.hypot(x,y))
ck('5000 synthetic mappings and vector reconstructions',True)
ck('half range is not midpoint',(80-20)/2==30 and (80+20)/2==50);ck('bounded half range cannot exceed55',(100-0)/2==50);ck('angle half span differs from midpoint',(140-20)/2==60 and (140+20)/2==80)
ck('hypot3,4',math.hypot(3,4)==5);ck('classifier128to8weights',128*8+8==1032);ck('classifier128to7weights',128*7+7==903)
# Plot the exact original helper with synthetic states, never a person's photograph.
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from IPython.display import clear_output,display
exec(compile(''.join(nb['cells'][19]['source']),str(p)+':cell19','exec'),ns)
r=RobotEmotionEngine();r.change('happy',75);h=HumanEmotionEngine();apply_analysis_to_human_engine(EmotionAnalysis(emotion='neutral',confidence=.5,valence=.6,arousal=-.4,explanation='Synthetic'),h)
f=plt.figure(figsize=(13,6));_plot_engine(f.add_subplot(121,projection='polar'),'Synthetic robot',r,'Result');_plot_engine(f.add_subplot(122,projection='polar'),'Synthetic model input',h,'Result');f.tight_layout();f.savefig(R/'audits/W10-L50-reproduced-engine.png');plt.close(f)
report={'batchId':'W10-L50','sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sourceRef':'a70ba559deefa15abd9045756f3c76f0bada8abd','executedExactCells':[9,11,13,17,19],'exactClassExtractedFromCell7':'EmotionAnalysis','notExecuted':['OS installation cell1','Ollama service and model download','live LLM inference','interactive Colab UI'],'executionScope':'Original deterministic classes and functions, with synthetic inputs; not an end-to-end model or browser test.','checks':checks,'checkGroups':len(checks),'variedTrials':5000,'allPassed':True,'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()};(R/'audits/W10-L50-author-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
