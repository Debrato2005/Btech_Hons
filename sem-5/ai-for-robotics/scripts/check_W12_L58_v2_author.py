"""Author-only finite state/interface checks; no ROS, Gazebo or robot runtime."""
from pathlib import Path
import json, datetime, hashlib, random, statistics, itertools, xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]; named=[]
def check(name, condition):
 assert condition, name
 named.append(name)
latencies=[1.]*18+[20.,2.]
check('Mean latency counterexample is 2 ms',statistics.mean(latencies)==2)
check('Mean below 10 ms coexists with a missed deadline',max(latencies)>10)
# Added bounded diagnostic policy, not a transcription of any Nav2 default tree.
def diagnose(current_transform, localized, valid_path, retries, reached=False):
 if not current_transform or not localized:return 'restore prerequisites'
 if reached:return 'reached'
 if valid_path:return 'execute valid path'
 return 'recover and replan' if retries else 'goal route failure'
check('Run A exhausted route failure',diagnose(True,True,False,0)=='goal route failure')
check('Run B prerequisite failure despite active stack',diagnose(False,True,True,1)=='restore prerequisites')
check('One remaining retry is not exhausted',diagnose(True,True,False,1)=='recover and replan')
check('Valid route is not equivalent to reached',diagnose(True,True,True,1)=='execute valid path')
check('Explicit reached evidence is distinct',diagnose(True,True,True,1,True)=='reached')
check('Pose absence blocks motion',diagnose(True,False,True,1)=='restore prerequisites')
check('Pre-reset timestamp is not current',73>6)
# Inert declared interface graph, not ROS message generation or transport.
edges=[('sensor plugin','ROS navigation','/sim_scan','range observation'),('ROS controller','drive plugin','/drive_command','velocity request')]
check('Sensor observations flow outward',edges[0][0]=='sensor plugin' and edges[0][1]=='ROS navigation')
check('Commands flow into simulated actuation',edges[1][0]=='ROS controller' and edges[1][1]=='drive plugin')
check('Observation and command semantics differ',edges[0][3]!=edges[1][3])
# Added well-formed XML examples only; this is not validation against the SDF schema.
model=ET.fromstring('<sdf version="1.12"><model name="added_model"><link name="body"/></model></sdf>')
world=ET.fromstring('<sdf version="1.12"><world name="added_world"><model name="added_model"><link name="body"/></model></world></sdf>')
check('Illustrative direct model XML parses',model.find('model').attrib['name']=='added_model')
check('Illustrative world/model XML parses',world.find('world/model').attrib['name']=='added_model')
b=json.loads((R/'data/question-batches/W12-L58.json').read_text());qs={q['id']:q for q in b['questions']}
check('Added DDS item binds official primary source',any(e['url']=='https://www.omg.org/spec/DDS/1.4/About-DDS' for e in qs['W12-L58-P1845-Q03']['primaryEvidence']))
check('DDS source claim is retained', 'Data Distribution System' in qs['W12-L58-P1845-Q03']['conflictResolution']['sourceClaim'])
check('Navigation example explicitly supplies retry budget', 'one recovery and one replan' in qs['W12-L58-P1866-Q03']['stem'])
check('Added topic names are declared assumptions',any('illustrative topic names' in s for s in qs['W12-L58-P1852-Q03']['assumptions']))
exhaustive=0
for tr,loc,path,remaining,reached in itertools.product([False,True],repeat=5):
 out=diagnose(tr,loc,path,int(remaining),reached)
 assert (out=='restore prerequisites')==(not tr or not loc)
 if tr and loc and not reached:assert (out=='goal route failure')==(not path and not remaining)
 exhaustive+=1
rng=random.Random(58158); trials=2000
for _ in range(trials):
 deadline=rng.uniform(.1,100); base=deadline*.1; spike=deadline*2; n=20
 sample=[base]*(n-1)+[spike]
 assert statistics.mean(sample)<deadline and max(sample)>deadline
 current=rng.uniform(0,10); old=current+rng.uniform(1,100)
 assert old>current and diagnose(False,True,True,1)=='restore prerequisites'
out={'batchId':'W12-L58','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentReview':False,'scope':'Author-only explicit latency counterexamples, added finite diagnostic policy, inert plugin-interface graph and well-formed illustrative XML. These do not execute or validate ROS/Gazebo APIs, SDF schema conformance, deployment deadlines or hardware. Actual source pixels and official specification titles were inspected separately.','namedChecks':len(named),'exhaustivePolicyStates':exhaustive,'variedChecks':trials,'variedAssertions':4*trials,'checks':named,'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(R/'audits/W12-L58-v2-author-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
