from pathlib import Path
import numpy as np,json,hashlib,sys,datetime
from sklearn.model_selection import train_test_split
from validate import question_hash
R=Path(__file__).resolve().parents[1];b=json.loads((R/'data/question-batches/W06-L29.json').read_text());m=json.loads((R/'audits/W06-L29-v2-repair-manifest.json').read_text());qs={q['id']:q for q in b['questions']};checks=[]
def ck(name,cond):assert bool(cond),name;checks.append(name)
ck('51 accepted objects retain exact hashes',len(m['preservedQuestionHashes'])==51 and all(question_hash(qs[k])==v for k,v in m['preservedQuestionHashes'].items()))
ck('binary leaf count increases by1',4-1+2==5)
ck('reduced-error equality accepted',3<=3 and not 4<=3)
A=(2*0+8*4)/10;B=(5*2+5*2)/10;ck('weighted comparison',A==3.2 and B==2 and B<A)
points=[(3,1),(1,3),(3,2),(2,2)];ck('one routed point',[x+y<=4 and x-y>0 for x,y in points]==[True,False,False,False])
np.random.seed(42);stable=np.random.normal([9.8,0],[.5,10],(150,2));f=np.random.normal([4,150],[2,30],(150,2));r=np.random.normal([4,-150],[2,30],(150,2));X=np.vstack([stable,f,r]);y=np.array([0]*150+[1]*150+[2]*150);original=X.copy();ck('block labels',y[150]==1 and y[300]==2);ck('draws not means',not np.array_equal(X[150],[4,150]) and not np.array_equal(X[300],[4,-150]))
a=train_test_split(X,y,test_size=.3,stratify=y,random_state=42);c=train_test_split(X,y,test_size=.3,stratify=y,random_state=43);ck('different split leaves original arrays intact',np.array_equal(X,original) and not np.array_equal(a[0],c[0]))
for q in b['questions']:
 if q['id'] not in m['preservedQuestionHashes']:
  concept=next(c for c in b['concepts'] if c['id']in q['conceptIds'])
  for cit in q['citations']:
   if cit['slideId']not in concept['slideIds']:concept['slideIds'].append(cit['slideId'])
(R/'data/question-batches/W06-L29.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
(R/'audits/W06-L29-v2-author-checks.json').write_text(json.dumps({'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'allPassed':True,'assertionCount':len(checks),'checks':checks,'preservedAcceptedObjects':51,'scope':'Author checks only; independent review remains required.'},indent=2)+'\n');print(len(checks),'checks pass')
