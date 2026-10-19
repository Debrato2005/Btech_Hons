"""Author-side arithmetic, schema and isolated merged-bank checks. Not independent verification."""
import json,sys,copy,datetime,hashlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import validate_bank,schema_errors
checks=[]
def check(name,actual,expected):
 assert actual==expected,(name,actual,expected)
 checks.append({'name':name,'actual':str(actual),'expected':str(expected),'passed':True})
check('Q022 period seconds',1/F(30),F(1,30))
check('Q022 period rounded milliseconds',round(float(1000/F(30)),2),33.33)
check('Q023 frequency hertz',1/F(1,10),F(10))
check('Q026 callbacks in (0,2]',sum(0<F(n,10)<=2 for n in range(1,30)),20)
check('Q027 detector capacity',1/F(1,10),F(10))
check('Q027 backlog rate',F(30)-1/F(1,10),F(20))
check('Q038 shown request sum',2+3,5)
check('Q039 printed speed default',f'Speed param: {1.0}','Speed param: 1.0')
check('Q041 independent parameter and sum',(2.5,2+3),(2.5,5))
check('Q072 independent periodic counts',(sum(0<F(n,30)<=1 for n in range(1,40)),sum(0<F(n,10)<=1 for n in range(1,20))),(30,10))
check('Q072 rate ratio',F(30,10),F(3))
check('Q077 signed request sum',-4+7,3)
batch=json.loads((ROOT/'data/question-batches/W01-L05.json').read_text());slides=json.loads((ROOT/'data/inspection-batches/W01-L05.json').read_text())['slides']
for kind,items in [('question',batch['questions']),('concept',batch['concepts']),('slide',slides)]:
 schema=json.loads((ROOT/f'data/schema.{kind}.json').read_text())
 errors=[e for x in items for e in schema_errors(x,schema)]
 assert not errors,errors
manifest=json.loads((ROOT/'sources/manifest.json').read_text())
allslides=[json.loads(l) for sid in ['lectures','assignments'] for l in (ROOT/f'sources/page_maps/{sid}.jsonl').read_text().splitlines()]
updates={s['id']:s for s in slides};allslides=[updates.get(s['id'],s) for s in allslides]
bank={'schemaVersion':'1.0.0','bankVersion':'L05-isolated-author-check','title':'L05 isolated author check','complete':False,'sources':manifest['sources'],'assets':manifest['assets'],'slides':allslides,'questions':batch['questions'],'concepts':batch['concepts'],'reviews':[],'learningTools':{'formulaSheet':[],'confusionPairs':[],'traps':[],'algorithmVisualizations':[],'numericalFamilies':[]}}
result=validate_bank(bank,ROOT,check_files=True)
assert result['valid'],result
out={'schemaVersion':'1.0.0','batchId':'W01-L05','authorId':batch['authorId'],'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Author-side explicit arithmetic and code-value checks plus schemas and temporary bank integration with actual source file hashes. No ROS runtime is installed or executed; this is not independent answer verification or complete-coverage certification.','checks':checks,'validation':result}
(ROOT/'audits/author-checks-W01-L05.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'checksPassed':len(checks),'schemaRecordsPassed':len(batch['questions'])+len(batch['concepts'])+len(slides),'validation':result},indent=2))
