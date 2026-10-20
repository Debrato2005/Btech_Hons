#!/usr/bin/env python3
"""Default-Python standard-library arithmetic and preservation checks. Not independent review."""
from pathlib import Path
import json,math,random,hashlib,sys,datetime,copy,re
from fractions import Fraction as F
R=Path(__file__).resolve().parents[1];B='W11-L54';started=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ('status','reviewIds')},ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
b=read(f'data/question-batches/{B}.json');Q={q['id'].removeprefix(B+'-'):q for q in b['questions']};notes=read(f'audits/{B}-v2-author-repair-notes.json');changed=[q for q in b['questions']if q['id']in notes['changedQuestionIds']];checks=[]
def ck(name,v,detail):assert v,name;checks.append({'id':f'L54-V2-AUTHOR-{len(checks)+1:02}','name':name,'detail':detail,'passed':True})
def close(a,b):return math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10)
def fk(a,b,l1=1,l2=1):return(l1*math.cos(a)+l2*math.cos(a+b),l1*math.sin(a)+l2*math.sin(a+b))
def vclose(a,b):return all(close(x,y)for x,y in zip(a,b))
def key(s,k):return Q[s]['correctOptionIds']==[k]
ck('19 changed drafts and 70 preserved hashes',len(changed)==19 and len(b['questions'])==89 and all(qhash(next(q for q in b['questions']if q['id']==i))==h for i,h in notes['acceptedQuestionHashes'].items()),'Exact canonical content hash excludes only status/reviewIds; no accepted mutation.')
ck('12 source qualifications byte-identical',sha(f'audits/source-disputes-{B}.json')==sha(f'audits/archive/{B}-v1-before-v2/source-disputes-{B}.json'),'Preserve original source issues; the seven unit errors were author text, not new course conflicts.')
ck('Source revisits complete, no unique-count inflation',len(read(f'audits/{B}-v2-author-revisits.json')['pages'])==16 and len(read(f'data/inspection-batches/{B}.json')['slides'])==30,'Author repair revisits, not independent review or additional unique pages.')
a,beta=math.pi/6,math.pi/3
ck('Metre FK endpoint and intended key',vclose(fk(a,beta),(math.sqrt(3)/2,1.5))and key('P1734-Q01','o1'),'Both unit links use metres; second absolute angle is pi/2.')
wrongabs=(math.cos(a)+math.cos(beta),math.sin(a)+math.sin(beta))
ck('FK alternative-angle distractor',vclose(wrongabs,((math.sqrt(3)+1)/2,(1+math.sqrt(3))/2))and not vclose(wrongabs,fk(a,beta)),'Treating elbow as absolute gives the second listed endpoint, not the correct relative-angle FK.')
ck('FK swapped-coordinate distractor',not close(math.sqrt(3)/2,1.5)and all(o['text'].endswith(' m')for o in Q['P1734-Q01']['options']),'All offered endpoints now share metres; the sine/cosine swap is distinct.')
ck('Positive branch closure alternatives',vclose(fk(0,math.pi/2),(1,1))and vclose(fk(math.pi/2,-math.pi/2),(1,1))and vclose(fk(math.pi/2,math.pi/2),(-1,1))and key('P1734-Q02','o2'),'Same target can have negative elbow, but branch filter selects (0,pi/2).')
ck('Unreachable radial target',close(math.hypot(1.5,1.5),math.sqrt(4.5))and math.hypot(1.5,1.5)>2 and 1.5<2 and key('P1734-Q03','o1'),'Coordinate bounds pass but radial bound fails; returning/clipping numeric coordinates does not establish reachability.')
rounded=fk(math.radians(27.9),math.radians(90.1))
ck('Rounded diagram coordinates in metres',round(rounded[0],4)==.4143 and round(rounded[1],4)==1.3509 and abs(rounded[0]-.415)<.001 and abs(rounded[1]-1.351)<.001 and key('P1735-Q02','o3'),str(rounded)+' m; errors smaller than one millimetre, not a 1000-fold discrepancy.')
# A consistent underlying angle pair lies inside both angle-rounding and coordinate-rounding cells.
consistent=fk(math.radians(27.87),math.radians(90.10))
ck('Display rounding consistency witness',round(27.87,1)==27.9 and round(90.10,1)==90.1 and round(consistent[0],3)==.415 and round(consistent[1],3)==1.351,'One supplied witness, not a reconstruction of the unknown original slider state.')
pairs={'A':(math.pi/2,-math.pi/2),'B':(math.pi/6,math.pi/2),'C':(0,math.pi/3)};pts={k:fk(*v)for k,v in pairs.items()};errs={k:math.dist(v,(1,1))for k,v in pts.items()};mses={k:((v[0])**2+(v[1]-math.pi/2)**2)/2 for k,v in pairs.items()}
ck('Integrated IK branch filter',pairs['A'][1]<0 and all(-math.pi<=pairs[k][0]<=math.pi and 0<=pairs[k][1]<=math.pi for k in ['B','C'])and errs['A']<1e-12,'A closes the target but is rejected before endpoint comparison.')
ck('Integrated IK B endpoint/error',vclose(pts['B'],((math.sqrt(3)-1)/2,(math.sqrt(3)+1)/2))and close(errs['B'],math.sqrt(3)-1),'B error = 0.7320508075688772 m.')
ck('Integrated IK C endpoint/error',vclose(pts['C'],(1.5,math.sqrt(3)/2))and close(errs['C'],math.sqrt(2-math.sqrt(3))),'C error = 0.5176380902050415 m.')
ck('Equal joint MSE is not equal task error',close(mses['B'],math.pi**2/72)and close(mses['B'],mses['C'])and errs['C']<errs['B']and key('P1737-Q01','o2'),'Same MSE pi²/72 rad², but C is the smaller admissible Cartesian error.')
widths=[2,256,256,128,2];weights=sum(x*y for x,y in zip(widths,widths[1:]));bias=sum(widths[1:]);total=weights+bias
ck('Dense weights plus bias count',weights==99072 and bias==642 and total==99714 and key('P1738-Q01','o1'),'Layer totals 768,65792,32896,258; 99072 excludes biases.')
ck('Parameter distractor arithmetic',total-(128+1)*2==99456 and len({total,weights,99456})==3,'Omitting output transition gives 99456; omitting all biases gives 99072.')
physical_mean_mm=(F(5,100)+0)/2;physical_cm=physical_mean_mm/10;raw_print=f'{float(physical_mean_mm)*100:.2f} cm'
ck('Literal print versus dimensional truth',physical_mean_mm==F(25,1000)and physical_cm==F(25,10000)and raw_print=='2.50 cm'and key('P1739-Q03','o2'),'Mean is0.025mm=0.0025cm; unmodified raw-number print emits2.50cm. No unit-aware array conversion exists.')
ck('Unit-print alternative values',f'{float(physical_cm):.2f} cm'=='0.00 cm'and float(physical_cm)*1000==2.5,'First alternative formats the physical value but is not literal code; accepting printed label inflates physical mean1000-fold.')
ck('Negative-x target closure',vclose(fk(math.pi/2,math.pi/2),(-1,1))and vclose(fk(math.pi/2,-math.pi/2),(1,1))and vclose(fk(math.pi,0),(-2,0))and key('P1740-Q02','o2'),'All points are metres; branch and target both required.')
pred=fk(1.6773,1.5809);e=math.dist(pred,(-1,1))*100
ck('Historical single-target norm',round(pred[0],5)==-1.09951 and round(pred[1],5)==.87799 and round(e,2)==15.74 and key('P1740-Q04','o2'),f'Historical rounded angles give {pred}m, error{e}cm; no model rerun claimed.')
ck('Rounded endpoint still selects same error',round(math.dist((-1.09951,.87799),(-1,1))*100,2)==15.74 and len({9.82,round(e,2),10.0})==3,'Given rounded endpoint sufficient;9.82cm is a test mean and10cm is a rough component scale.')
ck('Jacobian singularities',abs(math.sin(0))<1e-12 and abs(math.sin(math.pi))<1e-12 and close(math.sin(math.pi/2),1)and key('P1741-Q01','o2'),'Positive link product does not vanish; endpoints0,pi make sine zero.')
x=(2.5,1400,45);mu=(2,1500,40);sd=(.5,100,5);z=tuple((u-m)/s for u,m,s in zip(x,mu,sd));v1=(1,-1,1);v2=(0,0,0);gamma=math.log(2)/3
kern=lambda a,v:math.exp(-gamma*sum((u-w)**2 for u,w in zip(a,v)))
k1,k2=kern(z,v1),kern(z,v2);score=2*k1-k2-1.25
ck('Full scaled RBF trace',z==(1,-1,1)and close(k1,1)and close(k2,.5)and close(score,.25)and score>0 and key('P1729-Q08','o1'),'Three-channel standardization, two similarities, signed weighting and intercept all applied.')
ck('Kernel distractor traces',kern(x,v1)==kern(x,v2)==0 and close(2*k1+k2-1.25,1.25),'Skipping scaling underflows both kernels to zero in Python; changing negative coefficient to positive yields1.25.')
macro=(F(9,10)+F(1,2))/2;weighted=(80*F(9,10)+20*F(1,2))/100
ck('Macro versus support weighting',macro==F(7,10)and weighted==F(82,100)and key('P1730-Q08','o3'),'Macro0.70,weighted0.82; the reversed/equal alternatives represent actual averaging mistakes.')
ck('Feasible confusion counts for report exercise',72+8==80 and 10+10==20 and F(72,80)==F(9,10)and F(10,20)==F(1,2),'Confusion counts[[72,8],[10,10]] realize the supplied supports/recalls exactly.')
ck('Class-display order bound to source code',Q['P1730-Q07']['correctOptionIds']==['o3']and 'target_names=["normal", "overload"]'in Q['P1730-Q07']['stem'],'Default labels0,1 align with supplied names, not confidence or automatic relabeling.')
ck('Held-out fit provenance',any(c['physicalPage']==1730 and c['kind']=='code'for c in Q['P1729-Q01']['citations']),'Pipeline order alone is not the fitting-boundary evidence; actual fit/predict calls now cited.')
ck('New citation source tokens',any('("sc", StandardScaler())'in c['evidenceText']for c in Q['P1729-Q08']['citations']),'Actual pipeline step name is sc, not a guessed alternate label.')
ck('All numerical relationships have metadata',all(q['solution']['formulas']and q['solution']['steps']for q in changed if q['type']in ['numerical','synthesis']),'Complete expressions, variable definitions, units and assumptions remain required per formula.')
# Varied SI checks: analytical FK radius, determinant, finite-difference determinant, and unit conversion.
rng=random.Random(5402);random_assertions=0
for _ in range(1000):
 l1,l2=rng.uniform(.1,3),rng.uniform(.1,3);a,beta=rng.uniform(-math.pi,math.pi),rng.uniform(0,math.pi);px,py=fk(a,beta,l1,l2)
 assert close(px*px+py*py,l1*l1+l2*l2+2*l1*l2*math.cos(beta));random_assertions+=1
 j11=-l1*math.sin(a)-l2*math.sin(a+beta);j12=-l2*math.sin(a+beta);j21=l1*math.cos(a)+l2*math.cos(a+beta);j22=l2*math.cos(a+beta)
 assert close(j11*j22-j12*j21,l1*l2*math.sin(beta));random_assertions+=1
 h=1e-6;ap=fk(a+h,beta,l1,l2);am=fk(a-h,beta,l1,l2);bp=fk(a,beta+h,l1,l2);bm=fk(a,beta-h,l1,l2);detnum=((ap[0]-am[0])*(bp[1]-bm[1])-(bp[0]-bm[0])*(ap[1]-am[1]))/(4*h*h)
 assert abs(detnum-l1*l2*math.sin(beta))<1e-8;random_assertions+=1
 e_m=math.hypot(px,py);assert close(e_m*100,e_m*1000/10);random_assertions+=1
ck('1000 varied FK/Jacobian/unit cases',random_assertions==4000,'1000 seeded cases;4000 mathematical assertions in default stdlib, not independent review.')
write(f'audits/{B}-v2-author-checks.json',{'role':'Author checks only; independent re-review is pending','startedAt':started,'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pythonExecutable':sys.executable,'pythonVersion':sys.version,'importedModules':['pathlib','json','math','random','hashlib','sys','datetime','copy','re','fractions'],'executionScope':'Default Python standard library only. No installations, model fitting/inference, restricted runtime, notebook retrieval or hardware claims. Supplied numerical rules and historical printed values only.','questionBatchSha256':sha(f'data/question-batches/{B}.json'),'checkGroups':len(checks),'checks':checks,'randomCases':1000,'randomAssertions':random_assertions,'sourceQualificationSha256':notes['sourceQualificationSha256']})
print('AUTHOR CHECKS:',len(checks),'groups;1000 cases;',random_assertions,'varied assertions')
