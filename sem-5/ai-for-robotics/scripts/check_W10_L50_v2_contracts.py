"""Independent L50 revision checks from inspected notebook definitions only.
No installer, client constructor, network call, model or notebook UI is run.
"""
from pathlib import Path
import ast, json, math, random, hashlib, datetime, types, contextlib, io
from dataclasses import dataclass, field
from typing import Literal
import numpy as np
import pydantic
from pydantic import BaseModel, Field, ValidationError
R=Path(__file__).resolve().parents[1]
path='sources/supplemental/L50-official-week10_lecture50.ipynb'
raw=(R/path).read_bytes();book=json.loads(raw)
namespace=dict(math=math,np=np,json=json,dataclass=dataclass,field=field,Literal=Literal,BaseModel=BaseModel,Field=Field,MODEL_NAME='synthetic-test-no-model')
selected={7:['EmotionAnalysis'],9:['RobotEmotionEngine'],11:['HumanEmotionEngine'],13:['ConversationMemory'],15:['analyse_emotion','generate_reply'],17:['apply_analysis_to_human_engine','update_robot_policy','drain_battery'],19:['_plot_engine'],21:['submit_message','reset_demo']}
for i,names in selected.items():
 tree=ast.parse(''.join(book['cells'][i]['source']));nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names]
 assert len(nodes)==len(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),f'{path}:cell{i}','exec'),namespace)
Robot=namespace['RobotEmotionEngine'];Human=namespace['HumanEmotionEngine'];Memory=namespace['ConversationMemory'];Analysis=namespace['EmotionAnalysis'];apply=namespace['apply_analysis_to_human_engine'];policy=namespace['update_robot_policy'];drain=namespace['drain_battery']
checks=[]
def ck(name,actual,expected):
 assert actual==expected,(name,actual,expected);checks.append(dict(name=name,actual=actual,expected=expected))
def a(emotion='neutral',confidence=.8,valence=0,arousal=0):return Analysis(emotion=emotion,confidence=confidence,valence=valence,arousal=arousal,explanation='Synthetic supplied test, not inference')
r=Robot();r.change('happy',150);ck('Q022 clamp before complement',[r.emotions['happy'],r.emotions['sad']],[100.,0.])
h=Human();apply(a(valence=.6,arousal=-.4,confidence=.5),h);ck('Q023 offset and weighted mapping',[h.emotions['happy'],h.emotions['friendly']],[65.,60.])
r=Robot();policy(a('sad',.2),r);ck('Q026 low-confidence guard',[r.emotions['curious'],r.emotions['welcome'],r.emotions['friend']],[62.,50,50])
r.change('welcome',99);r.change('friend',99);policy(a('sad'),r);ck('Q027 assignment can lower values',[r.emotions['welcome'],r.emotions['friend'],r.emotions['curious']],[88.,82.,62.])
m=Memory()
for i in range(1,9):m.add_turn(f'input{i}',f'reply{i}')
ck('Q028 retention and lifetime count',[len(m.history),m.history[0]['content'],m.turn_count],[12,'input3',8])
valid=[]
for i,d in enumerate([dict(emotion='angry',confidence=.4,valence=-1.2,arousal=.7),dict(emotion='neutral',confidence=.4,valence=-.2,arousal=.7),dict(emotion='joy',confidence=.4,valence=-.2,arousal=.7),dict(emotion='sad',confidence=1.4,valence=-.2,arousal=.7)],1):
 try:Analysis(**d,explanation='demo');valid.append(i)
 except ValidationError:pass
ck('Q032 valid offered schema',[*valid],[2])
class StubClient:
 def __init__(self):self.calls=[];self.fail=False
 def chat(self,**kwargs):
  self.calls.append(kwargs)
  if self.fail:raise RuntimeError('deliberate inert failure')
  content=a().model_dump_json()if 'format'in kwargs else' synthetic reply '
  return types.SimpleNamespace(message=types.SimpleNamespace(content=content))
client=StubClient();namespace['client']=client;client.fail=True
with contextlib.redirect_stdout(io.StringIO()):fallback=namespace['analyse_emotion']('test',Memory())
ck('Q033 failure fallback',[fallback.emotion,fallback.confidence,fallback.valence,fallback.arousal],['neutral',0.,0.,0.]);client.fail=False
ck('Q043 final dense head',128*8+8,1032)
r=Robot()
for name,value in [('happy',80),('welcome',90),('friend',70)]:r.change(name,value)
x=sum((r.emotions[name]-50)*math.cos(math.radians(deg))for name,deg in r.emotion_axis.items());y=sum((r.emotions[name]-50)*math.sin(math.radians(deg))for name,deg in r.emotion_axis.items())
ck('Q066 independent vector and polar result',[round(x,2),round(y,2),round(r.state_r,2),round(r.state_theta,2),r.active_mood],[67.33,122.42,139.71,61.19,'FRIEND'])
class AxisStub:
 def __init__(self):self.annotations=[]
 def annotate(self,*args,**kwargs):self.annotations.append(kwargs)
 def __getattr__(self,key):return lambda *args,**kwargs:None
