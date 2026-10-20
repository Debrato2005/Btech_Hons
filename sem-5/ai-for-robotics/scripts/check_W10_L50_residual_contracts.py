"""Narrow independent residual review. Default installed Python only."""
import json,math,hashlib,ast,datetime
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(p,x):
 f=R/p
 assert not f.exists(),p
 f.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
p='audits/blind-W10-L50-residual-v3.json';bind='audits/W10-L50-residual-v3-minimal-bindings.json';packet=json.loads((R/p).read_text());binding=json.loads((R/bind).read_text());assert sha(p)==binding['packetSha256']=='9d0902062c496c741712dc86bc37665ffcea943bf3cc80e56430b1ec96115475'
npth='sources/supplemental/L50-official-week10_lecture50.ipynb';notebook=json.loads((R/npth).read_text());assert sha(npth)=='66c4de29a27675d8985b20ee815901e9201382ee290ee4ae0ae001233ec39fab'
code=ast.parse(''.join(notebook['cells'][9]['source']));ns={'math':math,'np':np};exec(compile(ast.Module(body=[n for n in code.body if isinstance(n,ast.ClassDef) and n.name=='RobotEmotionEngine'],type_ignores=[]),'<unmodified-source-cell9>','exec'),ns);e=ns['RobotEmotionEngine']()
for k,v in [('happy',80),('welcome',90),('friend',70)]:e.change(k,v)
angles={'happy':112,'welcome':22,'friend':67,'curious':157,'sad':292,'distant':202,'strange':247,'frustrated':337};values=dict.fromkeys(angles,50);values.update(happy=80,sad=20,welcome=90,distant=10,friend=70,strange=30)
x=sum((values[k]-50)*math.cos(math.radians(t)) for k,t in angles.items());y=sum((values[k]-50)*math.sin(math.radians(t)) for k,t in angles.items());radius=math.hypot(x,y);theta=math.degrees(math.atan2(y,x))%360;mood=min(angles,key=lambda k:abs((theta-angles[k]+180)%360-180)).upper()
assert math.isclose(e.state_r,radius) and math.isclose(e.state_theta,theta) and e.active_mood==mood=='FRIEND'
class Axis:
 def __init__(self):self.arrow=None;self.limit=None
 def __getattr__(self,name):
  def method(*args,**kwargs):
   if name=='annotate':self.arrow=kwargs['xy']
   if name=='set_ylim':self.limit=args
  return method
nodes=ast.parse(''.join(notebook['cells'][19]['source'])).body;exec(compile(ast.Module(body=[n for n in nodes if isinstance(n,ast.FunctionDef) and n.name=='_plot_engine'],type_ignores=[]),'<unmodified-source-cell19-definition>','exec'),ns);axis=Axis();ns['_plot_engine'](axis,'test-only',e,'vector');assert axis.arrow==(math.radians(theta),100.0) and axis.limit==(0,100)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();observations={1572:'Named angular axes, yellow values and purple resultant illustration. Exact notebook angles and clipping are not printed here.',1573:'Half-range formulas (max-min)/2 and45–55 neutral threshold are literally printed and differ from the notebook.',1574:'OppositeMagnitude=100-ActiveValue; boundary-scan prose is separate from the actual centered sum.',1576:'Albert pseudocode and complete-code hyperlink, not the exact engine implementation.',1581:'Printed dataset channel descriptions and AffectNet class, valence, arousal targets.',1582:'Category list and numbered display; numeric encodings are not globally interchangeable.',1583:'Lower example contrasts RAF-DB discrete label with AffectNet continuous annotations; inaccurate energy/calmness prose is excluded by the item.',1588:'Past interactions and current estimated evidence jointly enter dialogue planning.',1590:'Individual variation, occlusion and lighting challenge evaluation; no universal-domain guarantee.'}
obs=[]
for page,note in observations.items():
 f=f'sources/previews/lectures/page-{page:04d}.webp';obs.append({'physicalPage':page,'slideId':f'lectures-p{page:04d}','previewPath':f,'previewSha256':sha(f),'actualPixelsViewed':True,'observation':note})
write('audits/W10-L50-residual-contracts-source-observations.json',{'reviewerId':'robotics-contracts-independent-reviewer','observedAt':now,'sourceSha256':binding['sourceVersion'],'observations':obs,'notebookPath':npth,'notebookSha256':sha(npth),'codeCellsZeroBased':[9,19]})
write('audits/W10-L50-residual-contracts-independent-checks.json',{'at':now,'x':x,'y':y,'radius':radius,'angleDegrees':theta,'mood':mood,'plottedRadius':axis.arrow[1],'alternativeComputations':{'halfResultant':{'x':x/2,'y':y/2,'radius':radius/2},'swappedAtan2Angle':math.degrees(math.atan2(x,y)),'incorrectRawClip':100},'passed':True,'executionScope':'Executed only unmodified RobotEmotionEngine class and _plot_engine definition with inert local Axis stub in default installed Python. No browser, GUI rendering, model, client, retrieval or network execution.'})
reasons={'W10-L50-Q059':'Current request should influence the present response while historical preference stays contextual. Permanently generalizing the new request, rigidly privileging old memory, or copying a retrieved tone without current instruction are different credible planning errors.','W10-L50-Q066':f'Complementary centered vectors sum to ({x},{y}); radius{radius}, theta{theta}, nearest FRIEND, and the plotting definition clips only the displayed radius to100. Citation roles now distinguish the slide half-range conflict from notebook computation.','W10-L50-Q071':'Only the printed AffectNet target list supplies both named class and continuous targets. Alignment requires semantic labels, not numeric-code merging. New lighting/occlusion requires separate evaluation; class-mean imputation is not an image-specific measured continuous annotation.'}
answers=[]
for q in packet:answers.append({'questionId':q['id'],'questionVersion':q['version'],'questionSha256':binding['questionHashes'][q['id']],'independentAnswerOptionIds':['o1'] if q['id'].endswith('066') else ['o2'],'reasoning':reasons[q['id']],'solvedBeforeAnswerSeen':False,'currentVersionSolvedBeforeKeyedAccess':True,'priorAuthorExposure':'Reviewed earlier keyed versions and authored no revision. This is independently recomputed revision review, not fresh blind verification.'})
write('audits/blind-answers-W10-L50-residual-contracts.json',{'reviewerId':'robotics-contracts-independent-reviewer','frozenAt':now,'packetPath':p,'packetSha256':sha(p),'bindingPath':bind,'bindingSha256':sha(bind),'answers':answers,'sourceObservationsPath':'audits/W10-L50-residual-contracts-source-observations.json','computationsPath':'audits/W10-L50-residual-contracts-independent-checks.json'})
print('Frozen answers SHA',sha('audits/blind-answers-W10-L50-residual-contracts.json'))
