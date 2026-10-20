import json
from pathlib import Path
P=Path('.');plan=json.load(open('data/question-visuals/crop-plan.json'));refs=json.load(open('audits/question-visuals/source-overrides.json'));ov=json.load(open('audits/question-visuals/decision-overrides.json'))
rects={141:[505,55,720,245],164:[425,28,712,242],175:[15,65,690,350],216:[495,60,710,245],226:[470,45,718,190],236:[8,50,302,200],238:[8,35,340,218],251:[300,130,710,360],253:[180,185,465,367],258:[345,65,715,365],260:[60,95,710,365],261:[12,135,710,240],262:[465,45,690,245],265:[70,285,355,365],272:[493,35,719,250],281:[550,15,719,155],284:[575,215,710,365],286:[480,30,719,260],287:[480,30,719,260],289:[65,275,425,365],309:[472,6,720,244],329:[560,45,718,218],365:[485,50,715,245],375:[12,60,410,350],392:[410,45,715,270],407:[15,65,710,365],408:[530,30,710,245],454:[570,70,718,220],469:[190,300,515,345],481:[470,110,715,258],496:[15,70,710,215],499:[125,50,700,365],500:[165,50,475,365],501:[50,75,515,365],508:[345,65,719,365],534:[115,65,615,367],535:[5,100,490,330],537:[15,75,515,360],547:[460,65,719,245],556:[410,55,719,240],558:[430,40,715,255],560:[430,60,719,245],562:[450,55,719,260],563:[475,45,719,235],564:[455,45,719,245],570:[15,55,710,355],571:[350,215,530,355],573:[15,60,705,369],581:[445,15,715,250],588:[440,65,710,240],595:[440,90,710,230],602:[478,95,660,250],610:[525,35,718,190]}
for p,r in rects.items():plan[f'lectures-p{p:04}']=dict(sourceId='lectures',physicalPage=p,cropRectangle=r,renderDpi=216,alt=f'Exact source visual or input code from lecture physical page {p}; original labels and geometry preserved.')
extra={'lectures-p0282-diagram':(282,[395,15,525,175]),'lectures-p0282-table':(282,[520,125,718,246]),'lectures-p0329-transforms':(329,[20,85,505,365]),'lectures-p0408-premises':(408,[15,70,480,290]),'lectures-p0565-diagram':(565,[20,50,340,260]),'lectures-p0565-caption':(565,[15,275,550,325])}
for key,(p,r) in extra.items():plan[key]=dict(sourceId='lectures',physicalPage=p,cropRectangle=r,renderDpi=216,alt=f'Exact source input detail from lecture physical page {p}.')
# Boundary repairs requested by independent reviewer.
plan['lectures-p0090']['cropRectangle']=[20,50,700,130]
plan['lectures-p0130']['cropRectangle']=[530,87,710,249]
plan['lectures-p0151']['cropRectangle']=[485,30,715,231]
refs.update({'W01-L04-P0140-Q01':[141],'W02-L06-P0238-Q02':[236,238],'W02-L08-P0287-Q02':[287],'W02-L08-P0287-Q04':[287],'W03-L12-Q021':[392],'W04-L17-Q058':[534,535],'W04-L17-Q059':[537],'W04-L18-Q062':[571],'W04-L16-P0501-Q03':[496],'W04-L20-P0610-Q04':[610]})
for q in ['W02-L08-P0282-Q01','W02-L08-P0282-Q03','W02-L08-P0282-Q04']:ov[q]={'cropKeys':['lectures-p0282-diagram','lectures-p0282-table']}
for q in ['W02-L10-Q001','W02-L10-Q002']:ov[q]={'cropKeys':['lectures-p0329','lectures-p0329-transforms']}
ov['W03-L13-Q025']={'cropKeys':['lectures-p0407','lectures-p0408','lectures-p0408-premises']}
ov['W04-L18-Q041']={'cropKeys':['lectures-p0565-diagram','lectures-p0565-caption']}
for path,data in [('data/question-visuals/crop-plan.json',plan),('audits/question-visuals/source-overrides.json',refs),('audits/question-visuals/decision-overrides.json',ov)]:Path(path).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
