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
crop(119,[104,250,342,274],'-formula-a');crop(119,[104,277,283,299],'-formula-b')
for q in ['W01-L03-P0119-Q02','W01-L03-P0119-Q03']:bind(q,[119],['lectures-p0119-formula-a','lectures-p0119-formula-b'])
p['lectures-p0284']['cropRectangle']=[395,238,520,372]
for n,r in {703:[315,196,397,229],705:[45,34,663,337],712:[500,17,690,230],713:[15,58,510,215],719:[0,44,690,340],720:[266,100,508,365],730:[150,85,560,117],731:[88,240,438,367],734:[3,50,717,224],737:[23,143,715,355],738:[325,40,715,244],739:[25,196,445,295],741:[5,218,425,368],744:[15,77,390,145],746:[15,88,608,358],755:[8,246,510,334],757:[105,250,400,373],761:[15,250,460,371],763:[410,18,719,243],765:[315,18,718,221],769:[378,15,715,224]}.items():crop(n,r)
crop(731,[85,99,480,175],'-error-definition');crop(738,[220,313,380,342],'-steady-expression');crop(730,[43,242,420,339],'-partition')
for suf,pages in {'Q014':[703],'Q020':[705],'Q022':[706],'Q033':[712],'Q034':[712,713],'Q036':[715],'Q037':[716],'Q038':[716,717],'Q039':[717],'Q040':[717],'Q045':[716,718],'Q047':[717],'Q050':[719],'Q053':[720]}.items():bind('W05-L23-'+suf,pages)
for suf,pages in {'P0731-Q01':[731],'P0731-Q05':[731],'P0734-Q01':[734],'P0734-Q02':[734],'P0737-Q01':[737],'P0737-Q02':[737],'P0737-Q03':[737],'P0738-Q01':[731,738],'P0738-Q03':[730,731,738],'P0738-Q05':[738],'P0739-Q02':[730,731,739],'P0739-Q03':[730,731,739],'P0741-Q02':[741],'P0744-Q02':[744],'P0744-Q03':[744],'P0744-Q04':[744],'P0744-Q05':[744],'P0744-Q06':[744],'P0746-Q05':[746],'P0747-Q02':[746],'P0747-Q04':[746]}.items():bind('W05-L24-'+suf,pages)
o['W05-L24-P0731-Q01']['cropKeys']=['lectures-p0731-error-definition']
for suf in ['P0738-Q01','P0738-Q03']:o['W05-L24-'+suf]['cropKeys']=['lectures-p0731-error-definition','lectures-p0731','lectures-p0738']+(['lectures-p0730'] if suf=='P0738-Q03' else [])
o['W05-L24-P0738-Q05']['cropKeys']=['lectures-p0738-steady-expression']
for suf in ['P0739-Q02','P0739-Q03']:o['W05-L24-'+suf]['cropKeys']=['lectures-p0730-partition','lectures-p0731-error-definition','lectures-p0731','lectures-p0739']
for suf,pages in {'Q002':[755],'Q011':[757],'Q013':[755,757],'Q020':[761],'Q029':[763],'Q038':[765],'Q049':[769]}.items():bind('W05-L25-'+suf,pages)
for q,pages in {'W03-L14-Q035':[444],'W03-L15-Q032':[463],'W04-L17-Q055':[534],'W04-L16-P0496-Q02':[496],'W04-L16-P0496-Q04':[496],'W04-L16-P0496-Q05':[496],'W04-L16-P0496-Q06':[496],'W04-L16-P0499-Q05':[499],'W04-L16-P0501-Q02':[496]}.items():
 o.setdefault(q,{})['dependencyStatus']='required';bind(q,pages)
wr('data/question-visuals/crop-plan.json',p);wr('audits/question-visuals/decision-overrides.json',o);wr('audits/question-visuals/source-overrides.json',s)
