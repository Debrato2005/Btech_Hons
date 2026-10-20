import json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
def rd(p):return json.loads((R/p).read_text())
def wr(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
p=rd('data/question-visuals/crop-plan.json'); o=rd('audits/question-visuals/decision-overrides.json'); s=rd('audits/question-visuals/source-overrides.json')
def crop(n,r,suffix=''):
 k=f'lectures-p{n:04}'+suffix;p[k]={'sourceId':'lectures','physicalPage':n,'cropRectangle':r,'renderDpi':216,'alt':f'Exact source input crop from lecture PDF, physical page {n}.'};return k
def bind(q,pages,keys=None):
 s[q]=pages
 if keys:o.setdefault(q,{})['cropKeys']=keys
for n,r in {81:[30,92,300,355],175:[15,50,690,350],226:[470,30,718,190],251:[300,100,710,360],253:[180,160,465,367],258:[325,65,715,365],284:[395,238,520,368],289:[65,260,425,365],329:[535,35,705,222],365:[485,40,715,245],392:[380,40,710,270],408:[520,32,710,245],469:[190,280,515,345],481:[470,82,715,245],119:[105,251,338,298],157:[20,135,346,369]}.items():crop(n,r)
p['lectures-p0408-premises']['cropRectangle']=[15,80,480,275]
crop(464,[35,232,225,290],'-massmatrix')
for q in ['W02-L10-Q012','W02-L10-Q014','W02-L10-Q019']:bind(q,[329],['lectures-p0329','lectures-p0329-transforms'])
bind('W03-L15-Q031',[454,464],['lectures-p0454','lectures-p0464-massmatrix'])
for q in ['W01-L03-P0119-Q02','W01-L03-P0119-Q03','W01-L04-P0157-Q03','W01-L04-P0157-Q06','W01-L04-P0166-Q02','W01-L04-P0161-Q05','W01-L04-P0163-Q01','W01-L04-P0164-Q01']:
 o.setdefault(q,{})['dependencyStatus']='required';o[q]['reason']='The standalone question refers to a particular source formula or code program whose complete input definitions are not supplied in the stem, choices, or assumptions.'
bind('W01-L04-P0166-Q02',[165,166],['lectures-p0165','lectures-p0166-code'])
for n,r in {614:[25,105,514,255],615:[15,100,490,279],616:[15,75,710,228],618:[520,55,712,245],619:[195,67,660,222],621:[5,18,710,350],631:[8,50,506,366],632:[17,60,461,230],641:[5,70,590,240],642:[15,260,410,365],654:[400,55,715,205],659:[25,175,425,350],661:[5,225,415,365],675:[380,20,715,195],682:[405,65,710,245],684:[20,65,710,235],685:[2,75,720,349],686:[20,100,425,360],687:[8,73,373,213],688:[375,25,719,244],689:[40,75,510,278],706:[340,50,717,230],715:[5,165,525,365],716:[10,60,718,265],717:[5,50,715,365],718:[5,55,715,365]}.items():crop(n,r)
crop(688,[0,70,373,180],'-parameters')
for path in (R/'audits/question-visual-review/lead').glob('L*-input-triage.json'):
 for r in json.loads(path.read_text())['questions']:
  o.setdefault(r['questionId'],{}).update({'dependencyStatus':r['decision'],'reason':r['reason']})
for suf,pages in {'P0614-Q02':[614], 'P0614-Q03':[614], 'P0615-Q01':[615], 'P0615-Q03':[615], 'P0616-Q01':[616], 'P0617-Q02':[616], 'P0618-Q01':[618], 'P0619-Q02':[619], 'P0619-Q04':[619], 'P0621-Q01':[621], 'P0621-Q03':[621], 'P0621-Q04':[621], 'P0621-Q05':[621], 'P0622-Q04':[616], 'P0631-Q05':[631], 'P0632-Q03':[631,632], 'P0632-Q06':[631,632]}.items():bind('W04-L20-'+suf,pages)
for suf,pages in {'Q009':[675],'Q026':[682],'Q031':[684],'Q035':[685],'Q036':[685],'Q040':[686],'Q041':[685],'Q042':[687],'Q044':[685,688],'Q053':[689]}.items():bind('W05-L22-'+suf,pages)
bind('W05-L22-Q044',[685,688],['lectures-p0685','lectures-p0688','lectures-p0688-parameters'])
wr('data/question-visuals/crop-plan.json',p);wr('audits/question-visuals/decision-overrides.json',o);wr('audits/question-visuals/source-overrides.json',s)
