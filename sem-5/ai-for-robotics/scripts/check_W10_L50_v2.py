"""Source-cell deterministic checks with synthetic state and an explicit local stub."""
from pathlib import Path
import json,math,random,ast,types,dataclasses,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];p=R/'sources/supplemental/L50-official-week10_lecture50.ipynb';j=json.loads(p.read_text())
ns={'np':np,'math':math,'json':json,'dataclass':dataclasses.dataclass,'field':dataclasses.field,'EmotionAnalysis':types.SimpleNamespace,'MODEL_NAME':'synthetic-no-model'}
for i in [9,11,13,17]:exec(compile(''.join(j['cells'][i]['source']),f'L50-cell-{i}','exec'),ns)
checks=[]
def check(name,v):
 assert v,name
 checks.append(name)
r=ns['RobotEmotionEngine']();r.change('happy',80);r.change('welcome',90);r.change('friend',70)
x=sum((r.emotions[k]-50)*math.cos(math.radians(a))for k,a in r.emotion_axis.items());y=sum((r.emotions[k]-50)*math.sin(math.radians(a))for k,a in r.emotion_axis.items())
vector={'x':x,'y':y,'radius':r.state_r,'angleDegrees':r.state_theta,'mood':r.active_mood,'plottedRadius':min(100,r.state_r)}
check('multi-axis x',abs(x-67.32755789995922)<1e-10);check('multi-axis y',abs(y-122.41975288537782)<1e-10);check('multi-axis radius',abs(r.state_r-139.7125475728266)<1e-10);check('multi-axis angle',abs(r.state_theta-61.190394282542876)<1e-10);check('nearest mood',r.active_mood=='FRIEND');check('raw versus plotted radius',r.state_r>100 and vector['plottedRadius']==100)
h=ns['HumanEmotionEngine']();r=ns['RobotEmotionEngine']();m=ns['ConversationMemory']()
for i in range(1,6):m.add_turn(f'u{i}',f'a{i}')
analyses=[types.SimpleNamespace(emotion='fearful',confidence=.8,valence=-.5,arousal=.5),types.SimpleNamespace(emotion='sad',confidence=.30,valence=-.6,arousal=-.4),types.SimpleNamespace(emotion='neutral',confidence=0.,valence=0.,arousal=0.)]
states=[]
for number,a in enumerate(analyses,6):
 ns['apply_analysis_to_human_engine'](a,h);ns['update_robot_policy'](a,r);ns['drain_battery'](r);states.append({'turn':number,'human':dict(h.emotions),'robot':dict(r.emotions),'priorMessages':len(m.history),'classificationContext':m.history[-6:],'replyContext':m.history[-8:]});m.add_turn(f'u{number}',f'a{number}')
check('confidence .30 follows sad branch',states[1]['robot']['welcome']==88 and states[1]['robot']['friend']==82)
check('sad assignment can decrease previous values',states[0]['robot']['welcome']==92 and states[1]['robot']['welcome']==88)
check('failed classifier resets mapped human axes',all(v==50 for v in h.emotions.values()))
check('low-confidence branch preserves unrelated robot axes',r.emotions['welcome']==88 and r.emotions['friend']==82 and r.emotions['happy']==50)
check('three battery drains',r.emotions['fresh']==74 and r.emotions['tired']==26)
check('final curiosity',r.emotions['curious']==62)
check('history cap and lifetime count',len(m.history)==12 and m.turn_count==8)
check('oldest retained pair',m.history[0]['content']=='u3' and m.history[-1]['content']=='a8')
check('classification context packs last three prior pairs', [x['content']for x in states[2]['classificationContext']]==['u5','a5','u6','a6','u7','a7'])
check('reply context packs last four prior pairs',[x['content']for x in states[2]['replyContext']]==['u4','a4','u5','a5','u6','a6','u7','a7'])
check('known facts are not filled by add_turn',all(v is None for v in m.known_facts.values()))
tree=ast.parse(''.join(j['cells'][15]['source']));gen=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='generate_reply')
calls=[]
class Stub:
 def chat(self,**kw):calls.append(kw);return types.SimpleNamespace(message=types.SimpleNamespace(content='synthetic reply'))
ns['client']=Stub();exec(compile(ast.Module(body=[gen],type_ignores=[]),'L50-cell15-generate-reply-with-stub','exec'),ns)
prior=ns['ConversationMemory']()
for i in range(1,8):prior.add_turn(f'u{i}',f'a{i}')
reply=ns['generate_reply']('u8',analyses[-1],r,prior)
check('mocked reply only',reply=='synthetic reply' and len(calls)==1)
check('reply transport count',len(calls[0]['messages'])==10)
check('reply transport roles',calls[0]['messages'][0]['role']=='system' and calls[0]['messages'][-1]['content']=='u8')
analyse=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='analyse_emotion');message_lists=[kw.value for n in ast.walk(analyse)if isinstance(n,ast.Call)for kw in n.keywords if kw.arg=='messages'];check('classification transport has two entries',len(message_lists)==1 and len(message_lists[0].elts)==2)
ui=ast.parse(''.join(j['cells'][21]['source']));submit=next(n for n in ui.body if isinstance(n,ast.FunctionDef)and n.name=='submit_message');early=next(n for n in submit.body if isinstance(n,ast.If));check('blank input returns before processing',isinstance(early.body[0],ast.Return))
flat=(7*7*512+1)*256+(256+1)*128+(128+1)*8;gap=(512+1)*256+(256+1)*128+(128+1)*8
check('complete flatten head count',flat==6456712);check('complete pooled head count',gap==165256)
random.seed(505002)
for _ in range(5000):
 a=random.uniform(-200,200);r.change('happy',a);assert r.emotions['happy']==float(np.clip(a,0,100));assert r.emotions['happy']+r.emotions['sad']==100
 v=random.uniform(-1,1);ar=random.uniform(-1,1);c=random.random();z=types.SimpleNamespace(valence=v,arousal=ar,confidence=c);ns['apply_analysis_to_human_engine'](z,h);assert abs(h.emotions['happy']-(50+50*c*v))<1e-10;assert abs(h.emotions['friendly']-(50-50*c*ar))<1e-10
out={'authorOnly':True,'notebookSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checks':checks,'explicitChecks':len(checks),'variedCases':5000,'variedAssertions':20000,'vector':vector,'threeTurnTrace':states,'finalHistory':m.history,'headParameters':{'flatten':flat,'globalAveragePool':gap},'executionScope':'Original deterministic source cells9,11,13,17 and generate_reply with a locally defined inert client; synthetic inputs only. Classification/UI structure checked by AST. No live model, network call, hardware, package installation or denied environment.'}
(R/'audits/W10-L50-v2-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checks':len(checks),'variedCases':5000,'vector':vector,'headCounts':[flat,gap]}))