axis=AxisStub();namespace['_plot_engine'](axis,'test',r,'test');ck('Q066 plot clips only display',axis.annotations[0]['xy'][1],100.)
r=Robot();h=Human();trace=[]
for values in [('fearful',.8,-.5,.5),('sad',.30,-.6,-.4),('neutral',0,0,0)]:
 z=a(*values);apply(z,h);policy(z,r);drain(r);trace.append(dict(human=dict(h.emotions),robot=dict(r.emotions)))
ck('Q067 three-turn final state',[h.emotions['happy'],h.emotions['friendly'],r.emotions['welcome'],r.emotions['friend'],r.emotions['curious'],r.emotions['happy'],r.emotions['fresh']],[50.,50.,88.,82.,62.,50,74.])
ck('Q067 confidence equality enters sad branch',trace[1]['robot']['welcome'],88.)
m=Memory()
for i in range(1,8):m.add_turn(f'input{i}',f'reply{i}')
namespace['analyse_emotion']('input8',m);classification_call=client.calls[-1];namespace['generate_reply']('input8',a(),Robot(),m);reply_call=client.calls[-1]
ck('Q068 transport message counts',[len(classification_call['messages']),len(reply_call['messages'])],[2,10]);ck('Q068 classifier embeds last three pairs','input5'in classification_call['messages'][1]['content']and'input4'not in classification_call['messages'][1]['content'],True)
m.add_turn('input8','reply8');ck('Q068 post-save retained pairs',[m.history[0]['content'],m.history[-1]['content'],m.turn_count],['input3','reply8',8])
class WidgetStub:
 value='';disabled=False
 def __enter__(self):return self
 def __exit__(self,*args):return False
 def clear_output(self):pass
namespace.update(robot_engine=Robot(),human_engine=Human(),memory=Memory(),last_analysis='previous',message_box=WidgetStub(),send_button=WidgetStub(),status_label=WidgetStub(),chat_log=WidgetStub(),refresh_visualisation=lambda:None)
namespace['message_box'].value='  \n ';count=len(client.calls);namespace['submit_message']();ck('Q069 whitespace early return',[namespace['memory'].turn_count,len(client.calls)-count,namespace['last_analysis']],[0,0,'previous'])
namespace['memory'].add_turn('my name is synthetic','reply');ck('Q069 no fact extraction',namespace['memory'].known_facts['name'],None)
namespace['robot_engine'].change('happy',99);namespace['reset_demo']();ck('Q069 reset state',[namespace['memory'].turn_count,namespace['robot_engine'].emotions['happy'],namespace['last_analysis']],[0,50,None])
head=lambda n:(n+1)*256+(256+1)*128+(128+1)*8
ck('Q070 flatten and pooling heads',[head(7*7*512),head(512)],[6456712,165256]);ck('Q070 bias omission distractor',[head(7*7*512)-(256+128+8),head(512)-(256+128+8)],[6456320,164864])
# Additional bounded properties from the same source functions, independent of author checks.
rng=random.Random(5010);n=0
for _ in range(1000):
 r=Robot();value=rng.uniform(-100,200);r.change('happy',value);assert r.emotions['happy']==max(0,min(100,value));n+=1
 assert math.isclose(r.emotions['happy']+r.emotions['sad'],100);n+=1
 z=a(confidence=rng.random(),valence=rng.uniform(-1,1),arousal=rng.uniform(-1,1));h=Human();apply(z,h);assert math.isclose(h.emotions['happy'],50+50*z.confidence*z.valence);n+=1
 assert math.isclose(h.emotions['friendly'],50-50*z.confidence*z.arousal);n+=1
 r=Robot();before=r.state_r;drain(r);assert r.state_r==before and r.emotions['fresh']==78;n+=1
out=dict(completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourcePath=path,sourceSha256=hashlib.sha256(raw).hexdigest(),selectedDefinitions=selected,executionDisclosure='Exact inspected AST definitions executed in default Python with installed NumPy/Pydantic; all client calls hit an inert local stub. Install/client-construction/model/UI setup cells were not executed. The UI handlers were tested with synthetic widget stubs; this is not a live notebook or GUI demonstration.',versions=dict(numpy=np.__version__,pydantic=pydantic.__version__),explicitAssertions=len(checks),checks=checks,threeTurnTrace=trace,variedCases=1000,variedAssertions=n,externalMethodology=dict(url='https://scikit-learn.org/stable/modules/cross_validation.html',version='Page identified as scikit-learn1.9.1 on2026-10-20',finding='Use training/validation or cross-validation for selection; reserve a final test set and fit preprocessing on training data.'))
result=R/'audits/W10-L50-v2-contracts-independent-checks.json';assert not result.exists();result.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(explicit=len(checks),varied=n,sourceSha256=out['sourceSha256'])))
