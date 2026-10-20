import json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
def rd(p):return json.loads((R/p).read_text())
def wr(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
p=rd('data/question-visuals/crop-plan.json');o=rd('audits/question-visuals/decision-overrides.json');s=rd('audits/question-visuals/source-overrides.json')
def crop(n,r,suf=''):
 k=f'lectures-p{n:04}'+suf;p[k]=dict(sourceId='lectures',physicalPage=n,cropRectangle=r,renderDpi=216,alt=f'Exact source input crop from lecture PDF, physical page {n}.');return k
def bind(q,pages,keys=None):
 s[q]=pages
 if keys:o.setdefault(q,{})['cropKeys']=keys
for n,r in {781:[20,50,264,336],782:[7,186,497,327],786:[375,184,702,339],788:[50,169,328,359],789:[192,238,520,357],790:[44,185,686,334],791:[8,56,410,294],792:[8,169,412,223],796:[8,50,520,368],803:[8,54,415,266],805:[0,57,312,358],808:[455,25,710,242],811:[295,185,680,366],813:[8,185,434,266],815:[0,95,365,367],818:[335,18,678,204],843:[7,18,710,348],859:[508,107,695,245],863:[404,20,718,248],864:[508,90,716,247],872:[2,49,449,365],873:[7,80,290,309],881:[12,104,705,367],892:[2,228,523,356],911:[7,53,270,249],912:[7,142,528,219],913:[8,49,467,133],926:[12,159,524,369],932:[488,6,704,174],933:[500,51,715,125],934:[15,66,705,168],935:[38,17,405,212],936:[498,20,718,117],939:[390,27,717,216]}.items():crop(n,r)
crop(783,[10,80,309,175],'-manual-top');crop(783,[35,173,166,189],'-manual-return');crop(783,[10,195,451,296],'-ml');crop(786,[40,211,375,285],'-features');crop(873,[90,269,368,356],'-lower-leaves')
for path in (R/'audits/question-visual-review/lead').glob('L*-input-triage.json'):
 for r in json.loads(path.read_text())['questions']:
  if r['decision'] in ['required','self_contained']:o.setdefault(r['questionId'],{}).update(dependencyStatus=r['decision'],reason=r['reason'])
for suf in ['Q019','Q020']:bind('W06-L26-'+suf,[783],['lectures-p0783-manual-top','lectures-p0783-manual-return'])
bind('W06-L26-Q021',[782,783],['lectures-p0782','lectures-p0783-ml'])
bind('W06-L26-Q026',[786],['lectures-p0786','lectures-p0786-features'])
bind('W06-L26-Q043',[792])
for suf in ['Q033','Q034','Q035','Q037']:
 q='W06-L29-'+suf;bind(q,[872,873] if suf=='Q033' else [873],(['lectures-p0872'] if suf=='Q033' else [])+['lectures-p0873','lectures-p0873-lower-leaves'])
bind('W06-L30-Q045',[911,912])
wr('data/question-visuals/crop-plan.json',p);wr('audits/question-visuals/decision-overrides.json',o);wr('audits/question-visuals/source-overrides.json',s)
