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
p['lectures-p0119-formula-b']['cropRectangle']=[104,276,414,299]
crop(394,[78,255,440,352],'-recursions')
for suf in ['Q026','Q046']:bind('W03-L13-'+suf,[407,408,394],['lectures-p0407','lectures-p0408','lectures-p0394-recursions'])
for n,r in {944:[35,50,362,361],1004:[482,44,704,214],1006:[0,50,710,368],1008:[75,165,482,360],1017:[245,38,705,236],1031:[15,50,480,225],1033:[460,27,712,210],1052:[0,135,510,367],1053:[60,189,450,365],1055:[525,16,699,248],1056:[25,54,685,245],1077:[5,50,523,353],1078:[168,215,518,369],1081:[42,191,502,368]}.items():crop(n,r)
crop(947,[57,109,332,258],'-metric-code');crop(947,[57,334,393,352],'-move-code');crop(947,[434,81,704,223],'-pixel-code');crop(949,[16,85,362,218],'-grid-code');crop(949,[16,260,376,349],'-visibility-code');crop(997,[40,152,467,198],'-wavelengths');crop(997,[550,16,710,151],'-light-path')
bind('W07-L31-P0947-Q02',[947],['lectures-p0947-metric-code','lectures-p0947-move-code'])
bind('W07-L31-P0947-Q05',[947],['lectures-p0947-metric-code','lectures-p0947-move-code','lectures-p0947-pixel-code'])
bind('W07-L31-P0949-Q02',[947,949],['lectures-p0947-pixel-code','lectures-p0949-visibility-code'])
bind('W07-L31-P0949-Q05',[949],['lectures-p0949-grid-code','lectures-p0949-visibility-code'])
bind('W07-L33-Q018',[997],['lectures-p0997-wavelengths','lectures-p0997-light-path'])
for path,target in [('data/question-visuals/crop-plan-late-additions.json',p),('audits/question-visuals/late-decision-overrides.json',o),('audits/question-visuals/late-source-overrides.json',s)]:target.update(rd(path))
wr('data/question-visuals/crop-plan.json',p);wr('audits/question-visuals/decision-overrides.json',o);wr('audits/question-visuals/source-overrides.json',s)
